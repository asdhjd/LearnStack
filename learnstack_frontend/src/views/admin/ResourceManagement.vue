<template>
  <div class="admin-dashboard">
    <AdminSidebar />
    
    <div class="admin-content">
      <header class="admin-header">
        <h1>资源管理</h1>
      </header>
      
      <div class="content-section">
        <!-- 搜索和添加按钮 -->
        <div class="search-section">
          <div class="search-input-group">
            <div class="search-container">
              <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="搜索资源标题、描述或分类..."
                class="search-input"
                @keyup.enter="handleSearch"
              />
              <button class="search-btn" @click="handleSearch">
                <i class="fas fa-search"></i> 搜索
              </button>
            </div>
            <button class="add-btn" @click="showAddResourceModal = true">
              <i class="icon-plus"></i> 添加资源
            </button>
          </div>
        </div>
        
        <!-- 资源列表 - 按分类折叠面板 -->
        <div class="resource-list-section">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading">
            加载中...
          </div>
          
          <!-- 无数据提示 -->
          <div v-else-if="filteredCategories.length === 0 && !loading" class="no-data">
            {{ searchQuery ? '没有找到匹配的资源' : '暂无资源数据' }}
          </div>
          
          <!-- 按分类分组的折叠面板 -->
          <div v-else class="category-accordion">
            <div 
              v-for="category in filteredCategories" 
              :key="category.id"
              class="accordion-item"
            >
              <div 
                class="accordion-header"
                @click="toggleCategory(category.id)"
              >
                <span class="accordion-icon">{{ isExpanded(category.id) ? '−' : '+' }}</span>
                <h3 class="category-title">{{ category.name }}</h3>
                <span class="resource-count">({{ getCategoryResources(category.id).length }})</span>
              </div>
              
              <div 
                v-if="isExpanded(category.id)"
                class="accordion-content"
              >
                <table class="resource-table">
                  <thead>
                    <tr>
                      <th>标题</th>
                      <th>类型</th>
                      <th>目标受众</th>
                      <th>评分</th>
                      <th>创建时间</th>
                      <th>所属分类</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="resource in getCategoryResources(category.id)" :key="`${category.id}-${resource.id}`">
                      <td class="title-cell">
                        <a :href="resource.url" target="_blank" class="resource-url">{{ resource.title }}</a>
                      </td>
                      <td>{{ getResourceTypeText(resource.resource_type) }}</td>
                      <td>{{ getTargetAudienceText(resource.target_audience) }}</td>
                      <td>{{ resource.rating }}</td>
                      <td>{{ formatDate(resource.created_at) }}</td>
                      <td>
                        <span 
                          v-for="(cat, index) in resource.categories_display || resource.categories" 
                          :key="cat.id"
                          class="category-tag"
                        >
                          {{ cat.name }}<span v-if="index < (resource.categories_display || resource.categories).length - 1">, </span>
                        </span>
                      </td>
                      <td class="action-buttons">
                        <button class="edit-btn" @click="editResource(resource)">
                          <i class="fas fa-edit"></i> 编辑
                        </button>
                        <button class="delete-btn" @click="deleteResource(resource.id)">
                          <i class="fas fa-trash"></i> 删除
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                
                <div v-if="getCategoryResources(category.id).length === 0" class="empty-category">
                  该分类下暂无资源
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑资源模态框 -->
    <div v-if="showAddResourceModal || showEditResourceModal" class="modal-overlay">
      <div class="modal-content large-modal">
        <div class="modal-header">
          <h2>{{ showEditResourceModal ? '编辑资源' : '添加资源' }}</h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        
        <div class="modal-body">
          <!-- 标签页导航 -->
          <div class="form-tabs">
            <button 
              type="button"
              :class="['tab-btn', { active: activeTab === 'basic' }]"
              @click="activeTab = 'basic'"
            >
              <i class="fas fa-info-circle"></i> 基本信息
            </button>
            <button 
              type="button"
              :class="['tab-btn', { active: activeTab === 'content' }]"
              @click="activeTab = 'content'"
            >
              <i class="fas fa-file-alt"></i> 内容信息
            </button>
            <button 
              type="button"
              :class="['tab-btn', { active: activeTab === 'settings' }]"
              @click="activeTab = 'settings'"
            >
              <i class="fas fa-cog"></i> 分类与设置
            </button>
          </div>

          <form @submit.prevent="handleSubmit">
            <!-- 基本信息标签页 -->
            <div v-show="activeTab === 'basic'" class="tab-content">
            <div class="form-group">
              <label for="title">标题 *</label>
              <input 
                id="title" 
                v-model="formData.title" 
                type="text" 
                required 
                placeholder="请输入资源标题"
              />
            </div>
            
            <div class="form-group">
              <label for="description">描述 *</label>
              <textarea 
                id="description" 
                v-model="formData.description" 
                required 
                placeholder="请输入资源描述"
                rows="4"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="url">资源链接 <span v-if="formData.content_source === 'embedded'" class="required">*</span></label>
              <input 
                id="url" 
                v-model="formData.url" 
                type="url" 
                :required="formData.content_source === 'embedded'" 
                placeholder="请输入资源URL"
              />
            </div>
            
            <div class="form-group">
              <div class="label-row">
                <label for="hero_cover">封面图片 *</label>
                <span class="hint-text">学习详情页顶部 Banner</span>
              </div>
              <input 
                id="hero_cover" 
                v-model="formData.hero_cover" 
                type="url" 
                required 
                placeholder="https://example.com/cover.jpg"
              />
              <p class="form-hint">用于学习资源详情页的封面展示，建议使用 16:9 图片。</p>
            </div>
            
            <div class="form-group">
              <label for="resource_type">资源类型 *</label>
              <select id="resource_type" v-model="formData.resource_type" required @change="onResourceTypeChange">
                <option value="">请选择资源类型</option>
                <option value="book">书籍</option>
                <option value="course">课程</option>
                <option value="article">文章</option>
                <option value="project">项目</option>
                <option value="tool">工具</option>
                <option value="document">文档</option>
              </select>
            </div>
            
            <div 
              v-if="formData.resource_type"
              class="resource-type-hint"
            >
              <div class="hint-title">
                <i :class="resourceTypeMeta.icon"></i>
                <div>
                  <strong>{{ resourceTypeMeta.title }}</strong>
                  <p>{{ resourceTypeMeta.description }}</p>
                </div>
              </div>
              <ul>
                <li v-for="tip in resourceTypeMeta.tips" :key="tip">{{ tip }}</li>
              </ul>
            </div>
            </div>

            <!-- 内容信息标签页 -->
            <div v-show="activeTab === 'content'" class="tab-content">
              <div class="section-title">
                <h3>内容配置</h3>
                <p class="section-desc">根据资源类型和内容来源配置相应的内容</p>
              </div>

              <div class="form-group">
                <label for="content_source">内容来源 *</label>
                <select id="content_source" v-model="formData.content_source" required>
                  <option value="original">站内原创/上传</option>
                  <option value="embedded">外部导入</option>
                </select>
                <p class="form-hint">
                  <span v-if="formData.resource_type === 'document'">站内原创/上传：内容由您原创或上传到本站；外部导入：内容来自外部平台</span>
                  <span v-else-if="formData.resource_type === 'course'">站内原创/上传：内容由您原创或上传到本站；外部导入：视频来自外部平台（如 Bilibili、YouTube）</span>
                  <span v-else-if="formData.resource_type === 'tool'">站内原创/上传：内容由您原创或上传到本站；外部导入：工具来自外部平台或外链</span>
                  <span v-else-if="formData.resource_type === 'article'">站内原创/上传：内容由您原创或上传到本站；外部导入：文章来自外部平台或链接</span>
                  <span v-else-if="formData.resource_type === 'project'">站内原创/上传：内容由您原创或上传到本站；外部导入：项目来自外部平台或代码仓库</span>
                  <span v-else-if="formData.resource_type === 'book'">站内原创/上传：内容由您原创或上传到本站；外部导入：书籍来自外部平台或下载链接</span>
                  <span v-else>站内原创/上传：内容由您原创或上传到本站；外部导入：内容来自外部平台</span>
                </p>
              </div>

              <!-- 站内原创/上传的内容配置 -->
              <template v-if="formData.content_source === 'original'">
                <!-- 视频、书籍、工具、项目资源正文内容为可选 -->
                <template v-if="formData.resource_type === 'course' || formData.resource_type === 'book' || formData.resource_type === 'tool' || formData.resource_type === 'project'">
                  <div class="form-group">
                    <label for="body_format">正文格式（可选）</label>
                    <select id="body_format" v-model="formData.content.body_format">
                      <option value="">不填写正文</option>
                      <option value="markdown">Markdown</option>
                      <option value="html">HTML</option>
                      <option value="plaintext">纯文本</option>
                    </select>
                    <p class="form-hint">
                      <span v-if="formData.resource_type === 'course'">视频资源可以不填写正文，如需添加课程介绍或学习建议，可选择格式并填写</span>
                      <span v-else-if="formData.resource_type === 'book'">书籍资源可以不填写正文，如需添加书籍摘要或章节示例，可选择格式并填写</span>
                      <span v-else-if="formData.resource_type === 'tool'">工具资源可以不填写正文，如需添加工具介绍或使用说明，可选择格式并填写</span>
                      <span v-else-if="formData.resource_type === 'project'">项目资源可以不填写正文，如需添加项目说明或步骤，可选择格式并填写</span>
                    </p>
                  </div>

                  <div class="form-group" v-if="formData.content.body_format">
                    <label for="body_content">正文内容（可选）</label>
                    <textarea
                      id="body_content"
                      :value="formData.content.body_format === 'html' ? formData.content.body_html : formData.content.body_markdown"
                      @input="handleBodyContentInput"
                      :rows="12"
                      :placeholder="getBodyPlaceholder()"
                      class="content-textarea"
                    ></textarea>
                    <p class="form-hint">{{ getBodyHint() }}</p>
                  </div>
                </template>
                
                <!-- 文章和文档资源必须填写正文内容 -->
                <template v-else>
                  <div class="form-group">
                    <label for="body_format">正文格式 *</label>
                    <select id="body_format" v-model="formData.content.body_format" required>
                      <option value="">请选择格式</option>
                      <option value="markdown">Markdown</option>
                      <option value="html">HTML</option>
                      <option value="plaintext">纯文本</option>
                    </select>
                    <p class="form-hint">系统会智能识别内容格式，即使选择 HTML 格式，输入 Markdown 或纯文本也能正常显示</p>
                  </div>

                  <div class="form-group" v-if="formData.content.body_format">
                    <label for="body_content">正文内容 *</label>
                    <textarea
                      id="body_content"
                      :value="formData.content.body_format === 'html' ? formData.content.body_html : formData.content.body_markdown"
                      @input="handleBodyContentInput"
                      :rows="formData.content.body_format === 'html' ? 12 : 12"
                      :placeholder="getBodyPlaceholder()"
                      required
                      class="content-textarea"
                    ></textarea>
                    <p class="form-hint">{{ getBodyHint() }}</p>
                  </div>
                </template>

                <!-- 书籍文件上传 -->
                <div class="form-group" v-if="formData.resource_type === 'book'">
                  <label for="book_file">书籍文件</label>
                  <input 
                    type="file" 
                    id="book_file" 
                    ref="bookFileInput"
                    @change="handleBookFileChange"
                    accept=".pdf,.epub,.mobi,.doc,.docx,.zip,.rar,.7z,.tar,.gz,.tar.gz"
                  />
                  <p class="form-hint">
                    支持格式：PDF、EPUB、MOBI、DOC、DOCX、ZIP、RAR、7Z、TAR、GZ、TAR.GZ<br>
                    文件大小限制：100MB
                    <span v-if="bookFileName" style="display: block; margin-top: 5px; color: #4f46e5; font-weight: 500;">已选择：{{ bookFileName }}</span>
                  </p>
                </div>
              </template>

              <!-- 外部导入的内容配置 -->
              <template v-if="formData.content_source === 'embedded'">
                <div class="form-row">
                  <div class="form-group">
                    <label for="embed_provider">嵌入提供方</label>
                    <input
                      id="embed_provider"
                      v-model="formData.content.embed_provider"
                      type="text"
                      placeholder="如：Bilibili、YouTube"
                    />
                  </div>
                  <div class="form-group">
                    <label for="embed_url">嵌入地址</label>
                    <input
                      id="embed_url"
                      v-model="formData.content.embed_url"
                      type="url"
                      placeholder="https://example.com/embed"
                    />
                  </div>
                </div>
                
                <!-- 外部导入时可选填写正文内容 -->
                <div class="form-group">
                  <label for="body_format_embedded">正文格式（可选）</label>
                  <select id="body_format_embedded" v-model="formData.content.body_format">
                    <option value="">不填写正文</option>
                    <option value="markdown">Markdown</option>
                    <option value="html">HTML</option>
                    <option value="plaintext">纯文本</option>
                  </select>
                  <p class="form-hint">外部导入的资源可以选择性添加正文内容，如资源介绍、使用说明等</p>
                </div>

                <div class="form-group" v-if="formData.content.body_format">
                  <label for="body_content_embedded">正文内容（可选）</label>
                  <textarea
                    id="body_content_embedded"
                    :value="getEmbeddedBodyContent()"
                    @input="handleEmbeddedBodyContentInput"
                    :rows="12"
                    :placeholder="getBodyPlaceholder()"
                    class="content-textarea"
                  ></textarea>
                  <p class="form-hint">{{ getBodyHint() }}</p>
                </div>
              </template>

              <!-- 可选内容配置（折叠面板） -->
              <div class="collapsible-section">
                <button 
                  type="button"
                  class="collapsible-header"
                  @click="showAdvancedContent = !showAdvancedContent"
                >
                  <i :class="['fas', showAdvancedContent ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
                  <span>高级内容配置（可选）</span>
                </button>
                <div v-show="showAdvancedContent" class="collapsible-content">
                  <div class="form-row">
                    <div class="form-group">
                      <label for="sections_json">章节/目录 (JSON)</label>
                      <textarea
                        id="sections_json"
                        v-model="sectionsJson"
                        rows="5"
                        placeholder='例如: [{"title":"第一章","summary":"概要"}]'
                      ></textarea>
                      <p class="form-hint">可选，JSON 数组，支持 title/summary 等字段。</p>
                    </div>
                    <div class="form-group">
                      <label for="document_toc_json">文档目录 (JSON)</label>
                      <textarea
                        id="document_toc_json"
                        v-model="documentTocJson"
                        rows="5"
                        placeholder='例如: [{"text":"章节 1","href":"#id-1"}]'
                      ></textarea>
                      <p class="form-hint">可选，JSON 数组，用于构建 TOC。</p>
                    </div>
                  </div>

                  <div class="form-row">
                    <div class="form-group">
                      <label for="document_html">文档 HTML</label>
                      <textarea
                        id="document_html"
                        v-model="formData.content.document_html"
                        rows="4"
                        placeholder="用于展示的 HTML 片段（可选）"
                      ></textarea>
                    </div>
                    <div class="form-group">
                      <label for="download_url">下载链接</label>
                      <input
                        id="download_url"
                        v-model="formData.content.download_url"
                        type="url"
                        placeholder="https://example.com/download"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分类与设置标签页 -->
            <div v-show="activeTab === 'settings'" class="tab-content">
              <div class="section-title">
                <h3>分类设置</h3>
                <p class="section-desc">为资源选择一个或多个分类</p>
              </div>

              <div class="form-group">
                <label>选择分类 <span class="required">*</span></label>
              <!-- 搜索+多选优化版本 -->
              <div class="category-selector">
                <!-- 搜索框 -->
                <div class="category-search-wrapper">
                  <input 
                    type="text" 
                    v-model="categorySearchQuery" 
                    placeholder="搜索分类..."
                    class="category-search"
                  />
                </div>
                
                <!-- 分类列表 (带搜索过滤) -->
                <div class="category-list">
                  <label 
                    v-for="category in filteredCategoryOptions" 
                    :key="category.id"
                    class="category-checkbox"
                  >
                    <input 
                      type="checkbox" 
                      :value="category.id" 
                      v-model="formData.categories"
                    />
                    {{ category.name }}
                  </label>
                  
                  <div v-if="filteredCategoryOptions.length === 0" class="no-results">
                    没有找到匹配的分类
                  </div>
                </div>
                
                <!-- 已选分类提示 -->
                <div class="selected-count">
                  已选择 {{ formData.categories.length }} 个分类
                </div>
              </div>
              <div class="error-message" v-if="showCategoryError">请至少选择一个分类</div>
            </div>

            <div class="section-title" style="margin-top: 30px;">
              <h3>其他设置</h3>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="target_audience">适用人群 *</label>
                <select id="target_audience" v-model="formData.target_audience" required>
                  <option value="">请选择适用人群</option>
                  <option value="beginner">入门阶段</option>
                  <option value="intermediate">中级阶段</option>
                  <option value="advanced">高级阶段</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="rating">评分 *</label>
                <input 
                  id="rating" 
                  v-model.number="formData.rating" 
                  type="number" 
                  required 
                  min="1" 
                  max="5"
                  placeholder="请输入评分 (1-5)"
                />
              </div>
            </div>
            </div>
            
            <!-- 表单操作按钮 -->
            <div class="form-actions">
              <button type="button" class="cancel-btn" @click="closeModal">取消</button>
              <button type="submit" class="submit-btn" :disabled="submitting">
                {{ submitting ? '提交中...' : '确定' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    

    
    <!-- 消息提示 -->
    <div v-if="message" class="message-toast" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import AdminSidebar from '@/components/admin/AdminSidebar.vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import adminService from '@/services/adminService.js';

// 响应式数据：新增 timeoutId 替代 window.searchTimeout，避免全局污染
const timeoutId = ref(null);
const resources = ref([]);
const categories = ref([]);
const flatCategories = ref([]);
const searchQuery = ref('');
const searchQueryToApply = ref('');
const loading = ref(false);
const submitting = ref(false);
const deleting = ref(false);
const showAddResourceModal = ref(false);
const showEditResourceModal = ref(false);
const message = ref('');
const messageType = ref('');
const resourceToEditId = ref(null);
const expandedCategories = ref(new Set());
const showCategoryError = ref(false);
const categorySearchQuery = ref('');
const activeTab = ref('basic'); // 标签页状态：basic, content, settings
const showAdvancedContent = ref(false); // 高级内容配置折叠状态

// 组件挂载时加载数据
onMounted(() => {
  loadResources();
  loadCategories();
});

// 表单数据
const formData = ref({
  title: '',
  description: '',
  url: '',
  hero_cover: '',
  resource_type: '',
  target_audience: '',
  rating: 3,
  categories: [],
  content_source: 'original',
  content: {
    body_format: '',
    body_markdown: '',
    body_html: '',
    sections: [],
    document_html: '',
    document_toc: [],
    download_url: '',
    embed_provider: '',
    embed_url: ''
  }
});
const sectionsJson = ref('');
const documentTocJson = ref('');
const bookFile = ref(null);
const bookFileName = ref('');
const bookFileInput = ref(null);

// 加载资源列表
const loadResources = async () => {
  loading.value = true;
  try {
    const response = await adminService.getResources();
    resources.value = response.results || response;
  } catch {
    showMessage('加载资源列表失败', 'error');
  } finally {
    loading.value = false;
  }
};

// 加载分类列表：删除调试用 console.error
const flattenCategories = (items = [], parentId = null, accumulator = []) => {
  items.forEach(cat => {
    const cloned = { 
      ...cat, 
      parent: cat.parent ?? parentId,
      uniqueId: cat.id
    };
    accumulator.push(cloned);
    if (Array.isArray(cat.subcategories) && cat.subcategories.length > 0) {
      flattenCategories(cat.subcategories, cat.id, accumulator);
    }
  });
  return accumulator;
};

const loadCategories = async () => {
  try {
    const response = await adminService.getCategories();
    const data = response.results || response;
    categories.value = data;
    flatCategories.value = flattenCategories(data);
  } catch {
    // showMessage('加载分类失败', 'error');
  }
};

// 过滤分类选项（仅显示二级分类，带搜索功能）
// 获取正文输入框的占位符文本
const getBodyPlaceholder = () => {
  const format = formData.value.content.body_format
  if (format === 'markdown') {
    return '请输入 Markdown 格式的内容（支持标题、列表、代码块、链接等）'
  } else if (format === 'html') {
    return '请输入 HTML 格式的内容（可以直接粘贴从网页复制的 HTML，系统会智能识别）'
  } else if (format === 'plaintext') {
    return '请输入纯文本内容（系统会自动格式化，识别标题、列表、链接等）'
  }
  return '请先选择正文格式'
}

// 获取正文输入框的提示文本
const getBodyHint = () => {
  const format = formData.value.content.body_format
  if (format === 'markdown') {
    return '💡 提示：支持 Markdown 语法，如 # 标题、- 列表、`代码`、[链接](url) 等'
  } else if (format === 'html') {
    return '💡 提示：可以直接粘贴 HTML 代码，也可以输入 Markdown 或纯文本，系统会智能识别'
  } else if (format === 'plaintext') {
    return '💡 提示：系统会自动识别标题（# 开头）、列表（- 或数字. 开头）、链接等格式'
  }
  return '💡 提示：系统会智能识别内容格式（Markdown、HTML 或纯文本），自动转换显示'
}

// 获取外部导入时的正文内容（根据格式返回对应的字段）
const getEmbeddedBodyContent = () => {
  if (formData.value.content.body_format === 'html') {
    return formData.value.content.body_html || ''
  }
  return formData.value.content.body_markdown || ''
}

// 处理外部导入时的正文内容输入
const handleEmbeddedBodyContentInput = (event) => {
  const value = event.target.value
  if (formData.value.content.body_format === 'html') {
    formData.value.content.body_html = value
  } else {
    formData.value.content.body_markdown = value
  }
}

// 保存原始正文内容，用于恢复
const originalBodyContent = ref({
  markdown: '',
  html: '',
  format: ''
})

// 处理站内原创/上传时的正文内容输入
const handleBodyContentInput = (event) => {
  const value = event.target.value
  if (formData.value.content.body_format === 'html') {
    formData.value.content.body_html = value
    // 用户输入新内容时，如果之前有 markdown 内容且格式不匹配，清空 markdown
    // 但只在用户实际输入内容时才清空，避免误操作
    if (value && originalBodyContent.value.format === 'markdown' && originalBodyContent.value.format !== 'html') {
      // 用户正在输入 HTML 内容，如果原始格式是 markdown，不清空（保留原始值以防用户切换回去）
    }
  } else {
    formData.value.content.body_markdown = value
    // 用户输入新内容时，如果之前有 HTML 内容且格式不匹配，清空 HTML
    // 但只在用户实际输入内容时才清空，避免误操作
    if (value && originalBodyContent.value.format === 'html' && originalBodyContent.value.format !== 'markdown') {
      // 用户正在输入 Markdown 内容，如果原始格式是 HTML，不清空（保留原始值以防用户切换回去）
    }
  }
}

// 监听正文格式变化，保存原始值并在切换回原格式时恢复
watch(() => formData.value.content.body_format, (newFormat, oldFormat) => {
  if (newFormat !== oldFormat && oldFormat !== undefined) {
    // 保存切换前的原始值
    if (oldFormat && oldFormat !== '') {
      if (oldFormat === 'html') {
        originalBodyContent.value.html = formData.value.content.body_html || ''
        originalBodyContent.value.format = 'html'
      } else {
        originalBodyContent.value.markdown = formData.value.content.body_markdown || ''
        originalBodyContent.value.format = oldFormat
      }
    }
    
    // 切换格式时，如果目标格式的字段为空，尝试从原始值恢复
    if (newFormat === 'html') {
      if (!formData.value.content.body_html && originalBodyContent.value.html) {
        // 如果 HTML 字段为空，但原始值是 HTML，恢复原始值
        formData.value.content.body_html = originalBodyContent.value.html
      }
    } else if (newFormat === 'markdown' || newFormat === 'plaintext') {
      if (!formData.value.content.body_markdown && originalBodyContent.value.markdown) {
        // 如果 Markdown 字段为空，但原始值是 Markdown，恢复原始值
        formData.value.content.body_markdown = originalBodyContent.value.markdown
      }
    } else if (newFormat === '') {
      // 清空格式时，不清空内容字段，保留数据
    }
  }
})

const filteredCategoryOptions = computed(() => {
  const secondaryCategories = flatCategories.value.filter(category => 
    category.parent !== null && category.parent !== undefined
  );
  
  const seen = new Set();
  const uniqueSecondary = secondaryCategories.filter(category => {
    const key = `${category.uniqueId}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  
  if (!categorySearchQuery.value?.trim()) {
    return uniqueSecondary;
  }
  
  const query = categorySearchQuery.value.toLowerCase();
  return uniqueSecondary.filter(category => 
    category.name?.toLowerCase().includes(query)
  );
});

// 过滤包含匹配资源的分类
const filteredCategories = computed(() => {
  let result = categories.value.filter(category => 
    category.parent !== null && category.parent !== undefined
  );
  
  if (searchQueryToApply.value?.trim()) {
    const query = searchQueryToApply.value.toLowerCase();
    return result.filter(category => 
      category.name?.toLowerCase().includes(query) ||
      getCategoryResources(category.id).some(resource => 
        resource.title?.toLowerCase().includes(query) ||
        resource.description?.toLowerCase().includes(query) ||
        (resource.categories || []).some(cat => 
          typeof cat === 'object' && cat.name?.toLowerCase().includes(query)
        )
      )
    );
  }
  
  return result;
});

// 搜索处理：用 timeoutId 替代 window.searchTimeout，避免全局污染
const handleSearch = () => {
  searchQueryToApply.value = searchQuery.value;
  
  // 清除之前的定时器（使用响应式变量 timeoutId）
  clearTimeout(timeoutId.value);
  timeoutId.value = setTimeout(() => {
    if (searchQueryToApply.value) {
      filteredCategories.value.forEach(category => {
        if (getCategoryResources(category.id).length > 0) {
          toggleCategory(category.id, true);
        }
      });
    }
  }, 300);
};

// 显示消息提示
const showMessage = (msg, type = 'success') => {
  message.value = msg;
  messageType.value = type;
  setTimeout(() => {
    message.value = '';
  }, 3000);
};

// 切换分类展开状态
const toggleCategory = (categoryId, forceExpand = null) => {
  if (forceExpand === true) {
    expandedCategories.value.add(categoryId);
  } else if (forceExpand === false) {
    expandedCategories.value.delete(categoryId);
  } else {
    expandedCategories.value.has(categoryId)
      ? expandedCategories.value.delete(categoryId)
      : expandedCategories.value.add(categoryId);
  }
};

// 检查分类是否展开
const isExpanded = (categoryId) => {
  return expandedCategories.value.has(categoryId);
};

// 获取指定分类下的资源（带搜索过滤）
const getCategoryResources = (categoryId) => {
  let filteredResources = resources.value;
  
  if (searchQueryToApply.value?.trim()) {
    const query = searchQueryToApply.value.toLowerCase();
    filteredResources = resources.value.filter(resource => 
      resource.title?.toLowerCase().includes(query) ||
      resource.description?.toLowerCase().includes(query) ||
      ((resource.categories_display || resource.categories) || []).some(cat => 
        typeof cat === 'object' && cat.name?.toLowerCase().includes(query)
      )
    );
  }
  
  return filteredResources.filter(resource => {
    const resourceCategories = resource.categories_display || resource.categories;
    if (!Array.isArray(resourceCategories) || resourceCategories.length === 0) {
      return false;
    }
    
    return typeof resourceCategories[0] === 'number'
      ? resourceCategories.includes(categoryId)
      : resourceCategories.some(cat => cat.id === categoryId);
  });
};

// 清空表单
// 资源类型改变时的处理
const onResourceTypeChange = () => {
  // 所有资源类型都支持外部导入，不需要切换
  // 但需要重置内容相关字段，确保切换类型时数据清空
  formData.value.content = {
    body_format: '',
    body_markdown: '',
    body_html: '',
    sections: [],
    document_html: '',
    document_toc: [],
    download_url: '',
    embed_provider: '',
    embed_url: ''
  };
  sectionsJson.value = '';
  documentTocJson.value = '';
  bookFile.value = null;
  bookFileName.value = '';
  if (bookFileInput.value) {
    bookFileInput.value.value = '';
  }
}

const resetForm = () => {
  formData.value = {
    title: '',
    description: '',
    url: '',
    hero_cover: '',
    resource_type: '',
    target_audience: '',
    rating: 3,
    categories: [],
    content_source: 'original',
    content: {
      body_format: '',
      body_markdown: '',
      body_html: '',
      sections: [],
      document_html: '',
      document_toc: [],
      download_url: '',
      embed_provider: '',
      embed_url: ''
    }
  };
  resourceToEditId.value = null;
  showCategoryError.value = false;
  categorySearchQuery.value = '';
  sectionsJson.value = '';
  documentTocJson.value = '';
  bookFile.value = null;
  bookFileName.value = '';
  if (bookFileInput.value) {
    bookFileInput.value.value = '';
  }
  // 重置原始正文内容
  originalBodyContent.value = {
    markdown: '',
    html: '',
    format: ''
  }
};

// 表单验证
const validateForm = () => {
  showCategoryError.value = false;
  
  if (!formData.value.hero_cover?.trim()) {
    showMessage('请填写封面图片', 'warning');
    return false;
  }
  
  if (!formData.value.categories?.length) {
    showCategoryError.value = true;
    return false;
  }

  // 验证资源链接（外部导入时必须填写）
  if (formData.value.content_source === 'embedded') {
    if (!formData.value.url || !formData.value.url.trim()) {
      showMessage('外部导入的资源必须填写资源链接', 'warning');
      return false;
    }
    
    // 外部导入时如果选择了正文格式，则需要填写内容
    // 但如果格式字段为空字符串，则不验证（允许用户不填写正文）
    if (formData.value.content.body_format && formData.value.content.body_format.trim() !== '') {
      // 检查是否有内容（markdown 或 html）
      const hasMarkdown = formData.value.content.body_markdown?.trim();
      const hasHtml = formData.value.content.body_html?.trim();
      const hasContent = hasMarkdown || hasHtml;
      
      // 如果选择了格式但没有内容，允许通过验证（因为正文是可选的）
      // 只有在有内容时才验证格式匹配
      if (hasContent) {
        // 有内容，验证格式匹配
        if (formData.value.content.body_format === 'markdown' && !hasMarkdown) {
          showMessage('如果选择了 Markdown 格式，请填写正文内容', 'warning');
          return false;
        }
        if (formData.value.content.body_format === 'html' && !hasHtml) {
          showMessage('如果选择了 HTML 格式，请填写正文内容', 'warning');
          return false;
        }
      }
      // 如果没有内容，允许通过（因为正文是可选的）
    }
  }

  // 验证内容字段
  // 文章和文档资源必须填写正文内容
  const requiredBodyTypes = ['article', 'document'];
  if (formData.value.content_source === 'original' && requiredBodyTypes.includes(formData.value.resource_type)) {
    if (!formData.value.content.body_format) {
      showMessage('请选择正文格式', 'warning');
      return false;
    }
    if (formData.value.content.body_format === 'markdown' && !formData.value.content.body_markdown?.trim()) {
      showMessage('请输入 Markdown 正文内容', 'warning');
      return false;
    }
    if (formData.value.content.body_format === 'html' && !formData.value.content.body_html?.trim()) {
      showMessage('请输入 HTML 正文内容', 'warning');
      return false;
    }
  }
  
  // 视频、书籍、工具、项目资源如果选择了正文格式，则需要填写内容
  // 但这些资源类型的正文是可选的，如果选择了格式但没有内容，允许通过（用户可能只是想选择格式但暂时不填写）
  const optionalBodyTypes = ['course', 'book', 'tool', 'project'];
  if (formData.value.content_source === 'original' && optionalBodyTypes.includes(formData.value.resource_type)) {
    // 只有当格式字段有值且不是空字符串时才验证
    if (formData.value.content.body_format && formData.value.content.body_format.trim() !== '') {
      // 检查是否有内容（markdown 或 html）
      const hasMarkdown = formData.value.content.body_markdown?.trim();
      const hasHtml = formData.value.content.body_html?.trim();
      const hasContent = hasMarkdown || hasHtml;
      
      // 如果选择了格式但没有内容，允许通过验证（因为正文是可选的）
      // 只有在有内容时才验证格式匹配
      if (hasContent) {
        // 有内容，验证格式匹配
        if (formData.value.content.body_format === 'markdown' && !hasMarkdown) {
          showMessage('如果选择了 Markdown 格式，请填写正文内容', 'warning');
          return false;
        }
        if (formData.value.content.body_format === 'html' && !hasHtml) {
          showMessage('如果选择了 HTML 格式，请填写正文内容', 'warning');
          return false;
        }
      }
      // 如果没有内容，允许通过（因为正文是可选的）
    }
  }
  
  return true;
};

// 关闭模态框
const closeModal = () => {
  showAddResourceModal.value = false;
  showEditResourceModal.value = false;
  activeTab.value = 'basic'; // 重置到第一个标签页
  showAdvancedContent.value = false; // 重置折叠状态
  resetForm();
};

// 编辑资源
const editResource = async (resource) => {
  try {
    const detail = await adminService.getResource(resource.id);
    let categoryIds = [];
    if (Array.isArray(detail.categories)) {
      categoryIds = typeof detail.categories[0] === 'number'
        ? detail.categories
        : detail.categories.map(cat => cat.id);
    } else if (Array.isArray(detail.categories_display)) {
      categoryIds = detail.categories_display.map(cat => cat.id);
    }
    
    formData.value = {
      title: detail.title,
      description: detail.description,
      url: detail.url,
      hero_cover: detail.hero_cover || '',
      resource_type: detail.resource_type,
      target_audience: detail.target_audience,
      rating: detail.rating,
      categories: categoryIds,
      content_source: detail.content_source || 'original',
      content: {
        body_format: detail.content?.body_format || '',
        // 保持原始值，不进行同步，避免两个字段都有值
        body_markdown: detail.content?.body_markdown || '',
        body_html: detail.content?.body_html || '',
        sections: detail.content?.sections || [],
        document_html: detail.content?.document_html || '',
        document_toc: detail.content?.document_toc || [],
        download_url: detail.content?.download_url || '',
        embed_provider: detail.content?.embed_provider || '',
        embed_url: detail.content?.embed_url || ''
      }
    };
    
    // 保存原始正文内容，用于格式切换时恢复
    const bodyFormat = detail.content?.body_format || ''
    if (bodyFormat === 'html') {
      originalBodyContent.value = {
        html: detail.content?.body_html || '',
        markdown: '',
        format: 'html'
      }
    } else if (bodyFormat === 'markdown' || bodyFormat === 'plaintext') {
      originalBodyContent.value = {
        markdown: detail.content?.body_markdown || '',
        html: '',
        format: bodyFormat
      }
    } else {
      originalBodyContent.value = {
        markdown: '',
        html: '',
        format: ''
      }
    }
    
    sectionsJson.value = JSON.stringify(detail.content?.sections || [], null, 2);
    documentTocJson.value = JSON.stringify(detail.content?.document_toc || [], null, 2);
    resourceToEditId.value = resource.id;
    showEditResourceModal.value = true;
  } catch {
    showMessage('获取资源详情失败', 'error');
  }
};

// 删除资源
const deleteResource = async (resourceId) => {
  const resource = resources.value.find(r => r.id === resourceId);
  const resourceName = resource ? resource.title : '该资源';
  
  try {
    await ElMessageBox.confirm(
      `确定要永久删除资源"${resourceName}"吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        showClose: false
      }
    );
    
    deleting.value = true;
    await adminService.deleteResource(resourceId);
    ElMessage.success(`资源"${resourceName}"删除成功！`);
    await loadResources();
  } catch (error) {
    if (error === 'cancel' || error.name === 'CanceledError') {
      console.log('用户取消了删除操作');
      return;
    }
    console.error('删除资源失败:', error);
    const errorMessage = error.message || '删除失败，请稍后重试';
    ElMessage.error(`删除失败：${errorMessage}`);
  } finally {
    deleting.value = false;
  }
};

const safeParseJson = (input, fallback) => {
  if (!input?.trim()) return fallback;
  try {
    return JSON.parse(input);
  } catch (error) {
    console.warn('JSON 解析失败，使用默认值', error);
    return fallback;
  }
};

// 处理书籍文件选择
const handleBookFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    // 检查文件大小（100MB限制）
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      showMessage('文件大小不能超过100MB', 'error');
      if (bookFileInput.value) {
        bookFileInput.value.value = '';
      }
      bookFile.value = null;
      bookFileName.value = '';
      return;
    }
    bookFile.value = file;
    bookFileName.value = file.name;
  } else {
    bookFile.value = null;
    bookFileName.value = '';
  }
};

