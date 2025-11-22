/**
 * API client for backend communication.
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Employees API
 */
export const employeesAPI = {
  list: () => api.get('/employees'),
};

/**
 * Reimbursement API
 */
export const reimbursementAPI = {
  submit: (employeeId, file) => {
    const formData = new FormData();
    formData.append('employee_id', employeeId);
    formData.append('file', file);
    return api.post('/reimbursement/submit', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  get: (requestId) => api.get(`/reimbursement/${requestId}`),
};

/**
 * Categories API
 */
export const categoriesAPI = {
  list: () => api.get('/categories'),
  create: (data) => api.post('/categories', data),
  update: (categoryId, data) => api.put(`/categories/${categoryId}`, data),
  delete: (categoryId) => api.delete(`/categories/${categoryId}`),
  getKeywords: (categoryId) => api.get(`/categories/${categoryId}/keywords`),
  addKeyword: (categoryId, keyword) => api.post(`/categories/${categoryId}/keywords`, { keyword }),
  deleteKeyword: (categoryId, keywordId) => api.delete(`/categories/${categoryId}/keywords/${keywordId}`),
};

/**
 * Balances API
 */
export const balancesAPI = {
  getEmployeeBalances: (employeeId, year, month) => {
    const params = {};
    if (year) params.year = year;
    if (month) params.month = month;
    return api.get(`/employees/${employeeId}/balances`, { params });
  },
};

export default api;

