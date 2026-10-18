import React from 'react';

export default function StatCard({ label, value, subtext, icon: Icon, color = 'navy', badge }) {
  const colorMap = {
    navy: {
      border: 'border-legal-navy/30',
      iconBg: 'bg-legal-navy/10 text-legal-navy',
      text: 'text-legal-navy'
    },
    burgundy: {
      border: 'border-legal-burgundy/30',
      iconBg: 'bg-legal-burgundy/10 text-legal-burgundy',
      text: 'text-legal-burgundy'
    },
    gold: {
      border: 'border-legal-gold/50',
      iconBg: 'bg-legal-gold/15 text-legal-gold-dark',
      text: 'text-legal-navy'
    },
    emerald: {
      border: 'border-emerald-600/30',
      iconBg: 'bg-emerald-50 text-emerald-800',
      text: 'text-emerald-900'
    }
  };

  const scheme = colorMap[color] || colorMap.navy;

  return (
    <div className={`p-4 bg-white border border-legal-border rounded-none shadow-sm hover:border-legal-border-warm transition-colors`}>
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-legal-charcoal-muted">
          {label}
        </span>
        {Icon && (
          <div className={`p-1.5 rounded-none ${scheme.iconBg}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-2 flex items-baseline justify-between">
        <span className={`text-2xl font-bold font-serif ${scheme.text}`}>
          {value}
        </span>
        {badge && (
          <span className="text-[10px] font-mono px-1.5 py-0.5 bg-legal-parchment-dark border border-legal-border text-legal-charcoal-muted">
            {badge}
          </span>
        )}
      </div>

      {subtext && (
        <p className="text-[11px] text-legal-charcoal-subtle mt-1.5 border-t border-legal-border-warm/60 pt-1.5">
          {subtext}
        </p>
      )}
    </div>
  );
}
