import React, { useState } from 'react';
import { 
  Scale, 
  Home, 
  Files, 
  GitCompare, 
  PlusCircle, 
  Users, 
  ShieldAlert, 
  LogOut, 
  Settings, 
  X,
  User,
  ShieldCheck,
  Calendar,
  CheckCircle2
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Sidebar({ currentPage, onNavigate, isMobileOpen, onCloseMobile }) {
  const { user, logout } = useAuth();
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const userRole = (user?.role || 'USER').toUpperCase();
  const isAdmin = userRole === 'ADMIN';

  const navItems = [
    { id: 'dashboard', label: 'Workspace', icon: Home },
    { id: 'history', label: 'Documents', icon: Files },
    { id: 'compare', label: 'Compare', icon: GitCompare },
  ];

  const adminNavItems = [
    { id: 'admin_users', label: 'Users', icon: Users },
    { id: 'admin_audit', label: 'Audit Log', icon: ShieldAlert },
  ];

  const handleNavClick = (pageId) => {
    if (onNavigate) onNavigate(pageId);
    if (onCloseMobile) onCloseMobile();
  };

  const getInitials = (name) => {
    if (!name) return 'LX';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div 
          onClick={onCloseMobile}
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside className={`
        fixed top-0 bottom-0 left-0 z-50 w-64 bg-midnight text-slate-200 border-r border-midnight-light/50 flex flex-col justify-between
        transition-transform duration-200 ease-in-out
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Top Header & Navigation */}
        <div className="flex flex-col flex-1 overflow-hidden">
          
          {/* Brand Header */}
          <div className="p-5 border-b border-white/10 flex items-center justify-between">
            <button 
              onClick={() => handleNavClick('dashboard')}
              className="flex items-center space-x-3 text-left group"
            >
              <div className="w-9 h-9 rounded bg-white/10 border border-gold/40 flex items-center justify-center shrink-0 shadow-subtle group-hover:border-gold transition-colors">
                <Scale className="w-5 h-5 text-gold" />
              </div>
              <div>
                <span className="text-[17px] font-sans font-bold tracking-wider text-white block uppercase leading-none">
                  LexExtract
                </span>
                <span className="text-[11px] text-slate-400 block tracking-normal mt-1 font-normal">
                  Legal Intelligence
                </span>
              </div>
            </button>
            {isMobileOpen && (
              <button 
                onClick={onCloseMobile}
                className="lg:hidden p-1 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Prominent Action Button: + Analyze Document */}
          <div className="p-4 border-b border-white/5">
            <button
              onClick={() => handleNavClick('new_analysis')}
              className="w-full py-2.5 px-3 bg-crimson hover:bg-crimson-hover text-white text-[13px] font-semibold flex items-center justify-center space-x-2 transition-colors shadow-subtle"
            >
              <PlusCircle className="w-4 h-4 text-gold-light" />
              <span>+ Analyze Document</span>
            </button>
          </div>

          {/* Main Navigation */}
          <nav className="p-4 space-y-6 flex-1 overflow-y-auto">
            <div className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentPage === item.id || 
                  (item.id === 'dashboard' && currentPage === 'dashboard');
                
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavClick(item.id)}
                    className={`
                      w-full flex items-center space-x-3 px-3 py-2.5 text-[14px] font-medium transition-colors text-left
                      ${isActive
                        ? 'bg-midnight-light text-white font-semibold border-l-2 border-gold shadow-subtle'
                        : 'text-slate-300 hover:text-white hover:bg-white/5 border-l-2 border-transparent'}
                    `}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-gold' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Admin Section (Only for ADMIN role) */}
            {isAdmin && (
              <div className="pt-4 border-t border-white/10 space-y-1">
                <span className="px-3 text-[10px] font-bold tracking-wider text-slate-400 uppercase block mb-1">
                  Admin
                </span>
                {adminNavItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentPage === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => handleNavClick(item.id)}
                      className={`
                        w-full flex items-center space-x-3 px-3 py-2 text-[13px] font-medium transition-colors text-left
                        ${isActive
                          ? 'bg-midnight-light text-white font-semibold border-l-2 border-gold'
                          : 'text-slate-300 hover:text-white hover:bg-white/5 border-l-2 border-transparent'}
                      `}
                    >
                      <Icon className={`w-4 h-4 ${isActive ? 'text-gold' : 'text-slate-400'}`} />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </div>
            )}
          </nav>
        </div>

        {/* Bottom User Area: Avatar, Name, Role, Settings, Logout */}
        <div className="p-4 border-t border-white/10 bg-midnight-dark/60 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5 truncate">
              <div className="w-8 h-8 rounded-full bg-midnight-light border border-white/20 flex items-center justify-center shrink-0 text-gold-light font-semibold text-xs">
                {getInitials(user?.full_name || user?.username)}
              </div>
              <div className="truncate">
                <span className="text-[13px] font-medium text-white block truncate leading-tight">
                  {user?.full_name || user?.username || 'Legal Counsel'}
                </span>
                <span className="text-[10px] uppercase font-semibold tracking-wider text-gold-light/90 block">
                  {userRole}
                </span>
              </div>
            </div>

            <button
              onClick={() => setShowProfileModal(true)}
              className="p-1.5 text-slate-400 hover:text-white hover:bg-white/5 rounded transition-colors"
              title="Account Settings"
              aria-label="Account Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>

          <button
            onClick={() => setShowLogoutConfirm(true)}
            className="w-full py-1.5 px-2.5 text-[12px] text-slate-300 hover:text-white hover:bg-white/5 border border-white/10 flex items-center justify-center space-x-2 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5 text-crimson-light" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Profile / Account Modal */}
      {showProfileModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white max-w-md w-full border border-line shadow-modal p-6 space-y-5 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <div className="flex items-center space-x-2">
                <User className="w-5 h-5 text-midnight" />
                <h3 className="text-base font-bold text-midnight">User Profile &amp; Role</h3>
              </div>
              <button
                onClick={() => setShowProfileModal(false)}
                className="text-charcoal-muted hover:text-charcoal p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-[13px]">
              <div>
                <span className="text-[11px] text-charcoal-muted uppercase block font-semibold">Full Name</span>
                <span className="font-semibold text-charcoal">{user?.full_name || '—'}</span>
              </div>
              <div>
                <span className="text-[11px] text-charcoal-muted uppercase block font-semibold">Email Address</span>
                <span className="font-mono text-charcoal">{user?.email || '—'}</span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-[11px] text-charcoal-muted uppercase block font-semibold">Enterprise Role</span>
                  <span className="inline-flex items-center space-x-1 font-semibold text-midnight">
                    <ShieldCheck className="w-3.5 h-3.5 text-gold-dark" />
                    <span>{userRole}</span>
                  </span>
                </div>
                <div>
                  <span className="text-[11px] text-charcoal-muted uppercase block font-semibold">Status</span>
                  <span className="inline-flex items-center space-x-1 text-legalgreen font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Active Verified</span>
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-2 border-t border-line flex justify-end">
              <button
                onClick={() => setShowProfileModal(false)}
                className="btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* In-app Logout Confirmation Modal */}
      {showLogoutConfirm && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white max-w-sm w-full border border-line shadow-modal p-6 space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center space-x-3 text-crimson">
              <LogOut className="w-5 h-5 shrink-0" />
              <h3 className="text-base font-bold text-midnight">Sign Out</h3>
            </div>
            <p className="text-[13px] text-charcoal">
              Are you sure you want to end your current session in LexExtract?
            </p>
            <div className="pt-2 flex justify-end space-x-2 border-t border-line">
              <button
                type="button"
                onClick={() => setShowLogoutConfirm(false)}
                className="btn-secondary py-1.5 px-3 text-[13px]"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowLogoutConfirm(false);
                  logout();
                }}
                className="bg-crimson hover:bg-crimson-hover text-white font-medium py-1.5 px-4 text-[13px] transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
