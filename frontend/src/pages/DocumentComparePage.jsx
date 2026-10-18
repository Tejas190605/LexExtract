import React, { useState, useEffect } from 'react';
import { 
  GitCompare, 
  ArrowRight, 
  AlertCircle, 
  DollarSign, 
  Calendar, 
  Scale, 
  CheckCircle2, 
  Plus, 
  Minus, 
  RefreshCw,
  FileText,
  Clock,
  Layers,
  Sparkles
} from 'lucide-react';
import { listDocuments, compareDocuments } from '../services/api';
import { useToast } from '../context/ToastContext';

// Helper: Render redline word tokens with visual highlight
function renderRedlineTokens(tokens, fallbackText, side) {
  if (tokens && tokens.length > 0) {
    return (
      <p className="font-serif text-[13px] leading-relaxed">
        {tokens.map((tok, idx) => {
          if (tok.type === 'equal') {
            return <span key={idx} className={side === 'a' ? 'text-charcoal' : 'text-midnight'}>{tok.text} </span>;
          }
          if (side === 'a') {
            return (
              <del
                key={idx}
                className="bg-legalred-subtle text-legalred line-through decoration-legalred font-semibold px-1 py-0.5 rounded border border-legalred-border inline-block mx-0.5"
              >
                {tok.text}
              </del>
            );
          } else {
            return (
              <ins
                key={idx}
                className="bg-legalgreen-subtle text-legalgreen font-bold no-underline px-1 py-0.5 rounded border border-legalgreen-border ring-1 ring-legalgreen/30 inline-block mx-0.5"
              >
                {tok.text}
              </ins>
            );
          }
        })}
      </p>
    );
  }

  return (
    <p className={`font-serif text-[13px] leading-relaxed ${side === 'a' ? 'text-charcoal' : 'text-midnight font-medium'}`}>
      {fallbackText}
    </p>
  );
}

