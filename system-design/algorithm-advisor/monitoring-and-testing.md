# 混合推荐系统 - 监控、告警和数据管道

## 第一部分: 监控告警系统

### 1. Prometheus 监控指标

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'production'
    service: 'recommendation'

scrape_configs:
  - job_name: 'recommendation-api'
    static_configs:
      - targets: ['localhost:8000']
    metric_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'redis-cluster'
    static_configs:
      - targets: ['localhost:6379']

  - job_name: 'mysql'
    static_configs:
      - targets: ['localhost:9104']  # MySQL exporter

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

rule_files:
  - 'rules.yml'
```

### 2. 告警规则定义

```yaml
# rules.yml
groups:
  - name: recommendation_alerts
    interval: 30s
    rules:
      # 1. 推荐延迟告警
      - alert: HighRecommendationLatency
        expr: |
          histogram_quantile(0.99, recommendation_latency_ms) > 100
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "推荐延迟过高 (P99 > 100ms)"
          description: "当前P99延迟: {{ $value }}ms"

      # 2. 缓存命中率降低
      - alert: LowCacheHitRate
        expr: |
          cache_hit_rate < 0.75
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "缓存命中率低于75%"
          description: "当前命中率: {{ $value | humanizePercentage }}"

      # 3. Redis 连接失败
      - alert: RedisConnectionError
        expr: |
          increase(redis_connection_errors_total[5m]) > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis连接错误频繁"
          description: "最近5分钟错误次数: {{ $value }}"

      # 4. 错误率过高
      - alert: HighErrorRate
        expr: |
          (increase(recommendation_errors_total[5m]) /
           increase(recommendation_requests_total[5m])) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "推荐服务错误率超过5%"
          description: "当前错误率: {{ $value | humanizePercentage }}"

      # 5. QPS 异常下降
      - alert: LowQPS
        expr: |
          rate(recommendation_requests_total[5m]) < 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "推荐服务QPS异常下降"
          description: "当前QPS: {{ $value }}"

      # 6. 内存使用过高
      - alert: HighMemoryUsage
        expr: |
          process_resident_memory_bytes / 1024 / 1024 / 1024 > 7
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "推荐服务内存使用过高"
          description: "当前内存: {{ $value | humanize }}GB"

      # 7. CPU 使用过高
      - alert: HighCPUUsage
        expr: |
          rate(process_cpu_seconds_total[5m]) * 100 > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "推荐服务CPU使用过高"
          description: "当前CPU使用率: {{ $value | humanize }}%"

      # 8. CTR 模型准确率下降
      - alert: LowCTRAccuracy
        expr: |
          ctr_model_auc < 0.70
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "CTR模型AUC低于0.70"
          description: "当前AUC: {{ $value }}"

      # 9. 离线计算任务失败
      - alert: OfflineComputationFailed
        expr: |
          increase(offline_computation_failures_total[1h]) > 0
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "离线计算任务失败"
          description: "最近1小时失败次数: {{ $value }}"
```

### 3. 自定义指标定义 (Python)

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info
import time

# 请求指标
recommendation_requests_total = Counter(
    'recommendation_requests_total',
    'Total recommendation requests',
    ['endpoint', 'status']
)

recommendation_latency_ms = Histogram(
    'recommendation_latency_ms',
    'Recommendation latency in milliseconds',
    buckets=[10, 20, 50, 100, 200, 500, 1000],
    ['endpoint']
)

recommendation_errors_total = Counter(
    'recommendation_errors_total',
    'Total recommendation errors',
    ['error_type']
)

# 缓存指标
cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Cache hit rate',
    ['cache_level']
)

cache_access_total = Counter(
    'cache_access_total',
    'Total cache accesses',
    ['cache_level', 'result']
)

# 连接指标
redis_connection_errors_total = Counter(
    'redis_connection_errors_total',
    'Redis connection errors'
)

mysql_connection_pool_size = Gauge(
    'mysql_connection_pool_size',
    'MySQL connection pool size'
)

# 业务指标
ctr_score_distribution = Histogram(
    'ctr_score_distribution',
    'Distribution of CTR scores',
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

recommendation_diversity_score = Gauge(
    'recommendation_diversity_score',
    'Average diversity score of recommendations'
)

recommendation_ctr = Gauge(
    'recommendation_ctr',
    'Recommendation click-through rate'
)

# 模型指标
ctr_model_auc = Gauge(
    'ctr_model_auc',
    'CTR model AUC score'
)

ctr_model_load_time_ms = Gauge(
    'ctr_model_load_time_ms',
    'CTR model load time in milliseconds'
)

# 离线计算指标
offline_computation_duration_minutes = Histogram(
    'offline_computation_duration_minutes',
    'Offline computation duration in minutes',
    buckets=[30, 60, 90, 120, 150, 180],
    ['computation_type']
)

offline_computation_failures_total = Counter(
    'offline_computation_failures_total',
    'Offline computation failures',
    ['computation_type']
)

# 装饰器: 自动记录指标
def track_metrics(endpoint_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                latency = (time.time() - start_time) * 1000
                recommendation_latency_ms.labels(
                    endpoint=endpoint_name
                ).observe(latency)
                recommendation_requests_total.labels(
                    endpoint=endpoint_name,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                latency = (time.time() - start_time) * 1000
                recommendation_latency_ms.labels(
                    endpoint=endpoint_name
                ).observe(latency)
                recommendation_errors_total.labels(
                    error_type=type(e).__name__
                ).inc()
                recommendation_requests_total.labels(
                    endpoint=endpoint_name,
                    status='error'
                ).inc()
                raise
        return wrapper
    return decorator
```

