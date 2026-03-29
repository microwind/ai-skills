---
name: 状态模式
description: "对象状态变化时改变行为。在需要根据状态改变行为时使用。"
license: MIT
---

# 状态模式 (State Pattern)

## 概述

状态模式允许对象在其内部状态改变时改变它的行为。通过将状态对象化，状态模式消除了大量的 if-else 分支判断，使得代码更清晰、易维护。

**核心原则**:
- 🎯 **状态对象化**: 每个状态都是一个独立的对象
- 🔄 **行为随状态变化**: 不同状态具有不同的行为
- 📋 **单一职责**: 每个状态类只负责一个状态的行为
- 🔗 **状态转移明确**: 状态间的转移规则清晰

## 何时使用

### 完美适用场景

| 场景 | 说明 | 优先级 |
|------|------|--------|
| **订单工作流** | 订单状态转移（待支付→已支付→处理中→发货→完成） | ⭐⭐⭐ |
| **工作流任务** | 任务状态（草稿→审核→处理→完成→归档） | ⭐⭐⭐ |
| **用户认证流程** | 从未认证→认证中→已认证→会话过期 | ⭐⭐⭐ |
| **游戏角色状态** | 正常→冰冻→燃烧→麻痹→死亡 | ⭐⭐⭐ |
| **文件上传** | 就绪→上传中→已上传→处理中→完成 | ⭐⭐ |
| **TCP连接** | 建立→监听→连接→传输→关闭 | ⭐⭐ |

### 触发信号

✅ 以下信号表明应该使用状态模式：
- "这个对象的行为会根据状态改变"
- "有很多 if-else 检查当前状态"
- "不同状态间需要明确的转移规则"
- "状态数量会不断增加"
- "需要明确文档化状态转移图"

❌ 以下情况不应该使用：
- 状态数量少于 3 个
- 状态转移规则简单固定
- 只是简单的数据持有者
- 需要动态添加状态（用策略模式）

## 状态模式的优缺点

### 优点 ✅

1. **消除条件分支**
   - 替代大部分 if-else 语句
   - 代码逻辑更清晰
   - 易于阅读和维护

2. **单一职责原则**
   - 每个状态类只负责一个状态
   - 职责明确，易于扩展
   - 代码复用性高

3. **开闭原则**
   - 易于添加新状态
   - 无需修改现有代码
   - 系统更灵活

4. **显式状态转移**
   - 状态转移规则清晰
   - 调试时容易追踪
   - 易于测试各个状态

### 缺点 ❌

1. **类数量增加**
   - 每个状态都需要一个类
   - 代码文件变多
   - 可能过度设计简单场景

2. **学习曲线**
   - 概念相对复杂
   - 初心者容易混淆 State vs Strategy
   - 需要理解状态机概念

3. **状态间通信**
   - 状态对象间通信需要小心处理
   - 可能导致强耦合
   - 需要合理的设计

## 状态模式的 5 种实现方法

### 1. 基础 State 模式 - 接口式

**特点**: 最标准的实现，每个状态都实现统一接口

```java
// 定义状态接口
public interface OrderState {
    void handle(Order order);
    String getName();
}

// 具体状态
public class PendingState implements OrderState {
    @Override
    public void handle(Order order) {
        System.out.println("Processing pending order");
        order.setState(new ProcessingState());  // 状态转移由状态自己决定
    }
    
    @Override public String getName() { return "PENDING"; }
}

public class ProcessingState implements OrderState {
    @Override
    public void handle(Order order) {
        System.out.println("Processing order");
        order.setState(new ShippedState());
    }
    
    @Override public String getName() { return "PROCESSING"; }
}

// 上下文对象
public class Order {
    private OrderState state = new PendingState();
    
    public void process() {
        state.handle(this);
    }
    
    public void setState(OrderState state) {
        this.state = state;
    }
}
```

---

### 2. StrategyState - 策略风格

**特点**: 状态和转移分离，转移规则集中管理

```java
public class Order {
    private OrderState state;
    private StateTransitionRules rules;
    
    public Order() {
        this.state = OrderState.PENDING;
        this.rules = new StateTransitionRules();
    }
    
    public void process() {
        // 状态不直接转移，而是通过规则系统
        OrderState nextState = rules.getNextState(state, "PROCESS");
        if (nextState != null) {
            state = nextState;
            System.out.println("State changed to: " + state);
        }
    }
}

// 集中管理转移规则
public class StateTransitionRules {
    private Map<String, Map<String, OrderState>> rules = new HashMap<>();
    
    public StateTransitionRules() {
        // 定义转移规则
        Map<String, OrderState> pendingRules = new HashMap<>();
        pendingRules.put("PROCESS", OrderState.PROCESSING);
        rules.put("PENDING", pendingRules);
    }
    
    public OrderState getNextState(OrderState current, String action) {
        return rules.getOrDefault(current.name(), new HashMap<>()).get(action);
    }
}
```

