# 算法顾问 (Algorithm Advisor) - 参考资源

## 相关工具和框架

### 算法分析
- Big O Cheat Sheet - 算法复杂度速查
- Visualgo - 算法可视化
- Algorithm Archive - 算法实现参考

### 推荐系统
- Spark MLlib - 机器学习库
- TensorFlow Recommenders - 推荐系统框架
- Alibaba Graph Learning - 图算法库

### 性能工具
- JMH - Java 性能基准测试
- Go Benchmark - Go 性能测试
- PyBench - Python 性能测试

## 常见算法速查表

### 查找和排序
| 操作 | 最坏 | 平均 | 最好 | 空间 |
|------|------|------|------|------|
| Linear Search | O(n) | O(n) | O(1) | O(1) |
| Binary Search | O(log n) | O(log n) | O(1) | O(1) |
| Hash Lookup | O(n) | O(1) | O(1) | O(n) |
| Quicksort | O(n²) | O(n log n) | O(n log n) | O(log n) |
| Mergesort | O(n log n) | O(n log n) | O(n log n) | O(n) |

### 数据结构
| 结构 | 查找 | 插入 | 删除 | 空间 |
|------|------|------|------|------|
| Array | O(1) | O(n) | O(n) | O(n) |
| Linked List | O(n) | O(1) | O(1) | O(n) |
| Hash Table | O(1) | O(1) | O(1) | O(n) |
| Binary Tree | O(log n) | O(log n) | O(log n) | O(n) |
| Heap | O(log n) | O(log n) | O(log n) | O(n) |

## 推荐阅读

### 系统设计
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "System Design Interview" - Alex Xu

### 算法
- "Introduction to Algorithms" - CLRS
- "Algorithm Design Manual" - Steven Skiena

### 推荐系统
- "Recommendation Systems" - Aggarwal
- "Deep Learning for Recommender Systems" - Cheng et al.

## 最佳实践

1. **了解你的数据**
   - 数据规模、分布、更新频率
   - 用户访问模式和热点数据

2. **设定明确的目标**
   - 性能目标（延迟、吞吐量）
   - 准确性或业务指标
   - 成本限制

3. **评估多个方案**
   - 不要只考虑一个解决方案
   - 比较性能和成本权衡

4. **逐步优化**
   - 从简单的解决方案开始
   - 证明瓶颈后再优化
   - 使用基准测试验证改进

5. **考虑运维**
   - 复杂度不仅是时间复杂度
   - 实现复杂度、维护成本同样重要
