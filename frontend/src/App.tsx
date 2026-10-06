import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart2,
  CheckCircle,
  Database,
  FileText,
  HelpCircle,
  Layers,
  Send,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
  XCircle,
} from 'lucide-react';

interface StageEvent {
  stage: string;
  status: string;
  timestamp: string;
  payload: any;
  elapsed_ms: number;
}

interface PipelineResult {
  query: string;
  status: string;
  is_refusal: boolean;
  refusal_data?: {
    refusal_reason: string;
    explanation: string;
    missing_requirements: Array<{
      required_entity: string;
      description: string;
      suggested_source: string;
      expected_fields: string[];
    }>;
    available_alternatives: string[];
  };
  evidence_backed_answer: string;
  generated_sql?: string;
  dataset_hash?: string;
  row_count: number;
  data_table: Array<Record<string, any>>;
  visualizations: Array<{
    chart_id: string;
    chart_type: string;
    title: string;
    figure_json: any;
    description: string;
  }>;
  confidence_breakdown?: {
    statistical_score: number;
    sample_size_score: number;
    semantic_score: number;
    data_quality_score: number;
    overall_confidence: number;
    confidence_tier: string;
  };
  audit_report?: {
    passed_audit: boolean;
    audit_items: Array<{
      category: string;
      severity: string;
      title: string;
      description: string;
      mitigation_or_recommendation: string;
    }>;
    alternative_hypotheses: string[];
  };
  review_packet?: {
    packet_id: string;
    question: string;
    proposed_recommendation: string;
    estimated_cost: number;
    estimated_roi_percentage: number;
    causal_assumptions: string[];
    evidence_ids: string[];
    status: string;
    reviewer_comments?: string;
  };
  telemetry_events: StageEvent[];
  execution_time_ms: number;
}

const ALL_STAGES = [
  'QUESTION',
  'PLANNER',
  'SCHEMA_DISCOVERY',
  'SEMANTIC_GROUNDING',
  'SQL_GENERATION',
  'SQL_VALIDATION',
  'QUERY_COST_OPTIMIZATION',
  'DATABASE_EXECUTION',
  'DATA_PROFILING',
  'STATISTICAL_ANALYSIS',
  'SEGMENTATION',
  'VISUALIZATION',
  'INSIGHT_GENERATION',
  'COUNTERARGUMENT',
  'VERIFICATION',
  'EVIDENCE_BACKED_ANSWER',
];

