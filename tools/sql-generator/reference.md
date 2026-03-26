# SQL Generator 技术参考

## 概述

SQL Generator 是一个专门用于生成 SQL 查询语句的工具，支持多种数据库类型、查询模式优化、代码生成和数据库设计功能。

## 核心功能

### 查询生成
- **基础查询**: SELECT、INSERT、UPDATE、DELETE 语句生成
- **复杂查询**: JOIN、子查询、聚合函数、窗口函数
- **条件构建**: WHERE、HAVING、ORDER BY、GROUP BY 子句
- **动态查询**: 参数化查询、条件动态组装

### 数据库支持
- **关系型数据库**: MySQL、PostgreSQL、Oracle、SQL Server
- **NoSQL 数据库**: MongoDB、Cassandra、Redis 查询
- **云数据库**: AWS Aurora、Google Cloud SQL、Azure SQL
- **嵌入式数据库**: SQLite、H2、Derby

### 代码生成
- **ORM 代码**: 生成实体类、DAO、Repository 代码
- **API 接口**: 生成 REST API、GraphQL 接口
- **数据库脚本**: 生成建表、索引、约束脚本
- **测试代码**: 生成单元测试、集成测试代码

## 配置指南

### 基础配置
```json
{
  "sql-generator": {
    "database": {
      "type": "mysql",
      "version": "8.0",
      "charset": "utf8mb4",
      "collation": "utf8mb4_unicode_ci"
    },
    "connection": {
      "host": "localhost",
      "port": 3306,
      "database": "myapp",
      "username": "user",
      "password": "password"
    },
    "generation": {
      "table-prefix": "tbl_",
      "naming-convention": "snake_case",
      "include-comments": true,
      "include-indices": true
    }
  }
}
```

### 高级配置
```json
{
  "sql-generator": {
    "advanced": {
      "query-optimization": {
        "enable-index-hints": true,
        "enable-query-cache": true,
        "enable-explain-plan": true,
        "max-join-depth": 5
      },
      "code-generation": {
        "framework": "spring-boot",
        "package-name": "com.example.myapp",
        "base-class": "BaseEntity",
        "generate-validation": true,
        "generate-auditing": true
      },
      "templates": {
        "entity-template": "./templates/entity.java.hbs",
        "repository-template": "./templates/repository.java.hbs",
        "service-template": "./templates/service.java.hbs"
      }
    }
  }
}
```

## API 参考

### 查询生成器
```python
class SQLGenerator:
    def __init__(self, config=None):
        self.config = Config(config or {})
        self.dialect = self._create_dialect()
        self.parser = SQLParser(self.dialect)
        self.optimizer = QueryOptimizer(self.dialect)
    
    def select(self, table, columns="*", where=None, order_by=None, limit=None):
        """生成 SELECT 查询"""
        query = SelectQuery(table, columns)
        
        if where:
            query.where(where)
        
        if order_by:
            query.order_by(order_by)
        
        if limit:
            query.limit(limit)
        
        return self._build_query(query)
    
    def insert(self, table, data, on_duplicate=None):
        """生成 INSERT 查询"""
        query = InsertQuery(table, data)
        
        if on_duplicate:
            query.on_duplicate_key_update(on_duplicate)
        
        return self._build_query(query)
    
    def update(self, table, data, where=None):
        """生成 UPDATE 查询"""
        query = UpdateQuery(table, data)
        
        if where:
            query.where(where)
        
        return self._build_query(query)
    
    def delete(self, table, where=None):
        """生成 DELETE 查询"""
        query = DeleteQuery(table)
        
        if where:
            query.where(where)
        
        return self._build_query(query)
    
    def join(self, tables, join_type="INNER", on_conditions=None):
        """生成 JOIN 查询"""
        query = JoinQuery(tables, join_type)
        
        if on_conditions:
            query.on(on_conditions)
        
        return self._build_query(query)
```

