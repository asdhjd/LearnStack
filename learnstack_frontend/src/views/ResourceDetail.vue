<template>
  <div class="resource-detail-page" :class="{ 'has-document': isDocument }">
    <div class="resource-hero" v-if="resource">
      <div class="hero-meta">
        <router-link class="breadcrumb" to="/resources">
          ← 返回资源库
        </router-link>
        <div class="hero-tags">
          <span class="type-tag">{{ resourceTypeLabel }}</span>
          <span v-if="resource.target_audience_display || resource.target_audience" class="audience-tag">
            {{ resource.target_audience_display || resource.target_audience }}
          </span>
        </div>
        <h1>{{ resource.title }}</h1>
        <p class="description">
          {{ resource.description || '该资源暂未提供简介。' }}
        </p>
        <div class="hero-footer">
          <div class="meta">
            <span>创建时间：{{ formattedDate }}</span>
            <span>评分：{{ resource.rating }}/5</span>
          </div>
          <div class="categories">
            <span
              v-for="category in resource.categories_display"
              :key="category.id"
              class="category-chip"
            >
              <img 
                v-if="category.icon_image_url"
                :src="category.icon_image_url" 
                :alt="category.name"
                class="category-chip-icon"
              />
              <span v-else class="category-chip-placeholder">{{ category.name.charAt(0) }}</span>
              {{ category.name }}
            </span>
          </div>
        </div>
      </div>
      <div class="hero-cover" v-if="resource.hero_cover">
        <img 
          :src="resource.hero_cover" 
          :alt="resource.title"
          :crossorigin="getImageCorsAttribute(resource.hero_cover)"
          :referrerpolicy="getImageReferrerPolicy(resource.hero_cover)"
          @error="handleImageError"
          @load="handleImageLoad"
        />
      </div>
    </div>

    <div v-if="loading" class="state-card">正在加载资源内容…</div>
    <div v-else-if="error" class="state-card error">
      {{ error }}
      <button @click="fetchResource">重试</button>
    </div>

    <div v-if="resource" class="resource-body">
      <main class="main-content">
        <!-- 书籍 -->
        <section v-if="isBook" class="content-card">
          <h2>书籍简介</h2>
          <div v-html="primaryHtml" class="rich-text" />
          <div class="download-actions">
            <!-- 方式1：有上传文件，从服务器下载 -->
            <button
              v-if="resource.content && resource.content.book_file_url"
              @click="handleBookDownload"
              class="primary-btn"
            >
              下载书籍
            </button>
            <!-- 方式2：没有上传文件，但有下载链接，跳转到外部链接 -->
            <a
              v-else-if="resource.content && resource.content.download_url"
              :href="resource.content.download_url"
              target="_blank"
              rel="noopener"
              class="primary-btn"
            >
              下载书籍
            </a>
            <!-- 其他情况：显示资源链接或提示 -->
            <a
              v-else-if="resource.url"
              :href="resource.url"
              target="_blank"
              rel="noopener"
              class="ghost-btn"
            >
              查看资源链接
            </a>
            <p v-else class="no-download-hint">该资源暂无下载链接</p>
          </div>
        </section>

        <!-- 课程（包含视频播放） -->
        <section v-else-if="isCourse" class="content-card course-card">
          <h2>课程内容</h2>
          
          <!-- 课程主体：播放器 + 章节列表 -->
          <div class="course-main-layout">
            <!-- 左侧：视频播放器 -->
            <div class="course-video-section">
              <div v-if="currentVideoUrl" class="video-wrapper">
                <iframe
                  :key="currentVideoUrl"
                  :src="currentVideoUrl"
                  title="课程视频"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                  referrerpolicy="strict-origin-when-cross-origin"
                />
              </div>
              <div v-else class="video-placeholder">
                <i class="fas fa-video"></i>
                <p>暂无视频</p>
              </div>
            </div>
            
            <!-- 右侧：课程章节列表 -->
            <div v-if="sections.length" class="course-sections-sidebar">
              <h3 class="sections-title">
                <i class="fas fa-list"></i> 课程章节
                <span class="section-count">({{ sections.length }})</span>
              </h3>
              <div class="sections-list">
                <div
                  v-for="(section, index) in sections"
                  :key="section.id || section.title || index"
                  class="section-item-compact"
                  :class="{ 'active': currentSectionIndex === index, 'has-video': getSectionVideoUrl(section) }"
                  @click="getSectionVideoUrl(section) ? playSectionVideo(index) : null"
                >
                  <div class="section-number">{{ index + 1 }}</div>
                  <div class="section-content">
                    <div class="section-title-row">
                      <h4 class="section-title">{{ section.title }}</h4>
                      <button 
                        v-if="getSectionVideoUrl(section)" 
                        class="play-icon-btn"
                        @click.stop="playSectionVideo(index)"
                        :class="{ 'playing': currentSectionIndex === index }"
                        :title="currentSectionIndex === index ? '正在播放' : '播放此章节'"
                      >
                        <i class="fas" :class="currentSectionIndex === index ? 'fa-pause' : 'fa-play'"></i>
                      </button>
                    </div>
                    <p v-if="section.summary" class="section-summary">{{ section.summary }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 课程介绍文本（在播放器和章节下方） -->
          <div v-if="primaryHtml" class="course-intro">
            <h3>课程介绍</h3>
            <div class="rich-text" v-html="primaryHtml" />
          </div>
          
          <!-- 空状态提示 -->
          <p v-if="!currentVideoUrl && !sections.length && !primaryHtml" class="muted">
            该课程正在整理中。
          </p>
        </section>

        <!-- 文档 -->
        <section v-else-if="isDocument" class="content-card document-section">
          <h2>文档内容</h2>
          <div class="document-layout">
            <!-- 左侧：文档目录 -->
            <aside
              v-if="documentToc.length > 0"
              class="document-toc-sidebar"
            >
              <nav class="document-toc">
                <h3 class="toc-title">
                  <i class="fas fa-list"></i> 文档目录
                </h3>
                <ul class="toc-list">
                  <li
                    v-for="item in documentToc"
                    :key="item.id || item.title"
                    :class="['toc-item', `toc-level-${item.level || 1}`]"
                  >
                    <a
                      v-if="item.id"
                      href="#"
                      @click.prevent="scrollToSection(item.id)"
                      class="toc-link"
                    >
                      {{ item.title }}
                    </a>
                    <span v-else class="toc-text">{{ item.title }}</span>
                    <!-- 递归显示子目录 -->
                    <ul v-if="item.children && item.children.length > 0" class="toc-children">
                      <li
                        v-for="child in item.children"
                        :key="child.id || child.title"
                        :class="['toc-item', `toc-level-${child.level || 2}`]"
                      >
                        <a
                          v-if="child.id"
                          href="#"
                          @click.prevent="scrollToSection(child.id)"
                          class="toc-link"
                        >
                          {{ child.title }}
                        </a>
                        <span v-else class="toc-text">{{ child.title }}</span>
                      </li>
                    </ul>
                  </li>
                </ul>
              </nav>
            </aside>

            <!-- 右侧：文档内容 -->
            <div class="document-content-wrapper">
              <div
                v-if="documentHtml"
                class="rich-text document-content"
                ref="documentContent"
                v-html="documentHtml"
              />
              <div v-else-if="embedUrl" class="document-embed-wrapper">
                <!-- 使用容器裁剪来只显示中间部分（隐藏导航栏和页脚） -->
                <div
                  v-if="iframeClipConfig"
                  class="iframe-clip-container"
                  :style="{
                    height: iframeClipConfig.containerHeight || '800px'
                  }"
                >
                  <iframe
                    :src="embedUrl"
                    title="嵌入文档"
                    frameborder="0"
                    loading="lazy"
                    sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                    class="document-embed-iframe"
                    :style="{
                      marginTop: iframeClipConfig.marginTop || '0',
                      height: iframeClipConfig.iframeHeight || '100%',
                      width: iframeClipConfig.iframeWidth || '100%'
                    }"
                  />
                </div>
                <!-- 默认全屏显示（推荐：保持完整文档功能） -->
                <iframe
                  v-else
                  :src="embedUrl"
                  title="嵌入文档"
                  frameborder="0"
                  loading="lazy"
                  sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                  class="document-embed-iframe"
                />
              </div>
              <p v-else class="muted">
                暂无文档内容，请稍后再试。
              </p>
            </div>
          </div>
        </section>

        <!-- 项目 -->
        <section v-else-if="isProject" class="content-card article-section">
          <h2>项目介绍</h2>
          <div class="article-layout">
            <!-- 左侧：项目目录 -->
            <aside
              v-if="projectToc.length > 0"
              class="article-toc-sidebar"
            >
              <nav class="article-toc">
                <h3 class="toc-title">
                  <i class="fas fa-list"></i> 项目目录
                </h3>
                <ul class="toc-list project-toc-list">
                  <li
                    v-for="item in projectToc"
                    :key="item.id || item.title"
                    :class="['toc-item', `toc-level-${item.level || 1}`]"
                  >
                    <a
                      v-if="item.id"
                      href="#"
                      @click.prevent="scrollToProjectSection(item.id)"
                      class="toc-link"
                    >
                      {{ item.title }}
                    </a>
                    <span v-else class="toc-text">{{ item.title }}</span>
                    <!-- 递归显示子目录 -->
                    <ul v-if="item.children && item.children.length > 0" class="toc-children">
                      <li
                        v-for="child in item.children"
                        :key="child.id || child.title"
                        :class="['toc-item', `toc-level-${child.level || 2}`]"
                      >
                        <a
                          v-if="child.id"
                          href="#"
                          @click.prevent="scrollToProjectSection(child.id)"
                          class="toc-link"
                        >
                          {{ child.title }}
                        </a>
                        <span v-else class="toc-text">{{ child.title }}</span>
                      </li>
                    </ul>
                  </li>
                </ul>
              </nav>
            </aside>

            <!-- 右侧：项目内容 -->
            <div class="article-content-wrapper">
              <div
                v-if="primaryHtml"
                class="rich-text article-content"
                ref="projectContent"
                v-html="primaryHtml"
              />
              <p v-else class="muted">暂无详细的项目介绍。</p>
            </div>
          </div>
          <div class="download-actions">
            <a
              v-if="downloadUrl"
              :href="downloadUrl"
              target="_blank"
              rel="noopener"
              class="primary-btn"
            >
              下载项目资源
            </a>
            <a
              v-else
              :href="resource.url"
              target="_blank"
              rel="noopener"
              class="ghost-btn"
            >
              查看项目链接
            </a>
          </div>
        </section>

        <!-- 工具 -->
        <section v-else-if="isTool" class="content-card article-section">
          <h2>工具说明</h2>
          <div class="article-layout">
            <!-- 左侧：工具目录 -->
            <aside
              v-if="toolToc.length > 0"
              class="article-toc-sidebar"
            >
              <nav class="article-toc">
                <h3 class="toc-title">
                  <i class="fas fa-list"></i> 工具目录
                </h3>
                <ul class="toc-list tool-toc-list">
                  <li
                    v-for="item in toolToc"
                    :key="item.id || item.title"
                    :class="['toc-item', `toc-level-${item.level || 1}`]"
                  >
                    <a
                      v-if="item.id"
                      href="#"
                      @click.prevent="scrollToToolSection(item.id)"
                      class="toc-link"
                    >
                      {{ item.title }}
                    </a>
                    <span v-else class="toc-text">{{ item.title }}</span>
                    <!-- 递归显示子目录 -->
                    <ul v-if="item.children && item.children.length > 0" class="toc-children">
                      <li
                        v-for="child in item.children"
                        :key="child.id || child.title"
                        :class="['toc-item', `toc-level-${child.level || 2}`]"
                      >
                        <a
                          v-if="child.id"
                          href="#"
                          @click.prevent="scrollToToolSection(child.id)"
                          class="toc-link"
                        >
                          {{ child.title }}
                        </a>
                        <span v-else class="toc-text">{{ child.title }}</span>
                      </li>
                    </ul>
                  </li>
                </ul>
              </nav>
            </aside>

            <!-- 右侧：工具内容 -->
            <div class="article-content-wrapper">
              <div
                v-if="primaryHtml"
                class="rich-text article-content"
                ref="toolContent"
                v-html="primaryHtml"
              />
              <p v-else class="muted">暂未提供工具使用说明。</p>
            </div>
          </div>
          <div class="download-actions">
            <a
              v-if="downloadUrl"
              :href="downloadUrl"
              target="_blank"
              rel="noopener"
              class="primary-btn"
            >
              下载工具
            </a>
            <a
              v-else
              :href="resource.url"
              target="_blank"
              rel="noopener"
              class="ghost-btn"
            >
              访问外部站点
            </a>
          </div>
        </section>

        <!-- 文章 -->
        <section v-else-if="isArticle" class="content-card article-section">
          <h2>正文内容</h2>
          <div class="article-layout">
            <!-- 左侧：文章目录 -->
            <aside
              v-if="articleToc.length > 0"
              class="article-toc-sidebar"
            >
              <nav class="article-toc">
                <h3 class="toc-title">
                  <i class="fas fa-list"></i> 文章目录
                </h3>
                <ul class="toc-list">
                  <TocItem
                    v-for="item in articleToc"
                    :key="item.id || item.title"
                    :item="item"
                    :scroll-fn="scrollToArticleSection"
                  />
                </ul>
              </nav>
            </aside>

            <!-- 右侧：文章内容 -->
            <div class="article-content-wrapper">
              <div
                v-if="primaryHtml"
                class="rich-text article-content"
                ref="articleContent"
                v-html="primaryHtml"
              />
              <p v-else class="muted">
                暂无正文内容，先阅读资源描述或外部链接。
              </p>
            </div>
          </div>
        </section>

        <section v-if="additionalLinks.length" class="content-card">
          <h2>相关链接</h2>
          <ul class="link-list">
            <li v-for="(link, idx) in additionalLinks" :key="idx">
              <a :href="link.url" target="_blank" rel="noopener">
                {{ link.label || link.url }}
              </a>
            </li>
          </ul>
        </section>
      </main>

      <aside class="sidebar" v-if="resource">
        <div class="sidebar-card">
          <h3>资源信息</h3>
          <ul>
            <li><strong>类型：</strong>{{ resourceTypeLabel }}</li>
            <li v-if="resource.target_audience_display || resource.target_audience">
              <strong>适用人群：</strong>{{ resource.target_audience_display || resource.target_audience }}
            </li>
            <li><strong>评分：</strong>{{ resource.rating }}/5</li>
            <li><strong>来源：</strong>{{ contentSourceLabel }}</li>
          </ul>
          
          <!-- 按钮组 -->
          <div class="button-group">
            <!-- 收藏按钮 -->
            <button
              v-if="isAuthenticated"
              @click="handleFavorite"
              :class="['favorite-btn', { 'favorited': isFavorited }]"
            >
              <i :class="isFavorited ? 'fas fa-heart' : 'far fa-heart'"></i>
              {{ isFavorited ? '已收藏' : '收藏' }}
            </button>
            <button
              v-else
              @click="goToLogin"
              class="favorite-btn"
            >
              <i class="far fa-heart"></i>
              登录后收藏
            </button>
            
            <!-- 资源来源按钮 -->
            <a
              v-if="shouldShowSourceButton"
              :href="resource.url"
              target="_blank"
              rel="noopener"
              class="ghost-btn"
            >
              <i class="fas fa-external-link-alt"></i>
              资源来源
            </a>
          </div>
        </div>

        <div class="sidebar-card" v-if="recommendedResources.length > 0">
          <h3>相关推荐</h3>
          <ul class="recommended-resources">
            <li v-for="rec in recommendedResources" :key="rec.id" class="recommended-item">
              <router-link :to="`/resources/${rec.id}`" class="recommended-link">
                <span class="recommended-title">{{ rec.title }}</span>
                <span class="recommended-type">{{ resourceTypeMap[rec.resource_type] || '资源' }}</span>
              </router-link>
            </li>
          </ul>
        </div>
      </aside>
    </div>
    
    <!-- 收藏分类选择模态框 -->
    <div v-if="showCategorySelectModal" class="modal-overlay" @click.self="cancelFavorite">
      <div class="modal-content">
        <h3>选择收藏夹</h3>
        <select v-model="selectedCategoryId" class="category-select">
          <option v-for="cat in favoriteCategories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
        <div class="modal-actions">
          <button @click="confirmFavorite" class="primary-btn">确认</button>
          <button @click="cancelFavorite" class="ghost-btn">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch, defineComponent, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import resourceService from '@/services/resource'
