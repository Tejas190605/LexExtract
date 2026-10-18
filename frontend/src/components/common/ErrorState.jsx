import React from 'react';
import { AlertCircle, RotateCw, ArrowLeft } from 'lucide-react';

export default function ErrorState({ title = 'Operation Failed', error, onRetry, onBack }) {
  const message = typeof error === 'string'
    ? error
    : (error?.response?.data?.detail || error?.message || 'An unexpected server error occurred.');

  return (
    <div className="p-8 bg-white border-l-4 border-rose-600 border-r border-t border-b border-legal-border text-center space-y-3 shadow-sm my-4">
      <AlertCircle className="w-10 h-10 text-rose-600 mx-auto" />
      <h3 className="text-base font-serif font-bold text-legal-navy">
        {title}
      </h3>
      <p className="text-xs text-rose-800 max-w-lg mx-auto bg-rose-50 p-2.5 border border-rose-200">
        {message}
      </p>
      <div className="flex items-center justify-center space-x-3 pt-2">
        {onBack && (
          <button
            onClick={onBack}
            className="px-3.5 py-1.5 bg-white border border-legal-border hover:bg-slate-50 text-legal-navy text-xs font-semibold uppercase tracking-wider inline-flex items-center space-x-1.5"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Go Back</span>
          </button>
        )}
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-3.5 py-1.5 bg-legal-navy hover:bg-legal-navy-light text-white text-xs font-semibold uppercase tracking-wider inline-flex items-center space-x-1.5"
          >
            <RotateCw className="w-3.5 h-3.5" />
            <span>Retry Operation</span>
          </button>
        )}
      </div>
    </div>
  );
}
