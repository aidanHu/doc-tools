import os
import requests
import time
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv() # 从 .env 文件加载环境变量

# 在这里直接设置你的Pexels API密钥
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY") # 替换为你的实际API密钥

def search_and_download_images(query, per_page=10, download_folder="pexels_downloads"):
    """
    从Pexels搜索并下载图片
    
    参数:
        query (str): 搜索关键词
        per_page (int): 每页返回的图片数量
        download_folder (str): 下载图片的保存文件夹
    """
    # 创建下载文件夹
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # 创建特定关键词的子文件夹
    query_folder = os.path.join(download_folder, query.replace(" ", "_"))
    if not os.path.exists(query_folder):
        os.makedirs(query_folder)
    
    # Pexels API搜索端点
    url = "https://api.pexels.com/v1/search"
    
    # 设置请求头
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    # 设置请求参数
    params = {
        "query": query,
        "per_page": per_page,
        "page": 1
    }
    
    try:
        # 发送API请求
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # 检查请求是否成功
        
        data = response.json()
        
        if "photos" not in data or len(data["photos"]) == 0:
            print(f"未找到与 '{query}' 相关的图片。")
            return
        
        total_photos = len(data["photos"])
        print(f"找到 {total_photos} 张与 '{query}' 相关的图片，开始下载...")
        
        # 下载图片
        for i, photo in enumerate(data["photos"]):
            image_url = photo["src"]["original"]
            photographer = photo["photographer"]
            photo_id = photo["id"]
            
            # 构建文件名
            file_extension = image_url.split("?")[0].split(".")[-1]
            filename = f"{photo_id}_{photographer.replace(' ', '_')}.{file_extension}"
            file_path = os.path.join(query_folder, filename)
            
            # 下载图片
            print(f"正在下载图片 {i+1}/{total_photos}: {filename}")
            download_image(image_url, file_path)
            
            # 避免请求过于频繁
            time.sleep(0.5)
        
        print(f"\n下载完成！图片已保存到 '{query_folder}' 文件夹")
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

def download_image(url, file_path):
    """下载图片并显示进度条"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        
        with open(file_path, 'wb') as file, tqdm(
            desc="下载进度",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                bar.update(len(data))
                file.write(data)
                
        return True
    except Exception as e:
        print(f"下载图片时出错: {e}")
        return False

def main():
    print("欢迎使用Pexels图片下载工具！")
    
    while True:
        query = input("\n请输入搜索关键词 (输入'exit'退出): ")
        
        if query.lower() == 'exit':
            print("程序已退出。")
            break
        
        per_page = input("请输入要下载的图片数量 (默认10): ")
        per_page = int(per_page) if per_page.isdigit() else 10
        
        search_and_download_images(query, per_page)

if __name__ == "__main__":
    main()
