---
name: SQL优化与索引
description: "当优化数据库性能时，分析查询执行计划，设计高效索引，优化SQL语句。调整数据库配置，监控性能指标，和实施最佳实践。"
license: MIT
---

# SQL优化与索引技能

## 概述
SQL优化是提升数据库性能的核心技术。不当的查询设计和索引策略会导致系统响应缓慢、资源浪费、用户体验差。需要系统性的优化方法。

**核心原则**: 好的SQL优化应该查询高效、索引合理、资源利用充分、响应快速。坏的SQL优化会查询缓慢、资源浪费、系统不稳定。

## 何时使用

**始终:**
- 查询响应时间过长时
- 系统负载过高时
- 数据库性能下降时
- 用户体验不佳时
- 资源使用率异常时
- 并发访问困难时

**触发短语:**
- "SQL查询优化"
- "索引设计策略"
- "查询性能分析"
- "执行计划解读"
- "数据库调优"
- "慢查询优化"

## SQL优化功能

### 查询分析
- 执行计划分析
- 查询成本评估
- 性能瓶颈识别
- 资源使用分析
- 慢查询检测

### 索引优化
- 索引设计策略
- 复合索引优化
- 索引使用分析
- 索引维护管理
- 索引效果评估

### 语句优化
- 查询重写
- 连接优化
- 子查询优化
- 聚合查询优化
- 分页查询优化

### 配置调优
- 内存配置优化
- 连接池配置
- 缓存策略调整
- 并发参数优化
- 存储引擎优化

## 常见SQL优化问题

### 全表扫描
```
问题:
查询导致全表扫描，性能极差

错误示例:
- 缺少合适的索引
- 索引选择性差
- 查询条件不当
- 统计信息过时

解决方案:
1. 创建合适的索引
2. 优化查询条件
3. 更新统计信息
4. 重写查询语句
```

### 索引失效
```
问题:
索引存在但不被使用，查询仍然缓慢

错误示例:
- 索引列使用函数
- 类型不匹配
- 隐式转换
- 前导通配符

解决方案:
1. 避免索引列计算
2. 保证类型一致
3. 使用函数索引
4. 优化查询条件
```

### 连接查询性能差
```
问题:
多表连接查询性能差，响应时间长

错误示例:
- 缺少连接索引
- 连接顺序不当
- 笛卡尔积
- 不必要的连接

解决方案:
1. 优化连接索引
2. 调整连接顺序
3. 避免笛卡尔积
4. 减少连接表数
```

### 子查询性能问题
```
问题:
子查询执行效率低，影响整体性能

错误示例:
- 相关子查询
- 多层嵌套子查询
- 非优化子查询
- 重复计算

解决方案:
1. 使用JOIN代替子查询
2. 优化子查询结构
3. 使用EXISTS代替IN
4. 减少嵌套层次
```

## 代码实现示例

