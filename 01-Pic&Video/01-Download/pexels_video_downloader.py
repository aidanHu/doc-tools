#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import time
import sys
from tqdm import tqdm
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv() # 从 .env 文件加载环境变量

# 用户配置 - 直接在这里修改
API_KEY = os.getenv("PEXELS_API_KEY")  # 替换为你的Pexels API密钥
ORIENTATION = "portrait"  # 视频方向: "landscape"(横屏) 或 "portrait"(竖屏)
OUTPUT_DIRECTORY = "videos"  # 相对于当前目录的文件夹名称
DOWNLOAD_DELAY = 5  # 每个视频下载后的等待时间(秒)

class PexelsVideoDownloader:
    def __init__(self, api_key):
        """初始化下载器"""
        self.api_key = api_key
        self.headers = {
            'Authorization': api_key
        }
        self.base_url = "https://api.pexels.com/videos/search"
        
    def search_videos(self, query, per_page=10, page=1, orientation=None):
        """搜索视频"""
        # 对查询词进行URL编码，确保多词查询和特殊字符正确处理
        encoded_query = quote(query)
        
        params = {
            'query': encoded_query,
            'per_page': per_page,
            'page': page
        }
        
        # 添加方向过滤（如果指定）
        if orientation and orientation in ['landscape', 'portrait']:
            params['orientation'] = orientation
            
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()  # 如果响应包含错误状态码，则引发异常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"搜索视频时出错: {e}")
            return None
        
    def download_video(self, video_url, save_path):
        """下载视频"""
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 KB
            
            with open(save_path, 'wb') as file, tqdm(
                desc=os.path.basename(save_path),
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(block_size):
                    file.write(data)
                    bar.update(len(data))
                    
            return True
        except requests.exceptions.RequestException as e:
            print(f"下载视频时出错: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)  # 删除可能部分下载的文件
            return False
    
    def download_videos_by_query(self, query, count=5, orientation=None, output_dir="downloads"):
        """根据查询下载指定数量的视频"""
        # 获取当前工作目录
        current_dir = os.getcwd()
        
        # 创建输出目录（相对于当前目录）
        full_output_dir = os.path.join(current_dir, output_dir)
        if not os.path.exists(full_output_dir):
            os.makedirs(full_output_dir)
            
        # 将查询词转换为合法的文件夹名称
        safe_query = "".join([c if c.isalnum() else "_" for c in query])
        query_dir = os.path.join(full_output_dir, safe_query)
        if not os.path.exists(query_dir):
            os.makedirs(query_dir)
            
        downloaded = 0
        page = 1
        
        print(f"搜索关键词: '{query}'")
        print(f"视频方向: {orientation}")
        print(f"保存目录: {query_dir}")
        print(f"计划下载: {count} 个视频")
        print("-" * 50)
        
        while downloaded < count:
            # 每页最多30个视频（Pexels API限制）
            per_page = min(30, count - downloaded)
            
            print(f"正在获取第 {page} 页视频...")
            result = self.search_videos(query, per_page=per_page, page=page, orientation=orientation)
            if not result or 'videos' not in result or not result['videos']:
                print(f"没有更多视频可供下载，已下载 {downloaded} 个视频")
                break
                
            videos = result['videos']
            print(f"找到 {len(videos)} 个视频")
            
            for video in videos:
                if downloaded >= count:
                    break
                    
                # 获取最高质量的视频文件
                video_files = sorted(video['video_files'], key=lambda x: x.get('height', 0) * x.get('width', 0), reverse=True)
                
                if not video_files:
                    continue
                    
                best_video = video_files[0]
                video_url = best_video['link']
                
                # 创建文件名
                file_ext = video_url.split('.')[-1].split('?')[0]  # 获取扩展名
                if not file_ext:
                    file_ext = 'mp4'  # 默认扩展名
                
                width = best_video.get('width', 0)
                height = best_video.get('height', 0)
                resolution = f"{width}x{height}"
                
                filename = f"{safe_query}_{video['id']}_{resolution}.{file_ext}"
                save_path = os.path.join(query_dir, filename)
                
                print(f"\n下载视频 {downloaded+1}/{count}: {filename}")
                if self.download_video(video_url, save_path):
                    downloaded += 1
                    print(f"成功下载: {filename}")
                else:
                    print(f"下载失败: {filename}")
                    
                # 添加延迟以避免API速率限制和IP封禁
                if downloaded < count:
                    print(f"等待 {DOWNLOAD_DELAY} 秒后继续下载...")
                    time.sleep(DOWNLOAD_DELAY)
                
            page += 1
            
            # 如果没有更多页面，退出循环
            if 'next_page' not in result or not result['next_page']:
                if downloaded < count:
                    print(f"没有更多视频可供下载，已下载 {downloaded} 个视频")
                break
                
        print(f"\n完成! 共下载 {downloaded} 个视频到 {query_dir}")
        return downloaded

def main():
    print("=" * 50)
    print("Pexels 视频下载工具")
    print("=" * 50)
    print(f"视频方向: {ORIENTATION}")
    print(f"保存目录: {os.path.join(os.getcwd(), OUTPUT_DIRECTORY)}")
    print("=" * 50)
    
    # 获取用户输入的关键词
    query = ""
    while not query:
        query = input("请输入搜索关键词: ").strip()
        if not query:
            print("错误: 关键词不能为空，请重新输入")
    
    # 获取下载数量
    try:
        count = int(input("请输入要下载的视频数量 [5]: ").strip() or "5")
    except ValueError:
        print("输入无效，使用默认值: 5")
        count = 5
    
    # 开始下载
    print("\n开始下载...")
    downloader = PexelsVideoDownloader(API_KEY)
    downloader.download_videos_by_query(query, count, ORIENTATION, OUTPUT_DIRECTORY)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序发生错误: {e}")
        sys.exit(1)
