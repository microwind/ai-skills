# Chain of Responsibility - 诊断、规划、实现表单

## 第1步：诊断 (Diagnosis)

### 快速诊断表

| 问题 | 症状 | Chain of Resp? |
|------|------|---|
| 多个对象可能处理请求 | 需要查找合适的处理者 | ✅ 是 |
| 处理者编译时未知 | 运行时才确定谁处理 | ✅ 是 |
| 请求有默认处理路径 | 无法处理时有后备方案 | ✅ 是 |
| 需要预处理/后处理 | 多个中间件或过滤器 | ✅ 是 |
| 只有一个固定处理者 | 直接调用即可 | ❌ 否 |
| 所有对象都需处理 | 应使用观察者模式 | ❌ 否 |

### 诊断问卷

1. **当前架构中:**
   - 是否存在 `if-else` 链来判断由谁处理请求? 
   - 处理者数量是否大于3个?
   - 处理顺序是否可能变化?

2. **对象间通信:**
   - 发送者是否知道所有可能的接收者?
   - 接收者之间是否有优先级关系?
   - 是否需要动态添加/移除接收者?

3. **维护性问题:**
   - 每次添加新处理者是否需要修改发送者?
   - 处理流程是否容易测试?
   - 是否有性能瓶颈?

**诊断结论**: 如果上述问题大多数答案为"是"，则Chain of Responsibility是合适的选择。

---

## 第2步：规划 (Planning)

### 处理者选择矩阵

**根据你的需求，选择合适的实现方式:**

| 实现方式 | 适用场景 | 复杂度 | 性能 | 维护度 |
|---------|---------|-------|------|-------|
| **经典链式** | 标准责任链，处理者固定 | 低 | 高 | 简单 |
| **动态Builder** | 构建时确定链结构 | 中 | 高 | 中等 |
| **函数式** | Lambda表达式友好，函数式编程 | 中 | 中 | 复杂 |
| **事件驱动** | 异步处理，支持并发 | 高 | 中 | 复杂 |
| **流式处理** | Stream API，函数式处理 | 中 | 中 | 简单 |

### 基本流程设计

```
需求分析
    ↓
[是否固定链?] → 是 → 经典链式实现
    ↓ 否
[是否需要异步?] → 是 → 事件驱动实现
    ↓ 否
[是否用Lambda?] → 是 → 函数式实现
    ↓ 否
使用Builder模式
```

### 架构决策清单

- [ ] 处理者是否为单例?
- [ ] 链的生命周期是多长 (永久/请求级/会话级)?
- [ ] 是否支持动态添加/移除处理者?
- [ ] 异常处理策略 (停止/继续/回调)?
- [ ] 是否需要请求上下文共享?
- [ ] 性能目标 (QPS/延迟)?
- [ ] 是否需要操作日志/审计?
- [ ] 是否支持优先级/条件路由?

---

## 第3步：设计链结构 (Design Chain Structure)

### 链设计决策树

```
【分析处理需求】
        ↓
【确定处理者数量和类型】
    ↓
    ├→ 2-3个处理者 → 经典链式
    └→ >3个处理者 → Builder/Stream API
        ↓
【分析处理顺序】
    ├→ 严格顺序 (序列化) → 使用level/priority
    └→ 灵活顺序 → 运行时排序
        ↓
【分析异步需求】
    ├→ 同步处理 → 直接链式
    └→ 异步处理 → 事件驱动/线程池
        ↓
【最终选定实现】
```

### 处理者定义表

为你的项目填写处理者信息:

| 处理者名称 | 职责 | 处理条件 | 优先级 | 后续 |
|---------|------|--------|-------|------|
| 验证处理者 | 验证输入参数 | 字段非空 | 1 | 转发或返回 |
| 授权处理者 | 检查用户权限 | 有效Token | 2 | 转发或拒绝 |
| 日志处理者 | 记录操作日志 | 总是成功 | 3 | 总是转发 |
| 业务处理者 | 执行业务逻辑 | 总是成功 | 4 | 返回结果 |

### 链生命周期规划

```
应用启动
    ↓
构建处理链 (Initialization)
    ├→ 读取配置
    ├→ 实例化处理者
    ├→ 链接处理者
    └→ 验证链完整性
        ↓
请求处理 (Runtime)
    ├→ 请求进入
    ├→ 逐个处理
    └→ 返回结果
        ↓
应用关闭
    ↓
清理资源 (Cleanup)
```

---

## 第4步：编码实现 (Implementation)

### 6步实现清单

