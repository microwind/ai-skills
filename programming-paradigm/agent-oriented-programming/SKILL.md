---
name: 面向代理编程
description: "以自主代理为基本单元的编程范式，代理具有感知、决策和行动能力，通过消息通信协作。"
license: MIT
---

# 面向代理编程 (Agent-Oriented Programming)

## 概述

面向代理编程以**自主代理（Agent）**为核心：每个代理有自己的目标、信念和行为，通过感知环境和相互通信来协作完成任务。

**代理特征**：
- **自主性** — 独立决策，不需外部控制
- **反应性** — 感知环境并做出响应
- **主动性** — 有目标驱动的行为
- **社交性** — 与其他代理通信协作

## 代码示例

```python
from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.beliefs = {}      # 信念：对世界的认知
        self.goals = []        # 目标：要达成的状态
        self.inbox = []        # 消息队列

    def perceive(self, environment: dict):
        """感知环境"""
        self.beliefs.update(environment)

    @abstractmethod
    def decide(self) -> str:
        """决策：选择下一步行动"""
        pass

    @abstractmethod
    def act(self, action: str):
        """执行行动"""
        pass

    def send_message(self, to: 'Agent', message: dict):
        to.inbox.append({"from": self.name, **message})

    def process_messages(self):
        while self.inbox:
            msg = self.inbox.pop(0)
            self.handle_message(msg)

    def handle_message(self, message: dict):
        pass

# 具体代理：购买代理
class BuyerAgent(Agent):
    def __init__(self, name, budget):
        super().__init__(name)
        self.budget = budget
        self.goals = ["find_best_deal"]

    def decide(self) -> str:
        if "best_price" in self.beliefs and self.beliefs["best_price"] <= self.budget:
            return "buy"
        return "negotiate"

    def act(self, action: str):
        if action == "buy":
            print(f"{self.name}: 以 {self.beliefs['best_price']} 购买")
        elif action == "negotiate":
            print(f"{self.name}: 请求更低价格")

# 多代理系统
class MultiAgentSystem:
    def __init__(self):
        self.agents: list[Agent] = []

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    def run(self, environment: dict, steps: int = 10):
        for step in range(steps):
            for agent in self.agents:
                agent.perceive(environment)
                agent.process_messages()
                action = agent.decide()
                agent.act(action)
```

## AI Agent（LLM 时代）

```python
# 现代 AI Agent：LLM + 工具 + 记忆
class AIAgent:
    def __init__(self, llm, tools, memory):
        self.llm = llm           # 大语言模型
        self.tools = tools       # 可用工具
        self.memory = memory     # 长期记忆

    async def run(self, task: str) -> str:
        context = self.memory.recall(task)
        plan = await self.llm.plan(task, context, self.tools)

        results = []
        for step in plan:
            if step.requires_tool:
                result = await self.tools[step.tool_name].execute(step.params)
                results.append(result)
            else:
                result = await self.llm.reason(step.prompt, results)
                results.append(result)

        answer = await self.llm.synthesize(task, results)
        self.memory.store(task, answer)
        return answer
```

## 应用场景

| 场景 | 说明 |
|------|------|
| AI Agent | LLM 驱动的自主代理 |
| 多代理模拟 | 交通、经济、社会模拟 |
| 机器人控制 | 自主导航、协作搬运 |
| 分布式系统 | Actor 模型（Akka） |
| 游戏 AI | NPC 行为决策 |
| 自动化交易 | 交易策略代理 |

## Agent vs Object

| 维度 | Object | Agent |
|------|--------|-------|
| 控制 | 被动调用 | 自主决策 |
| 通信 | 方法调用 | 异步消息 |
| 状态 | 对象属性 | 信念 + 目标 |
| 行为 | 固定方法 | 适应性策略 |

## 与其他范式的关系

| 范式 | 关系 |
|------|------|
| [OOP](../object-oriented-programming/) | Agent 是具有自主性的 Object |
| [并发编程](../concurrent-programming/) | Agent 天然是并发实体 |
| [响应式](../reactive-programming/) | Agent 感知环境类似响应式 |

## 总结

**核心**：自主代理通过感知-决策-行动循环完成任务，通过消息协作。

**趋势**：随着 LLM 的发展，AI Agent 正成为软件开发的新范式。
