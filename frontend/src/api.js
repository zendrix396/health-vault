import axios from 'axios';

const api = axios.create({
    baseURL: 'https://unu5hmdhgh.execute-api.ap-south-1.amazonaws.com',
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
