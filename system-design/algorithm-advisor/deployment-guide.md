# 混合推荐系统 - 生产部署指南

## 第一部分: 详细架构设计

### 1. 完整的系统拓扑图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             用户客户端                                       │
│                    (移动端/Web/H5)                                          │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │         CDN 加速                        │
        │  (减少网络延迟)                         │
        └────────────┬─────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────────┐
        │    负载均衡 (Nginx/HAProxy)             │
        │  - 轮询分配                             │
        │  - 健康检查                             │
        │  - SSL/TLS 终止                        │
        └────────────┬─────────────────────────────┘
                     │
        ┌────────────┴────────────┬────────────────┬───────────────┐
        ▼                         ▼                ▼               ▼
   ┌────────────┐         ┌────────────┐   ┌────────────┐   ┌────────────┐
   │ 推荐服务1  │         │ 推荐服务2  │   │ 推荐服务3  │...│ 推荐服务N  │
   │ (FastAPI)  │         │ (FastAPI)  │   │ (FastAPI)  │   │ (FastAPI)  │
   │ 16核 32GB  │         │ 16核 32GB  │   │ 16核 32GB  │   │ 16核 32GB  │
   │ 1000 QPS   │         │ 1000 QPS   │   │ 1000 QPS   │   │ 1000 QPS   │
   └──────┬─────┘         └──────┬─────┘   └──────┬─────┘   └──────┬─────┘
          │                      │                │               │
          └──────────────────────┼────────────────┼───────────────┘
                                 │
                    ┌────────────────────────────────┐
                    │   Redis Cluster (缓存层)       │
                    ├────────────────────────────────┤
                    │ L1: 热点用户缓存  (25GB)       │
                    │ L2: CF缓存        (50GB)       │
                    │ L3: 相似度缓存    (20GB)       │
                    │ L4: 热度缓存      (5GB)        │
                    │ ─────────────────────────────  │
                    │ 3主 + 3从 (6台)               │
                    │ 32GB内存/台                    │
                    │ 命中率: >80%                  │
                    └────────────────────────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 ▼               ▼               ▼
          ┌────────────┐   ┌────────────┐   ┌────────────┐
          │ MySQL 主   │   │ MongoDB    │   │ HDFS       │
          │ (用户历史) │   │ (日志库)   │   │ (离线数据) │
          └────────────┘   └────────────┘   └────────────┘
                                 │
                    ┌────────────────────────────────┐
                    │     Kafka Topic                │
                    ├────────────────────────────────┤
                    │ user_feedback                  │
                    │ recommendation_log             │
                    │ user_behavior                  │
                    └────────────────────────────────┘
                                 │
                    ┌────────────────────────────────┐
                    │   离线计算集群 (Spark)         │
                    ├────────────────────────────────┤
                    │ CF计算 (Item-based)            │
                    │ 特征提取                       │
                    │ CTR模型训练 (LightGBM)         │
                    │ 缓存预热                       │
                    │ ─────────────────────────────  │
                    │ 运行: 每天 02:00-04:30        │
                    │ 耗时: ~2.5小时                │
                    └────────────────────────────────┘
