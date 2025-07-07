import os
import re
import jieba
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict
import json
import markdown
from bs4 import BeautifulSoup
import yaml

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class MarkdownInfoDensityAnalyzer:
    def __init__(self):
        """初始化分析器"""
        # 信息价值权重
        self.weights = {
            'number': 3.0,      # 数字信息
            'time': 2.5,        # 时间信息
            'entity': 2.0,      # 实体信息
            'professional': 2.0, # 专业术语
            'code': 2.5,        # 代码片段
            'link': 1.5,        # 链接
            'verb': 1.5,        # 动作动词
            'conjunction': 1.0,  # 连接词
            'modifier': -0.5,   # 修饰词（降权）
            'list_item': 1.2,   # 列表项
            'heading': 1.8      # 标题
        }
        
        # 预定义词汇库
        self.time_keywords = [
            '年', '月', '日', '时', '分', '秒', '今天', '昨天', '明天', '现在',
            '目前', '当前', '近期', '最近', '未来', '过去', '以前', '之后',
            '2023', '2024', '2025'
        ]
        
        self.conjunction_keywords = [
            '因此', '所以', '然而', '但是', '同时', '另外', '此外', '而且',
            '不过', '虽然', '尽管', '由于', '鉴于', '基于', '通过', '首先',
            '其次', '最后', '总之', '综上', '换言之'
        ]
        
        self.modifier_keywords = [
            '很', '非常', '特别', '十分', '相当', '比较', '较为', '极其',
            '相对', '基本', '大概', '可能', '或许', '似乎', '好像', '挺',
            '蛮', '还是', '比较'
        ]
        
        # 专业术语库（技术类）
        self.professional_terms = [
            '算法', '数据结构', '机器学习', '深度学习', '人工智能', '神经网络',
            '数据库', '架构', '框架', 'API', '接口', '协议', '服务器', '客户端',
            '前端', '后端', '全栈', '微服务', '容器', '云计算', '大数据',
            '区块链', '物联网', '边缘计算', '分布式', '并发', '异步', '同步',
            '缓存', '索引', '优化', '性能', '安全', '加密', '认证', '授权'
        ]
        
        # Markdown特殊模式
        self.md_patterns = {
            'code_block': r'```[\s\S]*?```',
            'inline_code': r'`[^`]+`',  # 不需要捕获组，直接移除
            'link': r'\[([^\]]+)\]\([^\)]+\)',
            'image': r'!\[([^\]]*)\]\([^\)]+\)',
            'heading': r'^#{1,6}\s+(.+)$',
            'list_item': r'^[\s]*[-*+]\s+(.+)$',
            'numbered_list': r'^[\s]*\d+\.\s+(.+)$',
            'blockquote': r'^>\s+(.+)$',
            'table_row': r'\|.*\|',
            'bold': r'\*\*([^*]+)\*\*',
            'italic': r'\*([^*]+)\*',
            'strikethrough': r'~~([^~]+)~~'
        }

    def parse_markdown_file(self, file_path):
        """解析Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分离Front Matter和正文
            front_matter = {}
            body_content = content
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        front_matter = yaml.safe_load(parts[1]) or {}
                        body_content = parts[2].strip()
                    except:
                        pass
            
            return body_content, front_matter, None
            
        except Exception as e:
            return None, {}, str(e)

    def extract_markdown_elements(self, content):
        """提取Markdown元素"""
        elements = {
            'headings': [],
            'code_blocks': [],
            'inline_codes': [],
            'links': [],
            'images': [],
            'list_items': [],
            'blockquotes': [],
            'tables': [],
            'emphasis': []
        }
        
        # 提取各种元素
        elements['headings'] = re.findall(self.md_patterns['heading'], content, re.MULTILINE)
        elements['code_blocks'] = re.findall(self.md_patterns['code_block'], content, re.DOTALL)
        elements['inline_codes'] = re.findall(self.md_patterns['inline_code'], content)
        elements['links'] = re.findall(self.md_patterns['link'], content)
        elements['images'] = re.findall(self.md_patterns['image'], content)
        elements['list_items'] = re.findall(self.md_patterns['list_item'], content, re.MULTILINE)
        elements['list_items'].extend(re.findall(self.md_patterns['numbered_list'], content, re.MULTILINE))
        elements['blockquotes'] = re.findall(self.md_patterns['blockquote'], content, re.MULTILINE)
        elements['tables'] = re.findall(self.md_patterns['table_row'], content, re.MULTILINE)
        
        # 提取强调文本
        elements['emphasis'].extend(re.findall(self.md_patterns['bold'], content))
        elements['emphasis'].extend(re.findall(self.md_patterns['italic'], content))
        
        return elements

    def clean_markdown_text(self, content):
        """清理Markdown文本，保留纯文本"""
        # 移除代码块
        content = re.sub(self.md_patterns['code_block'], '', content, flags=re.DOTALL)
        
        # 移除内联代码（修复：直接移除，不保留内容）
        content = re.sub(self.md_patterns['inline_code'], '', content)
        
        # 处理链接，保留链接文本
        content = re.sub(self.md_patterns['link'], r'\1', content)
        
        # 移除图片
        content = re.sub(self.md_patterns['image'], '', content)
        
        # 清理标题标记
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        
        # 清理列表标记
        content = re.sub(r'^[\s]*[-*+]\s+', '', content, flags=re.MULTILINE)
        content = re.sub(r'^[\s]*\d+\.\s+', '', content, flags=re.MULTILINE)
        
        # 清理引用标记
        content = re.sub(r'^>\s+', '', content, flags=re.MULTILINE)
        
        # 清理强调标记
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        content = re.sub(r'~~([^~]+)~~', r'\1', content)
        
        # 清理表格
        content = re.sub(r'\|.*\|', '', content)
        content = re.sub(r'^[-\s|:]+$', '', content, flags=re.MULTILINE)
        
        # 清理多余空白
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()


    def analyze_sentence(self, sentence, context=None):
        """分析单句信息密度"""
        if not sentence.strip():
            return None
        
        # 分词
        words = jieba.lcut(sentence)
        total_chars = len(sentence.replace(' ', ''))
        
        if total_chars == 0:
            return None
        
        # 统计各类信息
        stats = {
            'numbers': len(re.findall(r'\d+\.?\d*', sentence)),
            'time_words': sum(1 for word in words if any(t in word for t in self.time_keywords)),
            'professional_terms': sum(1 for word in words if word in self.professional_terms),
            'conjunctions': sum(1 for word in words if word in self.conjunction_keywords),
            'modifiers': sum(1 for word in words if word in self.modifier_keywords),
            'entities': len([w for w in words if len(w) > 1 and w.isalpha()]),
            'code_snippets': len(re.findall(r'`[^`]+`', sentence)),
            'links': len(re.findall(r'\[([^\]]+)\]\([^\)]+\)', sentence))
        }
        
        # 上下文加分
        context_bonus = 0
        if context:
            if context.get('is_heading'):
                context_bonus += self.weights['heading']
            if context.get('is_list_item'):
                context_bonus += self.weights['list_item']
        
        # 计算信息得分
        info_score = (
            stats['numbers'] * self.weights['number'] +
            stats['time_words'] * self.weights['time'] +
            stats['professional_terms'] * self.weights['professional'] +
            stats['conjunctions'] * self.weights['conjunction'] +
            stats['modifiers'] * self.weights['modifier'] +
            stats['code_snippets'] * self.weights['code'] +
            stats['links'] * self.weights['link'] +
            context_bonus
        )
        
        # 计算密度
        density = info_score / total_chars if total_chars > 0 else 0
        
        # 质量等级（针对Markdown调整阈值）
        if density > 0.12:  # Markdown文档阈值稍低
            quality = "高"
        elif density > 0.06:
            quality = "中"
        else:
            quality = "低"
        
        return {
            'sentence': sentence[:150] + "..." if len(sentence) > 150 else sentence,
            'density': density,
            'quality': quality,
            'total_chars': total_chars,
            'info_score': info_score,
            'context': context or {},
            **stats
        }

    def analyze_markdown_content(self, content, filename=""):
        """分析Markdown内容"""
        if not content:
            return {
                'filename': filename,
                'error': '内容为空',
                'total_sentences': 0,
                'average_density': 0,
                'high_quality_ratio': 0,
                'markdown_stats': {},
                'sentences': []
            }
        
        # 提取Markdown元素
        md_elements = self.extract_markdown_elements(content)
        
        # 清理文本
        clean_text = self.clean_markdown_text(content)
        
        # 分句分析
        sentences = re.split(r'[。！？\.\!\?]+', clean_text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]
        
        if not sentences:
            return {
                'filename': filename,
                'error': '未找到有效句子',
                'total_sentences': 0,
                'average_density': 0,
                'high_quality_ratio': 0,
                'markdown_stats': self.calculate_markdown_stats(md_elements, content),
                'sentences': []
            }
        
        # 分析每个句子
        sentence_results = []
        for sentence in sentences:
            # 判断句子上下文
            context = self.get_sentence_context(sentence, content)
            result = self.analyze_sentence(sentence, context)
            if result:
                sentence_results.append(result)
        
        if not sentence_results:
            return {
                'filename': filename,
                'error': '句子分析失败',
                'total_sentences': 0,
                'average_density': 0,
                'high_quality_ratio': 0,
                'markdown_stats': self.calculate_markdown_stats(md_elements, content),
                'sentences': []
            }
        
        # 计算整体指标
        densities = [r['density'] for r in sentence_results]
        average_density = sum(densities) / len(densities)
        high_quality_count = len([r for r in sentence_results if r['quality'] == '高'])
        high_quality_ratio = high_quality_count / len(sentence_results)
        
        return {
            'filename': filename,
            'total_sentences': len(sentence_results),
            'total_chars': sum(r['total_chars'] for r in sentence_results),
            'average_density': average_density,
            'high_quality_ratio': high_quality_ratio,
            'quality_distribution': {
                '高': len([r for r in sentence_results if r['quality'] == '高']),
                '中': len([r for r in sentence_results if r['quality'] == '中']),
                '低': len([r for r in sentence_results if r['quality'] == '低'])
            },
            'markdown_stats': self.calculate_markdown_stats(md_elements, content),
            'content_stats': {
                'numbers_count': sum(r['numbers'] for r in sentence_results),
                'time_words_count': sum(r['time_words'] for r in sentence_results),
                'professional_terms_count': sum(r['professional_terms'] for r in sentence_results),
                'code_snippets_count': sum(r['code_snippets'] for r in sentence_results),
                'links_count': sum(r['links'] for r in sentence_results),
                'avg_sentence_length': sum(r['total_chars'] for r in sentence_results) / len(sentence_results)
            },
            'sentences': sentence_results[:15]  # 保留前15个句子的详细信息
        }

    def get_sentence_context(self, sentence, full_content):
        """获取句子上下文信息"""
        context = {
            'is_heading': False,
            'is_list_item': False,
            'is_blockquote': False,
            'heading_level': 0
        }
        
        # 检查是否在标题中
        heading_matches = re.findall(r'^(#{1,6})\s+(.+)$', full_content, re.MULTILINE)
        for level, heading_text in heading_matches:
            if sentence in heading_text:
                context['is_heading'] = True
                context['heading_level'] = len(level)
                break
        
        # 检查是否在列表中
        if re.search(r'^[\s]*[-*+]\s+.*' + re.escape(sentence[:20]), full_content, re.MULTILINE):
            context['is_list_item'] = True
        
        # 检查是否在引用中
        if re.search(r'^>\s+.*' + re.escape(sentence[:20]), full_content, re.MULTILINE):
            context['is_blockquote'] = True
        
        return context

    def calculate_markdown_stats(self, md_elements, content):
        """计算Markdown特有统计信息"""
        lines = content.split('\n')
        
        stats = {
            'headings_count': len(md_elements['headings']),
            'heading_levels': {},
            'code_blocks_count': len(md_elements['code_blocks']),
            'inline_codes_count': len(md_elements['inline_codes']),
            'links_count': len(md_elements['links']),
            'images_count': len(md_elements['images']),
            'list_items_count': len(md_elements['list_items']),
            'blockquotes_count': len(md_elements['blockquotes']),
            'tables_count': len([line for line in lines if '|' in line and line.strip().startswith('|')]),
            'emphasis_count': len(md_elements['emphasis']),
            'total_lines': len(lines),
            'empty_lines': len([line for line in lines if not line.strip()]),
            'content_lines': len([line for line in lines if line.strip()])
        }
        
        # 统计标题层级分布
        for heading in md_elements['headings']:
            # 从原文中找到标题的层级
            for line in lines:
                if heading in line and line.strip().startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    stats['heading_levels'][f'h{level}'] = stats['heading_levels'].get(f'h{level}', 0) + 1
                    break
        
        # 计算结构化程度
        structured_elements = (stats['headings_count'] + stats['list_items_count'] + 
                             stats['tables_count'] + stats['blockquotes_count'])
        stats['structure_ratio'] = structured_elements / stats['content_lines'] if stats['content_lines'] > 0 else 0
        
        # 计算代码密度
        code_elements = stats['code_blocks_count'] + stats['inline_codes_count']
        stats['code_density'] = code_elements / stats['content_lines'] if stats['content_lines'] > 0 else 0
        
        return stats

    def analyze_markdown_folder(self, folder_path, output_dir="markdown_analysis_results"):
        """批量分析Markdown文件夹"""
        if not os.path.exists(folder_path):
            print(f"错误: 文件夹 {folder_path} 不存在")
            return
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有Markdown文件
        md_extensions = ['.md', '.markdown', '.mdown', '.mkd']
        md_files = []
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in md_extensions):
                    md_files.append(os.path.join(root, file))
        
        if not md_files:
            print(f"警告: 在 {folder_path} 中未找到Markdown文件")
            return
        
        print(f"找到 {len(md_files)} 个Markdown文件，开始分析...")
        
        results = []
        failed_files = []
        
        for i, file_path in enumerate(md_files, 1):
            filename = os.path.relpath(file_path, folder_path)
            print(f"正在处理 ({i}/{len(md_files)}): {filename}")
            
            # 解析文件
            content, front_matter, error = self.parse_markdown_file(file_path)
            
            if error:
                failed_files.append({'filename': filename, 'error': error})
                continue
            
            # 分析内容
            result = self.analyze_markdown_content(content, filename)
            
            # 添加Front Matter信息
            result['front_matter'] = front_matter
            result['file_path'] = file_path
            
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
            # 文件汇总数据
            summary_data = []
            for result in results:
                if 'error' not in result:
                    md_stats = result['markdown_stats']
                    content_stats = result['content_stats']
                    
                    summary_data.append({
                        '文件名': result['filename'],
                        '总句数': result['total_sentences'],
                        '总字数': result['total_chars'],
                        '平均信息密度': round(result['average_density'], 4),
                        '高质量句子占比': f"{result['high_quality_ratio']:.2%}",
                        '高质量句子数': result['quality_distribution']['高'],
                        '中质量句子数': result['quality_distribution']['中'],
                        '低质量句子数': result['quality_distribution']['低'],
                        '标题数量': md_stats['headings_count'],
                        '代码块数量': md_stats['code_blocks_count'],
                        '链接数量': md_stats['links_count'],
                        '列表项数量': md_stats['list_items_count'],
                        '图片数量': md_stats['images_count'],
                        '结构化程度': f"{md_stats['structure_ratio']:.2%}",
                        '代码密度': f"{md_stats['code_density']:.2%}",
                        '专业术语数量': content_stats['professional_terms_count'],
                        '数字信息数量': content_stats['numbers_count'],
                        '时间词数量': content_stats['time_words_count']
                    })
            
            df_summary = pd.DataFrame(summary_data)
            
            # Markdown结构分析
            structure_data = []
            for result in results:
                if 'error' not in result:
                    md_stats = result['markdown_stats']
                    structure_data.append({
                        '文件名': result['filename'],
                        '总行数': md_stats['total_lines'],
                        '内容行数': md_stats['content_lines'],
                        '空行数': md_stats['empty_lines'],
                        '标题分布': str(md_stats['heading_levels']),
                        '代码块': md_stats['code_blocks_count'],
                        '内联代码': md_stats['inline_codes_count'],
                        '表格数量': md_stats['tables_count'],
                        '引用数量': md_stats['blockquotes_count'],
                        '强调文本': md_stats['emphasis_count']
                    })
            
            df_structure = pd.DataFrame(structure_data)
            
            # 句子详细分析
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
                            '专业术语数量': sentence['professional_terms'],
                            '代码片段数量': sentence['code_snippets'],
                            '链接数量': sentence['links'],
                            '是否标题': sentence['context'].get('is_heading', False),
                            '是否列表项': sentence['context'].get('is_list_item', False)
                        })
            
            df_detail = pd.DataFrame(detail_data)
            
            # 保存到Excel
            excel_path = os.path.join(output_dir, f"Markdown分析报告_{timestamp}.xlsx")
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df_summary.to_excel(writer, sheet_name='文件汇总', index=False)
                df_structure.to_excel(writer, sheet_name='结构分析', index=False)
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
            
            # 创建2x3的子图布局
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle('Markdown文件信息密度分析报告', fontsize=16, fontweight='bold')
            
            # 1. 信息密度分布
            densities = [r['average_density'] for r in valid_results]
            axes[0, 0].hist(densities, bins=20, alpha=0.7, color='lightblue', edgecolor='black')
            axes[0, 0].set_title('信息密度分布')
            axes[0, 0].set_xlabel('平均信息密度')
            axes[0, 0].set_ylabel('文件数量')
            axes[0, 0].axvline(x=0.12, color='red', linestyle='--', label='高质量阈值')
            axes[0, 0].axvline(x=0.06, color='orange', linestyle='--', label='中质量阈值')
            axes[0, 0].legend()
            
            # 2. Markdown元素分布
            element_counts = {
                '标题': sum(r['markdown_stats']['headings_count'] for r in valid_results),
                '代码块': sum(r['markdown_stats']['code_blocks_count'] for r in valid_results),
                '链接': sum(r['markdown_stats']['links_count'] for r in valid_results),
                '列表': sum(r['markdown_stats']['list_items_count'] for r in valid_results),
                '图片': sum(r['markdown_stats']['images_count'] for r in valid_results)
            }
            
            axes[0, 1].bar(element_counts.keys(), element_counts.values(), 
                          color=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc'])
            axes[0, 1].set_title('Markdown元素分布')
            axes[0, 1].set_ylabel('数量')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. 质量分布饼图
            quality_counts = {'高': 0, '中': 0, '低': 0}
            for result in valid_results:
                for quality, count in result['quality_distribution'].items():
                    quality_counts[quality] += count
            
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            axes[0, 2].pie(quality_counts.values(), labels=quality_counts.keys(), 
                          autopct='%1.1f%%', colors=colors)
            axes[0, 2].set_title('句子质量分布')
            
            # 4. 文件质量排名
            sorted_results = sorted(valid_results, key=lambda x: x['average_density'], reverse=True)
            top_10 = sorted_results[:10]
            filenames = [os.path.basename(r['filename'])[:20] + '...' 
                        if len(os.path.basename(r['filename'])) > 20 
                        else os.path.basename(r['filename']) for r in top_10]
            densities_top = [r['average_density'] for r in top_10]
            
            bars = axes[1, 0].barh(range(len(filenames)), densities_top, color='lightgreen')
            axes[1, 0].set_yticks(range(len(filenames)))
            axes[1, 0].set_yticklabels(filenames)
            axes[1, 0].set_xlabel('平均信息密度')
            axes[1, 0].set_title('文件质量排名 (Top 10)')
            
            # 5. 结构化程度 vs 信息密度
            structure_ratios = [r['markdown_stats']['structure_ratio'] for r in valid_results]
            axes[1, 1].scatter(structure_ratios, densities, alpha=0.6, color='purple')
            axes[1, 1].set_xlabel('结构化程度')
            axes[1, 1].set_ylabel('信息密度')
            axes[1, 1].set_title('结构化程度 vs 信息密度')
            
            # 6. 代码密度分布
            code_densities = [r['markdown_stats']['code_density'] for r in valid_results]
            axes[1, 2].hist(code_densities, bins=15, alpha=0.7, color='orange', edgecolor='black')
            axes[1, 2].set_title('代码密度分布')
            axes[1, 2].set_xlabel('代码密度')
            axes[1, 2].set_ylabel('文件数量')
            
            plt.tight_layout()
            
            # 保存图表
            chart_path = os.path.join(output_dir, f"Markdown分析图表_{timestamp}.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # 生成额外的专项分析图表
            self.generate_additional_charts(valid_results, output_dir, timestamp)
            
            print(f"可视化图表已生成: {chart_path}")
            
        except Exception as e:
            print(f"生成可视化图表失败: {str(e)}")

    def generate_additional_charts(self, results, output_dir, timestamp):
        """生成额外的专项分析图表"""
        try:
            # 创建标题层级分析图
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Markdown文档结构深度分析', fontsize=14, fontweight='bold')
            
            # 1. 标题层级分布
            all_heading_levels = defaultdict(int)
            for result in results:
                heading_levels = result['markdown_stats']['heading_levels']
                for level, count in heading_levels.items():
                    all_heading_levels[level] += count
            
            if all_heading_levels:
                levels = sorted(all_heading_levels.keys())
                counts = [all_heading_levels[level] for level in levels]
                axes[0, 0].bar(levels, counts, color='skyblue')
                axes[0, 0].set_title('标题层级分布')
                axes[0, 0].set_xlabel('标题层级')
                axes[0, 0].set_ylabel('数量')
            
            # 2. 文档长度 vs 质量关系
            doc_lengths = [r['total_chars'] for r in results]
            quality_ratios = [r['high_quality_ratio'] for r in results]
            
            scatter = axes[0, 1].scatter(doc_lengths, quality_ratios, 
                                       c=[r['average_density'] for r in results], 
                                       cmap='viridis', alpha=0.6)
            axes[0, 1].set_xlabel('文档长度（字符数）')
            axes[0, 1].set_ylabel('高质量句子占比')
            axes[0, 1].set_title('文档长度 vs 质量关系')
            plt.colorbar(scatter, ax=axes[0, 1], label='平均信息密度')
            
            # 3. 不同元素类型的密度贡献
            element_contributions = {
                '数字信息': sum(r['content_stats']['numbers_count'] for r in results),
                '专业术语': sum(r['content_stats']['professional_terms_count'] for r in results),
                '代码片段': sum(r['content_stats']['code_snippets_count'] for r in results),
                '链接': sum(r['content_stats']['links_count'] for r in results),
                '时间词': sum(r['content_stats']['time_words_count'] for r in results)
            }
            
            axes[1, 0].pie(element_contributions.values(), labels=element_contributions.keys(),
                          autopct='%1.1f%%', startangle=90)
            axes[1, 0].set_title('信息密度贡献分布')
            
            # 4. 文档结构复杂度分析
            complexity_scores = []
            filenames = []
            
            for result in results:
                md_stats = result['markdown_stats']
                # 计算复杂度得分
                complexity = (
                    md_stats['headings_count'] * 0.3 +
                    md_stats['code_blocks_count'] * 0.4 +
                    md_stats['tables_count'] * 0.5 +
                    md_stats['list_items_count'] * 0.2 +
                    md_stats['links_count'] * 0.1
                ) / md_stats['content_lines'] if md_stats['content_lines'] > 0 else 0
                
                complexity_scores.append(complexity)
                filenames.append(os.path.basename(result['filename'])[:15])
            
            # 显示复杂度最高的10个文档
            sorted_data = sorted(zip(complexity_scores, filenames), reverse=True)[:10]
            if sorted_data:
                scores, names = zip(*sorted_data)
                y_pos = range(len(names))
                
                axes[1, 1].barh(y_pos, scores, color='coral')
                axes[1, 1].set_yticks(y_pos)
                axes[1, 1].set_yticklabels(names)
                axes[1, 1].set_xlabel('结构复杂度得分')
                axes[1, 1].set_title('文档结构复杂度排名')
            
            plt.tight_layout()
            
            additional_chart_path = os.path.join(output_dir, f"Markdown深度分析_{timestamp}.png")
            plt.savefig(additional_chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"生成额外图表失败: {str(e)}")

    def generate_json_report(self, results, failed_files, output_dir, timestamp):
        """生成JSON详细报告"""
        try:
            report_data = {
                'analysis_time': datetime.now().isoformat(),
                'summary': {
                    'total_files': len(results) + len(failed_files),
                    'successful_files': len(results),
                    'failed_files': len(failed_files),
                    'analyzer_version': '1.0.0',
                    'analysis_type': 'Markdown信息密度分析'
                },
                'global_stats': self.calculate_global_stats(results),
                'results': results,
                'failed_files': failed_files,
                'analysis_config': {
                    'weights': self.weights,
                    'quality_thresholds': {
                        'high': 0.12,
                        'medium': 0.06
                    }
                }
            }
            
            json_path = os.path.join(output_dir, f"Markdown详细报告_{timestamp}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            print(f"JSON详细报告已生成: {json_path}")
            
        except Exception as e:
            print(f"生成JSON报告失败: {str(e)}")

    def calculate_global_stats(self, results):
        """计算全局统计信息"""
        valid_results = [r for r in results if 'error' not in r]
        if not valid_results:
            return {}
        
        total_sentences = sum(r['total_sentences'] for r in valid_results)
        total_chars = sum(r['total_chars'] for r in valid_results)
        total_high_quality = sum(r['quality_distribution']['高'] for r in valid_results)
        
        # Markdown特有统计
        total_headings = sum(r['markdown_stats']['headings_count'] for r in valid_results)
        total_code_blocks = sum(r['markdown_stats']['code_blocks_count'] for r in valid_results)
        total_links = sum(r['markdown_stats']['links_count'] for r in valid_results)
        total_images = sum(r['markdown_stats']['images_count'] for r in valid_results)
        
        return {
            'total_sentences': total_sentences,
            'total_characters': total_chars,
            'average_density': sum(r['average_density'] for r in valid_results) / len(valid_results),
            'global_high_quality_ratio': total_high_quality / total_sentences if total_sentences > 0 else 0,
            'markdown_elements': {
                'total_headings': total_headings,
                'total_code_blocks': total_code_blocks,
                'total_links': total_links,
                'total_images': total_images,
                'avg_headings_per_doc': total_headings / len(valid_results),
                'avg_code_blocks_per_doc': total_code_blocks / len(valid_results)
            },
            'content_analysis': {
                'total_professional_terms': sum(r['content_stats']['professional_terms_count'] for r in valid_results),
                'total_numbers': sum(r['content_stats']['numbers_count'] for r in valid_results),
                'total_time_words': sum(r['content_stats']['time_words_count'] for r in valid_results),
                'avg_sentence_length': sum(r['content_stats']['avg_sentence_length'] for r in valid_results) / len(valid_results)
            }
        }

    def generate_summary_report(self, results, failed_files, output_dir, timestamp):
        """生成文本摘要报告"""
        try:
            valid_results = [r for r in results if 'error' not in r]
            global_stats = self.calculate_global_stats(results)
            
            report_lines = [
                "=" * 70,
                "Markdown文件信息密度分析摘要报告",
                "=" * 70,
                f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"分析工具: Markdown信息密度分析器 v1.0.0",
                "",
                "📊 文件统计:",
                "-" * 40,
                f"总文件数: {len(results) + len(failed_files)}",
                f"成功分析: {len(valid_results)} 个",
                f"失败文件: {len(failed_files)} 个",
                f"成功率: {len(valid_results)/(len(results) + len(failed_files))*100:.1f}%",
                "",
                "📈 整体质量指标:",
                "-" * 40
            ]
            
            if valid_results:
                report_lines.extend([
                    f"总句子数: {global_stats['total_sentences']:,}",
                    f"总字符数: {global_stats['total_characters']:,}",
                    f"平均信息密度: {global_stats['average_density']:.4f}",
                    f"全局高质量句子占比: {global_stats['global_high_quality_ratio']:.2%}",
                    f"平均句子长度: {global_stats['content_analysis']['avg_sentence_length']:.1f} 字符",
                    "",
                    "📝 Markdown元素统计:",
                    "-" * 40,
                    f"标题总数: {global_stats['markdown_elements']['total_headings']:,}",
                    f"代码块总数: {global_stats['markdown_elements']['total_code_blocks']:,}",
                    f"链接总数: {global_stats['markdown_elements']['total_links']:,}",
                    f"图片总数: {global_stats['markdown_elements']['total_images']:,}",
                    f"平均每文档标题数: {global_stats['markdown_elements']['avg_headings_per_doc']:.1f}",
                    f"平均每文档代码块数: {global_stats['markdown_elements']['avg_code_blocks_per_doc']:.1f}",
                    "",
                    "🎯 内容分析:",
                    "-" * 40,
                    f"专业术语总数: {global_stats['content_analysis']['total_professional_terms']:,}",
                    f"数字信息总数: {global_stats['content_analysis']['total_numbers']:,}",
                    f"时间词总数: {global_stats['content_analysis']['total_time_words']:,}",
                    "",
                    "🏆 文件质量排名 (按信息密度):",
                    "-" * 40
                ])
                
                # 排序并显示前15名
                sorted_results = sorted(valid_results, key=lambda x: x['average_density'], reverse=True)
                for i, result in enumerate(sorted_results[:15], 1):
                    filename = os.path.basename(result['filename'])
                    report_lines.append(
                        f"{i:2d}. {filename:<35} "
                        f"密度: {result['average_density']:.4f} "
                        f"高质量: {result['high_quality_ratio']:.1%} "
                        f"标题: {result['markdown_stats']['headings_count']:2d}"
                    )
                
                # 质量分布统计
                report_lines.extend([
                    "",
                    "📊 质量分布统计:",
                    "-" * 40
                ])
                
                quality_totals = {'高': 0, '中': 0, '低': 0}
                for result in valid_results:
                    for quality, count in result['quality_distribution'].items():
                        quality_totals[quality] += count
                
                total_quality_sentences = sum(quality_totals.values())
                for quality, count in quality_totals.items():
                    ratio = count / total_quality_sentences if total_quality_sentences > 0 else 0
                    report_lines.append(f"{quality}质量句子: {count:,} ({ratio:.1%})")
                
                # 结构分析
                report_lines.extend([
                    "",
                    "🏗️ 文档结构分析:",
                    "-" * 40
                ])
                
                avg_structure_ratio = sum(r['markdown_stats']['structure_ratio'] for r in valid_results) / len(valid_results)
                avg_code_density = sum(r['markdown_stats']['code_density'] for r in valid_results) / len(valid_results)
                
                report_lines.extend([
                    f"平均结构化程度: {avg_structure_ratio:.2%}",
                    f"平均代码密度: {avg_code_density:.2%}",
                ])
                
                # 最佳实践建议
                report_lines.extend([
                    "",
                    "💡 优化建议:",
                    "-" * 40
                ])
                
                low_quality_files = [r for r in valid_results if r['average_density'] < 0.06]
                high_structure_files = [r for r in valid_results if r['markdown_stats']['structure_ratio'] > 0.3]
                
                if low_quality_files:
                    report_lines.append(f"• {len(low_quality_files)} 个文件信息密度较低，建议增加具体数据和专业术语")
                
                if len(high_structure_files) / len(valid_results) < 0.5:
                    report_lines.append("• 建议增加文档结构化元素（标题、列表、表格等）")
                
                if global_stats['markdown_elements']['avg_code_blocks_per_doc'] < 1:
                    report_lines.append("• 技术文档建议增加代码示例以提高实用性")
                
                # 标题层级建议
                heading_distribution = defaultdict(int)
                for result in valid_results:
                    for level, count in result['markdown_stats']['heading_levels'].items():
                        heading_distribution[level] += count
                
                if 'h1' in heading_distribution and heading_distribution['h1'] > len(valid_results):
                    report_lines.append("• 建议减少一级标题使用，保持文档层次清晰")
                
                if sum(heading_distribution.values()) / len(valid_results) < 3:
                    report_lines.append("• 建议增加标题数量，改善文档可读性")
            
            # 失败文件列表
            if failed_files:
                report_lines.extend([
                    "",
                    "❌ 处理失败的文件:",
                    "-" * 40
                ])
                for failed in failed_files:
                    report_lines.append(f"- {failed['filename']}: {failed['error']}")
            
            # 技术说明
            report_lines.extend([
                "",
                "🔧 技术说明:",
                "-" * 40,
                "• 信息密度 = 信息价值得分 / 字符数",
                "• 高质量阈值: 0.12，中质量阈值: 0.06",
                "• 权重设置: 数字(3.0), 时间(2.5), 代码(2.5), 专业术语(2.0)",
                "• 结构化程度 = (标题+列表+表格+引用) / 内容行数",
                "• 代码密度 = (代码块+内联代码) / 内容行数",
                "",
                "=" * 70,
                "报告结束 - 感谢使用Markdown信息密度分析工具"
            ])
            
            # 保存报告
            summary_path = os.path.join(output_dir, f"Markdown摘要报告_{timestamp}.txt")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            # 同时打印到控制台
            print("\n" + '\n'.join(report_lines))
            print(f"\n摘要报告已保存: {summary_path}")
            
        except Exception as e:
            print(f"生成摘要报告失败: {str(e)}")

def main():
    """主函数"""
    print("Markdown文件信息密度批量分析工具")
    print("=" * 60)
    
    # 检查依赖
    missing_packages = []
    try:
        import jieba
    except ImportError:
        missing_packages.append('jieba')
    
    try:
        import pandas
    except ImportError:
        missing_packages.append('pandas')
    
    try:
        import matplotlib
    except ImportError:
        missing_packages.append('matplotlib')
    
    try:
        import seaborn
    except ImportError:
        missing_packages.append('seaborn')
    
    try:
        import markdown
    except ImportError:
        missing_packages.append('markdown')
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing_packages.append('beautifulsoup4')
    
    try:
        import yaml
    except ImportError:
        missing_packages.append('PyYAML')
    
    try:
        import openpyxl
    except ImportError:
        missing_packages.append('openpyxl')
    
    if missing_packages:
        print("请先安装必要的库:")
        print(f"pip install {' '.join(missing_packages)}")
        return
    
    # 获取用户输入
    while True:
        folder_path = input("请输入Markdown文件夹路径: ").strip().strip('"')
        if os.path.exists(folder_path):
            break
        print("文件夹不存在，请重新输入")
    
    output_dir = input("请输入输出目录路径 (直接回车使用默认路径 'markdown_analysis_results'): ").strip().strip('"')
    if not output_dir:
        output_dir = "markdown_analysis_results"
    
    print(f"\n开始分析 {folder_path} 中的Markdown文件...")
    print("支持的文件扩展名: .md, .markdown, .mdown, .mkd")
    print("-" * 60)
    
    # 创建分析器并开始分析
    analyzer = MarkdownInfoDensityAnalyzer()
    analyzer.analyze_markdown_folder(folder_path, output_dir)

if __name__ == "__main__":
    main()
