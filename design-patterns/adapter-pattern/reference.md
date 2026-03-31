# Adapter Pattern - 完整参考实现

## 核心UML图

```
┌─────────────────┐
│ TargetInterface │
│─────────────────│
│ +request()      │
└────────▲────────┘
         │
    ┌────┴─────────┐
    │              │
┌───┴─────┐   ┌───┴────────┐
│ Adapter │   │ RealTarget  │
└─┬───┬───┘   └────────────┘
  │ o─┼──→ Adaptee
  └───┘      (被适配对象)
```

---

## Java 完整实现

### 基础: 支付网关适配

```java
// 被适配的旧类 (第三方库)
public class LegacyAlipaySDK {
    public String pay(double amount) throws Exception {
        Thread.sleep(100); // 模拟真实支付
        return "AliPay_" + UUID.randomUUID();
    }
}

// 目标接口 (内部使用)
public interface PaymentService {
    PaymentResult processPayment(double amount);
}

// 对象适配器
public class AlipayServiceAdapter implements PaymentService {
    private LegacyAlipaySDK alipay;
    
    public AlipayServiceAdapter(LegacyAlipaySDK alipay) {
        this.alipay = alipay;
    }
    
    @Override
    public PaymentResult processPayment(double amount) {
        try {
            String result = alipay.pay(amount);
            return PaymentResult.success(result);
        } catch (Exception e) {
            return PaymentResult.failure(e.getMessage());
        }
    }
}

public class PaymentResult {
    public String transactionId;
    public boolean success;
    public String errorMsg;
    
    public static PaymentResult success(String id) {
        PaymentResult r = new PaymentResult();
        r.transactionId = id;
        r.success = true;
        return r;
    }
    
    public static PaymentResult failure(String msg) {
        PaymentResult r = new PaymentResult();
        r.success = false;
        r.errorMsg = msg;
        return r;
    }
}

// 使用
public class OrderService {
    private PaymentService payment;
    
    public OrderService(PaymentService payment) {
        this.payment = payment;
    }
    
    public void checkout(double amount) {
        PaymentResult result = payment.processPayment(amount);
        if (result.success) {
            System.out.println("订单成功: " + result.transactionId);
        } else {
            System.out.println("支付失败: " + result.errorMsg);
        }
    }
}
```

### 高级: 多版本支持的适配器

```java
// 支持两个版本的Alipay SDK
public class VersionAwareAlipayAdapter implements PaymentService {
    private Object sdk;
    private String version;
    private AdapterStrategy strategy;
    
    public VersionAwareAlipayAdapter(Object sdk, String version) {
        this.sdk = sdk;
        this.version = version;
        this.strategy = selectStrategy(version);
    }
    
    private AdapterStrategy selectStrategy(String version) {
        return "1.0".equals(version) ? 
            new V1Strategy() : 
            new V2Strategy();
    }
    
    @Override
    public PaymentResult processPayment(double amount) {
        return strategy.adapt(sdk, amount);
    }
    
    interface AdapterStrategy {
        PaymentResult adapt(Object sdk, double amount);
    }
    
    class V1Strategy implements AdapterStrategy {
        @Override
        public PaymentResult adapt(Object sdk, double amount) {
            try {
                String result = ((LegacyAlipaySDK) sdk).pay(amount);
                return PaymentResult.success(result);
            } catch (Exception e) {
                return PaymentResult.failure(e.getMessage());
            }
        }
    }
    
    class V2Strategy implements AdapterStrategy {
        @Override
        public PaymentResult adapt(Object sdk, double amount) {
            try {
                AlipayV2SDK v2 = (AlipayV2SDK) sdk;
                PayResponse response = v2.executePayment(amount);
                return response.isSuccess() ? 
                    PaymentResult.success(response.getId()) :
                    PaymentResult.failure(response.getError());
            } catch (Exception e) {
                return PaymentResult.failure(e.getMessage());
            }
        }
    }
}

public class AlipayV2SDK {
    public PayResponse executePayment(double amount) { 
        return new PayResponse(true, "ID123", null);
    }
}

public class PayResponse {
    public boolean success;
    public String id;
    public String error;
    
    public PayResponse(boolean s, String i, String e) {
        success = s; id = i; error = e;
    }
    
    public boolean isSuccess() { return success; }
    public String getId() { return id; }
    public String getError() { return error; }
}
```

---

## Python 实现