const buildRequestPayload = () => {
  const payload = JSON.parse(JSON.stringify(formData.value));
  payload.content.sections = safeParseJson(sectionsJson.value, []);
  payload.content.document_toc = safeParseJson(documentTocJson.value, []);
  return payload;
};

// 提交表单
const handleSubmit = async () => {
  submitting.value = true;
  try {
    if (!validateForm()) {
      // validateForm 已经显示了具体的错误信息，不需要再显示通用提示
      submitting.value = false;
      return;
    }
    
    // 如果有书籍文件，使用FormData提交
    if (bookFile.value) {
      const formDataObj = new FormData();
      const payload = buildRequestPayload();
      
      // 添加基本字段
      formDataObj.append('title', payload.title);
      formDataObj.append('description', payload.description || '');
      formDataObj.append('url', payload.url || '');
      formDataObj.append('hero_cover', payload.hero_cover || '');
      formDataObj.append('resource_type', payload.resource_type);
      formDataObj.append('target_audience', payload.target_audience);
      formDataObj.append('rating', payload.rating);
      formDataObj.append('content_source', payload.content_source);
      
      // 添加分类
      if (payload.categories && payload.categories.length > 0) {
        payload.categories.forEach(catId => {
          formDataObj.append('categories', catId);
        });
      }
      
      // 添加内容字段
      if (payload.content) {
        if (payload.content.body_format) {
          formDataObj.append('content[body_format]', payload.content.body_format);
        }
        if (payload.content.body_markdown) {
          formDataObj.append('content[body_markdown]', payload.content.body_markdown);
        }
        if (payload.content.body_html) {
          formDataObj.append('content[body_html]', payload.content.body_html);
        }
        if (payload.content.document_html) {
          formDataObj.append('content[document_html]', payload.content.document_html);
        }
        if (payload.content.download_url) {
          formDataObj.append('content[download_url]', payload.content.download_url);
        }
        if (payload.content.embed_provider) {
          formDataObj.append('content[embed_provider]', payload.content.embed_provider);
        }
        if (payload.content.embed_url) {
          formDataObj.append('content[embed_url]', payload.content.embed_url);
        }
        if (payload.content.sections && payload.content.sections.length > 0) {
          formDataObj.append('content[sections]', JSON.stringify(payload.content.sections));
        }
        if (payload.content.document_toc && payload.content.document_toc.length > 0) {
          formDataObj.append('content[document_toc]', JSON.stringify(payload.content.document_toc));
        }
      }
      
      // 添加书籍文件
      formDataObj.append('content[book_file]', bookFile.value);
      
      if (showEditResourceModal.value && resourceToEditId.value) {
        await adminService.updateResource(resourceToEditId.value, formDataObj);
        showMessage('资源更新成功');
      } else {
        await adminService.createResource(formDataObj);
        showMessage('资源创建成功');
      }
    } else {
      // 没有文件，使用JSON提交
      const payload = buildRequestPayload();
      if (showEditResourceModal.value && resourceToEditId.value) {
        await adminService.updateResource(resourceToEditId.value, payload);
        showMessage('资源更新成功');
      } else {
        await adminService.createResource(payload);
        showMessage('资源创建成功');
      }
    }
    
    closeModal();
    await loadResources();
  } catch (error) {
    showMessage(`操作失败: ${error.message || '未知错误'}`, 'error');
  } finally {
    submitting.value = false;
  }
};

