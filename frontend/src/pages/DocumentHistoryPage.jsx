import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  FileText, 
  Search, 
  RotateCw, 
  Download, 
  Plus, 
  ArrowRight,
  Eye,
  Filter,
  ArrowUpDown,
  BookOpen,
  Loader2
} from 'lucide-react';
import { listDocuments, listDocumentAnalyses, downloadDocumentFile, analyzeDocument } from '../services/api';
import { useToast } from '../context/ToastContext';

export default function DocumentHistoryPage({ 
  onNavigateToViewer, 
  onNavigateToResults, 
  onNavigateToIntake 
}) {
  const { showToast } = useToast();
  const [documents, setDocuments] = useState([]);
  const [docAnalyses, setDocAnalyses] = useState({}); // docId -> latest AnalysisRun
  const [isLoading, setIsLoading] = useState(true);
  const [analyzingDocId, setAnalyzingDocId] = useState(null);
  const [error, setError] = useState(null);

  // Filters & Sorting
  const [searchTerm, setSearchTerm] = useState('');
  const [formatFilter, setFormatFilter] = useState('ALL'); // 'ALL' | 'PDF' | 'DOCX'
  const [sortBy, setSortBy] = useState('recent'); // 'recent' | 'name' | 'analyzed'

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const docList = await listDocuments();
      setDocuments(docList || []);

      const analysisMap = {};
      await Promise.allSettled(
        (docList || []).map(async (doc) => {
          try {
            const runs = await listDocumentAnalyses(doc.id);
            if (runs && runs.length > 0) {
              analysisMap[doc.id] = runs[0];
            }
          } catch (e) {
            // Ignore missing analyses
          }
        })
      );
      setDocAnalyses(analysisMap);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load documents repository.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

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

  // Filter and sort
  const filteredDocuments = useMemo(() => {
    let result = [...documents];

    // Search query
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      result = result.filter(d => 
        (d.filename || '').toLowerCase().includes(q) ||
        String(d.id).includes(q)
      );
    }

    // Format filter
    if (formatFilter !== 'ALL') {
      result = result.filter(d => (d.file_type || '').toUpperCase() === formatFilter);
    }

    // Sort order
    result.sort((a, b) => {
      if (sortBy === 'recent') {
        const dateA = new Date(a.created_at || a.uploaded_at || 0).getTime();
        const dateB = new Date(b.created_at || b.uploaded_at || 0).getTime();
        return dateB - dateA;
      }
      if (sortBy === 'name') {
        return (a.filename || '').localeCompare(b.filename || '');
      }
      if (sortBy === 'analyzed') {
        const hasAnalysisA = docAnalyses[a.id] ? 1 : 0;
        const hasAnalysisB = docAnalyses[b.id] ? 1 : 0;
        return hasAnalysisB - hasAnalysisA;
      }
      return 0;
    });

    return result;
  }, [documents, docAnalyses, searchTerm, formatFilter, sortBy]);

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

  const handleDownload = async (docId, filename) => {
    try {
      await downloadDocumentFile(docId, filename);
      showToast('Document downloaded successfully.', 'success');
    } catch (err) {
      showToast('Failed to download document file.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl text-midnight font-bold tracking-tight">
            Documents
          </h1>
          <p className="text-[14px] text-charcoal-muted mt-0.5">
            Institutional repository of processed legal agreements, briefs, and corporate filings.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="p-2 border border-line bg-white hover:bg-ivory-subtle text-charcoal transition-colors"
            title="Refresh list"
            aria-label="Refresh list"
          >
            <RotateCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>

          {onNavigateToIntake && (
            <button
              onClick={onNavigateToIntake}
              className="btn-primary py-2 px-4 text-[13px]"
            >
              <Plus className="w-4 h-4 text-gold-light" />
              <span>+ Analyze Document</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-line p-4 shadow-subtle flex flex-col md:flex-row items-center justify-between gap-4 text-[13px]">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-charcoal-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search documents by title..."
            className="input-clean pl-9 py-1.5 text-[13px]"
          />
        </div>

        {/* Format Filter & Sort Controls */}
        <div className="flex flex-wrap items-center gap-4 w-full md:w-auto justify-between md:justify-end">
          {/* Format pills */}
          <div className="flex items-center space-x-1 border border-line p-0.5 bg-ivory">
            {['ALL', 'PDF', 'DOCX'].map((fmt) => (
              <button
                key={fmt}
                onClick={() => setFormatFilter(fmt)}
                className={`px-3 py-1 text-[12px] font-medium transition-colors ${
                  formatFilter === fmt
                    ? 'bg-midnight text-white'
                    : 'text-charcoal hover:bg-white'
                }`}
              >
                {fmt}
              </button>
            ))}
          </div>

          {/* Sort By */}
          <div className="flex items-center space-x-2">
            <span className="text-[12px] text-charcoal-muted">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-white border border-line px-2.5 py-1 text-[12px] text-midnight font-medium focus:outline-none"
            >
              <option value="recent">Most Recent</option>
              <option value="name">Document Title</option>
              <option value="analyzed">Analysis Status</option>
            </select>
          </div>
        </div>
      </div>

      {/* Repository Table / Compact Rows */}
      <div className="bg-white border border-line shadow-subtle overflow-hidden">
        {isLoading ? (
          <div className="p-16 text-center space-y-3">
            <div className="w-8 h-8 border-2 border-midnight border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-[14px] font-medium text-midnight">Loading document archive...</p>
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="p-16 text-center space-y-3 max-w-md mx-auto">
            <BookOpen className="w-10 h-10 text-charcoal-muted/40 mx-auto" />
            <h3 className="font-display text-lg text-midnight font-bold">No documents match criteria</h3>
            <p className="text-[13px] text-charcoal-muted">
              {searchTerm ? 'Try adjusting your search query or format filter.' : 'Upload your first contract or brief to begin.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[13px]">
              <thead className="bg-ivory border-b border-line text-charcoal-muted font-semibold text-[11px] uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-5">Document</th>
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">Date Added</th>
                  <th className="py-3 px-4">Word Count</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line text-charcoal">
                {filteredDocuments.map((doc) => {
                  const analysis = docAnalyses[doc.id];
                  const isAnalyzed = Boolean(analysis && analysis.status === 'completed');

                  return (
                    <tr key={doc.id} className="hover:bg-ivory/60 transition-colors">
                      <td className="py-3.5 px-5">
                        <div className="font-semibold text-midnight text-[14px] flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-midnight shrink-0" />
                          <span className="truncate max-w-sm">{doc.filename}</span>
                        </div>
                      </td>

                      <td className="py-3.5 px-4 font-mono uppercase text-charcoal-muted text-[12px]">
                        {doc.file_type || 'PDF'}
                      </td>

                      <td className="py-3.5 px-4 text-charcoal-muted text-[13px]">
                        {formatDate(doc.created_at || doc.uploaded_at)}
                      </td>

                      <td className="py-3.5 px-4 text-charcoal text-[13px]">
                        {doc.word_count?.toLocaleString() || 0}
                      </td>

                      <td className="py-3.5 px-4">
                        {isAnalyzed ? (
                          <span className="inline-flex items-center px-2 py-0.5 text-[11px] font-medium bg-legalgreen-subtle text-legalgreen border border-legalgreen-border">
                            Analyzed
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 text-[11px] font-medium bg-ivory text-charcoal-muted border border-line">
                            Uploaded
                          </span>
                        )}
                      </td>

                      <td className="py-3.5 px-5 text-right space-x-2">
                        {isAnalyzed && onNavigateToResults ? (
                          <button
                            onClick={() => onNavigateToResults(analysis.id, doc.id)}
                            className="btn-primary py-1 px-3 text-[12px]"
                          >
                            Open
                          </button>
                        ) : (
                          <button
                            onClick={() => handleRunAnalysis(doc.id)}
                            disabled={analyzingDocId === doc.id}
                            className="btn-primary py-1 px-3 text-[12px] inline-flex items-center space-x-1"
                            title="Start Document Intelligence Analysis"
                          >
                            {analyzingDocId === doc.id ? (
                              <>
                                <Loader2 className="w-3 h-3 animate-spin text-gold-light" />
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
                            className="btn-secondary py-1 px-2.5 text-[12px]"
                            title="View Document"
                          >
                            View
                          </button>
                        )}

                        <button
                          onClick={() => handleDownload(doc.id, doc.filename)}
                          className="p-1 border border-line text-charcoal-muted hover:text-midnight hover:bg-white transition-colors inline-flex items-center"
                          title="Download Original"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