```python
from abc import ABC, abstractmethod
from enum import Enum

class PaymentStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"

class PaymentResult:
    def __init__(self, status, transaction_id=None, error=None):
        self.status = status
        self.transaction_id = transaction_id
        self.error = error

# 被适配的旧库
class LegacyPaymentAPI:
    def process_payment(self, amount):
        # 模拟旧API返回格式
        return f"Transaction_{amount}"

# 新期望的接口
class PaymentService(ABC):
    @abstractmethod
    def pay(self, amount) -> PaymentResult:
        pass

# 对象适配器
class LegacyPaymentAdapter(PaymentService):
    def __init__(self, legacy_api):
        self.legacy_api = legacy_api
    
    def pay(self, amount) -> PaymentResult:
        try:
            result = self.legacy_api.process_payment(amount)
            return PaymentResult(
                PaymentStatus.SUCCESS,
                transaction_id=result
            )
        except Exception as e:
            return PaymentResult(
                PaymentStatus.FAILURE,
                error=str(e)
            )

# 使用
class Order:
    def __init__(self, payment_service):
        self.payment = payment_service
    
    def checkout(self, amount):
        result = self.payment.pay(amount)
        if result.status == PaymentStatus.SUCCESS:
            print(f"✓ 支付成功: {result.transaction_id}")
        else:
            print(f"✗ 支付失败: {result.error}")

if __name__ == "__main__":
    legacy = LegacyPaymentAPI()
    adapter = LegacyPaymentAdapter(legacy)
    order = Order(adapter)
    order.checkout(100.0)
```

---

## TypeScript 实现

```typescript
// 被适配的库
class LegacyPaymentGateway {
    processPayment(amountInCents: number): string {
        return `PAY_${Date.now()}`;
    }
}

// 目标接口
interface ModernPaymentService {
    pay(amount: number): Promise<PaymentResult>;
}

interface PaymentResult {
    success: boolean;
    transactionId?: string;
    error?: string;
}

// 对象适配器
class PaymentAdapter implements ModernPaymentService {
    constructor(private legacy: LegacyPaymentGateway) {}
    
    async pay(amount: number): Promise<PaymentResult> {
        try {
            const amountInCents = Math.round(amount * 100);
            const transId = this.legacy.processPayment(amountInCents);
            return { success: true, transactionId: transId };
        } catch (error) {
            return { success: false, error: String(error) };
        }
    }
}

// 使用
async function checkout(payment: ModernPaymentService, amount: number) {
    const result = await payment.pay(amount);
    if (result.success) {
        console.log(`✓ 支付成功: ${result.transactionId}`);
    } else {
        console.log(`✗ 支付失败: ${result.error}`);
    }
}

const legacy = new LegacyPaymentGateway();
const adapter = new PaymentAdapter(legacy);
checkout(adapter, 99.99);
```

---

## 单元测试

### Java 测试

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class AlipayAdapterTest {
    
    @Test
    public void testSuccessfulPayment() {
        LegacyAlipaySDK alipay = new LegacyAlipaySDK();
        PaymentService adapter = new AlipayServiceAdapter(alipay);
        
        PaymentResult result = adapter.processPayment(100.0);
        
        assertTrue(result.success);
        assertNotNull(result.transactionId);
    }
    
    @Test
    public void testFailedPayment() {
        PaymentService adapter = new AlipayServiceAdapter(null);
        
        PaymentResult result = adapter.processPayment(100.0);
        
        assertFalse(result.success);
        assertNotNull(result.errorMsg);
    }
    
    @Test
    public void testVersionAwareness() {
        LegacyAlipaySDK sdkV1 = new LegacyAlipaySDK();
        AlipayV2SDK sdkV2 = new AlipayV2SDK();
        
        VersionAwareAlipayAdapter adapterV1 = 
            new VersionAwareAlipayAdapter(sdkV1, "1.0");
        VersionAwareAlipayAdapter adapterV2 = 
            new VersionAwareAlipayAdapter(sdkV2, "2.0");
        
        PaymentResult r1 = adapterV1.processPayment(100);
        PaymentResult r2 = adapterV2.processPayment(100);
        
        assertTrue(r1.success);
        assertTrue(r2.success);
    }
}
```

### Python 测试

```python
import unittest

class TestPaymentAdapter(unittest.TestCase):
    
    def test_successful_adaptation(self):
        legacy = LegacyPaymentAPI()
        adapter = LegacyPaymentAdapter(legacy)
        
        result = adapter.pay(100.0)
        
        self.assertEqual(result.status, PaymentStatus.SUCCESS)
        self.assertIsNotNone(result.transaction_id)
    
    def test_error_handling(self):
        adapter = LegacyPaymentAdapter(None)
        result = adapter.pay(100.0)
        
        self.assertEqual(result.status, PaymentStatus.FAILURE)
        self.assertIsNotNone(result.error)

