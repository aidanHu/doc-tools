#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 这个文件用于删除md文件中的所有图片，并删除由此产生的空白行

import os
import re
import glob

def process_markdown_file(file_path):
    """处理单个Markdown文件，删除所有图片标记及产生的空白行"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 匹配Markdown中的图片标记
        image_pattern = re.compile(r'!\[.*?\]\(.*?\)')
        
        # 处理每一行，删除图片标记
        new_lines = []
        modified = False
        
        for line in lines:
            # 检查这一行是否只包含图片标记(可能有空格)
            stripped_line = line.strip()
            if stripped_line and image_pattern.search(stripped_line):
                # 如果图片标记删除后这一行变为空，则跳过这一行
                cleaned_line = image_pattern.sub('', stripped_line)
                if cleaned_line.strip():
                    # 如果删除图片后还有其他内容，保留这一行
                    new_lines.append(image_pattern.sub('', line))
                else:
                    # 如果删除图片后这一行变为空，不添加到新内容中
                    modified = True
            else:
                # 不包含图片的行直接保留
                new_lines.append(line)
        
        # 检查是否有变化
        modified = modified or len(new_lines) != len(lines)
        
        # 写回文件
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        
        return modified
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return False

def process_markdown_folder(folder_path):
    """处理文件夹中的所有Markdown文件"""
    # 确保路径末尾有斜杠
    if not folder_path.endswith(os.sep):
        folder_path += os.sep
    
    # 获取所有md文件
    md_files = glob.glob(f"{folder_path}**/*.md", recursive=True)
    
    if not md_files:
        print(f"在 {folder_path} 中没有找到Markdown文件")
        return
    
    processed_count = 0
    modified_count = 0
    
    print(f"开始处理 {len(md_files)} 个Markdown文件...")
    
    for file_path in md_files:
        processed_count += 1
        if process_markdown_file(file_path):
            modified_count += 1
            print(f"已修改: {file_path}")
    
    print(f"\n处理完成!")
    print(f"共处理 {processed_count} 个文件")
    print(f"其中 {modified_count} 个文件被修改")

def main():
    print("Markdown文档图片清理工具")
    print("功能: 删除文档中的所有图片及由此产生的空白行\n")
    
    folder_path = input("请输入要处理的文件夹路径: ")
    
    # 验证文件夹是否存在
    if not os.path.isdir(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在!")
        return
    
    print(f"\n将处理文件夹: {folder_path}")
    confirm = input("确认继续? (y/n): ")
    
    if confirm.lower() == 'y':
        process_markdown_folder(folder_path)
    else:
        print("操作已取消")

if __name__ == "__main__":
    main()
