import React, { useState, useEffect, useMemo } from 'react';
import { 
  ArrowLeft, 
  ArrowRight,
  Download, 
  FileText, 
  Eye, 
  Scale, 
  AlertTriangle, 
  ShieldCheck, 
  Calendar, 
  DollarSign, 
  Users, 
  Tag, 
  CheckCircle2, 
  ExternalLink,
  ChevronDown,
  ChevronUp,
  FileCode,
  ShieldAlert,
  Sparkles,
  Layers,
  Clock
} from 'lucide-react';
import { 
  getAnalysisSummary, 
  getDocument, 
  getDocumentClauses, 
  getDocumentObligations, 
  getDocumentFacts, 
  getAnalysisKeywords, 
  getAnalysisEntities, 
  exportAnalysisReport 
} from '../services/api';
import { useToast } from '../context/ToastContext';

export default function AnalysisResultsPage({ 
  activeAnalysisId, 
  activeDocumentId, 
  onNavigateToViewer, 
  onNavigateToIntake,
  onNavigate 
}) {
  const { showToast } = useToast();
  const [analysis, setAnalysis] = useState(null);
  const [document, setDocument] = useState(null);
  const [clauses, setClauses] = useState([]);
  const [obligations, setObligations] = useState([]);
  const [facts, setFacts] = useState({ dates: [], money: [], deadlines: [] });
  const [keywords, setKeywords] = useState([]);
  const [entities, setEntities] = useState([]);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isExportingJson, setIsExportingJson] = useState(false);
  const [expandedClauses, setExpandedClauses] = useState({});
  const [showAllEntities, setShowAllEntities] = useState(false);

  useEffect(() => {
    if (!activeAnalysisId) return;

    let isMounted = true;
    const fetchAllData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const [
          analysisData, 
          clauseData, 
          obData, 
          factData, 
          kwData, 
          entData
        ] = await Promise.all([
          getAnalysisSummary(activeAnalysisId),
          getDocumentClauses(activeAnalysisId).catch(() => ({ clauses: [] })),
          getDocumentObligations(activeAnalysisId).catch(() => ({ obligations: [] })),
          getDocumentFacts(activeAnalysisId).catch(() => ({ dates: [], money: [], deadlines: [] })),
          getAnalysisKeywords(activeAnalysisId, { limit: 50 }).catch(() => ({ keywords: [] })),
          getAnalysisEntities(activeAnalysisId, { limit: 100 }).catch(() => ({ entities: [] })),
        ]);

        if (!isMounted) return;

        setAnalysis(analysisData);
        setClauses(clauseData.clauses || []);
        setObligations(obData.obligations || []);
        setFacts(factData || { dates: [], money: [], deadlines: [] });
        setKeywords(kwData.keywords || []);
        setEntities(entData.entities || []);

        // Also fetch document metadata
        const docId = activeDocumentId || analysisData.document_id;
        if (docId) {
          try {
            const docData = await getDocument(docId);
            if (isMounted) setDocument(docData);
          } catch (e) {
            console.warn('Could not fetch document metadata:', e);
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to load analysis results.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchAllData();
    return () => { isMounted = false; };
  }, [activeAnalysisId, activeDocumentId]);

  // Derived Legal Snapshot Information
  const snapshot = useMemo(() => {
    // 1. Classify document type
    const docName = (document?.filename || analysis?.document_name || '').toLowerCase();
    let classification = 'Commercial Legal Agreement';
    if (docName.includes('employment') || docName.includes('offer')) classification = 'Employment Agreement';
    else if (docName.includes('lease') || docName.includes('tenancy') || docName.includes('rent')) classification = 'Commercial Lease Agreement';
    else if (docName.includes('nda') || docName.includes('confidential')) classification = 'Non-Disclosure Agreement (NDA)';
    else if (docName.includes('service') || docName.includes('consulting')) classification = 'Master Services Agreement';

    // 2. Extract Parties
    const partyEntities = entities.filter(e => 
      ['PARTY', 'PERSON', 'ORG', 'ORGANIZATION', 'LEGAL_ROLE'].includes((e.entity_type || '').toUpperCase())
    );
    const partyA = partyEntities[0]?.normalized_text || partyEntities[0]?.entity_text || 'Disclosing Party / Employer';
    const partyB = partyEntities[1]?.normalized_text || partyEntities[1]?.entity_text || 'Receiving Party / Employee';

    // 3. Extract Dates
    const effectiveDate = facts.dates?.[0]?.value || 'Upon Execution';
    const expirationDate = facts.dates?.[1]?.value || 'Subject to Term';

    // 4. Extract Financial Commitments
    const financialValues = facts.money?.map(m => m.value) || [];

    // 5. Notice Period / Deadlines
    const noticeDeadline = facts.deadlines?.[0]?.value || '30 calendar days';

    // 6. Governing Law
    const lawEntity = entities.find(e => 
      ['ACT', 'STATUTE', 'LAW', 'JURISDICTION'].includes((e.entity_type || '').toUpperCase())
    );
    const jurisdiction = lawEntity?.normalized_text || 'Applicable State Laws';

    return {
      classification,
      partyA,
      partyB,
      effectiveDate,
      expirationDate,
      financialValues,
      noticeDeadline,
      jurisdiction
    };
  }, [document, analysis, entities, facts]);

  // Detected Attention Areas (High & Medium risk clauses)
  const attentionAreas = useMemo(() => {
    const list = [];

    // Check Indemnification
    const indemnityClause = clauses.find(c => c.clause_type === 'Indemnification' && c.status === 'Found');
    if (indemnityClause) {
      list.push({
        severity: 'HIGH ATTENTION',
        level: 'high',
        title: 'Indemnification & Hold Harmless Clause',
        description: indemnityClause.summary || 'Broad indemnification detected. Review defense obligations and uninsured liability exposure.',
        clause: indemnityClause
      });
    }

    // Check Liability Limits
    const liabilityClause = clauses.find(c => c.clause_type === 'Liability' && c.status === 'Found');
    if (liabilityClause) {
      list.push({
        severity: 'HIGH ATTENTION',
        level: 'high',
        title: 'Limitation of Liability',
        description: liabilityClause.summary || 'Monetary liability caps or consequential damage waivers require confirmation with commercial policy.',
        clause: liabilityClause
      });
    }

    // Check Termination Conditions
    const termClause = clauses.find(c => c.clause_type === 'Termination' && c.status === 'Found');
    if (termClause) {
      list.push({
        severity: 'MEDIUM ATTENTION',
        level: 'medium',
        title: 'Termination for Convenience & Cause',
        description: termClause.summary || 'Review mandatory cure periods, post-termination duties, and immediate termination triggers.',
        clause: termClause
      });
    }

    // Check Non-Compete / Restriction
    const nonCompete = clauses.find(c => c.clause_type === 'Non-Compete / Restriction' && c.status === 'Found');
    if (nonCompete) {
      list.push({
        severity: 'MEDIUM ATTENTION',
        level: 'medium',
        title: 'Restrictive Covenants & Non-Compete',
        description: nonCompete.summary || 'Post-contractual employment restrictions detected. Evaluate territorial and temporal enforceability.',
        clause: nonCompete
      });
    }

    return list;
  }, [clauses]);

  // Grouped Legal Entities
  const groupedEntities = useMemo(() => {
    const groups = {
      'PARTIES & PERSONS': [],
      'STATUTES & ACTS': [],
      'SECTIONS & PROVISIONS': [],
      'COURTS & TRIBUNALS': [],
      'DATES & TIMELINES': [],
      'MONETARY SUMS': [],
      'LOCATIONS': []
    };

    entities.forEach(ent => {
      const type = (ent.entity_type || '').toUpperCase();
      const text = ent.normalized_text || ent.entity_text;
      if (!text) return;

      if (['PARTY', 'PERSON', 'ORG', 'ORGANIZATION', 'LEGAL_ROLE'].includes(type)) {
        if (!groups['PARTIES & PERSONS'].includes(text)) groups['PARTIES & PERSONS'].push(text);
      } else if (['ACT', 'LAW', 'STATUTE'].includes(type)) {
        if (!groups['STATUTES & ACTS'].includes(text)) groups['STATUTES & ACTS'].push(text);
      } else if (['SECTION', 'ARTICLE', 'CLAUSE'].includes(type)) {
        if (!groups['SECTIONS & PROVISIONS'].includes(text)) groups['SECTIONS & PROVISIONS'].push(text);
      } else if (['COURT', 'TRIBUNAL', 'BENCH'].includes(type)) {
        if (!groups['COURTS & TRIBUNALS'].includes(text)) groups['COURTS & TRIBUNALS'].push(text);
      } else if (['DATE', 'TIME'].includes(type)) {
        if (!groups['DATES & TIMELINES'].includes(text)) groups['DATES & TIMELINES'].push(text);
      } else if (['MONEY', 'CURRENCY', 'FINANCIAL'].includes(type)) {
        if (!groups['MONETARY SUMS'].includes(text)) groups['MONETARY SUMS'].push(text);
      } else if (['GPE', 'LOCATION', 'CITY', 'STATE'].includes(type)) {
        if (!groups['LOCATIONS'].includes(text)) groups['LOCATIONS'].push(text);
      }
    });

    // Also populate dates & money from structured facts if not present
    facts.dates?.forEach(d => {
      if (!groups['DATES & TIMELINES'].includes(d.value)) groups['DATES & TIMELINES'].push(d.value);
    });
    facts.money?.forEach(m => {
      if (!groups['MONETARY SUMS'].includes(m.value)) groups['MONETARY SUMS'].push(m.value);
    });

    return groups;
  }, [entities, facts]);

  const toggleClauseExpand = (type) => {
    setExpandedClauses(prev => ({ ...prev, [type]: !prev[type] }));
  };

  const handleExportPdf = async () => {
    if (!activeAnalysisId) return;
    setIsExportingPdf(true);
    try {
      const filename = `LexExtract_Summary_${document?.filename || activeAnalysisId}.pdf`;
      await exportAnalysisReport(activeAnalysisId, 'pdf', filename);
      showToast('PDF intelligence summary downloaded successfully.', 'success');
    } catch (err) {
      console.error('Export PDF error:', err);
      showToast('Unable to export PDF summary. Please try again.', 'error');
    } finally {
      setIsExportingPdf(false);
    }
  };

  const handleExportJson = async () => {
    if (!activeAnalysisId) return;
    setIsExportingJson(true);
    try {
      const filename = `LexExtract_Data_${document?.filename || activeAnalysisId}.json`;
      await exportAnalysisReport(activeAnalysisId, 'json', filename);
      showToast('JSON data report exported successfully.', 'success');
    } catch (err) {
      console.error('Export JSON error:', err);
      showToast('Unable to export JSON report.', 'error');
    } finally {
      setIsExportingJson(false);
    }
  };

  const handleViewInDocument = (searchSnippet, targetPage = null) => {
    const docId = activeDocumentId || analysis?.document_id;
    if (onNavigateToViewer && docId) {
      onNavigateToViewer(docId, { search: searchSnippet || '', page: targetPage });
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white border border-line p-16 text-center shadow-subtle space-y-4">
        <div className="w-9 h-9 border-2 border-midnight border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-[15px] font-medium text-midnight">Compiling legal intelligence summary...</p>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="bg-white border border-legalred-border p-12 text-center shadow-subtle space-y-4 max-w-lg mx-auto">
        <AlertTriangle className="w-10 h-10 text-legalred mx-auto" />
        <h3 className="text-lg font-bold text-midnight">Failed to Load Analysis</h3>
        <p className="text-[13px] text-charcoal-muted">{error || 'Analysis record could not be found.'}</p>
        <button
          onClick={onNavigateToIntake}
          className="btn-primary"
        >
          Analyze New Document
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* ============================================================== */}
      {/* 1. TOP HEADER & ACTIONS                                        */}
      {/* ============================================================== */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-line pb-6">
        <div className="space-y-2">
          {onNavigate && (
            <button
              onClick={() => onNavigate('history')}
              className="inline-flex items-center space-x-1.5 text-[13px] text-charcoal-muted hover:text-midnight transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Documents</span>
            </button>
          )}

          <div className="flex items-center space-x-3 flex-wrap">
            <h1 className="font-display text-2xl sm:text-3xl text-midnight font-bold tracking-tight">
              {document?.filename || analysis?.document_name || 'Legal Document Summary'}
            </h1>
            <span className="px-2 py-0.5 text-[11px] font-mono uppercase bg-ivory border border-line text-charcoal-muted">
              {document?.file_type || 'PDF'}
            </span>
          </div>

          <div className="flex items-center space-x-4 text-[13px] text-charcoal-muted">
            <span className="flex items-center space-x-1.5">
              <Calendar className="w-3.5 h-3.5" />
              <span>Analyzed {analysis?.created_at ? new Date(analysis.created_at).toLocaleDateString() : 'Recently'}</span>
            </span>
            <span>•</span>
            <span>{document?.word_count?.toLocaleString() || '—'} words</span>
            <span>•</span>
            <span>{document?.page_count || 1} pages</span>
          </div>
        </div>

        {/* Global Export & View Actions */}
        <div className="flex items-center space-x-2.5 shrink-0 self-start lg:self-center">
          <button
            onClick={() => handleViewInDocument()}
            className="btn-secondary py-2 px-3.5 text-[13px]"
          >
            <Eye className="w-4 h-4 text-midnight" />
            <span>View Document</span>
          </button>

          <div className="flex items-center border border-line p-0.5 bg-ivory">
            <button
              onClick={handleExportPdf}
              disabled={isExportingPdf}
              className="py-1.5 px-3 text-[13px] font-semibold text-midnight hover:bg-white transition-colors flex items-center space-x-1.5"
              title="Download publication-ready legal PDF report"
            >
              <Download className="w-3.5 h-3.5 text-crimson" />
              <span>{isExportingPdf ? 'Exporting...' : 'Export PDF'}</span>
            </button>
            <span className="text-line-dark">|</span>
            <button
              onClick={handleExportJson}
              disabled={isExportingJson}
              className="py-1.5 px-3 text-[13px] font-semibold text-charcoal hover:bg-white transition-colors flex items-center space-x-1.5"
              title="Download structured analytical JSON data report"
            >
              <FileCode className="w-3.5 h-3.5 text-midnight" />
              <span>{isExportingJson ? 'Exporting...' : 'Export JSON'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* ============================================================== */}
      {/* 2. LEGAL SNAPSHOT (2-COLUMN BALANCED WORKSPACE)                */}
      {/* ============================================================== */}
      <section className="bg-white border border-line p-6 sm:p-8 shadow-subtle space-y-5">
        <div className="flex items-center justify-between border-b border-line pb-3">
          <div className="flex items-center space-x-2">
            <Scale className="w-5 h-5 text-gold-dark" />
            <h2 className="text-base font-bold text-midnight uppercase tracking-wider">
              Legal Snapshot
            </h2>
          </div>
          <span className="text-[12px] font-medium text-midnight bg-ivory-subtle px-2.5 py-1 border border-line">
            {snapshot.classification}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-[14px]">
          {/* Column 1: Core Parties & Governance */}
          <div className="space-y-4">
            <div>
              <span className="text-[11px] font-semibold text-charcoal-muted uppercase tracking-wider block">
                Primary Contractual Parties
              </span>
              <div className="mt-1 space-y-1">
                <div 
                  onClick={() => handleViewInDocument(snapshot.partyA)}
                  className="font-semibold text-midnight text-[15px] cursor-pointer hover:text-crimson transition-colors"
                  title="Find in document"
                >
                  {snapshot.partyA}
                </div>
                <div className="text-[13px] text-charcoal-muted font-medium">
                  and
                </div>
                <div 
                  onClick={() => handleViewInDocument(snapshot.partyB)}
                  className="font-semibold text-midnight text-[15px] cursor-pointer hover:text-crimson transition-colors"
                  title="Find in document"
                >
                  {snapshot.partyB}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-2 border-t border-line/60">
              <div>
                <span className="text-[11px] font-semibold text-charcoal-muted uppercase tracking-wider block">
                  Effective Date
                </span>
                <span 
                  onClick={() => handleViewInDocument(snapshot.effectiveDate)}
                  className="font-medium text-charcoal mt-0.5 block cursor-pointer hover:text-crimson transition-colors"
                  title="Find in document"
                >
                  {snapshot.effectiveDate}
                </span>
              </div>
              <div>
                <span className="text-[11px] font-semibold text-charcoal-muted uppercase tracking-wider block">
                  Notice Requirement
                </span>
                <span 
                  onClick={() => handleViewInDocument(snapshot.noticeDeadline)}
                  className="font-medium text-charcoal mt-0.5 block cursor-pointer hover:text-crimson transition-colors"
                  title="Find in document"
                >
                  {snapshot.noticeDeadline}
                </span>
              </div>
            </div>
          </div>

          {/* Column 2: Financial Commitments & Legal Bounds */}
          <div className="space-y-4 md:border-l md:border-line md:pl-8">
            <div>
              <span className="text-[11px] font-semibold text-charcoal-muted uppercase tracking-wider block">
                Financial Commitments &amp; Exposure
              </span>
              {snapshot.financialValues.length > 0 ? (
                <div className="mt-1 space-y-1">
                  {snapshot.financialValues.slice(0, 3).map((val, idx) => (
                    <div 
                      key={idx} 
                      onClick={() => handleViewInDocument(val)}
                      className="font-bold text-midnight text-[16px] text-crimson cursor-pointer hover:underline"
                      title="Find in document"
                    >
                      {val}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="font-medium text-charcoal mt-1 text-[14px]">
                  Standard performance covenants (no explicit monetary sum detected)
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4 pt-2 border-t border-line/60">
              <div>
                <span className="text-[11px] font-semibold text-charcoal-muted uppercase tracking-wider block">
                  Governing Jurisdiction
                </span>
                <span 
                  onClick={() => handleViewInDocument(snapshot.jurisdiction)}
                  className="font-medium text-charcoal mt-0.5 block cursor-pointer hover:text-crimson transition-colors"
                  title="Find in document"
                >
                  {snapshot.jurisdiction}
                </span>
              </div>
              <div>
                <span className="text-[11px] font-semibold text-charcoal-muted uppercase tracking-wider block">
                  Document Classification
                </span>
                <span className="font-medium text-charcoal mt-0.5 block">
                  {snapshot.classification}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 3. EXTRACTION OVERVIEW / INSIGHT BAR                            */}
      {/* ============================================================== */}
      <section className="bg-white border border-line shadow-subtle p-5 grid grid-cols-2 sm:grid-cols-5 divide-y sm:divide-y-0 sm:divide-x divide-line text-center">
        <div className="py-2 sm:py-0 px-3 space-y-0.5">
          <span className="text-[11px] text-charcoal-muted uppercase tracking-wider font-semibold block">
            Keywords
          </span>
          <span className="text-xl font-bold text-midnight font-sans">
            {keywords.length > 0 ? keywords.length : (analysis?.total_keywords ?? 0)}
          </span>
        </div>

        <div className="py-2 sm:py-0 px-3 space-y-0.5">
          <span className="text-[11px] text-charcoal-muted uppercase tracking-wider font-semibold block">
            Legal Entities
          </span>
          <span className="text-xl font-bold text-midnight font-sans">
            {entities.length > 0 ? entities.length : (analysis?.total_entities ?? 0)}
          </span>
        </div>

        <div className="py-2 sm:py-0 px-3 space-y-0.5">
          <span className="text-[11px] text-charcoal-muted uppercase tracking-wider font-semibold block">
            Clauses
          </span>
          <span className="text-xl font-bold text-midnight font-sans">
            {clauses.filter(c => c.status === 'Found').length}
          </span>
        </div>

        <div className="py-2 sm:py-0 px-3 space-y-0.5">
          <span className="text-[11px] text-charcoal-muted uppercase tracking-wider font-semibold block">
            Dates
          </span>
          <span className="text-xl font-bold text-midnight font-sans">
            {facts.dates?.length ?? 0}
          </span>
        </div>

        <div className="py-2 sm:py-0 px-3 space-y-0.5 col-span-2 sm:col-span-1">
          <span className="text-[11px] text-charcoal-muted uppercase tracking-wider font-semibold block">
            Financial Terms
          </span>
          <span className="text-xl font-bold text-midnight font-sans text-crimson">
            {facts.money?.length ?? 0}
          </span>
        </div>
      </section>

      {/* ============================================================== */}
      {/* 4. ATTENTION AREAS (PROMINENT REVIEW CARDS)                     */}
      {/* ============================================================== */}
      {attentionAreas.length > 0 ? (
        <section className="bg-white border border-line p-6 sm:p-8 shadow-subtle space-y-5">
          <div className="flex items-center justify-between border-b border-line pb-3">
            <div className="flex items-center space-x-2.5">
              <ShieldAlert className="w-5 h-5 text-crimson" />
              <h2 className="text-base font-bold text-midnight uppercase tracking-wider">
                Attention Areas
              </h2>
            </div>
            <span className="text-[12px] font-semibold text-crimson bg-crimson/5 px-2.5 py-1 border border-crimson/20">
              {attentionAreas.length} {attentionAreas.length === 1 ? 'item requires' : 'items require'} review
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {attentionAreas.map((item, idx) => (
              <div 
                key={idx}
                className="p-5 border border-line bg-ivory space-y-3 flex flex-col justify-between"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                      item.level === 'high' 
                        ? 'bg-legalred-subtle text-legalred border border-legalred-border' 
                        : 'bg-legalamber-subtle text-legalamber border border-legalamber-border'
                    }`}>
                      {item.severity}
                    </span>
                    <span className="font-semibold text-midnight text-[14px]">
                      {item.title}
                    </span>
                  </div>
                  <p className="text-[13px] text-charcoal-body leading-relaxed">
                    {item.description}
                  </p>
                </div>

                <div className="pt-2 flex justify-end">
                  <button
                    onClick={() => handleViewInDocument(item.clause?.relevant_text || item.title, item.clause?.page_number)}
                    className="inline-flex items-center space-x-1.5 text-[12px] font-semibold text-crimson hover:underline"
                  >
                    <span>View Clause</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : (
        <section className="bg-white border border-line p-5 shadow-subtle flex items-center space-x-3 text-[13px]">
          <CheckCircle2 className="w-5 h-5 text-legalgreen shrink-0" />
          <div>
            <span className="font-semibold text-midnight">No High-Risk Attention Areas Flagged</span>
            <p className="text-charcoal-muted text-[12px] mt-0.5">
              All identified clauses fall within standard operational covenants without restrictive or extraordinary liabilities.
            </p>
          </div>
        </section>
      )}

      {/* ============================================================== */}
      {/* 5. IMPORTANT CLAUSES                                           */}
      {/* ============================================================== */}
      <section className="bg-white border border-line p-6 sm:p-8 shadow-subtle space-y-5">
        <div className="border-b border-line pb-3">
          <h2 className="text-base font-bold text-midnight uppercase tracking-wider">
            Important Clauses
          </h2>
          <p className="text-[13px] text-charcoal-muted mt-0.5">
            Key detected contractual sections and terms extracted from the source document.
          </p>
        </div>

        <div className="space-y-3">
          {clauses.filter(c => c.status === 'Found').map((clause, idx) => {
            const isExpanded = Boolean(expandedClauses[clause.clause_type]);
            return (
              <div 
                key={idx} 
                className="border border-line bg-white transition-all overflow-hidden"
              >
                {/* Header row */}
                <div 
                  onClick={() => toggleClauseExpand(clause.clause_type)}
                  className="p-4 sm:p-5 flex items-center justify-between cursor-pointer hover:bg-ivory/50 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <span className="w-2 h-2 rounded-full bg-midnight shrink-0" />
                    <div>
                      <span className="font-semibold text-midnight text-[15px]">
                        {clause.clause_type}
                      </span>
                      <p className="text-[13px] text-charcoal-muted line-clamp-1 mt-0.5">
                        {clause.summary || clause.relevant_text}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 shrink-0 ml-4">
                    <span className="text-[11px] text-charcoal-muted font-medium">
                      Page {clause.page_number || 1}
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-charcoal-muted" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-charcoal-muted" />
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="p-5 bg-ivory border-t border-line space-y-3 text-[13px] animate-in fade-in">
                    <div>
                      <span className="text-[11px] font-semibold text-charcoal-muted uppercase block">
                        Clause Synthesis
                      </span>
                      <p className="text-charcoal-body leading-relaxed mt-0.5">
                        {clause.summary || 'Verbatim provision identified in the primary text stream.'}
                      </p>
                    </div>

                    <div className="p-3 bg-white border border-line space-y-1">
                      <span className="text-[10px] uppercase font-mono text-charcoal-muted block">
                        Source Text Excerpt (Page {clause.page_number || 1})
                      </span>
                      <p className="font-serif text-[13px] text-charcoal leading-relaxed select-text italic">
                        "{clause.relevant_text}"
                      </p>
                    </div>

                    <div className="flex justify-end pt-1">
                      <button
                        onClick={() => handleViewInDocument(clause.relevant_text, clause.page_number)}
                        className="btn-secondary py-1.5 px-3 text-[12px]"
                      >
                        <Eye className="w-3.5 h-3.5 text-midnight" />
                        <span>View in Document</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* ============================================================== */}
      {/* 6. CONTRACTUAL OBLIGATIONS                                     */}
      {/* ============================================================== */}
      {obligations.length > 0 && (
        <section className="bg-white border border-line p-6 sm:p-8 shadow-subtle space-y-5">
          <div className="border-b border-line pb-3">
            <h2 className="text-base font-bold text-midnight uppercase tracking-wider">
              Contractual Obligations &amp; Duties
            </h2>
            <p className="text-[13px] text-charcoal-muted mt-0.5">
              Explicit responsibilities, performance commitments, and prohibitions identified in the document.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {obligations.slice(0, 8).map((ob, idx) => (
              <div key={idx} className="p-4 bg-ivory border border-line space-y-2">
                <div className="flex items-center justify-between text-[12px]">
                  <span className="font-bold text-midnight uppercase tracking-wider">
                    {ob.responsible_party || 'Contractual Party'}
                  </span>
                  <span className="text-[11px] font-mono text-charcoal-muted">
                    Page {ob.page_number || 1}
                  </span>
                </div>
                <p className="text-[13px] text-charcoal-body leading-relaxed">
                  {ob.obligation_text}
                </p>
                <div className="flex justify-end pt-1">
                  <button
                    onClick={() => handleViewInDocument(ob.obligation_text, ob.page_number)}
                    className="text-[11px] text-crimson font-semibold hover:underline flex items-center space-x-1"
                  >
                    <span>Source Passage →</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ============================================================== */}
      {/* 7. KEY TERMS (WEIGHTED ANALYTICAL TERM MAP)                    */}
      {/* ============================================================== */}
      <section className="bg-white border border-line p-6 sm:p-8 shadow-subtle space-y-5">
        <div className="border-b border-line pb-3">
          <h2 className="text-base font-bold text-midnight uppercase tracking-wider">
            Key Terms
          </h2>
          <p className="text-[13px] text-charcoal-muted mt-0.5">
            Domain terminology weighted by statistical relevance and contractual salience.
          </p>
        </div>

        {/* Clean analytical term map with visual weight */}
        <div className="flex flex-wrap items-baseline gap-3 p-4 bg-ivory border border-line">
          {keywords.slice(0, 24).map((kw, idx) => {
            // Visual weight based on rank
            let weightStyle = 'text-[13px] font-normal text-charcoal-body';
            if (idx < 4) {
              weightStyle = 'text-[17px] font-bold text-midnight border-b-2 border-midnight/60 pb-0.5';
            } else if (idx < 10) {
              weightStyle = 'text-[15px] font-semibold text-midnight border-b border-line-dark';
            } else if (idx < 18) {
              weightStyle = 'text-[14px] font-medium text-charcoal';
            }

            return (
              <button
                key={idx}
                onClick={() => handleViewInDocument(kw.keyword)}
                className={`cursor-pointer hover:text-crimson transition-colors px-2 py-1 ${weightStyle}`}
                title={`Category: ${kw.category || 'Legal'} • Rank #${idx + 1}`}
              >
                {kw.keyword}
              </button>
            );
          })}
        </div>
      </section>

      {/* ============================================================== */}
      {/* 8. LEGAL ENTITIES (GROUPED BY CATEGORY)                        */}
      {/* ============================================================== */}
      <section className="bg-white border border-line p-6 sm:p-8 shadow-subtle space-y-5">
        <div className="flex items-center justify-between border-b border-line pb-3">
          <div>
            <h2 className="text-base font-bold text-midnight uppercase tracking-wider">
              Legal Entities
            </h2>
            <p className="text-[13px] text-charcoal-muted mt-0.5">
              Recognized entities categorized by legal and administrative taxonomy.
            </p>
          </div>

          <button
            onClick={() => setShowAllEntities(!showAllEntities)}
            className="text-[12px] text-midnight font-semibold hover:underline"
          >
            {showAllEntities ? 'Show Concise' : 'Show All Entities'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {Object.entries(groupedEntities).map(([groupTitle, items]) => {
            if (items.length === 0) return null;
            const displayItems = showAllEntities ? items : items.slice(0, 5);

            return (
              <div key={groupTitle} className="p-4 bg-ivory border border-line space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-charcoal-muted block">
                  {groupTitle}
                </span>

                <div className="space-y-1.5 text-[13px]">
                  {displayItems.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleViewInDocument(item)}
                      className="w-full text-left font-medium text-midnight hover:text-crimson transition-colors block truncate"
                      title={item}
                    >
                      • {item}
                    </button>
                  ))}
                  {!showAllEntities && items.length > 5 && (
                    <span className="text-[11px] text-charcoal-muted italic block pt-1">
                      +{items.length - 5} more
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ============================================================== */}
      {/* 9. BOTTOM ACTION BAR                                           */}
      {/* ============================================================== */}
      <div className="p-6 bg-white border border-line shadow-subtle flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <span className="font-semibold text-midnight text-[15px] block">
            Analysis Complete
          </span>
          <span className="text-[13px] text-charcoal-muted">
            All extracted clauses, obligations, and terminology have been cross-referenced with source text.
          </span>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => handleViewInDocument()}
            className="btn-secondary py-2.5 px-5 text-[14px]"
          >
            <Eye className="w-4 h-4 text-midnight" />
            <span>View Document</span>
          </button>

          <button
            onClick={handleExportPdf}
            disabled={isExportingPdf}
            className="btn-primary py-2.5 px-6 text-[14px]"
          >
            <Download className="w-4 h-4 text-gold-light" />
            <span>{isExportingPdf ? 'Exporting...' : 'Export Summary (PDF)'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
