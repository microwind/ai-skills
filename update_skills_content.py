#!/usr/bin/env python3
"""
为核心skills添加完整内容
"""

skills_content = {
    "backend/async-tasks": """# 异步任务与消息队列

## 目的
掌握如何使用异步任务处理和消息队列提升应用性能。

## 核心概念

### 何时使用异步任务？
- 长时间运行的操作（图片处理、PDF生成）
- 邮件发送和外部API调用
- 数据处理和批量操作
- 定时任务

### 常见方案对比

| 方案 | 优点 | 缺点 | 使用场景 |
|------|------|------|---------|
| Celery | 功能完整，可扩展 | 学习曲线陡峭 | 复杂异步任务 |
| Redis Queue | 简单易用 | 功能简单 | 简单任务队列 |
| APScheduler | 轻量级定时任务 | 不适合分布式 | 单机定时任务 |
| Message Queue | 高可靠性 | 部署复杂 | 分布式系统 |

## 实现示例

### Python Celery + Redis
```python
from celery import Celery
from redis import Redis
import time

app = Celery('myapp', broker='redis://localhost:6379')

@app.task
def send_email(email, subject, message):
    \"\"\"发送邮件异步任务\"\"\"
    time.sleep(2)  # 模拟邮件发送
    print(f"邮件已发送到 {email}")
    return True

@app.task
def process_image(image_path):
    \"\"\"处理图片异步任务\"\"\"
    # 处理图片逻辑
    return f"图片处理完成: {image_path}"

# 在应用中使用
# 方式1：异步执行（立即返回）
send_email.delay('user@example.com', '欢迎', '欢迎使用我们的服务')

# 方式2：延迟执行
send_email.apply_async(
    args=('user@example.com', '欢迎', '欢迎信息'),
    countdown=60  # 60秒后执行
)

# 方式3：定时执行
from celery.schedules import crontab
app.conf.beat_schedule = {
    'send-reminder-every-day': {
        'task': 'tasks.send_reminder',
        'schedule': crontab(hour=9, minute=0),
    }
}
```

### Node.js - Bull队列
```javascript
const Queue = require('bull');
const emailQueue = new Queue('email', 'redis://localhost:6379');

// 定义任务处理器
emailQueue.process(async (job) => {
  const { email, subject, message } = job.data;

  // 发送邮件
  console.log(`发送邮件到: ${email}`);

  // 返回结果
  return { success: true };
});

// 添加任务
emailQueue.add(
  { email: 'user@example.com', subject: '欢迎', message: '欢迎信息' },
  { delay: 60000, attempts: 3 }
);

// 监听事件
emailQueue.on('completed', (job) => {
  console.log('任务完成:', job.id);
});

emailQueue.on('failed', (job, err) => {
  console.log('任务失败:', err.message);
});
```

## 最佳实践

1. **幂等性** - 任务可以安全地重新执行
2. **错误处理** - 失败重试和死信队列
3. **监控** - 监控任务执行状态
4. **超时设置** - 防止任务无限运行
5. **可观测性** - 记录任务日志

## 常见问题

**Q: 如何确保任务只执行一次？**
A: 实现幂等性，使用唯一ID和数据库检查。

**Q: 任务失败了怎么办？**
A: 配置重试机制、指数退避和死信队列。
""",

    "frontend/react-components": """# React组件最佳实践

## 目的
掌握React组件设计和最佳实践，提升代码质量。

## 核心原则

### 组件设计原则
1. **单一职责** - 每个组件只做一件事
2. **可复用性** - 通过props实现灵活配置
3. **可测试性** - 易于单元测试
4. **性能** - 避免不必要的重新渲染
5. **可维护性** - 清晰的结构和命名

## 函数式组件最佳实践

### 基础模式
```javascript
// ✓ 好的实践
export const UserCard = ({ user, onDelete }) => {
  const [isLoading, setIsLoading] = React.useState(false);

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await onDelete(user.id);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="user-card">
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <button onClick={handleDelete} disabled={isLoading}>
        {isLoading ? '删除中...' : '删除'}
      </button>
    </div>
  );
};

// ✗ 避免的做法
export const UserCard = (props) => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [user, setUser] = React.useState(null);

  // 副作用过多和管理不当
  React.useEffect(() => {
    // 多个关注点混在一起
  });

  return <div>{/* ... */}</div>;
};
```

### Hook组织
```javascript
// ✓ 好的做法 - 逻辑分离
const useUserData = (userId) => {
  const [user, setUser] = React.useState(null);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    setLoading(true);
    fetchUser(userId).then(data => {
      setUser(data);
      setLoading(false);
    });
  }, [userId]);

  return { user, loading };
};

const useAsync = (fn, deps) => {
  const [data, setData] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    setLoading(true);
    fn().then(setData).catch(setError).finally(() => setLoading(false));
  }, deps);

  return { data, error, loading };
};
```

## 性能优化

### 避免不必要的重新渲染
```javascript
// ✓ 使用React.memo
const UserItem = React.memo(({ user, onSelect }) => {
  return (
    <li onClick={() => onSelect(user.id)}>
      {user.name}
    </li>
  );
}, (prev, next) => {
  return prev.user.id === next.user.id;
});

// ✓ 使用useCallback稳定函数引用
const ParentComponent = () => {
  const [selectedId, setSelectedId] = React.useState(null);

  const handleSelect = React.useCallback((id) => {
    setSelectedId(id);
  }, []);

  return (
    <UserList users={users} onSelect={handleSelect} />
  );
};
```

## 组件文件结构
```
components/
├── UserCard/
│   ├── UserCard.jsx       # 主组件
│   ├── UserCard.module.css # 样式
│   ├── useUserData.js     # 自定义Hook
│   └── __tests__/
│       └── UserCard.test.js
├── UserList/
└── UserForm/
```

## 常见问题

**Q: 何时使用state？**
A: 数据会变化且影响UI时使用state。静态数据用props。

**Q: 如何选择context vs redux？**
A: 简单状态用Context，复杂全局状态用Redux。
""",

    "database/sql-optimization": """# SQL优化与索引

## 目的
学习如何编写高效的SQL查询和合理使用索引。

## 核心优化策略

### 1. 选择合适的列
```sql
-- ✓ 好的做法：只查询需要的列
SELECT id, name, email FROM users WHERE age > 18;

-- ✗ 避免：查询所有列
SELECT * FROM users WHERE age > 18;
```

### 2. 使用索引
```sql
-- 创建单列索引
CREATE INDEX idx_user_email ON users(email);

-- 创建复合索引
CREATE INDEX idx_user_age_status ON users(age, status);

-- 创建唯一索引
CREATE UNIQUE INDEX idx_user_username ON users(username);

-- 查看索引使用情况
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
```

### 3. JOIN优化
```sql
-- ✓ 有索引的关联
SELECT u.id, u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE u.age > 18;

-- ✗ 避免多表扫描
SELECT u.*, o.* FROM users u, orders o WHERE u.id = o.user_id;
```

### 4. 子查询优化
```sql
-- ✓ 使用JOIN替代子查询
SELECT u.id, u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- ✗ 避免N+1查询
SELECT u.id, u.name FROM users u;
-- 然后在应用中对每个user查询orders
```

## 常见索引误区

| 误区 | 现实 | 建议 |
|------|------|------|
| 更多索引更快 | 写入变慢，占空间 | 权衡读写性能 |
| 索引能解决所有问题 | 需要配合查询优化 | 分析执行计划 |
| 单列索引好于复合索引 | 复合索引通常更优 | 按查询条件创建 |

## 执行计划分析
```sql
-- MySQL
EXPLAIN SELECT * FROM orders WHERE user_id = 1 AND status = 'completed';

-- 重要指标：
-- type: 访问类型（const < eq_ref < ref < range < index < ALL）
-- rows: 预计扫描行数
-- key: 使用的索引
```

## 常见问题

**Q: 为什么加了索引还是很慢？**
A: 可能是：索引未被使用（查询方式不对）、数据量太大、有全表扫描。

**Q: 如何选择复合索引的列顺序？**
A: 等值条件优先，频繁出现优先，范围查询放最后。
""",

    "system-design/high-concurrency": """# 高并发系统设计

## 目的
学习如何设计和实现支持高并发的系统。

## 核心概念

### 并发常见瓶颈
1. **数据库连接** - 连接数有限
2. **内存** - 不是无限的
3. **CPU** - 线程上下文切换开销
4. **网络I/O** - 带宽限制
5. **磁盘I/O** - 读写速度限制

### 解决方案分层

#### 应用层
```
1. 异步处理 - 使用消息队列
2. 缓存 - 多层缓存（本地、分布式）
3. 限流降级 - 防止雪崩
4. 线程池 - 管理并发
```

#### 中间件层
```
1. 连接池 - 复用连接
2. 负载均衡 - 分散流量
3. 消息队列 - 解耦系统
4. 缓存层 - 提升响应速度
```

#### 数据库层
```
1. 数据库优化 - 索引、分片
2. 读写分离 - 主从复制
3. 缓存 - 减少数据库查询
4. 异步操作 - 非关键数据异步写入
```

## 缓存策略

### 多层缓存架构
```
用户请求
    ↓
本地内存缓存（L1）
    ↓ miss
分布式缓存（Redis）（L2）
    ↓ miss
数据库（L3）
```

### 缓存穿透、击穿、雪崩

```python
# 缓存穿透 - 数据不存在
# 解决：布隆过滤器
from bloom_filter import BloomFilter
bf = BloomFilter(1000000)  # 100万容量
for item in valid_ids:
    bf.add(item)

def get_user(user_id):
    if not bf.contains(user_id):
        return None  # 直接返回，不查询数据库
    return cache.get(f"user:{user_id}")

# 缓存击穿 - 热点数据失效
# 解决：加锁、永不过期
def get_hot_data(key):
    data = cache.get(key)
    if data is None:
        lock = acquire_lock(f"lock:{key}", timeout=10)
        if lock:
            # 只有一个线程重新加载
            data = db.query(key)
            cache.set(key, data, ttl=-1)
        else:
            # 其他线程等待
            time.sleep(0.1)
            return get_hot_data(key)
    return data

# 缓存雪崩 - 大量缓存同时失效
# 解决：错开过期时间
def set_cache(key, value):
    ttl = 3600 + random.randint(0, 600)  # 1小时 ± 10分钟
    cache.set(key, value, ttl=ttl)
```

## 常见问题

**Q: 如何预测系统能承载多少并发？**
A: 日均PV/86400 * 峰值系数(一般10-20倍)

**Q: 如何测试系统并发能力？**
A: 使用压力测试工具（JMeter、LoadRunner）进行测试
"""
}

from pathlib import Path

for skill_path, content in skills_content.items():
    path = Path(f"/Users/jarry/github/ai-skills/{skill_path}/中文说明.md")
    # 读取现有文件
    old_content = path.read_text(encoding='utf-8')
    # 替换为新内容
    path.write_text(content, encoding='utf-8')
    print(f"✓ 已更新: {skill_path}")

print(f"\n✅ 完成更新 {len(skills_content)} 个Skills")
