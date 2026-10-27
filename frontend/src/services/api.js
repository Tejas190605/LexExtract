import axios from 'axios';

const savedApiUrl = typeof window !== 'undefined' ? localStorage.getItem('lexextract_api_base_url') : null;
let rawBase = savedApiUrl || import.meta.env.VITE_API_BASE_URL || 'https://lexextract-backend.onrender.com';
if (rawBase === 'lexextract-backend' || rawBase === 'https://lexextract-backend' || rawBase === 'http://lexextract-backend') {
  rawBase = 'https://lexextract-backend.onrender.com';
}
if (rawBase && !rawBase.startsWith('http://') && !rawBase.startsWith('https://')) {
  if (!rawBase.includes('.') && !rawBase.includes(':')) {
    rawBase = `${rawBase}.onrender.com`;
  }
  rawBase = `https://${rawBase}`;
}
export const API_BASE_URL = rawBase.replace(/\/+$/, '');

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
});

// Request Interceptor: Attach Bearer JWT token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('lexextract_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 Unauthorized by clearing stale tokens
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear expired or invalid credentials
      localStorage.removeItem('lexextract_token');
    }
    return Promise.reject(error);
  }
);

/**
 * Health check probe
 */
export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

/**
 * API v1 info probe
 */
export const getApiInfo = async () => {
  const response = await apiClient.get('/api/v1/');
  return response.data;
};

// ==========================================
// Authentication & Identity (Phase 6)
// ==========================================

export const loginApi = async (credentials) => {
  const response = await apiClient.post('/api/v1/auth/login', credentials);
  return response.data;
};

export const registerApi = async (userData) => {
  const response = await apiClient.post('/api/v1/auth/register', userData);
  return response.data;
};

export const getMeApi = async () => {
  const response = await apiClient.get('/api/v1/auth/me');
  return response.data;
};

export const logoutApi = async () => {
  const response = await apiClient.post('/api/v1/auth/logout');
  return response.data;
};

// ==========================================
// User Administration & RBAC (Phase 6)
// ==========================================

export const listUsersAdmin = async (skip = 0, limit = 100) => {
  const response = await apiClient.get('/api/v1/users/', { params: { skip, limit } });
  return response.data;
};

export const updateUserStatusAdmin = async (userId, isActive) => {
  const response = await apiClient.patch(`/api/v1/users/${userId}/status`, { is_active: isActive });
  return response.data;
};

export const updateUserRoleAdmin = async (userId, role) => {
  const response = await apiClient.patch(`/api/v1/users/${userId}/role`, { role });
  return response.data;
};

// ==========================================
// Governance Audit Trail (Phase 6)
// ==========================================

export const getAuditLogsAdmin = async (params = {}) => {
  const response = await apiClient.get('/api/v1/admin/audit-logs', { params });
  return response.data;
};

// ==========================================
// Documents (Phase 3 & Phase 6 Protected)
// ==========================================

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post('/api/v1/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocumentText = async (documentId) => {
  const response = await apiClient.get(`/api/v1/documents/${documentId}/text`);
  return response.data;
};

export const getDocumentMetadata = async (documentId) => {
  const response = await apiClient.get(`/api/v1/documents/${documentId}`);
  return response.data;
};

export const getDocument = getDocumentMetadata;

export const listDocuments = async () => {
  const response = await apiClient.get('/api/v1/documents/');
  return response.data;
};

export const getDocumentFileUrl = (documentId, download = false) => {
  const token = localStorage.getItem('lexextract_token');
  const base = `${API_BASE_URL}/api/v1/documents/${documentId}/file`;
  const params = new URLSearchParams();
  if (download) params.append('download', 'true');
  if (token) params.append('token', token);
  const q = params.toString();
  return q ? `${base}?${q}` : base;
};

