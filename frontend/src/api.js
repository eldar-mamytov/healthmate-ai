import axios from 'axios';

// Create an Axios instance with a base URL
// During development, your React app runs on port 3000 (or similar)
// and your FastAPI backend runs on port 8000.
// When deployed, Nginx will proxy requests, so the path will be relative.
// For now, explicitly point to the backend's port 8000.
const api = axios.create({
  baseURL: '/api', // Your FastAPI backend URL
});

// Optional: Add a request interceptor to attach the JWT token
// to every outgoing request if it exists in localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Optional: Add a response interceptor to handle token expiration/invalidity
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Example: If 401 Unauthorized response and token exists, clear token
    if (error.response && error.response.status === 401) {
      const token = localStorage.getItem('access_token');
      // Only clear if a token was actually sent and rejected
      if (token && error.response.data.detail === "Could not validate credentials") {
        console.warn("Token expired or invalid. Clearing token from localStorage.");
        localStorage.removeItem('access_token');
        // You might want to redirect the user to the login page here
        // window.location.href = '/login'; // Or use React Router's history
      }
    }
    return Promise.reject(error);
  }
);


export default api;