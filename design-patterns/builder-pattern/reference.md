# 建造者模式完整参考实现

## UML 类图

```
┌──────────────┐
│  Director    │
├──────────────┤
│ - builder    │
│ + construct()│
└──────┬───────┘
       │ uses
       ▼
┌──────────────────────┐
│   Builder (接口)     │
├──────────────────────┤
│ + buildPart1()       │
│ + buildPart2()       │
│ + buildPart3()       │
│ + getResult()        │
└──────┬───────────────┘
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌─────────────────┐  ┌──────────────────┐
│ ConcreteBuilder │  │ FluetBuilder     │
├─────────────────┤  ├──────────────────┤
│ - product       │  │ - product        │
│ + buildPart1()  │  │ + part1()        │
└─────────────────┘  │ + build()        │
                     └──────────────────┘
```

---

## Java: 5种实现方法

### 方法1: 经典内部类处理器

```java
/**
 * HttpUrlBuilder - 经典建造者模式
 * 用于构建复杂的HTTP请求对象
 */
public class HttpRequest {
    private final String method;
    private final String url;
    private final Map<String, String> headers;
    private final String body;
    private final int timeout;
    private final boolean followRedirects;
    
    // ===== 构造器状态不可变 =====
    private HttpRequest(Builder builder) {
        this.method = builder.method;
        this.url = builder.url;
        this.headers = Collections.unmodifiableMap(builder.headers);
        this.body = builder.body;
        this.timeout = builder.timeout;
        this.followRedirects = builder.followRedirects;
    }
    
    // ===== 静态构造入口 =====
    public static Builder builder() {
        return new Builder();
    }
    
    // ===== 建造者内部类 =====
    public static class Builder {
        private String method = "GET";
        private String url;
        private Map<String, String> headers = new HashMap<>();
        private String body = "";
        private int timeout = 30;
        private boolean followRedirects = true;
        
        // ===== 流式接口 - 返回 this 支持链式调用 =====
        
        public Builder url(String url) {
            this.url = url;
            return this;
        }
        
        public Builder get() {
            this.method = "GET";
            return this;
        }
        
        public Builder post() {
            this.method = "POST";
            return this;
        }
        
        public Builder put() {
            this.method = "PUT";
            return this;
        }
        
        public Builder delete() {
            this.method = "DELETE";
            return this;
        }
        
        public Builder header(String key, String value) {
            this.headers.put(key, value);
            return this;
        }
        
        public Builder headers(Map<String, String> headers) {
            this.headers.putAll(headers);
            return this;
        }
        
        public Builder body(String body) {
            this.body = body;
            return this;
        }
        
        public Builder timeout(int seconds) {
            this.timeout = seconds;
            return this;
        }
        
        public Builder followRedirects(boolean follow) {
            this.followRedirects = follow;
            return this;
        }
        
        // ===== 验证与构建 =====
        
        public HttpRequest build() {
            // 参数验证
            if (url == null || url.isEmpty()) {
                throw new IllegalArgumentException("URL不能为空");
            }
            if (timeout <= 0) {
                throw new IllegalArgumentException("超时时间必须为正数");
            }
            
            return new HttpRequest(this);
        }
    }
    
    // ===== 使用示例 =====
    public void executeRequest() {
        System.out.printf("执行 %s 请求到: %s\n", method, url);
        System.out.println("请求头: " + headers);
        System.out.println("超时: " + timeout + "秒");
    }
    
    @Override
    public String toString() {
        return String.format("HttpRequest{method='%s', url='%s', headers=%s, timeout=%d}", 
            method, url, headers, timeout);
    }
}

// 使用示例
class HttpRequestExample {
    public static void main(String[] args) {
        // ===== 链式构建 =====
        HttpRequest request = HttpRequest.builder()
            .url("https://api.example.com/users")
            .post()
            .header("Content-Type", "application/json")
            .header("Authorization", "Bearer token123")
            .body("{\"name\": \"Alice\"}")
            .timeout(60)
            .build();
        
        System.out.println(request);
        request.executeRequest();
    }
}
```

### 方法2: 流式SQL查询构造器

