import axios from 'axios';

// Configuração base da API
const API_BASE_URL = 
process.env.NODE_ENV === 'production'
  ? '/api' // O Nginx vai rotear isso para o backend
  : 'http://localhost:8000'; // Para desenvolvimento local, se o backend estiver exposto
;

// Instância do axios com configurações padrão
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
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

// Interceptor para tratar respostas e erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Funções de autenticação
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },

  register: async (data) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  recoverPassword: async (email) => {
    const response = await api.post('/auth/recover', { email });
    return response.data;
  },

  resetPassword: async (token, newPassword) => {
    const response = await api.post('/auth/reset', { token, new_password: newPassword });
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};

// Funções para equipamentos
export const equipamentosAPI = {
  getClasses: async () => {
    const response = await api.get('/equipamentos/classes');
    return response.data;
  },
  
  getCaracteristicas: async (classes) => {
    const classesStr = Array.isArray(classes) ? classes.join(',') : classes;
    const response = await api.get(`/equipamentos/caracteristicas?classes=${encodeURIComponent(classesStr)}`);
    return response.data;
  },
  
  getValoresCaracteristica: async (caracteristica, classes) => {
    const classesStr = Array.isArray(classes) ? classes.join(',') : classes;
    const response = await api.get(`/equipamentos/valores/${encodeURIComponent(caracteristica)}?classes=${encodeURIComponent(classesStr)}`);
    return response.data;
  },
  
  filtrarEquipamentos: async (filtroData) => {
    const response = await api.post('/equipamentos/filtrar', filtroData);
    return response.data;
  }
};

// Funções para similaridade
export const similaridadeAPI = {
  getEquipamentosSimilares: async (equipmentId, quantidade = 10) => {
    const response = await api.get(`/equipamentos/similaridade/${encodeURIComponent(equipmentId)}?quantidade=${quantidade}`);
    return response.data;
  }
};

// Função para verificar saúde da API
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  }
};

export default api;

