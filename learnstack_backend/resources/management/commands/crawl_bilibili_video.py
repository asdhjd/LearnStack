"""
Bilibili 视频选集爬虫脚本

使用方法:
    python manage.py crawl_bilibili_video "https://www.bilibili.com/video/BV1gq1sBPECH/?share_source=copy_web"
    
或者:
    python manage.py crawl_bilibili_video "https://www.bilibili.com/video/BV1gq1sBPECH"
"""

import re
import json
import sys
from django.core.management.base import BaseCommand
from django.utils import timezone
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs


class Command(BaseCommand):
    help = '爬取 Bilibili 视频的选集信息并输出 JSON 格式'

    def add_arguments(self, parser):
        parser.add_argument(
            'url',
            type=str,
            help='Bilibili 视频链接'
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='输出 JSON 文件路径（可选，默认输出到控制台）'
        )

    def extract_bvid(self, url):
        """从 URL 中提取 BV 号"""
        # 匹配 BV 号
        bv_match = re.search(r'BV[a-zA-Z0-9]+', url)
        if bv_match:
            return bv_match.group(0)
        return None

    def get_video_info_from_api(self, bvid):
        """通过 Bilibili API 获取视频信息（更可靠的方法）"""
        try:
            # Bilibili 视频信息 API
            api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': f'https://www.bilibili.com/video/{bvid}'
            }
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {})
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'API 请求失败: {e}'))
        return None

    def parse_html_page(self, url):
        """解析 HTML 页面获取选集信息（备用方法）"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.bilibili.com/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 方法1: 从 script 标签中提取 JSON 数据（最可靠的方法）
            scripts = soup.find_all('script')
            for script in scripts:
                if not script.string:
                    continue
                
                script_text = script.string
                
                # 查找 window.__INITIAL_STATE__
                if 'window.__INITIAL_STATE__' in script_text:
                    # 尝试提取完整的 JSON 对象
                    # 匹配 window.__INITIAL_STATE__ = {...};
                    patterns = [
                        r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                        r'window\.__INITIAL_STATE__\s*=\s*({.+?})(?:\s*;|\s*$)',
                    ]
                    
                    for pattern in patterns:
                        json_match = re.search(pattern, script_text, re.DOTALL)
                        if json_match:
                            try:
                                json_str = json_match.group(1)
                                data = json.loads(json_str)
                                
                                # 尝试多种路径获取 pages
                                pages = (
                                    data.get('videoData', {}).get('pages', []) or
                                    data.get('videoData', {}).get('videos', []) or
                                    data.get('pages', [])
                                )
                                
                                if pages:
                                    return pages
                            except (json.JSONDecodeError, AttributeError) as e:
                                self.stdout.write(self.style.WARNING(f'JSON 解析错误: {e}'))
                                continue
                
                # 查找其他可能的 JSON 数据
                if 'videoData' in script_text or 'pages' in script_text:
                    # 尝试提取包含 pages 的 JSON
                    json_matches = re.findall(r'\{[^{}]*"pages"[^{}]*\}', script_text)
                    for match in json_matches:
                        try:
                            data = json.loads(match)
                            if 'pages' in data:
                                return data['pages']
                        except:
                            pass
            
            # 方法2: 从页面 DOM 中查找选集列表
            # 尝试多种选择器
            selectors = [
                '.list-box .item',
                '.episode-list .episode-item',
                '.video-page-list .item',
                '[class*="episode"]',
                '[class*="page-list"]',
                '[class*="video-page"]',
                '.cur-list .item',
                '.list-box-item'
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items and len(items) > 1:  # 至少要有2个才可能是选集列表
                    pages = []
                    for idx, item in enumerate(items, 1):
                        # 尝试多种方式提取标题
                        title = None
                        title_elem = (
                            item.find(['span', 'a', 'div', 'p'], class_=re.compile(r'title|name|part', re.I)) or
                            item.find('span', string=re.compile(r'.+')) or
                            item.find('a', string=re.compile(r'.+'))
                        )
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                        else:
                            # 直接获取文本
                            text = item.get_text(strip=True)
                            if text and len(text) < 100:  # 标题通常不会太长
                                title = text
                        
                        if title:
                            pages.append({
                                'page': idx,
                                'part': title
                            })
                    
                    if pages and len(pages) > 1:
                        return pages
            
            # 方法3: 尝试从特定的 DOM 结构提取（基于用户提供的 XPath）
            # XPath: /html/body/div[2]/div[2]/div[2]/div/div[6]/div[1]/div[2]/div/div[2]/div[1]/div[2]
            # 转换为大致的选择器路径
            body = soup.find('body')
            if body:
                # 尝试找到选集容器
                divs = body.find_all('div', recursive=True)
                for div in divs:
                    # 查找包含"选集"、"分P"等关键词的容器
                    text = div.get_text()
                    if any(keyword in text for keyword in ['选集', '分P', '分p', 'P1', 'P2']):
                        items = div.find_all(['div', 'li', 'a'], recursive=True)
                        if items:
                            pages = []
                            for idx, item in enumerate(items, 1):
                                title = item.get_text(strip=True)
                                if title and len(title) < 100:
                                    pages.append({
                                        'page': idx,
                                        'part': title
                                    })
                            if pages and len(pages) > 1:
                                return pages
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'HTML 解析失败: {e}'))
            import traceback
            self.stdout.write(self.style.WARNING(traceback.format_exc()))
        
        return None

    def handle(self, *args, **options):
        url = options['url']
        output_file = options.get('output')
        
        self.stdout.write(f'正在处理链接: {url}')
        
        # 提取 BV 号
        bvid = self.extract_bvid(url)
        if not bvid:
            self.stdout.write(self.style.ERROR('无法从 URL 中提取 BV 号'))
            return
        
        self.stdout.write(f'提取到 BV 号: {bvid}')
        
        # 优先使用 API 获取信息
        video_data = self.get_video_info_from_api(bvid)
        
        episodes = []
        
        if video_data:
            # 从 API 数据中提取选集信息
            pages = video_data.get('pages', [])
            if pages:
                self.stdout.write(f'通过 API 获取到 {len(pages)} 个选集')
                for page in pages:
                    page_num = page.get('page', 1)
                    title = page.get('part', '')
                    cid = page.get('cid', 0)
                    
                    # 构建视频 URL
                    if page_num == 1:
                        video_url = f"https://www.bilibili.com/video/{bvid}"
                    else:
                        video_url = f"https://www.bilibili.com/video/{bvid}?p={page_num}"
                    
                    episodes.append({
                        'title': title,
                        'video_url': video_url
                    })
        else:
            # 备用方法：解析 HTML 页面
            self.stdout.write('API 方法失败，尝试解析 HTML 页面...')
            pages = self.parse_html_page(url)
            
            if pages:
                self.stdout.write(f'通过 HTML 解析获取到 {len(pages)} 个选集')
                for idx, page in enumerate(pages, 1):
                    if isinstance(page, dict):
                        title = page.get('part', page.get('title', f'第{idx}集'))
                        page_num = page.get('page', idx)
                    else:
                        title = str(page)
                        page_num = idx
                    
                    # 构建视频 URL
                    if page_num == 1:
                        video_url = f"https://www.bilibili.com/video/{bvid}"
                    else:
                        video_url = f"https://www.bilibili.com/video/{bvid}?p={page_num}"
                    
                    episodes.append({
                        'title': title,
                        'video_url': video_url
                    })
            else:
                # 如果都失败了，至少返回第一集
                self.stdout.write(self.style.WARNING('无法获取选集信息，返回基本信息'))
                title = '第1集'
                if video_data:
                    title = video_data.get('title', title)
                episodes.append({
                    'title': title,
                    'video_url': f"https://www.bilibili.com/video/{bvid}"
                })
        
        if not episodes:
            self.stdout.write(self.style.ERROR('未能获取到任何选集信息'))
            return
        
        # 输出 JSON
        json_output = json.dumps(episodes, ensure_ascii=False, indent=2)
        
        if output_file:
            # 保存到文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            self.stdout.write(self.style.SUCCESS(f'结果已保存到: {output_file}'))
        else:
            # 输出到控制台
            self.stdout.write('\n' + '='*50)
            self.stdout.write('JSON 输出:')
            self.stdout.write('='*50)
            print(json_output)
            self.stdout.write('='*50)
        
        self.stdout.write(self.style.SUCCESS(f'\n成功处理 {len(episodes)} 个选集'))