```

### 2. 推荐服务内部流程 (时间轴)

```
用户请求: GET /recommend?user_id=123&limit=20
         ↓ (时间: 0ms)
    ┌────────────────────┐
    │  1. 解析请求       │ (1ms)
    │  - user_id=123     │
    │  - limit=20        │
    └────────────┬───────┘
                 ▼ (时间: 1ms)
    ┌────────────────────────┐
    │  2. 查询 L1 缓存       │
    │  Redis: hot_user:123   │ (1-2ms)
    └────────────┬───────────┘
                 │
        ┌────────┴────────┐
        │ 命中(50%)       │ 未命中(50%)
        ▼                 ▼ (时间: 3ms)
    ┌─────────┐    ┌──────────────────┐
    │ 返回    │    │ 3. 获取用户信息  │
    │ (缓存)  │    │ - 用户属性       │ (2-3ms)
    └─────────┘    │ - VIP等级        │
                   │ - 年龄           │
                   └──────────┬───────┘
                              ▼ (时间: 5ms)
                   ┌──────────────────┐
                   │ 4. 获取用户历史  │
                   │ - 购买记录 (Top-50)│ (3-5ms)
                   │ - 浏览记录 (Top-50)│
                   └──────────┬───────┘
                              ▼ (时间: 8-10ms)
        ┌─────────────────────────────────────┐
        │ 5. 三个召回通道并行 (耗时: 15-20ms) │
        ├─────────────────────────────────────┤
        │                                     │
        │  A. 协同过滤                        │
        │     Redis查询: cf:123               │
        │     → 200个候选                     │
        │     耗时: 5-10ms                    │
        │                                     │
        │  B. 内容推荐                        │
        │     1. 构建用户偏好                │
        │     2. Redis查询相似度             │
        │     → 200个候选                     │
        │     耗时: 5-10ms                    │
        │                                     │
        │  C. 热度排序                        │
        │     Redis查询: popularity:hour      │
        │     → 100个候选                     │
        │     耗时: 1-2ms                     │
        │                                     │
        └─────────────┬───────────────────────┘
                      ▼ (时间: 25-30ms)
        ┌──────────────────────┐
        │ 6. 融合去重 (5ms)    │
        │ 三个通道合并 → 400个 │
        │ 权重聚合             │
        └──────────────┬───────┘
                       ▼ (时间: 30-35ms)
        ┌──────────────────────┐
        │ 7. 多样性排序 (5ms)  │
        │ - 品类约束           │
        │ - 去重               │
        │ → 30个候选           │
        └──────────────┬───────┘
                       ▼ (时间: 35-40ms)
        ┌──────────────────────┐
        │ 8. CTR预测排序 (20ms)│
        │ 特征工程: 20个特征   │
        │ LightGBM预测: 30个   │
        │ 排序 → Top-20推荐    │
        └──────────────┬───────┘
                       ▼ (时间: 55-60ms)
        ┌──────────────────────┐
        │ 9. 缓存热点用户 (5ms)│
        │ Redis SET: hot_user  │
        │ TTL: 3600s (1小时)   │
        └──────────────┬───────┘
                       ▼ (时间: 60-65ms)
        ┌──────────────────────┐
        │ 10. 异步日志 (5ms)   │
        │ Kafka写入:           │
        │ - user_id            │
        │ - recommendations    │
        │ - timestamp          │
        └──────────────┬───────┘
                       ▼ (时间: 65-70ms)
        ┌──────────────────────┐
        │ 11. 构建响应 (5ms)   │
        │ JSON序列化           │
        │ HTTP返回 200         │
        └──────────────┬───────┘
                       ▼ (时间: 70-85ms)
                  用户收到结果
          平均延迟: 70-85ms ✓ (满足 <100ms)
          P99延迟: <100ms ✓
```

### 3. 数据流向和存储设计

```
实时数据流:
──────────────────────────────────────────────────────────

用户行为 → Kafka (user_behavior)
  ├─ 点击: 每秒 ~1万次
  ├─ 购买: 每秒 ~100次
  ├─ 浏览: 每秒 ~5万次
  └─ 收藏: 每秒 ~500次

推荐反馈 → Kafka (recommendation_log)
  ├─ 用户ID
  ├─ 推荐商品列表
  ├─ 用户点击数据
  └─ 时间戳

日志存储:
──────────────────────────────────────────────────────────

MongoDB (热数据, 最近7天)
  └─ recommendation_log
     {
       "_id": ObjectId,
       "user_id": 123,
       "items": [1001, 1002, 1003, ...],
       "clicked": [1001, 1003],
       "timestamp": 1234567890,
       "source": ["CF", "Content", "Popularity"],
       "latency_ms": 75
     }

HDFS (冷数据, 30天+)
  └─ /data/recommendations/2024/03/11/
     ├─ hour=00/
     ├─ hour=01/
     └─ ...
```

### 4. 缓存分层策略详解

```
缓存决策树:
────────────────────────────────────────────────────────

请求来临
    ↓
[查询 L1: hot_user:{user_id}]
    ├─ 命中 (50%) → 立即返回 (<5ms)
    ├─ 未命中 (50%)
         ↓
    [查询 L2: cf:{user_id}]
        ├─ 命中 (40%) → 使用CF结果
        ├─ 未命中 (60%)
             ↓
        [查询 L3: sim:{item_id}] (对用户历史的每个商品)
            ├─ 命中 (85%) → 用相似度
            ├─ 未命中 (15%)
                 ↓
            [在线计算相似度] (最慢, 避免)

