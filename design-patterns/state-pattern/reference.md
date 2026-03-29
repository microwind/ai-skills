# 状态模式完整参考实现

## UML 类图

```
       ┌─────────────┐
       │   Context   │
       ├─────────────┤
       │ - state     │
       │ + request() │
       └──────┬──────┘
              │
              ├─→ ┌─────────────┐
              │   │   State     │ ← 接口
              │   ├─────────────┤
              │   │ + handle()  │
              │   └─────────────┘
              │
              ├─→ ┌──────────────┐
              │   │ StateA       │
              │   ├──────────────┤
              │   │ + handle()   │
              │   └──────────────┘
              │
              └─→ ┌──────────────┐
                  │ StateB       │
                  ├──────────────┤
                  │ + handle()   │
                  └──────────────┘
```

---

## Java: 完整订单处理系统示例

### 基础类定义

```java
import java.time.LocalDateTime;
import java.util.*;

// ===== 订单类 (上下文) =====
public class Order {
    private String orderId;
    private Customer customer;
    private List<OrderItem> items;
    private OrderState state;
    private LocalDateTime createdTime;
    private double totalAmount;
    private List<StateChangeRecord> history;
    
    public Order(String orderId, Customer customer) {
        this.orderId = orderId;
        this.customer = customer;
        this.items = new ArrayList<>();
        this.state = new PendingState();
        this.createdTime = LocalDateTime.now();
        this.history = new ArrayList<>();
        recordStateChange("PENDING");
    }
    
    // ===== 状态操作 =====
    
    public void pay(PaymentInfo payment) {
        System.out.println("[Order] Attempting payment...");
        state.pay(this, payment);
    }
    
    public void ship(ShippingInfo shipping) {
        System.out.println("[Order] Attempting to ship...");
        state.ship(this, shipping);
    }
    
    public void deliver() {
        System.out.println("[Order] Attempting delivery...");
        state.deliver(this);
    }
    
    public void cancel(String reason) {
        System.out.println("[Order] Attempting cancellation: " + reason);
        state.cancel(this, reason);
    }
    
    public void refund() {
        System.out.println("[Order] Attempting refund...");
        state.refund(this);
    }
    
    // ===== 状态转移 =====
    
    public void setState(OrderState newState) {
        if (newState == null) {
            throw new IllegalStateException("Cannot set null state");
        }
        OrderState oldState = this.state;
        this.state = newState;
        recordStateChange(newState.getStateName());
        System.out.printf("[Order] State changed: %s → %s\n", 
            oldState.getStateName(), newState.getStateName());
    }
    
    // ===== 业务操作 =====
    
    public void addItem(OrderItem item) {
        if (!(state instanceof PendingState)) {
            throw new IllegalStateException("Can only add items when pending");
        }
        items.add(item);
        totalAmount += item.getPrice();
    }
    
    public void processPayment(PaymentInfo payment) {
        System.out.println("[Order] Processing payment: $" + payment.getAmount());
        // 模拟支付处理
        setState(new ProcessingState());
    }
    
    public void shipOrder(ShippingInfo shipping) {
        System.out.println("[Order] Shipping to: " + shipping.getAddress());
        // 模拟发货
        setState(new ShippedState());
    }
    
    public void deliverOrder() {
        System.out.println("[Order] Delivered successfully");
        setState(new DeliveredState());
    }
    
    public void cancelOrder(String reason) {
        System.out.println("[Order] Order cancelled: " + reason);
        setState(new CancelledState());
    }
    
    public void refundOrder() {
        System.out.println("[Order] Processing refund...");
        setState(new RefundedState());
    }
    
    // ===== 历史记录 =====
    
    private void recordStateChange(String toState) {
        history.add(new StateChangeRecord(toState, LocalDateTime.now()));
    }
    
    public void printHistory() {
        System.out.println("\n=== Order State History ===");
        for (StateChangeRecord record : history) {
            System.out.printf("→ %s at %s\n", record.state, record.time);
        }
    }
    
    // Getters
    public String getOrderId() { return orderId; }
    public OrderState getState() { return state; }
    public Customer getCustomer() { return customer; }
    public List<OrderItem> getItems() { return items; }
    public double getTotalAmount() { return totalAmount; }
}

// ===== 订单状态接口 =====
public interface OrderState {
    void pay(Order order, PaymentInfo payment);
    void ship(Order order, ShippingInfo shipping);
    void deliver(Order order);
    void cancel(Order order, String reason);
    void refund(Order order);
    String getStateName();
}

// ===== 具体状态 =====

public class PendingState implements OrderState {
    @Override
    public void pay(Order order, PaymentInfo payment) {
        if (payment.getAmount() < order.getTotalAmount()) {
            throw new IllegalArgumentException("Payment insufficient");
        }
        order.processPayment(payment);
    }
    
    @Override
    public void ship(Order order, ShippingInfo shipping) {
        throw new IllegalStateException("Cannot ship unpaid order");
    }
    
    @Override
    public void deliver(Order order) {
        throw new IllegalStateException("Order not shipped yet");
    }
    
    @Override
    public void cancel(Order order, String reason) {
        order.cancelOrder(reason);
    }
    
    @Override
    public void refund(Order order) {
        throw new IllegalStateException("No payment to refund");
    }
    
    @Override
    public String getStateName() { return "PENDING"; }
}

public class ProcessingState implements OrderState {
    @Override
    public void pay(Order order, PaymentInfo payment) {
        throw new IllegalStateException("Already paid");
    }
    
    @Override
    public void ship(Order order, ShippingInfo shipping) {
        order.shipOrder(shipping);
    }
    
    @Override
    public void deliver(Order order) {
        throw new IllegalStateException("Not shipped yet");
    }
    
    @Override
    public void cancel(Order order, String reason) {
        order.refundOrder();
        order.cancelOrder(reason);
    }
    
    @Override
    public void refund(Order order) {
        throw new IllegalStateException("Order not yet complete");
    }
    
    @Override
    public String getStateName() { return "PROCESSING"; }
}

public class ShippedState implements OrderState {
    @Override
    public void pay(Order order, PaymentInfo payment) {
        throw new IllegalStateException("Already paid");
    }
    
    @Override
    public void ship(Order order, ShippingInfo shipping) {
        throw new IllegalStateException("Already shipped");
    }
    
    @Override
    public void deliver(Order order) {
        order.deliverOrder();
    }
    
    @Override
    public void cancel(Order order, String reason) {
        throw new IllegalStateException("Cannot cancel shipped order");
    }
    
    @Override
    public void refund(Order order) {
        throw new IllegalStateException("Order not delivered");
    }
    
    @Override
    public String getStateName() { return "SHIPPED"; }
}

public class DeliveredState implements OrderState {
    @Override
    public void pay(Order order, PaymentInfo payment) {
        throw new IllegalStateException("Order complete");
    }
    
    @Override
    public void ship(Order order, ShippingInfo shipping) {
        throw new IllegalStateException("Order complete");
    }
    
    @Override
    public void deliver(Order order) {
        throw new IllegalStateException("Already delivered");
    }
    
    @Override
    public void cancel(Order order, String reason) {
        order.refundOrder();
    }
    
    @Override
    public void refund(Order order) {
        order.refundOrder();
    }
    
    @Override
    public String getStateName() { return "DELIVERED"; }
}

public class CancelledState implements OrderState {
    @Override
    public void pay(Order order, PaymentInfo payment) {
        throw new IllegalStateException("Order cancelled");
    }
    
    @Override
    public void ship(Order order, ShippingInfo shipping) {
        throw new IllegalStateException("Order cancelled");
    }
    
    @Override
    public void deliver(Order order) {
        throw new IllegalStateException("Order cancelled");
    }
    
    @Override
    public void cancel(Order order, String reason) {
        throw new IllegalStateException("Already cancelled");
    }
    
    @Override
    public void refund(Order order) {
        throw new IllegalStateException("Already cancelled");
    }
    
    @Override
    public String getStateName() { return "CANCELLED"; }
}

public class RefundedState implements OrderState {
    @Override
    public void pay(Order order, PaymentInfo payment) {
        throw new IllegalStateException("Refund completed");
    }
    
    @Override
    public void ship(Order order, ShippingInfo shipping) {
        throw new IllegalStateException("Order refunded");
    }
    
    @Override
    public void deliver(Order order) {
        throw new IllegalStateException("Order refunded");
    }
    
    @Override
    public void cancel(Order order, String reason) {
        throw new IllegalStateException("Already refunded");
    }
    
    @Override
    public void refund(Order order) {
        throw new IllegalStateException("Already refunded");
    }
    
    @Override
    public String getStateName() { return "REFUNDED"; }
}

// ===== 辅助类 =====

public class Customer {
    private String id;
    private String name;
    private String email;
    
    public Customer(String id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }
    
    public String getName() { return name; }
}

public class OrderItem {
    private String productId;
    private String productName;
    private int quantity;
    private double price;
    
    public OrderItem(String productId, String productName, int qty, double price) {
        this.productId = productId;
        this.productName = productName;
        this.quantity = qty;
        this.price = price * qty;
    }
    
    public double getPrice() { return price; }
}

public class PaymentInfo {
    private String method;
    private double amount;
    private String transactionId;
    
    public PaymentInfo(String method, double amount) {
        this.method = method;
        this.amount = amount;
        this.transactionId = UUID.randomUUID().toString();
    }
    
    public double getAmount() { return amount; }
}

public class ShippingInfo {
    private String address;
    private String carrier;
    private String trackingNumber;
    
    public ShippingInfo(String address, String carrier) {
        this.address = address;
        this.carrier = carrier;
        this.trackingNumber = UUID.randomUUID().toString();
    }
    
    public String getAddress() { return address; }
}

public class StateChangeRecord {
    public String state;
    public LocalDateTime time;
    
    public StateChangeRecord(String state, LocalDateTime time) {
        this.state = state;
        this.time = time;
    }
}
```

