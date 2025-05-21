import os
import random
import re
from typing import List, Optional
import glob


def load_image_urls_from_file(image_txt_path: str) -> List[str]:
    """
    从文件中加载图片URL
    
    Args:
        image_txt_path: 包含图片URL的文件路径
        
    Returns:
        图片URL列表
    """
    # 处理文件路径
    expanded_path = os.path.expandvars(image_txt_path)
    normalized_path = os.path.normpath(expanded_path)
    
    # 验证文件路径
    if not os.path.exists(normalized_path):
        raise FileNotFoundError(f"文件不存在: {normalized_path}")
    if not os.path.isfile(normalized_path):
        raise ValueError(f"路径不是文件: {normalized_path}")
        
    # 读取图片URL
    image_urls = []
    
    with open(normalized_path, 'r', encoding='utf-8') as f:
        for line in f:
            url = line.strip()
            if url and not url.startswith('#'):  # 忽略空行和注释行
                image_urls.append(url)
    
    if not image_urls:
        print(f"[WARN] 在文件中未找到有效的图片URL: {normalized_path}")
    
    return image_urls


def convert_url_to_markdown_image(url: str) -> str:
    """
    将URL转换为Markdown图片格式
    
    Args:
        url: 图片URL
        
    Returns:
        Markdown格式的图片引用
    """
    # 从URL中提取文件名作为alt文本
    try:
        file_name = os.path.basename(url).split('.')[0]
        # 处理特殊字符
        alt_text = re.sub(r'[^a-zA-Z0-9]', '', file_name) or "image"
    except:
        alt_text = "image"
    
    return f"![{alt_text}]({url})"


def insert_image_after_h1(text_content: str, image_url: str) -> str:
    """
    将单张图片插入到文档中：如果有一级标题则插入在一级标题之后，否则插入在文档开头
    
    Args:
        text_content: 原始文档内容
        image_url: 图片URL
        
    Returns:
        处理后的文档内容
    """
    if not image_url:
        return text_content
    
    # 将URL转换为Markdown图片格式
    markdown_image = convert_url_to_markdown_image(image_url)
    
    # 如果文档为空，直接返回图片
    if not text_content.strip():
        return markdown_image
    
    # 查找第一个一级标题（确保它是以单个#开头，不是##或更多）
    h1_pattern = re.compile(r'^# [^\n]+', re.MULTILINE)
    h1_match = h1_pattern.search(text_content)
    
    if h1_match:
        # 找到一级标题，在其后插入图片
        h1_end_pos = h1_match.end()
        return text_content[:h1_end_pos] + "\n\n" + markdown_image + text_content[h1_end_pos:]
    else:
        # 没有找到一级标题，在文档开头插入图片
        return markdown_image + "\n\n" + text_content


def process_markdown_folder(md_folder_path: str, image_txt_path: str) -> None:
    """
    处理Markdown文件夹，将一张图片插入到每个MD文件中
    
    Args:
        md_folder_path: Markdown文件夹路径
        image_txt_path: 包含图片URL的文件路径
    """
    try:
        # 规范化路径
        md_folder = os.path.normpath(os.path.expandvars(md_folder_path))
        
        # 验证文件夹路径
        if not os.path.exists(md_folder):
            raise FileNotFoundError(f"Markdown文件夹不存在: {md_folder}")
        if not os.path.isdir(md_folder):
            raise ValueError(f"路径不是文件夹: {md_folder}")
        
        # 加载所有图片URL
        try:
            all_image_urls = load_image_urls_from_file(image_txt_path)
            if not all_image_urls:
                print(f"[ERROR] 未能从 {image_txt_path} 加载任何图片URL")
                return
            print(f"[INFO] 成功加载 {len(all_image_urls)} 个图片URL")
        except Exception as e:
            print(f"[ERROR] 加载图片文件失败: {str(e)}")
            return
            
        # 获取所有MD文件
        md_files = glob.glob(os.path.join(md_folder, "*.md"))
        if not md_files:
            print(f"[WARN] 在 {md_folder} 中未找到任何Markdown文件")
            return
            
        print(f"[INFO] 开始处理 {len(md_files)} 个Markdown文件")
        
        # 处理每个文件
        total_images_inserted = 0
        
        for idx, md_file in enumerate(md_files):
            try:
                file_name = os.path.basename(md_file)
                
                # 读取文件内容
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 随机选择一个URL
                selected_url = random.choice(all_image_urls)
                
                # 插入图片
                new_content = insert_image_after_h1(content, selected_url)
                
                # 写回文件
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                total_images_inserted += 1
                print(f"[INFO] ({idx+1}/{len(md_files)}) 已处理: {file_name} - 已插入1张图片")
                    
            except Exception as e:
                print(f"[ERROR] 处理文件 {os.path.basename(md_file)} 时出错: {str(e)}")
        
        print(f"[SUCCESS] 处理完成! 共处理 {len(md_files)} 个文件，总共插入 {total_images_inserted} 张图片")
        
    except Exception as e:
        print(f"[ERROR] 处理过程中发生错误: {str(e)}")
        print(f"[调试信息] 错误类型: {type(e).__name__}")


def main(md_folder_path: Optional[str] = None, 
         image_txt_path: Optional[str] = None):
    """
    主函数，处理Markdown文件夹中的所有文件
    
    Args:
        md_folder_path: Markdown文件夹路径，如果为None则从用户获取
        image_txt_path: 包含图片URL的文件路径，如果为None则从用户获取
    """
    try:
        # 如果参数为None，从用户获取输入
        if md_folder_path is None:
            md_folder_path = input("请输入Markdown文件夹路径: ").strip()
        
        if image_txt_path is None:
            image_txt_path = input("请输入图片URL文件路径: ").strip()
        
        # 处理文件夹
        process_markdown_folder(md_folder_path, image_txt_path)
        
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断了操作")
    except Exception as e:
        print(f"[ERROR] 执行过程中发生错误: {str(e)}")
        print(f"[调试信息] 错误类型: {type(e).__name__}")


if __name__ == "__main__":
    main()