```java
/**
 * SQLQueryBuilder - 流式查询构造
 * 用于动态构建SQL SELECT语句
 */
public class SQLQuery {
    private List<String> selectFields;
    private String fromTable;
    private List<String> joinClauses;
    private List<String> whereConditions;
    private List<String> groupByFields;
    private List<String> orderByFields;
    private int limit = -1;
    private int offset = 0;
    
    private SQLQuery(SQLQueryBuilder builder) {
        this.selectFields = new ArrayList<>(builder.selectFields);
        this.fromTable = builder.fromTable;
        this.joinClauses = new ArrayList<>(builder.joinClauses);
        this.whereConditions = new ArrayList<>(builder.whereConditions);
        this.groupByFields = new ArrayList<>(builder.groupByFields);
        this.orderByFields = new ArrayList<>(builder.orderByFields);
        this.limit = builder.limit;
        this.offset = builder.offset;
    }
    
    public static class SQLQueryBuilder {
        private List<String> selectFields = new ArrayList<>();
        private String fromTable;
        private List<String> joinClauses = new ArrayList<>();
        private List<String> whereConditions = new ArrayList<>();
        private List<String> groupByFields = new ArrayList<>();
        private List<String> orderByFields = new ArrayList<>();
        private int limit = -1;
        private int offset = 0;
        
        // ===== SELECT 子句 =====
        public SQLQueryBuilder select(String... fields) {
            selectFields.addAll(Arrays.asList(fields));
            return this;
        }
        
        public SQLQueryBuilder selectAll() {
            selectFields.add("*");
            return this;
        }
        
        // ===== FROM 子句 =====
        public SQLQueryBuilder from(String table) {
            this.fromTable = table;
            return this;
        }
        
        // ===== JOIN 子句 =====
        public SQLQueryBuilder innerJoin(String table, String condition) {
            joinClauses.add("INNER JOIN " + table + " ON " + condition);
            return this;
        }
        
        public SQLQueryBuilder leftJoin(String table, String condition) {
            joinClauses.add("LEFT JOIN " + table + " ON " + condition);
            return this;
        }
        
        // ===== WHERE 子句 =====
        public SQLQueryBuilder where(String condition) {
            whereConditions.add(condition);
            return this;
        }
        
        public SQLQueryBuilder and(String condition) {
            if (!whereConditions.isEmpty()) {
                whereConditions.set(whereConditions.size() - 1, 
                    whereConditions.get(whereConditions.size() - 1) + " AND " + condition);
            }
            return this;
        }
        
        // ===== GROUP BY 子句 =====
        public SQLQueryBuilder groupBy(String... fields) {
            groupByFields.addAll(Arrays.asList(fields));
            return this;
        }
        
        // ===== ORDER BY 子句 =====
        public SQLQueryBuilder orderBy(String field, boolean ascending) {
            orderByFields.add(field + (ascending ? " ASC" : " DESC"));
            return this;
        }
        
        // ===== LIMIT/OFFSET 子句 =====
        public SQLQueryBuilder limit(int limit) {
            this.limit = limit;
            return this;
        }
        
        public SQLQueryBuilder offset(int offset) {
            this.offset = offset;
            return this;
        }
        
        // ===== 构建SQL字符串 =====
        public SQLQuery build() {
            if (fromTable == null || fromTable.isEmpty()) {
                throw new IllegalArgumentException("FROM表不能为空");
            }
            return new SQLQuery(this);
        }
    }
    
    public String toSql() {
        StringBuilder sql = new StringBuilder();
        
        // SELECT
        sql.append("SELECT ").append(String.join(", ", selectFields)).append("\n");
        
        // FROM
        sql.append("FROM ").append(fromTable).append("\n");
        
        // JOIN
        for (String join : joinClauses) {
            sql.append(join).append("\n");
        }
        
        // WHERE
        if (!whereConditions.isEmpty()) {
            sql.append("WHERE ").append(String.join(" AND ", whereConditions)).append("\n");
        }
        
        // GROUP BY
        if (!groupByFields.isEmpty()) {
            sql.append("GROUP BY ").append(String.join(", ", groupByFields)).append("\n");
        }
        
        // ORDER BY
        if (!orderByFields.isEmpty()) {
            sql.append("ORDER BY ").append(String.join(", ", orderByFields)).append("\n");
        }
        
        // LIMIT/OFFSET
        if (limit > 0) {
            sql.append("LIMIT ").append(limit);
            if (offset > 0) {
                sql.append(" OFFSET ").append(offset);
            }
            sql.append("\n");
        }
        
        return sql.toString();
    }
}

// 使用示例
class SQLQueryExample {
    public static void main(String[] args) {
        SQLQuery query = new SQLQuery.SQLQueryBuilder()
            .select("u.id", "u.name", "o.order_id", "COUNT(*) AS order_count")
            .from("users u")
            .leftJoin("orders o", "u.id = o.user_id")
            .where("u.status = 'active'")
            .and("o.created_date >= '2024-01-01'")
            .groupBy("u.id", "u.name", "o.order_id")
            .orderBy("order_count", false)
            .limit(10)
            .offset(0)
            .build();
        
        System.out.println(query.toSql());
    }
}
```

