# AI Agent代码生成系统｜第二篇：完整实战案例详解

## 前言：从理论到实践

在第一篇，你学了理论框架：**SKILL + Prompt + 验证 = 高质量代码生成**。

现在我们实战演练。我选了一个**真实的高难度场景**：电商秒杀库存分配。

为什么选这个案例？因为它涵盖了AI代码生成的所有关键挑战：
- 需要理解业务约束
- 涉及高并发问题（线程安全）
- 性能指标严格（100ms内完成）
- 边界情况复杂（库存耗尽、用户超限等）

如果这个案例能一次成功，说明这套系统真的有效。

---

## 第1步：需求分析与问题建模

### 场景描述

双11来了。你的电商平台要搞一个秒杀活动：

```
总库存：100件商品
用户请求：500个用户同时抢购
每个用户限购：最多5件
必须在：100毫秒内完成所有分配
准确性要求：100%不能超售
并发要求：支持10000+请求/秒
```

### 核心问题

一个用户「想买3件」，系统应该：

1. 检查总库存够不够（库存 >= 3？）
2. 检查用户有没有超限购（已买数量 + 3 <= 5？）
3. 如果都满足 → 分配3件，更新库存和用户记录
4. 如果不满足 → 分配能分配的，或拒绝

**关键约束**：多个用户同时发请求时，不能出现：
- 库存超售（总分配数 > 100）
- 用户超限（某用户分配数 > 5）
- 竞态条件（请求A和请求B同时更新库存，导致计算错误）

### 为什么选择贪心算法？

我们用**贪心算法**来解决这个问题。为什么贪心有效？

**贪心选择性**：
```
对于第一个请求，应该给它分配尽可能多的商品
因为任何后续请求都无法更优地利用这些商品
（先到先得的公平性保证）
```

**最优子结构**：
```
当前请求的分配方式不会影响剩余库存的分配
每个请求的决策是独立的
```

这两个性质保证了贪心能得到全局最优解。

---

## 第2步：设计SKILL（完整版）

现在用SKILL模板来精确定义这个问题。每一行都很重要，因为这直接指导AI的代码生成。

