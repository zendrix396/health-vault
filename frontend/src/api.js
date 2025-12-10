import axios from 'axios';

const BACKEND_BASE_URL =
  import.meta.env.VITE_BACKEND_URL || 'https://health-vault-9.onrender.com';

const api = axios.create({
  baseURL: BACKEND_BASE_URL,
  headers: {
    Accept: 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

export default api;
