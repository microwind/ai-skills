# 例子 3：快速定位和修复 Bug

**场景**：用户反馈登录后页面闪屏，需要快速定位和修复问题。

**学习目标**：
- 学习系统的 Bug 诊断方法
- 理解 React 生命周期问题
- 掌握 TDD 防止回归

---

## 问题描述

用户报告：登录成功后，页面会闪一下才显示内容。这是一个常见的 React 问题。

---

## 第一步：信息收集

### 提示词

```bash
$ claude "
登录后页面会闪屏。这是什么原因？常见的可能有：
1. 用户认证状态变化时 UI 错乱
2. 页面重定向不当
3. 数据加载时的空状态显示
4. 组件卸载/重挂载

我的主要代码文件：
- src/hooks/useAuth.ts（认证逻辑）
- src/pages/Dashboard.tsx（仪表板页面）
- src/components/ProtectedRoute.tsx（路由保护）

你能帮我分析可能的原因吗？
"
```

Claude 会列出常见原因。

---

## 第二步：代码审查

### 提示词

```bash
$ claude "
这是我的 Dashboard 组件：

\`\`\`typescript
export const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div>
      <h1>欢迎, {user.name}</h1>
      <p>用户邮箱: {user.email}</p>
      {/* 其他内容 */}
    </div>
  );
};
\`\`\`

这里有什么问题吗？
"
```

Claude 会指出：**当 `user` 是 `null` 或 `undefined` 时，会报错或显示 `undefined`**。

---

## 第三步：识别根本原因

### 提示词

```bash
$ claude "
这是 useAuth hook：

\`\`\`typescript
export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // 从 localStorage 恢复用户信息
    const saved = localStorage.getItem('user');
    if (saved) {
      setUser(JSON.parse(saved));
    }
    setIsLoading(false);
  }, []);

  return { user, isLoading };
};
\`\`\`

现在我明白了：Dashboard 在 isLoading 期间还在渲染，导致 user 是 null。

该怎么修复？
"
```

---

## 第四步：实现修复

### 提示词

```bash
$ claude "
改进 Dashboard 组件，要求：
1. 在 isLoading 时显示加载骨架屏
2. user 不存在时重定向到登录页
3. 使用 React Router 的 useNavigate

避免条件渲染导致的闪屏
"
```

### 修复后的代码

```typescript
export const Dashboard = () => {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();

  // 加载中
  if (isLoading) {
    return <LoadingSkeleton />;
  }

  // 未登录
  if (!user) {
    navigate('/login', { replace: true });
    return null;
  }

  // 登录成功
  return (
    <div>
      <h1>欢迎, {user.name}</h1>
      <p>用户邮箱: {user.email}</p>
    </div>
  );
};
```

---

## 第五步：进一步优化

### 提示词

```bash
$ claude "
这个修复有没有还能改进的地方？
比如：
1. 使用 Suspense + lazy 更优雅吗？
2. 骨架屏怎么设计才不刺眼？
3. 如何减少不必要的重新渲染？
"
```

---

## 第六步：编写防回归测试

### 提示词

```bash
$ claude "
写测试防止这个问题再出现：
1. 测试加载中状态显示骨架屏
2. 测试未登录时重定向
3. 测试登录成功时显示内容

使用 React Testing Library
"
```

### 测试代码

```typescript
describe('Dashboard', () => {
  it('应该在加载中显示骨架屏', () => {
    // Mock useAuth 返回 isLoading: true
    const { getByTestId } = render(<Dashboard />);
    expect(getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  it('未登录时应该重定向到登录页', () => {
    // Mock useAuth 返回 user: null
    const { navigate } = useNavigateMock();
    render(<Dashboard />);
    expect(navigate).toHaveBeenCalledWith('/login', { replace: true });
  });

  it('登录成功时应该显示欢迎信息', () => {
    // Mock useAuth 返回有效的 user
    const { getByText } = render(<Dashboard />);
    expect(getByText(/欢迎/)).toBeInTheDocument();
  });
});
```

---

## 完整工作流

```
症状描述 → 信息收集 → 审查代码 → 识别原因 → 实现修复 → 编写测试 → 验证
```

---

## 常见原因速查表

| 症状 | 可能原因 | 解决方案 |
|------|--------|--------|
| 页面闪屏 | 状态初始化延迟 | 添加加载状态 |
| 白屏 | 渲染错误 | 错误边界 |
| 内容抖动 | 布局计算延迟 | 预留空间 |
| 数据不同步 | 状态管理混乱 | Redux/Context |

---

## 这个例子的要点

✅ **学到的技巧**：
- 结构化的调试方法
- React 生命周期陷阱
- TDD 防止回归

✅ **应用场景**：
- 快速定位任何 Bug
- 理解框架行为
- 编写更稳定的代码

---

## 下一个例子

→ [例子 4：生成文档](./04-生成文档.md)

或查看其他：
- [例子 5：测试用例](./05-测试用例.md)

