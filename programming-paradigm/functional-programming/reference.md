# 函数式编程 - 参考实现

## Java Stream API 完整示例

```java
public class DataProcessor {
    // 数据类
    record Order(String id, String customerId, double amount, boolean paid) {}
    record Customer(String id, String name, String email) {}
    record ProcessedOrder(String id, String customerName, double discountedAmount) {}

    // 纯函数：计算折扣
    public static double calculateDiscount(double amount) {
        return amount > 1000 ? amount * 0.15 : amount * 0.05;
    }

    // 纯函数：应用折扣
    public static double applyDiscount(double amount) {
        return amount - calculateDiscount(amount);
    }

    // 处理数据管道
    public static List<ProcessedOrder> processOrders(
            List<Order> orders,
            Map<String, Customer> customers) {

        return orders.stream()
            // 第1步：过滤已支付的订单
            .filter(Order::paid)
            // 第2步：过滤金额有效的订单
            .filter(o -> o.amount() > 0)
            // 第3步：转换为处理结果
            .map(order -> {
                Customer customer = customers.get(order.customerId());
                double discountedAmount = applyDiscount(order.amount());
                return new ProcessedOrder(
                    order.id(),
                    customer.name(),
                    discountedAmount
                );
            })
            // 第4步：按金额排序
            .sorted((a, b) -> Double.compare(b.discountedAmount(), a.discountedAmount()))
            // 第5步：收集结果
            .collect(toList());
    }

    // 统计分析
    public static Map<String, Double> analyzeByCustomer(List<ProcessedOrder> orders) {
        return orders.stream()
            .collect(groupingBy(
                ProcessedOrder::customerName,
                summingDouble(ProcessedOrder::discountedAmount)
            ));
    }

    // 使用示例
    public static void main(String[] args) {
        // 准备数据
        List<Order> orders = Arrays.asList(
            new Order("O1", "C1", 1500, true),
            new Order("O2", "C2", 500, true),
            new Order("O3", "C1", 800, false),  // 未支付，会被过滤
            new Order("O4", "C3", 2000, true)
        );

        Map<String, Customer> customers = Map.of(
            "C1", new Customer("C1", "Alice", "alice@example.com"),
            "C2", new Customer("C2", "Bob", "bob@example.com"),
            "C3", new Customer("C3", "Charlie", "charlie@example.com")
        );

        // 处理订单
        List<ProcessedOrder> processed = processOrders(orders, customers);
        processed.forEach(o -> System.out.println(o));

        // 分析数据
        Map<String, Double> analysis = analyzeByCustomer(processed);
        analysis.forEach((name, total) ->
            System.out.printf("%s: %.2f%n", name, total)
        );
    }
}
```

## Python 完整示例

```python
from functools import reduce
from typing import List, Dict, Callable

# 数据类
class Order:
    def __init__(self, id, customer_id, amount, paid):
        self.id = id
        self.customer_id = customer_id
        self.amount = amount
        self.paid = paid

class Customer:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

# 纯函数
def calculate_discount(amount: float) -> float:
    return amount * 0.15 if amount > 1000 else amount * 0.05

def apply_discount(amount: float) -> float:
    return amount - calculate_discount(amount)

def is_valid_order(order: Order) -> bool:
    return order.paid and order.amount > 0

# 数据处理管道
def process_orders(orders: List[Order], customers: Dict[str, Customer]) -> List:
    def transform_order(order):
        customer = customers[order.customer_id]
        return {
            'id': order.id,
            'customer_name': customer.name,
            'discounted_amount': apply_discount(order.amount)
        }

    return list(map(
        transform_order,
        filter(is_valid_order, orders)
    ))

# 统计分析
def analyze_by_customer(processed: List[Dict]) -> Dict[str, float]:
    result = {}
    for order in processed:
        name = order['customer_name']
        amount = order['discounted_amount']
        result[name] = result.get(name, 0) + amount
    return result

# 使用示例
if __name__ == "__main__":
    orders = [
        Order("O1", "C1", 1500, True),
        Order("O2", "C2", 500, True),
        Order("O3", "C1", 800, False),
        Order("O4", "C3", 2000, True)
    ]

    customers = {
        "C1": Customer("C1", "Alice", "alice@example.com"),
        "C2": Customer("C2", "Bob", "bob@example.com"),
        "C3": Customer("C3", "Charlie", "charlie@example.com")
    }

    processed = process_orders(orders, customers)
    for order in processed:
        print(order)

    analysis = analyze_by_customer(processed)
    for name, total in analysis.items():
        print(f"{name}: {total:.2f}")
```