// 辅助方法：资源类型转中文
const getResourceTypeText = (type) => {
  const typeMap = { 
    book: '书籍', 
    video: '视频', 
    article: '文章', 
    course: '课程',
    project: '项目',
    tool: '工具',
    document: '文档'
  };
  return typeMap[type] || type;
};

// 辅助方法：目标受众转中文
const getTargetAudienceText = (audience) => {
  if (!audience) return '未指定';
  
  const audienceMap = {
    'beginner': '入门阶段',
    'intermediate': '中级阶段',
    'advanced': '高级阶段',
    '入门阶段': '入门阶段',
    '中级阶段': '中级阶段',
    '高级阶段': '高级阶段'
  };
  
  return audienceMap[audience] || audience;
};

const resourceTypeMeta = computed(() => {
  const metaMap = {
    book: {
      title: '书籍类资源',
      description: '适合作为系统性学习材料，可上传章节/文档内容。',
      icon: 'fas fa-book',
      tips: [
        '正文区可填写整本书的摘要或章节示例',
        '章节 JSON 可用于列出目录结构',
        '可附带下载链接或文档 HTML 供阅读'
      ]
    },
    course: {
      title: '课程/视频资源',
      description: '用于整理课程章节、视频嵌入链接等内容。',
      icon: 'fas fa-graduation-cap',
      tips: [
        '正文里可梳理课程目标与学习建议',
        '章节 JSON 可写各章节/实战任务',
        '若有嵌入平台，请填写嵌入提供方与地址'
      ]
    },
    article: {
      title: '文章/教程资源',
      description: '重点突出正文内容，可直接粘贴 Markdown/HTML。',
      icon: 'fas fa-file-alt',
      tips: [
        '正文内容是学习详情页的主文本',
        '可配合文档 HTML/TOC 提供延伸阅读',
        '站内原创/上传的资源可以不填写资源链接'
      ]
    },
    project: {
      title: '项目/实战资源',
      description: '适合记录项目步骤与代码片段，帮助用户实操练习。',
      icon: 'fas fa-code-branch',
      tips: [
        '正文可拆分为多步操作或任务说明',
        '章节 JSON 可描述每个模块/里程碑',
        '可附带代码仓库、演示地址等链接'
      ]
    },
    tool: {
      title: '工具/平台资源',
      description: '介绍特定开发工具或在线平台的使用方式。',
      icon: 'fas fa-wrench',
      tips: [
        '正文可写工具亮点、用法示例',
        '可补充嵌入链接或下载地址',
        '若为外链工具，选择"外部导入"并填写资源链接'
      ]
    },
    document: {
      title: '文档/资料资源',
      description: '汇总 PDF/规范/标准等资料，适合配合文档 HTML 与 TOC。',
      icon: 'fas fa-folder-open',
      tips: [
        '正文可概述文档结构或关键章节',
        'document_html 可放置全文或精选段落',
        'document_toc 用于生成目录导航'
      ]
    }
  };
  return metaMap[formData.value.resource_type] || {
    title: '学习资源',
    description: '根据资源类型填写相应内容。',
    icon: 'fas fa-lightbulb',
    tips: ['选择资源类型后，会显示更详细的填写说明。']
  };
});

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.admin-content {
  flex: 1;
  padding: 20px;
  margin-left: 240px; /* 与侧边栏宽度一致 */
  min-height: 100vh;
  box-sizing: border-box;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.admin-header h1 {
  color: #333;
  font-size: 24px;
  margin: 0;
}

.content-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-section {
  margin-bottom: 20px;
}

/* 统一的搜索容器样式 */
.search-input-group {
  display: flex;
  align-items: center;
  gap: 10px; /* 添加按钮间距 */
}

.search-container {
  display: flex;
  align-items: center;
  gap: 0;
}

/* 统一的搜索输入框样式 */
.search-input {
  padding: 11px 16px;
  border: 1px solid #d1d5db;
  border-radius: 4px 0 0 4px;
  width: 300px;
  font-size: 14px;
  border-right: none;
  box-sizing: border-box;
  height: 40px;
}

/* 搜索按钮 */
.search-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.2s;
  height: 40px;
  box-sizing: border-box;
}

