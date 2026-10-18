import React from 'react';
import { Menu, Plus, ShieldCheck, Activity } from 'lucide-react';

export default function TopBar({ onOpenMobile, healthStatus, onQuickUpload, currentPage }) {
  const getPageTitle = (page) => {
    switch (page) {
      case 'dashboard': return 'Workspace';
      case 'new_analysis': return 'Document Analysis Intake';
      case 'results': return 'Analysis Results';
      case 'viewer': return 'Document Viewer';
      case 'history': return 'Documents';
      case 'compare': return 'Compare';
      case 'admin_users': return 'Users';
      case 'admin_audit': return 'Audit Log';
      default: return 'Workspace';
    }
  };

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/95 backdrop-blur-xs border-b border-line px-4 sm:px-8 flex items-center justify-between">
      {/* Left: Mobile Toggle & Page Context */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onOpenMobile}
          className="lg:hidden p-2 text-charcoal hover:bg-ivory-subtle transition-colors"
          aria-label="Open Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2.5">
          <span className="text-[14px] font-semibold text-midnight tracking-tight">
            {getPageTitle(currentPage)}
          </span>
          <span className="hidden sm:inline-block text-line-dark">/</span>
          <span className="hidden sm:inline-block text-[12px] text-charcoal-muted">
            LexExtract Legal Engine
          </span>
        </div>
      </div>

      {/* Right: Quick Action & Connection Status */}
      <div className="flex items-center space-x-4">
        {/* Subtle Online Status Dot */}
        <div className="hidden sm:flex items-center space-x-1.5 text-[12px] text-charcoal-muted">
          <span className={`w-2 h-2 rounded-full ${healthStatus?.status === 'online' ? 'bg-legalgreen' : 'bg-legalamber'}`} />
          <span className="font-medium">
            {healthStatus?.status === 'online' ? 'System Ready' : 'Connecting...'}
          </span>
        </div>

        {/* Quick CTA button */}
        {onQuickUpload && currentPage !== 'new_analysis' && (
          <button
            onClick={onQuickUpload}
            className="btn-primary py-2 px-3.5 text-[13px]"
          >
            <Plus className="w-4 h-4 text-gold-light" />
            <span>+ Analyze Document</span>
          </button>
        )}
      </div>
    </header>
  );
}
