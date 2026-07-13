<template>
  <div class="question-detail">
    <div class="container">
      <!-- 左侧边栏 -->
      <aside v-if="question && !loading" class="sidebar">
        <div class="sidebar-card">
          <h3 class="sidebar-title">
            <i class="fas fa-fire"></i> 热门评论
          </h3>
          <div class="sidebar-content">
            <div v-if="hotAnswers.length > 0" class="hot-answers">
              <div 
                v-for="answer in hotAnswers" 
                :key="answer.id"
                class="hot-answer-item"
                @click="scrollToAnswer(answer.id)"
              >
                <div class="hot-answer-author">{{ answer.author_info.nickname }}</div>
                <div class="hot-answer-content">{{ truncateText(answer.content, 60) }}</div>
                <div class="hot-answer-stats">
                  <span><i class="fas fa-thumbs-up"></i> {{ answer.likes_count }}</span>
                  <span v-if="answer.is_accepted" class="accepted-indicator">已采纳</span>
                </div>
              </div>
            </div>
            <div v-else class="no-hot-answers">
              <p>暂无评论</p>
            </div>
          </div>
        </div>
      </aside>

      <!-- 主内容区域 -->
      <div class="main-content">
        <!-- 返回按钮 -->
        <div class="back-nav">
          <router-link to="/community" class="back-btn">
            <i class="fas fa-arrow-left"></i> 返回社区
          </router-link>
        </div>

        <!-- 帖子详情 -->
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="fetchQuestionDetail" class="retry-btn">重试</button>
      </div>
      <div v-else-if="question" class="question-section">
        <!-- Hero Section -->
        <div class="question-hero">
          <div class="hero-content">
            <h1 class="question-title">{{ question.title }}</h1>
            <div class="hero-meta">
              <div class="meta-item">
                <i class="fas fa-user"></i>
                <span>{{ question.author_info.nickname }}</span>
              </div>
              <div class="meta-item">
                <i class="fas fa-clock"></i>
                <span>{{ question.created_at }}</span>
              </div>
            </div>
          </div>
          <div class="hero-stats">
            <div class="stat-card">
              <div class="stat-icon views-icon">
                <i class="fas fa-eye"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ question.views_count || 0 }}</div>
                <div class="stat-label">浏览</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon answers-icon">
                <i class="fas fa-comments"></i>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ totalAnswers }}</div>
                <div class="stat-label">评论</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Question Content -->
        <div class="question-content-wrapper">
          <div v-if="question.description" class="question-description">
            <div class="description-header">
              <i class="fas fa-info-circle"></i>
              <span>帖子描述</span>
            </div>
            <p>{{ question.description }}</p>
          </div>
          <div class="question-content" v-html="formatContent(question.content || '')"></div>
        </div>

        <!-- Tags and Actions -->
        <div class="question-footer">
          <div class="question-tags">
            <i class="fas fa-tags"></i>
            <span 
              v-for="tag in parseTags(question.tags)" 
              :key="tag"
              class="tag"
            >
              {{ tag }}
            </span>
          </div>
          <div class="question-actions">
            <button
              v-if="isAuthenticated && !isSameUser(question.author_info && question.author_info.id)"
              class="report-btn"
              @click="openReportModal('question', question.id, question.title)"
            >
              <i class="fas fa-flag"></i> 举报
            </button>
            <button
              v-if="isAuthenticated && question.author_info && question.author_info.id === currentUserId"
              class="delete-question-btn"
              @click="openDeleteQuestionModal"
            >
              <i class="fas fa-trash"></i> 删除帖子
            </button>
          </div>
        </div>
      </div>

      <!-- 评论列表 -->
      <div v-if="question && !loading" class="answers-section">
        <div class="answers-header">
            <h2>{{ totalAnswers }} 个评论</h2>
          <div class="answers-sort">
            <select v-model="answersSort" @change="sortAnswers">
              <option value="votes">按点赞数排序</option>
              <option value="time">按时间排序</option>
            </select>
          </div>
        </div>

        <div class="answers-list">
          <!-- 如果有评论但数组为空，重新获取数据 -->
          <div v-if="question && question.answers_count > 0 && answers.length === 0" class="no-answers">
            <p>检测到有评论但未能加载，正在重新获取...</p>
            <button @click="fetchAnswers" class="retry-btn">重新获取</button>
          </div>
          
          <!-- 正常渲染评论列表 -->
          <template v-else-if="sortedAnswers.length > 0">
            <div 
              v-for="answer in sortedAnswers" 
              :key="answer.id"
              :data-answer-id="answer.id"
              class="answer-card"
            >
              <div class="answer-header">
                <div class="answer-author">
                  <i class="fas fa-user"></i>
                  <span>{{ answer.author_info.nickname }}</span>
                  <span class="answer-time">{{ answer.created_at }}</span>
                </div>
                <div v-if="answer.is_accepted" class="accepted-badge">
                  <i class="fas fa-check"></i> 已采纳
                </div>
              </div>
              <div class="answer-content" v-html="formatContent(answer.content)"></div>
              <div class="answer-actions">
                <div class="answer-actions-left">
                  <button 
                    class="action-btn like-btn"
                    :class="{ active: userLikedAnswers.includes(answer.id) }"
                    @click="handleAnswerLike(answer.id)"
                  >
                    <i class="fas fa-thumbs-up"></i>
                    <span>{{ answer.likes_count }}</span>
                  </button>
                  <button 
                    class="action-btn dislike-btn"
                    :class="{ active: userDislikedAnswers.includes(answer.id) }"
                    @click="handleAnswerDislike(answer.id)"
                  >
                    <i class="fas fa-thumbs-down"></i>
                    <span>{{ answer.dislikes_count }}</span>
                  </button>
                </div>
                <div class="answer-actions-right">
                  <button 
                    v-if="isAuthenticated && question && question.author_info && question.author_info.id === currentUserId && !answer.is_accepted"
                    class="action-btn accept-btn"
                    @click.stop="handleAcceptAnswer(answer.id)"
                  >
                    <i class="fas fa-check-circle"></i> 采纳
                  </button>
                  <button 
                    v-if="isAuthenticated && answer.author_info && answer.author_info.id === currentUserId"
                    class="action-btn delete-btn"
                    @click="openDeleteAnswerModal(answer)"
                  >
                    <i class="fas fa-trash"></i> 删除
                  </button>
                  <button 
                    v-if="isAuthenticated && !isSameUser(answer.author_info && answer.author_info.id)"
                    class="action-btn report-btn"
                    @click.stop="openReportModal('answer', answer.id, answer.content)"
                  >
                    <i class="fas fa-flag"></i> 举报
                  </button>
                </div>
              </div>
            </div>
          </template>
          
          <!-- 真正的无评论状态 -->
          <div v-else class="no-answers">
            <p>暂无评论，来做第一个评论者吧！</p>
          </div>
        </div>
        
        <!-- 分页控件 -->
        <div v-if="paginationData && totalAnswers > 0" class="pagination">
          <button 
            @click="goToFirstPage" 
            class="pagination-btn"
            :disabled="currentPage === 1"
          >
            <i class="fas fa-angle-double-left"></i>
          </button>
          <button 
            @click="goToPrevPage" 
            class="pagination-btn"
            :disabled="currentPage === 1"
          >
            <i class="fas fa-angle-left"></i>
          </button>
          
          <span class="pagination-info">
            {{ currentPage }} / {{ paginationData.totalPages }}
          </span>
          <span class="pagination-total">
            共 {{ totalAnswers }} 条评论
          </span>
          
          <button 
            @click="goToNextPage" 
            class="pagination-btn"
            :disabled="currentPage === paginationData.totalPages"
          >
            <i class="fas fa-angle-right"></i>
          </button>
          <button 
            @click="goToLastPage" 
            class="pagination-btn"
            :disabled="currentPage === paginationData.totalPages"
          >
            <i class="fas fa-angle-double-right"></i>
          </button>
        </div>
      </div>

      <!-- 评论表单 -->
      <div v-if="question && !loading" class="answer-form-section">
        <h3>发表你的评论</h3>
        <div v-if="!isAuthenticated" class="login-prompt">
          <p>请先登录后再评论帖子</p>
          <router-link to="/login" class="login-btn">去登录</router-link>
        </div>
        <div v-else class="answer-form">
          <textarea 
            v-model="answerContent"
            placeholder="请输入你的评论..."
            class="answer-textarea"
          ></textarea>
          <div class="answer-form-actions">
            <button 
              @click="submitAnswer"
              :disabled="!answerContent.trim() || submittingAnswer"
              class="submit-answer-btn"
            >
              {{ submittingAnswer ? '提交中...' : '提交评论' }}
            </button>
          </div>
        </div>
      </div>
      </div>

      <div v-if="showReportModal" class="report-modal-overlay" @click.self="closeReportModal">
        <div class="report-modal" @click.stop>
          <div class="report-modal-header">
            <h3>举报{{ reportTarget && reportTarget.type === 'question' ? '帖子' : '评论' }}</h3>
            <button class="close-btn" @click="closeReportModal">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="report-modal-body">
            <label>举报原因 *</label>
            <select v-model="reportForm.reason" class="report-input">
              <option value="">请选择原因</option>
              <option v-for="reason in reportReasons" :key="reason" :value="reason">
                {{ reason }}
              </option>
            </select>
            <label>详细描述（可选）</label>
            <textarea
              class="report-textarea"
              rows="4"
              v-model="reportForm.description"
              placeholder="请填写更多信息，帮助管理员快速处理..."
            ></textarea>
          </div>
          <div class="report-modal-footer">
            <button class="cancel-btn" @click="closeReportModal">取消</button>
            <button
              class="submit-btn"
              :disabled="!reportForm.reason || submittingReport"
              @click="submitReport"
            >
              {{ submittingReport ? '提交中...' : '提交举报' }}
            </button>
          </div>
        </div>
      </div>
    </div>
      <div v-if="showDeleteQuestionConfirm" class="confirm-modal-overlay" @click.self="closeDeleteQuestionModal">
        <div class="confirm-modal">
          <h3>确认删除帖子</h3>
          <p>删除后将无法恢复，确定要删除当前帖子吗？</p>
          <div class="confirm-actions">
            <button class="cancel-btn" @click="closeDeleteQuestionModal">取消</button>
            <button class="danger-btn" @click="confirmDeleteQuestion">删除</button>
          </div>
        </div>
      </div>
      <div v-if="showDeleteAnswerConfirm" class="confirm-modal-overlay" @click.self="closeDeleteAnswerModal">
        <div class="confirm-modal">
          <h3>确认删除评论</h3>
          <p>删除后将无法恢复，确定要删除这条评论吗？</p>
          <div class="confirm-actions">
            <button class="cancel-btn" @click="closeDeleteAnswerModal">取消</button>
            <button class="danger-btn" @click="confirmDeleteAnswer">删除</button>
          </div>
        </div>
      </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import communityService from '../services/communityService';

