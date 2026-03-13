---
name: SQL生成器
description: "当生成SQL查询、验证SQL、优化查询或调试SQL错误时，在执行到生产数据库之前验证SQL。"
license: MIT
---

# SQL生成器技能

## 概述
SQL是强大且永久的。无效的SQL会导致数据丢失或损坏。在执行到生产数据库之前彻底测试SQL。

**核心原则**: SQL是永久的。先测试，后执行。

## 何时使用

**始终:**
- 在执行到生产环境之前
- 编写新查询
- 优化慢查询
- 创建迁移
- 调试SQL错误
- 数据库设计

**触发短语:**
- "生成SQL查询"
- "优化这个SQL"
- "验证SQL语法"
- "创建数据库表"
- "生成插入语句"
- "SQL调试"

## SQL生成功能

### 查询生成
- SELECT查询构建
- INSERT语句生成
- UPDATE语句创建
- DELETE语句生成
- 复杂查询组合

### 数据库设计
- 表结构生成
- 索引创建
- 约束定义
- 外键关系
- 视图创建

### SQL优化
- 查询性能分析
- 索引建议
- 执行计划分析
- 慢查询优化
- 资源使用优化

## 常见SQL问题

### SQL注入攻击
```
问题:
SQL注入导致安全漏洞

错误示例:
"SELECT * FROM users WHERE name = '" + userName + "'"

解决方案:
使用参数化查询:
"SELECT * FROM users WHERE name = ?"

或使用ORM框架:
User.objects.filter(name=userName)
```

### 慢查询
```
问题:
查询执行时间过长

错误示例:
SELECT * FROM orders WHERE customer_id IN (
    SELECT id FROM customers WHERE status = 'active'
)

解决方案:
1. 添加索引
2. 使用JOIN替代子查询
3. 优化WHERE条件
4. 分页查询
```

### 死锁问题
```
问题:
并发操作导致死锁

错误示例:
事务1: 锁定表A，然后锁定表B
事务2: 锁定表B，然后锁定表A

解决方案:
1. 统一锁定顺序
2. 减少事务时间
3. 使用乐观锁
4. 设置合理的超时
```

## 代码实现示例

