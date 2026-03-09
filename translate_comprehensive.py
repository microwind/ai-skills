#!/usr/bin/env python3
"""
完整的中文翻译脚本 - 处理所有skill文件
"""
import os
import re
import yaml
from pathlib import Path

# YAML frontmatter字段翻译
YAML_TRANSLATIONS = {
    'name': 'name',
    'description': 'description',
    'license': 'license',
}

# 完整的英文到中文词汇字典
COMPREHENSIVE_TRANSLATIONS = {
    # 核心概念
    r'\b[Ss]kill\b': '技能',
    r'\b[Ss]kills\b': '技能',
    r'\b[Oo]verview\b': '概述',
    r'\b[Ww]hen\s+to\s+[Uu]se\b': '何时使用',
    r'\b[Hh]ow\s+to\s+[Uu]se\b': '如何使用',
    r'\b[Hh]ow\s+to\b': '如何',
    r'\b[Cc]ommon\s+[Ii]ssues\b': '常见问题',
    r'\b[Cc]ommon\s+[Pp]roblems\b': '常见问题',
    r'\b[Vv]erification\s+[Cc]hecklist\b': '验证检查清单',
    r'\b[Cc]hecklist\b': '检查清单',
    r'\b[Aa]nti-[Pp]atterns?\b': '反模式',
    r'\b[Rr]ed\s+[Ff]lags?\b': '红旗警告',
    r'\b[Dd]esign\s+[Pp]atterns?\b': '设计模式',
    r'\b[Rr]elated\s+[Ss]kills?\b': '相关技能',
    r'\b[Ww]hen\s+[Ss]tuck\b': '当遇到困难时',
    r'\b[Ww]hen\s+[Ss]tricks\b': '当困难时',

    # API相关
    r'\bAPI\b': 'API',
    r'\b[Ee]ndpoint\b': '端点',
    r'\b[Ee]ndpoints\b': '端点',
    r'\b[Rr]equest\b': '请求',
    r'\b[Rr]equests\b': '请求',
    r'\b[Rr]esponse\b': '响应',
    r'\b[Rr]esponses\b': '响应',
    r'\b[Hh]eader\b': '头部',
    r'\b[Hh]eaders\b': '头部',
    r'\b[Ss]tatus\s+code\b': '状态码',
    r'\b[Ss]tatus\s+codes\b': '状态码',
    r'\b[Rr]estful\b': 'RESTful',
    r'\bREST\b': 'REST',
    r'\bHTTP\b': 'HTTP',
    r'\bGET\b': 'GET',
    r'\bPOST\b': 'POST',
    r'\bPUT\b': 'PUT',
    r'\bPATCH\b': 'PATCH',
    r'\bDELETE\b': 'DELETE',
    r'\bJSON\b': 'JSON',
    r'\bXML\b': 'XML',
    r'\bYAML\b': 'YAML',

    # 安全相关
    r'\b[Aa]uthentication\b': '身份认证',
    r'\b[Aa]uthorization\b': '授权',
    r'\b[Ss]ecurity\b': '安全',
    r'\b[Ee]ncryption\b': '加密',
    r'\b[Vv]ulnerability\b': '漏洞',
    r'\b[Vv]ulnerabilities\b': '漏洞',
    r'\b[Tt]oken\b': '令牌',
    r'\b[Tt]okens\b': '令牌',
    r'\bJWT\b': 'JWT',
    r'\bOAuth\b': 'OAuth',
    r'\bCORS\b': 'CORS',

    # 数据库相关
    r'\b[Dd]atabase\b': '数据库',
    r'\b[Qq]uery\b': '查询',
    r'\b[Qq]ueries\b': '查询',
    r'\bSQL\b': 'SQL',
    r'\b[Ii]ndex\b': '索引',
    r'\b[Ii]ndexes\b': '索引',
    r'\b[Ii]ndices\b': '索引',
    r'\b[Ss]chema\b': '模式',
    r'\b[Mm]igration\b': '迁移',
    r'\b[Mm]igrations\b': '迁移',
    r'\b[Tt]ransaction\b': '事务',
    r'\b[Tt]ransactions\b': '事务',

    # 代码相关
    r'\b[Cc]ode\b': '代码',
    r'\b[Ff]unction\b': '函数',
    r'\b[Ff]unctions\b': '函数',
    r'\b[Vv]ariable\b': '变量',
    r'\b[Vv]ariables\b': '变量',
    r'\b[Ll]ibrary\b': '库',
    r'\b[Ff]ramework\b': '框架',
    r'\b[Cc]omponent\b': '组件',
    r'\b[Cc]omponents\b': '组件',
    r'\b[Mm]odule\b': '模块',
    r'\b[Mm]odules\b': '模块',
    r'\b[Pp]ackage\b': '包',
    r'\b[Pp]ackages\b': '包',

    # 测试相关
    r'\b[Tt]est\b': '测试',
    r'\b[Tt]esting\b': '测试',
    r'\b[Uu]nit\s+[Tt]est\b': '单元测试',
    r'\b[Ii]ntegration\s+[Tt]est\b': '集成测试',
    r'\b[Ee]2[Ee]\s+[Tt]est\b': '端到端测试',

    # 部署和运维
    r'\b[Dd]eployment\b': '部署',
    r'\b[Ee]nvironment\b': '环境',
    r'\b[Cc]ontainer\b': '容器',
    r'\b[Cc]ontainers\b': '容器',
    r'\b[Dd]ocker\b': 'Docker',
    r'\b[Kk]ubernetes\b': 'Kubernetes',
    r'\b[Cc]i/cd\b': 'CI/CD',
    r'\b[Mm]onitoring\b': '监控',
    r'\b[Ll]ogging\b': '日志',
    r'\b[Ll]og\b': '日志',

    # 性能
    r'\b[Pp]erformance\b': '性能',
    r'\b[Pp]erfomance\b': '性能',
    r'\b[Ss]calability\b': '可扩展性',
    r'\b[Cc]ache\b': '缓存',
    r'\b[Cc]aching\b': '缓存',
    r'\b[Oo]ptimization\b': '优化',
    r'\b[Oo]ptimize\b': '优化',

    # 架构
    r'\b[Aa]rchitecture\b': '架构',
    r'\b[Dd]esign\b': '设计',
    r'\b[Pp]attern\b': '模式',
    r'\b[Pp]atterns\b': '模式',
    r'\b[Rr]efactor\b': '重构',
    r'\b[Rr]efactoring\b': '重构',

    # 错误相关
    r'\b[Ee]rror\b': '错误',
    r'\b[Ee]rrors\b': '错误',
    r'\b[Ee]xception\b': '异常',
    r'\b[Ee]xceptions\b': '异常',
    r'\b[Bb]ug\b': '错误',
    r'\b[Bb]ugs\b': '错误',
    r'\b[Dd]ebug\b': '调试',
    r'\b[Dd]ebugging\b': '调试',
    r'\b[Tt]roubleshoot\b': '故障排除',

    # 常用短语
    r'\b[Bb]est\s+[Pp]ractice\b': '最佳实践',
    r'\b[Bb]est\s+[Pp]ractices\b': '最佳实践',
    r'\b[Cc]ore\s+[Pp]rinciple\b': '核心原则',
    r'\b[Ww]orst\s+[Pp]ractice\b': '最差实践',
    r'\b[Pp]roblem\b': '问题',
    r'\b[Pp]roblems\b': '问题',
    r'\b[Ss]olution\b': '解决方案',
    r'\b[Ss]olutions\b': '解决方案',
    r'\b[Cc]onsequence\b': '后果',
    r'\b[Cc]onsequences\b': '后果',
    r'\b[Ee]xample\b': '示例',
    r'\b[Ee]xamples\b': '示例',
    r'\b[Tt]rigger\s+phrase\b': '触发短语',
    r'\b[Aa]lways\b': '始终',

    # 其他常用词
    r'\b[Ss]ervice\b': '服务',
    r'\b[Ss]ervices\b': '服务',
    r'\b[Ss]ystem\b': '系统',
    r'\b[Ss]ystems\b': '系统',
    r'\b[Cc]lient\b': '客户端',
    r'\b[Cc]lients\b': '客户端',
    r'\b[Ss]erver\b': '服务器',
    r'\b[Ss]ervers\b': '服务器',
    r'\b[Ii]ntegration\b': '集成',
    r'\b[Rr]esource\b': '资源',
    r'\b[Rr]esources\b': '资源',
    r'\b[Vv]ersion\b': '版本',
    r'\b[Vv]ersions\b': '版本',
    r'\b[Cc]ompliance\b': '合规性',
    r'\b[Mm]igration\b': '迁移',
    r'\b[Bb]reak\b': '破坏',
    r'\b[Pp]agination\b': '分页',
    r'\b[Ff]ilter\b': '过滤',
    r'\b[Ss]ort\b': '排序',
}