### 方法3: 参数对象构造器

```java
/**
 * DatabaseConnectionBuilder - 参数对象模式
 */
public class DatabaseConnection {
    private String host;
    private int port;
    private String database;
    private String username;
    private String password;
    private int maxConnections;
    private long connectionTimeout;
    private boolean useSSL;
    private String charset = "UTF-8";
    
    private DatabaseConnection() {}
    
    public static class ConnectionParams {
        public String host;
        public int port = 5432;
        public String database;
        public String username;
        public String password;
        public int maxConnections = 10;
        public long connectionTimeout = 30000;
        public boolean useSSL = true;
        public String charset = "UTF-8";
    }
    
    public static DatabaseConnection create(Consumer<ConnectionParams> configurer) {
        ConnectionParams params = new ConnectionParams();
        configurer.accept(params);
        
        DatabaseConnection conn = new DatabaseConnection();
        conn.host = params.host;
        conn.port = params.port;
        conn.database = params.database;
        conn.username = params.username;
        conn.password = params.password;
        conn.maxConnections = params.maxConnections;
        conn.connectionTimeout = params.connectionTimeout;
        conn.useSSL = params.useSSL;
        conn.charset = params.charset;
        
        return conn;
    }
    
    public void connect() {
        System.out.printf("连接到 %s:%d/%s (用户: %s, 超时: %dms, SSL: %b)\n",
            host, port, database, username, connectionTimeout, useSSL);
    }
}

// 使用示例
class DBConnectionExample {
    public static void main(String[] args) {
        DatabaseConnection conn = DatabaseConnection.create(params -> {
            params.host = "localhost";
            params.port = 5432;
            params.database = "mydb";
            params.username = "admin";
            params.password = "password123";
            params.maxConnections = 20;
            params.useSSL = true;
        });
        
        conn.connect();
    }
}
```

### 方法4: 继承式构造器（类型安全）

```java
/**
 * PizzaBuilder - 继承式构造器，支持多种Pizza子类
 */
public abstract class Pizza {
    protected List<String> toppings = new ArrayList<>();
    protected String size;
    protected double price;
    
    public abstract static class PizzaBuilder<S extends PizzaBuilder<S, P>, P extends Pizza> {
        protected List<String> toppings = new ArrayList<>();
        protected String size = "MEDIUM";
        protected double price = 0;
        
        // ===== 通用配置 =====
        public S size(String size) {
            this.size = size;
            return self();
        }
        
        public S addTopping(String topping) {
            toppings.add(topping);
            return self();
        }
        
        public S price(double price) {
            this.price = price;
            return self();
        }
        
        // ===== 子类必须实现 =====
        protected abstract P build();
        protected abstract S self();
    }
    
    public void describe() {
        System.out.printf("Pizza[size=%s, price=$%.2f, toppings=%s]\n", size, price, toppings);
    }
}

public class NYPizza extends Pizza {
    public static class NYPizzaBuilder extends PizzaBuilder<NYPizzaBuilder, NYPizza> {
        private String crustType = "thin";
        
        public NYPizzaBuilder crustType(String type) {
            this.crustType = type;
            return this;
        }
        
        @Override
        public NYPizza build() {
            NYPizza pizza = new NYPizza();
            pizza.toppings = new ArrayList<>(this.toppings);
            pizza.size = this.size;
            pizza.price = this.price;
            pizza.crustType = this.crustType;
            return pizza;
        }
        
        @Override
        protected NYPizzaBuilder self() {
            return this;
        }
    }
    
    private String crustType;
    
    public static NYPizzaBuilder builder() {
        return new NYPizzaBuilder();
    }
}

// 使用示例
class PizzaExample {
    public static void main(String[] args) {
        NYPizza pizza = NYPizza.builder()
            .size("LARGE")
            .crustType("thin")
            .addTopping("cheese")
            .addTopping("pepperoni")
            .price(18.99)
            .build();
        
        pizza.describe();
    }
}
```

### 方法5: Lombok @Builder 注解

