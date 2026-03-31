---
name: Chain of Responsibility
description: "将请求沿着处理者链进行传递，直到有处理者处理该请求"
license: MIT
---

# Chain of Responsibility Pattern (责任链模式)

## 核心概念

**Chain of Responsibility**是一种Behavioral设计模式。

**定义**: 将请求沿着一个处理者链进行传递，直到有一个处理者处理该请求。它避免了发送者和接收者之间的紧耦合。

### 核心思想

- **传递链**: 请求从链的首端开始，逐个传递给处理者
- **权责分离**: 每个处理者关注自己能处理的请求类型
- **灵活组合**: 可以动态添加、移除或重新排列处理者
- **自动降级**: 如果一个处理者无法处理，自动传递给下一个

---

## 何时使用

### 触发条件

1. **多个处理者，任意一个可以处理请求** - 如日志系统、身份验证、事件处理
2. **处理者集合不固定** - 需要动态组织处理流程
3. **想要解耦发起者和处理者** - 发起者不关心谁最终处理
4. **请求有优先级或依赖关系** - 审批流、事件分发
5. **处理过程涉及多个层级** - 如权限验证、异常处理链

### 不适合场景

- ❌ 只有单一处理者的情况 - 直接调用即可
- ❌ 需要并行处理所有请求 - 应该使用观察者模式
- ❌ 处理顺序完全随意且无规律

---

## 基本结构

### 参与者

1. **Handler (处理者)** - 定义处理请求的接口，包含对下一个处理者的引用
2. **ConcreteHandler (具体处理者)** - 实现处理请求的逻辑，决定是否处理或传递给下一个
3. **Client (客户端)** - 向链中的某个处理者提交请求

### UML关系

```
┌─────────────────┐
│    Handler      │
├─────────────────┤
│ - successor     │
│ + handleRequest │
└─────────────────┘
        △
        │ implements
        │
    ┌───┴───────────────────┐
    │                       │
┌───────────────────┐  ┌─────────────────┐
│ ConcreteHandler1  │  │ ConcreteHandler2 │
├───────────────────┤  ├─────────────────┤
│ + handleRequest() │  │ + handleRequest()│
└───────────────────┘  └─────────────────┘

Client → Handler Chain → Handler1 → Handler2 → Handler3
```

### 流程图

```
请求进入
    ↓
[Handler1能处理?] → 是 → 处理请求并返回
    ↓ 否
[Handler2能处理?] → 是 → 处理请求并返回
    ↓ 否
[Handler3能处理?] → 是 → 处理请求并返回
    ↓ 否
[还有下一个处理者?] → 是 → 传递给下一个
    ↓ 否
请求未处理 (返回null或异常)
```

---

## 实现方式对比

### 方法1: 经典链式实现 (基础)

**特点**: 最基础的职责链，处理者手动管理next引用

```java
// Handler接口
abstract class Handler {
    protected Handler successor;
    
    public void setSuccessor(Handler handler) {
        this.successor = handler;
    }
    
    public abstract void handleRequest(Request request);
}

// 具体处理者
class ConcreteHandler1 extends Handler {
    @Override
    public void handleRequest(Request request) {
        if (request.getType() == RequestType.TYPE1) {
            System.out.println("Handler1 处理请求: " + request);
        } else if (successor != null) {
            successor.handleRequest(request);
        }
    }
}

// 使用示例
Handler handler1 = new ConcreteHandler1();
Handler handler2 = new ConcreteHandler2();
handler1.setSuccessor(handler2);
handler1.handleRequest(request);
```

### 方法2: 动态链式实现 (流式构建)

**特点**: 使用Builder模式动态构建处理链

```java
class ChainBuilder {
    private Handler head;
    private Handler tail;
    
    public ChainBuilder add(Handler handler) {
        if (head == null) {
            head = tail = handler;
        } else {
            tail.setSuccessor(handler);
            tail = handler;
        }
        return this;
    }
    
    public Handler build() {
        return head;
    }
}

// 使用示例
Handler chain = new ChainBuilder()
    .add(new AuthenticationHandler())
    .add(new AuthorizationHandler())
    .add(new LoggingHandler())
    .add(new ProcessingHandler())
    .build();

chain.handleRequest(request);
```

### 方法3: 函数式链式实现

**特点**: 使用函数式编程，支持Lambda表达式