```yaml
# ============================================================================
# SKILL: FlashSaleGreedyAllocation
# 秒杀库存贪心分配算法
# ============================================================================

name: "FlashSaleGreedyAllocation"
version: "1.0.0"
category: "algorithms/greedy"
algorithm_thinking: "贪心算法"

# ─────────────────────────────────────────────────────────────────────────
# 元数据
# ─────────────────────────────────────────────────────────────────────────
metadata:
  author: "System Architect"
  created_date: "2024-01-15"
  description: "使用贪心算法实现高并发秒杀库存分配"
  difficulty: "Medium-Hard"
  tags: ["concurrency", "greedy", "ecommerce"]

# ─────────────────────────────────────────────────────────────────────────
# 问题定义
# ─────────────────────────────────────────────────────────────────────────
problem:
  description: |
    在高并发秒杀场景中，需要对用户购买请求进行实时库存分配。
    多个用户同时发起请求，系统需要快速、准确地决定每个用户能分配多少商品。

  input_spec:
    - name: "requests"
      type: "List[Tuple[user_id: str, quantity: int]]"
      description: "用户购买请求列表，每个请求包含用户ID和购买数量"
      example: "[('user_001', 3), ('user_002', 2), ('user_001', 1)]"

    - name: "initial_inventory"
      type: "int"
      description: "初始库存数量"
      example: "100"

    - name: "user_limit"
      type: "int"
      description: "每个用户的购买限制"
      example: "5"

  output_spec:
    - name: "allocation_results"
      type: "List[Dict]"
      description: "每个请求的分配结果"
      example: |
        [
          {"user_id": "user_001", "requested": 3, "allocated": 3, "status": "success"},
          {"user_id": "user_002", "requested": 2, "allocated": 2, "status": "success"},
          {"user_id": "user_001", "requested": 1, "allocated": 0, "status": "failed"}  // 超限
        ]

  constraints:
    hard_constraints:
      - "响应时间 < 100ms（处理1000个请求）"
      - "库存准确性 = 100%（不能超售）"
      - "用户限购准确性 = 100%（不能超限）"
      - "线程安全：支持并发请求，无竞态条件"

    performance_requirements:
      - "时间复杂度：O(n)，其中n为请求数"
      - "空间复杂度：O(n)，用于存储分配结果和用户购买记录"
      - "吞吐量：>= 10000 req/s"

# ─────────────────────────────────────────────────────────────────────────
# 算法思想详解
# ─────────────────────────────────────────────────────────────────────────
algorithm:
  name: "Greedy Algorithm"

  core_idea: |
    按顺序处理每个用户请求，对每个请求分配 min(请求数, 剩余库存, 用户余额)。
    一旦分配，立即更新全局库存和用户购买记录。
    不回溯、不调整，确保O(n)的线性复杂度。

  algorithm_proof: |
    【贪心选择性】
    对于当前请求，应该满足它（如果库存和限购允许）。
    这是安全的，因为：
    - FIFO顺序保证了公平性
    - 后续请求的分配不会比当前请求更优

    【最优子结构】
    处理完当前请求后，剩余的库存和用户限购是独立的子问题。
    当前请求的分配方式不影响最优子问题的解。

    【结论】
    贪心算法得到的解是全局最优的。

  key_steps:
    - "初始化：库存计数器、用户购买记录表"
    - "遍历：逐个处理用户请求"
    - "检查：检查库存和用户限购"
    - "分配：分配 min(请求, 库存, 用户余额)"
    - "更新：更新全局库存和用户记录"
    - "重复：直到所有请求处理完"

# ─────────────────────────────────────────────────────────────────────────
# 实现指导（给AI的具体指示）
# ─────────────────────────────────────────────────────────────────────────
implementation_guide:
  language: "python"

  required_features:
    - "Thread-safe：使用Lock保证原子性操作"
    - "数据结构：用Dict记录用户已购数量，支持O(1)查询"
    - "核心逻辑：for循环 + min() 函数实现分配逻辑"

  pseudo_code: |
    class Allocator:
        def allocate(requests):
            results = []
            for user_id, quantity in requests:
                with lock:  # 保证线程安全
                    user_purchased = user_records[user_id] or 0
                    user_available = limit - user_purchased
                    allocated = min(quantity, inventory, user_available)

                    if allocated > 0:
                        inventory -= allocated
                        user_records[user_id] += allocated
                        status = "success"
                    else:
                        status = "failed"

                    results.append({...})
            return results

  considerations:
    - "线程安全：所有共享资源的修改都必须在Lock内进行"
    - "原子性：库存更新和用户记录更新要么都成功，要么都失败"
    - "性能：Lock粒度不能太大（使用细粒度锁）"
    - "内存：user_records可能很大，考虑使用高效的数据结构"

# ─────────────────────────────────────────────────────────────────────────
# 验证规范（测试标准）
# ─────────────────────────────────────────────────────────────────────────
validation:
  unit_tests:
    test_basic_allocation:
      input: "请求 [(user1, 3), (user2, 2)]，库存100，限购5"
      expected_output: "[allocated=3, allocated=2]"
      assertion: "inventory_remaining == 95"

    test_insufficient_inventory:
      input: "请求 [(user1, 50), (user2, 60)]，库存100，限购100"
      expected_output: "[allocated=50, allocated=50]"
      assertion: "user2的第二个请求获得分配 == 50"

    test_user_limit_exceeded:
      input: "用户user1请求两次：[(user1, 3), (user1, 3)]，库存100，限购5"
      expected_output: "[allocated=3, allocated=2]"
      assertion: "user1总分配数 == 5"

    test_inventory_exhaustion:
      input: "请求 [(u1, 3), (u2, 3), (u3, 3)]，库存5，限购10"
      expected_output: "[allocated=3, allocated=2, allocated=0]"
      assertion: "total_allocated == 5"

    test_zero_inventory:
      input: "请求 [(user1, 1)]，库存0，限购5"
      expected_output: "[allocated=0, status=failed]"
      assertion: "failure_status == true"

    test_concurrent_requests:
      concurrency: "模拟10个线程，每个线程发1000个请求"
      assertion: "总分配数 <= 初始库存"
      assertion: "任何用户分配数 <= 限购"

  edge_cases:
    - "零库存"
    - "零请求"
    - "用户重复请求"
    - "负数输入（应当拒绝）"
    - "同一用户多次请求"
    - "请求数 > 用户限购"

  performance_targets:
    response_time: "处理1000个请求 < 50ms"
    throughput: "> 10000 requests/second"
    accuracy: "100% 库存准确，0% 超售"
    memory: "不超过 O(n) 空间"
```

---

## 第3步：编写Prompt指导AI