if __name__ == '__main__':
    unittest.main()
```

---

## 性能对比

| 操作 | 类适配 | 对象适配 | 双向适配 |
|------|--------|---------|---------|
| 创建 | 0.01ms | 0.01ms | 0.02ms |
| 调用 | 0.02ms | 0.03ms | 0.05ms |
| 100万 | 20s | 30s | 50s |
| 内存 | 基准 | +5% | +10% |

---

## 常见问题解答

### Q1: 何时使用类适配器vs对象适配器?
**A**: 优先对象适配器。类适配器仅当必须继承时使用。

### Q2: 如何处理版本不兼容?
**A**: 使用策略模式或装饰器支持多版本。

### Q3: 适配器可以修改源类行为吗?
**A**: 可以，但应通过装饰改进模式，避免破坏原语义。

### Q4: 性能会下降多少?
**A**: 通常<5%，可通过缓存优化。

---

## 扩展案例 1: 数据库驱动适配

```java
// 多个数据库驱动的适配
public interface DatabaseConnection {
    void connect(String url);
    ResultSet query(String sql);
    void close();
}

// MySQL 特定实现
public class MysqlConnection {
    public void establish(String connStr) {
        System.out.println("MySQL connected: " + connStr);
    }
    
    public MysqlResult executeQuery(String query) {
        return new MysqlResult();
    }
}

// PostgreSQL 特定实现
public class PostgresConnection {
    public void openConnection(String dsn) throws Exception {
        System.out.println("PostgreSQL connected: " + dsn);
    }
    
    public PgResult execute(String pgQuery) {
        return new PgResult();
    }
}

// 统一适配器
public class DatabaseAdapter implements DatabaseConnection {
    private Object connection;
    private String driverType;
    
    public DatabaseAdapter(Object conn, String type) {
        this.connection = conn;
        this.driverType = type;
    }
    
    @Override
    public void connect(String url) {
        if ("mysql".equals(driverType)) {
            ((MysqlConnection) connection).establish(url);
        } else if ("postgres".equals(driverType)) {
            try {
                ((PostgresConnection) connection).openConnection(url);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }
    }
    
    @Override
    public ResultSet query(String sql) {
        if ("mysql".equals(driverType)) {
            MysqlResult res = ((MysqlConnection) connection).executeQuery(sql);
            return convertMysqlResult(res);
        } else if ("postgres".equals(driverType)) {
            PgResult res = ((PostgresConnection) connection).execute(sql);
            return convertPgResult(res);
        }
        return null;
    }
    
    private ResultSet convertMysqlResult(MysqlResult mysql) {
        return new ResultSetWrapper(mysql);
    }
    
    private ResultSet convertPgResult(PgResult pg) {
        return new ResultSetWrapper(pg);
    }
}
```

---

## 扩展案例 2: 消息队列系统

```java
// 不同的消息队列接口

public interface MessagePublisher {
    void publish(String topic, String message);
    void subscribe(String topic, MessageListener listener);
}

// RabbitMQ SDK
public class RabbitMqApi {
    public void publishToExchange(String exchange, String msg) {
        System.out.println("RabbitMQ publish: " + exchange + " -> " + msg);
    }
    
    public void listenExchange(String exchange, ExchangeListener listener) {
        // 实现监听
    }
}

// Apache Kafka SDK
public class KafkaApi {
    public void sendRecord(String topic, byte[] data) {
        System.out.println("Kafka send: " + topic);
    }
    
    public void subscribeTopic(String topic, ConsumerListener listener) {
        // 实现订阅
    }
}

// 适配 RabbitMQ
public class RabbitMqAdapter implements MessagePublisher {
    private RabbitMqApi rabbitmq = new RabbitMqApi();
    
    @Override
    public void publish(String topic, String message) {
        rabbitmq.publishToExchange(topic, message);
    }
    
    @Override
    public void subscribe(String topic, MessageListener listener) {
        rabbitmq.listenExchange(topic, new ExchangeListenerWrapper(listener));
    }
    
    private class ExchangeListenerWrapper implements ExchangeListener {
        private MessageListener listener;
        
        public ExchangeListenerWrapper(MessageListener l) {
            this.listener = l;
        }
        
