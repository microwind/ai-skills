# Factory 模式 - 完整参考实现

## 核心原理与设计

### 模式定义
**工厂模式** 定义一个创建对象的接口，让其子类决定实例化哪一个类。工厂方法使一个类的实例化延迟到其子类。

**核心思想**:
- 🎯 **分离创建与使用**：创建逻辑与业务逻辑解耦
- 📦 **返回接口而非具体类**：面向接口编程
- 🔒 **内聚创建逻辑**：所有创建代码集中在工厂
- 📈 **易于扩展**：新增类型只需新增工厂类，无需修改现有代码

### 关键参与者

```
┌──────────────────────────────────────────┐
│         Product (接口)                    │
│  ─────────────────────────────          │
│  + operation(): void                     │
└──────────────────────────────────────────┘
         △                    △
         │                    │
    ┌────┴──────┐        ┌────┴──────┐
    │ ConcreteA │        │ ConcreteB │
    │ ────────  │        │ ────────  │
    │ +operation│        │ +operation│
    └────────────┘       └────────────┘
         △                    △
         │                    │
┌────────┴──────────────────┬─────────┐
│   Creator (抽象)           │         │
│ ────────────────────────  │         │
│ + factoryMethod(): abstract│         │
│ + businessLogic(): void    │         │
└────────┬──────────────────┘         │
         │                             │
    ┌────┴──────┐              ┌───────┴───────┐
    │CreatorA   │              │CreatorB       │
    │───────────│              │───────────────│
    │+factoryA()│              │+factoryB()    │
    └───────────┘              │implements:    │
                               │return TypeB   │
                               └───────────────┘
```

## 完整的实现参考

### Java 实现 - 生产级工厂方法+参数化工厂混合

