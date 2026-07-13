<template>
  <div class="ai-assistant">
    <div class="container">
      <div class="page-header">
        <h1>AI 学习助手</h1>
        <p>专业的编程学习问答助手，为你解答技术疑惑</p>
      </div>

      <div class="assistant-layout">
        <div class="chat-panel">
          <!-- 对话容器 -->
          <div class="chat-container glass-panel">
            <!-- 对话历史 -->
            <div class="chat-history" ref="chatHistory">
            <!-- 清除历史按钮 -->
            <div v-if="messages.length > 0" class="clear-history-container">
              <button class="clear-history-btn" @click="clearChatHistory">
                <i class="fas fa-trash-alt"></i> 清除对话历史
              </button>
            </div>
            <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="ai-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
              <p>你好！欢迎使用智慧校园学习平台的AI助手。</p>
              <p>我可以帮助你：</p>
              <ul>
                <li>解答各类问题技术疑惑</li>
                <li>提供个性化的学习建议</li>
                <li>推荐平台上的优质学习资源</li>
              </ul>
              <p>请输入你的问题，我会为你提供专业的帮助！</p>
            </div>
          </div>

          <!-- 对话消息 -->
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            :class="['message', message.role]"
          >
            <div :class="message.role === 'user' ? 'user-avatar' : 'ai-avatar'">
              <i v-if="message.role === 'user'" class="fas fa-user"></i>
              <i v-else class="fas fa-robot"></i>
            </div>
            <div class="message-content">
              <div v-if="message.role === 'user'" class="message-text">{{ message.content }}</div>
              <div v-else class="message-text" v-html="formatMessage(message.content)"></div>
              
              <!-- AI回答后的相关操作 -->
              <div v-if="message.role === 'assistant'" class="message-actions">
                <button 
                  class="action-btn community-btn"
                  @click="askInCommunity(message.content)"
                >
                  <i class="fas fa-users"></i> 到社区提问
                </button>
              </div>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="loading" class="message assistant loading-message">
            <div class="ai-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-container">
          <div class="chat-input-wrapper">
            <div class="input-wrapper">
                <textarea
                  v-model="inputMessage"
                  class="chat-input"
                  placeholder="输入你的问题..."
                  rows="3"
                  maxlength="1000"
                  :style="{ height: 'auto', minHeight: '24px', width: '95%' }"
                  @input="adjustTextareaHeight"
                  ref="textareaRef"
                ></textarea>
            </div>
            <div class="button-wrapper">
              <div class="input-tips">
                <span class="char-count">{{ inputMessage.length }}/1000</span>
              </div>
              <button 
                class="send-btn"
                @click="sendMessage"
                :disabled="!inputMessage.trim() || loading"
              >
                <i class="fas fa-paper-plane"></i> 发送
              </button>
            </div>
          </div>
        </div>
      </div>
        </div>

        <aside class="assistant-sidebar">
          <section class="sidebar-card guide-card">
            <div class="sidebar-card-header">
              <h3><i class="fas fa-compass"></i> 使用指南</h3>
            </div>
            <ul class="guide-list">
              <li>
                <strong>描述清晰</strong>
                <span>说明目标、背景与遇到的问题</span>
              </li>
              <li>
                <strong>多轮追问</strong>
                <span>可基于回答继续追问、补充</span>
              </li>
              <li>
                <strong>资源推荐</strong>
                <span>若站内有课程或文章，会优先推荐</span>
              </li>
            </ul>
          </section>

          <section class="sidebar-card faq-card">
            <div class="sidebar-card-header">
              <h3><i class="fas fa-question-circle"></i> 常见问题</h3>
            </div>
            <ul class="faq-list">
              <li>
                <p class="faq-question">AI 助手会保存我的对话吗？</p>
                <p class="faq-answer">仅在当前浏览器本地保存，可随时清除。</p>
              </li>
              <li>
                <p class="faq-question">推荐资源打不开怎么办？</p>
                <p class="faq-answer">先刷新页面，如仍异常可到社区反馈。</p>
              </li>
              <li>
                <p class="faq-question">如何获取更多学习资料？</p>
                <p class="faq-answer">访问“学习路径”或“资源中心”页面。</p>
              </li>
            </ul>
          </section>
        </aside>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { resourceService } from '../services/resource.js';
