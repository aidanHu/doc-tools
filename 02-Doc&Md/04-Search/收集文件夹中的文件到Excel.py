import os
import pandas as pd
from pathlib import Path

def collect_filenames(directory):
    """
    Recursively collect filenames from a directory and its subdirectories,
    excluding extensions.
    
    Returns a list of filenames without extensions.
    """
    filenames = []
    
    # Walk through directory and subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Get filename without extension
            filename_without_ext = Path(file).stem
            filenames.append(filename_without_ext)
    
    return filenames

def main():
    # Ask for directory path
    directory = input("请输入文件夹路径: ")
    
    # Validate directory path
    if not os.path.isdir(directory):
        print(f"错误: '{directory}' 不是有效的文件夹路径。")
        return
    
    # Ask for output file path
    output_file = input("请输入输出的Excel文件路径 (默认: filenames.xlsx): ")
    if not output_file:
        output_file = "filenames.xlsx"
    
    try:
        # Collect filenames
        filenames = collect_filenames(directory)
        
        # Create DataFrame
        df = pd.DataFrame(filenames, columns=["文件名"])
        
        # Save to Excel
        df.to_excel(output_file, index=False)
        
        print(f"成功保存 {len(filenames)} 个文件名到 {output_file}")
    
    except PermissionError:
        print("错误: 访问某些文件夹或文件时权限被拒绝。")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()