### SQL查询分析器
```python
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time

class QueryType(Enum):
    """查询类型"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    DROP = "drop"
    ALTER = "alter"

class OptimizationLevel(Enum):
    """优化级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class QueryAnalysis:
    """查询分析结果"""
    query: str
    query_type: QueryType
    complexity_score: int
    tables: List[str]
    columns: List[str]
    joins: List[str]
    where_conditions: List[str]
    group_by: List[str]
    order_by: List[str]
    having_conditions: List[str]
    subqueries: List[str]

@dataclass
class OptimizationSuggestion:
    """优化建议"""
    type: str
    description: str
    impact: str
    difficulty: str
    example: str

@dataclass
class IndexRecommendation:
    """索引推荐"""
    table_name: str
    column_names: List[str]
    index_type: str
    estimated_improvement: float
    reason: str

class SQLQueryAnalyzer:
    def __init__(self):
        self.optimization_patterns = {
            'full_table_scan': self._detect_full_table_scan,
            'missing_index': self._detect_missing_index,
            'inefficient_join': self._detect_inefficient_join,
            'subquery_optimization': self._detect_subquery_optimization,
            'function_on_index': self._detect_function_on_index,
            'select_star': self._detect_select_star,
            'implicit_conversion': self._detect_implicit_conversion,
        }
        
        self.index_analyzer = IndexAnalyzer()
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """分析SQL查询"""
        # 标准化查询
        normalized_query = self._normalize_query(query)
        
        # 识别查询类型
        query_type = self._identify_query_type(normalized_query)
        
        # 提取查询组件
        tables = self._extract_tables(normalized_query)
        columns = self._extract_columns(normalized_query)
        joins = self._extract_joins(normalized_query)
        where_conditions = self._extract_where_conditions(normalized_query)
        group_by = self._extract_group_by(normalized_query)
        order_by = self._extract_order_by(normalized_query)
        having_conditions = self._extract_having_conditions(normalized_query)
        subqueries = self._extract_subqueries(normalized_query)
        
        # 计算复杂度分数
        complexity_score = self._calculate_complexity_score(
            tables, joins, where_conditions, group_by, having_conditions, subqueries
        )
        
        return QueryAnalysis(
            query=query,
            query_type=query_type,
            complexity_score=complexity_score,
            tables=tables,
            columns=columns,
            joins=joins,
            where_conditions=where_conditions,
            group_by=group_by,
            order_by=order_by,
            having_conditions=having_conditions,
            subqueries=subqueries
        )
    
    def generate_optimization_suggestions(self, analysis: QueryAnalysis) -> List[OptimizationSuggestion]:
        """生成优化建议"""
        suggestions = []
        
        # 检查各种优化模式
        for pattern_name, pattern_func in self.optimization_patterns.items():
            pattern_suggestions = pattern_func(analysis)
            suggestions.extend(pattern_suggestions)
        
        # 生成索引建议
        index_suggestions = self._generate_index_suggestions(analysis)
        suggestions.extend(index_suggestions)
        
        # 按影响程度排序
        suggestions.sort(key=lambda x: self._get_impact_priority(x.impact), reverse=True)
        
        return suggestions
    
    def _normalize_query(self, query: str) -> str:
        """标准化查询"""
        # 移除注释
        query = re.sub(r'--.*?\n', '\n', query)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # 标准化空白字符
        query = re.sub(r'\s+', ' ', query)
        query = query.strip()
        
        return query
    
    def _identify_query_type(self, query: str) -> QueryType:
        """识别查询类型"""
        query_upper = query.upper()
        
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
            return QueryType.SELECT  # 默认为SELECT
    
    def _extract_tables(self, query: str) -> List[str]:
        """提取表名"""
        tables = []
        
        # FROM子句中的表
        from_match = re.search(r'FROM\s+([^WHERE]+)', query, re.IGNORECASE)
        if from_match:
            from_clause = from_match.group(1)
            # 移除子查询
            from_clause = re.sub(r'\(.*?\)', '', from_clause)
            # 分割表名
            table_names = re.findall(r'(\w+)', from_clause)
            tables.extend(table_names)
        
        # JOIN子句中的表
        join_matches = re.findall(r'JOIN\s+(\w+)', query, re.IGNORECASE)
        tables.extend(join_matches)
        
        return list(set(tables))
    
    def _extract_columns(self, query: str) -> List[str]:
        """提取列名"""
        columns = []
        
        # SELECT子句中的列
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if select_match:
            select_clause = select_match.group(1)
            
            # 处理SELECT *
            if '*' in select_clause:
                columns.append('*')
            else:
                # 提取列名
                column_names = re.findall(r'(\w+)', select_clause)
                # 过滤掉函数名和关键字
                columns.extend([col for col in column_names if col.upper() not in ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'DISTINCT']])
        
        return list(set(columns))
    
    def _extract_joins(self, query: str) -> List[str]:
        """提取连接条件"""
        joins = []
        
        # 查找JOIN语句
        join_patterns = [
            r'JOIN\s+(\w+)\s+ON\s+([^JOIN]+)',
            r'LEFT\s+JOIN\s+(\w+)\s+ON\s+([^JOIN]+)',
            r'RIGHT\s+JOIN\s+(\w+)\s+ON\s+([^JOIN]+)',
            r'INNER\s+JOIN\s+(\w+)\s+ON\s+([^JOIN]+)',
            r'OUTER\s+JOIN\s+(\w+)\s+ON\s+([^JOIN]+)'
        ]
        
        for pattern in join_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                join_info = f"{match[0]} ON {match[1].strip()}"
                joins.append(join_info)
        
        return joins
    
    def _extract_where_conditions(self, query: str) -> List[str]:
        """提取WHERE条件"""
        conditions = []
        
        where_match = re.search(r'WHERE\s+(.*?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+HAVING|\s+LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1).strip()
            # 分割条件
            condition_parts = re.split(r'\s+(?:AND|OR)\s+', where_clause, flags=re.IGNORECASE)
            conditions.extend([part.strip() for part in condition_parts if part.strip()])
        
        return conditions
    
    def _extract_group_by(self, query: str) -> List[str]:
        """提取GROUP BY字段"""
        group_by_match = re.search(r'GROUP\s+BY\s+(.*?)(?:\s+ORDER\s+BY|\s+HAVING|\s+LIMIT|$)', query, re.IGNORECASE)
        if group_by_match:
            group_by_clause = group_by_match.group(1)
            return [col.strip() for col in group_by_clause.split(',')]
        return []
    
    def _extract_order_by(self, query: str) -> List[str]:
        """提取ORDER BY字段"""
        order_by_match = re.search(r'ORDER\s+BY\s+(.*?)(?:\s+LIMIT|$)', query, re.IGNORECASE)
        if order_by_match:
            order_by_clause = order_by_match.group(1)
            return [col.strip() for col in order_by_clause.split(',')]
        return []
    
    def _extract_having_conditions(self, query: str) -> List[str]:
        """提取HAVING条件"""
        conditions = []
        
        having_match = re.search(r'HAVING\s+(.*?)(?:\s+ORDER\s+BY|\s+LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if having_match:
            having_clause = having_match.group(1).strip()
            condition_parts = re.split(r'\s+(?:AND|OR)\s+', having_clause, flags=re.IGNORECASE)
            conditions.extend([part.strip() for part in condition_parts if part.strip()])
        
        return conditions
    
    def _extract_subqueries(self, query: str) -> List[str]:
        """提取子查询"""
        subqueries = []
        
        # 查找子查询模式
        subquery_patterns = [
            r'\(\s*SELECT\s+.*?\s*\)',
            r'IN\s*\(\s*SELECT\s+.*?\s*\)',
            r'EXISTS\s*\(\s*SELECT\s+.*?\s*\)',
            r'NOT\s+EXISTS\s*\(\s*SELECT\s+.*?\s*\)'
        ]
        
        for pattern in subquery_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE | re.DOTALL)
            subqueries.extend(matches)
        
        return subqueries
    
    def _calculate_complexity_score(self, tables: List[str], joins: List[str], 
                                   where_conditions: List[str], group_by: List[str], 
                                   having_conditions: List[str], subqueries: List[str]) -> int:
        """计算查询复杂度分数"""
        score = 0
        
        # 表数量影响
        score += len(tables) * 2
        
        # 连接复杂度
        score += len(joins) * 3
        
        # WHERE条件复杂度
        score += len(where_conditions) * 1
        
        # GROUP BY复杂度
        score += len(group_by) * 2
        
        # HAVING条件复杂度
        score += len(having_conditions) * 2
        
        # 子查询复杂度
        score += len(subqueries) * 5
        
        return score
    
    def _detect_full_table_scan(self, analysis: QueryAnalysis) -> List[OptimizationSuggestion]:
        """检测全表扫描"""
        suggestions = []
        
        # 检查是否有WHERE条件但没有合适的索引列
        if analysis.where_conditions and not any('WHERE' in cond for cond in analysis.where_conditions):
            suggestions.append(OptimizationSuggestion(
                type="full_table_scan",
                description="查询可能导致全表扫描",
                impact="高",
                difficulty="中",
                example="在WHERE条件列上创建索引"
            ))
        
        return suggestions
    
    def _detect_missing_index(self, analysis: QueryAnalysis) -> List[OptimizationSuggestion]:
        """检测缺失索引"""
        suggestions = []
        
        # 检查WHERE条件中的列
        for condition in analysis.where_conditions:
            columns = re.findall(r'(\w+)\s*=', condition)
            for column in columns:
                if column not in analysis.columns:
                    suggestions.append(OptimizationSuggestion(
                        type="missing_index",
                        description=f"列 {column} 可能需要索引",
                        impact="高",
                        difficulty="低",
                        example=f"CREATE INDEX idx_{column} ON table_name ({column})"
                    ))
        
        return suggestions
    
    def _detect_inefficient_join(self, analysis: QueryAnalysis) -> List[OptimizationSuggestion]:
        """检测低效连接"""
        suggestions = []
        
        # 检查连接条件
        for join in analysis.joins:
            if 'ON' in join:
                on_condition = join.split('ON')[1].strip()
                # 检查是否使用了合适的连接列
                if '=' not in on_condition:
                    suggestions.append(OptimizationSuggestion(
                        type="inefficient_join",
                        description="连接条件可能不够高效",
                        impact="中",
                        difficulty="中",
                        example="使用等值连接并确保连接列有索引"
                    ))
        
        return suggestions
    
    def _detect_subquery_optimization(self, analysis: QueryAnalysis) -> List[OptimizationSuggestion]:
        """检测子查询优化机会"""
        suggestions = []
        
        for subquery in analysis.subqueries:
            # 检查是否可以转换为JOIN
            if 'IN' in subquery or 'EXISTS' in subquery:
                suggestions.append(OptimizationSuggestion(
                    type="subquery_optimization",
                    description="子查询可能可以优化为JOIN",
                    impact="中",
                    difficulty="中",
                    example="考虑使用JOIN代替子查询"
                ))
        
        return suggestions
    
    def _detect_function_on_index(self, analysis: QueryAnalysis) -> List[OptimizationSuggestion]:
        """检测索引列上使用函数"""
        suggestions = []
        
        for condition in analysis.where_conditions:
            # 检查函数使用
            if re.search(r'\w+\s*\(', condition):
                suggestions.append(OptimizationSuggestion(
                    type="function_on_index",
                    description="索引列上使用函数可能导致索引失效",
                    impact="高",
                    difficulty="中",
                    example="避免在索引列上使用函数，或使用函数索引"
                ))
        
        return suggestions
    
    def _detect_select_star(self, analysis: QueryAnalysis) -> List[OptimizationSuggestion]:
        """检测SELECT *"""
        suggestions = []
        
        if '*' in analysis.columns:
            suggestions.append(OptimizationSuggestion(
                type="select_star",
                description="使用SELECT *可能影响性能",
                impact="低",
                difficulty="低",
                example="只查询需要的列"
            ))
        
        return suggestions
    
    def _detect_implicit_conversion(self, analysis: QueryAnalysis) -> List[OptimizationSuggestion]:
        """检测隐式类型转换"""
        suggestions = []
        
        # 简化的隐式转换检测
        for condition in analysis.where_conditions:
            if "'" in condition and re.search(r'\w+\s*=', condition):
                suggestions.append(OptimizationSuggestion(
                    type="implicit_conversion",
                    description="可能存在隐式类型转换",
                    impact="中",
                    difficulty="低",
                    example="确保比较操作类型一致"
                ))
        
        return suggestions
    
    def _generate_index_suggestions(self, analysis: QueryAnalysis) -> List[OptimizationSuggestion]:
        """生成索引建议"""
        suggestions = []
        
        # 为WHERE条件生成索引建议
        if analysis.where_conditions:
            columns = []
            for condition in analysis.where_conditions:
                condition_columns = re.findall(r'(\w+)\s*=', condition)
                columns.extend(condition_columns)
            
            if columns:
                unique_columns = list(set(columns))
                if len(unique_columns) > 1:
                    suggestions.append(OptimizationSuggestion(
                        type="composite_index",
                        description=f"考虑创建复合索引: {', '.join(unique_columns)}",
                        impact="高",
                        difficulty="低",
                        example=f"CREATE INDEX idx_composite ON table_name ({', '.join(unique_columns)})"
                    ))
                else:
                    suggestions.append(OptimizationSuggestion(
                        type="single_index",
                        description=f"考虑为列 {unique_columns[0]} 创建索引",
                        impact="高",
                        difficulty="低",
                        example=f"CREATE INDEX idx_{unique_columns[0]} ON table_name ({unique_columns[0]})"
                    ))
        
        # 为ORDER BY生成索引建议
        if analysis.order_by and not analysis.where_conditions:
            order_columns = [col.split()[0] for col in analysis.order_by]
            suggestions.append(OptimizationSuggestion(
                type="order_index",
                description=f"为ORDER BY列创建索引: {', '.join(order_columns)}",
                impact="中",
                difficulty="低",
                example=f"CREATE INDEX idx_order ON table_name ({', '.join(order_columns)})"
            ))
        
        return suggestions
    
    def _get_impact_priority(self, impact: str) -> int:
        """获取影响优先级"""
        impact_priorities = {
            "高": 3,
            "中": 2,
            "低": 1
        }
        return impact_priorities.get(impact, 0)

class IndexAnalyzer:
    def __init__(self):
        self.index_types = {
            'btree': 'B-Tree索引',
            'hash': '哈希索引',
            'gist': 'GiST索引',
            'gin': 'GIN索引',
            'spatial': '空间索引',
            'fulltext': '全文索引'
        }
    
    def analyze_index_usage(self, query: str, existing_indexes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析索引使用情况"""
        analysis = {
            'used_indexes': [],
            'unused_indexes': [],
            'missing_indexes': [],
            'recommendations': []
        }
        
        # 简化的索引使用分析
        for index in existing_indexes:
            if index['table_name'].lower() in query.lower():
                # 检查索引列是否在查询中使用
                index_columns = index['columns']
                query_lower = query.lower()
                
                used = False
                for column in index_columns:
                    if column.lower() in query_lower:
                        used = True
                        break
                
                if used:
                    analysis['used_indexes'].append(index)
                else:
                    analysis['unused_indexes'].append(index)
        
        return analysis

# 使用示例
def main():
    print("=== SQL查询分析器 ===")
    
    # 创建分析器
    analyzer = SQLQueryAnalyzer()
    
    # 示例查询
    queries = [
        """
        SELECT u.name, p.title, c.content
        FROM users u
        JOIN posts p ON u.id = p.user_id
        JOIN comments c ON p.id = c.post_id
        WHERE u.status = 'active' AND p.created_at > '2023-01-01'
        ORDER BY p.created_at DESC
        LIMIT 10
        """,
        
        """
        SELECT * FROM orders 
        WHERE customer_id IN (SELECT id FROM customers WHERE city = '北京')
        """,
        
        """
        SELECT product_name, COUNT(*) as order_count
        FROM order_items
        WHERE price > 100
        GROUP BY product_name
        HAVING COUNT(*) > 5
        """
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n=== 查询 {i} ===")
        print(f"SQL: {query.strip()}")
        
        # 分析查询
        analysis = analyzer.analyze_query(query)
        
        print(f"查询类型: {analysis.query_type.value}")
        print(f"复杂度分数: {analysis.complexity_score}")
        print(f"涉及表: {', '.join(analysis.tables)}")
        print(f"涉及列: {', '.join(analysis.columns)}")
        print(f"连接数: {len(analysis.joins)}")
        print(f"WHERE条件数: {len(analysis.where_conditions)}")
        print(f"子查询数: {len(analysis.subqueries)}")
        
        # 生成优化建议
        suggestions = analyzer.generate_optimization_suggestions(analysis)
        
        if suggestions:
            print(f"\n优化建议:")
            for j, suggestion in enumerate(suggestions, 1):
                print(f"{j}. [{suggestion.impact}影响] {suggestion.description}")
                print(f"   示例: {suggestion.example}")
        else:
            print("\n查询已优化，无需改进")

if __name__ == '__main__':
    main()
```

