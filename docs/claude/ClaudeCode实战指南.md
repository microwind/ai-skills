# ⚠️ 本文已重组为完整系列指南

## 📖 请访问新的 Claude Code 使用大全

👉 **[Claude Code 完整学习系列](./claude-code-guide/README.md)**

原有的长文章已经被重新组织为一套完整、循序渐进的系列，包含：

- **快速入门** - 5 分钟了解 Claude Code
- **常用技巧** - 11 个高效编程技巧
- **命令速查** - 快速参考
- **5 个实战例子** - 算法、前端、调试、文档、测试
- **工作流方法** - 从简单到复杂的工作流
- **2 个完整项目** - Java Spring Boot & Go Gin 实现
- **最佳实践** - 企业级规范和常见陷阱

### 快速导航

| 你的情况 | 推荐路径 |
|---------|---------|
| 初学者 | [快速入门](./claude-code-guide/01-快速入门.md) → [常用技巧](./claude-code-guide/02-常用技巧.md) |
| 想看代码 | [实战例子](./claude-code-guide/04-实战例子/) |
| 学习具体技术 | [Java 项目](./claude-code-guide/06-项目实战/01-Java登录系统.md) 或 [Go 项目](./claude-code-guide/06-项目实战/02-Go登录系统.md) |
| 想快速查询 | [命令速查](./claude-code-guide/03-命令速查.md) |

---

## 原始内容（已过时 - 保留用于备份）

以下内容已整合到新系列中。

---

## 第一部分：Claude Code 常用技巧（10+ 条）

### 1. 善用「上下文感知」进行多轮对话

**技巧核心**：Claude Code 记住整个对话历史，你不需要重复背景信息。

```bash
# 第一次提问
$ claude code "分析这个函数的性能"
# Claude 记住了你的项目上下文

# 后续提问直接迭代
$ "现在优化它"
# Claude 知道你说的是哪个函数
```

**实战场景**：调试一个复杂 Bug 时，你可以逐步引导 Claude 深入代码，每次只关注一个问题点，而不是一次性描述整个场景。

---

### 2. 利用 `/tasks` 命令管理后台任务

Claude Code 支持在后台运行长时任务，不阻塞你的命令行。

```bash
# 启动一个耗时的构建任务
$ claude --background "构建整个项目"

# 查看所有后台任务
$ /tasks

# 获取某个任务的结果
$ /tasks <task-id>
```

**实战优势**：在编写代码时，同时运行测试套件，充分利用系统资源。

---

### 3. 精准使用「文件定位」减少噪音

告诉 Claude 要修改哪个文件，而不是让它搜索整个项目。

```bash
$ claude "修复 src/auth/login.ts 中的验证逻辑"
# 比这个好：
$ claude "修复登录验证逻辑"  # 可能会搜索整个项目
```

**为什么有效**：减少 Claude 需要理解的代码量，更快找到问题。

---

### 4. 使用 Markdown 代码块指定编程语言

清晰的语言标记让 Claude 提供更精准的建议。

```
我的 React 代码：
\`\`\`typescript
// 你的代码
\`\`\`

我需要转换为 Vue，怎么做？
```

Claude 会更准确地理解代码意图，提供对应语言的最佳实践。

---

### 5. 利用「分支思维」处理复杂决策

遇到多个实现方案时，先让 Claude 列出选项，再深入某个方案。

```bash
$ claude "在我的项目中实现缓存，有什么方案？"
# Claude 列出：Redis、内存缓存、数据库缓存等

$ "我选择 Redis，具体怎么集成到 Node.js 项目？"
# Claude 针对该选择深入讲解
```

**效果**：避免一开始就陷入实现细节，先从全局思考。

---

### 6. 使用 `--resume` 恢复之前的会话

```bash
# 查看会话 ID
$ /sessions

# 恢复某个会话
$ claude --resume <session-id> "继续之前的工作"
```

**场景应用**：处理跨越多天的大型项目，不需要重新解释整个背景。

---

### 7. 让 Claude 生成「测试优先」的代码

先要求 Claude 写测试，再写实现代码。

```bash
$ claude "为用户注册功能写单元测试，使用 Jest"
# Claude 生成测试文件

$ "现在实现这些测试"
# 实现代码会更符合需求
```

**好处**：确保代码质量，同时测试也作为文档。

---

### 8. 精用「对比式」提问找出最佳实践

```bash
$ claude "
对比以下两种错误处理方式的优缺点：
1. try-catch 包装一切
2. Result<T, E> 类型模式
在我的 TypeScript 项目中哪个更好？
"
```

Claude 会给出考虑你项目特点的建议。

---

### 9. 利用代码片段快速定位

使用 `file_path:line_number` 格式快速指向代码位置。

```bash
$ claude "
src/api/handler.ts:45 这里的错误处理有问题，
应该返回更详细的错误信息
"
```

Claude 能立即理解你指的确切位置。

---

### 10. 使用「渐进式精化」优化代码

不要一次性要求「优化整个函数」，而是逐步改进。

```bash
$ claude "这个函数的时间复杂度是多少？"
# Claude 分析后告诉你

$ "优化到 O(n) 怎么做？"
# 针对性的优化建议

$ "现在加上错误处理"
# 在已优化的基础上继续
```

**优势**：避免优化引入新 Bug，每步都可验证。

---

### 11. 善用「约束条件」获得更好的代码

明确指定约束，让 Claude 生成更实用的代码。

```bash
$ claude "
写一个 JSON 解析函数：
- 必须处理格式错误
- 性能要超过 JSON.parse 的 80%
- 代码不超过 50 行
"
```

具体约束能引导 Claude 生成最优解决方案。

---

## 第二部分：Claude Code 主要命令介绍

