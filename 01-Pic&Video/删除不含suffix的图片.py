#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除文件夹及其子文件夹中文件名不含有"suffix"的图片文件

作者: Assistant
功能: 递归遍历指定文件夹，删除文件名中不包含指定后缀的图片文件
"""

import os
import sys
from pathlib import Path
from typing import List, Set

class ImageCleaner:
    """图片清理器"""
    
    # 支持的图片格式
    IMAGE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
        '.webp', '.ico', '.svg', '.raw', '.heic', '.heif'
    }
    
    def __init__(self, target_suffix: str = "suffix"):
        """
        初始化图片清理器
        
        Args:
            target_suffix: 要保留的图片文件名中必须包含的字符串
        """
        self.target_suffix = target_suffix
        self.deleted_files = []
        self.kept_files = []
        self.total_files_scanned = 0
    
    def is_image_file(self, file_path: Path) -> bool:
        """
        检查文件是否为图片文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为图片文件
        """
        return file_path.suffix.lower() in self.IMAGE_EXTENSIONS
    
    def should_keep_file(self, file_path: Path) -> bool:
        """
        检查文件是否应该保留（文件名包含指定后缀）
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否应该保留
        """
        filename = file_path.stem  # 不包含扩展名的文件名
        return self.target_suffix in filename
    
    def scan_and_delete(self, folder_path: str) -> None:
        """
        扫描文件夹并删除不符合条件的图片
        
        Args:
            folder_path: 要扫描的文件夹路径
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            print(f"❌ 错误：文件夹 '{folder_path}' 不存在")
            return
        
        if not folder.is_dir():
            print(f"❌ 错误：'{folder_path}' 不是一个文件夹")
            return
        
        print(f"📁 开始扫描文件夹: {folder.absolute()}")
        print(f"🔍 保留条件: 文件名包含 '{self.target_suffix}'")
        print(f"🗑️  模式: 直接删除")
        print("-" * 60)
        
        # 递归遍历所有文件
        for file_path in folder.rglob('*'):
            if file_path.is_file() and self.is_image_file(file_path):
                self.total_files_scanned += 1
                
                if self.should_keep_file(file_path):
                    self.kept_files.append(file_path)
                    print(f"✅ 保留: {file_path}")
                else:
                    self.deleted_files.append(file_path)
                    print(f"❌ 正在删除: {file_path}")
                    
                    # 直接删除文件
                    try:
                        file_path.unlink()
                        print(f"   ✅ 删除成功")
                    except Exception as e:
                        print(f"   ⚠️  删除失败: {e}")
    
    def print_summary(self) -> None:
        """
        打印扫描和删除结果摘要
        """
        print("\n" + "=" * 60)
        print("📊 扫描结果摘要")
        print("=" * 60)
        print(f"总计扫描图片文件: {self.total_files_scanned}")
        print(f"保留文件数量: {len(self.kept_files)}")
        print(f"已删除文件数量: {len(self.deleted_files)}")
        
        if self.deleted_files:
            print("\n✅ 删除操作已完成")

def main():
    """主函数"""
    print("🖼️  图片文件清理工具")
    print("=" * 40)
    
    # 获取用户输入
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = input("请输入要处理的文件夹路径: ").strip()
    
    if not folder_path:
        print("❌ 错误：必须提供文件夹路径")
        return
    
    # 获取要保留的文件名后缀
    if len(sys.argv) > 2:
        suffix = sys.argv[2]
    else:
        suffix = input("请输入要保留的文件名关键字 (默认: suffix): ").strip()
        if not suffix:
            suffix = "suffix"
    
    # 确认删除操作
    confirm = input(f"\n⚠️  确认要删除文件夹 '{folder_path}' 中不包含 '{suffix}' 的图片文件吗？(输入 'yes' 确认): ").strip().lower()
    if confirm != 'yes':
        print("❌ 操作已取消")
        return
    
    # 创建清理器并执行
    cleaner = ImageCleaner(target_suffix=suffix)
    cleaner.scan_and_delete(folder_path)
    cleaner.print_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc() 