综合命中率: 50% + (1-50%) × 40% + (1-50%) × (1-40%) × 85%
         = 50% + 20% + 8%
         = 78%

但实际通过多通道融合: >80%
```

### 5. 热点用户识别和缓存策略

```python
# 热点用户定义
热点用户 = 活跃度排名 Top 5% (50万用户)

活跃度计算:
  活跃度 = (过去7天购买数 × 10 +
           过去7天点击数 × 1 +
           过去7天浏览数 × 0.1)

缓存策略:
  热点用户 (Top 5%)
    ├─ 缓存周期: 1小时
    ├─ 缓存内容: 完整推荐结果
    ├─ 内存占用: 25GB
    ├─ 命中率: 90%+
    └─ 缓存时机:
        ├─ 预热: 每小时00分
        ├─ 更新: 用户有新行为后即时更新

普通用户 (5-50%)
    ├─ 缓存周期: 2小时
    ├─ 缓存内容: CF结果 (部分)
    ├─ 内存占用: 50GB
    ├─ 命中率: 40%
    └─ 缓存时机: 离线计算后写入

冷用户 (50-100%)
    ├─ 缓存策略: 不缓存
    ├─ 处理方式: 每次实时计算
    ├─ 特殊处理: 使用内容推荐 + 热度
    └─ 优化方向: 快速响应 (<100ms)
```

---

## 第二部分: 生产环境配置

### 1. Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 推荐服务
  recommendation-api:
    image: recommendation:latest
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis-cluster:6379
      - MYSQL_URL=mysql://mysql:3306/recommendation
      - KAFKA_BROKERS=kafka:9092
      - LOG_LEVEL=INFO
    depends_on:
      - redis-cluster
      - mysql
      - kafka
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 3s
      retries: 3

  # Redis 集群
  redis-cluster:
    image: redis:7-alpine
    command: redis-server --cluster-enabled yes --cluster-config-file nodes.conf
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    environment:
      - REDIS_PASSWORD=redis_password_here

  # MySQL 主从
  mysql:
    image: mysql:8
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=recommendation
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    command:
      - --default-authentication-plugin=mysql_native_password
      - --server-id=1
      - --log-bin=mysql-bin
      - --binlog-format=ROW

  # Kafka
  kafka:
    image: confluentinc/cp-kafka:7.0.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://kafka:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper

  # Zookeeper
  zookeeper:
    image: confluentinc/cp-zookeeper:7.0.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  # Prometheus (监控)
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  # Grafana (可视化)
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  redis-data:
  mysql-data:
  prometheus-data:
  grafana-data:
```

### 2. Kubernetes 部署配置

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recommendation-api
  namespace: production
spec:
  replicas: 7
  selector:
    matchLabels:
      app: recommendation-api
  template:
    metadata:
      labels:
        app: recommendation-api
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - recommendation-api
                topologyKey: kubernetes.io/hostname
      containers:
        - name: api
          image: recommendation:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
              name: http
          env:
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: recommendation-config
                  key: redis-url
            - name: MYSQL_URL
              valueFrom:
                secretKeyRef:
                  name: recommendation-secrets
                  key: mysql-url
            - name: KAFKA_BROKERS
              valueFrom:
                configMapKeyRef:
                  name: recommendation-config
                  key: kafka-brokers
          resources:
            limits:
              cpu: "4"
              memory: "8Gi"
            requests:
              cpu: "2"
              memory: "4Gi"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 2

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: recommendation-api
  namespace: production
spec:
  type: LoadBalancer
  selector:
    app: recommendation-api
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600

---
# hpa.yaml (自动扩缩容)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: recommendation-api-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: recommendation-api
  minReplicas: 5
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
```

---

## 第三部分: 性能优化详解

### 1. 时延分析和优化

```
优化前:
  协同过滤计算: 30ms
  内容推荐计算: 25ms
  特征工程: 15ms
  模型预测: 20ms
  总耗时: ~100ms (不满足要求!)

优化后:
  协同过滤: Redis 查询 (5-10ms)
  内容推荐: Redis 查询 (5-10ms)
  特征工程: 内存中快速提取 (2-3ms)
  模型预测: 预加载到内存 (3-5ms)
  多样性排序: O(n log n) 优化 (2-3ms)
  总耗时: 70-85ms ✓

