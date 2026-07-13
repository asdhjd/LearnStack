import axios from 'axios';
import { setupTokenRefreshInterceptor } from '@/utils/tokenRefresh';
import { API_BASE_URL } from '@/config/api';

const api = axios.create({
  baseURL: `${API_BASE_URL}/users/`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器，添加认证token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  console.error('请求拦截器错误:', error);
  return Promise.reject(error);
});

// 设置token自动刷新拦截器
setupTokenRefreshInterceptor(api);

// 响应拦截器，处理错误
api.interceptors.response.use(
  response => {
    console.log('API响应成功，URL:', response.config?.url, '状态码:', response.status);
    return response.data;
  },
  error => {
    console.error('响应拦截器错误:', error);
    console.error('请求URL:', error.config?.url);
    console.error('响应数据:', error.response?.data);
    
    // 改进错误信息提取，特别是处理Django REST Framework的验证错误
    let errorMessage = '网络请求失败';
    
    // 如果有响应数据
    if (error.response?.data) {
      // 处理单个错误详情
      if (error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      // 处理验证错误（通常是字段级别的错误）
      else if (typeof error.response.data === 'object') {
        const errorMessages = [];
        
        // 遍历所有字段的错误信息
        for (const field in error.response.data) {
          if (Array.isArray(error.response.data[field])) {
            // 将每个字段的所有错误消息添加到列表中
            errorMessages.push(...error.response.data[field]);
          } else {
            errorMessages.push(error.response.data[field]);
          }
        }
        
        // 如果收集到了错误消息，用分号连接它们
        if (errorMessages.length > 0) {
          errorMessage = errorMessages.join('; ');
        } else {
          // 作为后备，尝试将整个响应数据转换为字符串
          errorMessage = JSON.stringify(error.response.data);
        }
      } else {
        errorMessage = String(error.response.data);
      }
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    throw new Error(errorMessage);
  }
);

// 用户管理API
export const adminService = {
  /**
   * 获取用户列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.page_size - 每页大小
   * @returns {Promise} - 返回用户列表数据
   */
  getUsers: async (params = {}) => {
    try {
      console.log('获取用户列表请求参数:', params);
      return await api.get('admin/users/', { params });
    } catch (error) {
      console.error('获取用户列表失败:', error);
      throw error;
    }
  },

  /**
   * 获取单个用户信息
   * @param {number} userId - 用户ID
   * @returns {Promise} - 返回用户信息
   */
  getUser: async (userId) => {
    try {
      return await api.get(`admin/users/${userId}/`);
    } catch (error) {
      console.error(`获取用户${userId}信息失败:`, error);
      throw error;
    }
  },

  /**
   * 创建新用户
   * @param {Object} userData - 用户数据
   * @returns {Promise} - 返回创建的用户信息
   */
  createUser: async (userData) => {
    try {
      console.log('创建用户请求数据:', userData);
      console.log('请求URL:', 'admin/users/create/');
      const response = await api.post('admin/users/create/', userData);
      console.log('创建用户成功，响应数据:', response);
      return response;
    } catch (error) {
      console.error('创建用户失败:', error);
      console.error('错误详情:', error.response?.data);
      console.error('状态码:', error.response?.status);
      throw error;
    }
  },

  /**
   * 更新用户信息
   * @param {number} userId - 用户ID
   * @param {Object} userData - 用户数据
   * @returns {Promise} - 返回更新后的用户信息
   */
  updateUser: async (userId, userData) => {
    try {
      console.log(`更新用户${userId}请求数据:`, userData);
      return await api.put(`admin/users/${userId}/`, userData);
    } catch (error) {
      console.error(`更新用户${userId}失败:`, error);
      throw error;
    }
  },

  /**
   * 删除用户
   * @param {number} userId - 用户ID
   * @returns {Promise}
   */
  deleteUser: async (userId) => {
    try {
      console.log(`删除用户${userId}`);
      return await api.delete(`admin/users/${userId}/`);
    } catch (error) {
      console.error(`删除用户${userId}失败:`, error);
      throw error;
    }
  },

  /**
     * 创建分类
     * @param {Object} categoryData - 分类数据
     * @returns {Promise} - 返回创建的分类信息
     */
    createCategory: async (categoryData) => {
      try {
        console.log('创建分类请求数据:', categoryData);
        const token = localStorage.getItem('access_token');
        
        // 检查token是否存在且有效
        if (!token || token.trim() === '') {
          throw new Error('未登录或登录已过期，请重新登录');
        }
        
        const url = `${API_BASE_URL}/categories/admin/categories/`;
        console.log('请求URL:', url);
        
        // 如果是FormData，不需要设置Content-Type，让浏览器自动设置
        const headers = categoryData instanceof FormData 
          ? { 'Authorization': `Bearer ${token}` }
          : { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
        
        const response = await axios.post(url, categoryData, { headers });
        console.log('创建分类成功响应:', response.data);
        return response.data;
      } catch (error) {
        console.error('创建分类失败:', error);
        let errorMessage = '创建分类失败';
        
        if (error.response) {
          if (error.response.data && error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else if (error.response.data && typeof error.response.data === 'object') {
            const errorFields = Object.keys(error.response.data);
            if (errorFields.length > 0) {
              errorMessage = `${errorFields[0]}: ${error.response.data[errorFields[0]][0]}`;
            }
          }
        } else if (error.message) {
          errorMessage = error.message;
        }
        throw new Error(errorMessage);
      }
    },
    
    /**
     * 更新分类
     * @param {number} categoryId - 分类ID
     * @param {Object} categoryData - 分类数据
     * @returns {Promise} - 返回更新后的分类信息
     */
    updateCategory: async (categoryId, categoryData) => {
      try {
        console.log(`更新分类${categoryId}请求数据:`, categoryData);
        const token = localStorage.getItem('access_token');
        console.log('使用的token:', token ? token.substring(0, 10) + '...' : '无token');
        
        // 检查token是否存在且有效
        if (!token || token.trim() === '') {
          throw new Error('未登录或登录已过期，请重新登录');
        }
        
        // 如果是FormData，不需要设置Content-Type，让浏览器自动设置
        const headers = categoryData instanceof FormData 
          ? { 'Authorization': `Bearer ${token}` }
          : { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
        
        const response = await axios.put(`${API_BASE_URL}/categories/admin/categories/${categoryId}/`, categoryData, {
          headers
        });
        return response.data;
      } catch (error) {
        console.error(`更新分类${categoryId}失败:`, error);
        let errorMessage = '更新分类失败';
        
        // 特殊处理token相关错误
        if (error.message && error.message.includes('token')) {
          errorMessage = error.message;
        } else if (error.response && error.response.data) {
          if (error.response.data.detail) {
            const detail = error.response.data.detail;
            // 处理token无效错误
            if (typeof detail === 'string' && detail.includes('token')) {
              errorMessage = '登录已过期，请重新登录';
            } else {
              errorMessage = detail;
            }
          } else if (typeof error.response.data === 'object') {
            const errorFields = Object.keys(error.response.data);
            if (errorFields.length > 0) {
              errorMessage = `${errorFields[0]}: ${error.response.data[errorFields[0]][0]}`;
            }
          }
        }
        throw new Error(errorMessage);
      }
    },
    
    /**
     * 删除分类
     * @param {number} categoryId - 分类ID
     * @returns {Promise}
     */
    deleteCategory: async (categoryId) => {
      try {
        console.log(`删除分类${categoryId}`);
        const token = localStorage.getItem('access_token');
        console.log('使用的token:', token ? token.substring(0, 10) + '...' : '无token');
        
        // 检查token是否存在且有效
        if (!token || token.trim() === '') {
          throw new Error('未登录或登录已过期，请重新登录');
        }
        
        const response = await axios.delete(`${API_BASE_URL}/categories/admin/categories/${categoryId}/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.data;
      } catch (error) {
        console.error(`删除分类${categoryId}失败:`, error);
        let errorMessage = '删除分类失败';
        
        // 特殊处理token相关错误
        if (error.message && error.message.includes('token')) {
          errorMessage = error.message;
        } else if (error.response && error.response.data) {
          if (error.response.data.detail) {
            const detail = error.response.data.detail;
            // 处理token无效错误
            if (typeof detail === 'string' && detail.includes('token')) {
              errorMessage = '登录已过期，请重新登录';
            } else {
              errorMessage = detail;
            }
          }
        }
        throw new Error(errorMessage);
      }
    },
    
    /**
     * 切换分类热门状态
     * @param {number} categoryId - 分类ID
     * @param {boolean} isHot - 是否热门
     * @returns {Promise}
     */
    toggleCategoryHotStatus: async (categoryId, isHot) => {
      try {
        console.log(`切换分类${categoryId}热门状态为:`, isHot);
        const token = localStorage.getItem('access_token');
        
        if (!token || token.trim() === '') {
          throw new Error('未登录或登录已过期，请重新登录');
        }
        
        // 使用统一的 PATCH 端点
        const response = await axios.patch(`${API_BASE_URL}/categories/admin/categories/${categoryId}/`, 
          { is_hot: isHot },
          { 
            headers: { 'Authorization': `Bearer ${token}` }
          }
        );
        return response.data;
      } catch (error) {
        console.error(`切换分类${categoryId}热门状态失败:`, error);
        let errorMessage = '切换热门状态失败';
        
        if (error.response) {
          if (error.response.data && error.response.data.detail) {
            errorMessage = error.response.data.detail;
          }
        } else if (error.message) {
          errorMessage = error.message;
        }
        throw new Error(errorMessage);
      }
    },
    
    /**
     * 获取分类列表
     * @param {Object} params - 查询参数
     * @param {number} params.page - 页码
     * @param {number} params.page_size - 每页大小
     * @param {string} params.search - 搜索关键词
     * @returns {Promise} - 返回分类列表数据
     */
    getCategories: async (params = {}) => {
      try {
        console.log('获取分类列表请求参数:', params);
        // 设置一个很大的page_size来确保获取所有分类，避免分页限制
        const requestParams = { ...params, page_size: 1000 };
        console.log('实际请求参数(增加了page_size):', requestParams);
        const token = localStorage.getItem('access_token');
        const response = await axios.get(`${API_BASE_URL}/categories/admin/categories/`, {
          params: requestParams,
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        console.log('获取分类列表响应数据:', response.data);
        // 确保返回的数据结构包含results和count
        if (Array.isArray(response.data)) {
          return {
            results: response.data,
            count: response.data.length
          };
        }
        return response.data;
      } catch (error) {
        console.error('获取分类列表失败:', error);
        throw error;
      }
    },
    
    /**
     * 获取单个分类信息
     * @param {number} categoryId - 分类ID
     * @returns {Promise} - 返回分类信息
     */
    getCategory: async (categoryId) => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get(`${API_BASE_URL}/categories/admin/categories/${categoryId}/`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        return response.data;
      } catch (error) {
        console.error(`获取分类${categoryId}信息失败:`, error);
        throw error;
      }
    },

    /**
     * 获取资源列表
     * @param {Object} params - 查询参数
     * @param {string} params.search - 搜索关键词
     * @returns {Promise} - 返回资源列表数据
     */
    getResources: async (params = {}) => {
      try {
        console.log('获取资源列表请求参数:', params);
        const token = localStorage.getItem('access_token');
        const response = await axios.get(`${API_BASE_URL}/resources/admin/`, {
          params,
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        console.log('获取资源列表响应数据:', response.data);
        // 确保返回的数据结构包含results和count
        if (Array.isArray(response.data)) {
          return {
            results: response.data,
            count: response.data.length
          };
        }
        return response.data;
      } catch (error) {
        console.error('获取资源列表失败:', error);
        throw error;
      }
    },

    /**
     * 获取单个资源详情
     * @param {number} resourceId - 资源ID
     * @returns {Promise} - 返回资源信息
     */
    getResource: async (resourceId) => {
      try {
        console.log(`获取资源${resourceId}详情`);
        const token = localStorage.getItem('access_token');
        const response = await axios.get(`${API_BASE_URL}/resources/admin/${resourceId}/`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        return response.data;
      } catch (error) {
        console.error(`获取资源${resourceId}详情失败:`, error);
        throw error;
      }
    },

    /**
     * 创建新资源
     * @param {Object} resourceData - 资源数据
     * @returns {Promise} - 返回创建的资源信息
     */
    createResource: async (resourceData) => {
      try {
        console.log('创建资源请求数据:', resourceData);
        const token = localStorage.getItem('access_token');
        
        // 检查是否是FormData
        const isFormData = resourceData instanceof FormData;
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        
        // 如果是FormData，不设置Content-Type，让浏览器自动设置
        if (!isFormData) {
          headers['Content-Type'] = 'application/json';
        }
        
        const response = await axios.post(`${API_BASE_URL}/resources/admin/`, resourceData, {
          headers: headers
        });
        console.log('创建资源成功响应:', response.data);
        return response.data;
      } catch (error) {
        console.error('创建资源失败:', error);
        let errorMessage = '创建资源失败';
        if (error.response && error.response.data) {
          if (error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else if (typeof error.response.data === 'object') {
            const errorFields = Object.keys(error.response.data);
            if (errorFields.length > 0) {
              errorMessage = `${errorFields[0]}: ${error.response.data[errorFields[0]][0]}`;
            }
          }
        }
        throw new Error(errorMessage);
      }
    },

    /**
     * 更新资源信息
     * @param {number} resourceId - 资源ID
     * @param {Object} resourceData - 资源数据
     * @returns {Promise} - 返回更新后的资源信息
     */
    updateResource: async (resourceId, resourceData) => {
      try {
        console.log(`更新资源${resourceId}请求数据:`, resourceData);
        const token = localStorage.getItem('access_token');
        
        // 检查是否是FormData
        const isFormData = resourceData instanceof FormData;
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        
        // 如果是FormData，不设置Content-Type，让浏览器自动设置
        if (!isFormData) {
          headers['Content-Type'] = 'application/json';
        }
        
        const response = await axios.put(`${API_BASE_URL}/resources/admin/${resourceId}/`, resourceData, {
          headers: headers
        });
        return response.data;
      } catch (error) {
        console.error(`更新资源${resourceId}失败:`, error);
        let errorMessage = '更新资源失败';
        if (error.response && error.response.data) {
          if (error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else if (typeof error.response.data === 'object') {
            const errorFields = Object.keys(error.response.data);
            if (errorFields.length > 0) {
              errorMessage = `${errorFields[0]}: ${error.response.data[errorFields[0]][0]}`;
            }
          }
        }
        throw new Error(errorMessage);
      }
    },

    /**
     * 删除资源
     * @param {number} resourceId - 资源ID
     * @returns {Promise}
     */
    deleteResource: async (resourceId) => {
      try {
        console.log(`删除资源${resourceId}`);
        const token = localStorage.getItem('access_token');
        
        // 检查token是否存在且有效
        if (!token || token.trim() === '') {
          throw new Error('未登录或登录已过期，请重新登录');
        }
        
        const response = await axios.delete(`${API_BASE_URL}/resources/admin/${resourceId}/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.data;
      } catch (error) {
        console.error(`删除资源${resourceId}失败:`, error);
        let errorMessage = '删除资源失败';
        if (error.response) {
          if (error.response.status === 401 || error.response.status === 403) {
            errorMessage = '登录已过期，请重新登录';
          } else if (error.response.data && error.response.data.detail) {
            errorMessage = error.response.data.detail;
          }
        } else if (error.message === '未登录或登录已过期，请重新登录') {
          errorMessage = error.message;
        }
        throw new Error(errorMessage);
      }
    }
  };

// 添加正确的默认导出语句
export default adminService;