```java
// ============ 第一步：定义产品接口 ============
public interface Database {
    void connect() throws DatabaseException;
    QueryResult query(String sql) throws DatabaseException;
    void disconnect();
    String getType();
    DatabaseMetadata getMetadata();
}

public interface DatabaseMetadata {
    String getVersion();
    String getDriverName();
    int getMaxConnections();
}

// ============ 第二步：实现具体产品 ============

/**
 * MySQL 数据库实现
 * 连接信息：默认 localhost:3306
 * 特性：支持事务、复制、分布式存储
 */
public class MySQLDatabase implements Database {
    private String url;
    private String user;
    private String password;
    private boolean connected;
    private static final String DRIVER_NAME = "com.mysql.cj.jdbc.Driver";
    
    public MySQLDatabase(String host, int port, String database) {
        this.url = String.format("jdbc:mysql://%s:%d/%s", host, port, database);
        this.user = "root";
        this.password = "";
        this.connected = false;
    }
    
    @Override
    public void connect() throws DatabaseException {
        try {
            Class.forName(DRIVER_NAME);
            // 模拟连接逻辑
            System.out.println("[MySQL] Connecting to " + url);
            this.connected = true;
            System.out.println("[MySQL] Connected successfully");
        } catch (Exception e) {
            throw new DatabaseException("MySQL connection failed: " + e.getMessage(), e);
        }
    }
    
    @Override
    public QueryResult query(String sql) throws DatabaseException {
        if (!connected) throw new DatabaseException("Database not connected");
        System.out.println("[MySQL Executing: " + sql);
        return new QueryResult("MySQL", sql, new String[]{"id", "name"});
    }
    
    @Override
    public void disconnect() {
        System.out.println("[MySQL] Disconnecting");
        connected = false;
    }
    
    @Override
    public String getType() { return "MySQL"; }
    
    @Override
    public DatabaseMetadata getMetadata() {
        return new DatabaseMetadata() {
            public String getVersion() { return "8.0.x"; }
            public String getDriverName() { return DRIVER_NAME; }
            public int getMaxConnections() { return 151; }
        };
    }
}

/**
 * PostgreSQL 数据库实现
 * 连接信息：默认 localhost:5432
 * 特性：强大的 SQL 支持、JSON 类型、范围类型
 */
public class PostgreSQLDatabase implements Database {
    private String url;
    private boolean connected;
    private static final String DRIVER_NAME = "org.postgresql.Driver";
    
    public PostgreSQLDatabase(String host, int port, String database) {
        this.url = String.format("jdbc:postgresql://%s:%d/%s", host, port, database);
        this.connected = false;
    }
    
    @Override
    public void connect() throws DatabaseException {
        try {
            Class.forName(DRIVER_NAME);
            System.out.println("[PostgreSQL] Connecting to " + url);
            this.connected = true;
            System.out.println("[PostgreSQL] Connected successfully");
        } catch (Exception e) {
            throw new DatabaseException("PostgreSQL connection failed: " + e.getMessage(), e);
        }
    }
    
    @Override
    public QueryResult query(String sql) throws DatabaseException {
        if (!connected) throw new DatabaseException("Database not connected");
        System.out.println("[PostgreSQL] Executing: " + sql);
        return new QueryResult("PostgreSQL", sql, new String[]{"id", "name", "json_data"});
    }
    
    @Override
    public void disconnect() {
        System.out.println("[PostgreSQL] Disconnecting");
        connected = false;
    }
    
    @Override
    public String getType() { return "PostgreSQL"; }
    
    @Override
    public DatabaseMetadata getMetadata() {
        return new DatabaseMetadata() {
            public String getVersion() { return "13.x"; }
            public String getDriverName() { return DRIVER_NAME; }
            public int getMaxConnections() { return 100; }
        };
    }
}

/**
 * MongoDB 数据库实现（文档型数据库）
 * 连接信息：默认 localhost:27017
 * 特性：灵活 Schema、水平扩展、副本集
 */
public class MongoDBDatabase implements Database {
    private String url;
    private boolean connected;
    private static final String DRIVER_NAME = "com.mongodb.client.MongoClient";
    
    public MongoDBDatabase(String host, int port, String database) {
        this.url = String.format("mongodb://%s:%d/%s", host, port, database);
        this.connected = false;
    }
    
    @Override
    public void connect() throws DatabaseException {
        try {
            System.out.println("[MongoDB] Connecting to " + url);
            this.connected = true;
            System.out.println("[MongoDB] Connected successfully");
        } catch (Exception e) {
            throw new DatabaseException("MongoDB connection failed: " + e.getMessage(), e);
        }
    }
    
    @Override
    public QueryResult query(String sql) throws DatabaseException {
        if (!connected) throw new DatabaseException("Database not connected");
        System.out.println("[MongoDB] Executing query: " + sql);
        return new QueryResult("MongoDB", sql, new String[]{"_id", "name", "data"});
    }
    
    @Override
    public void disconnect() {
        System.out.println("[MongoDB] Disconnecting");
        connected = false;
    }
    
    @Override
    public String getType() { return "MongoDB"; }
    
    @Override
    public DatabaseMetadata getMetadata() {
        return new DatabaseMetadata() {
            public String getVersion() { return "4.x / 5.x"; }
            public String getDriverName() { return DRIVER_NAME; }
            public int getMaxConnections() { return 1000; }
        };
    }
}

// ============ 辅助类 ============
public class QueryResult {
    private String dbType;
    private String query;
    private String[] columns;
    
    public QueryResult(String dbType, String query, String[] columns) {
        this.dbType = dbType;
        this.query = query;
        this.columns = columns;
    }
    
    public void print() {
        System.out.println("[" + dbType + " Result]");
        System.out.print("Columns: ");
        for (String col : columns) {
            System.out.print(col + ", ");
        }
        System.out.println();
    }
}

public class DatabaseException extends Exception {
    public DatabaseException(String message) { super(message); }
    public DatabaseException(String message, Throwable cause) { super(message, cause); }
}

// ============ 第三步：定义工厂接口 ============
public interface DatabaseFactory {
    Database createDatabase() throws DatabaseException;
}

// ============ 第四步：实现具体工厂 ============
public class MySQLFactory implements DatabaseFactory {
    private String host;
    private int port;
    private String database;
    
    public MySQLFactory() {
        this("localhost", 3306, "mydb");
    }
    
    public MySQLFactory(String host, int port, String database) {
        this.host = host;
        this.port = port;
        this.database = database;
    }
    
    @Override
    public Database createDatabase() throws DatabaseException {
        try {
            return new MySQLDatabase(host, port, database);
        } catch (Exception e) {
            throw new DatabaseException("Failed to create MySQL database", e);
        }
    }
}

public class PostgreSQLFactory implements DatabaseFactory {
    private String host;
    private int port;
    private String database;
    
    public PostgreSQLFactory() {
        this("localhost", 5432, "mydb");
    }
    
    public PostgreSQLFactory(String host, int port, String database) {
        this.host = host;
        this.port = port;
        this.database = database;
    }
    
    @Override
    public Database createDatabase() throws DatabaseException {
        try {
            return new PostgreSQLDatabase(host, port, database);
        } catch (Exception e) {
            throw new DatabaseException("Failed to create PostgreSQL database", e);
        }
    }
}

public class MongoDBFactory implements DatabaseFactory {
    private String host;
    private int port;
    private String database;
    
    public MongoDBFactory() {
        this("localhost", 27017, "mydb");
    }
    
    public MongoDBFactory(String host, int port, String database) {
        this.host = host;
        this.port = port;
        this.database = database;
    }
    
    @Override
    public Database createDatabase() throws DatabaseException {
        try {
            return new MongoDBDatabase(host, port, database);
        } catch (Exception e) {
            throw new DatabaseException("Failed to create MongoDB database", e);
        }
    }
}

// ============ 第五步：高级 - 参数化工厂 + 注册表（实现无需修改代码的扩展）============
public class ParameterizedDatabaseFactory {
    private static final Map<String, Supplier<DatabaseFactory>> REGISTRY = new ConcurrentHashMap<>();
    
    static {
        // 初始化注册表
        register("MYSQL", () -> new MySQLFactory());
        register("POSTGRESQL", () -> new PostgreSQLFactory());
        register("MONGODB", () -> new MongoDBFactory());
    }
    
    /**
     * 注册新的数据库工厂
     * @param type 数据库类型（大小写不敏感）
     * @param factorySupplier 工厂生成器
     */
    public static void register(String type, Supplier<DatabaseFactory> factorySupplier) {
        REGISTRY.put(type.toUpperCase(), factorySupplier);
        System.out.println("[Factory] Registered database type: " + type);
    }
    
    /**
     * 创建数据库连接
     * @param type 数据库类型
     * @return Database 实例
     * @throws DatabaseException 创建失败
     */
    public static Database create(String type) throws DatabaseException {
        Supplier<DatabaseFactory> factorySupplier = REGISTRY.get(type.toUpperCase());
        if (factorySupplier == null) {
            throw new DatabaseException(
                "Unsupported database type: " + type + 
                ". Available types: " + REGISTRY.keySet()
            );
        }
        return factorySupplier.get().createDatabase();
    }
    
    /**
     * 创建带参数的数据库（支持自定义连接信息）
     */
    public static Database createWithConfig(String type, DatabaseConfig config) throws DatabaseException {
        Supplier<DatabaseFactory> factorySupplier = REGISTRY.get(type.toUpperCase());
        if (factorySupplier == null) {
            throw new DatabaseException("Unsupported database type: " + type);
        }
        
        DatabaseFactory factory;
        switch (type.toUpperCase()) {
            case "MYSQL":
                factory = new MySQLFactory(config.getHost(), config.getPort(), config.getDatabase());
                break;
            case "POSTGRESQL":
                factory = new PostgreSQLFactory(config.getHost(), config.getPort(), config.getDatabase());
                break;
            case "MONGODB":
                factory = new MongoDBFactory(config.getHost(), config.getPort(), config.getDatabase());
                break;
            default:
                throw new DatabaseException("Unsupported database type: " + type);
        }
        
        return factory.createDatabase();
    }
    
    /**
     * 获取所有可用的数据库类型
     */
    public static Set<String> getAvailableTypes() {
        return new HashSet<>(REGISTRY.keySet());
    }
    
    /**
     * 移除已注册的数据库类型
     */
    public static void unregister(String type) {
        REGISTRY.remove(type.toUpperCase());
        System.out.println("[Factory] Unregistered database type: " + type);
    }
}

public class DatabaseConfig {
    private String host;
    private int port;
    private String database;
    private String user;
    private String password;
    private Map<String, String> options = new HashMap<>();
    
    // Builder 模式支持
    public static class Builder {
        private final DatabaseConfig config = new DatabaseConfig();
        
        public Builder host(String host) { config.host = host; return this; }
        public Builder port(int port) { config.port = port; return this; }
        public Builder database(String database) { config.database = database; return this; }
        public Builder user(String user) { config.user = user; return this; }
        public Builder password(String password) { config.password = password; return this; }
        public Builder option(String key, String value) { config.options.put(key, value); return this; }
        
        public DatabaseConfig build() {
            if (config.host == null) config.host = "localhost";
            if (config.port <= 0) config.port = 3306;
            if (config.database == null) config.database = "test";
            return config;
        }
    }
    
    public static Builder builder() { return new Builder(); }
    
    // Getters
    public String getHost() { return host; }
    public int getPort() { return port; }
    public String getDatabase() { return database; }
    public String getUser() { return user; }
    public String getPassword() { return password; }
    public Map<String, String> getOptions() { return options; }
}

// ============ 第六步：使用工厂 ============
public class DatabaseApplicationExample {
    
    public static void exampleBasicFactory() throws DatabaseException {
        System.out.println("\n========== Example 1: 基础工厂方法 ==========");
        
        // 创建 MySQL 数据库
        DatabaseFactory mysqlFactory = new MySQLFactory("db.example.com", 3306, "production");
        Database mysql = mysqlFactory.createDatabase();
        mysql.connect();
        mysql.query("SELECT * FROM users WHERE age > 18");
        mysql.disconnect();
    }
    
    public static void exampleParameterizedFactory() throws DatabaseException {
        System.out.println("\n========== Example 2: 参数化工厂（无需修改代码） ==========");
        
        // 运行时动态选择数据库类型
        String dbType = System.getProperty("db.type", "MYSQL");
        
        Database db = ParameterizedDatabaseFactory.create(dbType);
        db.connect();
        db.query("SELECT COUNT(*) FROM products");
        
        // 打印数据库元数据
        DatabaseMetadata metadata = db.getMetadata();
        System.out.println("Version: " + metadata.getVersion());
        System.out.println("Driver: " + metadata.getDriverName());
        System.out.println("Max Connections: " + metadata.getMaxConnections());
        
        db.disconnect();
    }
    
    public static void exampleWithConfig() throws DatabaseException {
        System.out.println("\n========== Example 3: 使用配置对象 ==========");
        
        DatabaseConfig config = DatabaseConfig.builder()
            .host("remote.db.server")
            .port(5432)
            .database("analytics")
            .user("analyst")
            .password("secret123")
            .option("ssl", "true")
            .build();
        
        Database db = ParameterizedDatabaseFactory.createWithConfig("POSTGRESQL", config);
        db.connect();
        db.query("SELECT * FROM events WHERE timestamp > NOW() - INTERVAL '1 day'");
        db.disconnect();
    }
    
    public static void main(String[] args) throws DatabaseException {
        exampleBasicFactory();
        exampleParameterizedFactory();
        exampleWithConfig();
        
        System.out.println("\n========== Available Database Types: ==========");
        System.out.println(ParameterizedDatabaseFactory.getAvailableTypes());
    }
}
```