### 4. Grafana 仪表板配置

```json
{
  "dashboard": {
    "title": "推荐系统监控",
    "panels": [
      {
        "title": "推荐延迟 (实时)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, recommendation_latency_ms)",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, recommendation_latency_ms)",
            "legendFormat": "P99"
          }
        ],
        "yaxes": [
          {"format": "ms", "label": "延迟(ms)"}
        ],
        "alert": {
          "message": "P99延迟超过100ms"
        }
      },
      {
        "title": "缓存命中率",
        "type": "gauge",
        "targets": [
          {
            "expr": "cache_hit_rate{cache_level='L1'}",
            "legendFormat": "L1缓存"
          },
          {
            "expr": "cache_hit_rate{cache_level='L2'}",
            "legendFormat": "L2缓存"
          },
          {
            "expr": "cache_hit_rate{cache_level='L3'}",
            "legendFormat": "L3缓存"
          }
        ]
      },
      {
        "title": "请求QPS",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(recommendation_requests_total[1m])",
            "legendFormat": "总QPS"
          }
        ]
      },
      {
        "title": "错误率",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(recommendation_errors_total[5m]) / rate(recommendation_requests_total[5m])",
            "legendFormat": "错误率"
          }
        ]
      },
      {
        "title": "CTR 模型性能",
        "type": "gauge",
        "targets": [
          {
            "expr": "ctr_model_auc",
            "legendFormat": "AUC"
          }
        ]
      },
      {
        "title": "系统资源使用",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes / 1024 / 1024",
            "legendFormat": "内存(MB)"
          },
          {
            "expr": "rate(process_cpu_seconds_total[1m]) * 100",
            "legendFormat": "CPU使用率(%)"
          }
        ]
      }
    ]
  }
}
```

---

## 第二部分: 数据管道和 A/B 测试框架

### 1. 实时数据处理管道 (Kafka + Spark Streaming)

