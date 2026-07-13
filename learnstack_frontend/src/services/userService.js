import axios from 'axios';
import { API_BASE_URL } from '@/config/api';

const API_URL = `${API_BASE_URL}/users`;

// 登录函数
export const login = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}/login/`, userData);
    // 保存access token和refresh token
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    console.log('登录成功，存储的 access_token:', response.data.access); // 调试日志
    console.log('登录成功，存储的 refresh_token:', response.data.refresh); // 调试日志
    
    // 登录成功后立即获取用户信息
    try {
      const userInfo = await getUserInfo();
      // 将用户信息合并到响应中
      response.data.user = userInfo;
    } catch (error) {
      console.warn('获取用户信息失败，但登录成功:', error.message);
    }
    
    return response.data;
  } catch (error) {
    console.error('登录失败:', error.response?.data || error.message);
    throw error.response?.data?.error || '登录失败，请稍后再试';
  }
};

// 刷新token函数
export const refreshToken = async () => {
  try {
    const refreshTokenValue = localStorage.getItem('refresh_token');
    if (!refreshTokenValue) {
      throw new Error('没有refresh token');
    }
    
    const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
      refresh: refreshTokenValue
    });
    
    // 更新access token
    localStorage.setItem('access_token', response.data.access);
    
    // 如果返回了新的refresh token，也更新它
    if (response.data.refresh) {
      localStorage.setItem('refresh_token', response.data.refresh);
    }
    
    console.log('Token刷新成功');
    return response.data;
  } catch (error) {
    console.error('刷新token失败:', error.response?.data || error.message);
    // 刷新失败，清除所有token，需要重新登录
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    throw error;
  }
};

// 注册函数
export const register = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}/register/`, userData);
    return response.data;
  } catch (error) {
    console.error('Registration error:', error.response?.data);
    throw error.response?.data?.error || error.response?.data || '注册失败，请检查信息';
  }
};

// 获取当前用户信息
export const getUserInfo = async () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('未登录，无有效访问令牌');
  }
  const res = await axios.get(`${API_URL}/me/`, {
    headers: { Authorization: `Bearer ${token}` } // 确保格式为 "Bearer <token>"
  });
  return res.data;
};

// 更新用户信息（支持文件上传）
export const updateUserInfo = async (formData) => {
  const res = await axios.patch(`${API_URL}/me/`, formData, {
    headers: { 
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'multipart/form-data'  // 关键头信息
    }
  });
  return res.data;
};

// 修改密码
export const changePassword = async (oldPassword, newPassword) => {
  const res = await axios.post(`${API_URL}/change-password/`, {
    old_password: oldPassword,
    new_password: newPassword
  }, {
    headers: { 
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });
  return res.data;
};