### 核心命令速查表

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `claude [prompt]` | 基础对话 | 日常编程问题咨询 |
| `claude --file [path]` | 分析特定文件 | 理解复杂模块 |
| `claude --diff` | 显示变更对比 | 代码审查 |
| `claude --background` | 后台运行任务 | 耗时操作（测试、构建） |
| `/help` | 帮助文档 | 查看所有命令 |
| `/tasks` | 查看后台任务 | 管理并发作业 |
| `/sessions` | 查看会话列表 | 恢复之前的工作 |
| `--resume [id]` | 恢复会话 | 继续长期项目 |

### 实用命令组合

**快速代码审查流程**：
```bash
$ claude --file src/payment.ts
# 分析支付模块

$ "检查是否有安全漏洞"
# Claude 审视代码安全性

$ /help
# 查看有什么其他功能可用
```

**Bug 诊断工作流**：
```bash
$ claude "为什么这个 API 返回 500 错误？"
$ "日志里有什么线索？"  # 上传日志
$ "这个错误怎么快速修复？"
$ "写个单元测试防止回归"
```

---

## 第三部分：Claude Code 实战例子（5 个）

### 例子 1：快速实现排序算法（体现代码生成+优化）

**场景**：在面试前快速复习快速排序，并理解时间复杂度。

```bash
$ claude "
用 TypeScript 实现快速排序，包括：
1. 基础实现
2. 性能优化（三路分割）
3. 单元测试
4. 时间复杂度分析
"
```

Claude 会生成：
```typescript
// 基础快速排序
function quickSort(arr: number[], left = 0, right = arr.length - 1): number[] {
  if (left >= right) return arr;

  const pivot = partition(arr, left, right);
  quickSort(arr, left, pivot - 1);
  quickSort(arr, pivot + 1, right);
  return arr;
}

// 优化版本（三路分割）
function quickSortOptimized(arr: number[], left = 0, right = arr.length - 1): number[] {
  if (left >= right) return arr;

  let lt = left;
  let gt = right;
  let i = left + 1;
  const pivot = arr[left];

  while (i <= gt) {
    if (arr[i] < pivot) {
      [arr[lt++], arr[i++]] = [arr[i], arr[lt]];
    } else if (arr[i] > pivot) {
      [arr[i], arr[gt--]] = [arr[gt], arr[i]];
    } else {
      i++;
    }
  }

  quickSort(arr, left, lt - 1);
  quickSort(arr, gt + 1, right);
  return arr;
}

// 单元测试
describe('Quick Sort', () => {
  test('handles empty array', () => {
    expect(quickSort([])).toEqual([]);
  });

  test('sorts single element', () => {
    expect(quickSort([1])).toEqual([1]);
  });

  test('sorts duplicates correctly', () => {
    expect(quickSort([3, 1, 3, 2, 1])).toEqual([1, 1, 2, 3, 3]);
  });
});
```

**关键对话**：
```bash
$ "为什么三路分割比标准快速排序更快？"
# Claude 解释处理重复元素的优势

$ "最坏情况下时间复杂度是多少？怎么避免？"
# Claude 讲解随机化枢纽的重要性
```

**收获**：不仅得到代码，还深刻理解了算法。

---

### 例子 2：设计现代响应式页面（体现前端最佳实践）

**场景**：快速原型化一个产品卡片组件，从设计到实现。

```bash
$ claude "
用 React + Tailwind CSS 设计一个产品卡片组件：
- 展示产品图片、标题、价格、评分
- 响应式设计（手机/平板/桌面）
- 悬停动画效果
- 可以添加到购物车
"
```

Claude 生成的组件：
```typescript
// ProductCard.tsx
import React, { useState } from 'react';
import { ShoppingCart, Star } from 'lucide-react';

interface Product {
  id: string;
  title: string;
  price: number;
  image: string;
  rating: number;
  reviews: number;
}

export const ProductCard: React.FC<{ product: Product; onAddCart: (id: string) => void }> = ({
  product,
  onAddCart,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-xl transform hover:scale-105"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 图片容器 */}
      <div className="relative w-full h-48 sm:h-64 md:h-72 bg-gray-200 overflow-hidden">
        <img
          src={product.image}
          alt={product.title}
          className={`w-full h-full object-cover transition-transform duration-500 ${
            isHovered ? 'scale-110' : 'scale-100'
          }`}
        />
      </div>

      {/* 内容区域 */}
      <div className="p-4 sm:p-6">
        {/* 标题 */}
        <h3 className="text-lg sm:text-xl font-semibold text-gray-800 line-clamp-2 mb-2">
          {product.title}
        </h3>

        {/* 评分 */}
        <div className="flex items-center gap-2 mb-3">
          <div className="flex items-center">
            {Array(5)
              .fill(0)
              .map((_, i) => (
                <Star
                  key={i}
                  size={16}
                  className={i < Math.floor(product.rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
                />
              ))}
          </div>
          <span className="text-sm text-gray-600">({product.reviews})</span>
        </div>

        {/* 价格和按钮 */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <div>
            <p className="text-2xl font-bold text-blue-600">${product.price.toFixed(2)}</p>
          </div>
          <button
            onClick={() => onAddCart(product.id)}
            className="bg-blue-600 hover:bg-blue-700 text-white p-2 sm:p-3 rounded-lg transition-colors flex items-center gap-2"
          >
            <ShoppingCart size={20} />
            <span className="hidden sm:inline">加购</span>
          </button>
        </div>
      </div>
    </div>
  );
};
```

**响应式布局容器**：
```typescript
// ProductGrid.tsx
export const ProductGrid: React.FC<{ products: Product[] }> = ({ products }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6 p-4 md:p-8">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} onAddCart={handleAddCart} />
      ))}
    </div>
  );
};
```

**交互对话**：
```bash
$ "移动端看起来文字太小，怎么优化？"
# Claude 建议使用 Tailwind 的响应式文字大小

$ "如何实现图片懒加载？"
# Claude 添加 next/image 或 Intersection Observer

$ "加个「收藏」功能，用心形图标"
# 动态更新组件
```

