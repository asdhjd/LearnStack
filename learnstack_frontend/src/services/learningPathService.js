import axios from 'axios';
import { setupTokenRefreshInterceptor } from '@/utils/tokenRefresh';
import { API_BASE_URL } from '@/config/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器，添加认证token
api.interceptors.request.use(config => {
  // 从localStorage中获取token，与userService.js保持一致
  const token = localStorage.getItem('access_token');
  
  if (token) {
    // 使用Bearer格式，与userService.js中的认证格式保持一致
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  return config;
}, error => {
  console.error('请求拦截器错误:', error);
  return Promise.reject(error);
});

// 设置token自动刷新拦截器
setupTokenRefreshInterceptor(api);

/**
 * 根据分类ID获取学习路径
 * @param {number} categoryId - 技术分类ID
 * @returns {Promise} - 返回学习路径数据的Promise
 */
export const getLearningPathByCategory = async (categoryId) => {
  try {
    console.log(`调用API: /learningpaths/paths/by-category/${categoryId}/`);
    const response = await api.get(`/learningpaths/paths/by-category/${categoryId}/`);
    console.log('API响应:', response.data);
    return response;
  } catch (error) {
    console.error('获取学习路径失败:', error);
    console.error('错误响应:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * 获取所有学习路径列表
 * @returns {Promise} - 返回学习路径列表的Promise
 */
export const getAllLearningPaths = async () => {
  try {
    const response = await api.get('/learningpaths/paths/');
    return response;
  } catch (error) {
    console.error('获取学习路径列表失败:', error);
    throw error;
  }
};

/**
 * 获取单个学习路径详情
 * @param {number} pathId - 学习路径ID
 * @returns {Promise} - 返回学习路径详情的Promise
 */
export const getLearningPathDetail = async (pathId) => {
  try {
    const response = await api.get(`/learningpaths/paths/${pathId}/`);
    return response;
  } catch (error) {
    console.error('获取学习路径详情失败:', error);
    throw error;
  }
};

/**
 * 标记学习阶段为已完成
 * @param {number} stageId - 学习阶段ID
 * @returns {Promise} - 返回操作结果的Promise
 */
export const markStageCompleted = async (stageId, stageTitle = '', stageOrder = 1) => {
  try {
    console.log(`调用API: /learningpaths/paths/mark-stage-completed/`);
    
    // 构建请求数据，包含阶段ID、标题和顺序
    const requestData = {
      stage_id: stageId
    };
    
    // 只有当提供了额外信息时才添加到请求中
    if (stageTitle) {
      requestData.stage_title = stageTitle;
    }
    if (stageOrder) {
      requestData.stage_order = stageOrder;
    }
    
    const response = await api.post('/learningpaths/paths/mark-stage-completed/', requestData);
    
    console.log('标记学习阶段为已完成响应状态码:', response.status);
    console.log('标记学习阶段为已完成响应:', response.data);
    
    return response;
  } catch (error) {
    console.error('标记学习阶段为已完成失败:', error);
    console.error('错误响应状态码:', error.response?.status);
    console.error('错误响应:', error.response?.data || error.message);
    
    throw error;
  }
};

/**
 * 取消标记学习阶段为已完成
 * @param {number} stageId - 学习阶段ID
 * @returns {Promise} - 返回操作结果的Promise
 */
export const unmarkStageCompleted = async (stageId) => {
  try {
    console.log(`调用API: /learningpaths/paths/unmark-stage-completed/`);
    
    // 构建请求数据，包含阶段ID
    const requestData = {
      stage_id: stageId
    };
    
    const response = await api.post('/learningpaths/paths/unmark-stage-completed/', requestData);
    
    console.log('取消标记学习阶段为已完成响应状态码:', response.status);
    console.log('取消标记学习阶段为已完成响应:', response.data);
    
    return response;
  } catch (error) {
    console.error('取消标记学习阶段为已完成失败:', error);
    console.error('错误响应状态码:', error.response?.status);
    console.error('错误响应:', error.response?.data || error.message);
    
    throw error;
  }
};

/**
 * 获取用户学习进度
 * @param {number} categoryId - 分类ID（可选）
 * @returns {Promise} - 返回用户学习进度的Promise
 */
export const getUserProgress = async (categoryId = null) => {
  try {
    console.log(`调用API: /learningpaths/paths/user-progress/`);
    
    const params = {};
    if (categoryId) {
      params.category_id = categoryId;
    }
    
    const response = await api.get('/learningpaths/paths/user-progress/', { params });
    
    console.log('获取用户学习进度响应状态码:', response.status);
    console.log('获取用户学习进度响应:', response.data);
    
    return response;
  } catch (error) {
    console.error('获取用户学习进度失败:', error);
    console.error('错误响应状态码:', error.response?.status);
    console.error('错误响应:', error.response?.data || error.message);
    
    throw error;
  }
};

/**
 * 记录用户学习时长
 * @param {number} studyHours - 学习时长（小时）
 * @param {string} studyDate - 学习日期（可选，格式：YYYY-MM-DD，默认为今天）
 * @returns {Promise} - 返回操作结果的Promise
 */
export const recordStudyTime = async (studyHours, studyDate = null) => {
  try {
    console.log(`[recordStudyTime] 调用API: /learningpaths/paths/record-study-time/`, {
      study_hours: studyHours,
      study_date: studyDate
    });
    
    const requestData = {
      study_hours: studyHours
    };
    
    if (studyDate) {
      requestData.study_date = studyDate;
    }
    
    const response = await api.post('/learningpaths/paths/record-study-time/', requestData);
    
    console.log('[recordStudyTime] 记录学习时长响应状态码:', response.status);
    console.log('[recordStudyTime] 记录学习时长响应:', response.data);
    
    if (response.data && response.data.success) {
      console.log('[recordStudyTime] 学习时长记录成功:', {
        study_hours: studyHours,
        saved_data: response.data.data
      });
    }
    
    return response;
  } catch (error) {
    console.error('[recordStudyTime] 记录学习时长失败:', error);
    console.error('[recordStudyTime] 错误响应状态码:', error.response?.status);
    console.error('[recordStudyTime] 错误响应:', error.response?.data || error.message);
    
    throw error;
  }
};

/**
 * 获取用户学习时长统计
 * @returns {Promise} - 返回学习时长统计的Promise
 */
export const getStudyTimeStats = async () => {
  try {
    console.log(`调用API: /learningpaths/paths/study-time-stats/`);
    
    const response = await api.get('/learningpaths/paths/study-time-stats/');
    
    console.log('获取学习时长统计响应状态码:', response.status);
    console.log('获取学习时长统计完整响应:', response);
    console.log('获取学习时长统计响应数据:', response.data);
    
    // 返回响应数据（后端直接返回对象，不是包装在data中）
    return response.data || response;
  } catch (error) {
    console.error('获取学习时长统计失败:', error);
    console.error('错误响应状态码:', error.response?.status);
    console.error('错误响应:', error.response?.data || error.message);
    
    throw error;
  }
};