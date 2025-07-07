#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MD文件标点分段工具
功能：根据句号（。）、问号（？）、感叹号（！）对md文件内容进行分段，但排除引号内的标点
作者：Assistant
"""

import os
import re
import argparse
from pathlib import Path


def process_content(content):
    """
    处理文本内容，根据标点符号进行分段，但排除引号内的标点
    
    Args:
        content (str): 要处理的文本内容
        
    Returns:
        str: 处理后的文本内容
    """
    result = []
    i = 0
    in_quotes = False
    quote_pairs = {
        '"': '"',
        '"': '"', 
        "'": "'",
        "'": "'",
        '"': '"',  # 处理英文双引号
        "'": "'"   # 处理英文单引号
    }
    current_quote_start = None
    
    while i < len(content):
        char = content[i]
        
        # 检查是否遇到开始引号
        if not in_quotes and char in quote_pairs:
            in_quotes = True
            current_quote_start = char
            result.append(char)
        # 检查是否遇到结束引号
        elif in_quotes and char == quote_pairs.get(current_quote_start, ''):
            in_quotes = False
            current_quote_start = None
            result.append(char)
        # 处理标点符号
        elif char in ['。', '？', '！']:
            result.append(char)
            # 只有在引号外才添加段落分隔
            if not in_quotes:
                result.append('\n\n')
        else:
            result.append(char)
        
        i += 1
    
    processed_content = ''.join(result)
    
    # 去除多余的空行（超过两个连续换行的情况）
    processed_content = re.sub(r'\n{3,}', r'\n\n', processed_content)
    
    return processed_content


def process_md_file(file_path, output_path=None):
    """
    处理单个md文件，根据标点符号进行分段
    
    Args:
        file_path (str): 输入文件路径
        output_path (str): 输出文件路径，如果为None则覆盖原文件
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 处理内容
        processed_content = process_content(content)
        
        # 确定输出路径
        if output_path is None:
            output_path = file_path
        
        # 写入处理后的内容
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(processed_content)
        
        print(f"✅ 已处理文件: {file_path}")
        if output_path != file_path:
            print(f"   输出到: {output_path}")
            
    except Exception as e:
        print(f"❌ 处理文件失败 {file_path}: {str(e)}")


def process_directory(directory_path, output_directory=None):
    """
    处理目录中的所有md文件
    
    Args:
        directory_path (str): 输入目录路径
        output_directory (str): 输出目录路径，如果为None则覆盖原文件
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"❌ 目录不存在: {directory_path}")
        return
    
    # 查找所有md文件
    md_files = list(directory.glob("*.md"))
    
    if not md_files:
        print(f"❌ 在目录 {directory_path} 中未找到md文件")
        return
    
    print(f"🔍 找到 {len(md_files)} 个md文件")
    
    for md_file in md_files:
        if output_directory:
            # 创建输出目录
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / md_file.name
        else:
            output_path = None
        
        process_md_file(str(md_file), str(output_path) if output_path else None)


def main():
    parser = argparse.ArgumentParser(description='根据标点符号分段MD文件内容')
    parser.add_argument('path', help='要处理的文件或目录路径')
    parser.add_argument('-o', '--output', help='输出路径（文件或目录）')
    parser.add_argument('--preview', action='store_true', help='预览模式，显示处理后的内容但不保存')
    
    args = parser.parse_args()
    
    input_path = Path(args.path)
    
    if not input_path.exists():
        print(f"❌ 路径不存在: {args.path}")
        return
    
    if args.preview and input_path.is_file():
        # 预览模式
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            processed_content = process_content(content)
            
            print("📋 预览处理后的内容：")
            print("-" * 50)
            print(processed_content)
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ 预览失败: {str(e)}")
        return
    
    if input_path.is_file():
        # 处理单个文件
        if input_path.suffix.lower() != '.md':
            print("❌ 请选择md文件")
            return
        process_md_file(str(input_path), args.output)
    elif input_path.is_dir():
        # 处理目录
        process_directory(str(input_path), args.output)
    else:
        print("❌ 无效的路径类型")


def test_quote_processing():
    """测试引号处理功能"""
    test_content = '''"老汤，电车真就这么猛吗？"
"SU7真能把BBA按地上摩擦？"
这是正常的句子。这里应该分段！但是"引号内的内容。不应该分段！"继续写。'''
    
    result = process_content(test_content)
    print("🧪 测试引号处理功能：")
    print("原文：")
    print(test_content)
    print("\n处理后：")
    print(result)
    print("\n" + "="*50)


if __name__ == "__main__":
    print("🚀 MD文件标点分段工具")
    print("=" * 40)
    
    # 如果没有命令行参数，提供交互式使用方式
    import sys
    if len(sys.argv) == 1:
        print("📝 交互式模式")
        
        # 先运行测试
        test_quote_processing()
        
        print("请输入要处理的文件或目录路径:")
        path = input().strip()
        
        if not path:
            print("❌ 路径不能为空")
            sys.exit(1)
        
        print("是否预览处理效果？(y/n):")
        preview = input().strip().lower() == 'y'
        
        if preview and Path(path).is_file():
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                processed_content = process_content(content)
                
                print("\n📋 预览处理后的内容：")
                print("-" * 50)
                print(processed_content[:500] + "..." if len(processed_content) > 500 else processed_content)
                print("-" * 50)
                
                print("\n确认处理？(y/n):")
                if input().strip().lower() != 'y':
                    print("❌ 已取消操作")
                    sys.exit(0)
                    
            except Exception as e:
                print(f"❌ 预览失败: {str(e)}")
                sys.exit(1)
        
        # 执行处理
        input_path = Path(path)
        if input_path.is_file():
            process_md_file(path)
        elif input_path.is_dir():
            process_directory(path)
        else:
            print("❌ 无效的路径")
    else:
        main()
    
    print("\n✨ 处理完成！") 