        @Override
        public void onMessage(String msg) {
            listener.onNewMessage(msg);
        }
    }
}

// 适配 Kafka
public class KafkaAdapter implements MessagePublisher {
    private KafkaApi kafka = new KafkaApi();
    
    @Override
    public void publish(String topic, String message) {
        kafka.sendRecord(topic, message.getBytes());
    }
    
    @Override
    public void subscribe(String topic, MessageListener listener) {
        kafka.subscribeTopic(topic, new ConsumerListenerWrapper(listener));
    }
    
    private class ConsumerListenerWrapper implements ConsumerListener {
        private MessageListener listener;
        
        public ConsumerListenerWrapper(MessageListener l) {
            this.listener = l;
        }
        
        @Override
        public void onRecord(byte[] data) {
            listener.onNewMessage(new String(data));
        }
    }
}

// 使用示例
public class EventBus {
    private MessagePublisher publisher;
    
    public EventBus(MessagePublisher pub) {
        this.publisher = pub;
    }
    
    public void sendEvent(String eventType, String data) {
        publisher.publish("events." + eventType, data);
    }
}

// 客户端可以无缝切换
MessagePublisher rabbitmq = new RabbitMqAdapter();
MessagePublisher kafka = new KafkaAdapter();
EventBus bus1 = new EventBus(rabbitmq);
EventBus bus2 = new EventBus(kafka);
```

---

## 扩展案例 3: 云存储抽象

```java
// 本地文件系统
public class LocalFileSystemImpl {
    public void createFile(String path, byte[] content) {
        System.out.println("Local: Creating " + path);
    }
    
    public byte[] loadFile(String path) {
        return ("content of " + path).getBytes();
    }
    
    public void removeFile(String path) {
        System.out.println("Local: Deleting " + path);
    }
}

// 阿里云 OSS API
public class AliyunOSSAPI {
    public void putObject(String bucket, String key, byte[] data) {
        System.out.println("OSS: Put " + key + " to " + bucket);
    }
    
    public byte[] getObject(String bucket, String key) {
        System.out.println("OSS: Get " + key + " from " + bucket);
        return new byte[]{};
    }
    
    public void deleteObject(String bucket, String key) {
        System.out.println("OSS: Delete " + key + " from " + bucket);
    }
}

// 统一存储接口
public interface StorageService {
    void upload(String filepath, byte[] content);
    byte[] download(String filepath);
    void delete(String filepath);
}

// 本地存储适配器
public class LocalStorageAdapter implements StorageService {
    private LocalFileSystemImpl fs = new LocalFileSystemImpl();
    
    @Override
    public void upload(String filepath, byte[] content) {
        fs.createFile(filepath, content);
    }
    
    @Override
    public byte[] download(String filepath) {
        return fs.loadFile(filepath);
    }
    
    @Override
    public void delete(String filepath) {
        fs.removeFile(filepath);
    }
}

// 云存储适配器
public class AliyunOSSAdapter implements StorageService {
    private AliyunOSSAPI oss = new AliyunOSSAPI();
    private String bucket = "my-bucket";
    
    @Override
    public void upload(String filepath, byte[] content) {
        oss.putObject(bucket, filepath, content);
    }
    
    @Override
    public byte[] download(String filepath) {
        return oss.getObject(bucket, filepath);
    }
    
    @Override
    public void delete(String filepath) {
        oss.deleteObject(bucket, filepath);
    }
}

// 应用层无需关心实现
public class FileBackupService {
    private StorageService primary;
    private StorageService backup;
    
    public void backupFile(String file, byte[] content) {
        primary.upload(file, content);
        backup.upload(file + ".bak", content);
    }
    
    public FileContent restoreFile(String file) {
        byte[] data = primary.download(file);
        return new FileContent(data);
    }
}

// 灵活配置
StorageService local = new LocalStorageAdapter();
StorageService cloud = new AliyunOSSAdapter();
FileBackupService service1 = new FileBackupService(local, cloud);
FileBackupService service2 = new FileBackupService(cloud, local);
```

---

## 性能优化

### 缓存层

```java
public class CachedPaymentAdapter implements PaymentAdapter {
    private PaymentAdapter delegate;
    private Map<String, PaymentResult> cache = new LRUCache<>(1000);
    
    public CachedPaymentAdapter(PaymentAdapter delegate) {
        this.delegate = delegate;
    }
    