export default function DocumentComparePage({ onNavigateToViewer, onNavigateToIntake }) {
  const { showToast } = useToast();
  const [documents, setDocuments] = useState([]);
  const [docAId, setDocAId] = useState('');
  const [docBId, setDocBId] = useState('');

  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  // Fetch user's documents
  useEffect(() => {
    let isMounted = true;
    const fetchDocs = async () => {
      try {
        const docs = await listDocuments();
        if (isMounted) {
          setDocuments(docs || []);
          if (docs && docs.length >= 2) {
            setDocAId(docs[0].id);
            setDocBId(docs[1].id);
          } else if (docs && docs.length === 1) {
            setDocAId(docs[0].id);
          }
        }
      } catch (err) {
        if (isMounted) {
          setErrorMessage('Failed to load user documents for comparison.');
        }
      } finally {
        if (isMounted) {
          setIsLoadingDocs(false);
        }
      }
    };
    fetchDocs();
    return () => { isMounted = false; };
  }, []);

  const handleCompare = async () => {
    if (!docAId || !docBId) {
      setErrorMessage('Please select both Document A and Document B to compare.');
      return;
    }
    if (Number(docAId) === Number(docBId)) {
      setErrorMessage('Please select two distinct documents for comparative diff analysis.');
      return;
    }

    setIsComparing(true);
    setErrorMessage(null);
    try {
      const result = await compareDocuments(Number(docAId), Number(docBId));
      setComparisonResult(result);
      showToast('Document comparison completed.', 'success');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Document comparison failed.';
      setErrorMessage(detail);
      showToast(detail, 'error');
    } finally {
      setIsComparing(false);
    }
  };

  const docA = documents.find(d => Number(d.id) === Number(docAId));
  const docB = documents.find(d => Number(d.id) === Number(docBId));

  // Extract clause comparison items
  const clauseList = comparisonResult?.clause_comparison || comparisonResult?.clause_comp || [];
  const modifiedClauses = clauseList.filter(c => c.status === 'MODIFIED');
  const addedClauses = clauseList.filter(c => c.status === 'ADDED');
  const removedClauses = clauseList.filter(c => c.status === 'REMOVED');
  const allClauseChanges = modifiedClauses.flatMap(c => (c.changes || []).map(ch => ({ ...ch, clause_type: c.clause_type })));

  // Commercial terms (money & dates)
  const moneyData = comparisonResult?.money_comparison || comparisonResult?.money_comp || {};
  const addedMoney = moneyData.added || [];
  const removedMoney = moneyData.removed || [];

  const dateData = comparisonResult?.date_comparison || comparisonResult?.date_comp || {};
  const addedDates = dateData.added || [];
  const removedDates = dateData.removed || [];

  // Entities & Keywords diff
  const entData = comparisonResult?.entity_comparison || comparisonResult?.ent_comp || {};
  const addedEntities = entData.added || [];
  const removedEntities = entData.removed || [];

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-display text-3xl sm:text-4xl text-midnight font-bold tracking-tight">
          Compare Legal Documents
        </h1>
        <p className="text-[15px] text-charcoal-muted mt-1">
          Perform side-by-side legal redline comparison across clauses, deadlines, financial commitments, and parties.
        </p>
      </div>

      {/* Empty State (< 2 documents) vs Selection Workspace */}
      {!isLoadingDocs && documents.length < 2 ? (
        <div className="bg-white border border-line p-12 sm:p-16 text-center shadow-subtle space-y-5 max-w-xl mx-auto my-6">
          <div className="w-14 h-14 rounded-full bg-ivory-subtle border border-line flex items-center justify-center mx-auto text-charcoal-muted">
            <GitCompare className="w-7 h-7 text-midnight" />
          </div>
          <div className="space-y-2">
            <h3 className="font-display text-xl text-midnight font-bold">
              Document comparison requires at least two documents.
            </h3>
            <p className="text-[14px] text-charcoal-body leading-relaxed max-w-md mx-auto">
              Upload a baseline agreement and a revised version to identify clause and term changes.
            </p>
          </div>
          {onNavigateToIntake && (
            <button
              onClick={onNavigateToIntake}
              className="btn-primary py-2.5 px-6 text-[14px]"
            >
              <Plus className="w-4 h-4 text-gold-light" />
              <span>+ Upload Document</span>
            </button>
          )}
        </div>
      ) : (
        /* Document Selection Workspace */
        <div className="bg-white border border-line p-6 sm:p-8 shadow-subtle space-y-6">
          {errorMessage && (
            <div className="p-4 bg-legalred-subtle border border-legalred-border text-legalred text-[13px] flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-legalred" />
              <span>{errorMessage}</span>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-end">
            {/* Document A Selector */}
            <div className="space-y-1.5">
              <label className="text-[12px] font-bold text-midnight uppercase tracking-wider block">
                Document A (Baseline / Reference)
              </label>
              <select
                value={docAId}
                onChange={(e) => setDocAId(e.target.value)}
                className="w-full text-[14px] bg-ivory border border-line p-3 text-midnight font-medium focus:outline-none focus:border-midnight"
              >
                <option value="">Select Document A</option>
                {documents.map((d) => (
                  <option key={d.id} value={d.id} disabled={Number(d.id) === Number(docBId)}>
                    {d.filename} ({d.file_type.toUpperCase()})
                  </option>
                ))}
              </select>
            </div>

            {/* Document B Selector */}
            <div className="space-y-1.5">
              <label className="text-[12px] font-bold text-midnight uppercase tracking-wider block">
                Document B (Counter-proposal / Modified Version)
              </label>
              <select
                value={docBId}
                onChange={(e) => setDocBId(e.target.value)}
                className="w-full text-[14px] bg-ivory border border-line p-3 text-midnight font-medium focus:outline-none focus:border-midnight"
              >
                <option value="">Select Document B</option>
                {documents.map((d) => (
                  <option key={d.id} value={d.id} disabled={Number(d.id) === Number(docAId)}>
                    {d.filename} ({d.file_type.toUpperCase()})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              onClick={handleCompare}
              disabled={isComparing || !docAId || !docBId}
              className="btn-primary py-3 px-7 text-[14px] font-semibold"
            >
              {isComparing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-gold-light" />
                  <span>Generating Redline Diff...</span>
                </>
              ) : (
                <>
                  <GitCompare className="w-4 h-4 text-gold-light" />
                  <span>Compare Documents</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Redline Results */}
      {comparisonResult && (
        <div className="space-y-8 animate-in fade-in">
          
          {/* 1. Comparison Overview Banner */}
          <div className="bg-white border border-line p-6 shadow-subtle flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-charcoal-muted block">
                Comparative Redline Analysis
              </span>
              <div className="flex items-center space-x-2 mt-1 flex-wrap">
                <span className="font-semibold text-midnight text-[16px]">
                  {docA?.filename}
                </span>
                <ArrowRight className="w-4 h-4 text-charcoal-muted shrink-0" />
                <span className="font-semibold text-midnight text-[16px]">
                  {docB?.filename}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-6 text-[13px] shrink-0">
              <div className="text-right">
                <span className="text-[11px] text-charcoal-muted uppercase tracking-wider block">Content Similarity</span>
                <span className="font-bold text-2xl text-midnight font-sans">
                  {comparisonResult.similarity_percentage}%
                </span>
              </div>
              <div className="text-right">
                <span className="text-[11px] text-charcoal-muted uppercase tracking-wider block">Modified Clauses</span>
                <span className="font-bold text-2xl text-crimson font-sans">
                  {modifiedClauses.length}
                </span>
              </div>
            </div>
          </div>

          {/* 2. Key Commercial & Timeline Changes (Financial & Notice Diff) */}
          {(addedMoney.length > 0 || removedMoney.length > 0 || addedDates.length > 0 || removedDates.length > 0 || allClauseChanges.length > 0) && (
            <section className="bg-white border border-line p-6 sm:p-8 shadow-subtle space-y-5">
              <div className="border-b border-line pb-3">
                <h2 className="text-base font-bold text-midnight uppercase tracking-wider">
                  Commercial &amp; Timeline Redline
                </h2>
                <p className="text-[13px] text-charcoal-muted mt-0.5">
                  High-priority financial figures, fee structures, and notice period revisions.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {/* Notice & Clause Revisions */}
                {allClauseChanges.length > 0 && (
                  <div className="p-5 bg-ivory border border-line space-y-3">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-charcoal-muted flex items-center space-x-1.5">
                      <Clock className="w-3.5 h-3.5 text-midnight" />
                      <span>Notice &amp; Term Revisions</span>
                    </span>

                    <div className="space-y-2 pt-1 text-[13px]">
                      {allClauseChanges.map((ch, idx) => (
                        <div key={idx} className="p-2.5 bg-white border border-line space-y-1">
                          <span className="text-[11px] font-bold text-midnight block uppercase tracking-wider">
                            {ch.clause_type}
                          </span>
                          <div className="flex items-center space-x-2 font-mono text-[12px]">
                            <span className="text-legalred line-through font-semibold">{ch.original}</span>
                            <span className="text-charcoal-muted">→</span>
                            <span className="text-legalgreen font-bold">{ch.modified}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Monetary Differences */}
                {(addedMoney.length > 0 || removedMoney.length > 0) && (
                  <div className="p-5 bg-ivory border border-line space-y-3">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-charcoal-muted flex items-center space-x-1.5">
                      <DollarSign className="w-3.5 h-3.5 text-midnight" />
                      <span>Financial Exposure Revisions</span>
                    </span>

                    {removedMoney.length > 0 && addedMoney.length > 0 ? (
                      <div className="space-y-3 pt-1">
                        <div className="grid grid-cols-2 gap-3 text-[13px]">
                          <div className="p-3 bg-legalred-subtle border border-legalred-border">
                            <span className="text-[10px] font-bold text-legalred uppercase block">OLD (Doc A)</span>
                            <span className="font-bold text-charcoal line-through mt-0.5 block">
                              {removedMoney.join(', ')}
                            </span>
                          </div>
                          <div className="p-3 bg-legalgreen-subtle border border-legalgreen-border">
                            <span className="text-[10px] font-bold text-legalgreen uppercase block">NEW (Doc B)</span>
                            <span className="font-bold text-midnight mt-0.5 block">
                              {addedMoney.join(', ')}
                            </span>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-2 text-[13px]">
                        {addedMoney.length > 0 && (
                          <div>
                            <span className="text-[11px] text-charcoal-muted block">Added in Document B:</span>
                            <span className="font-semibold text-legalgreen">{addedMoney.join(', ')}</span>
                          </div>
                        )}
                        {removedMoney.length > 0 && (
                          <div>
                            <span className="text-[11px] text-charcoal-muted block">Removed from Document A:</span>
                            <span className="font-semibold text-legalred line-through">{removedMoney.join(', ')}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* Timeline / Dates Differences */}
                {(addedDates.length > 0 || removedDates.length > 0) && (
                  <div className="p-5 bg-ivory border border-line space-y-3">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-charcoal-muted flex items-center space-x-1.5">
                      <Calendar className="w-3.5 h-3.5 text-midnight" />
                      <span>Dates &amp; Period Modifications</span>
                    </span>

                    {removedDates.length > 0 && addedDates.length > 0 ? (
                      <div className="space-y-3 pt-1">
                        <div className="grid grid-cols-2 gap-3 text-[13px]">
                          <div className="p-3 bg-legalred-subtle border border-legalred-border">
                            <span className="text-[10px] font-bold text-legalred uppercase block">OLD (Doc A)</span>
                            <span className="font-bold text-charcoal line-through mt-0.5 block">
                              {removedDates.join(', ')}
                            </span>
                          </div>
                          <div className="p-3 bg-legalgreen-subtle border border-legalgreen-border">
                            <span className="text-[10px] font-bold text-legalgreen uppercase block">NEW (Doc B)</span>
                            <span className="font-bold text-midnight mt-0.5 block">
                              {addedDates.join(', ')}
                            </span>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-2 text-[13px]">
                        {addedDates.length > 0 && (
                          <div>
                            <span className="text-[11px] text-charcoal-muted block">Added in Document B:</span>
                            <span className="font-semibold text-legalgreen">{addedDates.join(', ')}</span>
                          </div>
                        )}
                        {removedDates.length > 0 && (
                          <div>
                            <span className="text-[11px] text-charcoal-muted block">Removed from Document A:</span>
                            <span className="font-semibold text-legalred line-through">{removedDates.join(', ')}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </section>
          )}

          {/* 3. Section / Clause Redline Diffs */}
          <section className="bg-white border border-line p-6 sm:p-8 shadow-subtle space-y-5">
            <div className="border-b border-line pb-3">
              <h2 className="text-base font-bold text-midnight uppercase tracking-wider">
                Clause Redline Differences
              </h2>
              <p className="text-[13px] text-charcoal-muted mt-0.5">
                Contractual clauses modified, introduced, or deleted between versions.
              </p>
            </div>

            {modifiedClauses.length === 0 && addedClauses.length === 0 && removedClauses.length === 0 ? (
              <p className="text-[14px] text-charcoal-muted italic py-4">
                No substantive clause modifications detected between these two documents.
              </p>
            ) : (
              <div className="space-y-4">
                {/* Modified Clauses */}
                {modifiedClauses.map((clause, idx) => (
                  <div key={idx} className="border border-line bg-white p-5 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2.5">
                        <span className="font-bold text-midnight text-[15px]">
                          {clause.clause_type}
                        </span>
                        <span className="px-2 py-0.5 text-[11px] font-bold uppercase tracking-wider bg-legalamber-subtle text-legalamber border border-legalamber-border">
                          Modified
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[13px] pt-1">
                      <div className="p-4 bg-legalred-subtle/60 border border-legalred-border space-y-1">
                        <span className="text-[10px] font-bold text-legalred uppercase tracking-wider block">
                          Original Text (Document A)
                        </span>
                        {renderRedlineTokens(clause.tokens_a, clause.doc_a_snippet || clause.original_text, 'a')}
                      </div>

                      <div className="p-4 bg-legalgreen-subtle/60 border border-legalgreen-border space-y-1">
                        <span className="text-[10px] font-bold text-legalgreen uppercase tracking-wider block">
                          Modified Text (Document B)
                        </span>
                        {renderRedlineTokens(clause.tokens_b, clause.doc_b_snippet || clause.modified_text, 'b')}
                      </div>
                    </div>

                    {/* Detected specific revisions */}
                    {clause.changes && clause.changes.length > 0 && (
                      <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-line/60">
                        <span className="text-[11px] font-bold text-charcoal-muted uppercase tracking-wider">
                          Detected Revisions:
                        </span>
                        {clause.changes.map((ch, cIdx) => (
                          <span key={cIdx} className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 bg-ivory border border-line text-xs font-mono">
                            <span className="text-legalred line-through font-semibold">{ch.original}</span>
                            <span className="text-charcoal-muted">→</span>
                            <span className="text-legalgreen font-bold">{ch.modified}</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}

                {/* Added Clauses */}
                {addedClauses.map((clause, idx) => (
                  <div key={idx} className="border border-legalgreen-border p-5 bg-legalgreen-subtle/30 space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-midnight text-[15px]">
                        {clause.clause_type}
                      </span>
                      <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-legalgreen-subtle text-legalgreen border border-legalgreen-border">
                        Added in Document B
                      </span>
                    </div>
                    <p className="font-serif text-[13px] text-charcoal leading-relaxed">
                      {clause.doc_b_snippet}
                    </p>
                  </div>
                ))}

                {/* Removed Clauses */}
                {removedClauses.map((clause, idx) => (
                  <div key={idx} className="border border-legalred-border p-5 bg-legalred-subtle/30 space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-midnight text-[15px]">
                        {clause.clause_type}
                      </span>
                      <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-legalred-subtle text-legalred border border-legalred-border">
                        Removed in Document B
                      </span>
                    </div>
                    <p className="font-serif text-[13px] text-charcoal-muted line-through leading-relaxed">
                      {clause.doc_a_snippet}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* 4. Changed Entities */}
          {(addedEntities.length > 0 || removedEntities.length > 0) && (
            <section className="bg-white border border-line p-6 shadow-subtle space-y-4">
              <h3 className="text-base font-bold text-midnight uppercase tracking-wider">
                Entity Changes
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[13px]">
                {addedEntities.length > 0 && (
                  <div className="p-4 bg-ivory border border-line space-y-1">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-legalgreen block">
                      Added in Document B ({addedEntities.length})
                    </span>
                    <p className="text-charcoal-body">{addedEntities.join(', ')}</p>
                  </div>
                )}
                {removedEntities.length > 0 && (
                  <div className="p-4 bg-ivory border border-line space-y-1">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-legalred block">
                      Removed from Document A ({removedEntities.length})
                    </span>
                    <p className="text-charcoal-body line-through">{removedEntities.join(', ')}</p>
                  </div>
                )}
              </div>
            </section>
          )}

        </div>
      )}
    </div>
  );
}