```python
# data_pipeline.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, count, avg
import json

class RecommendationDataPipeline:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("RecommendationDataPipeline") \
            .getOrCreate()

    def process_recommendation_logs(self):
        """
        实时处理推荐日志，计算关键指标
        """
        # 读取 Kafka 数据流
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", "recommendation_log") \
            .option("startingOffsets", "latest") \
            .load()

        # 解析 JSON 数据
        schema = """
            user_id LONG,
            items ARRAY<LONG>,
            clicked ARRAY<LONG>,
            timestamp LONG,
            latency_ms INT,
            source ARRAY<STRING>
        """

        parsed_df = df \
            .select(from_json(col("value").cast("string"), schema).alias("data")) \
            .select("data.*")

        # 1. 实时计算推荐准确率
        accuracy_df = parsed_df \
            .withColumn("accuracy", col("array_size(clicked)") / col("array_size(items)")) \
            .groupBy(window(col("timestamp"), "1 minute")) \
            .agg(avg("accuracy").alias("avg_accuracy"))

        # 2. 实时计算推荐延迟分布
        latency_df = parsed_df \
            .groupBy(window(col("timestamp"), "1 minute")) \
            .agg(
                avg("latency_ms").alias("avg_latency"),
                max("latency_ms").alias("max_latency"),
                min("latency_ms").alias("min_latency")
            )

        # 3. 写入 Redis (实时监控)
        accuracy_df.writeStream \
            .format("org.apache.spark.sql.redis") \
            .option("redis.host", "redis") \
            .option("redis.port", "6379") \
            .option("key", "recommendation:accuracy") \
            .start()

        latency_df.writeStream \
            .format("org.apache.spark.sql.redis") \
            .option("redis.host", "redis") \
            .option("redis.port", "6379") \
            .option("key", "recommendation:latency") \
            .start()

        # 4. 写入 MongoDB (历史数据)
        accuracy_df.writeStream \
            .format("com.mongodb.spark.sql") \
            .option("uri", "mongodb://mongodb/recommendation.accuracy") \
            .option("replacedocument", "false") \
            .start()

        self.spark.streams.awaitAnyTermination()

    def process_user_feedback(self):
        """
        处理用户反馈，用于模型训练
        """
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", "user_feedback") \
            .load()

        schema = """
            user_id LONG,
            item_id LONG,
            action STRING,
            timestamp LONG
        """

        parsed_df = df \
            .select(from_json(col("value").cast("string"), schema).alias("data")) \
            .select("data.*")

        # 计算用户兴趣
        interest_df = parsed_df \
            .filter(col("action").isin(["purchase", "like"])) \
            .groupBy("user_id", "item_id") \
            .agg(count("*").alias("interest_count"))

        # 计算商品热度
        popularity_df = parsed_df \
            .groupBy("item_id") \
            .agg(count("*").alias("popularity_score"))

        # 写入 HDFS (离线训练数据)
        interest_df.writeStream \
            .format("parquet") \
            .option("path", "/data/user_interests") \
            .option("checkpointLocation", "/checkpoint/interests") \
            .start()

        popularity_df.writeStream \
            .format("parquet") \
            .option("path", "/data/item_popularity") \
            .option("checkpointLocation", "/checkpoint/popularity") \
            .start()

        self.spark.streams.awaitAnyTermination()
```

### 2. A/B 测试框架

