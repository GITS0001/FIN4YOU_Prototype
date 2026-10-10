import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('fin4you_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for consistent error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      return Promise.reject({ message, status: error.response.status });
    } else if (error.request) {
      return Promise.reject({
        message: "FIN4YOU couldn't connect to the financial engine. Please ensure the backend is running.",
        status: 0,
      });
    }
    return Promise.reject({ message: error.message || 'Unknown error' });
  }
);

export const DEMO_USER_ID = import.meta.env.VITE_DEMO_USER_ID || 'user_28';