**收获**：学到现代前端的响应式设计思路和 Tailwind 实战技巧。

---

### 例子 3：快速定位和修复 Bug（体现调试工作流）

**场景**：用户反馈登录后页面闪屏，需要快速定位。

```bash
$ claude "
我的 React 应用登录后页面会闪一下才显示内容。
这是 src/hooks/useAuth.ts 和 src/pages/Dashboard.tsx

[上传两个文件]

为什么会这样？怎么修复？
"
```

Claude 分析并指出：
```typescript
// 问题代码
export const Dashboard = () => {
  const { user } = useAuth();

  // 这里问题：如果 user 还在加载，会返回 null
  return (
    <div>
      <h1>欢迎, {user.name}</h1>
      {/* 内容 */}
    </div>
  );
};

// 修复方案
export const Dashboard = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <Redirect to="/login" />;
  }

  return (
    <div>
      <h1>欢迎, {user.name}</h1>
      {/* 内容 */}
    </div>
  );
};
```

**进一步优化**：
```bash
$ "能不能用 Suspense 让体验更流畅？"
# Claude 重构为 Suspense + lazy loading 模式

$ "写个测试确保登录流程没问题"
# Claude 生成端到端测试
```

**收获**：学到 React 生命周期管理和常见陷阱。

---

### 例子 4：生成高质量设计文档（体现文档生成能力）

**场景**：新加入的开发者需要了解认证系统，快速生成设计文档。

```bash
$ claude "
基于这些文件生成一份认证系统的设计文档：
- src/auth/middleware.ts
- src/auth/jwt.ts
- src/auth/service.ts
- src/models/User.ts

文档应包括：
1. 系统架构图（用 mermaid）
2. 认证流程（序列图）
3. 关键数据结构
4. 安全注意事项
5. 集成指南
"
```

Claude 生成的文档片段：

```markdown
## 认证系统设计文档

### 系统架构

\`\`\`mermaid
graph TB
  Client[客户端]
  API[API 网关]
  Auth[认证服务]
  DB[(数据库)]
  Cache[(缓存)]

  Client -->|登录| API
  API -->|验证| Auth
  Auth -->|查询| DB
  Auth -->|缓存| Cache
\`\`\`

### 认证流程

\`\`\`mermaid
sequenceDiagram
  User->>Client: 输入用户名密码
  Client->>API: POST /login
  API->>Auth: validateCredentials()
  Auth->>DB: 查询用户
  Auth->>Cache: 缓存 JWT
  Auth-->>API: 返回 token
  API-->>Client: 登录成功
  Client->>Client: 保存 token
  Client->>API: 请求 (Header: Authorization)
\`\`\`

### 安全注意事项

| 项目 | 措施 |
|------|------|
| 密码存储 | bcrypt + salt |
| Token 过期 | 15 分钟刷新，7 天长期 |
| CSRF 保护 | SameSite Cookie |
| 速率限制 | 5 次失败后锁定 10 分钟 |
```

**与 Claude 的对话**：
```bash
$ "能用 Swagger 格式添加 API 文档吗？"
# Claude 生成完整的 OpenAPI 规范

$ "为新人添加一个「常见问题」部分"
# 自动补充
```

**收获**：自动化文档生成，保持文档与代码同步。

---

### 例子 5：批量生成测试用例（体现测试驱动开发）

**场景**：要给购物车模块补充完整的单元测试。

```bash
$ claude "
为这个购物车模块生成全面的单元测试：
src/cart/CartService.ts

要求：
- 覆盖所有公开方法
- 包括边界情况和错误处理
- 使用 Jest + Vitest
- 包括性能测试
"
```

Claude 生成的测试套件：

```typescript
// CartService.test.ts
import { CartService } from './CartService';

describe('CartService', () => {
  let cart: CartService;

  beforeEach(() => {
    cart = new CartService();
  });

  describe('addItem', () => {
    test('should add item to empty cart', () => {
      cart.addItem('PROD-1', 1);
      expect(cart.getItems()).toHaveLength(1);
    });

    test('should increment quantity if item exists', () => {
      cart.addItem('PROD-1', 1);
      cart.addItem('PROD-1', 2);
      const items = cart.getItems();
      expect(items[0].quantity).toBe(3);
    });

    test('should throw error if quantity is invalid', () => {
      expect(() => cart.addItem('PROD-1', -1)).toThrow('数量必须大于 0');
      expect(() => cart.addItem('PROD-1', 0)).toThrow('数量必须大于 0');
    });

    test('should handle max quantity limit', () => {
      cart.addItem('PROD-1', 999);
      expect(() => cart.addItem('PROD-1', 1)).toThrow('超过最大购买量');
    });
  });

  describe('removeItem', () => {
    test('should remove item from cart', () => {
      cart.addItem('PROD-1', 1);
      cart.removeItem('PROD-1');
      expect(cart.getItems()).toHaveLength(0);
    });

    test('should throw error if item not found', () => {
      expect(() => cart.removeItem('NONEXISTENT')).toThrow('商品不存在');
    });
  });

  describe('calculateTotal', () => {
    test('should calculate correct total with multiple items', () => {
      cart.addItem('PROD-1', 2); // $10 each
      cart.addItem('PROD-2', 1); // $20
      // 总计应该是 $40
      expect(cart.calculateTotal()).toBe(40);
    });

    test('should apply discount correctly', () => {
      cart.addItem('PROD-1', 2);
      cart.applyDiscount(0.1); // 10% 折扣
      expect(cart.calculateTotal()).toBe(18); // $20 * 0.9
    });

    test('should handle empty cart', () => {
      expect(cart.calculateTotal()).toBe(0);
    });
  });

  describe('performance', () => {
    test('should handle large number of items efficiently', () => {
      const start = performance.now();
      for (let i = 0; i < 1000; i++) {
        cart.addItem(`PROD-${i}`, 1);
      }
      const end = performance.now();
      expect(end - start).toBeLessThan(100); // 应该在 100ms 内完成
    });
  });
});
```

