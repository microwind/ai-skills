---
name: 面向切面编程
description: "将横切关注点（日志、事务、安全等）从业务逻辑中分离，通过切面统一处理。"
license: MIT
---

# 面向切面编程 (Aspect-Oriented Programming, AOP)

## 概述

AOP 解决**横切关注点**问题：日志、事务、安全、缓存等逻辑散布在多个模块中，AOP 将它们抽取到独立的"切面"中统一管理。

**核心概念**：
- **切面 (Aspect)**：横切关注点的模块化（如日志切面）
- **连接点 (Join Point)**：程序执行的点（如方法调用）
- **切入点 (Pointcut)**：匹配连接点的表达式
- **通知 (Advice)**：在切入点执行的逻辑（前置、后置、环绕）
- **织入 (Weaving)**：将切面应用到目标的过程

## Java Spring AOP

```java
// ❌ 没有 AOP：日志散布在每个方法中
public class OrderService {
    public void placeOrder(Order order) {
        log.info("开始下单: {}", order.getId());
        long start = System.currentTimeMillis();
        try {
            // 业务逻辑
            order.place();
            orderRepo.save(order);
            log.info("下单成功: {}", order.getId());
        } catch (Exception e) {
            log.error("下单失败: {}", order.getId(), e);
            throw e;
        } finally {
            log.info("下单耗时: {}ms", System.currentTimeMillis() - start);
        }
    }
}

// ✅ 使用 AOP：业务逻辑干净
public class OrderService {
    public void placeOrder(Order order) {
        order.place();
        orderRepo.save(order);
    }
}

// 切面统一处理日志
@Aspect
@Component
public class LoggingAspect {
    @Around("execution(* com.shop.service.*.*(..))")
    public Object log(ProceedingJoinPoint joinPoint) throws Throwable {
        String method = joinPoint.getSignature().getName();
        log.info("开始执行: {}", method);
        long start = System.currentTimeMillis();
        try {
            Object result = joinPoint.proceed();
            log.info("执行成功: {}, 耗时: {}ms", method, System.currentTimeMillis() - start);
            return result;
        } catch (Exception e) {
            log.error("执行失败: {}", method, e);
            throw e;
        }
    }
}

// 事务切面
@Aspect
@Component
public class TransactionAspect {
    @Around("@annotation(Transactional)")
    public Object manage(ProceedingJoinPoint joinPoint) throws Throwable {
        Transaction tx = txManager.begin();
        try {
            Object result = joinPoint.proceed();
            tx.commit();
            return result;
        } catch (Exception e) {
            tx.rollback();
            throw e;
        }
    }
}
```

## Python 装饰器（AOP 的体现）

```python
import time
import functools

# 日志切面
def log_method(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"调用: {func.__name__}")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            print(f"成功: {func.__name__}, 耗时: {time.time()-start:.3f}s")
            return result
        except Exception as e:
            print(f"失败: {func.__name__}, 错误: {e}")
            raise
    return wrapper

# 缓存切面
def cache(ttl=60):
    def decorator(func):
        _cache = {}
        @functools.wraps(func)
        def wrapper(*args):
            key = args
            if key in _cache and time.time() - _cache[key][1] < ttl:
                return _cache[key][0]
            result = func(*args)
            _cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator

# 重试切面
def retry(max_attempts=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(2 ** attempt)
        return wrapper
    return decorator

# 使用：业务代码干净
class OrderService:
    @log_method
    @retry(max_attempts=3)
    def place_order(self, order):
        order.place()
        self.repo.save(order)

    @cache(ttl=300)
    def get_order(self, order_id: str):
        return self.repo.find_by_id(order_id)
```

## TypeScript 装饰器

```typescript
// 日志装饰器
function Log(target: any, key: string, descriptor: PropertyDescriptor) {
    const original = descriptor.value;
    descriptor.value = function(...args: any[]) {
        console.log(`调用 ${key}，参数:`, args);
        const result = original.apply(this, args);
        console.log(`${key} 返回:`, result);
        return result;
    };
}

// 性能监控装饰器
function Measure(target: any, key: string, descriptor: PropertyDescriptor) {
    const original = descriptor.value;
    descriptor.value = async function(...args: any[]) {
        const start = Date.now();
        const result = await original.apply(this, args);
        console.log(`${key} 耗时: ${Date.now() - start}ms`);
        return result;
    };
}

class OrderService {
    @Log
    @Measure
    async placeOrder(orderId: string): Promise<Order> {
        // 纯业务逻辑，无横切关注点
        const order = await this.repo.findById(orderId);
        order.place();
        await this.repo.save(order);
        return order;
    }
}
```

## 常见横切关注点

| 关注点 | AOP 实现 |
|--------|---------|
| 日志记录 | 方法调用前后记录 |
| 事务管理 | 方法环绕开启/提交/回滚 |
| 权限校验 | 方法调用前检查权限 |
| 缓存 | 方法调用前查缓存，调用后写缓存 |
| 重试 | 方法失败时自动重试 |
| 性能监控 | 方法调用前后计时 |
| 异常处理 | 统一异常转换和日志 |

## 优缺点

### ✅ 优点
1. **关注点分离** — 业务代码不含横切逻辑
2. **代码复用** — 一个切面应用到多个方法
3. **集中管理** — 修改日志策略只需改一个地方
4. **非侵入** — 不修改原有代码

### ❌ 缺点
1. **隐式行为** — 代码背后有"魔法"，调试困难
2. **执行顺序** — 多个切面的执行顺序需要关注
3. **性能开销** — 反射/代理有微小性能损耗
4. **过度使用** — 一切都切面化会让代码不可读

## 与其他范式的关系

| 范式 | 关系 |
|------|------|
| [OOP](../object-oriented-programming/) | AOP 补充 OOP 难以处理的横切关注点 |
| [FP](../functional-programming/) | Python/TS 用装饰器（高阶函数）实现 AOP |
| [关注点分离](../../design-principles/separation-of-concerns/) | AOP 是 SoC 在横切维度的实现 |

## 总结

**核心**：将横切关注点从业务逻辑中分离到独立切面中。

**实践**：日志/事务/安全等用切面处理，保持业务代码纯净。Java 用 Spring AOP，Python/TS 用装饰器。
