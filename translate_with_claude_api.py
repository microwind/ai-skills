#!/usr/bin/env python3
"""
使用Claude API生成高质量的中文skill翻译
"""
import os
import json
import re
from pathlib import Path
from anthropic import Anthropic

client = Anthropic()

# 保留不翻译的内容
KEEP_AS_IS = {
    'API', 'REST', 'HTTP', 'JSON', 'SQL', 'YAML', 'XML',
    'GET', 'POST', 'PUT', 'DELETE', 'PATCH',
    'Python', 'JavaScript', 'TypeScript', 'Java', 'Go', 'Rust', 'C++',
    'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure',
    'React', 'Vue', 'Angular', 'Django', 'Flask', 'Spring', 'Express',
    'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
    'Git', 'GitHub', 'GitLab', 'Jira', 'Slack',
    'Docker', 'Jenkins', 'Travis', 'CircleCI',
    'N+1', 'CORS', 'CSRF', 'XSS', 'JWT', 'OAuth', 'LDAP',
    'EOF', 'MIT', 'Apache', 'GPL',
}

def translate_with_claude(english_text, skill_name):
    """使用Claude AI翻译单个skill文件"""

    prompt = f"""你是一个专业的技术文档翻译专家，需要将以下英文技能文档翻译成中文。

翻译要求：
1. 完全翻译成中文，不要保留英文混杂
2. 保留所有代码块、代码示例不翻译
3. 保留所有技术术语如：API, REST, HTTP, JSON, SQL, YAML, XML, GET, POST, PUT, DELETE, PATCH等
4. 保留所有编程语言名称：Python, JavaScript, TypeScript, Java, Go, Rust, C++等
5. 保留所有框架/工具名称：Docker, Kubernetes, AWS, React, Vue, Django, Flask等
6. 保留所有代码文件路径和代码示例
7. 保留markdown格式和结构
8. 翻译后的文档应该易于理解，用词准确

技能名称：{skill_name}

英文内容：
---
{english_text}
---

请直接返回翻译后的中文内容，不要包含任何其他说明或注释。
"""

    message = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

def translate_file(file_path):
    """翻译单个文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取frontmatter和body
    if content.startswith('---'):
        parts = content.split('---', 2)
        frontmatter = parts[1]
        body = parts[2] if len(parts) > 2 else ''

        # 翻译body部分
        skill_name = file_path.parent.name
        translated_body = translate_with_claude(body, skill_name)

        # 重新组合
        translated_content = f'---{frontmatter}---{translated_body}'
    else:
        translated_content = translate_with_claude(content, file_path.parent.name)

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(translated_content)

    return file_path

def main():
    """主函数"""
    base_path = Path('/Users/jarry/github/ai-skills')

    # 找所有SKILL.md文件
    skill_files = sorted(base_path.rglob('SKILL.md'))

    print(f"🔍 找到 {len(skill_files)} 个 SKILL.md 文件")
    print(f"⏳ 开始翻译...\n")

    success = 0
    failed = 0

    for i, file_path in enumerate(skill_files, 1):
        try:
            rel_path = file_path.relative_to(base_path)
            print(f"⏳ [{i}/{len(skill_files)}] 正在翻译: {rel_path}")

            translate_file(file_path)

            print(f"✅ [{i}/{len(skill_files)}] 已完成: {rel_path}\n")
            success += 1
        except Exception as e:
            rel_path = file_path.relative_to(base_path)
            print(f"❌ [{i}/{len(skill_files)}] 失败: {rel_path}")
            print(f"   错误: {str(e)}\n")
            failed += 1

    print(f"\n{'='*60}")
    print(f"✅ 成功翻译: {success} 个文件")
    print(f"❌ 失败: {failed} 个文件")
    print(f"✅ 翻译完成!")

if __name__ == '__main__':
    main()