### 使用示例

```java
class OrderProcessingTest {
    public static void main(String[] args) {
        System.out.println("=== 订单处理流程示例 ===\n");
        
        // 创建订单
        Customer customer = new Customer("C001", "张三", "zhangsan@example.com");
        Order order = new Order("ORD001", customer);
        
        // 添加商品
        System.out.println("--- 添加商品 ---");
        order.addItem(new OrderItem("P001", "笔记本", 1, 5999));
        order.addItem(new OrderItem("P002", "鼠标", 2, 99));
        System.out.println("订单总额: $" + order.getTotalAmount());
        
        // 支付
        System.out.println("\n--- 支付 ---");
        PaymentInfo payment = new PaymentInfo("支付宝", 6197);
        order.pay(payment);
        
        // 发货
        System.out.println("\n--- 发货 ---");
        ShippingInfo shipping = new ShippingInfo("北京市朝阳区", "圆通快递");
        order.ship(shipping);
        
        // 收货
        System.out.println("\n--- 收货 ---");
        order.deliver();
        
        // 退货
        System.out.println("\n--- 退货 ---");
        order.refund();
        
        // 打印历史
        order.printHistory();
        
        System.out.println("\n╔════════════════════════════════╗");
        System.out.println("║   最终状态: " + order.getState().getStateName() + "     ║");
        System.out.println("╚════════════════════════════════╝");
    }
}
```

