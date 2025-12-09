const API_BASE_URL = 'http://localhost:5000/api';

export const getAuthToken = (): string | null => {
  return localStorage.getItem('token');
};

const createHeaders = (includeAuth: boolean = true): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (includeAuth) {
    const token = getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  return headers;
};

export const apiCall = async <T>(
  endpoint: string,
  options: RequestInit & { method?: 'GET' | 'POST' | 'PUT' | 'DELETE' } = {}
): Promise<T> => {
  const { method = 'GET', body, ...rest } = options;
  const url = `${API_BASE_URL}${endpoint}`;

  const headers = createHeaders(true);

  const response = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
    ...rest,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `API request failed: ${response.status}`);
  }

  return response.json();
};

export const authAPI = {
  login: (email: string, password: string) =>
    apiCall('/auth/login', {
      method: 'POST',
      body: { email, password },
    }),

  register: (name: string, email: string, password: string) =>
    apiCall('/auth/register', {
      method: 'POST',
      body: { name, email, password },
    }),
};

export const userAPI = {
  getMe: () => apiCall('/users/me', { method: 'GET' }),

  updateProfile: (name: string, email: string) =>
    apiCall('/users/me', {
      method: 'PUT',
      body: { name, email },
    }),
};

export const cvAPI = {
  getAll: () => apiCall('/cvs', { method: 'GET' }),

  getById: (id: string) => apiCall(`/cvs/${id}`, { method: 'GET' }),

  create: (cvData: any) =>
    apiCall('/cvs', {
      method: 'POST',
      body: cvData,
    }),

  update: (id: string, cvData: any) =>
    apiCall(`/cvs/${id}`, {
      method: 'PUT',
      body: cvData,
    }),

  delete: (id: string) =>
    apiCall(`/cvs/${id}`, {
      method: 'DELETE',
    }),
};

export default {
  apiCall,
  authAPI,
  userAPI,
  cvAPI,
  getAuthToken,
};