### Python 实现 - 工厂方法 + 参数化工厂

```python
from abc import ABC, abstractmethod
from typing import Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import threading

# ============ 第一步：定义产品接口 ============

class Database(ABC):
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def query(self, sql: str) -> Dict:
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        pass
    
    @abstractmethod
    def get_metadata(self) -> 'DatabaseMetadata':
        pass

@dataclass
class DatabaseMetadata:
    version: str
    driver_name: str
    max_connections: int

# ============ 第二步：实现具体产品 ============

class MySQLDatabase(Database):
    def __init__(self, host: str = 'localhost', port: int = 3306, database: str = 'mydb'):
        self.host = host
        self.port = port
        self.database = database
        self.url = f"mysql+pymysql://{host}:{port}/{database}"
        self.connected = False
    
    def connect(self):
        print(f"[MySQL] Connecting to {self.url}")
        # 模拟连接逻辑
        self.connected = True
        print("[MySQL] Connected successfully")
    
    def query(self, sql: str) -> Dict:
        if not self.connected:
            raise Exception("Database not connected")
        print(f"[MySQL] Executing: {sql}")
        return {"rows": 100, "columns": ["id", "name", "email"]}
    
    def disconnect(self):
        print("[MySQL] Disconnecting")
        self.connected = False
    
    def get_type(self) -> str:
        return "MySQL"
    
    def get_metadata(self) -> DatabaseMetadata:
        return DatabaseMetadata(
            version="8.0.x",
            driver_name="pymysql",
            max_connections=151
        )

class PostgreSQLDatabase(Database):
    def __init__(self, host: str = 'localhost', port: int = 5432, database: str = 'mydb'):
        self.host = host
        self.port = port
        self.database = database
        self.url = f"postgresql://user@{host}:{port}/{database}"
        self.connected = False
    
    def connect(self):
        print(f"[PostgreSQL] Connecting to {self.url}")
        self.connected = True
        print("[PostgreSQL] Connected successfully")
    
    def query(self, sql: str) -> Dict:
        if not self.connected:
            raise Exception("Database not connected")
        print(f"[PostgreSQL] Executing: {sql}")
        return {"rows": 50, "columns": ["id", "name", "data", "json_field"]}
    
    def disconnect(self):
        print("[PostgreSQL] Disconnecting")
        self.connected = False
    
    def get_type(self) -> str:
        return "PostgreSQL"
    
    def get_metadata(self) -> DatabaseMetadata:
        return DatabaseMetadata(
            version="13.x",
            driver_name="psycopg2",
            max_connections=100
        )

class MongoDBDatabase(Database):
    def __init__(self, host: str = 'localhost', port: int = 27017, database: str = 'mydb'):
        self.host = host
        self.port = port
        self.database = database
        self.url = f"mongodb://{host}:{port}/{database}"
        self.connected = False
    
    def connect(self):
        print(f"[MongoDB] Connecting to {self.url}")
        self.connected = True
        print("[MongoDB] Connected successfully")
    
    def query(self, sql: str) -> Dict:
        if not self.connected:
            raise Exception("Database not connected")
        print(f"[MongoDB] Executing: {sql}")
        return {"documents": 1000, "collections": ["users", "products", "orders"]}
    
    def disconnect(self):
        print("[MongoDB] Disconnecting")
        self.connected = False
    
    def get_type(self) -> str:
        return "MongoDB"
    
    def get_metadata(self) -> DatabaseMetadata:
        return DatabaseMetadata(
            version="4.x/5.x",
            driver_name="pymongo",
            max_connections=1000
        )

# ============ 第三步：定义工厂接口 ============

class DatabaseFactory(ABC):
    @abstractmethod
    def create_database(self) -> Database:
        pass

# ============ 第四步：实现具体工厂 ============

class MySQLFactory(DatabaseFactory):
    def __init__(self, host: str = 'localhost', port: int = 3306, database: str = 'mydb'):
        self.host = host
        self.port = port
        self.database = database
    
    def create_database(self) -> Database:
        return MySQLDatabase(self.host, self.port, self.database)

class PostgreSQLFactory(DatabaseFactory):
    def __init__(self, host: str = 'localhost', port: int = 5432, database: str = 'mydb'):
        self.host = host
        self.port = port
        self.database = database
    
    def create_database(self) -> Database:
        return PostgreSQLDatabase(self.host, self.port, self.database)

class MongoDBFactory(DatabaseFactory):
    def __init__(self, host: str = 'localhost', port: int = 27017, database: str = 'mydb'):
        self.host = host
        self.port = port
        self.database = database
    
    def create_database(self) -> Database:
        return MongoDBDatabase(self.host, self.port, self.database)

# ============ 第五步：参数化工厂 + 注册表 ============

class DatabaseType(Enum):
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    MONGODB = "MONGODB"

class ParameterizedDatabaseFactory:
    _registry: Dict[str, type] = {}
    _lock = threading.Lock()
    
    @classmethod
    def register(cls, db_type: str, factory_class: type):
        with cls._lock:
            cls._registry[db_type.upper()] = factory_class
            print(f"[Factory] Registered database type: {db_type}")
    
    @classmethod
    def create(cls, db_type: str, **kwargs) -> Database:
        factory_class = cls._registry.get(db_type.upper())
        if not factory_class:
            raise ValueError(
                f"Unsupported database type: {db_type}. "
                f"Available: {cls.get_available_types()}"
            )
        factory = factory_class(**kwargs)
        return factory.create_database()
    
    @classmethod
    def get_available_types(cls) -> Set[str]:
        return set(cls._registry.keys())
    
    @classmethod
    def unregister(cls, db_type: str):
        with cls._lock:
            removed = cls._registry.pop(db_type.upper(), None)
            if removed:
                print(f"[Factory] Unregistered database type: {db_type}")

# 初始化默认注册表
ParameterizedDatabaseFactory.register("MYSQL", MySQLFactory)
ParameterizedDatabaseFactory.register("POSTGRESQL", PostgreSQLFactory)
ParameterizedDatabaseFactory.register("MONGODB", MongoDBFactory)

# ============ 第六步：使用示例 ============

def example_basic_factory():
    print("\n========== Example 1: 基础工厂方法 ==========")
    
    factory = MySQLFactory(host="db.example.com", port=3306, database="production")
    db = factory.create_database()
    db.connect()
    result = db.query("SELECT * FROM users WHERE age > 18")
    print(f"Query result: {result}")
    db.disconnect()

def example_parameterized_factory():
    print("\n========== Example 2: 参数化工厂 ==========")
    
    db = ParameterizedDatabaseFactory.create("POSTGRESQL", 
                                             host="remote.server",
                                             port=5432,
                                             database="analytics")
    db.connect()
    result = db.query("SELECT * FROM events")
    metadata = db.get_metadata()
    print(f"Metadata - Version: {metadata.version}, Driver: {metadata.driver_name}")
    db.disconnect()

def example_runtime_dbtype_selection():
    print("\n========== Example 3: 运行时数据库类型选择 ==========")
    
    # 从配置、环境变量等动态获取数据库类型
    db_type = "MONGODB"
    
    try:
        db = ParameterizedDatabaseFactory.create(db_type)
        db.connect()
        db.query("find({status: 'active'})")
        db.disconnect()
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    example_basic_factory()
    example_parameterized_factory()
    example_runtime_dbtype_selection()
    print("\nAvailable databases:", ParameterizedDatabaseFactory.get_available_types())
```

