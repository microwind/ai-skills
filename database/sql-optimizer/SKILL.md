---
name: SQL优化器
description: "当优化SQL查询时，分析执行计划，检查索引使用，优化查询性能。验证SQL语法，分析查询复杂度，和最佳实践。"
license: MIT
---

# SQL优化器技能

## 概述
慢SQL查询会复合影响。一个慢查询会影响100个事务。在扩展之前先优化。需要建立完善的SQL查询分析和优化机制。

**核心原则**: 慢SQL查询会复合影响。一个慢查询会影响100个事务。在扩展之前先优化。

## 何时使用

**始终:**
- 优化慢查询
- 数据库性能问题
- 扩展数据库之前
- 性能分析后的查询调优
- 索引设计优化
- 查询性能监控

**触发短语:**
- "优化这个SQL查询"
- "查询太慢了"
- "如何优化数据库性能？"
- "检查SQL执行计划"
- "索引怎么设计？"
- "SQL性能分析"

## SQL优化功能

### 查询分析
- 执行计划分析
- 查询复杂度评估
- 索引使用检查
- 统计信息分析
- 性能瓶颈识别

### 索引优化
- 索引设计建议
- 索引使用效率分析
- 冗余索引检测
- 索引优化方案
- 覆盖索引设计

### 性能调优
- 查询重写建议
- 表结构优化
- 分区策略分析
- 缓存优化建议
- 参数调优

## 常见SQL性能问题

### 缺少索引
```
问题:
查询条件没有合适的索引支持

后果:
- 全表扫描
- 查询速度慢
- CPU占用高
- 锁竞争严重

解决方案:
- 创建合适的索引
- 复合索引优化
- 覆盖索引设计
- 索引选择性分析
```

### 查询设计不当
```
问题:
SQL查询语句设计不合理

后果:
- 执行计划不优
- 资源浪费
- 性能下降
- 扩展性差

解决方案:
- 重写查询语句
- 避免子查询
- 优化JOIN操作
- 减少数据传输
```

### 统计信息过时
```
问题:
数据库统计信息不准确

后果:
- 执行计划错误
- 索引选择不当
- 查询性能下降
- 资源分配不合理

解决方案:
- 更新统计信息
- 定期维护
- 自动统计收集
- 手动统计更新
```

## SQL优化策略

### 查询重写技巧
```
避免子查询:
- 使用JOIN替代子查询
- 使用EXISTS替代IN
- 优化相关子查询
- 减少嵌套层次

优化JOIN:
- 选择合适的JOIN类型
- 确保连接字段有索引
- 减少JOIN的数据量
- 优化JOIN顺序
```

### 索引设计原则
```
单列索引:
- 高选择性字段
- 频繁查询条件
- 排序字段
- 外键字段

复合索引:
- 多条件查询
- 字段顺序重要
- 覆盖查询需求
- 减少回表查询
```

## 代码实现示例