export default {
  name: 'QuestionDetail',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const question = ref(null);
    const answers = ref([]);
    const loading = ref(false);
    const error = ref('');
    const answersSort = ref('time');
    const userLikedAnswers = ref([]);
    const userDislikedAnswers = ref([]);
    const answerContent = ref('');
    const submittingAnswer = ref(false);
    const showReportModal = ref(false);
    const reportTarget = ref(null);
    const reportForm = ref({
      reason: '',
      description: ''
    });
    const submittingReport = ref(false);
    const reportReasons = [
      '垃圾广告/推广',
      '不当言论或人身攻击',
      '违法违规内容',
      '侵犯版权或隐私',
      '其他'
    ];
    const showDeleteQuestionConfirm = ref(false);
    const showDeleteAnswerConfirm = ref(false);
    const answerToDelete = ref(null);
    
    // 分页相关状态
    const currentPage = ref(1);
    const pageSize = ref(5); // 每页显示5条评论
    const totalAnswers = ref(0);
    const paginationData = ref(null); // 存储分页元数据

    // 检查用户是否已登录
    const isAuthenticated = computed(() => {
      return !!localStorage.getItem('access_token');
    });
    
    // 获取当前登录用户的ID
    const currentUserId = computed(() => {
      try {
        const userInfo = localStorage.getItem('user_info');
        if (userInfo) {
          const parsed = JSON.parse(userInfo);
          return parsed.id;
        }
        return null;
      } catch (e) {
        console.error('解析用户信息失败:', e);
        return null;
      }
    });

    const normalizeId = (value) => {
      if (value === null || value === undefined) return null;
      const num = Number(value);
      return Number.isNaN(num) ? null : num;
    };

    const isSameUser = (authorId) => {
      const currentId = normalizeId(currentUserId.value);
      const otherId = normalizeId(authorId);
      if (!currentId || !otherId) return false;
      return currentId === otherId;
    };

    // 解析标签字符串为数组
    const parseTags = (tagsString) => {
      if (!tagsString) return [];
      return tagsString.split(',').map(tag => tag.trim()).filter(tag => tag);
    };

    // 格式化内容，处理代码块和图片
    const formatContent = (content) => {
      if (!content) return '';
      
      // 简单的格式化处理
      let formatted = content;
      
      // 确保图片有点击放大的样式
      formatted = formatted.replace(/<img/g, '<img class="content-image" ');
      
      // 确保代码块有样式
      formatted = formatted.replace(/<pre/g, '<pre class="code-block" ');
      formatted = formatted.replace(/<code/g, '<code class="code-inline" ');
      
      return formatted;
    };

    // 获取帖子详情
    const fetchQuestionDetail = async () => {
      loading.value = true;
      error.value = '';
      try {
        const questionId = route.params.id;
        console.log(`正在获取帖子${questionId}的详情...`);
        
        // 只获取帖子详情
        const questionResponse = await communityService.getQuestionDetail(questionId);
        
        console.log('帖子详情API响应:', JSON.stringify(questionResponse, null, 2));
        
        question.value = questionResponse;
        
        // 总是调用单独的API获取评论，不使用帖子详情中的answers字段
        await fetchAnswers(currentPage.value);
        
        // 初始化用户的点赞和反对状态
        if (isAuthenticated.value) {
          // 根据评论数据初始化用户的点赞/反对状态
          userLikedAnswers.value = answers.value.filter(answer => 
            answer.is_liked_by_current_user
          ).map(answer => answer.id);
          
          userDislikedAnswers.value = answers.value.filter(answer => 
            answer.is_disliked_by_current_user
          ).map(answer => answer.id);
        }
      } catch (err) {
        console.error('获取数据失败:', err);
        error.value = '获取数据失败，请稍后重试';
        answers.value = [];
      } finally {
        loading.value = false;
      }
    };
    
    // 单独获取评论列表的方法
    const fetchAnswers = async (page = 1) => {
      if (!question.value) {
        console.log('帖子详情未加载，跳过获取评论');
        return;
      }
      
      try {
        const questionId = question.value.id;
        console.log(`开始获取问题${questionId}的评论列表，页码: ${page}, 每页数量: ${pageSize.value}...`);
        
        const startTime = Date.now();
        const answersResponse = await communityService.getAnswers(questionId, page, pageSize.value);
        const endTime = Date.now();
        
        console.log(`API调用耗时: ${endTime - startTime}ms`);
        console.log('评论列表API响应类型:', typeof answersResponse);
        console.log('评论列表API响应是否为数组:', Array.isArray(answersResponse));
        console.log('评论列表API响应结构:', JSON.stringify(Object.keys(answersResponse || {})));
        
        // 强制分页逻辑，无论API是否支持分页
        let answerResults = [];
        let totalCount = 0;
        
        if (answersResponse && answersResponse.results) {
          // API支持分页格式
          answerResults = answersResponse.results;
          totalCount = answersResponse.count || 0;
        } else if (Array.isArray(answersResponse)) {
          // 兼容旧格式并手动分页
          answerResults = answersResponse;
          totalCount = answersResponse.length;
          
          // 手动实现前端分页
          const startIndex = (page - 1) * pageSize.value;
          const endIndex = startIndex + pageSize.value;
          answerResults = answersResponse.slice(startIndex, endIndex);
        } else {
          answerResults = [];
          totalCount = 0;
        }
        
        // 更新本地状态
        answers.value = answerResults;
        totalAnswers.value = totalCount;
        
        // 计算总页数
        const totalPages = Math.ceil(totalCount / pageSize.value);
        
        paginationData.value = {
          total: totalCount,
          page: page,
          pageSize: pageSize.value,
          totalPages: totalPages
        };
        
        // 更新当前页码
        currentPage.value = page;
        
        console.log(`成功获取到${answers.value.length}个评论，总计${totalAnswers.value}个评论，总页数: ${totalPages}`);
      } catch (err) {
        console.error('获取评论列表失败:', err.response ? JSON.stringify(err.response.data) : err.message);
        answers.value = [];
        totalAnswers.value = 0;
        paginationData.value = null;
      }
    };

    // 排序评论
    const sortedAnswers = computed(() => {
      if (!answers.value.length) return [];
      
      const sorted = [...answers.value];
      if (answersSort.value === 'votes') {
        // 按点赞数排序，已采纳的评论排在最前面
        return sorted.sort((a, b) => {
          if (a.is_accepted && !b.is_accepted) return -1;
          if (!a.is_accepted && b.is_accepted) return 1;
          return b.likes_count - a.likes_count;
        });
      } else {
        // 按时间排序
        return sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      }
    });

    // 热门评论：按点赞数排序，取前3个
    const hotAnswers = computed(() => {
      if (!answers.value.length) return [];
      
      const sorted = [...answers.value].sort((a, b) => {
        // 已采纳的评论排在最前面
        if (a.is_accepted && !b.is_accepted) return -1;
        if (!a.is_accepted && b.is_accepted) return 1;
        // 然后按点赞数降序排序
        return b.likes_count - a.likes_count;
      });
      
      return sorted.slice(0, 3);
    });

    const sortAnswers = () => {
      // 排序逻辑通过computed属性自动处理
    };

    const openReportModal = (type, targetId, title) => {
      if (!isAuthenticated.value) {
        router.push('/login');
        return;
      }
      if (type === 'question' && isSameUser(question.value && question.value.author_info && question.value.author_info.id)) {
        alert('不能举报自己发布的帖子');
        return;
      }
      if (type === 'answer') {
        const targetAnswer = answers.value.find(ans => ans.id === targetId);
        if (isSameUser(targetAnswer && targetAnswer.author_info && targetAnswer.author_info.id)) {
          alert('不能举报自己发布的评论');
          return;
        }
      }
      reportTarget.value = {
        type,
        targetId,
        title: type === 'answer' ? (title ? title.slice(0, 60) : '评论内容') : title
      };
      reportForm.value = {
        reason: '',
        description: ''
      };
      showReportModal.value = true;
    };

    const closeReportModal = () => {
      showReportModal.value = false;
    };

    const submitReport = async () => {
      if (!reportForm.value.reason || !reportTarget.value) return;
      submittingReport.value = true;
      try {
        await communityService.submitReport({
          target_type: reportTarget.value.type,
          target_id: reportTarget.value.targetId,
          reason: reportForm.value.reason,
          description: reportForm.value.description
        });
        alert('举报已提交，管理员会尽快处理。');
        showReportModal.value = false;
      } catch (err) {
        console.error('提交举报失败:', err);
      const detail = err.response && err.response.data && err.response.data.detail;
      alert(detail || '提交举报失败，请稍后再试');
      } finally {
        submittingReport.value = false;
      }
    };
    
    // 分页控制方法
    const goToPage = (page) => {
      const totalPages = (paginationData.value && paginationData.value.totalPages) || 1;
      if (page >= 1 && page <= totalPages) {
        fetchAnswers(page);
      }
    };
    
    const goToFirstPage = () => {
      goToPage(1);
    };
    
    const goToLastPage = () => {
      const totalPages = (paginationData.value && paginationData.value.totalPages) || 1;
      goToPage(totalPages);
    };
    
    const goToPrevPage = () => {
      if (currentPage.value > 1) {
        goToPage(currentPage.value - 1);
      }
    };
    
    const goToNextPage = () => {
      const totalPages = (paginationData.value && paginationData.value.totalPages) || 1;
      if (currentPage.value < totalPages) {
        goToPage(currentPage.value + 1);
      }
    };

    // 处理评论点赞
    const handleAnswerLike = async (answerId) => {
      if (!isAuthenticated.value) {
        alert('请先登录后再操作');
        return;
      }

      try {
        // 检查是否已经点赞
        const isLiked = userLikedAnswers.value.includes(answerId);
        // 检查是否已经反对
        const isDisliked = userDislikedAnswers.value.includes(answerId);
        
        if (isLiked) {
          // 取消点赞：传递 is_like: true，后端会识别为取消操作
          await communityService.toggleAnswerLike(answerId, true);
          userLikedAnswers.value = userLikedAnswers.value.filter(id => id !== answerId);
        } else {
          // 添加点赞：传递 is_like: true
          await communityService.toggleAnswerLike(answerId, true);
          // 先取消可能的反对
          if (isDisliked) {
            userDislikedAnswers.value = userDislikedAnswers.value.filter(id => id !== answerId);
          }
          userLikedAnswers.value.push(answerId);
        }
        
        // 重新获取评论列表以更新点赞/反对数量，保持当前页码
        await fetchAnswers(currentPage.value);
      } catch (err) {
        console.error('点赞操作失败:', err);
        alert('操作失败，请稍后重试');
      }
    };

    // 处理评论反对
    const handleAnswerDislike = async (answerId) => {
      if (!isAuthenticated.value) {
        alert('请先登录后再操作');
        return;
      }

      try {
        // 检查是否已经反对
        const isDisliked = userDislikedAnswers.value.includes(answerId);
        // 检查是否已经点赞
        const isLiked = userLikedAnswers.value.includes(answerId);
        
        if (isDisliked) {
          // 取消反对：传递 is_like: false，后端会识别为取消操作
          await communityService.toggleAnswerLike(answerId, false);
          userDislikedAnswers.value = userDislikedAnswers.value.filter(id => id !== answerId);
        } else {
          // 添加反对：传递 is_like: false
          await communityService.toggleAnswerLike(answerId, false);
          // 先取消可能的点赞
          if (isLiked) {
            userLikedAnswers.value = userLikedAnswers.value.filter(id => id !== answerId);
          }
          userDislikedAnswers.value.push(answerId);
        }
        
        // 重新获取评论列表以更新点赞/反对数量，保持当前页码
        await fetchAnswers(currentPage.value);
      } catch (err) {
        console.error('反对操作失败:', err);
        alert('操作失败，请稍后重试');
      }
    };

    // 提交评论
    const submitAnswer = async () => {
      if (!answerContent.value.trim()) return;
      
      submittingAnswer.value = true;
      try {
        const answerData = {
          question: question.value.id,
          content: answerContent.value
        };
        
        // 调用提交评论API
        await communityService.createAnswer(answerData);
        
        // 提交成功后，重新获取帖子详情以更新评论列表
        await fetchQuestionDetail();
        // 提交新评论后返回到第一页
        currentPage.value = 1;
        await fetchAnswers(1);
        answerContent.value = '';
        
        // 滚动到新评论
        setTimeout(() => {
          const lastAnswer = document.querySelector('.answer-card:last-child');
          if (lastAnswer) {
            lastAnswer.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, 100);
      } catch (err) {
        console.error('提交评论失败:', err);
        alert('提交失败，请稍后重试');
      } finally {
        submittingAnswer.value = false;
      }
    };
    
    const openDeleteAnswerModal = (answer) => {
      answerToDelete.value = answer;
      showDeleteAnswerConfirm.value = true;
    };

    const closeDeleteAnswerModal = () => {
      showDeleteAnswerConfirm.value = false;
      answerToDelete.value = null;
    };

    // 处理删除评论
    const confirmDeleteAnswer = async () => {
      if (!answerToDelete.value) return;
      const answerId = answerToDelete.value.id;

      try {
        await communityService.deleteAnswer(answerId);
        
        // 从本地状态中移除评论
        answers.value = answers.value.filter(answer => answer.id !== answerId);
        
        // 重新获取帖子详情以更新评论计数，但保持当前页码
        const currentPageNum = currentPage.value;
        await fetchQuestionDetail();
        await fetchAnswers(currentPageNum);
        
      } catch (err) {
        console.error('删除评论失败:', err);
        alert('删除失败，请稍后重试');
      } finally {
        closeDeleteAnswerModal();
      }
    };
    
    // 处理采纳回答
    const handleAcceptAnswer = async (answerId) => {
      if (!confirm('确定要采纳这个回答吗？这将取消之前采纳的回答。')) {
        return;
      }
      
      try {
        await communityService.acceptAnswer(answerId);
        
        // 重新获取帖子详情和评论列表以更新采纳状态
        await fetchQuestionDetail();
        await fetchAnswers(currentPage.value);
        
        alert('采纳成功！');
      } catch (err) {
        console.error('采纳回答失败:', err);
      const detail = err.response && err.response.data && err.response.data.detail;
      alert('采纳失败：' + (detail || '未知错误'));
      }
    };

    // 初始化图片点击放大和代码复制功能
    const initContentFeatures = () => {
      // 图片点击放大功能
      document.querySelectorAll('.content-image').forEach(img => {
        img.addEventListener('click', (e) => {
          // 简单的图片预览逻辑
          const modal = document.createElement('div');
          modal.className = 'image-viewer';
          modal.innerHTML = `
            <div class="image-viewer-overlay">
              <img src="${e.target.src}" class="preview-image">
              <button class="close-btn">&times;</button>
            </div>
          `;
          document.body.appendChild(modal);
          
          modal.querySelector('.close-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
          });
        });
      });
      
      // 代码复制功能
      document.querySelectorAll('pre.code-block').forEach((block) => {
        const button = document.createElement('button');
        button.className = 'copy-code-btn';
        button.textContent = '复制';
        button.addEventListener('click', () => {
          const code = block.textContent;
          navigator.clipboard.writeText(code).then(() => {
            button.textContent = '已复制！';
            setTimeout(() => {
              button.textContent = '复制';
            }, 2000);
          });
        });
        block.parentNode.insertBefore(button, block.nextSibling);
      });
    };

    // 监听问题数据变化，初始化内容功能
    watch(question, (newQuestion) => {
      if (newQuestion) {
        setTimeout(() => {
          initContentFeatures();
        }, 100);
      }
    });

    const openDeleteQuestionModal = () => {
      showDeleteQuestionConfirm.value = true;
    };

    const closeDeleteQuestionModal = () => {
      showDeleteQuestionConfirm.value = false;
    };

    // 处理删除帖子
    const confirmDeleteQuestion = async () => {
      try {
        await communityService.deleteQuestion(question.value.id);
        router.push('/community');
      } catch (err) {
        console.error('删除帖子失败:', err);
        alert('删除失败，请稍后重试');
      } finally {
        closeDeleteQuestionModal();
      }
    };

    // 监听路由参数变化
    watch(() => route.params.id, () => {
      fetchQuestionDetail();
    });

    // 截断文本
    const truncateText = (text, length) => {
      if (!text) return '';
      // 移除HTML标签（简单正则）
      const plainText = text.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim();
      if (plainText.length <= length) return plainText;
      return plainText.substring(0, length) + '...';
    };

    // 滚动到指定评论
    const scrollToAnswer = (answerId) => {
      const answerElement = document.querySelector(`[data-answer-id="${answerId}"]`);
      if (answerElement) {
        answerElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // 高亮显示
        answerElement.style.transition = 'background-color 0.3s';
        answerElement.style.backgroundColor = '#fef3c7';
        setTimeout(() => {
          answerElement.style.backgroundColor = '';
        }, 2000);
      }
    };

    // 页面加载时获取数据
    onMounted(() => {
      fetchQuestionDetail();
    });

    return {
      question,
      answers,
      loading,
      error,
      answersSort,
      sortedAnswers,
      hotAnswers,
      userLikedAnswers,
      userDislikedAnswers,
      answerContent,
      submittingAnswer,
      isAuthenticated,
      currentUserId,
      // 分页相关
      currentPage,
      pageSize,
      totalAnswers,
      paginationData,
      parseTags,
      formatContent,
      fetchQuestionDetail,
      sortAnswers,
      handleAnswerLike,
      handleAnswerDislike,
      submitAnswer,
      openDeleteAnswerModal,
      closeDeleteAnswerModal,
      confirmDeleteAnswer,
      openDeleteQuestionModal,
      closeDeleteQuestionModal,
      confirmDeleteQuestion,
      // 分页控制方法
      goToPage,
      goToFirstPage,
      goToLastPage,
      goToPrevPage,
      goToNextPage,
      handleAcceptAnswer,
      showReportModal,
      showDeleteQuestionConfirm,
      showDeleteAnswerConfirm,
      answerToDelete,
      reportForm,
      reportReasons,
      submittingReport,
      openReportModal,
      closeReportModal,
      submitReport,
      reportTarget,
      isSameUser,
      truncateText,
      scrollToAnswer
    };
  }
};
</script>

