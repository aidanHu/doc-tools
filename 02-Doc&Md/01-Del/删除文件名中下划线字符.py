import os

def remove_underscores_from_filenames(folder_path):
    """
    删除指定文件夹中所有文件名中的下划线字符
    
    参数:
        folder_path (str): 要处理的文件夹路径
    """
    try:
        # 确保文件夹路径存在
        if not os.path.isdir(folder_path):
            print(f"错误: '{folder_path}' 不是一个有效的文件夹路径")
            return
        
        # 获取文件夹中的所有项目
        items = os.listdir(folder_path)
        
        # 计数器
        renamed_count = 0
        
        # 遍历所有项目
        for item in items:
            # 构建完整路径
            old_path = os.path.join(folder_path, item)
            
            # 只处理文件，不处理文件夹
            if os.path.isfile(old_path):
                # 如果文件名包含下划线
                if "_" in item:
                    # 创建新文件名（删除下划线）
                    new_name = item.replace("_", "")
                    new_path = os.path.join(folder_path, new_name)
                    
                    # 重命名文件
                    os.rename(old_path, new_path)
                    print(f"已重命名: '{item}' -> '{new_name}'")
                    renamed_count += 1
        
        if renamed_count > 0:
            print(f"\n完成! 共重命名了 {renamed_count} 个文件。")
        else:
            print("\n未找到包含下划线的文件。")
    
    except Exception as e:
        print(f"发生错误: {e}")

def main():
    print("=== 文件名下划线删除工具 ===")
    print("此脚本将删除指定文件夹中所有文件名中的下划线('_')字符")
    
    # 提示用户输入文件夹路径
    folder_path = input("\n请输入要处理的文件夹路径: ").strip()
    
    # 如果用户输入了路径，则执行处理
    if folder_path:
        print(f"\n开始处理文件夹: {folder_path}")
        remove_underscores_from_filenames(folder_path)
    else:
        print("未提供文件夹路径，操作已取消。")

if __name__ == "__main__":
    main()