```python
# ab_testing.py
import random
import json
from datetime import datetime
from typing import Dict, List

class ABTestingFramework:
    """
    A/B 测试框架，支持多个测试同时进行
    """

    def __init__(self, redis_client, mysql_client):
        self.redis = redis_client
        self.mysql = mysql_client

    def create_experiment(
        self,
        experiment_id: str,
        name: str,
        description: str,
        start_date: str,
        end_date: str,
        traffic_allocation: Dict[str, float],
        metrics: List[str]
    ):
        """
        创建新的 A/B 测试

        参数:
            experiment_id: 测试ID
            name: 测试名称
            traffic_allocation: 流量分配
                {
                    'control': 0.5,      # 对照组 (旧算法)
                    'variant_a': 0.25,   # 测试组A (新算法1)
                    'variant_b': 0.25    # 测试组B (新算法2)
                }
            metrics: 跟踪的指标
                ['ctr', 'cvr', 'latency', 'diversity_score']
        """

        experiment = {
            'id': experiment_id,
            'name': name,
            'description': description,
            'start_date': start_date,
            'end_date': end_date,
            'traffic_allocation': traffic_allocation,
            'metrics': metrics,
            'created_at': datetime.now().isoformat(),
            'status': 'running'
        }

        # 保存到 MySQL
        self.mysql.insert('experiments', experiment)

        # 保存到 Redis (快速查询)
        self.redis.set(
            f'experiment:{experiment_id}',
            json.dumps(experiment),
            ex=86400*7  # 保留7天
        )

    def assign_user_to_group(self, user_id: int, experiment_id: str) -> str:
        """
        根据实验配置，将用户分配到对照组或测试组

        使用一致性哈希确保：
        1. 同一用户总是分配到同一组
        2. 流量分配比例正确
        """

        # 生成用户在该实验中的哈希值
        hash_key = f"{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16) % 100

        # 获取实验配置
        experiment = json.loads(
            self.redis.get(f'experiment:{experiment_id}')
        )

        # 根据流量分配确定分组
        traffic_allocation = experiment['traffic_allocation']
        cumulative = 0

        for group_name, allocation_percentage in traffic_allocation.items():
            cumulative += allocation_percentage * 100

            if hash_value < cumulative:
                # 缓存用户的分组 (避免重复计算)
                self.redis.set(
                    f'user_group:{experiment_id}:{user_id}',
                    group_name,
                    ex=86400*7
                )
                return group_name

        return 'control'  # 默认返回对照组

    def get_user_group(self, user_id: int, experiment_id: str) -> str:
        """
        获取用户在该实验中的分组
        (首先查询缓存，避免重复计算)
        """

        # 查询缓存
        cached_group = self.redis.get(f'user_group:{experiment_id}:{user_id}')

        if cached_group:
            return cached_group

        # 缓存未命中，计算分组
        return self.assign_user_to_group(user_id, experiment_id)

    def log_metric(
        self,
        experiment_id: str,
        user_id: int,
        group: str,
        metric_name: str,
        metric_value: float
    ):
        """
        记录用户在实验中的指标
        """

        metric_record = {
            'experiment_id': experiment_id,
            'user_id': user_id,
            'group': group,
            'metric_name': metric_name,
            'metric_value': metric_value,
            'timestamp': datetime.now().isoformat()
        }

        # 异步写入 Kafka
        self.kafka_producer.send('ab_test_metrics', metric_record)

        # 同步写入 Redis (用于实时分析)
        key = f'ab_test:{experiment_id}:{group}:{metric_name}'
        self.redis.lpush(key, json.dumps(metric_record))
        self.redis.expire(key, 86400*7)

    def calculate_metrics(
        self,
        experiment_id: str
    ) -> Dict[str, Dict[str, float]]:
        """
        计算实验的关键指标

        返回格式:
            {
                'control': {
                    'ctr': 0.08,
                    'cvr': 0.01,
                    'latency': 85,
                    'diversity_score': 0.92
                },
                'variant_a': {
                    'ctr': 0.12,
                    'cvr': 0.02,
                    'latency': 88,
                    'diversity_score': 0.94
                },
                ...
            }
        """

        experiment = json.loads(
            self.redis.get(f'experiment:{experiment_id}')
        )

        results = {}

        for group in experiment['traffic_allocation'].keys():
            results[group] = {}

            for metric_name in experiment['metrics']:
                # 从 MongoDB 查询原始数据
                query = {
                    'experiment_id': experiment_id,
                    'group': group,
                    'metric_name': metric_name
                }

                records = list(
                    self.mongodb.find('ab_test_metrics', query)
                )

                # 计算统计量
                values = [r['metric_value'] for r in records]

                if values:
                    results[group][metric_name] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'count': len(values),
                        '95_percentile': np.percentile(values, 95)
                    }

        return results

    def calculate_statistical_significance(
        self,
        control_values: List[float],
        treatment_values: List[float],
        alpha: float = 0.05
    ) -> Dict:
        """
        计算统计显著性 (T-test)
        """
        from scipy import stats

        t_statistic, p_value = stats.ttest_ind(control_values, treatment_values)

        is_significant = p_value < alpha

        return {
            't_statistic': t_statistic,
            'p_value': p_value,
            'is_significant': is_significant,
            'confidence_level': 1 - alpha
        }

    def generate_report(self, experiment_id: str) -> str:
        """
        生成 A/B 测试报告
        """

        experiment = json.loads(
            self.redis.get(f'experiment:{experiment_id}')
        )

        metrics_results = self.calculate_metrics(experiment_id)

        report = f"""
╔════════════════════════════════════════════════════════════╗
║          A/B 测试报告                                      ║
╚════════════════════════════════════════════════════════════╝

实验名称: {experiment['name']}
实验ID: {experiment_id}
说明: {experiment['description']}
时间: {experiment['start_date']} ~ {experiment['end_date']}
流量分配: {experiment['traffic_allocation']}

┌────────────────────────────────────────────────────────────┐
│                    关键指标                                 │
└────────────────────────────────────────────────────────────┘
"""

        for metric_name in experiment['metrics']:
            report += f"\n{metric_name.upper()}:\n"

            for group, metrics in metrics_results.items():
                if metric_name in metrics:
                    m = metrics[metric_name]
                    report += f"  {group:12} 平均值: {m['mean']:.4f} "
                    report += f"(样本数: {m['count']}, 标准差: {m['std']:.4f})\n"

        # 统计显著性检验
        report += "\n┌────────────────────────────────────────────────────────────┐\n"
        report += "│                  统计显著性检验                            │\n"
        report += "└────────────────────────────────────────────────────────────┘\n"

        control_ctr = metrics_results.get('control', {}).get('ctr', {})
        variant_a_ctr = metrics_results.get('variant_a', {}).get('ctr', {})

        if control_ctr and variant_a_ctr:
            # 重建原始数据 (这里简化，实际应该从数据库查询)
            control_values = [control_ctr['mean']] * control_ctr['count']
            variant_a_values = [variant_a_ctr['mean']] * variant_a_ctr['count']

            sig_result = self.calculate_statistical_significance(
                control_values,
                variant_a_values
            )

            report += f"\nCTR (Control vs Variant A):\n"
            report += f"  p-value: {sig_result['p_value']:.6f}\n"
            report += f"  显著性: {'✓ 显著' if sig_result['is_significant'] else '✗ 不显著'}\n"

        report += "\n┌────────────────────────────────────────────────────────────┐\n"
        report += "│                    建议                                     │\n"
        report += "└────────────────────────────────────────────────────────────┘\n"

        # 生成建议
        if variant_a_ctr and control_ctr:
            if variant_a_ctr['mean'] > control_ctr['mean'] * 1.1:
                report += "\n✓ Variant A 的CTR显著高于Control (提升>10%)\n"
                report += "  建议: 灰度发布 Variant A (逐步增加流量)"
            elif variant_a_ctr['mean'] < control_ctr['mean'] * 0.9:
                report += "\n✗ Variant A 的CTR显著低于Control (下降>10%)\n"
                report += "  建议: 回滚 Variant A，不推荐发布"
            else:
                report += "\n≈ Variant A 与 Control 性能相近\n"
                report += "  建议: 继续观察，需要更多样本数据"

        return report
```