<style scoped>
.question-detail {
  padding: 2rem 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 120px);
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 2rem;
}

.main-content {
  min-width: 0;
}

@media (max-width: 1200px) {
  .container {
    grid-template-columns: 1fr;
    max-width: 1200px;
  }
  
  .sidebar {
    display: none;
  }
}

.back-nav {
  margin-bottom: 1rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #2563eb;
  text-decoration: none;
  padding: 0.5rem 1rem;
  background: white;
  border-radius: 4px;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #f8f9fa;
}

.loading,
.error {
  text-align: center;
  padding: 3rem 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #dc3545;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.question-section,
.answers-section,
.answer-form-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.06);
}

/* Hero Section */
.question-hero {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  border-radius: 12px 12px 0 0;
  padding: 2.5rem;
  margin: -2rem -2rem 2rem -2rem;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
}

.hero-content {
  flex: 1;
  min-width: 300px;
}

.question-title {
  font-size: 2rem;
  color: white;
  margin-bottom: 1rem;
  line-height: 1.4;
  font-weight: 600;
}

.hero-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
}

.meta-item i {
  opacity: 0.8;
}

.hero-stats {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 120px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.views-icon {
  background: rgba(59, 130, 246, 0.3);
  color: #93c5fd;
}

.answers-icon {
  background: rgba(16, 185, 129, 0.3);
  color: #6ee7b7;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.85rem;
  opacity: 0.9;
}

.question-content-wrapper {
  margin-bottom: 1.5rem;
}

.question-content {
  line-height: 1.8;
  color: #333;
  font-size: 1.05rem;
}

.question-content img {
  max-width: 100%;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.question-content img:hover {
  transform: scale(1.02);
}

.question-content pre {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
}

.question-content code {
  background: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.question-tags {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.question-tags i {
  color: #6b7280;
  font-size: 0.9rem;
}

.tag {
  padding: 0.4rem 1rem;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  border-radius: 20px;
  font-size: 0.9rem;
  color: #4b5563;
  transition: all 0.3s;
  font-weight: 500;
  border: 1px solid #d1d5db;
}

.tag:hover {
  background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.delete-question-btn {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.delete-question-btn:hover {
  background: #c82333;
}

.report-btn {
  border: 1px solid #f59e0b;
  color: #f59e0b;
  background: transparent;
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  transition: all 0.2s;
}

.report-btn:hover {
  background: rgba(245, 158, 11, 0.1);
}

.answer-actions .report-btn {
  border-color: #f97316;
  color: #f97316;
  background: transparent;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.2s;
}

.answer-card:hover .answer-actions .report-btn {
  opacity: 1;
}

.answer-actions .report-btn:hover {
  background: #f97316;
  color: white;
  border-color: #f97316;
}

.report-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1100;
}

.report-modal {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 25px 60px rgba(30, 41, 59, 0.25);
  overflow: hidden;
}

.report-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.report-modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #111827;
}

.report-modal-header .close-btn {
  background: transparent;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: #94a3b8;
  transition: color 0.2s;
}

.report-modal-header .close-btn:hover {
  color: #475569;
}

.report-modal-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.report-modal-body label {
  font-weight: 600;
  color: #1f2937;
}

.target-title {
  background: #f8fafc;
  padding: 10px 12px;
  border-radius: 10px;
  color: #475569;
  font-size: 0.95rem;
}

.report-input,
.report-textarea {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 0.95rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.report-input:focus,
.report-textarea:focus {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
  outline: none;
}

.report-modal-footer {
  padding: 16px 24px 20px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.report-modal-footer .cancel-btn {
  background: #f3f4f6;
  border: none;
  border-radius: 10px;
  padding: 10px 18px;
  color: #374151;
  cursor: pointer;
}

.report-modal-footer .submit-btn {
  background: linear-gradient(135deg, #f59e0b, #f97316);
  border: none;
  border-radius: 10px;
  padding: 10px 18px;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(249, 115, 22, 0.35);
}

.report-modal-footer .submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.confirm-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1200;
}

.confirm-modal {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.25);
}

.confirm-modal h3 {
  margin: 0 0 12px;
  font-size: 1.1rem;
  color: #111827;
  font-weight: 600;
}

.confirm-modal p {
  margin: 0;
  color: #4b5563;
  line-height: 1.6;
  font-size: 0.95rem;
}

.confirm-hint {
  margin-top: 10px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
  color: #475569;
  font-size: 0.9rem;
}

.confirm-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.confirm-actions .cancel-btn,
.confirm-actions .danger-btn {
  padding: 8px 18px;
  border-radius: 8px;
  border: none;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.2s;
}

.confirm-actions .cancel-btn {
  background: #f3f4f6;
  color: #4b5563;
}

.confirm-actions .cancel-btn:hover {
  background: #e5e7eb;
}

.confirm-actions .danger-btn {
  background: #ef4444;
  color: #fff;
  box-shadow: 0 10px 20px rgba(239, 68, 68, 0.25);
}

.confirm-actions .danger-btn:hover {
  background: #dc2626;
}

.question-description {
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-left: 4px solid #2563eb;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
}

.description-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #1e40af;
  font-size: 0.95rem;
}

.description-header i {
  color: #2563eb;
}

.question-description p {
  margin: 0;
  color: #1e3a8a;
  font-size: 1rem;
  line-height: 1.7;
}

.question-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.question-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.answers-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.answers-header h2 {
  font-size: 1.5rem;
  color: #1f2937;
  font-weight: 600;
}

.answers-sort select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.answer-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  transition: all 0.3s;
  background: white;
  position: relative;
}

.answer-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
  border-color: #d1d5db;
}

.answer-card:has(.accepted-badge) {
  border-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
  border-width: 2px;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.answer-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #333;
}

.answer-time {
  color: #6c757d;
  margin-left: 1rem;
  font-weight: normal;
}

.answer-content {
  line-height: 1.8;
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.05rem;
}

.answer-content img {
  max-width: 100%;
  border-radius: 4px;
  cursor: pointer;
}

.answer-content pre {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  position: relative;
}

.answer-content code {
  background: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.answer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0;
}

.answer-actions-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.answer-actions-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  color: #666;
}

.action-btn:hover {
  background: #f8f9fa;
}

.action-btn.active {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

.like-btn {
  color: #28a745;
  border-color: #28a745;
}

.like-btn:hover:not(.active) {
  background: #28a745;
  color: white;
  border-color: #28a745;
}

.like-btn.active {
  background: #28a745;
  border-color: #28a745;
  color: white;
}

.like-btn.active:hover {
  background: #218838;
  border-color: #218838;
}

.dislike-btn {
  color: #dc3545;
  border-color: #dc3545;
}

.dislike-btn:hover:not(.active) {
  background: #dc3545;
  color: white;
  border-color: #dc3545;
}

.dislike-btn.active {
  background: #dc3545;
  border-color: #dc3545;
  color: white;
}

.dislike-btn.active:hover {
  background: #c82333;
  border-color: #c82333;
}

.delete-btn {
  color: #dc3545;
  border-color: #dc3545;
  background: transparent;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.2s;
}

.answer-card:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: #dc3545;
  color: white;
  border-color: #dc3545;
}

.accept-btn {
  color: #10b981;
  border-color: #10b981;
  background: transparent;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.2s;
}

.answer-card:hover .accept-btn {
  opacity: 1;
}

.accept-btn:hover {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.accepted-badge {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
}

.no-answers {
  text-align: center;
  padding: 3rem 0;
  color: #6c757d;
}

/* 分页样式 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  color: #6c757d;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #2563eb;
  color: #2563eb;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 500;
  min-width: 60px;
  text-align: center;
}

.pagination-total {
  font-size: 0.9rem;
  color: #6c757d;
  font-style: italic;
}

.answer-form-section h3 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #1f2937;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.answer-form-section h3::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  border-radius: 2px;
}

.login-prompt {
  text-align: center;
  padding: 2rem 0;
  color: #6c757d;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border-radius: 8px;
  border: 1px dashed #d1d5db;
}

.login-btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: #2563eb;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  transition: background 0.3s;
}

.login-btn:hover {
  background: #2625ebff;
}

.answer-textarea {
  width: 100%;
  min-height: 150px;
  padding: 1rem 1.25rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  margin-bottom: 1rem;
  box-sizing: border-box;
  transition: all 0.3s;
  background: #fafafa;
  font-family: inherit;
}

.answer-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  background: white;
}

.answer-form-actions {
  display: flex;
  justify-content: flex-end;
}

.submit-answer-btn {
  padding: 0.875rem 2.5rem;
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.submit-answer-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

.submit-answer-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 图片查看器样式 */
.image-viewer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
}

.image-viewer-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-image {
  max-width: 90%;
  max-height: 90%;
  border-radius: 4px;
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 30px;
  font-size: 40px;
  color: white;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.close-btn:hover {
  opacity: 1;
}

/* 代码复制按钮 */
.copy-code-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 0.3rem 0.6rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 3px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.3s;
}

.copy-code-btn:hover {
  background: #2625ebff;
}

/* 侧边栏样式 */
.sidebar {
  position: sticky;
  top: 90px;
  height: fit-content;
  max-height: calc(100vh - 110px);
  overflow-y: auto;
}

.sidebar-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.sidebar-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.sidebar-title i {
  color: #2563eb;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 500;
}

.info-value {
  font-size: 0.95rem;
  color: #1f2937;
  font-weight: 500;
}

.info-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.sidebar-tag {
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  border-radius: 12px;
  font-size: 0.8rem;
  color: #4b5563;
  font-weight: 500;
}

.hot-answers {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.hot-answer-item {
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.hot-answer-item:hover {
  background: #ffffff;
  border-color: #2563eb;
  transform: translateX(6px) translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15), 0 2px 4px rgba(0, 0, 0, 0.1);
}

.hot-answer-author {
  font-size: 0.85rem;
  font-weight: 600;
  color: #2563eb;
  margin-bottom: 0.5rem;
}

.hot-answer-content {
  font-size: 0.9rem;
  color: #4b5563;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.hot-answer-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: #6b7280;
}

.hot-answer-stats i {
  margin-right: 0.25rem;
}

.accepted-indicator {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.no-hot-answers {
  text-align: center;
  padding: 2rem 0;
  color: #9ca3af;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .container {
    padding: 0 1rem;
  }
  
  .question-section,
  .answers-section,
  .answer-form-section {
    padding: 1.5rem;
  }
  
  .question-hero {
    padding: 1.5rem;
    margin: -1.5rem -1.5rem 1.5rem -1.5rem;
    flex-direction: column;
  }
  
  .question-title {
    font-size: 1.5rem;
  }
  
  .hero-stats {
    width: 100%;
    justify-content: space-between;
  }
  
  .stat-card {
    flex: 1;
    min-width: 100px;
  }
  
  .question-footer {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .question-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .answers-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .answer-header {
    flex-wrap: wrap;
  }
  
  .accepted-badge {
    margin-left: 0;
    margin-top: 0.5rem;
  }
}
</style>