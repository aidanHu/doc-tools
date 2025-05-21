#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 这个文件的主要作用是根据excel中提供的文件名，匹配指定文件夹中的文件，如果文件夹中存在Excel中不存在的文件，就移走

import os
import shutil
import pandas as pd

def read_excel_filenames(excel_file):
    """
    从Excel文件中读取文件名列表
    
    参数:
        excel_file: Excel文件路径
        
    返回:
        包含文件名的集合
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(excel_file, engine='openpyxl')
        
        # 查找包含文件名的列
        filename_column = None
        for column in df.columns:
            if '文件名' in column.lower():
                filename_column = column
                break
        
        if filename_column is None:
            # 如果没有找到名为"文件名"的列，使用第一列
            filename_column = df.columns[0]
            
        # 提取文件名并转换为集合
        filenames = set(df[filename_column].dropna().astype(str).tolist())
        return filenames
    
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return set()

def compare_and_move_files(folder_path, excel_filenames, destination_folder):
    """
    比对文件夹中的文件与Excel中的文件名，移动不在Excel中的文件
    只对比不含后缀的文件名
    
    参数:
        folder_path: 要扫描的文件夹路径
        excel_filenames: Excel中的文件名集合(不含后缀)
        destination_folder: 移动文件的目标文件夹
    
    返回:
        移动的文件数量
    """
    # 确保目标文件夹存在
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        print(f"创建目标文件夹: {destination_folder}")
    
    moved_count = 0
    
    try:
        # 获取文件夹中的所有文件
        all_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        # 对比并移动文件
        for filename in all_files:
            # 提取不含后缀的文件名进行对比
            filename_without_ext = os.path.splitext(filename)[0]
            
            if filename_without_ext not in excel_filenames:
                # 文件名不在Excel列表中，需要移动
                source_path = os.path.join(folder_path, filename)
                dest_path = os.path.join(destination_folder, filename)
                
                # 检查目标文件夹中是否已存在同名文件
                if os.path.exists(dest_path):
                    base, extension = os.path.splitext(filename)
                    i = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{base}_{i}{extension}"
                        dest_path = os.path.join(destination_folder, new_filename)
                        i += 1
                
                # 移动文件
                shutil.move(source_path, dest_path)
                print(f"已移动: {filename} -> {destination_folder}")
                moved_count += 1
                
        return moved_count
    
    except Exception as e:
        print(f"比对和移动文件时出错: {e}")
        return moved_count

def main():
    # 获取用户输入
    excel_file = input("请输入Excel文件路径: ").strip()
    source_folder = input("请输入要扫描的源文件夹路径: ").strip()
    destination_folder = input("请输入移动文件的目标文件夹路径: ").strip()
    
    # 验证路径
    if not os.path.exists(excel_file):
        print(f"错误: Excel文件 '{excel_file}' 不存在")
        return
    
    if not os.path.exists(source_folder):
        print(f"错误: 源文件夹 '{source_folder}' 不存在")
        return
    
    # 读取Excel中的文件名
    excel_filenames = read_excel_filenames(excel_file)
    
    if not excel_filenames:
        print("Excel文件中没有找到文件名，请检查Excel文件格式")
        return
    
    print(f"从Excel中读取了 {len(excel_filenames)} 个文件名")
    
    # 显示部分Excel文件名作为示例
    sample_size = min(5, len(excel_filenames))
    if sample_size > 0:
        sample_names = list(excel_filenames)[:sample_size]
        print(f"Excel中的部分文件名示例: {', '.join(sample_names)}")
    
    # 比对并移动文件
    moved_count = compare_and_move_files(source_folder, excel_filenames, destination_folder)
    
    # 打印结果
    print(f"\n处理完成:")
    print(f"- Excel中的文件名数量: {len(excel_filenames)}")
    print(f"- 移动的文件数量: {moved_count}")
    
    # 计算留在源文件夹的文件数量
    remaining_files = len([f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))])
    print(f"- 保留在源文件夹的文件数量: {remaining_files}")
    
    if moved_count == 0 and remaining_files > 0:
        print("\n提示: 没有移动任何文件。请确认Excel中的文件名是否不含后缀，与源文件夹中的文件名(不含后缀)匹配。")

if __name__ == "__main__":
    main()