---

## Python: 使用__getattr__动态处理

```python
from datetime import datetime
from typing import Any, Callable, Dict, List
from enum import Enum

class OrderState(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class Order:
    """订单类 - 支持状态机"""
    
    def __init__(self, order_id: str, customer_name: str):
        self.order_id = order_id
        self.customer_name = customer_name
        self.state = OrderState.PENDING
        self.items: List[Dict] = []
        self.total_amount = 0.0
        self.history: List[tuple] = [(OrderState.PENDING, datetime.now())]
        
        # 定义状态转移规则
        self.state_handlers: Dict[OrderState, Dict[str, Callable]] = {
            OrderState.PENDING: {
                'pay': self._pay_pending,
                'cancel': self._cancel_any,
            },
            OrderState.PROCESSING: {
                'ship': self._ship_processing,
                'cancel': self._refund_cancel,
            },
            OrderState.SHIPPED: {
                'deliver': self._deliver_shipped,
            },
            OrderState.DELIVERED: {
                'refund': self._refund_delivered,
            },
            OrderState.CANCELLED: {},
            OrderState.REFUNDED: {},
        }
    
    def __getattr__(self, name: str) -> Any:
        """动态拦截方法调用"""
        if name in self.state_handlers[self.state]:
            handler = self.state_handlers[self.state][name]
            return lambda *args, **kwargs: self._execute_action(name, handler, *args, **kwargs)
        raise AttributeError(f"订单在 {self.state.value} 状态下不支持 {name} 操作")
    
    def _execute_action(self, action: str, handler: Callable, *args, **kwargs):
        """执行操作并更新状态"""
        print(f"[Order] Executing {action}...")
        try:
            new_state = handler(*args, **kwargs)
            if new_state:
                self._change_state(new_state)
            return True
        except Exception as e:
            print(f"[Error] {e}")
            return False
    
    def _change_state(self, new_state: OrderState):
        """转移状态"""
        old_state = self.state
        self.state = new_state
        self.history.append((new_state, datetime.now()))
        print(f"[State] {old_state.value} → {new_state.value}")
    
    # ===== 状态处理器 =====
    
    def _pay_pending(self, amount: float):
        """待支付状态：支付"""
        if amount >= self.total_amount:
            print(f"[Payment] 处理支付: ${amount}")
            return OrderState.PROCESSING
        else:
            raise ValueError("支付金额不足")
    
    def _ship_processing(self, address: str, carrier: str):
        """处理中状态：发货"""
        print(f"[Shipping] 发货到: {address}, 承运商: {carrier}")
        return OrderState.SHIPPED
    
    def _deliver_shipped(self):
        """已发货状态：收货"""
        print("[Delivery] 订单已收货")
        return OrderState.DELIVERED
    
    def _refund_delivered(self):
        """已交付状态：退款"""
        print("[Refund] 处理退款")
        return OrderState.REFUNDED
    
    def _refund_cancel(self, reason: str = ""):
        """处理中状态：取消并退款"""
        print(f"[Cancel] 订单取消: {reason}, 处理退款")
        # 这里会先取消再转到REFUNDED
        self._change_state(OrderState.CANCELLED)
        return OrderState.REFUNDED
    
    def _cancel_any(self, reason: str = ""):
        """任何状态：取消"""
        print(f"[Cancel] 订单取消: {reason}")
        return OrderState.CANCELLED
    
    def add_item(self, product_id: str, name: str, qty: int, price: float):
        """添加商品"""
        if self.state != OrderState.PENDING:
            raise ValueError("只能在待支付状态下添加商品")
        self.items.append({'id': product_id, 'name': name, 'qty': qty, 'price': price})
        self.total_amount += qty * price
        print(f"[Item] 已添加: {name}")
    
    def print_history(self):
        """打印订单历史"""
        print("\n=== 订单状态变更历史 ===")
        for state, time in self.history:
            print(f"→ {state.value} at {time.strftime('%Y-%m-%d %H:%M:%S')}")

# 使用示例
if __name__ == "__main__":
    order = Order("ORD001", "张三")
    
    # 添加商品
    order.add_item("P001", "笔记本", 1, 5999)
    order.add_item("P002", "鼠标", 2, 99)
    print(f"总额: ${order.total_amount}\n")
    
    # 支付
    order.pay(6197)
    
    # 发货
    order.ship("北京市朝阳区", "圆通快递")
    
    # 收货
    order.deliver()
    
    # 退款
    order.refund()
    
    # 历史
    order.print_history()
```

