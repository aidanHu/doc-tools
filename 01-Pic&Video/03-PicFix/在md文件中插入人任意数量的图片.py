import os
import random
import re
from typing import List, Optional, Tuple, Dict
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


def insert_images_randomly(text_content: str, image_urls: List[str]) -> str:
    """
    将图片随机插入到文档段落中 (确保插入所有提供的图片URL)
    
    Args:
        text_content: 原始文档内容
        image_urls: 图片URL列表
        
    Returns:
        处理后的文档内容
    """
    if not image_urls:
        return text_content
    
    markdown_images = [convert_url_to_markdown_image(url) for url in image_urls]
    num_images_to_insert = len(markdown_images)
            
    # 将文本按段落分割 (原始段落)
    paragraphs_original = [p.strip() for p in text_content.split('\n\n') if p.strip()]
    
    if not paragraphs_original:
        # 如果没有段落 (例如，文件是空的或只有单行无\n\n)
        # 就将所有图片追加到原始内容的末尾
        prefix = text_content.strip()
        if prefix: # 如果原始内容不为空，则在其后添加换行
            prefix += '\n\n'
        return prefix + '\n\n'.join(markdown_images)
        
    new_content_blocks = []
    # 为每张要插入的图片选择一个目标段落索引 (在其后插入)
    # 允许重复选择段落，如果图片数量多于段落数量
    target_para_indices_for_each_image = sorted(random.choices(range(len(paragraphs_original)), k=num_images_to_insert))
    
    current_image_idx = 0
    for para_idx, para_content in enumerate(paragraphs_original):
        new_content_blocks.append(para_content)
        # 检查有多少图片被指定要插入到当前这个段落之后
        while current_image_idx < num_images_to_insert and \
              target_para_indices_for_each_image[current_image_idx] == para_idx:
            new_content_blocks.append(markdown_images[current_image_idx])
            current_image_idx += 1
            
    # 重新组合文本
    return '\n\n'.join(new_content_blocks)


def process_markdown_folder(md_folder_path: str, image_txt_path: str, images_per_file: Dict[str, int] = None, default_image_count: Tuple[int, int] = (1, 3)) -> None:
    """
    处理Markdown文件夹，将图片随机插入到每个MD文件中
    
    Args:
        md_folder_path: Markdown文件夹路径
        image_txt_path: 包含图片URL的文件路径
        images_per_file: 每个文件插入的图片数量字典 {文件名: 图片数量}
        default_image_count: 默认图片数量范围 (最小值, 最大值)
    """
    try:
        # 规范化路径
        md_folder = os.path.normpath(os.path.expandvars(md_folder_path))
        
        # 验证文件夹路径
        if not os.path.exists(md_folder):
            raise FileNotFoundError(f"Markdown文件夹不存在: {md_folder}")
        if not os.path.isdir(md_folder):
            raise ValueError(f"路径不是文件夹: {md_folder}")
        
        # 设置默认图片数量配置
        if images_per_file is None:
            images_per_file = {}
        
        min_count, max_count = default_image_count
        
        # 加载所有图片URL
        try:
            all_image_urls = load_image_urls_from_file(image_txt_path)
            if not all_image_urls:
                print(f"[WARN] 未能从 {image_txt_path} 加载任何图片URL。将无法插入图片。")
                return # 如果没有图片URL，则不处理任何文件
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
                
                # 确定插入图片数量
                num_images: int
                if file_name in images_per_file:
                    num_images = images_per_file[file_name] # 完全采用用户指定的数量
                else:
                    num_images = random.randint(min_count, max_count) # 使用默认随机范围
                
                if num_images <= 0: # 如果指定数量为0或负数，则跳过
                    print(f"[INFO] ({idx+1}/{len(md_files)}) 跳过: {file_name} - 配置为插入 {num_images} 张图片。")
                    continue
                
                # (all_image_urls 在此必定不为空, 因为前面有检查)
                # 随机选择URL，允许重复使用以满足 num_images 的要求
                selected_urls = random.choices(all_image_urls, k=num_images)
                
                # 插入图片
                new_content = insert_images_randomly(content, selected_urls)
                
                # 写回文件
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                total_images_inserted += len(selected_urls) # 使用实际选择的URL数量
                print(f"[INFO] ({idx+1}/{len(md_files)}) 已处理: {file_name} - 插入了 {len(selected_urls)} 张图片")
                    
            except Exception as e:
                print(f"[ERROR] 处理文件 {os.path.basename(md_file)} 时出错: {str(e)}")
        
        print(f"[SUCCESS] 处理完成! 共处理 {len(md_files)} 个文件，总共插入 {total_images_inserted} 张图片")
        
    except Exception as e:
        print(f"[ERROR] 处理过程中发生错误: {str(e)}")
        print(f"[调试信息] 错误类型: {type(e).__name__}")


def parse_image_count_config(config_str: str) -> Dict[str, int]:
    """
    解析图片数量配置字符串
    
    Args:
        config_str: 格式为 "file1.md:2,file2.md:3" 的配置字符串
        
    Returns:
        配置字典 {文件名: 图片数量}
    """
    if not config_str or config_str.strip() == "":
        return {}
        
    result = {}
    try:
        pairs = config_str.split(',')
        for pair in pairs:
            if ':' in pair:
                file_name, count = pair.split(':', 1)
                file_name = file_name.strip()
                count = int(count.strip())
                if count > 0:
                    result[file_name] = count
    except Exception as e:
        print(f"[WARN] 解析图片数量配置失败: {str(e)}")
    
    return result


def main(md_folder_path: Optional[str] = None, 
         image_txt_path: Optional[str] = None,
         image_count_config: Optional[str] = None,
         default_min: int = 1,
         default_max: int = 3):
    """
    主函数，处理Markdown文件夹中的所有文件
    
    Args:
        md_folder_path: Markdown文件夹路径，如果为None则从用户获取
        image_txt_path: 包含图片URL的文件路径，如果为None则从用户获取
        image_count_config: 图片数量配置，格式为 "file1.md:2,file2.md:3"
        default_min: 默认最小图片数量
        default_max: 默认最大图片数量
    """
    try:
        # 如果参数为None，从用户获取输入
        if md_folder_path is None:
            md_folder_path = input("请输入Markdown文件夹路径: ").strip()
        
        if image_txt_path is None:
            image_txt_path = input("请输入图片URL文件路径: ").strip()
        
        if image_count_config is None:
            print("\n图片数量配置(可选):")
            print("- 默认每个文件将随机插入 {} 到 {} 张图片".format(default_min, default_max))
            print("- 若要为特定文件指定图片数量，请使用格式: file1.md:2,file2.md:3")
            print("- 留空则使用默认配置")
            image_count_config = input("请输入图片数量配置(可选): ").strip()
        
        # 解析图片数量配置
        images_per_file = parse_image_count_config(image_count_config)
        
        # 处理文件夹
        process_markdown_folder(
            md_folder_path, 
            image_txt_path, 
            images_per_file=images_per_file,
            default_image_count=(default_min, default_max)
        )
        
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断了操作")
    except Exception as e:
        print(f"[ERROR] 执行过程中发生错误: {str(e)}")
        print(f"[调试信息] 错误类型: {type(e).__name__}")


if __name__ == "__main__":
    main()