import { 
  getImageCorsAttribute, 
  getImageReferrerPolicy, 
  handleImageError, 
  handleImageLoad 
} from '@/utils/imageUtils'
import { initStudyTimeTracker, cleanupStudyTimeTracker } from '@/utils/studyTimeTracker'
import { recordStudyTime } from '@/services/learningPathService'
import { addFavorite, getFavoriteCategories } from '@/services/favoriteService'
import axios from 'axios'
import { API_BASE_URL } from '@/config/api'

// 递归目录项组件（支持无限层级）
const TocItem = defineComponent({
  name: 'TocItem',
  props: {
    item: {
      type: Object,
      required: true
    },
    scrollFn: {
      type: Function,
      required: true
    }
  },
  setup(props) {
    return () => {
      const { item, scrollFn } = props
      const level = item.level || 1
      
      // 根据层级设置颜色
      const getColor = () => {
        if (level === 1) return '#0f172a'
        if (level === 2) return '#475569'
        return '#64748b'
      }
      
      // 根据层级设置字体大小
      const getFontSize = () => {
        if (level === 1) return '0.95rem'
        if (level === 2) return '0.85rem'
        if (level === 3) return '0.8rem'
        return '0.75rem'
      }
      
      const children = item.children && item.children.length > 0
        ? h('ul', { 
            class: 'toc-children',
            style: {
              listStyle: 'none',
              padding: 0,
              margin: '4px 0 0 0'
            }
          }, 
            item.children.map(child => 
              h(TocItem, { item: child, scrollFn: scrollFn, key: child.id || child.title })
            )
          )
        : null
      
      const linkStyle = {
        display: 'block',
        padding: '6px 8px',
        color: getColor(),
        textDecoration: 'none',
        borderRadius: '4px',
        transition: 'all 0.2s',
        fontSize: getFontSize(),
        lineHeight: '1.5',
        cursor: 'pointer'
      }
      
      const textStyle = {
        display: 'block',
        padding: '6px 8px',
        color: getColor(),
        fontSize: getFontSize(),
        lineHeight: '1.5'
      }
      
      const liStyle = {
        listStyle: 'none',
        margin: 0,
        padding: 0,
        ...(level === 1 ? { fontWeight: '600', marginBottom: '4px' } :
            level === 2 ? { marginLeft: '8px', fontWeight: '500', marginBottom: '2px' } :
            level === 3 ? { marginLeft: '16px', fontWeight: '400', marginBottom: '2px' } :
            { marginLeft: `${(level - 1) * 8}px`, fontWeight: '400', marginBottom: '2px' })
      }
      
      return h('li', { 
        class: ['toc-item', `toc-level-${level}`],
        style: liStyle
      }, [
        item.id
          ? h('a', {
              href: '#',
              class: 'toc-link',
              style: linkStyle,
              onMouseenter: (e) => {
                e.target.style.background = '#f1f5f9'
                e.target.style.color = '#4f46e5'
                e.target.style.paddingLeft = '12px'
              },
              onMouseleave: (e) => {
                e.target.style.background = ''
                e.target.style.color = getColor()
                e.target.style.paddingLeft = '8px'
              },
              onClick: (e) => {
                e.preventDefault()
                scrollFn(item.id)
              }
            }, item.title)
          : h('span', { class: 'toc-text', style: textStyle }, item.title),
        children
      ])
    }
  }
})

const route = useRoute()
const router = useRouter()
const resource = ref(null)
const loading = ref(true)
const error = ref('')
const documentContent = ref(null)
const articleContent = ref(null)
const toolContent = ref(null)
const projectContent = ref(null)
const recommendedResources = ref([])

const resourceTypeMap = {
  book: '书籍',
  course: '课程',
  article: '文章',
  project: '项目',
  tool: '工具',
  document: '文档'
}

const contentSourceMap = {
  original: '站内原创/上传',
  embedded: '外部导入'
}

const fetchResource = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await resourceService.getResourceById(route.params.id)
    resource.value = data
    // 加载推荐资源
    await fetchRecommendedResources(data)
  } catch (err) {
    console.error('加载资源详情失败', err)
    error.value = '加载资源详情失败，请稍后再试。'
  } finally {
    loading.value = false
  }
}

// 获取推荐资源（根据当前资源的分类）
const fetchRecommendedResources = async (currentResource) => {
  if (!currentResource || !currentResource.categories_display || currentResource.categories_display.length === 0) {
    recommendedResources.value = []
    return
  }

  try {
    // 获取所有资源（处理分页）
    const allResources = []
    let nextUrl = `${API_BASE_URL}/resources/`
    
    // 遍历所有页面获取所有资源
    while (nextUrl) {
      const response = await axios.get(nextUrl, {
        params: {
          page_size: 100 // 每页100条，减少请求次数
        }
      })
      
      // 处理分页响应数据
      if (response.data.results) {
        // 分页格式：{ count, next, previous, results }
        allResources.push(...response.data.results)
        nextUrl = response.data.next || null
      } else if (Array.isArray(response.data)) {
        // 兼容非分页格式（向后兼容）
        allResources.push(...response.data)
        nextUrl = null
      } else {
        // 如果既不是分页格式也不是数组，尝试直接使用
        allResources.push(...(response.data || []))
        nextUrl = null
      }
    }
    
    // 获取当前资源的分类ID列表
    const currentCategoryIds = currentResource.categories_display.map(cat => cat.id)
    
    // 筛选出有相同分类的资源，排除当前资源，最多显示5个
    const recommended = allResources
      .filter(res => {
        // 排除当前资源
        if (res.id === currentResource.id) return false
        
        // 检查是否有相同的分类
        if (!res.categories_display || res.categories_display.length === 0) return false
        
        const resCategoryIds = res.categories_display.map(cat => cat.id)
        // 检查是否有交集
        return resCategoryIds.some(id => currentCategoryIds.includes(id))
      })
      .slice(0, 5) // 最多显示5个
    
    recommendedResources.value = recommended
  } catch (err) {
    console.error('获取推荐资源失败:', err)
    recommendedResources.value = []
  }
}

// 实时学习时长显示（用于实时更新显示）
const currentStudyTime = ref(0);

// 初始化学习时长跟踪（仅登录用户）
const initStudyTimeTracking = () => {
  const isAuthenticated = !!localStorage.getItem('access_token');
  if (isAuthenticated) {
    // 创建记录学习时长的回调函数
    const recordCallback = async (hours) => {
      try {
        await recordStudyTime(hours);
        console.log(`自动记录学习时长: ${hours.toFixed(2)}小时`);
        // 记录后重置当前显示时长
        currentStudyTime.value = 0;
      } catch (err) {
        console.error('记录学习时长失败:', err);
        throw err;
      }
    };
    
    // 创建显示更新回调函数（实时显示当前累计时长）
    const displayUpdateCallback = (hours) => {
      currentStudyTime.value = hours;
      // 可以在这里更新UI显示，比如在页面上显示"当前学习时长: X小时"
      console.log(`当前累计学习时长: ${hours.toFixed(2)}小时`);
    };
    
    // 初始化跟踪
    initStudyTimeTracker(recordCallback, displayUpdateCallback);
  }
};

onMounted(async () => {
  // 初始化学习时长跟踪
  initStudyTimeTracking();
  await fetchResource();
  // 加载收藏状态
  await fetchFavoritedResources();
});

// 页面卸载时清理学习时长跟踪
onBeforeUnmount(() => {
  cleanupStudyTimeTracker();
});

watch(
  () => route.params.id,
  async () => {
    if (route.params.id) {
      // 切换资源时，清理旧的跟踪并重新初始化
      cleanupStudyTimeTracker();
      initStudyTimeTracking();
      await fetchResource();
      // 重新加载收藏状态
      await fetchFavoritedResources();
    }
  }
)

