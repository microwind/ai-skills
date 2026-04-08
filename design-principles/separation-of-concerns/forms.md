# 关注点分离 - 诊断与规划表

## 概述

关注点分离（Separation of Concerns, SoC）是软件设计中最基本的原则之一。
它要求将程序分解为功能上尽可能少重叠的模块，每个模块只负责一个"关注点"。
本表用于诊断代码中关注点混合的问题，并规划分离策略。

---

## 第一部分：关注点混合诊断

### 1.1 混合关注点的典型症状

| 症状 | 说明 | 严重程度 |
|------|------|----------|
| 一个类/函数超过 300 行 | 大概率混合了多个关注点 | 高 |
| 修改业务逻辑需要同时改数据库代码 | 业务与持久化耦合 | 高 |
| 修改 UI 显示需要重新测试后端逻辑 | 表现层与业务层耦合 | 高 |
| 单元测试需要启动数据库/网络 | 基础设施渗透到业务层 | 中 |
| 同一个函数里有 try-catch、日志、业务判断 | 横切关注点与核心逻辑混合 | 中 |
| 复制粘贴代码以适配不同场景 | 缺乏抽象分离 | 中 |

### 1.2 诊断检查清单

```
□ 该类/模块是否只有一个变化的原因？
□ 能否用一句话描述该模块的职责？
□ 修改该模块时，是否影响不相关的功能？
□ 测试该模块时，是否需要大量 mock？
□ 该模块是否依赖了不应该知道的实现细节？
□ 是否存在"上帝类"（God Class）或"上帝函数"？
```

### 1.3 混合代码示例（反面教材）

以下是一个典型的混合关注点代码——业务逻辑、数据库操作、邮件发送、
日志记录全部混在一个类中：

**Java:**

```java
// ❌ 所有关注点混在一起
public class OrderProcessor {

    public void processOrder(OrderRequest request) {
        // 关注点1: 输入验证
        if (request.getItems() == null || request.getItems().isEmpty()) {
            throw new IllegalArgumentException("订单不能为空");
        }
        if (request.getCustomerId() == null) {
            throw new IllegalArgumentException("客户ID不能为空");
        }
        for (OrderItem item : request.getItems()) {
            if (item.getQuantity() <= 0) {
                throw new IllegalArgumentException("数量必须大于0");
            }
        }

        // 关注点2: 数据库操作
        Connection conn = null;
        try {
            conn = DriverManager.getConnection("jdbc:mysql://localhost/orders");
            conn.setAutoCommit(false);

            // 关注点3: 业务逻辑（价格计算）
            double total = 0;
            for (OrderItem item : request.getItems()) {
                PreparedStatement ps = conn.prepareStatement(
                    "SELECT price FROM products WHERE id = ?");
                ps.setString(1, item.getProductId());
                ResultSet rs = ps.executeQuery();
                if (rs.next()) {
                    double price = rs.getDouble("price");
                    double discount = calculateDiscount(request.getCustomerId(), price);
                    total += (price - discount) * item.getQuantity();
                }
            }

            // 关注点4: 持久化
            PreparedStatement insertOrder = conn.prepareStatement(
                "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)");
            insertOrder.setString(1, request.getCustomerId());
            insertOrder.setDouble(2, total);
            insertOrder.setString(3, "PENDING");
            insertOrder.executeUpdate();
            conn.commit();

            // 关注点5: 通知
            String emailBody = "<h1>订单确认</h1><p>总金额: " + total + "</p>";
            Properties props = new Properties();
            props.put("mail.smtp.host", "smtp.example.com");
            Session session = Session.getDefaultInstance(props);
            MimeMessage message = new MimeMessage(session);
            message.setSubject("订单确认");
            message.setContent(emailBody, "text/html");
            Transport.send(message);

            // 关注点6: 日志
            System.out.println("[" + new Date() + "] 订单处理完成, 金额: " + total);

        } catch (Exception e) {
            // 关注点7: 错误处理（混杂回滚、日志、通知）
            System.err.println("订单处理失败: " + e.getMessage());
            try { if (conn != null) conn.rollback(); } catch (Exception ex) {}
            throw new RuntimeException("处理失败", e);
        }
    }
}
```