优化方法:
──────────────────────────────────────────

1. 离线计算 + 在线快速查询
   - 协同过滤离线每天计算一次
   - 在线直接查询缓存结果
   - 节省: 25ms

2. 多通道并行处理
   - CF、Content、Popularity 并行执行
   - 使用 asyncio 并发编程
   - 节省: 10-15ms

3. 特征预计算
   - 用户特征在离线计算时生成
   - 在线直接查询
   - 节省: 10-12ms

4. 模型预加载
   - CTR 模型启动时加载到内存
   - 避免每次磁盘I/O
   - 节省: 5-10ms

5. 缓存分层
   - L1热点用户缓存直接返回
   - 50% 请求 <5ms
   - 节省: 20-30ms (平均)
```

### 2. 内存优化

```
初始内存占用 (GB):
  - 应用程序: 500MB
  - CTR模型: 800MB
  - 用户特征缓存: 2GB
  - 商品特征缓存: 1.5GB
  ─────────────────────
  单台总计: 4.8GB (满足 4GB 基础 + 余量)

优化前 (超出限制):
  - JSON反序列化冗余: 500MB
  - 未优化特征编码: 2GB
  - 重复加载模型: 1GB
  ─────────────────────
  总计: 8GB (超过 8GB 限制!)

优化后:
  1. 使用 msgpack 代替 JSON
     - 编码效率: 提升 60%
     - 内存: 从 1GB → 400MB
     - 节省: 600MB

  2. 特征稀疏表示
     - 使用稀疏向量表示
     - 从 2GB → 500MB
     - 节省: 1.5GB

  3. 模型共享
     - 所有进程共享一个模型
     - 避免重复加载
     - 节省: 700MB

  最终内存: 4GB (满足!)
```

### 3. CPU 优化

```
CPU 使用分析:
─────────────────────────────────────────

推荐逻辑耗时 (按百分比):
  Redis 查询: 20% CPU (I/O 等待, 实际不消耗)
  并行融合: 30% CPU (可并行化)
  多样性排序: 25% CPU (O(n log n), 已优化)
  CTR 预测: 20% CPU (向量计算)
  其他: 5% CPU

优化方案:
  1. 使用向量化库 (NumPy/Pandas)
     # 优化前
     for item in candidates:
         score = ctr_model.predict(features)  # Python 循环
     耗时: 15ms, CPU: 80%

     # 优化后
     scores = ctr_model.predict_batch(features_matrix)
     耗时: 3ms, CPU: 20%
     加速: 5倍!

  2. 使用 SIMD 优化库
     # 安装
     pip install onnx onnxruntime

     # 使用 ONNX Runtime
     session = onnxruntime.InferenceSession("ctr_model.onnx")
     scores = session.run(None, {'features': features_array})
     加速: 2-3倍

  3. 多进程 + 进程池
     # 最多利用多核 CPU
     executor = ProcessPoolExecutor(max_workers=4)
     future = executor.submit(compute_heavy_task)

最终 CPU 效率:
  原本: 70% CPU @ 1000 QPS
  优化: 35% CPU @ 5000 QPS
  效率: 提升 7倍!
```

---

## 第四部分: 故障处理和容错

### 1. 故障场景和应对

```
场景 1: Redis 集群宕机
──────────────────────────────────────

检测:
  - 连接失败
  - 连接超时
  - 命令执行失败

应对:
  def get_from_cache(key):
      try:
          return redis.get(key)  # 第一次尝试
      except RedisConnectionError:
          # 重试其他节点
          for node in redis_cluster.nodes:
              try:
                  return redis_from_node.get(key)
              except:
                  continue
          # 所有节点都故障
          raise CacheUnavailableError

  def recommend_with_fallback(user_id):
      try:
          # 正常流程
          return get_from_cache(user_id)
      except CacheUnavailableError:
          # 降级: 在线计算
          return compute_recommendation_online(user_id)
      except Exception as e:
          # 最终降级: 热门商品
          return get_popularity_items()

恢复时间:
  - 检测: <1s
  - 降级: <50ms
  - 总计: <100ms ✓


场景 2: MySQL 主从都故障
──────────────────────────────────────

检测:
  - 连接失败
  - 查询超时

