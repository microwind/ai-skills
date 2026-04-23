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

## 仓储的实现方式

仓储是一种**模式**（抽象接口），其背后可以用多种存储技术实现：

```
Repository（领域层，接口）
      │
      │ 由以下具体技术实现：
      │
      ├──▶ MyBatis 的 Mapper（SQL 映射）
      ├──▶ JPA / Hibernate EntityManager（ORM）
      ├──▶ Spring Data JPA Repository
      ├──▶ 纯 JDBC + SQL
      ├──▶ MongoDB Driver（文档数据库）
      ├──▶ Redis Client（内存数据库）
      └──▶ HashMap（测试用，内存实现）
```

> **经验**：如果项目用 MyBatis，则 **Mapper 就是 Repository 的一种实现**——但要注意，Mapper 本身接口应放在仓储层，**领域层依赖的是 Repository 接口，而不是 Mapper 接口**。

## DO ↔ Model 转换

领域层使用**领域模型（Model）**，数据库层使用**数据对象（DO）**，二者**不应等同**。仓储层负责两者之间的转换：

```
┌─────────────────────┐                      ┌──────────────────┐
│   领域层（Domain）    │                      │  数据库表（MySQL）  │
│                     │                      │                  │
│  Subscription       │                      │  t_subscription  │
│   ├─ id: SubscriptionId                    │   ├─ id          │
│   ├─ reader: ReaderId                      │   ├─ reader_id   │
│   ├─ column: ColumnId                      │   ├─ column_id   │
│   ├─ period: DateRange  (值对象)            │   ├─ start_time  │
│   └─ status: SubscriptionStatus            │   ├─ end_time    │
│                     │                      │   └─ status      │
└─────────┬───────────┘                      └────────┬─────────┘
          ▲                                           ▲
          │ 转换                                       │
          │                                           │
    ┌─────┴─────────────────────────────────┐        │
    │  DO2ModelConverter                    │        │
    │  Model2DOConverter                    │◀───────┘
    └────────────────────────────────────────┘
              (仓储层 repository)

                     SubscriptionDO
                      ├─ id: Long
                      ├─ readerId: Long
                      ├─ columnId: Long
                      ├─ startTime: Timestamp
                      ├─ endTime: Timestamp
                      └─ status: Integer
```

**关键约束**：

- **DO 只存在于仓储层** ——不暴露给应用层 / 领域层
- **转换建议手写** ——逐字段转换，避免 `BeanUtils.copyProperties` / MapStruct 带来的字段变更盲点
- **值对象打平** ——`DateRange` 在 DO 里打成两列（`start_time` + `end_time`）
- **枚举双向映射** ——`SubscriptionStatus.ACTIVE` ↔ 数据库 `1`

## 代码示例

```java
// 领域层：定义接口（只面向聚合）
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    List<Order> findByCustomerId(CustomerId customerId);
    void save(Order order);
    void delete(OrderId id);
}

// JPA 实现
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

### MyBatis 实现示例（Mapper 作为 Repository 的实现）

```java
// 1. 领域层：Repository 接口（不依赖 MyBatis）
package com.rabbit.subscription.domain;

public interface SubscriptionRepository {
    Subscription findById(SubscriptionId id);
    boolean existsActive(ReaderId reader, ColumnId column);
    void save(Subscription subscription);
}

// 2. 仓储层：DO（数据对象，字段与表一一对应）
package com.rabbit.subscription.repository;

public class SubscriptionDO {
    private Long id;
    private Long readerId;
    private Long columnId;
    private Date startTime;
    private Date endTime;
    private Integer status;
    // getters / setters
}

// 3. 仓储层：Mapper（MyBatis 接口，只能在仓储层被调用）
public interface SubscriptionMapper {
    SubscriptionDO queryById(@Param("id") Long id);
    int countActive(@Param("readerId") Long reader, @Param("columnId") Long column);
    int insert(SubscriptionDO data);
    int update(SubscriptionDO data);
}

// 4. 仓储层：Repository 实现 = Mapper + Converter
@Component
public class SubscriptionRepositoryImpl implements SubscriptionRepository {

    @Autowired private SubscriptionMapper mapper;

    @Override
    public Subscription findById(SubscriptionId id) {
        SubscriptionDO data = mapper.queryById(id.getValue());
        return DO2ModelConverter.toModel(data);      // 仓储内部转换，不泄漏 DO
    }

    @Override
    public boolean existsActive(ReaderId reader, ColumnId column) {
        return mapper.countActive(reader.getValue(), column.getValue()) > 0;
    }

    @Override
    public void save(Subscription subscription) {
        SubscriptionDO data = Model2DOConverter.toDO(subscription);
        if (data.getId() == null) {
            mapper.insert(data);
        } else {
            mapper.update(data);
        }
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
