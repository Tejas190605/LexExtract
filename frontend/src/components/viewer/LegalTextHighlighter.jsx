import React, { useMemo } from 'react';

export default function LegalTextHighlighter({
  text = '',
  pages = [],
  activePageNumber = 1,
  keywords = [],
  entities = [],
  selectedItem = null,
  onSelectItem,
  searchTerm = '',
  activeFilters = { keywords: true, entities: true }
}) {
  // Determine display text (either current page text or full text)
  const currentText = useMemo(() => {
    if (pages && pages.length > 0) {
      const pageObj = pages.find((p) => p.page_number === activePageNumber);
      return pageObj ? pageObj.text : (pages[0]?.text || text);
    }
    return text || '';
  }, [text, pages, activePageNumber]);

  // Color mapping by category / entity type
  const getHighlightStyle = (type, isSelected) => {
    const baseSelected = isSelected ? 'ring-2 ring-legal-navy shadow-xs font-semibold' : '';
    switch (type) {
      case 'SEARCH_MATCH':
        return `bg-amber-300 text-amber-950 font-bold border-b-2 border-amber-600 px-0.5 rounded-xs ring-2 ring-amber-400 ${baseSelected}`;
      case 'KEYWORD':
        return `bg-amber-100 text-amber-950 border-b-2 border-amber-400 hover:bg-amber-200 ${baseSelected}`;
      case 'COURT':
        return `bg-purple-100 text-purple-950 border-b-2 border-purple-400 hover:bg-purple-200 ${baseSelected}`;
      case 'ACT':
      case 'LAW':
        return `bg-indigo-100 text-indigo-950 border-b-2 border-indigo-400 hover:bg-indigo-200 ${baseSelected}`;
      case 'SECTION':
      case 'ARTICLE':
      case 'CASE_REFERENCE':
        return `bg-blue-100 text-blue-950 border-b-2 border-blue-400 hover:bg-blue-200 ${baseSelected}`;
      case 'MONEY':
        return `bg-emerald-100 text-emerald-950 border-b-2 border-emerald-400 hover:bg-emerald-200 ${baseSelected}`;
      case 'DATE':
        return `bg-slate-200 text-slate-900 border-b-2 border-slate-400 hover:bg-slate-300 ${baseSelected}`;
      case 'PERSON':
      case 'LEGAL_ROLE':
        return `bg-rose-100 text-rose-950 border-b-2 border-rose-400 hover:bg-rose-200 ${baseSelected}`;
      default:
        return `bg-yellow-100 text-yellow-950 border-b-2 border-yellow-400 hover:bg-yellow-200 ${baseSelected}`;
    }
  };

  // Build match terms
  const tokenMap = useMemo(() => {
    const tokens = [];

    // Add search term if provided (highest precedence)
    if (searchTerm && searchTerm.trim().length > 1) {
      tokens.push({
        term: searchTerm.trim(),
        type: 'SEARCH_MATCH',
        category: 'search',
        data: { text: searchTerm.trim(), entity_type: 'SEARCH_MATCH' }
      });
    }

    // Add entities
    if (activeFilters.entities && entities && entities.length > 0) {
      entities.forEach((ent) => {
        const term = ent.text || ent.normalized_text;
        if (term && term.length > 1) {
          tokens.push({
            term,
            type: ent.entity_type,
            category: 'entity',
            data: ent
          });
        }
      });
    }

    // Add keywords
    if (activeFilters.keywords && keywords && keywords.length > 0) {
      keywords.forEach((kw) => {
        const term = kw.keyword;
        if (term && term.length > 1) {
          // Avoid duplicate if already covered by entity
          const exists = tokens.some((t) => t.term.toLowerCase() === term.toLowerCase());
          if (!exists) {
            tokens.push({
              term,
              type: 'KEYWORD',
              category: 'keyword',
              data: kw
            });
          }
        }
      });
    }

    // Sort tokens by length descending so longer phrases match first
    return tokens.sort((a, b) => b.term.length - a.term.length);
  }, [keywords, entities, activeFilters]);

  // Highlight the current text
  const renderedContent = useMemo(() => {
    if (!currentText || tokenMap.length === 0) {
      return (
        <span className="whitespace-pre-wrap leading-relaxed text-legal-charcoal font-serif text-sm">
          {currentText || 'No text content available.'}
        </span>
      );
    }

    // Escape regex characters
    const escapeRegex = (s) => s.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');

    // Build combined regex with word boundaries
    const termsPattern = tokenMap
      .map((t) => `(?:\\b${escapeRegex(t.term)}\\b)`)
      .join('|');

    if (!termsPattern) {
      return (
        <span className="whitespace-pre-wrap leading-relaxed text-legal-charcoal font-serif text-sm">
          {currentText}
        </span>
      );
    }

    let regex;
    try {
      regex = new RegExp(`(${termsPattern})`, 'gi');
    } catch {
      return (
        <span className="whitespace-pre-wrap leading-relaxed text-legal-charcoal font-serif text-sm">
          {currentText}
        </span>
      );
    }

    const parts = currentText.split(regex);

    return parts.map((part, index) => {
      const lowerPart = part.toLowerCase();
      const match = tokenMap.find((t) => t.term.toLowerCase() === lowerPart);

      if (match) {
        const isSelected = selectedItem && 
          (selectedItem.term?.toLowerCase() === lowerPart || 
           selectedItem.data?.text?.toLowerCase() === lowerPart ||
           selectedItem.data?.keyword?.toLowerCase() === lowerPart);

        return (
          <mark
            key={`highlight-${index}-${part}`}
            onClick={() => onSelectItem && onSelectItem(match)}
            title={`${match.type}: Click to inspect intelligence details`}
            className={`cursor-pointer px-1 py-0.5 rounded-none text-xs transition-all ${getHighlightStyle(match.type, isSelected)}`}
          >
            {part}
          </mark>
        );
      }

      return (
        <span key={`text-${index}`} className="whitespace-pre-wrap text-legal-charcoal font-serif text-sm leading-relaxed">
          {part}
        </span>
      );
    });
  }, [currentText, tokenMap, selectedItem, onSelectItem]);

  return (
    <div className="bg-white p-6 sm:p-8 border border-legal-border shadow-xs font-serif leading-relaxed text-legal-charcoal select-text">
      {renderedContent}
    </div>
  );
}
