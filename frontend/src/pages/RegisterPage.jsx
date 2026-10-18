import React, { useState } from 'react';
import { UserPlus, Lock, Mail, User, ShieldCheck, ArrowRight, AlertCircle, CheckCircle2, Scale } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage({ onSwitchToLogin }) {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    fullName: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setIsSubmitting(true);
    const result = await register({
      full_name: formData.fullName.trim(),
      username: formData.username.trim().toLowerCase(),
      email: formData.email.trim().toLowerCase(),
      password: formData.password
    });
    setIsSubmitting(false);

    if (result.success) {
      setSuccess(true);
    } else {
      setError(result.error);
    }
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
            <h2 className="text-xl font-bold text-midnight tracking-tight">Create Account</h2>
            <p className="text-[12px] text-charcoal-muted">LexExtract Legal Intelligence Portal</p>
          </div>
        </div>

        {success ? (
          <div className="p-6 bg-legalgreen-subtle border border-legalgreen-border text-center space-y-4">
            <CheckCircle2 className="w-10 h-10 text-legalgreen mx-auto" />
            <h3 className="text-base font-bold text-midnight">Registration Successful</h3>
            <p className="text-[13px] text-charcoal-muted">
              Your account has been created with role <span className="font-semibold text-midnight">USER</span>. You may now sign in.
            </p>
            <button
              onClick={() => onSwitchToLogin(formData.email || formData.username)}
              className="btn-primary w-full py-2.5 text-[14px]"
            >
              Proceed to Sign In
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 bg-legalred-subtle border border-legalred-border text-[13px] text-legalred flex items-start space-x-2">
                <AlertCircle className="w-4 h-4 text-legalred shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-[12px] font-semibold text-midnight mb-1">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-charcoal-subtle absolute left-3 top-2.5" />
                <input
                  type="text"
                  required
                  value={formData.fullName}
                  onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                  placeholder="e.g. Adv. Rajesh Sharma"
                  className="input-clean pl-9"
                />
              </div>
            </div>

            <div>
              <label className="block text-[12px] font-semibold text-midnight mb-1">
                Username
              </label>
              <div className="relative">
                <ShieldCheck className="w-4 h-4 text-charcoal-subtle absolute left-3 top-2.5" />
                <input
                  type="text"
                  required
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="e.g. rajesh_sharma"
                  className="input-clean pl-9"
                />
              </div>
            </div>

            <div>
              <label className="block text-[12px] font-semibold text-midnight mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-charcoal-subtle absolute left-3 top-2.5" />
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="e.g. lawyer@example.com"
                  className="input-clean pl-9"
                />
              </div>
            </div>

            <div>
              <label className="block text-[12px] font-semibold text-midnight mb-1">
                Password (min. 8 characters)
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-charcoal-subtle absolute left-3 top-2.5" />
                <input
                  type="password"
                  required
                  minLength={8}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="••••••••"
                  className="input-clean pl-9"
                />
              </div>
            </div>

            <div>
              <label className="block text-[12px] font-semibold text-midnight mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-charcoal-subtle absolute left-3 top-2.5" />
                <input
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
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
                <span>{isSubmitting ? 'Creating Account...' : 'Register Account'}</span>
                <ArrowRight className="w-4 h-4 text-gold-light" />
              </button>
            </div>

            <div className="border-t border-line pt-4 text-center">
              <p className="text-[13px] text-charcoal-muted">
                Already registered?{' '}
                <button
                  type="button"
                  onClick={onSwitchToLogin}
                  className="text-crimson font-semibold hover:underline"
                >
                  Sign In to Portal
                </button>
              </p>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