**Python:**

```python
# ❌ 所有关注点混在一起
class OrderProcessor:
    def process_order(self, request: dict):
        # 验证
        if not request.get("items"):
            raise ValueError("订单不能为空")
        if not request.get("customer_id"):
            raise ValueError("客户ID不能为空")

        # 数据库 + 业务逻辑 + 通知全部混合
        import pymysql
        conn = pymysql.connect(host="localhost", db="orders")
        cursor = conn.cursor()
        try:
            total = 0
            for item in request["items"]:
                cursor.execute(
                    "SELECT price FROM products WHERE id = %s", (item["product_id"],)
                )
                row = cursor.fetchone()
                if row:
                    price = row[0]
                    discount = self._calc_discount(request["customer_id"], price)
                    total += (price - discount) * item["quantity"]

            cursor.execute(
                "INSERT INTO orders (customer_id, total, status) VALUES (%s, %s, %s)",
                (request["customer_id"], total, "PENDING"),
            )
            conn.commit()

            # 发邮件
            import smtplib
            from email.mime.text import MIMEText
            msg = MIMEText(f"订单确认，总金额: {total}")
            msg["Subject"] = "订单确认"
            with smtplib.SMTP("smtp.example.com") as server:
                server.send_message(msg)

            print(f"[{datetime.now()}] 订单处理完成, 金额: {total}")

        except Exception as e:
            conn.rollback()
            print(f"订单处理失败: {e}")
            raise
```

**TypeScript:**

```typescript
// ❌ 所有关注点混在一起
class OrderProcessor {
  async processOrder(request: OrderRequest): Promise<void> {
    // 验证
    if (!request.items?.length) throw new Error("订单不能为空");
    if (!request.customerId) throw new Error("客户ID不能为空");

    // 数据库
    const pool = mysql.createPool({ host: "localhost", database: "orders" });
    const conn = await pool.getConnection();
    try {
      let total = 0;
      for (const item of request.items) {
        const [rows] = await conn.query(
          "SELECT price FROM products WHERE id = ?", [item.productId]
        );
        if (rows[0]) {
          const price = rows[0].price;
          const discount = this.calcDiscount(request.customerId, price);
          total += (price - discount) * item.quantity;
        }
      }
      await conn.query(
        "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)",
        [request.customerId, total, "PENDING"]
      );
      await conn.commit();

      // 发邮件
      await transporter.sendMail({
        subject: "订单确认",
        html: `<h1>订单确认</h1><p>总金额: ${total}</p>`,
      });
      console.log(`[${new Date()}] 订单处理完成, 金额: ${total}`);
    } catch (e) {
      await conn.rollback();
      console.error("订单处理失败:", e);
      throw e;
    }
  }
}
```

---

## 第二部分：关注点识别

### 2.1 关注点分类矩阵

| 关注点类型 | 示例 | 分离方式 |
|-----------|------|----------|
| **核心业务逻辑** | 价格计算、折扣规则、库存判断 | 纯函数/领域服务 |
| **数据持久化** | SQL查询、ORM操作、缓存读写 | Repository模式 |
| **输入验证** | 参数校验、格式检查、权限验证 | Validator/Guard |
| **表现层** | HTML渲染、JSON序列化、响应格式 | Controller/View |
| **外部通信** | 邮件发送、消息队列、第三方API | Gateway/Adapter |
| **横切关注点** | 日志、监控、事务、安全 | AOP/中间件/装饰器 |

### 2.2 识别练习模板

```
模块名称: _______________
当前职责（列出所有）:
  1. _______________
  2. _______________
  3. _______________

哪些职责应该分离？
  □ 职责1 → 应归属: _______________
  □ 职责2 → 应归属: _______________
  □ 职责3 → 应归属: _______________

分离后的依赖关系:
  模块A → 模块B（通过接口）
  模块A → 模块C（通过事件）
```

---

## 第三部分：分离策略

### 3.1 按层分离（Layered Architecture）

