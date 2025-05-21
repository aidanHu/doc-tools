import os
import re
import sys

def remove_h1_headings(folder_path):
    """
    Remove all first-level headings (# Heading) from markdown files in the specified folder.
    
    Args:
        folder_path: Path to the folder containing markdown files
    """
    # Check if the folder exists
    if not os.path.isdir(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在。")
        return
    
    # Find all markdown files in the folder
    md_files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    
    if not md_files:
        print(f"在 '{folder_path}' 中未找到markdown文件。")
        return
    
    # Count for statistics
    processed_files = 0
    modified_files = 0
    
    # Process each markdown file
    for md_file in md_files:
        file_path = os.path.join(folder_path, md_file)
        
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Remove first-level headings using regex
            # This pattern matches lines that start with a single # followed by a space/tab,
            # ensuring it's not a higher level heading (##, ###)
            new_content = re.sub(r'^#[ \t](?!#).*(\n|\r\n?)?', '', content, flags=re.MULTILINE)
            
            # Check if any changes were made
            if new_content != content:
                # Write the modified content back to the file
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                modified_files += 1
                print(f"已修改: {md_file}")
            else:
                print(f"无需修改: {md_file}")
            
            processed_files += 1
            
        except Exception as e:
            print(f"处理 {md_file} 时出错: {str(e)}")
    
    print(f"完成! 处理了 {processed_files} 个文件, 修改了 {modified_files} 个文件。")

if __name__ == "__main__":
    # Check if folder path is provided as a command-line argument
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        remove_h1_headings(folder_path)
    else:
        # If no command-line argument, prompt the user for the folder path
        folder_path = input("请输入包含markdown文件的文件夹路径: ")
        remove_h1_headings(folder_path)