const formattedDate = computed(() => {
  if (!resource.value?.created_at) return '未知'
  const date = new Date(resource.value.created_at)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const resourceTypeLabel = computed(
  () => resourceTypeMap[resource.value?.resource_type] || '资源'
)

const contentSourceLabel = computed(
  () => contentSourceMap[resource.value?.content_source] || '站内原创/上传'
)

// 是否应该显示资源来源按钮
const shouldShowSourceButton = computed(() => {
  if (!resource.value) return false
  // 外部导入的资源，如果有url则显示
  if (resource.value.content_source === 'embedded') {
    return !!(resource.value.url && resource.value.url.trim())
  }
  // 站内原创/上传的资源，如果有url则显示
  if (resource.value.content_source === 'original') {
    return !!(resource.value.url && resource.value.url.trim())
  }
  return false
})

// 检查用户是否已登录
const isAuthenticated = computed(() => {
  return !!localStorage.getItem('access_token')
})

// 检查资源是否已收藏
const isFavorited = ref(false)
const favoritedResourceIds = ref(new Set())

// 获取已收藏的资源列表
const fetchFavoritedResources = async () => {
  if (!isAuthenticated.value) return
  
  try {
    const token = localStorage.getItem('access_token')
    if (!token) return
    
    const response = await axios.get(`${API_BASE_URL}/favorites/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // 提取已收藏的资源ID（只处理 resources.Resource 类型）
    const favoritedIds = response.data
      .filter(fav => fav.content_object && fav.content_object.id)
      .map(fav => fav.content_object.id)
    
    favoritedResourceIds.value = new Set(favoritedIds)
    isFavorited.value = favoritedResourceIds.value.has(parseInt(route.params.id))
  } catch (error) {
    console.error('获取已收藏资源失败:', error)
  }
}

// 收藏相关状态
const showCategorySelectModal = ref(false)
const favoriteCategories = ref([])
const selectedCategoryId = ref(null)

// 处理收藏点击
const handleFavorite = async () => {
  try {
    if (!isAuthenticated.value) {
      alert('请先登录！')
      return
    }
    
    // 如果已收藏，提示用户
    if (isFavorited.value) {
      alert('该资源已在您的收藏列表中')
      return
    }
    
    // 加载收藏分类
    favoriteCategories.value = await getFavoriteCategories()
    if (!favoriteCategories.value.length) {
      alert('暂未创建收藏夹，请先在收藏中心创建。')
      return
    }
    const defaultCategory = favoriteCategories.value.find(cat => cat.name === '默认收藏夹')
    selectedCategoryId.value = defaultCategory ? defaultCategory.id : favoriteCategories.value[0].id
    showCategorySelectModal.value = true
  } catch (error) {
    console.error('加载收藏分类失败:', error)
    alert('加载收藏分类失败，请稍后重试。')
  }
}

// 确认收藏
const confirmFavorite = async () => {
  if (!resource.value) return
  try {
    await addFavorite(
      'resources.Resource',
      resource.value.id,
      selectedCategoryId.value
    )
    favoritedResourceIds.value.add(resource.value.id)
    isFavorited.value = true
    alert('收藏成功！')
    showCategorySelectModal.value = false
    selectedCategoryId.value = null
  } catch (error) {
    if (error.response && error.response.status === 400) {
      favoritedResourceIds.value.add(resource.value.id)
      isFavorited.value = true
      alert('已收藏该资源，请勿重复操作！')
    } else if (error.response && error.response.status === 401) {
      alert('登录状态失效，请重新登录！')
    } else {
      alert('收藏失败，请检查网络或登录状态！')
    }
    showCategorySelectModal.value = false
    selectedCategoryId.value = null
  }
}

// 取消收藏操作
const cancelFavorite = () => {
  showCategorySelectModal.value = false
  selectedCategoryId.value = null
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

const isBook = computed(() => resource.value?.resource_type === 'book')
const isCourse = computed(() => resource.value?.resource_type === 'course')
const isArticle = computed(() => resource.value?.resource_type === 'article')
const isProject = computed(() => resource.value?.resource_type === 'project')
const isTool = computed(() => resource.value?.resource_type === 'tool')
const isDocument = computed(() => resource.value?.resource_type === 'document')

const content = computed(() => resource.value?.content || {})

// 注意：封面图片处理函数已从 @/utils/imageUtils 导入
// 以下函数仅用于 HTML 内容中的图片处理（processHtmlImages）

// 格式化纯文本为 HTML
const formatPlainText = (text) => {
  if (!text) return ''
  
  // 如果已经是 HTML，直接返回
  if (text.includes('<') && text.includes('>')) {
    return text
  }
  
  // 按行分割
  const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0)
  const result = []
  let currentList = []
  let inDirectorySection = false // 标记是否在目录部分
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    
    // 识别"目录："标题，标记进入目录部分
    if (line === '目录：' || line === '目录:' || line === '目录') {
      if (currentList.length > 0) {
        result.push(`<ul class="formatted-list">${currentList.join('')}</ul>`)
        currentList = []
      }
      result.push(`<h3 class="chapter-title">目录</h3>`)
      inDirectorySection = true
      continue
    }
    
    // 在目录部分，所有内容都作为列表项显示（保持样式一致）
    if (inDirectorySection) {
      // 识别 URL 并转换为链接
      const urlPattern = /(https?:\/\/[^\s]+)/g
      const lineWithLinks = line.replace(urlPattern, '<a href="$1" target="_blank" rel="noopener">$1</a>')
      currentList.push(`<li>${lineWithLinks}</li>`)
      continue
    }
    
    // 识别章节标题（如 "第一部分"、"Chapter01"、"Appendix A" 等）
    // 注意：在目录部分之外才识别为标题
    const chapterPattern = /^(第[一二三四五六七八九十\d]+[部分]|Chapter\s*\d+|Appendix\s+[A-Z]|附录\s*[A-Z])/i
    if (chapterPattern.test(line)) {
      // 先关闭当前列表
      if (currentList.length > 0) {
        result.push(`<ul class="formatted-list">${currentList.join('')}</ul>`)
        currentList = []
      }
      result.push(`<h3 class="chapter-title">${line}</h3>`)
      inDirectorySection = true
      continue
    }
    
    // 识别项目标题（如 "项目1"、"Project01" 等）
    // 注意：在目录部分之外才识别为标题
    const projectPattern = /^(项目\s*\d+|Project\s*\d+)/i
    if (projectPattern.test(line)) {
      if (currentList.length > 0) {
        result.push(`<ul class="formatted-list">${currentList.join('')}</ul>`)
        currentList = []
      }
      result.push(`<h3 class="project-title">${line}</h3>`)
      inDirectorySection = true
      continue
    }
    
    // 识别普通列表项（数字编号、短横线、项目编号等）
    const listItemPattern = /^(\d+\.|[-•*]|项目\d+)/
    if (listItemPattern.test(line)) {
      // 识别 URL 并转换为链接
      const urlPattern = /(https?:\/\/[^\s]+)/g
      const lineWithLinks = line.replace(urlPattern, '<a href="$1" target="_blank" rel="noopener">$1</a>')
      currentList.push(`<li>${lineWithLinks}</li>`)
      continue
    }
    
    // 识别标签行（统一规则：任何包含冒号且标签长度合理的行）
    // 格式：标签：值 或 标签:值
    if (line.includes('：') || line.includes(':')) {
      const parts = line.split(/[：:]/)
      if (parts.length >= 2) {
        const label = parts[0].trim()
        const value = parts.slice(1).join('：').trim() // 处理值中可能包含冒号的情况
        
        // 判断是否为标签行：
        // 1. 标签长度合理（通常不超过30个字符）
        // 2. 值不为空
        // 3. 不是URL
        // 4. 标签不以纯数字开头（避免误识别章节编号）
        const isLabelLine = label.length > 0 && 
                           label.length < 30 && 
                           value.length > 0 && 
                           !label.match(/^https?:\/\//) && 
                           !value.match(/^https?:\/\//) &&
                           !label.match(/^\d+$/) // 避免纯数字被识别为标签
        
        if (isLabelLine) {
          // 先关闭当前列表
          if (currentList.length > 0) {
            result.push(`<ul class="formatted-list">${currentList.join('')}</ul>`)
            currentList = []
          }
          inDirectorySection = false // 标签行会结束目录部分
          
          // 识别 URL 并转换为链接
          const urlPattern = /(https?:\/\/[^\s]+)/g
          const valueWithLinks = value.replace(urlPattern, '<a href="$1" target="_blank" rel="noopener">$1</a>')
          // 统一使用中文冒号显示
          const displayLabel = label.endsWith('：') || label.endsWith(':') ? label : `${label}：`
          result.push(`<p class="info-item"><strong>${displayLabel}</strong>${valueWithLinks}</p>`)
          continue
        }
      }
    }
    
    // 普通段落
    // 先关闭当前列表
    if (currentList.length > 0) {
      result.push(`<ul class="formatted-list">${currentList.join('')}</ul>`)
      currentList = []
    }
    inDirectorySection = false // 普通段落会结束目录部分
    
    // 识别 URL 并转换为链接
    const urlPattern = /(https?:\/\/[^\s]+)/g
    const lineWithLinks = line.replace(urlPattern, '<a href="$1" target="_blank" rel="noopener">$1</a>')
    result.push(`<p>${lineWithLinks}</p>`)
  }
  
  // 处理剩余的列表项
  if (currentList.length > 0) {
    result.push(`<ul class="formatted-list">${currentList.join('')}</ul>`)
  }
  
  return result.join('')
}

// HTML 转义函数
const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// Markdown 转 HTML 转换函数
const markdownToHtml = (markdown) => {
  if (!markdown) return ''
  
  // 统一换行符：将 \r\n 和 \r 转换为 \n
  let normalizedMarkdown = markdown.replace(/\r\n/g, '\n').replace(/\r/g, '\n')
  
  // 先标记代码块，避免在代码块内处理其他 Markdown 语法
  const codeBlockPlaceholders = []
  let codeBlockIndex = 0
  let processedText = normalizedMarkdown.replace(/```(\w+)?\s*\n?([\s\S]*?)```/g, (match, lang, code) => {
    const placeholder = `__CODE_BLOCK_${codeBlockIndex}__`
    codeBlockPlaceholders.push({
      placeholder,
      lang: lang || 'text',
      code: code.trim()
    })
    codeBlockIndex++
    return `\n${placeholder}\n`
  })
  
  // 处理行内代码（`code`），但不在代码块占位符内
  processedText = processedText.replace(/`([^`]+)`/g, '<code>$1</code>')
  
  // 按行处理
  const lines = processedText.split('\n')
  const result = []
  let currentList = null
  let listType = null // 'ul' 或 'ol'
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i]
    
    // 检查是否是代码块占位符
    const codeBlockMatch = line.match(/__CODE_BLOCK_(\d+)__/)
    if (codeBlockMatch) {
      // 关闭当前列表
      if (currentList) {
        result.push(`<${listType}>${currentList.join('')}</${listType}>`)
        currentList = null
        listType = null
      }
      
      const index = parseInt(codeBlockMatch[1])
      const codeBlock = codeBlockPlaceholders[index]
      if (codeBlock) {
        const escapedCode = escapeHtml(codeBlock.code)
        result.push(`<pre><code class="language-${codeBlock.lang}">${escapedCode}</code></pre>`)
      }
      continue
    }
    
    // 处理标题（# ## ### 等）
    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/)
    if (headingMatch) {
      // 关闭当前列表
      if (currentList) {
        result.push(`<${listType}>${currentList.join('')}</${listType}>`)
        currentList = null
        listType = null
      }
      
      const level = headingMatch[1].length
      const title = headingMatch[2].trim()
      // 处理标题中的 Markdown 格式
      let processedTitle = processInlineMarkdown(title)
      result.push(`<h${level}>${processedTitle}</h${level}>`)
      continue
    }
    
    // 处理无序列表（- * +）
    const ulMatch = line.match(/^[-*+]\s+(.+)$/)
    if (ulMatch) {
      if (listType !== 'ul') {
        if (currentList) {
          result.push(`<${listType}>${currentList.join('')}</${listType}>`)
        }
        currentList = []
        listType = 'ul'
      }
      const content = processInlineMarkdown(ulMatch[1])
      currentList.push(`<li>${content}</li>`)
      continue
    }
    
    // 处理有序列表（1. 2. 等）
    const olMatch = line.match(/^(\d+)\.\s+(.+)$/)
    if (olMatch) {
      if (listType !== 'ol') {
        if (currentList) {
          result.push(`<${listType}>${currentList.join('')}</${listType}>`)
        }
        currentList = []
        listType = 'ol'
      }
      const content = processInlineMarkdown(olMatch[2])
      currentList.push(`<li>${content}</li>`)
      continue
    }
    
    // 空行：关闭列表，开始新段落
    if (line.trim() === '') {
      if (currentList) {
        result.push(`<${listType}>${currentList.join('')}</${listType}>`)
        currentList = null
        listType = null
      }
      continue
    }
    
    // 普通段落
    if (currentList) {
      result.push(`<${listType}>${currentList.join('')}</${listType}>`)
      currentList = null
      listType = null
    }
    
    const processedLine = processInlineMarkdown(line.trim())
    result.push(`<p>${processedLine}</p>`)
  }
  
  // 处理剩余的列表
  if (currentList) {
    result.push(`<${listType}>${currentList.join('')}</${listType}>`)
  }
  
  return result.join('\n')
}

// 处理行内 Markdown 格式（粗体、斜体、链接、图片）
const processInlineMarkdown = (text) => {
  if (!text) return ''
  
  let processed = text
  
  // 处理图片（![alt](url)）
  processed = processed.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')
  
  // 处理链接（[text](url)）
  processed = processed.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
  
  // 处理粗体（**text** 或 __text__）
  processed = processed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  processed = processed.replace(/__(.+?)__/g, '<strong>$1</strong>')
  
  // 处理斜体（*text* 或 _text_），但要避免与粗体冲突
  processed = processed.replace(/(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
  processed = processed.replace(/(?<!_)_(?!_)([^_]+?)(?<!_)_(?!_)/g, '<em>$1</em>')
  
  // 处理行内代码（`code`）
  processed = processed.replace(/`([^`]+)`/g, '<code>$1</code>')
  
  return processed
}

// 智能检测内容格式
const detectContentFormat = (content) => {
  if (!content || !content.trim()) return 'plaintext'
  
  // 统一换行符，便于检测
  const normalized = content.replace(/\r\n/g, '\n').replace(/\r/g, '\n')
  const trimmed = normalized.trim()
  
  // 检测是否是 HTML（包含 HTML 标签）
  if (trimmed.includes('<') && trimmed.includes('>')) {
    // 检查是否包含常见的 HTML 标签
    const htmlTagPattern = /<\/?(?:div|p|span|h[1-6]|ul|ol|li|a|img|strong|em|code|pre|br|hr|table|tr|td|th|thead|tbody|section|article|header|footer|nav|aside|blockquote)[\s>]/i
    if (htmlTagPattern.test(trimmed)) {
      return 'html'
    }
  }
  
  // 检测是否是 Markdown（包含 Markdown 语法）
  // 优先检测标题（最常见的 Markdown 语法）
  if (/^#{1,6}\s+.+$/m.test(trimmed)) {
    return 'markdown'
  }
  
  const markdownPatterns = [
    /```[\s\S]*?```/,            // 代码块
    /\[.+\]\(.+\)/,              // 链接
    /!\[.+\]\(.+\)/,             // 图片
    /^\s*[-*+]\s+.+$/m,          // 无序列表
    /^\s*\d+\.\s+.+$/m,          // 有序列表
    /\*\*.*?\*\*/,               // 粗体
    /__.*?__/,                   // 粗体
  ]
  
  const hasMarkdown = markdownPatterns.some(pattern => pattern.test(trimmed))
  if (hasMarkdown) {
    return 'markdown'
  }
  
  return 'plaintext'
}

const primaryHtml = computed(() => {
  // 优先使用 body_html，其次使用 body_markdown
  const raw = content.value.body_html || content.value.body_markdown || ''
  if (!raw) return ''
  
  let processedHtml = ''
  
  // 智能检测和处理内容格式
  // 无论用户选择什么格式，都先智能检测实际格式，确保正确显示
  const detectedFormat = detectContentFormat(raw)
  
  // 根据检测到的格式进行处理
  if (detectedFormat === 'html') {
    // 检测到是 HTML，直接使用
    processedHtml = raw
  } else if (detectedFormat === 'markdown') {
    // 检测到是 Markdown，转换为 HTML
    processedHtml = markdownToHtml(raw)
  } else {
    // 检测到是纯文本，格式化处理
    processedHtml = formatPlainText(raw)
  }
  
  // 先清理无用链接
  let cleanedHtml = cleanUselessLinks(processedHtml)
  
  // 移除固定宽度样式（防止内容撑大容器）
  cleanedHtml = removeFixedWidths(cleanedHtml)
  
  // 处理代码块（确保代码块结构完整）
  cleanedHtml = processCodeBlocks(cleanedHtml)
  
  // 再次移除固定宽度样式（代码块处理可能会重新引入固定宽度）
  cleanedHtml = removeFixedWidths(cleanedHtml)
  
  // 再处理图片路径
  const resourceUrl = resource.value?.url || ''
  return processHtmlImages(cleanedHtml, resourceUrl)
})

// HTML 清理配置 - 通用的清理规则
const HTML_CLEANUP_CONFIG = {
  // 无用链接的匹配规则
  uselessLinkPatterns: [
    // URL 模式（部分匹配）
    { type: 'url', pattern: /so\.csdn\.net\/so\/search/i },
    { type: 'url', pattern: /csdn\.net\/so/i },
    // 锚点链接
    { type: 'url', pattern: /^#/ },
    // 相对路径（但保留协议相对路径 //）
    { type: 'url', pattern: /^\/[^/]/ },
    // JavaScript 链接
    { type: 'url', pattern: /^javascript:/i },
    { type: 'url', pattern: /^void\(0\)/i },
    // 空链接
    { type: 'url', pattern: /^$/ },
    { type: 'url', pattern: /^#$/ }
  ],
  
  // 短文本链接规则（文本长度 + URL 模式）
  shortLinkRules: [
    { maxLength: 8, urlPattern: /so\.csdn\.net|csdn\.net\/so/i }
  ],
  
  // 需要移除的元素选择器（紧跟在标题后面）
  elementsAfterHeadings: [
    'hr',
    '[data-lake-card="hr"]',
    '[data-card-type="block"][data-lake-card="hr"]',
    '[class*="divider"]',
    '[class*="separator"]'
  ],
  
  // 图片懒加载属性（按优先级排序）
  imageLazyAttrs: [
    'data-raw-src',  // 阿里云等
    'data-src',
    'data-original',
    'data-lazy-src',
    'data-lazy',
    'data-url',
    'data-img',
    'data-srcset',  // CSDN 等可能使用
    'data-actualsrc',  // CSDN 实际图片源
    'data-actualsrcset'  // CSDN 实际图片源集合
  ],
  
  // 需要添加跨域属性的图片域名模式（仅对已知支持 CORS 的 CDN 设置）
  // 注意：大多数图片服务器不支持 CORS，设置 crossorigin 会导致加载失败
  imageCorsDomains: [
    // 已知支持 CORS 的 CDN
    { pattern: /csdnimg\.cn|csdn\.net/i, crossorigin: 'anonymous', referrerpolicy: 'no-referrer' },
    { pattern: /aliyun\.com|aliyuncs\.com|alicdn\.com/i, crossorigin: 'anonymous', referrerpolicy: 'no-referrer' },
    { pattern: /hdslb\.com/i, crossorigin: 'anonymous', referrerpolicy: 'no-referrer' },  // Bilibili CDN
    { pattern: /bilibili\.com/i, crossorigin: 'anonymous', referrerpolicy: 'no-referrer' },
    { pattern: /b23\.tv/i, crossorigin: 'anonymous', referrerpolicy: 'no-referrer' }
  ],
  
  // 不需要跨域属性的域名（这些域名不支持 CORS，设置会导致加载失败）
  noCorsDomains: [
    /17golang\.com/i,
    /github\.com/i,
    /githubusercontent\.com/i,
    /imgur\.com/i,
    /unsplash\.com/i,
    /pexels\.com/i
    // 可以根据需要添加更多域名
  ],
  
  // 域名推断规则（用于相对路径图片）
  domainInference: [
    { htmlPattern: /csdn\.net/i, domain: 'https://blog.csdn.net' },
    { htmlPattern: /juejin\.cn/i, domain: 'https://juejin.cn' },
    { htmlPattern: /zhihu\.com/i, domain: 'https://www.zhihu.com' },
    { htmlPattern: /developer\.aliyun\.com|aliyun\.com/i, domain: 'https://developer.aliyun.com' }
  ]
}

// 通用的 HTML 清理函数
const cleanHtml = (html) => {
  if (!html) return ''
  
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    
    // 1. 清理无用链接
    const links = doc.querySelectorAll('a')
    links.forEach(link => {
      const href = link.getAttribute('href') || ''
      const linkText = link.textContent?.trim() || ''
      
      // 检查是否匹配无用链接模式
      let isUseless = HTML_CLEANUP_CONFIG.uselessLinkPatterns.some(rule => {
        if (rule.type === 'url') {
          return typeof rule.pattern === 'string' 
            ? href.includes(rule.pattern) 
            : rule.pattern.test(href)
        }
        return false
      })
      
      // 检查短文本链接规则
      if (!isUseless) {
        isUseless = HTML_CLEANUP_CONFIG.shortLinkRules.some(rule => {
          return linkText.length < rule.maxLength && rule.urlPattern.test(href)
        })
      }
      
      if (isUseless) {
        const textNode = doc.createTextNode(linkText || '')
        link.parentNode?.replaceChild(textNode, link)
      } else {
        // 保留有效链接，确保在新窗口打开
        if (!link.hasAttribute('target')) {
          link.setAttribute('target', '_blank')
          link.setAttribute('rel', 'noopener noreferrer')
        }
      }
    })
    
    // 2. 移除标题后面的分割线
    const headings = doc.querySelectorAll('h1, h2, h3, h4, h5, h6')
    headings.forEach(heading => {
      HTML_CLEANUP_CONFIG.elementsAfterHeadings.forEach(selector => {
        const elements = doc.querySelectorAll(selector)
        elements.forEach(el => {
          // 检查是否紧跟在标题后面
          if (el.previousElementSibling === heading) {
            el.remove()
          }
        })
      })
    })
    
    return doc.body.innerHTML
  } catch (error) {
    console.error('清理 HTML 失败:', error)
    return html
  }
}

// 保持向后兼容
const cleanUselessLinks = cleanHtml

// 处理 HTML 中的代码块（确保代码块结构完整，只显示代码内容）
// 代码块清理配置 - 通用的清理规则
const CODE_BLOCK_CLEANUP_CONFIG = {
  // 需要提取 pre 的容器选择器（这些容器应该被移除，只保留其中的 pre）
  containersToExtract: [
    '[class*="markdown-code"]',
    '[class*="code-container"]',
    '[class*="code-block-wrapper"]',
    '[class*="code-wrapper"]'
  ],
  
  // 需要移除的元素选择器（通用模式）
  unwantedSelectors: [
    // 行号相关
    '.line-numbers', '.line-number', '.code-line-number',
    '.hljs-ln-numbers', '.hljs-ln-n', '.hljs-ln-line',
    'span[class*="line-number"]', 'span[class*="line-numbers"]',
    // 工具栏和按钮
    '[class*="code-toolbar"]', '[class*="code-opt"]',
    '[class*="copy-btn"]', '[class*="copy-button"]', '[class*="code-copy"]',
    '[class*="toolbar"]', 'button', '.btn',
    // 标题和头部
    '.code-title', '.code-header', '.code-block-header',
    '.code-block-footer', '.code-block-extension-header',
    // 其他装饰性元素
    '.opt-box', '.hide-preCode-box', '.highlight',
    '.highlight-line', '.highlight-line-number',
    '.prism-line-number', '.prism-line-numbers',
    // 图标和 SVG
    'i[class*="copy"]', 'svg[class*="copy"]',
    '[class*="code-language"]', '[class*="code-lang"]',
    '[class*="ai-code"]', '[class*="code-explain"]'
  ],
  
  // 需要移除的文本模式（正则表达式或字符串）
  unwantedTextPatterns: [
    /代码语言[：:]/,
    /^复制$/,
    /AI代码解释/,
    /AI代码/
  ],
  
  // 需要移除的 class 名称模式（部分匹配）
  unwantedClassPatterns: [
    'copy', 'code-language', 'code-lang',
    'ai-code', 'code-explain', 'is-ai-btn',
    'code-toolbar', 'code-opt', 'developer-code-block'
  ],
  
  // 需要移除的标签（如果包含特定 class 或文本）
  unwantedTags: {
    'I': ['copy', 'icon-copy'],
    'SVG': ['copy'],
    'BUTTON': ['copy', 'btn']
  }
}

// 通用的代码块容器处理函数
const extractPreFromContainer = (container, preElement) => {
  if (!preElement) return false
  
  // 如果 pre 在嵌套容器内部，先提取出来
  const nestedContainers = container.querySelectorAll('[class*="code"], [class*="block"]')
  nestedContainers.forEach(nested => {
    if (nested !== container && nested.contains(preElement)) {
      const parent = nested.parentElement
      if (parent) {
        parent.insertBefore(preElement, nested)
        nested.remove()
      }
    }
  })
  
  // 移除容器内的所有非 pre 元素
  CODE_BLOCK_CLEANUP_CONFIG.unwantedSelectors.forEach(selector => {
    const elements = container.querySelectorAll(selector)
    elements.forEach(el => {
      if (el !== preElement && !el.contains(preElement)) {
        el.remove()
      }
    })
  })
  
  // 移除包含特定文本的元素
  const allElements = Array.from(container.querySelectorAll('*'))
  allElements.forEach(el => {
    if (el === preElement || el.closest('pre') === preElement || el.closest('code')) {
      return
    }
    
    const text = (el.textContent || el.innerText || '').trim()
    const className = (el.className || '').toLowerCase()
    
    // 检查文本模式
    if (CODE_BLOCK_CLEANUP_CONFIG.unwantedTextPatterns.some(pattern => {
      return typeof pattern === 'string' ? text.includes(pattern) : pattern.test(text)
    })) {
      if (el.tagName !== 'CODE') {
        el.remove()
        return
      }
    }
    
    // 检查 class 模式
    if (CODE_BLOCK_CLEANUP_CONFIG.unwantedClassPatterns.some(pattern => {
      return className.includes(pattern)
    })) {
      el.remove()
      return
    }
    
    // 检查标签和 class 组合
    const tagName = el.tagName
    if (CODE_BLOCK_CLEANUP_CONFIG.unwantedTags[tagName]) {
      const unwantedClasses = CODE_BLOCK_CLEANUP_CONFIG.unwantedTags[tagName]
      if (unwantedClasses.some(cls => className.includes(cls))) {
        el.remove()
        return
      }
    }
  })
  
  // 用 pre 替换容器
  const parent = container.parentElement
  if (parent) {
    parent.insertBefore(preElement, container)
    container.remove()
    return true
  }
  return false
}

const processCodeBlocks = (html) => {
  if (!html) return ''
  
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    
    // 第一步：处理需要提取 pre 的容器
    CODE_BLOCK_CLEANUP_CONFIG.containersToExtract.forEach(containerSelector => {
      const containers = doc.querySelectorAll(containerSelector)
      containers.forEach(container => {
        const preElement = container.querySelector('pre')
        if (preElement) {
          extractPreFromContainer(container, preElement)
        } else {
          // 如果没有 pre，移除整个容器
          container.remove()
        }
      })
    })
    
    // 第二步：处理所有 pre 标签，清理内部的多余元素
    const preElements = doc.querySelectorAll('pre')
    preElements.forEach(pre => {
      // 提取特殊结构的代码内容（如 hljs-ln-code）
      const codeLines = pre.querySelectorAll('.hljs-ln-code')
      let extractedCodeText = ''
      
      if (codeLines.length > 0) {
        extractedCodeText = Array.from(codeLines)
          .map(line => line.textContent || line.innerText || '')
          .join('\n')
      }
      
      // 移除不需要的元素（使用通用配置）
      CODE_BLOCK_CLEANUP_CONFIG.unwantedSelectors.forEach(selector => {
        const elements = pre.querySelectorAll(selector)
        elements.forEach(el => el.remove())
      })
      
      // 移除包含特定文本的元素
      const allElements = Array.from(pre.querySelectorAll('*'))
      allElements.forEach(el => {
        const text = (el.textContent || el.innerText || '').trim()
        const className = (el.className || '').toLowerCase()
        const tagName = el.tagName
        
        // 跳过 code 元素本身
        if (tagName === 'CODE') return
        
        // 检查文本模式
        if (CODE_BLOCK_CLEANUP_CONFIG.unwantedTextPatterns.some(pattern => {
          return typeof pattern === 'string' ? text.includes(pattern) : pattern.test(text)
        })) {
          el.remove()
          return
        }
        
        // 检查 class 模式
        if (CODE_BLOCK_CLEANUP_CONFIG.unwantedClassPatterns.some(pattern => {
          return className.includes(pattern)
        })) {
          el.remove()
          return
        }
        
        // 检查标签和 class 组合
        if (CODE_BLOCK_CLEANUP_CONFIG.unwantedTags[tagName]) {
          const unwantedClasses = CODE_BLOCK_CLEANUP_CONFIG.unwantedTags[tagName]
          if (unwantedClasses.some(cls => className.includes(cls))) {
            el.remove()
            return
          }
        }
      })
      
      // 移除包含行号的 ul/ol 元素（CSDN 可能在 pre 内添加行号列表）
      // 这些 ul/ol 通常紧跟在 code 元素后面
      const listElements = pre.querySelectorAll('ul, ol')
      listElements.forEach(list => {
        // 检查列表是否只包含数字（行号）
        const listItems = list.querySelectorAll('li')
        if (listItems.length === 0) return
        
        // 检查所有 li 元素是否只包含数字
        let isLineNumbers = true
        for (const li of listItems) {
          const text = (li.textContent || li.innerText || '').trim()
          // 如果 li 内容不是纯数字，或者包含其他内容，则不是行号
          if (!/^\d+$/.test(text)) {
            isLineNumbers = false
            break
          }
        }
        
        // 如果所有 li 都是数字，且数量较多（超过2个），很可能是行号
        if (isLineNumbers && listItems.length > 2) {
          list.remove()
        } else {
          // 进一步检查：如果列表内容整体看起来像行号（连续数字）
          const allText = (list.textContent || list.innerText || '').trim()
          const normalizedText = allText.replace(/\n/g, ' ').replace(/\s+/g, ' ')
          // 检查是否只包含数字和空格
          if (/^(\d+\s*)+$/.test(normalizedText)) {
            const numbers = normalizedText.split(/\s+/).filter(n => n.trim())
            // 如果数字数量较多且是连续递增的，很可能是行号
            if (numbers.length > 2) {
              let isSequential = true
              for (let i = 1; i < numbers.length; i++) {
                const prev = parseInt(numbers[i - 1])
                const curr = parseInt(numbers[i])
                if (isNaN(prev) || isNaN(curr) || curr !== prev + 1) {
                  isSequential = false
                  break
                }
              }
              if (isSequential) {
                list.remove()
              }
            }
          }
        }
      })
      
      // 确保 pre 有 code 子元素
      let codeElement = pre.querySelector('code')
      
      if (!codeElement) {
        // 如果没有 code 元素，创建一个
        codeElement = doc.createElement('code')
        
        // 如果已经提取了代码内容，使用提取的内容
        if (extractedCodeText) {
          codeElement.textContent = extractedCodeText
        } else {
          // 否则将 pre 的内容移动到 code 中（排除已删除的元素）
          while (pre.firstChild) {
            const child = pre.firstChild
            // 跳过非文本节点中的非代码元素
            if (child.nodeType === Node.TEXT_NODE || 
                (child.nodeType === Node.ELEMENT_NODE && 
                 child.tagName !== 'BUTTON' && 
                 !child.classList.contains('line-number') &&
                 !child.classList.contains('copy-btn') &&
                 !child.classList.contains('hljs-ln-numbers') &&
                 !child.classList.contains('hljs-ln-n') &&
                 !child.classList.contains('hljs-ln-code') &&
                 !child.classList.contains('hljs-ln-line') &&
                 !child.classList.contains('opt-box') &&
                 !child.classList.contains('hide-preCode-box') &&
                 !child.classList.contains('highlight') &&
                 !child.classList.contains('highlight-line') &&
                 !child.classList.contains('highlight-line-number') &&
                 !child.classList.contains('code-block-header') &&
                 !child.classList.contains('code-block-footer') &&
                 !child.classList.contains('code-block-extension-header') &&
                 !child.classList.contains('prism-line-number') &&
                 !child.classList.contains('prism-line-numbers') &&
                 !child.className?.includes('line-number') &&
                 !child.className?.includes('line-numbers'))) {
              codeElement.appendChild(child)
            } else {
              pre.removeChild(child)
            }
          }
        }
        pre.appendChild(codeElement)
      } else {
        // 如果已有 code 元素
        // 如果已经提取了代码内容，优先使用提取的内容
        if (extractedCodeText) {
          codeElement.textContent = extractedCodeText
        } else {
          // 否则清理其中的非代码内容（使用通用配置）
          CODE_BLOCK_CLEANUP_CONFIG.unwantedSelectors.forEach(selector => {
            const elements = codeElement.querySelectorAll(selector)
            elements.forEach(el => el.remove())
          })
          
          // 提取纯文本内容（移除所有子元素，只保留文本）
          const codeText = codeElement.textContent || codeElement.innerText || ''
          if (codeText) {
            // 清空 code 元素
            codeElement.innerHTML = ''
            // 设置纯文本内容
            codeElement.textContent = codeText
          }
        }
      }
      
      // 保留代码高亮的 class（如 language-python, language-shell 等）
      // 只保留 language- 相关的 class，移除其他装饰性 class
      const codeClass = codeElement.className || ''
      if (codeClass) {
        // 提取 language-xxx 相关的 class
        const langMatch = codeClass.match(/language-[\w-]+/i)
        if (langMatch) {
          codeElement.className = langMatch[0]
        } else {
          // 如果没有 language-，尝试从其他格式中提取
          // 掘金可能使用 hljs 或其他格式
          const altLangMatch = codeClass.match(/(?:lang|language|hljs)[-_]?(\w+)/i)
          if (altLangMatch) {
            codeElement.className = `language-${altLangMatch[1]}`
          } else {
            // 检查是否有 hljs class（如 hljs javascript）
            const hljsMatch = codeClass.match(/hljs\s+(\w+)/i)
            if (hljsMatch) {
              codeElement.className = `language-${hljsMatch[1]}`
            } else {
              codeElement.className = ''
            }
          }
        }
      }
      
      // 清理 pre 的 class，只保留必要的
      pre.className = 'code-block'
      
      // 移除 pre 上的其他属性（如 data-* 等）
      Array.from(pre.attributes).forEach(attr => {
        if (attr.name !== 'class' && attr.name !== 'style') {
          pre.removeAttribute(attr.name)
        }
      })
      
      // 确保代码块有正确的宽度限制和滚动
      const existingStyle = pre.getAttribute('style') || ''
      // 移除所有 width 相关的样式
      let newStyle = existingStyle
        .replace(/width\s*:\s*[^;]+/gi, '')
        .replace(/max-width\s*:\s*\d+px/gi, '')
        .replace(/min-width\s*:\s*[^;]+/gi, '')
        .replace(/,\s*,/g, ',')
        .replace(/^,\s*/, '')
        .replace(/,\s*$/, '')
        .trim()
      
      // 设置正确的样式：宽度限制 + 横向滚动
      pre.setAttribute('style', `width: 100%; max-width: 100%; overflow-x: auto; box-sizing: border-box; ${newStyle}`.trim())
    })
    
    // 处理单独的 code 标签（不在 pre 中的内联代码）
    const codeElements = doc.querySelectorAll('code')
    codeElements.forEach(code => {
      // 如果 code 不在 pre 中，确保它有合适的样式
      if (code.parentElement?.tagName !== 'PRE') {
        // 内联代码，移除装饰性 class
        const codeClass = code.className || ''
        if (codeClass && codeClass.includes('language-')) {
          // 保留 language- class（用于样式）
          const langMatch = codeClass.match(/language-[\w-]+/i)
          if (langMatch) {
            code.className = langMatch[0]
          }
        } else {
          code.className = 'inline-code'
        }
      }
    })
    
    return doc.body.innerHTML
  } catch (error) {
    console.error('处理代码块失败:', error)
    return html
  }
}

// 处理 HTML 中的图片路径（修复相对路径、懒加载等问题）
const processHtmlImages = (html, baseUrl = '') => {
  if (!html) return ''
  
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    
    // 提取基础 URL
    let baseOrigin = ''
    if (baseUrl) {
      try {
        const url = new URL(baseUrl)
        baseOrigin = `${url.protocol}//${url.host}`
      } catch (err) {
        console.warn('解析 base href 失败:', err)
        const linkMatch = html.match(/https?:\/\/[^/]+/)
        if (linkMatch) {
          baseOrigin = linkMatch[0]
        }
      }
    }
    
    // 处理所有图片
    const images = doc.querySelectorAll('img')
    images.forEach(img => {
      // 收集所有可能的图片源（按优先级）
      const possibleSources = []
      
      // 1. 优先检查懒加载属性
      for (const attr of HTML_CLEANUP_CONFIG.imageLazyAttrs) {
        const value = img.getAttribute(attr)
        if (value && value.trim() && !value.startsWith('data:')) {
          // 处理 srcset 格式（如 "url1 1x, url2 2x"）
          if (attr.includes('srcset')) {
            const urls = value.split(',').map(s => s.trim().split(/\s+/)[0]).filter(Boolean)
            possibleSources.push(...urls)
          } else {
            possibleSources.push(value)
          }
        }
      }
      
      // 2. 检查 srcset 属性
      const srcset = img.getAttribute('srcset')
      if (srcset && !srcset.startsWith('data:')) {
        const urls = srcset.split(',').map(s => s.trim().split(/\s+/)[0]).filter(Boolean)
        possibleSources.push(...urls)
      }
      
      // 3. 检查 src 属性
      const srcAttr = img.getAttribute('src')
      if (srcAttr && !srcAttr.startsWith('data:')) {
        possibleSources.push(srcAttr)
      }
      
      // 选择最佳图片源（优先选择完整的 HTTP/HTTPS URL）
      let src = ''
      if (possibleSources.length > 0) {
        // 优先选择完整的 URL
        const fullUrl = possibleSources.find(s => s.startsWith('http://') || s.startsWith('https://'))
        if (fullUrl) {
          src = fullUrl
        } else {
          // 否则使用第一个
          src = possibleSources[0]
        }
      }
      
      // 如果仍然没有找到，且 src 是 data URI，尝试从所有属性中查找
      if (!src && srcAttr && srcAttr.startsWith('data:')) {
        // 检查所有 data-* 属性
        Array.from(img.attributes).forEach(attr => {
          if (attr.name.startsWith('data-') && attr.value && !attr.value.startsWith('data:')) {
            const value = attr.value.trim()
            if (value && (value.startsWith('http://') || value.startsWith('https://') || value.startsWith('/'))) {
              src = value
            }
          }
        })
      }
      
      if (!src) {
        console.warn('无法找到图片源:', img.outerHTML.substring(0, 200))
        return
      }
      
      // 设置 src 属性
      img.setAttribute('src', src)
      
      // 清理懒加载属性（保留 srcset 如果它包含有用的信息）
      for (const attr of HTML_CLEANUP_CONFIG.imageLazyAttrs) {
        if (img.hasAttribute(attr) && attr !== 'data-srcset') {
          img.removeAttribute(attr)
        }
      }
      
      // 处理相对路径
      if (src && !src.startsWith('http://') && !src.startsWith('https://') && !src.startsWith('data:')) {
        if (src.startsWith('//')) {
          src = `https:${src}`
        } else if (src.startsWith('/')) {
          if (baseOrigin) {
            src = `${baseOrigin}${src}`
          } else {
            // 使用配置的域名推断规则
            const matchedRule = HTML_CLEANUP_CONFIG.domainInference.find(rule => 
              rule.htmlPattern.test(html)
            )
            if (matchedRule) {
              src = `${matchedRule.domain}${src}`
            }
          }
        } else {
          if (baseOrigin) {
            const basePath = baseUrl.split('/').slice(0, -1).join('/')
            src = `${basePath}/${src}`
          }
        }
        img.setAttribute('src', src)
      }
      
      // 添加跨域属性（仅对已知支持 CORS 的 CDN 设置）
      // 注意：大多数图片服务器不支持 CORS，默认不设置跨域属性
      // 1. 检查是否在不需要跨域的域名列表中
      const isNoCorsDomain = HTML_CLEANUP_CONFIG.noCorsDomains.some(pattern => 
        pattern.test(src)
      )
      
      if (!isNoCorsDomain) {
        // 2. 检查是否有特殊配置规则（已知支持 CORS 的 CDN）
        const corsRule = HTML_CLEANUP_CONFIG.imageCorsDomains.find(rule => 
          rule.pattern.test(src)
        )
        
        if (corsRule) {
          // 使用特殊配置（仅对已知支持 CORS 的 CDN）
          img.setAttribute('crossorigin', corsRule.crossorigin)
          img.setAttribute('referrerpolicy', corsRule.referrerpolicy)
        }
        // 其他外部图片默认不设置跨域属性，避免加载失败
      }
      
      // 添加错误处理和响应式样式
      // 保存原始 src 以便调试
      if (!img.dataset.originalSrc) {
        img.dataset.originalSrc = src
      }
      
      // 智能错误处理：如果设置了 crossorigin 但加载失败，尝试移除它
      img.onerror = function() {
        const originalSrc = this.dataset.originalSrc || this.src
        console.warn('图片加载失败:', originalSrc)
        
        // 如果设置了 crossorigin，尝试移除后重新加载
        if (this.crossOrigin === 'anonymous' && !this.dataset.retried) {
          this.dataset.retried = 'true'
          this.removeAttribute('crossorigin')
          this.removeAttribute('referrerpolicy')
          this.src = originalSrc
          return
        }
        
        // 如果已经重试过或没有 crossorigin，显示占位符
        if (!this.src.includes('data:image/svg+xml')) {
          this.src = 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'400\' height=\'300\'%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dy=\'.3em\' fill=\'%23999\'%3E图片加载失败%3C/text%3E%3C/svg%3E'
        }
      }
      
      if (!img.hasAttribute('style')) {
        img.setAttribute('style', 'max-width: 100%; height: auto;')
      }
    })
    
    return doc.body.innerHTML
  } catch (error) {
    console.error('处理 HTML 图片失败:', error)
    return html
  }
}