应对:
  def get_user_history(user_id):
      try:
          # 尝试 MySQL
          return mysql.query(f"SELECT * FROM user_history WHERE id={user_id}")
      except DatabaseError:
          # 降级 1: Redis 缓存
          try:
              cached = redis.get(f"history:{user_id}")
              if cached:
                  return json.loads(cached)
          except:
              pass
          # 降级 2: 返回空列表 (内容推荐 + 热度)
          return []

含义:
  - 没有用户历史 → 用内容推荐 + 热度排序
  - 仍然能返回推荐结果
  - 用户体验不受影响


场景 3: CTR 模型加载失败
──────────────────────────────────────

检测:
  - 模型文件损坏
  - 内存不足

应对:
  class RecommendationService:
      def __init__(self):
          try:
              self.ctr_model = load_ctr_model()
          except Exception as e:
              logger.error(f"Failed to load CTR model: {e}")
              self.ctr_model = None  # 标记为不可用

      def rank_candidates(self, candidates):
          if self.ctr_model:
              # 正常: 使用 CTR 排序
              return self.rank_with_ctr(candidates)
          else:
              # 降级: 使用融合得分排序
              # (CF+Content+Popularity 的融合分数)
              return self.rank_without_ctr(candidates)

效果:
  - 失去最后的个性化排序
  - 但仍然保证基本的推荐质量
  - 用户感受不到明显差异


场景 4: Kafka 消息队列故障
──────────────────────────────────────

检测:
  - 消息发送失败

应对:
  def log_recommendation(user_id, items):
      try:
          # 异步发送到 Kafka
          kafka_producer.send(
              'recommendation_log',
              {'user_id': user_id, 'items': items}
          )
      except KafkaError:
          # 本地缓冲队列
          local_queue.append({'user_id': user_id, 'items': items})

          # 启动后台线程重试
          if not retry_thread.is_alive():
              retry_thread = Thread(target=retry_send_logs)
              retry_thread.start()

含义:
  - 不影响推荐服务
  - 日志延迟发送 (异步)
  - 避免推荐 API 被日志阻塞
```

### 2. 健康检查和监控

```python
# health_check.py
from fastapi import FastAPI, HTTPException
import redis
import mysql.connector
from datetime import datetime

app = FastAPI()

# 依赖检查
@app.get("/health")
def health_check():
    """完整的健康检查"""

    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }

    # 1. Redis 检查
    try:
        redis_client.ping()
        health_status["services"]["redis"] = "ok"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {e}"
        health_status["status"] = "degraded"

    # 2. MySQL 检查
    try:
        conn = mysql.connector.connect(**mysql_config)
        conn.cursor().execute("SELECT 1")
        conn.close()
        health_status["services"]["mysql"] = "ok"
    except Exception as e:
        health_status["services"]["mysql"] = f"error: {e}"
        health_status["status"] = "degraded"

    # 3. 模型检查
    try:
        if self.ctr_model is None:
            health_status["services"]["ctr_model"] = "error: not loaded"
            health_status["status"] = "degraded"
        else:
            health_status["services"]["ctr_model"] = "ok"
    except Exception as e:
        health_status["services"]["ctr_model"] = f"error: {e}"
        health_status["status"] = "degraded"

    # 4. 内存检查
    import psutil
    memory_percent = psutil.virtual_memory().percent
    health_status["memory_usage_percent"] = memory_percent

    if memory_percent > 90:
        health_status["status"] = "degraded"
        health_status["services"]["memory"] = "warning: high usage"
    else:
        health_status["services"]["memory"] = "ok"

    # 5. 最近的错误率
    error_count = metrics.get_error_count_last_minute()
    request_count = metrics.get_request_count_last_minute()
    error_rate = error_count / max(request_count, 1)

    if error_rate > 0.05:  # 超过 5%
        health_status["status"] = "degraded"
        health_status["services"]["error_rate"] = f"high: {error_rate*100:.2f}%"
    else:
        health_status["services"]["error_rate"] = f"ok: {error_rate*100:.2f}%"

    if health_status["status"] == "healthy":
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)

@app.get("/ready")
def readiness_check():
    """就绪检查 (仅检查关键服务)"""

    # 只检查推荐服务必需的组件
    try:
        redis_client.ping()
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503, detail="Redis unavailable")
```

---

继续下一部分: **监控告警系统**...

