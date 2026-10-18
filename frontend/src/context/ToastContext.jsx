import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from 'lucide-react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now() + Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);

    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    }
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Toast Notification Container */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col space-y-2.5 max-w-md w-full pointer-events-none px-4 sm:px-0">
        {toasts.map((toast) => {
          let bgColor = 'bg-white border-line text-charcoal';
          let icon = <Info className="w-4 h-4 text-midnight shrink-0 mt-0.5" />;

          if (toast.type === 'success') {
            bgColor = 'bg-white border-legalgreen/40 text-charcoal shadow-elevated';
            icon = <CheckCircle2 className="w-4 h-4 text-legalgreen shrink-0 mt-0.5" />;
          } else if (toast.type === 'error') {
            bgColor = 'bg-white border-legalred/40 text-charcoal shadow-elevated';
            icon = <AlertCircle className="w-4 h-4 text-legalred shrink-0 mt-0.5" />;
          } else if (toast.type === 'warning') {
            bgColor = 'bg-white border-legalamber/40 text-charcoal shadow-elevated';
            icon = <AlertTriangle className="w-4 h-4 text-legalamber shrink-0 mt-0.5" />;
          }

          return (
            <div
              key={toast.id}
              className={`pointer-events-auto p-4 border flex items-start space-x-3 transition-all transform translate-y-0 opacity-100 shadow-elevated animate-in fade-in slide-in-from-bottom-2 ${bgColor}`}
            >
              {icon}
              <div className="flex-1 text-[13px] leading-snug font-medium text-charcoal">
                {toast.message}
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-charcoal-muted hover:text-charcoal transition-colors p-0.5"
                aria-label="Close notification"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    return { showToast: (msg) => console.log('Toast:', msg) };
  }
  return context;
}
