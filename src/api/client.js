import axios from 'axios';
import { supabase } from '../lib/supabase';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach Supabase or local auth token
apiClient.interceptors.request.use(
  async (config) => {
    // 1. Try Supabase active session token first
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`;
        return config;
      }
    } catch {
      // Fall through to localStorage if Supabase session call fails
    }

    // 2. Fall back to local storage token
    const token = localStorage.getItem('fin4you_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for clear, actionable error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const message =
        error.response.data?.detail ||
        error.response.data?.message ||
        `Server returned ${error.response.status}`;
      return Promise.reject({
        message,
        status: error.response.status,
        data: error.response.data,
      });
    } else if (error.request) {
      return Promise.reject({
        message: 'FIN4YOU financial engine connection unavailable. Verify the backend service is running on port 8000.',
        status: 0,
      });
    }
    return Promise.reject({
      message: error.message || 'Unknown network error',
      status: -1,
    });
  }
);

export const DEFAULT_USER_ID = 'user_28';
