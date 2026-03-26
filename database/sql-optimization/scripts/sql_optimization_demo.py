#!/usr/bin/env python3
"""
SQL优化演示 - 实现查询优化、索引策略和性能调优
"""

import sqlite3
import time
import random
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import statistics

class QueryType(Enum):
    """查询类型"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class OptimizationType(Enum):
    """优化类型"""
    INDEX = "index"
    QUERY_REWRITE = "query_rewrite"
    PARTITIONING = "partitioning"
    CACHING = "caching"

@dataclass
class QueryPlan:
    """查询执行计划"""
    query: str
    execution_time: float
    rows_examined: int
    rows_returned: int
    index_used: Optional[str]
    optimization_applied: List[str]
    
@dataclass
class IndexInfo:
    """索引信息"""
    name: str
    table: str
    columns: List[str]
    index_type: str
    cardinality: int
    is_unique: bool
    is_primary: bool

@dataclass
class PerformanceMetrics:
    """性能指标"""
    query_count: int
    avg_execution_time: float
    min_execution_time: float
    max_execution_time: float
    total_execution_time: float
    rows_processed: int

class SQLAnalyzer:
    """SQL分析器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.query_history: List[QueryPlan] = []
        self.indexes: Dict[str, IndexInfo] = {}
    
    def connect(self):
        """连接数据库"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        # 启用查询计划分析
        self.connection.execute("PRAGMA optimize")
    
    def disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[dict]:
        """执行查询并记录性能"""
        start_time = time.time()
        
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # 获取查询计划
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        cursor.execute(explain_query)
        plan_info = cursor.fetchall()
        
        # 获取结果
        if query.strip().upper().startswith("SELECT"):
            results = [dict(row) for row in cursor.fetchall()]
        else:
            self.connection.commit()
            results = [{"affected_rows": cursor.rowcount}]
        
        execution_time = time.time() - start_time
        
        # 分析查询计划
        index_used = None
        for row in plan_info:
            if "USING INDEX" in str(row):
                index_used = str(row).split("USING INDEX")[1].strip()
                break
        
        # 记录查询计划
        query_plan = QueryPlan(
            query=query,
            execution_time=execution_time,
            rows_examined=len(plan_info),
            rows_returned=len(results),
            index_used=index_used,
            optimization_applied=[]
        )
        
        self.query_history.append(query_plan)
        
        return results
    
    def analyze_query_performance(self) -> PerformanceMetrics:
        """分析查询性能"""
        if not self.query_history:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0)
        
        execution_times = [qp.execution_time for qp in self.query_history]
        
        return PerformanceMetrics(
            query_count=len(self.query_history),
            avg_execution_time=statistics.mean(execution_times),
            min_execution_time=min(execution_times),
            max_execution_time=max(execution_times),
            total_execution_time=sum(execution_times),
            rows_processed=sum(qp.rows_returned for qp in self.query_history)
        )
    
    def get_slow_queries(self, threshold: float = 0.1) -> List[QueryPlan]:
        """获取慢查询"""
        return [qp for qp in self.query_history if qp.execution_time > threshold]

class IndexOptimizer:
    """索引优化器"""
    
    def __init__(self, analyzer: SQLAnalyzer):
        self.analyzer = analyzer
        self.recommendations: List[dict] = []
    
    def analyze_missing_indexes(self) -> List[dict]:
        """分析缺失的索引"""
        recommendations = []
        
        # 获取所有表
        cursor = self.analyzer.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            
            # 分析查询历史，找出常用的WHERE条件
            where_columns = self._analyze_where_columns(table)
            
            # 推荐索引
            for column in where_columns:
                if column in columns:
                    recommendation = {
                        "table": table,
                        "column": column,
                        "index_type": "btree",
                        "reason": "Frequently used in WHERE clause",
                        "estimated_improvement": "20-50%"
                    }
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_where_columns(self, table: str) -> List[str]:
        """分析WHERE条件中使用的列"""
        columns = set()
        
        for qp in self.analyzer.query_history:
            if table in qp.query.upper():
                # 简化的WHERE条件解析
                query_upper = qp.query.upper()
                if "WHERE" in query_upper:
                    where_part = query_upper.split("WHERE")[1].split("ORDER")[0].split("GROUP")[0]
                    for column in self.analyzer.get_table_columns(table):
                        if column.upper() in where_part:
                            columns.add(column)
        
        return list(columns)
    
    def create_index(self, table: str, columns: List[str], index_name: str = None) -> bool:
        """创建索引"""
        if not index_name:
            index_name = f"idx_{table}_{'_'.join(columns)}"
        
        try:
            cursor = self.analyzer.connection.cursor()
            create_sql = f"CREATE INDEX {index_name} ON {table} ({', '.join(columns)})"
            cursor.execute(create_sql)
            self.analyzer.connection.commit()
            
            # 记录索引信息
            index_info = IndexInfo(
                name=index_name,
                table=table,
                columns=columns,
                index_type="btree",
                cardinality=0,  # SQLite不提供基数统计
                is_unique=False,
                is_primary=False
            )
            
            self.analyzer.indexes[index_name] = index_info
            
            print(f"✅ 创建索引: {index_name}")
            return True
            
        except Exception as e:
            print(f"❌ 创建索引失败: {e}")
            return False
    
    def drop_index(self, index_name: str) -> bool:
        """删除索引"""
        try:
            cursor = self.analyzer.connection.cursor()
            cursor.execute(f"DROP INDEX {index_name}")
            self.analyzer.connection.commit()
            
            if index_name in self.analyzer.indexes:
                del self.analyzer.indexes[index_name]
            
            print(f"✅ 删除索引: {index_name}")
            return True
            
        except Exception as e:
            print(f"❌ 删除索引失败: {e}")
            return False

class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self, analyzer: SQLAnalyzer):
        self.analyzer = analyzer
        self.optimization_rules = []
    
    def optimize_query(self, original_query: str) -> Tuple[str, List[str]]:
        """优化查询"""
        optimized_query = original_query
        optimizations_applied = []
        
        # 应用优化规则
        optimizations_applied.extend(self._apply_select_optimizations(optimized_query))
        optimizations_applied.extend(self._apply_join_optimizations(optimized_query))
        optimizations_applied.extend(self._apply_where_optimizations(optimized_query))
        optimizations_applied.extend(self._apply_order_optimizations(optimized_query))
        
        return optimized_query, optimizations_applied
    
    def _apply_select_optimizations(self, query: str) -> List[str]:
        """应用SELECT优化"""
        optimizations = []
        
        # 避免 SELECT *
        if "SELECT *" in query.upper():
            optimizations.append("Replace SELECT * with specific columns")
        
        # 使用 LIMIT 限制结果集
        if "LIMIT" not in query.upper() and "SELECT" in query.upper():
            optimizations.append("Consider adding LIMIT for large result sets")
        
        return optimizations
    
    def _apply_join_optimizations(self, query: str) -> List[str]:
        """应用JOIN优化"""
        optimizations = []
        
        # 检查JOIN条件
        if "JOIN" in query.upper():
            optimizations.append("Ensure JOIN columns are indexed")
            optimizations.append("Consider using INNER JOIN instead of OUTER JOIN when possible")
        
        return optimizations
    
    def _apply_where_optimizations(self, query: str) -> List[str]:
        """应用WHERE优化"""
        optimizations = []
        
        # 检查函数使用
        if "WHERE" in query.upper():
            where_part = query.upper().split("WHERE")[1].split("ORDER")[0].split("GROUP")[0]
            
            # 避免在WHERE中使用函数
            if any(func in where_part for func in ["UPPER(", "LOWER(", "SUBSTR("]):
                optimizations.append("Avoid functions in WHERE clause")
            
            # 使用索引友好的操作符
            if "LIKE" in where_part and "%" in where_part:
                optimizations.append("Leading wildcards in LIKE prevent index usage")
        
        return optimizations
    
    def _apply_order_optimizations(self, query: str) -> List[str]:
        """应用ORDER BY优化"""
        optimizations = []
        
        if "ORDER BY" in query.upper():
            optimizations.append("Consider indexing ORDER BY columns")
            optimizations.append("Limit ORDER BY results with LIMIT")
        
        return optimizations

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, analyzer: SQLAnalyzer):
        self.analyzer = analyzer
        self.baseline_metrics: Optional[PerformanceMetrics] = None
    
    def set_baseline(self):
        """设置性能基线"""
        self.baseline_metrics = self.analyzer.analyze_query_performance()
        print("📊 性能基线已设置")
    
    def compare_performance(self) -> dict:
        """比较当前性能与基线"""
        if not self.baseline_metrics:
            return {"error": "No baseline set"}
        
        current_metrics = self.analyzer.analyze_query_performance()
        
        improvement = {
            "query_count_change": current_metrics.query_count - self.baseline_metrics.query_count,
            "avg_time_change": current_metrics.avg_execution_time - self.baseline_metrics.avg_execution_time,
            "total_time_change": current_metrics.total_execution_time - self.baseline_metrics.total_execution_time,
            "improvement_percentage": 0
        }
        
        if self.baseline_metrics.total_execution_time > 0:
            improvement["improvement_percentage"] = (
                (self.baseline_metrics.total_execution_time - current_metrics.total_execution_time) / 
                self.baseline_metrics.total_execution_time * 100
            )
        
        return improvement
    
    def generate_report(self) -> str:
        """生成性能报告"""
        metrics = self.analyzer.analyze_query_performance()
        slow_queries = self.analyzer.get_slow_queries()
        
        report = f"""
