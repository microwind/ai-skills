---
name: 建造者模式
description: "分步骤构建复杂对象。在对象有很多可选参数或构建步骤复杂时使用。"
license: MIT
---

# 建造者模式 (Builder Pattern)

## 概述

建造者模式将复杂对象的构建与其表示分离，使得可以按步骤构建对象。这个模式特别适用于对象有多个可选属性或构建过程复杂的场景。

**核心原则**:
- 🏗️ **分离构建和表示**: 构建者负责如何构建，客户端负责如何使用
- 📝 **链式调用**: 支持流畅的函数式编程风格
- ✅ **参数验证集中**: 在 build 方法中验证所有参数
- 🔁 **灵活性高**: 支持多种构建顺序和组合

## 何时使用

### 完美适用场景

| 场景 | 说明 | 优先级 |
|------|------|--------|
| **HTTP 请求构建** | URL、方法、头、参数、超时等可选属性 | ⭐⭐⭐ |
| **SQL 查询构建** | SELECT、WHERE、ORDER BY、LIMIT 等灵活组合 | ⭐⭐⭐ |
| **对象配置** | 大量可选配置项的对象初始化 | ⭐⭐⭐ |
| **DTO/VO 构建** | 从多个数据源组装 DTO | ⭐⭐⭐ |
| **复杂表单** | 表单验证、多步骤填写 | ⭐⭐ |
| **数据库连接池配置** | 众多可选参数的配置对象 | ⭐⭐ |

### 触发信号

✅ 以下信号表明应该使用 Builder：
- "这个类的构造函数有太多参数"
- "大部分参数都是可选的"
- "需要多种方式配置同一对象"
- "构建过程复杂，涉及多个步骤"
- "参数间有依赖关系，需要验证"

❌ 以下情况不应该使用：
- 对象只有 1-2 个参数
- 所有参数都是必需的
- 参数组合并无实际意义
- 性能关键路径（build() 有开销）

## 建造者模式的优缺点

### 优点 ✅

1. **参数管理清晰**
   - 避免构造函数参数过多
   - 代码易读性大幅提高
   - 无需记忆参数顺序

2. **支持链式调用**
   - 代码风格优雅流畅
   - 支持函数式编程
   - 可读性更高

3. **灵活的构建过程**
   - 支持多种参数组合
   - 构建顺序灵活
   - 支持默认值

4. **参数验证集中**
   - 所有验证在 build() 方法
   - 确保对象始终有效
   - 减少运行时错误

5. **易于扩展**
   - 添加新参数无需改变客户端
   - 向后兼容性好
   - 容易添加新的构建方式

### 缺点 ❌

1. **代码量增加**
   - 需要编写 Builder 类
   - 代码行数增加
   - 简单对象可能过度设计

2. **性能开销**
   - build() 方法有开销
   - 创建额外对象
   - 不适用于性能关键路径

3. **复杂度增加**
   - 初学者容易混淆
   - 需要理解嵌套类或独立类
   - 调试相对复杂

## 建造者模式的 5 种实现方法

### 1. 经典 Builder - 静态内部类

**特点**: 标准实现方式，安全且易维护

```java
public class HttpRequest {
    private String url;
    private String method;
    private Map<String, String> headers;
    private String body;
    private int timeout;
    private boolean followRedirects;
    
    // 私有构造函数，强制使用 Builder
    private HttpRequest(Builder builder) {
        this.url = builder.url;
        this.method = builder.method;
        this.headers = builder.headers;
        this.body = builder.body;
        this.timeout = builder.timeout;
        this.followRedirects = builder.followRedirects;
    }
    
    // Builder 内部类
    public static class Builder {
        private String url;
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();
        private String body = "";
        private int timeout = 5000;
        private boolean followRedirects = true;
        
        public Builder(String url) {
            this.url = url;
        }
        
        public Builder method(String method) {
            this.method = method;
            return this;
        }
        
        public Builder header(String name, String value) {
            this.headers.put(name, value);
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
        
        public Builder timeout(int timeout) {
            this.timeout = timeout;
            return this;
        }
        
        public Builder followRedirects(boolean follow) {
            this.followRedirects = follow;
            return this;
        }
        
        // 构建并验证
        public HttpRequest build() {
            if (url == null || url.isEmpty()) {
                throw new IllegalArgumentException("URL is required");
            }
            if (timeout <= 0) {
                throw new IllegalArgumentException("Timeout must be positive");
            }
            return new HttpRequest(this);
        }
    }
    
    @Override
    public String toString() {
        return String.format("HttpRequest{%s %s, timeout=%d}", method, url, timeout);
    }
}

// 使用
HttpRequest request = new HttpRequest.Builder("https://api.example.com/users")
    .method("POST")
    .header("Content-Type", "application/json")
    .header("Authorization", "Bearer token")
    .body("{\"name\":\"John\"}")
    .timeout(10000)
    .build();
```

---

### 2. 流式 Builder - 链式编程