**扩展对话**：
```bash
$ "生成集成测试，覆盖购物车到支付的完整流程"
# Claude 生成 E2E 测试

$ "添加性能基准测试"
# 自动添加性能监测

$ "生成测试覆盖率报告"
# Claude 配置 Istanbul 并生成报告
```

**收获**：理解 TDD 的重要性，学会系统地编写可靠的测试。

---

## 第四部分：Claude Code 工作流使用方式

### 工作流是什么

工作流是 Claude Code 的核心生产力特性，让你能定义可重复的、多步骤的 AI 任务流程。

### 基本工作流结构

一个工作流包括：
1. **输入**：用户提供的初始信息
2. **处理步骤**：一系列 AI 处理阶段
3. **输出**：最终的可交付成果

### 创建工作流的三个级别

#### 级别 1：快速工作流（Bash 中的多步骤）

最简单的工作流：在一个命令中链接多个操作。

```bash
# 典型工作流：代码审查
$ claude "
分析这个函数：
src/payment/process.ts

然后：
1. 检查是否有性能问题
2. 检查是否有安全漏洞
3. 建议如何改进
4. 给出重构代码
"
```

Claude 会自动分多个步骤执行，每步建立在前一步的基础上。

#### 级别 2：有状态工作流（使用 `--resume`）

对于跨越多个会话的长期项目。

```bash
# 会话 1：创建基础架构
$ claude "设计一个电商平台的数据库结构"
# 记下会话 ID

# 会话 2：实现后端
$ claude --resume <session-id> "现在基于这个数据库设计实现后端 API"

# 会话 3：添加测试
$ claude --resume <session-id> "为这些 API 写单元测试"
```

**优势**：Claude 始终知道整个项目的背景，建议更连贯。

#### 级别 3：完整工作流定义（声明式）

对于团队内可复用的标准流程。

```yaml
# auth-workflow.yaml
name: "User Authentication System"
description: "完整的用户认证系统实现"

inputs:
  framework:
    type: choice
    options: ["Express", "NestJS", "Django", "Go"]
    description: "选择后端框架"

  database:
    type: choice
    options: ["PostgreSQL", "MongoDB", "MySQL"]
    description: "选择数据库"

steps:
  - name: "Design"
    prompt: |
      设计 {framework} + {database} 的认证系统
      要求：
      - JWT token 管理
      - 密码安全存储
      - 刷新 token 机制
      - OAuth 支持

  - name: "Implementation"
    prompt: |
      基于上一步的设计，用 {framework} 实现认证模块
      包括：
      - 用户模型
      - 认证中间件
      - 登录/登出 API
      - Token 刷新 API

  - name: "Testing"
    prompt: |
      为认证模块写完整的单元测试和集成测试
      覆盖所有正常流程和异常情况

  - name: "Documentation"
    prompt: |
      生成 API 文档和集成指南
      包括完整的 curl 示例

outputs:
  - type: code
    path: "auth/"
    description: "认证模块源代码"

  - type: document
    path: "AUTH_GUIDE.md"
    description: "认证系统集成指南"

  - type: tests
    path: "auth.test.ts"
    description: "自动化测试套件"
```

### 实战工作流示例：API 开发流程

```bash
# 启动工作流
$ claude "
执行 API 开发工作流：
1. 设计 REST API：用户管理端点（CRUD）
2. 实现 Express 后端
3. 编写单元测试（覆盖率 >90%）
4. 生成 Swagger 文档
5. 创建 Postman 集合
"
```

Claude 会自动流畅地执行这 5 个步骤，每步输出都作为下一步的输入。

### 工作流的最佳实践

1. **明确的分界点**：每个步骤应该有清晰的起点和终点
2. **依赖关系清晰**：说明哪些步骤依赖于前面的结果
3. **验证机制**：在关键步骤后添加验证（如运行测试）
4. **可视化进度**：使用 `/tasks` 追踪进度

```bash
# 好的工作流结构
$ claude "
多步骤工作流：
步骤 1：分析需求 → 输出：需求文档
步骤 2：设计架构 → 输入：需求文档 → 输出：设计方案
步骤 3：实现代码 → 输入：设计方案 → 输出：源代码
步骤 4：编写测试 → 输入：源代码 → 输出：测试套件
步骤 5：验证 → 输入：测试套件 → 执行测试 → 输出：测试报告
"
```

---

## 第五部分：项目实战

### 项目 1：Java 版用户登录系统

**完整的用户认证系统**：包括登录页面、后台 API、数据库集成。

#### 工作流设计

```
[提示词] → [框架选型] → [数据库设计] → [后端实现] → [前端实现] → [集成测试] → [部署]
```

#### 初始提示词

```
我需要用 Java + Spring Boot + PostgreSQL 构建一个用户登录系统。

要求：
1. **后端 API**：
   - POST /api/auth/register - 用户注册
   - POST /api/auth/login - 用户登录
   - POST /api/auth/refresh - 刷新 Token
   - GET /api/auth/profile - 获取用户信息
   - POST /api/auth/logout - 登出

2. **安全要求**：
   - 密码使用 bcrypt 加密
   - JWT token 认证（有效期 15 分钟）
   - 刷新 token（有效期 7 天）
   - 防止 CSRF 攻击

3. **前端页面**：
   - 登录页面（邮箱 + 密码）
   - 注册页面
   - 个人资料页面
   - 用响应式设计

4. **数据库**：
   - User 表（id, email, password_hash, created_at）
   - RefreshToken 表（token, user_id, expires_at）

5. **完整的测试**：
   - 单元测试
   - 集成测试
   - API 测试

请按顺序提供：
1. 数据库初始化脚本
2. User 和 RefreshToken 实体类
3. AuthService 和 AuthController
4. JWT Token 工具类
5. 前端登录页面（React + Tailwind）
6. 完整的测试套件
7. API 文档
"
```