// 移除 HTML 中的固定宽度样式，确保内容响应式
const removeFixedWidths = (html) => {
  if (!html) return ''
  
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    
    // 处理所有有 style 属性的元素
    const elementsWithStyle = doc.querySelectorAll('[style]')
    elementsWithStyle.forEach(el => {
      const style = el.getAttribute('style') || ''
      if (!style) return
      
      // 移除固定宽度相关的样式
      // 匹配 width: 数字px, width:数字px, width: 数字%, width:数字% 等
      let newStyle = style
        .replace(/width\s*:\s*\d+px/gi, '') // 移除 width: 数字px
        .replace(/width\s*:\s*\d+%/gi, '') // 移除 width: 数字%
        .replace(/min-width\s*:\s*\d+px/gi, '') // 移除 min-width: 数字px
        .replace(/max-width\s*:\s*\d+px/gi, '') // 移除 max-width: 数字px（但保留 max-width: 100%）
        .replace(/,\s*,/g, ',') // 清理多余的逗号
        .replace(/^,\s*/, '') // 清理开头的逗号
        .replace(/,\s*$/, '') // 清理结尾的逗号
        .trim()
      
      if (newStyle) {
        el.setAttribute('style', newStyle)
      } else {
        el.removeAttribute('style')
      }
    })
    
    // 移除表格的 width 属性
    const tables = doc.querySelectorAll('table[width]')
    tables.forEach(table => {
      table.removeAttribute('width')
    })
    
    // 移除其他元素的 width 属性
    const elementsWithWidth = doc.querySelectorAll('[width]')
    elementsWithWidth.forEach(el => {
      // 保留 img 的 width 属性（因为图片处理函数会处理）
      if (el.tagName !== 'IMG') {
        el.removeAttribute('width')
      }
    })
    
    // 处理代码块中的固定宽度元素（如 hljs-ln）
    const codeElements = doc.querySelectorAll('.hljs-ln, ol.hljs-ln, ul.hljs-ln')
    codeElements.forEach(el => {
      // 移除固定宽度样式
      const style = el.getAttribute('style') || ''
      if (style) {
        let newStyle = style
          .replace(/width\s*:\s*[^;]+/gi, '') // 移除所有 width 相关样式
          .replace(/max-width\s*:\s*\d+px/gi, '')
          .replace(/min-width\s*:\s*[^;]+/gi, '')
          .replace(/,\s*,/g, ',')
          .replace(/^,\s*/, '')
          .replace(/,\s*$/, '')
          .trim()
        
        if (newStyle) {
          el.setAttribute('style', `width: 100%; max-width: 100%; overflow-x: auto; box-sizing: border-box; ${newStyle}`.trim())
        } else {
          el.setAttribute('style', 'width: 100%; max-width: 100%; overflow-x: auto; box-sizing: border-box;')
        }
      } else {
        el.setAttribute('style', 'width: 100%; max-width: 100%; overflow-x: auto; box-sizing: border-box;')
      }
    })
    
    // 特别处理 pre 和 code 元素，确保它们不会撑大容器
    const preElements = doc.querySelectorAll('pre')
    preElements.forEach(pre => {
      const style = pre.getAttribute('style') || ''
      // 移除所有 width 相关的样式
      let newStyle = style
        .replace(/width\s*:\s*[^;]+/gi, '')
        .replace(/max-width\s*:\s*\d+px/gi, '')
        .replace(/min-width\s*:\s*[^;]+/gi, '')
        .replace(/,\s*,/g, ',')
        .replace(/^,\s*/, '')
        .replace(/,\s*$/, '')
        .trim()
      
      // 确保有正确的宽度限制
      if (!newStyle.includes('width: 100%')) {
        pre.setAttribute('style', `width: 100%; max-width: 100%; overflow-x: auto; box-sizing: border-box; ${newStyle}`.trim())
      } else if (!newStyle.includes('max-width: 100%')) {
        pre.setAttribute('style', `${newStyle}; max-width: 100%; box-sizing: border-box;`.trim())
      } else if (!newStyle.includes('box-sizing: border-box')) {
        pre.setAttribute('style', `${newStyle}; box-sizing: border-box;`.trim())
      }
    })
    
    // 处理 code 元素（在 pre 中的）
    const codeInPre = doc.querySelectorAll('pre code')
    codeInPre.forEach(code => {
      const style = code.getAttribute('style') || ''
      // 移除所有 width 相关的样式
      let newStyle = style
        .replace(/width\s*:\s*[^;]+/gi, '')
        .replace(/max-width\s*:\s*\d+px/gi, '')
        .replace(/min-width\s*:\s*[^;]+/gi, '')
        .replace(/,\s*,/g, ',')
        .replace(/^,\s*/, '')
        .replace(/,\s*$/, '')
        .trim()
      
      // 确保有正确的宽度限制
      if (!newStyle.includes('max-width: 100%')) {
        code.setAttribute('style', `max-width: 100%; box-sizing: border-box; ${newStyle}`.trim())
      } else if (!newStyle.includes('box-sizing: border-box')) {
        code.setAttribute('style', `${newStyle}; box-sizing: border-box;`.trim())
      }
    })
    
    return doc.body.innerHTML
  } catch (error) {
    console.error('移除固定宽度失败:', error)
    return html
  }
}