```java
@FunctionalInterface
interface RequestHandler {
    Result handle(Request request, RequestHandler next);
}

class FunctionalChain {
    public static RequestHandler chain(List<RequestHandler> handlers) {
        return (request, next) -> {
            final RequestHandler[] current = {null};
            for (int i = handlers.size() - 1; i >= 0; i--) {
                final RequestHandler handler = handlers.get(i);
                final RequestHandler finalNext = current[0];
                current[0] = (req, n) -> handler.handle(req, 
                    (r, fn) -> {
                        if (finalNext != null) {
                            return finalNext.handle(r, fn);
                        }
                        return new Result(false, "No handler");
                    });
            }
            return current[0].handle(request, next);
        };
    }
}

// 使用示例
RequestHandler chain = FunctionalChain.chain(Arrays.asList(
    (req, next) -> req.type == 1 ? new Result(true, "handled") : next.handle(req, null),
    (req, next) -> req.type == 2 ? new Result(true, "handled") : next.handle(req, null),
    (req, next) -> new Result(false, "unhandled")
));
```

### 方法4: 事件驱动链 (异步处理)

**特点**: 基于事件总线，支持异步处理和并发

```java
class EventDrivenChain {
    private EventBus eventBus = new EventBus();
    private List<EventHandler> handlers = new CopyOnWriteArrayList<>();
    
    public void register(EventHandler handler) {
        handlers.add(handler);
        eventBus.register(handler);
    }
    
    public void process(Request request) {
        eventBus.post(new RequestEvent(request));
    }
    
    static class EventHandler {
        @Subscribe
        public void handleRequest(RequestEvent event) {
            // 异步处理请求
        }
    }
}

// 使用示例
EventDrivenChain chain = new EventDrivenChain();
chain.register(new ValidationHandler());
chain.register(new ProcessingHandler());
chain.register(new NotificationHandler());
chain.process(request);
```

---

## 8个真实使用场景

### 场景1: 日志系统 (Logging)

**应用**: Apache Commons Logging, SLF4J

```java
// 日志处理链：ERROR -> WARN -> INFO -> DEBUG -> TRACE
abstract class LogHandler {
    protected LogHandler nextHandler;
    protected LogLevel level;
    
    public void setNextHandler(LogHandler handler) {
        this.nextHandler = handler;
    }
    
    public void log(LogLevel level, String message) {
        if (this.level.getValue() <= level.getValue()) {
            writeLog(message);
        }
        if (nextHandler != null) {
            nextHandler.log(level, message);
        }
    }
    
    protected abstract void writeLog(String message);
}

class ErrorHandler extends LogHandler {
    public ErrorHandler() { this.level = LogLevel.ERROR; }
    protected void writeLog(String msg) { System.err.println("[ERROR] " + msg); }
}

class WarnHandler extends LogHandler {
    public WarnHandler() { this.level = LogLevel.WARN; }
    protected void writeLog(String msg) { System.out.println("[WARN] " + msg); }
}

// 构建链
LogHandler errorHandler = new ErrorHandler();
LogHandler warnHandler = new WarnHandler();
errorHandler.setNextHandler(warnHandler);
```

### 场景2: Web请求处理 (Middleware)

**应用**: Spring Security Filter Chain, Express.js中间件

```java
// Spring Security FilterChain
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) {
        return http
            .authorizeRequests()
            .antMatchers("/public/**").permitAll()
            .anyRequest().authenticated()
            .and()
            .formLogin()
            .and()
            .build(); // 内部构建责任链
    }
}

// 中间件链: CORS → Authentication → Authorization → Logging
public class SecurityFilterChain {
    private List<SecurityFilter> filters = new ArrayList<>();
    
    public SecurityFilterChain addFilter(SecurityFilter filter) {
        filters.add(filter);
        return this;
    }
    
    public void doFilter(Request req, Response res) {
        new FilterChainImpl(filters, 0).doFilter(req, res);
    }
}
```

### 场景3: 审批工作流 (Approval Workflow)

**应用**: Alfresco工作流, 企业审批系统

```java
// 审批流：员工 → 部门经理 → 总监 → CFO → CEO
abstract class ApprovalHandler {
    protected ApprovalHandler nextApprover;
    protected double approvalLimit;
    
    public void setNextApprover(ApprovalHandler handler) {
        this.nextApprover = handler;
    }
    
    public void handleRequest(ExpenseRequest request) {
        if (request.getAmount() <= approvalLimit) {
            approve(request);
        } else if (nextApprover != null) {
            nextApprover.handleRequest(request);
        } else {
            reject(request);
        }
    }
    
    abstract void approve(ExpenseRequest request);
    abstract void reject(ExpenseRequest request);
}

class ManagerApprover extends ApprovalHandler {
    public ManagerApprover() { this.approvalLimit = 5000; }
    void approve(ExpenseRequest req) { System.out.println("经理批准: " + req); }
    void reject(ExpenseRequest req) { System.out.println("经理拒绝: " + req); }
}
```

