#!/usr/bin/env python3
"""
更智能的中文翻译脚本 - 避免部分替换问题
"""
import os
import re
from pathlib import Path

# 主要section标题翻译 (优先处理)
SECTION_TRANSLATIONS = {
    "## Overview": "## 概述",
    "## When to Use": "## 何时使用",
    "## What ": "## 什么",  # What Does... What Is...
    " Does": "的功能",
    "## Common Issues": "## 常见问题",
    "## Verification Checklist": "## 验证检查清单",
    "## How to Use": "## 如何使用",
    "## How to": "## 如何",
    "## When Stuck": "## 当遇到困难时",
    "## Anti-Patterns (Red Flags)": "## 反模式（红旗警告）",
    "## Anti-Patterns": "## 反模式",
    "## Red Flags": "## 红旗警告",
    "## Related Skills": "## 相关技能",
    "## Design Patterns": "## 设计模式",

    # 重要标记
    "**Always:**": "**始终:**",
    "**Trigger phrases:**": "**触发短语:**",
    "**Core Principle:**": "**核心原则:**",
    "**Problem:**": "**问题:**",
    "**Consequence:**": "**后果:**",
    "**Solution:**": "**解决方案:**",
}

# 常见技术术语（完整单词匹配）
TECHNICAL_TERMS = {
    r'\bAPI\b': 'API',
    r'\bRESTful\b': 'RESTful',
    r'\bREST\b': 'REST',
    r'\bHTTP\b': 'HTTP',
    r'\bJSON\b': 'JSON',
    r'\bXML\b': 'XML',
    r'\bYAML\b': 'YAML',
    r'\bSQL\b': 'SQL',
    r'\bPython\b': 'Python',
    r'\bJavaScript\b': 'JavaScript',
    r'\bTypeScript\b': 'TypeScript',
    r'\bGET\b': 'GET',
    r'\bPOST\b': 'POST',
    r'\bPUT\b': 'PUT',
    r'\bPATCH\b': 'PATCH',
    r'\bDELETE\b': 'DELETE',
    r'\bDocker\b': 'Docker',
    r'\bKubernetes\b': 'Kubernetes',
    r'\bAWS\b': 'AWS',
    r'\bGCP\b': 'GCP',
    r'\bFlask\b': 'Flask',
    r'\bDjango\b': 'Django',
    r'\bReact\b': 'React',
    r'\bVue\b': 'Vue',
    r'\bSpring\b': 'Spring',
}