### 索引设计器
```python
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json

class IndexType(Enum):
    """索引类型"""
    BTREE = "btree"
    HASH = "hash"
    GIST = "gist"
    GIN = "gin"
    SPATIAL = "spatial"
    FULLTEXT = "fulltext"

class IndexUsage(Enum):
    """索引用途"""
    EQUALITY = "equality"
    RANGE = "range"
    ORDER = "order"
    GROUP = "group"
    JOIN = "join"
    SEARCH = "search"

@dataclass
class ColumnInfo:
    """列信息"""
    name: str
    data_type: str
    is_nullable: bool
    is_unique: bool
    cardinality: int
    selectivity: float
    avg_length: int

@dataclass
class TableInfo:
    """表信息"""
    name: str
    row_count: int
    columns: List[ColumnInfo]
    primary_key: List[str]
    foreign_keys: Dict[str, str]

@dataclass
class IndexDefinition:
    """索引定义"""
    name: str
    table_name: str
    columns: List[str]
    index_type: IndexType
    is_unique: bool
    is_partial: bool
    where_condition: Optional[str] = None
    usage_types: List[IndexUsage] = field(default_factory=list)

@dataclass
class IndexRecommendation:
    """索引推荐"""
    definition: IndexDefinition
    reason: str
    estimated_improvement: float
    creation_cost: float
    priority: str

class IndexDesigner:
    def __init__(self):
        self.design_rules = {
            'primary_key': self._design_primary_key_index,
            'foreign_key': self._design_foreign_key_index,
            'equality_search': self._design_equality_search_index,
            'range_search': self._design_range_search_index,
            'order_by': self._design_order_by_index,
            'group_by': self._design_group_by_index,
            'join_optimization': self._design_join_optimization_index,
            'full_text_search': self._design_full_text_search_index,
        }
    
    def analyze_table_and_recommend_indexes(self, table_info: TableInfo, 
                                           query_patterns: List[str]) -> List[IndexRecommendation]:
        """分析表并推荐索引"""
        recommendations = []
        
        # 分析表结构
        structure_recommendations = self._analyze_table_structure(table_info)
        recommendations.extend(structure_recommendations)
        
        # 分析查询模式
        query_recommendations = self._analyze_query_patterns(table_info, query_patterns)
        recommendations.extend(query_recommendations)
        
        # 分析现有索引
        existing_recommendations = self._analyze_existing_indexes(table_info)
        recommendations.extend(existing_recommendations)
        
        # 排序推荐
        recommendations.sort(key=lambda x: x.estimated_improvement / x.creation_cost, reverse=True)
        
        return recommendations
    
    def _analyze_table_structure(self, table_info: TableInfo) -> List[IndexRecommendation]:
        """分析表结构推荐索引"""
        recommendations = []
        
        # 主键索引
        if table_info.primary_key:
            primary_key_rec = self._design_primary_key_index(table_info, table_info.primary_key)
            recommendations.append(primary_key_rec)
        
        # 外键索引
        for fk_column, ref_table in table_info.foreign_keys.items():
            fk_rec = self._design_foreign_key_index(table_info, [fk_column], ref_table)
            recommendations.append(fk_rec)
        
        # 唯一列索引
        for column in table_info.columns:
            if column.is_unique and column.name not in table_info.primary_key:
                unique_rec = self._design_unique_column_index(table_info, column)
                recommendations.append(unique_rec)
        
        return recommendations
    
    def _analyze_query_patterns(self, table_info: TableInfo, query_patterns: List[str]) -> List[IndexRecommendation]:
        """分析查询模式推荐索引"""
        recommendations = []
        
        for query in query_patterns:
            query_lower = query.lower()
            
            # 检查等值查询
            if 'where' in query_lower and '=' in query_lower:
                equality_recommendations = self._analyze_equality_queries(table_info, query)
                recommendations.extend(equality_recommendations)
            
            # 检查范围查询
            if any(op in query_lower for op in ['>', '<', '>=', '<=', 'between', 'like']):
                range_recommendations = self._analyze_range_queries(table_info, query)
                recommendations.extend(range_recommendations)
            
            # 检查排序查询
            if 'order by' in query_lower:
                order_recommendations = self._analyze_order_queries(table_info, query)
                recommendations.extend(order_recommendations)
            
            # 检查分组查询
            if 'group by' in query_lower:
                group_recommendations = self._analyze_group_queries(table_info, query)
                recommendations.extend(group_recommendations)
            
            # 检查连接查询
            if 'join' in query_lower:
                join_recommendations = self._analyze_join_queries(table_info, query)
                recommendations.extend(join_recommendations)
            
            # 检查全文搜索
            if 'like' in query_lower or 'match' in query_lower:
                search_recommendations = self._analyze_search_queries(table_info, query)
                recommendations.extend(search_recommendations)
        
        return recommendations
    
    def _analyze_existing_indexes(self, table_info: TableInfo) -> List[IndexRecommendation]:
        """分析现有索引"""
        recommendations = []
        
        # 这里可以添加分析现有索引的逻辑
        # 检查是否有冗余索引、未使用索引等
        
        return recommendations
    
    def _design_primary_key_index(self, table_info: TableInfo, columns: List[str]) -> IndexRecommendation:
        """设计主键索引"""
        index_def = IndexDefinition(
            name=f"pk_{'_'.join(columns)}",
            table_name=table_info.name,
            columns=columns,
            index_type=IndexType.BTREE,
            is_unique=True,
            is_partial=False,
            usage_types=[IndexUsage.EQUALITY, IndexUsage.JOIN]
        )
        
        return IndexRecommendation(
            definition=index_def,
            reason="主键索引，用于唯一标识记录和连接查询",
            estimated_improvement=0.9,
            creation_cost=0.1,
            priority="高"
        )
    
    def _design_foreign_key_index(self, table_info: TableInfo, columns: List[str], ref_table: str) -> IndexRecommendation:
        """设计外键索引"""
        index_def = IndexDefinition(
            name=f"fk_{'_'.join(columns)}_{ref_table}",
            table_name=table_info.name,
            columns=columns,
            index_type=IndexType.BTREE,
            is_unique=False,
            is_partial=False,
            usage_types=[IndexUsage.JOIN, IndexUsage.EQUALITY]
        )
        
        return IndexRecommendation(
            definition=index_def,
            reason=f"外键索引，优化与{ref_table}表的连接查询",
            estimated_improvement=0.8,
            creation_cost=0.2,
            priority="高"
        )
    
    def _design_unique_column_index(self, table_info: TableInfo, column: ColumnInfo) -> IndexRecommendation:
        """设计唯一列索引"""
        index_def = IndexDefinition(
            name=f"uk_{column.name}",
            table_name=table_info.name,
            columns=[column.name],
            index_type=IndexType.BTREE,
            is_unique=True,
            is_partial=False,
            usage_types=[IndexUsage.EQUALITY]
        )
        
        return IndexRecommendation(
            definition=index_def,
            reason=f"唯一列索引，保证数据唯一性",
            estimated_improvement=0.7,
            creation_cost=0.2,
            priority="中"
        )
    
    def _analyze_equality_queries(self, table_info: TableInfo, query: str) -> List[IndexRecommendation]:
        """分析等值查询"""
        recommendations = []
        
        # 提取WHERE等值条件
        where_match = re.search(r'WHERE\s+(.*?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1)
            equality_conditions = re.findall(r'(\w+)\s*=\s*[\'"]?([^\'"\s]+)[\'"]?', where_clause, re.IGNORECASE)
            
            if equality_conditions:
                columns = [cond[0] for cond in equality_conditions]
                # 检查列是否存在于表中
                valid_columns = [col for col in columns if col in [c.name for c in table_info.columns]]
                
                if valid_columns:
                    index_def = IndexDefinition(
                        name=f"idx_eq_{'_'.join(valid_columns)}",
                        table_name=table_info.name,
                        columns=valid_columns,
                        index_type=IndexType.BTREE,
                        is_unique=False,
                        is_partial=False,
                        usage_types=[IndexUsage.EQUALITY]
                    )
                    
                    recommendations.append(IndexRecommendation(
                        definition=index_def,
                        reason=f"等值查询优化: {', '.join(valid_columns)}",
                        estimated_improvement=0.8,
                        creation_cost=0.3,
                        priority="高"
                    ))
        
        return recommendations
    
    def _analyze_range_queries(self, table_info: TableInfo, query: str) -> List[IndexRecommendation]:
        """分析范围查询"""
        recommendations = []
        
        # 提取范围查询条件
        range_patterns = [
            r'(\w+)\s*>\s*[\'"]?([^\'"\s]+)[\'"]?',
            r'(\w+)\s*<\s*[\'"]?([^\'"\s]+)[\'"]?',
            r'(\w+)\s*>=\s*[\'"]?([^\'"\s]+)[\'"]?',
            r'(\w+)\s*<=\s*[\'"]?([^\'"\s]+)[\'"]?',
            r'(\w+)\s+BETWEEN\s+[\'"]?([^\'"\s]+)[\'"]?\s+AND\s+[\'"]?([^\'"\s]+)[\'"]?'
        ]
        
        for pattern in range_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                column = match[0] if isinstance(match, tuple) else match
                if column in [c.name for c in table_info.columns]:
                    index_def = IndexDefinition(
                        name=f"idx_range_{column}",
                        table_name=table_info.name,
                        columns=[column],
                        index_type=IndexType.BTREE,
                        is_unique=False,
                        is_partial=False,
                        usage_types=[IndexUsage.RANGE]
                    )
                    
                    recommendations.append(IndexRecommendation(
                        definition=index_def,
                        reason=f"范围查询优化: {column}",
                        estimated_improvement=0.7,
                        creation_cost=0.3,
                        priority="中"
                    ))
        
        return recommendations
    
    def _analyze_order_queries(self, table_info: TableInfo, query: str) -> List[IndexRecommendation]:
        """分析排序查询"""
        recommendations = []
        
        # 提取ORDER BY字段
        order_match = re.search(r'ORDER\s+BY\s+(.*?)(?:\s+LIMIT|$)', query, re.IGNORECASE)
        if order_match:
            order_clause = order_match.group(1)
            order_columns = [col.strip().split()[0] for col in order_clause.split(',')]
            
            # 检查列是否存在于表中
            valid_columns = [col for col in order_columns if col in [c.name for c in table_info.columns]]
            
            if valid_columns:
                index_def = IndexDefinition(
                    name=f"idx_order_{'_'.join(valid_columns)}",
                    table_name=table_info.name,
                    columns=valid_columns,
                    index_type=IndexType.BTREE,
                    is_unique=False,
                    is_partial=False,
                    usage_types=[IndexUsage.ORDER]
                )
                
                recommendations.append(IndexRecommendation(
                    definition=index_def,
                    reason=f"排序优化: {', '.join(valid_columns)}",
                    estimated_improvement=0.6,
                    creation_cost=0.3,
                    priority="中"
                ))
        
        return recommendations
    
    def _analyze_group_queries(self, table_info: TableInfo, query: str) -> List[IndexRecommendation]:
        """分析分组查询"""
        recommendations = []
        
        # 提取GROUP BY字段
        group_match = re.search(r'GROUP\s+BY\s+(.*?)(?:\s+ORDER\s+BY|\s+HAVING|\s+LIMIT|$)', query, re.IGNORECASE)
        if group_match:
            group_clause = group_match.group(1)
            group_columns = [col.strip() for col in group_clause.split(',')]
            
            # 检查列是否存在于表中
            valid_columns = [col for col in group_columns if col in [c.name for c in table_info.columns]]
            
            if valid_columns:
                index_def = IndexDefinition(
                    name=f"idx_group_{'_'.join(valid_columns)}",
                    table_name=table_info.name,
                    columns=valid_columns,
                    index_type=IndexType.BTREE,
                    is_unique=False,
                    is_partial=False,
                    usage_types=[IndexUsage.GROUP]
                )
                
                recommendations.append(IndexRecommendation(
                    definition=index_def,
                    reason=f"分组优化: {', '.join(valid_columns)}",
                    estimated_improvement=0.5,
                    creation_cost=0.3,
                    priority="中"
                ))
        
        return recommendations
    
    def _analyze_join_queries(self, table_info: TableInfo, query: str) -> List[IndexRecommendation]:
        """分析连接查询"""
        recommendations = []
        
        # 提取连接条件
        join_patterns = [
            r'JOIN\s+\w+\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',
            r'LEFT\s+JOIN\s+\w+\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)',
            r'RIGHT\s+JOIN\s+\w+\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
        ]
        
        for pattern in join_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                # match格式: (table1, col1, table2, col2)
                if len(match) == 4:
                    table1, col1, table2, col2 = match
                    if table1.lower() == table_info.name.lower():
                        column = col1
                    elif table2.lower() == table_info.name.lower():
                        column = col2
                    else:
                        continue
                    
                    if column in [c.name for c in table_info.columns]:
                        index_def = IndexDefinition(
                            name=f"idx_join_{column}",
                            table_name=table_info.name,
                            columns=[column],
                            index_type=IndexType.BTREE,
                            is_unique=False,
                            is_partial=False,
                            usage_types=[IndexUsage.JOIN]
                        )
                        
                        recommendations.append(IndexRecommendation(
                            definition=index_def,
                            reason=f"连接优化: {column}",
                            estimated_improvement=0.8,
                            creation_cost=0.3,
                            priority="高"
                        ))
        
        return recommendations
    
    def _analyze_search_queries(self, table_info: TableInfo, query: str) -> List[IndexRecommendation]:
        """分析搜索查询"""
        recommendations = []
        
        # 检查LIKE查询
        like_matches = re.findall(r'(\w+)\s+LIKE\s+[\'"]([^\'"\s]+)%[\'"]', query, re.IGNORECASE)
        for column in like_matches:
            if column in [c.name for c in table_info.columns]:
                index_def = IndexDefinition(
                    name=f"idx_search_{column}",
                    table_name=table_info.name,
                    columns=[column],
                    index_type=IndexType.FULLTEXT,
                    is_unique=False,
                    is_partial=False,
                    usage_types=[IndexUsage.SEARCH]
                )
                
                recommendations.append(IndexRecommendation(
                    definition=index_def,
                    reason=f"搜索优化: {column}",
                    estimated_improvement=0.6,
                    creation_cost=0.4,
                    priority="中"
                ))
        
        return recommendations
    
    def generate_index_creation_script(self, recommendations: List[IndexRecommendation]) -> str:
        """生成索引创建脚本"""
        script_lines = ["-- 索引创建脚本", "-- 根据优先级排序", ""]
        
        for i, rec in enumerate(recommendations, 1):
            script_lines.append(f"-- 索引 {i}: {rec.reason}")
            script_lines.append(f"-- 预期改进: {rec.estimated_improvement:.1%}")
            script_lines.append(f"-- 创建成本: {rec.creation_cost:.1%}")
            script_lines.append(f"-- 优先级: {rec.priority}")
            
            index_def = rec.definition
            
            # 生成CREATE INDEX语句
            columns_str = ", ".join(index_def.columns)
            
            if index_def.is_unique:
                create_stmt = f"CREATE UNIQUE INDEX {index_def.name}"
            else:
                create_stmt = f"CREATE INDEX {index_def.name}"
            
            create_stmt += f" ON {index_def.table_name} ({columns_str})"
            
            if index_def.is_partial and index_def.where_condition:
                create_stmt += f" WHERE {index_def.where_condition}"
            
            create_stmt += ";"
            
            script_lines.append(create_stmt)
            script_lines.append("")
        
        return "\n".join(script_lines)

# 使用示例
def main():
    print("=== 索引设计器 ===")
    
    # 创建表信息
    table_info = TableInfo(
        name="orders",
        row_count=1000000,
        columns=[
            ColumnInfo("id", "bigint", False, True, 1000000, 1.0, 8),
            ColumnInfo("customer_id", "bigint", False, False, 50000, 0.05, 8),
            ColumnInfo("order_date", "datetime", False, False, 365, 0.000365, 8),
            ColumnInfo("status", "varchar", False, False, 5, 0.000005, 10),
            ColumnInfo("total_amount", "decimal", False, False, 10000, 0.01, 12),
            ColumnInfo("product_category", "varchar", True, False, 50, 0.00005, 20),
        ],
        primary_key=["id"],
        foreign_keys={"customer_id": "customers"}
    )
    
    # 查询模式
    query_patterns = [
        "SELECT * FROM orders WHERE customer_id = 12345",
        "SELECT * FROM orders WHERE order_date BETWEEN '2023-01-01' AND '2023-12-31'",
        "SELECT * FROM orders WHERE status = 'completed' ORDER BY order_date DESC",
        "SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id",
        "SELECT o.* FROM orders o JOIN customers c ON o.customer_id = c.id",
        "SELECT * FROM orders WHERE product_category LIKE 'electronics%'"
    ]
    
    # 创建索引设计器
    designer = IndexDesigner()
    
    # 分析并推荐索引
    recommendations = designer.analyze_table_and_recommend_indexes(table_info, query_patterns)
    
    print(f"为表 {table_info.name} 推荐的索引:")
    print(f"表行数: {table_info.row_count:,}")
    print(f"查询模式数: {len(query_patterns)}")
    print(f"推荐索引数: {len(recommendations)}")
    
    print("\n=== 索引推荐详情 ===")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec.definition.name}")
        print(f"   列: {', '.join(rec.definition.columns)}")
        print(f"   类型: {rec.definition.index_type.value}")
        print(f"   唯一: {'是' if rec.definition.is_unique else '否'}")
        print(f"   原因: {rec.reason}")
        print(f"   预期改进: {rec.estimated_improvement:.1%}")
        print(f"   创建成本: {rec.creation_cost:.1%}")
        print(f"   优先级: {rec.priority}")
    
    # 生成创建脚本
    print("\n=== 索引创建脚本 ===")
    script = designer.generate_index_creation_script(recommendations)
    print(script)

if __name__ == '__main__':
    main()
```

