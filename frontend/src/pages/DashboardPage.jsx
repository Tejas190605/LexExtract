import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  FileText, 
  ArrowRight, 
  Plus, 
  RotateCw, 
  Layers, 
  FileCheck, 
  Scale, 
  AlertTriangle, 
  Search,
  Calendar,
  Sparkles,
  BookOpen,
  Loader2
} from 'lucide-react';
import { listDocuments, listDocumentAnalyses, getDocumentClauses, analyzeDocument } from '../services/api';
import { useToast } from '../context/ToastContext';

export default function DashboardPage({ 
  onNavigateToIntake, 
  onNavigateToViewer, 
  onNavigateToResults,
  onNavigateToHistory,
  onNavigate 
}) {
  const { showToast } = useToast();
  const [documents, setDocuments] = useState([]);
  const [docAnalyses, setDocAnalyses] = useState({}); // docId -> latest AnalysisRun
  const [docClausesMap, setDocClausesMap] = useState({}); // docId -> clauses list
  const [isLoading, setIsLoading] = useState(true);
  const [analyzingDocId, setAnalyzingDocId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Handle upload CTA navigation safely
  const handleOpenUpload = () => {
    if (onNavigateToIntake) {
      onNavigateToIntake();
    } else if (onNavigate) {
      onNavigate('new_analysis');
    }
  };

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const docs = await listDocuments();
      setDocuments(docs || []);

      const analysisMap = {};
      const clausesMap = {};

      await Promise.allSettled(
        (docs || []).map(async (doc) => {
          try {
            const runs = await listDocumentAnalyses(doc.id);
            if (runs && runs.length > 0) {
              const latest = runs[0];
              analysisMap[doc.id] = latest;

              // Check clauses / attention areas for analyzed docs
              try {
                const cData = await getDocumentClauses(latest.id);
                if (cData && cData.clauses) {
                  clausesMap[doc.id] = cData.clauses;
                }
              } catch (cErr) {
                // Non-critical
              }
            }
          } catch (e) {
            // Ignore missing analyses
          }
        })
      );

      setDocAnalyses(analysisMap);
      setDocClausesMap(clausesMap);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle running analysis on an unanalyzed document
  const handleRunAnalysis = async (docId) => {
    if (analyzingDocId) return;
    setAnalyzingDocId(docId);
    try {
      const res = await analyzeDocument(docId);
      showToast('Document analyzed successfully.', 'success');
      const analysisId = res.analysis_id || res.id;
      if (onNavigateToResults) {
        onNavigateToResults(analysisId, docId);
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Document analysis failed. Please try again.';
      showToast(msg, 'error');
    } finally {
      setAnalyzingDocId(null);
    }
  };

  // Aggregate metrics
  const stats = useMemo(() => {
    const totalDocs = documents.length;
    let totalKeywords = 0;
    let totalEntities = 0;
    let totalAttention = 0;

    Object.values(docAnalyses).forEach((run) => {
      totalKeywords += run.total_keywords || 0;
      totalEntities += run.total_entities || 0;
    });

    Object.values(docClausesMap).forEach((clauses) => {
      // High or medium attention clauses
      const flagged = clauses.filter(c => 
        c.status === 'Found' && 
        ['Indemnification', 'Liability', 'Non-Compete / Restriction', 'Arbitration / Dispute Resolution'].includes(c.clause_type)
      );
      totalAttention += flagged.length;
    });

    return {
      totalDocs,
      totalKeywords,
      totalEntities,
      totalAttention
    };
  }, [documents, docAnalyses, docClausesMap]);

  // Filter recent documents
  const filteredDocs = useMemo(() => {
    let result = [...documents];
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      result = result.filter(d => 
        (d.filename || '').toLowerCase().includes(q) ||
        String(d.id).includes(q)
      );
    }
    result.sort((a, b) => {
      const dateA = new Date(a.created_at || a.uploaded_at || 0).getTime();
      const dateB = new Date(b.created_at || b.uploaded_at || 0).getTime();
      return dateB - dateA;
    });
    return result;
  }, [documents, searchTerm]);

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-US', {
        month: 'short',
        day: '2-digit',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-8">
      {/* ============================================================== */}
      {/* 1. HERO SECTION: LEGAL DOCUMENT INTELLIGENCE                   */}
      {/* ============================================================== */}
      <section className="bg-white border border-line p-8 sm:p-10 shadow-subtle relative overflow-hidden">
        {/* Subtle decorative background watermarks */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-ivory-subtle/70 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
        
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="flex items-center space-x-2 text-gold-dark text-[12px] font-semibold tracking-wider uppercase">
            <Scale className="w-4 h-4 text-gold-dark" />
            <span>Legal Document Intelligence</span>
          </div>

          <h1 className="font-display text-3xl sm:text-4xl text-midnight font-bold tracking-tight leading-tight">
            Turn lengthy legal documents into structured, searchable information.
          </h1>

          <p className="text-[16px] text-charcoal-body leading-relaxed max-w-2xl">
            Extract key terms, contractual entities, clauses, dates, financial commitments, and high-priority attention areas in seconds.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={handleOpenUpload}
              className="btn-primary py-3 px-6 text-[15px] font-semibold"
            >
              <Plus className="w-4 h-4 text-gold-light" />
              <span>+ Analyze Document</span>
            </button>

            {onNavigateToHistory && (
              <button
                onClick={onNavigateToHistory}
                className="btn-secondary py-3 px-5 text-[14px]"
              >
                <span>Browse Documents</span>
                <ArrowRight className="w-3.5 h-3.5 text-charcoal-muted" />
              </button>
            )}
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 2. COMPACT HORIZONTAL METRIC STRIP                             */}
      {/* ============================================================== */}
      <section className="bg-white border border-line shadow-subtle divide-y sm:divide-y-0 sm:divide-x divide-line grid grid-cols-2 sm:grid-cols-4">
        <div className="p-5 sm:p-6 flex items-center space-x-4">
          <div className="w-10 h-10 rounded bg-midnight/5 flex items-center justify-center shrink-0">
            <FileText className="w-5 h-5 text-midnight" />
          </div>
          <div>
            <span className="text-[12px] text-charcoal-muted uppercase tracking-wider block font-medium">
              Documents Analyzed
            </span>
            <span className="text-2xl font-bold font-sans text-midnight mt-0.5 block">
              {stats.totalDocs}
            </span>
          </div>
        </div>

        <div className="p-5 sm:p-6 flex items-center space-x-4">
          <div className="w-10 h-10 rounded bg-midnight/5 flex items-center justify-center shrink-0">
            <Sparkles className="w-5 h-5 text-midnight" />
          </div>
          <div>
            <span className="text-[12px] text-charcoal-muted uppercase tracking-wider block font-medium">
              Keywords Extracted
            </span>
            <span className="text-2xl font-bold font-sans text-midnight mt-0.5 block">
              {stats.totalKeywords}
            </span>
          </div>
        </div>

        <div className="p-5 sm:p-6 flex items-center space-x-4">
          <div className="w-10 h-10 rounded bg-midnight/5 flex items-center justify-center shrink-0">
            <Layers className="w-5 h-5 text-midnight" />
          </div>
          <div>
            <span className="text-[12px] text-charcoal-muted uppercase tracking-wider block font-medium">
              Entities Identified
            </span>
            <span className="text-2xl font-bold font-sans text-midnight mt-0.5 block">
              {stats.totalEntities}
            </span>
          </div>
        </div>

        <div className="p-5 sm:p-6 flex items-center space-x-4">
          <div className="w-10 h-10 rounded bg-crimson/5 flex items-center justify-center shrink-0">
            <AlertTriangle className="w-5 h-5 text-crimson" />
          </div>
          <div>
            <span className="text-[12px] text-charcoal-muted uppercase tracking-wider block font-medium">
              Attention Areas
            </span>
            <span className="text-2xl font-bold font-sans text-crimson mt-0.5 block">
              {stats.totalAttention}
            </span>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 3. RECENT ANALYSES SECTION                                     */}
      {/* ============================================================== */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-midnight tracking-tight">
              Recent Analyses
            </h2>
            <p className="text-[13px] text-charcoal-muted mt-0.5">
              Review and inspect recently processed legal briefs, agreements, and corporate filings.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            {documents.length > 3 && (
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-charcoal-muted absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Filter documents..."
                  className="input-clean pl-8 py-1.5 text-xs w-48 sm:w-60"
                />
              </div>
            )}

            <button
              onClick={loadData}
              disabled={isLoading}
              className="p-2 border border-line bg-white hover:bg-ivory-subtle text-charcoal transition-colors"
              title="Refresh repository"
              aria-label="Refresh repository"
            >
              <RotateCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Content list or Polished Empty State */}
        {isLoading ? (
          <div className="p-16 text-center bg-white border border-line shadow-subtle space-y-3">
            <div className="w-8 h-8 border-2 border-midnight border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-[14px] font-medium text-midnight">Loading legal workspace...</p>
          </div>
        ) : filteredDocs.length === 0 ? (
          /* Polished Empty State */
          <div className="p-16 text-center bg-white border border-line shadow-subtle space-y-4 max-w-xl mx-auto my-6">
            <div className="w-14 h-14 rounded-full bg-ivory-subtle border border-line flex items-center justify-center mx-auto text-charcoal-muted">
              <Scale className="w-7 h-7 text-gold-dark" />
            </div>
            <div className="space-y-1.5">
              <h3 className="font-display text-xl text-midnight font-bold">
                Your legal workspace is empty
              </h3>
              <p className="text-[14px] text-charcoal-body leading-relaxed max-w-md mx-auto">
                Upload your first contract or brief to begin extracting useful legal terms, obligations, entities, and risk clauses automatically.
              </p>
            </div>
            <button
              onClick={handleOpenUpload}
              className="btn-primary py-2.5 px-5 text-[14px]"
            >
              <Plus className="w-4 h-4 text-gold-light" />
              <span>Analyze First Document</span>
            </button>
          </div>
        ) : (
          /* Compact, visually rich document rows */
          <div className="bg-white border border-line shadow-subtle divide-y divide-line">
            {filteredDocs.slice(0, 8).map((doc) => {
              const analysis = docAnalyses[doc.id];
              const isAnalyzed = Boolean(analysis && analysis.status === 'completed');
              const clauses = docClausesMap[doc.id] || [];
              const attentionCount = clauses.filter(c => 
                c.status === 'Found' && 
                ['Indemnification', 'Liability', 'Non-Compete / Restriction'].includes(c.clause_type)
              ).length;

              return (
                <div 
                  key={doc.id}
                  className="p-4 sm:p-5 hover:bg-ivory/50 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  {/* Left: Document info */}
                  <div className="flex items-start space-x-3.5">
                    <div className="w-9 h-9 rounded bg-midnight/5 border border-line flex items-center justify-center shrink-0 mt-0.5">
                      <FileText className="w-5 h-5 text-midnight" />
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center space-x-2 flex-wrap">
                        <span className="font-semibold text-[15px] text-midnight">
                          {doc.filename}
                        </span>
                        <span className="px-1.5 py-0.5 text-[10px] font-mono uppercase bg-ivory-subtle text-charcoal-muted border border-line">
                          {doc.file_type || 'PDF'}
                        </span>
                        {isAnalyzed ? (
                          <span className="px-2 py-0.5 text-[11px] font-medium bg-legalgreen-subtle text-legalgreen border border-legalgreen-border">
                            Analyzed
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 text-[11px] font-medium bg-ivory-subtle text-charcoal-muted border border-line">
                            Uploaded
                          </span>
                        )}
                      </div>

                      <div className="flex items-center space-x-3 text-[12px] text-charcoal-muted">
                        <span>{formatDate(doc.created_at || doc.uploaded_at)}</span>
                        <span>•</span>
                        <span>{doc.word_count?.toLocaleString() || 0} words</span>
                        <span>•</span>
                        <span>{doc.page_count || 1} {doc.page_count === 1 ? 'page' : 'pages'}</span>
                      </div>
                    </div>
                  </div>

                  {/* Middle: Rich Summary Tags */}
                  <div className="flex flex-wrap items-center gap-2 text-[12px]">
                    {isAnalyzed ? (
                      <>
                        <span className="px-2 py-1 bg-ivory border border-line text-charcoal font-medium">
                          {analysis.total_keywords ?? 0} Keywords
                        </span>
                        <span className="px-2 py-1 bg-ivory border border-line text-charcoal font-medium">
                          {analysis.total_entities ?? 0} Entities
                        </span>
                        {attentionCount > 0 && (
                          <span className="px-2 py-1 bg-legalamber-subtle border border-legalamber-border text-legalamber font-semibold flex items-center space-x-1">
                            <AlertTriangle className="w-3 h-3" />
                            <span>{attentionCount} Attention Areas</span>
                          </span>
                        )}
                      </>
                    ) : (
                      <span className="text-[12px] text-charcoal-muted italic">
                        Ready for extraction
                      </span>
                    )}
                  </div>

                  {/* Right: Actions */}
                  <div className="flex items-center space-x-2 shrink-0 self-end md:self-center">
                    {isAnalyzed && onNavigateToResults ? (
                      <button
                        onClick={() => onNavigateToResults(analysis.id, doc.id)}
                        className="btn-primary py-1.5 px-3.5 text-[13px]"
                      >
                        <span>Open Analysis</span>
                        <ArrowRight className="w-3.5 h-3.5 text-gold-light" />
                      </button>
                    ) : (
                      <button
                        onClick={() => handleRunAnalysis(doc.id)}
                        disabled={analyzingDocId === doc.id}
                        className="btn-primary py-1.5 px-3.5 text-[13px] flex items-center space-x-1.5"
                        title="Start Document Intelligence Analysis"
                      >
                        {analyzingDocId === doc.id ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 animate-spin text-gold-light" />
                            <span>Analyzing...</span>
                          </>
                        ) : (
                          <span>Analyze</span>
                        )}
                      </button>
                    )}

                    {onNavigateToViewer && (
                      <button
                        onClick={() => onNavigateToViewer(doc.id)}
                        className="btn-secondary py-1.5 px-3 text-[13px]"
                        title="View Document"
                      >
                        View
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