# 重要词汇翻译 (使用单词边界)
VOCABULARY = {
    r'\bendpoint\b': '端点',
    r'\bEndpoint\b': '端点',
    r'\bendpoints\b': '端点',
    r'\bEndpoints\b': '端点',
    r'\brequest\b': '请求',
    r'\bRequest\b': '请求',
    r'\brequests\b': '请求',
    r'\bRequests\b': '请求',
    r'\bresponse\b': '响应',
    r'\bResponse\b': '响应',
    r'\bresponses\b': '响应',
    r'\bResponses\b': '响应',
    r'\bheader\b': '头部',
    r'\bHeader\b': '头部',
    r'\bheaders\b': '头部',
    r'\bHeaders\b': '头部',
    r'\bstatus code\b': '状态码',
    r'\bStatus code\b': '状态码',
    r'\bStatus codes\b': '状态码',
    r'\bauthentication\b': '身份认证',
    r'\bAuthentication\b': '身份认证',
    r'\bauthorization\b': '授权',
    r'\bAuthorization\b': '授权',
    r'\berror\b': '错误',
    r'\bError\b': '错误',
    r'\berrors\b': '错误',
    r'\bErrors\b': '错误',
    r'\bquery\b': '查询',
    r'\bQuery\b': '查询',
    r'\bdatabase\b': '数据库',
    r'\bDatabase\b': '数据库',
    r'\bservice\b': '服务',
    r'\bService\b': '服务',
    r'\bservices\b': '服务',
    r'\bServices\b': '服务',
    r'\bcomponent\b': '组件',
    r'\bComponent\b': '组件',
    r'\bcomponents\b': '组件',
    r'\bComponents\b': '组件',
    r'\bmodule\b': '模块',
    r'\bModule\b': '模块',
    r'\bmodules\b': '模块',
    r'\bModules\b': '模块',
    r'\btest\b': '测试',
    r'\bTest\b': '测试',
    r'\btesting\b': '测试',
    r'\bTesting\b': '测试',
    r'\bperformance\b': '性能',
    r'\bPerformance\b': '性能',
    r'\bsecurity\b': '安全',
    r'\bSecurity\b': '安全',
    r'\bvulnerability\b': '漏洞',
    r'\bVulnerability\b': '漏洞',
    r'\bdeployment\b': '部署',
    r'\bDeployment\b': '部署',
    r'\benvironment\b': '环境',
    r'\bEnvironment\b': '环境',
    r'\barchitecture\b': '架构',
    r'\bArchitecture\b': '架构',
    r'\bdesign\b': '设计',
    r'\bDesign\b': '设计',
    r'\bframework\b': '框架',
    r'\bFramework\b': '框架',
    r'\blibrary\b': '库',
    r'\bLibrary\b': '库',
    r'\bcache\b': '缓存',
    r'\bCache\b': '缓存',
    r'\bencryption\b': '加密',
    r'\bEncryption\b': '加密',
    r'\bindex\b': '索引',
    r'\bIndex\b': '索引',
    r'\bindexes\b': '索引',
    r'\bIndexes\b': '索引',
    r'\bmigration\b': '迁移',
    r'\bMigration\b': '迁移',
    r'\btransaction\b': '事务',
    r'\bTransaction\b': '事务',
    r'\bschema\b': '模式',
    r'\bSchema\b': '模式',
}

def translate_file_content(content):
    """翻译文件内容"""
    result = content

    # 1. 首先翻译section标题 (高优先级)
    for eng, chn in SECTION_TRANSLATIONS.items():
        result = result.replace(eng, chn)

    # 2. 翻译词汇（使用正则表达式避免部分替换）
    for pattern, translation in VOCABULARY.items():
        result = re.sub(pattern, translation, result)

    # 3. 技术术语保持不变（只确保它们被保留）
    # 这些已经在上面处理了

    return result

def process_skill_md(file_path):
    """处理SKILL.md文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translated = translate_file_content(content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(translated)

    return file_path

def process_forms_md(file_path):
    """处理forms.md文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # forms.md 通常只需要翻译标题
    translated = content

    # 翻译常见的检查清单标题
    translations = {
        'Checklist': '检查清单',
        'checklist': '检查清单',
        'Pre-use': '使用前',
        'During': '使用中',
        'Post-use': '使用后',
        '- [ ]': '- [ ]',
    }

    for eng, chn in translations.items():
        translated = translated.replace(eng, chn)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(translated)

    return file_path

# 处理所有SKILL.md文件
base_path = Path('/Users/jarry/github/ai-skills')
skill_files = list(base_path.rglob('SKILL.md'))
forms_files = list(base_path.rglob('forms.md'))

print(f"开始翻译 {len(skill_files)} 个SKILL.md文件...")
for i, file_path in enumerate(skill_files, 1):
    try:
        process_skill_md(file_path)
        print(f"✅ [{i}/{len(skill_files)}] 已翻译: {file_path.relative_to(base_path)}")
    except Exception as e:
        print(f"❌ [{i}/{len(skill_files)}] 错误: {file_path.relative_to(base_path)}")

print(f"\n开始翻译 {len(forms_files)} 个forms.md文件...")
for i, file_path in enumerate(forms_files, 1):
    try:
        process_forms_md(file_path)
        print(f"✅ [{i}/{len(forms_files)}] 已翻译: {file_path.relative_to(base_path)}")
    except Exception as e:
        print(f"❌ [{i}/{len(forms_files)}] 错误: {file_path.relative_to(base_path)}")

print(f"\n✅ 翻译完成!")
