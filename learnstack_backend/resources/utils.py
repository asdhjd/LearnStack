"""
内容抓取工具函数
支持从常见网站（CSDN、Juejin、阿里云、博客园等）抓取文章内容
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import urllib3
import ssl
from requests.adapters import HTTPAdapter

# 禁用SSL警告（因为我们可能需要禁用SSL验证来处理某些网站）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 创建自定义的SSL上下文，允许较旧的TLS版本
class CustomHTTPAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        # 创建SSL上下文，允许所有TLS版本
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        # 设置最低安全级别，允许较旧的TLS版本
        try:
            ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
        except:
            # 如果set_ciphers失败，尝试其他方法
            pass
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

# 备用方法：使用urllib3直接请求（用于SSL问题严重的网站）
def fetch_with_urllib3(url, headers):
    """使用urllib3直接请求，绕过requests的SSL问题"""
    import urllib3.poolmanager
    # 创建不验证SSL的PoolManager
    http = urllib3.poolmanager.PoolManager(
        cert_reqs=ssl.CERT_NONE,
        ca_certs=None,
    )
    try:
        response = http.request('GET', url, headers=headers, timeout=urllib3.Timeout(20))
        # 尝试自动检测编码
        encoding = 'utf-8'
        if response.headers.get('Content-Type'):
            import re
            charset_match = re.search(r'charset=([^;]+)', response.headers.get('Content-Type', ''))
            if charset_match:
                encoding = charset_match.group(1).strip()
        return response.data.decode(encoding, errors='ignore')
    except Exception as e:
        raise Exception(f'urllib3请求失败: {str(e)}')


def get_article_content(url, max_retries=3):
    """
    从URL抓取文章内容
    
    Args:
        url: 文章URL
        max_retries: 最大重试次数
        
    Returns:
        dict: {
            'title': 文章标题,
            'content': HTML内容,
            'cover': 封面图片URL（如果有）,
            'success': 是否成功
        }
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    # 使用session来保持连接
    session = requests.Session()
    session.headers.update(headers)
    
    # 使用自定义的HTTP适配器来处理SSL问题
    try:
        adapter = CustomHTTPAdapter()
        session.mount('https://', adapter)
        session.mount('http://', adapter)
    except Exception as e:
        # 如果自定义适配器失败，使用默认配置
        print(f'警告：无法使用自定义SSL适配器: {e}')
    
    # 重试机制
    last_error = None
    for attempt in range(max_retries):
        try:
            # 禁用SSL验证（某些网站可能有SSL问题）
            # 注意：在生产环境中应该谨慎使用
            response = session.get(
                url, 
                timeout=20, 
                verify=False, 
                allow_redirects=True,
                stream=False
            )
            
            # 检查响应状态
            if response.status_code != 200:
                if attempt < max_retries - 1:
                    continue
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: 无法访问该URL',
                    'title': '',
                    'content': '',
                    'cover': ''
                }
            
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取域名
            domain = urlparse(url).netloc.lower()
            
            # 根据域名选择不同的提取策略
            if 'csdn.net' in domain:
                return extract_csdn_content(soup, url)
            elif 'juejin.cn' in domain:
                return extract_juejin_content(soup, url)
            elif 'aliyun.com' in domain or 'developer.aliyun.com' in domain:
                return extract_aliyun_content(soup, url)
            elif 'cnblogs.com' in domain:
                return extract_cnblogs_content(soup, url)
            elif 'imooc.com' in domain:
                return extract_imooc_content(soup, url)
            elif 'tencent.com' in domain or 'cloud.tencent.com' in domain:
                return extract_tencent_content(soup, url)
            else:
                # 通用提取策略
                return extract_generic_content(soup, url)
                
        except requests.exceptions.SSLError as e:
            last_error = f'SSL连接错误: {str(e)}'
            # 对于SSL错误，尝试使用urllib3作为备用方案
            if attempt == max_retries - 1:  # 最后一次尝试
                try:
                    html_content = fetch_with_urllib3(url, headers)
                    soup = BeautifulSoup(html_content, 'html.parser')
                    domain = urlparse(url).netloc.lower()
                    
                    # 根据域名选择不同的提取策略
                    if 'csdn.net' in domain:
                        return extract_csdn_content(soup, url)
                    elif 'juejin.cn' in domain:
                        return extract_juejin_content(soup, url)
                    elif 'aliyun.com' in domain or 'developer.aliyun.com' in domain:
                        return extract_aliyun_content(soup, url)
                    elif 'cnblogs.com' in domain:
                        return extract_cnblogs_content(soup, url)
                    elif 'imooc.com' in domain:
                        return extract_imooc_content(soup, url)
                    elif 'tencent.com' in domain or 'cloud.tencent.com' in domain:
                        return extract_tencent_content(soup, url)
                    else:
                        return extract_generic_content(soup, url)
                except Exception as urllib3_error:
                    last_error = f'SSL错误且urllib3备用方案也失败: {str(urllib3_error)}'
            else:
                import time
                time.sleep(2)  # SSL错误等待更长时间
                # 尝试重新创建session
                try:
                    session.close()
                except:
                    pass
                session = requests.Session()
                session.headers.update(headers)
                try:
                    adapter = CustomHTTPAdapter()
                    session.mount('https://', adapter)
                    session.mount('http://', adapter)
                except:
                    pass
                continue
        except requests.exceptions.Timeout as e:
            last_error = f'请求超时: {str(e)}'
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
                continue
        except requests.exceptions.ConnectionError as e:
            last_error = f'连接错误: {str(e)}'
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
                continue
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
                continue
    
    # 所有重试都失败
    return {
        'success': False,
        'error': f'抓取失败（已重试{max_retries}次）: {last_error}',
        'title': '',
        'content': '',
        'cover': ''
    }


