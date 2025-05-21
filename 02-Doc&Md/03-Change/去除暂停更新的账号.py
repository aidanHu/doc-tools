import pandas as pd
import datetime
import os
from datetime import timedelta

def analyze_active_accounts(file_path, days=7):
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 输出初始信息
        print(f"已读取文件，共 {len(df)} 行数据")
        
        # 过滤掉"发文日期"为"作者精选"的行
        df = df[df['发文日期'] != "作者精选"]
        print(f"过滤'作者精选'后，剩余 {len(df)} 行数据")
        
        # 确保日期是数字格式（可能是Excel序列号）
        numeric_date_rows = pd.to_numeric(df['发文日期'], errors='coerce').notna()
        df = df[numeric_date_rows]
        print(f"过滤非数字日期后，剩余 {len(df)} 行数据")
        
        # 将序列号转换为实际日期 - 使用Excel的基准日期 (1899-12-30)
        excel_epoch = pd.Timestamp('1899-12-30')
        df['日期转换'] = df['发文日期'].apply(lambda x: excel_epoch + timedelta(days=int(x)))
        
        # 获取最新的发文日期
        latest_date = df['日期转换'].max()
        
        # 计算最新日期前N天的窗口期（包括最新日期）
        date_window_start = latest_date - timedelta(days=days-1)
        date_window = [date_window_start + timedelta(days=i) for i in range(days)]
        
        # 获取在窗口期内有发文的公众号
        active_df = df[df['日期转换'] >= date_window_start]
        active_accounts_df = active_df[['公众号']].drop_duplicates()
        
        # 生成输出文件名 - 基于文件所在的文件夹名
        # 获取文件所在的文件夹路径
        parent_dir = os.path.dirname(file_path)
        # 获取父文件夹名称
        folder_name = os.path.basename(parent_dir)
        # 生成输出文件名
        output_path = os.path.join(parent_dir, f'{folder_name}_active_last_{days}_days.xlsx')
        
        # 保存到Excel（不包含表头）
        active_accounts_df.to_excel(output_path, index=False, header=False)
        
        print("\n分析结果:")
        print("=" * 50)
        print(f"最新发文日期: {latest_date.strftime('%Y-%m-%d')} (序列号: {df['发文日期'].max()})")
        print(f"时间窗口: {date_window_start.strftime('%Y-%m-%d')} 至 {latest_date.strftime('%Y-%m-%d')}")
        print(f"\n共找到 {len(active_accounts_df)} 个在最近 {days} 天内有发文的公众号")
        print(f"结果已保存至: {output_path}")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("公众号活跃度分析工具")
    print("=" * 50)
    
    # 获取用户输入的文件路径
    file_path = input("请输入Excel文件路径: ")
    
    # 验证文件路径
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        return
    
    # 获取用户输入的天数，默认为7
    days_input = input("请输入要分析的天数 (默认7天，直接回车使用默认值): ")
    days = 7  # 默认值
    if days_input.strip():
        try:
            days = int(days_input)
            if days <= 0:
                print("天数必须大于0，将使用默认值7天")
                days = 7
        except ValueError:
            print("输入无效，将使用默认值7天")
    
    # 分析活跃的公众号
    analyze_active_accounts(file_path, days)

if __name__ == "__main__":
    main()