const documentHtml = computed(() => {
  const html = content.value.document_html || ''
  if (!html) return ''
  
  // 先清理无用链接
  let cleanedHtml = cleanUselessLinks(html)
  
  // 移除固定宽度样式
  cleanedHtml = removeFixedWidths(cleanedHtml)
  
  // 再处理代码块
  cleanedHtml = processCodeBlocks(cleanedHtml)
  
  // 再处理图片路径
  const resourceUrl = resource.value?.url || ''
  return processHtmlImages(cleanedHtml, resourceUrl)
})

const documentToc = computed(() => content.value.document_toc || [])
const embedUrl = computed(() => content.value.embed_url || '')
const downloadUrl = computed(() => content.value.download_url || '')
const sections = computed(() => content.value.sections || [])
const additionalLinks = computed(() => content.value.extra_links || [])

// 处理书籍下载（使用 POST + JSON + Base64，完全伪装成普通 API，避免 IDM 拦截）
const handleBookDownload = async () => {
  if (!resource.value) {
    alert('资源信息不存在')
    return
  }
  
  // 检查是否有可下载的文件
  const hasBookFile = resource.value.content?.book_file_url
  if (!hasBookFile) {
    alert('该资源没有可下载的文件')
    return
  }
  
  try {
    // 显示下载提示
    const loadingMessage = document.createElement('div')
    loadingMessage.textContent = '正在获取文件数据，请稍候...'
    loadingMessage.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.8); color: white; padding: 20px 30px; border-radius: 8px; z-index: 10000; font-size: 16px;'
    document.body.appendChild(loadingMessage)
    
    // 使用 POST 请求，伪装成普通 API 调用
    const token = localStorage.getItem('access_token')
    const apiDownloadUrl = `${API_BASE_URL}/resources/${resource.value.id}/download/`
    
    // 使用 fetch POST 请求，发送 JSON 数据，让 IDM 认为这是普通 API 调用
    const response = await fetch(apiDownloadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        action: 'get_file_data',  // 伪装成 API 调用
        timestamp: Date.now()
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }))
      throw new Error(errorData.error || `下载失败: ${response.statusText}`)
    }
    
    // 解析 JSON 响应（IDM 不会拦截 JSON 响应）
    const data = await response.json()
    
    if (!data.success) {
      throw new Error(data.error || '获取文件数据失败')
    }
    
    // 检查是否是大文件分块传输
    if (data.chunked) {
      // 大文件分块下载（这里简化处理，实际可以优化）
      alert('文件较大，请稍后实现分块下载功能')
      if (document.body.contains(loadingMessage)) {
        document.body.removeChild(loadingMessage)
      }
      return
    }
    
    // 小文件：从 Base64 解码
    loadingMessage.textContent = '正在解码文件数据...'
    
    // 将 Base64 字符串转换为 Blob
    const base64Data = data.data
    const binaryString = atob(base64Data)
    const bytes = new Uint8Array(binaryString.length)
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i)
    }
    const blob = new Blob([bytes], { type: 'application/octet-stream' })
    
    // 获取文件名
    const filename = data.filename || resource.value.title || 'book'
    
    // 创建 Blob URL 并触发下载
    loadingMessage.textContent = '正在准备下载...'
    const blobUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = filename
    link.style.display = 'none'
    
    document.body.appendChild(link)
    link.click()
    
    // 清理
    setTimeout(() => {
      document.body.removeChild(link)
      URL.revokeObjectURL(blobUrl)
      if (document.body.contains(loadingMessage)) {
        document.body.removeChild(loadingMessage)
      }
    }, 100)
  } catch (error) {
    console.error('下载失败:', error)
    alert(error.message || '下载失败，请检查网络连接或联系管理员')
    // 清理加载提示
    const loadingMessages = document.querySelectorAll('div[style*="position: fixed"]')
    loadingMessages.forEach(msg => {
      if (document.body.contains(msg)) {
        document.body.removeChild(msg)
      }
    })
  }
}

// 获取 iframe 裁剪配置（用于跨域 iframe，只显示特定区域）
const iframeClipConfig = computed(() => {
  const config = content.value.extra_data?.iframe_clip || null
  if (!config) return null
  
  // 计算 iframe 的实际高度
  // 容器高度 + 顶部偏移 + 底部隐藏高度 = iframe 总高度
  const containerHeight = parseFloat(config.height) || 600  // 降低默认高度从 800px 到 600px
  const marginTop = Math.abs(parseFloat(config.marginTop) || 0)
  const marginBottom = Math.abs(parseFloat(config.marginBottom) || 0)
  
  // iframe 需要足够高以包含完整内容
  // 如果用户指定了 iframeHeight，使用它；否则自动计算
  const calculatedIframeHeight = containerHeight + marginTop + marginBottom
  const iframeHeight = config.iframeHeight 
    ? parseFloat(config.iframeHeight) 
    : calculatedIframeHeight
  
  return {
    ...config,
    // 容器显示高度
    containerHeight: `${containerHeight}px`,
    // iframe 实际高度（包含完整页面）
    iframeHeight: `${iframeHeight}px`,
    // 顶部偏移（隐藏导航栏）
    marginTop: `-${marginTop}px`,
    // 底部会被容器的 overflow: hidden 自动裁剪
  }
})

// 从文章 HTML 内容中提取目录结构
const extractTocFromHtml = (html) => {
  if (!html) return []
  
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const headings = doc.querySelectorAll('h1, h2, h3, h4, h5, h6')
    
    if (headings.length === 0) return []
    
    const toc = []
    const stack = [] // 用于处理嵌套的标题层级
    
    headings.forEach((heading, index) => {
      const level = parseInt(heading.tagName.charAt(1)) // h1 -> 1, h2 -> 2, etc.
      const title = heading.textContent?.trim() || ''
      const id = heading.id || `heading-${index}`
      
      // 如果没有 id，生成一个
      if (!heading.id && title) {
        const generatedId = title
          .toLowerCase()
          .replace(/[^\w\u4e00-\u9fa5]/g, '-')
          .replace(/-+/g, '-')
          .replace(/^-|-$/g, '')
        heading.id = generatedId
      }
      
      const tocItem = {
        id: heading.id || id,
        title: title,
        level: level
      }
      
      // 处理嵌套结构
      while (stack.length > 0 && stack[stack.length - 1].level >= level) {
        stack.pop()
      }
      
      if (stack.length === 0) {
        // 顶级标题
        toc.push(tocItem)
        stack.push(tocItem)
      } else {
        // 子标题
        const parent = stack[stack.length - 1]
        if (!parent.children) {
          parent.children = []
        }
        parent.children.push(tocItem)
        stack.push(tocItem)
      }
    })
    
    return toc
  } catch (error) {
    console.error('提取目录失败:', error)
    return []
  }
}

// 文章目录：优先使用 sections，否则从 HTML 中提取
// 递归处理 sections，确保所有层级的子项都有正确的 id
const processSections = (items) => {
  return items.map(item => {
    const processedItem = {
      id: item.id || item.title?.toLowerCase().replace(/[^\w\u4e00-\u9fa5]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, ''),
      title: item.title || '',
      level: item.level || 1,
      children: []
    }
    
    // 递归处理子项
    if (item.children && item.children.length > 0) {
      processedItem.children = processSections(item.children)
    }
    
    return processedItem
  })
}

const articleToc = computed(() => {
  // 优先从 HTML 中提取完整的目录结构（包含所有层级的标题）
  if (primaryHtml.value) {
    const htmlToc = extractTocFromHtml(primaryHtml.value)
    // 如果从 HTML 提取到了目录，优先使用（因为它包含完整的层级结构）
    if (htmlToc.length > 0) {
      return htmlToc
    }
  }
  
  // 如果 HTML 中没有提取到目录，使用 sections 数据
  if (sections.value && sections.value.length > 0) {
    return processSections(sections.value)
  }
  
  return []
})

