import React from 'react';

export default function PageHeader({ title, subtitle, breadcrumb, actions }) {
  return (
    <div className="border-b border-legal-border pb-4 mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        {breadcrumb && (
          <div className="text-[11px] font-mono uppercase tracking-wider text-legal-charcoal-subtle mb-1">
            {breadcrumb}
          </div>
        )}
        <h2 className="text-2xl font-bold font-serif text-legal-navy tracking-tight">
          {title}
        </h2>
        {subtitle && (
          <p className="text-xs text-legal-charcoal-muted mt-1 max-w-3xl leading-relaxed">
            {subtitle}
          </p>
        )}
      </div>

      {actions && (
        <div className="flex items-center space-x-3 shrink-0">
          {actions}
        </div>
      )}
    </div>
  );
}