### SQL生成器
```python
import re
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Function
from sqlparse.tokens import Keyword, DML, Name

class SQLOperation(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"

class SQLJoinType(Enum):
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"
    CROSS = "CROSS JOIN"

@dataclass
class SQLColumn:
    """SQL列定义"""
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None
    default_value: Optional[str] = None
    unique: bool = False
    auto_increment: bool = False

@dataclass
class SQLTable:
    """SQL表定义"""
    name: str
    columns: List[SQLColumn]
    indexes: List[Dict[str, Any]] = None
    constraints: List[Dict[str, Any]] = None

@dataclass
class SQLQuery:
    """SQL查询"""
    operation: SQLOperation
    tables: List[str]
    columns: List[str]
    conditions: List[str]
    joins: List[Dict[str, Any]] = None
    group_by: List[str] = None
    having: List[str] = None
    order_by: List[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

class SQLGenerator:
    """SQL生成器"""
    
    def __init__(self):
        self.data_type_mapping = {
            'string': 'VARCHAR(255)',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'bigint': 'BIGINT',
            'decimal': 'DECIMAL(10,2)',
            'float': 'FLOAT',
            'boolean': 'BOOLEAN',
            'date': 'DATE',
            'datetime': 'DATETIME',
            'timestamp': 'TIMESTAMP',
            'json': 'JSON'
        }
    
    def create_table(self, table: SQLTable) -> str:
        """创建建表语句"""
        columns_sql = []
        
        for column in table.columns:
            column_sql = self._build_column_definition(column)
            columns_sql.append(column_sql)
        
        # 添加主键约束
        primary_keys = [col.name for col in table.columns if col.primary_key]
        if len(primary_keys) > 1:
            columns_sql.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
        
        # 添加外键约束
        foreign_keys = [col for col in table.columns if col.foreign_key]
        for fk in foreign_keys:
            columns_sql.append(f"FOREIGN KEY ({fk.name}) REFERENCES {fk.foreign_key}")
        
        # 添加唯一约束
        unique_columns = [col.name for col in table.columns if col.unique]
        if unique_columns:
            columns_sql.append(f"UNIQUE ({', '.join(unique_columns)})")
        
        sql = f"CREATE TABLE {table.name} (\n    "
        sql += ",\n    ".join(columns_sql)
        sql += "\n)"
        
        return sql
    
    def _build_column_definition(self, column: SQLColumn) -> str:
        """构建列定义"""
        sql = f"{column.name} {column.data_type}"
        
        if not column.nullable:
            sql += " NOT NULL"
        
        if column.auto_increment:
            sql += " AUTO_INCREMENT"
        
        if column.default_value is not None:
            sql += f" DEFAULT {column.default_value}"
        
        if column.primary_key and len([col for col in [column] if col.primary_key]) == 1:
            sql += " PRIMARY KEY"
        
        return sql
    
    def generate_insert(self, table_name: str, data: Dict[str, Any]) -> str:
        """生成INSERT语句"""
        columns = list(data.keys())
        values = list(data.values())
        
        # 处理值
        formatted_values = []
        for value in values:
            if isinstance(value, str):
                formatted_values.append(f"'{value.replace("'", "''")}'")
            elif isinstance(value, bool):
                formatted_values.append("TRUE" if value else "FALSE")
            elif value is None:
                formatted_values.append("NULL")
            else:
                formatted_values.append(str(value))
        
        sql = f"INSERT INTO {table_name} ({', '.join(columns)})\n"
        sql += f"VALUES ({', '.join(formatted_values)})"
        
        return sql
    
    def generate_update(self, table_name: str, data: Dict[str, Any], 
                       conditions: Dict[str, Any]) -> str:
        """生成UPDATE语句"""
        set_clauses = []
        for column, value in data.items():
            if isinstance(value, str):
                set_clauses.append(f"{column} = '{value.replace("'", "''")}'")
            elif isinstance(value, bool):
                set_clauses.append(f"{column} = {('TRUE' if value else 'FALSE')}")
            elif value is None:
                set_clauses.append(f"{column} = NULL")
            else:
                set_clauses.append(f"{column} = {value}")
        
        where_clauses = []
        for column, value in conditions.items():
            if isinstance(value, str):
                where_clauses.append(f"{column} = '{value.replace("'", "''")}'")
            elif isinstance(value, bool):
                where_clauses.append(f"{column} = {('TRUE' if value else 'FALSE')}")
            elif value is None:
                where_clauses.append(f"{column} IS NULL")
            else:
                where_clauses.append(f"{column} = {value}")
        
        sql = f"UPDATE {table_name}\nSET {', '.join(set_clauses)}\n"
        if where_clauses:
            sql += f"WHERE {' AND '.join(where_clauses)}"
        
        return sql
    
    def generate_select(self, query: SQLQuery) -> str:
        """生成SELECT语句"""
        # SELECT子句
        if query.columns == ['*']:
            select_clause = "*"
        else:
            select_clause = ', '.join(query.columns)
        
        sql = f"SELECT {select_clause}\nFROM {', '.join(query.tables)}"
        
        # JOIN子句
        if query.joins:
            for join in query.joins:
                join_type = join.get('type', SQLJoinType.INNER.value)
                table = join['table']
                condition = join['condition']
                sql += f"\n{join_type} {table} ON {condition}"
        
        # WHERE子句
        if query.conditions:
            sql += f"\nWHERE {' AND '.join(query.conditions)}"
        
        # GROUP BY子句
        if query.group_by:
            sql += f"\nGROUP BY {', '.join(query.group_by)}"
        
        # HAVING子句
        if query.having:
            sql += f"\nHAVING {' AND '.join(query.having)}"
        
        # ORDER BY子句
        if query.order_by:
            sql += f"\nORDER BY {', '.join(query.order_by)}"
        
        # LIMIT和OFFSET
        if query.limit is not None:
            sql += f"\nLIMIT {query.limit}"
            if query.offset is not None:
                sql += f" OFFSET {query.offset}"
        
        return sql
    
    def generate_delete(self, table_name: str, conditions: Dict[str, Any]) -> str:
        """生成DELETE语句"""
        where_clauses = []
        for column, value in conditions.items():
            if isinstance(value, str):
                where_clauses.append(f"{column} = '{value.replace("'", "''")}'")
            elif isinstance(value, bool):
                where_clauses.append(f"{column} = {('TRUE' if value else 'FALSE')}")
            elif value is None:
                where_clauses.append(f"{column} IS NULL")
            else:
                where_clauses.append(f"{column} = {value}")
        
        sql = f"DELETE FROM {table_name}"
        if where_clauses:
            sql += f"\nWHERE {' AND '.join(where_clauses)}"
        
        return sql
    
    def create_index(self, table_name: str, index_name: str, 
                    columns: List[str], unique: bool = False) -> str:
        """创建索引语句"""
        index_type = "UNIQUE INDEX" if unique else "INDEX"
        sql = f"CREATE {index_type} {index_name} ON {table_name} ({', '.join(columns)})"
        return sql
    
    def parse_table_from_dict(self, table_dict: Dict[str, Any]) -> SQLTable:
        """从字典解析表结构"""
        columns = []
        
        for col_name, col_info in table_dict['columns'].items():
            column = SQLColumn(
                name=col_name,
                data_type=col_info['type'],
                nullable=col_info.get('nullable', True),
                primary_key=col_info.get('primary_key', False),
                foreign_key=col_info.get('foreign_key'),
                default_value=col_info.get('default'),
                unique=col_info.get('unique', False),
                auto_increment=col_info.get('auto_increment', False)
            )
            columns.append(column)
        
        return SQLTable(
            name=table_dict['name'],
            columns=columns,
            indexes=table_dict.get('indexes', []),
            constraints=table_dict.get('constraints', [])
        )
    
    def generate_migration_sql(self, old_table: SQLTable, new_table: SQLTable) -> List[str]:
        """生成迁移SQL"""
        migrations = []
        
        # 检查列的增删改
        old_columns = {col.name: col for col in old_table.columns}
        new_columns = {col.name: col for col in new_table.columns}
        
        # 新增列
        for col_name, column in new_columns.items():
            if col_name not in old_columns:
                alter_sql = f"ALTER TABLE {new_table.name} ADD COLUMN {self._build_column_definition(column)}"
                migrations.append(alter_sql)
        
        # 删除列
        for col_name in old_columns:
            if col_name not in new_columns:
                alter_sql = f"ALTER TABLE {new_table.name} DROP COLUMN {col_name}"
                migrations.append(alter_sql)
        
        # 修改列
        for col_name, new_column in new_columns.items():
            if col_name in old_columns:
                old_column = old_columns[col_name]
                if old_column.data_type != new_column.data_type:
                    alter_sql = f"ALTER TABLE {new_table.name} ALTER COLUMN {col_name} TYPE {new_column.data_type}"
                    migrations.append(alter_sql)
        
        return migrations

### SQL查询构建器
```python
class QueryBuilder:
    """SQL查询构建器"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置查询构建器"""
        self._operation = None
        self._tables = []
        self._columns = []
        self._conditions = []
        self._joins = []
        self._group_by = []
        self._having = []
        self._order_by = []
        self._limit = None
        self._offset = None
        return self
    
    def select(self, *columns):
        """SELECT子句"""
        self._operation = SQLOperation.SELECT
        self._columns = list(columns) if columns else ['*']
        return self
    
    def from_table(self, *tables):
        """FROM子句"""
        self._tables = list(tables)
        return self
    
    def where(self, condition):
        """WHERE子句"""
        self._conditions.append(condition)
        return self
    
    def where_in(self, column, values):
        """WHERE IN子句"""
        if isinstance(values, (list, tuple)):
            formatted_values = []
            for v in values:
                if isinstance(v, str):
                    formatted_values.append(f"'{v}'")
                else:
                    formatted_values.append(str(v))
            condition = f"{column} IN ({', '.join(formatted_values)})"
        else:
            condition = f"{column} IN ({values})"
        
        self._conditions.append(condition)
        return self
    
    def where_like(self, column, pattern):
        """WHERE LIKE子句"""
        self._conditions.append(f"{column} LIKE '{pattern}'")
        return self
    
    def join(self, table, condition, join_type=SQLJoinType.INNER):
        """JOIN子句"""
        self._joins.append({
            'type': join_type.value,
            'table': table,
            'condition': condition
        })
        return self
    
    def left_join(self, table, condition):
        """LEFT JOIN子句"""
        return self.join(table, condition, SQLJoinType.LEFT)
    
    def right_join(self, table, condition):
        """RIGHT JOIN子句"""
        return self.join(table, condition, SQLJoinType.RIGHT)
    
    def group_by(self, *columns):
        """GROUP BY子句"""
        self._group_by = list(columns)
        return self
    
    def having(self, condition):
        """HAVING子句"""
        self._having.append(condition)
        return self
    
    def order_by(self, *columns):
        """ORDER BY子句"""
        self._order_by = list(columns)
        return self
    
    def order_by_desc(self, *columns):
        """ORDER BY DESC子句"""
        self._order_by = [f"{col} DESC" for col in columns]
        return self
    
    def limit(self, count):
        """LIMIT子句"""
        self._limit = count
        return self
    
    def offset(self, count):
        """OFFSET子句"""
        self._offset = count
        return self
    
    def build(self) -> str:
        """构建SQL查询"""
        if not self._operation or not self._tables:
            raise ValueError("必须指定操作和表名")
        
        query = SQLQuery(
            operation=self._operation,
            tables=self._tables,
            columns=self._columns,
            conditions=self._conditions,
            joins=self._joins,
            group_by=self._group_by,
            having=self._having,
            order_by=self._order_by,
            limit=self._limit,
            offset=self._offset
        )
        
        generator = SQLGenerator()
        return generator.generate_select(query)
    
    def count(self):
        """COUNT查询"""
        self._columns = ["COUNT(*)"]
        return self
    
    def distinct(self):
        """DISTINCT查询"""
        self._columns = [f"DISTINCT {col}" for col in self._columns]
        return self