#### 工作流步骤详解

**步骤 1：数据库设计**

```bash
$ claude "
设计 PostgreSQL 数据库：
1. User 表 - 用户信息
2. RefreshToken 表 - Token 管理
3. 添加必要的索引和约束
生成 DDL 脚本
"
```

预期输出：`schema.sql`

```sql
-- User 表
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_email (email)
);

-- RefreshToken 表
CREATE TABLE refresh_tokens (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token VARCHAR(500) NOT NULL UNIQUE,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_token (token)
);
```

**步骤 2：后端实体和 Repository**

```bash
$ claude "
基于上面的数据库设计，生成 Spring Boot 实体类和 Repository：
1. User 实体（JPA）
2. RefreshToken 实体（JPA）
3. UserRepository
4. RefreshTokenRepository
包括所有必要的验证注解和方法
"
```

预期输出：`User.java`

```java
package com.auth.model;

import javax.persistence.*;
import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Email(message = "邮箱格式不正确")
    @Column(nullable = false, unique = true)
    private String email;

    @NotBlank(message = "密码不能为空")
    @Column(nullable = false)
    private String passwordHash;

    @Column(name = "full_name")
    private String fullName;

    @Column(name = "is_active", columnDefinition = "boolean default true")
    private Boolean isActive = true;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @CreationTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
```

**步骤 3：JWT Token 工具类**

```bash
$ claude "
实现 JWT Token 管理工具类，包括：
1. token 生成（包含 user id 和 email）
2. token 验证
3. token 过期时间管理
4. 刷新 token 逻辑

使用 io.jsonwebtoken:jjwt 库
"
```

预期输出：`JwtTokenProvider.java`

```java
package com.auth.security;

import io.jsonwebtoken.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Slf4j
@Component
public class JwtTokenProvider {
    @Value("${jwt.secret}")
    private String jwtSecret;

    @Value("${jwt.expiration}")
    private int jwtExpirationMs; // 15 分钟

    public String generateToken(Long userId, String email) {
        return Jwts.builder()
                .setSubject(userId.toString())
                .claim("email", email)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + jwtExpirationMs))
                .signWith(SignatureAlgorithm.HS512, jwtSecret.getBytes(StandardCharsets.UTF_8))
                .compact();
    }

    public Long getUserIdFromToken(String token) {
        return Long.valueOf(
            Jwts.parser()
                .setSigningKey(jwtSecret.getBytes(StandardCharsets.UTF_8))
                .parseClaimsJws(token)
                .getBody()
                .getSubject()
        );
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parser()
                .setSigningKey(jwtSecret.getBytes(StandardCharsets.UTF_8))
                .parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            log.error("Invalid JWT token: {}", e.getMessage());
            return false;
        }
    }
}
```

**步骤 4：认证服务和控制器**

```bash
$ claude "
实现 AuthService 和 AuthController：

AuthService：
- register(RegisterRequest) - 注册用户
- login(LoginRequest) - 登录，返回 access token 和 refresh token
- refreshToken(RefreshTokenRequest) - 刷新 access token
- logout(userId) - 登出

AuthController：
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh
- POST /api/auth/logout
- GET /api/auth/profile (需要认证)

包括完整的错误处理和验证
"
```

预期的关键代码：

```java
// AuthService
@Service
@RequiredArgsConstructor
public class AuthService {
    private final UserRepository userRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;

    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
            .orElseThrow(() -> new UnauthorizedException("用户不存在"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new UnauthorizedException("密码错误");
        }

        String accessToken = jwtTokenProvider.generateToken(user.getId(), user.getEmail());
        String refreshToken = generateRefreshToken(user.getId());

        return AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .user(UserDto.from(user))
                .build();
    }

    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BadRequestException("邮箱已被注册");
        }

        User user = User.builder()
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .fullName(request.getFullName())
                .isActive(true)
                .build();

        userRepository.save(user);

        String accessToken = jwtTokenProvider.generateToken(user.getId(), user.getEmail());
        String refreshToken = generateRefreshToken(user.getId());

        return AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .user(UserDto.from(user))
                .build();
    }

    private String generateRefreshToken(Long userId) {
        String token = UUID.randomUUID().toString();
        RefreshToken refreshToken = RefreshToken.builder()
                .userId(userId)
                .token(token)
                .expiresAt(LocalDateTime.now().plusDays(7))
                .build();
        refreshTokenRepository.save(refreshToken);
        return token;
    }
}
```

**步骤 5：前端登录页面**

```bash
$ claude "
使用 React + TypeScript + Tailwind CSS 创建登录页面：
1. 邮箱和密码输入框
2. 登录和注册切换
3. 表单验证和错误提示
4. 记住我复选框
5. 响应式设计（手机/平板/桌面）
6. 加载动画
包括 API 调用逻辑
"
```

预期输出：`LoginPage.tsx`

```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import axios from 'axios';

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export const LoginPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false,
  });
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/auth/login', {
        email: formData.email,
        password: formData.password,
      });

      // 保存 token
      localStorage.setItem('accessToken', response.data.accessToken);
      localStorage.setItem('refreshToken', response.data.refreshToken);

      if (formData.rememberMe) {
        localStorage.setItem('rememberEmail', formData.email);
      }

      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.message || '登录失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-8">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-8">登录</h1>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          {/* 邮箱输入 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              邮箱
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 text-gray-400" size={20} />
              <input
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="your@email.com"
                required
              />
            </div>
          </div>

          {/* 密码输入 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              密码
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 text-gray-400" size={20} />
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {/* 记住我 */}
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.rememberMe}
              onChange={(e) =>
                setFormData({ ...formData, rememberMe: e.target.checked })
              }
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              记住我
            </label>
          </div>

          {/* 登录按钮 */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 rounded-lg transition-colors"
          >
            {isLoading ? '登录中...' : '登录'}
          </button>
        </form>

        <p className="text-center text-gray-600 text-sm mt-4">
          没有账户？{' '}
          <a href="/register" className="text-blue-600 hover:underline font-semibold">
            立即注册
          </a>
        </p>
      </div>
    </div>
  );
};
```