### 3. 推荐服务集成 A/B 测试

```python
# recommendation_service.py (集成 A/B 测试)
from fastapi import FastAPI
from ab_testing import ABTestingFramework

app = FastAPI()
ab_test = ABTestingFramework(redis_client, mysql_client)

@app.get("/recommend")
def recommend(user_id: int, limit: int = 20):
    """
    支持 A/B 测试的推荐接口
    """

    # 1. 检查该用户是否在任何活跃的实验中
    experiments = get_active_experiments()  # 从数据库查询

    user_groups = {}  # 存储用户在各实验中的分组

    for experiment in experiments:
        group = ab_test.get_user_group(user_id, experiment['id'])
        user_groups[experiment['id']] = group

    # 2. 根据分组选择推荐算法
    recommendations = None

    for experiment_id, group in user_groups.items():
        if group == 'control':
            # 对照组: 使用原有算法 (CF + Content + Popularity)
            recommendations = recommend_with_hybrid(user_id, limit)

        elif group == 'variant_a':
            # 测试组A: 使用新算法 (比如加入用户协作信号)
            recommendations = recommend_with_variant_a(user_id, limit)

        elif group == 'variant_b':
            # 测试组B: 使用另一个新算法
            recommendations = recommend_with_variant_b(user_id, limit)

        # 立即记录指标
        # (避免等待日志处理)
        ab_test.log_metric(
            experiment_id=experiment_id,
            user_id=user_id,
            group=group,
            metric_name='latency_ms',
            metric_value=latency_ms
        )

    # 3. 如果没有实验，使用默认算法
    if not recommendations:
        recommendations = recommend_with_hybrid(user_id, limit)

    return {
        'items': recommendations,
        'user_groups': user_groups,
        'latency_ms': latency_ms
    }

@app.post("/feedback")
def log_feedback(user_id: int, item_id: int, action: str):
    """
    记录用户反馈（用于 A/B 测试指标计算）
    """

    # 1. 查找该用户所在的实验
    experiments = get_active_experiments()

    for experiment in experiments:
        group = ab_test.get_user_group(user_id, experiment['id'])

        # 2. 根据反馈类型，记录不同的指标
        if action == 'click':
            ab_test.log_metric(
                experiment_id=experiment['id'],
                user_id=user_id,
                group=group,
                metric_name='ctr',
                metric_value=1.0
            )

        elif action == 'purchase':
            ab_test.log_metric(
                experiment_id=experiment['id'],
                user_id=user_id,
                group=group,
                metric_name='cvr',
                metric_value=1.0
            )

    # 3. 同时发送到 Kafka 供离线分析
    kafka_producer.send('user_feedback', {
        'user_id': user_id,
        'item_id': item_id,
        'action': action,
        'timestamp': time.time()
    })

    return {'status': 'success'}

@app.get("/ab_test_report/{experiment_id}")
def get_ab_test_report(experiment_id: str):
    """
    获取 A/B 测试报告
    """

    report = ab_test.generate_report(experiment_id)

    return {
        'experiment_id': experiment_id,
        'report': report,
        'timestamp': datetime.now().isoformat()
    }
```

---

**下一步将包含:**
- 扩展性和性能优化方案 (如何支持 10 倍增长)
- 详细的部署脚本和自动化配置
- 模型训练和更新流程
- 实时特征工程系统
- 更多的生产级代码示例
