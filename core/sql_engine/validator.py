"""SQL AST Validator enforcing read-only safety, join integrity, and schema grounding via sqlglot."""

from __future__ import annotations

from typing import Dict, List, Optional, Set
import sqlglot
from sqlglot import exp
from pydantic import BaseModel, Field
from core.semantic_layer.catalog import SemanticCatalog


class SQLValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    referenced_tables: List[str] = Field(default_factory=list)
    referenced_columns: List[str] = Field(default_factory=list)
    has_aggregates: bool = False
    has_group_by: bool = False


class SQLValidator:
    """Validates SQL syntax, security constraints, and join graph compliance using AST analysis."""

    FORBIDDEN_EXPRESSIONS = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Alter,
        exp.Create,
        exp.Command,
    )

    def __init__(self, catalog: Optional[SemanticCatalog] = None):
        self.catalog = catalog or SemanticCatalog()

    def validate_sql(self, sql: str) -> SQLValidationResult:
        errors: List[str] = []
        try:
            parsed = sqlglot.parse_one(sql)
        except Exception as e:
            return SQLValidationResult(is_valid=False, errors=[f"SQL Syntax Error: {str(e)}"])

        # 1. Enforce that statement is strictly a SELECT query
        if not isinstance(parsed, exp.Select):
            errors.append(f"Forbidden SQL statement type: {type(parsed).__name__}. Only SELECT queries are permitted.")
            return SQLValidationResult(is_valid=False, errors=errors)

        # 2. Check for nested mutating subqueries
        for forbidden_type in self.FORBIDDEN_EXPRESSIONS:
            if list(parsed.find_all(forbidden_type)):
                errors.append(f"Detected prohibited mutating expression: {forbidden_type.__name__}")

        # 3. Extract tables and alias map
        alias_to_table: Dict[str, str] = {}
        referenced_tables: Set[str] = set()

        for tbl in parsed.find_all(exp.Table):
            tbl_name = tbl.name.lower()
            referenced_tables.add(tbl_name)
            if tbl.alias:
                alias_to_table[tbl.alias.lower()] = tbl_name
            else:
                alias_to_table[tbl_name] = tbl_name

        # Validate that referenced tables exist in catalog
        for tbl_name in referenced_tables:
            if not self.catalog.get_entity(tbl_name):
                errors.append(f"Unknown table '{tbl_name}' not defined in semantic catalog.")

        # 4. Validate JOIN paths against JoinGraph
        joins = list(parsed.find_all(exp.Join))
        from_clause = parsed.args.get("from")
        base_table = None
        if from_clause and isinstance(from_clause.this, exp.Table):
            base_table = from_clause.this.name.lower()

        for j in joins:
            join_table_expr = j.this
            if isinstance(join_table_expr, exp.Table):
                join_tbl_name = join_table_expr.name.lower()
                # Check that join between base_table (or other joined tables) and join_tbl_name is valid
                is_connected = False
                for existing_tbl in referenced_tables:
                    if existing_tbl != join_tbl_name and self.catalog.join_graph.is_valid_join(existing_tbl, join_tbl_name):
                        is_connected = True
                        break
                if not is_connected:
                    errors.append(
                        f"Unapproved JOIN on table '{join_tbl_name}'. Join path violates semantic layer join graph."
                    )

        # 5. Check aggregates and GROUP BY
        has_aggregates = bool(list(parsed.find_all(exp.AggFunc)))
        has_group_by = parsed.args.get("group") is not None

        cols = [c.name for c in parsed.find_all(exp.Column)]

        return SQLValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            referenced_tables=list(referenced_tables),
            referenced_columns=cols,
            has_aggregates=has_aggregates,
            has_group_by=has_group_by,
        )