**特点**: 支持更流畅的链式调用

```java
public class SQLBuilder {
    private List<String> selectClauses = new ArrayList<>();
    private String fromClause;
    private List<String> whereClauses = new ArrayList<>();
    private List<String> orderByClauses = new ArrayList<>();
    private int limit = -1;
    
    public SQLBuilder select(String... columns) {
        selectClauses.addAll(Arrays.asList(columns));
        return this;
    }
    
    public SQLBuilder from(String table) {
        this.fromClause = table;
        return this;
    }
    
    public SQLBuilder where(String condition) {
        whereClauses.add(condition);
        return this;
    }
    
    public SQLBuilder orderBy(String column, String direction) {
        orderByClauses.add(column + " " + direction);
        return this;
    }
    
    public SQLBuilder limit(int limit) {
        this.limit = limit;
        return this;
    }
    
    public String build() {
        if (fromClause == null) {
            throw new IllegalArgumentException("FROM clause is required");
        }
        
        StringBuilder sql = new StringBuilder();
        
        // SELECT
        sql.append("SELECT ");
        if (selectClauses.isEmpty()) {
            sql.append("*");
        } else {
            sql.append(String.join(", ", selectClauses));
        }
        
        // FROM
        sql.append(" FROM ").append(fromClause);
        
        // WHERE
        if (!whereClauses.isEmpty()) {
            sql.append(" WHERE ").append(String.join(" AND ", whereClauses));
        }
        
        // ORDER BY
        if (!orderByClauses.isEmpty()) {
            sql.append(" ORDER BY ").append(String.join(", ", orderByClauses));
        }
        
        // LIMIT
        if (limit > 0) {
            sql.append(" LIMIT ").append(limit);
        }
        
        return sql.toString();
    }
}

// 使用
String sql = new SQLBuilder()
    .select("id", "name", "email")
    .from("users")
    .where("age > 18")
    .where("status = 'active'")
    .orderBy("created_at", "DESC")
    .limit(10)
    .build();

System.out.println(sql);
// SELECT id, name, email FROM users WHERE age > 18 AND status = 'active' ORDER BY created_at DESC LIMIT 10
```

---

### 3. 参数对象 Builder

**特点**: 用单独的参数对象，适合参数众多的情况

```java
// 参数对象
public class QueryParams {
    public int page = 1;
    public int pageSize = 20;
    public String sortBy = "id";
    public String sortOrder = "ASC";
    public List<String> filters = new ArrayList<>();
    
    public static class Builder {
        private QueryParams params = new QueryParams();
        
        public Builder page(int page) {
            params.page = Math.max(1, page);
            return this;
        }
        
        public Builder pageSize(int pageSize) {
            params.pageSize = Math.min(100, pageSize);
            return this;
        }
        
        public Builder sort(String sortBy, String order) {
            params.sortBy = sortBy;
            params.sortOrder = order.toUpperCase();
            return this;
        }
        
        public Builder filter(String condition) {
            params.filters.add(condition);
            return this;
        }
        
        public QueryParams build() {
            return params;
        }
    }
}

// 使用
QueryParams params = new QueryParams.Builder()
    .page(2)
    .pageSize(50)
    .sort("name", "asc")
    .filter("status=active")
    .filter("type=premium")
    .build();
```

---

### 4. 继承 Builder - 支持多态

**特点**: Builder 本身也支持继承，适合复杂继承体系

```java
public abstract class Pizza {
    public enum Topping { HAM, MUSHROOM, ONION, PEPPER, SAUSAGE }
    
    final Set<Topping> toppings;
    
    abstract static class Builder<T extends Builder<T>> {
        EnumSet<Topping> toppings = EnumSet.noneOf(Topping.class);
        
        public T addTopping(Topping topping) {
            toppings.add(Objects.requireNonNull(topping));
            return self();
        }
        
        abstract Pizza build();
        
        protected abstract T self();
    }
    
    Pizza(Builder<?> builder) {
        toppings = builder.toppings.clone();
    }
}

public class NyPizza extends Pizza {
    public enum Size { SMALL, MEDIUM, LARGE }
    
    public final Size size;
    
    public static class Builder extends Pizza.Builder<Builder> {
        private final Size size;
        
        public Builder(Size size) {
            this.size = Objects.requireNonNull(size);
        }
        
        @Override
        public NyPizza build() {
            return new NyPizza(this);
        }
        
        @Override
        protected Builder self() {
            return this;
        }
    }
    
    private NyPizza(Builder builder) {
        super(builder);
        size = builder.size;
    }
}

// 使用
NyPizza pizza = new NyPizza.Builder(NyPizza.Size.SMALL)
    .addTopping(Pizza.Topping.SAUSAGE)
    .addTopping(Pizza.Topping.ONION)
    .build();
```

---

### 5. Lombok @Builder - 自动生成

**特点**: 使用注解自动生成 Builder 代码

