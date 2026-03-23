# SQL优化参考文档

## SQL性能优化基础

### 执行计划分析

#### MySQL执行计划
```sql
-- 基础执行计划
EXPLAIN SELECT * FROM users WHERE id = 1;

-- 详细执行计划
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE id = 1;

-- 执行分析
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 1;
```

#### PostgreSQL执行计划
```sql
-- 基础执行计划
EXPLAIN SELECT * FROM users WHERE id = 1;

-- 执行分析
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 1;

-- 详细执行计划
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT * FROM users WHERE id = 1;
```

#### 执行计划关键指标
- **type**: 访问类型 (const, eq_ref, ref, range, index, ALL)
- **key**: 使用的索引
- **rows**: 预估扫描行数
- **filtered**: 过滤比例
- **Extra**: 额外信息 (Using where, Using index, Using filesort)

### 索引原理

#### B-Tree索引结构
```
B-Tree索引结构:
根节点
├── 内部节点
│   ├── 叶子节点1 (key1 -> data1)
│   ├── 叶子节点2 (key2 -> data2)
│   └── 叶子节点3 (key3 -> data3)
└── 内部节点
    ├── 叶子节点4 (key4 -> data4)
    └── 叶子节点5 (key5 -> data5)
```

#### 索引类型对比
| 索引类型 | 适用场景 | 优点 | 缺点 |
|---------|----------|------|------|
| B-Tree | 精确查询、范围查询 | 通用性强 | 写入性能影响 |
| Hash | 等值查询 | 查询速度快 | 不支持范围查询 |
| Fulltext | 全文搜索 | 支持复杂搜索 | 占用空间大 |
| Spatial | 地理位置查询 | 支持空间索引 | 特定场景使用 |

## 查询优化策略

### SELECT优化

#### 避免SELECT *
```sql
-- 不好的示例
SELECT * FROM users WHERE status = 'active';

-- 好的示例
SELECT id, name, email FROM users WHERE status = 'active';
```

#### 使用LIMIT限制结果
```sql
-- 分页查询
SELECT id, name, email FROM users 
WHERE status = 'active' 
ORDER BY created_at DESC 
LIMIT 10 OFFSET 20;

-- 使用子查询优化大偏移量
SELECT u.id, u.name, u.email 
FROM users u
JOIN (
    SELECT id FROM users 
    WHERE status = 'active' 
    ORDER BY created_at DESC 
    LIMIT 10 OFFSET 20
) t ON u.id = t.id;
```

### WHERE子句优化

#### 索引列在前
```sql
-- 好的示例 - 索引列在前
SELECT * FROM orders WHERE user_id = 123 AND status = 'completed';

-- 不好的示例 - 非索引列在前
SELECT * FROM orders WHERE status = 'completed' AND user_id = 123;
```

#### 避免函数操作
```sql
-- 不好的示例 - 函数操作导致索引失效
SELECT * FROM users WHERE YEAR(created_at) = 2023;

-- 好的示例 - 使用范围查询
SELECT * FROM users WHERE created_at >= '2023-01-01' AND created_at < '2024-01-01';
```

#### 避免类型转换
```sql
-- 不好的示例 - 隐式类型转换
SELECT * FROM users WHERE phone = 1234567890;  -- phone是varchar类型

-- 好的示例 - 保持类型一致
SELECT * FROM users WHERE phone = '1234567890';
```

### JOIN优化

#### 小表驱动大表
```sql
-- 好的示例 - 小表在前
SELECT u.*, o.*
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active';

-- 如果users表小，orders表大，这样写更好
SELECT u.*, o.*
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active';
```

#### 使用适当的JOIN类型
```sql
-- INNER JOIN - 只返回匹配的行
SELECT u.*, o.*
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN - 返回左表所有行
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- 确保JOIN条件有索引
ALTER TABLE orders ADD INDEX idx_user_id (user_id);
```

### 聚合查询优化

#### 合理使用GROUP BY
```sql
-- 好的示例 - 只聚合必要的字段
SELECT user_id, COUNT(*) as order_count, SUM(amount) as total_amount
FROM orders 
WHERE status = 'completed'
GROUP BY user_id;

-- 优化 - 添加索引
ALTER TABLE orders ADD INDEX idx_status_user_id (status, user_id);
```

#### 使用HAVING过滤
```sql
-- 好的示例 - 使用HAVING过滤聚合结果
SELECT user_id, COUNT(*) as order_count
FROM orders 
WHERE status = 'completed'
GROUP BY user_id
HAVING COUNT(*) > 10;
```