// 工具目录：优先使用 sections，否则从 HTML 中提取
const toolToc = computed(() => {
  // 如果有 sections，优先使用
  if (sections.value && sections.value.length > 0) {
    return sections.value.map(section => ({
      id: section.id || section.title?.toLowerCase().replace(/[^\w\u4e00-\u9fa5]/g, '-'),
      title: section.title || '',
      level: section.level || 1,
      children: section.children || []
    }))
  }
  
  // 否则从 HTML 中提取
  if (primaryHtml.value) {
    return extractTocFromHtml(primaryHtml.value)
  }
  
  return []
})

// 项目目录：优先使用 sections，否则从 HTML 中提取
const projectToc = computed(() => {
  // 如果有 sections，优先使用
  if (sections.value && sections.value.length > 0) {
    return sections.value.map(section => ({
      id: section.id || section.title?.toLowerCase().replace(/[^\w\u4e00-\u9fa5]/g, '-'),
      title: section.title || '',
      level: section.level || 1,
      children: section.children || []
    }))
  }
  
  // 否则从 HTML 中提取
  if (primaryHtml.value) {
    return extractTocFromHtml(primaryHtml.value)
  }
  
  return []
})

// 为文档 HTML 中的标题添加 id（基于 document_toc）
const addIdsToDocumentHeadings = () => {
  if (!documentContent.value || !documentToc.value.length) return
  
  const tocMap = new Map()
  // 构建目录 id 到标题的映射
  const buildTocMap = (items) => {
    items.forEach(item => {
      if (item.id && item.title) {
        tocMap.set(item.title.toLowerCase().trim(), item.id)
      }
      if (item.children) {
        buildTocMap(item.children)
      }
    })
  }
  buildTocMap(documentToc.value)
  
  // 为标题元素添加 id
  const headings = documentContent.value.querySelectorAll('h1, h2, h3, h4, h5, h6')
  headings.forEach(heading => {
    if (!heading.id) {
      const titleText = heading.textContent?.trim().toLowerCase()
      if (titleText && tocMap.has(titleText)) {
        heading.id = tocMap.get(titleText)
      } else {
        // 如果没有匹配的目录项，生成一个基于标题文本的 id
        heading.id = titleText
          .replace(/[^\w\u4e00-\u9fa5]/g, '-')
          .replace(/-+/g, '-')
          .replace(/^-|-$/g, '')
      }
    }
  })
}

// 为文章 HTML 中的标题添加 id
const addIdsToArticleHeadings = () => {
  if (!articleContent.value) return
  
  const headings = articleContent.value.querySelectorAll('h1, h2, h3, h4, h5, h6')
  
  // 如果有 sections 数据，使用 sections 中的 id 来匹配
  if (sections.value && sections.value.length > 0) {
    // 构建标题文本到 id 的映射（支持多种匹配方式）
    const titleToIdMap = new Map()
    const buildMap = (items) => {
      items.forEach(item => {
        if (item.title) {
          const title = item.title.trim()
          const id = item.id || title.toLowerCase().replace(/[^\w\u4e00-\u9fa5]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '')
          
          // 使用多种 key 形式来匹配，提高匹配成功率
          const normalizedTitle = title.toLowerCase().trim()
          titleToIdMap.set(normalizedTitle, id)
          // 移除所有空格和标点符号的版本
          const noSpaceTitle = normalizedTitle.replace(/\s+/g, '').replace(/[^\w\u4e00-\u9fa5]/g, '')
          if (noSpaceTitle && noSpaceTitle !== normalizedTitle) {
            titleToIdMap.set(noSpaceTitle, id)
          }
          // 只保留中文和英文的版本
          const cleanTitle = normalizedTitle.replace(/[^\w\u4e00-\u9fa5]/g, '').trim()
          if (cleanTitle && cleanTitle !== normalizedTitle) {
            titleToIdMap.set(cleanTitle, id)
          }
        }
        if (item.children && item.children.length > 0) {
          buildMap(item.children)
        }
      })
    }
    buildMap(sections.value)
    
    // 为标题添加 id（即使已有 id，如果 sections 中有匹配的，也要更新）
    headings.forEach((heading, index) => {
      const titleText = heading.textContent?.trim() || heading.innerText?.trim()
      if (!titleText) return
      
      const normalizedText = titleText.toLowerCase().trim()
      
      // 尝试多种匹配方式
      let matchedId = titleToIdMap.get(normalizedText)
      
      if (!matchedId) {
        // 尝试移除空格和标点符号的版本
        const noSpaceText = normalizedText.replace(/\s+/g, '').replace(/[^\w\u4e00-\u9fa5]/g, '')
        matchedId = titleToIdMap.get(noSpaceText)
      }
      
      if (!matchedId) {
        // 尝试只保留中文和英文的版本
        const cleanText = normalizedText.replace(/[^\w\u4e00-\u9fa5]/g, '').trim()
        matchedId = titleToIdMap.get(cleanText)
      }
      
          if (!matchedId) {
            // 尝试模糊匹配：检查是否包含关键部分（更宽松的匹配）
            for (const [key, id] of titleToIdMap.entries()) {
              // 移除空格和标点后比较
              const cleanKey = key.replace(/\s+/g, '').replace(/[^\w\u4e00-\u9fa5]/g, '')
              const cleanText = normalizedText.replace(/\s+/g, '').replace(/[^\w\u4e00-\u9fa5]/g, '')
              // 精确匹配清理后的文本
              if (cleanText === cleanKey) {
                matchedId = id
                break
              }
              // 包含匹配（更宽松）
              if (cleanText.includes(cleanKey) || cleanKey.includes(cleanText) || 
                  normalizedText.includes(key) || key.includes(normalizedText)) {
                matchedId = id
                break
              }
              // 反向匹配：如果 HTML 标题包含 sections 标题，或者 sections 标题包含 HTML 标题
              // 例如："项目总结" 包含 "总结"
              if (normalizedText.includes(key) || key.includes(normalizedText)) {
                matchedId = id
                break
              }
            }
          }
      
      // 如果找到了匹配的 id，更新标题的 id（即使已有 id）
      if (matchedId) {
        heading.id = matchedId
      } else if (!heading.id) {
        // 如果没有匹配且没有 id，使用标题文本生成 id
        heading.id = titleText
          .toLowerCase()
          .replace(/[^\w\u4e00-\u9fa5]/g, '-')
          .replace(/-+/g, '-')
          .replace(/^-|-$/g, '') || `heading-${index}`
      }
    })
  } else {
    // 如果没有 sections，使用原来的方式
    headings.forEach((heading, index) => {
      if (!heading.id) {
        const titleText = heading.textContent?.trim()
        if (titleText) {
          heading.id = titleText
            .toLowerCase()
            .replace(/[^\w\u4e00-\u9fa5]/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '') || `heading-${index}`
        }
      }
    })
  }
}

// 为工具 HTML 中的标题添加 id
const addIdsToToolHeadings = () => {
  if (!toolContent.value) return
  
  const headings = toolContent.value.querySelectorAll('h1, h2, h3, h4, h5, h6')
  headings.forEach((heading, index) => {
    if (!heading.id) {
      const titleText = heading.textContent?.trim()
      if (titleText) {
        heading.id = titleText
          .toLowerCase()
          .replace(/[^\w\u4e00-\u9fa5]/g, '-')
          .replace(/-+/g, '-')
          .replace(/^-|-$/g, '') || `heading-${index}`
      }
    }
  })
}

// 为项目 HTML 中的标题添加 id
const addIdsToProjectHeadings = () => {
  if (!projectContent.value) return
  
  const headings = projectContent.value.querySelectorAll('h1, h2, h3, h4, h5, h6')
  headings.forEach((heading, index) => {
    if (!heading.id) {
      const titleText = heading.textContent?.trim()
      if (titleText) {
        heading.id = titleText
          .toLowerCase()
          .replace(/[^\w\u4e00-\u9fa5]/g, '-')
          .replace(/-+/g, '-')
          .replace(/^-|-$/g, '') || `heading-${index}`
      }
    }
  })
}

// 跳转到文档中的指定章节
const scrollToSection = (sectionId) => {
  if (!sectionId) return
  
  // 确保标题已有 id
  addIdsToDocumentHeadings()
  
  // 等待 DOM 更新
  setTimeout(() => {
    const element = document.getElementById(sectionId)
    if (element) {
      // 滚动到元素位置，留出一些顶部间距
      const yOffset = -80
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset
      window.scrollTo({ top: y, behavior: 'smooth' })
    } else {
      // 如果找不到 id，尝试查找包含该 id 的元素
      const allElements = document.querySelectorAll('[id]')
      for (const el of allElements) {
        if (el.id.includes(sectionId) || sectionId.includes(el.id)) {
          const yOffset = -80
          const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset
          window.scrollTo({ top: y, behavior: 'smooth' })
          break
        }
      }
    }
  }, 100)
}

// 跳转到文章中的指定章节
const scrollToArticleSection = (sectionId) => {
  if (!sectionId) return
  
  // 确保标题已有 id
  addIdsToArticleHeadings()
  
  // 等待 DOM 更新，使用重试机制
  let retryCount = 0
  const maxRetries = 5
  
  const tryScroll = () => {
    // 首先在文章内容区域内查找
    let element = null
    if (articleContent.value) {
      // 使用属性选择器，避免 ID 以数字开头时的 CSS 选择器错误
      try {
        element = articleContent.value.querySelector(`[id="${sectionId}"]`)
      } catch {
        // 如果属性选择器也失败，使用 getElementById 并检查是否在容器内
        element = document.getElementById(sectionId)
        if (element && !articleContent.value.contains(element)) {
          element = null
        }
      }
    }
    
    // 如果没找到，在整个文档中查找
    if (!element) {
      element = document.getElementById(sectionId)
    }
    
    if (element) {
      // 滚动到元素位置，留出一些顶部间距
      const yOffset = -80
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset
      window.scrollTo({ top: y, behavior: 'smooth' })
      return true
    } else {
      // 如果找不到精确匹配的 id，尝试模糊匹配
      // 优先在文章内容区域内查找
      const searchContainer = articleContent.value || document
      const allElements = searchContainer.querySelectorAll('[id]')
      
      for (const el of allElements) {
        // 尝试多种匹配方式
        const elId = el.id.toLowerCase()
        const targetId = sectionId.toLowerCase()
        
        // 精确匹配
        if (elId === targetId) {
          const yOffset = -80
          const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset
          window.scrollTo({ top: y, behavior: 'smooth' })
          return true
        }
        
        // 移除连字符后比较
        if (elId.replace(/-/g, '') === targetId.replace(/-/g, '')) {
          const yOffset = -80
          const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset
          window.scrollTo({ top: y, behavior: 'smooth' })
          return true
        }
        
        // 包含匹配（更宽松）
        if (elId.includes(targetId) || targetId.includes(elId)) {
          const yOffset = -80
          const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset
          window.scrollTo({ top: y, behavior: 'smooth' })
          return true
        }
      }
      
      // 如果还是没找到，尝试通过标题文本查找
      // 首先尝试直接从 articleToc 中找到对应的标题文本
      if (articleContent.value && articleToc.value && articleToc.value.length > 0) {
        // 从 articleToc 中找到对应的标题文本
        let targetTitle = null
        const findTitleInToc = (items) => {
          for (const item of items) {
            // 如果 id 匹配，使用该标题
            if (item.id === sectionId || item.id?.toLowerCase() === sectionId.toLowerCase()) {
              return item.title?.trim()
            }
            // 如果标题本身就是 sectionId（可能是从 HTML 提取的，id 就是标题）
            if (item.title?.trim().toLowerCase() === sectionId.toLowerCase()) {
              return item.title?.trim()
            }
            // 递归查找子项
            if (item.children && item.children.length > 0) {
              const found = findTitleInToc(item.children)
              if (found) return found
            }
          }
          return null
        }
        targetTitle = findTitleInToc(articleToc.value)
        
        // 如果找到了标题文本，通过文本查找对应的标题元素
        if (targetTitle) {
          const headings = articleContent.value.querySelectorAll('h1, h2, h3, h4, h5, h6')
          for (const heading of headings) {
            const headingText = heading.textContent?.trim() || heading.innerText?.trim()
            const headingTextLower = headingText.toLowerCase()
            const targetTitleLower = targetTitle.toLowerCase()
            
            // 精确匹配
            if (headingTextLower === targetTitleLower) {
              // 确保标题有正确的 id
              if (!heading.id || heading.id !== sectionId) {
                heading.id = sectionId
              }
              const yOffset = -80
              const y = heading.getBoundingClientRect().top + window.pageYOffset + yOffset
              window.scrollTo({ top: y, behavior: 'smooth' })
              return true
            }
            
            // 模糊匹配：移除空格和标点后比较
            const cleanHeadingText = headingTextLower.replace(/\s+/g, '').replace(/[^\w\u4e00-\u9fa5]/g, '')
            const cleanTargetTitle = targetTitleLower.replace(/\s+/g, '').replace(/[^\w\u4e00-\u9fa5]/g, '')
            if (cleanHeadingText === cleanTargetTitle || 
                cleanHeadingText.includes(cleanTargetTitle) || 
                cleanTargetTitle.includes(cleanHeadingText)) {
              if (!heading.id || heading.id !== sectionId) {
                heading.id = sectionId
              }
              const yOffset = -80
              const y = heading.getBoundingClientRect().top + window.pageYOffset + yOffset
              window.scrollTo({ top: y, behavior: 'smooth' })
              return true
            }
          }
        }
      }
      
      // 如果还是没找到，尝试从 sections 数据中查找
      if (articleContent.value && sections.value && sections.value.length > 0) {
        // 从 sections 数据中找到对应的标题文本
        let targetTitle = null
        for (const section of sections.value) {
          if (section.id === sectionId || section.id?.toLowerCase() === sectionId.toLowerCase()) {
            targetTitle = section.title?.trim().toLowerCase()
            break
          }
          // 递归查找子项
          const findInChildren = (items) => {
            for (const item of items) {
              if (item.id === sectionId || item.id?.toLowerCase() === sectionId.toLowerCase()) {
                return item.title?.trim().toLowerCase()
              }
              if (item.children && item.children.length > 0) {
                const found = findInChildren(item.children)
                if (found) return found
              }
            }
            return null
          }
          if (section.children && section.children.length > 0) {
            const found = findInChildren(section.children)
            if (found) {
              targetTitle = found
              break
            }
          }
        }
        
        // 如果找到了标题文本，通过文本查找对应的标题元素（支持部分匹配）
        if (targetTitle) {
          const headings = articleContent.value.querySelectorAll('h1, h2, h3, h4, h5, h6')
          for (const heading of headings) {
            const headingText = heading.textContent?.trim().toLowerCase() || heading.innerText?.trim().toLowerCase()
            
            // 精确匹配
            if (headingText === targetTitle) {
              if (!heading.id || heading.id !== sectionId) {
                heading.id = sectionId
              }
              const yOffset = -80
              const y = heading.getBoundingClientRect().top + window.pageYOffset + yOffset
              window.scrollTo({ top: y, behavior: 'smooth' })
              return true
            }
            
            // 模糊匹配：移除空格和标点后比较
            const cleanHeadingText = headingText.replace(/\s+/g, '').replace(/[^\w\u4e00-\u9fa5]/g, '')
            const cleanTargetTitle = targetTitle.replace(/\s+/g, '').replace(/[^\w\u4e00-\u9fa5]/g, '')
            if (cleanHeadingText === cleanTargetTitle || 
                cleanHeadingText.includes(cleanTargetTitle) || 
                cleanTargetTitle.includes(cleanHeadingText)) {
              if (!heading.id || heading.id !== sectionId) {
                heading.id = sectionId
              }
              const yOffset = -80
              const y = heading.getBoundingClientRect().top + window.pageYOffset + yOffset
              window.scrollTo({ top: y, behavior: 'smooth' })
              return true
            }
            
            // 更宽松的匹配：如果标题包含目标关键词（如"项目总结"包含"总结"）
            if (headingText.includes(targetTitle) || targetTitle.includes(headingText)) {
              if (!heading.id || heading.id !== sectionId) {
                heading.id = sectionId
              }
              const yOffset = -80
              const y = heading.getBoundingClientRect().top + window.pageYOffset + yOffset
              window.scrollTo({ top: y, behavior: 'smooth' })
              return true
            }
          }
        }
      }
      
      // 最后尝试：如果 sectionId 本身就是标题文本（从 HTML 提取的目录），直接查找
      if (articleContent.value) {
        const headings = articleContent.value.querySelectorAll('h1, h2, h3, h4, h5, h6')
        for (const heading of headings) {
          const headingText = heading.textContent?.trim() || heading.innerText?.trim()
          const headingTextLower = headingText.toLowerCase()
          const sectionIdLower = sectionId.toLowerCase()
          
          // 如果标题文本完全匹配 sectionId
          if (headingTextLower === sectionIdLower) {
            if (!heading.id || heading.id !== sectionId) {
              heading.id = sectionId
            }
            const yOffset = -80
            const y = heading.getBoundingClientRect().top + window.pageYOffset + yOffset
            window.scrollTo({ top: y, behavior: 'smooth' })
            return true
          }
          
          // 模糊匹配
          const cleanHeadingText = headingTextLower.replace(/\s+/g, '').replace(/[^\w\u4e00-\u9fa5]/g, '')
          const cleanSectionId = sectionIdLower.replace(/\s+/g, '').replace(/[^\w\u4e00-\u9fa5]/g, '')
          if (cleanHeadingText === cleanSectionId || 
              cleanHeadingText.includes(cleanSectionId) || 
              cleanSectionId.includes(cleanHeadingText)) {
            if (!heading.id || heading.id !== sectionId) {
              heading.id = sectionId
            }
            const yOffset = -80
            const y = heading.getBoundingClientRect().top + window.pageYOffset + yOffset
            window.scrollTo({ top: y, behavior: 'smooth' })
            return true
          }
        }
      }
      
      // 如果还是没找到，重试
      retryCount++
      if (retryCount < maxRetries) {
        // 再次确保 id 已添加
        addIdsToArticleHeadings()
        setTimeout(tryScroll, 100)
      } else {
        console.warn(`无法找到章节: ${sectionId}`)
      }
      return false
    }
  }
  
  setTimeout(tryScroll, 100)
}