### 代码生成器
```python
class CodeGenerator:
    def __init__(self, config=None):
        self.config = Config(config or {})
        self.template_engine = self._create_template_engine()
        self.metadata_reader = DatabaseMetadataReader(self.config)
    
    def generate_entity(self, table_name, output_dir=None):
        """生成实体类"""
        metadata = self.metadata_reader.get_table_metadata(table_name)
        
        context = {
            'table_name': table_name,
            'class_name': self._to_class_name(table_name),
            'fields': metadata.columns,
            'primary_key': metadata.primary_key,
            'package': self.config.get('code-generation.package-name'),
            'imports': self._generate_imports(metadata.columns)
        }
        
        template = self.template_engine.get_template('entity.hbs')
        code = template.render(context)
        
        if output_dir:
            self._save_code(code, output_dir, f"{context['class_name']}.java")
        
        return code
    
    def generate_repository(self, table_name, output_dir=None):
        """生成 Repository 接口"""
        metadata = self.metadata_reader.get_table_metadata(table_name)
        
        context = {
            'table_name': table_name,
            'entity_name': self._to_class_name(table_name),
            'repository_name': f"{self._to_class_name(table_name)}Repository",
            'package': self.config.get('code-generation.package-name'),
            'primary_key': metadata.primary_key,
            'table_columns': metadata.columns
        }
        
        template = self.template_engine.get_template('repository.hbs')
        code = template.render(context)
        
        if output_dir:
            self._save_code(code, output_dir, f"{context['repository_name']}.java")
        
        return code
    
    def generate_service(self, table_name, output_dir=None):
        """生成 Service 类"""
        metadata = self.metadata_reader.get_table_metadata(table_name)
        
        context = {
            'table_name': table_name,
            'entity_name': self._to_class_name(table_name),
            'service_name': f"{self._to_class_name(table_name)}Service",
            'repository_name': f"{self._to_class_name(table_name)}Repository",
            'package': self.config.get('code-generation.package-name'),
            'primary_key': metadata.primary_key
        }
        
        template = self.template_engine.get_template('service.hbs')
        code = template.render(context)
        
        if output_dir:
            self._save_code(code, output_dir, f"{context['service_name']}.java")
        
        return code
```

### 数据库方言
```python
class MySQLDialect:
    """MySQL 数据库方言"""
    
    def __init__(self):
        self.name = "mysql"
        self.version = "8.0"
        self.features = {
            "limit_syntax": "LIMIT offset, count",
            "auto_increment": "AUTO_INCREMENT",
            "primary_key": "PRIMARY KEY",
            "foreign_key": "FOREIGN KEY",
            "unique_key": "UNIQUE KEY"
        }
    
    def quote_identifier(self, identifier):
        """引用标识符"""
        return f"`{identifier}`"
    
    def get_limit_clause(self, offset, limit):
        """获取 LIMIT 子句"""
        if offset is not None:
            return f"LIMIT {offset}, {limit}"
        return f"LIMIT {limit}"
    
    def get_auto_increment_clause(self):
        """获取自增子句"""
        return self.features["auto_increment"]
    
    def format_date_literal(self, date_value):
        """格式化日期字面量"""
        if isinstance(date_value, datetime):
            return f"'{date_value.strftime('%Y-%m-%d %H:%M:%S')}'"
        return f"'{date_value}'"

class PostgreSQLDialect:
    """PostgreSQL 数据库方言"""
    
    def __init__(self):
        self.name = "postgresql"
        self.version = "13.0"
        self.features = {
            "limit_syntax": "LIMIT count OFFSET offset",
            "serial": "SERIAL",
            "primary_key": "PRIMARY KEY",
            "foreign_key": "FOREIGN KEY",
            "unique_key": "UNIQUE"
        }
    
    def quote_identifier(self, identifier):
        """引用标识符"""
        return f'"{identifier}"'
    
    def get_limit_clause(self, offset, limit):
        """获取 LIMIT 子句"""
        if offset is not None:
            return f"LIMIT {limit} OFFSET {offset}"
        return f"LIMIT {limit}"
    
    def get_serial_clause(self):
        """获取序列子句"""
        return self.features["serial"]
    
    def format_date_literal(self, date_value):
        """格式化日期字面量"""
        if isinstance(date_value, datetime):
            return f"'{date_value.isoformat()}'"
        return f"'{date_value}'"
```

