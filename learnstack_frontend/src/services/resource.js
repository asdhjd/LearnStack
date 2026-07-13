import axios from 'axios';
import { API_BASE_URL } from '@/config/api';

const API_URL = API_BASE_URL;

export const resourceService = {
  // 获取所有资源
  async getAllResources() {
    try {
      const response = await axios.get(`${API_URL}/resources/`);
      return response.data;
    } catch (error) {
      console.error('获取资源列表失败:', error);
      throw error;
    }
  },

  // 根据分类获取学习路径
  async getLearningPathByCategory(categoryId) {
    try {
      const response = await axios.get(`${API_URL}/learningpaths/paths/by-category/${categoryId}/`);
      return response.data;
    } catch (error) {
      console.error('获取学习路径失败:', error);
      throw error;
    }
  },

  // 获取单个资源详情
  async getResourceById(id) {
    try {
      const response = await axios.get(`${API_URL}/resources/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`获取资源 ${id} 详情失败:`, error);
      throw error;
    }
  },

  // 搜索资源（新增）
  async searchResources(query) {
    try {
      const response = await axios.get(`${API_URL}/resources/?search=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error('搜索资源失败:', error);
      throw error;
    }
  },

  // 提交资源投稿
  async submitResource(resourceData) {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `${API_URL}/resources/submit/`,
        resourceData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('提交资源失败:', error);
      throw error;
    }
  }
};

export default resourceService;