📊 SQL性能报告
{'='*50}

查询统计:
- 总查询数: {metrics.query_count}
- 平均执行时间: {metrics.avg_execution_time:.4f}s
- 最快执行时间: {metrics.min_execution_time:.4f}s
- 最慢执行时间: {metrics.max_execution_time:.4f}s
- 总执行时间: {metrics.total_execution_time:.4f}s
- 处理行数: {metrics.rows_processed}

慢查询 (>{0.1}s):
"""
        
        for i, query in enumerate(slow_queries[:5], 1):
            report += f"{i}. 执行时间: {query.execution_time:.4f}s\n"
            report += f"   查询: {query.query[:100]}...\n"
            report += f"   返回行数: {query.rows_returned}\n"
            report += f"   使用索引: {query.index_used or 'None'}\n\n"
        
        # 索引信息
        if self.analyzer.indexes:
            report += "当前索引:\n"
            for name, index in self.analyzer.indexes.items():
                report += f"- {name}: {index.table}({', '.join(index.columns)})\n"
        
        return report

def create_sample_database():
    """创建示例数据库"""
    db_path = "performance_test.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            age INTEGER,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_name TEXT,
            amount REAL,
            status TEXT,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 插入大量测试数据
    print("🔄 生成测试数据...")
    cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "西安"]
    products = [
        ("笔记本电脑", "电子产品", 5999.99, 100),
        ("手机", "电子产品", 2999.99, 200),
        ("平板", "电子产品", 1999.99, 150),
        ("耳机", "电子产品", 299.99, 300),
        ("键盘", "电子产品", 199.99, 250),
        ("鼠标", "电子产品", 99.99, 400),
        ("显示器", "电子产品", 1299.99, 80),
        ("台灯", "家居用品", 199.99, 120)
    ]
    
    # 插入用户数据
    users_data = []
    for i in range(10000):
        users_data.append((
            f"用户{i}",
            f"user{i}@example.com",
            random.randint(18, 65),
            random.choice(cities)
        ))
    
    cursor.executemany(
        "INSERT INTO users (name, email, age, city) VALUES (?, ?, ?, ?)",
        users_data
    )
    
    # 插入产品数据
    cursor.executemany(
        "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
        products
    )
    
    # 插入订单数据
    orders_data = []
    for i in range(50000):
        orders_data.append((
            random.randint(1, 10000),
            random.choice(products)[0],
            random.uniform(10, 1000),
            random.choice(["pending", "completed", "cancelled"])
        ))
    
    cursor.executemany(
        "INSERT INTO orders (user_id, product_name, amount, status) VALUES (?, ?, ?, ?)",
        orders_data
    )
    
    conn.commit()
    conn.close()
    
    print(f"✅ 示例数据库创建完成: {db_path}")
    return db_path

async def demonstrate_query_analysis():
    """演示查询分析"""
    print("\n🔍 查询分析演示")
    print("=" * 50)
    
    # 创建数据库
    db_path = create_sample_database()
    
    # 创建分析器
    analyzer = SQLAnalyzer(db_path)
    analyzer.connect()
    
    # 执行各种查询
    queries = [
        "SELECT * FROM users WHERE age > 30",
        "SELECT * FROM users WHERE city = '北京'",
        "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id",
        "SELECT product_name, COUNT(*) as count FROM orders GROUP BY product_name",
        "SELECT * FROM users WHERE name LIKE '用户%'",
        "SELECT * FROM orders WHERE amount > 500 ORDER BY amount DESC LIMIT 10"
    ]
    
    print("🔄 执行测试查询...")
    for query in queries:
        results = analyzer.execute_query(query)
        print(f"查询: {query[:50]}...")
        print(f"结果数: {len(results)}")
    
    # 分析性能
    metrics = analyzer.analyze_query_performance()
    print(f"\n📊 性能指标:")
    print(f"  查询数量: {metrics.query_count}")
    print(f"  平均执行时间: {metrics.avg_execution_time:.4f}s")
    print(f"  总执行时间: {metrics.total_execution_time:.4f}s")
    
    analyzer.disconnect()

async def demonstrate_index_optimization():
    """演示索引优化"""
    print("\n🚀 索引优化演示")
    print("=" * 50)
    
    db_path = "performance_test.db"
    analyzer = SQLAnalyzer(db_path)
    analyzer.connect()
    
    # 创建索引优化器
    optimizer = IndexOptimizer(analyzer)
    
    # 设置性能基线
    monitor = PerformanceMonitor(analyzer)
    
    # 测试无索引性能
    print("\n📈 测试无索引性能...")
    test_query = "SELECT * FROM users WHERE city = '北京'"
    
    # 执行多次查询取平均值
    for _ in range(10):
        analyzer.execute_query(test_query)
    
    monitor.set_baseline()
    
    # 创建索引
    print("\n🔧 创建索引...")
    optimizer.create_index("users", ["city"])
    
    # 测试有索引性能
    print("\n📈 测试有索引性能...")
    for _ in range(10):
        analyzer.execute_query(test_query)
    
    # 比较性能
    improvement = monitor.compare_performance()
    print(f"\n📊 性能改进:")
    print(f"  平均时间变化: {improvement['avg_time_change']:.4f}s")
    print(f"  改进百分比: {improvement['improvement_percentage']:.2f}%")
    
    # 分析缺失索引
    recommendations = optimizer.analyze_missing_indexes()
    print(f"\n💡 索引建议:")
    for rec in recommendations[:5]:
        print(f"  表 {rec['table']}: {rec['column']} - {rec['reason']}")
    
    analyzer.disconnect()

async def demonstrate_query_optimization():
    """演示查询优化"""
    print("\n⚡ 查询优化演示")
    print("=" * 50)
    
    db_path = "performance_test.db"
    analyzer = SQLAnalyzer(db_path)
    analyzer.connect()
    
    # 创建查询优化器
    optimizer = QueryOptimizer(analyzer)
    
    # 测试查询优化
    test_queries = [
        "SELECT * FROM users WHERE age > 30",
        "SELECT * FROM users WHERE UPPER(name) LIKE 'USER%'",
        "SELECT u.*, o.* FROM users u JOIN orders o ON u.id = o.user_id WHERE u.city = '北京'",
        "SELECT * FROM orders ORDER BY amount DESC"
    ]
    
    for query in test_queries:
        print(f"\n🔍 原始查询: {query}")
        
        # 优化查询
        optimized_query, optimizations = optimizer.optimize_query(query)
        
        print(f"🚀 优化建议:")
        for opt in optimizations:
            print(f"  - {opt}")
        
        # 性能测试
        start_time = time.time()
        analyzer.execute_query(query)
        original_time = time.time() - start_time
        
        start_time = time.time()
        analyzer.execute_query(optimized_query)
        optimized_time = time.time() - start_time
        
        print(f"⏱️  性能对比:")
        print(f"  原始查询: {original_time:.4f}s")
        print(f"  优化查询: {optimized_time:.4f}s")
    
    analyzer.disconnect()

async def demonstrate_performance_monitoring():
    """演示性能监控"""
    print("\n📊 性能监控演示")
    print("=" * 50)
    
    db_path = "performance_test.db"
    analyzer = SQLAnalyzer(db_path)
    analyzer.connect()
    
    # 创建监控器
    monitor = PerformanceMonitor(analyzer)
    
    # 执行一系列查询
    queries = [
        "SELECT COUNT(*) FROM users",
        "SELECT * FROM users LIMIT 100",
        "SELECT * FROM orders WHERE status = 'completed'",
        "SELECT u.name, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id",
        "SELECT * FROM products WHERE price > 1000"
    ]
    
    print("🔄 执行查询序列...")
    for query in queries:
        analyzer.execute_query(query)
    
    # 生成报告
    report = monitor.generate_report()
    print(report)
    
    # 获取慢查询
    slow_queries = analyzer.get_slow_queries(0.05)
    print(f"\n🐌 慢查询分析:")
    for i, query in enumerate(slow_queries[:3], 1):
        print(f"{i}. {query.query}")
        print(f"   执行时间: {query.execution_time:.4f}s")
        print(f"   返回行数: {query.rows_returned}")
    
    analyzer.disconnect()

async def main():
    """主函数"""
    print("⚡ SQL优化演示")
    print("=" * 60)
    
    try:
        await demonstrate_query_analysis()
        await demonstrate_index_optimization()
        await demonstrate_query_optimization()
        await demonstrate_performance_monitoring()
        
        print("\n✅ SQL优化演示完成!")
        print("\n📚 关键概念:")
        print("  - 查询分析: 分析查询执行计划和性能")
        print("  - 索引优化: 创建合适的索引提高查询速度")
        print("  - 查询重写: 优化SQL语句结构")
        print("  - 性能监控: 监控查询性能和慢查询")
        print("  - 执行计划: 分析数据库如何执行查询")
        print("  - 基准测试: 建立性能基线进行对比")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
    finally:
        # 清理临时文件
        import os
        if os.path.exists("performance_test.db"):
            os.remove("performance_test.db")

if __name__ == '__main__':
    asyncio.run(main())