def extract_csdn_content(soup, url):
    """提取CSDN文章内容"""
    try:
        # 提取标题
        title_elem = soup.select_one('h1.title-article, .title-article, #articleContentId h1')
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # 提取封面
        cover_elem = soup.select_one('.article-header img, .article-header-cover img')
        cover = cover_elem.get('src') or cover_elem.get('data-src') if cover_elem else ''
        
        # 提取正文内容（尝试多个选择器）
        content_elem = None
        selectors = [
            '#article_content',
            '.article_content',
            '.markdown_views',
            '.baidu_pl',
            '[id*="article_content"]',
            '[class*="article_content"]'
        ]
        
        for selector in selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        if not content_elem:
            return {
                'success': False,
                'error': '无法找到文章内容区域',
                'title': title,
                'content': '',
                'cover': cover
            }
        
        # 清理内容
        content = str(content_elem)
        
        return {
            'success': True,
            'title': title,
            'content': content,
            'cover': cover
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'提取CSDN内容失败: {str(e)}',
            'title': '',
            'content': '',
            'cover': ''
        }


def extract_juejin_content(soup, url):
    """提取掘金文章内容"""
    try:
        # 提取标题
        title_elem = soup.select_one('h1.article-title, .article-title')
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # 提取封面
        cover_elem = soup.select_one('.article-cover img, .cover img')
        cover = cover_elem.get('src') or cover_elem.get('data-src') if cover_elem else ''
        
        # 提取正文内容
        content_elem = soup.select_one('.article-content, .markdown-body, .article-viewer')
        if not content_elem:
            return {
                'success': False,
                'error': '无法找到文章内容区域',
                'title': title,
                'content': '',
                'cover': cover
            }
        
        content = str(content_elem)
        
        return {
            'success': True,
            'title': title,
            'content': content,
            'cover': cover
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'提取掘金内容失败: {str(e)}',
            'title': '',
            'content': '',
            'cover': ''
        }


def extract_aliyun_content(soup, url):
    """提取阿里云开发者社区文章内容"""
    try:
        # 提取标题
        title_elem = soup.select_one('h1, .article-title, [class*="title"]')
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # 提取封面
        cover_elem = soup.select_one('.article-cover img, .cover img, [class*="cover"] img')
        cover = cover_elem.get('src') or cover_elem.get('data-raw-src') if cover_elem else ''
        
        # 提取正文内容
        content_elem = soup.select_one('.article-content, .article-body, [class*="content"]')
        if not content_elem:
            return {
                'success': False,
                'error': '无法找到文章内容区域',
                'title': title,
                'content': '',
                'cover': cover
            }
        
        content = str(content_elem)
        
        return {
            'success': True,
            'title': title,
            'content': content,
            'cover': cover
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'提取阿里云内容失败: {str(e)}',
            'title': '',
            'content': '',
            'cover': ''
        }