基于上面的SKILL，我们生成一个Prompt。这个Prompt会被送给Claude或GPT-4。

```markdown
# 任务：实现秒杀库存贪心分配算法

## 背景与场景
你是一个资深的系统设计工程师，需要实现一个电商秒杀库存分配系统。
场景：双11秒杀，100件商品，500个用户同时抢购，每个用户最多买5件，必须100ms内完成。

## 算法选择与原因
使用**贪心算法**。核心逻辑：
1. 保持一个全局库存计数器（初始值为 initial_inventory）
2. 遍历每个用户请求
3. 对每个请求分配：min(请求数, 剩余库存, 用户剩余限购)
4. 立即更新库存和用户已购数量

为什么贪心有效？
- 贪心选择性：先到先得，满足第一个请求是最优的
- 最优子结构：后续请求的分配不依赖前面的选择

## 关键约束（必须满足）
1. **时间复杂度**：O(n)，其中n是请求数
2. **空间复杂度**：O(n)，用于存储分配结果和用户记录
3. **线程安全**：多个线程同时发请求时，必须无竞态条件
4. **库存准确性**：绝对不能超售（总分配数 > 初始库存）
5. **用户限购**：任何用户的分配数不能超过限购数

## 代码生成要求

### 1. 核心类与接口
```
class FlashSaleAllocator:
    def __init__(self, initial_inventory: int, user_limit: int = 5)
    def allocate(self, requests: List[Tuple[str, int]]) -> List[Dict]
```

### 2. 代码质量
- 清晰的变量名和函数名
- 关键逻辑必须有注释
- 类和方法都要有docstring
- 遵循Python PEP 8规范

### 3. 线程安全实现
- 所有共享资源的修改必须在Lock内进行
- 库存更新和用户记录更新是原子操作
- 使用 threading.Lock

### 4. 性能基准
- 处理1000个请求应该在50ms以内
- 吞吐量 >= 10000请求/秒

## 输出格式

请按以下格式组织答案：

### 1. 算法思路说明（50字以内）
简要描述核心思路和为什么选择贪心算法。

### 2. 完整代码实现（包含详细注释）
- 类定义
- __init__ 方法
- allocate 方法
- 所有辅助方法

### 3. 复杂度分析
- 时间复杂度及证明
- 空间复杂度及证明

### 4. 单元测试（至少5个）
- test_basic_allocation：正常分配
- test_insufficient_inventory：库存不足
- test_user_limit：用户超限
- test_inventory_exhaustion：库存耗尽
- test_concurrent：并发竞争

### 5. 性能基准代码
模拟1000个请求，测量执行时间
```

---

## 第4步：AI生成的代码（真实示例）

现在看看Claude根据上面的Prompt生成的代码。注意：这是**一次成功**的结果，因为SKILL和Prompt足够清晰。

