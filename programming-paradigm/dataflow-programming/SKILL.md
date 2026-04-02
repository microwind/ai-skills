---
name: 数据流编程
description: "以数据流动为核心的编程范式，程序表示为节点间的数据转换图，天然支持并行执行。"
license: MIT
---

# 数据流编程 (Dataflow Programming)

## 概述

数据流编程将程序建模为**有向图**：节点是计算单元，边是数据通道。数据到达即触发计算，天然支持并行。

```
输入数据 → [过滤] → [转换] → [聚合] → 输出
              │                    ↑
              └──→ [验证] ──→ [丰富] ──┘
```

## 代码示例

```python
# Unix 管道：最经典的数据流
# cat log.txt | grep "ERROR" | awk '{print $3}' | sort | uniq -c

# Python 数据流管道
from functools import reduce

def pipeline(*steps):
    def execute(data):
        return reduce(lambda d, step: step(d), steps, data)
    return execute

# 定义处理节点
def read_records(path):
    import csv
    with open(path) as f:
        return list(csv.DictReader(f))

def filter_active(records):
    return [r for r in records if r["status"] == "active"]

def calculate_totals(records):
    return [
        {**r, "total": float(r["price"]) * int(r["quantity"])}
        for r in records
    ]

def summarize(records):
    total = sum(r["total"] for r in records)
    return {"count": len(records), "total_amount": total}

# 组合管道
process = pipeline(
    filter_active,
    calculate_totals,
    summarize
)

data = read_records("orders.csv")
result = process(data)
```

## 流处理框架

```java
// Apache Flink / Kafka Streams 风格
DataStream<Order> orders = env.addSource(new KafkaSource<>("orders"));

orders
    .filter(order -> order.getAmount() > 100)
    .keyBy(Order::getCategory)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new SumAggregator())
    .addSink(new ElasticsearchSink<>());

// 数据到达即处理，无需等待全部数据
```

```typescript
// Node.js Stream：数据流处理
import { createReadStream } from 'fs';
import { Transform } from 'stream';

const filterTransform = new Transform({
    objectMode: true,
    transform(chunk, encoding, callback) {
        const record = JSON.parse(chunk);
        if (record.status === 'active') {
            this.push(JSON.stringify(record));
        }
        callback();
    }
});

createReadStream('data.jsonl')
    .pipe(filterTransform)
    .pipe(process.stdout);
```

## 应用场景

| 场景 | 工具 | 说明 |
|------|------|------|
| 流数据处理 | Kafka Streams, Flink | 实时事件处理 |
| ETL 管道 | Apache Beam, Airflow | 数据转换和加载 |
| 音视频处理 | GStreamer, FFmpeg | 媒体流处理 |
| 可视化编程 | Node-RED, Scratch | 拖拽式数据流 |
| 电子表格 | Excel | 单元格间的数据依赖 |

## 优缺点

### ✅ 优点
- **天然并行** — 无依赖的节点可以并行执行
- **可组合** — 节点可自由组合成不同管道
- **可视化友好** — 数据流图直观

### ❌ 缺点
- **状态管理复杂** — 有状态的节点需要特殊处理
- **调试困难** — 数据在节点间流动难以追踪
- **不适合交互式** — 更适合批处理/流处理

## 与其他范式的关系

| 范式 | 关系 |
|------|------|
| [FP](../functional-programming/) | 管道 = 函数组合 |
| [响应式](../reactive-programming/) | 响应式是数据流的一种实现 |
| [并发编程](../concurrent-programming/) | 数据流天然支持并行 |

## 总结

**核心**：程序 = 数据流图，节点接收数据 → 处理 → 输出到下一个节点。

**适用**：ETL管道、流处理、音视频处理、数据分析。