**步骤 6：集成测试**

```bash
$ claude "
为认证系统写完整的集成测试：
1. 用户注册测试
2. 用户登录测试
3. Token 刷新测试
4. 登出测试
5. 无效 token 处理
6. 边界情况（重复邮箱、弱密码等）

使用 JUnit 5 + MockMvc
"
```

预期输出：`AuthControllerTest.java`

```java
@SpringBootTest
@AutoConfigureMockMvc
class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private RefreshTokenRepository refreshTokenRepository;

    @BeforeEach
    void setUp() {
        refreshTokenRepository.deleteAll();
        userRepository.deleteAll();
    }

    @Test
    void testRegisterSuccess() throws Exception {
        RegisterRequest request = new RegisterRequest();
        request.setEmail("test@example.com");
        request.setPassword("Password123!");
        request.setFullName("Test User");

        mockMvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content(asJsonString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.accessToken").exists())
                .andExpect(jsonPath("$.refreshToken").exists());
    }

    @Test
    void testLoginSuccess() throws Exception {
        // 先注册
        User user = createTestUser("test@example.com", "password123");

        LoginRequest request = new LoginRequest();
        request.setEmail("test@example.com");
        request.setPassword("password123");

        mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(asJsonString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.user.email").value("test@example.com"));
    }

    @Test
    void testLoginWithInvalidPassword() throws Exception {
        createTestUser("test@example.com", "password123");

        LoginRequest request = new LoginRequest();
        request.setEmail("test@example.com");
        request.setPassword("wrongpassword");

        mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(asJsonString(request)))
                .andExpect(status().isUnauthorized());
    }

    private User createTestUser(String email, String password) {
        User user = User.builder()
                .email(email)
                .passwordHash(new BCryptPasswordEncoder().encode(password))
                .fullName("Test User")
                .isActive(true)
                .build();
        return userRepository.save(user);
    }
}
```

#### 关键提示词总结

```bash
# 快速启动整个项目
$ claude "
构建 Java Spring Boot 用户登录系统完整项目：

系统要求：
- Java 17 + Spring Boot 3.x
- PostgreSQL
- JWT 认证
- 前端：React + TypeScript

按顺序生成：
1. 项目结构和 pom.xml 配置
2. application.yml 配置
3. 数据库 DDL 脚本
4. 完整后端代码（实体、Repository、Service、Controller）
5. JWT 工具类和安全配置
6. React 前端（登录、注册、个人资料页面）
7. 集成测试
8. API 文档

每个部分包括注释和最佳实践
"
```

---

### 项目 2：Go 版用户登录系统

**用 Go + Gin + PostgreSQL 实现类似的系统**

#### 初始提示词

```
我需要用 Go + Gin 框架 + PostgreSQL 构建用户登录系统。

要求：
1. **后端 API**（RESTful）：
   - POST /api/auth/register - 注册
   - POST /api/auth/login - 登录
   - POST /api/auth/refresh - 刷新 token
   - GET /api/auth/profile - 个人资料（需认证）
   - POST /api/auth/logout - 登出

2. **认证方式**：
   - JWT token（有效期 15 分钟）
   - Refresh token（有效期 7 天）
   - Bearer token 验证中间件

3. **安全**：
   - 密码使用 bcrypt
   - CORS 保护
   - 请求速率限制

4. **前端**：
   - 登录/注册页面
   - 响应式设计

5. **数据库**：
   - PostgreSQL
   - User 表
   - RefreshToken 表

6. **完整测试**：
   - 单元测试
   - 集成测试

请提供：
1. Go 项目结构
2. models 包（User 实体）
3. database 包（初始化和数据库操作）
4. utils 包（JWT token 工具）
5. middleware 包（认证中间件）
6. handlers 包（auth 处理函数）
7. main.go（Gin 服务器配置）
8. 单元测试和集成测试
9. docker-compose.yml（快速启动）
10. API 文档
"
```

#### 工作流步骤详解

**步骤 1：Go 项目结构和依赖**

```bash
$ claude "
创建 Go 项目结构：
```
auth-system/
├── cmd/
│   └── main/
│       └── main.go
├── internal/
│   ├── models/
│   ├── handlers/
│   ├── middleware/
│   ├── utils/
│   ├── database/
│   └── config/
├── tests/
├── go.mod
├── go.sum
├── docker-compose.yml
└── README.md
```

主要依赖：
- gin-gonic/gin - Web 框架
- golang-jwt/jwt - JWT 认证
- lib/pq - PostgreSQL 驱动
- golang.org/x/crypto/bcrypt - 密码加密

生成 go.mod 和 main.go 框架
"
```

预期输出：`go.mod`

```go
module auth-system

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/golang-jwt/jwt v3.2.2+incompatible
    github.com/lib/pq v1.10.9
    golang.org/x/crypto v0.17.0
)
```

**步骤 2：数据库模型和初始化**

```bash
$ claude "
用 Go 实现数据库操作：
1. User 结构体（id, email, password_hash, created_at）
2. RefreshToken 结构体
3. database.go 初始化函数（连接 PostgreSQL）
4. 数据库迁移函数
5. 仓储层（CRUD 操作）

使用标准的 database/sql 和 lib/pq
"
```

预期输出：`internal/models/user.go`