```java
import lombok.Builder;
import lombok.ToString;

/**
 * User - 使用 Lombok @Builder 自动生成构造器
 */
@Builder
@ToString
public class User {
    private String id;
    private String name;
    private String email;
    private int age;
    
    @Builder.Default
    private boolean active = true;
    
    @Builder.Default
    private String role = "USER";
    
    public static void main(String[] args) {
        // Lombok 自动生成 builder()
        User user = User.builder()
            .id("U001")
            .name("Alice")
            .email("alice@example.com")
            .age(28)
            .role("ADMIN")
            .build();
        
        System.out.println(user);
    }
}
```

---

## Python: 使用描述符协议

```python
from dataclasses import dataclass, field
from typing import List, Optional

class BuilderDescriptor:
    """描述符用于追踪字段状态"""
    
    def __init__(self, name):
        self.name = name
        self.attr_name = f'_{name}'
    
    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return getattr(obj, self.attr_name, None)
    
    def __set__(self, obj, value):
        setattr(obj, self.attr_name, value)

class DocumentBuilder:
    """文档构造器 - 使用链式调用"""
    
    def __init__(self):
        self.title: Optional[str] = None
        self.author: Optional[str] = None
        self.chapters: List[str] = []
        self.metadata: dict = {}
        self._validated = False
    
    def set_title(self, title: str) -> 'DocumentBuilder':
        """链式设置标题"""
        if not title or len(title) < 1:
            raise ValueError("标题不能为空")
        self.title = title
        return self
    
    def set_author(self, author: str) -> 'DocumentBuilder':
        """链式设置作者"""
        if not author:
            raise ValueError("作者不能为空")
        self.author = author
        return self
    
    def add_chapter(self, chapter: str) -> 'DocumentBuilder':
        """链式添加章节"""
        if chapter:
            self.chapters.append(chapter)
        return self
    
    def add_metadata(self, key: str, value) -> 'DocumentBuilder':
        """链式添加元数据"""
        self.metadata[key] = value
        return self
    
    def _validate(self) -> bool:
        """验证必需字段"""
        errors = []
        
        if not self.title:
            errors.append("标题必需")
        if not self.author:
            errors.append("作者必需")
        if not self.chapters:
            errors.append("至少需要一个章节")
        
        if errors:
            raise ValueError("验证失败: " + "; ".join(errors))
        
        self._validated = True
        return True
    
    def build(self) -> 'Document':
        """构建不可变文档对象"""
        self._validate()
        return Document(
            title=self.title,
            author=self.author,
            chapters=self.chapters.copy(),
            metadata=self.metadata.copy()
        )

@dataclass(frozen=True)
class Document:
    """不可变文档对象"""
    title: str
    author: str
    chapters: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def summary(self):
        """输出文档摘要"""
        print(f"文档: {self.title}")
        print(f"作者: {self.author}")
        print(f"章节数: {len(self.chapters)}")
        print(f"元数据: {self.metadata}")

# 使用示例
if __name__ == "__main__":
    doc = (DocumentBuilder()
        .set_title("Python设计模式完全指南")
        .set_author("张三")
        .add_chapter("第1章: 创建型模式")
        .add_chapter("第2章: 结构型模式")
        .add_chapter("第3章: 行为型模式")
        .add_metadata("version", "1.0")
        .add_metadata("language", "zh_CN")
        .build())
    
    doc.summary()
    
    # 尝试修改（会失败）
    try:
        doc.title = "新标题"
    except Exception as e:
        print(f"错误: {e}")  # frozen dataclass 不可修改
```

---

## TypeScript: 类型安全的构造器

