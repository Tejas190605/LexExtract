import React from 'react';
import { X, ShieldCheck, Tag, Layers, Scale, Sparkles, BookOpen, ChevronRight } from 'lucide-react';

export default function EntityContextDrawer({ item, onClose, onNavigateToAnalysis }) {
  if (!item) return null;

  const isEntity = item.category === 'entity';
  const data = item.data || {};

  const termTitle = item.term || data.text || data.keyword || 'Selected Legal Item';
  const itemType = item.type || data.entity_type || 'KEYWORD';

  const getSourceLabel = (src) => {
    switch ((src || '').toLowerCase()) {
      case 'hybrid': return 'Hybrid Consensus (spaCy + Statutory Rule)';
      case 'spacy': return 'Statistical Named Entity Recognition (spaCy NER)';
      case 'regex': return 'Statutory Regular Expression Pattern';
      case 'dictionary': return 'Domain Legal Gazetteer / Ontological Lexicon';
      default: return 'Rule-Based Extractor';
    }
  };

  const getConfidenceBadge = (conf) => {
    const score = typeof conf === 'number' ? conf : 1.0;
    const pct = Math.round(score * 100);
    let color = 'bg-emerald-100 text-emerald-800 border-emerald-300';
    if (score < 0.8) color = 'bg-amber-100 text-amber-800 border-amber-300';
    if (score < 0.6) color = 'bg-rose-100 text-rose-800 border-rose-300';

    return (
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs">
          <span className="text-legal-charcoal-muted font-medium">Confidence Score:</span>
          <span className={`px-2 py-0.5 font-bold font-mono text-[11px] border ${color}`}>
            {score.toFixed(2)} ({pct}%)
          </span>
        </div>
        <div className="w-full bg-slate-100 h-1.5 border border-slate-200">
          <div 
            className="bg-legal-gold h-full transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="p-4 bg-white border border-legal-border shadow-sm space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-legal-border pb-3">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-legal-navy text-legal-gold">
            {isEntity ? <Scale className="w-4 h-4" /> : <Layers className="w-4 h-4" />}
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-legal-burgundy block">
              {isEntity ? 'Extracted Legal Entity' : 'Ranked Legal Keyword'}
            </span>
            <h4 className="text-sm font-bold font-serif text-legal-navy">
              {termTitle}
            </h4>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600 p-1 transition-colors"
          title="Close Inspector Drawer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Attributes Grid */}
      <div className="space-y-3 text-xs">
        {/* Type / Category */}
        <div className="flex items-center justify-between p-2 bg-legal-parchment-dark border border-legal-border-warm">
          <span className="text-legal-charcoal-muted font-semibold uppercase tracking-wider text-[10px]">
            {isEntity ? 'Entity Classification' : 'Keyword Domain'}
          </span>
          <span className="font-bold text-legal-navy px-2 py-0.5 bg-white border border-legal-border text-[11px]">
            {itemType}
          </span>
        </div>

        {/* Confidence or Score */}
        {isEntity ? (
          getConfidenceBadge(data.confidence)
        ) : (
          <div className="space-y-1.5 p-2 bg-slate-50 border border-slate-200">
            <div className="flex items-center justify-between text-xs">
              <span className="text-legal-charcoal-muted font-semibold">Composite Score:</span>
              <span className="font-bold font-mono text-legal-burgundy">
                {(data.final_score || data.score || 0).toFixed(4)}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-1 pt-1 text-[10px] text-center border-t border-slate-200">
              <div>
                <span className="text-slate-400 block uppercase">Frequency</span>
                <span className="font-mono font-semibold">{(data.tfidf_score || 0).toFixed(2)}</span>
              </div>
              <div>
                <span className="text-slate-400 block uppercase">Phrase</span>
                <span className="font-mono font-semibold">{(data.rake_score || 0).toFixed(2)}</span>
              </div>
              <div>
                <span className="text-slate-400 block uppercase">Lexicon</span>
                <span className="font-mono font-semibold">{(data.lexicon_score || 0).toFixed(2)}</span>
              </div>
            </div>
          </div>
        )}

        {/* Provenance Source */}
        {isEntity && (
          <div>
            <span className="text-[10px] font-semibold text-legal-charcoal-muted uppercase tracking-wider block mb-1">
              Provenance Channel
            </span>
            <div className="p-2 bg-slate-50 border border-slate-200 text-legal-charcoal text-[11px] leading-relaxed flex items-center space-x-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-legal-navy shrink-0" />
              <span>{getSourceLabel(data.source)}</span>
            </div>
          </div>
        )}

        {/* Normalized Form if different */}
        {data.normalized_text && data.normalized_text !== termTitle && (
          <div>
            <span className="text-[10px] font-semibold text-legal-charcoal-muted uppercase tracking-wider block mb-1">
              Normalized Citation
            </span>
            <div className="p-2 bg-slate-50 border border-slate-200 text-legal-charcoal text-[11px] font-mono">
              {data.normalized_text}
            </div>
          </div>
        )}

        {/* Frequency */}
        {data.frequency && (
          <div className="flex items-center justify-between text-xs pt-1 border-t border-legal-border-warm text-legal-charcoal-muted">
            <span>Document Occurrences:</span>
            <span className="font-bold text-legal-navy">{data.frequency}</span>
          </div>
        )}
      </div>

      {onNavigateToAnalysis && (
        <button
          onClick={onNavigateToAnalysis}
          className="w-full py-2 bg-legal-navy hover:bg-legal-navy-light text-white text-xs font-semibold uppercase tracking-wider transition-colors flex items-center justify-center space-x-1"
        >
          <span>View In Results Workspace</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