### TypeScript/JavaScript 实现 - 工厂方法 + 高级特性

```typescript
// ============ 第一步：定义产品接口 ============

interface DatabaseMetadata {
    version: string;
    driverName: string;
    maxConnections: number;
}

interface Database {
    connect(): Promise<void>;
    query(sql: string): Promise<QueryResult>;
    disconnect(): Promise<void>;
    getType(): string;
    getMetadata(): DatabaseMetadata;
}

interface QueryResult {
    rows: any[];
    columns: string[];
    affectedRows?: number;
}

// ============ 第二步：实现具体产品（使用 Class）============

class MySQLDatabase implements Database {
    private connected: boolean = false;
    private readonly url: string;
    
    constructor(
        private host: string = 'localhost',
        private port: number = 3306,
        private database: string = 'mydb'
    ) {
        this.url = `mysql://${host}:${port}/${database}`;
    }
    
    async connect(): Promise<void> {
        console.log(`[MySQL] Connecting to ${this.url}`);
        // 模拟异步连接
        await new Promise(resolve => setTimeout(resolve, 100));
        this.connected = true;
        console.log("[MySQL] Connected successfully");
    }
    
    async query(sql: string): Promise<QueryResult> {
        if (!this.connected) throw new Error("Database not connected");
        console.log(`[MySQL] Executing: ${sql}`);
        return {
            rows: [{id: 1, name: 'John'}, {id: 2, name: 'Jane'}],
            columns: ['id', 'name']
        };
    }
    
    async disconnect(): Promise<void> {
        console.log("[MySQL] Disconnecting");
        this.connected = false;
    }
    
    getType(): string { return "MySQL"; }
    
    getMetadata(): DatabaseMetadata {
        return {
            version: "8.0.x",
            driverName: "mysql2",
            maxConnections: 151
        };
    }
}