# 标记和格式化保留
SECTION_HEADERS = {
    '## Overview': '## 概述',
    '## When to Use': '## 何时使用',
    '## How to Use': '## 如何使用',
    '## Common Issues': '## 常见问题',
    '## Common Problems': '## 常见问题',
    '## Verification Checklist': '## 验证检查清单',
    '## Anti-Patterns': '## 反模式',
    '## Red Flags': '## 红旗警告',
    '## Related Skills': '## 相关技能',
    '## When Stuck': '## 当困难时',
    '## Design Patterns': '## 设计模式',
    '**Always:**': '**始终:**',
    '**Core Principle:**': '**核心原则:**',
    '**Problem:**': '**问题:**',
    '**Consequence:**': '**后果:**',
    '**Solution:**': '**解决方案:**',
    '**Trigger phrases:**': '**触发短语:**',
    '| Problem': '| 问题',
    '| Solution': '| 解决方案',
}

def is_code_block(line):
    """检查是否在代码块中"""
    return line.strip().startswith('```')

def translate_text(text):
    """翻译文本，保留代码块"""
    lines = text.split('\n')
    in_code_block = False
    result = []

    for line in lines:
        # 处理代码块开始/结束
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue

        # 如果在代码块中，不翻译
        if in_code_block:
            result.append(line)
            continue

        # 翻译section标题
        translated_line = line
        for eng, chn in SECTION_HEADERS.items():
            if eng in translated_line:
                translated_line = translated_line.replace(eng, chn)

        # 翻译词汇（使用正则表达式）
        for pattern, replacement in COMPREHENSIVE_TRANSLATIONS.items():
            translated_line = re.sub(pattern, replacement, translated_line)

        result.append(translated_line)

    return '\n'.join(result)