# 使用示例
def main():
    generator = SQLGenerator()
    
    # 创建表
    users_table = SQLTable(
        name="users",
        columns=[
            SQLColumn("id", "INTEGER", primary_key=True, auto_increment=True),
            SQLColumn("username", "VARCHAR(50)", unique=True, nullable=False),
            SQLColumn("email", "VARCHAR(100)", unique=True, nullable=False),
            SQLColumn("created_at", "TIMESTAMP", default_value="CURRENT_TIMESTAMP")
        ]
    )
    
    create_sql = generator.create_table(users_table)
    print("=== 建表语句 ===")
    print(create_sql)
    
    # 插入数据
    user_data = {
        "username": "john_doe",
        "email": "john@example.com"
    }
    
    insert_sql = generator.generate_insert("users", user_data)
    print("\n=== 插入语句 ===")
    print(insert_sql)
    
    # 查询构建器
    query_builder = QueryBuilder()
    query = (query_builder
             .select("username", "email", "created_at")
             .from_table("users")
             .where("email LIKE '%@example.com'")
             .order_by_desc("created_at")
             .limit(10)
             .build())
    
    print("\n=== 查询语句 ===")
    print(query)
    
    # 更新语句
    update_sql = generator.generate_update(
        "users", 
        {"username": "john_doe_updated"}, 
        {"id": 1}
    )
    print("\n=== 更新语句 ===")
    print(update_sql)