class PostgreSQLDatabase implements Database {
    private connected: boolean = false;
    private readonly url: string;
    
    constructor(
        private host: string = 'localhost',
        private port: number = 5432,
        private database: string = 'mydb'
    ) {
        this.url = `postgresql://${host}:${port}/${database}`;
    }
    
    async connect(): Promise<void> {
        console.log(`[PostgreSQL] Connecting to ${this.url}`);
        await new Promise(resolve => setTimeout(resolve, 150));
        this.connected = true;
        console.log("[PostgreSQL] Connected successfully");
    }
    
    async query(sql: string): Promise<QueryResult> {
        if (!this.connected) throw new Error("Database not connected");
        console.log(`[PostgreSQL] Executing: ${sql}`);
        return {
            rows: [{id: 1, name: 'Alice', json_data: {age: 30}}],
            columns: ['id', 'name', 'json_data']
        };
    }
    
    async disconnect(): Promise<void> {
        console.log("[PostgreSQL] Disconnecting");
        this.connected = false;
    }
    
    getType(): string { return "PostgreSQL"; }
    
    getMetadata(): DatabaseMetadata {
        return {
            version: "13.x",
            driverName: "pg",
            maxConnections: 100
        };
    }
}

class MongoDBDatabase implements Database {
    private connected: boolean = false;
    private readonly url: string;
    
