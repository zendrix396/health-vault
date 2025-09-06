import axios from 'axios';

const api = axios.create({
    baseURL: 'https://healthvault.zendrix.dev',
    headers: {
        'Accept': 'application/json',
    }
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