# Claude Code 实战指南

> 真实场景，真实对话，真实开发流程

## 目录

- [完整项目实战](#完整项目实战)
  - [场景1：电商系统从0到1](#场景1电商系统从0到1)
  - [场景2：SaaS平台迭代开发](#场景2saas平台迭代开发)
  - [场景3：移动App跨平台开发](#场景3移动app跨平台开发)
- [Vibe Coding实战](#vibe-coding实战)
- [Spec Coding指南](#spec-coding指南)
- [Skills应用场景](#skills应用场景)
- [团队协作模式](#团队协作模式)
- [高级调试技巧](#高级调试技巧)
- [实战场景库](#实战场景库)
- [高效工作流](#高效工作流)
- [实用技巧](#实用技巧)

---

## 完整项目实战

### 场景1：电商系统从0到1

**背景**：2周内上线电商MVP（商品、购物车、订单、支付），1个全栈工程师用Claude Code加速。

**关键提示词**：
```
我要做一个电商MVP，时间很紧，只有2周。核心功能：商品列表、购物车、订单、支付。技术栈我还没定，你给个建议，要快，要稳，要能快速迭代。
```

**Claude响应**：推荐Next.js 14 + TypeScript + shadcn/ui（前端），Node.js + Express + MongoDB（后端），Stripe（支付），Vercel + Railway（部署）

**系统架构图**：
```mermaid
graph TB
    subgraph "前端层"
        A[Next.js 14 + TypeScript]
        B[Tailwind CSS + shadcn/ui]
    end
    subgraph "后端层"
        C[Node.js + Express]
        D[MongoDB]
    end
    subgraph "第三方服务"
        E[Stripe支付]
        F[Vercel部署]
    end
    A --> C
    C --> D
    C --> E
    A --> F
```

**关键步骤**：
- Day 1：技术选型 + 项目初始化
- Day 2-3：商品列表 + 购物车 + 订单
- Day 4：支付集成（Stripe）
- Day 7：测试优化（自动扫描代码发现问题）
- Day 14：部署上线

**技巧**：描述需求时明确时间约束和核心功能，Claude会给出最优技术栈和实施计划。

---

### 场景2：SaaS平台迭代开发

**背景**：已上线SaaS平台添加团队协作模块，3天内完成核心功能（团队管理、项目管理、实时评论）。

**关键提示词**：
```
产品经理给了需求文档，核心点：团队创建管理、项目管理、实时协作（评论@提醒）、数据权限。技术约束：兼容现有系统（React 18 + Node.js）、支持100+并发、数据安全要求高。你觉得这个需求怎么样？有没有风险点？
```

**Claude响应**：推荐Supabase Realtime（托管服务省运维）、RBAC权限系统、数据库租户隔离（team_id）、Redis缓存提升性能

**数据库ER图**：
```mermaid
erDiagram
    users ||--o{ team_members : "belongs to"
    teams ||--o{ team_members : "has"
    teams ||--o{ projects : "owns"
    projects ||--o{ comments : "has"
    users ||--o{ comments : "writes"
```

**关键步骤**：
- Day 1：数据库schema + RBAC权限系统 + Supabase Realtime集成
- Day 2：团队CRUD API + 权限校验中间件 + 前端页面
- Day 3：实时评论 + @提醒 + 测试（发现删除同步问题并修复）

**技巧**：迭代开发时先识别风险点（实时协作技术选型、权限系统设计），Claude会给出最优方案和实施计划。

---

### 场景3：移动App跨平台开发

**背景**：电商公司开发iOS/Android双平台App，预算有限时间紧，用React Native + Expo快速开发。

**关键提示词**：
```
我们要开发电商App，iOS和Android都要。预算有限，时间紧。你给个技术方案。
```

**Claude响应**：推荐React Native + Expo（一套代码双平台节省50%时间）、Expo SDK 50 + TypeScript + React Navigation + React Query、Expo提供现成组件（相机/推送/支付）支持热更新

**移动App架构图**：
```mermaid
graph TB
    subgraph "UI层"
        A[React Native]
        B[Expo SDK]
        C[React Navigation]
    end
    subgraph "状态管理"
        D[React Query]
        E[AsyncStorage]
    end
    subgraph "业务逻辑"
        F[API Services]
        G[Offline Sync]
    end
    subgraph "原生功能"
        H[Stripe支付]
        I[相机/相册]
    end
    A --> C
    A --> D
    D --> F
    D --> E
    E --> G
    F --> H
    A --> I
    B --> A
```

**关键步骤**：
- Day 1：项目初始化 + 导航配置（Stack + Bottom Tab）
- Day 2：首页商品列表（FlatList + React Query）
- Day 3：Stripe支付集成 + 离线同步（AsyncStorage）

**技巧**：跨平台开发时明确双平台需求和时间预算，Claude会推荐合适的跨平台框架和开发策略。

---

## Vibe Coding实战

Vibe Coding是一种边聊边写的开发方式，像结对编程一样自然流畅。

#### Vibe Coding工作流程

```mermaid
sequenceDiagram
    participant 我 as 开发者
    participant Claude as Claude Code
    participant Code as 代码库

    我->>Claude: 描述问题/需求
    Claude->>Claude: 分析代码
    Claude->>我: 提出问题和建议
    我->>Claude: 确认方向
    Claude->>Code: 生成/修改代码
    Code-->>Claude: 代码状态
    Claude->>我: 展示结果
    我->>Claude: 反馈和调整
    Claude->>Code: 迭代优化
    loop 持续对话
        我->>Claude: 新的想法/问题
        Claude->>我: 实时响应
    end
```

### 实战案例：重构遗留代码

**背景**：接手一个遗留项目，代码质量差，需要重构。

#### 对话开始

```
我：这个项目代码太乱了，我给你看一下。

Claude：好的，我看看。

（Claude读取代码）

我看到了几个问题：
1. 一个文件2000行，职责不清晰
2. 大量重复代码
3. 没有类型定义，全是any
4. 错误处理缺失
5. 测试覆盖率0%

你想从哪里开始重构？
```

```
我：先从最大的文件开始，src/services/UserService.ts，2000行。

Claude：我先分析这个文件的职责。

（Claude分析文件）

这个文件混入了太多职责：
- 用户CRUD
- 认证逻辑
- 权限校验
- 邮件发送
- 日志记录
- 数据验证

建议拆分成：
- UserService（用户CRUD）
- AuthService（认证）
- PermissionService（权限）
- NotificationService（通知）
- ValidationService（验证）

我先拆分？
```

```
我：好，先拆分UserService和AuthService。

Claude：好的，我先提取认证相关的代码到AuthService。
```

**Claude执行重构**：
```typescript
// 提取前：UserService.ts（2000行）
export class UserService {
  async createUser(data: any) {
    // 验证
    if (!data.email) throw new Error('邮箱必填');
    if (!data.password) throw new Error('密码必填');
    
    // 密码加密
    const hashedPassword = await bcrypt.hash(data.password, 10);
    
    // 创建用户
    const user = await db.users.create({
      email: data.email,
      password: hashedPassword
    });
    
    // 发送欢迎邮件
    await sendEmail(user.email, '欢迎注册');
    
    return user;
  }
  
  async login(email: string, password: string) {
    const user = await db.users.findOne({ email });
    if (!user) throw new Error('用户不存在');
    
    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) throw new Error('密码错误');
    
    const token = jwt.sign({ userId: user.id }, SECRET);
    return { token, user };
  }
}

// 提取后：AuthService.ts（专注认证）
export class AuthService {
  async register(data: RegisterDto) {
    const hashedPassword = await bcrypt.hash(data.password, 10);
    const user = await db.users.create({
      email: data.email,
      password: hashedPassword
    });
    await notificationService.sendWelcomeEmail(user.email);
    return user;
  }
  
  async login(credentials: LoginDto) {
    const user = await this.validateUser(credentials.email, credentials.password);
    const token = this.generateToken(user);
    return { token, user };
  }
  
  private async validateUser(email: string, password: string) {
    const user = await db.users.findOne({ email });
    if (!user) throw new UnauthorizedError('用户不存在');
    
    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) throw new UnauthorizedError('密码错误');
    
    return user;
  }
  
  private generateToken(user: User): string {
    return jwt.sign({ userId: user.id }, SECRET, { expiresIn: '7d' });
  }
}

// 提取后：UserService.ts（专注用户CRUD）
export class UserService {
  async create(data: CreateUserDto) {
    return await db.users.create(data);
  }
  
  async findById(id: string) {
    return await db.users.findById(id);
  }
  
  async update(id: string, data: UpdateUserDto) {
    return await db.users.findByIdAndUpdate(id, data);
  }
}
```

```
我：拆分后清晰多了。现在处理重复代码。

Claude：我扫描了一下，发现重复代码主要在：
1. 错误处理（try-catch重复）
2. 数据验证（验证逻辑重复）
3. 日志记录（日志格式重复）

我先提取错误处理的通用逻辑？
```

**Claude提取通用逻辑**：
```typescript
// 提取通用错误处理
export async function withErrorHandler<T>(
  fn: () => Promise<T>,
  errorMessage?: string
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    logger.error('Operation failed', { error, errorMessage });
    throw new AppError(errorMessage || '操作失败', error);
  }
}

// 使用
export class UserService {
  async findById(id: string) {
    return withErrorHandler(
      () => db.users.findById(id),
      '查询用户失败'
    );
  }
}

// 提取通用验证
export class Validator {
  static email(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
  
  static password(password: string): boolean {
    return password.length >= 8;
  }
  
  static required(value: any): boolean {
    return value !== null && value !== undefined && value !== '';
  }
}

// 使用
export class AuthService {
  async register(data: RegisterDto) {
    if (!Validator.email(data.email)) {
      throw new ValidationError('邮箱格式不正确');
    }
    if (!Validator.password(data.password)) {
      throw new ValidationError('密码至少8位');
    }
    // ...
  }
}
```

```
我：代码质量提升很多了。现在加类型定义。

Claude：好的，我先定义核心类型，然后逐步替换any。
```

**Claude添加类型定义**：
```typescript
// src/types/user.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateUserDto {
  email: string;
  password: string;
  name: string;
}

export interface UpdateUserDto {
  name?: string;
  role?: 'admin' | 'user';
}

export interface LoginDto {
  email: string;
  password: string;
}

export interface RegisterDto {
  email: string;
  password: string;
  name: string;
}
```

```
我：类型定义好了。现在加测试。

Claude：好的，我先为核心功能写单元测试。
```

**Claude生成测试**：
```typescript
// src/services/__tests__/AuthService.test.ts
import { AuthService } from '../AuthService';
import { describe, it, expect, beforeEach, jest } from '@jest/globals';

describe('AuthService', () => {
  let authService: AuthService;
  
  beforeEach(() => {
    authService = new AuthService();
  });
  
  describe('login', () => {
    it('应该返回token和用户信息', async () => {
      const result = await authService.login({
        email: 'test@example.com',
        password: 'password123'
      });
      
      expect(result).toHaveProperty('token');
      expect(result).toHaveProperty('user');
      expect(result.user.email).toBe('test@example.com');
    });
    
    it('应该拒绝错误的密码', async () => {
      await expect(
        authService.login({
          email: 'test@example.com',
          password: 'wrongpassword'
        })
      ).rejects.toThrow('密码错误');
    });
  });
  
  describe('register', () => {
    it('应该创建新用户', async () => {
      const user = await authService.register({
        email: 'new@example.com',
        password: 'password123',
        name: 'Test User'
      });
      
      expect(user.email).toBe('new@example.com');
      expect(user.name).toBe('Test User');
    });
  });
});
```

```
我：重构完成了，代码质量提升很大。总结一下成果？

Claude：重构成果：

**代码质量**：
- 文件行数：2000行 → 5个文件，每个<300行
- 重复代码：减少60%
- 类型覆盖率：0% → 95%
- 测试覆盖率：0% → 80%

**可维护性**：
- 职责清晰，单一职责原则
- 错误处理统一
- 验证逻辑复用
- 类型安全

**性能**：
- 没有明显性能提升（主要是代码质量）

接下来可以：
1. 继续重构其他模块
2. 添加集成测试
3. 性能优化
4. 文档完善

要继续吗？
```

---

## Spec Coding指南

Spec Coding是从需求规格到代码实现的完整流程，强调先明确需求再写代码。

#### Spec Coding完整流程

```mermaid
flowchart TD
    A[PRD需求文档] --> B[需求理解与澄清]
    B --> C{需求明确?}
    C -->|否| B
    C -->|是| D[技术方案设计]
    D --> E[数据库schema设计]
    E --> F[API接口设计]
    F --> G[数据库迁移实现]
    G --> H[API控制器实现]
    H --> I[前端组件实现]
    I --> J[功能测试]
    J --> K{测试通过?}
    K -->|否| L[修复问题]
    L --> J
    K -->|是| M[部署文档生成]
    M --> N[部署上线]
    
    style A fill:#e1f5ff
    style N fill:#c8e6c9
    style K fill:#fff9c4
```

### 实战案例：从PRD到可运行代码

**背景**：产品经理给了一个PRD（产品需求文档），需要实现一个用户反馈系统。

#### 第一步：理解需求

```
我：产品经理给了PRD，我给你念一下核心需求：

用户反馈系统需求：
1. 用户可以提交反馈（文本、截图、日志）
2. 反馈分类（Bug、功能建议、其他）
3. 优先级标记（低、中、高、紧急）
4. 管理员可以查看和处理反馈
5. 反馈状态流转（待处理→处理中→已解决→已关闭）
6. 用户可以查看自己反馈的处理进度

非功能需求：
- 反馈提交后3秒内响应
- 支持离线提交，联网后自动同步
- 数据安全，用户反馈加密存储
- 支持批量导出反馈

你先分析一下这个需求，看看有没有不清楚的地方？
```

```
Claude：我分析了一下，有几个问题需要确认：

1. **用户身份**
   - 是否需要登录才能提交反馈？
   - 匿名用户是否可以提交？

2. **反馈附件**
   - 截图大小限制？
   - 日志文件大小限制？
   - 支持哪些格式？

3. **管理员权限**
   - 谁是管理员？需要权限系统吗？
   - 管理员可以修改反馈内容吗？

4. **通知机制**
   - 反馈状态变更需要通知用户吗？
   - 用什么方式通知（邮件、站内信、推送）？

5. **数据保留**
   - 反馈保留多久？
   - 已关闭的反馈是否可以删除？

这些问题明确后，我可以给出更精确的技术方案。
```

```
我：好的，我回答一下：

1. 需要登录才能提交，不支持匿名
2. 截图限制5MB，日志限制10MB，支持jpg/png/txt/log
3. 管理员是后台配置的用户ID，有专门的管理后台，管理员可以修改反馈内容
4. 需要通知，用站内信+邮件
5. 反馈保留1年，已关闭的反馈30天后自动删除

现在清楚了，你给个技术方案？
```

#### 第二步：技术方案设计

```
Claude：清楚了。技术方案如下：

**技术栈选择**：
- 前端：React 18 + TypeScript + Ant Design
- 后端：Node.js + Express + TypeScript
- 数据库：PostgreSQL（关系型数据适合反馈系统）
- 文件存储：AWS S3（附件存储）
- 通知：Nodemailer（邮件）+ WebSocket（站内信）
- 离线存储：IndexedDB（前端）+ PouchDB（同步）

**数据库设计**：
```
反馈表（feedbacks）
- id: UUID
- user_id: UUID (外键)
- category: ENUM (bug, feature, other)
- priority: ENUM (low, medium, high, urgent)
- status: ENUM (pending, processing, resolved, closed)
- title: VARCHAR(255)
- content: TEXT
- attachments: JSONB (附件信息数组)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- resolved_at: TIMESTAMP (可选)
- resolved_by: UUID (管理员ID，可选)

附件表（attachments）
- id: UUID
- feedback_id: UUID (外键)
- file_name: VARCHAR(255)
- file_url: TEXT (S3 URL)
- file_size: INTEGER
- file_type: VARCHAR(50)
- created_at: TIMESTAMP

通知表（notifications）
- id: UUID
- user_id: UUID
- feedback_id: UUID (外键)
- type: ENUM (status_change, comment)
- message: TEXT
- read: BOOLEAN
- created_at: TIMESTAMP
```

**API设计**：
```
POST /api/feedbacks - 提交反馈
GET /api/feedbacks - 获取反馈列表（管理员）
GET /api/feedbacks/:id - 获取反馈详情
PUT /api/feedbacks/:id - 更新反馈（管理员）
DELETE /api/feedbacks/:id - 删除反馈（管理员）
GET /api/feedbacks/my - 获取我的反馈列表
POST /api/feedbacks/:id/attachments - 上传附件
GET /api/notifications - 获取通知
PUT /api/notifications/:id/read - 标记已读
```

**离线同步策略**：
- 前端用IndexedDB存储离线反馈
- 联网后用PouchDB同步到后端
- 冲突解决：以后端为准

这个方案可行吗？
```

```
我：方案可以。现在开始实现吧，先做数据库和API。
```

#### 第三步：数据库实现

**Claude生成数据库迁移**：
```typescript
// src/migrations/001_create_feedbacks_table.ts
import { Pool } from 'pg';

export async function up(pool: Pool) {
  await pool.query(`
    CREATE TABLE feedbacks (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      category VARCHAR(20) NOT NULL CHECK (category IN ('bug', 'feature', 'other')),
      priority VARCHAR(20) NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
      status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'resolved', 'closed')),
      title VARCHAR(255) NOT NULL,
      content TEXT NOT NULL,
      attachments JSONB DEFAULT '[]',
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW(),
      resolved_at TIMESTAMP,
      resolved_by UUID REFERENCES users(id)
    );
    
    CREATE INDEX idx_feedbacks_user_id ON feedbacks(user_id);
    CREATE INDEX idx_feedbacks_status ON feedbacks(status);
    CREATE INDEX idx_feedbacks_priority ON feedbacks(priority);
  `);
}

export async function down(pool: Pool) {
  await pool.query('DROP TABLE feedbacks');
}
```

```typescript
// src/migrations/002_create_attachments_table.ts
export async function up(pool: Pool) {
  await pool.query(`
    CREATE TABLE attachments (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      feedback_id UUID NOT NULL REFERENCES feedbacks(id) ON DELETE CASCADE,
      file_name VARCHAR(255) NOT NULL,
      file_url TEXT NOT NULL,
      file_size INTEGER NOT NULL,
      file_type VARCHAR(50) NOT NULL,
      created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE INDEX idx_attachments_feedback_id ON attachments(feedback_id);
  `);
}

export async function down(pool: Pool) {
  await pool.query('DROP TABLE attachments');
}
```

```typescript
// src/migrations/003_create_notifications_table.ts
export async function up(pool: Pool) {
  await pool.query(`
    CREATE TABLE notifications (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      feedback_id UUID REFERENCES feedbacks(id) ON DELETE CASCADE,
      type VARCHAR(20) NOT NULL CHECK (type IN ('status_change', 'comment')),
      message TEXT NOT NULL,
      read BOOLEAN DEFAULT FALSE,
      created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE INDEX idx_notifications_user_id ON notifications(user_id);
    CREATE INDEX idx_notifications_read ON notifications(read);
  `);
}

export async function down(pool: Pool) {
  await pool.query('DROP TABLE notifications');
}
```

#### 第四步：API实现

**Claude生成API代码**：
```typescript
// src/types/feedback.ts
export interface Feedback {
  id: string;
  userId: string;
  category: 'bug' | 'feature' | 'other';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'processing' | 'resolved' | 'closed';
  title: string;
  content: string;
  attachments: Attachment[];
  createdAt: Date;
  updatedAt: Date;
  resolvedAt?: Date;
  resolvedBy?: string;
}

export interface CreateFeedbackDto {
  category: 'bug' | 'feature' | 'other';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  title: string;
  content: string;
  attachments?: File[];
}

export interface UpdateFeedbackDto {
  status?: 'pending' | 'processing' | 'resolved' | 'closed';
  title?: string;
  content?: string;
  resolvedBy?: string;
}

export interface Attachment {
  id: string;
  feedbackId: string;
  fileName: string;
  fileUrl: string;
  fileSize: number;
  fileType: string;
  createdAt: Date;
}
```

```typescript
// src/controllers/feedbackController.ts
import { Request, Response } from 'express';
import { FeedbackService } from '../services/FeedbackService';
import { S3Service } from '../services/S3Service';
import { NotificationService } from '../services/NotificationService';

const feedbackService = new FeedbackService();
const s3Service = new S3Service();
const notificationService = new NotificationService();

export class FeedbackController {
  async createFeedback(req: Request, res: Response) {
    try {
      const userId = req.user.id;
      const { category, priority, title, content } = req.body;
      
      // 上传附件
      const attachments = [];
      if (req.files) {
        for (const file of req.files as Express.Multer.File[]) {
          const fileUrl = await s3Service.uploadFile(file);
          attachments.push({
            fileName: file.originalname,
            fileUrl,
            fileSize: file.size,
            fileType: file.mimetype
          });
        }
      }
      
      // 创建反馈
      const feedback = await feedbackService.create({
        userId,
        category,
        priority,
        title,
        content,
        attachments
      });
      
      res.status(201).json(feedback);
    } catch (error) {
      res.status(500).json({ error: '创建反馈失败' });
    }
  }
  
  async getFeedbacks(req: Request, res: Response) {
    try {
      const { status, priority, page = 1, limit = 20 } = req.query;
      
      const feedbacks = await feedbackService.findAll({
        status: status as string,
        priority: priority as string,
        page: Number(page),
        limit: Number(limit)
      });
      
      res.json(feedbacks);
    } catch (error) {
      res.status(500).json({ error: '获取反馈列表失败' });
    }
  }
  
  async updateFeedback(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const updates = req.body;
      const adminId = req.user.id;
      
      // 获取原反馈
      const oldFeedback = await feedbackService.findById(id);
      if (!oldFeedback) {
        return res.status(404).json({ error: '反馈不存在' });
      }
      
      // 更新反馈
      const feedback = await feedbackService.update(id, {
        ...updates,
        resolvedBy: updates.status === 'resolved' ? adminId : undefined,
        resolvedAt: updates.status === 'resolved' ? new Date() : undefined
      });
      
      // 发送通知
      if (updates.status && updates.status !== oldFeedback.status) {
        await notificationService.create({
          userId: oldFeedback.userId,
          feedbackId: id,
          type: 'status_change',
          message: `你的反馈状态已更新为${updates.status}`
        });
        
        // 发送邮件
        await notificationService.sendEmail(
          oldFeedback.userId,
          '反馈状态更新',
          `你的反馈"${oldFeedback.title}"状态已更新为${updates.status}`
        );
      }
      
      res.json(feedback);
    } catch (error) {
      res.status(500).json({ error: '更新反馈失败' });
    }
  }
  
  async getMyFeedbacks(req: Request, res: Response) {
    try {
      const userId = req.user.id;
      const feedbacks = await feedbackService.findByUserId(userId);
      
      res.json(feedbacks);
    } catch (error) {
      res.status(500).json({ error: '获取我的反馈失败' });
    }
  }
}
```

#### 第五步：前端实现

#### 用户反馈系统数据流图

```mermaid
flowchart LR
    subgraph "用户端"
        A[用户提交反馈]
        B[离线存储IndexedDB]
        C[联网检测]
    end
    
    subgraph "同步层"
        D[PouchDB同步]
        E[重试机制]
    end
    
    subgraph "服务端"
        F[API接收]
        G[文件上传S3]
        H[数据库存储]
    end
    
    subgraph "通知层"
        I[站内信WebSocket]
        J[邮件Nodemailer]
    end
    
    A --> B
    B --> C
    C -->|在线| F
    C -->|离线| D
    D --> E
    E --> F
    F --> G
    F --> H
    H --> I
    H --> J
    
    style A fill:#e1f5ff
    style H fill:#c8e6c9
    style C fill:#fff9c4
```

**Claude生成前端代码**：
```tsx
// src/components/FeedbackForm.tsx
import { useState } from 'react';
import { Form, Input, Select, Button, Upload, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

interface FeedbackFormProps {
  onSubmit: (data: any) => Promise<void>;
}

export function FeedbackForm({ onSubmit }: FeedbackFormProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState<any[]>([]);
  
  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      // 验证文件大小
      const oversizedFiles = fileList.filter(f => f.size > 10 * 1024 * 1024);
      if (oversizedFiles.length > 0) {
        message.error('文件大小不能超过10MB');
        return;
      }
      
      await onSubmit({
        ...values,
        attachments: fileList
      });
      
      form.resetFields();
      setFileList([]);
      message.success('反馈提交成功');
    } catch (error) {
      message.error('提交失败，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  const uploadProps = {
    beforeUpload: (file: File) => {
      const isValidType = ['image/jpeg', 'image/png', 'text/plain', 'application/octet-stream'].includes(file.type);
      if (!isValidType) {
        message.error('只支持jpg/png/txt/log格式');
      }
      return isValidType;
    },
    onChange: (info: any) => {
      setFileList(info.fileList);
    },
    fileList
  };
  
  return (
    <Form form={form} onFinish={handleSubmit} layout="vertical">
      <Form.Item
        label="反馈类型"
        name="category"
        rules={[{ required: true, message: '请选择反馈类型' }]}
      >
        <Select>
          <Select.Option value="bug">Bug</Select.Option>
          <Select.Option value="feature">功能建议</Select.Option>
          <Select.Option value="other">其他</Select.Option>
        </Select>
      </Form.Item>
      
      <Form.Item
        label="优先级"
        name="priority"
        rules={[{ required: true, message: '请选择优先级' }]}
      >
        <Select>
          <Select.Option value="low">低</Select.Option>
          <Select.Option value="medium">中</Select.Option>
          <Select.Option value="high">高</Select.Option>
          <Select.Option value="urgent">紧急</Select.Option>
        </Select>
      </Form.Item>
      
      <Form.Item
        label="标题"
        name="title"
        rules={[{ required: true, message: '请输入标题' }]}
      >
        <Input maxLength={255} placeholder="简要描述问题" />
      </Form.Item>
      
      <Form.Item
        label="详细描述"
        name="content"
        rules={[{ required: true, message: '请输入详细描述' }]}
      >
        <Input.TextArea rows={6} placeholder="详细描述问题或建议" />
      </Form.Item>
      
      <Form.Item label="附件">
        <Upload {...uploadProps} multiple>
          <Button icon={<UploadOutlined />}>上传附件</Button>
        </Upload>
        <div style={{ marginTop: 8, color: '#999' }}>
          支持jpg/png/txt/log格式，单个文件最大10MB
        </div>
      </Form.Item>
      
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block>
          提交反馈
        </Button>
      </Form.Item>
    </Form>
  );
}
```

```tsx
// src/components/OfflineFeedback.tsx
import { useState, useEffect } from 'react';
import { openDB } from 'idb';
import PouchDB from 'pouchdb';

#### 离线同步流程图

```mermaid
flowchart TD
    A[用户提交反馈] --> B{网络状态检测}
    B -->|在线| C[直接提交到服务器]
    B -->|离线| D[保存到IndexedDB]
    C --> E[服务器处理]
    E --> F[返回成功]
    D --> G[显示离线提示]
    G --> H[监听网络状态]
    H --> I{网络恢复?}
    I -->|否| H
    I -->|是| J[读取本地数据]
    J --> K[批量同步到服务器]
    K --> L{同步成功?}
    L -->|是| M[删除本地数据]
    L -->|否| N[标记失败]
    N --> O[等待下次重试]
    M --> P[更新UI状态]
    
    style B fill:#fff9c4
    style I fill:#fff9c4
    style L fill:#fff9c4
    style F fill:#c8e6c9
    style P fill:#c8e6c9
```

export function OfflineFeedback() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingFeedbacks, setPendingFeedbacks] = useState<any[]>([]);
  
  useEffect(() => {
    // 监听网络状态
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // 加载离线反馈
    loadPendingFeedbacks();
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  useEffect(() => {
    // 联网后自动同步
    if (isOnline && pendingFeedbacks.length > 0) {
      syncPendingFeedbacks();
    }
  }, [isOnline]);
  
  const loadPendingFeedbacks = async () => {
    const db = await openDB('feedback-db', 1);
    const feedbacks = await db.getAll('pending-feedbacks');
    setPendingFeedbacks(feedbacks);
  };
  
  const syncPendingFeedbacks = async () => {
    for (const feedback of pendingFeedbacks) {
      try {
        await fetch('/api/feedbacks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(feedback.data)
        });
        
        // 删除已同步的反馈
        const db = await openDB('feedback-db', 1);
        await db.delete('pending-feedbacks', feedback.id);
      } catch (error) {
        console.error('同步失败:', error);
      }
    }
    
    loadPendingFeedbacks();
  };
  
  const saveOfflineFeedback = async (data: any) => {
    const db = await openDB('feedback-db', 1);
    await db.put('pending-feedbacks', {
      id: Date.now().toString(),
      data,
      timestamp: new Date()
    });
    
    loadPendingFeedbacks();
  };
  
  if (!isOnline) {
    return (
      <div style={{ padding: 16, background: '#fff3cd', borderRadius: 4 }}>
        <strong>离线模式</strong>
        <p>反馈将保存在本地，联网后自动同步</p>
        {pendingFeedbacks.length > 0 && (
          <p>待同步反馈：{pendingFeedbacks.length}条</p>
        )}
      </div>
    );
  }
  
  return null;
}
```

#### 第六步：测试

```
我：前后端都做完了，现在测试一下。

Claude：好的，我帮你测试：

1. **功能测试**
   - 提交反馈（带附件）
   - 查看反馈列表
   - 更新反馈状态
   - 离线提交和同步

2. **性能测试**
   - 并发提交100个反馈
   - 附件上传性能

3. **安全测试**
   - 文件类型验证
   - 文件大小限制
   - 权限校验

先测哪个？
```

```
我：先测功能。

Claude：好的，我运行功能测试。

（Claude执行测试）

测试结果：
- ✅ 提交反馈正常
- ✅ 附件上传正常
- ✅ 状态更新正常
- ✅ 通知发送正常
- ⚠️ 发现问题：离线同步时，如果网络中断，会丢失数据

需要修复离线同步的可靠性？
```

```
我：需要修复。

Claude：好的，我添加重试机制和本地备份。
```

**Claude修复离线同步**：
```typescript
const syncPendingFeedbacks = async () => {
  const maxRetries = 3;
  
  for (const feedback of pendingFeedbacks) {
    let retryCount = 0;
    let success = false;
    
    while (retryCount < maxRetries && !success) {
      try {
        await fetch('/api/feedbacks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(feedback.data)
        });
        
        success = true;
        
        // 删除已同步的反馈
        const db = await openDB('feedback-db', 1);
        await db.delete('pending-feedbacks', feedback.id);
      } catch (error) {
        retryCount++;
        if (retryCount >= maxRetries) {
          console.error('同步失败，已达到最大重试次数:', error);
          // 标记为失败，但不删除
          const db = await openDB('feedback-db', 1);
          await db.put('pending-feedbacks', {
            ...feedback,
            syncFailed: true,
            lastError: error.message
          });
        } else {
          // 等待后重试
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
        }
      }
    }
  }
  
  loadPendingFeedbacks();
};
```

```
我：修复完成。现在整体测试一下吧。

Claude：好的，运行完整测试套件。

测试结果：
- ✅ 功能测试：全部通过
- ✅ 性能测试：100并发响应时间<500ms
- ✅ 安全测试：文件验证正常
- ✅ 离线同步：重试机制正常

可以部署了。要生成部署文档吗？
```

#### 第七步：部署

**Claude生成部署文档**：
```markdown
# 用户反馈系统部署文档

## 环境要求
- Node.js 18+
- PostgreSQL 14+
- AWS S3账户
- SMTP服务器（邮件发送）

## 环境变量
```env
DATABASE_URL=postgresql://...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=feedback-attachments
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
```

## 部署步骤

### 1. 数据库迁移
```bash
npm run migrate
```

### 2. 构建前端
```bash
cd frontend
npm run build
```

### 3. 启动后端
```bash
cd backend
npm run start
```

### 4. 配置Nginx
```nginx
server {
    listen 80;
    server_name feedback.example.com;
    
    location / {
        root /var/www/feedback-frontend;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. 配置定时任务（清理旧反馈）
```cron
# 每天凌晨2点清理30天前已关闭的反馈
0 2 * * * cd /var/www/feedback-backend && npm run cleanup
```
```

```
我：部署文档很详细。总结一下这个Spec Coding的流程？

Claude：Spec Coding的完整流程：

1. **需求理解**：深入分析PRD，提出澄清问题
2. **技术方案**：设计技术栈、数据库、API
3. **数据库实现**：编写迁移脚本
4. **API实现**：编写控制器和服务层
5. **前端实现**：实现UI和交互
6. **测试验证**：功能、性能、安全测试
7. **部署上线**：编写部署文档和脚本

关键点：
- 先明确需求再动手
- 每一步都有文档和代码
- 测试驱动，发现问题及时修复
- 考虑边界情况（离线、重试）

这个流程可以复用到任何项目，减少返工，提高质量。
```

---

## Skills应用场景

Claude Code的Skills是预定义的编程能力模块，可以快速解决特定问题。

#### Skills应用场景图

```mermaid
mindmap
  root((Claude Code Skills))
    开发加速
      find-skills
      skill-creator
      programmer-prompt-engineering-guide
    质量保证
      code-review
      webapp-testing
      audit-website
    自动化
      agent-browser
      pdf
    创意辅助
      brainstorming
      documentation-generator
```

### Skill 1：find-skills - 发现和安装Skills

**场景**：需要找到合适的Skill来加速开发。

```
我：我需要找一个React相关的Skill，帮我找找。

Claude：好的，我用find-skills搜索React相关的Skills。

（Claude执行搜索）

找到以下React相关Skills：

1. **vercel-react-best-practices** (216K+ 安装)
   - Vercel官方React最佳实践
   - 包含性能优化、代码规范
   - 适合：React项目优化

2. **frontend-design** (164K+ 安装)
   - 前端设计指南
   - UI/UX最佳实践
   - 适合：前端设计决策

3. **remotion-best-practices** (150K+ 安装)
   - Remotion视频框架最佳实践
   - 适合：视频相关项目

4. **web-design-guidelines** (171K+ 安装)
   - Web设计规范
   - 响应式设计指南
   - 适合：Web项目设计

你要哪个？我帮你安装。
```

```
我：安装vercel-react-best-practices。

Claude：好的，安装命令：

```bash
npx skills add vercel/skills --skill vercel-react-best-practices
```

安装完成后，你可以这样使用：

```bash
claude "用vercel-react-best-practices优化这个React组件"
```

要我现在帮你优化一个组件吗？
```

### Skill 2：programmer-prompt-engineering-guide - 提示词工程

**场景**：需要写出更好的提示词来让Claude Code生成更准确的代码。

```
我：我总觉得我的提示词不够精确，Claude Code生成的代码不太符合预期。你教我怎么写好提示词？

Claude：好的，提示词工程有几个关键原则：

**1. 明确目标**
❌ 不好："优化这个函数"
✅ 好："优化这个函数的时间复杂度，从O(n²)降到O(n)"

**2. 提供上下文**
❌ 不好："修复登录bug"
✅ 好："修复登录bug：使用React+TypeScript，认证库@auth0/react-auth0，错误信息'Cannot read property of undefined'，相关文件src/components/Login.tsx"

**3. 分步骤**
❌ 不好："做一个电商系统"
✅ 好："第一步：设计数据库schema；第二步：实现用户认证API；第三步：实现商品列表API"

**4. 指定约束**
❌ 不好："写一个排序算法"
✅ 好："用JavaScript写一个快速排序算法，要求：时间复杂度O(n log n)，空间复杂度O(log n)，包含类型定义"

**5. 提供示例**
❌ 不好："写一个API接口"
✅ 好："写一个用户管理API，参考这个格式：{id, name, email, role, createdAt}"

我给你一个实战例子？
```

```
我：好，给我一个实战例子。

Claude：好的，假设你要让Claude Code生成一个购物车组件。

❌ 不好：
```
claude "写一个购物车组件"
```

✅ 好：
```
claude "
用React + TypeScript + Tailwind CSS写一个购物车组件：

需求：
1. 显示商品列表（图片、名称、价格、数量）
2. 可以增减数量
3. 显示总价
4. 有删除按钮
5. 空购物车显示提示

技术约束：
- 使用shadcn/ui的Card组件
- 用Zustand管理状态
- 图片用next/image优化
- 价格格式化为¥XX.XX

参考这个数据结构：
interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  image: string;
}
"
```

后者生成的代码会更精准，更符合你的需求。
```

### Skill 3：audit-website - 网站审计

**场景**：需要审计网站的性能、SEO、可访问性。

```
我：我的网站上线了，但不知道质量怎么样。帮我审计一下。

Claude：好的，我用audit-website Skill全面审计你的网站。

（Claude执行审计）

审计报告：

**性能评分：72/100**
- 首次内容绘制（FCP）：2.1s（目标<1.8s）
- 最大内容绘制（LCP）：3.5s（目标<2.5s）
- 累积布局偏移（CLS）：0.08（目标<0.1）
- ⚠️ 图片未优化，建议用WebP格式
- ⚠️ CSS未压缩，建议用CSS压缩工具

**SEO评分：85/100**
- ✅ meta标签完整
- ✅ 结构化数据正确
- ⚠️ 缺少sitemap.xml
- ⚠️ robots.txt配置不完整

**可访问性评分：90/100**
- ✅ 颜色对比度符合WCAG AA
- ✅ 键盘导航可用
- ⚠️ 部分图片缺少alt属性

**安全评分：95/100**
- ✅ HTTPS配置正确
- ✅ CSP头部设置合理
- ✅ 无已知安全漏洞

建议优先修复：
1. 图片优化（WebP格式，懒加载）
2. 添加sitemap.xml
3. 补充图片alt属性

要我帮你修复这些问题吗？
```

### Skill 4：brainstorming - 头脑风暴

**场景**：需要为项目想名字、想功能点、想解决方案。

```
我：我要做一个AI写作助手，想不出好名字。帮我头脑风暴一下。

Claude：好的，我用brainstorming Skill帮你想名字。

（Claude执行头脑风暴）

生成的名字分类：

**科技感强**：
- AIWriter Pro
- SmartScribe
- IntelliText
- NeuralPen

**文艺感强**：
- 墨韵
- 笔耕
- 文心
- 思泉

**现代感强**：
- WriteFlow
- TextMate
- InkAI
- DraftBot

**简洁有力**：
- 写作
- 灵感
- 笔记
- 文案

你偏好哪种风格？我可以继续生成更多。
```

```
我：科技感强的不错，再生成几个。

Claude：好的，继续生成科技感强的名字：

- CodeWriter
- AIQuill
- SmartPen
- TextGenius
- WriteAI
- IntelliWrite
- AutoScribe
- NeuralWriter

这些名字怎么样？有喜欢的吗？
```

### Skill 5：pdf - PDF处理

**场景**：需要生成PDF、解析PDF、合并PDF。

```
我：我需要把用户的订单生成PDF发票。帮我实现。

Claude：好的，我用pdf Skill帮你实现PDF生成。

（Claude执行）

生成的代码：
```typescript
import PDFDocument from 'pdfkit';
import { saveAs } from 'file-saver';

export async function generateInvoicePDF(order: Order) {
  const doc = new PDFDocument();
  const stream = doc.pipe(blobStream());
  
  // 设置字体（支持中文）
  doc.font('src/assets/fonts/NotoSansSC-Regular.ttf');
  
  // 添加标题
  doc.fontSize(24).text('发票', { align: 'center' });
  doc.moveDown();
  
  // 添加订单信息
  doc.fontSize(12).text(`订单号：${order.id}`);
  doc.text(`日期：${order.createdAt.toLocaleDateString('zh-CN')}`);
  doc.moveDown();
  
  // 添加商品列表
  doc.fontSize(14).text('商品明细', { underline: true });
  doc.moveDown();
  
  order.items.forEach((item, index) => {
    doc.fontSize(12).text(
      `${index + 1}. ${item.name} - ¥${item.price} x ${item.quantity}`
    );
  });
  
  doc.moveDown();
  
  // 添加总价
  doc.fontSize(16).text(`总计：¥${order.total}`, { align: 'right' });
  
  // 生成PDF
  doc.end();
  
  return new Promise<Blob>((resolve) => {
    stream.on('finish', () => {
      const blob = stream.toBlob('application/pdf');
      resolve(blob);
    });
  });
}

// 使用
const pdfBlob = await generateInvoicePDF(order);
saveAs(pdfBlob, `invoice-${order.id}.pdf`);
```

这个实现支持中文、自定义样式、商品列表。要调整样式吗？
```

### Skill 6：skill-creator - 创建自定义Skill

**场景**：需要创建一个自定义Skill来重复使用特定的编程模式。

```
我：我们团队经常需要创建REST API，每次都要写类似的代码。能不能创建一个Skill来自动生成？

Claude：好的，我用skill-creator帮你创建一个REST API生成Skill。

（Claude执行）

生成的Skill结构：
```typescript
// skills/rest-api-generator/skill.json
{
  "name": "rest-api-generator",
  "description": "快速生成REST API的完整代码",
  "version": "1.0.0",
  "author": "your-team",
  "commands": [
    {
      "name": "generate-api",
      "description": "生成REST API",
      "parameters": {
        "entity": "实体名称",
        "fields": "字段定义",
        "database": "数据库类型"
      }
    }
  ]
}
```

```typescript
// skills/rest-api-generator/index.ts
export class RestApiGenerator {
  async generateAPI(params: {
    entity: string;
    fields: Field[];
    database: 'postgresql' | 'mongodb';
  }) {
    // 生成数据库模型
    const model = this.generateModel(params);
    
    // 生成控制器
    const controller = this.generateController(params);
    
    // 生成路由
    const routes = this.generateRoutes(params);
    
    // 生成服务层
    const service = this.generateService(params);
    
    return { model, controller, routes, service };
  }
  
  private generateModel(params: any) {
    // 根据数据库类型生成模型代码
  }
  
  private generateController(params: any) {
    // 生成控制器代码
  }
  
  // ... 其他方法
}
```

使用方法：
```bash
claude "用rest-api-generator生成用户管理API，字段：id, name, email, role, createdAt"
```

这个Skill可以节省你每次创建API的时间。要调整生成规则吗？
```

### Skill 7：agent-browser - 浏览器自动化

**场景**：需要自动化浏览器操作，比如爬取数据、自动化测试。

```
我：我需要爬取电商网站的商品数据，包括价格、库存、评价。帮我实现。

Claude：好的，我用agent-browser Skill帮你实现浏览器自动化。

（Claude执行）

生成的代码：
```typescript
import { chromium } from 'playwright';

export async function scrapeProductData(url: string) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.goto(url);
  
  // 等待商品列表加载
  await page.waitForSelector('.product-item');
  
  // 提取商品数据
  const products = await page.evaluate(() => {
    const items = document.querySelectorAll('.product-item');
    return Array.from(items).map(item => ({
      name: item.querySelector('.product-name')?.textContent,
      price: item.querySelector('.product-price')?.textContent,
      stock: item.querySelector('.product-stock')?.textContent,
      rating: item.querySelector('.product-rating')?.textContent
    }));
  });
  
  await browser.close();
  return products;
}

// 使用
const products = await scrapeProductData('https://example.com/products');
console.log(products);
```

这个实现支持：
- 自动等待元素加载
- 提取结构化数据
- 处理动态加载
- 反爬虫策略

需要添加更多功能吗？
```

### Skill 8：webapp-testing - Web应用测试

**场景**：需要为Web应用编写自动化测试。

```
我：我的Web应用需要E2E测试，帮我写测试用例。

Claude：好的，我用webapp-testing Skill帮你生成测试用例。

（Claude执行）

生成的测试代码：
```typescript
// tests/e2e/checkout.spec.ts
import { test, expect } from '@playwright/test';

test.describe('购物车结账流程', () => {
  test('应该能完成完整的购物流程', async ({ page }) => {
    // 访问首页
    await page.goto('/');
    
    // 添加商品到购物车
    await page.click('.product-item:first-child .add-to-cart');
    
    // 进入购物车
    await page.click('.cart-icon');
    
    // 验证商品在购物车中
    await expect(page.locator('.cart-item')).toHaveCount(1);
    
    // 点击结账
    await page.click('.checkout-button');
    
    // 填写表单
    await page.fill('#name', '张三');
    await page.fill('#email', 'zhangsan@example.com');
    await page.fill('#address', '北京市朝阳区');
    
    // 提交订单
    await page.click('.submit-order');
    
    // 验证订单成功
    await expect(page.locator('.order-success')).toBeVisible();
  });
  
  test('应该显示正确的总价', async ({ page }) => {
    await page.goto('/');
    
    // 添加多个商品
    await page.click('.product-item:nth-child(1) .add-to-cart');
    await page.click('.product-item:nth-child(2) .add-to-cart');
    
    await page.click('.cart-icon');
    
    // 验证总价
    const totalPrice = await page.textContent('.total-price');
    expect(totalPrice).toBe('¥299.00');
  });
});
```

运行测试：
```bash
npx playwright test
```

需要添加更多测试场景吗？
```

### Skill 9：code-review - 代码审查

**场景**：需要对代码进行审查，找出潜在问题和改进点。

```
我：我刚写了一个用户认证模块，帮我审查一下代码质量。

Claude：好的，我用code-review Skill帮你审查代码。

（Claude执行）

代码审查报告：

**安全性问题**：
- ⚠️ 密码没有加盐，建议使用bcrypt的saltRounds
- ⚠️ JWT密钥硬编码，应该用环境变量
- ⚠️ 没有速率限制，容易被暴力破解

**代码质量问题**：
- ⚠️ 函数过长（200行），建议拆分
- ⚠️ 缺少错误处理
- ⚠️ 没有输入验证
- ⚠️ 缺少类型定义

**性能问题**：
- ⚠️ 每次请求都查询数据库，建议加缓存
- ⚠️ 没有连接池配置

**改进建议**：
```typescript
// 添加输入验证
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});

// 添加错误处理
export async function login(credentials: LoginDto) {
  try {
    const validated = loginSchema.parse(credentials);
    // ...
  } catch (error) {
    throw new ValidationError('输入格式不正确');
  }
}

// 添加速率限制
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 5 // 最多5次尝试
});
```

要我帮你修复这些问题吗？
```

### Skill 10：documentation-generator - 文档生成

**场景**：需要为API或组件生成文档。

```
我：我刚写了一组API接口，需要生成API文档。帮我生成。

Claude：好的，我用documentation-generator Skill帮你生成文档。

（Claude执行）

生成的文档：
```markdown
# 用户管理API文档

## 基础信息
- Base URL: `https://api.example.com`
- 认证方式: Bearer Token
- 响应格式: JSON

## 接口列表

### 1. 用户注册

**请求**
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "张三"
}
```

**响应**
```
201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "张三",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

**错误码**
- 400: 参数错误
- 409: 邮箱已存在

### 2. 用户登录

**请求**
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**
```
200 OK
{
  "token": "jwt_token",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "张三"
  }
}
```

**错误码**
- 400: 参数错误
- 401: 密码错误

### 3. 获取当前用户

**请求**
```
GET /api/users/me
Authorization: Bearer {token}
```

**响应**
```
200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "张三",
  "role": "user",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

**错误码**
- 401: 未认证
```

文档已生成，包含：
- 完整的接口列表
- 请求/响应示例
- 错误码说明
- 认证方式

需要调整格式或添加更多内容吗？
```

---

## 团队协作模式

多Agent协作可以让多个Claude Code实例同时工作，像一个小团队一样。

#### 多Agent协作架构

```mermaid
graph TB
    subgraph "协调层"
        A[协调Agent]
        A --> B[API规范设计]
        A --> C[接口对接]
        A --> D[问题分配]
    end
    
    subgraph "开发层"
        E[前端Agent]
        F[后端Agent]
        G[测试Agent]
    end
    
    subgraph "执行层"
        H[React组件]
        I[Node.js API]
        J[测试用例]
    end
    
    A --> E
    A --> F
    A --> G
    E --> H
    F --> I
    G --> J
    E -.-> C
    F -.-> C
    G -.-> D
    
    style A fill:#e1f5ff
    style E fill:#fff9c4
    style F fill:#fff9c4
    style G fill:#fff9c4
```

#### 协作时序图

```mermaid
sequenceDiagram
    participant Coord as 协调Agent
    participant Frontend as 前端Agent
    participant Backend as 后端Agent
    participant Test as 测试Agent

    Coord->>Coord: 设计API规范
    Coord->>Frontend: 发送API规范
    Coord->>Backend: 发送API规范
    Coord->>Test: 准备测试环境
    
    par 并行开发
        Frontend->>Frontend: 实现前端组件
        Backend->>Backend: 实现后端API
        Test->>Test: 编写测试用例
    end
    
    Frontend->>Coord: 前端完成
    Backend->>Coord: 后端完成
    Test->>Coord: 测试完成
    
    Coord->>Coord: 检查接口一致性
    alt 发现问题
        Coord->>Frontend: 修复前端
        Coord->>Backend: 修复后端
    end
    
    Coord->>Test: 运行测试
    Test->>Coord: 测试结果
    alt 测试失败
        Coord->>Frontend: 修复bug
        Coord->>Backend: 修复bug
        Test->>Test: 重新测试
    end
    
    Coord->>Coord: 部署上线
```

### 实战案例：全栈开发协作

**背景**：一个3人团队需要开发一个博客系统，前端、后端、测试同时进行。

#### 协作方案

```
我：我们团队要开发一个博客系统，我想用多Agent协作提高效率。你给个方案？

Claude：好的，多Agent协作方案如下：

**角色分配**：
- Agent 1（前端）：负责React前端开发
- Agent 2（后端）：负责Node.js后端API
- Agent 3（测试）：负责编写测试用例
- Agent 4（协调）：负责整体协调和接口对接

**工作流程**：
```
Day 1：
- Agent 4：设计API接口规范
- Agent 1：搭建前端框架
- Agent 2：搭建后端框架

Day 2：
- Agent 1：实现前端页面
- Agent 2：实现后端API
- Agent 3：编写API测试

Day 3：
- Agent 4：协调前后端对接
- Agent 3：编写E2E测试
- Agent 1 + Agent 2：联调修复bug
```

**启动方式**：
```bash
# 终端1：前端Agent
claude --session frontend "搭建React前端框架，使用Next.js + TypeScript + Tailwind"

# 终端2：后端Agent
claude --session backend "搭建Node.js后端框架，使用Express + TypeScript + PostgreSQL"

# 终端3：测试Agent
claude --session testing "准备测试环境，安装Jest和Playwright"

# 终端4：协调Agent
claude --session coordinator "设计博客系统的API接口规范"
```

这个方案可行吗？
```

```
我：可行，开始执行。

Claude：好的，我先启动协调Agent设计API规范。

（Claude执行）

API规范设计完成：
```
用户相关：
- POST /api/auth/register - 注册
- POST /api/auth/login - 登录
- GET /api/users/me - 获取当前用户

文章相关：
- GET /api/posts - 获取文章列表
- GET /api/posts/:id - 获取文章详情
- POST /api/posts - 创建文章
- PUT /api/posts/:id - 更新文章
- DELETE /api/posts/:id - 删除文章

评论相关：
- GET /api/posts/:id/comments - 获取评论
- POST /api/posts/:id/comments - 添加评论
```

现在启动其他Agent？
```

#### 协作执行

```
我：启动前端Agent。

Claude：好的，前端Agent开始工作。

（Claude执行）

前端Agent输出：
```
✅ 搭建Next.js项目
✅ 配置TypeScript
✅ 安装Tailwind CSS
✅ 创建页面结构
  - pages/index.tsx (首页)
  - pages/posts/index.tsx (文章列表)
  - pages/posts/[id].tsx (文章详情)
  - pages/login.tsx (登录)
  - pages/register.tsx (注册)
✅ 配置路由
✅ 创建组件
  - components/PostCard.tsx
  - components/CommentList.tsx
  - components/Navbar.tsx
```

前端框架搭建完成，等待API对接。
```

```
我：启动后端Agent。

Claude：好的，后端Agent开始工作。

（Claude执行）

后端Agent输出：
```
✅ 搭建Express项目
✅ 配置TypeScript
✅ 连接PostgreSQL
✅ 创建数据模型
  - User
  - Post
  - Comment
✅ 实现API路由
  - routes/auth.ts
  - routes/posts.ts
  - routes/comments.ts
✅ 实现控制器
  - controllers/authController.ts
  - controllers/postsController.ts
  - controllers/commentsController.ts
✅ 添加中间件
  - 认证中间件
  - 错误处理中间件
```

后端API实现完成，等待测试。
```

```
我：启动测试Agent。

Claude：好的，测试Agent开始工作。

（Claude执行）

测试Agent输出：
```
✅ 安装Jest
✅ 安装Playwright
✅ 编写API测试
  - tests/api/auth.test.ts
  - tests/api/posts.test.ts
✅ 编写E2E测试
  - tests/e2e/registration.spec.ts
  - tests/e2e/login.spec.ts
  - tests/e2e/create-post.spec.ts
```

测试用例编写完成，准备运行测试。
```

#### 协调对接

```
我：现在让协调Agent对接前后端。

Claude：好的，协调Agent开始工作。

（Claude执行）

协调Agent输出：
```
✅ 检查API接口一致性
✅ 发现问题：
  - 前端期望的响应格式与后端不一致
  - 部分字段命名不统一（camelCase vs snake_case）
✅ 修复方案：
  - 统一使用camelCase
  - 添加响应拦截器转换数据格式
✅ 前端添加API客户端
  - lib/api/client.ts
  - lib/api/posts.ts
  - lib/api/auth.ts
✅ 后端添加CORS配置
```

前后端对接完成，准备联调测试。
```

#### 联调测试

```
我：运行测试Agent执行测试。

Claude：好的，测试Agent开始执行测试。

（Claude执行）

测试结果：
```
API测试：
✅ POST /api/auth/register - 通过
✅ POST /api/auth/login - 通过
✅ GET /api/posts - 通过
✅ POST /api/posts - 通过
⚠️ PUT /api/posts/:id - 失败（权限校验问题）

E2E测试：
✅ 注册流程 - 通过
✅ 登录流程 - 通过
⚠️ 创建文章 - 失败（图片上传问题）
```

发现2个问题，需要修复。要启动修复流程吗？
```

```
我：启动修复流程。

Claude：好的，协调Agent分配任务：
- 前端Agent：修复图片上传问题
- 后端Agent：修复权限校验问题

（Claude执行）

修复完成：
```
✅ 前端：添加FormData处理图片上传
✅ 后端：修复权限中间件的逻辑
✅ 测试Agent：重新运行测试，全部通过
```

博客系统开发完成！
```

#### 协作总结

```
我：总结一下这次多Agent协作的效果？

Claude：多Agent协作成果：

**效率提升**：
- 传统方式：1人串行开发，需要5天
- 多Agent协作：3人并行开发，只需2天
- 效率提升：60%

**质量提升**：
- 专职测试Agent，测试覆盖率从60%提升到90%
- 专职协调Agent，减少前后端对接问题
- 代码质量更高

**协作优势**：
1. 并行开发，节省时间
2. 专职专责，质量更高
3. 实时协调，减少返工
4. 自动化测试，发现问题早

**适用场景**：
- 全栈项目（前端+后端+测试）
- 微服务架构（多个服务并行开发）
- 大型项目（模块化并行开发）

多Agent协作就像拥有一个小团队，但成本更低、效率更高。
```

---

## 高级调试技巧

复杂问题的定位和解决需要系统化的方法。

#### 内存泄漏排查流程

```mermaid
flowchart TD
    A[发现内存持续增长] --> B[收集系统信息]
    B --> C[启用内存分析]
    C --> D[生成堆快照]
    D --> E[对比快照分析]
    E --> F{找到泄漏点?}
    F -->|否| G[深入排查]
    G --> H[检查连接池]
    H --> I[检查缓存策略]
    I --> J[检查定时任务]
    J --> D
    F -->|是| K[定位具体代码]
    K --> L[修复代码]
    L --> M[验证修复效果]
    M --> N{内存稳定?}
    N -->|否| K
    N -->|是| O[添加监控告警]
    O --> P[预防措施]
    
    style A fill:#ffcdd2
    style P fill:#c8e6c9
    style F fill:#fff9c4
    style N fill:#fff9c4
```

### 实战案例：内存泄漏排查

**背景**：生产环境Node.js应用内存持续增长，最终OOM崩溃。

#### 问题定位

```
我：我们的Node.js应用内存持续增长，每天增长500MB，3天后就OOM崩溃。帮我排查。

Claude：内存泄漏排查需要系统化方法。我先收集信息：

**需要的信息**：
1. 应用版本和依赖
2. 内存使用趋势图
3. 最近部署记录
3. 错误日志
5. 代码变更历史

你先提供这些信息？
```

```
我：信息如下：
- Node.js版本：18.16.0
- 主要依赖：Express 4.18, MongoDB 6.3, Redis 4.6
- 内存趋势：每天增长500MB，GC后不释放
- 最近部署：3天前添加了WebSocket功能
- 错误日志：无明显错误
- 代码变更：新增了实时通知功能

Claude：根据信息，初步判断是WebSocket相关的内存泄漏。我建议：

**排查步骤**：
1. 启用Node.js内存分析
2. 使用heapdump生成堆快照
3. 对比快照找出泄漏点
4. 定位具体代码
5. 修复并验证

先启用内存分析？
```

#### 内存分析

**Claude生成内存分析代码**：
```javascript
// 启用内存分析
const v8 = require('v8');

// 定期打印内存使用情况
setInterval(() => {
  const used = process.memoryUsage();
  console.log('Memory Usage:');
  for (let key in used) {
    console.log(`${key} ${Math.round(used[key] / 1024 / 1024)}MB`);
  }
}, 60000);

// 生成堆快照
const heapdump = require('heapdump');
heapdump.writeSnapshot('/tmp/heap-' + Date.now() + '.heapsnapshot');

// 使用Chrome DevTools分析快照
// 1. 打开Chrome DevTools
// 2. Memory -> Load
// 3. 加载heapsnapshot文件
// 4. 对比不同时间点的快照
```

```
我：生成了堆快照，对比后发现WebSocket连接没有正确关闭。

Claude：找到问题了。WebSocket连接没有正确关闭，导致：
1. 连接对象累积
2. 事件监听器未移除
3. 相关闭包引用无法释放

修复方案：
```javascript
// 添加连接管理
const connections = new Map();

io.on('connection', (socket) => {
  connections.set(socket.id, socket);
  
  socket.on('disconnect', () => {
    // 清理连接
    connections.delete(socket.id);
    
    // 移除所有事件监听器
    socket.removeAllListeners();
    
    // 清理相关数据
    cleanupUserData(socket.id);
  });
});

// 定期清理僵尸连接
setInterval(() => {
  for (const [id, socket] of connections.entries()) {
    if (socket.disconnected) {
      connections.delete(id);
    }
  }
}, 300000);
```

要应用这个修复吗？
```

#### 修复验证

```
我：应用修复后，内存增长明显放缓。但还是有少量增长，继续排查？

Claude：好的，继续深入分析。我建议：

**进一步排查**：
1. 检查MongoDB连接池
2. 检查Redis连接
3. 检查定时任务
4. 检查缓存策略

先检查MongoDB连接池？
```

**Claude生成连接池检查代码**：
```javascript
// 检查MongoDB连接池
const mongoose = require('mongoose');

setInterval(() => {
  const state = mongoose.connection.readyState;
  const states = ['disconnected', 'connected', 'connecting', 'disconnecting'];
  console.log('MongoDB State:', states[state]);
  
  // 检查连接池
  if (mongoose.connection.db) {
    const pool = mongoose.connection.db.serverConfig;
    console.log('Pool Size:', pool.poolSize);
    console.log('Active Connections:', pool.s.pool.length);
  }
}, 60000);
```

```
我：检查发现MongoDB连接池配置不当，最大连接数设为100，但实际只用了10个，导致连接频繁创建销毁。

Claude：找到第二个问题了。修复方案：
```javascript
// 优化MongoDB连接池
mongoose.connect(process.env.MONGODB_URI, {
  maxPoolSize: 50, // 最大连接数
  minPoolSize: 10, // 最小连接数
  socketTimeoutMS: 45000, // socket超时
  serverSelectionTimeoutMS: 5000, // 服务器选择超时
  heartbeatFrequencyMS: 10000, // 心跳频率
});
```

应用这个修复？
```

```
我：应用后内存增长进一步放缓，基本稳定了。总结一下排查过程？

Claude：内存泄漏排查总结：

**问题定位**：
1. WebSocket连接未正确关闭（主要问题）
2. MongoDB连接池配置不当（次要问题）

**修复方案**：
1. 添加WebSocket连接管理和清理
2. 优化MongoDB连接池配置
3. 添加内存监控和告警

**预防措施**：
1. 定期生成堆快照对比
2. 设置内存使用告警阈值
3. 代码审查关注资源清理
4. 压力测试验证内存稳定性

**工具推荐**：
- heapdump：生成堆快照
- Chrome DevTools：分析快照
- clinic.js：Node.js性能分析
- node-memwatch：内存监控

内存泄漏排查需要耐心和系统化方法，找到根本原因才能彻底解决。
```

---

## 快速开始

Claude Code 是 Anthropic 推出的 AI 编程助手，通过自然语言对话帮你完成代码编写、调试、优化等任务。

### 基本使用

```bash
# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 基础对话
claude "帮我写一个快速排序算法"

# 分析特定文件
claude --file src/utils/sort.js

# 后台运行耗时任务
claude --background "运行完整测试套件"
```

---

## 实战场景

### 场景 1：快速原型开发

**需求**：2小时内完成一个产品展示页面

```bash
claude "
用 React + Tailwind CSS 创建产品展示页面：
- 响应式网格布局
- 产品卡片（图片、标题、价格、评分）
- 搜索和筛选功能
- 购物车功能
- 使用 TypeScript
"
```

**Claude 输出**：
```typescript
// ProductCard.tsx
interface Product {
  id: string;
  title: string;
  price: number;
  image: string;
  rating: number;
}

export const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow">
      <img src={product.image} alt={product.title} className="w-full h-48 object-cover" />
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2">{product.title}</h3>
        <div className="flex justify-between items-center">
          <span className="text-2xl font-bold text-blue-600">${product.price}</span>
          <div className="flex items-center">
            <span className="text-yellow-400">{'★'.repeat(Math.floor(product.rating))}</span>
            <span className="text-gray-400">{'★'.repeat(5 - Math.floor(product.rating))}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
```

**后续优化**：
```bash
claude "添加图片懒加载和加载动画"
claude "实现价格筛选和评分排序"
```

---

### 场景 2：Bug 快速修复

**问题**：用户反馈登录后页面闪白

```bash
claude "
React 应用登录后页面会闪一下才显示内容。
相关文件：
- src/hooks/useAuth.ts
- src/pages/Dashboard.tsx

帮我定位问题并提供修复方案。
"
```

**问题诊断**：
```typescript
// 问题代码
export const Dashboard = () => {
  const { user } = useAuth();
  
  // 问题：user 可能为 undefined，导致闪白
  return <h1>欢迎, {user.name}</h1>;
};

// 修复方案
export const Dashboard = () => {
  const { user, isLoading } = useAuth();
  
  if (isLoading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" />;
  
  return <h1>欢迎, {user.name}</h1>;
};
```

---

### 场景 3：API 接口开发

**需求**：开发用户管理 REST API

```bash
claude "
用 Express.js 开发用户管理 API：
- GET /api/users - 获取用户列表
- GET /api/users/:id - 获取单个用户
- POST /api/users - 创建用户
- PUT /api/users/:id - 更新用户
- DELETE /api/users/:id - 删除用户
- 使用 MongoDB + Mongoose
- 包含输入验证和错误处理
- 添加 JWT 认证中间件
"
```

**核心代码生成**：
```typescript
// users.controller.ts
export class UsersController {
  async getUsers(req: Request, res: Response) {
    try {
      const { page = 1, limit = 10, search } = req.query;
      const filter = search ? { name: { $regex: search, $options: 'i' } } : {};
      
      const users = await User.find(filter)
        .limit(Number(limit))
        .skip((Number(page) - 1) * Number(limit));
      
      res.json({
        success: true,
        data: users,
        total: await User.countDocuments(filter)
      });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  }

  async createUser(req: Request, res: Response) {
    try {
      const { name, email, password } = req.body;
      
      // 验证
      if (!name || !email || !password) {
        return res.status(400).json({ 
          success: false, 
          error: '缺少必填字段' 
        });
      }
      
      const user = new User({ name, email, password });
      await user.save();
      
      res.status(201).json({ success: true, data: user });
    } catch (error) {
      if (error.code === 11000) {
        return res.status(400).json({ 
          success: false, 
          error: '邮箱已存在' 
        });
      }
      res.status(500).json({ success: false, error: error.message });
    }
  }
}
```

---

### 场景 4：测试用例生成

**需求**：为购物车功能编写完整测试

```bash
claude "
为购物车服务生成全面的单元测试：
src/services/CartService.ts

要求：
- 覆盖所有 CRUD 操作
- 包含边界情况测试
- 性能测试（1000+ 商品）
- 使用 Jest
"
```

**测试代码**：
```typescript
// CartService.test.ts
describe('CartService', () => {
  let cartService: CartService;

  beforeEach(() => {
    cartService = new CartService();
  });

  describe('addItem', () => {
    test('应该能添加商品到空购物车', () => {
      cartService.addItem('PROD-001', 2);
      expect(cartService.getItems()).toHaveLength(1);
      expect(cartService.getItems()[0].quantity).toBe(2);
    });

    test('应该能增加已存在商品的数量', () => {
      cartService.addItem('PROD-001', 2);
      cartService.addItem('PROD-001', 3);
      expect(cartService.getItems()[0].quantity).toBe(5);
    });

    test('应该拒绝无效数量', () => {
      expect(() => cartService.addItem('PROD-001', -1))
        .toThrow('数量必须大于0');
      expect(() => cartService.addItem('PROD-001', 0))
        .toThrow('数量必须大于0');
    });
  });

  describe('calculateTotal', () => {
    test('应该正确计算总价', () => {
      cartService.addItem('PROD-001', 2, 10); // $20
      cartService.addItem('PROD-002', 1, 30); // $30
      expect(cartService.calculateTotal()).toBe(50);
    });

    test('空购物车应该返回0', () => {
      expect(cartService.calculateTotal()).toBe(0);
    });
  });

  describe('performance', () => {
    test('应该能处理大量商品', () => {
      const start = performance.now();
      
      for (let i = 0; i < 1000; i++) {
        cartService.addItem(`PROD-${i}`, 1, Math.random() * 100);
      }
      
      const end = performance.now();
      expect(end - start).toBeLessThan(100); // 100ms 内完成
    });
  });
});
```

---

### 场景 5：代码重构优化

**需求**：优化遗留代码性能

```bash
claude "
分析并优化这个函数的性能问题：

function findDuplicates(arr) {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j] && !duplicates.includes(arr[i])) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}

要求：
1. 分析时间复杂度
2. 提供优化方案
3. 对比性能差异
4. 添加类型定义
"
```

**优化结果**：
```typescript
// 原始版本：O(n²)
function findDuplicatesNaive<T>(arr: T[]): T[] {
  const duplicates: T[] = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j] && !duplicates.includes(arr[i])) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}

// 优化版本：O(n)
function findDuplicatesOptimized<T>(arr: T[]): T[] {
  const seen = new Set<T>();
  const duplicates = new Set<T>();
  
  for (const item of arr) {
    if (seen.has(item)) {
      duplicates.add(item);
    } else {
      seen.add(item);
    }
  }
  
  return Array.from(duplicates);
}

// 性能测试
const testArray = Array.from({ length: 10000 }, (_, i) => i % 1000);

console.time('Naive');
findDuplicatesNaive(testArray);
console.timeEnd('Naive'); // ~200ms

console.time('Optimized');
findDuplicatesOptimized(testArray);
console.timeEnd('Optimized'); // ~2ms
```

---

### 场景 6：全栈 Web 应用开发

**需求**：构建一个完整的任务管理系统

```bash
claude "
帮我构建一个全栈任务管理系统：

前端要求：
- React + TypeScript + Vite
- 使用 Tailwind CSS
- 包含登录/注册页面
- 任务列表（增删改查）
- 拖拽排序功能
- 实时更新

后端要求：
- Node.js + Express + TypeScript
- PostgreSQL 数据库
- JWT 认证
- Socket.io 实时通信
- RESTful API 设计

部署要求：
- Docker 容器化
- docker-compose 一键启动
- 包含环境变量配置
"
```

**项目结构生成**：
```
task-manager/
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── components/      # 组件
│   │   ├── pages/          # 页面
│   │   ├── hooks/          # 自定义 hooks
│   │   ├── services/       # API 服务
│   │   └── types/          # TypeScript 类型
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # Node.js 后端
│   ├── src/
│   │   ├── controllers/    # 控制器
│   │   ├── middleware/     # 中间件
│   │   ├── models/         # 数据模型
│   │   ├── routes/         # 路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml       # Docker 编排
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

**核心功能实现**：

```typescript
// 前端：TaskList 组件
import { useQuery, useMutation } from '@tanstack/react-query';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

export const TaskList: React.FC = () => {
  const { data: tasks, refetch } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => taskService.getTasks()
  });

  const updateTaskOrder = useMutation({
    mutationFn: taskService.updateTaskOrder,
    onSuccess: () => refetch()
  });

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;
    
    const items = Array.from(tasks || []);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    
    updateTaskOrder.mutate(items);
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <Droppable droppableId="tasks">
        {(provided) => (
          <div {...provided.droppableProps} ref={provided.innerRef}>
            {tasks?.map((task, index) => (
              <Draggable key={task.id} draggableId={task.id} index={index}>
                {(provided) => (
                  <TaskItem 
                    task={task} 
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    {...provided.dragHandleProps}
                  />
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </DragDropContext>
  );
};
```

```typescript
// 后端：Socket.io 实时更新
import { Server } from 'socket.io';
import { TaskService } from './services/TaskService';

export const initializeSocket = (httpServer: any) => {
  const io = new Server(httpServer, {
    cors: { origin: process.env.FRONTEND_URL }
  });

  io.on('connection', (socket) => {
    console.log('用户连接:', socket.id);

    socket.on('join-room', (roomId: string) => {
      socket.join(roomId);
    });

    socket.on('task-updated', async (data) => {
      await TaskService.updateTask(data.taskId, data.updates);
      
      // 广播更新给房间内所有用户
      socket.to(data.roomId).emit('task-update', {
        taskId: data.taskId,
        updates: data.updates
      });
    });
  });

  return io;
};
```

**Docker 配置**：
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/taskmanager
      JWT_SECRET: your-secret-key
    depends_on:
      - postgres
    volumes:
      - ./backend:/app
      - /app/node_modules

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

### 场景 7：移动应用开发

**需求**：跨平台任务管理 App

```bash
claude "
使用 React Native + Expo 开发移动应用：

功能要求：
- 跨平台（iOS/Android）
- 离线优先设计
- 推送通知
- 生物识别认证
- 手势操作（滑动删除、长按菜单）
- 深色模式支持

技术要求：
- Expo SDK 50+
- TypeScript
- React Navigation 6
- AsyncStorage 本地存储
- Expo Notifications
- React Query 数据管理
"
```

**核心实现**：

```typescript
// App.tsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';

const Stack = createNativeStackNavigator();
const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <NavigationContainer>
            <Stack.Navigator>
              <Stack.Screen name="Login" component={LoginScreen} />
              <Stack.Screen name="Tasks" component={TaskListScreen} />
              <Stack.Screen name="TaskDetail" component={TaskDetailScreen} />
            </Stack.Navigator>
          </NavigationContainer>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
```

```typescript
// 离线优先的数据同步
import { useQuery, useMutation } from '@tanstack/react-query';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

export const useOfflineTasks = () => {
  const { data: onlineTasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: taskService.getTasks,
    enabled: false // 默认禁用，根据网络状态启用
  });

  const syncTasks = async () => {
    const netInfo = await NetInfo.fetch();
    if (netInfo.isConnected) {
      // 在线时同步数据
      const offlineTasks = await AsyncStorage.getItem('offlineTasks');
      if (offlineTasks) {
        await taskService.syncTasks(JSON.parse(offlineTasks));
        await AsyncStorage.removeItem('offlineTasks');
      }
    }
  };

  const createTaskOffline = useMutation({
    mutationFn: async (task: Task) => {
      const netInfo = await NetInfo.fetch();
      
      if (netInfo.isConnected) {
        return taskService.createTask(task);
      } else {
        // 离线时存储到本地
        const existingTasks = await AsyncStorage.getItem('offlineTasks');
        const tasks = existingTasks ? JSON.parse(existingTasks) : [];
        tasks.push({ ...task, id: Date.now().toString(), pending: true });
        await AsyncStorage.setItem('offlineTasks', JSON.stringify(tasks));
        return task;
      }
    },
    onSuccess: () => syncTasks()
  });

  return { createTaskOffline };
};
```

---

### 场景 8：微服务架构设计

**需求**：设计可扩展的电商系统

```bash
claude "
设计微服务架构的电商系统：

服务拆分：
- 用户服务（注册、登录、个人信息）
- 商品服务（商品管理、库存、分类）
- 订单服务（订单创建、状态管理）
- 支付服务（支付处理、退款）
- 通知服务（邮件、短信、推送）

技术要求：
- Node.js + NestJS 框架
- Docker + Kubernetes 部署
- Redis 缓存
- RabbitMQ 消息队列
- PostgreSQL 数据库
- API Gateway 统一入口
- 分布式追踪（Jaeger）
- 服务发现（Consul）
"
```

**架构设计**：

#### 微服务架构图

```mermaid
graph TB
    subgraph "客户端层"
        A[Web前端]
        B[移动App]
    end
    
    subgraph "API Gateway"
        C[API Gateway]
        C1[认证]
        C2[路由]
        C3[限流]
    end
    
    subgraph "微服务层"
        D[用户服务]
        E[商品服务]
        F[订单服务]
        G[支付服务]
        H[通知服务]
    end
    
    subgraph "消息队列"
        I[RabbitMQ]
    end
    
    subgraph "数据层"
        J[PostgreSQL集群]
        K[Redis缓存]
        L[Elasticsearch]
    end
    
    subgraph "基础设施"
        M[Consul服务发现]
        N[Jaeger追踪]
        O[Prometheus监控]
    end
    
    A --> C
    B --> C
    C --> C1
    C1 --> C2
    C2 --> C3
    C3 --> D
    C3 --> E
    C3 --> F
    C3 --> G
    C3 --> H
    
    D --> J
    E --> J
    F --> J
    D --> K
    E --> K
    F --> K
    E --> L
    
    F --> I
    G --> I
    H --> I
    I --> F
    I --> H
    
    D -.-> M
    E -.-> M
    F -.-> M
    G -.-> M
    H -.-> M
    
    D -.-> N
    E -.-> N
    F -.-> N
    G -.-> N
    H -.-> N
    
    D -.-> O
    E -.-> O
    F -.-> O
    G -.-> O
    H -.-> O
    
    style C fill:#e1f5ff
    style I fill:#fff9c4
    style J fill:#c8e6c9
```

```typescript
// API Gateway 配置
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import * as proxy from 'express-http-proxy';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // 全局验证管道
  app.useGlobalPipes(new ValidationPipe());
  
  // Swagger 文档
  const config = new DocumentBuilder()
    .setTitle('E-commerce API Gateway')
    .setVersion('1.0')
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);
  
  // 微服务代理
  app.use('/api/users', proxy('http://user-service:3001'));
  app.use('/api/products', proxy('http://product-service:3002'));
  app.use('/api/orders', proxy('http://order-service:3003'));
  app.use('/api/payments', proxy('http://payment-service:3004'));
  
  await app.listen(3000);
}
```

```typescript
// 分布式事件处理
import { Controller } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import { OrderService } from './order.service';

@Controller()
export class OrderController {
  constructor(private readonly orderService: OrderService) {}

  @EventPattern('order_created')
  async handleOrderCreated(@Payload() data: any) {
    // 处理订单创建事件
    await this.orderService.processOrder(data);
    
    // 发布库存扣减事件
    await this.orderService.publishEvent('inventory_reserved', {
      productId: data.productId,
      quantity: data.quantity,
      orderId: data.orderId
    });
  }

  @EventPattern('payment_completed')
  async handlePaymentCompleted(@Payload() data: any) {
    // 支付完成，更新订单状态
    await this.orderService.updateOrderStatus(data.orderId, 'PAID');
    
    // 发布发货通知事件
    await this.orderService.publishEvent('order_shipped', {
      orderId: data.orderId,
      userId: data.userId
    });
  }
}
```

**Kubernetes 部署**：
```yaml
# k8s/user-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:latest
        ports:
        - containerPort: 3001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - port: 3001
    targetPort: 3001
```

---

### 场景 9：AI 驱动的智能系统

**需求**：构建智能客服系统

```bash
claude "
构建 AI 智能客服系统：

核心功能：
- 自然语言理解（NLU）
- 意图识别和实体提取
- 多轮对话管理
- 知识库检索
- 情感分析
- 智能路由

技术栈：
- Python + FastAPI
- LangChain 框架
- OpenAI/Claude API
- Elasticsearch 搜索
- Redis 会话存储
- WebSocket 实时通信
- React 前端界面
"
```

**智能对话引擎**：

```python
# conversation_engine.py
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import ElasticsearchStore
from typing import Dict, List

class ConversationEngine:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = ElasticsearchStore(
            es_url="http://localhost:9200",
            index_name="knowledge_base",
            embedding=self.embeddings
        )
        self.memory = ConversationBufferWindowMemory(
            k=5, 
            return_messages=True,
            memory_key="chat_history"
        )
        
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model="gpt-4"),
            retriever=self.vectorstore.as_retriever(),
            memory=self.memory,
            verbose=True
        )
    
    async def process_message(self, 
                             user_id: str, 
                             message: str) -> Dict[str, any]:
        # 意图识别
        intent = await self.detect_intent(message)
        
        # 情感分析
        sentiment = await self.analyze_sentiment(message)
        
        # 生成回复
        if intent == "complaint":
            response = await self.handle_complaint(message)
        elif intent == "inquiry":
            response = await self.chain({"question": message})
            response = response["answer"]
        else:
            response = await self.generate_general_response(message)
        
        # 保存对话历史
        await self.save_conversation(user_id, message, response)
        
        return {
            "response": response,
            "intent": intent,
            "sentiment": sentiment,
            "confidence": 0.85
        }
    
    async def detect_intent(self, message: str) -> str:
        # 使用分类模型识别意图
        intents = {
            "complaint": ["投诉", "不满", "问题", "错误"],
            "inquiry": ["查询", "怎么", "如何", "什么"],
            "greeting": ["你好", "您好", "早上好"],
            "farewell": ["再见", "谢谢", "感谢"]
        }
        
        for intent, keywords in intents.items():
            if any(keyword in message for keyword in keywords):
                return intent
        
        return "general"
```

**实时 WebSocket 通信**：

```python
# websocket_handler.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import redis

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # 加载历史对话
        history = self.redis_client.get(f"chat_history:{user_id}")
        if history:
            await websocket.send_text(json.dumps({
                "type": "history",
                "data": json.loads(history)
            }))
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    engine = ConversationEngine()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "message":
                response = await engine.process_message(
                    user_id, 
                    message["content"]
                )
                
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "data": response
                }))
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
```

---

### 场景 10：DevOps 自动化平台

**需求**：构建 CI/CD 自动化平台

```bash
claude "
构建 DevOps 自动化平台：

功能模块：
- Git 仓库管理集成
- 自动化构建和测试
- 容器镜像管理
- 部署流水线设计
- 监控和告警系统
- 日志聚合和分析

技术实现：
- Node.js + Express 后端
- React + TypeScript 前端
- Docker 容器化
- GitHub Actions CI/CD
- Prometheus + Grafana 监控
- ELK Stack 日志处理
- Kubernetes 部署
"
```

**CI/CD 流水线配置**：

#### CI/CD流水线流程图

```mermaid
flowchart TB
    subgraph "代码提交"
        A[Git Push]
        B[Pull Request]
    end
    
    subgraph "测试阶段"
        C[单元测试]
        D[E2E测试]
        E[代码覆盖率]
    end
    
    subgraph "构建阶段"
        F[Docker构建]
        G[镜像推送]
    end
    
    subgraph "部署阶段"
        H[Staging部署]
        I[人工验证]
        J[生产部署]
    end
    
    subgraph "监控阶段"
        K[健康检查]
        L[性能监控]
        M[告警通知]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
    
    style A fill:#e1f5ff
    style J fill:#c8e6c9
    style M fill:#ffcdd2
```

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker tag myapp:${{ github.sha }} myapp:latest
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push myapp:${{ github.sha }}
          docker push myapp:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: |
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig
          
          # 更新镜像版本
          sed -i "s/myapp:latest/myapp:${{ github.sha }}/g" k8s/deployment.yaml
          
          # 应用更新
          kubectl apply -f k8s/
          
          # 等待部署完成
          kubectl rollout status deployment/myapp
```

**监控和告警系统**：

```typescript
// monitoring-service.ts
import express from 'express';
import prometheus from 'prom-client';
import { logger } from './utils/logger';

// 创建指标
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

const httpRequestTotal = new prometheus.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new prometheus.Gauge({
  name: 'websocket_connections_active',
  help: 'Number of active WebSocket connections'
});

// 中间件：收集指标
export const metricsMiddleware = (req: express.Request, res: express.Response, next: express.NextFunction) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route?.path || req.path;
    
    httpRequestDuration
      .labels(req.method, route, res.statusCode.toString())
      .observe(duration);
    
    httpRequestTotal
      .labels(req.method, route, res.statusCode.toString())
      .inc();
  });
  
  next();
};

// 告警规则
export const checkAlerts = async () => {
  const metrics = await prometheus.register.getMetricsAsJSON();
  
  // 检查错误率
  const errorRate = calculateErrorRate(metrics);
  if (errorRate > 0.05) { // 5% 错误率阈值
    await sendAlert({
      level: 'critical',
      message: `错误率过高: ${(errorRate * 100).toFixed(2)}%`,
      metric: 'error_rate',
      value: errorRate
    });
  }
  
  // 检查响应时间
  const avgResponseTime = calculateAvgResponseTime(metrics);
  if (avgResponseTime > 1000) { // 1秒阈值
    await sendAlert({
      level: 'warning',
      message: `平均响应时间过长: ${avgResponseTime}ms`,
      metric: 'response_time',
      value: avgResponseTime
    });
  }
};

// 告警发送
const sendAlert = async (alert: Alert) => {
  // 发送到 Slack
  await fetch(process.env.SLACK_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: `🚨 ${alert.level.toUpperCase()}: ${alert.message}`,
      attachments: [{
        color: alert.level === 'critical' ? 'danger' : 'warning',
        fields: [
          { title: '指标', value: alert.metric },
          { title: '当前值', value: alert.value.toString() }
        ]
      }]
    })
  });
  
  // 记录日志
  logger.warn('Alert triggered', alert);
};
```

---

## 高效工作流

### 1. 渐进式开发

```bash
# 步骤 1：定义接口
claude "设计用户管理 API 的接口规范"

# 步骤 2：实现核心逻辑
claude "基于刚才的接口规范实现后端服务"

# 步骤 3：添加测试
claude "为用户管理 API 编写单元测试"

# 步骤 4：生成文档
claude "生成 API 文档，包含示例代码"
```

### 2. 错误处理工作流

```bash
# 步骤 1：复现错误
claude "这个 API 返回 500 错误，帮我分析日志"

# 步骤 2：定位问题
claude "根据错误信息，定位可能的问题原因"

# 步骤 3：修复方案
claude "提供具体的修复代码"

# 步骤 4：预防措施
claude "添加监控和告警，防止类似问题"
```

### 4. Plan 模式工作流

先规划后执行，避免返工：

```bash
# 进入 Plan 模式（按两次 Shift+Tab）
# 详细描述需求，让 Claude 制定方案

# 方案确认后，切换回执行模式
# 使用 Auto-accept 一次性完成
```

### 5. 多 Agent 协作

复杂任务分而治之：

```bash
# 终端 1：前端 Agent
claude --session frontend "实现 React 组件"

# 终端 2：后端 Agent  
claude --session backend "开发 API 接口"

# 终端 3：测试 Agent
claude --session testing "编写测试用例"

# 主终端：协调 Agent
claude "整合前后端，确保接口对接正确"
```

---

## 实用技巧

### 1. 精准提问

**不好**：
```bash
claude "优化这个函数"
```

**好**：
```bash
claude "
优化这个函数的时间复杂度：
function processData(data) {
  return data.map(item => 
    data.find(d => d.id === item.parentId)
  );
}

当前是 O(n²)，需要优化到 O(n)
"
```

### 2. 提供上下文

**不好**：
```bash
claude "修复登录 bug"
```

**好**：
```bash
claude "
修复登录 bug：
- 使用 React + TypeScript
- 认证库：@auth0/react-auth0
- 错误信息：'Cannot read property of undefined'
- 相关文件：src/components/Login.tsx
"
```

### 3. 分步骤处理复杂任务

```bash
# 第一步：理解需求
claude "分析这个需求的技术要点：..."

# 第二步：设计方案
claude "基于刚才的分析，设计技术方案"

# 第三步：实现代码
claude "按照设计方案实现核心功能"

# 第四步：测试验证
claude "编写测试用例验证功能"
```

### 4. 使用 CLAUDE.md 配置项目

在项目根目录创建 CLAUDE.md：

```markdown
# 项目：电商系统

## 技术栈
- 前端：React 18 + TypeScript + Tailwind CSS
- 后端：Node.js + Express + MongoDB
- 部署：Docker + AWS

## 编码规范
- 使用 ESLint + Prettier
- 组件用 PascalCase
- 文件名用 kebab-case
- 提交信息遵循 Conventional Commits

## 项目结构
```
src/
  components/    # React 组件
  pages/         # 页面组件
  hooks/         # 自定义 hooks
  services/      # API 服务
  utils/         # 工具函数
  types/         # TypeScript 类型
```

## 测试策略
- 单元测试：Jest + React Testing Library
- E2E 测试：Playwright
- 测试覆盖率要求：80%+

## 部署流程
1. 推送到 main 分支触发 CI/CD
2. 自动运行测试和构建
3. 部署到 staging 环境
4. 人工验证后部署到生产
```

---

## 常见问题

### Q: Claude Code 生成的代码可靠吗？

A: Claude Code 生成的代码质量很高，但仍需要人工审查。建议：
- 重要功能一定要写测试
- 关注安全性和性能
- 逐步集成，不要一次性替换大量代码

### Q: 如何让 Claude Code 理解项目结构？

A: 提供项目上下文：
```bash
claude "
我的项目结构：
src/
  components/    # React 组件
  services/      # API 服务
  utils/         # 工具函数
  types/         # TypeScript 类型定义

技术栈：React 18 + TypeScript + Tailwind CSS
"
```

### Q: 如何处理大型项目？

A: 分模块处理：
```bash
# 先处理核心模块
claude "实现用户认证模块"

# 再处理业务模块
claude "基于认证模块实现订单系统"

# 最后集成测试
claude "编写端到端测试"
```

---

## 最佳实践

1. **明确需求**：详细描述功能需求和技术约束
2. **提供上下文**：说明项目结构、技术栈、业务背景
3. **分步进行**：复杂任务拆分为多个小步骤
4. **及时验证**：每步完成后进行测试和验证
5. **持续优化**：基于反馈不断改进代码质量

---

## 进阶使用

### 自定义工作流

创建可重复的开发流程：

```bash
# 保存常用提示词
claude --save "api-development" "
开发 REST API：
1. 设计数据模型
2. 实现控制器
3. 添加验证中间件
4. 编写单元测试
5. 生成 API 文档
"

# 使用保存的工作流
claude --load "api-development" "用户管理模块"
```

### 多文件协作

```bash
# 同时分析多个相关文件
claude --file src/auth/service.ts --file src/auth/middleware.ts "
分析认证系统的完整流程，找出潜在问题
"
```

---

## 总结

Claude Code 是强大的编程助手，关键在于：

- **精准提问**：明确需求，提供充分上下文
- **渐进开发**：分步骤处理复杂任务
- **质量把控**：人工审查 + 自动化测试
- **持续学习**：积累项目特定的最佳实践

通过合理使用 Claude Code，可以显著提升开发效率，让开发者更专注于业务逻辑和架构设计。

---

## 相关资源

- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)
- [Claude Code 快速入门（本仓库 claude-code-guide）](https://github.com/microwind/ai-skills/blob/main/docs/claude/claude-code-guide/01-快速入门.md)
- [Claude Code 完整学习系列（本仓库索引）](https://github.com/microwind/ai-skills/blob/main/docs/claude/claude-code-guide/README.md)
- [AI 编程核心知识库](https://microwind.github.io)
- [Claude Code Skills 推荐（本仓库）](https://github.com/microwind/ai-skills/blob/main/docs/skills/Claude-Code-10大Skills推荐.md)
- [51万行代码分析报告（附录 · 本仓库）](https://github.com/microwind/ai-skills/blob/main/docs/claude/claude-code-guide/附录-最佳实践.md)
- [Claude Code AI 编程完全指南（本仓库长文）](https://github.com/microwind/ai-skills/blob/main/docs/claude/ClaudeCodeAI编程完全指南.md)
