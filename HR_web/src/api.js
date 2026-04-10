// src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/', // 指向你的 Django 後端
});

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Token ${token}`;
    localStorage.setItem('hr_token', token);
  } else {
    delete api.defaults.headers.common.Authorization;
    localStorage.removeItem('hr_token');
  }
};

const savedToken = localStorage.getItem('hr_token');
if (savedToken) {
  setAuthToken(savedToken);
}

export default api;