### 场景4: 事件处理系统 (Event Processing)

**应用**: Swing事件处理, DOM事件冒泡

```java
// GUI事件链: 按钮 → 容器 → 窗口
abstract class Component {
    protected Component parent;
    
    public void setParent(Component parent) {
        this.parent = parent;
    }
    
    public void handleEvent(Event event) {
        if (canHandle(event)) {
            processEvent(event);
            event.setProcessed(true);
        }
        
        if (!event.isProcessed() && parent != null) {
            parent.handleEvent(event);
        }
    }
    
    abstract boolean canHandle(Event event);
    abstract void processEvent(Event event);
}

class Button extends Component {
    boolean canHandle(Event event) { return event instanceof ClickEvent; }
    void processEvent(Event event) { System.out.println("Button clicked"); }
}
```

### 场景5: 异常处理链 (Exception Handling)

**应用**: Java异常处理, 防御性编程

```java
// 异常处理链: 业务异常 → IO异常 → 系统异常 → 默认 
abstract class ExceptionHandler {
    protected ExceptionHandler nextHandler;
    
    public void setNextHandler(ExceptionHandler handler) {
        this.nextHandler = handler;
    }
    
    public void handle(Exception ex) {
        if (canHandle(ex)) {
            processException(ex);
        } else if (nextHandler != null) {
            nextHandler.handle(ex);
        } else {
            System.err.println("未处理的异常: " + ex);
        }
    }
    
    abstract boolean canHandle(Exception ex);
    abstract void processException(Exception ex);
}

class DatabaseExceptionHandler extends ExceptionHandler {
    boolean canHandle(Exception ex) { return ex instanceof SQLException; }
    void processException(Exception ex) { 
        System.out.println("数据库异常重试or回滚");
    }
}
```

### 场景6: 请求验证链 (Validation Chain)

**应用**: Bean Validation, 表单验证

```java
// 验证链: 空值检查 → 格式检查 → 业务规则检查
abstract class Validator {
    protected Validator nextValidator;
    
    public void setNextValidator(Validator validator) {
        this.nextValidator = validator;
    }
    
    public ValidationResult validate(User user) {
        ValidationResult result = doValidate(user);
        
        if (!result.isValid()) {
            return result;
        }
        
        if (nextValidator != null) {
            return nextValidator.validate(user);
        }
        
        return new ValidationResult(true);
    }
    
    abstract ValidationResult doValidate(User user);
}

class EmailValidator extends Validator {
    ValidationResult doValidate(User user) {
        if (user.email == null || !user.email.contains("@")) {
            return new ValidationResult(false, "Invalid email");
        }
        return new ValidationResult(true);
    }
}
```

### 场景7: 消息处理管道 (Message Pipeline)

**应用**: 消息队列处理, 数据流处理

```java
// 消息处理链: 反序列化 → 加密 → 业务处理 → 序列化
abstract class MessageHandler {
    protected MessageHandler next;
    
    public void setNext(MessageHandler handler) {
        this.next = handler;
    }
    
    public final Message handle(Message message) {
        Message result = process(message);
        if (next != null && result != null) {
            return next.handle(result);
        }
        return result;
    }
    
    abstract Message process(Message message);
}

class EncryptionHandler extends MessageHandler {
    Message process(Message msg) {
        msg.payload = encrypt(msg.payload);
        return msg;
    }
}

class BusinessHandler extends MessageHandler {
    Message process(Message msg) {
        // 执行业务逻辑
        return msg;
    }
}
```

### 场景8: 路由和调度 (Routing)

**应用**: 请求路由, 任务调度

```java
// 路由链: HTTP方法识别 → 内容类型 → API版本 → 具体处理
abstract class RouteHandler {
    protected RouteHandler next;
    
    public void setNext(RouteHandler handler) {
        this.next = handler;
    }
    
    public Response handle(Request request) {
        if (matches(request)) {
            return process(request);
        }
        if (next != null) {
            return next.handle(request);
        }
        return new Response(404, "Not Found");
    }
    
    abstract boolean matches(Request request);
    abstract Response process(Request request);
}

class GetRouteHandler extends RouteHandler {
    boolean matches(Request req) { return "GET".equals(req.method); }
    Response process(Request req) { return fetchData(req.path); }
}

class PostRouteHandler extends RouteHandler {
    boolean matches(Request req) { return "POST".equals(req.method); }
    Response process(Request req) { return createData(req.body); }
}
```

---

