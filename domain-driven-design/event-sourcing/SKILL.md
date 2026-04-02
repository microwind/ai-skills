---
name: 事件溯源
description: "将状态变更存储为不可变的事件序列，通过重播事件重建状态，提供完整的审计追踪。"
license: MIT
---

# 事件溯源 (Event Sourcing)

## 概述

事件溯源是一种持久化模式：**不存储当前状态，而是存储导致状态变化的所有事件**。当前状态通过重播事件序列来重建。

```
传统方式：只存最终状态
Account { balance: 850 }

事件溯源：存储所有变化
Event 1: AccountOpened { amount: 1000 }
Event 2: MoneyWithdrawn { amount: 200 }
Event 3: MoneyDeposited { amount: 50 }
→ 重播后: balance = 1000 - 200 + 50 = 850
```

## 代码示例

```java
// 事件定义
public sealed interface AccountEvent {
    record AccountOpened(String accountId, BigDecimal initialBalance, Instant at) implements AccountEvent {}
    record MoneyDeposited(String accountId, BigDecimal amount, Instant at) implements AccountEvent {}
    record MoneyWithdrawn(String accountId, BigDecimal amount, Instant at) implements AccountEvent {}
}

// 聚合通过事件重建状态
public class Account {
    private String id;
    private BigDecimal balance;
    private List<AccountEvent> uncommittedEvents = new ArrayList<>();

    // 从事件历史重建
    public static Account fromHistory(List<AccountEvent> history) {
        Account account = new Account();
        history.forEach(account::apply);
        return account;
    }

    // 业务操作产生事件
    public void deposit(BigDecimal amount) {
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new DomainException("金额必须为正");
        }
        raiseEvent(new MoneyDeposited(id, amount, Instant.now()));
    }

    public void withdraw(BigDecimal amount) {
        if (amount.compareTo(balance) > 0) {
            throw new DomainException("余额不足");
        }
        raiseEvent(new MoneyWithdrawn(id, amount, Instant.now()));
    }

    // 应用事件改变状态
    private void apply(AccountEvent event) {
        switch (event) {
            case AccountOpened e -> {
                this.id = e.accountId();
                this.balance = e.initialBalance();
            }
            case MoneyDeposited e -> this.balance = balance.add(e.amount());
            case MoneyWithdrawn e -> this.balance = balance.subtract(e.amount());
        }
    }

    private void raiseEvent(AccountEvent event) {
        apply(event);
        uncommittedEvents.add(event);
    }
}

// 事件存储
public class EventStore {
    public void save(String aggregateId, List<AccountEvent> events, long expectedVersion) {
        // 追加事件到事件流（乐观锁检查版本号）
        for (AccountEvent event : events) {
            db.append("events", Map.of(
                "aggregate_id", aggregateId,
                "version", ++expectedVersion,
                "event_type", event.getClass().getSimpleName(),
                "data", serialize(event),
                "timestamp", Instant.now()
            ));
        }
    }

    public List<AccountEvent> load(String aggregateId) {
        return db.query("events")
            .where("aggregate_id", aggregateId)
            .orderBy("version")
            .map(this::deserialize);
    }
}
```

```python
# Python 事件溯源
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True)
class AccountOpened:
    account_id: str
    initial_balance: Decimal
    at: datetime

@dataclass(frozen=True)
class MoneyDeposited:
    account_id: str
    amount: Decimal
    at: datetime

class Account:
    def __init__(self):
        self.id = None
        self.balance = Decimal(0)
        self._uncommitted = []

    @classmethod
    def from_history(cls, events: list) -> "Account":
        account = cls()
        for event in events:
            account._apply(event)
        return account

    def deposit(self, amount: Decimal):
        if amount <= 0:
            raise DomainError("金额必须为正")
        self._raise(MoneyDeposited(self.id, amount, datetime.now()))

    def _apply(self, event):
        match event:
            case AccountOpened():
                self.id = event.account_id
                self.balance = event.initial_balance
            case MoneyDeposited():
                self.balance += event.amount

    def _raise(self, event):
        self._apply(event)
        self._uncommitted.append(event)
```

## 快照优化

```
事件很多时重播很慢，用快照加速：

Events: [E1, E2, E3, ..., E999, E1000]
                      ↑
Snapshot at E500: { balance: 5000 }

重建时：从 Snapshot 开始 + 重播 E501-E1000
而非：重播全部 1000 个事件
```

## 优缺点

### ✅ 优点
1. **完整审计** — 所有变更历史可追溯
2. **时间旅行** — 可重建任意时间点的状态
3. **事件驱动** — 天然支持事件驱动架构
4. **无数据丢失** — 只追加不修改不删除
5. **调试友好** — 可重播事件复现问题

### ❌ 缺点
1. **查询困难** — 需要配合 CQRS 构建读模型
2. **事件演化** — 事件格式变更需要版本管理
3. **学习曲线** — 思维方式与传统 CRUD 不同
4. **存储增长** — 事件不断累积需要快照和归档

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [领域事件](../domain-events/) | 事件溯源的基础是领域事件 |
| [CQRS](../cqrs-pattern/) | 事件溯源几乎总是配合 CQRS 使用 |
| [读模型优化](../read-model-optimization/) | 从事件投影构建读模型 |
| [聚合根](../aggregate-root-design/) | 聚合通过事件重建状态 |

## 总结

**核心**：存储事件序列而非当前状态，通过重播事件重建状态。

**适用**：需要完整审计、时间旅行、事件驱动的场景。通常配合 CQRS 使用。
