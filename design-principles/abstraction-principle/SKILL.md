---
name: 抽象原则
description: "提取事物的本质特征，忽略非本质细节，通过抽象层简化复杂系统的理解和使用。"
license: MIT
---

# 抽象原则 (Abstraction Principle)

## 概述

抽象是管理复杂性的核心工具：**捕获事物的本质特征，隐藏不必要的细节，提供更简单的理解模型**。

**核心思想**：
- 好的抽象隐藏复杂性，暴露简单接口
- 抽象应该稳定，不因实现变化而改变
- 每个抽象层只处理一个复杂度级别

## 抽象层次

```java
// 从低到高的抽象层次

// 最低层：硬件指令
// MOV AX, [address]

// 操作系统层
// read(fd, buffer, size)

// 语言运行时层
// FileInputStream.read()

// 框架层
// Files.readString(Path.of("data.txt"))

// 业务层 — 最高抽象
public class ReportService {
    public Report generateMonthlyReport(YearMonth month) {
        // 调用方不需要知道数据从哪来、如何格式化
        return reportGenerator.generate(month);
    }
}
```

## 好的抽象 vs 差的抽象

```java
// ❌ 抽象泄漏：暴露了实现细节
public interface UserRepository {
    User findBySQL(String sql);                    // 暴露了数据库
    User findByMongoQuery(Document query);          // 暴露了 MongoDB
    void saveWithRetry(User user, int maxRetries);  // 暴露了重试机制
}

// ✅ 好的抽象：隐藏实现
public interface UserRepository {
    Optional<User> findById(UserId id);
    Optional<User> findByEmail(String email);
    void save(User user);
    void delete(UserId id);
}
```

```python
# ❌ 错误的抽象级别：太高或太低
class FileProcessor:
    def process(self, data):  # 太抽象，什么都能传
        pass

class CsvFileByteProcessor:  # 太具体，名字暴露所有实现
    def process_csv_bytes_with_utf8_encoding(self, raw_bytes):
        pass

# ✅ 恰当的抽象级别
class CsvImporter:
    def import_records(self, file_path: str) -> list[Record]:
        """导入CSV文件中的记录"""
        pass
```

## 抽象设计原则

### 1. 依赖抽象而非具体

```typescript
// ❌ 依赖具体
class OrderService {
    private mysqlDb = new MySQLConnection();
    private sendGridEmail = new SendGridClient();
}

// ✅ 依赖抽象
class OrderService {
    constructor(
        private db: Database,          // 抽象
        private mailer: EmailSender    // 抽象
    ) {}
}
```

### 2. 同一方法内保持同一抽象级别

```java
// ❌ 混合抽象级别
public void processOrder(Order order) {
    // 高层抽象
    validateOrder(order);
    // 突然降到低层细节
    Connection conn = DriverManager.getConnection("jdbc:mysql://...");
    PreparedStatement ps = conn.prepareStatement("INSERT INTO orders ...");
    ps.setString(1, order.getId());
    ps.executeUpdate();
    // 又回到高层
    notifyCustomer(order);
}

// ✅ 保持一致的抽象级别
public void processOrder(Order order) {
    validateOrder(order);
    saveOrder(order);       // 隐藏数据库细节
    notifyCustomer(order);
}
```

## 何时不应该抽象

```
❌ 只有一个实现且不太可能变化
❌ 抽象增加的复杂度大于它简化的复杂度
❌ 为了"将来可能"而抽象（违反 YAGNI）
❌ 抽象无法完全隐藏细节（抽象泄漏）

✅ 有多个实现或预期会有
✅ 需要隔离变化（如外部依赖）
✅ 降低了理解成本
✅ 简化了测试
```

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [封装](../encapsulation-principle/) | 封装隐藏内部，抽象提取本质 |
| [DIP](../dependency-inversion-principle/) | DIP 要求依赖抽象 |
| [OCP](../open-closed-principle/) | 通过抽象实现扩展开放 |
| [KISS](../kiss-principle/) | 好的抽象简化理解，坏的抽象增加复杂 |

## 总结

**抽象核心**：捕获本质，隐藏细节，提供简单接口。

**实践要点**：
- 抽象应该隐藏复杂性而非转移复杂性
- 同一方法内保持一致的抽象级别
- 不要过度抽象——抽象也有成本
- 好的抽象让代码"像读英语一样"
