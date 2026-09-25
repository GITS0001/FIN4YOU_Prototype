import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export const DEMO_USER_ID = import.meta.env.VITE_DEMO_USER_ID || 'user_01';