## 4个常见问题及解决方案

### 问题1: 链断裂导致请求丢失

**症状**: 
- 有些请求在链中消失，未被处理也未被传递
- 某个处理者忘记调用next.handle()

**解决方案**:

```java
// ✅ 好的做法：使用模板方法确保链传递
abstract class SafeHandler implements Handler {
    private Handler next;
    
    @Override
    public final void handle(Request request) {
        if (shouldHandle(request)) {
            process(request);
            return; // 此处理者处理了请求
        }
        
        // 必须继续传递
        if (next != null) {
            next.handle(request);
        } else {
            // 链末尾，记录未处理的请求
            logUnhandledRequest(request);
        }
    }
    
    protected abstract boolean shouldHandle(Request request);
    protected abstract void process(Request request);
}

// ❌ 危险的做法：容易遗漏传递
class UnsafeHandler {
    public void handle(Request request) {
        if (request.type == MY_TYPE) {
            // 处理...
            // 忘记了传递给next!
        }
    }
}
```

### 问题2: 优先级和顺序管理混乱

**症状**:
- 处理顺序不确定，导致结果不一致
- 高优先级请求可能被低优先级处理者先处理

**解决方案**:

```java
// ✅ 使用PriorityQueue维护优先级
class PriorityChain {
    private PriorityQueue<Handler> handlers = new PriorityQueue<>(
        (h1, h2) -> h2.getPriority() - h1.getPriority()
    );
    
    public void addHandler(Handler handler) {
        handlers.add(handler);
    }
    
    public void handle(Request request) {
        Handler[] current = new Handler[1];
        handlers.forEach(handler -> {
            if (current[0] == null && handler.canHandle(request)) {
                handler.handle(request);
                current[0] = handler;
            } else if (current[0] != null) {
                handler.setNext(handler);
            }
        });
    }
}

// ✅ 或使用显式排序和级别
class SortedChain {
    private List<Handler> handlers;
    
    public void build() {
        //按照levels严格排序
        handlers.sort((h1, h2) -> 
            h1.getLevel().compareTo(h2.getLevel())
        );
        
        for (int i = 0; i < handlers.size() - 1; i++) {
            handlers.get(i).setNext(handlers.get(i + 1));
        }
    }
}
```

### 问题3: 异步处理中的竞态条件

**症状**:
- 多个线程同时修改处理链
- 请求处理顺序混乱
- 上下文丢失

**解决方案**:

```java
// ✅ 使用CopyOnWriteArrayList确保线程安全
class ThreadSafeChain {
    private final List<Handler> handlers = new CopyOnWriteArrayList<>();
    private final ExecutorService executor = Executors.newFixedThreadPool(4);
    
    public void addHandler(Handler handler) {
        handlers.add(handler);
    }
    
    public Future<Result> handleAsync(Request request) {
        return executor.submit(() -> {
            for (Handler handler : handlers) {
                if (handler.canHandle(request)) {
                    return handler.handle(request);
                }
            }
            return new Result(false, "Unhandled");
        });
    }
}

// ✅ 使用ThreadLocal保存请求上下文
class ContextAwareChain {
    private static final ThreadLocal<RequestContext> CONTEXT = new ThreadLocal<>();
    
    public void handle(Request request) {
        RequestContext context = new RequestContext(request);
        CONTEXT.set(context);
        try {
            process(request);
        } finally {
            CONTEXT.remove();
        }
    }
    
    protected RequestContext getContext() {
        return CONTEXT.get();
    }
}
```

### 问题4: 链未匹配时的异常处理

**症状**:
- 没有处理者能处理请求，返回null
- 调用者无法区分"未处理"和"处理失败"
- 应用状态不可控

**解决方案**:

```java
// ✅ 使用Result模式返回明确的结果
class ChainWithResult {
    abstract static class Result {
        public final boolean processed;
        public final String message;
        public final Object data;
        
        Result(boolean processed, String message, Object data) {
            this.processed = processed;
            this.message = message;
            this.data = data;
        }
    }
    
    abstract class Handler {
        protected Handler next;
        
        public Result handle(Request request) {
            if (canHandle(request)) {
                return new Result(true, "Processed", process(request));
            }
            if (next != null) {
                return next.handle(request);
            }
            return new Result(false, "No handler", null);
        }
        
        protected abstract boolean canHandle(Request request);
        protected abstract Object process(Request request);
    }
}

// 使用
Result result = chain.handle(request);
if (result.processed) {
    System.out.println("已处理: " + result.data);
} else {
    System.out.println("未处理: " + result.message);
    handleUnprocessed(request);
}

// ✅ 或使用异常处理
class ChainWithFallback {
    public Object handle(Request request) throws UnhandledException {
        try {
            return doHandle(request);
        } catch (Exception e) {
            if (fallbackHandler != null) {
                return fallbackHandler.handle(request);
            }
            throw new UnhandledException("Chain exhausted", e);
        }
    }
}
```