```
┌─────────────────────────────────┐
│       表现层 (Presentation)      │  → 处理HTTP请求/响应
├─────────────────────────────────┤
│       应用层 (Application)       │  → 编排业务用例
├─────────────────────────────────┤
│       领域层 (Domain)            │  → 核心业务规则
├─────────────────────────────────┤
│       基础设施层 (Infrastructure) │  → 数据库、外部服务
└─────────────────────────────────┘
```

### 3.2 按模块分离（Modular Architecture）

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  订单模块  │  │  用户模块  │  │  支付模块  │
│          │  │          │  │          │
│ - 验证   │  │ - 注册   │  │ - 扣款   │
│ - 计算   │  │ - 登录   │  │ - 退款   │
│ - 存储   │  │ - 权限   │  │ - 对账   │
└──────────┘  └──────────┘  └──────────┘
```

### 3.3 按组件分离（Component-based）

适用于前端场景：

```
┌─────────────────────────────────────┐
│ OrderPage                           │
│  ├── OrderForm (表单输入)            │
│  ├── OrderSummary (订单汇总)         │
│  ├── useOrderValidation (验证逻辑)   │
│  ├── useOrderApi (API调用)           │
│  └── orderUtils.ts (纯计算)          │
└─────────────────────────────────────┘
```

---

## 第四部分：横切关注点处理

### 4.1 AOP 方式（Java）

```java
// 使用注解 + AOP 处理日志、事务等横切关注点
@Aspect
@Component
public class LoggingAspect {

    @Around("@annotation(Loggable)")
    public Object logExecution(ProceedingJoinPoint joinPoint) throws Throwable {
        String method = joinPoint.getSignature().getName();
        log.info("开始执行: {}", method);
        long start = System.currentTimeMillis();
        try {
            Object result = joinPoint.proceed();
            log.info("执行完成: {}, 耗时: {}ms", method, System.currentTimeMillis() - start);
            return result;
        } catch (Throwable e) {
            log.error("执行失败: {}, 错误: {}", method, e.getMessage());
            throw e;
        }
    }
}

// 业务代码保持干净
@Service
public class OrderService {

    @Loggable
    @Transactional
    public Order createOrder(OrderRequest request) {
        // 只有纯业务逻辑，没有日志和事务管理代码
        Order order = orderFactory.create(request);
        return orderRepository.save(order);
    }
}
```

### 4.2 装饰器方式（Python）

```python
import functools
import logging
import time

logger = logging.getLogger(__name__)

def log_execution(func):
    """日志横切关注点"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"开始执行: {func.__name__}")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"执行完成: {func.__name__}, 耗时: {elapsed:.3f}s")
            return result
        except Exception as e:
            logger.error(f"执行失败: {func.__name__}, 错误: {e}")
            raise
    return wrapper

def transactional(func):
    """事务横切关注点"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        session = self.session_factory()
        try:
            result = func(self, *args, session=session, **kwargs)
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    return wrapper

# 业务代码保持干净
class OrderService:
    @log_execution
    @transactional
    def create_order(self, request: dict, session=None) -> Order:
        order = Order.from_request(request)
        session.add(order)
        return order
```

### 4.3 中间件方式（TypeScript / Express）

```typescript
// 日志中间件
function loggingMiddleware(req: Request, res: Response, next: NextFunction) {
  const start = Date.now();
  res.on("finish", () => {
    console.log(`${req.method} ${req.path} ${res.statusCode} ${Date.now() - start}ms`);
  });
  next();
}

// 认证中间件
function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization;
  if (!token) return res.status(401).json({ error: "未认证" });
  try {
    req.user = verifyToken(token);
    next();
  } catch {
    res.status(403).json({ error: "令牌无效" });
  }
}

// 路由只关注业务
app.use(loggingMiddleware);
app.use("/api", authMiddleware);

app.post("/api/orders", async (req, res) => {
  // 只有业务逻辑——日志和认证已由中间件处理
  const order = await orderService.createOrder(req.body);
  res.status(201).json(order);
});
```

---

## 第五部分：五大常见陷阱

### 陷阱 1：过度分离

```
❌ 把一个简单的 CRUD 拆成 8 层
   Controller → DTO → Service → Domain → Repository → DAO → Entity → DB

