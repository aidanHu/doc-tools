#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def process_markdown_file(file_path):
    """
    处理单个Markdown文件，添加二级标题并均匀分段
    """
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 去除可能已存在的二级标题（## 01、## 02等）
    content = re.sub(r'##\s+0[1-4].*?\n', '', content)
    
    # 提取文章正文，跳过可能存在的YAML头信息和一级标题
    # 跳过YAML头信息 (--- 到 ---)
    yaml_match = re.match(r'---\n.*?\n---\n', content, re.DOTALL)
    if yaml_match:
        # 如果有YAML头，从头结束后开始处理
        start_pos = yaml_match.end()
        title_part = content[:start_pos]
        main_content = content[start_pos:]
    else:
        title_part = ""
        main_content = content
    
    # 跳过一级标题 (# 开头的行)
    first_title_match = re.match(r'# .*?\n', main_content)
    if first_title_match:
        title_part += main_content[:first_title_match.end()]
        main_content = main_content[first_title_match.end():]
    
    # 查找开头的图片
    image_pattern = r'!\[.*?\]\(.*?\)'
    header_images = ""
    
    # 查找文章开头所有的图片
    image_matches = re.findall(r'^' + image_pattern + r'\s*\n', main_content, re.MULTILINE)
    if image_matches:
        for match in image_matches:
            # 将图片从主内容中移除并添加到标题部分
            main_content = main_content.replace(match, '', 1)
            header_images += match
        
        # 如果图片后面有空行，也添加到标题部分
        main_content = re.sub(r'^\s*\n', '', main_content, 1)
        
        # 将图片添加到标题部分
        title_part += header_images + "\n\n"
    
    # 按段落分割内容（空行作为分隔符）
    paragraphs = re.split(r'\n\s*\n', main_content.strip())
    
    # 计算每个小节应该包含的段落数量
    total_paragraphs = len(paragraphs)
    paragraphs_per_section = total_paragraphs // 4
    remainder = total_paragraphs % 4
    
    # 初始化结果
    result = title_part if title_part else ""
    
    # 分配段落到各个小节
    current_paragraph = 0
    for section in range(1, 5):
        # 添加二级标题
        section_title = f"## {section:02d}\n\n"
        result += section_title
        
        # 计算当前小节应包含的段落数
        section_paragraphs = paragraphs_per_section
        if section <= remainder:
            section_paragraphs += 1
        
        # 添加该小节的段落
        for i in range(section_paragraphs):
            if current_paragraph < total_paragraphs:
                result += paragraphs[current_paragraph] + "\n\n"
                current_paragraph += 1
    
    # 保存修改后的内容到原始文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(result.strip() + "\n")
    
    return True

def process_folder(folder_path):
    """
    处理指定文件夹中的所有Markdown文件
    """
    success_count = 0
    failed_files = []
    
    # 检查目录是否存在
    if not os.path.isdir(folder_path):
        print(f"错误: 目录 '{folder_path}' 不存在")
        return
    
    # 处理文件夹中的所有markdown文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.md'):
            file_path = os.path.join(folder_path, filename)
            try:
                if process_markdown_file(file_path):
                    success_count += 1
                    print(f"成功处理: {filename}")
                else:
                    failed_files.append(filename)
            except Exception as e:
                print(f"处理 {filename} 时出错: {str(e)}")
                failed_files.append(filename)
    
    # 输出处理结果统计
    print(f"\n处理完成! 成功处理 {success_count} 个文件")
    if failed_files:
        print(f"失败文件数: {len(failed_files)}")
        print("失败的文件列表:")
        for file in failed_files:
            print(f"- {file}")

if __name__ == "__main__":
    print("Markdown文件二级标题分段工具")
    print("=" * 40)
    
    # 提示用户输入文件夹路径
    folder_path = input("请输入包含Markdown文件的文件夹路径: ")
    
    # 处理用户输入的路径
    folder_path = folder_path.strip()
    
    # 如果用户输入的路径包含引号，则去除
    if (folder_path.startswith('"') and folder_path.endswith('"')) or \
       (folder_path.startswith("'") and folder_path.endswith("'")):
        folder_path = folder_path[1:-1]
    
    # 处理文件夹
    process_folder(folder_path)