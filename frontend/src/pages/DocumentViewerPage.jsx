import React, { useState, useEffect, useMemo, useRef } from 'react';
import { 
  FileText, 
  Download, 
  Search, 
  ChevronLeft, 
  ChevronRight,
  ChevronUp,
  ChevronDown,
  ArrowLeft,
  Calendar,
  DollarSign,
  Users,
  Tag,
  Scale,
  CheckCircle2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  AlertCircle
} from 'lucide-react';
import { 
  getDocument, 
  getDocumentText, 
  listDocuments, 
  listDocumentAnalyses, 
  getAnalysisKeywords, 
  getAnalysisEntities, 
  getDocumentClauses,
  getDocumentObligations,
  getDocumentFacts, 
  downloadDocumentFile 
} from '../services/api';
import { useToast } from '../context/ToastContext';

export default function DocumentViewerPage({ 
  activeDocumentId, 
  initialSearch = '',
  initialPage = null,
  onNavigateToResults,
  onNavigateToIntake 
}) {
  const { showToast } = useToast();
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(activeDocumentId || null);
  const [docMetadata, setDocMetadata] = useState(null);
  const [docContent, setDocContent] = useState(null);
  const [analysisRun, setAnalysisRun] = useState(null);
  
  // Extracted intelligence elements
  const [keywords, setKeywords] = useState([]);
  const [entities, setEntities] = useState([]);
  const [clauses, setClauses] = useState([]);
  const [obligations, setObligations] = useState([]);
  const [facts, setFacts] = useState({ dates: [], money: [] });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Viewer states
  const [activePageNum, setActivePageNum] = useState(initialPage ? Number(initialPage) : 1);
  const [activeTab, setActiveTab] = useState('clauses'); // 'clauses' | 'obligations' | 'facts' | 'entities' | 'keywords'
  const [searchTerm, setSearchTerm] = useState(initialSearch || '');
  const [highlightSnippet, setHighlightSnippet] = useState(initialSearch || '');
  const [activeSearchRegex, setActiveSearchRegex] = useState(null);
  const [fontSizeLevel, setFontSizeLevel] = useState(1); // 0: standard (15px), 1: medium (16px), 2: large (18px)
  const [activeMatchIndex, setActiveMatchIndex] = useState(0);

  const documentTextRef = useRef(null);

  // Helper: Build flexible regex tolerant of whitespace, newlines, and punctuation
  const buildFlexibleRegex = (query) => {
    if (!query) return null;
    const clean = query
      .trim()
      .replace(/["'“”‘’]/g, '')
      .replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    if (!clean) return null;

    const words = clean.split(/\s+/).filter(Boolean);
    if (words.length === 0) return null;

    const anchorWords = words.length > 8 ? words.slice(0, 7) : words;
    const pattern = anchorWords.join('[\\s,;.:\\-—\'"“”‘’()\\[\\]{}]+');
    try {
      return new RegExp(pattern, 'gi');
    } catch {
      return null;
    }
  };

  // Helper: Test page text against query using multi-stage matching
  const testPageMatch = (pageText, query) => {
    if (!pageText || !query) return null;
    
    // Stage 1: Flexible regex
    const regex1 = buildFlexibleRegex(query);
    if (regex1 && regex1.test(pageText)) {
      return regex1;
    }

    // Stage 2: Normalized substring matching fallback
    const normPage = pageText.toLowerCase().replace(/\s+/g, ' ');
    const normQuery = query.toLowerCase().replace(/\s+/g, ' ').trim();
    const shortQuery = normQuery.length > 35 ? normQuery.slice(0, 30) : normQuery;

    if (normPage.includes(shortQuery)) {
      const regex2 = buildFlexibleRegex(shortQuery);
      if (regex2 && regex2.test(pageText)) return regex2;
    }

    return null;
  };

  // Load document list
  useEffect(() => {
    let isMounted = true;
    const fetchDocList = async () => {
      try {
        const list = await listDocuments();
        if (isMounted) {
          setDocuments(list || []);
          if (!selectedDocId && list && list.length > 0) {
            setSelectedDocId(list[0].id);
          }
        }
      } catch (err) {
        console.error('Failed to load documents list:', err);
      }
    };
    fetchDocList();
    return () => { isMounted = false; };
  }, []);

  // Update selected doc if prop changes
  useEffect(() => {
    if (activeDocumentId) {
      setSelectedDocId(activeDocumentId);
    }
  }, [activeDocumentId]);

  // Fetch document text, metadata, and analysis layers
  useEffect(() => {
    if (!selectedDocId) return;

    let isMounted = true;
    const fetchAllData = async () => {
      setIsLoading(true);
      setError(null);
      if (initialPage && Number(initialPage) > 0) {
        setActivePageNum(Number(initialPage));
      } else {
        setActivePageNum(1);
      }

      try {
        const [textData, metaData, analyses] = await Promise.allSettled([
          getDocumentText(selectedDocId),
          getDocument(selectedDocId),
          listDocumentAnalyses(selectedDocId)
        ]);

        if (!isMounted) return;

        if (textData.status === 'fulfilled') {
          setDocContent(textData.value);
        } else {
          throw textData.reason;
        }

        if (metaData.status === 'fulfilled') {
          setDocMetadata(metaData.value);
        }

        if (analyses.status === 'fulfilled' && analyses.value && analyses.value.length > 0) {
          const latestRun = analyses.value[0];
          setAnalysisRun(latestRun);

          const [kwData, entData, clauseData, obData, factData] = await Promise.allSettled([
            getAnalysisKeywords(latestRun.id, { limit: 50 }),
            getAnalysisEntities(latestRun.id, { limit: 100 }),
            getDocumentClauses(latestRun.id),
            getDocumentObligations(latestRun.id),
            getDocumentFacts(latestRun.id)
          ]);

          if (isMounted) {
            if (kwData.status === 'fulfilled') setKeywords(kwData.value?.keywords || []);
            if (entData.status === 'fulfilled') setEntities(entData.value?.entities || []);
            if (clauseData.status === 'fulfilled') setClauses(clauseData.value?.clauses || []);
            if (obData.status === 'fulfilled') setObligations(obData.value?.obligations || []);
            if (factData.status === 'fulfilled') setFacts(factData.value || { dates: [], money: [] });
          }
        } else {
          setAnalysisRun(null);
          setKeywords([]);
          setEntities([]);
          setClauses([]);
          setObligations([]);
          setFacts({ dates: [], money: [] });
        }
      } catch (err) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to retrieve document contents.');
          setDocContent(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchAllData();
    return () => { isMounted = false; };
  }, [selectedDocId]);

  // Handle initialSearch navigation after docContent is loaded
  useEffect(() => {
    if (initialSearch && docContent) {
      handleJumpToSource(initialSearch, initialPage);
    }
  }, [initialSearch, initialPage, docContent]);

  // Current page text extraction
  const currentPageData = useMemo(() => {
    if (!docContent || !docContent.pages || docContent.pages.length === 0) {
      return { page_number: 1, text: docContent?.text || '' };
    }
    const found = docContent.pages.find(p => p.page_number === activePageNum);
    return found || docContent.pages[0];
  }, [docContent, activePageNum]);

  const totalPages = docContent?.pages?.length || (docMetadata?.page_count || 1);

  // Jump to specific passage / snippet with robust multi-page scanning
  const handleJumpToSource = (textSnippet, targetPage = null) => {
    if (!textSnippet) {
      showToast('Source location unavailable for this item.', 'info');
      return;
    }
    const clean = String(textSnippet).trim();
    if (!clean) {
      showToast('Source location unavailable for this item.', 'info');
      return;
    }

    const pages = docContent?.pages || [];
    let matchFound = false;
    let targetPageNumber = null;
    let matchingRegex = null;

    // 1. If targetPage is provided, check that page first
    if (targetPage && pages.length > 0) {
      const preferred = pages.find(p => p.page_number === Number(targetPage));
      if (preferred) {
        const matched = testPageMatch(preferred.text, clean);
        if (matched) {
          matchFound = true;
          targetPageNumber = preferred.page_number;
          matchingRegex = matched;
        }
      }
    }

    // 2. If not found on preferred page, scan ALL pages
    if (!matchFound && pages.length > 0) {
      for (const p of pages) {
        const matched = testPageMatch(p.text, clean);
        if (matched) {
          matchFound = true;
          targetPageNumber = p.page_number;
          matchingRegex = matched;
          break;
        }
      }
    }

    // 3. Fallback for single-page / raw text documents
    if (!matchFound && docContent?.text) {
      const matched = testPageMatch(docContent.text, clean);
      if (matched) {
        matchFound = true;
        targetPageNumber = 1;
        matchingRegex = matched;
      }
    }

    // If genuinely not found in the source text
    if (!matchFound) {
      showToast('Source location unavailable for this item.', 'info');
      return;
    }

    // Successfully located
    setHighlightSnippet(clean);
    setSearchTerm(clean.length > 40 ? clean.slice(0, 40) : clean);
    setActiveSearchRegex(matchingRegex);
    setActiveMatchIndex(0);

    if (targetPageNumber && targetPageNumber !== activePageNum) {
      setActivePageNum(targetPageNumber);
    }

    setTimeout(() => {
      if (documentTextRef.current) {
        const highlightedEl = documentTextRef.current.querySelector('.doc-highlight-current') ||
                              documentTextRef.current.querySelector('.doc-highlight-active');
        if (highlightedEl) {
          highlightedEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    }, 150);
  };

  const handleDownload = async () => {
    if (!selectedDocId || !docMetadata) return;
    try {
      await downloadDocumentFile(selectedDocId, docMetadata.filename);
      showToast('Document downloaded.', 'success');
    } catch (err) {
      showToast('Failed to download document file.', 'error');
    }
  };

  // Total matches for search query on active page
  const totalMatches = useMemo(() => {
    const query = searchTerm.trim() || highlightSnippet.trim() || '';
    if (!query || !currentPageData?.text) return 0;
    try {
      const regex = activeSearchRegex || buildFlexibleRegex(query);
      if (!regex) return 0;
      const execRegex = new RegExp(regex.source, 'gi');
      const matches = currentPageData.text.match(execRegex);
      return matches ? matches.length : 0;
    } catch {
      return 0;
    }
  }, [searchTerm, highlightSnippet, activeSearchRegex, currentPageData]);

  // Reset active match index on search or page change
  useEffect(() => {
    setActiveMatchIndex(0);
  }, [searchTerm, activePageNum]);

  const handleNextMatch = () => {
    if (totalMatches <= 0) return;
    setActiveMatchIndex((prev) => (prev + 1) % totalMatches);
  };

  const handlePrevMatch = () => {
    if (totalMatches <= 0) return;
    setActiveMatchIndex((prev) => (prev - 1 + totalMatches) % totalMatches);
  };

  // Scroll active match element into view
  useEffect(() => {
    if (totalMatches > 0 && documentTextRef.current) {
      const activeEl = documentTextRef.current.querySelector('.doc-highlight-current');
      if (activeEl) {
        activeEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [activeMatchIndex, totalMatches]);

  // Font size classes for legal paper reader
  const fontSizes = ['text-[14px]', 'text-[16px]', 'text-[18px]'];
  const lineHeights = ['leading-relaxed', 'leading-loose', 'leading-loose'];

  // Render document text with robust slice-based highlight
  const renderDocumentText = (rawText) => {
    if (!rawText) return null;

    const query = searchTerm.trim() || highlightSnippet.trim() || '';
    const regex = activeSearchRegex || buildFlexibleRegex(query);

    if (!regex) {
      return (
        <div className={`whitespace-pre-wrap font-serif ${fontSizes[fontSizeLevel]} ${lineHeights[fontSizeLevel]} text-charcoal`}>
          {rawText}
        </div>
      );
    }

    try {
      const execRegex = new RegExp(regex.source, 'gi');
      const matches = [];
      let m;
      while ((m = execRegex.exec(rawText)) !== null) {
        matches.push({ index: m.index, length: m[0].length, text: m[0] });
        if (execRegex.lastIndex === m.index) execRegex.lastIndex++;
      }

      if (matches.length === 0) {
        return (
          <div className={`whitespace-pre-wrap font-serif ${fontSizes[fontSizeLevel]} ${lineHeights[fontSizeLevel]} text-charcoal`}>
            {rawText}
          </div>
        );
      }

      const elements = [];
      let lastIndex = 0;

      matches.forEach((match, idx) => {
        const start = match.index;
        const end = start + match.length;
        if (start > lastIndex) {
          elements.push(rawText.slice(lastIndex, start));
        }
        const isCurrent = idx === activeMatchIndex;
        elements.push(
          <mark
            key={`mark-${start}-${idx}`}
            className={
              isCurrent
                ? "doc-highlight-current bg-midnight text-gold-light px-1 py-0.5 rounded-xs font-bold border-b-2 border-gold shadow-xs ring-2 ring-gold/40"
                : "doc-highlight-active bg-legalamber/30 text-midnight px-1 py-0.5 rounded-xs font-semibold border-b-2 border-crimson"
            }
          >
            {rawText.slice(start, end)}
          </mark>
        );
        lastIndex = end;
      });

      if (lastIndex < rawText.length) {
        elements.push(rawText.slice(lastIndex));
      }

      return (
        <div className={`whitespace-pre-wrap font-serif ${fontSizes[fontSizeLevel]} ${lineHeights[fontSizeLevel]} text-charcoal`}>
          {elements}
        </div>
      );
    } catch {
      return (
        <div className={`whitespace-pre-wrap font-serif ${fontSizes[fontSizeLevel]} ${lineHeights[fontSizeLevel]} text-charcoal`}>
          {rawText}
        </div>
      );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Selector */}
      <div className="bg-white border border-line p-5 shadow-subtle flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          {onNavigateToResults && analysisRun && (
            <button
              onClick={() => onNavigateToResults(analysisRun.id, selectedDocId)}
              className="p-2 border border-line hover:bg-ivory-subtle text-charcoal transition-colors"
              title="Return to Summary"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
          )}

          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold font-sans text-midnight tracking-tight">
                {docMetadata?.filename || 'Document Reviewer'}
              </h1>
              <span className="px-2 py-0.5 text-[11px] font-mono uppercase bg-ivory text-charcoal-muted border border-line">
                {docMetadata?.file_type || 'PDF'}
              </span>
            </div>
            <div className="flex items-center space-x-3 text-[12px] text-charcoal-muted mt-0.5">
              <span>{totalPages} {totalPages === 1 ? 'Page' : 'Pages'}</span>
              <span>•</span>
              <span>{docContent?.word_count?.toLocaleString() || 0} words</span>
              {analysisRun && (
                <>
                  <span>•</span>
                  <span className="text-legalgreen font-medium">Intelligence Synchronized</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Controls: Document Switcher, Download & Summary Jump */}
        <div className="flex items-center space-x-3">
          {documents.length > 1 && (
            <select
              value={selectedDocId || ''}
              onChange={(e) => setSelectedDocId(Number(e.target.value))}
              aria-label="Select Document"
              className="text-[13px] bg-ivory border border-line px-3 py-1.5 text-midnight font-medium focus:outline-none focus:border-midnight"
            >
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename}
                </option>
              ))}
            </select>
          )}

          <button
            onClick={handleDownload}
            className="btn-secondary py-1.5 px-3 text-[13px]"
            title="Download original file"
          >
            <Download className="w-3.5 h-3.5 text-crimson" />
            <span>Download</span>
          </button>

          {analysisRun && onNavigateToResults && (
            <button
              onClick={() => onNavigateToResults(analysisRun.id, selectedDocId)}
              className="btn-primary py-1.5 px-3.5 text-[13px]"
            >
              <span>Summary</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Split Layout: Document Area (Left) & Extracted Intelligence Panel (Right) */}
      {isLoading ? (
        <div className="bg-white border border-line p-16 text-center shadow-subtle space-y-3">
          <div className="w-8 h-8 border-2 border-midnight border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-[14px] font-medium text-midnight">Loading legal document text stream...</p>
        </div>
      ) : error ? (
        <div className="bg-white border border-legalred-border p-10 text-center shadow-subtle space-y-3">
          <AlertCircle className="w-8 h-8 text-legalred mx-auto" />
          <h3 className="text-base font-bold text-midnight">Unable to Load Document</h3>
          <p className="text-[13px] text-charcoal-muted">{error}</p>
        </div>
      ) : !docContent ? (
        <div className="bg-white border border-line p-16 text-center shadow-subtle space-y-3">
          <p className="text-[14px] text-charcoal-muted">No document selected.</p>
          <button onClick={onNavigateToIntake} className="btn-primary">
            + Upload Document
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* ============================================================== */}
          {/* LEFT COLUMN (7 COLS): CLEAN PAPER-LIKE DOCUMENT SURFACE        */}
          {/* ============================================================== */}
          <div className="lg:col-span-7 space-y-3">
            <div className="bg-white border border-line shadow-subtle">
              
              {/* Document Toolbar: Search, Matches, Zoom, Page Navigator */}
              <div className="p-3 bg-ivory border-b border-line flex flex-wrap items-center justify-between gap-3 text-[13px]">
                {/* Search in document */}
                <div className="flex items-center space-x-2 flex-1 min-w-[240px]">
                  <Search className="w-4 h-4 text-charcoal-muted shrink-0" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => {
                      setSearchTerm(e.target.value);
                      setHighlightSnippet(e.target.value);
                    }}
                    placeholder="Search document text..."
                    className="w-full bg-white border border-line px-2.5 py-1 text-[13px] text-midnight focus:outline-none focus:border-midnight"
                  />
                  {searchTerm && (
                    <div className="flex items-center space-x-1 shrink-0">
                      <span className="text-[11px] font-mono font-medium text-charcoal-muted px-1 whitespace-nowrap">
                        {totalMatches > 0 ? `${activeMatchIndex + 1} of ${totalMatches}` : '0 matches'}
                      </span>
                      <button
                        type="button"
                        onClick={handlePrevMatch}
                        disabled={totalMatches <= 1}
                        className="p-1 border border-line bg-white hover:bg-ivory-subtle disabled:opacity-30 transition-colors"
                        title="Previous match"
                        aria-label="Previous match"
                      >
                        <ChevronUp className="w-3.5 h-3.5 text-midnight" />
                      </button>
                      <button
                        type="button"
                        onClick={handleNextMatch}
                        disabled={totalMatches <= 1}
                        className="p-1 border border-line bg-white hover:bg-ivory-subtle disabled:opacity-30 transition-colors"
                        title="Next match"
                        aria-label="Next match"
                      >
                        <ChevronDown className="w-3.5 h-3.5 text-midnight" />
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setSearchTerm('');
                          setHighlightSnippet('');
                        }}
                        className="text-[11px] text-charcoal-muted hover:text-midnight px-1"
                      >
                        Clear
                      </button>
                    </div>
                  )}
                </div>

                {/* Font Size / Zoom Controls */}
                <div className="flex items-center space-x-1 border border-line bg-white p-0.5">
                  <button
                    onClick={() => setFontSizeLevel(Math.max(0, fontSizeLevel - 1))}
                    disabled={fontSizeLevel <= 0}
                    className="p-1 hover:bg-ivory-subtle disabled:opacity-30"
                    title="Decrease font size"
                  >
                    <ZoomOut className="w-3.5 h-3.5 text-charcoal" />
                  </button>
                  <button
                    onClick={() => setFontSizeLevel(1)}
                    className="px-1 text-[10px] font-mono text-charcoal hover:bg-ivory-subtle"
                    title="Reset font size"
                  >
                    100%
                  </button>
                  <button
                    onClick={() => setFontSizeLevel(Math.min(2, fontSizeLevel + 1))}
                    disabled={fontSizeLevel >= 2}
                    className="p-1 hover:bg-ivory-subtle disabled:opacity-30"
                    title="Increase font size"
                  >
                    <ZoomIn className="w-3.5 h-3.5 text-charcoal" />
                  </button>
                </div>

                {/* Page Navigation */}
                {totalPages > 1 && (
                  <div className="flex items-center space-x-1.5">
                    <button
                      onClick={() => setActivePageNum(Math.max(1, activePageNum - 1))}
                      disabled={activePageNum <= 1}
                      className="p-1 border border-line bg-white hover:bg-ivory-subtle disabled:opacity-40"
                      title="Previous Page"
                    >
                      <ChevronLeft className="w-4 h-4 text-midnight" />
                    </button>
                    <span className="text-[12px] text-midnight font-medium px-1">
                      {activePageNum} / {totalPages}
                    </span>
                    <button
                      onClick={() => setActivePageNum(Math.min(totalPages, activePageNum + 1))}
                      disabled={activePageNum >= totalPages}
                      className="p-1 border border-line bg-white hover:bg-ivory-subtle disabled:opacity-40"
                      title="Next Page"
                    >
                      <ChevronRight className="w-4 h-4 text-midnight" />
                    </button>
                  </div>
                )}
              </div>

              {/* Clean Paper-Like Reading Surface */}
              <div 
                ref={documentTextRef}
                className="p-8 sm:p-12 min-h-[640px] max-h-[780px] overflow-y-auto bg-white select-text border-b border-line shadow-inner"
              >
                {currentPageData.text ? (
                  renderDocumentText(currentPageData.text)
                ) : (
                  <p className="text-charcoal-muted italic text-center py-16">
                    No text detected on Page {activePageNum}.
                  </p>
                )}
              </div>

              {/* Bottom Document Status Bar */}
              <div className="p-3 bg-ivory flex items-center justify-between text-[12px] text-charcoal-muted">
                <span>Page {activePageNum} of {totalPages}</span>
                {highlightSnippet && (
                  <span className="text-crimson font-medium truncate max-w-sm">
                    Active highlight: "{highlightSnippet.slice(0, 35)}..."
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* ============================================================== */}
          {/* RIGHT COLUMN (5 COLS): EXTRACTED INTELLIGENCE PANEL            */}
          {/* ============================================================== */}
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-white border border-line p-5 shadow-subtle space-y-4">
              <div>
                <h2 className="text-[15px] font-bold text-midnight uppercase tracking-wider">
                  Extracted Intelligence
                </h2>
                <p className="text-[12px] text-charcoal-muted mt-0.5">
                  Click any element to locate and highlight it in the source text.
                </p>
              </div>

              {/* Category Filter Tabs */}
              <div className="flex flex-wrap gap-1 border-b border-line pb-3 text-[12px]">
                {[
                  { id: 'clauses', label: `Clauses (${clauses.filter(c => c.status === 'Found').length})` },
                  { id: 'obligations', label: `Obligations (${obligations.length})` },
                  { id: 'facts', label: `Dates & Money (${(facts.dates?.length || 0) + (facts.money?.length || 0)})` },
                  { id: 'entities', label: `Entities (${entities.length})` },
                  { id: 'keywords', label: `Keywords (${keywords.length})` }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-2.5 py-1 text-[12px] font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-midnight text-white'
                        : 'bg-ivory text-charcoal hover:bg-line'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Intelligence Stream Container */}
              <div className="space-y-3 max-h-[640px] overflow-y-auto pr-1 text-[13px]">
                
                {/* 1. CLAUSES */}
                {activeTab === 'clauses' && (
                  <div className="space-y-2.5">
                    {clauses.filter(c => c.status === 'Found').map((clause, idx) => (
                      <div
                        key={idx}
                        onClick={() => handleJumpToSource(clause.relevant_text, clause.page_number)}
                        className="p-3 bg-ivory border border-line hover:border-midnight cursor-pointer transition-colors space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-midnight text-[14px]">
                            {clause.clause_type}
                          </span>
                          <span className="text-[11px] text-crimson font-medium hover:underline">
                            Find in Doc →
                          </span>
                        </div>
                        <p className="text-charcoal-body text-[12px] line-clamp-2 leading-relaxed">
                          {clause.summary || clause.relevant_text}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {/* 2. OBLIGATIONS */}
                {activeTab === 'obligations' && (
                  <div className="space-y-2.5">
                    {obligations.map((ob, idx) => (
                      <div
                        key={idx}
                        onClick={() => handleJumpToSource(ob.obligation_text, ob.page_number)}
                        className="p-3 bg-ivory border border-line hover:border-midnight cursor-pointer transition-colors space-y-1"
                      >
                        <div className="flex items-center justify-between text-[12px]">
                          <span className="font-bold text-midnight uppercase tracking-wider">
                            {ob.responsible_party || 'Party'}
                          </span>
                          <span className="text-[11px] text-crimson font-medium hover:underline">
                            Find in Doc →
                          </span>
                        </div>
                        <p className="text-charcoal-body text-[12px] line-clamp-2 leading-relaxed">
                          {ob.obligation_text}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                {/* 3. DATES & MONEY */}
                {activeTab === 'facts' && (
                  <div className="space-y-4">
                    {facts.money?.length > 0 && (
                      <div className="space-y-2">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-charcoal-muted block">
                          Monetary Commitments
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {facts.money.map((m, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleJumpToSource(m.value, m.page_number)}
                              className="px-2.5 py-1 bg-ivory border border-line hover:border-midnight text-[13px] font-bold text-crimson transition-colors"
                            >
                              {m.value}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {facts.dates?.length > 0 && (
                      <div className="space-y-2">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-charcoal-muted block">
                          Critical Dates
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {facts.dates.map((d, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleJumpToSource(d.value, d.page_number)}
                              className="px-2.5 py-1 bg-ivory border border-line hover:border-midnight text-[13px] font-medium text-midnight transition-colors"
                            >
                              {d.value}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* 4. ENTITIES */}
                {activeTab === 'entities' && (
                  <div className="flex flex-wrap gap-1.5">
                    {entities.slice(0, 35).map((ent, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleJumpToSource(ent.entity_text || ent.normalized_text, ent.page_number)}
                        className="px-2.5 py-1 bg-ivory border border-line hover:border-midnight text-[12px] text-charcoal transition-colors"
                      >
                        <span className="font-medium">{ent.entity_text || ent.normalized_text}</span>
                        {ent.entity_type && (
                          <span className="ml-1 text-[10px] text-charcoal-muted">
                            ({ent.entity_type})
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                )}

                {/* 5. KEYWORDS */}
                {activeTab === 'keywords' && (
                  <div className="flex flex-wrap gap-1.5">
                    {keywords.slice(0, 35).map((kw, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleJumpToSource(kw.keyword)}
                        className="px-2.5 py-1 bg-ivory border border-line hover:border-midnight text-[12px] text-charcoal transition-colors"
                      >
                        {kw.keyword}
                      </button>
                    ))}
                  </div>
                )}

              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