## 索引优化

#### 单列索引
```sql
-- 创建单列索引
CREATE INDEX idx_email ON users(email);

-- 查看索引使用情况
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';
```

#### 复合索引
```sql
-- 创建复合索引 - 注意列顺序
CREATE INDEX idx_status_created_at ON users(status, created_at);

-- 复合索引使用场景
-- 1. 状态查询
SELECT * FROM users WHERE status = 'active';
-- 2. 状态+时间查询
SELECT * FROM users WHERE status = 'active' AND created_at > '2023-01-01';
-- 3. 状态+时间排序
SELECT * FROM users WHERE status = 'active' ORDER BY created_at DESC;
```

#### 覆盖索引
```sql
-- 创建覆盖索引
CREATE INDEX idx_covering ON orders(user_id, status, amount);

-- 查询只需要索引中的字段，避免回表
SELECT user_id, status, SUM(amount) 
FROM orders 
WHERE user_id = 123 
GROUP BY status;
```

#### 前缀索引
```sql
-- 对长字符串字段创建前缀索引
CREATE INDEX idx_email_prefix ON users(email(20));

-- 查看前缀选择性
SELECT COUNT(DISTINCT LEFT(email, 20)) / COUNT(*) as selectivity 
FROM users;
```

## 表结构优化

#### 数据类型选择
```sql
-- 整数类型选择
CREATE TABLE users (
    id TINYINT UNSIGNED,      -- 0-255
    age SMALLINT UNSIGNED,    -- 0-65535
    score MEDIUMINT,          -- -8388608-8388607
    balance INT,              -- -2147483648-2147483647
    timestamp BIGINT          -- 大整数
);

-- 字符串类型选择
CREATE TABLE products (
    name VARCHAR(100),        -- 变长字符串
    description TEXT,         -- 长文本
    status CHAR(1),           -- 定长字符串
    created_at DATE           -- 日期类型
);
```

#### 表分区
```sql
-- MySQL分区示例
CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT,
    user_id INT,
    amount DECIMAL(10,2),
    created_at DATETIME,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- 查询分区
SELECT * FROM orders PARTITION (p2023) 
WHERE created_at BETWEEN '2023-01-01' AND '2023-12-31';
```

#### 表规范化
```sql
-- 第一范式 - 原子性
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),        -- 原子字段
    email VARCHAR(100),       -- 原子字段
    phone VARCHAR(20)         -- 原子字段
);

-- 第二范式 - 完全依赖
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,             -- 依赖订单ID
    order_date DATETIME,      -- 依赖订单ID
    total_amount DECIMAL(10,2) -- 依赖订单ID
);

-- 第三范式 - 传递依赖
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,        -- 外键
    email VARCHAR(100)
);

CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT
);
```

## 查询重写技巧

#### 子查询优化
```sql
-- 不好的示例 - 相关子查询
SELECT u.*, 
       (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) as order_count
FROM users u;

-- 好的示例 - JOIN优化
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name, u.email;
```

#### EXISTS vs IN
```sql
-- EXISTS - 适用于外表大，内表小
SELECT u.* 
FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.user_id = u.id 
    AND o.status = 'completed'
);

-- IN - 适用于外表小，内表大
SELECT u.*
FROM users u
WHERE u.id IN (
    SELECT DISTINCT user_id 
    FROM orders 
    WHERE status = 'completed'
);
```

#### UNION优化
```sql
-- 不好的示例 - UNION会去重
SELECT name FROM active_users
UNION
SELECT name FROM inactive_users;

-- 好的示例 - UNION ALL不去重，性能更好
SELECT name FROM active_users
UNION ALL
SELECT name FROM inactive_users;
```

## 配置参数优化

#### MySQL配置
```sql
-- 内存配置
SET GLOBAL innodb_buffer_pool_size = 2147483648;  -- 2GB
SET GLOBAL innodb_log_file_size = 268435456;      -- 256MB
SET GLOBAL innodb_flush_log_at_trx_commit = 2;    -- 性能优化

-- 连接配置
SET GLOBAL max_connections = 200;
SET GLOBAL max_connect_errors = 1000;

-- 查询缓存
SET GLOBAL query_cache_size = 67108864;            -- 64MB
SET GLOBAL query_cache_type = ON;
```

#### PostgreSQL配置
```sql
-- 内存配置
SET shared_buffers = '256MB';
SET work_mem = '4MB';
SET maintenance_work_mem = '64MB';

-- 连接配置
SET max_connections = 100;
SET shared_preload_libraries = 'pg_stat_statements';

-- 统计信息
SET track_activities = on;
SET track_counts = on;
SET track_io_timing = on;
```