def extract_cnblogs_content(soup, url):
    """提取博客园文章内容"""
    try:
        # 提取标题
        title_elem = soup.select_one('#cb_post_title_url, .postTitle, h1')
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # 提取封面
        cover_elem = soup.select_one('.postBody img:first-of-type')
        cover = cover_elem.get('src') if cover_elem else ''
        
        # 提取正文内容
        content_elem = soup.select_one('#cnblogs_post_body, .postBody')
        if not content_elem:
            return {
                'success': False,
                'error': '无法找到文章内容区域',
                'title': title,
                'content': '',
                'cover': cover
            }
        
        content = str(content_elem)
        
        return {
            'success': True,
            'title': title,
            'content': content,
            'cover': cover
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'提取博客园内容失败: {str(e)}',
            'title': '',
            'content': '',
            'cover': ''
        }


def extract_imooc_content(soup, url):
    """提取慕课网文章内容"""
    try:
        # 提取标题
        title_elem = soup.select_one('h1, .article-title')
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # 提取封面
        cover_elem = soup.select_one('.article-cover img, .cover img')
        cover = cover_elem.get('src') if cover_elem else ''
        
        # 提取正文内容
        content_elem = soup.select_one('.article-content, .article-body, .article-view')
        if not content_elem:
            return {
                'success': False,
                'error': '无法找到文章内容区域',
                'title': title,
                'content': '',
                'cover': cover
            }
        
        content = str(content_elem)
        
        return {
            'success': True,
            'title': title,
            'content': content,
            'cover': cover
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'提取慕课网内容失败: {str(e)}',
            'title': '',
            'content': '',
            'cover': ''
        }


def extract_tencent_content(soup, url):
    """提取腾讯云开发者社区文章内容"""
    try:
        # 提取标题
        title_elem = soup.select_one('h1, .article-title, [class*="title"]')
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # 提取封面
        cover_elem = soup.select_one('.article-cover img, .cover img')
        cover = cover_elem.get('src') if cover_elem else ''
        
        # 提取正文内容
        content_elem = soup.select_one('.article-content, .article-body, [class*="content"]')
        if not content_elem:
            return {
                'success': False,
                'error': '无法找到文章内容区域',
                'title': title,
                'content': '',
                'cover': cover
            }
        
        content = str(content_elem)
        
        return {
            'success': True,
            'title': title,
            'content': content,
            'cover': cover
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'提取腾讯云内容失败: {str(e)}',
            'title': '',
            'content': '',
            'cover': ''
        }


def extract_generic_content(soup, url):
    """通用内容提取策略"""
    try:
        # 提取标题
        title_elem = soup.select_one('h1, .title, [class*="title"]')
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # 提取封面
        cover_elem = soup.select_one('img[class*="cover"], img[class*="hero"], .cover img, .hero img')
        cover = cover_elem.get('src') or cover_elem.get('data-src') if cover_elem else ''
        
        # 尝试多个常见的内容选择器
        content_elem = None
        selectors = [
            'article',
            '.article-content',
            '.article-body',
            '.content',
            '#content',
            '.post-content',
            '.entry-content',
            'main',
            '[role="article"]'
        ]
        
        for selector in selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        if not content_elem:
            # 如果还是找不到，尝试找最大的div
            divs = soup.find_all('div', class_=re.compile(r'content|article|post|entry', re.I))
            if divs:
                content_elem = max(divs, key=lambda d: len(d.get_text()))
        
        if not content_elem:
            return {
                'success': False,
                'error': '无法找到文章内容区域，请手动复制HTML内容',
                'title': title,
                'content': '',
                'cover': cover
            }
        
        content = str(content_elem)
        
        return {
            'success': True,
            'title': title,
            'content': content,
            'cover': cover
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'提取内容失败: {str(e)}',
            'title': '',
            'content': '',
            'cover': ''
        }

