import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — attach JWT token to every request
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('verity_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle 401 errors (expired/invalid token)
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('verity_token');
      // Only redirect if not already on auth pages
      if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/register')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth API ───
export const authAPI = {
  register: (email, password) =>
    client.post('/auth/register', { email, password }),

  login: (email, password) =>
    client.post('/auth/login', { email, password }),
};

// ─── Queries API ───
export const queriesAPI = {
  submit: (raw_query) =>
    client.post('/queries/', { raw_query }),

  list: () =>
    client.get('/queries/'),

  detail: (queryId) =>
    client.get(`/queries/${queryId}`),

  delete: (queryId) =>
    client.delete(`/queries/${queryId}`),
};

// ─── Reports API ───
export const reportsAPI = {
  get: (queryId) =>
    client.get(`/reports/${queryId}`),
};

export default client;