## TypeScript 完整示例

```typescript
interface Order {
    id: string;
    customerId: string;
    amount: number;
    paid: boolean;
}

interface Customer {
    id: string;
    name: string;
    email: string;
}

interface ProcessedOrder {
    id: string;
    customerName: string;
    discountedAmount: number;
}

// 纯函数
const calculateDiscount = (amount: number): number =>
    amount > 1000 ? amount * 0.15 : amount * 0.05;

const applyDiscount = (amount: number): number =>
    amount - calculateDiscount(amount);

const isValidOrder = (order: Order): boolean =>
    order.paid && order.amount > 0;

// 数据处理管道
const processOrders = (
    orders: Order[],
    customers: Map<string, Customer>
): ProcessedOrder[] => {
    return orders
        .filter(isValidOrder)
        .map(order => ({
            id: order.id,
            customerName: customers.get(order.customerId)?.name ?? "Unknown",
            discountedAmount: applyDiscount(order.amount)
        }))
        .sort((a, b) => b.discountedAmount - a.discountedAmount);
};

// 统计分析
const analyzeByCustomer = (processed: ProcessedOrder[]): Map<string, number> => {
    const result = new Map<string, number>();
    processed.forEach(order => {
        const current = result.get(order.customerName) ?? 0;
        result.set(order.customerName, current + order.discountedAmount);
    });
    return result;
};

// 使用示例
const orders: Order[] = [
    { id: "O1", customerId: "C1", amount: 1500, paid: true },
    { id: "O2", customerId: "C2", amount: 500, paid: true },
    { id: "O3", customerId: "C1", amount: 800, paid: false },
    { id: "O4", customerId: "C3", amount: 2000, paid: true }
];

const customers = new Map<string, Customer>([
    ["C1", { id: "C1", name: "Alice", email: "alice@example.com" }],
    ["C2", { id: "C2", name: "Bob", email: "bob@example.com" }],
    ["C3", { id: "C3", name: "Charlie", email: "charlie@example.com" }]
]);

const processed = processOrders(orders, customers);
console.log(processed);

const analysis = analyzeByCustomer(processed);
analysis.forEach((total, name) => console.log(`${name}: ${total.toFixed(2)}`));
```

## 单元测试示例

```java
@Test
public void testCalculateDiscount() {
    assertEquals(150, DataProcessor.calculateDiscount(1500), 0.01);
    assertEquals(25, DataProcessor.calculateDiscount(500), 0.01);
}

@Test
public void testProcessOrders() {
    List<Order> orders = Arrays.asList(
        new Order("O1", "C1", 1500, true),
        new Order("O2", "C2", 500, true)
    );
    Map<String, Customer> customers = Map.of(
        "C1", new Customer("C1", "Alice", "alice@example.com"),
        "C2", new Customer("C2", "Bob", "bob@example.com")
    );

    List<ProcessedOrder> result = DataProcessor.processOrders(orders, customers);

    assertEquals(2, result.size());
    assertEquals("Alice", result.get(0).customerName());
}

@Test
public void testPureFunction() {
    double result1 = DataProcessor.applyDiscount(1000);
    double result2 = DataProcessor.applyDiscount(1000);

    // 纯函数：相同输入 → 相同输出
    assertEquals(result1, result2, 0.01);
}
```

---

## 核心模式

### 1. 映射 (Map)
转换每个元素。

### 2. 过滤 (Filter)
选择符合条件的元素。

### 3. 折叠 (Reduce)
将集合归约为单一值。

### 4. 函数组合
组合小函数形成大函数。

---

## 总结

**FP的核心优势**：
- 纯函数易于测试和推理
- 不可变数据天然线程安全
- 函数组合提高代码复用
- 易于并行化

**最佳实践**：
- 优先使用纯函数
- 隔离副作用
- 使用 Stream API 处理集合
- 用 Optional 代替 null

FP 对于数据处理和并发系统来说是理想选择。
