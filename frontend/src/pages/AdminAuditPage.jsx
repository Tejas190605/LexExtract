import React, { useState, useEffect, useCallback } from 'react';
import { 
  ShieldAlert, 
  Users, 
  FileSpreadsheet, 
  Filter, 
  RotateCw, 
  CheckCircle2, 
  AlertTriangle, 
  UserCheck, 
  UserX, 
  ShieldCheck, 
  ChevronLeft, 
  ChevronRight,
  Info
} from 'lucide-react';
import { 
  getAuditLogsAdmin, 
  listUsersAdmin, 
  updateUserStatusAdmin, 
  updateUserRoleAdmin 
} from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function AdminAuditPage({ initialTab = 'audit' }) {
  const { user: currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState(initialTab);

  useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab]); // 'audit' | 'users'

  // ===============================
  // Audit Ledger State
  // ===============================
  const [auditLogs, setAuditLogs] = useState([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [auditLoading, setAuditLoading] = useState(false);
  const [auditError, setAuditError] = useState(null);
  const [limit] = useState(25);
  const [offset, setOffset] = useState(0);

  // Filters
  const [actionFilter, setActionFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [userIdFilter, setUserIdFilter] = useState('');

  // ===============================
  // User Management State
  // ===============================
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [usersError, setUsersError] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);

  // Fetch Audit Logs
  const fetchAuditLogs = useCallback(async () => {
    setAuditLoading(true);
    setAuditError(null);
    try {
      const params = { limit, offset };
      if (actionFilter) params.action = actionFilter;
      if (statusFilter) params.status = statusFilter;
      if (userIdFilter) params.user_id = parseInt(userIdFilter, 10);

      const data = await getAuditLogsAdmin(params);
      setAuditLogs(data.logs || []);
      setTotalLogs(data.total || 0);
    } catch (err) {
      setAuditError(err.response?.data?.detail || 'Failed to fetch audit ledger records.');
    } finally {
      setAuditLoading(false);
    }
  }, [limit, offset, actionFilter, statusFilter, userIdFilter]);

  // Fetch Users
  const fetchUsers = useCallback(async () => {
    setUsersLoading(true);
    setUsersError(null);
    try {
      const data = await listUsersAdmin();
      setUsers(data || []);
    } catch (err) {
      setUsersError(err.response?.data?.detail || 'Failed to fetch user directory.');
    } finally {
      setUsersLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'audit') {
      fetchAuditLogs();
    } else {
      fetchUsers();
    }
  }, [activeTab, fetchAuditLogs, fetchUsers]);

  // Handle User Status Toggle
  const handleToggleStatus = async (targetUser) => {
    const nextStatus = !targetUser.is_active;
    const confirmMsg = nextStatus
      ? `Activate user account: ${targetUser.email}?`
      : `Deactivate user account: ${targetUser.email}? This will prevent login.`;

    if (!window.confirm(confirmMsg)) return;

    try {
      setActionMessage(null);
      await updateUserStatusAdmin(targetUser.id, nextStatus);
      setActionMessage({ type: 'success', text: `Account for ${targetUser.email} successfully ${nextStatus ? 'activated' : 'deactivated'}.` });
      fetchUsers();
    } catch (err) {
      setActionMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to update user status.' });
    }
  };

  // Handle User Role Change
  const handleChangeRole = async (targetUser, newRole) => {
    if (targetUser.role === newRole) return;
    if (!window.confirm(`Change role of ${targetUser.email} from ${targetUser.role} to ${newRole}?`)) return;

    try {
      setActionMessage(null);
      await updateUserRoleAdmin(targetUser.id, newRole);
      setActionMessage({ type: 'success', text: `Role for ${targetUser.email} changed to ${newRole}.` });
      fetchUsers();
    } catch (err) {
      setActionMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to update user role.' });
    }
  };

  const formatTimestamp = (ts) => {
    if (!ts) return '—';
    try {
      const d = new Date(ts);
      return d.toLocaleString('en-US', {
        month: 'short',
        day: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    } catch {
      return ts;
    }
  };

  const getActionBadgeColor = (action, status) => {
    if (status === 'FAILURE') return 'bg-rose-100 text-rose-800 border-rose-300';
    if (action.includes('LOGIN')) return 'bg-blue-100 text-blue-800 border-blue-300';
    if (action.includes('DOCUMENT')) return 'bg-amber-100 text-amber-800 border-amber-300';
    if (action.includes('ANALYSIS')) return 'bg-purple-100 text-purple-800 border-purple-300';
    if (action.includes('USER')) return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    return 'bg-slate-100 text-slate-800 border-slate-300';
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Context Header */}
      <div className="border-b border-line pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <ShieldAlert className="w-6 h-6 text-crimson" />
            <h2 className="text-2xl font-bold font-sans text-midnight tracking-tight">
              Enterprise Governance &amp; Administration
            </h2>
          </div>
          <p className="text-[13px] text-charcoal-muted mt-1">
            Role-based user management, permission control, and immutable security audit trail.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex space-x-1 bg-ivory p-1 border border-line">
          <button
            onClick={() => setActiveTab('audit')}
            className={`flex items-center space-x-2 px-4 py-2 text-[13px] font-semibold transition-colors ${
              activeTab === 'audit'
                ? 'bg-midnight text-white shadow-subtle'
                : 'text-charcoal hover:bg-white'
            }`}
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Audit Ledger</span>
            <span className="ml-1.5 px-1.5 py-0.2 bg-white/20 text-[11px] rounded">
              {totalLogs}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`flex items-center space-x-2 px-4 py-2 text-[13px] font-semibold transition-colors ${
              activeTab === 'users'
                ? 'bg-midnight text-white shadow-subtle'
                : 'text-charcoal hover:bg-white'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>User Directory &amp; RBAC</span>
          </button>
        </div>
      </div>

      {/* Action Notification Banner */}
      {actionMessage && (
        <div className={`p-4 border text-[13px] flex items-start space-x-3 ${
          actionMessage.type === 'success' 
            ? 'bg-legalgreen-subtle border-legalgreen-border text-legalgreen' 
            : 'bg-legalred-subtle border-legalred-border text-legalred'
        }`}>
          {actionMessage.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-legalgreen shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-legalred shrink-0 mt-0.5" />
          )}
          <div className="flex-1 font-medium">
            <span className="font-bold">{actionMessage.type === 'success' ? 'Success: ' : 'Administrative Notice: '}</span>
            {actionMessage.text}
          </div>
          <button 
            onClick={() => setActionMessage(null)}
            className="text-[12px] font-bold underline ml-2 opacity-70 hover:opacity-100"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 1: AUDIT LEDGER                                                      */}
      {/* ========================================================================= */}
      {activeTab === 'audit' && (
        <div className="space-y-4">
          {/* Controls & Filter Bar */}
          <div className="p-4 bg-white border border-line shadow-subtle flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center space-x-1.5 text-xs text-charcoal-muted">
                <Filter className="w-3.5 h-3.5 text-midnight" />
                <span className="font-semibold uppercase tracking-wider">Filters:</span>
              </div>

              {/* Action Filter */}
              <select
                value={actionFilter}
                onChange={(e) => { setActionFilter(e.target.value); setOffset(0); }}
                className="text-xs bg-ivory border border-line px-3 py-1.5 text-charcoal focus:outline-none focus:border-midnight"
              >
                <option value="">All Security Actions</option>
                <option value="LOGIN_SUCCESS">LOGIN_SUCCESS</option>
                <option value="LOGIN_FAILURE">LOGIN_FAILURE</option>
                <option value="LOGOUT">LOGOUT</option>
                <option value="REGISTER">REGISTER</option>
                <option value="DOCUMENT_UPLOAD">DOCUMENT_UPLOAD</option>
                <option value="DOCUMENT_VIEW">DOCUMENT_VIEW</option>
                <option value="ANALYSIS_START">ANALYSIS_START</option>
                <option value="ANALYSIS_COMPLETE">ANALYSIS_COMPLETE</option>
                <option value="ANALYSIS_FAILED">ANALYSIS_FAILED</option>
                <option value="KEYWORD_VIEW">KEYWORD_VIEW</option>
                <option value="ENTITY_VIEW">ENTITY_VIEW</option>
                <option value="USER_ROLE_CHANGED">USER_ROLE_CHANGED</option>
                <option value="USER_ACTIVATED">USER_ACTIVATED</option>
                <option value="USER_DEACTIVATED">USER_DEACTIVATED</option>
                <option value="UNAUTHORIZED_ACCESS">UNAUTHORIZED_ACCESS</option>
              </select>

              {/* Status Filter */}
              <select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setOffset(0); }}
                className="text-xs bg-ivory border border-line px-3 py-1.5 text-charcoal focus:outline-none focus:border-midnight"
              >
                <option value="">All Statuses</option>
                <option value="SUCCESS">SUCCESS</option>
                <option value="FAILURE">FAILURE</option>
              </select>

              {/* User ID Filter */}
              <input
                type="text"
                placeholder="User ID..."
                value={userIdFilter}
                onChange={(e) => { setUserIdFilter(e.target.value); setOffset(0); }}
                className="text-xs bg-ivory border border-line px-3 py-1.5 text-charcoal placeholder-charcoal-muted w-24 focus:outline-none focus:border-midnight"
              />
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={fetchAuditLogs}
                disabled={auditLoading}
                className="flex items-center space-x-1.5 px-3 py-1.5 bg-white hover:bg-ivory border border-line text-xs font-semibold uppercase tracking-wider text-midnight transition-colors"
              >
                <RotateCw className={`w-3.5 h-3.5 ${auditLoading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          {/* Audit Table */}
          <div className="bg-white border border-line shadow-subtle overflow-hidden">
            {auditError && (
              <div className="p-4 bg-rose-50 border-b border-rose-200 text-xs text-rose-800">
                {auditError}
              </div>
            )}

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-line text-left">
                <thead className="bg-ivory border-b border-line text-charcoal-muted text-[11px] font-semibold uppercase tracking-wider">
                  <tr>
                    <th scope="col" className="px-4 py-3">Timestamp (UTC/Local)</th>
                    <th scope="col" className="px-4 py-3">Action</th>
                    <th scope="col" className="px-4 py-3">User</th>
                    <th scope="col" className="px-4 py-3">Resource</th>
                    <th scope="col" className="px-4 py-3">Status</th>
                    <th scope="col" className="px-4 py-3">Client IP</th>
                    <th scope="col" className="px-4 py-3">Details / Audit Context</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line text-xs bg-white">
                  {auditLoading && auditLogs.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="px-4 py-8 text-center text-charcoal-muted">
                        Loading governance audit ledger...
                      </td>
                    </tr>
                  ) : auditLogs.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="px-4 py-8 text-center text-charcoal-muted">
                        No audit records found matching the active filter criteria.
                      </td>
                    </tr>
                  ) : (
                    auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-ivory/60 transition-colors">
                        <td className="px-4 py-3 whitespace-nowrap text-charcoal font-mono text-[11px]">
                          {formatTimestamp(log.timestamp)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <span className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase border rounded ${getActionBadgeColor(log.action, log.status)}`}>
                            {log.action}
                          </span>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {log.user_id ? (
                            <span className="font-semibold text-midnight">User #{log.user_id}</span>
                          ) : (
                            <span className="text-charcoal-muted italic">Unauthenticated</span>
                          )}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-charcoal-muted font-mono text-[11px]">
                          {log.resource_type ? `${log.resource_type}${log.resource_id ? ` #${log.resource_id}` : ''}` : '—'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {log.status === 'SUCCESS' ? (
                            <span className="inline-flex items-center space-x-1 text-emerald-700 font-bold text-[10px]">
                              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                              <span>SUCCESS</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center space-x-1 text-rose-700 font-bold text-[10px]">
                              <AlertTriangle className="w-3 h-3 text-rose-600" />
                              <span>FAILURE</span>
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-charcoal-muted font-mono text-[11px]">
                          {log.ip_address || '—'}
                        </td>
                        <td className="px-4 py-3 text-charcoal max-w-xs truncate" title={log.details || ''}>
                          {log.details || '—'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="p-3 bg-ivory border-t border-line flex items-center justify-between text-xs text-charcoal-muted">
              <div>
                Showing <span className="font-semibold text-charcoal">{totalLogs === 0 ? 0 : offset + 1}</span> to{' '}
                <span className="font-semibold text-charcoal">
                  {Math.min(offset + limit, totalLogs)}
                </span>{' '}
                of <span className="font-semibold text-charcoal">{totalLogs}</span> security events
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setOffset(Math.max(0, offset - limit))}
                  disabled={offset === 0 || auditLoading}
                  className="p-1.5 bg-white border border-line text-midnight disabled:opacity-40 disabled:cursor-not-allowed hover:bg-ivory"
                  title="Previous Page"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="font-mono text-[11px]">
                  Page {Math.floor(offset / limit) + 1} of {Math.ceil(totalLogs / limit) || 1}
                </span>
                <button
                  onClick={() => setOffset(offset + limit)}
                  disabled={offset + limit >= totalLogs || auditLoading}
                  className="p-1.5 bg-white border border-line text-midnight disabled:opacity-40 disabled:cursor-not-allowed hover:bg-ivory"
                  title="Next Page"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: USER MANAGEMENT & RBAC                                             */}
      {/* ========================================================================= */}
      {activeTab === 'users' && (
        <div className="space-y-4">
          {/* Section Description */}
          <div className="p-4 bg-white border-l-4 border-crimson border-r border-t border-b border-line flex items-start space-x-3">
            <Info className="w-5 h-5 text-crimson flex-shrink-0 mt-0.5" />
            <div className="text-xs text-charcoal leading-relaxed">
              <span className="font-bold text-midnight">Role-Based Access Governance: </span>
              Administrators can provision and revoke user access, adjust enterprise roles (<span className="font-mono font-semibold">USER</span>, <span className="font-mono font-semibold">ANALYST</span>, <span className="font-mono font-semibold">ADMIN</span>), and monitor account status.
              A safety control prevents deactivating or demoting the final active administrator to protect against accidental system lockout.
            </div>
          </div>

          <div className="bg-white border border-line shadow-subtle overflow-hidden">
            {usersError && (
              <div className="p-4 bg-rose-50 border-b border-rose-200 text-xs text-rose-800">
                {usersError}
              </div>
            )}

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-line text-left">
                <thead className="bg-ivory border-b border-line text-charcoal-muted text-[11px] font-semibold uppercase tracking-wider">
                  <tr>
                    <th scope="col" className="px-4 py-3">User</th>
                    <th scope="col" className="px-4 py-3">Email Address</th>
                    <th scope="col" className="px-4 py-3">Enterprise Role</th>
                    <th scope="col" className="px-4 py-3">Account Status</th>
                    <th scope="col" className="px-4 py-3">Registration Date</th>
                    <th scope="col" className="px-4 py-3 text-right">Administrative Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line text-xs bg-white">
                  {usersLoading && users.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-4 py-8 text-center text-charcoal-muted">
                        Loading system user directory...
                      </td>
                    </tr>
                  ) : users.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-4 py-8 text-center text-charcoal-muted">
                        No registered users found.
                      </td>
                    </tr>
                  ) : (
                    users.map((u) => {
                      const isSelf = currentUser && currentUser.id === u.id;
                      return (
                        <tr key={u.id} className="hover:bg-ivory/60 transition-colors">
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="font-bold text-midnight">
                              {u.full_name || u.username}
                              {isSelf && (
                                <span className="ml-2 text-[10px] font-bold text-gold-light bg-midnight px-1.5 py-0.5 rounded">
                                  YOU
                                </span>
                              )}
                            </div>
                            <div className="text-[11px] text-charcoal-muted font-mono">@{u.username}</div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-charcoal">
                            {u.email}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <span className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded border ${
                              u.role === 'ADMIN'
                                ? 'bg-purple-100 text-purple-800 border-purple-300'
                                : u.role === 'ANALYST'
                                ? 'bg-blue-100 text-blue-800 border-blue-300'
                                : 'bg-slate-100 text-slate-800 border-slate-300'
                            }`}>
                              {u.role}
                            </span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            {u.is_active ? (
                              <span className="inline-flex items-center space-x-1 text-emerald-700 font-semibold text-[11px]">
                                <UserCheck className="w-3.5 h-3.5 text-emerald-600" />
                                <span>Active</span>
                              </span>
                            ) : (
                              <span className="inline-flex items-center space-x-1 text-rose-700 font-semibold text-[11px]">
                                <UserX className="w-3.5 h-3.5 text-rose-600" />
                                <span>Deactivated</span>
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-charcoal-muted font-mono text-[11px]">
                            {formatTimestamp(u.created_at)}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right space-x-2">
                            {/* Role Selector */}
                            <select
                              value={u.role}
                              onChange={(e) => handleChangeRole(u, e.target.value)}
                              className="text-[11px] bg-white border border-line px-2 py-1 text-midnight font-medium focus:outline-none focus:border-midnight cursor-pointer"
                            >
                              <option value="USER">USER</option>
                              <option value="ANALYST">ANALYST</option>
                              <option value="ADMIN">ADMIN</option>
                            </select>

                            {/* Status Toggle Button */}
                            <button
                              onClick={() => handleToggleStatus(u)}
                              className={`px-2.5 py-1 text-[11px] font-semibold border transition-colors ${
                                u.is_active
                                  ? 'bg-legalred-subtle text-legalred border-legalred-border hover:bg-rose-100'
                                  : 'bg-legalgreen-subtle text-legalgreen border-legalgreen-border hover:bg-emerald-100'
                              }`}
                            >
                              {u.is_active ? 'Deactivate' : 'Activate'}
                            </button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
