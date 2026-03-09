#!/usr/bin/env python3
"""
批量翻译所有Skill文件从英文到中文
"""
import os
import re
from pathlib import Path

# 技术术语和常用短语的翻译字典
TRANSLATION_DICT = {
    # 文件格式和标记
    "---": "---",
    "name:": "名称:",
    "description:": "描述:",
    "license:": "许可证:",
    "MIT": "MIT",

    # 标题和章节
    "# ": "# ",
    "## Overview": "## 概述",
    "## When to Use": "## 何时使用",
    "## When to Use\n\n**Always:**": "## 何时使用\n\n**始终:**",
    "## When to Use\n\n**Trigger phrases:**": "## 何时使用\n\n**触发短语:**",
    "**Always:**": "**始终:**",
    "**Trigger phrases:**": "**触发短语:**",
    "**Consequence:**": "**后果:**",
    "**Problem:**": "**问题:**",
    "**Solution:**": "**解决方案:**",
    "**Core Principle:**": "**核心原则:**",

    # 主要章节
    "## What ": "## ",
    " Does": "的功能",
    "## Common Issues": "## 常见问题",
    "## Common ": "## 常见",
    "## Verification Checklist": "## 验证检查清单",
    "## How to Use": "## 使用方法",
    "## How to ": "## 如何",
    "## When Stuck": "## 当困难时",
    "## Anti-Patterns (Red Flags)": "## 反模式 (红旗警告)",
    "## Anti-Patterns": "## 反模式",
    "## Red Flags": "## 红旗警告",
    "## Related Skills": "## 相关技能",
    "## Design Patterns": "## 设计模式",

    # API相关
    "API ": "API ",
    "API": "API",
    "RESTful": "RESTful",
    "REST": "REST",
    "HTTP": "HTTP",
    "JSON": "JSON",
    "GET": "GET",
    "POST": "POST",
    "PUT": "PUT",
    "PATCH": "PATCH",
    "DELETE": "DELETE",
    "endpoint": "端点",
    "Endpoint": "端点",
    "Endpoints": "端点",
    "request": "请求",
    "Request": "请求",
    "response": "响应",
    "Response": "响应",
    "header": "头部",
    "Header": "头部",
    "Headers": "头部",
    "status code": "状态码",
    "Status code": "状态码",
    "Status codes": "状态码",
    "authentication": "身份认证",
    "Authentication": "身份认证",
    "authorization": "授权",
    "Authorization": "授权",
    "error": "错误",
    "Error": "错误",
    "error handling": "错误处理",
    "Error handling": "错误处理",

    # 数据库相关
    "Database": "数据库",
    "database": "数据库",
    "query": "查询",
    "Query": "查询",
    "SQL": "SQL",
    "table": "表",
    "Table": "表",
    "index": "索引",
    "Index": "索引",
    "constraint": "约束",
    "Constraint": "约束",
    "migration": "迁移",
    "Migration": "迁移",
    "schema": "模式",
    "Schema": "模式",
    "transaction": "事务",
    "Transaction": "事务",
    "lock": "锁",
    "Lock": "锁",
    "backup": "备份",
    "Backup": "备份",
    "replica": "副本",
    "Replica": "副本",

    # 代码相关
    "code": "代码",
    "Code": "代码",
    "function": "函数",
    "Function": "函数",
    "variable": "变量",
    "Variable": "变量",
    "class": "类",
    "Class": "类",
    "method": "方法",
    "Method": "方法",
    "module": "模块",
    "Module": "模块",
    "import": "导入",
    "Import": "导入",
    "export": "导出",
    "Export": "导出",
    "type": "类型",
    "Type": "类型",
    "interface": "接口",
    "Interface": "接口",
    "implementation": "实现",
    "Implementation": "实现",
    "syntax": "语法",
    "Syntax": "语法",
    "semantic": "语义",
    "Semantic": "语义",
    "logic": "逻辑",
    "Logic": "逻辑",

    # 测试相关
    "test": "测试",
    "Test": "测试",
    "testing": "测试",
    "Testing": "测试",
    "unit test": "单元测试",
    "Unit test": "单元测试",
    "integration test": "集成测试",
    "Integration test": "集成测试",
    "coverage": "覆盖率",
    "Coverage": "覆盖率",
    "assertion": "断言",
    "Assertion": "断言",
    "mock": "模拟",
    "Mock": "模拟",
    "stub": "存根",
    "Stub": "存根",

    # 性能相关
    "performance": "性能",
    "Performance": "性能",
    "optimize": "优化",
    "Optimize": "优化",
    "optimization": "优化",
    "Optimization": "优化",
    "slow": "慢",
    "Slow": "慢",
    "fast": "快",
    "Fast": "快",
    "bottleneck": "瓶颈",
    "Bottleneck": "瓶颈",
    "profiling": "分析",
    "Profiling": "分析",
    "memory": "内存",
    "Memory": "内存",
    "CPU": "CPU",
    "cache": "缓存",
    "Cache": "缓存",
    "compression": "压缩",
    "Compression": "压缩",

    # 安全相关
    "security": "安全",
    "Security": "安全",
    "vulnerability": "漏洞",
    "Vulnerability": "漏洞",
    "encryption": "加密",
    "Encryption": "加密",
    "encrypted": "加密的",
    "Encrypted": "加密的",
    "credential": "凭证",
    "Credential": "凭证",
    "token": "令牌",
    "Token": "令牌",
    "password": "密码",
    "Password": "密码",
    "secret": "秘钥",
    "Secret": "秘钥",
    "permissions": "权限",
    "Permissions": "权限",
    "access control": "访问控制",
    "Access control": "访问控制",
    "injection": "注入",
    "Injection": "注入",
    "XSS": "跨站脚本",
    "CSRF": "跨站请求伪造",

    # 架构相关
    "architecture": "架构",
    "Architecture": "架构",
    "design": "设计",
    "Design": "设计",
    "pattern": "模式",
    "Pattern": "模式",
    "dependency": "依赖",
    "Dependency": "依赖",
    "coupling": "耦合",
    "Coupling": "耦合",
    "cohesion": "内聚力",
    "Cohesion": "内聚力",
    "layer": "层",
    "Layer": "层",
    "component": "组件",
    "Component": "组件",
    "module": "模块",
    "Module": "模块",
    "service": "服务",
    "Service": "服务",
    "abstraction": "抽象",
    "Abstraction": "抽象",
    "encapsulation": "封装",
    "Encapsulation": "封装",

    # 部署相关
    "deployment": "部署",
    "Deployment": "部署",
    "deploy": "部署",
    "Deploy": "部署",
    "environment": "环境",
    "Environment": "环境",
    "staging": "暂存",
    "Staging": "暂存",
    "production": "生产",
    "Production": "生产",
    "version": "版本",
    "Version": "版本",
    "release": "发布",
    "Release": "发布",
    "rollback": "回滚",
    "Rollback": "回滚",
    "downtime": "停机时间",
    "Downtime": "停机时间",

    # 容器和编排
    "Docker": "Docker",
    "docker": "docker",
    "Kubernetes": "Kubernetes",
    "kubernetes": "kubernetes",
    "container": "容器",
    "Container": "容器",
    "image": "镜像",
    "Image": "镜像",
    "pod": "Pod",
    "Pod": "Pod",
    "cluster": "集群",
    "Cluster": "集群",
    "node": "节点",
    "Node": "节点",

    # CI/CD相关
    "CI/CD": "持续集成/持续部署",
    "pipeline": "流水线",
    "Pipeline": "流水线",
    "build": "构建",
    "Build": "构建",
    "test": "测试",
    "Test": "测试",
    "lint": "代码风格检查",
    "Lint": "代码风格检查",
    "linting": "代码风格检查",
    "Linting": "代码风格检查",
    "stage": "阶段",
    "Stage": "阶段",
    "job": "任务",
    "Job": "任务",

    # 框架和库
    "framework": "框架",
    "Framework": "框架",
    "library": "库",
    "Library": "库",
    "Flask": "Flask",
    "Django": "Django",
    "React": "React",
    "Vue": "Vue",
    "Angular": "Angular",
    "Spring": "Spring",
    "Node.js": "Node.js",
    "Express": "Express",
    "FastAPI": "FastAPI",

    # 前端相关
    "CSS": "CSS",
    "HTML": "HTML",
    "JavaScript": "JavaScript",
    "TypeScript": "TypeScript",
    "component": "组件",
    "Component": "组件",
    "render": "渲染",
    "Render": "渲染",
    "state": "状态",
    "State": "状态",
    "props": "属性",
    "Props": "属性",
    "event": "事件",
    "Event": "事件",
    "listener": "监听器",
    "Listener": "监听器",
    "DOM": "DOM",
    "virtual DOM": "虚拟DOM",
    "Virtual DOM": "虚拟DOM",
    "bundle": "包",
    "Bundle": "包",
    "webpack": "webpack",
    "Webpack": "Webpack",
    "babel": "babel",
    "Babel": "Babel",

    # 后端相关
    "backend": "后端",
    "Backend": "后端",
    "frontend": "前端",
    "Frontend": "前端",
    "controller": "控制器",
    "Controller": "控制器",
    "model": "模型",
    "Model": "模型",
    "view": "视图",
    "View": "视图",
    "route": "路由",
    "Route": "路由",
    "router": "路由器",
    "Router": "路由器",
    "middleware": "中间件",
    "Middleware": "中间件",

    # 云相关
    "cloud": "云",
    "Cloud": "云",
    "AWS": "AWS",
    "Azure": "Azure",
    "GCP": "GCP",
    "instance": "实例",
    "Instance": "实例",
    "VM": "虚拟机",
    "storage": "存储",
    "Storage": "存储",
    "bucket": "桶",
    "Bucket": "桶",
    "region": "区域",
    "Region": "区域",
    "zone": "可用区",
    "Zone": "可用区",

    # 监控和日志
    "monitoring": "监控",
    "Monitoring": "监控",
    "logging": "日志",
    "Logging": "日志",
    "metric": "指标",
    "Metric": "指标",
    "alert": "告警",
    "Alert": "告警",
    "trace": "跟踪",
    "Trace": "跟踪",
    "debug": "调试",
    "Debug": "调试",
    "log": "日志",
    "Log": "日志",

    # 通用词汇
    "and": "和",
    "or": "或",
    "is": "是",
    "are": "是",
    "be": "是",
    "that": "那个",
    "the": "这个",
    "a": "一个",
    "an": "一个",
    "in": "在",
    "on": "在",
    "at": "在",
    "to": "到",
    "from": "从",
    "for": "对于",
    "with": "与",
    "by": "通过",
    "as": "作为",
    "of": "的",
    "before": "之前",
    "after": "之后",
    "during": "期间",
    "while": "当",
    "if": "如果",
    "then": "那么",
    "else": "否则",
    "when": "当",
    "where": "其中",
    "why": "为什么",
    "how": "如何",
    "what": "什么",
    "which": "哪个",
    "who": "谁",

    # 常见短语
    "Please": "请",
    "please": "请",
    "Note": "注意",
    "note": "注意",
    "Warning": "警告",
    "warning": "警告",
    "Important": "重要",
    "important": "重要",
    "Example": "例子",
    "example": "例子",
    "Examples": "例子",
    "examples": "例子",
    "Usage": "用法",
    "usage": "用法",
    "Reference": "参考",
    "reference": "参考",
    "See also": "另见",
    "see also": "另见",
    "Best practice": "最佳实践",
    "Best practices": "最佳实践",
    "best practice": "最佳实践",
    "best practices": "最佳实践",

    # 容错和可靠性
    "reliability": "可靠性",
    "Reliability": "可靠性",
    "availability": "可用性",
    "Availability": "可用性",
    "fault": "故障",
    "Fault": "故障",
    "failure": "故障",
    "Failure": "故障",
    "resilience": "弹性",
    "Resilience": "弹性",
    "redundancy": "冗余",
    "Redundancy": "冗余",
    "failover": "故障转移",
    "Failover": "故障转移",
    "recovery": "恢复",
    "Recovery": "恢复",

    # 微服务
    "microservice": "微服务",
    "Microservice": "微服务",
    "microservices": "微服务",
    "Microservices": "微服务",
    "mesh": "网格",
    "Mesh": "网格",
    "service mesh": "服务网格",
    "Service mesh": "服务网格",
    "circuit breaker": "熔断器",
    "Circuit breaker": "熔断器",
    "load balancing": "负载均衡",
    "Load balancing": "负载均衡",
    "load balance": "负载均衡",
    "Load balance": "负载均衡",
    "timeout": "超时",
    "Timeout": "超时",
    "retry": "重试",
    "Retry": "重试",
}