## 模板系统

### 实体类模板
```handlebars
{{!-- entity.java.hbs --}}
package {{package}};

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.Date;

{{#each imports}}
import {{.}};
{{/each}}

@Entity
@Table(name = "{{table_name}}")
{{#if table_comment}}
@Table(comment = "{{table_comment}}")
{{/if}}
public class {{class_name}} {
    
    {{#each fields}}
    {{#if is_primary_key}}
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    {{/if}}
    {{#if is_foreign_key}}
    @ManyToOne
    @JoinColumn(name = "{{column_name}}")
    {{/if}}
    @Column(name = "{{column_name}}"{{#if length}}, length = {{length}}{{/if}}{{#if nullable}}, nullable = {{nullable}}{{/if}})
    {{#if comment}}
    @Column(comment = "{{comment}}")
    {{/if}}
    private {{java_type}} {{field_name}};
    
    {{/each}}
    
    // Getters and Setters
    {{#each fields}}
    public {{java_type}} get{{capitalize field_name}}() {
        return {{field_name}};
    }
    
    public void set{{capitalize field_name}}({{java_type}} {{field_name}}) {
        this.{{field_name}} = {{field_name}};
    }
    
    {{/each}}
}
```

### Repository 模板
```handlebars
{{!-- repository.java.hbs --}}
package {{package}};

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface {{repository_name}} extends JpaRepository<{{entity_name}}, {{primary_key.java_type}}> {
    
    // 自定义查询方法
    List<{{entity_name}}> findBy{{capitalize lookup_field}}({{lookup_field.java_type}} {{lookup_field}});
    
    Optional<{{entity_name}}> findBy{{capitalize lookup_field}}And{{capitalize status_field}}(
        {{lookup_field.java_type}} {{lookup_field}}, 
        {{status_field.java_type}} {{status_field}}
    );
    
    @Query("SELECT e FROM {{entity_name}} e WHERE e.{{lookup_field}} = :{{lookup_field}}")
    List<{{entity_name}}> findByCustomQuery(@Param("{{lookup_field}}") {{lookup_field.java_type}} {{lookup_field}});
    
    // 分页查询
    @Query("SELECT e FROM {{entity_name}} e WHERE e.{{status_field}} = :status ORDER BY e.{{created_field}} DESC")
    Page<{{entity_name}}> findByStatusOrderByCreatedDesc(
        @Param("status") {{status_field.java_type}} status, 
        Pageable pageable
    );
}
```

## 集成指南

### Spring Boot 集成
```java
@Configuration
@EnableJpaRepositories(basePackages = "{{package}}")
public class DatabaseConfig {
    
    @Bean
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://localhost:3306/{{database}}");
        config.setUsername("{{username}}");
        config.setPassword("{{password}}");
        config.setMaximumPoolSize(10);
        return new HikariDataSource(config);
    }
    
    @Bean
    public LocalContainerEntityManagerFactoryBean entityManagerFactory() {
        LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(dataSource());
        em.setPackagesToScan(new String[] { "{{package}}" });
        em.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        return em;
    }
    
    @Bean
    public PlatformTransactionManager transactionManager() {
        JpaTransactionManager transactionManager = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(entityManagerFactory().getObject());
        return transactionManager;
    }
}
```

