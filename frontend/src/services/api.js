import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor to attach DRF Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('officer_token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle session expiration or unauthorized status
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token if expired or invalid (except on login attempts)
      if (!error.config.url.includes('/users/login/')) {
        localStorage.removeItem('officer_token');
        localStorage.removeItem('officer_data');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