export const downloadDocumentFile = async (documentId, filename) => {
  const response = await apiClient.get(`/api/v1/documents/${documentId}/file`, {
    params: { download: true },
    responseType: 'blob'
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename || `document_${documentId}`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

// ==========================================
// Analysis, Keywords & Entities (Phases 4 & 5)
// ==========================================

export const analyzeDocument = async (documentId) => {
  const response = await apiClient.post(`/api/v1/analyses/${documentId}`);
  return response.data;
};

export const getAnalysisKeywords = async (analysisId, categoryOrOptions = null, limit = 20) => {
  let params = { limit };
  if (typeof categoryOrOptions === 'object' && categoryOrOptions !== null) {
    if (categoryOrOptions.limit) params.limit = categoryOrOptions.limit;
    if (categoryOrOptions.category && categoryOrOptions.category !== 'All') {
      params.category = categoryOrOptions.category;
    }
  } else if (typeof categoryOrOptions === 'string' && categoryOrOptions !== 'All') {
    params.category = categoryOrOptions;
  }
  const response = await apiClient.get(`/api/v1/analyses/${analysisId}/keywords`, { params });
  return response.data;
};

export const getAnalysisEntities = async (analysisId, typeOrOptions = null, limit = 50) => {
  let params = { limit };
  if (typeof typeOrOptions === 'object' && typeOrOptions !== null) {
    if (typeOrOptions.limit) params.limit = typeOrOptions.limit;
    if (typeOrOptions.type && typeOrOptions.type !== 'All') {
      params.type = typeOrOptions.type;
    }
  } else if (typeof typeOrOptions === 'string' && typeOrOptions !== 'All') {
    params.type = typeOrOptions;
  }
  const response = await apiClient.get(`/api/v1/analyses/${analysisId}/entities`, { params });
  return response.data;
};

export const getAnalysisEntitiesSummary = async (analysisId) => {
  const response = await apiClient.get(`/api/v1/analyses/${analysisId}/entities/summary`);
  return response.data;
};

export const getAnalysisSummary = async (analysisId) => {
  const response = await apiClient.get(`/api/v1/analyses/${analysisId}`);
  return response.data;
};

export const listDocumentAnalyses = async (documentId) => {
  const response = await apiClient.get(`/api/v1/analyses/document/${documentId}`);
  return response.data;
};

// ==========================================
// ASTMA Benchmark Evaluation (Phase 8)
// ==========================================

export const getEvaluationSummary = async () => {
  const response = await apiClient.get('/api/v1/evaluation/summary');
  return response.data;
};

export const getEvaluationDocuments = async () => {
  const response = await apiClient.get('/api/v1/evaluation/documents');
  return response.data;
};

export const getEvaluationSingleDocument = async (documentId) => {
  const response = await apiClient.get(`/api/v1/evaluation/documents/${documentId}`);
  return response.data;
};

export const getEvaluationErrors = async () => {
  const response = await apiClient.get('/api/v1/evaluation/errors');
  return response.data;
};

export const runEvaluationBenchmark = async () => {
  const response = await apiClient.post('/api/v1/evaluation/run');
  return response.data;
};

// ==========================================
// Phase 11 User-Value Enhancements
// ==========================================

export const getDocumentInsights = async (analysisId) => {
  const response = await apiClient.get(`/api/v1/analyses/${analysisId}/insights`);
  return response.data;
};

export const getDocumentClauses = async (analysisId) => {
  const response = await apiClient.get(`/api/v1/analyses/${analysisId}/clauses`);
  return response.data;
};

export const getDocumentObligations = async (analysisId) => {
  const response = await apiClient.get(`/api/v1/analyses/${analysisId}/obligations`);
  return response.data;
};

export const getDocumentFacts = async (analysisId) => {
  const response = await apiClient.get(`/api/v1/analyses/${analysisId}/facts`);
  return response.data;
};

export const searchDocument = async (documentId, query) => {
  const response = await apiClient.get(`/api/v1/documents/${documentId}/search`, {
    params: { q: query }
  });
  return response.data;
};

export const compareDocuments = async (docAId, docBId) => {
  const response = await apiClient.post('/api/v1/documents/compare', {
    doc_a_id: docAId,
    doc_b_id: docBId
  });
  return response.data;
};

export const exportAnalysisReport = async (analysisId, format = 'pdf', filename = null) => {
  if (format === 'json') {
    const response = await apiClient.get(`/api/v1/analyses/${analysisId}/export`, {
      params: { format: 'json' }
    });
    // Trigger browser JSON download
    const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename || `lexextract_report_${analysisId}.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    return response.data;
  } else {
    const response = await apiClient.get(`/api/v1/analyses/${analysisId}/export`, {
      params: { format: 'pdf' },
      responseType: 'blob'
    });
    // Trigger browser PDF download
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename || `lexextract_report_${analysisId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    return true;
  }
};

export default apiClient;

