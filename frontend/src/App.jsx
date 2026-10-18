import React, { useState, useEffect } from 'react';
import { Scale, ShieldAlert } from 'lucide-react';
import { checkHealth, getApiInfo } from './services/api';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';

// Layout
import AppShell from './components/layout/AppShell';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import NewAnalysisPage from './pages/NewAnalysisPage';
import AnalysisResultsPage from './pages/AnalysisResultsPage';
import DocumentViewerPage from './pages/DocumentViewerPage';
import DocumentHistoryPage from './pages/DocumentHistoryPage';
import DocumentComparePage from './pages/DocumentComparePage';
import EvaluationPage from './pages/EvaluationPage';
import AdminAuditPage from './pages/AdminAuditPage';
import AnalysisErrorBoundary from './components/common/AnalysisErrorBoundary';

function AppContent() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [authView, setAuthView] = useState('login'); // 'login' | 'register'
  const [registeredIdentifier, setRegisteredIdentifier] = useState('');
  const [healthStatus, setHealthStatus] = useState({ status: 'checking', message: 'Checking backend...' });
  const [apiInfo, setApiInfo] = useState(null);

  const [activeDocumentId, setActiveDocumentId] = useState(null);
  const [activeAnalysisId, setActiveAnalysisId] = useState(null);
  const [viewerSearch, setViewerSearch] = useState('');
  const [viewerPage, setViewerPage] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const verifyBackendConnection = async () => {
      try {
        const health = await checkHealth();
        const info = await getApiInfo();
        if (isMounted) {
          setHealthStatus({ status: 'online', message: health.status });
          setApiInfo(info);
        }
      } catch (err) {
        if (isMounted) {
          setHealthStatus({ status: 'offline', message: 'Backend unreachable' });
        }
      }
    };

    verifyBackendConnection();
    const interval = setInterval(verifyBackendConnection, 30000);
    return () => { 
      isMounted = false; 
      clearInterval(interval);
    };
  }, []);

  // Role helpers
  const userRole = user ? (user.role || 'USER').toUpperCase() : 'ANONYMOUS';
  const isAdmin = userRole === 'ADMIN';
  const isAnalystOrAdmin = userRole === 'ANALYST' || userRole === 'ADMIN';

  const handleNavigateToViewer = (docId, options = null) => {
    setActiveDocumentId(docId);
    if (options && options.search) {
      setViewerSearch(options.search);
    } else {
      setViewerSearch('');
    }
    if (options && options.page) {
      setViewerPage(options.page);
    } else {
      setViewerPage(null);
    }
    setCurrentPage('viewer');
  };

  const handleNavigateToResults = (analysisId, docId) => {
    setActiveAnalysisId(analysisId);
    if (docId) setActiveDocumentId(docId);
    setCurrentPage('results');
  };

  const handleNavigateToIntake = () => {
    setCurrentPage('new_analysis');
  };

  const handleNavigateToHistory = () => {
    setCurrentPage('history');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-legal-parchment">
        <div className="text-center space-y-3">
          <Scale className="w-10 h-10 text-legal-navy animate-pulse mx-auto" />
          <p className="text-xs uppercase tracking-widest font-semibold text-legal-charcoal">
            Verifying Authentication Credentials...
          </p>
        </div>
      </div>
    );
  }

  // Unauthenticated Flow
  if (!isAuthenticated) {
    if (authView === 'register') {
      return (
        <RegisterPage 
          onSwitchToLogin={(identifier) => {
            if (identifier) setRegisteredIdentifier(identifier);
            setAuthView('login');
          }} 
        />
      );
    }
    return (
      <LoginPage 
        initialIdentifier={registeredIdentifier}
        onLoginSuccess={() => setCurrentPage('dashboard')} 
        onSwitchToRegister={() => setAuthView('register')} 
      />
    );
  }

  // Render role-protected or standard content
  const renderActivePage = () => {
    // Admin route protection
    if ((currentPage === 'admin_audit' || currentPage === 'admin_users' || currentPage === 'audit') && !isAdmin) {
      return (
        <div className="p-8 bg-white border border-legal-border text-center space-y-3 shadow-xs">
          <ShieldAlert className="w-12 h-12 text-legal-burgundy mx-auto" />
          <h3 className="text-base font-serif font-bold text-legal-navy">Access Denied (HTTP 403 Forbidden)</h3>
          <p className="text-xs text-legal-charcoal-muted max-w-md mx-auto">
            Administrative privileges required. Your enterprise role is <strong className="text-legal-navy font-mono">{userRole}</strong>.
          </p>
          <button
            onClick={() => setCurrentPage('dashboard')}
            className="px-4 py-2 bg-legal-navy text-white text-xs font-semibold uppercase tracking-wider hover:bg-legal-navy-light"
          >
            Return to Dashboard
          </button>
        </div>
      );
    }

    // Analyst/Admin evaluation protection
    if (currentPage === 'evaluation' && !isAnalystOrAdmin) {
      return (
        <div className="p-8 bg-white border border-legal-border text-center space-y-3 shadow-xs">
          <ShieldAlert className="w-12 h-12 text-legal-burgundy mx-auto" />
          <h3 className="text-base font-serif font-bold text-legal-navy">Access Denied (HTTP 403 Forbidden)</h3>
          <p className="text-xs text-legal-charcoal-muted max-w-md mx-auto">
            The Evaluation Benchmark workspace is restricted to Analyst and Administrator enterprise roles.
          </p>
          <button
            onClick={() => setCurrentPage('dashboard')}
            className="px-4 py-2 bg-legal-navy text-white text-xs font-semibold uppercase tracking-wider hover:bg-legal-navy-light"
          >
            Return to Dashboard
          </button>
        </div>
      );
    }

    switch (currentPage) {
      case 'dashboard':
        return (
          <DashboardPage
            onNavigateToIntake={handleNavigateToIntake}
            onNavigateToViewer={handleNavigateToViewer}
            onNavigateToResults={handleNavigateToResults}
            onNavigateToHistory={handleNavigateToHistory}
          />
        );
      case 'new_analysis':
        return (
          <NewAnalysisPage 
            onNavigateToViewer={handleNavigateToViewer} 
            onNavigateToResults={handleNavigateToResults} 
          />
        );
      case 'results':
        return (
          <AnalysisErrorBoundary
            key={activeAnalysisId}
            onBackToWorkspace={() => setCurrentPage('dashboard')}
          >
            <AnalysisResultsPage 
              activeAnalysisId={activeAnalysisId} 
              activeDocumentId={activeDocumentId}
              onNavigateToViewer={handleNavigateToViewer}
              onNavigateToIntake={handleNavigateToIntake}
              onNavigate={(p) => setCurrentPage(p)}
            />
          </AnalysisErrorBoundary>
        );
      case 'viewer':
        return (
          <DocumentViewerPage 
            activeDocumentId={activeDocumentId} 
            initialSearch={viewerSearch}
            initialPage={viewerPage}
            onNavigateToResults={handleNavigateToResults}
            onNavigateToIntake={handleNavigateToIntake}
          />
        );
      case 'history':
        return (
          <DocumentHistoryPage
            onNavigateToViewer={handleNavigateToViewer}
            onNavigateToResults={handleNavigateToResults}
            onNavigateToIntake={handleNavigateToIntake}
          />
        );
      case 'compare':
        return (
          <DocumentComparePage
            onNavigateToViewer={handleNavigateToViewer}
            onNavigateToIntake={handleNavigateToIntake}
          />
        );
      case 'evaluation':
        return <EvaluationPage />;
      case 'admin_users':
        return <AdminAuditPage initialTab="users" />;
      case 'admin_audit':
      case 'audit':
        return <AdminAuditPage initialTab="audit" />;
      default:
        return (
          <DashboardPage
            onNavigateToIntake={handleNavigateToIntake}
            onNavigateToViewer={handleNavigateToViewer}
            onNavigateToResults={handleNavigateToResults}
            onNavigateToHistory={handleNavigateToHistory}
            onNavigate={(p) => setCurrentPage(p)}
          />
        );
    }
  };

  return (
    <AppShell
      currentPage={currentPage}
      onNavigate={(pageId) => setCurrentPage(pageId)}
      healthStatus={healthStatus}
      onQuickUpload={handleNavigateToIntake}
    >
      {renderActivePage()}
    </AppShell>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ToastProvider>
  );
}