    constructor(
        private host: string = 'localhost',
        private port: number = 27017,
        private database: string = 'mydb'
    ) {
        this.url = `mongodb://${host}:${port}/${database}`;
    }
    
    async connect(): Promise<void> {
        console.log(`[MongoDB] Connecting to ${this.url}`);
        await new Promise(resolve => setTimeout(resolve, 200));
        this.connected = true;
        console.log("[MongoDB] Connected successfully");
    }
    
    async query(sql: string): Promise<QueryResult> {
        if (!this.connected) throw new Error("Database not connected");
        console.log(`[MongoDB] Executing: ${sql}`);
        return {
            rows: [{_id: 'obj1', name: 'Bob', metadata: {created: new Date()}}],
            columns: ['_id', 'name', 'metadata']
        };
    }
    
    async disconnect(): Promise<void> {
        console.log("[MongoDB] Disconnecting");
        this.connected = false;
    }
    
    getType(): string { return "MongoDB"; }
    
    getMetadata(): DatabaseMetadata {
        return {
            version: "4.x/5.x",
            driverName: "mongodb",
            maxConnections: 1000
        };
    }
}

// ============ 第三步：定义工厂接口 ============

interface DatabaseFactory {
    createDatabase(): Database;
}

// ============ 第四步：实现具体工厂 ============