---

## TypeScript: 使用 Proxy 和 DecoratorPattern

```typescript
// 状态定义
type OrderStateType = 'PENDING' | 'PROCESSING' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED' | 'REFUNDED';

interface StateHandler {
    pay?(amount: number): void;
    ship?(address: string): void;
    deliver?(): void;
    cancel?(reason: string): void;
    refund?(): void;
}

// 状态转换规则
const stateTransitions: Record<OrderStateType, StateHandler> = {
    'PENDING': {
        pay: function(this: Order, amount: number) {
            console.log(`[Payment] 处理支付: $${amount}`);
            this.changeState('PROCESSING');
        },
        cancel: function(this: Order, reason: string) {
            console.log(`[Cancel] 订单取消: ${reason}`);
            this.changeState('CANCELLED');
        }
    },
    'PROCESSING': {
        ship: function(this: Order, address: string) {
            console.log(`[Shipping] 发货到: ${address}`);
            this.changeState('SHIPPED');
        },
        cancel: function(this: Order, reason: string) {
            console.log(`[Refund] 取消并退款: ${reason}`);
            this.changeState('REFUNDED');
        }
    },
    'SHIPPED': {
        deliver: function(this: Order) {
            console.log("[Delivery] 订单已收货");
            this.changeState('DELIVERED');
        }
    },
    'DELIVERED': {
        refund: function(this: Order) {
            console.log("[Refund] 处理退款");
            this.changeState('REFUNDED');
        }
    },
    'CANCELLED': {},
    'REFUNDED': {}
};

class Order {
    private orderId: string;
    private customerName: string;
    private state: OrderStateType = 'PENDING';
    private totalAmount: number = 0;
    private history: Array<{state: OrderStateType, time: Date}> = [];
    
    constructor(orderId: string, customerName: string) {
        this.orderId = orderId;
        this.customerName = customerName;
        this.recordState('PENDING');
    }
    
    // ===== 使用 Proxy 实现动态方法调用 =====
    private createProxy() {
        return new Proxy(this, {
            get: (target, prop: string) => {
                const handler = stateTransitions[target.state as OrderStateType][prop as keyof StateHandler];
                
                if (!handler) {
                    throw new Error(`当前状态 ${target.state} 不支持操作: ${prop}`);
                }
                
                return (...args: any[]) => {
                    handler.apply(target, args);
                };
            }
        });
    }
    
    // ===== 状态转换 =====
    private changeState(newState: OrderStateType) {
        const oldState = this.state;
        this.state = newState;
        this.recordState(newState);
        console.log(`[State] ${oldState} → ${newState}\n`);
    }
    
    private recordState(state: OrderStateType) {
        this.history.push({ state, time: new Date() });
    }
    
    // ===== 公共接口 =====
    public pay(amount: number) {
        const proxy = this.createProxy();
        return proxy.pay(amount);
    }
    
    public ship(address: string) {
        const proxy = this.createProxy();
        return proxy.ship(address);
    }
    
    public deliver() {
        const proxy = this.createProxy();
        return proxy.deliver();
    }
    
    public cancel(reason: string) {
        const proxy = this.createProxy();
        return proxy.cancel(reason);
    }
    
    public refund() {
        const proxy = this.createProxy();
        return proxy.refund();
    }
    
    public getState(): OrderStateType {
        return this.state;
    }
    
    public printHistory() {
        console.log("\n=== 订单状态变更历史 ===");
        this.history.forEach(({state, time}) => {
            console.log(`→ ${state} at ${time.toLocaleString()}`);
        });
    }
}

// 使用示例
const order = new Order("ORD001", "张三");

console.log("=== 订单处理流程 ===\n");

console.log("--- 支付 ---");
order.pay(6197);

console.log("--- 发货 ---");
order.ship("北京市朝阳区");

console.log("--- 收货 ---");
order.deliver();

console.log("--- 退款 ---");
order.refund();

console.log(`最终状态: ${order.getState()}`);
order.printHistory();
```