✅ 简单场景用简单结构
   Controller → Service → Repository → DB
```

**诊断**: 如果每层只是简单透传，没有独立逻辑，说明分离过度。

### 陷阱 2：只分层不分模块

```
❌ 所有 Service 在一个包里，所有 Repository 在一个包里
   services/
     OrderService.java
     UserService.java
     PaymentService.java    ← 跨模块依赖不清晰

✅ 先按业务模块分，再按层分
   order/
     OrderService.java
     OrderRepository.java
   user/
     UserService.java
     UserRepository.java
```

### 陷阱 3：用继承代替组合

```java
// ❌ 用继承"分离"关注点
class OrderService extends LoggableTransactionalService {
    // 继承链越来越长，关注点实际上更紧耦合了
}

// ✅ 用组合和依赖注入
class OrderService {
    private final OrderRepository repository;
    private final NotificationService notification;
    // 每个依赖是独立的关注点
}
```

### 陷阱 4：横切关注点硬编码

```python
# ❌ 每个方法都重复日志/监控代码
class UserService:
    def create_user(self, data):
        logger.info("创建用户开始")        # 重复
        start = time.time()                # 重复
        try:
            user = User(**data)
            self.repo.save(user)
            logger.info(f"创建用户完成, 耗时: {time.time()-start}")  # 重复
            return user
        except Exception as e:
            logger.error(f"创建用户失败: {e}")  # 重复
            raise

# ✅ 用装饰器/AOP统一处理
class UserService:
    @log_execution
    def create_user(self, data):
        user = User(**data)
        return self.repo.save(user)
```

### 陷阱 5：前端组件承担过多职责

```typescript
// ❌ 组件同时处理 UI、状态、API、业务逻辑
function OrderPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch("/api/orders")
      .then(res => res.json())
      .then(data => {
        // 业务逻辑：过滤、排序、计算
        const filtered = data.filter(o => o.status !== "CANCELLED");
        const sorted = filtered.sort((a, b) => b.createdAt - a.createdAt);
        const withTotals = sorted.map(o => ({
          ...o,
          displayTotal: `¥${(o.total / 100).toFixed(2)}`,
        }));
        setOrders(withTotals);
      })
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  // 200行JSX...
}

// ✅ 分离关注点
function OrderPage() {
  const { orders, loading, error } = useOrders();  // 数据获取
  const displayOrders = useOrderDisplay(orders);     // 展示逻辑

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <OrderList orders={displayOrders} />;       // 纯渲染
}
```

---

## 第六部分：规划模板

### 分离规划表

```
项目/模块: _______________
当前代码行数: _______________
识别出的关注点数量: _______________

分离计划:
┌────┬──────────────┬──────────────┬──────────┬─────────┐
│ #  │ 关注点        │ 目标模块      │ 分离方式  │ 优先级   │
├────┼──────────────┼──────────────┼──────────┼─────────┤
│ 1  │              │              │          │ P0/P1/P2│
│ 2  │              │              │          │         │
│ 3  │              │              │          │         │
│ 4  │              │              │          │         │
└────┴──────────────┴──────────────┴──────────┴─────────┘

预期效果:
  □ 每个模块可独立测试
  □ 修改一个关注点不影响其他关注点
  □ 新增功能只需修改对应模块
  □ 横切关注点统一管理

风险评估:
  □ 分离是否会引入过多间接层？
  □ 团队是否熟悉目标架构模式？
  □ 是否有足够的测试覆盖来保障重构安全？
```

---

## 附录：快速决策流程图

```
代码是否超过 200 行？
  │
  ├─ 否 → 是否有多个变化原因？
  │         ├─ 否 → 暂不分离
  │         └─ 是 → 按职责拆分
  │
  └─ 是 → 识别关注点
           │
           ├─ 核心业务 → 提取到领域层
           ├─ 数据访问 → 提取到 Repository
           ├─ 外部通信 → 提取到 Gateway/Adapter
           ├─ 输入验证 → 提取到 Validator
           └─ 日志/监控 → 用 AOP/装饰器/中间件
```
