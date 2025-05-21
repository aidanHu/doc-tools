import os
import re
from pathlib import Path

def remove_time_mark(file_path):
    """删除指定 Markdown 文件最后一行的时间标记"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        if not lines:
            print(f"文件 {file_path} 为空，跳过处理")
            return False
        
        # 检查最后一行是否是时间标记（格式如 "19:15"）
        last_line = lines[-1].strip()
        time_pattern = re.compile(r'^\d{1,2}:\d{2}$')
        
        if time_pattern.match(last_line):
            # 删除最后一行
            lines = lines[:-1]
            
            # 如果新的最后一行是空行，也删除它
            while lines and lines[-1].strip() == '':
                lines = lines[:-1]
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            
            print(f"已从 {file_path} 删除时间标记 '{last_line}'")
            return True
        else:
            print(f"文件 {file_path} 最后一行不是时间标记，跳过处理")
            return False
    
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        return False

def main():
    print("=== Markdown 文件时间标记删除工具 ===")
    
    # 要求用户输入路径
    path_input = input("请输入要处理的 Markdown 文件或目录路径: ").strip()
    path = Path(path_input)
    
    if not path.exists():
        print(f"错误：路径 '{path}' 不存在")
        return
    
    # 如果是目录，询问是否递归处理
    recursive = False
    if path.is_dir():
        recursive_input = input("是否递归处理所有子目录中的 Markdown 文件？(y/n): ").strip().lower()
        recursive = recursive_input in ('y', 'yes')
    
    # 处理文件或目录
    processed_count = 0
    if path.is_file() and path.suffix.lower() == '.md':
        if remove_time_mark(path):
            processed_count += 1
    elif path.is_dir():
        if recursive:
            for md_file in path.glob('**/*.md'):
                if remove_time_mark(md_file):
                    processed_count += 1
        else:
            for md_file in path.glob('*.md'):
                if remove_time_mark(md_file):
                    processed_count += 1
    else:
        print(f"错误：{path} 不是有效的 Markdown 文件或目录")
    
    print(f"\n处理完成！成功处理了 {processed_count} 个文件。")

if __name__ == '__main__':
    main()