---

## 单元测试示例

```java
@Test
public void testValidTransitions() {
    Order order = new Order("TEST001", new Customer("C001", "Test", "test@test.com"));
    
    // PENDING → PROCESSING
    PaymentInfo payment = new PaymentInfo("card", 100);
    order.pay(payment);
    assertEquals("PROCESSING", order.getState().getStateName());
    
    // PROCESSING → SHIPPED
    ShippingInfo shipping = new ShippingInfo("Address", "Carrier");
    order.ship(shipping);
    assertEquals("SHIPPED", order.getState().getStateName());
    
    // SHIPPED → DELIVERED
    order.deliver();
    assertEquals("DELIVERED", order.getState().getStateName());
}

@Test
public void testInvalidTransitions() {
    Order order = new Order("TEST002", new Customer("C002", "Test2", "test2@test.com"));
    
    // Cannot deliver from PENDING
    assertThrows(IllegalStateException.class, () -> order.deliver());
    
    // Cannot ship from PENDING (before payment)
    assertThrows(IllegalStateException.class, 
        () -> order.ship(new ShippingInfo("addr", "carrier")));
}

@Test
public void testCancellation() {
    Order order = new Order("TEST003", new Customer("C003", "Test3", "test3@test.com"));
    
    // Can cancel from PENDING
    order.cancel("Changed mind");
    assertEquals("CANCELLED", order.getState().getStateName());
}
```

---

## 性能对比与最佳实践

| 实现方式 | 内存占用 | 执行速度 | 灵活性 | 推荐度 |
|---------|---------|---------|--------|--------|
| 接口式 | 低 | ⭐⭐⭐⭐⭐ | 高 | ⭐⭐⭐ |
| 枚举式 | 很低 | ⭐⭐⭐⭐⭐ | 中 | ⭐⭐⭐ |
| 钩子式 | 低 | ⭐⭐⭐ | 很高 | ⭐⭐ |
| Python 动态 | 中 | ⭐⭐ | 很高 | ⭐⭐ |
| TypeScript Proxy | 中 | ⭐⭐⭐ | 很高 | ⭐⭐⭐ |

---

## 何时使用状态模式

✅ **强烈推荐**:
- 订单或审批工作流
- 游戏角色状态系统
- TCP 连接管理
- 任务调度系统
- 权限和角色管理

⚠️ **权衡使用**:
- 只有 2-3 个状态（可用 if-else）
- 状态转移规则简单

❌ **不推荐**:
- 对象无状态
- 状态数量极多（>20）未收敛
- 实时性要求极高
    // 测试代码
}
```
