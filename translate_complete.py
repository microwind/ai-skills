#!/usr/bin/env python3
"""
完整翻译脚本 - 使用全面的短语和句子翻译
"""
import re
from pathlib import Path

# 完整的英中翻译对照表（长的短语优先）
PHRASE_TRANSLATIONS = [
    # 完整句子和长短语
    ('Optimize queries before they slow down your system', '在查询拖慢系统之前进行优化'),
    ('Bad queries compound as data grows', '坏查询会随着数据增长而加剧'),
    ('when they slow down your system', '当它们拖慢你的系统时'),
    ('Invalid Kubernetes manifests deploy silently then fail mysteriously', '无效的Kubernetes清单会静默部署然后神秘失败'),
    ('Validate before deploying', '在部署前进行验证'),
    ('Misconfigured cloud resources leak data, waste money, and expose security vulnerabilities', '配置错误的云资源会泄露数据、浪费金钱并暴露安全漏洞'),
    ('Slow SQL queries compound', '缓慢的SQL查询会加剧'),
    ('One slow query becomes 100 slow transactions', '一个缓慢的查询会变成100个缓慢的事务'),
    ('Optimize before scaling', '在扩展前进行优化'),
    ('Bad CI/CD pipelines hide problems until production', '糟糕的CI/CD管道会隐藏问题直到生产环境'),
    ('Validate pipeline quality to catch issues early', '验证管道质量以尽早发现问题'),
    ('Good infrastructure scales', '好的基础设施可以扩展'),
    ('Bad infrastructure breaks at scale', '糟糕的基础设施在扩展时会崩溃'),
    ('Analyze before problems cascade', '在问题级联之前进行分析'),
    ('Web frameworks enable fast development', 'Web框架实现快速开发'),
    ('bad patterns create maintenance nightmares', '糟糕的模式会造成维护噩梦'),

    # 关键短语
    ('running slow', '运行缓慢'),
    ('Database CPU spiking', '数据库CPU飙升'),
    ('App performance degrading', '应用性能下降'),
    ('Planning data model', '规划数据模型'),
    ('Reviewing SQL queries', '审查SQL查询'),
    ('Investigating N+1 problems', '调查N+1问题'),
    ('Query Analysis', '查询分析'),
    ('Index Detection', '索引检测'),
    ('Optimization Tips', '优化技巧'),
    ('Full Table Scan', '全表扫描'),
    ('Inefficient JOIN', '低效的JOIN'),
    ('Missing WHERE Clause', '缺少WHERE子句'),
    ('Implicit Type Conversion', '隐式类型转换'),
    ('OR Condition Inefficiency', 'OR条件低效'),
    ('Lazy-loaded Queries', '懒加载查询'),
    ('View Too Complex', '视图过于复杂'),
    ('Circular Dependencies', '循环依赖'),
    ('Slow Queries', '查询缓慢'),
    ('High Specificity', '高特异性'),
    ('Not Responsive', '不响应式'),
    ('Over-Specific Component', '过度特定的组件'),
    ('Unnecessary Re-renders', '不必要的重新渲染'),
    ('Large Dependencies', '大型依赖'),
    ('No Code Splitting', '没有代码分割'),
    ('No Type Hints', '没有类型提示'),
    ('Mutable Default Arguments', '可变默认参数'),

    # 核心概念和标题
    ('Overview', '概述'),
    ('When to Use', '何时使用'),
    ('Common Issues', '常见问题'),
    ('Verification Checklist', '验证检查清单'),
    ('How to Use', '如何使用'),
    ('When Stuck', '当困难时'),
    ('Anti-Patterns', '反模式'),
    ('Anti-Patterns (Red Flags)', '反模式（红旗警告）'),
    ('Related Skills', '相关技能'),
    ('Design Patterns', '设计模式'),
    ('Best Practices', '最佳实践'),
    ('Always', '始终'),
    ('Trigger phrases', '触发短语'),
    ('Core Principle', '核心原则'),
    ('Problem', '问题'),
    ('Consequence', '后果'),
    ('Solution', '解决方案'),

    # 常见动词
    ('Identify', '识别'),
    ('Find', '查找'),
    ('Detect', '检测'),
    ('Analyze', '分析'),
    ('Check', '检查'),
    ('Review', '审查'),
    ('Validate', '验证'),
    ('Optimize', '优化'),
    ('Improve', '改进'),
    ('Rewrite', '重写'),
    ('Add', '添加'),
    ('Use', '使用'),
    ('Batch', '批处理'),
    ('Cache', '缓存'),

    # 技术词汇
    ('query', '查询'),
    ('Query', '查询'),
    ('queries', '查询'),
    ('Queries', '查询'),
    ('index', '索引'),
    ('Index', '索引'),
    ('indexes', '索引'),
    ('Indexes', '索引'),
    ('database', '数据库'),
    ('Database', '数据库'),
    ('table', '表'),
    ('Table', '表'),
    ('column', '列'),
    ('Column', '列'),
    ('scans', '扫描'),
    ('scanning', '扫描'),
    ('scan', '扫描'),
    ('Scan', '扫描'),
    ('Execution', '执行'),
    ('execution', '执行'),

    # 形容词
    ('slow', '缓慢'),
    ('Slow', '缓慢的'),
    ('fast', '快速'),
    ('Fast', '快速的'),
    ('efficient', '高效的'),
    ('Efficient', '高效的'),
    ('inefficient', '低效的'),
    ('Inefficient', '低效的'),
    ('unused', '未使用的'),
    ('Unused', '未使用的'),
    ('missing', '缺失的'),
    ('Missing', '缺失的'),
    ('full', '完整的'),
    ('Full', '完整的'),

    # 常用短语
    ('full table scan', '全表扫描'),
    ('N+1 problem', 'N+1问题'),
    ('N+1 Query', 'N+1查询'),
    ('N+1', 'N+1'),
    ('no index', '没有索引'),
    ('without WHERE', '没有WHERE'),
    ('composite index', '复合索引'),
    ('selectivity', '选择性'),
    ('performance', '性能'),
    ('Performance', '性能'),
    ('efficiency', '效率'),
    ('Efficiency', '效率'),
    ('memory', '内存'),
    ('Memory', '内存'),
    ('CPU', 'CPU'),
    ('Disk', '磁盘'),
    ('disk', '磁盘'),
]

