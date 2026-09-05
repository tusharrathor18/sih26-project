import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

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
      if (!error.config?.url?.includes('/auth/login/')) {
        localStorage.removeItem('officer_token');
        localStorage.removeItem('officer_data');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const getApiErrorMessage = (error, fallback = 'Something went wrong. Please try again.') => {
  if (!error.response) {
    return 'Unable to connect to the backend service. Please check that Django is running.';
  }

  const messages = {
    400: 'Please check the information you entered.',
    401: 'Your session is invalid or has expired. Please sign in again.',
    403: 'You are not authorized to perform this action.',
    404: 'The requested resource was not found.',
    500: 'The server could not complete the request. Please try again later.',
  };

  return messages[error.response.status] || fallback;
};

export default api;
