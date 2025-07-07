import os
import re
import jieba
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import json

# 处理PDF文件
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    print("警告: 未安装PDF处理库，请运行: pip install PyPDF2 pdfplumber")
    PDF_AVAILABLE = False

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class PDFInfoDensityAnalyzer:
    def __init__(self):
        """初始化分析器"""
        # 信息价值权重
        self.weights = {
            'number': 3.0,      # 数字信息
            'time': 2.5,        # 时间信息
            'entity': 2.0,      # 实体信息
            'professional': 2.0, # 专业术语
            'verb': 1.5,        # 动作动词
            'conjunction': 1.0,  # 连接词
            'modifier': -0.5    # 修饰词（降权）
        }
        
        # 预定义词汇库
        self.time_keywords = [
            '年', '月', '日', '时', '分', '秒', '今天', '昨天', '明天', '现在',
            '目前', '当前', '近期', '最近', '未来', '过去', '以前', '之后'
        ]
        
        self.conjunction_keywords = [
            '因此', '所以', '然而', '但是', '同时', '另外', '此外', '而且',
            '不过', '虽然', '尽管', '由于', '鉴于', '基于', '通过'
        ]
        
        self.modifier_keywords = [
            '很', '非常', '特别', '十分', '相当', '比较', '较为', '极其',
            '相对', '基本', '大概', '可能', '或许', '似乎', '好像'
        ]
        
        # 专业术语库（可扩展）
        self.professional_terms = [
            '数据', '分析', '系统', '平台', '技术', '算法', '模型', '框架',
            '架构', '方案', '策略', '机制', '流程', '标准', '规范', '指标'
        ]

    def extract_text_from_pdf(self, pdf_path):
        """从PDF文件提取文本"""
        if not PDF_AVAILABLE:
            return None, "PDF处理库未安装"
        
        text = ""
        error_msg = None
        
        try:
            # 首先尝试使用pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            try:
                # 如果pdfplumber失败，尝试PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                error_msg = f"PDF读取失败: {str(e2)}"
        
        return text.strip(), error_msg

    def clean_text(self, text):
        """清理文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符但保留中文标点
        text = re.sub(r'[^\u4e00-\u9fff\w\s。！？，、；：""''（）【】《》\.\!\?\,\;\:\(\)\[\]\"\']+', ' ', text)
        
        return text.strip()

    def analyze_sentence(self, sentence):
        """分析单句信息密度"""
        if not sentence.strip():
            return None
        
        # 分词
        words = jieba.lcut(sentence)
        total_chars = len(sentence.replace(' ', ''))  # 不计算空格
        
        if total_chars == 0:
            return None
        
        # 统计各类信息
        stats = {
            'numbers': len(re.findall(r'\d+\.?\d*', sentence)),
            'time_words': sum(1 for word in words if any(t in word for t in self.time_keywords)),
            'professional_terms': sum(1 for word in words if word in self.professional_terms),
            'conjunctions': sum(1 for word in words if word in self.conjunction_keywords),
            'modifiers': sum(1 for word in words if word in self.modifier_keywords),
            'entities': len([w for w in words if len(w) > 1 and w.isalpha()]),  # 简化的实体识别
        }
        
        # 计算信息得分
        info_score = (
            stats['numbers'] * self.weights['number'] +
            stats['time_words'] * self.weights['time'] +
            stats['professional_terms'] * self.weights['professional'] +
            stats['conjunctions'] * self.weights['conjunction'] +
            stats['modifiers'] * self.weights['modifier']
        )
        
        # 计算密度
        density = info_score / total_chars if total_chars > 0 else 0
        
        # 质量等级
        if density > 0.15:
            quality = "高"
        elif density > 0.08:
            quality = "中"
        else:
            quality = "低"
        
        return {
            'sentence': sentence[:100] + "..." if len(sentence) > 100 else sentence,
            'density': density,
            'quality': quality,
            'total_chars': total_chars,
            'info_score': info_score,
            **stats
        }

    def analyze_text(self, text, filename=""):
        """分析整篇文本"""
        if not text:
            return {
                'filename': filename,
                'error': '文本为空',
                'total_sentences': 0,
                'average_density': 0,
                'high_quality_ratio': 0,
                'sentences': []
            }
        
        # 分句
        sentences = re.split(r'[。！？\.\!\?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
        
        if not sentences:
            return {
                'filename': filename,
                'error': '未找到有效句子',
                'total_sentences': 0,
                'average_density': 0,
                'high_quality_ratio': 0,
                'sentences': []
            }
        
        # 分析每个句子
        sentence_results = []
        for sentence in sentences:
            result = self.analyze_sentence(sentence)
            if result:
                sentence_results.append(result)
        
        if not sentence_results:
            return {
                'filename': filename,
                'error': '句子分析失败',
                'total_sentences': 0,
                'average_density': 0,
                'high_quality_ratio': 0,
                'sentences': []
            }
        
        # 计算整体指标
        densities = [r['density'] for r in sentence_results]
        average_density = sum(densities) / len(densities)
        high_quality_count = len([r for r in sentence_results if r['quality'] == '高'])
        high_quality_ratio = high_quality_count / len(sentence_results)
        
        # 统计信息
        total_chars = sum(r['total_chars'] for r in sentence_results)
        total_numbers = sum(r['numbers'] for r in sentence_results)
        total_time_words = sum(r['time_words'] for r in sentence_results)
        
        return {
            'filename': filename,
            'total_sentences': len(sentence_results),
            'total_chars': total_chars,
            'average_density': average_density,
            'high_quality_ratio': high_quality_ratio,
            'quality_distribution': {
                '高': len([r for r in sentence_results if r['quality'] == '高']),
                '中': len([r for r in sentence_results if r['quality'] == '中']),
                '低': len([r for r in sentence_results if r['quality'] == '低'])
            },
            'content_stats': {
                'numbers_count': total_numbers,
                'time_words_count': total_time_words,
                'avg_sentence_length': total_chars / len(sentence_results)
            },
            'sentences': sentence_results[:10]  # 只保留前10个句子的详细信息
        }

    def analyze_pdf_folder(self, folder_path, output_dir="analysis_results"):
        """批量分析PDF文件夹"""
        if not os.path.exists(folder_path):
            print(f"错误: 文件夹 {folder_path} 不存在")
            return
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有PDF文件
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"警告: 在 {folder_path} 中未找到PDF文件")
            return
        
        print(f"找到 {len(pdf_files)} 个PDF文件，开始分析...")
        
        results = []
        failed_files = []
        
        for i, filename in enumerate(pdf_files, 1):
            print(f"正在处理 ({i}/{len(pdf_files)}): {filename}")
            
            pdf_path = os.path.join(folder_path, filename)
            
            # 提取文本
            text, error = self.extract_text_from_pdf(pdf_path)
            
            if error:
                failed_files.append({'filename': filename, 'error': error})
                continue
            
            # 清理文本
            clean_text = self.clean_text(text)
            
            # 分析文本
            result = self.analyze_text(clean_text, filename)
            results.append(result)
        
        # 生成报告
        self.generate_reports(results, failed_files, output_dir)
        
        print(f"\n分析完成！结果保存在 {output_dir} 目录中")
        print(f"成功分析: {len(results)} 个文件")
        print(f"失败文件: {len(failed_files)} 个")

    def generate_reports(self, results, failed_files, output_dir):
        """生成分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 生成Excel报告
        self.generate_excel_report(results, output_dir, timestamp)
        
        # 2. 生成可视化图表
        self.generate_visualizations(results, output_dir, timestamp)
        
        # 3. 生成JSON详细报告
        self.generate_json_report(results, failed_files, output_dir, timestamp)
        
        # 4. 生成文本摘要报告
        self.generate_summary_report(results, failed_files, output_dir, timestamp)

    def generate_excel_report(self, results, output_dir, timestamp):
        """生成Excel报告"""
        try:
            # 主要指标汇总
            summary_data = []
            for result in results:
                if 'error' not in result:
                    summary_data.append({
                        '文件名': result['filename'],
                        '总句数': result['total_sentences'],
                        '总字数': result['total_chars'],
                        '平均信息密度': round(result['average_density'], 4),
                        '高质量句子占比': f"{result['high_quality_ratio']:.2%}",
                        '高质量句子数': result['quality_distribution']['高'],
                        '中质量句子数': result['quality_distribution']['中'],
                        '低质量句子数': result['quality_distribution']['低'],
                        '数字信息数量': result['content_stats']['numbers_count'],
                        '时间词数量': result['content_stats']['time_words_count'],
                        '平均句长': round(result['content_stats']['avg_sentence_length'], 1)
                    })
            
            df_summary = pd.DataFrame(summary_data)
            
            # 详细句子分析
            detail_data = []
            for result in results:
                if 'error' not in result:
                    for sentence in result['sentences']:
                        detail_data.append({
                            '文件名': result['filename'],
                            '句子内容': sentence['sentence'],
                            '信息密度': round(sentence['density'], 4),
                            '质量等级': sentence['quality'],
                            '字数': sentence['total_chars'],
                            '数字数量': sentence['numbers'],
                            '时间词数量': sentence['time_words'],
                            '专业术语数量': sentence['professional_terms']
                        })
            
            df_detail = pd.DataFrame(detail_data)
            
            # 保存到Excel
            excel_path = os.path.join(output_dir, f"PDF分析报告_{timestamp}.xlsx")
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df_summary.to_excel(writer, sheet_name='文件汇总', index=False)
                df_detail.to_excel(writer, sheet_name='句子详情', index=False)
            
            print(f"Excel报告已生成: {excel_path}")
            
        except Exception as e:
            print(f"生成Excel报告失败: {str(e)}")

    def generate_visualizations(self, results, output_dir, timestamp):
        """生成可视化图表"""
        try:
            valid_results = [r for r in results if 'error' not in r]
            if not valid_results:
                return
            
            # 设置图表样式
            plt.style.use('default')
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('PDF文件信息密度分析报告', fontsize=16, fontweight='bold')
            
            # 1. 信息密度分布直方图
            densities = [r['average_density'] for r in valid_results]
            axes[0, 0].hist(densities, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            axes[0, 0].set_title('信息密度分布')
            axes[0, 0].set_xlabel('平均信息密度')
            axes[0, 0].set_ylabel('文件数量')
            axes[0, 0].axvline(x=0.15, color='red', linestyle='--', label='高质量阈值(0.15)')
            axes[0, 0].axvline(x=0.08, color='orange', linestyle='--', label='中质量阈值(0.08)')
            axes[0, 0].legend()
            
            # 2. 质量等级分布饼图
            quality_counts = {'高': 0, '中': 0, '低': 0}
            for result in valid_results:
                for quality, count in result['quality_distribution'].items():
                    quality_counts[quality] += count
            
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            axes[0, 1].pie(quality_counts.values(), labels=quality_counts.keys(), 
                          autopct='%1.1f%%', colors=colors)
            axes[0, 1].set_title('整体句子质量分布')
            
            # 3. 文件质量排名
            sorted_results = sorted(valid_results, key=lambda x: x['average_density'], reverse=True)
            top_10 = sorted_results[:10]
            filenames = [r['filename'][:15] + '...' if len(r['filename']) > 15 else r['filename'] 
                        for r in top_10]
            densities = [r['average_density'] for r in top_10]
            
            bars = axes[1, 0].barh(range(len(filenames)), densities, color='lightgreen')
            axes[1, 0].set_yticks(range(len(filenames)))
            axes[1, 0].set_yticklabels(filenames)
            axes[1, 0].set_xlabel('平均信息密度')
            axes[1, 0].set_title('文件质量排名 (Top 10)')
            
            # 添加数值标签
            for i, bar in enumerate(bars):
                width = bar.get_width()
                axes[1, 0].text(width, bar.get_y() + bar.get_height()/2, 
                               f'{width:.3f}', ha='left', va='center')
            
            # 4. 内容特征分析
            avg_sentences = [r['total_sentences'] for r in valid_results]
            avg_chars = [r['total_chars'] for r in valid_results]
            
            scatter = axes[1, 1].scatter(avg_sentences, densities, 
                                       c=avg_chars, cmap='viridis', alpha=0.6)
            axes[1, 1].set_xlabel('句子数量')
            axes[1, 1].set_ylabel('平均信息密度')
            axes[1, 1].set_title('句子数量 vs 信息密度')
            
            # 添加颜色条
            cbar = plt.colorbar(scatter, ax=axes[1, 1])
            cbar.set_label('总字数')
            
            plt.tight_layout()
            
            # 保存图表
            chart_path = os.path.join(output_dir, f"分析图表_{timestamp}.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"可视化图表已生成: {chart_path}")
            
        except Exception as e:
            print(f"生成可视化图表失败: {str(e)}")

    def generate_json_report(self, results, failed_files, output_dir, timestamp):
        """生成JSON详细报告"""
        try:
            report_data = {
                'analysis_time': datetime.now().isoformat(),
                'summary': {
                    'total_files': len(results) + len(failed_files),
                    'successful_files': len(results),
                    'failed_files': len(failed_files)
                },
                'results': results,
                'failed_files': failed_files
            }
            
            json_path = os.path.join(output_dir, f"详细报告_{timestamp}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            print(f"JSON详细报告已生成: {json_path}")
            
        except Exception as e:
            print(f"生成JSON报告失败: {str(e)}")

    def generate_summary_report(self, results, failed_files, output_dir, timestamp):
        """生成文本摘要报告"""
        try:
            valid_results = [r for r in results if 'error' not in r]
            
            report_lines = [
                "=" * 60,
                "PDF文件信息密度分析摘要报告",
                "=" * 60,
                f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"总文件数: {len(results) + len(failed_files)}",
                f"成功分析: {len(valid_results)} 个",
                f"失败文件: {len(failed_files)} 个",
                "",
                "整体统计:",
                "-" * 30
            ]
            
            if valid_results:
                total_sentences = sum(r['total_sentences'] for r in valid_results)
                total_chars = sum(r['total_chars'] for r in valid_results)
                avg_density = sum(r['average_density'] for r in valid_results) / len(valid_results)
                
                high_quality_sentences = sum(r['quality_distribution']['高'] for r in valid_results)
                high_quality_ratio = high_quality_sentences / total_sentences if total_sentences > 0 else 0
                
                report_lines.extend([
                    f"总句子数: {total_sentences:,}",
                    f"总字符数: {total_chars:,}",
                    f"平均信息密度: {avg_density:.4f}",
                    f"高质量句子数: {high_quality_sentences:,}",
                    f"高质量句子占比: {high_quality_ratio:.2%}",
                    "",
                    "文件排名 (按信息密度):",
                    "-" * 30
                ])
                
                # 排序并显示前10名
                sorted_results = sorted(valid_results, key=lambda x: x['average_density'], reverse=True)
                for i, result in enumerate(sorted_results[:10], 1):
                    report_lines.append(
                        f"{i:2d}. {result['filename']:<30} "
                        f"密度: {result['average_density']:.4f} "
                        f"高质量占比: {result['high_quality_ratio']:.2%}"
                    )
                
                # 质量分布统计
                report_lines.extend([
                    "",
                    "质量分布统计:",
                    "-" * 30
                ])
                
                quality_totals = {'高': 0, '中': 0, '低': 0}
                for result in valid_results:
                    for quality, count in result['quality_distribution'].items():
                        quality_totals[quality] += count
                
                total_quality_sentences = sum(quality_totals.values())
                for quality, count in quality_totals.items():
                    ratio = count / total_quality_sentences if total_quality_sentences > 0 else 0
                    report_lines.append(f"{quality}质量句子: {count:,} ({ratio:.1%})")
            
            # 失败文件列表
            if failed_files:
                report_lines.extend([
                    "",
                    "处理失败的文件:",
                    "-" * 30
                ])
                for failed in failed_files:
                    report_lines.append(f"- {failed['filename']}: {failed['error']}")
            
            report_lines.extend([
                "",
                "=" * 60,
                "报告结束"
            ])
            
            # 保存报告
            summary_path = os.path.join(output_dir, f"摘要报告_{timestamp}.txt")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            # 同时打印到控制台
            print("\n" + '\n'.join(report_lines))
            print(f"\n摘要报告已保存: {summary_path}")
            
        except Exception as e:
            print(f"生成摘要报告失败: {str(e)}")

def main():
    """主函数"""
    print("PDF信息密度批量分析工具")
    print("=" * 50)
    
    # 检查依赖
    if not PDF_AVAILABLE:
        print("请先安装必要的库:")
        print("pip install PyPDF2 pdfplumber pandas matplotlib seaborn jieba openpyxl")
        return
    
    # 获取用户输入
    while True:
        folder_path = input("请输入PDF文件夹路径: ").strip().strip('"')
        if os.path.exists(folder_path):
            break
        print("文件夹不存在，请重新输入")
    
    output_dir = input("请输入输出目录路径 (直接回车使用默认路径 'analysis_results'): ").strip().strip('"')
    if not output_dir:
        output_dir = "analysis_results"
    
    # 创建分析器并开始分析
    analyzer = PDFInfoDensityAnalyzer()
    analyzer.analyze_pdf_folder(folder_path, output_dir)

if __name__ == "__main__":
    main()
