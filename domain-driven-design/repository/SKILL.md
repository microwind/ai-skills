---
name: 仓储
description: "为聚合提供持久化抽象，隐藏数据访问细节，让领域层不依赖具体的存储技术。"
license: MIT
---

# 仓储 (Repository)

## 概述

仓储为聚合提供**类似集合的接口**，隐藏数据存储的细节，让领域层不知道数据是存在数据库、文件还是内存中。

**核心规则**：
- 每个聚合根对应一个仓储
- 接口定义在领域层，实现在基础设施层
- 仓储操作的单位是完整的聚合

## 代码示例

```java
// 领域层：定义接口
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    List<Order> findByCustomerId(CustomerId customerId);
    void save(Order order);
    void delete(OrderId id);
}

// 基础设施层：实现
@Repository
public class JpaOrderRepository implements OrderRepository {
    private final JpaEntityManager em;

    @Override
    public Optional<Order> findById(OrderId id) {
        OrderEntity entity = em.find(OrderEntity.class, id.getValue());
        return Optional.ofNullable(entity).map(OrderEntity::toDomain);
    }

    @Override
    public void save(Order order) {
        OrderEntity entity = OrderEntity.fromDomain(order);
        em.merge(entity);
    }
}
```

```python
# 领域层：接口
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: pass

    @abstractmethod
    def save(self, order: Order): pass

    @abstractmethod
    def delete(self, order_id: str): pass

# 基础设施层：实现
class SqlOrderRepository(OrderRepository):
    def __init__(self, session):
        self.session = session

    def find_by_id(self, order_id: str) -> Order | None:
        row = self.session.query(OrderModel).get(order_id)
        return row.to_domain() if row else None

    def save(self, order: Order):
        model = OrderModel.from_domain(order)
        self.session.merge(model)
        self.session.commit()

# 测试用：内存实现
class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._store = {}

    def find_by_id(self, order_id: str) -> Order | None:
        return self._store.get(order_id)

    def save(self, order: Order):
        self._store[order.id] = order
```

## 仓储 vs DAO

| 维度 | Repository | DAO |
|------|-----------|-----|
| 抽象级别 | 领域概念（聚合） | 数据访问（表/行） |
| 操作单位 | 完整的聚合 | 单个表 |
| 接口位置 | 领域层 | 数据访问层 |
| 关注点 | 业务对象的生命周期 | CRUD操作 |

## 最佳实践

1. **一个聚合根一个仓储** — 不为内部实体创建独立仓储
2. **接口在领域层，实现在基础设施层** — 遵循依赖倒置
3. **返回领域对象** — 不返回数据库实体或 Map
4. **保存完整聚合** — save(order) 包括其所有 OrderItems

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [聚合根](../aggregate-root-design/) | 仓储按聚合根为单位操作 |
| [应用服务](../application-service/) | 应用服务通过仓储加载和保存聚合 |
| [领域模型](../domain-model/) | 仓储隐藏持久化，让领域模型纯净 |

## 总结

**核心**：仓储 = 聚合的持久化抽象，接口在领域层，实现在基础设施层。

**实践**：每个聚合根一个仓储，操作完整聚合，返回领域对象。