---

## 与其他模式的关系

| 模式 | 关系 | 何时结合 |
|--------|------|---------|
| **Command** | 责任链传递命令对象 | 当请求本身是对象时，如撤销/重做 |
| **Observer** | 都是处理事件，但方向不同 | 观察者是广播，责任链是线性查找 |
| **Strategy** | 策略选择处理方式，责任链选择处理者 | 结合确定由哪个策略处理 |
| **Template Method** | 定义处理步骤框架 | 与责任链结合定义固定处理流程 |
| **Decorator** | 都是包装和增强 | 使用装饰器动态添加处理者 |
| **Composite** | 组织处理者的树形结构 | 在树中传递请求 |
| **Mediator** | 都解耦对象间通信 | 中介者是中心协调，责任链是线性传递 |

---

## 最佳实践

### 1. 使用强类型请求对象
```java
// ✅ 好
abstract class BaseRequest {}
class EmailRequest extends BaseRequest { String email; }
class ValidationHandler {
    Result handle(BaseRequest req) {
        if (req instanceof EmailRequest) {
            // 处理...
        }
    }
}

// 不好
void handle(Object request) { // 弱类型，容易出错
    if (request instanceof String) { ... }
}
```

### 2. 定义清晰的处理契约
```java
// ✅ 定义接口，明确职责
interface Handler {
    /**
     * @return true如果自己处理了，false则传递给下一个
     */
    boolean handle(Request request);
    void setNext(Handler handler);
}

// 实现时遵循契约
class MyHandler implements Handler {
    @Override
    public boolean handle(Request request) {
        if (isMyDomain(request)) {
            doProcess(request);
            return true; // 已处理
        }
        return false; // 需要传递
    }
}
```

### 3. 避免"上帝处理者"
```java
// ❌ 一个处理者做太多事
class GodHandler {
    void handle(Request req) {
        // 验证、授权、日志、业务、发送邮件、缓存...
    }
}

// ✅ 职责分离
class ValidationHandler extends Handler { }
class AuthHandler extends Handler { }
class LoggingHandler extends Handler { }
class BusinessHandler extends Handler { }
```

### 4. 提供链的可视化和调试
```java
// ✅ 支持链的检视和调试
class DebugChain {
    public void printChain() {
        Handler current = head;
        int index = 0;
        while (current != null) {
            System.out.println(index + ": " + current.getClass().getName());
            current = current.getNext();
            index++;
        }
    }
    
    public void enableDebugLogging() {
        Handler current = head;
        while (current != null) {
            current.setDebugEnabled(true);
            current = current.getNext();
        }
    }
}
```

### 5. 避免无限循环
```java
// ❌ 危险
handler1.setNext(handler2);
handler2.setNext(handler1); // 循环!

// ✅ 检测循环
class ChainValidator {
    static void validate(Handler head) {
        Set<Handler> visited = new HashSet<>();
        Handler current = head;
        while (current != null) {
            if (visited.contains(current)) {
                throw new IllegalArgumentException("Circular chain!");
            }
            visited.add(current);
            current = current.getNext();
        }
    }
}
```

### 6. 使用现代Java特性
```java
// ✅ 使用Stream API简化链处理
class StreamChain {
    List<Handler> handlers = new ArrayList<>();
    
    public Result handle(Request req) {
        return handlers.stream()
            .filter(h -> h.canHandle(req))
            .findFirst()
            .map(h -> h.handle(req))
            .orElse(new Result(false, "Unhandled", null));
    }
}
```

---

## 何时避免使用

- ❌ **只有唯一处理者** - 直接调用即可，不需要责任链
- ❌ **需要所有处理者都处理** - 使用观察者模式代替
- ❌ **需要并行处理** - 使用线程池或响应式框架
- ❌ **处理者数量动态变化剧烈** - 维护成本高
- ❌ **性能要求极高且链很长** - 递归调用有开销

---

## 总结

责任链模式通过将请求处理转移给一系列处理者，实现了请求发送者和处理者的完全解耦。它特别适用于：
- 多个对象可能处理同一请求
- 处理者在运行时才被确定
- 需要动态组织处理流程

关键是**避免链断裂**、**管理好优先级**、**处理好异常情况**，才能充分发挥责任链的优势。
