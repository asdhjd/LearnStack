<template>
  <div class="submit-resource-page">
    <div class="page-header">
      <h1>投稿学习资源</h1>
      <p class="subtitle">分享优质的学习资源，帮助更多开发者成长</p>
    </div>

    <div class="submit-form-container">
      <form @submit.prevent="handleSubmit" class="submit-form">
        <!-- 基本信息 -->
        <section class="form-section">
          <h2>基本信息</h2>
          
          <div class="form-group">
            <label for="title">资源标题 <span class="required">*</span></label>
            <input 
              type="text" 
              id="title" 
              v-model="formData.title" 
              required 
              placeholder="例如：Python编程从入门到实践"
              maxlength="200"
            />
          </div>

          <div class="form-group">
            <label for="description">资源描述 <span class="required">*</span></label>
            <textarea 
              id="description" 
              v-model="formData.description" 
              required 
              placeholder="请简要描述这个资源的内容、特点和适用场景"
              rows="4"
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="resource_type">资源类型 <span class="required">*</span></label>
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

            <div class="form-group">
              <label for="target_audience">适用人群 <span class="required">*</span></label>
              <select id="target_audience" v-model="formData.target_audience" required>
                <option value="">请选择适用人群</option>
                <option value="beginner">入门阶段</option>
                <option value="intermediate">中级阶段</option>
                <option value="advanced">高级阶段</option>
              </select>
            </div>
          </div>

          <!-- 资源类型说明 -->
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

          <div class="form-group">
            <label for="content_source">内容来源 <span class="required">*</span></label>
            <select id="content_source" v-model="formData.content_source" required>
              <option value="original">站内原创/上传</option>
              <option value="embedded">外部导入</option>
            </select>
            <p class="form-hint">
              <strong>站内原创/上传</strong>：内容由您原创或上传到本站<br>
              <strong>外部导入</strong>：内容来自外部平台，需要提供资源链接
            </p>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="url">资源链接 <span v-if="formData.content_source === 'embedded'" class="required">*</span></label>
              <input 
                type="url" 
                id="url" 
                v-model="formData.url" 
                :required="formData.content_source === 'embedded'"
                placeholder="https://example.com"
              />
              <p v-if="formData.content_source === 'original'" class="form-hint">站内原创/上传的资源可以不填写链接</p>
              <p v-if="formData.content_source === 'embedded'" class="form-hint">外部导入的资源必须提供链接</p>
            </div>

            <div class="form-group">
              <label for="hero_cover">封面图片 <span class="required">*</span></label>
              <input 
                type="url" 
                id="hero_cover" 
                v-model="formData.hero_cover" 
                required
                placeholder="https://example.com/cover.jpg"
              />
              <p class="form-hint">请提供资源的封面图片URL</p>
            </div>
          </div>

          <div class="form-group">
            <label for="rating">评分（1-5，可选）</label>
            <input 
              type="number" 
              id="rating" 
              v-model.number="formData.rating" 
              min="1" 
              max="5" 
              placeholder="5"
            />
          </div>

          <div class="form-group">
            <label for="categories">关联分类 <span class="required">*</span></label>
            
            <!-- 已选择的分类标签 -->
            <div v-if="formData.categories.length > 0" class="selected-categories">
              <span 
                v-for="categoryId in formData.categories" 
                :key="categoryId"
                class="category-tag"
              >
                <i :class="getCategoryIcon(categoryId)"></i>
                {{ getCategoryName(categoryId) }}
                <button 
                  type="button" 
                  @click="removeCategory(categoryId)"
                  class="remove-tag-btn"
                >
                  ×
                </button>
              </span>
            </div>
            
            <!-- 分类下拉框 -->
            <select 
              id="categories" 
              v-model="selectedCategoryId"
              @change="addCategory"
              class="category-select"
            >
              <option value="">请选择分类（可多选）</option>
              <option 
                v-for="category in availableCategories" 
                :key="category.id"
                :value="category.id"
                :disabled="formData.categories.includes(category.id)"
              >
                {{ category.name }}
              </option>
            </select>
            <p class="form-hint">至少选择一个分类，已选择的分类会显示在上方</p>
          </div>
        </section>

        <!-- 内容部分（根据资源类型动态显示） -->
        <section class="form-section" v-if="formData.resource_type">
          <h2>内容信息</h2>

          <!-- 书籍 -->
          <template v-if="formData.resource_type === 'book'">
            <div class="form-group">
              <label for="body_format">正文格式 <span class="required">*</span></label>
              <select id="body_format" v-model="formData.content.body_format" required>
                <option value="">请选择格式</option>
                <option value="plaintext">纯文本</option>
                <option value="markdown">Markdown</option>
                <option value="html">HTML</option>
              </select>
              <small class="form-hint">提示：系统会智能识别内容格式，即使选择 HTML 格式，输入 Markdown 或纯文本也能正常显示</small>
            </div>

            <div class="form-group">
              <label for="body_content">正文内容 <span class="required">*</span></label>
              <textarea 
                id="body_content" 
                v-model="formData.content.body_markdown" 
                required
                :placeholder="getBodyPlaceholder()"
                rows="15"
              ></textarea>
              <small class="form-hint">{{ getBodyHint() }}</small>
            </div>

            <div class="form-group">
              <label for="book_file">书籍文件 <span class="required">*</span></label>
              <input 
                type="file" 
                id="book_file" 
                ref="bookFileInput"
                @change="handleBookFileChange"
                accept=".pdf,.epub,.mobi,.doc,.docx,.zip,.rar,.7z,.tar,.gz,.tar.gz"
                required
              />
              <p class="form-hint">
                支持格式：PDF、EPUB、MOBI、DOC、DOCX、ZIP、RAR、7Z、TAR、GZ、TAR.GZ<br>
                文件大小限制：100MB
                <span v-if="bookFileName" style="display: block; margin-top: 5px; color: #4f46e5; font-weight: 500;">已选择：{{ bookFileName }}</span>
              </p>
            </div>
            
            <div class="form-group">
              <label for="download_url">下载链接（可选）</label>
              <input 
                type="url" 
                id="download_url" 
                v-model="formData.content.download_url" 
                placeholder="https://example.com/download"
              />
              <p class="form-hint">如果已上传文件，此字段可选。如果没有上传文件，请提供外部下载链接。</p>
            </div>
          </template>

          <!-- 课程 -->
          <template v-if="formData.resource_type === 'course'">
            <div class="form-group">
              <label>课程章节来源</label>
              <div class="radio-group">
                <label>
                  <input type="radio" value="url" v-model="courseInputMode" />
                  从Bilibili视频URL自动抓取
                </label>
                <label>
                  <input type="radio" value="manual" v-model="courseInputMode" />
                  手动输入JSON
                </label>
              </div>
            </div>

            <template v-if="courseInputMode === 'url'">
              <div class="form-group">
                <label for="bilibili_url">Bilibili视频URL <span class="required">*</span></label>
                <div class="url-input-group">
                  <input 
                    type="url" 
                    id="bilibili_url" 
                    v-model="bilibiliUrl" 
                    placeholder="https://www.bilibili.com/video/BV1gq1sBPECH"
                  />
                  <button type="button" @click="fetchBilibiliSections" class="fetch-btn" :disabled="fetchingBilibili">
                    {{ fetchingBilibili ? '抓取中...' : '自动抓取章节' }}
                  </button>
                </div>
                <p class="form-hint">输入Bilibili视频链接，系统会自动抓取所有章节信息</p>
                <div v-if="bilibiliFetchFailed" class="fetch-failed-notice">
                  <p class="error-text">自动抓取失败，您可以：</p>
                  <button type="button" @click="openRequestModal" class="request-admin-btn">
                    <i class="fas fa-user-shield"></i> 申请管理员添加
                  </button>
                </div>
              </div>
            </template>

            <template v-if="courseInputMode === 'manual'">
              <div class="form-group">
                <label for="sections">课程章节（JSON格式） <span class="required">*</span></label>
                <textarea 
                  id="sections" 
                  v-model="sectionsJson" 
                  required
                  placeholder='[{"title": "第一章：Python基础", "summary": "介绍Python基本语法", "video_url": "https://www.bilibili.com/video/BV1gq1sBPECH?p=1", "embed_url": "https://player.bilibili.com/player.html?bvid=BV1gq1sBPECH&page=1"}]'
                  rows="10"
                ></textarea>
                <p class="form-hint">JSON 格式：每个章节包含 title（标题）、summary（简介，可选）、video_url（视频链接，可选）、embed_url（嵌入链接，必填）</p>
              </div>
            </template>
          </template>

          <!-- 文章 -->
          <template v-if="formData.resource_type === 'article'">
            <div class="form-group">
              <label>内容来源</label>
              <div class="radio-group">
                <label>
                  <input type="radio" value="url" v-model="articleInputMode" />
                  从文章URL自动抓取
                </label>
                <label>
                  <input type="radio" value="manual" v-model="articleInputMode" />
                  手动输入内容
                </label>
              </div>
            </div>

            <template v-if="articleInputMode === 'url'">
              <div class="form-group">
                <label for="article_url">文章URL <span class="required">*</span></label>
                <div class="url-input-group">
                  <input 
                    type="url" 
                    id="article_url" 
                    v-model="articleUrl" 
                    placeholder="https://blog.csdn.net/xxx/article/details/xxx"
                  />
                  <button type="button" @click="fetchArticleContent" class="fetch-btn" :disabled="fetchingArticle">
                    {{ fetchingArticle ? '抓取中...' : '自动抓取内容' }}
                  </button>
                </div>
                <p class="form-hint">支持CSDN、掘金、阿里云、博客园、慕课网、腾讯云等网站</p>
                <div v-if="articleFetchFailed" class="fetch-failed-notice">
                  <p class="error-text">自动抓取失败，您可以：</p>
                  <button type="button" @click="openRequestModal" class="request-admin-btn">
                    <i class="fas fa-user-shield"></i> 申请管理员添加
                  </button>
                </div>
              </div>
            </template>

            <template v-if="articleInputMode === 'manual'">
              <div class="form-group">
                <label for="body_format">正文格式 <span class="required">*</span></label>
                <select id="body_format" v-model="formData.content.body_format" required>
                  <option value="">请选择格式</option>
                  <option value="markdown">Markdown</option>
                  <option value="html">HTML</option>
                </select>
                <small class="form-hint">提示：系统会智能识别内容格式，即使选择 HTML 格式，输入 Markdown 或纯文本也能正常显示</small>
              </div>

              <div class="form-group">
                <label for="body_content">正文内容 <span class="required">*</span></label>
                <textarea 
                  id="body_content" 
                  v-model="formData.content.body_markdown" 
                  required
                  :placeholder="getBodyPlaceholder()"
                  rows="15"
                ></textarea>
                <small class="form-hint">{{ getBodyHint() }}</small>
              </div>
            </template>
          </template>

          <!-- 项目 -->
          <template v-if="formData.resource_type === 'project'">
            <div class="form-group">
              <label for="body_format">正文格式 <span class="required">*</span></label>
              <select id="body_format" v-model="formData.content.body_format" required>
                <option value="">请选择格式</option>
                <option value="markdown">Markdown</option>
                <option value="html">HTML</option>
              </select>
              <small class="form-hint">提示：系统会智能识别内容格式，即使选择 HTML 格式，输入 Markdown 或纯文本也能正常显示</small>
            </div>

            <div class="form-group">
              <label for="body_content">项目介绍 <span class="required">*</span></label>
              <textarea 
                id="body_content" 
                v-model="formData.content.body_markdown" 
                required
                :placeholder="getBodyPlaceholder()"
                rows="15"
              ></textarea>
              <small class="form-hint">{{ getBodyHint() }}</small>
            </div>

            <div class="form-group">
              <label for="download_url">下载链接 <span class="required">*</span></label>
              <input 
                type="url" 
                id="download_url" 
                v-model="formData.content.download_url" 
                required
                placeholder="https://example.com/download"
              />
            </div>
          </template>

          <!-- 工具 -->
          <template v-if="formData.resource_type === 'tool'">
            <div class="form-group">
              <label for="body_format">正文格式 <span class="required">*</span></label>
              <select id="body_format" v-model="formData.content.body_format" required>
                <option value="">请选择格式</option>
                <option value="markdown">Markdown</option>
                <option value="html">HTML</option>
              </select>
              <small class="form-hint">提示：系统会智能识别内容格式，即使选择 HTML 格式，输入 Markdown 或纯文本也能正常显示</small>
            </div>

            <div class="form-group">
              <label for="body_content">工具说明 <span class="required">*</span></label>
              <textarea 
                id="body_content" 
                v-model="formData.content.body_markdown" 
                required
                :placeholder="getBodyPlaceholder()"
                rows="15"
              ></textarea>
              <small class="form-hint">{{ getBodyHint() }}</small>
            </div>

            <div class="form-group">
              <label for="download_url">下载链接 <span class="required">*</span></label>
              <input 
                type="url" 
                id="download_url" 
                v-model="formData.content.download_url" 
                required
                placeholder="https://example.com/download"
              />
            </div>
          </template>

          <!-- 文档 -->
          <template v-if="formData.resource_type === 'document'">
            <div class="form-group">
              <label>文档内容方式 <span class="required">*</span></label>
              <div class="radio-group">
                <label>
                  <input 
                    type="radio" 
                    value="html" 
                    v-model="documentMode"
                  />
                  直接提供 HTML 内容
                </label>
                <label>
                  <input 
                    type="radio" 
                    value="embed" 
                    v-model="documentMode"
                  />
                  嵌入外部文档
                </label>
              </div>
            </div>

            <template v-if="documentMode === 'html'">
              <div class="form-group">
                <label for="document_html">文档 HTML 内容 <span class="required">*</span></label>
                <textarea 
                  id="document_html" 
                  v-model="formData.content.document_html" 
                  required
                  placeholder="请输入完整的 HTML 内容（包括标题、段落、代码块等）"
                  rows="15"
                ></textarea>
              </div>

              <div class="form-group">
                <label for="document_toc">文档目录（JSON，可选）</label>
                <textarea 
                  id="document_toc" 
                  v-model="documentTocJson" 
                  placeholder='[{"id": "intro", "title": "1. 介绍", "level": 1}, {"id": "install", "title": "2. 安装", "level": 1}]'
                  rows="8"
                ></textarea>
                <p class="form-hint">JSON 格式：每个目录项包含 id（锚点ID）、title（标题）、level（层级：1=h1, 2=h2, 3=h3）</p>
              </div>
            </template>

            <template v-if="documentMode === 'embed'">
              <div class="form-group">
                <label for="embed_provider">文档提供方</label>
                <input 
                  type="text" 
                  id="embed_provider" 
                  v-model="formData.content.embed_provider" 
                  placeholder="例如：antd, react, vue"
                />
              </div>

              <div class="form-group">
                <label for="embed_url">嵌入地址 <span class="required">*</span></label>
                <input 
                  type="url" 
                  id="embed_url" 
                  v-model="formData.content.embed_url" 
                  required
                  placeholder="https://ant.design/docs/react/getting-started-cn"
                />
              </div>
            </template>
          </template>
        </section>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <button type="button" @click="handleCancel" class="cancel-btn">取消</button>
          <button type="submit" class="submit-btn" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交投稿' }}
          </button>
        </div>
      </form>
    </div>

    <!-- 申请管理员添加模态框 -->
    <div v-if="showRequestModal" class="modal-overlay" @click.self="closeRequestModal">
      <div class="modal-content request-modal">
        <div class="modal-header">
          <h3>申请管理员添加资源</h3>
          <button @click="closeRequestModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="submitResourceRequest" class="request-form">
          <div class="form-group">
            <label for="request_title">资源标题 <span class="required">*</span></label>
            <input 
              type="text" 
              id="request_title" 
              v-model="requestForm.title" 
              required 
              placeholder="请输入资源标题"
              maxlength="200"
            />
          </div>

          <div class="form-group">
            <label for="request_description">资源描述</label>
            <textarea 
              id="request_description" 
              v-model="requestForm.description" 
              placeholder="请简要描述这个资源"
              rows="3"
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="request_url">资源链接 <span class="required">*</span></label>
              <input 
                type="url" 
                id="request_url" 
                v-model="requestForm.url" 
                required 
                placeholder="https://example.com"
              />
            </div>

            <div class="form-group">
              <label for="request_type">资源类型 <span class="required">*</span></label>
              <select id="request_type" v-model="requestForm.resource_type" required>
                <option value="">请选择</option>
                <option value="book">书籍</option>
                <option value="course">课程</option>
                <option value="article">文章</option>
                <option value="project">项目</option>
                <option value="tool">工具</option>
                <option value="document">文档</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="request_audience">适用人群</label>
            <select id="request_audience" v-model="requestForm.target_audience">
              <option value="">请选择</option>
              <option value="beginner">入门阶段</option>
              <option value="intermediate">中级阶段</option>
              <option value="advanced">高级阶段</option>
            </select>
          </div>

          <div class="form-group">
            <label for="request_reason">申请理由 <span class="required">*</span></label>
            <textarea 
              id="request_reason" 
              v-model="requestForm.reason" 
              required
              placeholder="请说明为什么无法使用自动抓取功能（例如：网站不支持、需要登录、内容格式特殊等）"
              rows="4"
            ></textarea>
            <p class="form-hint">请详细说明无法自动抓取的原因，帮助管理员更好地处理您的申请</p>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeRequestModal" class="cancel-btn">取消</button>
            <button type="submit" class="submit-btn" :disabled="submittingRequest">
              {{ submittingRequest ? '提交中...' : '提交申请' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { API_BASE_URL } from '@/config/api'
import { getAllTechnologies } from '@/services/category'

const router = useRouter()

// 书籍文件相关
const bookFileInput = ref(null)
const bookFile = ref(null)
const bookFileName = ref('')

// 处理书籍文件选择
const handleBookFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 检查文件大小（100MB限制）
    if (file.size > 100 * 1024 * 1024) {
      alert('文件大小不能超过100MB')
      event.target.value = ''
      bookFile.value = null
      bookFileName.value = ''
      return
    }
    bookFile.value = file
    bookFileName.value = file.name
  } else {
    bookFile.value = null
    bookFileName.value = ''
  }
}