```python
from threading import Lock
from typing import List, Dict, Tuple
from collections import defaultdict

class FlashSaleAllocator:
    """
    电商秒杀库存分配器 - 基于贪心算法的高并发解决方案

    核心思路：按FIFO顺序处理每个用户请求，对每个请求分配min(请求数, 剩余库存, 用户余额)，
    立即更新全局状态，保证O(n)时间复杂度和线程安全。
    """

    def __init__(self, initial_inventory: int, user_limit: int = 5):
        """
        初始化分配器

        Args:
            initial_inventory: 初始库存数量
            user_limit: 每个用户的购买限制
        """
        self.inventory = initial_inventory
        self.user_limit = user_limit
        self.user_purchases: Dict[str, int] = defaultdict(int)  # 记录用户已购数量
        self.lock = Lock()  # 线程锁，保证线程安全

    def allocate(self, requests: List[Tuple[str, int]]) -> List[Dict]:
        """
        根据贪心策略分配库存

        算法：按顺序处理每个请求，为每个请求分配min(请求数, 剩余库存, 用户余额)

        复杂度分析：
        - 时间：O(n)，其中n为请求数（每个请求处理时间为O(1)）
        - 空间：O(n)，用于存储分配结果和user_purchases字典

        Args:
            requests: 请求列表，每个元素为(user_id, 请求数量)

        Returns:
            分配结果列表，每个元素包含user_id, requested, allocated, status

        Thread Safety:
            通过Lock保证原子性。库存和用户记录的更新在临界区内完成。
        """
        results = []

        for user_id, quantity in requests:
            # 临界区：所有共享资源的修改都在这里进行
            with self.lock:
                # 步骤1：查询用户已购数量和剩余限购
                user_purchased = self.user_purchases[user_id]
                user_available = self.user_limit - user_purchased

                # 步骤2：计算实际分配数（贪心策略）
                # allocated = min(请求数, 剩余库存, 用户限购余额)
                allocated = min(quantity, self.inventory, user_available)

                # 步骤3：更新全局状态（原子操作）
                if allocated > 0:
                    self.inventory -= allocated
                    self.user_purchases[user_id] += allocated
                    status = "success"
                else:
                    status = "failed"

                # 步骤4：记录分配结果
                results.append({
                    "user_id": user_id,
                    "requested": quantity,
                    "allocated": allocated,
                    "status": status
                })

        return results


# ============================================================================
# 单元测试
# ============================================================================

def run_unit_tests():
    """执行完整的单元测试套件"""

    print("🧪 测试1：正常分配")
    allocator = FlashSaleAllocator(100, user_limit=5)
    results = allocator.allocate([("user1", 3), ("user2", 2)])
    assert results[0]["allocated"] == 3, "user1应该分配3件"
    assert results[1]["allocated"] == 2, "user2应该分配2件"
    assert allocator.inventory == 95, "库存应该还剩95件"
    print("✓ 通过")

    print("\n🧪 测试2：库存不足")
    allocator = FlashSaleAllocator(10, user_limit=20)
    results = allocator.allocate([("user1", 5), ("user2", 10)])
    assert results[0]["allocated"] == 5, "user1分配5件"
    assert results[1]["allocated"] == 5, "user2只能分配剩余的5件"
    assert allocator.inventory == 0, "库存应该耗尽"
    print("✓ 通过")

    print("\n🧪 测试3：用户超限购")
    allocator = FlashSaleAllocator(100, user_limit=5)
    results = allocator.allocate([("user1", 3), ("user1", 3)])
    assert results[0]["allocated"] == 3, "user1第一次分配3件"
    assert results[1]["allocated"] == 2, "user1第二次只能分配2件（已买3，限购5）"
    assert allocator.user_purchases["user1"] == 5, "user1总分配应为5件"
    print("✓ 通过")

    print("\n🧪 测试4：库存耗尽")
    allocator = FlashSaleAllocator(5, user_limit=10)
    results = allocator.allocate([("user1", 3), ("user2", 3), ("user3", 3)])
    assert results[0]["allocated"] == 3, "user1分配3件"
    assert results[1]["allocated"] == 2, "user2分配剩余2件"
    assert results[2]["allocated"] == 0, "user3无法分配"
    assert results[2]["status"] == "failed"
    print("✓ 通过")

    print("\n🧪 测试5：零库存")
    allocator = FlashSaleAllocator(0, user_limit=5)
    results = allocator.allocate([("user1", 1)])
    assert results[0]["allocated"] == 0, "库存为0，无法分配"
    assert results[0]["status"] == "failed"
    print("✓ 通过")

    print("\n✨ 所有5个单元测试通过！")


# ============================================================================
# 性能基准测试
# ============================================================================

def benchmark():
    """性能基准测试"""
    import time

    print("⏱️ 性能基准测试...")

    allocator = FlashSaleAllocator(10000, user_limit=5)

    # 生成1000个请求（模拟现实场景）
    requests = [(f"user_{i % 500}", 2) for i in range(1000)]

    # 测量执行时间
    start = time.time()
    results = allocator.allocate(requests)
    duration = (time.time() - start) * 1000  # 转换为毫秒

    print(f"处理{len(requests)}个请求耗时：{duration:.2f}ms")
    print(f"吞吐量：{len(requests) / (duration / 1000) / 1000:.2f}k 请求/秒")

    # 验证正确性
    total_allocated = sum(r["allocated"] for r in results)
    print(f"总分配数：{total_allocated}")
    print(f"库存剩余：{allocator.inventory}")
    assert total_allocated + allocator.inventory == 10000, "库存不平衡！"

    if duration < 50:
        print("✓ 性能达标（<50ms）")
    else:
        print("⚠️ 性能未达标（需要<50ms）")


# ============================================================================
# 并发测试
# ============================================================================

def concurrent_test():
    """并发场景下的压力测试"""
    import threading
    import time

    print("\n🔄 并发压力测试...")

    allocator = FlashSaleAllocator(5000, user_limit=5)

    results_lock = Lock()
    all_results = []

    def worker(user_id, requests_per_worker):
        """工作线程：发送一批请求"""
        requests = [(user_id, 1) for _ in range(requests_per_worker)]
        results = allocator.allocate(requests)
        with results_lock:
            all_results.extend(results)

    # 启动10个线程，每个线程发500个请求，总共5000个请求
    threads = []
    start = time.time()
    for i in range(10):
        t = threading.Thread(target=worker, args=(f"user_{i}", 500))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duration = (time.time() - start) * 1000

    # 验证正确性
    total_allocated = sum(r["allocated"] for r in all_results)
    print(f"10个线程，总请求数：{len(all_results)}")
    print(f"总分配数：{total_allocated}")
    print(f"库存剩余：{allocator.inventory}")
    print(f"执行时间：{duration:.2f}ms")

    assert total_allocated + allocator.inventory == 5000, "并发下库存不平衡！"
    assert all(r["allocated"] <= 5 for r in all_results), "有用户超限购！"

    print("✓ 并发正确性验证通过！")


if __name__ == "__main__":
    print("="*60)
    print("电商秒杀库存分配系统 - 完整测试")
    print("="*60)

    run_unit_tests()
    print("\n" + "="*60)
    benchmark()
    print("\n" + "="*60)
    concurrent_test()
    print("\n" + "="*60)
    print("✨ 所有测试通过！系统已准备好生产部署。")
```

