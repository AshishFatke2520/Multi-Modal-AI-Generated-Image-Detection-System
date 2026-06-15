import axios from 'axios';

const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api/v1'
  : window.location.origin + '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor (for JWT)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const authService = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
};

export const analysisService = {
  uploadFusion: async (formData) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/analyze/fusion?explain=true`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    if (!response.ok) {
        let errMsg = `Upload failed with status ${response.status}`;
        try {
            const errData = await response.json();
            if (errData.detail) errMsg = errData.detail;
        } catch (e) {}
        throw new Error(errMsg);
    }
    const data = await response.json();
    return { data };
  }
};

export const historyService = {
  getAll: () => api.get('/history/'),
  clearAll: () => api.delete('/history/'),
};

export default api;