class MySQLFactory implements DatabaseFactory {
    constructor(
        private host: string = 'localhost',
        private port: number = 3306,
        private database: string = 'mydb'
    ) {}
    
    createDatabase(): Database {
        return new MySQLDatabase(this.host, this.port, this.database);
    }
}

class PostgreSQLFactory implements DatabaseFactory {
    constructor(
        private host: string = 'localhost',
        private port: number = 5432,
        private database: string = 'mydb'
    ) {}
    
    createDatabase(): Database {
        return new PostgreSQLDatabase(this.host, this.port, this.database);
    }
}

class MongoDBFactory implements DatabaseFactory {
    constructor(
        private host: string = 'localhost',
        private port: number = 27017,
        private database: string = 'mydb'
    ) {}
    
    createDatabase(): Database {
        return new MongoDBDatabase(this.host, this.port, this.database);
    }
}

// ============ 第五步：参数化工厂 + 类型安全 ============

type DatabaseType = 'MYSQL' | 'POSTGRESQL' | 'MONGODB';

class ParameterizedDatabaseFactory {
    private static factories: Map<DatabaseType, () => DatabaseFactory> = new Map([
        ['MYSQL', () => new MySQLFactory()],
        ['POSTGRESQL', () => new PostgreSQLFactory()],
        ['MONGODB', () => new MongoDBFactory()]
    ]);
    
    static create(type: DatabaseType, config?: any): Database {
        const factory = this.factories.get(type);
        if (!factory) {
            throw new Error(`Unsupported database type: ${type}`);
        }
        
        let dbFactory: DatabaseFactory;
        if (config) {
            switch (type) {
                case 'MYSQL':
                    dbFactory = new MySQLFactory(config.host, config.port, config.database);
                    break;
                case 'POSTGRESQL':
                    dbFactory = new PostgreSQLFactory(config.host, config.port, config.database);
                    break;
                case 'MONGODB':
                    dbFactory = new MongoDBFactory(config.host, config.port, config.database);
                    break;
                default:
                    throw new Error(`Unsupported database type: ${type}`);
            }
        } else {
            dbFactory = factory();
        }
        
        return dbFactory.createDatabase();
    }
    
    static register(type: DatabaseType, factory: () => DatabaseFactory): void {
        this.factories.set(type, factory);
        console.log(`[Factory] Registered database type: ${type}`);
    }
    
    static getAvailableTypes(): DatabaseType[] {
        return Array.from(this.factories.keys());
    }
}

// ============ 第六步：使用示例 ============

async function exampleBasicFactory() {
    console.log("\n========== Example 1: 基础工厂方法 ==========");
    
    const factory = new MySQLFactory("db.example.com", 3306, "production");
    const db = factory.createDatabase();
    
    await db.connect();
    const result = await db.query("SELECT * FROM users WHERE age > 18");
    console.log("Query result:", result);
    await db.disconnect();
}

async function exampleParameterizedFactory() {
    console.log("\n========== Example 2: 参数化工厂 ==========");
    
    const db = ParameterizedDatabaseFactory.create('POSTGRESQL', {
        host: 'remote.server',
        port: 5432,
        database: 'analytics'
    });
    
    await db.connect();
    const result = await db.query("SELECT * FROM events");
    const metadata = db.getMetadata();
    console.log(`Metadata - Version: ${metadata.version}, Driver: ${metadata.driverName}`);
    await db.disconnect();
}

async function exampleRuntimeTypeSelection() {
    console.log("\n========== Example 3: 运行时类型选择 ==========");
    
    const dbType: DatabaseType = (process.env.DB_TYPE || 'MYSQL') as DatabaseType;
    
    try {
        const db = ParameterizedDatabaseFactory.create(dbType);
        await db.connect();
        await db.query("SELECT * FROM data");
        await db.disconnect();
    } catch (error) {
        console.error("Error:", error);
    }
}