// 表单数据
const formData = ref({
  title: '',
  description: '',
  url: '',
  resource_type: '',
  target_audience: '',
  rating: 5,
  hero_cover: '',
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
    embed_url: '',
  }
})

// 文档模式（HTML 或嵌入）
const documentMode = ref('html')

// 文章输入模式（URL 或手动）
const articleInputMode = ref('url')
const articleUrl = ref('')
const fetchingArticle = ref(false)
const articleFetchFailed = ref(false)

// 课程输入模式（URL 或手动）
const courseInputMode = ref('url')
const bilibiliUrl = ref('')
const fetchingBilibili = ref(false)
const bilibiliFetchFailed = ref(false)

// 申请管理员添加相关
const showRequestModal = ref(false)
const submittingRequest = ref(false)
const requestForm = ref({
  title: '',
  description: '',
  url: '',
  resource_type: '',
  target_audience: '',
  reason: ''
})

// 可用分类
const availableCategories = ref([])
const submitting = ref(false)

// 课程章节 JSON 字符串
const sectionsJson = ref('')
// 文档目录 JSON 字符串
const documentTocJson = ref('')

// 当前选中的分类ID（用于下拉框）
const selectedCategoryId = ref('')

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
  return '请输入正文内容（系统会智能识别格式）'
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