### 命令行工具
```python
#!/usr/bin/env python3
# sqlgen.py

import argparse
import sys
from sql_generator import SQLGenerator, CodeGenerator

def main():
    parser = argparse.ArgumentParser(description='SQL Generator')
    parser.add_argument('command', choices=['generate', 'query', 'migrate'])
    parser.add_argument('--config', '-c', help='Configuration file')
    parser.add_argument('--table', '-t', help='Table name')
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--type', help='Generation type (entity, repository, service)')
    
    args = parser.parse_args()
    
    # 加载配置
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    if args.command == 'generate':
        generator = CodeGenerator(config)
        
        if args.type == 'entity':
            code = generator.generate_entity(args.table, args.output)
        elif args.type == 'repository':
            code = generator.generate_repository(args.table, args.output)
        elif args.type == 'service':
            code = generator.generate_service(args.table, args.output)
        else:
            # 生成所有代码
            generator.generate_all(args.table, args.output)
    
    elif args.command == 'query':
        generator = SQLGenerator(config)
        # 交互式查询生成
        interactive_query_generator(generator)
    
    elif args.command == 'migrate':
        generator = SQLGenerator(config)
        # 生成迁移脚本
        generate_migration_script(generator, args.table)

def interactive_query_generator(generator):
    """交互式查询生成"""
    print("SQL Generator - Interactive Mode")
    print("Enter 'quit' to exit")
    
    while True:
        try:
            command = input("sqlgen> ").strip()
            
            if command.lower() == 'quit':
                break
            
            # 解析命令并生成 SQL
            sql = parse_and_generate_sql(generator, command)
            print(f"Generated SQL:\n{sql}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()
```

## 最佳实践

### 查询优化
1. **索引使用**: 为常用查询字段创建索引
2. **避免全表扫描**: 使用适当的 WHERE 条件
3. **分页优化**: 使用高效的分页方法
4. **查询缓存**: 启用查询结果缓存

### 代码生成
1. **命名规范**: 使用一致的命名约定
2. **代码风格**: 遵循项目代码风格
3. **注释完整**: 生成完整的注释和文档
4. **测试覆盖**: 生成相应的测试代码

### 安全考虑
1. **SQL 注入**: 使用参数化查询
2. **权限控制**: 实施适当的数据库权限
3. **数据加密**: 敏感数据加密存储
4. **审计日志**: 记录数据库操作日志

## 故障排除

### 常见问题
1. **连接失败**: 检查数据库连接配置
2. **语法错误**: 验证生成的 SQL 语法
3. **性能问题**: 优化查询和索引
4. **编码问题**: 确保字符集配置正确

### 调试技巧
1. **启用日志**: 启用详细的 SQL 日志
2. **执行计划**: 分析查询执行计划
3. **逐步测试**: 分步测试生成的代码
4. **数据库工具**: 使用数据库管理工具验证

## 工具和资源

### 开发工具
- **数据库管理工具**: MySQL Workbench, pgAdmin, DBeaver
- **SQL 编辑器**: SQL Developer, DataGrip, HeidiSQL
- **版本控制**: Git, SVN, Mercurial
- **构建工具**: Maven, Gradle, Ant

### 相关库
- **ORM 框架**: Hibernate, MyBatis, JPA
- **连接池**: HikariCP, C3P0, DBCP
- **数据库驱动**: MySQL Connector, PostgreSQL JDBC
- **代码生成**: MyBatis Generator, Hibernate Tools

### 学习资源
- [SQL 教程](https://www.w3schools.com/sql/)
- [MySQL 文档](https://dev.mysql.com/doc/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [JPA 规范](https://jakarta.ee/specifications/persistence/)

### 社区支持
- [Stack Overflow SQL 标签](https://stackoverflow.com/questions/tagged/sql)
- [数据库论坛](https://forums.oracle.com/forums/main.jspa?categoryID=84)
- [GitHub 数据库项目](https://github.com/topics/database)
- [数据库中文社区](https://www.mysql.cn/)
