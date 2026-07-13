import axios from 'axios';
import { setupTokenRefreshInterceptor } from '@/utils/tokenRefresh';
import { API_BASE_URL } from '@/config/api';

const api = axios.create({
  baseURL: `${API_BASE_URL}/community/`,
});

// 请求拦截器 - 添加认证token和详细日志
api.interceptors.request.use(
  (config) => {
    console.log('发送API请求:', {
      method: config.method,
      url: config.baseURL + config.url,
      params: config.params,
      data: config.data,
      headers: { ...config.headers }
    });
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('请求配置错误:', error);
    return Promise.reject(error);
  }
);

// 设置token自动刷新拦截器
setupTokenRefreshInterceptor(api);

// 响应拦截器 - 记录响应信息
api.interceptors.response.use(
  (response) => {
    console.log('API响应成功:', {
      url: response.config.baseURL + response.config.url,
      status: response.status,
      data: response.data
    });
    return response;
  },
  (error) => {
    console.error('API响应错误:', {
      url: error.config ? error.config.baseURL + error.config.url : 'unknown',
      error: error
    });
    return Promise.reject(error);
  }
);

const communityService = {
  /**
   * 获取问题列表
   * @param {Object} params - 查询参数
   * @param {string} params.sort - 排序方式: 'latest' | 'hot'
   * @param {string} params.category - 分类ID
   * @param {string} params.search - 搜索关键词
   * @param {string} params.user_id - 用户ID，用于筛选特定用户的提问
   * @returns {Promise}
   */
  getQuestions(params = {}) {
    console.log('调用getQuestions，完整URL:', api.defaults.baseURL + 'questions/');
    return api.get('questions/', { params })
      .then(response => {
        console.log('getQuestions成功，返回数据:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error('获取问题列表失败:', error);
        if (error.response) {
          // 服务器响应了，但状态码不是2xx
          console.error('错误状态码:', error.response.status);
          console.error('错误数据:', error.response.data);
        } else if (error.request) {
          // 请求已发送，但没有收到响应
          console.error('没有收到响应:', error.request);
        } else {
          // 设置请求时发生错误
          console.error('请求设置错误:', error.message);
        }
        throw error;
      });
  },

  /**
   * 获取问题详情
   * @param {number} questionId - 问题ID
   * @returns {Promise}
   */
  getQuestionDetail(questionId) {
    return api.get(`questions/${questionId}/`)
      .then(response => response.data)
      .catch(error => {
        console.error(`获取问题${questionId}详情失败:`, error);
        throw error;
      });
  },

  /**
   * 创建问题
   * @param {Object} questionData - 问题数据
   * @returns {Promise}
   */
  createQuestion(questionData) {
    return api.post('questions/', questionData)
      .then(response => response.data)
      .catch(error => {
        console.error('创建问题失败:', error);
        throw error;
      });
  },

  /**
   * 点赞/取消点赞问题
   * @param {number} questionId - 问题ID
   * @returns {Promise}
   */
  toggleQuestionLike(questionId) {
    return api.post(`questions/${questionId}/like/`)
      .then(response => response.data)
      .catch(error => {
        console.error(`问题点赞操作失败:`, error);
        throw error;
      });
  },

  /**
   * 获取问题的评论列表
   * @param {number} questionId - 问题ID
   * @param {number} page - 页码，从1开始
   * @param {number} pageSize - 每页显示数量
   * @returns {Promise}
   */
  getAnswers(questionId, page = 1, pageSize = 10) {
    const params = { 
      question_id: questionId 
    };
    
    // 添加分页参数
    if (page) params.page = page;
    if (pageSize) params.page_size = pageSize;
    
    console.log('调用getAnswers API，参数:', params);
    
    return api.get('answers/', { params })
      .then(response => {
        console.log('getAnswers API返回数据:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error(`获取评论列表失败:`, error);
        throw error;
      });
  },

  /**
   * 创建回答
   * @param {Object} answerData - 回答数据
   * @returns {Promise}
   */
  createAnswer(answerData) {
    return api.post('answers/', answerData)
      .then(response => response.data)
      .catch(error => {
        console.error('创建回答失败:', error);
        throw error;
      });
  },

  /**
   * 点赞/取消点赞回答
   * @param {number} answerId - 回答ID
   * @param {boolean} isLike - 是否点赞（true为赞，false为踩）
   * @returns {Promise}
   */
  toggleAnswerLike(answerId, isLike = true) {
    return api.post(`answers/${answerId}/like/`, { is_like: isLike })
      .then(response => response.data)
      .catch(error => {
        console.error(`回答点赞操作失败:`, error);
        throw error;
      });
  },

  /**
   * 采纳回答
   * @param {number} answerId - 回答ID
   * @returns {Promise}
   */
  acceptAnswer(answerId) {
    return api.post(`answers/${answerId}/accept/`)
      .then(response => {
        console.log('采纳回答成功:', response.data);
        return response.data;
      })
      .catch(error => {
        console.error(`采纳回答失败:`, error);
        throw error;
      });
  },
  
  /**
   * 删除问题
   * @param {number} questionId - 问题ID
   * @returns {Promise}
   */
  deleteQuestion(questionId) {
    return api.delete(`questions/${questionId}/`)
      .then(response => response.data)
      .catch(error => {
        console.error(`删除问题失败:`, error);
        throw error;
      });
  },
  
  /**
   * 删除回答
   * @param {number} answerId - 回答ID
   * @returns {Promise}
   */
  deleteAnswer(answerId) {
    return api.delete(`answers/${answerId}/`)
      .then(response => response.data)
      .catch(error => {
        console.error(`删除回答失败:`, error);
        throw error;
      });
  },

  /**
   * 获取所有回答（管理员专用）
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.page_size - 每页数量
   * @returns {Promise}
   */
  getAllAnswers(params = {}) {
    return api.get('answers/', { params })
      .then(response => response.data)
      .catch(error => {
        console.error('获取所有回答失败:', error);
        throw error;
      });
  },

  /**
   * 提交帖子/评论举报
   * @param {{target_type: 'question'|'answer', target_id: number, reason: string, description?: string}} payload
   */
  submitReport(payload) {
    return api.post('reports/', payload)
      .then(response => response.data)
      .catch(error => {
        console.error('提交举报失败:', error);
        throw error;
      });
  },

  /**
   * 获取举报列表（管理员）
   * @param {Object} params
   */
  getReports(params = {}) {
    return api.get('reports/', { params })
      .then(response => response.data)
      .catch(error => {
        console.error('获取举报列表失败:', error);
        throw error;
      });
  },

  /**
   * 更新举报状态（管理员）
   * @param {number} reportId 
   * @param {Object} data 
   */
  updateReport(reportId, data) {
    return api.patch(`reports/${reportId}/`, data)
      .then(response => response.data)
      .catch(error => {
        console.error('更新举报状态失败:', error);
        throw error;
      });
  }
};

export default communityService;