const getCategoryName = (categoryId) => {
  const category = availableCategories.value.find(cat => cat.id === categoryId)
  return category ? category.name : '未命名分类'
}

const getCategoryIcon = (categoryId) => {
  const category = availableCategories.value.find(cat => cat.id === categoryId)
  return category ? category.icon_image_url : ''
}

// 添加分类
const addCategory = () => {
  if (selectedCategoryId.value && !formData.value.categories.includes(selectedCategoryId.value)) {
    formData.value.categories.push(selectedCategoryId.value)
    selectedCategoryId.value = '' // 重置下拉框
  }
}

// 移除分类
const removeCategory = (categoryId) => {
  const index = formData.value.categories.indexOf(categoryId)
  if (index > -1) {
    formData.value.categories.splice(index, 1)
  }
}

// 资源类型改变时的处理
const onResourceTypeChange = () => {
  // 重置内容字段
  formData.value.content = {
    body_format: '',
    body_markdown: '',
    body_html: '',
    sections: [],
    document_html: '',
    document_toc: [],
    download_url: '',
    embed_provider: '',
    embed_url: '',
  }
  // 重置文件上传
  bookFile.value = null
  bookFileName.value = ''
  if (bookFileInput.value) {
    bookFileInput.value.value = ''
  }
  sectionsJson.value = ''
  documentTocJson.value = ''
  documentMode.value = 'html'
  articleInputMode.value = 'url'
  articleUrl.value = ''
  courseInputMode.value = 'url'
  bilibiliUrl.value = ''
  selectedCategoryId.value = ''
}

