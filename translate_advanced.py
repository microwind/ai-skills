#!/usr/bin/env python3
"""
高级翻译脚本 - 完整的英中对照翻译
"""
import re
from pathlib import Path

# 完整的英文到中文翻译对照表（按长度排序，最长的先）
TRANSLATIONS = [
    # 长句子和短语
    ('Detailed analysis and validation of', '详细的分析和验证'),
    ('when they slow down your system', '当它们拖慢你的系统时'),
    ('Bad queries compound as data grows', '坏的查询在数据增长时会加剧'),
    ('Optimize queries before they slow down your system', '在查询拖慢系统之前进行优化'),
    ('Bad queries compound as', '糟糕的查询会随着'),
    ('running slow', '运行缓慢'),
    ('Database CPU spiking', '数据库CPU飙升'),
    ('App performance degrading', '应用性能下降'),
    ('Planning data model', '规划数据模型'),
    ('Reviewing SQL queries', '审查SQL查询'),
    ('Investigating N+1 problems', '调查N+1问题'),

    # 核心标题和章节
    (r'\bOverview\b', '概述'),
    (r'\bWhen to Use\b', '何时使用'),
    (r'\bWhat .* Does\b', '功能'),
    (r'\bCommon Issues\b', '常见问题'),
    (r'\bCore Principle\b', '核心原则'),
    (r'\bAlways\b', '始终'),
    (r'\bTrigger phrases\b', '触发短语'),

    # 技术术语
    (r'\bAnalysis\b', '分析'),
    (r'\bDetection\b', '检测'),
    (r'\bOptimization\b', '优化'),
    (r'\bTips\b', '技巧'),
    (r'\bProblem\b', '问题'),
    (r'\bConsequence\b', '后果'),
    (r'\bSolution\b', '解决方案'),

    # 数据库相关
    (r'\bquery\b', '查询'),
    (r'\bQuery\b', '查询'),
    (r'\bqueries\b', '查询'),
    (r'\bQueries\b', '查询'),
    (r'\bindex\b', '索引'),
    (r'\bIndex\b', '索引'),
    (r'\bindexes\b', '索引'),
    (r'\bIndexes\b', '索引'),
    (r'\bdatabase\b', '数据库'),
    (r'\bDatabase\b', '数据库'),
    (r'\btable\b', '表'),
    (r'\bTable\b', '表'),
    (r'\bcolumn\b', '列'),
    (r'\bColumn\b', '列'),
    (r'\bscans\b', '扫描'),
    (r'\bscanning\b', '扫描'),
    (r'\bExecut', '执行'),

    # 常见词汇
    (r'\bIdentify\b', '识别'),
    (r'\bFind\b', '查找'),
    (r'\bDetect\b', '检测'),
    (r'\bAnalyze\b', '分析'),
    (r'\bCheck\b', '检查'),
    (r'\bRewrite\b', '重写'),
    (r'\bAdd\b', '添加'),
    (r'\bUse\b', '使用'),
    (r'\bBatch\b', '批处理'),
    (r'\bCache\b', '缓存'),
    (r'\bperformance\b', '性能'),
    (r'\bPerformance\b', '性能'),
    (r'\befficiency\b', '效率'),
    (r'\befficient\b', '高效的'),
    (r'\binefficient\b', '低效的'),
    (r'\bslow\b', '缓慢'),
    (r'\bfull table scan', '全表扫描'),
    (r'\bno index', '无索引'),
    (r'\bunused\b', '未使用的'),
    (r'\bmissing\b', '缺失的'),

    # 短语和句子片段
    (r'for each user', '对于每个用户'),
    (r'Disk I/O increases', '磁盘I/O增加'),
    (r'CPU usage high', 'CPU使用率高'),
    (r'Temporary tables created', '创建了临时表'),
    (r'High memory usage', '高内存使用'),
    (r'composite index', '复合索引'),
    (r'selectivity', '选择性'),
]

def translate_line(line):
    """翻译单行文本"""
    translated = line

    # 跳过代码块、代码示例、URL等
    if line.strip().startswith('```') or line.strip().startswith('#') and '```' in line:
        return line

    if line.strip().startswith('http') or 'github.com' in line:
        return line

    # 应用翻译
    for pattern, replacement in TRANSLATIONS:
        # 使用不同的替换方法
        if pattern.startswith(r'\b'):
            # 正则表达式模式
            translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
        else:
            # 直接字符串替换
            translated = translated.replace(pattern, replacement)

    return translated

def translate_skill_file(file_path):
    """翻译SKILL.md文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code_block = False
    translated_lines = []

    for line in lines:
        # 检查代码块边界
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            translated_lines.append(line)
            continue

        # 代码块内不翻译
        if in_code_block:
            translated_lines.append(line)
            continue

        # 翻译行
        translated_line = translate_line(line)
        translated_lines.append(translated_line)

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)

def main():
    """主函数"""
    base_path = Path('/Users/jarry/github/ai-skills')

    # 只翻译SKILL.md文件
    skill_files = sorted(base_path.rglob('SKILL.md'))

    print(f"🔍 找到 {len(skill_files)} 个 SKILL.md 文件")
    print(f"⏳ 开始翻译...\n")

    success = 0
    failed = 0

    for i, file_path in enumerate(skill_files, 1):
        try:
            rel_path = file_path.relative_to(base_path)
            translate_skill_file(file_path)
            print(f"✅ [{i}/{len(skill_files)}] {rel_path}")
            success += 1
        except Exception as e:
            rel_path = file_path.relative_to(base_path)
            print(f"❌ [{i}/{len(skill_files)}] {rel_path} - {str(e)}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"✅ 成功翻译: {success} 个SKILL.md文件")
    print(f"❌ 失败: {failed} 个文件")
    print(f"✅ 翻译完成!")

if __name__ == '__main__':
    main()