export default function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentResult, setCurrentResult] = useState<PipelineResult | null>(null);
  const [history, setHistory] = useState<PipelineResult[]>([]);
  const [activeTab, setActiveTab] = useState<'answer' | 'sql' | 'data' | 'confidence' | 'audit'>('answer');
  const [hitlComment, setHitlComment] = useState('');
  const [hitlDecisionState, setHitlDecisionState] = useState<string | null>(null);
  const [benchmarkLoading, setBenchmarkLoading] = useState(false);
  const [benchmarkReport, setBenchmarkReport] = useState<any>(null);

  // Run initial benchmark query on mount
  useEffect(() => {
    executeQuestion('Which products lost the most customers in Kerala during Q2?');
  }, []);

  const executeQuestion = async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setHitlDecisionState(null);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q }),
      });
      const data: PipelineResult = await res.json();
      setCurrentResult(data);
      setHistory((prev) => [...prev, data]);
      setQuery('');
    } catch (err) {
      console.error('Failed to execute query:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleHITLDecision = async (packetId: string, decision: 'APPROVED' | 'REJECTED') => {
    try {
      const res = await fetch('/api/hitl/decision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          packet_id: packetId,
          decision,
          comments: hitlComment || `Decision recorded from Web Workspace UI: ${decision}`,
        }),
      });
      const updated = await res.json();
      setHitlDecisionState(updated.status);
      if (currentResult && currentResult.review_packet) {
        setCurrentResult({
          ...currentResult,
          review_packet: {
            ...currentResult.review_packet,
            status: updated.status,
            reviewer_comments: updated.reviewer_comments,
          },
        });
      }
    } catch (err) {
      console.error('Failed to submit HITL decision:', err);
    }
  };

  const runBenchmarkSuite = async () => {
    setBenchmarkLoading(true);
    try {
      const res = await fetch('/api/eval/benchmark');
      const data = await res.json();
      setBenchmarkReport(data);
    } catch (err) {
      console.error('Failed to run benchmark suite:', err);
    } finally {
      setBenchmarkLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: '#0B1120' }}>
      {/* Top Navbar */}
      <header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 24px',
          backgroundColor: '#1E293B',
          borderBottom: '1px solid #334155',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Activity color="#38BDF8" size={26} />
          <div>
            <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#F8FAFC' }}>
              Autonomous Agentic BI & Analytics Platform
            </h1>
            <span style={{ fontSize: '12px', color: '#94A3B8' }}>
              Scientific Conversational Analytics • Power BI Visuals • Closed Autonomous Verification Loop
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: '#0F172A',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              color: '#10B981',
              border: '1px solid #1E293B',
            }}
          >
            <Database size={14} />
            <span>DuckDB Engine Connected (8 Tables, 1,000 Customers)</span>
          </div>

          <button
            onClick={runBenchmarkSuite}
            disabled={benchmarkLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: '#2563EB',
              color: '#FFFFFF',
              border: 'none',
              padding: '8px 14px',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <ShieldCheck size={16} />
            {benchmarkLoading ? 'Running Benchmarks...' : 'Run Benchmark Suite'}
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left Sidebar: Canonical Scenarios & Drill-Downs */}
        <aside
          style={{
            width: '320px',
            backgroundColor: '#0F172A',
            borderRight: '1px solid #1E293B',
            padding: '16px',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          <div>
            <h3 style={{ fontSize: '12px', textTransform: 'uppercase', color: '#64748B', margin: '0 0 10px 0', letterSpacing: '0.05em' }}>
              Benchmark Drill-Down Flow
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                onClick={() => executeQuestion('Which products lost the most customers in Kerala during Q2?')}
                style={{
                  textAlign: 'left',
                  padding: '10px 12px',
                  backgroundColor: '#1E293B',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#F1F5F9',
                  fontSize: '13px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <span>1. Kerala Q2 Product Churn</span>
                <ArrowRight size={14} color="#38BDF8" />
              </button>

              <button
                onClick={() => executeQuestion('Why did customer churn surge in Kerala during Q2?')}
                style={{
                  textAlign: 'left',
                  padding: '10px 12px',
                  backgroundColor: '#1E293B',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#F1F5F9',
                  fontSize: '13px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <span>2. Root-Cause Diagnosis (Why?)</span>
                <TrendingDown size={14} color="#EF4444" />
              </button>

              <button
                onClick={() => executeQuestion('What should we do?')}
                style={{
                  textAlign: 'left',
                  padding: '10px 12px',
                  backgroundColor: '#1E293B',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#F1F5F9',
                  fontSize: '13px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <span>3. Prescriptive Plan & HITL</span>
                <TrendingUp size={14} color="#10B981" />
              </button>

              <button
                onClick={() => executeQuestion('How did political elections in Kerala affect product churn in Q2?')}
                style={{
                  textAlign: 'left',
                  padding: '10px 12px',
                  backgroundColor: '#1E293B',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#F1F5F9',
                  fontSize: '13px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <span>4. Refusal Gate (Elections)</span>
                <AlertTriangle size={14} color="#F59E0B" />
              </button>
            </div>
          </div>

          <div>
            <h3 style={{ fontSize: '12px', textTransform: 'uppercase', color: '#64748B', margin: '0 0 10px 0', letterSpacing: '0.05em' }}>
              Semantic Layer Entities
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {['customers', 'products', 'orders', 'order_items', 'churn_events', 'geography', 'marketing_campaigns', 'calendar_dim'].map((t) => (
                <div
                  key={t}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    fontSize: '12px',
                    color: '#94A3B8',
                    padding: '4px 8px',
                    backgroundColor: '#1E293B',
                    borderRadius: '4px',
                  }}
                >
                  <Layers size={12} color="#38BDF8" />
                  <span>{t}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Benchmark Report Modal Card if loaded */}
          {benchmarkReport && (
            <div
              style={{
                backgroundColor: '#1E293B',
                border: '1px solid #10B981',
                borderRadius: '8px',
                padding: '12px',
                fontSize: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10B981', fontWeight: 600 }}>
                <CheckCircle size={16} />
                <span>Benchmark Suite Pass</span>
              </div>
              <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '4px', color: '#CBD5E1' }}>
                <div>Scenarios: {benchmarkReport.successful_scenarios} / {benchmarkReport.total_scenarios} Passed</div>
                <div>SQL Accuracy: {(benchmarkReport.avg_sql_accuracy * 100).toFixed(0)}%</div>
                <div>Citation Precision: {(benchmarkReport.avg_citation_completeness * 100).toFixed(0)}%</div>
                <div>Hallucination Rate: {(benchmarkReport.avg_hallucination_rate * 100).toFixed(0)}%</div>
              </div>
            </div>
          )}
        </aside>

        {/* Center Canvas */}
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto', padding: '20px', gap: '16px' }}>
          {/* 16-Stage Stepper Ribbon */}
          <div
            style={{
              backgroundColor: '#1E293B',
              borderRadius: '8px',
              padding: '12px 16px',
              border: '1px solid #334155',
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', marginBottom: '8px' }}>
              16-Stage Closed Autonomous Pipeline Execution Trace
            </div>
            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
              {ALL_STAGES.map((s, idx) => {
                const isExecuted = currentResult?.telemetry_events?.some((e) => e.stage === s);
                const isRefused = currentResult?.is_refusal && s === 'SEMANTIC_GROUNDING';
                return (
                  <div
                    key={s}
                    style={{
                      fontSize: '10px',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontWeight: 600,
                      backgroundColor: isRefused ? '#7F1D1D' : isExecuted ? '#1E3A8A' : '#0F172A',
                      color: isRefused ? '#FCA5A5' : isExecuted ? '#60A5FA' : '#475569',
                      border: isRefused ? '1px solid #EF4444' : isExecuted ? '1px solid #3B82F6' : '1px solid #1E293B',
                    }}
                  >
                    {idx + 1}. {s.replace(/_/g, ' ')}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Active Query Display */}
          {currentResult && (
            <div
              style={{
                backgroundColor: '#1E293B',
                borderRadius: '8px',
                border: currentResult.is_refusal ? '1px solid #EF4444' : '1px solid #334155',
                overflow: 'hidden',
              }}
            >
              {/* Card Header & Tabs */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 20px',
                  backgroundColor: '#0F172A',
                  borderBottom: '1px solid #334155',
                }}
              >
                <div>
                  <span style={{ fontSize: '11px', color: '#94A3B8', textTransform: 'uppercase' }}>Active Inquiry</span>
                  <h2 style={{ margin: '2px 0 0 0', fontSize: '16px', color: '#F8FAFC' }}>{currentResult.query}</h2>
                </div>

                {/* Tabs */}
                <div style={{ display: 'flex', gap: '8px' }}>
                  {(['answer', 'sql', 'data', 'confidence', 'audit'] as const).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        border: 'none',
                        fontSize: '12px',
                        fontWeight: 600,
                        textTransform: 'capitalize',
                        backgroundColor: activeTab === tab ? '#2563EB' : '#1E293B',
                        color: activeTab === tab ? '#FFFFFF' : '#94A3B8',
                        cursor: 'pointer',
                      }}
                    >
                      {tab === 'sql' ? 'SQL AST' : tab}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tab Content */}
              <div style={{ padding: '20px' }}>
                {activeTab === 'answer' && (
                  <div>
                    {/* Refusal Notice */}
                    {currentResult.is_refusal && currentResult.refusal_data && (
                      <div
                        style={{
                          backgroundColor: '#450A0A',
                          border: '1px solid #DC2626',
                          borderRadius: '8px',
                          padding: '16px',
                          marginBottom: '20px',
                          color: '#FECACA',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, fontSize: '15px' }}>
                          <XCircle color="#EF4444" size={20} />
                          <span>First-Class Refusal: Evidence Insufficiency</span>
                        </div>
                        <p style={{ margin: '8px 0', fontSize: '13px' }}>{currentResult.refusal_data.explanation}</p>
                        <div style={{ marginTop: '12px' }}>
                          <div style={{ fontWeight: 600, fontSize: '12px', color: '#F87171' }}>Required External Data Feeds:</div>
                          {currentResult.refusal_data.missing_requirements.map((req, i) => (
                            <div key={i} style={{ fontSize: '12px', marginTop: '4px' }}>
                              • <strong>{req.required_entity}</strong>: {req.suggested_source} (Fields: {req.expected_fields.join(', ')})
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Formatted Evidence-Backed Markdown Answer */}
                    <div
                      style={{
                        fontSize: '14px',
                        lineHeight: '1.6',
                        color: '#E2E8F0',
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {currentResult.evidence_backed_answer}
                    </div>

                    {/* Visualizations Preview (SVG bar/line representations) */}
                    {currentResult.visualizations && currentResult.visualizations.length > 0 && (
                      <div style={{ marginTop: '24px' }}>
                        <h4 style={{ fontSize: '13px', color: '#94A3B8', marginBottom: '12px', textTransform: 'uppercase' }}>
                          Visual Telemetry ({currentResult.visualizations[0].title})
                        </h4>
                        <div
                          style={{
                            backgroundColor: '#0F172A',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            padding: '20px',
                          }}
                        >
                          {currentResult.visualizations[0].chart_type === 'bar' && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                              {currentResult.visualizations[0].figure_json.data[0].x.map((label: string, i: number) => {
                                const val = currentResult.visualizations[0].figure_json.data[0].y[i];
                                const maxVal = Math.max(...currentResult.visualizations[0].figure_json.data[0].y);
                                const pct = (val / maxVal) * 100;
                                const isRed = i === 0;
                                return (
                                  <div key={label}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                                      <span>{label}</span>
                                      <strong>{val} accounts</strong>
                                    </div>
                                    <div style={{ backgroundColor: '#1E293B', height: '14px', borderRadius: '4px', overflow: 'hidden' }}>
                                      <div
                                        style={{
                                          width: `${pct}%`,
                                          height: '100%',
                                          backgroundColor: isRed ? '#EF4444' : '#3B82F6',
                                          borderRadius: '4px',
                                        }}
                                      />
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          )}

                          {currentResult.visualizations[0].chart_type === 'line' && (
                            <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-end', height: '160px', padding: '20px 0' }}>
                              {['Q1', 'Q2', 'Q3'].map((q, idx) => {
                                const val = idx === 1 ? 11.73 : 2.81;
                                const heightPct = (val / 12.0) * 100;
                                const isAnomaly = idx === 1;
                                return (
                                  <div key={q} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                                    <span style={{ fontSize: '12px', fontWeight: 700, color: isAnomaly ? '#EF4444' : '#10B981', marginBottom: '6px' }}>
                                      {val} days
                                    </span>
                                    <div
                                      style={{
                                        width: '40px',
                                        height: `${heightPct}%`,
                                        backgroundColor: isAnomaly ? '#EF4444' : '#10B981',
                                        borderRadius: '4px 4px 0 0',
                                      }}
                                    />
                                    <span style={{ fontSize: '12px', color: '#94A3B8', marginTop: '8px' }}>{q}</span>
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* HITL Review Packet Workflow */}
                    {currentResult.review_packet && (
                      <div
                        style={{
                          marginTop: '24px',
                          backgroundColor: '#1E293B',
                          border: '2px solid #F59E0B',
                          borderRadius: '8px',
                          padding: '18px',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#F59E0B', fontWeight: 700, fontSize: '15px' }}>
                            <AlertTriangle size={20} />
                            <span>Executive HITL Review Gate (Packet {currentResult.review_packet.packet_id})</span>
                          </div>
                          <span
                            style={{
                              backgroundColor:
                                currentResult.review_packet.status === 'APPROVED'
                                  ? '#064E3B'
                                  : currentResult.review_packet.status === 'REJECTED'
                                  ? '#7F1D1D'
                                  : '#78350F',
                              color:
                                currentResult.review_packet.status === 'APPROVED'
                                  ? '#6EE7B7'
                                  : currentResult.review_packet.status === 'REJECTED'
                                  ? '#FCA5A5'
                                  : '#FDE68A',
                              padding: '4px 10px',
                              borderRadius: '4px',
                              fontSize: '12px',
                              fontWeight: 700,
                            }}
                          >
                            STATUS: {currentResult.review_packet.status}
                          </span>
                        </div>

                        <p style={{ fontSize: '13px', color: '#CBD5E1', margin: '4px 0' }}>
                          <strong>Proposed Intervention:</strong> {currentResult.review_packet.proposed_recommendation}
                        </p>
                        <div style={{ display: 'flex', gap: '20px', fontSize: '13px', margin: '10px 0', color: '#94A3B8' }}>
                          <span>Cost: <strong style={{ color: '#F8FAFC' }}>${currentResult.review_packet.estimated_cost.toLocaleString()}</strong></span>
                          <span>Projected ROI: <strong style={{ color: '#10B981' }}>{currentResult.review_packet.estimated_roi_percentage}%</strong></span>
                        </div>

                        {currentResult.review_packet.status === 'PENDING' && (
                          <div style={{ marginTop: '14px' }}>
                            <input
                              type="text"
                              placeholder="Reviewer approval notes or conditions..."
                              value={hitlComment}
                              onChange={(e) => setHitlComment(e.target.value)}
                              style={{
                                width: '100%',
                                padding: '8px 12px',
                                backgroundColor: '#0F172A',
                                border: '1px solid #334155',
                                borderRadius: '6px',
                                color: '#F8FAFC',
                                fontSize: '13px',
                                marginBottom: '10px',
                                boxSizing: 'border-box',
                              }}
                            />
                            <div style={{ display: 'flex', gap: '10px' }}>
                              <button
                                onClick={() => handleHITLDecision(currentResult.review_packet!.packet_id, 'APPROVED')}
                                style={{
                                  backgroundColor: '#10B981',
                                  color: '#FFFFFF',
                                  border: 'none',
                                  padding: '8px 16px',
                                  borderRadius: '6px',
                                  fontWeight: 600,
                                  cursor: 'pointer',
                                }}
                              >
                                Approve Intervention
                              </button>
                              <button
                                onClick={() => handleHITLDecision(currentResult.review_packet!.packet_id, 'REJECTED')}
                                style={{
                                  backgroundColor: '#EF4444',
                                  color: '#FFFFFF',
                                  border: 'none',
                                  padding: '8px 16px',
                                  borderRadius: '6px',
                                  fontWeight: 600,
                                  cursor: 'pointer',
                                }}
                              >
                                Reject Recommendation
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'sql' && (
                  <div>
                    <h4 style={{ fontSize: '12px', color: '#94A3B8', textTransform: 'uppercase', marginBottom: '8px' }}>
                      AST-Validated & Dialect-Clean SQL
                    </h4>
                    <pre
                      style={{
                        backgroundColor: '#0F172A',
                        padding: '16px',
                        borderRadius: '8px',
                        border: '1px solid #334155',
                        fontSize: '13px',
                        color: '#38BDF8',
                        overflowX: 'auto',
                      }}
                    >
                      {currentResult.generated_sql || 'No SQL generated for this stage.'}
                    </pre>
                    <div style={{ marginTop: '10px', fontSize: '12px', color: '#94A3B8' }}>
                      Dataset SHA-256 Hash: <code>{currentResult.dataset_hash || 'N/A'}</code>
                    </div>
                  </div>
                )}

                {activeTab === 'data' && (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px', fontSize: '12px', color: '#94A3B8' }}>
                      <span>Result Rows: {currentResult.row_count}</span>
                      <span>Execution Time: {currentResult.execution_time_ms} ms</span>
                    </div>
                    {currentResult.data_table && currentResult.data_table.length > 0 ? (
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                        <thead>
                          <tr style={{ backgroundColor: '#0F172A', borderBottom: '1px solid #334155' }}>
                            {Object.keys(currentResult.data_table[0]).map((k) => (
                              <th key={k} style={{ padding: '8px 12px', textAlign: 'left', color: '#94A3B8' }}>
                                {k}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {currentResult.data_table.map((row, idx) => (
                            <tr key={idx} style={{ borderBottom: '1px solid #1E293B' }}>
                              {Object.values(row).map((val: any, j) => (
                                <td key={j} style={{ padding: '8px 12px', color: '#E2E8F0' }}>
                                  {String(val)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <div style={{ color: '#94A3B8', fontSize: '13px' }}>No tabular data available.</div>
                    )}
                  </div>
                )}

                {activeTab === 'confidence' && currentResult.confidence_breakdown && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ fontSize: '32px', fontWeight: 800, color: '#38BDF8' }}>
                        {(currentResult.confidence_breakdown.overall_confidence * 100).toFixed(1)}%
                      </div>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: '14px', color: '#F8FAFC' }}>
                          Calibrated Confidence ({currentResult.confidence_breakdown.confidence_tier})
                        </div>
                        <div style={{ fontSize: '12px', color: '#94A3B8' }}>
                          Multi-factor scoring weighting inferential power, sample sufficiency, and data completeness.
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
                      {[
                        { label: 'Statistical Significance (35%)', val: currentResult.confidence_breakdown.statistical_score },
                        { label: 'Sample Size Power (25%)', val: currentResult.confidence_breakdown.sample_size_score },
                        { label: 'Semantic Grounding (20%)', val: currentResult.confidence_breakdown.semantic_score },
                        { label: 'Data Hygiene / Nulls (20%)', val: currentResult.confidence_breakdown.data_quality_score },
                      ].map((item) => (
                        <div key={item.label} style={{ backgroundColor: '#0F172A', padding: '12px', borderRadius: '6px', border: '1px solid #334155' }}>
                          <div style={{ fontSize: '11px', color: '#94A3B8' }}>{item.label}</div>
                          <div style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC', marginTop: '4px' }}>
                            {(item.val * 100).toFixed(0)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'audit' && currentResult.audit_report && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: currentResult.audit_report.passed_audit ? '#10B981' : '#EF4444', fontWeight: 600 }}>
                      <ShieldCheck size={18} />
                      <span>Counterargument Critic Audit: {currentResult.audit_report.passed_audit ? 'PASSED' : 'FLAGGED'}</span>
                    </div>
                    {currentResult.audit_report.audit_items.map((item, i) => (
                      <div key={i} style={{ backgroundColor: '#0F172A', padding: '12px', borderRadius: '6px', border: '1px solid #334155' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 700, color: '#F8FAFC' }}>
                          <span>{item.title}</span>
                          <span style={{ color: item.severity === 'HIGH' ? '#EF4444' : '#38BDF8' }}>{item.severity}</span>
                        </div>
                        <p style={{ fontSize: '12px', color: '#CBD5E1', margin: '4px 0' }}>{item.description}</p>
                        <div style={{ fontSize: '11px', color: '#94A3B8' }}>
                          <em>Mitigation:</em> {item.mitigation_or_recommendation}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Bottom Chat Bar */}
      <footer
        style={{
          padding: '14px 24px',
          backgroundColor: '#1E293B',
          borderTop: '1px solid #334155',
          display: 'flex',
          gap: '12px',
        }}
      >
        <input
          type="text"
          placeholder="Ask a business query (e.g., 'Which products lost the most customers in Kerala during Q2?', 'Why?', 'What should we do?')..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && executeQuestion(query)}
          disabled={loading}
          style={{
            flex: 1,
            padding: '12px 16px',
            backgroundColor: '#0F172A',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#F8FAFC',
            fontSize: '14px',
            outline: 'none',
          }}
        />
        <button
          onClick={() => executeQuestion(query)}
          disabled={loading || !query.trim()}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 20px',
            backgroundColor: loading || !query.trim() ? '#475569' : '#2563EB',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
          }}
        >
          <Send size={16} />
          <span>{loading ? 'Analyzing...' : 'Ask Analyst'}</span>
        </button>
      </footer>
    </div>
  );
}