// 跳转到工具中的指定章节
const scrollToToolSection = (sectionId) => {
  if (!sectionId) return
  
  // 确保标题已有 id
  addIdsToToolHeadings()
  
  // 等待 DOM 更新
  setTimeout(() => {
    const element = document.getElementById(sectionId)
    if (element) {
      // 滚动到元素位置，留出一些顶部间距
      const yOffset = -80
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset
      window.scrollTo({ top: y, behavior: 'smooth' })
    } else {
      // 如果找不到 id，尝试查找包含该 id 的元素
      const allElements = document.querySelectorAll('[id]')
      for (const el of allElements) {
        if (el.id.includes(sectionId) || sectionId.includes(el.id)) {
          const yOffset = -80
          const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset
          window.scrollTo({ top: y, behavior: 'smooth' })
          break
        }
      }
    }
  }, 100)
}

// 跳转到项目中的指定章节
const scrollToProjectSection = (sectionId) => {
  if (!sectionId) return
  
  // 确保标题已有 id
  addIdsToProjectHeadings()
  
  // 等待 DOM 更新
  setTimeout(() => {
    const element = document.getElementById(sectionId)
    if (element) {
      // 滚动到元素位置，留出一些顶部间距
      const yOffset = -80
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset
      window.scrollTo({ top: y, behavior: 'smooth' })
    } else {
      // 如果找不到 id，尝试查找包含该 id 的元素
      const allElements = document.querySelectorAll('[id]')
      for (const el of allElements) {
        if (el.id.includes(sectionId) || sectionId.includes(el.id)) {
          const yOffset = -80
          const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset
          window.scrollTo({ top: y, behavior: 'smooth' })
          break
        }
      }
    }
  }, 100)
}

// 监听 documentHtml 变化，自动为标题添加 id
watch([documentHtml, documentToc], () => {
  if (documentHtml.value && documentToc.value.length > 0) {
    // 等待 DOM 更新
    setTimeout(() => {
      addIdsToDocumentHeadings()
    }, 200)
  }
}, { immediate: true })

// 监听文章内容变化，自动为标题添加 id 并提取目录
watch([primaryHtml, isArticle], () => {
  if (isArticle.value && primaryHtml.value) {
    // 等待 DOM 更新
    setTimeout(() => {
      addIdsToArticleHeadings()
    }, 200)
  }
}, { immediate: true })

// 监听工具内容变化，自动为标题添加 id 并提取目录
watch([primaryHtml, isTool], () => {
  if (isTool.value && primaryHtml.value) {
    // 等待 DOM 更新
    setTimeout(() => {
      addIdsToToolHeadings()
    }, 200)
  }
}, { immediate: true })

// 监听项目内容变化，自动为标题添加 id 并提取目录
watch([primaryHtml, isProject], () => {
  if (isProject.value && primaryHtml.value) {
    // 等待 DOM 更新
    setTimeout(() => {
      addIdsToProjectHeadings()
    }, 200)
  }
}, { immediate: true })

// 当前选中的章节索引
const currentSectionIndex = ref(-1)
// 当前播放的视频 URL
const currentVideoUrl = ref('')

// 将 Bilibili 视频链接转换为 iframe 嵌入链接
const convertBilibiliToEmbed = (url) => {
  if (!url) return ''
  
  try {
    // 如果已经是 player.bilibili.com 格式，直接返回
    if (url.includes('player.bilibili.com')) {
      return url
    }
    
    // 解析 Bilibili 视频链接
    // 支持格式：
    // - https://www.bilibili.com/video/BV1gq1sBPECH
    // - https://www.bilibili.com/video/BV1gq1sBPECH?t=1.0
    // - https://www.bilibili.com/video/BV1gq1sBPECH?t=0.5&p=2
    const bvidMatch = url.match(/\/video\/(BV[a-zA-Z0-9]+)/i)
    if (bvidMatch) {
      const bvid = bvidMatch[1]
      const urlObj = new URL(url)
      
      // 提取页码参数（p=2 表示第2集）
      const page = urlObj.searchParams.get('p') || '1'
      // 提取时间参数（t=1.0 表示从1秒开始）
      const t = urlObj.searchParams.get('t') || ''
      
      // 构建播放器链接
      let embedUrl = `https://player.bilibili.com/player.html?bvid=${bvid}&page=${page}`
      
      // 如果有时间参数，添加到链接中
      if (t) {
        embedUrl += `&t=${t}`
      }
      
      return embedUrl
    }
    
    // 如果是短链接 b23.tv，提示使用完整链接
    if (url.includes('b23.tv')) {
      console.warn('Bilibili 短链接无法自动转换，请使用完整的视频链接')
      return url
    }
    
    return url
  } catch (error) {
    console.error('转换 Bilibili URL 失败:', error)
    return url
  }
}

// 获取章节的视频 URL
const getSectionVideoUrl = (section) => {
  if (!section) return ''
  
  // 优先使用章节的 embed_url 或 video_url
  const videoUrl = section.embed_url || section.video_url || ''
  if (videoUrl) {
    // 如果是 Bilibili 链接，转换为嵌入格式
    if (videoUrl.includes('bilibili.com') || videoUrl.includes('b23.tv')) {
      return convertBilibiliToEmbed(videoUrl)
    }
    return videoUrl
  }
  
  return ''
}

// 播放章节视频
const playSectionVideo = (index) => {
  const section = sections.value[index]
  if (section) {
    const videoUrl = getSectionVideoUrl(section)
    if (videoUrl) {
      currentVideoUrl.value = videoUrl
      currentSectionIndex.value = index
      // 滚动到视频播放器
      setTimeout(() => {
        const videoWrapper = document.querySelector('.video-wrapper')
        if (videoWrapper) {
          videoWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)
    }
  }
}

// 初始化视频：优先使用章节视频，其次使用主视频URL
watch([sections, embedUrl], ([newSections, newEmbedUrl]) => {
  // 优先检查章节视频
  if (newSections && newSections.length > 0) {
    const firstSection = newSections[0]
    const firstVideoUrl = getSectionVideoUrl(firstSection)
    if (firstVideoUrl) {
      currentVideoUrl.value = firstVideoUrl
      currentSectionIndex.value = 0
      return
    }
  }
  
  // 如果没有章节视频，使用主视频URL
  if (newEmbedUrl && !currentVideoUrl.value) {
    if (newEmbedUrl.includes('bilibili.com') || newEmbedUrl.includes('b23.tv')) {
      currentVideoUrl.value = convertBilibiliToEmbed(newEmbedUrl)
    } else {
      currentVideoUrl.value = newEmbedUrl
    }
  }
}, { immediate: true })
</script>

<style scoped>
.resource-detail-page {
  padding: 24px 12px;
  max-width: 1600px;
  margin: 0 auto;
  /* 确保不会阻止子元素的 sticky 定位 */
  overflow: visible;
  /* 确保页面有足够的高度 */
  min-height: 100vh;
}

/* 文档类型：进一步优化 */
.resource-detail-page.has-document {
  padding: 24px 12px;
  max-width: 1600px;
}

.resource-hero {
  display: flex;
  gap: 24px;
  padding: 24px 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #eef2ff, #fdf2f8);
}

.hero-meta {
  flex: 1;
}

.breadcrumb {
  font-size: 0.9rem;
  color: #4f46e5;
  text-decoration: none;
}

.hero-tags {
  margin: 12px 0;
  display: flex;
  gap: 12px;
}

.type-tag,
.audience-tag {
  padding: 4px 12px;
  border-radius: 999px;
  background: #eef2ff;
  color: #4338ca;
  font-size: 0.85rem;
}

.audience-tag {
  background: #ecfeff;
  color: #155e75;
}

.hero-meta h1 {
  margin: 0;
  font-size: 2rem;
  color: #0f172a;
}

.description {
  color: #475569;
  line-height: 1.6;
}

.hero-footer {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta {
  color: #475569;
  display: flex;
  gap: 24px;
}

.categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-chip-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  border-radius: 3px;
  margin-right: 4px;
  vertical-align: middle;
}

.category-chip-placeholder {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  margin-right: 4px;
  vertical-align: middle;
}

.category-chip {
  background: rgba(15, 23, 42, 0.05);
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.85rem;
  color: #0f172a;
}

.hero-cover {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 12px;
  padding: 8px;
}

.hero-cover img {
  max-width: 360px;
  max-height: 270px;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.state-card {
  margin-top: 24px;
  padding: 16px;
  border-radius: 12px;
  background: #f8fafc;
  text-align: center;
}

.state-card.error {
  background: #fef2f2;
  color: #b91c1c;
}

.resource-body {
  display: flex;
  gap: 24px;
  margin-top: 24px;
  /* 确保父容器不会阻止 sticky 定位 */
  overflow: visible;
}

.main-content {
  flex: 1;
  min-width: 0; /* 关键：防止 flex 子元素根据内容撑大 */
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.content-card {
  background: #fafbfc; /* 浅灰背景，与白色页面背景形成对比 */
  border-radius: 16px;
  padding: 24px 16px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08), 0 1px 3px rgba(15, 23, 42, 0.1);
  border: 1px solid rgba(226, 232, 240, 0.6); /* 轻微边框增强区分度 */
  transition: all 0.2s ease;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  /* 确保不会阻止子元素的 sticky 定位 */
  overflow: visible;
  /* 确保有足够的高度 */
  position: relative;
}

/* 对于有内容的 content-card，使用内部容器来处理溢出 */
.content-card > .rich-text {
  overflow-x: hidden; /* 防止内容横向溢出 */
}

/* article-layout 和 document-layout 内部的溢出处理 */
.article-layout > .article-content-wrapper,
.document-layout > .document-content-wrapper {
  overflow-x: hidden; /* 防止内容横向溢出 */
}

.content-card h2 {
  margin-top: 0;
  color: #0f172a;
}

.rich-text {
  color: #475569;
  line-height: 1.8;
  word-wrap: break-word;
  overflow-wrap: break-word;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow-x: hidden; /* 防止内容横向溢出 */
}

/* 确保所有子元素不会撑大容器 */
.rich-text :deep(*) {
  max-width: 100%;
  box-sizing: border-box;
}

/* 特别处理可能有固定宽度的元素 */
.rich-text :deep(ol),
.rich-text :deep(ul),
.rich-text :deep(li),
.rich-text :deep(div),
.rich-text :deep(span),
.rich-text :deep(p),
.rich-text :deep(pre),
.rich-text :deep(code) {
  max-width: 100%;
  box-sizing: border-box;
}

/* 代码块中的行号列表 */
.rich-text :deep(.hljs-ln),
.rich-text :deep(ol.hljs-ln),
.rich-text :deep(ul.hljs-ln) {
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  overflow-x: auto;
}

.rich-text :deep(p) {
  color: #475569;
  line-height: 1.8;
  margin: 0.75rem 0;
}

.rich-text :deep(h1) {
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: #0f172a;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.3;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.rich-text :deep(h2) {
  margin-top: 1.75rem;
  margin-bottom: 0.875rem;
  color: #0f172a;
  font-size: 1.5rem;
  font-weight: 600;
  line-height: 1.4;
}

.rich-text :deep(h3) {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: #0f172a;
  font-size: 1.25rem;
  font-weight: 600;
}

.rich-text :deep(h4) {
  margin-top: 1.25rem;
  margin-bottom: 0.625rem;
  color: #0f172a;
  font-size: 1.1rem;
  font-weight: 600;
}

.rich-text :deep(h5),
.rich-text :deep(h6) {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: #0f172a;
  font-size: 1rem;
  font-weight: 600;
}

.rich-text :deep(.chapter-title) {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: #4f46e5;
  font-size: 1.15rem;
  font-weight: 600;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e0e7ff;
}

.rich-text :deep(.info-item) {
  margin: 0.5rem 0;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.rich-text :deep(.info-item strong) {
  color: #0f172a;
  font-weight: 600;
  min-width: 100px;
  display: inline-block;
}

.rich-text :deep(.formatted-list) {
  margin: 1rem 0;
  padding-left: 1.5rem;
  list-style-type: disc;
}

.rich-text :deep(.formatted-list li) {
  margin: 0.5rem 0;
  line-height: 1.6;
}

/* rich-text 中的链接样式 - 但不影响目录 */
.rich-text:not(.article-toc):not(.toc-list) :deep(a) {
  color: #4f46e5;
  text-decoration: none;
  word-break: break-all;
}

.rich-text:not(.article-toc):not(.toc-list) :deep(a:hover) {
  text-decoration: underline;
}

.rich-text :deep(code) {
  background: #f1f5f9;
  color: #e11d48;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: 'Courier New', Courier, monospace;
}

.rich-text :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1rem 0;
  line-height: 1.6;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.rich-text :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
  border-radius: 0;
  font-size: 0.9rem;
  display: block;
  white-space: pre;
  overflow-x: auto;
  max-width: 100%;
  box-sizing: border-box;
}

/* CSDN 代码块样式支持 */
.rich-text :deep(pre[class*="prism"]),
.rich-text :deep(pre.code-block) {
  position: relative;
}

.rich-text :deep(code[class*="language-"]),
.rich-text :deep(code.language-python),
.rich-text :deep(code.language-shell),
.rich-text :deep(code.language-bash),
.rich-text :deep(code.language-javascript),
.rich-text :deep(code.language-json),
.rich-text :deep(code.language-html),
.rich-text :deep(code.language-css) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
}

/* 确保代码块可以横向滚动且不撑大容器 */
.rich-text :deep(pre) {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
}

.rich-text :deep(pre code) {
  word-wrap: normal;
  word-break: normal;
  white-space: pre;
  overflow-wrap: normal;
  max-width: 100%;
  box-sizing: border-box;
}

.rich-text :deep(blockquote) {
  border-left: 4px solid #4f46e5;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #64748b;
  font-style: italic;
  background: #f8fafc;
  padding: 1rem;
  border-radius: 4px;
}

.rich-text :deep(ul),
.rich-text :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.rich-text :deep(ul) {
  list-style-type: disc;
}

.rich-text :deep(ol) {
  list-style-type: decimal;
}

.rich-text :deep(li) {
  margin: 0.5rem 0;
  line-height: 1.6;
}

.rich-text :deep(strong),
.rich-text :deep(b) {
  font-weight: 600;
  color: #0f172a;
}

.rich-text :deep(em),
.rich-text :deep(i) {
  font-style: italic;
}

.rich-text :deep(hr) {
  border: none;
  border-top: 2px solid #e2e8f0;
  margin: 2rem 0;
}

.rich-text :deep(table) {
  width: 100%;
  max-width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  display: block;
  overflow-x: auto;
  box-sizing: border-box;
}

.rich-text :deep(table th),
.rich-text :deep(table td) {
  border: 1px solid #e2e8f0;
  padding: 0.75rem;
  text-align: left;
  max-width: 100%;
  box-sizing: border-box;
  word-wrap: break-word;
}

.rich-text :deep(table th) {
  background: #f8fafc;
  font-weight: 600;
  color: #0f172a;
}

.rich-text :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1rem 0;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

/* 处理图片加载失败的情况 */
.rich-text :deep(img[src=""]) {
  display: none;
}

/* 确保图片容器正确显示 */
.rich-text :deep(.article_content),
.rich-text :deep(.article_content img) {
  max-width: 100%;
  height: auto;
}

/* CSDN 特定的图片样式 */
.rich-text :deep(.article_content .code_img_closed),
.rich-text :deep(.article_content .code_img_opened) {
  cursor: pointer;
}

.download-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-btn,
.ghost-btn {
  padding: 10px 18px;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  text-decoration: none;
  font-size: 0.95rem;
  text-align: center;
}

.primary-btn {
  background: #4f46e5;
  color: #fff;
}

.ghost-btn {
  background: rgba(79, 70, 229, 0.1);
  color: #4f46e5;
}

.ghost-btn.full-width {
  display: block;
  width: 100%;
  margin-top: 12px;
}

.button-group .ghost-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 0;
  white-space: nowrap;
  min-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.video-wrapper iframe {
  width: 100%;
  height: 100%;
  min-height: 540px;
  border-radius: 12px;
  background: #000;
}

.document-embed-iframe {
  width: 100%;
  height: 100%;
  min-height: 500px;  /* 文档 iframe 最小高度 */
  max-height: 800px; /* 文档 iframe 最大高度，避免过高 */
  border-radius: 12px;
  background: #000;
}

.document-embed-wrapper {
  position: relative;
}

/* iframe 裁剪容器 - 用于只显示中间部分（隐藏导航栏和页脚） */
.iframe-clip-container {
  position: relative;
  overflow: hidden; /* 关键：隐藏超出容器的内容 */
  border-radius: 12px;
  background: #fff;
  width: 100%;
  max-height: 800px; /* 限制最大高度，避免过高 */
  /* 容器高度由配置决定，超出部分会被 overflow: hidden 裁剪 */
}

.iframe-clip-container .document-embed-iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  border-radius: 0;
  /* iframe 高度大于容器高度，通过 marginTop 向上移动隐藏顶部 */
  /* 底部超出部分会被容器的 overflow: hidden 自动裁剪 */
}

/* 课程布局：左右分栏 */
.course-main-layout {
  display: flex;
  gap: 20px;
  margin-top: 16px;
  align-items: stretch; /* 确保左右两侧高度一致 */
}

.course-video-section {
  flex: 1;
  min-width: 0; /* 防止 flex 子元素溢出 */
  display: flex;
  flex-direction: column;
}

.video-wrapper {
  flex: 1;
  display: flex;
  min-height: 540px;
}

.video-placeholder {
  width: 100%;
  min-height: 540px;
  border-radius: 12px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  border: 2px dashed #cbd5e1;
}

.video-placeholder i {
  font-size: 3rem;
  margin-bottom: 12px;
}

.video-placeholder p {
  margin: 0;
  font-size: 1rem;
}

/* 右侧章节列表 */
.course-sections-sidebar {
  width: 200px;
  flex-shrink: 0;
  background: #f8fafc;
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  min-height: 540px; /* 与视频播放器高度一致 */
  max-height: 540px; /* 限制最大高度与视频播放器一致 */
  overflow: hidden; /* 外层容器不滚动 */
}

/* 自定义滚动条样式 */
.course-sections-sidebar::-webkit-scrollbar,
.sections-list::-webkit-scrollbar {
  width: 5px;
}

.course-sections-sidebar::-webkit-scrollbar-track,
.sections-list::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.course-sections-sidebar::-webkit-scrollbar-thumb,
.sections-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.course-sections-sidebar::-webkit-scrollbar-thumb:hover,
.sections-list::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.sections-title {
  margin: 0 0 8px 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0; /* 标题不参与滚动 */
}

.sections-title i {
  color: #4f46e5;
}

.section-count {
  font-size: 0.8rem;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
}

.sections-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  overflow-y: auto;
  min-height: 0; /* 允许 flex 子元素缩小 */
}