WORD_TRANSLATIONS = [
    # 单词翻译
    (r'\bAnalyzer\b', '分析器'),
    (r'\bValidator\b', '验证器'),
    (r'\bGenerator\b', '生成器'),
    (r'\bOptimizer\b', '优化器'),
    (r'\bTester\b', '测试器'),
    (r'\bScanner\b', '扫描器'),
    (r'\bFormatter\b', '格式化器'),
    (r'\bManager\b', '管理器'),
    (r'\bMonitor\b', '监视器'),
    (r'\bDeployer\b', '部署器'),
    (r'\bHandler\b', '处理器'),
    (r'\bTracer\b', '追踪器'),
    (r'\bLogger\b', '记录器'),
    (r'\bBuilder\b', '构建器'),
    (r'\bCompiler\b', '编译器'),
    (r'\bParser\b', '解析器'),
    (r'\bSerializer\b', '序列化器'),
    (r'\bDeserializer\b', '反序列化器'),
    (r'\bService\b', '服务'),
    (r'\bGateway\b', '网关'),
    (r'\bProxy\b', '代理'),
    (r'\bRouter\b', '路由器'),
    (r'\bController\b', '控制器'),
    (r'\bMiddleware\b', '中间件'),
    (r'\bPlugin\b', '插件'),
    (r'\bExtension\b', '扩展'),
    (r'\bIntegration\b', '集成'),
    (r'\bMigration\b', '迁移'),
    (r'\bConflict\b', '冲突'),
    (r'\bException\b', '异常'),
    (r'\bError\b', '错误'),
]

def apply_translations(text):
    """应用翻译"""
    result = text

    # 首先应用长短语翻译
    for english, chinese in PHRASE_TRANSLATIONS:
        result = result.replace(english, chinese)

    # 然后应用单词翻译（使用正则表达式）
    for pattern, replacement in WORD_TRANSLATIONS:
        result = re.sub(pattern, replacement, result)

    return result

def translate_skill_file(file_path):
    """翻译SKILL.md文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code_block = False
    in_frontmatter = False
    translated_lines = []

    for i, line in enumerate(lines):
        # 检查frontmatter
        if i == 0 and line.strip() == '---':
            in_frontmatter = True
            translated_lines.append(line)
            continue

        if in_frontmatter:
            if line.strip() == '---':
                in_frontmatter = False
            translated_lines.append(line)
            continue

        # 检查代码块边界
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            translated_lines.append(line)
            continue

        # 代码块内不翻译
        if in_code_block:
            translated_lines.append(line)
            continue

        # 跳过空行和仅有空格的行
        if not line.strip():
            translated_lines.append(line)
            continue

        # 翻译行
        translated_line = apply_translations(line)
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
