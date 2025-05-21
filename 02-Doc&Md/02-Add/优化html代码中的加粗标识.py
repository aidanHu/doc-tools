import os
import re
import glob

def convert_markdown_bold_to_html(content):
    """将**文本**格式转换为<strong>文本</strong>格式"""
    # 使用正则表达式查找所有的**文本**格式
    pattern = r'\*\*([^*]+)\*\*'
    
    # 替换为<strong>文本</strong>
    converted_content = re.sub(pattern, r'<strong>\1</strong>', content)
    
    return converted_content

def process_txt_files(folder_path):
    """处理指定文件夹中的所有TXT文件"""
    # 获取文件夹中所有的TXT文件
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    
    if not txt_files:
        print(f"在 {folder_path} 中没有找到TXT文件")
        return
    
    total_files = len(txt_files)
    processed_files = 0
    modified_files = 0
    
    print(f"找到 {total_files} 个TXT文件")
    
    for file_path in txt_files:
        try:
            # 读取TXT文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 转换格式
            converted_content = convert_markdown_bold_to_html(content)
            
            # 统计替换次数
            original_count = content.count('**')
            converted_count = converted_content.count('**')
            replacements = (original_count - converted_count) // 2
            
            # 如果内容有变化，则写回文件
            if content != converted_content:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(converted_content)
                print(f"✓ 已处理: {os.path.basename(file_path)} (替换了 {replacements} 处)")
                modified_files += 1
            else:
                print(f"- 无需修改: {os.path.basename(file_path)}")
                
            processed_files += 1
                
        except Exception as e:
            print(f"✗ 处理 {file_path} 时出错: {str(e)}")
    
    print(f"\n处理完成! 共处理 {processed_files} 个文件，修改了 {modified_files} 个文件。")

def process_single_file(file_path):
    """处理单个TXT文件"""
    try:
        print(f"正在处理: {os.path.basename(file_path)}")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 转换格式
        converted_content = convert_markdown_bold_to_html(content)
        
        # 统计替换次数
        original_count = content.count('**')
        converted_count = converted_content.count('**')
        replacements = (original_count - converted_count) // 2
        
        # 如果内容有变化，则写回文件
        if content != converted_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(converted_content)
            print(f"✓ 已处理: {os.path.basename(file_path)} (替换了 {replacements} 处)")
            return True
        else:
            print(f"- 无需修改: {os.path.basename(file_path)}")
            return False
            
    except Exception as e:
        print(f"✗ 处理 {file_path} 时出错: {str(e)}")
        return False

if __name__ == "__main__":
    path = input("请输入TXT文件或文件夹路径: ")
    
    if os.path.isdir(path):
        process_txt_files(path)
    elif os.path.isfile(path):
        if path.endswith('.txt'):
            process_single_file(path)
        else:
            print("不是TXT文件，是否继续处理? (y/n)")
            choice = input().lower()
            if choice == 'y' or choice == 'yes':
                process_single_file(path)
            else:
                print("已取消处理")
    else:
        print("无效的路径!")
    
    print("\n脚本执行完毕!")