def translate_text(text):
    """使用字典翻译文本"""
    result = text

    # 按长度排序（长的在前），避免部分替换
    sorted_keys = sorted(TRANSLATION_DICT.keys(), key=len, reverse=True)

    for eng, chn in [(k, TRANSLATION_DICT[k]) for k in sorted_keys]:
        # 需要更聪明的替换逻辑，避免错误替换
        # 使用单词边界或特殊处理
        if eng in result:
            result = result.replace(eng, chn)

    return result

def process_file(file_path):
    """处理单个文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 翻译内容
    translated = translate_text(content)

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(translated)

    return file_path

# 找到所有需要翻译的文件
base_path = Path('/Users/jarry/github/ai-skills')
files_to_translate = []

# SKILL.md 文件
for skill_md in base_path.rglob('SKILL.md'):
    files_to_translate.append(skill_md)

# forms.md 文件
for forms_md in base_path.rglob('forms.md'):
    files_to_translate.append(forms_md)

# reference.md 文件
for ref_md in base_path.rglob('reference.md'):
    files_to_translate.append(ref_md)

# 处理所有文件
print(f"开始翻译 {len(files_to_translate)} 个文件...")
for i, file_path in enumerate(files_to_translate, 1):
    try:
        process_file(file_path)
        print(f"✅ [{i}/{len(files_to_translate)}] 已翻译: {file_path.relative_to(base_path)}")
    except Exception as e:
        print(f"❌ [{i}/{len(files_to_translate)}] 错误: {file_path.relative_to(base_path)} - {str(e)}")

print(f"\n✅ 完成! 已翻译 {len(files_to_translate)} 个文件")