### SQL查询优化器
```python
import re
import sqlparse
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class QueryType(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"

@dataclass
class QueryAnalysis:
    """查询分析结果"""
    query_type: QueryType
    complexity_score: int
    tables: List[str]
    columns: List[str]
    joins: List[Dict[str, str]]
    where_conditions: List[str]
    group_by: List[str]
    order_by: List[str]
    issues: List[str]
    recommendations: List[str]
    execution_plan: Optional[Dict[str, Any]] = None

class SQLOptimizer:
    """SQL查询优化器"""
    
    def __init__(self):
        self.optimization_rules = self._setup_optimization_rules()
        self.index_suggestions = []
        self.performance_metrics = {}
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """分析SQL查询"""
        # 格式化SQL
        formatted_query = sqlparse.format(query, reindent=True, keyword_case='upper')
        
        # 解析查询类型
        query_type = self._detect_query_type(formatted_query)
        
        # 提取查询组件
        tables = self._extract_tables(formatted_query)
        columns = self._extract_columns(formatted_query)
        joins = self._extract_joins(formatted_query)
        where_conditions = self._extract_where_conditions(formatted_query)
        group_by = self._extract_group_by(formatted_query)
        order_by = self._extract_order_by(formatted_query)
        
        # 计算复杂度
        complexity_score = self._calculate_complexity(
            tables, columns, joins, where_conditions, group_by, order_by
        )
        
        # 分析问题和建议
        issues = []
        recommendations = []
        
        self._analyze_performance_issues(
            query_type, tables, columns, joins, where_conditions, 
            group_by, order_by, issues, recommendations
        )
        
        return QueryAnalysis(
            query_type=query_type,
            complexity_score=complexity_score,
            tables=tables,
            columns=columns,
            joins=joins,
            where_conditions=where_conditions,
            group_by=group_by,
            order_by=order_by,
            issues=issues,
            recommendations=recommendations
        )
    
    def optimize_query(self, query: str) -> Dict[str, Any]:
        """优化SQL查询"""
        analysis = self.analyze_query(query)
        
        optimized_query = query
        optimizations_applied = []
        
        # 应用优化规则
        for rule in self.optimization_rules:
            result = rule.apply(optimized_query, analysis)
            if result.modified:
                optimized_query = result.query
                optimizations_applied.append(rule.name)
        
        # 生成索引建议
        index_suggestions = self._generate_index_suggestions(analysis)
        
        # 生成执行计划建议
        execution_plan_hints = self._generate_execution_plan_hints(analysis)
        
        return {
            'original_query': query,
            'optimized_query': optimized_query,
            'analysis': analysis,
            'optimizations_applied': optimizations_applied,
            'index_suggestions': index_suggestions,
            'execution_plan_hints': execution_plan_hints,
            'performance_improvement_estimate': self._estimate_improvement(analysis)
        }
    
    def _detect_query_type(self, query: str) -> QueryType:
        """检测查询类型"""
        query_upper = query.strip().upper()
        
        if query_upper.startswith('SELECT'):
            return QueryType.SELECT
        elif query_upper.startswith('INSERT'):
            return QueryType.INSERT
        elif query_upper.startswith('UPDATE'):
            return QueryType.UPDATE
        elif query_upper.startswith('DELETE'):
            return QueryType.DELETE
        elif query_upper.startswith('CREATE'):
            return QueryType.CREATE
        elif query_upper.startswith('DROP'):
            return QueryType.DROP
        elif query_upper.startswith('ALTER'):
            return QueryType.ALTER
        else:
            return QueryType.SELECT  # 默认
    
    def _extract_tables(self, query: str) -> List[str]:
        """提取表名"""
        tables = []
        
        # 使用正则表达式提取表名
        # FROM子句
        from_pattern = r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        from_matches = re.findall(from_pattern, query, re.IGNORECASE)
        tables.extend(from_matches)
        
        # JOIN子句
        join_pattern = r'JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        join_matches = re.findall(join_pattern, query, re.IGNORECASE)
        tables.extend(join_matches)
        
        # INSERT INTO子句
        insert_pattern = r'INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        insert_matches = re.findall(insert_pattern, query, re.IGNORECASE)
        tables.extend(insert_matches)
        
        # UPDATE子句
        update_pattern = r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        update_matches = re.findall(update_pattern, query, re.IGNORECASE)
        tables.extend(update_matches)
        
        return list(set(tables))  # 去重
    
    def _extract_columns(self, query: str) -> List[str]:
        """提取列名"""
        columns = []
        
        # SELECT子句中的列
        select_pattern = r'SELECT\s+(.*?)\s+FROM'
        select_match = re.search(select_pattern, query, re.IGNORECASE | re.DOTALL)
        if select_match:
            select_clause = select_match.group(1)
            
            # 排除函数和聚合
            if select_clause != '*':
                # 简单的列名提取
                column_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:,|$|\s+FROM)'
                column_matches = re.findall(column_pattern, select_clause)
                columns.extend(column_matches)
        
        return list(set(columns))
    
    def _extract_joins(self, query: str) -> List[Dict[str, str]]:
        """提取JOIN信息"""
        joins = []
        
        # JOIN模式
        join_pattern = r'(INNER|LEFT|RIGHT|FULL|CROSS)\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+ON\s+([^JOIN]+)'
        join_matches = re.findall(join_pattern, query, re.IGNORECASE)
        
        for join_type, table, condition in join_matches:
            joins.append({
                'type': join_type.upper(),
                'table': table,
                'condition': condition.strip()
            })
        
        return joins
    
    def _extract_where_conditions(self, query: str) -> List[str]:
        """提取WHERE条件"""
        conditions = []
        
        where_pattern = r'WHERE\s+(.*?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)'
        where_match = re.search(where_pattern, query, re.IGNORECASE | re.DOTALL)
        
        if where_match:
            where_clause = where_match.group(1)
            # 分割AND和OR条件
            and_conditions = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)
            for condition in and_conditions:
                or_conditions = re.split(r'\s+OR\s+', condition, flags=re.IGNORECASE)
                conditions.extend([c.strip() for c in or_conditions])
        
        return conditions
    
    def _extract_group_by(self, query: str) -> List[str]:
        """提取GROUP BY字段"""
        group_by = []
        
        group_pattern = r'GROUP\s+BY\s+(.*?)(?:\s+ORDER\s+BY|\s+LIMIT|$)'
        group_match = re.search(group_pattern, query, re.IGNORECASE)
        
        if group_match:
            group_clause = group_match.group(1)
            group_by = [col.strip() for col in group_clause.split(',')]
        
        return group_by
    
    def _extract_order_by(self, query: str) -> List[str]:
        """提取ORDER BY字段"""
        order_by = []
        
        order_pattern = r'ORDER\s+BY\s+(.*?)(?:\s+LIMIT|$)'
        order_match = re.search(order_pattern, query, re.IGNORECASE)
        
        if order_match:
            order_clause = order_match.group(1)
            order_by = [col.strip() for col in order_clause.split(',')]
        
        return order_by
    
    def _calculate_complexity(self, tables: List[str], columns: List[str], 
                            joins: List[Dict], where_conditions: List[str],
                            group_by: List[str], order_by: List[str]) -> int:
        """计算查询复杂度"""
        score = 0
        
        # 表数量影响
        score += len(tables) * 10
        
        # 列数量影响
        score += len(columns) * 2
        
        # JOIN影响
        score += len(joins) * 15
        
        # WHERE条件影响
        score += len(where_conditions) * 5
        
        # GROUP BY影响
        score += len(group_by) * 8
        
        # ORDER BY影响
        score += len(order_by) * 3
        
        # 子查询影响
        # 这里简化处理，实际应该解析嵌套层次
        
        return score
    
    def _analyze_performance_issues(self, query_type: QueryType, tables: List[str],
                                  columns: List[str], joins: List[Dict],
                                  where_conditions: List[str], group_by: List[str],
                                  order_by: List[str], issues: List[str],
                                  recommendations: List[str]):
        """分析性能问题"""
        
        # 检查SELECT *
        if query_type == QueryType.SELECT and '*' in columns:
            issues.append("查询使用了SELECT *，可能返回不必要的数据")
            recommendations.append("只查询需要的列，避免使用SELECT *")
        
        # 检查JOIN数量
        if len(joins) > 5:
            issues.append(f"查询包含过多JOIN操作({len(joins)}个)")
            recommendations.append("考虑分解复杂查询或优化表结构")
        
        # 检查WHERE条件
        if not where_conditions and query_type == QueryType.SELECT:
            issues.append("查询缺少WHERE条件，可能扫描全表")
            recommendations.append("添加适当的WHERE条件限制数据范围")
        
        # 检查GROUP BY和ORDER BY
        if group_by and order_by:
            if set(group_by) & set(order_by):
                recommendations.append("GROUP BY和ORDER BY使用相同字段，可以利用索引")
        
        # 检查表数量
        if len(tables) > 10:
            issues.append(f"查询涉及过多表({len(tables)}个)")
            recommendations.append("考虑使用视图或分解查询")
    
    def _generate_index_suggestions(self, analysis: QueryAnalysis) -> List[Dict[str, Any]]:
        """生成索引建议"""
        suggestions = []
        
        # 基于WHERE条件建议索引
        for condition in analysis.where_conditions:
            # 简单的字段提取
            field_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*[=<>!]'
            field_matches = re.findall(field_pattern, condition)
            
            for field in field_matches:
                suggestions.append({
                    'type': 'single_column',
                    'table': analysis.tables[0] if analysis.tables else 'unknown',
                    'column': field,
                    'reason': f'WHERE条件中使用: {condition}',
                    'priority': 'high'
                })
        
        # 基于JOIN条件建议索引
        for join in analysis.joins:
            # 提取JOIN字段
            condition = join['condition']
            field_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)'
            field_matches = re.findall(field_pattern, condition)
            
            for table1, table2, field in field_matches:
                suggestions.append({
                    'type': 'foreign_key',
                    'table': table1,
                    'column': field,
                    'reason': f'JOIN条件: {condition}',
                    'priority': 'high'
                })
        
        # 基于ORDER BY建议索引
        if analysis.order_by:
            for field in analysis.order_by:
                clean_field = field.split()[0]  # 移除ASC/DESC
                suggestions.append({
                    'type': 'order_by',
                    'table': analysis.tables[0] if analysis.tables else 'unknown',
                    'column': clean_field,
                    'reason': f'ORDER BY使用: {field}',
                    'priority': 'medium'
                })
        
        return suggestions
    
    def _generate_execution_plan_hints(self, analysis: QueryAnalysis) -> List[str]:
        """生成执行计划提示"""
        hints = []
        
        if analysis.complexity_score > 100:
            hints.append("查询复杂度较高，建议分解为多个简单查询")
        
        if len(analysis.joins) > 3:
            hints.append("考虑使用EXISTS替代部分JOIN操作")
        
        if analysis.group_by and len(analysis.group_by) > 3:
            hints.append("GROUP BY字段较多，考虑使用覆盖索引")
        
        return hints
    
    def _estimate_improvement(self, analysis: QueryAnalysis) -> Dict[str, float]:
        """估算性能提升"""
        improvement = {
            'query_speed': 0.0,
            'resource_usage': 0.0,
            'scalability': 0.0
        }
        
        # 基于问题数量估算
        issue_count = len(analysis.issues)
        if issue_count > 0:
            improvement['query_speed'] = min(0.8, issue_count * 0.15)
            improvement['resource_usage'] = min(0.6, issue_count * 0.12)
            improvement['scalability'] = min(0.4, issue_count * 0.08)
        
        return improvement
    
    def _setup_optimization_rules(self) -> List['OptimizationRule']:
        """设置优化规则"""
        return [
            SelectStarOptimization(),
            SubqueryOptimization(),
            JoinOptimization(),
            WhereOptimization(),
            IndexHintOptimization()
        ]

class OptimizationRule:
    """优化规则基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    def apply(self, query: str, analysis: QueryAnalysis) -> 'OptimizationResult':
        """应用优化规则"""
        raise NotImplementedError

@dataclass
class OptimizationResult:
    """优化结果"""
    query: str
    modified: bool
    reason: str

class SelectStarOptimization(OptimizationRule):
    """SELECT *优化"""
    
    def __init__(self):
        super().__init__("SELECT *优化")
    
    def apply(self, query: str, analysis: QueryAnalysis) -> OptimizationResult:
        if '*' in analysis.columns:
            # 这里应该根据实际表结构替换*
            # 简化处理，提示用户手动优化
            return OptimizationResult(
                query=query,
                modified=False,
                reason="需要手动指定具体列名替代SELECT *"
            )
        
        return OptimizationResult(query=query, modified=False, reason="无需优化")

class SubqueryOptimization(OptimizationRule):
    """子查询优化"""
    
    def __init__(self):
        super().__init__("子查询优化")
    
    def apply(self, query: str, analysis: QueryAnalysis) -> OptimizationResult:
        # 检查是否可以转换为JOIN
        # 简化处理
        optimized_query = query
        
        # 检查IN子查询
        in_pattern = r'IN\s*\(\s*SELECT\s+.*?\)'
        if re.search(in_pattern, optimized_query, re.IGNORECASE | re.DOTALL):
            # 可以建议使用EXISTS或JOIN替代
            return OptimizationResult(
                query=optimized_query,
                modified=False,
                reason="建议使用EXISTS或JOIN替代IN子查询"
            )
        
        return OptimizationResult(query=optimized_query, modified=False, reason="无需优化")

class JoinOptimization(OptimizationRule):
    """JOIN优化"""
    
    def __init__(self):
        super().__init__("JOIN优化")
    
    def apply(self, query: str, analysis: QueryAnalysis) -> OptimizationResult:
        optimized_query = query
        
        # 检查JOIN顺序
        if len(analysis.joins) > 2:
            return OptimizationResult(
                query=optimized_query,
                modified=False,
                reason="建议优化JOIN顺序，小表在前"
            )
        
        return OptimizationResult(query=optimized_query, modified=False, reason="无需优化")

class WhereOptimization(OptimizationRule):
    """WHERE条件优化"""
    
    def __init__(self):
        super().__init__("WHERE条件优化")
    
    def apply(self, query: str, analysis: QueryAnalysis) -> OptimizationResult:
        optimized_query = query
        
        # 检查函数使用
        for condition in analysis.where_conditions:
            if re.search(r'[A-Z_]+\(', condition, re.IGNORECASE):
                return OptimizationResult(
                    query=optimized_query,
                    modified=False,
                    reason="WHERE条件中使用了函数，可能影响索引使用"
                )
        
        return OptimizationResult(query=optimized_query, modified=False, reason="无需优化")

class IndexHintOptimization(OptimizationRule):
    """索引提示优化"""
    
    def __init__(self):
        super().__init__("索引提示优化")
    
    def apply(self, query: str, analysis: QueryAnalysis) -> OptimizationResult:
        # 可以添加索引提示
        # 简化处理
        return OptimizationResult(
            query=query,
            modified=False,
            reason="可以考虑添加索引提示"
        )

# 使用示例
def main():
    optimizer = SQLOptimizer()
    
    # 示例查询
    sample_queries = [
        """
        SELECT u.name, o.order_date, p.product_name
        FROM users u
        INNER JOIN orders o ON u.id = o.user_id
        INNER JOIN order_items oi ON o.id = oi.order_id
        INNER JOIN products p ON oi.product_id = p.id
        WHERE u.status = 'active' AND o.order_date > '2023-01-01'
        ORDER BY o.order_date DESC
        """,
        
        """
        SELECT * FROM products WHERE price > 100
        """,
        
        """
        SELECT COUNT(*) FROM orders WHERE user_id IN (SELECT id FROM users WHERE status = 'active')
        """
    ]
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n=== 查询 {i} ===")
        print(f"原始查询: {query.strip()}")
        
        # 分析查询
        analysis = optimizer.analyze_query(query)
        print(f"查询类型: {analysis.query_type.value}")
        print(f"复杂度分数: {analysis.complexity_score}")
        print(f"涉及表: {analysis.tables}")
        print(f"涉及列: {analysis.columns}")
        
        if analysis.issues:
            print("发现的问题:")
            for issue in analysis.issues:
                print(f"  - {issue}")
        
        if analysis.recommendations:
            print("优化建议:")
            for rec in analysis.recommendations:
                print(f"  - {rec}")
        
        # 优化查询
        optimization = optimizer.optimize_query(query)
        print(f"优化后查询: {optimization['optimized_query'].strip()}")
        
        if optimization['index_suggestions']:
            print("索引建议:")
            for suggestion in optimization['index_suggestions']:
                print(f"  - {suggestion['table']}.{suggestion['column']} ({suggestion['type']}) - {suggestion['reason']}")
        
        improvement = optimization['performance_improvement_estimate']
        print(f"预计性能提升: 查询速度{improvement['query_speed']:.1%}, 资源使用{improvement['resource_usage']:.1%}")

if __name__ == "__main__":
    main()
```