import { getCategories, getAllTechnologies } from '../services/category.js';

export default {
  name: 'AIAssistant',
  setup() {
    const router = useRouter();
    const messages = ref([]);
    const inputMessage = ref('');
    const loading = ref(false);
    const chatHistory = ref(null);
    const textareaRef = ref(null);
    const contentCategories = ref([]);
    const categoriesLoaded = ref(false);
    
    // 存储键名
    const STORAGE_KEY = 'ai_assistant_chat_history';

    // DeepSeek API配置
    const API_URL = 'https://ark.cn-beijing.volces.com/api/v3/chat/completions';
    const API_KEY = '4ddec786-f593-477d-ad76-afb95c3b2d13';
    const MODEL = 'deepseek-v3-250324';

    // 系统提示词（支持各种学习内容类型）
    const systemPrompt = {
      role: 'system',
      content: '你是智慧校园学习平台的专业AI学习助手，能够帮助用户学习各种知识内容。请用友好、清晰的语言解答用户的问题，提供详细的解释和实用的建议。\n\n重要：\n1. 【严禁编造链接】绝对不要创建任何链接！无论是Markdown链接还是直接提到的页面名称，如"实践项目专区"、"在线编程实验室"等都不能提及。\n2. 对于代码相关问题，请提供清晰的代码示例和解释。\n3. 根据用户的问题类型，提供有针对性的、结构化的回答。\n4. 不仅限于编程技术，还应支持其他领域的学习内容，如语言学习、艺术、科学、人文等。\n5. 如果用户询问学习资源，请只提供学习建议和方法，不要推荐任何具体的资源或页面。'
    };

    // 保存对话历史到localStorage
    const saveChatHistory = () => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.value));
      } catch (error) {
        console.error('保存对话历史失败:', error);
      }
    };
    
    // 从localStorage加载对话历史
    const loadChatHistory = () => {
      try {
        const savedHistory = localStorage.getItem(STORAGE_KEY);
        if (savedHistory) {
          messages.value = JSON.parse(savedHistory);
        }
      } catch (error) {
        console.error('加载对话历史失败:', error);
        messages.value = [];
      }
    };
    
    // 清除对话历史
    const clearChatHistory = () => {
      // 添加确认对话框，避免误操作
      if (confirm('确定要清除所有对话历史吗？此操作无法撤销。')) {
        messages.value = [];
        try {
          localStorage.removeItem(STORAGE_KEY);
          // 添加一个简短的提示
          alert('对话历史已清除');
        } catch (error) {
          console.error('清除对话历史失败:', error);
          alert('清除对话历史失败，请重试');
        }
      }
    };
    
    // 发送消息给AI
    const sendMessage = async () => {
      const message = inputMessage.value.trim();
      if (!message || loading.value) return;

      // 添加用户消息到对话历史
      messages.value.push({ role: 'user', content: message });
      // 保存对话历史
      saveChatHistory();
      inputMessage.value = '';
      loading.value = true;

      // 滚动到底部
      await nextTick();
      scrollToBottom();

      try {
        // 判断是否是学习资源相关问题（通用方法，支持各种学习内容）
        const isResourceQuestion = message.toLowerCase().includes('学习') || 
                                  message.toLowerCase().includes('资源') ||
                                  message.toLowerCase().includes('教程') ||
                                  message.toLowerCase().includes('推荐') ||
                                  message.toLowerCase().includes('learn') ||
                                  message.toLowerCase().includes('resource') ||
                                  message.toLowerCase().includes('tutorial') ||
                                  message.toLowerCase().includes('recommend') ||
                                  message.toLowerCase().includes('课程') ||
                                  message.toLowerCase().includes('课程推荐') ||
                                  message.toLowerCase().includes('资料') ||
                                  message.toLowerCase().includes('书籍') ||
                                  message.toLowerCase().includes('article') ||
                                  message.toLowerCase().includes('book') ||
                                  message.toLowerCase().includes('course');

        let aiResponse = '';
        let siteResources = [];
        let extractedKeywords = '';

        // 如果是资源相关问题，尝试从网站获取相关资源
        if (isResourceQuestion) {
          try {
            // 从问题中提取关键词用于搜索
            extractedKeywords = extractKeywords(message);
            console.log('提取的关键词:', extractedKeywords);
            
            // 优先从学习路径获取推荐资源 - 这些资源是按技术分类组织好的
            siteResources = await fetchResourcesFromLearningPaths(extractedKeywords || message);
            console.log('从学习路径获取到的资源:', siteResources);

            // 如果学习路径没有足够资源，再搜索补充
            if (!siteResources || siteResources.length < 3) {
              if (extractedKeywords) {
                const searchResult = await resourceService.searchResources(extractedKeywords);
                const searchResources = normalizeSiteResources(searchResult);
                siteResources = mergeUniqueResources(siteResources, searchResources);
              }
              
              // 如果还是不够，使用兜底资源
              if (!siteResources || siteResources.length < 3) {
                const fallbackResources = await fetchFallbackResources(extractedKeywords || message);
                siteResources = mergeUniqueResources(siteResources, fallbackResources);
              }
            }
          } catch (resourceError) {
            console.log('获取网站资源失败，仅使用AI回答:', resourceError);
          }
        }
        
        const internalResources = (siteResources || []).filter(resource => !resource.is_external);
        const externalResources = (siteResources || []).filter(resource => resource.is_external);
        const hasAnyResources = internalResources.length > 0 || externalResources.length > 0;
        
        // 获取内容类型，用于优化AI回答
        // 如果分类数据尚未加载完成，先使用默认类型
        const contentType = getContentType(message);

        // 准备API请求参数
        const requestMessages = [
          {
            role: systemPrompt.role,
            content: systemPrompt.content + `\n\n当前问题内容类型: ${contentType}`
          },
          ...messages.value.map(msg => ({ role: msg.role, content: msg.content }))
        ];

        // 不向AI提供资源信息，完全由我们自己控制资源展示

        // 调用DeepSeek API
        const response = await axios.post(API_URL, {
          model: MODEL,
          messages: requestMessages
        }, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_KEY}`
          }
        });

        // 处理API响应
        if (response.data && response.data.choices && response.data.choices[0]) {
          aiResponse = response.data.choices[0].message.content;
          
          // 完全由我们自己控制资源展示，确保只展示真实存在的资源
          if (hasAnyResources && isResourceQuestion) {
            aiResponse += '\n\n---\n\n## 📚 推荐学习资源\n';
            
            if (internalResources.length > 0) {
              aiResponse += '\n### 站内学习资源\n';
              internalResources.slice(0, 6).forEach(resource => {
                const resourceUrl = buildResourceDetailUrl(resource);
                aiResponse += `- **[${resource.title}](${resourceUrl})**\n`;
                if (resource.description) {
                  aiResponse += `  ${resource.description}\n`;
                }
                if (resource.target_audience_display) {
                  aiResponse += `  适用：${resource.target_audience_display}\n`;
                }
                aiResponse += '\n';
              });
              if (internalResources.length > 6) {
                aiResponse += `\n...还有 ${internalResources.length - 6} 个站内资源，可前往资源中心查看更多\n`;
              }
            }

            if (externalResources.length > 0) {
              aiResponse += '\n### 外部参考资源\n';
              externalResources.slice(0, 4).forEach(resource => {
                const externalUrl = resource.external_url || buildResourceDetailUrl(resource);
                aiResponse += `- [${resource.title}](${externalUrl})\n`;
              });
              if (externalResources.length > 4) {
                aiResponse += `\n...还有 ${externalResources.length - 4} 个外部资源\n`;
              }
            }
          } else if (!hasAnyResources && isResourceQuestion) {
            aiResponse += '\n\n---\n\n> 💡 提示：当前平台暂未收录该方向的学习资源，我们会尽快补充。';
          }
          
          messages.value.push({ role: 'assistant', content: aiResponse });
          saveChatHistory();
        } else {
          messages.value.push({ 
            role: 'assistant', 
            content: '抱歉，我暂时无法提供回答。请稍后再试或尝试其他问题。' 
          });
          saveChatHistory();
        }
      } catch (error) {
        console.error('API调用失败:', error);
        messages.value.push({ 
            role: 'assistant', 
            content: '抱歉，连接AI服务失败。请检查网络连接或稍后再试。' 
          });
          // 保存对话历史
          saveChatHistory();
      } finally {
        loading.value = false;
        // 滚动到底部
        await nextTick();
        scrollToBottom();
      }
    };

    const normalizeSiteResources = (data) => {
      const list = Array.isArray(data)
        ? data
        : (Array.isArray(data?.results) ? data.results : []);
      return list
        .filter(resource => resource && resource.id)
        .map(resource => {
          const detailUrl = buildResourceDetailUrl(resource);
          return {
            ...resource,
            detail_url: detailUrl,
            url: detailUrl
          };
        });
    };

    const buildResourceDetailUrl = (resource) => {
      if (resource?.detail_url && !resource.detail_url.startsWith('http')) {
        return resource.detail_url;
      }
      if (resource?.detail_url) {
        return resource.detail_url;
      }
      if (resource?.id) return `/resources/${resource.id}`;
      if (resource?.url?.startsWith('/resources/')) return resource.url;
      if (resource?.url?.startsWith('http')) return resource.url;
      return '/';
    };

    const mergeUniqueResources = (primary = [], secondary = []) => {
      const map = new Map();
      [...primary, ...secondary].forEach(resource => {
        if (resource && resource.id && !map.has(resource.id)) {
          map.set(resource.id, resource);
        }
      });
      return Array.from(map.values());
    };

    const buildKeywordList = (keywords) => {
      if (!keywords) return [];
      return keywords
        .toLowerCase()
        .match(/[\u4e00-\u9fa5]+|[a-z0-9]+/g) || [];
    };

    const fetchFallbackResources = async (keywords) => {
      try {
        const allResources = await resourceService.getAllResources();
        const normalized = normalizeSiteResources(allResources);
        if (!keywords) {
          return normalized.slice(0, 5);
        }

        const keywordList = buildKeywordList(keywords);
        const filtered = normalized.filter(resource => {
          const haystack = `${resource.title || ''} ${resource.description || ''}`.toLowerCase();
          return keywordList.some(keyword => haystack.includes(keyword));
        });

        if (filtered.length > 0) {
          return filtered.slice(0, 5);
        }
        return normalized.slice(0, 5);
      } catch (error) {
        console.error('兜底获取站内资源失败:', error);
        return [];
      }
    };

    const fetchResourcesFromLearningPaths = async (keywords) => {
      try {
        const keywordList = buildKeywordList(keywords);
        const categoryId = findCategoryIdByKeywords(keywordList);
        if (!categoryId) {
          return [];
        }

        const learningPath = await resourceService.getLearningPathByCategory(categoryId);
        if (!learningPath || !Array.isArray(learningPath.stages)) {
          return [];
        }

        const resources = [];
        learningPath.stages.forEach(stage => {
          stage?.recommended_resources?.forEach(resource => {
            resources.push({
              ...resource,
              is_external: false
            });
          });
        });

        const normalized = normalizeSiteResources(resources);
        return normalized.slice(0, 8);
      } catch (error) {
        console.error('从学习路径获取资源失败:', error);
        return [];
      }
    };

    const findCategoryIdByKeywords = (keywordList) => {
      if (!Array.isArray(keywordList) || keywordList.length === 0) return null;
      
      for (const category of contentCategories.value) {
        if (!category.categoryId || !category.keywords) continue;
        
        const matchScore = calculateMatchScore(keywordList, category.keywords);
        if (matchScore > 0) {
          console.log(`找到匹配分类: ${category.type} (ID: ${category.categoryId}), 匹配分数: ${matchScore}`);
          return category.categoryId;
        }
      }
      return null;
    };

    const calculateMatchScore = (inputKeywords, categoryKeywords) => {
      let score = 0;
      inputKeywords.forEach(input => {
        if (!input) return;
        categoryKeywords.forEach(categoryKeyword => {
          if (!categoryKeyword) return;
          if (input === categoryKeyword) {
            score += 10;
          } else if (input.includes(categoryKeyword) || categoryKeyword.includes(input)) {
            score += 5;
          }
        });
      });
      return score;
    };

    // 从问题中提取关键词（通用方法，支持各种学习内容）
    const extractKeywords = (question) => {
      // 移除常见的提问词和标点符号
      let keywords = question.toLowerCase()
        .replace(/[，。？！.,?!]/g, ' ') 
        .replace(/[\s]+/g, ' ') 
        .replace(/^[\s\S]*?[关于对针对]\s*/, '')
        .replace(/的[问题知识内容了解掌握学习]/g, ' ') 
        .replace(/[请请问能否能否够能不能]\s*/g, '')
        .replace(/推荐[一些几个]?[学习资源教程资料]?/g, '')
        .trim();
      
      // 分割句子为单词
      const words = keywords.split(' ').filter(word => word.length > 1);
      
      // 移除通用停用词
      const stopWords = ['是', '的', '了', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', 'about', 'the', 'a', 'an', 'and', 'or', 'but', 'if', 'because', 'for', 'of', 'to', 'with', 'on', 'in', 'by', 'at', 'from', 'is', 'are', 'was', 'were'];
      const filteredWords = words.filter(word => !stopWords.includes(word));
      
      // 返回前5个最可能的关键词（足够搜索使用）
      return filteredWords.slice(0, 5).join(' ');
    };

    // 跳转到社区提问
    const askInCommunity = (questionContext) => {
      // 将当前AI对话内容作为参考，跳转到社区提问页面
      const context = `我之前咨询过AI助手关于:\n\n${questionContext}\n\n但仍有疑问，希望得到更多帮助。`;
      router.push({
        path: '/community/ask',
        query: { context: encodeURIComponent(context) }
      });
    };
    
    // 初始化分类数据
    const loadCategories = async () => {
      try {
        // 首先获取所有分类（包括子分类）
        const allCategories = await getAllTechnologies();
        // 也获取一级分类作为补充
        const parentCategories = await getCategories();
        
        // 合并所有分类
        const categories = [...allCategories, ...parentCategories];
        
        // 转换分类数据为适合关键词匹配的格式
        contentCategories.value = categories.map(category => ({
          type: category.name.toLowerCase(),
          categoryId: category.id,
          keywords: [
            category.name.toLowerCase(),
            ...(category.description
              ? (category.description.toLowerCase().match(/[\u4e00-\u9fa5]+|[a-z0-9]+/g) || [])
              : [])
          ]
        }));
        // 添加一些通用的内容类型关键词
        const additionalTypes = [
          { type: 'language', keywords: ['英语', '日语', '语言', 'english', 'language', '外语', '学习语言'] },
          { type: 'math', keywords: ['数学', '微积分', '代数', '几何', 'mathematics', 'calculus'] },
          { type: 'science', keywords: ['科学', '物理', '化学', '生物', 'physics', 'chemistry'] },
          { type: 'art', keywords: ['艺术', '设计', '音乐', '绘画', 'art', 'design'] },
          { type: 'business', keywords: ['商业', '营销', '管理', '经济', 'business', 'marketing'] }
        ];
        
        // 合并并去重
        additionalTypes.forEach(addType => {
          const existing = contentCategories.value.find(c => c.type === addType.type);
          if (existing) {
            // 合并关键词并去重
            existing.keywords = [...new Set([...existing.keywords, ...addType.keywords])];
          } else {
            contentCategories.value.push(addType);
          }
        });
        
        console.log('加载完成的分类数据:', contentCategories.value);
        categoriesLoaded.value = true;
      } catch (error) {
        console.error('加载分类数据失败:', error);
        // 如果加载失败，使用默认类型
        contentCategories.value = [
          { type: 'programming', keywords: ['编程', 'code', 'javascript', 'python', 'java', 'coding'] },
          { type: 'general', keywords: [] }
        ];
        categoriesLoaded.value = true;
      }
    };
    
    // 获取学习内容类型（基于动态加载的分类数据）
    const getContentType = (question) => {
      const lowerQuestion = question.toLowerCase();
      
      // 查找匹配的内容类型
      for (const category of contentCategories.value) {
        if (category.keywords && category.keywords.some(keyword => lowerQuestion.includes(keyword))) {
          return category.type;
        }
      }
      
      return 'general'; // 默认类型
    };



    // 格式化消息内容（支持Markdown）
    const formatMessage = (content) => {
      if (!content) return '';
      
      // 简单的Markdown渲染
      let formatted = content
        // 标题处理
        .replace(/^####\s+(.+)$/gm, '<h4>$1</h4>')
        .replace(/^###\s+(.+)$/gm, '<h3>$1</h3>')
        .replace(/^##\s+(.+)$/gm, '<h2>$1</h2>')
        .replace(/^#\s+(.+)$/gm, '<h1>$1</h1>')
        // 链接处理
        // 先处理站内资源链接
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
          // 判断是否是站内链接
          if (url.includes('/resources/') || url.includes(window.location.origin)) {
            return `<a href="#" onclick="event.preventDefault(); window.handleInternalLinkClick && window.handleInternalLinkClick('${url}')">${text}</a>`;
          }
          // 外部链接
          return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
        })
        // 代码块
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        // 行内代码
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // 粗体
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        // 斜体
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        // 换行
        .replace(/\n/g, '<br>')
        // 移除标题后的多余换行
        .replace(/<\/h([1-4])><br>/g, '</h$1>');
      
      return formatted;
    };

    // 处理站内链接点击
    const handleInternalLinkClick = (url) => {
      if (!url) return;
      
      // 提取资源ID
      const resourceIdMatch = url.match(/\/resources\/(\d+)/);
      if (resourceIdMatch && resourceIdMatch[1]) {
        const resourceId = resourceIdMatch[1];
        router.push(`/resources/${resourceId}`);
        return;
      }
      
      // 如果无法提取不到资源ID，尝试其他方式
      if (url.startsWith('/')) {
        router.push(url);
      } else {
        window.open(url, '_blank');
      }
    };

    // 将处理函数挂载到window对象，供HTML事件可以调用
    onMounted(async () => {
      window.handleInternalLinkClick = handleInternalLinkClick;
      // 加载对话历史
      loadChatHistory();
      adjustTextareaHeight();
      // 加载分类数据
      await loadCategories();
      // 如果有历史消息，滚动到底部
      if (messages.value.length > 0) {
        await nextTick();
        scrollToBottom();
      }
    });

    // 滚动到底部
    const scrollToBottom = () => {
      if (chatHistory.value) {
        chatHistory.value.scrollTop = chatHistory.value.scrollHeight;
      }
    };

    // 调整textarea高度
    const adjustTextareaHeight = (event) => {
      if (textareaRef.value) {
        textareaRef.value.style.height = 'auto';
        textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 200) + 'px'; // 限制最大高度
      } else if (event && event.target) {
        const textarea = event.target;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'; // 限制最大高度
      }
    };



    return {
        messages,
        inputMessage,
        loading,
        chatHistory,
        textareaRef,
        sendMessage,
        askInCommunity,
        formatMessage,
        adjustTextareaHeight,
        extractKeywords,
        getContentType,
        clearChatHistory
      };
  }
};
</script>

<style scoped>
.ai-assistant {
  padding: 0;
  min-height: calc(100vh - 120px);
  background: radial-gradient(circle at top, #e0edff 0%, #f4f7fb 60%, #f8fafc 100%);
}

.container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 0.8rem 1.5rem;
}

.page-header {
  text-align: center;
  margin-bottom: 1rem;
}

.page-header h1 {
  font-size: 2.2rem;
  color: #0f172a;
  margin: 0;
  font-weight: 700;
}

.page-header p {
  font-size: 0.95rem;
  color: #475569;
  margin: 0;
}

.assistant-layout {
  display: grid;
  grid-template-columns: minmax(0, 3.5fr) minmax(220px, 1fr);
  gap: 1.5rem;
  align-items: flex-start;
}

.chat-panel {
  min-width: 0;
}

.assistant-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 18px;
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.08);
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.sidebar-card {
  background: white;
  border-radius: 14px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
  padding: 1rem 1.1rem;
  border: 1px solid rgba(226, 232, 240, 0.75);
  max-height: 420px;
  overflow-y: auto;
}

.sidebar-card-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.6rem;
}

.sidebar-card-header h3 {
  font-size: 0.95rem;
  color: #0f172a;
  font-weight: 600;
  margin: 0;
}

.sidebar-card-header i {
  color: #2563eb;
}

.sidebar-card-header p {
  margin: 0;
  font-size: 0.8rem;
  color: #64748b;
}

.guide-card .guide-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.guide-list li {
  background: #f8fafc;
  border-radius: 10px;
  padding: 0.6rem 0.7rem;
  border: 1px solid rgba(226, 232, 240, 0.75);
}

.guide-list strong {
  display: block;
  color: #0f172a;
  font-weight: 600;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

.guide-list span {
  font-size: 0.75rem;
  color: #64748b;
}

.faq-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.faq-question {
  font-weight: 600;
  margin: 0;
  color: #0f172a;
  font-size: 0.9rem;
}

.faq-answer {
  margin: 0.2rem 0 0;
  color: #64748b;
  font-size: 0.78rem;
}

.chat-container {
  overflow: hidden;
  width: 100%;
}

.chat-history {
  height: 420px;
  overflow-y: auto;
  padding: 0.5rem;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.clear-history-container {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.clear-history-btn {
  padding: 0.5rem 1rem;
  background-color: #fef2f2;
  color: #ef4444;
  border: 1px solid #fecaca;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.clear-history-btn:hover {
  background-color: #fee2e2;
  border-color: #fca5a5;
}

.chat-history::-webkit-scrollbar {
  width: 6px;
}

.chat-history::-webkit-scrollbar-track {
  background: transparent;
}

.chat-history::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}

.welcome-message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.user-avatar,
.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.user-avatar {
  background-color: #3b82f6;
  color: white;
  margin-left: 12px;
  margin-right: 0;
}

.ai-avatar {
  background-color: #10b981;
  color: white;
  margin-right: 12px;
  margin-left: 0;
}

.message-content {
  max-width: min(80%, 820px);
  width: 100%;
  word-wrap: break-word;
}

/* 用户消息样式 - 蓝色背景 */
.message.user {
  flex-direction: row-reverse;
}

.message.user .message-content {
  text-align: right;
  margin-right: 0;
}

.message-text {
  padding: 1rem;
  border-radius: 12px;
  line-height: 1.45;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: anywhere;
  font-size: 0.9rem;
  max-width: 100%;
  display: inline-block;
}

/* 用户消息样式 - 蓝色背景气泡 */
.message.user .message-text {
  background-color: #3b82f6;
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* AI助手消息样式 - 浅绿色背景气泡 */
.message.assistant .message-text {
  background-color: #f0fdf4;
  color: #1f2937;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* 资源卡片样式 */
.message-text h3, .message-text h4 {
  margin-top: 0.9rem;
  margin-bottom: 0.35rem;
  color: #1f2937;
  font-size: 1rem;
}

.message.user .message-text h3, 
.message.user .message-text h4 {
  color: white;
}

.message-text a {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.message-text a:hover {
  text-decoration: underline;
}

.message.user .message-text a {
  color: #bfdbfe;
}

/* 欢迎消息特殊样式 */
.welcome-message .message-content {
  background-color: #f0fdf4;
  color: #1f2937;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  padding: 1.5rem;
  border-radius: 12px;
}

.message-text pre {
  background-color: #1f2937;
  color: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1rem 0;
  font-size: 0.8rem;
}

.message-text code {
  background-color: #e5e7eb;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
}

.message.user .message-text code {
  background-color: rgba(255, 255, 255, 0.2);
}

.message-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  justify-content: flex-start;
}

.action-btn {
  padding: 0.3rem 0.8rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: #f3f4f6;
}

.community-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}



.loading-message .message-content {
  min-height: 40px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #6b7280;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input-container {
  padding: 0.5rem 0.7rem;
  border-top: 1px solid #e5e7eb;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.5), rgba(255, 255, 255, 0.9));
}

.chat-input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 0.6rem;
}

.input-wrapper {
  flex: 1;
}

.button-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.3rem;
}

.chat-input {
  width: 100%;
  padding: 0.45rem 0.65rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.85rem;
  resize: vertical;
  min-height: 28px;
  font-family: inherit;
}

.chat-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-tips {
  font-size: 0.72rem;
  color: #6b7280;
}

.char-count {
  color: #9ca3af;
}

.send-btn {
  padding: 0.5rem 1.1rem;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: transform 0.2s, box-shadow 0.2s;
  height: fit-content;
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.3);
  margin-bottom: 5px;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 14px 24px rgba(37, 99, 235, 0.4);
}

.send-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .assistant-layout {
    grid-template-columns: 1fr;
  }

  .assistant-sidebar {
    order: -1;
  }

  .page-header h1 {
    font-size: 2rem;
  }
  
  .chat-history {
    height: 360px;
    padding: 1rem;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .chat-input-container {
    padding: 0.7rem;
    flex-direction: column;
  }
  
  .chat-input-wrapper {
    flex-direction: column;
    align-items: stretch;
    gap: 0.4rem;
  }

  .button-wrapper {
    align-items: flex-start;
  }

  .input-tips {
    width: 100%;
    text-align: right;
  }

  .send-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>