#!/usr/bin/env python3
"""
技能库生成脚本 - 创建中文AI Skills编程知识库
"""

import os
import json
from pathlib import Path

# 定义所有Skills
SKILLS_STRUCTURE = {
    "backend": [
        {"name": "error-handling-logging", "title": "错误处理与日志系统"},
        {"name": "caching-strategies", "title": "缓存策略与实现"},
        {"name": "async-tasks", "title": "异步任务与消息队列"},
        {"name": "file-upload", "title": "文件上传处理"},
        {"name": "data-validation", "title": "数据验证与序列化"},
        {"name": "graphql-api", "title": "GraphQL API开发"},
    ],
    "frontend": [
        {"name": "react-components", "title": "React组件最佳实践"},
        {"name": "state-management", "title": "状态管理（Redux/Context）"},
        {"name": "performance-optimization", "title": "前端性能优化"},
        {"name": "responsive-design", "title": "响应式设计"},
        {"name": "form-handling", "title": "表单处理与验证"},
        {"name": "testing-frontend", "title": "前端测试"},
    ],
    "frameworks": [
        {"name": "django-development", "title": "Django Web框架"},
        {"name": "fastapi-setup", "title": "FastAPI高性能API"},
        {"name": "spring-boot", "title": "Spring Boot应用开发"},
        {"name": "express-js", "title": "Express.js服务"},
        {"name": "nestjs-architecture", "title": "NestJS企业架构"},
        {"name": "flask-microframework", "title": "Flask轻量级应用"},
    ],
    "cloud-native": [
        {"name": "docker-containerization", "title": "Docker容器化"},
        {"name": "kubernetes-basics", "title": "Kubernetes编排"},
        {"name": "serverless-functions", "title": "无服务器函数"},
        {"name": "container-registry", "title": "容器镜像管理"},
        {"name": "networking-policies", "title": "网络策略配置"},
    ],
    "microservices": [
        {"name": "service-communication", "title": "服务间通信"},
        {"name": "service-discovery", "title": "服务治理与发现"},
        {"name": "distributed-tracing", "title": "分布式链路追踪"},
        {"name": "circuit-breaker", "title": "熔断器模式"},
        {"name": "api-gateway", "title": "API网关设计"},
    ],
    "system-design": [
        {"name": "high-concurrency", "title": "高并发系统设计"},
        {"name": "distributed-consistency", "title": "分布式一致性"},
        {"name": "cap-theorem", "title": "CAP定理应用"},
        {"name": "database-sharding", "title": "数据库分片策略"},
        {"name": "cache-invalidation", "title": "缓存失效策略"},
    ],
    "database": [
        {"name": "sql-optimization", "title": "SQL优化与索引"},
        {"name": "transaction-management", "title": "事务管理"},
        {"name": "nosql-databases", "title": "NoSQL数据库应用"},
        {"name": "backup-recovery", "title": "备份与恢复"},
    ],
    "devops": [
        {"name": "ci-cd-pipeline", "title": "CI/CD流水线"},
        {"name": "infrastructure-as-code", "title": "基础设施即代码"},
        {"name": "monitoring-alerting", "title": "监控与告警"},
        {"name": "log-aggregation", "title": "日志聚合分析"},
    ],
    "code-quality": [
        {"name": "code-review", "title": "代码审查与标准"},
        {"name": "refactoring-patterns", "title": "重构模式"},
        {"name": "testing-strategies", "title": "测试策略与覆盖"},
        {"name": "code-optimization", "title": "代码优化技巧"},
    ],
    "languages": [
        {"name": "python-advanced", "title": "Python高级特性"},
        {"name": "javascript-es6", "title": "JavaScript ES6+ 特性"},
        {"name": "golang-patterns", "title": "Go语言模式"},
        {"name": "rust-systems", "title": "Rust系统编程"},
    ],
    "tools": [
        {"name": "git-workflows", "title": "Git工作流"},
        {"name": "docker-compose", "title": "Docker Compose编排"},
        {"name": "api-documentation", "title": "API文档生成"},
    ],
}

def create_skill_files(category: str, skill_name: str, skill_title: str):
    """为单个skill创建文件结构"""
    base_path = Path(f"/Users/jarry/github/ai-skills/{category}/{skill_name}")
    base_path.mkdir(parents=True, exist_ok=True)

    # 创建脚本目录
    (base_path / "scripts").mkdir(exist_ok=True)
    (base_path / "references").mkdir(exist_ok=True)
    (base_path / "assets").mkdir(exist_ok=True)

    # 创建README
    readme_content = f"""# {skill_title}

中文AI Skills编程知识库 - {skill_title}

## 快速开始

请查看以下文件了解详情：

- `中文说明.md` - 中文详细说明
- `SKILL.md` - 标准技能说明（英文）
- `scripts/` - 示例代码和脚本
- `references/` - 参考文档

## 目标受众

- 初级开发者 - 学习{skill_title}的基础知识
- 中级开发者 - 提升实战能力
- 高级开发者 - 深入理解最佳实践

## 前置条件

- 基础编程知识
- 对相关概念的理解

## 主要内容

1. 核心概念讲解
2. 实战代码示例
3. 最佳实践总结
4. 常见问题解答
"""

    (base_path / "README.md").write_text(readme_content, encoding='utf-8')

    # 创建SKILL.md基础框架
    skill_md = f"""# {skill_title}

## Purpose
Learn {skill_title} with practical examples and best practices.

## Use Cases
- Use case 1
- Use case 2
- Use case 3

## Prerequisites
- Basic programming knowledge
- Understanding of related concepts

## Core Steps
1. Step 1
2. Step 2
3. Step 3

## Key Code Examples
```python
# Example code
pass
```

## FAQ
Q: Common question?
A: Answer here.

## Resources
- [Resource Name](https://example.com)
- [Documentation](https://docs.example.com)
"""

    (base_path / "SKILL.md").write_text(skill_md, encoding='utf-8')

    # 创建中文说明基础框架
    zh_content = f"""# {skill_title}

## 目的
深入学习{skill_title}，掌握实战应用和最佳实践。

## 使用场景
- 场景1
- 场景2
- 场景3

## 前置条件
- 基础编程知识
- 相关概念的理解

## 核心步骤
1. 步骤1
2. 步骤2
3. 步骤3

## 关键代码示例
```python
# 示例代码
pass
```

## 常见问题

**Q: 常见问题？**
A: 答案说明

## 相关资源
- [资源名称](https://example.com)
- [文档](https://docs.example.com)
"""

    (base_path / "中文说明.md").write_text(zh_content, encoding='utf-8')

    # 创建示例脚本
    example_script = f"""#!/usr/bin/env python3
\"\"\"
{skill_title} - 示例脚本
\"\"\"

def main():
    print(f'开始学习: {skill_title}')
    # 添加你的代码

if __name__ == '__main__':
    main()
"""

    (base_path / "scripts" / "example.py").write_text(example_script, encoding='utf-8')

    print(f"✓ 已创建: {category}/{skill_name}")

def main():
    """主函数"""
    print("🚀 开始生成中文AI Skills编程知识库...\n")

    total = 0
    for category, skills in SKILLS_STRUCTURE.items():
        print(f"\n📁 分类: {category}")
        for skill in skills:
            create_skill_files(category, skill['name'], skill['title'])
            total += 1

    print(f"\n✅ 完成！共创建 {total} 个Skills\n")

if __name__ == '__main__':
    main()