### 数据库性能监控
```python
import time
import psycopg2
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

@dataclass
class PerformanceMetrics:
    """性能指标"""
    query_time: float
    rows_examined: int
    rows_returned: int
    index_usage: Dict[str, int]
    buffer_usage: Dict[str, int]
    cpu_usage: float
    memory_usage: float

class DatabasePerformanceMonitor:
    """数据库性能监控"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.metrics_history = []
        self.slow_queries = []
    
    def monitor_query_performance(self, query: str, params: tuple = None) -> PerformanceMetrics:
        """监控查询性能"""
        start_time = time.time()
        
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                # 执行EXPLAIN ANALYZE
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                cursor.execute(explain_query, params)
                explain_result = cursor.fetchone()[0]
                
                # 执行实际查询
                cursor.execute(query, params)
                rows = cursor.fetchall()
        
        end_time = time.time()
        
        # 解析执行计划
        plan = explain_result[0]
        
        metrics = PerformanceMetrics(
            query_time=end_time - start_time,
            rows_examined=plan.get('Actual Rows', 0),
            rows_returned=len(rows),
            index_usage=self._extract_index_usage(plan),
            buffer_usage=self._extract_buffer_usage(plan),
            cpu_usage=self._get_cpu_usage(),
            memory_usage=self._get_memory_usage()
        )
        
        self.metrics_history.append(metrics)
        
        # 检查是否为慢查询
        if metrics.query_time > 1.0:  # 超过1秒
            self.slow_queries.append({
                'query': query,
                'params': params,
                'metrics': metrics,
                'timestamp': datetime.now()
            })
        
        return metrics
    
    def _extract_index_usage(self, plan: Dict[str, Any]) -> Dict[str, int]:
        """提取索引使用情况"""
        index_usage = {}
        
        def traverse_plan(node):
            if 'Node Type' in node:
                node_type = node['Node Type']
                
                if 'Index Name' in node:
                    index_name = node['Index Name']
                    index_usage[index_name] = index_usage.get(index_name, 0) + 1
                
                if 'Plans' in node:
                    for sub_plan in node['Plans']:
                        traverse_plan(sub_plan)
        
        traverse_plan(plan)
        return index_usage
    
    def _extract_buffer_usage(self, plan: Dict[str, Any]) -> Dict[str, int]:
        """提取缓冲区使用情况"""
        buffers = plan.get('Buffers', {})
        
        return {
            'shared_hit': buffers.get('shared hit', 0),
            'shared_read': buffers.get('shared read', 0),
            'shared_dirtied': buffers.get('shared dirtied', 0),
            'shared_written': buffers.get('shared written', 0),
            'local_hit': buffers.get('local hit', 0),
            'local_read': buffers.get('local read', 0),
            'local_dirtied': buffers.get('local dirtied', 0),
            'local_written': buffers.get('local written', 0),
            'temp_read': buffers.get('temp read', 0),
            'temp_written': buffers.get('temp written', 0)
        }
    
    def _get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        import psutil
        return psutil.cpu_percent()
    
    def _get_memory_usage(self) -> float:
        """获取内存使用率"""
        import psutil
        return psutil.virtual_memory().percent
    
    def analyze_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """分析性能趋势"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.now() - timedelta(hours=hours) <= datetime.now()
        ]
        
        if not recent_metrics:
            return {'message': '没有足够的数据进行分析'}
        
        query_times = [m.query_time for m in recent_metrics]
        cpu_usage = [m.cpu_usage for m in recent_metrics]
        memory_usage = [m.memory_usage for m in recent_metrics]
        
        analysis = {
            'period_hours': hours,
            'total_queries': len(recent_metrics),
            'avg_query_time': statistics.mean(query_times),
            'max_query_time': max(query_times),
            'min_query_time': min(query_times),
            'avg_cpu_usage': statistics.mean(cpu_usage),
            'avg_memory_usage': statistics.mean(memory_usage),
            'slow_query_count': len([m for m in recent_metrics if m.query_time > 1.0]),
            'trend': self._calculate_trend(query_times)
        }
        
        return analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return 'insufficient_data'
        
        # 简单的线性趋势计算
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        # 计算斜率
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.01:
            return 'increasing'
        elif slope < -0.01:
            return 'decreasing'
        else:
            return 'stable'
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """生成优化报告"""
        if not self.metrics_history:
            return {'message': '没有性能数据'}
        
        # 分析慢查询
        slow_query_analysis = self._analyze_slow_queries()
        
        # 分析索引使用
        index_analysis = self._analyze_index_usage()
        
        # 分析缓冲区使用
        buffer_analysis = self._analyze_buffer_usage()
        
        # 生成建议
        recommendations = self._generate_recommendations(
            slow_query_analysis, index_analysis, buffer_analysis
        )
        
        return {
            'summary': {
                'total_queries': len(self.metrics_history),
                'slow_queries': len(self.slow_queries),
                'avg_query_time': statistics.mean([m.query_time for m in self.metrics_history])
            },
            'slow_queries': slow_query_analysis,
            'index_usage': index_analysis,
            'buffer_usage': buffer_analysis,
            'recommendations': recommendations
        }
    
    def _analyze_slow_queries(self) -> Dict[str, Any]:
        """分析慢查询"""
        if not self.slow_queries:
            return {'message': '没有慢查询'}
        
        slow_times = [sq['metrics'].query_time for sq in self.slow_queries]
        
        return {
            'count': len(self.slow_queries),
            'avg_time': statistics.mean(slow_times),
            'max_time': max(slow_times),
            'min_time': min(slow_times),
            'queries': [
                {
                    'query': sq['query'][:100] + '...',
                    'time': sq['metrics'].query_time,
                    'rows_examined': sq['metrics'].rows_examined,
                    'timestamp': sq['timestamp'].isoformat()
                }
                for sq in self.slow_queries[-5:]  # 最近5个慢查询
            ]
        }
    
    def _analyze_index_usage(self) -> Dict[str, Any]:
        """分析索引使用"""
        all_index_usage = {}
        
        for metrics in self.metrics_history:
            for index, count in metrics.index_usage.items():
                all_index_usage[index] = all_index_usage.get(index, 0) + count
        
        # 排序
        sorted_indexes = sorted(all_index_usage.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_index_usage': sum(all_index_usage.values()),
            'unique_indexes': len(all_index_usage),
            'top_indexes': sorted_indexes[:10],
            'unused_indexes': []  # 需要与数据库中的索引列表比较
        }
    
    def _analyze_buffer_usage(self) -> Dict[str, Any]:
        """分析缓冲区使用"""
        total_shared_hit = sum(m.buffer_usage.get('shared_hit', 0) for m in self.metrics_history)
        total_shared_read = sum(m.buffer_usage.get('shared_read', 0) for m in self.metrics_history)
        
        hit_ratio = total_shared_hit / (total_shared_hit + total_shared_read) if (total_shared_hit + total_shared_read) > 0 else 0
        
        return {
            'shared_buffer_hit_ratio': hit_ratio,
            'total_shared_hit': total_shared_hit,
            'total_shared_read': total_shared_read,
            'cache_efficiency': 'good' if hit_ratio > 0.95 else 'poor'
        }
    
    def _generate_recommendations(self, slow_query_analysis: Dict, 
                                index_analysis: Dict, buffer_analysis: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 慢查询建议
        if slow_query_analysis.get('count', 0) > 0:
            recommendations.append(
                f"发现{slow_query_analysis['count']}个慢查询，平均执行时间{slow_query_analysis['avg_time']:.3f}秒"
            )
            recommendations.append("建议分析慢查询的执行计划并优化索引")
        
        # 缓冲区建议
        hit_ratio = buffer_analysis.get('shared_buffer_hit_ratio', 0)
        if hit_ratio < 0.95:
            recommendations.append(
                f"共享缓冲区命中率{hit_ratio:.1%}较低，建议增加shared_buffers配置"
            )
        
        # 索引建议
        if index_analysis.get('unique_indexes', 0) > 20:
            recommendations.append("索引数量较多，建议清理未使用的索引")
        
        return recommendations

# 使用示例
def main():
    monitor = DatabasePerformanceMonitor("postgresql://user:password@localhost/dbname")
    
    # 监控一些查询
    queries = [
        "SELECT * FROM users WHERE status = 'active'",
        "SELECT COUNT(*) FROM orders WHERE created_at > '2023-01-01'",
        "SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.name"
    ]
    
    for query in queries:
        print(f"执行查询: {query}")
        metrics = monitor.monitor_query_performance(query)
        print(f"执行时间: {metrics.query_time:.3f}秒")
        print(f"检查行数: {metrics.rows_examined}")
        print(f"返回行数: {metrics.rows_returned}")
        print()
    
    # 生成报告
    report = monitor.generate_optimization_report()
    print("=== 性能优化报告 ===")
    print(f"总查询数: {report['summary']['total_queries']}")
    print(f"慢查询数: {report['summary']['slow_queries']}")
    print(f"平均执行时间: {report['summary']['avg_query_time']:.3f}秒")
    
    if report['recommendations']:
        print("\n优化建议:")
        for rec in report['recommendations']:
            print(f"- {rec}")

if __name__ == "__main__":
    main()
```

## SQL优化最佳实践

### 查询设计原则
1. **避免SELECT ***: 只查询需要的列
2. **合理使用WHERE**: 限制数据范围
3. **优化JOIN**: 选择合适的JOIN类型和顺序
4. **使用索引**: 为查询条件创建合适的索引

### 索引设计原则
1. **高选择性**: 选择性高的字段适合建索引
2. **复合索引**: 多条件查询使用复合索引
3. **覆盖索引**: 包含查询所有字段的索引
4. **定期维护**: 定期分析和重建索引

### 性能监控
1. **慢查询日志**: 记录和分析慢查询
2. **执行计划**: 分析查询执行计划
3. **性能指标**: 监控关键性能指标
4. **趋势分析**: 分析性能变化趋势

## 相关技能

- **database-query-analyzer** - 数据库查询分析
- **api-validator** - API接口验证和设计
- **performance-profiler** - 性能分析和监控
- **database-design** - 数据库设计优化