## 性能监控

#### 慢查询日志
```sql
-- MySQL慢查询配置
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 2;  -- 2秒
SET GLOBAL log_queries_not_using_indexes = ON;

-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log%';
SHOW VARIABLES LIKE 'long_query_time';
```

#### 性能模式 (MySQL)
```sql
-- 启用性能模式
UPDATE performance_schema.setup_instruments 
SET ENABLED = 'YES', TIMED = 'YES' 
WHERE NAME LIKE '%statement/%';

-- 查询性能统计
SELECT * FROM performance_schema.events_statements_summary_by_digest 
ORDER BY SUM_TIMER_WAIT DESC LIMIT 10;
```

#### pg_stat_statements (PostgreSQL)
```sql
-- 启用扩展
CREATE EXTENSION pg_stat_statements;

-- 查看查询统计
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;
```

## 常见问题和解决方案

### 全表扫描问题

#### 问题诊断
```sql
-- 查看执行计划中的全表扫描
EXPLAIN SELECT * FROM users WHERE email LIKE '%example.com%';

-- 查看索引使用情况
SHOW INDEX FROM users;
```

#### 解决方案
```sql
-- 添加合适的索引
CREATE INDEX idx_email ON users(email);

-- 使用前缀匹配而非后缀匹配
SELECT * FROM users WHERE email LIKE 'user%@example.com%';
```

### 索引失效问题

#### 常见导致索引失效的情况
```sql
-- 1. 函数操作
SELECT * FROM users WHERE UPPER(name) = 'JOHN';

-- 2. 类型转换
SELECT * FROM users WHERE id = '123';  -- id是数值类型

-- 3. 前导通配符
SELECT * FROM users WHERE email LIKE '%@example.com';

-- 4. OR条件
SELECT * FROM users WHERE name = 'John' OR email = 'john@example.com';
```

#### 解决方案
```sql
-- 1. 避免函数操作
SELECT * FROM users WHERE name = 'JOHN';

-- 2. 保持类型一致
SELECT * FROM users WHERE id = 123;

-- 3. 使用全文索引或前缀匹配
SELECT * FROM users WHERE email LIKE 'john%@example.com%';

-- 4. 使用UNION替代OR
SELECT * FROM users WHERE name = 'John'
UNION ALL
SELECT * FROM users WHERE email = 'john@example.com';
```

### 锁等待问题

#### 问题诊断
```sql
-- MySQL查看锁等待
SHOW ENGINE INNODB STATUS;

-- PostgreSQL查看锁等待
SELECT * FROM pg_locks WHERE NOT granted;

-- 查看长时间运行的查询
SELECT * FROM information_schema.processlist 
WHERE time > 60 AND state != 'Sleep';
```

#### 解决方案
```sql
-- 优化事务长度
BEGIN;
-- 尽量减少事务中的操作
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- 使用合适的隔离级别
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

## 优化工具

#### MySQL工具
```bash
# MySQLTuner - 性能分析工具
mysqltuner.pl

# pt-query-digest - 慢查询分析
pt-query-digest /var/log/mysql/mysql-slow.log

# MySQL Enterprise Monitor - 商业监控工具
```

#### PostgreSQL工具
```bash
# pgBadger - 日志分析
pgbadger /var/log/postgresql/postgresql-*.log

# pg_stat_statements - 查询统计
psql -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# pgAdmin - 图形化管理工具
```

#### 通用工具
```bash
# 数据库连接池配置
# HikariCP (Java)
# psycopg2.pool (Python)
# SQLAlchemy (Python)

# 监控工具
# Prometheus + Grafana
# DataDog
# New Relic
```

## 参考资源

### 官方文档
- [MySQL Performance Tuning](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/performance-tips.html)
- [Oracle Performance Tuning Guide](https://docs.oracle.com/en/database/oracle/oracle-database/19/tgdba/)

### 优化指南
- [High Performance MySQL](https://www.oreilly.com/library/view/high-performance-mysql/9781449332471/)
- [PostgreSQL High Performance Cookbook](https://www.packtpub.com/product/postgresql-high-performance-cookbook/9781789538349/)
- [SQL Performance Explained](https://use-the-index-luke.com/)

### 社区资源
- [Stack Overflow Database Tag](https://stackoverflow.com/questions/tagged/database)
- [DBA Stack Exchange](https://dba.stackexchange.com/)
- [Reddit r/Database](https://www.reddit.com/r/Database/)