```go
package models

import "time"

type User struct {
    ID           int64     `db:"id"`
    Email        string    `db:"email"`
    PasswordHash string    `db:"password_hash"`
    FullName     string    `db:"full_name"`
    IsActive     bool      `db:"is_active"`
    CreatedAt    time.Time `db:"created_at"`
    UpdatedAt    time.Time `db:"updated_at"`
}

type RefreshToken struct {
    ID        int64     `db:"id"`
    UserID    int64     `db:"user_id"`
    Token     string    `db:"token"`
    ExpiresAt time.Time `db:"expires_at"`
    CreatedAt time.Time `db:"created_at"`
}

type LoginRequest struct {
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"password" binding:"required"`
}

type RegisterRequest struct {
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"password" binding:"required,min=8"`
    FullName string `json:"full_name" binding:"required"`
}

type AuthResponse struct {
    AccessToken  string `json:"access_token"`
    RefreshToken string `json:"refresh_token"`
    User         *UserDTO `json:"user"`
}

type UserDTO struct {
    ID       int64  `json:"id"`
    Email    string `json:"email"`
    FullName string `json:"full_name"`
}
```

**步骤 3：JWT 工具和中间件**

```bash
$ claude "
实现 JWT 认证系统：
1. jwt.go - token 生成和验证
2. middleware.go - JWT 验证中间件
3. 支持 token 刷新
4. 错误处理
"
```

预期输出：`internal/utils/jwt.go`

```go
package utils

import (
    "errors"
    "fmt"
    "time"

    "github.com/golang-jwt/jwt"
)

var jwtSecret = []byte("your-secret-key-change-in-production")

type Claims struct {
    UserID int64  `json:"user_id"`
    Email  string `json:"email"`
    jwt.StandardClaims
}

func GenerateToken(userID int64, email string, expirationHours int) (string, error) {
    claims := &Claims{
        UserID: userID,
        Email:  email,
        StandardClaims: jwt.StandardClaims{
            ExpiresAt: time.Now().Add(time.Hour * time.Duration(expirationHours)).Unix(),
            IssuedAt:  time.Now().Unix(),
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(jwtSecret)
}

func ValidateToken(tokenString string) (*Claims, error) {
    claims := &Claims{}

    token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, errors.New("unexpected signing method")
        }
        return jwtSecret, nil
    })

    if err != nil {
        return nil, err
    }

    if !token.Valid {
        return nil, errors.New("invalid token")
    }

    return claims, nil
}
```

预期输出：`internal/middleware/auth.go`

```go
package middleware

import (
    "net/http"
    "strings"

    "auth-system/internal/utils"
    "github.com/gin-gonic/gin"
)

func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "missing auth header"})
            c.Abort()
            return
        }

        parts := strings.SplitN(authHeader, " ", 2)
        if len(parts) != 2 || parts[0] != "Bearer" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid auth header"})
            c.Abort()
            return
        }

        claims, err := utils.ValidateToken(parts[1])
        if err != nil {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
            c.Abort()
            return
        }

        c.Set("user_id", claims.UserID)
        c.Set("email", claims.Email)
        c.Next()
    }
}
```

**步骤 4：认证处理函数**

```bash
$ claude "
实现 Gin 处理函数：
1. RegisterHandler - 用户注册
2. LoginHandler - 用户登录
3. RefreshHandler - 刷新 token
4. ProfileHandler - 获取个人资料
5. LogoutHandler - 登出

使用上面定义的中间件和工具
"
```

预期输出：`internal/handlers/auth.go` 片段

```go
package handlers

import (
    "database/sql"
    "net/http"

    "auth-system/internal/models"
    "auth-system/internal/utils"
    "github.com/gin-gonic/gin"
    "golang.org/x/crypto/bcrypt"
)

type AuthHandler struct {
    db *sql.DB
}

func NewAuthHandler(db *sql.DB) *AuthHandler {
    return &AuthHandler{db: db}
}

func (h *AuthHandler) Register(c *gin.Context) {
    var req models.RegisterRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 检查邮箱是否已存在
    var existingEmail string
    err := h.db.QueryRow("SELECT email FROM users WHERE email = $1", req.Email).Scan(&existingEmail)
    if err == nil {
        c.JSON(http.StatusConflict, gin.H{"error": "email already registered"})
        return
    }

    // 密码加密
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "password hashing failed"})
        return
    }

    // 保存用户
    var userID int64
    err = h.db.QueryRow(
        "INSERT INTO users (email, password_hash, full_name) VALUES ($1, $2, $3) RETURNING id",
        req.Email, string(hashedPassword), req.FullName,
    ).Scan(&userID)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "registration failed"})
        return
    }

    // 生成 token
    accessToken, _ := utils.GenerateToken(userID, req.Email, 0) // 15 分钟
    refreshToken, _ := utils.GenerateToken(userID, req.Email, 168) // 7 天

    c.JSON(http.StatusOK, models.AuthResponse{
        AccessToken:  accessToken,
        RefreshToken: refreshToken,
        User: &models.UserDTO{
            ID:       userID,
            Email:    req.Email,
            FullName: req.FullName,
        },
    })
}

func (h *AuthHandler) Login(c *gin.Context) {
    var req models.LoginRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 查询用户
    var user models.User
    err := h.db.QueryRow("SELECT id, email, password_hash, full_name FROM users WHERE email = $1", req.Email).
        Scan(&user.ID, &user.Email, &user.PasswordHash, &user.FullName)
    if err == sql.ErrNoRows {
        c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
        return
    }

    // 验证密码
    err = bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(req.Password))
    if err != nil {
        c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
        return
    }

    // 生成 token
    accessToken, _ := utils.GenerateToken(user.ID, user.Email, 0)
    refreshToken, _ := utils.GenerateToken(user.ID, user.Email, 168)

    c.JSON(http.StatusOK, models.AuthResponse{
        AccessToken:  accessToken,
        RefreshToken: refreshToken,
        User: &models.UserDTO{
            ID:       user.ID,
            Email:    user.Email,
            FullName: user.FullName,
        },
    })
}

func (h *AuthHandler) Profile(c *gin.Context) {
    userID := c.GetInt64("user_id")
    email := c.GetString("email")

    var user models.User
    err := h.db.QueryRow(
        "SELECT id, email, full_name FROM users WHERE id = $1",
        userID,
    ).Scan(&user.ID, &user.Email, &user.FullName)

    if err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
        return
    }

    c.JSON(http.StatusOK, models.UserDTO{
        ID:       user.ID,
        Email:    user.Email,
        FullName: user.FullName,
    })
}
```

**步骤 5：Main 应用启动**

```bash
$ claude "
写 main.go 应用程序：
1. 读取配置（数据库连接）
2. 初始化数据库
3. 设置 Gin 路由
4. 配置 CORS 和中间件
5. 启动服务器

监听 :8080 端口
"
```

预期输出：`cmd/main/main.go`

```go
package main

import (
    "database/sql"
    "log"
    "os"

    "auth-system/internal/handlers"
    "auth-system/internal/middleware"
    _ "github.com/lib/pq"
    "github.com/gin-gonic/gin"
)

func initDB() *sql.DB {
    dsn := os.Getenv("DATABASE_URL")
    if dsn == "" {
        dsn = "postgres://user:password@localhost:5432/auth_db?sslmode=disable"
    }

    db, err := sql.Open("postgres", dsn)
    if err != nil {
        log.Fatalf("Failed to connect to database: %v", err)
    }

    // 初始化表
    schema := `
    CREATE TABLE IF NOT EXISTS users (
        id BIGSERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(255),
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token VARCHAR(500) NOT NULL UNIQUE,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
    `

    if _, err := db.Exec(schema); err != nil {
        log.Fatalf("Failed to initialize database: %v", err)
    }

    return db
}

func main() {
    gin.SetMode(gin.ReleaseMode)
    router := gin.Default()

    // 初始化数据库
    db := initDB()
    defer db.Close()

    // 创建 handler
    authHandler := handlers.NewAuthHandler(db)

    // 设置路由
    auth := router.Group("/api/auth")
    {
        auth.POST("/register", authHandler.Register)
        auth.POST("/login", authHandler.Login)
        auth.POST("/refresh", authHandler.Refresh)
        auth.POST("/logout", middleware.AuthMiddleware(), authHandler.Logout)
        auth.GET("/profile", middleware.AuthMiddleware(), authHandler.Profile)
    }

    log.Println("Server running on :8080")
    router.Run(":8080")
}
```

**步骤 6：单元测试**

```bash
$ claude "
为 Go 认证系统写单元测试：
1. 密码加密和验证测试
2. JWT token 生成和验证测试
3. 注册处理函数测试
4. 登录处理函数测试
5. 中间件验证测试

使用 testing 包和 testify/assert
"
```

预期输出：`internal/utils/jwt_test.go`

```go
package utils

import (
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
)

func TestGenerateAndValidateToken(t *testing.T) {
    // 生成 token
    token, err := GenerateToken(1, "test@example.com", 1)
    assert.NoError(t, err)
    assert.NotEmpty(t, token)

    // 验证 token
    claims, err := ValidateToken(token)
    assert.NoError(t, err)
    assert.Equal(t, int64(1), claims.UserID)
    assert.Equal(t, "test@example.com", claims.Email)
}

func TestExpiredToken(t *testing.T) {
    // 生成过期 token（-1 小时）
    token, _ := GenerateToken(1, "test@example.com", -1)

    // 应该验证失败
    claims, err := ValidateToken(token)
    assert.Error(t, err)
    assert.Nil(t, claims)
}

func TestInvalidToken(t *testing.T) {
    claims, err := ValidateToken("invalid.token.here")
    assert.Error(t, err)
    assert.Nil(t, claims)
}
```

**步骤 7：Docker 快速启动**

```bash
$ claude "
生成 docker-compose.yml，一键启动整个系统：
1. PostgreSQL 服务
2. Go 应用服务
3. 环境变量配置
4. 端口映射
5. 健康检查

支持 docker-compose up 直接启动
"
```

预期输出：`docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: authuser
      POSTGRES_PASSWORD: authpass
      POSTGRES_DB: auth_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U authuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    environment:
      DATABASE_URL: "postgres://authuser:authpass@postgres:5432/auth_db?sslmode=disable"
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
    command: /app/auth-system

volumes:
  postgres_data:
```

#### 完整启动指南

```bash
# 启动整个系统
$ docker-compose up -d

# 检查服务状态
$ docker-compose ps

# 查看日志
$ docker-compose logs -f app

# 测试 API
$ curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'

# 停止服务
$ docker-compose down
```

---

## 总结：Claude Code 使用的核心原则

1. **对话式编程**：不是一次性生成，而是持续对话和迭代
2. **工作流驱动**：复杂项目分步骤，利用 Claude 的上下文记忆
3. **验证导向**：每个步骤都应该可验证（测试、运行、审查）
4. **文档并行**：边写代码边生成文档，确保同步
5. **最佳实践**：让 Claude 推荐每个技术栈的最佳实践

---

## 快速参考：常用指令模板

```bash
# 快速代码审查
$ claude --file src/critical.ts "检查这个文件的性能和安全问题"

# 多步骤工作流
$ claude "
步骤 1：分析需求
步骤 2：设计架构
步骤 3：实现代码
步骤 4：编写测试
"

# 恢复长期项目
$ claude --resume <session-id> "继续昨天的工作"

# 后台运行耗时任务
$ claude --background "运行完整的测试套件和覆盖率检查"

# 对比方案
$ claude "对比方案 A 和方案 B 在我的项目中的优缺点"
```