---

### 3. 枚举 State - 轻量级

**特点**: 使用枚举表示状态，代码简洁

```java
public enum OrderStatus {
    PENDING {
        @Override
        public OrderStatus nextState() {
            return PROCESSING;
        }
        
        @Override
        public void handle(Order order) {
            System.out.println("Order pending...");
        }
    },
    
    PROCESSING {
        @Override
        public OrderStatus nextState() {
            return SHIPPED;
        }
        
        @Override
        public void handle(Order order) {
            System.out.println("Order processing...");
        }
    },
    
    SHIPPED {
        @Override
        public OrderStatus nextState() {
            return COMPLETED;
        }
        
        @Override
        public void handle(Order order) {
            System.out.println("Order shipped...");
        }
    },
    
    COMPLETED {
        @Override
        public OrderStatus nextState() {
            return this;  // 终态
        }
        
        @Override
        public void handle(Order order) {
            System.out.println("Order completed");
        }
    };
    
    public abstract OrderStatus nextState();
    public abstract void handle(Order order);
}

public class Order {
    private OrderStatus status = OrderStatus.PENDING;
    
    public void process() {
        status.handle(this);
        status = status.nextState();
    }
}
```

---

### 4. 嵌套 State（带回退）

**特点**: 支持状态回退，保留历史状态

```java
public class Order {
    private OrderState state;
    private Stack<OrderState> history = new Stack<>();
    
    public Order() {
        this.state = new PendingState();
    }
    
    public void nextState() {
        history.push(state);  // 保存当前状态
        state = state.nextState(this);
        System.out.println("Next: " + state.getClass().getSimpleName());
    }
    
    public void previousState() {
        if (!history.isEmpty()) {
            state = history.pop();  // 恢复上一状态
            System.out.println("Back to: " + state.getClass().getSimpleName());
        }
    }
}

public interface OrderState {
    OrderState nextState(Order order);
}
```

---

### 5. 钩子 State（带前置和后置处理）

**特点**: 支持状态转入转出时的额外处理

```java
public abstract class OrderStateWithHooks implements OrderState {
    // 进入状态时调用
    public void onEnter(Order order) {}
    
    // 离开状态时调用
    public void onExit(Order order) {}
    
    // 处理业务逻辑
    public abstract void handle(Order order);
}

public class ProcessingStateWithHooks extends OrderStateWithHooks {
    @Override
    public void onEnter(Order order) {
        System.out.println("准备处理订单，检查库存...");
        order.checkInventory();
    }
    
    @Override
    public void handle(Order order) {
        System.out.println("处理中...");
    }
    
    @Override
    public void onExit(Order order) {
        System.out.println("订单已处理，发送通知...");
        order.notifyCustomer();
    }
}

public class Order {
    private OrderState state;
    
    public void setState(OrderState newState) {
        if (state instanceof OrderStateWithHooks) {
            ((OrderStateWithHooks) state).onExit(this);
        }
        
        this.state = newState;
        
        if (state instanceof OrderStateWithHooks) {
            ((OrderStateWithHooks) state).onEnter(this);
        }
    }
}
```

---

## 常见问题与完整解决方案

### 问题 1: 状态转移过于复杂

**症状**: 状态之间转移规则众多，容易出错

```java
// ❌ 混乱的转移
state -> pending -> processing -> shipped -> completed
             |  ↓           |  ↓
             └─ cancelled ←─┘

// ✅ 解决方案：明确文档化
/**
 * 订单状态转移图
 * 
 * PENDING ──process──→ PROCESSING ──ship──→ SHIPPED ──deliver──→ COMPLETED
 *    ↑                     |                    ↑                     ↑
 *    |                     cancel               |                     |
 *    |                     ↓                    refund                 |
 *    └──────────────────→ CANCELLED ←──────────────────→ REFUNDED ◄──┘
 */
public class OrderStateTransitionValidator {
    private static final Map<OrderState, Set<OrderState>> VALID_TRANSITIONS = 
        Map.ofEntries(
            Map.entry(OrderState.PENDING, Set.of(OrderState.PROCESSING, OrderState.CANCELLED)),
            Map.entry(OrderState.PROCESSING, Set.of(OrderState.SHIPPED, OrderState.CANCELLED)),
            Map.entry(OrderState.SHIPPED, Set.of(OrderState.COMPLETED, OrderState.REFUNDED))
        );
    
    public static boolean isValidTransition(OrderState from, OrderState to) {
        Set<OrderState> allowedStates = VALID_TRANSITIONS.getOrDefault(from, Set.of());
        return allowedStates.contains(to);
    }
}

// 使用
if (OrderStateTransitionValidator.isValidTransition(currentState, nextState)) {
    setState(nextState);
} else {
    throw new IllegalStateTransitionException(currentState, nextState);
}
```

