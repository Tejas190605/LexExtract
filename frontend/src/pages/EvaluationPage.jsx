import React, { useState, useEffect, useMemo } from 'react';
import { 
  Target, 
  Play, 
  RotateCw, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  BookOpen, 
  Layers, 
  FileText, 
  ChevronRight, 
  ChevronDown, 
  Filter, 
  Info,
  ShieldCheck,
  TrendingUp,
  Award,
  Database
} from 'lucide-react';
import { 
  getEvaluationSummary, 
  getEvaluationDocuments, 
  getEvaluationErrors, 
  runEvaluationBenchmark 
} from '../services/api';
import { useAuth } from '../context/AuthContext';
import StatCard from '../components/common/StatCard';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';

export default function EvaluationPage() {
  const { user } = useAuth();
  const userRole = (user?.role || 'USER').toUpperCase();
  const canRunBenchmark = userRole === 'ANALYST' || userRole === 'ADMIN';

  // Data states
  const [summary, setSummary] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [errors, setErrors] = useState(null);
  
  // UI states
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [statusMessage, setStatusMessage] = useState(null);

  // Sorting & Filtering
  const [sortBy, setSortBy] = useState('doc_id'); // 'doc_id' | 'kw_f1' | 'ent_f1' | 'latency'
  const [errorTab, setErrorTab] = useState('keywords'); // 'keywords' | 'entities' | 'mismatches'
  const [selectedDocId, setSelectedDocId] = useState(null);

  // Load latest benchmark results on mount
  const loadEvaluationData = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const [sumData, docsData, errData] = await Promise.all([
        getEvaluationSummary(),
        getEvaluationDocuments(),
        getEvaluationErrors()
      ]);
      setSummary(sumData);
      setDocuments(docsData || []);
      setErrors(errData);
    } catch (err) {
      console.error('Failed to load evaluation data:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to retrieve benchmark evaluation report.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEvaluationData();
  }, []);

  // Trigger live benchmark run
  const handleRunBenchmark = async () => {
    if (!canRunBenchmark) {
      alert('Only Analyst and Administrator roles are authorized to execute the benchmark suite.');
      return;
    }

    setIsRunning(true);
    setStatusMessage(null);
    try {
      const result = await runEvaluationBenchmark();
      setSummary({
        benchmark_summary: result.benchmark_summary,
        performance: result.performance,
        keyword_evaluation: result.keyword_evaluation,
        entity_evaluation: result.entity_evaluation
      });
      setDocuments(result.document_results || []);
      setErrors(result.error_analysis || null);
      setStatusMessage({
        type: 'success',
        text: `Benchmark execution completed successfully on ${result.benchmark_summary.total_documents} legal documents in ${result.benchmark_summary.total_execution_time_seconds}s.`
      });
    } catch (err) {
      setStatusMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Benchmark evaluation failed during execution.'
      });
    } finally {
      setIsRunning(false);
    }
  };

  // Sort document results
  const sortedDocuments = useMemo(() => {
    const list = [...documents];
    list.sort((a, b) => {
      if (sortBy === 'kw_f1') {
        return (b.keyword_metrics?.f1 || 0) - (a.keyword_metrics?.f1 || 0);
      }
      if (sortBy === 'ent_f1') {
        return (b.entity_metrics?.f1 || 0) - (a.entity_metrics?.f1 || 0);
      }
      if (sortBy === 'latency') {
        return (b.processing_time_ms || 0) - (a.processing_time_ms || 0);
      }
      return (a.document_id || '').localeCompare(b.document_id || '');
    });
    return list;
  }, [documents, sortBy]);

  // Format timestamp
  const formatTimestamp = (ts) => {
    if (!ts) return '—';
    try {
      const d = new Date(ts);
      return d.toLocaleString('en-US', {
        month: 'short',
        day: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return ts;
    }
  };

  const kwMacro = summary?.keyword_evaluation?.macro || {};
  const kwMicro = summary?.keyword_evaluation?.micro || {};
  const entMacro = summary?.entity_evaluation?.macro || {};
  const entMicro = summary?.entity_evaluation?.micro || {};
  const perf = summary?.performance || {};
  const bSummary = summary?.benchmark_summary || {};
  const ablation = summary?.keyword_evaluation?.ablation_comparison || {};
  const topK = summary?.keyword_evaluation?.top_k_cutoffs || {};

  return (
    <div className="space-y-6">
      {/* Institutional Page Header */}
      <div className="bg-white border border-legal-border p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-legal-navy text-white shadow-xs">
              <Target className="w-6 h-6 text-legal-gold" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-bold font-serif text-legal-navy tracking-tight">
                  ASTMA Quantitative Evaluation &amp; Benchmarking
                </h1>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 bg-purple-100 text-purple-900 border border-purple-300">
                  Empirical Evidence
                </span>
              </div>
              <p className="text-xs text-legal-charcoal-muted mt-1">
                Quantitative Information Retrieval (IR) and NLP evaluation against curated 12-document legal ground-truth corpus.
              </p>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={loadEvaluationData}
            disabled={isLoading || isRunning}
            className="inline-flex items-center space-x-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 border border-legal-border text-legal-navy text-xs font-semibold uppercase tracking-wider transition-colors disabled:opacity-50"
            title="Reload cached benchmark report"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Reload</span>
          </button>

          {canRunBenchmark && (
            <button
              onClick={handleRunBenchmark}
              disabled={isRunning || isLoading}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-legal-burgundy hover:bg-legal-burgundy-hover text-white text-xs font-semibold uppercase tracking-wider transition-colors shadow-xs disabled:opacity-60"
            >
              <Play className={`w-3.5 h-3.5 text-legal-gold ${isRunning ? 'animate-pulse' : ''}`} />
              <span>{isRunning ? 'Running Benchmark...' : 'Run Benchmark'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Execution Notification */}
      {statusMessage && (
        <div className={`p-4 border text-xs flex items-start space-x-3 ${
          statusMessage.type === 'success' 
            ? 'bg-emerald-50 border-emerald-300 text-emerald-900' 
            : 'bg-rose-50 border-rose-300 text-rose-900'
        }`}>
          {statusMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          )}
          <div className="flex-1 leading-relaxed">
            <span className="font-bold">{statusMessage.type === 'success' ? 'Benchmark Completed: ' : 'Error: '}</span>
            {statusMessage.text}
          </div>
          <button
            onClick={() => setStatusMessage(null)}
            className="text-[11px] underline opacity-70 hover:opacity-100 font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Benchmark Metadata Strip */}
      <div className="bg-legal-parchment-dark border border-legal-border-warm px-4 py-2.5 flex flex-wrap items-center justify-between text-xs text-legal-charcoal-muted gap-2">
        <div className="flex items-center space-x-2">
          <Database className="w-3.5 h-3.5 text-legal-navy" />
          <span>Corpus: <strong className="text-legal-navy">{bSummary.dataset_name || '12 Curated Legal Documents'}</strong></span>
          <span>•</span>
          <span>Last Run: <strong className="text-legal-navy">{formatTimestamp(bSummary.execution_timestamp)}</strong></span>
        </div>
        <div className="flex items-center space-x-3 font-mono text-[11px]">
          <span>Total Runtime: <strong className="text-legal-burgundy">{bSummary.total_execution_time_seconds || '—'}s</strong></span>
          <span>•</span>
          <span>Documents: <strong className="text-legal-navy">{bSummary.total_documents || 12}</strong></span>
        </div>
      </div>

      {isLoading && !summary && (
        <LoadingState
          message="Executing empirical Information Retrieval evaluation benchmark..."
          subtext="Evaluating RAKE n-grams, TF-IDF weights, statutory lexicons, and spaCy hybrid NER against 12 ground-truth files."
        />
      )}

      {errorMsg && !summary && (
        <ErrorState
          title="Benchmark Execution Error"
          message={errorMsg}
          onRetry={loadEvaluationData}
        />
      )}

      {summary && (
        <>
          {/* ============================================================== */}
          {/* SECTION 1: KEYWORD & ENTITY MACRO SCORECARD                     */}
          {/* ============================================================== */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Keyword Extraction Metrics Card */}
            <div className="bg-white border border-legal-border p-5 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-legal-border pb-3">
                <div className="flex items-center space-x-2">
                  <Award className="w-4 h-4 text-legal-burgundy" />
                  <h3 className="font-serif font-bold text-sm text-legal-navy uppercase tracking-wider">
                    Keyword Extraction (Hybrid RAKE + TF-IDF)
                  </h3>
                </div>
                <span className="text-[10px] font-mono text-slate-500 uppercase">Macro / Micro</span>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 bg-legal-parchment border border-legal-border-warm text-center">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-legal-charcoal-muted block">
                    Precision
                  </span>
                  <p className="text-2xl font-bold font-serif text-legal-navy mt-1">
                    {kwMacro.precision !== undefined ? kwMacro.precision.toFixed(3) : '—'}
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono block mt-1">
                    Micro: {kwMicro.precision !== undefined ? kwMicro.precision.toFixed(3) : '—'}
                  </span>
                </div>

                <div className="p-3 bg-legal-parchment border border-legal-border-warm text-center">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-legal-charcoal-muted block">
                    Recall
                  </span>
                  <p className="text-2xl font-bold font-serif text-legal-burgundy mt-1">
                    {kwMacro.recall !== undefined ? kwMacro.recall.toFixed(3) : '—'}
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono block mt-1">
                    Micro: {kwMicro.recall !== undefined ? kwMicro.recall.toFixed(3) : '—'}
                  </span>
                </div>

                <div className="p-3 bg-legal-parchment border border-legal-border-warm text-center">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-legal-charcoal-muted block">
                    F1-Score
                  </span>
                  <p className="text-2xl font-bold font-serif text-legal-gold mt-1">
                    {kwMacro.f1 !== undefined ? kwMacro.f1.toFixed(3) : '—'}
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono block mt-1">
                    Micro: {kwMicro.f1 !== undefined ? kwMicro.f1.toFixed(3) : '—'}
                  </span>
                </div>
              </div>

              <p className="text-[11px] text-legal-charcoal-muted leading-relaxed">
                Evaluates candidate unigrams, bigrams, and trigrams against human-curated statutory and contractual terminology.
              </p>
            </div>

            {/* Entity Extraction Metrics Card */}
            <div className="bg-white border border-legal-border p-5 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-legal-border pb-3">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-700" />
                  <h3 className="font-serif font-bold text-sm text-legal-navy uppercase tracking-wider">
                    Named Entity Recognition (Hybrid spaCy + Rules)
                  </h3>
                </div>
                <span className="text-[10px] font-mono text-slate-500 uppercase">Macro / Micro</span>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 bg-legal-parchment border border-legal-border-warm text-center">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-legal-charcoal-muted block">
                    Precision
                  </span>
                  <p className="text-2xl font-bold font-serif text-legal-navy mt-1">
                    {entMacro.precision !== undefined ? entMacro.precision.toFixed(3) : '—'}
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono block mt-1">
                    Micro: {entMicro.precision !== undefined ? entMicro.precision.toFixed(3) : '—'}
                  </span>
                </div>

                <div className="p-3 bg-legal-parchment border border-legal-border-warm text-center">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-legal-charcoal-muted block">
                    Recall
                  </span>
                  <p className="text-2xl font-bold font-serif text-legal-burgundy mt-1">
                    {entMacro.recall !== undefined ? entMacro.recall.toFixed(3) : '—'}
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono block mt-1">
                    Micro: {entMicro.recall !== undefined ? entMicro.recall.toFixed(3) : '—'}
                  </span>
                </div>

                <div className="p-3 bg-legal-parchment border border-legal-border-warm text-center">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-legal-charcoal-muted block">
                    F1-Score
                  </span>
                  <p className="text-2xl font-bold font-serif text-legal-gold mt-1">
                    {entMacro.f1 !== undefined ? entMacro.f1.toFixed(3) : '—'}
                  </p>
                  <span className="text-[10px] text-slate-500 font-mono block mt-1">
                    Micro: {entMicro.f1 !== undefined ? entMicro.f1.toFixed(3) : '—'}
                  </span>
                </div>
              </div>

              <p className="text-[11px] text-legal-charcoal-muted leading-relaxed">
                Requires exact normalized text and matching entity category (<span className="font-mono text-[10px]">COURT</span>, <span className="font-mono text-[10px]">ACT</span>, <span className="font-mono text-[10px]">SECTION</span>, <span className="font-mono text-[10px]">PERSON</span>, etc.).
              </p>
            </div>
          </div>

          {/* ============================================================== */}
          {/* SECTION 2: LATENCY & MATHEMATICAL FORMULA DEFINITIONS           */}
          {/* ============================================================== */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-white border border-legal-border">
              <span className="text-[10px] font-bold uppercase tracking-wider text-legal-charcoal-muted block">
                Avg Latency / Document
              </span>
              <p className="text-xl font-bold font-serif text-legal-navy mt-1">
                {perf.average_time_ms || 0} ms
              </p>
              <span className="text-[10px] text-slate-500 font-mono block mt-0.5">
                Min: {perf.min_time_ms || 0} ms • Max: {perf.max_time_ms || 0} ms
              </span>
            </div>

            <div className="p-4 bg-white border border-legal-border">
              <span className="text-[10px] font-bold uppercase tracking-wider text-legal-charcoal-muted block">
                Avg Keyword Extraction
              </span>
              <p className="text-xl font-bold font-serif text-legal-navy mt-1">
                {perf.avg_keyword_time_ms || 0} ms
              </p>
              <span className="text-[10px] text-slate-500 font-mono block mt-0.5">
                RAKE + TF-IDF matrix
              </span>
            </div>

            <div className="p-4 bg-white border border-legal-border">
              <span className="text-[10px] font-bold uppercase tracking-wider text-legal-charcoal-muted block">
                Avg Entity Extraction
              </span>
              <p className="text-xl font-bold font-serif text-legal-navy mt-1">
                {perf.avg_entity_time_ms || 0} ms
              </p>
              <span className="text-[10px] text-slate-500 font-mono block mt-0.5">
                spaCy pipeline + gazetteer
              </span>
            </div>

            <div className="p-4 bg-white border border-legal-border">
              <span className="text-[10px] font-bold uppercase tracking-wider text-legal-charcoal-muted block">
                IR Metrics Formula
              </span>
              <div className="mt-1 font-mono text-[10px] text-legal-charcoal leading-tight">
                <div>P = TP / (TP + FP)</div>
                <div>R = TP / (TP + FN)</div>
                <div>F1 = 2PR / (P + R)</div>
              </div>
            </div>
          </div>

          {/* ============================================================== */}
          {/* SECTION 3: ABLATION COMPARISON & TOP-K EVALUATION               */}
          {/* ============================================================== */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Model Ablation Study */}
            <div className="bg-white border border-legal-border p-5 shadow-xs space-y-3">
              <div className="flex items-center space-x-2 border-b border-legal-border pb-2">
                <TrendingUp className="w-4 h-4 text-legal-burgundy" />
                <h3 className="font-serif font-bold text-xs uppercase tracking-wider text-legal-navy">
                  Algorithm Ablation Comparison (Keyword Models)
                </h3>
              </div>
              <p className="text-[11px] text-legal-charcoal-muted">
                Measures the empirical benefit of combining statistical (TF-IDF), co-occurrence (RAKE), and legal statutory lexicons into a weighted rank fusion.
              </p>
              <table className="min-w-full text-xs divide-y divide-legal-border text-left">
                <thead className="bg-legal-navy text-white text-[10px] uppercase font-semibold">
                  <tr>
                    <th className="px-3 py-2">Algorithm Technique</th>
                    <th className="px-3 py-2 text-center">Precision</th>
                    <th className="px-3 py-2 text-center">Recall</th>
                    <th className="px-3 py-2 text-center">F1-Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-legal-border bg-white text-[11px]">
                  <tr>
                    <td className="px-3 py-2 font-semibold text-legal-navy">TF-IDF Alone (Corpus Relative)</td>
                    <td className="px-3 py-2 text-center font-mono">{ablation.tfidf?.precision?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono">{ablation.tfidf?.recall?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono font-bold text-legal-charcoal">{ablation.tfidf?.f1?.toFixed(3) || '—'}</td>
                  </tr>
                  <tr>
                    <td className="px-3 py-2 font-semibold text-legal-navy">RAKE Alone (Graph Degree)</td>
                    <td className="px-3 py-2 text-center font-mono">{ablation.rake?.precision?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono">{ablation.rake?.recall?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono font-bold text-legal-charcoal">{ablation.rake?.f1?.toFixed(3) || '—'}</td>
                  </tr>
                  <tr className="bg-legal-parchment font-semibold">
                    <td className="px-3 py-2 text-legal-burgundy font-bold">Hybrid Fusion (Production)</td>
                    <td className="px-3 py-2 text-center font-mono text-legal-burgundy">{ablation.hybrid?.precision?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono text-legal-burgundy">{ablation.hybrid?.recall?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono font-bold text-legal-burgundy">{ablation.hybrid?.f1?.toFixed(3) || '—'}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Top-K Cutoff Performance */}
            <div className="bg-white border border-legal-border p-5 shadow-xs space-y-3">
              <div className="flex items-center space-x-2 border-b border-legal-border pb-2">
                <Filter className="w-4 h-4 text-legal-navy" />
                <h3 className="font-serif font-bold text-xs uppercase tracking-wider text-legal-navy">
                  Top-K Cutoff Retrieval Evaluation
                </h3>
              </div>
              <p className="text-[11px] text-legal-charcoal-muted">
                Evaluates keyword precision and recall when restricting output candidates to the top 5, 10, and 20 ranked predictions.
              </p>
              <table className="min-w-full text-xs divide-y divide-legal-border text-left">
                <thead className="bg-legal-navy text-white text-[10px] uppercase font-semibold">
                  <tr>
                    <th className="px-3 py-2">Cutoff Threshold</th>
                    <th className="px-3 py-2 text-center">Precision@K</th>
                    <th className="px-3 py-2 text-center">Recall@K</th>
                    <th className="px-3 py-2 text-center">F1@K</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-legal-border bg-white text-[11px]">
                  <tr>
                    <td className="px-3 py-2 font-mono font-semibold">Top-5 (K=5)</td>
                    <td className="px-3 py-2 text-center font-mono">{topK.k_5?.precision?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono">{topK.k_5?.recall?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono font-bold text-legal-charcoal">{topK.k_5?.f1?.toFixed(3) || '—'}</td>
                  </tr>
                  <tr>
                    <td className="px-3 py-2 font-mono font-semibold">Top-10 (K=10)</td>
                    <td className="px-3 py-2 text-center font-mono">{topK.k_10?.precision?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono">{topK.k_10?.recall?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono font-bold text-legal-charcoal">{topK.k_10?.f1?.toFixed(3) || '—'}</td>
                  </tr>
                  <tr>
                    <td className="px-3 py-2 font-mono font-semibold">Top-20 (K=20)</td>
                    <td className="px-3 py-2 text-center font-mono">{topK.k_20?.precision?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono">{topK.k_20?.recall?.toFixed(3) || '—'}</td>
                    <td className="px-3 py-2 text-center font-mono font-bold text-legal-burgundy">{topK.k_20?.f1?.toFixed(3) || '—'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* ============================================================== */}
          {/* SECTION 4: PER-DOCUMENT BENCHMARK RESULTS TABLE                 */}
          {/* ============================================================== */}
          <div className="bg-white border border-legal-border shadow-xs overflow-hidden">
            <div className="p-4 bg-legal-parchment border-b border-legal-border flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="font-serif font-bold text-sm text-legal-navy uppercase tracking-wider">
                  Document-Level Evaluation Breakdown
                </h3>
                <p className="text-[11px] text-legal-charcoal-muted mt-0.5">
                  Granular performance across the 12 curated legal benchmark documents.
                </p>
              </div>

              {/* Sort By Dropdown */}
              <div className="flex items-center space-x-2 text-xs">
                <span className="font-semibold text-legal-charcoal uppercase tracking-wider text-[11px]">
                  Sort By:
                </span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-white border border-legal-border px-2.5 py-1 text-xs text-legal-navy font-semibold focus:outline-none"
                >
                  <option value="doc_id">Document ID</option>
                  <option value="kw_f1">Keyword F1 (High to Low)</option>
                  <option value="ent_f1">Entity F1 (High to Low)</option>
                  <option value="latency">Processing Latency</option>
                </select>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-legal-border text-left">
                <thead className="bg-legal-navy text-white text-[10px] uppercase font-semibold">
                  <tr>
                    <th className="px-4 py-3">Document Title &amp; ID</th>
                    <th className="px-4 py-3">Genre</th>
                    <th className="px-4 py-3 text-center">Words</th>
                    <th className="px-4 py-3 text-center">Keyword P / R / F1</th>
                    <th className="px-4 py-3 text-center">Entity P / R / F1</th>
                    <th className="px-4 py-3 text-right">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-legal-border text-xs bg-white">
                  {sortedDocuments.map((doc) => (
                    <tr key={doc.document_id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-4 py-3 max-w-xs">
                        <div className="font-semibold text-legal-navy truncate">{doc.title}</div>
                        <div className="text-[10px] text-slate-400 font-mono">#{doc.document_id}</div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className="text-[11px] px-2 py-0.5 bg-slate-100 border border-slate-200 text-slate-700">
                          {doc.genre}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center font-mono text-[11px]">
                        {doc.word_count}
                      </td>
                      <td className="px-4 py-3 text-center font-mono text-[11px]">
                        <span className="text-slate-600">{doc.keyword_metrics?.precision?.toFixed(2)}</span>
                        <span className="text-slate-300 mx-1">/</span>
                        <span className="text-slate-600">{doc.keyword_metrics?.recall?.toFixed(2)}</span>
                        <span className="text-slate-300 mx-1">/</span>
                        <span className="font-bold text-legal-navy">{doc.keyword_metrics?.f1?.toFixed(2)}</span>
                      </td>
                      <td className="px-4 py-3 text-center font-mono text-[11px]">
                        <span className="text-slate-600">{doc.entity_metrics?.precision?.toFixed(2)}</span>
                        <span className="text-slate-300 mx-1">/</span>
                        <span className="text-slate-600">{doc.entity_metrics?.recall?.toFixed(2)}</span>
                        <span className="text-slate-300 mx-1">/</span>
                        <span className="font-bold text-legal-burgundy">{doc.entity_metrics?.f1?.toFixed(2)}</span>
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-[11px] text-slate-600">
                        {doc.processing_time_ms} ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* ============================================================== */}
          {/* SECTION 5: SYSTEMATIC ERROR ANALYSIS INSPECTOR                  */}
          {/* ============================================================== */}
          {errors && (
            <div className="bg-white border border-legal-border shadow-xs p-5 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-legal-border pb-3">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-legal-burgundy" />
                  <h3 className="font-serif font-bold text-sm text-legal-navy uppercase tracking-wider">
                    ASTMA Systematic Error Classification
                  </h3>
                </div>

                {/* Error Tab Switcher */}
                <div className="flex space-x-1 text-xs">
                  <button
                    onClick={() => setErrorTab('keywords')}
                    className={`px-3 py-1 font-semibold uppercase text-[11px] border transition-colors ${
                      errorTab === 'keywords'
                        ? 'bg-legal-navy text-white border-legal-navy'
                        : 'bg-slate-50 text-legal-charcoal border-legal-border hover:bg-slate-100'
                    }`}
                  >
                    Keyword Errors ({errors.false_positive_keywords_count + errors.false_negative_keywords_count})
                  </button>
                  <button
                    onClick={() => setErrorTab('entities')}
                    className={`px-3 py-1 font-semibold uppercase text-[11px] border transition-colors ${
                      errorTab === 'entities'
                        ? 'bg-legal-navy text-white border-legal-navy'
                        : 'bg-slate-50 text-legal-charcoal border-legal-border hover:bg-slate-100'
                    }`}
                  >
                    Entity Errors ({errors.false_positive_entities_count + errors.false_negative_entities_count})
                  </button>
                  <button
                    onClick={() => setErrorTab('mismatches')}
                    className={`px-3 py-1 font-semibold uppercase text-[11px] border transition-colors ${
                      errorTab === 'mismatches'
                        ? 'bg-legal-navy text-white border-legal-navy'
                        : 'bg-slate-50 text-legal-charcoal border-legal-border hover:bg-slate-100'
                    }`}
                  >
                    Category Mismatches ({errors.type_mismatches_count})
                  </button>
                </div>
              </div>

              {errorTab === 'keywords' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* False Positives */}
                  <div className="p-4 bg-slate-50 border border-legal-border space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs uppercase tracking-wider text-rose-800">
                        False Positive Keywords (Spurious)
                      </span>
                      <span className="font-mono text-[10px] text-slate-500">
                        {errors.false_positive_keywords_count} total
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Terms extracted by the candidate scoring pipeline that were not selected in the curated gold standard:
                    </p>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {errors.sample_fp_keywords?.slice(0, 15).map((item, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-white border border-rose-200 text-rose-900 text-[11px] font-mono">
                          {item.keyword}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* False Negatives */}
                  <div className="p-4 bg-slate-50 border border-legal-border space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs uppercase tracking-wider text-amber-800">
                        False Negative Keywords (Omitted)
                      </span>
                      <span className="font-mono text-[10px] text-slate-500">
                        {errors.false_negative_keywords_count} total
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Gold-standard keywords omitted by the top-K ranking threshold:
                    </p>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {errors.sample_fn_keywords?.slice(0, 15).map((item, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-white border border-amber-200 text-amber-900 text-[11px] font-mono">
                          {item.keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {errorTab === 'entities' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* False Positive Entities */}
                  <div className="p-4 bg-slate-50 border border-legal-border space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs uppercase tracking-wider text-rose-800">
                        False Positive Entities
                      </span>
                      <span className="font-mono text-[10px] text-slate-500">
                        {errors.false_positive_entities_count} total
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Extracted entities whose text mention was not recognized in the gold dataset:
                    </p>
                    <div className="space-y-1 pt-1 max-h-48 overflow-y-auto">
                      {errors.sample_fp_entities?.slice(0, 10).map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between text-[11px] font-mono bg-white p-1.5 border border-slate-200">
                          <span className="text-legal-navy font-semibold truncate max-w-xs">{item.text}</span>
                          <span className="text-slate-500 text-[10px] uppercase">[{item.type}]</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* False Negative Entities */}
                  <div className="p-4 bg-slate-50 border border-legal-border space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs uppercase tracking-wider text-amber-800">
                        False Negative Entities
                      </span>
                      <span className="font-mono text-[10px] text-slate-500">
                        {errors.false_negative_entities_count} total
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Gold entities missed entirely by the statistical NER and regex engines:
                    </p>
                    <div className="space-y-1 pt-1 max-h-48 overflow-y-auto">
                      {errors.sample_fn_entities?.slice(0, 10).map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between text-[11px] font-mono bg-white p-1.5 border border-slate-200">
                          <span className="text-amber-900 font-semibold truncate max-w-xs">{item.text}</span>
                          <span className="text-slate-500 text-[10px] uppercase">[{item.type}]</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {errorTab === 'mismatches' && (
                <div className="p-4 bg-slate-50 border border-legal-border space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs uppercase tracking-wider text-purple-900">
                      Entity Category / Semantic Type Mismatches
                    </span>
                    <span className="font-mono text-[10px] text-slate-500">
                      {errors.type_mismatches_count} instances
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600">
                    Instances where the text span boundary was successfully extracted, but assigned an incorrect semantic category (e.g. general <span className="font-mono">ORGANIZATION</span> vs specific <span className="font-mono">COURT</span>):
                  </p>
                  <div className="space-y-1.5">
                    {errors.sample_type_mismatches?.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between text-xs bg-white p-2 border border-slate-200">
                        <span className="font-semibold text-legal-navy">{item.text}</span>
                        <div className="flex items-center space-x-2 font-mono text-[11px]">
                          <span className="text-rose-700 font-bold bg-rose-50 px-1.5 py-0.5 border border-rose-200">
                            Pred: {item.predicted_type}
                          </span>
                          <span className="text-slate-400">→</span>
                          <span className="text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 border border-emerald-200">
                            Gold: {item.gold_types?.join(', ')}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Academic Methodology & Integrity Note */}
          <div className="p-4 bg-white border-l-4 border-legal-gold border-r border-t border-b border-legal-border text-xs text-legal-charcoal space-y-1.5 shadow-xs">
            <span className="font-bold text-legal-navy uppercase tracking-wider flex items-center space-x-1.5">
              <Info className="w-4 h-4 text-legal-gold" />
              <span>Academic Integrity &amp; ASTMA Information Retrieval Methodology</span>
            </span>
            <p className="text-[11px] leading-relaxed text-legal-charcoal-muted">
              All reported evaluation figures reflect exact execution against the 12-document curated benchmark dataset.
              Keyword extraction applies deterministic rank fusion (0.40 TF-IDF + 0.35 RAKE + 0.25 Statutory Lexicon).
              NER utilizes a hybrid architecture merging spaCy statistical predictions with deterministic regular expression grammars and legal gazetteers.
              Scores are unmanipulated and represent genuine retrieval performance under exact-match criteria.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
