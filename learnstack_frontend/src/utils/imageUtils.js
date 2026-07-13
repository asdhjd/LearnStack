// 图片处理工具函数 - 统一管理所有页面的图片加载逻辑
// 采用智能默认策略，减少手动配置需求

// 图片处理配置
const IMAGE_CONFIG = {
  // 已知支持 CORS 的 CDN（白名单 - 仅这些域名会设置 CORS 属性）
  // 注意：大多数图片服务器不支持 CORS，默认不设置
  imageCorsDomains: [
    { pattern: /csdnimg\.cn|csdn\.net/i, crossorigin: 'anonymous', referrerpolicy: 'no-referrer' },
    { pattern: /aliyun\.com|aliyuncs\.com|alicdn\.com/i, crossorigin: 'anonymous', referrerpolicy: 'no-referrer' },
    { pattern: /hdslb\.com/i, crossorigin: 'anonymous', referrerpolicy: 'no-referrer' },
    { pattern: /bilibili\.com/i, crossorigin: 'anonymous', referrerpolicy: 'no-referrer' },
    { pattern: /b23\.tv/i, crossorigin: 'anonymous', referrerpolicy: 'no-referrer' }
  ],
  
  // 已知不支持 CORS 的域名（黑名单 - 这些域名明确不支持，避免尝试）
  // 注意：这个列表主要用于记录已知问题，不是必需的
  noCorsDomains: [
    /cnblogs\.com/i,
    /images\d+\.cnblogs\.com/i,
    /images2018\.cnblogs\.com/i,
    /17golang\.com/i,
    /github\.com/i,
    /githubusercontent\.com/i
  ],
  
  // 图片代理服务（可选 - 如果图片加载失败，可以尝试通过代理加载）
  // 格式：{ url: '代理服务URL', enabled: true/false }
  // 例如：{ url: 'https://images.weserv.nl/?url=', enabled: false }
  proxyService: {
    enabled: false,
    url: '' // 可以配置图片代理服务
  }
}

// 获取当前页面的源
export const getCurrentOrigin = () => {
  if (typeof window !== 'undefined') {
    return window.location.origin
  }
  return ''
}

// 从 URL 中提取域名（支持多种格式）
export const getDomainFromUrl = (url) => {
  if (!url) return null
  try {
    // 处理 data URI
    if (url.startsWith('data:')) return null
    // 处理相对路径
    if (url.startsWith('/') && !url.startsWith('//')) return null
    // 处理协议相对路径
    if (url.startsWith('//')) {
      const urlObj = new URL(`https:${url}`)
      return urlObj.hostname
    }
    // 处理完整 URL
    const urlObj = new URL(url)
    return urlObj.hostname
  } catch {
    return null
  }
}

// 获取图片的跨域属性（智能判断 - 默认不设置，仅对白名单域名设置）
export const getImageCorsAttribute = (imageUrl) => {
  if (!imageUrl) return undefined
  
  // 如果是 data URI 或相对路径，不需要跨域
  if (imageUrl.startsWith('data:') || imageUrl.startsWith('/')) {
    return undefined
  }
  
  // 默认策略：不设置 CORS 属性（因为大多数服务器不支持）
  // 仅对已知支持 CORS 的 CDN（白名单）设置
  const corsRule = IMAGE_CONFIG.imageCorsDomains.find(rule => 
    rule.pattern.test(imageUrl)
  )
  
  if (corsRule) {
    return corsRule.crossorigin
  }
  
  // 其他所有图片默认不设置 CORS 属性
  // 这样可以避免因设置 CORS 导致的加载失败
  return undefined
}

// 获取图片的 referrer 策略（智能默认策略）
export const getImageReferrerPolicy = (imageUrl) => {
  if (!imageUrl) return undefined
  
  // 如果是 data URI 或相对路径，不需要 referrer
  if (imageUrl.startsWith('data:') || imageUrl.startsWith('/')) {
    return undefined
  }
  
  // 检查是否有 CORS 配置规则（白名单域名）
  const corsRule = IMAGE_CONFIG.imageCorsDomains.find(rule => 
    rule.pattern.test(imageUrl)
  )
  
  if (corsRule) {
    return corsRule.referrerpolicy
  }
  
  // 默认策略：不设置 referrerpolicy，让浏览器使用默认策略
  // 这样可以避免因 referrer 策略导致的加载失败
  // 如果加载失败，错误处理函数会尝试不同的策略
  return undefined
}

// 处理图片加载失败（智能重试机制 - 自动尝试不同策略）
export const handleImageError = (event) => {
  const img = event.target
  let originalSrc = img.dataset.originalSrc || img.src
  
  // 如果已经是占位符，不再重试
  if (originalSrc && originalSrc.includes('data:image/svg+xml')) {
    return
  }
  
  // 保存原始 URL（如果还没有保存）
  if (!img.dataset.originalSrc && originalSrc && !originalSrc.includes('data:image/svg+xml')) {
    img.dataset.originalSrc = originalSrc
  }
  
  const retryCount = parseInt(img.dataset.retryCount || '0')
  const maxRetries = 5
  
  // 如果超过最大重试次数，显示占位符
  if (retryCount >= maxRetries) {
    if (originalSrc && !originalSrc.includes('data:image/svg+xml')) {
      // 如果启用了代理服务，尝试使用代理
      if (IMAGE_CONFIG.proxyService.enabled && IMAGE_CONFIG.proxyService.url) {
        const proxyUrl = IMAGE_CONFIG.proxyService.url + encodeURIComponent(originalSrc)
        img.dataset.retryCount = String(maxRetries + 1)
        img.src = proxyUrl
        return
      }
      
      // 显示占位符
      img.src = 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'400\' height=\'300\'%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dy=\'.3em\' fill=\'%23999\'%3E图片加载失败%3C/text%3E%3C/svg%3E'
      console.warn('图片加载失败，已尝试多种方式:', originalSrc)
    } else {
      img.style.display = 'none'
    }
    return
  }
  
  // 渐进式重试策略
  img.dataset.retryCount = String(retryCount + 1)
  
  switch (retryCount) {
    case 0:
      // 第一次重试：移除所有属性，使用最基础的方式
      img.removeAttribute('crossorigin')
      img.removeAttribute('referrerpolicy')
      break
      
    case 1:
      // 第二次重试：尝试 origin-when-cross-origin
      img.setAttribute('referrerpolicy', 'origin-when-cross-origin')
      break
      
    case 2:
      // 第三次重试：尝试 origin
      img.setAttribute('referrerpolicy', 'origin')
      break
      
    case 3:
      // 第四次重试：尝试 unsafe-url（发送完整 referrer）
      img.setAttribute('referrerpolicy', 'unsafe-url')
      break
      
    case 4:
      // 第五次重试：完全不设置 referrerpolicy
      img.removeAttribute('referrerpolicy')
      break
      
    default:
      break
  }
  
  // 重新加载
  if (originalSrc && !originalSrc.includes('data:image/svg+xml')) {
    img.src = originalSrc
  }
}

// 处理图片加载成功
export const handleImageLoad = (event) => {
  const img = event.target
  // 清除可能保存的原始 URL 和重试计数
  if (img.dataset.originalSrc) {
    delete img.dataset.originalSrc
  }
  if (img.dataset.retryCount) {
    delete img.dataset.retryCount
  }
}