// 抓取文章内容
const fetchArticleContent = async () => {
  if (!articleUrl.value.trim()) {
    alert('请输入文章URL')
    return
  }

  fetchingArticle.value = true
  articleFetchFailed.value = false
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.post(
      `${API_BASE_URL}/resources/fetch-content/`,
      { url: articleUrl.value },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    if (response.data.success) {
      // 填充标题和描述（如果为空）
      if (!formData.value.title && response.data.title) {
        formData.value.title = response.data.title
      }
      if (!formData.value.description) {
        formData.value.description = `来自 ${articleUrl.value} 的文章内容`
      }
      
      // 填充HTML内容（自动抓取场景只填充 body_html，body_markdown 保持为空）
      formData.value.content.body_format = 'html'
      formData.value.content.body_html = response.data.content
      
      // 填充封面（如果有）
      if (response.data.cover && !formData.value.hero_cover) {
        formData.value.hero_cover = response.data.cover
      }
      
      alert('内容抓取成功！请检查并编辑内容后提交。')
      articleFetchFailed.value = false
    } else {
      articleFetchFailed.value = true
      alert(`抓取失败：${response.data.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('抓取文章内容失败:', error)
    articleFetchFailed.value = true
    alert(`抓取失败：${error.response?.data?.error || error.message || '网络错误'}`)
  } finally {
    fetchingArticle.value = false
  }
}

// 抓取Bilibili视频章节
const fetchBilibiliSections = async () => {
  if (!bilibiliUrl.value.trim()) {
    alert('请输入Bilibili视频URL')
    return
  }

  fetchingBilibili.value = true
  bilibiliFetchFailed.value = false
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.post(
      `${API_BASE_URL}/resources/fetch-bilibili-sections/`,
      { url: bilibiliUrl.value },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    if (response.data.success) {
      formData.value.content.sections = response.data.sections
      sectionsJson.value = JSON.stringify(response.data.sections, null, 2)
      
      // 填充标题和描述（如果为空）
      if (!formData.value.title) {
        formData.value.title = `Bilibili视频课程 - ${response.data.sections.length}个章节`
      }
      if (!formData.value.description) {
        formData.value.description = `来自 ${bilibiliUrl.value} 的视频课程，共 ${response.data.sections.length} 个章节`
      }
      
      alert(`成功抓取 ${response.data.sections.length} 个章节！`)
      bilibiliFetchFailed.value = false
    } else {
      bilibiliFetchFailed.value = true
      alert(`抓取失败：${response.data.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('抓取Bilibili章节失败:', error)
    bilibiliFetchFailed.value = true
    alert(`抓取失败：${error.response?.data?.error || error.message || '网络错误'}`)
  } finally {
    fetchingBilibili.value = false
  }
}

// 打开申请模态框（从抓取失败时调用）
const openRequestModal = () => {
  console.log('打开申请模态框')
  // 如果已经有URL，自动填充
  if (articleUrl.value) {
    requestForm.value.url = articleUrl.value
  } else if (bilibiliUrl.value) {
    requestForm.value.url = bilibiliUrl.value
  }
  if (formData.value.resource_type) {
    requestForm.value.resource_type = formData.value.resource_type
  }
  if (formData.value.title) {
    requestForm.value.title = formData.value.title
  }
  if (formData.value.description) {
    requestForm.value.description = formData.value.description
  }
  if (formData.value.target_audience) {
    requestForm.value.target_audience = formData.value.target_audience
  }
  console.log('设置 showRequestModal 为 true')
  showRequestModal.value = true
  console.log('showRequestModal 值:', showRequestModal.value)
}

// 关闭申请模态框
const closeRequestModal = () => {
  showRequestModal.value = false
  requestForm.value = {
    title: '',
    description: '',
    url: '',
    resource_type: '',
    target_audience: '',
    reason: ''
  }
}

// 提交资源添加申请
const submitResourceRequest = async () => {
  submittingRequest.value = true
  
  try {
    const token = localStorage.getItem('access_token')
    if (!token) {
      alert('请先登录')
      router.push('/login')
      return
    }

    console.log('提交申请数据:', requestForm.value)

    const response = await axios.post(
      `${API_BASE_URL}/resources/requests/`,
      requestForm.value,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    console.log('申请提交响应:', response.status, response.data)

    // DRF 创建成功时返回 201，数据中包含 id
    if (response.status === 201 && response.data.id) {
      alert('申请已提交！管理员会在审核后处理您的申请。')
      closeRequestModal()
      router.push('/resources')
    } else {
      alert(`提交失败：${response.data.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('提交申请失败:', error)
    console.error('错误详情:', error.response?.data)
    
    if (error.response?.data) {
      const errorData = error.response.data
      let errorMsg = '提交失败：\n'
      
      // 处理 DRF 验证错误
      if (error.response.status === 400) {
        if (typeof errorData === 'string') {
          errorMsg += errorData
        } else if (errorData.detail) {
          errorMsg += errorData.detail
        } else if (Array.isArray(errorData)) {
          errorMsg += errorData.join('\n')
        } else {
          // 处理字段验证错误
          const fieldErrors = []
          for (const [field, messages] of Object.entries(errorData)) {
            if (Array.isArray(messages)) {
              fieldErrors.push(`${field}: ${messages.join(', ')}`)
            } else {
              fieldErrors.push(`${field}: ${messages}`)
            }
          }
          if (fieldErrors.length > 0) {
            errorMsg += fieldErrors.join('\n')
          } else {
            errorMsg += JSON.stringify(errorData)
          }
        }
      } else {
        errorMsg += errorData.detail || errorData.error || JSON.stringify(errorData)
      }
      
      alert(errorMsg)
    } else {
      alert('提交失败，请检查网络连接或稍后重试')
    }
  } finally {
    submittingRequest.value = false
  }
}

// 加载可用分类
const loadCategories = async () => {
  try {
    const response = await getAllTechnologies()
    // 只显示子分类（parent_id 不为空的分类）
    availableCategories.value = response.filter(cat => cat.parent_id !== null)
  } catch (error) {
    console.error('加载分类失败:', error)
    alert('加载分类失败，请刷新页面重试')
  }
}

// 提交表单
const handleSubmit = async () => {
  // 验证分类
  if (formData.value.categories.length === 0) {
    alert('请至少选择一个分类')
    return
  }

  // 验证内容字段
  try {
    // 处理课程章节 JSON
    if (formData.value.resource_type === 'course') {
      if (!sectionsJson.value.trim()) {
        alert('请填写课程章节')
        return
      }
      try {
        formData.value.content.sections = JSON.parse(sectionsJson.value)
      } catch (err) {
        console.error('课程章节 JSON 解析失败:', err)
        alert('课程章节 JSON 格式错误，请检查格式')
        return
      }
    }

    // 处理文档目录 JSON
    if (formData.value.resource_type === 'document' && documentMode.value === 'html' && documentTocJson.value.trim()) {
      try {
        formData.value.content.document_toc = JSON.parse(documentTocJson.value)
      } catch (err) {
        console.error('文档目录 JSON 解析失败:', err)
        alert('文档目录 JSON 格式错误，请检查格式')
        return
      }
    }

    // 清理空字段
    const submitData = {
      ...formData.value,
      content: {}
    }

    // 根据资源类型添加必要的内容字段
    if (formData.value.resource_type === 'book') {
      if (!formData.value.content.body_format) {
        alert('请选择正文格式')
        return
      }
      // 统一验证：所有格式都使用 body_markdown 字段
      if (!formData.value.content.body_markdown || !formData.value.content.body_markdown.trim()) {
        alert('请填写正文内容')
        return
      }
      // 书籍类型需要上传文件或提供下载链接
      if (!bookFile.value && !formData.value.content.download_url) {
        alert('请上传书籍文件或填写下载链接')
        return
      }
      submitData.content = {
        body_format: formData.value.content.body_format,
        body_markdown: formData.value.content.body_markdown || '',
        body_html: '', // 统一使用 body_markdown，body_html 留空，由后端或前端智能处理
        download_url: formData.value.content.download_url || ''
      }
    } else if (formData.value.resource_type === 'course') {
      if (!formData.value.content.sections || formData.value.content.sections.length === 0) {
        alert('请填写课程章节')
        return
      }
      submitData.content = {
        sections: formData.value.content.sections
      }
    } else if (formData.value.resource_type === 'article') {
      // 如果是从URL自动抓取的，body_format 可能已经设置，但需要检查内容
      // 如果 body_format 未设置，检查是否有内容（自动抓取时可能只填充了 body_html）
      if (!formData.value.content.body_format) {
        // 如果有 body_html 或 body_markdown，自动设置格式
        if (formData.value.content.body_html || formData.value.content.body_markdown) {
          formData.value.content.body_format = 'html'
        } else {
          alert('请选择正文格式或使用自动抓取功能')
          return
        }
      }
      // 验证：自动抓取场景 body_html 有内容即可，手动输入场景 body_markdown 有内容即可
      const hasBodyHtml = formData.value.content.body_html && formData.value.content.body_html.trim()
      const hasBodyMarkdown = formData.value.content.body_markdown && formData.value.content.body_markdown.trim()
      if (!hasBodyHtml && !hasBodyMarkdown) {
        alert('请填写正文内容')
        return
      }
      submitData.content = {
        body_format: formData.value.content.body_format,
        body_markdown: formData.value.content.body_markdown || '', // 自动抓取时可能为空
        body_html: formData.value.content.body_html || '' // 自动抓取时填充这里
      }
    } else if (formData.value.resource_type === 'project' || formData.value.resource_type === 'tool') {
      if (!formData.value.content.body_format) {
        alert('请选择正文格式')
        return
      }
      // 统一验证：所有格式都使用 body_markdown 字段
      if (!formData.value.content.body_markdown || !formData.value.content.body_markdown.trim()) {
        alert('请填写正文内容')
        return
      }
      if (!formData.value.content.download_url) {
        alert('请填写下载链接')
        return
      }
      submitData.content = {
        body_format: formData.value.content.body_format,
        body_markdown: formData.value.content.body_markdown || '',
        body_html: '', // 统一使用 body_markdown，body_html 留空，由后端或前端智能处理
        download_url: formData.value.content.download_url
      }
    } else if (formData.value.resource_type === 'document') {
      if (documentMode.value === 'html') {
        if (!formData.value.content.document_html) {
          alert('请填写文档 HTML 内容')
          return
        }
        submitData.content = {
          document_html: formData.value.content.document_html,
          document_toc: formData.value.content.document_toc || []
        }
      } else {
        if (!formData.value.content.embed_url) {
          alert('请填写嵌入地址')
          return
        }
        submitData.content = {
          embed_provider: formData.value.content.embed_provider || '',
          embed_url: formData.value.content.embed_url
        }
      }
    }

    // 验证资源链接（外部导入时必须填写）
    if (formData.value.content_source === 'embedded') {
      if (!submitData.url || !submitData.url.trim()) {
        alert('外部导入的资源必须填写资源链接')
        return
      }
    }

    // 验证封面图片
    if (!submitData.hero_cover || !submitData.hero_cover.trim()) {
      alert('请填写封面图片URL')
      return
    }

    // 移除空字段
    if (!submitData.rating) {
      delete submitData.rating
    }

    submitting.value = true

    // 提交数据
    const token = localStorage.getItem('access_token')
    if (!token) {
      alert('请先登录')
      router.push('/login')
      return
    }

    // 如果书籍类型有文件，使用FormData上传
    if (formData.value.resource_type === 'book' && bookFile.value) {
      const formDataToSend = new FormData()
      
      // 添加基本字段
      Object.keys(submitData).forEach(key => {
        if (key !== 'content' && key !== 'categories') {
          formDataToSend.append(key, submitData[key])
        }
      })
      
      // 添加分类
      submitData.categories.forEach(catId => {
        formDataToSend.append('categories', catId)
      })
      
      // 添加内容字段
      if (submitData.content) {
        Object.keys(submitData.content).forEach(key => {
          if (key !== 'book_file') {
            formDataToSend.append(`content.${key}`, submitData.content[key])
          }
        })
        // 添加书籍文件
        formDataToSend.append('content.book_file', bookFile.value)
      }
      
      await axios.post(
        `${API_BASE_URL}/resources/submit/`,
        formDataToSend,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      )
    } else {
      // 其他类型使用JSON格式
      await axios.post(
        `${API_BASE_URL}/resources/submit/`,
        submitData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      )
    }

    alert('资源投稿成功！等待管理员审核')
    router.push('/resources')

  } catch (error) {
    console.error('投稿失败:', error)
    if (error.response?.data) {
      const errorData = error.response.data
      let errorMsg = '投稿失败：'
      if (typeof errorData === 'string') {
        errorMsg += errorData
      } else if (errorData.detail) {
        errorMsg += errorData.detail
      } else if (errorData.content) {
        errorMsg += JSON.stringify(errorData.content)
      } else {
        errorMsg += JSON.stringify(errorData)
      }
      alert(errorMsg)
    } else {
      alert('投稿失败，请检查网络连接或稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

// 取消投稿
const handleCancel = () => {
  if (confirm('确定要取消投稿吗？未保存的内容将丢失。')) {
    router.back()
  }
}

// 资源类型元数据（针对用户投稿的友好提示）
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

// 监听文章输入模式变化，当切换到手动输入时，将自动抓取的内容同步到 body_markdown
watch(articleInputMode, (newMode, oldMode) => {
  // 当从 URL 模式切换到手动输入模式时
  if (newMode === 'manual' && oldMode === 'url') {
    // 如果 body_html 有内容但 body_markdown 为空，将 body_html 复制到 body_markdown
    if (formData.value.content.body_html && 
        formData.value.content.body_html.trim() && 
        (!formData.value.content.body_markdown || !formData.value.content.body_markdown.trim())) {
      formData.value.content.body_markdown = formData.value.content.body_html
    }
    // 如果 body_format 未设置，设置为 html
    if (!formData.value.content.body_format && formData.value.content.body_html) {
      formData.value.content.body_format = 'html'
    }
  }
})

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.submit-resource-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 30%, #93c5fd 60%, #bfdbfe 100%);
  position: relative;
  padding: 40px 20px;
  box-sizing: border-box;
}

.submit-resource-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(99, 102, 241, 0.1) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.submit-resource-page > * {
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2rem;
  color: #1f2937;
  margin-bottom: 8px;
}

.subtitle {
  color: #6b7280;
  font-size: 1rem;
}

.submit-form-container {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.form-section {
  margin-bottom: 32px;
}

.form-section h2 {
  font-size: 1.25rem;
  color: #1f2937;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.required {
  color: #ef4444;
}

.form-group input[type="text"],
.form-group input[type="url"],
.form-group input[type="number"],
.form-group select,
.form-group textarea {
  width: 100%;
  max-width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-row .form-group {
  min-width: 0; /* 防止grid子元素溢出 */
  display: flex;
  flex-direction: column;
}

.form-row .form-group input,
.form-row .form-group select {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.form-hint {
  font-size: 0.85rem;
  color: #6b7280;
  margin-top: 4px;
}

/* 资源类型说明样式 */
.resource-type-hint {
  padding: 12px 16px;
  border: 1px solid #dbeafe;
  border-radius: 8px;
  background: #f8fbff;
  margin-bottom: 20px;
  margin-top: 10px;
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

.resource-type-hint .hint-title i {
  font-size: 18px;
  margin-top: 2px;
}

.resource-type-hint .hint-title strong {
  font-size: 14px;
  color: #1e3a8a;
  display: block;
  margin-bottom: 4px;
}

.resource-type-hint .hint-title p {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
}

.url-input-group {
  display: flex;
  gap: 8px;
}

.url-input-group input {
  flex: 1;
}

.fetch-btn {
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.fetch-btn:hover:not(:disabled) {
  background: #2563eb;
}

.fetch-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 已选择的分类标签 */
.selected-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  min-height: 40px;
  padding: 8px;
  background: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.category-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.category-tag i {
  font-size: 0.85rem;
}

.remove-tag-btn {
  background: rgba(255, 255, 255, 0.3);
  border: none;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
  margin-left: 4px;
  transition: background 0.2s;
}

.remove-tag-btn:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 分类下拉框 */
.category-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.category-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.category-select option:disabled {
  color: #9ca3af;
  font-style: italic;
}

.radio-group {
  display: flex;
  gap: 24px;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: normal;
  margin: 0;
}

.radio-group input[type="radio"] {
  width: 18px;
  height: 18px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn,
.submit-btn {
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 抓取失败提示 */
.fetch-failed-notice {
  margin-top: 12px;
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
}

.error-text {
  color: #dc2626;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.request-admin-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.request-admin-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3);
}

/* 申请模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.request-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
}

.request-form {
  padding: 30px;
}

.request-form .form-group {
  margin-bottom: 20px;
}

.request-form .form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .request-form .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