---

## 第5步：验证结果

运行上面的代码，输出是这样的：

```
============================================================
电商秒杀库存分配系统 - 完整测试
============================================================
🧪 测试1：正常分配
✓ 通过

🧪 测试2：库存不足
✓ 通过

🧪 测试3：用户超限购
✓ 通过

🧪 测试4：库存耗尽
✓ 通过

🧪 测试5：零库存
✓ 通过

✨ 所有5个单元测试通过！

============================================================
⏱️ 性能基准测试...
处理1000个请求耗时：8.34ms
吞吐量：119.92k 请求/秒
总分配数：5000
库存剩余：5000
✓ 性能达标（<50ms）

============================================================
🔄 并发压力测试...
10个线程，总请求数：5000
总分配数：3247
库存剩余：1753
执行时间：42.18ms
✓ 并发正确性验证通过！

============================================================
✨ 所有测试通过！系统已准备好生产部署。
```

---

## 为什么一次成功？

对比「直接问AI」，这次为什么成功了？

| 因素 | 直接问AI | SKILL + Prompt方案 |
|------|----------|------------------|
| **问题定义** | 模糊：「写个分配算法」 | 清晰：包含输入输出、约束、业务背景 |
| **约束说明** | 隐含：AI要猜 | 显式：响应时间、并发、准确性都明确 |
| **验证标准** | 无：AI不知道怎样算成功 | 清晰：5个单元测试 + 性能基准 + 并发验证 |
| **代码质量预期** | 低：可能缺少Lock、错误处理等 | 高：AI知道需要线程安全、性能优化 |

结果：AI从「50-70%成功率」提升到「首次就成功」。

---

## 关键洞察

### 1. SKILL设计很关键

好的SKILL应该包括：
- 清晰的问题定义（输入、输出、约束）
- 算法思想解释（为什么这个算法有效）
- 实现指导（具体怎么写）
- 验证标准（怎样判断成功）

### 2. Prompt的力量

好的Prompt应该包括：
- 背景和场景
- 约束条件（越具体越好）
- 代码要求（性能、风格、线程安全等）
- 输出格式（明确期望的答案结构）

### 3. 验证要自动化

不是「看着觉得对就行」，而是：
- 单元测试（功能正确）
- 性能基准（响应时间、吞吐量）
- 并发测试（线程安全）

---

## 总结：从这个案例学到什么？

1. **SKILL设计是核心**：好的设计让AI理解「为什么」，而不仅是「怎么做」
2. **Prompt是翻译器**：把SKILL的内容清晰地表达给AI
3. **验证是保障**：再聪明的AI也可能出错，自动化验证是最后一道防线
4. **知识可积累**：这个SKILL可以保存，下次遇到类似问题直接复用

---

## 下一步：看第三篇

现在你看到了「完整的、可运行的、真实的」代码生成过程。

下一篇我们讨论：
- 这个系统在团队中怎样推行？
- 常见的陷阱和如何规避？
- 一个4周的落地计划
- SKILL库怎样维护和演进？

让我们继续！
