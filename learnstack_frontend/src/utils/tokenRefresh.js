/**
 * Token自动刷新工具
 * 用于统一处理所有axios实例的token刷新逻辑
 */

import axios from 'axios';
import { refreshToken } from '@/services/userService';

// 全局状态
let isRefreshing = false;
let failedQueue = [];

/**
 * 处理队列中的请求
 */
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

/**
 * 为axios实例添加token自动刷新拦截器
 * @param {AxiosInstance} axiosInstance - axios实例
 */
export function setupTokenRefreshInterceptor(axiosInstance) {
  axiosInstance.interceptors.response.use(
    response => response,
    async error => {
      const originalRequest = error.config;

      // 如果是401错误且不是刷新token的请求，且未重试过
      if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/token/refresh/')) {
        if (isRefreshing) {
          // 如果正在刷新token，将请求加入队列
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then(token => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return axiosInstance(originalRequest);
            })
            .catch(err => {
              return Promise.reject(err);
            });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          // 尝试刷新token
          const tokenData = await refreshToken();
          // refreshToken函数返回的是response.data，包含access字段
          const newAccessToken = tokenData.access;
          
          // 更新请求头
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          
          // 处理队列中的请求
          processQueue(null, newAccessToken);
          isRefreshing = false;
          
          // 重试原始请求
          return axiosInstance(originalRequest);
        } catch (refreshError) {
          // 刷新失败，处理队列并跳转到登录页
          processQueue(refreshError, null);
          isRefreshing = false;
          
          // 清除token并跳转到登录页
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          
          // 如果是在浏览器环境，跳转到登录页
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );
}