#### Step 1: 定义Handler接口
```java
public interface Handler {
    void setNext(Handler handler);
    void handle(Request request);
    // 可选：
    // boolean canHandle(Request request);
    // Result handle(Request request);
}
```

#### Step 2: 实现基类
```java
public abstract class AbstractHandler implements Handler {
    protected Handler next;
    
    @Override
    public void setNext(Handler handler) {
        this.next = handler;
    }
    
    @Override
    public void handle(Request request) {
        if (canHandle(request)) {
            process(request);
        } else if (next != null) {
            next.handle(request);
        }
    }
    
    protected abstract boolean canHandle(Request request);
    protected abstract void process(Request request);
}
```

#### Step 3: 实现具体处理者
```java
public class ConcreteHandlerA extends AbstractHandler {
    @Override
    protected boolean canHandle(Request request) {
        return request.getType() == RequestType.TYPE_A;
    }
    
    @Override
    protected void process(Request request) {
        // 处理逻辑
        System.out.println("Handler A处理请求");
    }
}
```

#### Step 4: 构建链
```java
Handler chain = new ConcreteHandlerA();
chain.setNext(new ConcreteHandlerB());
chain.setNext(new ConcreteHandlerC());
```

或使用Builder:
```java
Handler chain = new ChainBuilder()
    .add(new ConcreteHandlerA())
    .add(new ConcreteHandlerB())
    .add(new ConcreteHandlerC())
    .build();
```

#### Step 5: 测试链
```java
@Test
public void testChain() {
    Handler chain = buildChain();
    Request request = new Request(RequestType.TYPE_B);
    chain.handle(request);
    // 断言：HandlerB处理了请求
}
```

#### Step 6: 集成和验证
```java
// 集成到应用
@Configuration
public class ChainConfiguration {
    @Bean
    public Handler requestChain() {
        return new ChainBuilder()
            .add(validationHandler())
            .add(authorizationHandler())
            .add(loggingHandler())
            .add(businessHandler())
            .build();
    }
}
```

---

## 第5步：测试 (Testing)

### 单元测试清单

- [ ] 单个处理者的正确处理
- [ ] 请求转发给下一个处理者
- [ ] 链的末尾处理
- [ ] 异常处理
- [ ] 性能基准测试

### 集成测试清单

- [ ] 完整链的端到端测试
- [ ] 多个处理者的交互
- [ ] 动态链构建
- [ ] 并发处理
- [ ] 内存泄漏检查

---

## 第6步：审查与优化 (Review & Optimization)

### 代码审查清单

- [ ] 是否存在链断裂风险?
- [ ] 异常处理是否完善?
- [ ] 是否有性能瓶颈?
- [ ] 代码是否易于维护?
- [ ] 文档是否清晰?

### 性能优化清单

- [ ] 处理者是否有不必要的递归?
- [ ] 是否有重复的处理判断?
- [ ] 序列化/反序列化是否高效?
- [ ] 缓存策略是否合理?

### 常见陷阱预防

| 陷阱 | 症状 | 防止方法 |
|------|------|--------|
| 链断裂 | 请求丢失 | 使用模板方法，强制传递 |
| 无限循环 | 程序hang | 链构建时验证，避免设置相同handler |
| 上帝处理者 | 单个处理者过于复杂 | 职责分离，每个handler只做一件事 |
| NPE异常 | next为null时崩溃 | null检查或使用Optional |
| 优先级混乱 | 处理顺序不确定 | 显式定义优先级或order |
| 内存泄漏 | 处理者未释放资源 | 实现Closeable，定期清理 |

---

## 决策矩阵：何时使用哪个变体

### 场景1: 标准Web请求处理

```
需求：HTTP请求 → 认证 → 授权 → 日志 → 业务处理
使用: 经典链式 (同步)
理由: 流程固定，顺序明确，无需异步
```

### 场景2: 异步事件处理

```
需求：多个事件处理器，可能异步执行
使用: 事件驱动链
理由: 需要支持异步、并发，松耦合
```

### 场景3: 函数式编程风格

```
需求：使用Lambda，Stream API处理
使用: 函数式链
理由: 代码简洁，现代Java，易于组合
```

### 场景4: 复杂工作流

```
需求：多步审批，动态添加/删除步骤
使用: Builder模式 + 优先级
理由: 灵活构建，易于维护，支持动态修改
```

---

## 总结模板

在实现Chain of Responsibility时记住：

1. **清晰的职责** - 每个处理者做一件事
2. **完善的传递** - 确保请求不会丢失
3. **异常处理** - 处理链中的所有异常情况
4. **可维护性** - 易于添加新处理者和调试
5. **性能** - 避免过长的链，使用缓存/优化
