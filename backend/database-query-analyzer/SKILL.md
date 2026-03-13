---
name: 数据库查询分析器
description: "当分析数据库查询性能时，优化SQL查询，解决性能瓶颈，监控数据库负载。验证查询计划，优化索引设计，和最佳实践。"
license: MIT
---

# 数据库查询分析器技能

## 概述
数据库查询性能是应用性能的关键因素。慢查询会导致系统响应缓慢、资源占用过高、用户体验差。需要建立完善的查询分析和优化机制。

**核心原则**: 优化查询，防止它们拖慢系统。随着数据增长，糟糕的查询问题会加剧。

## 何时使用

**始终:**
- 查询运行缓慢时
- 数据库CPU飙升时
- 应用性能下降时
- 规划数据模型时
- 设计数据库索引时
- 分析数据库负载时

**触发短语:**
- "查询太慢了"
- "数据库CPU很高"
- "如何优化这个查询？"
- "索引怎么设计？"
- "查询计划怎么分析？"
- "数据库负载过高"

## 数据库查询分析功能

### 查询性能分析
- 查询执行计划分析
- 慢查询日志分析
- 查询复杂度评估
- 索引使用效率分析
- 查询性能基准测试

### 索引优化策略
- 索引设计建议
- 索引使用情况分析
- 冗余索引检测
- 索引优化方案
- 索引性能监控

### 数据库监控
- 查询执行统计
- 数据库负载监控
- 资源使用分析
- 性能趋势分析
- 异常查询检测

## 常见查询性能问题

### 缺少索引问题
```
问题:
查询条件没有合适的索引支持

后果:
- 全表扫描
- 查询速度慢
- CPU占用高
- 内存使用大

解决方案:
- 创建合适的索引
- 复合索引优化
- 覆盖索引设计
- 索引选择性分析
```

### 查询设计问题
```
问题:
SQL查询语句设计不当

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

### 数据库配置问题
```
问题:
数据库配置不当影响性能

后果:
- 缓存效率低
- 连接池不足
- 内存分配不当
- I/O瓶颈

解决方案:
- 优化配置参数
- 调整缓存设置
- 优化连接池
- 监控资源使用
```

## 查询优化策略

### 索引设计原则
```
单列索引:
- 适合高选择性字段
- 查询条件简单
- 数据更新频繁

复合索引:
- 多条件查询
- 字段顺序重要
- 覆盖查询需求

覆盖索引:
- 包含查询所有字段
- 避免回表查询
- 提升查询性能
```

### 查询优化技巧
```
查询重写:
- 避免SELECT *
- 使用LIMIT限制结果
- 优化WHERE条件
- 合理使用JOIN

执行计划分析:
- 查看查询成本
- 分析索引使用
- 识别性能瓶颈
- 优化访问路径
```

## 代码实现示例

### Python查询分析器
```python
import psycopg2
import time
from contextlib import contextmanager
from typing import Dict, List, Any
import json

