import React, { useState, useEffect } from 'react';
import { Lock, Mail, ArrowRight, AlertCircle, KeyRound, Scale, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage({ onLoginSuccess, onSwitchToRegister, initialIdentifier = '' }) {
  const { login } = useAuth();
  const [identifier, setIdentifier] = useState(initialIdentifier);
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialIdentifier) {
      setIdentifier(initialIdentifier);
    }
  }, [initialIdentifier]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const result = await login(identifier.trim(), password);
    setIsSubmitting(false);

    if (result.success) {
      if (onLoginSuccess) onLoginSuccess();
    } else {
      setError(result.error);
    }
  };

  const handleFillDemo = (demoIdentifier, demoPassword) => {
    setIdentifier(demoIdentifier);
    setPassword(demoPassword);
    setError(null);
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white border border-line p-8 shadow-elevated space-y-6">
        
        {/* Header */}
        <div className="flex items-center space-x-3.5 border-b border-line pb-5">
          <div className="w-10 h-10 rounded bg-midnight border border-gold/40 flex items-center justify-center text-gold-light shrink-0">
            <Scale className="w-5 h-5 text-gold" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-midnight tracking-tight">LexExtract</h2>
            <p className="text-[12px] text-charcoal-muted">Legal Intelligence Workspace • Access Portal</p>
          </div>
        </div>

        {/* Demo Credentials Quick-Fill Buttons */}
        <div className="p-3.5 bg-ivory border border-line text-[12px] space-y-2">
          <div className="font-semibold text-midnight flex items-center space-x-1.5">
            <KeyRound className="w-3.5 h-3.5 text-gold-dark" />
            <span>Select Demo Workspace Account:</span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => handleFillDemo('demo@lexextract.local', 'User@Lex2026!')}
              className="p-2 bg-white border border-line hover:border-midnight text-center transition-colors shadow-2xs"
            >
              <span className="block font-semibold text-midnight text-[12px]">Lawyer</span>
              <span className="text-[10px] text-charcoal-muted font-mono">USER</span>
            </button>
            <button
              type="button"
              onClick={() => handleFillDemo('analyst@lexextract.local', 'Analyst@Lex2026!')}
              className="p-2 bg-white border border-line hover:border-midnight text-center transition-colors shadow-2xs"
            >
              <span className="block font-semibold text-midnight text-[12px]">Analyst</span>
              <span className="text-[10px] text-gold-dark font-mono">ANALYST</span>
            </button>
            <button
              type="button"
              onClick={() => handleFillDemo('admin@lexextract.local', 'Admin@Lex2026!')}
              className="p-2 bg-white border border-line hover:border-midnight text-center transition-colors shadow-2xs"
            >
              <span className="block font-semibold text-midnight text-[12px]">Admin</span>
              <span className="text-[10px] text-crimson font-mono">ADMIN</span>
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {initialIdentifier && !error && (
            <div className="p-3 bg-legalgreen-subtle border border-legalgreen-border text-[13px] text-legalgreen flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-legalgreen" />
              <span>Account created. Please sign in with your password.</span>
            </div>
          )}

          {error && (
            <div className="p-3 bg-legalred-subtle border border-legalred-border text-[13px] text-legalred flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-legalred shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-[12px] font-semibold text-midnight mb-1">
              Email or Username
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-charcoal-subtle absolute left-3 top-2.5" />
              <input
                type="text"
                required
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="e.g. demo@lexextract.local or admin"
                className="input-clean pl-9"
              />
            </div>
          </div>

          <div>
            <label className="block text-[12px] font-semibold text-midnight mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-charcoal-subtle absolute left-3 top-2.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="input-clean pl-9"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-primary w-full py-2.5 text-[14px]"
            >
              <span>{isSubmitting ? 'Authenticating...' : 'Sign In to Portal'}</span>
              <ArrowRight className="w-4 h-4 text-gold-light" />
            </button>
          </div>

          <div className="border-t border-line pt-4 text-center">
            <p className="text-[13px] text-charcoal-muted">
              New legal practitioner?{' '}
              <button
                type="button"
                onClick={onSwitchToRegister}
                className="text-crimson font-semibold hover:underline"
              >
                Register New Account
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