if __name__ == "__main__":
    main()
```

### SQL验证器
```python
class SQLValidator:
    """SQL验证器"""
    
    def __init__(self):
        self.reserved_keywords = {
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
            'CREATE', 'DROP', 'ALTER', 'INDEX', 'TABLE', 'DATABASE',
            'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
            'GROUP', 'BY', 'HAVING', 'ORDER', 'LIMIT', 'OFFSET',
            'UNION', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'
        }
    
    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """验证SQL语法"""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        try:
            # 使用sqlparse解析SQL
            parsed = sqlparse.parse(sql)
            
            if not parsed:
                result['valid'] = False
                result['errors'].append("无法解析SQL语句")
                return result
            
            for statement in parsed:
                self._validate_statement(statement, result)
            
            # 检查SQL注入风险
            self._check_injection_risks(sql, result)
            
            # 性能建议
            self._performance_analysis(sql, result)
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"SQL解析错误: {str(e)}")
        
        return result
    
    def _validate_statement(self, statement, result):
        """验证单个SQL语句"""
        tokens = list(statement.flatten())
        
        # 检查基本语法
        if not any(token.ttype is DML for token in tokens):
            result['warnings'].append("未检测到DML操作")
        
        # 检查表名和列名
        identifiers = [token for token in tokens if isinstance(token, Identifier)]
        for identifier in identifiers:
            if identifier.get_real_name() in self.reserved_keywords:
                result['warnings'].append(f"标识符 '{identifier}' 是保留关键字")
    
    def _check_injection_risks(self, sql: str, result):
        """检查SQL注入风险"""
        # 检查字符串拼接
        if "'" in sql and "+" in sql:
            result['warnings'].append("检测到可能的字符串拼接，存在SQL注入风险")
        
        # 检查动态SQL
        patterns = [
            r'\$\{.*?\}',  # ${variable}
            r'#\{.*?\}',   # #{variable}
            r'%s.*?%'      # %s formatting
        ]
        
        for pattern in patterns:
            if re.search(pattern, sql):
                result['warnings'].append("检测到动态SQL，建议使用参数化查询")
    
    def _performance_analysis(self, sql: str, result):
        """性能分析"""
        # 检查SELECT *
        if "SELECT *" in sql.upper():
            result['suggestions'].append("避免使用SELECT *，明确指定需要的列")
        
        # 检查缺少WHERE条件
        upper_sql = sql.upper()
        if "UPDATE" in upper_sql or "DELETE" in upper_sql:
            if "WHERE" not in upper_sql:
                result['warnings'].append("UPDATE/DELETE语句缺少WHERE条件")
        
        # 检查子查询
        if "SELECT" in upper_sql and upper_sql.count("SELECT") > 1:
            result['suggestions'].append("考虑使用JOIN替代子查询以提高性能")
    
    def format_sql(self, sql: str) -> str:
        """格式化SQL"""
        try:
            formatted = sqlparse.format(sql, reindent=True, keyword_case='upper')
            return formatted
        except:
            return sql

