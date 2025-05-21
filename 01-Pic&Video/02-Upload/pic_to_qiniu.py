import os
import sys
import random
import string
import mimetypes
from qiniu import Auth, put_file, etag
import qiniu.config
import time
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件中的环境变量

def generate_random_string(length=10):
    """生成指定长度的随机字符串"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def is_image_file(filename):
    """判断文件是否为图片"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type and mime_type.startswith('image/')

def upload_to_qiniu(local_file, key, access_key, secret_key, bucket_name, domain):
    """上传文件到七牛云"""
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    
    print(f"正在上传: {local_file} -> {key}")
    
    # 上传文件
    start_time = time.time()
    ret, info = put_file(token, key, local_file, version='v2')
    end_time = time.time()
    
    if info.status_code == 200:
        # 返回文件的访问链接
        url = f"http://{domain}/{key}"
        file_size = os.path.getsize(local_file) / 1024  # KB
        upload_time = end_time - start_time
        speed = file_size / upload_time if upload_time > 0 else 0
        
        print(f"✅ 上传成功: {os.path.basename(local_file)}")
        print(f"   大小: {file_size:.2f} KB")
        print(f"   耗时: {upload_time:.2f} 秒")
        print(f"   速度: {speed:.2f} KB/s")
        print(f"   链接: {url}")
        print("-" * 80)
        
        return url
    else:
        print(f"❌ 上传失败: {os.path.basename(local_file)}")
        print(f"   错误信息: {info}")
        print("-" * 80)
        return None

def upload_images_in_directory(directory, access_key, secret_key, bucket_name, domain, output_file):
    """上传目录中的所有图片"""
    # 获取所有图片文件
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if is_image_file(file_path):
                image_files.append(file_path)
    
    total_files = len(image_files)
    print(f"找到 {total_files} 个图片文件待上传")
    print("=" * 80)
    
    successful_uploads = 0
    failed_uploads = 0
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for index, file_path in enumerate(image_files, 1):
            # 生成随机文件名，保留原始扩展名
            _, ext = os.path.splitext(file_path)
            random_name = generate_random_string(16) + ext
            
            print(f"[{index}/{total_files}] 进度: {index/total_files*100:.2f}%")
            
            # 上传到七牛云
            url = upload_to_qiniu(file_path, random_name, access_key, secret_key, bucket_name, domain)
            
            if url:
                f.write(f"{url}\n")
                successful_uploads += 1
            else:
                failed_uploads += 1
    
    print("=" * 80)
    print(f"上传完成! 总计: {total_files} 个文件")
    print(f"成功: {successful_uploads} 个")
    print(f"失败: {failed_uploads} 个")
    print(f"所有链接已保存到 {output_file}")

def main():
    print("=" * 80)
    print("七牛云图片批量上传工具")
    print("=" * 80)
    
    # 七牛云配置信息
    access_key = os.getenv('QINIU_ACCESS_KEY')
    secret_key = os.getenv('QINIU_SECRET_KEY')
    bucket_name = os.getenv('QINIU_BUCKET_NAME')
    domain = os.getenv('QINIU_DOMAIN')
    
    # 检查环境变量是否都已设置
    if not all([access_key, secret_key, bucket_name, domain]):
        print("错误：部分或全部七牛云配置环境变量未设置。请检查您的 .env 文件。")
        print("需要设置以下环境变量：QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME, QINIU_DOMAIN")
        sys.exit(1)
        
    # 从用户处获取要上传的目录
    while True:
        directory = input("请输入要上传的图片所在目录的完整路径: ").strip()
        if os.path.isdir(directory):
            break
        else:
            print(f"错误: '{directory}' 不是一个有效的目录，或者目录不存在。请重新输入。")
            
    # 从用户处获取输出文件名
    output_file_name = input("请输入保存链接的输出文件名 (例如: uploaded_links.txt): ").strip()
    # 默认将输出文件保存在脚本所在目录下
    output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_file_name)
    
    print(f"图片将从目录: {directory} 上传")
    print(f"上传链接将保存到: {output_file_path}")
    
    # if not os.path.isdir(directory):
    #     print(f"错误: {directory} 不是有效的目录")
    #     return
    
    print("\n开始上传过程...\n")
    upload_images_in_directory(directory, access_key, secret_key, bucket_name, domain, output_file_path)

if __name__ == "__main__":
    main()
