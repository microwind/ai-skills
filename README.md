# ai-skills
构建高质量的AI编程Skills库，利用AI来学习编程技术，让AI更好地替你打工。用好AI事半功倍，不用AI落后时代。
=======
# 中文AI Skills编程知识库

> 🚀 一个为中文开发者打造的全面AI编程Skills库 - 帮助程序员学习和直接使用各类编程技能

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![中文文档](https://img.shields.io/badge/documentation-中文-brightgreen.svg)](#)
![Skills](https://img.shields.io/badge/skills-50+-brightblue.svg)

## 简介

这是一个结构化的编程知识库，包含**100多个**精选的AI-powered Skills，涵盖：

- ✅ **后端开发** - RESTful API、数据库、认证授权
- ✅ **前端开发** - React、Vue、性能优化
- ✅ **框架生态** - Flask、Django、FastAPI、Spring Boot、Express、NestJS、Gin、Fiber等
- ✅ **云原生** - Docker、Kubernetes、微服务
- ✅ **系统设计** - 高并发、分布式、缓存策略
- ✅ **DevOps** - CI/CD、监控、日志
- ✅ **代码质量** - 测试、重构、优化
- ✅ **编程语言** - Java、Python、TypeScript、JavaScript、Go、Rust、C、C++

## 快速开始

### 浏览Skills

所有Skills按分类组织：

```
ai-skills/
├── backend/              # 后端开发 (10+ skills)
├── frontend/             # 前端开发 (10+ skills)
├── frameworks/           # 框架与库 (6+ skills)
├── cloud-native/         # 云原生 (5+ skills)
├── microservices/        # 微服务 (5+ skills)
├── system-design/        # 系统设计 (7+ skills)
├── database/             # 数据库 (4+ skills)
├── devops/               # DevOps (4+ skills)
├── code-quality/         # 代码质量 (4+ skills)
├── languages/            # 编程语言 (4+ skills)
└── tools/                # 工具与脚本 (3+ skills)
```

### 查看一个Skill

每个Skill都有标准的目录结构：

```
├── README.md               # 一级目录说明
skill-name/
├── SKILL.md                # 标准SKILL文档
├── scripts/                # 示例代码和脚本
├── references/             # 参考文档
└── assets/                 # 模板和资源
```

### 使用示例

**例1：学习RESTful API设计**
```bash
cd backend/restful-api-design/
# 阅读中文说明
cat 中文说明.md
# 查看示例代码
ls scripts/
```

**例2：学习Docker容器化**
```bash
cd cloud-native/docker-containerization/
# 阅读详细说明
cat 中文说明.md
# 查看Dockerfile示例
ls scripts/
```

## 主要Skills列表

### 后端开发
- [RESTful API设计与实现](./backend/restful-api-design/) - 设计高质量的Web API
- [JWT认证实现](./backend/jwt-authentication/) - 安全的令牌认证
- [错误处理与日志系统](./backend/error-handling-logging/) - 日志和错误管理
- [缓存策略与实现](./backend/caching-strategies/) - 多层缓存设计
- [异步任务与消息队列](./backend/async-tasks/) - Celery、Bull等
- [数据验证与序列化](./backend/data-validation/) - 输入验证和数据处理
- [GraphQL API开发](./backend/graphql-api/) - 现代API设计
- [文件上传处理](./backend/file-upload/) - 安全的文件处理

### 前端开发
- [React组件最佳实践](./frontend/react-components/) - 组件设计和性能
- [状态管理](./frontend/state-management/) - Redux、Context等
- [前端性能优化](./frontend/performance-optimization/) - 渲染优化、代码分割
- [响应式设计](./frontend/responsive-design/) - 移动端适配
- [表单处理与验证](./frontend/form-handling/) - 表单库和验证
- [前端测试](./frontend/testing-frontend/) - Jest、Vitest等

### 框架与库
- [Django Web框架](./frameworks/django-development/) - Python Web开发
- [FastAPI高性能API](./frameworks/fastapi-setup/) - 现代Python API
- [Spring Boot应用开发](./frameworks/spring-boot/) - Java企业应用
- [Express.js服务](./frameworks/express-js/) - Node.js Web框架
- [NestJS企业架构](./frameworks/nestjs-architecture/) - Node.js企业框架
- [Flask轻量级应用](./frameworks/flask-microframework/) - 微框架快速开发

### 云原生与容器
- [Docker容器化](./cloud-native/docker-containerization/) - 容器基础
- [Kubernetes编排](./cloud-native/kubernetes-basics/) - 容器编排
- [无服务器函数](./cloud-native/serverless-functions/) - FaaS架构
- [容器镜像管理](./cloud-native/container-registry/) - 镜像仓库
- [网络策略配置](./cloud-native/networking-policies/) - 容器网络

### 系统设计
- [算法顾问](./system-design/algorithm-advisor/) - 复杂系统算法选择与优化
- [架构分析器](./system-design/architecture-analyzer/) - 系统架构分析与改进
- [高并发系统设计](./system-design/high-concurrency/) - 支持高并发
- [分布式一致性](./system-design/distributed-consistency/) - 分布式事务
- [CAP定理应用](./system-design/cap-theorem/) - 系统权衡
- [数据库分片策略](./system-design/database-sharding/) - 水平扩展
- [缓存失效策略](./system-design/cache-invalidation/) - 缓存管理

### 数据库
- [SQL优化与索引](./database/sql-optimization/) - 查询优化
- [事务管理](./database/transaction-management/) - ACID和隔离级别
- [NoSQL数据库应用](./database/nosql-databases/) - MongoDB、Redis等
- [备份与恢复](./database/backup-recovery/) - 数据可靠性

### 更多...
- DevOps: CI/CD流水线、基础设施即代码、监控与告警、日志聚合
- 代码质量: 代码审查、重构模式、测试策略、代码优化
- 编程语言: Python高级特性、JavaScript ES6+、Go模式、Rust系统编程

## Skill文件说明

### SKILL.md
每个Skill的主要文档，包含：
- 目的和使用场景
- 核心概念讲解
- 实战代码示例
- 性能优化建议
- 常见问题解答
- 相关资源链接

### 示例代码（scripts/）
- Python、JavaScript、Go、Java等多语言示例
- 可直接运行的代码片段
- 最佳实践参考

## 如何使用本库

### 1. 找到您需要的Skill
按分类浏览，或使用搜索找到相关技能。

### 2. 阅读中文说明
从`SKILL.md`开始了解核心内容。

### 3. 查看示例代码
在`scripts/`目录中查看实战示例。

### 4. 参考官方文档
使用`references/`中的链接深入学习。

### 5. 动手实践
复制代码示例，在自己的项目中应用。

## 库结构统计

```
总Skills数: 50+
├── 后端: 10+
├── 前端: 10+
├── 框架: 6+
├── 云原生: 5+
├── 微服务: 5+
├── 系统设计: 7+
├── 数据库: 4+
├── DevOps: 4+
├── 代码质量: 4+
├── 语言: 4+
└── 工具: 3+

代码示例: 100+
参考链接: 200+
```

### Skill模板
```markdown
# [技能名称]

## 目的
简明说明用途

## 核心概念
- 概念1
- 概念2

## 实现步骤
1. 步骤1
2. 步骤2

## 代码示例
\`\`\`python
# 示例代码
\`\`\`

## 最佳实践
- 实践1
- 实践2

## 常见问题
**Q:** 问题
**A:** 答案
```

## 快速导航

- [完整Skills索引](./SKILLS_INDEX.md)
- [按难度分类](./SKILLS_BY_DIFFICULTY.md)
- [按学习路径](./SKILLS_ROADMAP.md)
- [常见问题FAQ](./FAQ.md)

---

## 相关链接：AI时代程序员成长体系
- [《AI时代，人人都是Agent工程师》](https://github.com/microwind/algorithms/blob/main/start-here/AI-Era-Programmers-as-Agent-Engineers.md)
- ai-prompt - AI编程提示词库：[https://github.com/microwind/ai-prompt](https://github.com/microwind/ai-prompt)
- ai-skills - AI编程Skill库：[https://github.com/microwind/ai-skills](https://github.com/microwind/ai-skills)
- algorithms - 算法思想与数据结构：[https://github.com/microwind/algorithms](https://github.com/microwind/algorithms)
- design-patterns - 设计模式与编程范式：[https://github.com/microwind/design-patterns](https://github.com/microwind/design-patterns)

## 致谢

感谢以下开源项目的启发：
- [Anthropic Skills](https://github.com/anthropics/skills)
- [Awesome OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills)
- [OpenClaw Skills](https://github.com/openclaw/skills)

## 联系与反馈

**我是Jarry 李春平** **祝您学习愉快！**
- mail: lichunping@buaa.edu.cn
- weixin: springbuild
- 🌟 感谢您给本项目点个Star