### 问题 2: 状态间数据共享

**症状**: 不同状态需要访问相同的数据，导致强耦合

```java
// ✅ 解决方案：通过上下文对象传递数据
public class Order {
    // 共享数据
    private String id;
    private Customer customer;
    private List<Item> items;
    private OrderState state;
    
    // 状态只通过接口与Order交互
    public void process() {
        state.handle(this);  // 状态可以访问Order的数据
    }
}

public class ProcessingState implements OrderState {
    @Override
    public void handle(Order order) {
        // 通过order获取需要的数据
        List<Item> items = order.getItems();
        Customer customer = order.getCustomer();
        
        // 处理
        System.out.println("Processing order for: " + customer.getName());
        
        // 转移状态
        order.setState(new ShippedState());
    }
}
```

### 问题 3: 状态数量爆炸

**症状**: 需要过多的状态类，导致代码复杂

```java
// ✅ 解决方案：使用策略组合
public class OrderStateWithBehaviors {
    private OrderState mainState;  // 主状态
    private Set<OrderModifier> modifiers;  // 临时修饰符
    
    public OrderStateWithBehaviors() {
        this.modifiers = new HashSet<>();
    }
    
    public void addModifier(OrderModifier modifier) {
        modifiers.add(modifier);  // 添加临时修饰，而不是新增状态
    }
    
    public void handle() {
        // 先应用修饰符
        for (OrderModifier modifier : modifiers) {
            modifier.modify(this);
        }
        
        // 再处理主状态
        mainState.handle(this);
    }
}

// 例子：不用创建 "VIPProcessingState" 和 "NormalProcessingState"
// 而是用 Modifier 组合
OrderStateWithBehaviors order = new OrderStateWithBehaviors();
order.setMainState(new ProcessingState());
order.addModifier(new VIPModifier());  // 临时升级为VIP处理
order.addModifier(new FastShippingModifier());  // 添加快速发货
```

### 问题 4: 状态转移触发的异常处理

**症状**: 状态转移过程中出出现异常，导致数据不一致

```java
// ✅ 解决方案：事务性状态转移
public class TransactionalOrder {
    private OrderState state;
    private OrderState previousState;
    
    public void safeTransition(OrderStateTransition transition) {
        // 保存当前状态
        previousState = state;
        
        try {
            // 执行转移逻辑
            OrderState nextState = transition.execute(state);
            
            // 验证新状态合法性
            if (!validateStateTransition(state, nextState)) {
                throw new IllegalStateTransitionException();
            }
            
            // 执行状态改变
            this.state = nextState;
            
            System.out.println("State transition successful: " + previousState + " → " + nextState);
            
        } catch (Exception e) {
            // 回滚状态
            this.state = previousState;
            System.out.println("State transition failed, rolled back to: " + previousState);
            throw e;
        }
    }
    
    private boolean validateStateTransition(OrderState from, OrderState to) {
        // 验证转移规则
        return true;
    }
}
```

---

## 状态 vs 策略模式对比

| 维度 | 状态 | 策略 |
|------|------|------|
| **目的** | 状态改变行为 | 算法选择 |
| **初始化** | 对象创建时 | 客户端主动选择 |
| **转移** | 由状态对象自己决定 | 由客户端代码决定 |
| **上下文改变** | 状态改变时改变 | 策略改变时改变 |
| **示例** | 订单状态机 | 排序算法选择 |
| **何时使用** | "对象行为随状态变化" | "需要灵活切换算法" |

---

## 最佳实践

1. ✅ **状态职责单一** - 每个状态类只负责一个状态的行为
2. ✅ **明确文档化状态转移** - 使用图表说明转移规则
3. ✅ **状态间无直接耦合** - 通过上下文对象通信
4. ✅ **考虑使用状态机框架** - 复杂系统用标准框架
5. ✅ **提供状态转移验证** - 防止非法状态转移
6. ✅ **完善异常处理** - 转移失败时能回滚

---

## 何时避免使用

- ❌ 状态数量少于 3 个（直接用 if-else）
- ❌ 状态转移规则简单固定（用枚举）
- ❌ 只需要选择不同算法（用策略模式）
- ❌ 对象是无状态的数据容器