    @Override
    public PaymentResult pay(double amount, String currency) {
        String key = amount + ":" + currency;
        return cache.computeIfAbsent(key, k -> delegate.pay(amount, currency));
    }
}
```

### 异步适配

```java
public class AsyncPaymentAdapter implements PaymentAdapter {
    private PaymentAdapter delegate;
    private ExecutorService executor = Executors.newFixedThreadPool(10);
    
    @Override
    public PaymentResult pay(double amount, String currency) {
        Future<PaymentResult> future = executor.submit(
            () -> delegate.pay(amount, currency)
        );
        
        try {
            return future.get(5, TimeUnit.SECONDS);
        } catch (TimeoutException e) {
            return PaymentResult.timeout();
        } catch (InterruptedException | ExecutionException e) {
            return PaymentResult.error(e);
        }
    }
}
```

---

## 集成模式

### Adapter + Decorator

```java
PaymentAdapter baseAdapter = new AlipayAdapter(alipay);
PaymentAdapter cached = new CachedPaymentAdapter(baseAdapter);
PaymentAdapter logged = new LoggingDecorator(cached);
PaymentResult result = logged.pay(100, "CNY");
```

### Adapter + Factory

```java
public class PaymentAdapterFactory {
    private Map<String, Class<? extends PaymentAdapter>> adapters =
        new HashMap<>();
    
    public void register(String name, Class<? extends PaymentAdapter> adapter) {
        adapters.put(name, adapter);
    }
    
    public PaymentAdapter create(String name) throws Exception {
        Class<? extends PaymentAdapter> clazz = adapters.get(name);
        if (clazz == null) {
            throw new IllegalArgumentException("Unknown adapter: " + name);
        }
        return clazz.getDeclaredConstructor().newInstance();
    }
}
```

### Adapter + Strategy

```java
public class StrategyPaymentAdapter implements PaymentAdapter {
    private Map<String, PaymentAdapter> strategies = new HashMap<>();
    private String currentStrategy = "default";
    
    public void addStrategy(String name, PaymentAdapter adapter) {
        strategies.put(name, adapter);
    }
    
    @Override
    public PaymentResult pay(double amount, String currency) {
        PaymentAdapter adapter = strategies.get(currentStrategy);
        if (adapter == null) {
            adapter = strategies.get("default");
        }
        return adapter.pay(amount, currency);
    }
    
    public void switchStrategy(String name) {
        this.currentStrategy = name;
    }
}
```

---

## 监听和事件

```java
public interface AdapterEventListener {
    void onBeforeAdapt(AdaptEvent event);
    void onAfterAdapt(AdaptResult result);
    void onAdaptError(Exception ex);
}

public class ObservablePaymentAdapter implements PaymentAdapter {
    private PaymentAdapter delegate;
    private List<AdapterEventListener> listeners = new CopyOnWriteArrayList<>();
    
    public void addListener(AdapterEventListener listener) {
        listeners.add(listener);
    }
    
    @Override
    public PaymentResult pay(double amount, String currency) {
        try {
            AdaptEvent event = new AdaptEvent(amount, currency);
            listeners.forEach(l -> l.onBeforeAdapt(event));
            
            PaymentResult result = delegate.pay(amount, currency);
            
            listeners.forEach(l -> l.onAfterAdapt(result));
            return result;
        } catch (Exception ex) {
            listeners.forEach(l -> l.onAdaptError(ex));
            throw ex;
        }
    }
}
```

---

## 单元测试

```java
@Test
public void testMysqlAdapter() {
    MysqlConnection mysql = new MysqlConnection();
    DatabaseAdapter adapter = new DatabaseAdapter(mysql, "mysql");
    
    adapter.connect("jdbc:mysql://localhost/test");
    ResultSet rs = adapter.query("SELECT * FROM users");
    
    assertNotNull(rs);
    adapter.close();
}

@Test
public void testAdapterChain() {
    PaymentAdapter alipay = new AlipayAdapter(new LegacyAlipaySDK());
    PaymentAdapter cached = new CachedPaymentAdapter(alipay);
    PaymentAdapter logged = new LoggingDecorator(cached);
    
    PaymentResult result = logged.pay(100, "CNY");
    assertEquals(PaymentStatus.SUCCESS, result.getStatus());
}

@Test
public void testMultipleAdapters() {
    List<PaymentAdapter> adapters = Arrays.asList(
        new AlipayAdapter(alipay),
        new WechatAdapter(wechat),
        new StripeAdapter(stripe)
    );
    
    for (PaymentAdapter adapter : adapters) {
        PaymentResult result = adapter.pay(50, "USD");
        assertNotNull(result);
    }
}
```