/* 紧凑型章节项 */
.section-item-compact {
  display: flex;
  gap: 6px;
  padding: 6px;
  border-radius: 6px;
  background: white;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.section-item-compact.has-video {
  cursor: pointer;
}

.section-item-compact.has-video:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transform: translateY(-1px);
}

.section-item-compact.active {
  border-color: #4f46e5;
  background: #eef2ff;
  box-shadow: 0 2px 12px rgba(79, 70, 229, 0.15);
}

.section-item-compact.active.has-video:hover {
  border-color: #4338ca;
  box-shadow: 0 4px 16px rgba(79, 70, 229, 0.2);
}

.section-number {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.75rem;
  transition: all 0.2s;
}

.section-item-compact.active .section-number {
  background: #4f46e5;
  color: white;
}

.section-content {
  flex: 1;
  min-width: 0;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 4px;
  margin-bottom: 1px;
}

.section-title {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.2;
  flex: 1;
  word-break: break-word;
}

.section-item-compact.active .section-title {
  color: #4f46e5;
}

.section-item-compact.has-video .section-title {
  cursor: pointer;
}

.section-summary {
  margin: 1px 0 0 0;
  font-size: 0.7rem;
  color: #64748b;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-clamp: 1;
}

.play-icon-btn {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #e2e8f0;
  border: none;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 0.6rem;
}

.play-icon-btn:hover {
  background: #4f46e5;
  color: white;
  transform: scale(1.1);
}

.play-icon-btn.playing {
  background: #4f46e5;
  color: white;
}


/* 课程介绍 */
.course-intro {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.course-intro h3 {
  margin: 0 0 12px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #0f172a;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .course-main-layout {
    flex-direction: column;
  }
  
  .course-sections-sidebar {
    width: 100%;
    min-height: auto;
    max-height: 400px;
  }
  
  .video-wrapper iframe {
    min-height: 300px;
  }
}

@media (max-width: 768px) {
  .course-sections-sidebar {
    padding: 16px;
    max-height: 350px;
  }
  
  .sections-title {
    font-size: 1rem;
  }
  
  .section-item-compact {
    padding: 10px;
  }
  
  .section-title {
    font-size: 0.9rem;
  }
  
  .section-summary {
    font-size: 0.8rem;
  }
  
  .video-wrapper iframe {
    min-height: 250px;
  }
}


.link-list {
  padding-left: 18px;
  color: #475569;
}

.sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: -webkit-sticky; /* Safari 兼容 */
  position: sticky;
  top: 80px; /* 完整展示卡片内容 */
  align-self: flex-start;
  max-height: calc(100vh - 160px); /* 上下各留 80px */
  overflow-y: auto;
  z-index: 10; /* 确保在其他内容之上 */
}

.sidebar-card {
  background: #fafbfc; /* 浅灰背景，与白色页面背景形成对比 */
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08), 0 1px 3px rgba(15, 23, 42, 0.1);
  border: 1px solid rgba(226, 232, 240, 0.6); /* 轻微边框增强区分度 */
  transition: all 0.2s ease;
}

.sidebar-card h3 {
  font-size: 1rem;
  margin: 0 0 12px 0;
  color: #0f172a;
}

.sidebar-card ul {
  list-style: none;
  padding: 0;
  margin: 0 0 12px;
  color: #475569;
  font-size: 0.9rem;
}

.sidebar-card li {
  margin-bottom: 6px;
  line-height: 1.5;
}

/* 按钮组样式 */
.button-group {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  width: 100%;
  flex-wrap: nowrap;
}

/* 收藏按钮样式 */
.favorite-btn {
  flex: 1;
  padding: 10px 18px;
  border: none;
  border-radius: 999px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-size: 0.95rem;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  white-space: nowrap;
  min-width: 0;
}

.favorite-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #dc2626;
}

.favorite-btn.favorited {
  background: rgba(220, 38, 38, 0.15);
  color: #dc2626;
}

.favorite-btn.favorited:hover {
  background: rgba(220, 38, 38, 0.2);
  color: #b91c1c;
}

.favorite-btn i {
  font-size: 1rem;
}

/* 模态框样式 */
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

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  min-width: 320px;
  max-width: 90%;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-content h3 {
  margin: 0 0 16px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #0f172a;
}

.category-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #475569;
  background: white;
  margin-bottom: 16px;
  cursor: pointer;
}

.category-select:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.modal-actions .primary-btn,
.modal-actions .ghost-btn {
  padding: 8px 16px;
  font-size: 0.9rem;
}

/* 推荐资源列表 */
.recommended-resources {
  list-style: none;
  padding: 0;
  margin: 0;
}

.recommended-item {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
}

.recommended-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.recommended-link {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-decoration: none;
  color: inherit;
  transition: color 0.2s ease;
}

.recommended-link:hover {
  color: #4f46e5;
}

.recommended-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #0f172a;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-clamp: 2;
}

.recommended-link:hover .recommended-title {
  color: #4f46e5;
}

.recommended-type {
  font-size: 0.75rem;
  color: #64748b;
  padding: 2px 8px;
  background: #f1f5f9;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.muted {
  color: #94a3b8;
}


.article-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  margin-top: 16px;
  /* 确保父容器不会阻止 sticky 定位 */
  overflow: visible;
  /* 确保有足够的高度让 sticky 工作 - 使用 auto 让内容自然撑开 */
  position: relative;
}

.document-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  margin-top: 16px;
  /* 确保父容器不会阻止 sticky 定位 */
  overflow: visible;
  /* 确保有足够的高度让 sticky 工作 - 使用 auto 让内容自然撑开 */
  position: relative;
}

/* 左侧：文档目录（跟随滚动，到达顶部时固定） */
.document-toc-sidebar {
  width: 240px;
  flex-shrink: 0;
  position: -webkit-sticky; /* Safari 兼容 */
  position: sticky;
  top: 80px; /* 完整展示卡片内容 */
  align-self: flex-start;
  max-height: calc(100vh - 160px); /* 上下各留 80px */
  overflow-y: auto;
  background: #fafbfc; /* 浅灰背景，与白色页面背景形成对比 */
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08), 0 1px 3px rgba(15, 23, 42, 0.1);
  border: 1px solid rgba(226, 232, 240, 0.6); /* 轻微边框增强区分度 */
  transition: all 0.2s ease;
  z-index: 10; /* 确保在其他内容之上 */
}

/* 左侧：文章目录（跟随滚动，到达顶部时固定，与文档目录相同样式） */
.article-toc-sidebar {
  width: 240px;
  flex-shrink: 0;
  position: -webkit-sticky; /* Safari 兼容 */
  position: sticky;
  top: 85px; /* 完整展示卡片内容 */
  align-self: flex-start;
  max-height: calc(100vh - 160px); /* 上下各留 80px */
  overflow-y: auto;
  background: #fafbfc; /* 浅灰背景，与白色页面背景形成对比 */
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08), 0 1px 3px rgba(15, 23, 42, 0.1);
  border: 1px solid rgba(226, 232, 240, 0.6); /* 轻微边框增强区分度 */
  transition: all 0.2s ease;
  z-index: 10; /* 确保在其他内容之上 */
}

.document-toc {
  width: 100%;
}

.article-toc {
  width: 100%;
}

/* 右侧：文档内容 */
.document-content-wrapper {
  flex: 1;
  min-width: 0;
}

.document-content {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow-x: hidden; /* 防止内容横向溢出 */
}

/* 确保文档内容中的所有元素都不会撑大容器 */
.document-content :deep(*) {
  max-width: 100%;
  box-sizing: border-box;
}

/* 特别处理代码块和表格 */
.document-content :deep(pre),
.document-content :deep(.hljs-ln),
.document-content :deep(ol.hljs-ln),
.document-content :deep(ul.hljs-ln) {
  width: 100% !important;
  max-width: 100% !important;
  overflow-x: auto;
  box-sizing: border-box !important;
}

.document-content :deep(table) {
  width: 100% !important;
  max-width: 100% !important;
  display: block;
  overflow-x: auto;
  box-sizing: border-box !important;
}

/* 右侧：文章内容 */
.article-content-wrapper {
  flex: 1;
  min-width: 0;
}

.article-content {
  width: 100%;
}

.toc-title {
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

.toc-title i {
  color: #4f46e5;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-item {
  margin: 0;
  padding: 0;
}

/* 目录样式已通过 TocItem 组件的内联样式实现，这里保留基础样式以防万一 */
.toc-children {
  list-style: none;
  padding: 0;
  margin: 4px 0 0 0;
}

/* 工具和项目目录的样式（不使用 TocItem 组件） */
.tool-toc-list .toc-item,
.project-toc-list .toc-item {
  list-style: none;
  margin: 0;
  padding: 0;
}

.tool-toc-list .toc-level-1,
.project-toc-list .toc-level-1 {
  font-weight: 600;
  margin-bottom: 4px;
  color: #0f172a;
  font-size: 0.95rem;
}

.tool-toc-list .toc-level-2,
.project-toc-list .toc-level-2 {
  margin-left: 8px;
  font-weight: 500;
  margin-bottom: 2px;
  color: #475569;
  font-size: 0.85rem;
}

.tool-toc-list .toc-level-3,
.project-toc-list .toc-level-3 {
  margin-left: 16px;
  font-weight: 400;
  margin-bottom: 2px;
  color: #64748b;
  font-size: 0.8rem;
}

.tool-toc-list .toc-link,
.project-toc-list .toc-link {
  display: block;
  padding: 6px 8px;
  color: inherit;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
  font-size: inherit;
  line-height: 1.5;
  cursor: pointer;
}

.tool-toc-list .toc-link:hover,
.project-toc-list .toc-link:hover {
  background: #f1f5f9;
  color: #4f46e5;
  padding-left: 12px;
}

.tool-toc-list .toc-text,
.project-toc-list .toc-text {
  display: block;
  padding: 6px 8px;
  color: inherit;
  font-size: inherit;
  line-height: 1.5;
}

/* 自定义滚动条 */
.document-toc-sidebar::-webkit-scrollbar,
.article-toc-sidebar::-webkit-scrollbar {
  width: 6px;
}

.document-toc-sidebar::-webkit-scrollbar-track,
.article-toc-sidebar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.document-toc-sidebar::-webkit-scrollbar-thumb,
.article-toc-sidebar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.document-toc-sidebar::-webkit-scrollbar-thumb:hover,
.article-toc-sidebar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

@media (max-width: 1024px) {
  .resource-body {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
  }

  /* 文档布局：小屏幕时目录在上方 */
  .document-layout {
    flex-direction: column;
  }

  .document-toc-sidebar {
    width: 100%;
    position: relative;
    top: 0;
    max-height: 400px;
  }

  /* 文章布局：小屏幕时目录在上方 */
  .article-layout {
    flex-direction: column;
  }

  .article-toc-sidebar {
    width: 100%;
    position: relative;
    top: 0;
    max-height: 400px;
  }
}

@media (max-width: 768px) {
  .resource-hero {
    flex-direction: column;
  }
}
</style>

