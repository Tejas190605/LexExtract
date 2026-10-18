import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ message = 'Loading legal document intelligence data...', subtext }) {
  return (
    <div className="p-16 bg-white border border-legal-border text-center space-y-3 shadow-sm my-4">
      <Loader2 className="w-8 h-8 animate-spin text-legal-burgundy mx-auto" />
      <p className="text-xs font-semibold uppercase tracking-widest text-legal-navy">
        {message}
      </p>
      {subtext && (
        <p className="text-[11px] text-legal-charcoal-subtle max-w-sm mx-auto">
          {subtext}
        </p>
      )}
    </div>
  );
}