```java
@Builder
@Data
public class Document {
    private String title;
    private String content;
    @Builder.Default
    private String author = "Anonymous";
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
    private boolean published;
}

// 自动生成的 Builder 代码（由 Lombok 生成）
// 使用时：
Document doc = Document.builder()
    .title("Document Title")
    .content("Content here")
    .author("John Doe")
    .published(true)
    .build();
```

---

## 常见问题与完整解决方案

### 问题 1: 参数验证与可选参数

**症状**: 不清楚哪些参数是必需的，哪些是可选的

```java
// ✅ 解决方案：明确标记必需参数
public static class Builder {
    // 必需参数在构造函数中
    private String url;
    
    public Builder(String url) {  // 强制提供
        this.url = Objects.requireNonNull(url, "URL is required");
    }
    
    // 可选参数有默认值
    private int timeout = 5000;
    private boolean followRedirects = true;
    private Map<String, String> headers = new HashMap<>();
    
    public Builder timeout(int timeout) {
        if (timeout <= 0) {
            throw new IllegalArgumentException("Timeout must be positive");
        }
        this.timeout = timeout;
        return this;
    }
    
    public HttpRequest build() {
        // 最终验证所有参数
        validateAll();
        return new HttpRequest(this);
    }
    
    private void validateAll() {
        // 检查所有必需参数都有值
        // 检查所有值的有效性
    }
}
```

### 问题 2: 不可变对象的构建

**症状**: 构建后的对象需要保证不可变性

```java
// ✅ 解决方案：返回不可变副本
public class ImmutableConfig {
    private final Map<String, String> properties;
    
    private ImmutableConfig(Builder builder) {
        // 使用 Collections.unmodifiableMap 保证不可变
        this.properties = Collections.unmodifiableMap(
            new HashMap<>(builder.properties)
        );
    }
    
    public String get(String key) {
        return properties.get(key);
    }
    
    public static class Builder {
        private Map<String, String> properties = new HashMap<>();
        
        public Builder set(String key, String value) {
            properties.put(key, value);
            return this;
        }
        
        public ImmutableConfig build() {
            return new ImmutableConfig(this);
        }
    }
}

// 使用
ImmutableConfig config = new ImmutableConfig.Builder()
    .set("app.name", "MyApp")
    .set("debug", "true")
    .build();

// config.properties.put(...);  // 编译错误！不可修改
```

### 问题 3: 性能 - 创建过多中间对象

**症状**: 每次 build() 都创建新对象，性能不佳

```java
// ✅ 解决方案：对象池或缓存
public class CachedBuilder {
    private static final Map<BuildConfig, CachedObject> cache = 
        Collections.synchronizedMap(new WeakHashMap<>());
    
    public CachedObject build() {
        BuildConfig config = createConfig();
        
        // 检查缓存中是否已存在相同配置
        return cache.computeIfAbsent(config, cfg -> 
            createObject(cfg)
        );
    }
    
    private CachedObject createObject(BuildConfig config) {
        // 创建新对象
        return new CachedObject(...);
    }
}
```

### 问题 4: 嵌套对象的构建

**症状**: 需要构建含有嵌套对象的复杂对象

```java
// ✅ 解决方案：嵌套 Builder
public class User {
    private String name;
    private Address address;
    
    public static class Builder {
        private String name;
        private Address.Builder addressBuilder = new Address.Builder();
        
        public Builder name(String name) {
            this.name = name;
            return this;
        }
        
        // 支持地址构建
        public Builder city(String city) {
            addressBuilder.city(city);
            return this;
        }
        
        public Builder zipCode(String zipCode) {
            addressBuilder.zipCode(zipCode);
            return this;
        }
        
        public User build() {
            User user = new User();
            user.name = this.name;
            user.address = addressBuilder.build();
            return user;
        }
    }
}

// 使用
User user = new User.Builder()
    .name("John")
    .city("New York")
    .zipCode("10001")
    .build();
```

---

## Builder vs 其他模式对比

| 方面 | Builder | 工厂方法 | 构造函数 |
|------|---------|---------|---------|
| **参数数量** | 很多（10+） | 中等(3-5) | 少(<3) |
| **可选参数** | 支持很好 | 不支持 | 不支持 |
| **灵活性** | 很高 | 中等 | 低 |
| **代码量** | 多 | 中等 | 少 |
| **学习曲线** | 中等 | 简单 | 简单 |

---

## 最佳实践

1. ✅ **参数验证集中** - 所有验证在 build() 方法
2. ✅ **提供明确的必需参数** - 在构造函数中
3. ✅ **使用流畅接口** - 支持链式调用
4. ✅ **文档化默认值** - 说明每个参数的默认值
5. ✅ **考虑线程安全** - 如果 Builder 在多线程中使用
6. ✅ **返回不可变对象** - build() 的结果应该是不可变的

---

## 何时避免使用

- ❌ 对象只有 1-2 个参数
- ❌ 所有参数都是必需的
- ❌ 性能关键路径（实时系统）
- ❌ 极小型项目（过度设计）