## SQL优化最佳实践

### 查询设计原则
1. **避免SELECT ***: 只查询需要的列，减少数据传输
2. **合理使用WHERE**: 有效的过滤条件减少结果集
3. **优化JOIN**: 使用合适的连接类型和顺序
4. **控制子查询**: 避免过度嵌套，考虑使用JOIN
5. **使用参数化**: 防止SQL注入，提高执行效率

### 索引设计策略
1. **选择合适的列**: 高选择性、频繁查询的列
2. **复合索引设计**: 考虑查询顺序和列基数
3. **避免过度索引**: 平衡查询性能和写入成本
4. **定期维护**: 重建碎片化索引，更新统计信息
5. **监控使用情况**: 识别未使用和冗余索引

### 性能监控方法
1. **执行计划分析**: 理解查询执行路径
2. **慢查询日志**: 识别和优化性能问题
3. **性能计数器**: 监控数据库资源使用
4. **查询分析工具**: 使用专业工具分析性能
5. **基准测试**: 建立性能基准和回归测试

### 数据库配置优化
1. **内存配置**: 合理分配缓冲池和缓存
2. **连接池设置**: 优化连接数和超时设置
3. **存储引擎选择**: 根据场景选择合适引擎
4. **日志配置**: 平衡安全性和性能
5. **参数调优**: 根据工作负载调整参数

## 相关技能

- **nosql-databases** - NoSQL数据库应用
- **backup-recovery** - 备份与恢复
- **migration-validator** - 迁移验证
- **transaction-management** - 事务管理