.search-btn:hover {
  background-color: #2563eb;
}

/* 统一的添加按钮样式 */
.add-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.2s;
  height: 40px;
}

.add-btn:hover {
  background-color: #2563eb;
}

/* 分类折叠面板 */
.category-accordion {
  margin-top: 20px;
}

.accordion-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}

.accordion-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background-color: #f8f9fa;
  cursor: pointer;
  transition: background-color 0.3s;
}

.accordion-header:hover {
  background-color: #e9ecef;
}

/* 折叠图标：删除无效的 transform 过渡（仅文本切换，无 transform 操作） */
.accordion-icon {
  font-size: 18px;
  font-weight: bold;
  margin-right: 12px;
}

.category-title {
  flex: 1;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.resource-count {
  color: #6c757d;
  font-size: 14px;
}

.accordion-content {
  padding: 0;
}

.empty-category {
  padding: 40px 20px;
  text-align: center;
  color: #6c757d;
  font-style: italic;
}

/* 表格样式 */
.resource-table {
  width: 100%;
  border-collapse: collapse;
}

.resource-table th,
.resource-table td {
  padding: 12px 20px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.resource-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #495057;
}

.title-cell {
  max-width: 250px;
}

.resource-url {
  color: #007bff;
  text-decoration: none;
  transition: color 0.3s;
}

.resource-url:hover {
  color: #0056b3;
  text-decoration: underline;
}

.category-tag {
  display: inline-block;
  background-color: #e9ecef;
  color: #495057;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-right: 4px;
  margin-bottom: 4px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.edit-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  transition: background-color 0.3s;
}

.edit-btn:hover {
  background-color: #2563eb;
}

.delete-btn {
  background-color: #ef4444;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  transition: background-color 0.3s;
}

.delete-btn:hover {
  background-color: #dc2626;
}

.no-data,
.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.delete-modal {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ddd;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

/* 标签说明 */
.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.resource-type-hint {
  padding: 12px 16px;
  border: 1px solid #dbeafe;
  border-radius: 8px;
  background: #f8fbff;
  margin-bottom: 20px;
}

.resource-type-hint ul {
  margin: 8px 0 0;
  padding-left: 20px;
  color: #4b5563;
  font-size: 13px;
}

.resource-type-hint li {
  margin-bottom: 4px;
}

.resource-type-hint .hint-title {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  color: #1d4ed8;
}

.hint-title strong {
  font-size: 14px;
  color: #1e3a8a;
}

.hint-text {
  font-size: 12px;
  color: #6b7280;
}

.form-group textarea,
.form-group select,
.category-search-wrapper {
  width: 100%;
  box-sizing: border-box;
}

.form-group textarea,
.form-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group textarea {
  resize: vertical;
}

/* 排除复选框/单选框的输入框样式 */
.form-group input:not([type="checkbox"]):not([type="radio"]) {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

/* 分类选择器样式 */
.category-selector {
  margin-top: 10px;
}

.category-search-wrapper {
  margin-bottom: 10px;
}

.category-search {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.category-search:focus {
  outline: none;
  border-color: #409eff;
}

.category-list {
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  margin-top: 10px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-sizing: border-box;
}

.category-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  cursor: pointer;
  user-select: none;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.category-checkbox:hover {
  background-color: #f5f7fa;
}

/* 重置复选框样式 */
.category-checkbox input[type="checkbox"] {
  width: auto;
  padding: 0;
  margin: 0;
}

.no-results {
  text-align: center;
  color: #909399;
  font-size: 14px;
  padding: 20px;
}

.selected-count {
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.required {
  color: #f56c6c;
  margin-left: 4px;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 5px;
}

.form-hint {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.submit-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #45a049;
}

.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.delete-confirm-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.delete-confirm-btn:hover:not(:disabled) {
  background-color: #c82333;
}

.delete-confirm-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 消息提示 */
/* 标签页样式 */
.form-tabs {
  display: flex;
  gap: 8px;
  border-bottom: 2px solid #e5e7eb;
  margin-bottom: 24px;
  padding: 0 4px;
}

.tab-btn {
  padding: 12px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-btn:hover {
  color: #4f46e5;
  background: #f3f4f6;
}

.tab-btn.active {
  color: #4f46e5;
  border-bottom-color: #4f46e5;
  background: #f8fafc;
}

.tab-btn i {
  font-size: 16px;
}

.tab-content {
  min-height: 400px;
}

.section-title {
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.section-title h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #1f2937;
  font-weight: 600;
}

.section-desc {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

/* 折叠面板样式 */
.collapsible-section {
  margin-top: 24px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.collapsible-header {
  width: 100%;
  padding: 12px 16px;
  background: #f9fafb;
  border: none;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  transition: background 0.2s;
}

.collapsible-header:hover {
  background: #f3f4f6;
}

.collapsible-header i {
  font-size: 12px;
  color: #6b7280;
  transition: transform 0.2s;
}

.collapsible-content {
  padding: 16px;
  background: white;
}

.content-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.message-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 4px;
  color: white;
  font-size: 14px;
  z-index: 1001;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease-out;
}

.message-toast.success {
  background-color: #28a745;
}

.message-toast.error {
  background-color: #dc3545;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>