class DatabaseQueryAnalyzer:
    """数据库查询分析器"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
        finally:
            conn.close()
    
    def analyze_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """分析查询性能"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 执行EXPLAIN ANALYZE
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            start_time = time.time()
            
            cursor.execute(explain_query, params)
            explain_result = cursor.fetchone()[0]
            
            execution_time = time.time() - start_time
            
            # 解析执行计划
            plan = explain_result[0]
            
            return {
                'query': query,
                'execution_time': execution_time,
                'plan': plan,
                'cost': plan.get('Total Cost', 0),
                'rows': plan.get('Actual Rows', 0),
                'buffers': plan.get('Buffers', {}),
                'warnings': self._analyze_warnings(plan)
            }
    
    def _analyze_warnings(self, plan: Dict) -> List[str]:
        """分析执行计划中的警告"""
        warnings = []
        
        # 检查全表扫描
        if plan.get('Node Type') == 'Seq Scan':
            warnings.append("检测到全表扫描，考虑添加索引")
        
        # 检查排序操作
        if plan.get('Node Type') == 'Sort':
            warnings.append("检测到排序操作，可能影响性能")
        
        # 检查哈希连接
        if plan.get('Node Type') == 'Hash Join':
            warnings.append("检测到哈希连接，注意内存使用")
        
        # 检查嵌套循环
        if plan.get('Node Type') == 'Nested Loop':
            warnings.append("检测到嵌套循环，可能需要优化")
        
        return warnings
    
    def find_slow_queries(self, threshold_ms: float = 1000) -> List[Dict]:
        """查找慢查询"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 查询pg_stat_statements视图
            query = """
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                rows,
                100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
            FROM pg_stat_statements 
            WHERE mean_time > %s
            ORDER BY mean_time DESC
            LIMIT 10
            """
            
            cursor.execute(query, (threshold_ms,))
            results = cursor.fetchall()
            
            return [
                {
                    'query': row[0],
                    'calls': row[1],
                    'total_time': row[2],
                    'mean_time': row[3],
                    'rows': row[4],
                    'hit_percent': row[5]
                }
                for row in results
            ]
    
    def analyze_index_usage(self) -> List[Dict]:
        """分析索引使用情况"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 查询索引使用统计
            query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan ASC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            return [
                {
                    'schema': row[0],
                    'table': row[1],
                    'index': row[2],
                    'scans': row[3],
                    'tuples_read': row[4],
                    'tuples_fetched': row[5],
                    'size': row[6]
                }
                for row in results
            ]
    
    def suggest_indexes(self, table_name: str) -> List[Dict]:
        """建议索引优化"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 分析表结构
            cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
            """, (table_name,))
            
            columns = cursor.fetchall()
            
            # 分析查询模式
            cursor.execute("""
            SELECT query, calls
            FROM pg_stat_statements 
            WHERE query LIKE %s
            ORDER BY calls DESC
            LIMIT 5
            """, (f'%{table_name}%',))
            
            queries = cursor.fetchall()
            
            suggestions = []
            
            # 基于查询模式建议索引
            for query, calls in queries:
                if 'WHERE' in query:
                    # 提取WHERE条件中的字段
                    where_clause = query.split('WHERE')[1].split('ORDER')[0].split('GROUP')[0]
                    # 简单的字段提取逻辑
                    fields = self._extract_where_fields(where_clause)
                    
                    if fields:
                        suggestions.append({
                            'type': 'composite_index',
                            'fields': fields,
                            'reason': f'基于高频查询（调用次数：{calls}）',
                            'query_sample': query[:100] + '...'
                        })
            
            return suggestions
    
    def _extract_where_fields(self, where_clause: str) -> List[str]:
        """从WHERE子句中提取字段名"""
        import re
        
        # 简单的字段提取正则表达式
        pattern = r'(\w+)\s*='
        matches = re.findall(pattern, where_clause)
        
        # 过滤掉常见的非字段名
        excluded = {'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN'}
        fields = [field for field in matches if field.upper() not in excluded]
        
        return list(set(fields))[:3]  # 最多返回3个字段
    
    def monitor_database_load(self) -> Dict[str, Any]:
        """监控数据库负载"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取数据库状态
            cursor.execute("""
            SELECT 
                datname,
                numbackends,
                xact_commit,
                xact_rollback,
                blks_read,
                blks_hit,
                tup_returned,
                tup_fetched,
                tup_inserted,
                tup_updated,
                tup_deleted
            FROM pg_stat_database
            WHERE datname = current_database()
            """)
            
            stats = cursor.fetchone()
            
            # 计算缓存命中率
            hit_ratio = 0
            if stats[4] + stats[5] > 0:
                hit_ratio = stats[5] / (stats[4] + stats[5]) * 100
            
            return {
                'database': stats[0],
                'active_connections': stats[1],
                'transactions_committed': stats[2],
                'transactions_rolled_back': stats[3],
                'blocks_read': stats[4],
                'blocks_hit': stats[5],
                'cache_hit_ratio': hit_ratio,
                'tuples_returned': stats[6],
                'tuples_fetched': stats[7],
                'tuples_inserted': stats[8],
                'tuples_updated': stats[9],
                'tuples_deleted': stats[10]
            }

# 使用示例
analyzer = DatabaseQueryAnalyzer("postgresql://user:password@localhost/dbname")

# 分析查询性能
result = analyzer.analyze_query("SELECT * FROM users WHERE email = %s", ("test@example.com",))
print(f"查询执行时间: {result['execution_time']:.3f}s")
print(f"执行成本: {result['cost']}")
print(f"警告: {result['warnings']}")

# 查找慢查询
slow_queries = analyzer.find_slow_queries(threshold_ms=500)
for query in slow_queries:
    print(f"慢查询: {query['query'][:50]}...")
    print(f"平均执行时间: {query['mean_time']:.3f}ms")

# 分析索引使用
index_usage = analyzer.analyze_index_usage()
for index in index_usage:
    if index['scans'] == 0:
        print(f"未使用的索引: {index['index']} (大小: {index['size']})")

# 建议索引优化
suggestions = analyzer.suggest_indexes('users')
for suggestion in suggestions:
    print(f"建议: 在{suggestion['fields']}上创建{suggestion['type']}")
    print(f"原因: {suggestion['reason']}")
```

### 查询优化建议系统
```python
class QueryOptimizer:
    """查询优化建议系统"""
    
    def __init__(self, analyzer: DatabaseQueryAnalyzer):
        self.analyzer = analyzer
    
    def optimize_query(self, query: str) -> Dict[str, Any]:
        """优化查询建议"""
        analysis = self.analyzer.analyze_query(query)
        
        suggestions = []
        
        # 基于执行计划的优化建议
        plan = analysis['plan']
        
        if plan.get('Node Type') == 'Seq Scan':
            suggestions.append({
                'type': 'add_index',
                'description': '考虑添加索引以避免全表扫描',
                'priority': 'high'
            })
        
        if 'Sort' in str(plan):
            suggestions.append({
                'type': 'add_order_index',
                'description': '考虑添加排序索引以优化ORDER BY操作',
                'priority': 'medium'
            })
        
        # 分析查询语句本身
        query_lower = query.lower()
        
        if 'select *' in query_lower:
            suggestions.append({
                'type': 'select_specific_columns',
                'description': '避免使用SELECT *，只查询需要的列',
                'priority': 'medium'
            })
        
        if 'like' in query_lower and '%' in query:
            suggestions.append({
                'type': 'optimize_like',
                'description': '考虑优化LIKE查询，避免前导通配符',
                'priority': 'low'
            })
        
        return {
            'original_query': query,
            'analysis': analysis,
            'suggestions': suggestions,
            'estimated_improvement': self._estimate_improvement(suggestions)
        }
    
    def _estimate_improvement(self, suggestions: List[Dict]) -> float:
        """估算性能提升百分比"""
        improvement = 0
        
        for suggestion in suggestions:
            if suggestion['priority'] == 'high':
                improvement += 50
            elif suggestion['priority'] == 'medium':
                improvement += 20
            elif suggestion['priority'] == 'low':
                improvement += 5
        
        return min(improvement, 80)  # 最多80%提升

# 使用示例
optimizer = QueryOptimizer(analyzer)

query = "SELECT * FROM orders WHERE user_id = 123 ORDER BY created_at DESC"
optimization = optimizer.optimize_query(query)

print(f"原始查询: {optimization['original_query']}")
print(f"执行时间: {optimization['analysis']['execution_time']:.3f}s")

for suggestion in optimization['suggestions']:
    print(f"建议: {suggestion['description']} (优先级: {suggestion['priority']})")

print(f"预计性能提升: {optimization['estimated_improvement']}%")
```

## 性能监控最佳实践

### 查询监控
1. **慢查询日志**: 记录执行时间超过阈值的查询
2. **查询统计**: 统计查询执行频率和性能
3. **执行计划缓存**: 缓存常用查询的执行计划
4. **性能趋势**: 监控查询性能变化趋势

### 索引管理
1. **定期分析**: 定期分析索引使用情况
2. **清理冗余**: 清理未使用或重复的索引
3. **监控大小**: 监控索引大小和增长
4. **优化建议**: 基于查询模式优化索引

## 相关技能

- **api-validator** - API接口验证和设计
- **caching-strategies** - 缓存策略和实现
- **database-design** - 数据库设计优化
- **performance-profiler** - 性能分析和监控