// 运行示例
async function main() {
    await exampleBasicFactory();
    await exampleParameterizedFactory();
    await exampleRuntimeTypeSelection();
    console.log("\nAvailable databases:", ParameterizedDatabaseFactory.getAvailableTypes());
}

main().catch(console.error);
```

---

## 单元测试示例

### Java 单元测试

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class DatabaseFactoryTest {
    
    @Test
    public void testMySQLFactoryCreateDatabase() throws DatabaseException {
        DatabaseFactory factory = new MySQLFactory("localhost", 3306, "testdb");
        Database db = factory.createDatabase();
        
        assertNotNull(db);
        assertEquals("MySQL", db.getType());
        assertTrue(db.getMetadata().getVersion().contains("8.0"));
    }
    
    @Test
    public void testPostgreSQLFactoryCreateDatabase() throws DatabaseException {
        DatabaseFactory factory = new PostgreSQLFactory("localhost", 5432, "testdb");
        Database db = factory.createDatabase();
        
        assertNotNull(db);
        assertEquals("PostgreSQL", db.getType());
        assertNotNull(db.getMetadata());
    }
    
    @Test
    public void testParameterizedFactoryInvalidType() {
        assertThrows(DatabaseException.class, () -> {
            ParameterizedDatabaseFactory.create("INVALID_TYPE");
        });
    }
    
    @Test
    public void testParameterizedFactoryAvailableTypes() {
        Set<String> types = ParameterizedDatabaseFactory.getAvailableTypes();
        assertTrue(types.contains("MYSQL"));
        assertTrue(types.contains("POSTGRESQL"));
        assertTrue(types.contains("MONGODB"));
    }
    
    @Test
    public void testDatabaseConnection() throws DatabaseException {
        Database db = ParameterizedDatabaseFactory.create("MYSQL");
        
        assertDoesNotThrow(() -> {
            db.connect();
            assertNotNull(db.query("SELECT 1"));
            db.disconnect();
        });
    }
    
    @Test
    public void testFactoryRegistration() throws DatabaseException {
        // 创建自定义数据库工厂
        class CustomDatabase implements Database {
            @Override public void connect() {}
            @Override public QueryResult query(String sql) { return new QueryResult("Custom", sql, new String[]{}); }
            @Override public void disconnect() {}
            @Override public String getType() { return "CUSTOM"; }
            @Override public DatabaseMetadata getMetadata() { return null; }
        }
        
        ParameterizedDatabaseFactory.register("CUSTOM", 
            () -> new DatabaseFactory() {
                @Override
                public Database createDatabase() { return new CustomDatabase(); }
            });
        
        Set<String> types = ParameterizedDatabaseFactory.getAvailableTypes();
        assertTrue(types.contains("CUSTOM"));
    }
}
```

### Python 单元测试

```python
import unittest
from typing import Optional

class TestDatabaseFactory(unittest.TestCase):
    
    def test_mysql_factory_creates_database(self):
        factory = MySQLFactory("localhost", 3306, "testdb")
        db = factory.create_database()
        
        self.assertIsNotNone(db)
        self.assertEqual(db.get_type(), "MySQL")
        self.assertIn("8.0", db.get_metadata().version)
    
    def test_parameterized_factory_invalid_type(self):
        with self.assertRaises(ValueError):
            ParameterizedDatabaseFactory.create("INVALID_TYPE")
    
    def test_parameterized_factory_available_types(self):
        types = ParameterizedDatabaseFactory.get_available_types()
        self.assertIn("MYSQL", types)
        self.assertIn("POSTGRESQL", types)
        self.assertIn("MONGODB", types)
    
    def test_database_connection(self):
        db = ParameterizedDatabaseFactory.create("MYSQL")
        
        db.connect()
        result = db.query("SELECT 1")
        self.assertIsNotNone(result)
        db.disconnect()
    
    def test_custom_database_registration(self):
        class CustomDatabase(Database):
            def connect(self): pass
            def query(self, sql): return {"result": "custom"}
            def disconnect(self): pass
            def get_type(self): return "CUSTOM"
            def get_metadata(self): return DatabaseMetadata(version="1.0", driver_name="custom", max_connections=10)
        
        class CustomFactory(DatabaseFactory):
            def create_database(self): return CustomDatabase()
        
        ParameterizedDatabaseFactory.register("CUSTOM", CustomFactory)
        types = ParameterizedDatabaseFactory.get_available_types()
        self.assertIn("CUSTOM", types)

if __name__ == '__main__':
    unittest.main()
```
