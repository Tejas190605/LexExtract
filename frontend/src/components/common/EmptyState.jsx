import React from 'react';
import { FileQuestion } from 'lucide-react';

export default function EmptyState({ icon: Icon = FileQuestion, title, description, actionLabel, onAction }) {
  return (
    <div className="p-12 bg-white border border-legal-border text-center space-y-3 shadow-sm my-4">
      <div className="w-12 h-12 bg-legal-parchment-dark text-legal-charcoal-muted flex items-center justify-center mx-auto border border-legal-border-warm">
        <Icon className="w-6 h-6 text-legal-charcoal-subtle" />
      </div>
      <h3 className="text-base font-serif font-bold text-legal-navy tracking-tight">
        {title}
      </h3>
      {description && (
        <p className="text-xs text-legal-charcoal-muted max-w-md mx-auto leading-relaxed">
          {description}
        </p>
      )}
      {actionLabel && onAction && (
        <div className="pt-2">
          <button
            onClick={onAction}
            className="px-4 py-2 bg-legal-navy hover:bg-legal-navy-light text-white text-xs font-semibold uppercase tracking-wider transition-colors inline-flex items-center space-x-1.5"
          >
            <span>{actionLabel}</span>
          </button>
        </div>
      )}
    </div>
  );
}