```typescript
/**
 * GraphQL 查询构造器 - 类型安全
 */

interface QueryField {
    name: string;
    args?: Record<string, any>;
    fields?: QueryField[];
}

class GraphQLQueryBuilder {
    private query: QueryField = { name: 'query', fields: [] };
    private variables: Record<string, any> = {};
    
    public selectQuery(name: string): this {
        this.query.name = 'query';
        return this;
    }
    
    public field(fieldName: string, config?: (builder: FieldBuilder) => void): this {
        const fieldBuilder = new FieldBuilder();
        
        if (config) {
            config(fieldBuilder);
        }
        
        this.query.fields?.push(fieldBuilder.build());
        return this;
    }
    
    public variable(name: string, value: any): this {
        this.variables[name] = value;
        return this;
    }
    
    public build(): string {
        const queryStr = this.buildQueryString(this.query);
        
        let result = queryStr;
        if (Object.keys(this.variables).length > 0) {
            result = `query(${Object.entries(this.variables)
                .map(([k, v]) => `$${k}: ${typeof v}`)
                .join(', ')}) ${queryStr}`;
        }
        
        return result;
    }
    
    private buildQueryString(field: QueryField, depth = 0): string {
        const indent = '  '.repeat(depth);
        let result = `${indent}${field.name}`;
        
        if (field.args && Object.keys(field.args).length > 0) {
            const argsStr = Object.entries(field.args)
                .map(([k, v]) => `${k}: "${v}"`)
                .join(', ');
            result += `(${argsStr})`;
        }
        
        if (field.fields && field.fields.length > 0) {
            result += ' {\n';
            result += field.fields
                .map(f => this.buildQueryString(f, depth + 1))
                .join('\n');
            result += `\n${indent}}`;
        }
        
        return result;
    }
}

class FieldBuilder {
    private field: QueryField = { name: '', fields: [] };
    
    public name(name: string): this {
        this.field.name = name;
        return this;
    }
    
    public arg(key: string, value: any): this {
        if (!this.field.args) {
            this.field.args = {};
        }
        this.field.args[key] = value;
        return this;
    }
    
    public subField(fieldName: string, config?: (builder: FieldBuilder) => void): this {
        const subBuilder = new FieldBuilder();
        
        if (config) {
            config(subBuilder);
        }
        
        this.field.fields?.push(subBuilder.build());
        return this;
    }
    
    public build(): QueryField {
        return this.field;
    }
}

// 使用示例
const query = new GraphQLQueryBuilder()
    .selectQuery('Query')
    .field('user', (f) => {
        f.name('user')
            .arg('id', 'U123')
            .subField('id', (sf) => sf.name('id'))
            .subField('name', (sf) => sf.name('name'))
            .subField('posts', (sf) => {
                sf.name('posts')
                    .subField('title', (t) => t.name('title'))
                    .subField('content', (c) => c.name('content'));
            });
    })
    .build();

console.log(query);
```

---

## 单元测试

```java
@Test
public void testHttpRequestBuilder() {
    HttpRequest request = HttpRequest.builder()
        .url("https://api.example.com/data")
        .post()
        .header("Content-Type", "application/json")
        .timeout(60)
        .build();
    
    assertEquals("POST", request.method);
    assertEquals("https://api.example.com/data", request.url);
}

@Test
public void testMissingRequiredField() {
    assertThrows(IllegalArgumentException.class, () -> {
        HttpRequest.builder()
            .post()
            .timeout(30)
            .build();  // 缺少URL
    });
}

@Test
public void testSQLQueryBuilder() {
    String sql = new SQLQuery.SQLQueryBuilder()
        .selectAll()
        .from("users")
        .where("status = 'active'")
        .orderBy("created_date", false)
        .build()
        .toSql();
    
    assertTrue(sql.contains("SELECT *"));
    assertTrue(sql.contains("FROM users"));
}

@Test
public void testImmutability() {
    var builder1 = new DocumentBuilder()
        .set_title("Book1")
        .set_author("Author1");
    
    var builder2 = builder1  // 复制
        .set_title("Book2")
        .set_author("Author2");
    
    // 验证独立性
    assertNotEquals("Book1", builder2.title);
}
```

---

## 性能对比表

| 实现方式 | 代码行数 | 构建速度 | 类型安全 | 灵活性 |
|---------|---------|---------|---------|--------|
| 经典内部类 | 80-120 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 流式接口 | 60-100 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 参数对象 | 40-60 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| 继承式构造 | 100-150 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Lombok @Builder | 20-30 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| Python 描述符 | 50-80 | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

---

## 何时使用建造者模式

✅ **强烈推荐**:
- HTTP/数据库连接配置
- SQL查询动态构建
- 复杂对象配置（超过3个参数）
- DTO/VO数据传输对象
- JSON/XML 文档构建

⚠️ **权衡使用**:
- 参数少于3个（直接constructor）
- 简单值对象

❌ **不推荐**:
- 不需要验证的简单对象
- 频繁构建小对象（性能开销）

## 与其他模式关系

**vs 单例模式**: 建造者用于构建对象，单例用于限制实例数量
**vs 工厂模式**: 工厂决定创建哪类对象，建造者控制对象如何构建
**vs 原型模式**: 原型通过复制创建，建造者通过步骤搭建
    // 测试代码
}
```