def translate_skill_file(file_path):
    """翻译skill文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 分离frontmatter和内容
    if content.startswith('---'):
        parts = content.split('---', 2)
        frontmatter = parts[1]
        body = parts[2] if len(parts) > 2 else ''

        # 翻译frontmatter中的描述
        translated_frontmatter = frontmatter
        translated_body = translate_text(body)

        translated_content = f'---{translated_frontmatter}---{translated_body}'
    else:
        translated_content = translate_text(content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(translated_content)

    return file_path

def main():
    """主函数"""
    base_path = Path('/Users/jarry/github/ai-skills')

    # 查找所有skill相关文件
    skill_files = list(base_path.rglob('SKILL.md'))
    forms_files = list(base_path.rglob('forms.md'))
    reference_files = list(base_path.rglob('reference.md'))

    all_files = skill_files + forms_files + reference_files

    print(f"🔍 找到 {len(skill_files)} 个 SKILL.md 文件")
    print(f"🔍 找到 {len(forms_files)} 个 forms.md 文件")
    print(f"🔍 找到 {len(reference_files)} 个 reference.md 文件")
    print(f"🔍 总共 {len(all_files)} 个文件\n")

    success = 0
    failed = 0

    for i, file_path in enumerate(all_files, 1):
        try:
            translate_skill_file(file_path)
            rel_path = file_path.relative_to(base_path)
            print(f"✅ [{i}/{len(all_files)}] {rel_path}")
            success += 1
        except Exception as e:
            rel_path = file_path.relative_to(base_path)
            print(f"❌ [{i}/{len(all_files)}] {rel_path} - {str(e)}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"✅ 成功翻译: {success} 个文件")
    print(f"❌ 失败: {failed} 个文件")
    print(f"✅ 翻译完成!")

if __name__ == '__main__':
    main()
