#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 主要用于匹配是否有使用过，如果使用过的文件就移走

import os
import pandas as pd

def get_files_in_directory(folder_path):
    """
    获取指定文件夹中的所有文件名（不含子文件夹，不含文件后缀）
    
    参数:
        folder_path: 要扫描的文件夹路径
        
    返回:
        文件名列表（无后缀）
    """
    try:
        # 确保路径存在
        if not os.path.exists(folder_path):
            print(f"错误: 路径 '{folder_path}' 不存在")
            return []
            
        # 获取文件夹中的所有条目
        all_items = os.listdir(folder_path)
        
        # 过滤出文件（不包括文件夹）并去除后缀
        files = []
        for item in all_items:
            full_path = os.path.join(folder_path, item)
            if os.path.isfile(full_path):
                # 去除文件后缀
                filename_without_ext = os.path.splitext(item)[0]
                files.append(filename_without_ext)
        
        return files
    except Exception as e:
        print(f"获取文件时出错: {e}")
        return []

def save_to_excel(file_list, output_excel):
    """
    将文件名列表保存到Excel文件
    
    参数:
        file_list: 文件名列表
        output_excel: 输出的Excel文件路径
    """
    try:
        # 创建DataFrame
        df = pd.DataFrame(file_list, columns=['文件名'])
        
        # 保存到Excel，不包含索引
        df.to_excel(output_excel, sheet_name='文件列表', index=False)
            
        print(f"文件名已成功保存到 {output_excel}")
    except Exception as e:
        print(f"保存Excel时出错: {e}")

def main():
    # 获取用户输入的文件夹路径
    folder_path = input("请输入要扫描的文件夹路径: ").strip()
    
    # 设置输出Excel文件路径（默认在当前目录下）
    output_excel = input("请输入保存的Excel文件名 (默认为'文件列表.xlsx'): ").strip()
    if not output_excel:
        output_excel = "文件列表.xlsx"
    if not output_excel.endswith('.xlsx'):
        output_excel += '.xlsx'
    
    # 获取文件列表
    files = get_files_in_directory(folder_path)
    
    if files:
        print(f"找到 {len(files)} 个文件")
        
        # 保存到Excel
        save_to_excel(files, output_excel)
    else:
        print("没有找到文件或文件夹为空")

if __name__ == "__main__":
    main()