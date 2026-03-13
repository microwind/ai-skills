# 中文AI Skills编程知识库 - 结构规划

## 主要分类（一级目录）

```
ai-skills/
├── backend/              # 后端开发
├── frontend/             # 前端开发
├── frameworks/           # 框架与库
├── cloud-native/         # 云原生
├── microservices/        # 微服务
├── system-design/        # 系统设计
├── languages/            # 编程语言
├── code-quality/         # 代码质量与优化
├── devops/               # DevOps与部署
├── database/             # 数据库
└── tools/                # 工具与脚本
```

## 每个Skill的标准结构

```
skill-name/
├── SKILL.md              # 必需：主技能文件
├── 中文描述.md            # 中文说明文档
├── scripts/              # 可选：可执行代码
│   ├── main.py
│   ├── run.sh
│   └── example.js
├── references/           # 可选：参考文档
│   ├── tutorial.md
│   ├── api-doc.md
│   └── examples/
├── assets/               # 可选：模板、图表等
│   ├── template.md
│   ├── checklist.md
│   └── diagram.png
└── README.md             # 技能概览
```

## SKILL.md标准格式

```markdown
# [技能名称]

## 目的（Purpose）
简明说明此技能的用途

## 使用场景（Use Cases）
- 场景1
- 场景2

## 前置条件（Prerequisites）
- 要求1
- 要求2

## 核心步骤（Core Steps）
1. 步骤1
2. 步骤2
3. 步骤3

## 关键代码示例（Code Examples）
\`\`\`python
# 示例代码
\`\`\`

## 常见问题（FAQ）
Q: 问题？
A: 答案

## 相关资源（Resources）
- [资源名](链接)
```

## 初期规划（100+ Skills）

### 后端开发 (20+ Skills)
- RESTful API设计与实现
- GraphQL服务开发
- 数据验证与序列化
- 认证与授权（JWT、OAuth）
- 错误处理与日志
- 缓存策略
- 队列与异步任务
- 文件上传处理
- 数据库连接池
- ORM框架使用

### 前端开发 (20+ Skills)
- React组件最佳实践
- Vue.js生态
- 状态管理（Redux、Vuex）
- 前端性能优化
- 响应式设计
- 表单处理与验证
- 动画与交互
- 跨浏览器兼容性
- 构建工具配置
- 前端测试

### 框架与库 (15+ Skills)
- Django开发
- Flask轻量级应用
- FastAPI高性能API
- Spring Boot应用
- Express.js服务
- NestJS架构
- Ruby on Rails
- 等等

### 云原生 (15+ Skills)
- Docker容器化
- Kubernetes编排
- 无服务器函数
- 容器注册表管理
- 网络策略配置
- 等等

### 微服务 (10+ Skills)
- 服务间通信
- 服务治理
- 分布式追踪
- 熔断器模式
- 等等

### 系统设计 (7+ Skills)
- 算法顾问 - 复杂系统算法选择与优化
- 架构分析器 - 系统架构分析与改进
- 高并发系统设计
- 分布式一致性
- CAP定理应用
- 数据库分片策略
- 缓存失效策略

### 其他
- 多编程语言skills
- 代码优化techniques
- 重构patterns
- 等等
```

保存此结构规划文件。现在我开始创建实际的Skills目录和内容。