# 使用示例
def main():
    validator = SQLValidator()
    
    # 测试SQL
    test_sql = "SELECT * FROM users WHERE name = '" + user_input + "'"
    
    result = validator.validate_sql(test_sql)
    
    print("=== SQL验证结果 ===")
    print(f"有效: {result['valid']}")
    
    if result['errors']:
        print("\n错误:")
        for error in result['errors']:
            print(f"  - {error}")
    
    if result['warnings']:
        print("\n警告:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    if result['suggestions']:
        print("\n建议:")
        for suggestion in result['suggestions']:
            print(f"  - {suggestion}")

if __name__ == "__main__":
    main()
```

## SQL最佳实践

### 查询优化
1. **索引使用**: 为常用查询字段创建索引
2. **避免SELECT ***: 只查询需要的列
3. **分页查询**: 使用LIMIT和OFFSET
4. **批量操作**: 减少数据库往返次数

### 安全性
1. **参数化查询**: 防止SQL注入
2. **最小权限**: 应用程序使用最小必要权限
3. **数据加密**: 敏感数据加密存储
4. **审计日志**: 记录重要操作

### 数据库设计
1. **规范化**: 遵循数据库范式
2. **数据类型**: 选择合适的数据类型
3. **约束定义**: 使用外键和约束
4. **命名规范**: 统一的命名约定

## 相关技能

- **sql-optimizer** - SQL优化
- **database-design** - 数据库设计
- **data-migration** - 数据迁移
- **performance-tuning** - 性能调优
