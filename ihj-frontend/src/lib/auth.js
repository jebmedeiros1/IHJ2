// Utilitários para gerenciamento de autenticação

export const getToken = () => {
  return localStorage.getItem('access_token');
};

export const setToken = (token) => {
  localStorage.setItem('access_token', token);
};

export const removeToken = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_info');
};

export const getUserInfo = () => {
  const userInfo = localStorage.getItem('user_info');
  return userInfo ? JSON.parse(userInfo) : null;
};

export const setUserInfo = (userInfo) => {
  localStorage.setItem('user_info', JSON.stringify(userInfo));
};

export const isAuthenticated = () => {
  const token = getToken();
  return !!token;
};

export const logout = () => {
  removeToken();
  window.location.href = '/login';
};

