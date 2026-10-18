import React, { useState } from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

export default function AppShell({ 
  children, 
  currentPage, 
  onNavigate, 
  healthStatus, 
  onQuickUpload 
}) {
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-ivory flex">
      {/* Sidebar (Desktop ~256px, drawer on mobile) */}
      <Sidebar
        currentPage={currentPage}
        onNavigate={onNavigate}
        isMobileOpen={isMobileOpen}
        onCloseMobile={() => setIsMobileOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        <TopBar
          onOpenMobile={() => setIsMobileOpen(true)}
          healthStatus={healthStatus}
          onQuickUpload={onQuickUpload}
          currentPage={currentPage}
        />

        {/* Content Viewport with intelligent grid and sensible padding */}
        <main className="flex-1 p-6 sm:p-8 lg:p-10 max-w-[1560px] w-full mx-auto">
          {children}
        </main>

        {/* Professional Quiet Legal Footer */}
        <footer className="border-t border-line py-5 px-6 sm:px-10 text-[12px] text-charcoal-muted flex flex-col sm:flex-row items-center justify-between gap-2 max-w-[1560px] w-full mx-auto">
          <div>
            LexExtract Legal Intelligence Workspace • Automated Information Extraction
          </div>
          <div className="text-[11px] text-charcoal-subtle">
            Confidential attorney-client workflow • ISO/IEC compliant local session boundary
          </div>
        </footer>
      </div>
    </div>
  );
}
