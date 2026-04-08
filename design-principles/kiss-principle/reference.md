# KISS原则 - 参考实现

## 核心原理与设计

KISS（Keep It Simple, Stupid）原则的核心思想：**用最简单的方式解决当前问题，避免引入不必要的复杂度**。

### 关键设计要点

| 要点 | 说明 | 判断标准 |
|------|------|---------|
| 避免过度工程 | 不为"未来可能的需求"提前设计 | 当前是否有明确需求 |
| 优先标准库 | 用语言内置功能替代自定义实现 | 标准库是否已提供 |
| 减少抽象层 | 每一层抽象都必须有明确理由 | 去掉这层是否影响功能 |
| 直接表达意图 | 代码应该直接反映业务逻辑 | 新人能否快速理解 |
| 小方法优于大方法 | 每个方法只做一件事 | 能否用一句话描述方法功能 |

### KISS 与其他原则的关系

```
KISS ←→ YAGNI：都反对过度设计，YAGNI 关注"不需要的功能"，KISS 关注"不必要的复杂度"
KISS ←→ DRY：DRY 消除重复，但过度 DRY 会违反 KISS（为消除微小重复引入复杂抽象）
KISS ←→ SOLID：SOLID 指导结构设计，但不应为遵循 SOLID 而过度拆分简单逻辑
```

---

## Java 参考实现

### 场景1: 数字分类器 - 工厂模式的滥用

```java
// ❌ 过度设计：为简单的奇偶判断创建工厂 + 策略体系

public interface NumberClassifier {
    String classify(int number);
}

public class EvenClassifier implements NumberClassifier {
    @Override
    public String classify(int number) {
        return number % 2 == 0 ? "偶数" : null;
    }
}

public class OddClassifier implements NumberClassifier {
    @Override
    public String classify(int number) {
        return number % 2 != 0 ? "奇数" : null;
    }
}

public class PositiveClassifier implements NumberClassifier {
    @Override
    public String classify(int number) {
        return number > 0 ? "正数" : null;
    }
}

public class NegativeClassifier implements NumberClassifier {
    @Override
    public String classify(int number) {
        return number < 0 ? "负数" : null;
    }
}

public class NumberClassifierFactory {
    private static final Map<String, Supplier<NumberClassifier>> REGISTRY = new HashMap<>();

    static {
        REGISTRY.put("even", EvenClassifier::new);
        REGISTRY.put("odd", OddClassifier::new);
        REGISTRY.put("positive", PositiveClassifier::new);
        REGISTRY.put("negative", NegativeClassifier::new);
    }

    public static NumberClassifier create(String type) {
        Supplier<NumberClassifier> supplier = REGISTRY.get(type);
        if (supplier == null) {
            throw new IllegalArgumentException("未知分类器: " + type);
        }
        return supplier.get();
    }
}

public class NumberClassifierChain {
    private final List<NumberClassifier> classifiers;

    public NumberClassifierChain(List<String> types) {
        this.classifiers = types.stream()
            .map(NumberClassifierFactory::create)
            .collect(Collectors.toList());
    }

    public List<String> classify(int number) {
        return classifiers.stream()
            .map(c -> c.classify(number))
            .filter(Objects::nonNull)
            .collect(Collectors.toList());
    }
}

// 使用: 60+ 行代码，只为判断奇偶
NumberClassifierChain chain = new NumberClassifierChain(
    List.of("even", "odd", "positive", "negative")
);
List<String> result = chain.classify(42);  // ["偶数", "正数"]
```

```java
// ✅ KISS：直接用简单方法

public class NumberUtils {

    public static boolean isEven(int number) {
        return number % 2 == 0;
    }

    public static boolean isPositive(int number) {
        return number > 0;
    }

    public static List<String> classify(int number) {
        List<String> labels = new ArrayList<>();
        labels.add(isEven(number) ? "偶数" : "奇数");
        if (number > 0) labels.add("正数");
        else if (number < 0) labels.add("负数");
        else labels.add("零");
        return labels;
    }
}

// 使用: 清晰直接
List<String> result = NumberUtils.classify(42);  // ["偶数", "正数"]
```

**对比分析**:
- 过度设计版：7 个类/接口，60+ 行代码
- KISS 版：1 个工具类，15 行代码
- 行为完全一致，KISS 版更容易理解和维护

---

### 场景2: 复杂嵌套条件 vs Early Return

```java
// ❌ 过度嵌套的权限检查
public class PermissionChecker {

    public boolean canAccessResource(User user, Resource resource) {
        if (user != null) {
            if (user.isActive()) {
                if (resource != null) {
                    if (resource.isPublic()) {
                        return true;
                    } else {
                        if (user.getRoles() != null) {
                            for (Role role : user.getRoles()) {
                                if (role.getPermissions() != null) {
                                    for (Permission perm : role.getPermissions()) {
                                        if (perm.getResourceType().equals(resource.getType())) {
                                            if (perm.getAction().equals("read")
                                                || perm.getAction().equals("admin")) {
                                                return true;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        return false;
                    }
                } else {
                    return false;
                }
            } else {
                return false;
            }
        } else {
            return false;
        }
    }
}
```

```java
// ✅ KISS：使用 early return + 提取方法
public class PermissionChecker {

    public boolean canAccessResource(User user, Resource resource) {
        if (user == null || !user.isActive()) return false;
        if (resource == null) return false;
        if (resource.isPublic()) return true;
        return hasPermission(user, resource);
    }

    private boolean hasPermission(User user, Resource resource) {
        if (user.getRoles() == null) return false;

        return user.getRoles().stream()
            .filter(role -> role.getPermissions() != null)
            .flatMap(role -> role.getPermissions().stream())
            .anyMatch(perm ->
                perm.getResourceType().equals(resource.getType())
                && Set.of("read", "admin").contains(perm.getAction())
            );
    }
}
```

**对比分析**:
- 过度嵌套版：最大嵌套深度 8 层，圈复杂度 10+
- KISS 版：最大嵌套深度 2 层，逻辑清晰分层

---

### 场景3: 不必要的 StringFormatter 接口体系

```java
// ❌ 过度设计：为字符串格式化创建完整的接口体系
public interface StringFormatter {
    String format(String input);
}

public interface FormatterConfig {
    boolean isEnabled();
    Map<String, String> getOptions();
}

public class DefaultFormatterConfig implements FormatterConfig {
    private boolean enabled = true;
    private Map<String, String> options = new HashMap<>();

    @Override
    public boolean isEnabled() { return enabled; }

    @Override
    public Map<String, String> getOptions() { return options; }

    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public void addOption(String key, String value) { options.put(key, value); }
}

public class TrimFormatter implements StringFormatter {
    @Override
    public String format(String input) {
        return input != null ? input.trim() : null;
    }
}

public class UpperCaseFormatter implements StringFormatter {
    @Override
    public String format(String input) {
        return input != null ? input.toUpperCase() : null;
    }
}

public class FormatterPipeline {
    private final List<StringFormatter> formatters = new ArrayList<>();
    private final FormatterConfig config;

    public FormatterPipeline(FormatterConfig config) {
        this.config = config;
    }

    public void addFormatter(StringFormatter formatter) {
        formatters.add(formatter);
    }

    public String format(String input) {
        if (!config.isEnabled()) return input;
        String result = input;
        for (StringFormatter formatter : formatters) {
            result = formatter.format(result);
        }
        return result;
    }
}

// 使用
DefaultFormatterConfig config = new DefaultFormatterConfig();
FormatterPipeline pipeline = new FormatterPipeline(config);
pipeline.addFormatter(new TrimFormatter());
pipeline.addFormatter(new UpperCaseFormatter());
String result = pipeline.format("  hello world  ");  // "HELLO WORLD"
```

```java
// ✅ KISS：直接调用标准库方法
String result = "  hello world  ".trim().toUpperCase();  // "HELLO WORLD"
```

**对比分析**:
- 过度设计版：5 个类/接口，50+ 行代码
- KISS 版：1 行代码
- 如果未来确实需要可配置的格式化管道，再重构也来得及

---

## Python 参考实现

### 场景1: 比较策略 - 为 max() 创建策略模式

```python
# ❌ 过度设计：为简单的最大值比较创建策略体系
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

T = TypeVar('T')


class ComparatorStrategy(ABC, Generic[T]):
    """比较策略抽象基类"""

    @abstractmethod
    def compare(self, a: T, b: T) -> int:
        """返回正数表示 a > b，负数表示 a < b，0 表示相等"""
        pass


class IntegerComparator(ComparatorStrategy[int]):
    def compare(self, a: int, b: int) -> int:
        return a - b


class StringLengthComparator(ComparatorStrategy[str]):
    def compare(self, a: str, b: str) -> int:
        return len(a) - len(b)


class MaxFinder(Generic[T]):
    """使用策略模式查找最大值"""

    def __init__(self, comparator: ComparatorStrategy[T]):
        self._comparator = comparator

    def find_max(self, items: List[T]) -> T:
        if not items:
            raise ValueError("列表不能为空")
        result = items[0]
        for item in items[1:]:
            if self._comparator.compare(item, result) > 0:
                result = item
        return result


class MaxFinderFactory:
    """最大值查找器工厂"""

    @staticmethod
    def create_int_finder() -> MaxFinder[int]:
        return MaxFinder(IntegerComparator())

    @staticmethod
    def create_string_length_finder() -> MaxFinder[str]:
        return MaxFinder(StringLengthComparator())


# 使用
finder = MaxFinderFactory.create_int_finder()
result = finder.find_max([3, 1, 4, 1, 5, 9, 2, 6])  # 9

length_finder = MaxFinderFactory.create_string_length_finder()
longest = length_finder.find_max(["cat", "elephant", "dog"])  # "elephant"
```

```python
# ✅ KISS：直接使用内置函数
result = max([3, 1, 4, 1, 5, 9, 2, 6])  # 9
longest = max(["cat", "elephant", "dog"], key=len)  # "elephant"
```

**对比分析**:
- 过度设计版：5 个类，40+ 行代码
- KISS 版：2 行代码
- Python 的 `max()` 内置 `key` 参数已经覆盖了自定义比较需求

---

### 场景2: 配置加载器的过度工程化

```python
# ❌ 过度设计：为读取一个 JSON 配置文件创建插件架构
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
import os


class ConfigSource(ABC):
    """配置源抽象"""

    @abstractmethod
    def load(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def supports(self, path: str) -> bool:
        pass


class JsonConfigSource(ConfigSource):
    def __init__(self, file_path: str):
        self._file_path = file_path

    def load(self) -> Dict[str, Any]:
        with open(self._file_path, 'r') as f:
            return json.load(f)

    def supports(self, path: str) -> bool:
        return path.endswith('.json')


class ConfigValidator(ABC):
    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> bool:
        pass


class RequiredFieldsValidator(ConfigValidator):
    def __init__(self, required_fields: list):
        self._required_fields = required_fields

    def validate(self, config: Dict[str, Any]) -> bool:
        return all(field in config for field in self._required_fields)


class ConfigMerger:
    """配置合并器"""

    def merge(self, base: Dict, override: Dict) -> Dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge(result[key], value)
            else:
                result[key] = value
        return result


class ConfigLoader:
    """配置加载器"""

    def __init__(self):
        self._sources: list[ConfigSource] = []
        self._validators: list[ConfigValidator] = []
        self._merger = ConfigMerger()
        self._cache: Optional[Dict] = None

    def add_source(self, source: ConfigSource):
        self._sources.append(source)
        return self

    def add_validator(self, validator: ConfigValidator):
        self._validators.append(validator)
        return self

    def load(self) -> Dict[str, Any]:
        if self._cache is not None:
            return self._cache

        config = {}
        for source in self._sources:
            data = source.load()
            config = self._merger.merge(config, data)

        for validator in self._validators:
            if not validator.validate(config):
                raise ValueError("配置验证失败")

        self._cache = config
        return config

    def get(self, key: str, default: Any = None) -> Any:
        config = self.load()
        keys = key.split('.')
        result = config
        for k in keys:
            if isinstance(result, dict) and k in result:
                result = result[k]
            else:
                return default
        return result


# 使用
loader = ConfigLoader()
loader.add_source(JsonConfigSource("config.json"))
loader.add_validator(RequiredFieldsValidator(["database", "port"]))
config = loader.load()
db_host = loader.get("database.host", "localhost")
```

```python
# ✅ KISS：直接读取 JSON 配置
import json
from pathlib import Path


def load_config(path: str = "config.json") -> dict:
    """加载 JSON 配置文件。"""
    config_file = Path(path)
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with open(config_file) as f:
        return json.load(f)


# 使用
config = load_config()
db_host = config.get("database", {}).get("host", "localhost")
```

**对比分析**:
- 过度设计版：6 个类，80+ 行代码，支持多配置源合并、验证、缓存
- KISS 版：1 个函数，8 行代码
- 当项目只需要读取一个 JSON 文件时，插件架构完全是浪费
- 如果未来需要多配置源，使用 `python-dotenv` 或 `dynaconf` 等成熟库

---

### 场景3: 过度封装的 HTTP 客户端

```python
# ❌ 过度设计
class HttpMethod:
    GET = "GET"
    POST = "POST"

class HttpRequest:
    def __init__(self, method: str, url: str, headers: dict = None, body: dict = None):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.body = body

class HttpResponse:
    def __init__(self, status: int, body: dict):
        self.status = status
        self.body = body

class HttpClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._default_headers = {}

    def set_default_header(self, key: str, value: str):
        self._default_headers[key] = value

    def execute(self, request: HttpRequest) -> HttpResponse:
        import requests
        headers = {**self._default_headers, **request.headers}
        resp = requests.request(
            request.method, self._base_url + request.url,
            headers=headers, json=request.body
        )
        return HttpResponse(resp.status_code, resp.json())

# 使用
client = HttpClient("https://api.example.com")
client.set_default_header("Authorization", "Bearer token")
req = HttpRequest(HttpMethod.GET, "/users/1")
resp = client.execute(req)
print(resp.body)
```

```python
# ✅ KISS：直接使用 requests 库
import requests

resp = requests.get(
    "https://api.example.com/users/1",
    headers={"Authorization": "Bearer token"}
)
data = resp.json()
```

---

## TypeScript 参考实现

### 场景1: 不必要的事件总线

```typescript
// ❌ 过度设计：为组件间通信自建事件总线

type EventHandler = (data: any) => void;

class EventBus {
    private handlers: Map<string, EventHandler[]> = new Map();

    on(event: string, handler: EventHandler): void {
        if (!this.handlers.has(event)) {
            this.handlers.set(event, []);
        }
        this.handlers.get(event)!.push(handler);
    }

    off(event: string, handler: EventHandler): void {
        const handlers = this.handlers.get(event);
        if (handlers) {
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    emit(event: string, data?: any): void {
        const handlers = this.handlers.get(event);
        if (handlers) {
            handlers.forEach(handler => handler(data));
        }
    }
}

// 全局事件总线
const eventBus = new EventBus();

// 订单服务
class OrderService {
    constructor(private bus: EventBus) {}

    createOrder(order: Order): void {
        // 保存订单...
        this.bus.emit("order:created", order);
    }
}

// 通知服务
class NotificationService {
    constructor(private bus: EventBus) {
        this.bus.on("order:created", this.onOrderCreated.bind(this));
    }

    private onOrderCreated(order: Order): void {
        this.sendEmail(order.userEmail, "订单创建成功");
    }

    private sendEmail(to: string, message: string): void {
        console.log(`发送邮件到 ${to}: ${message}`);
    }
}

// 库存服务
class InventoryService {
    constructor(private bus: EventBus) {
        this.bus.on("order:created", this.onOrderCreated.bind(this));
    }

    private onOrderCreated(order: Order): void {
        this.reduceStock(order.items);
    }

    private reduceStock(items: OrderItem[]): void {
        // 减少库存...
    }
}

// 使用
const bus = new EventBus();
const orderService = new OrderService(bus);
const notificationService = new NotificationService(bus);
const inventoryService = new InventoryService(bus);

orderService.createOrder(newOrder);
```

```typescript
// ✅ KISS：直接方法调用（当只有 2-3 个消费者时）

class NotificationService {
    sendOrderConfirmation(email: string): void {
        console.log(`发送邮件到 ${email}: 订单创建成功`);
    }
}

class InventoryService {
    reduceStock(items: OrderItem[]): void {
        // 减少库存...
    }
}

class OrderService {
    constructor(
        private notificationService: NotificationService,
        private inventoryService: InventoryService
    ) {}

    createOrder(order: Order): void {
        // 保存订单...
        this.notificationService.sendOrderConfirmation(order.userEmail);
        this.inventoryService.reduceStock(order.items);
    }
}

// 使用
const notificationService = new NotificationService();
const inventoryService = new InventoryService();
const orderService = new OrderService(notificationService, inventoryService);

orderService.createOrder(newOrder);
```

**对比分析**:
- 事件总线版：事件名是字符串（无类型安全），调试困难，调用链不可见
- 直接调用版：类型安全，IDE 可追踪调用链，调试简单
- 当消费者数量少且固定时，事件总线是不必要的间接层
- 当消费者数量多、动态变化、或需要跨模块解耦时，事件总线才有意义

---

### 场景2: 过度抽象的验证框架

```typescript
// ❌ 过度设计：为表单验证创建完整框架
interface ValidationRule<T> {
    validate(value: T): ValidationResult;
}

interface ValidationResult {
    isValid: boolean;
    errors: string[];
}

class RequiredRule implements ValidationRule<string> {
    validate(value: string): ValidationResult {
        const isValid = value !== null && value !== undefined && value.trim() !== "";
        return { isValid, errors: isValid ? [] : ["字段不能为空"] };
    }
}

class MinLengthRule implements ValidationRule<string> {
    constructor(private minLength: number) {}

    validate(value: string): ValidationResult {
        const isValid = value.length >= this.minLength;
        return { isValid, errors: isValid ? [] : [`最少需要${this.minLength}个字符`] };
    }
}

class EmailRule implements ValidationRule<string> {
    validate(value: string): ValidationResult {
        const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        return { isValid, errors: isValid ? [] : ["邮箱格式错误"] };
    }
}

class FieldValidator<T> {
    private rules: ValidationRule<T>[] = [];

    addRule(rule: ValidationRule<T>): FieldValidator<T> {
        this.rules.push(rule);
        return this;
    }

    validate(value: T): ValidationResult {
        const errors: string[] = [];
        for (const rule of this.rules) {
            const result = rule.validate(value);
            if (!result.isValid) {
                errors.push(...result.errors);
            }
        }
        return { isValid: errors.length === 0, errors };
    }
}

class FormValidator {
    private fields: Map<string, FieldValidator<any>> = new Map();

    addField(name: string, validator: FieldValidator<any>): FormValidator {
        this.fields.set(name, validator);
        return this;
    }

    validate(data: Record<string, any>): Map<string, ValidationResult> {
        const results = new Map<string, ValidationResult>();
        for (const [name, validator] of this.fields) {
            results.set(name, validator.validate(data[name]));
        }
        return results;
    }
}

// 使用
const formValidator = new FormValidator()
    .addField("email", new FieldValidator<string>()
        .addRule(new RequiredRule())
        .addRule(new EmailRule()))
    .addField("password", new FieldValidator<string>()
        .addRule(new RequiredRule())
        .addRule(new MinLengthRule(8)));

const results = formValidator.validate({ email: "test@example.com", password: "12345678" });
```

```typescript
// ✅ KISS：简单的验证函数

interface ValidationErrors {
    [field: string]: string;
}

function validateRegistrationForm(data: {
    email: string;
    password: string;
}): ValidationErrors {
    const errors: ValidationErrors = {};

    if (!data.email || !data.email.trim()) {
        errors.email = "邮箱不能为空";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
        errors.email = "邮箱格式错误";
    }

    if (!data.password || !data.password.trim()) {
        errors.password = "密码不能为空";
    } else if (data.password.length < 8) {
        errors.password = "密码最少需要8个字符";
    }

    return errors;
}

// 使用
const errors = validateRegistrationForm({
    email: "test@example.com",
    password: "12345678"
});
const isValid = Object.keys(errors).length === 0;
```

**对比分析**:
- 框架版：7 个类/接口，70+ 行代码，适合有几十个表单的大型应用
- KISS 版：1 个函数，20 行代码，清晰直接
- 如果只有少量表单，直接写验证函数最简单
- 如果表单数量增长，可以引入 `zod` 或 `yup` 等成熟验证库

---

## 单元测试示例

### Java 测试

```java
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class NumberUtilsTest {

    @ParameterizedTest
    @CsvSource({"2, true", "3, false", "0, true", "-4, true", "-7, false"})
    void isEven_shouldClassifyCorrectly(int number, boolean expected) {
        assertEquals(expected, NumberUtils.isEven(number));
    }

    @Test
    void classify_positiveEven_shouldReturnBothLabels() {
        List<String> result = NumberUtils.classify(42);
        assertEquals(List.of("偶数", "正数"), result);
    }

    @Test
    void classify_negativeOdd_shouldReturnBothLabels() {
        List<String> result = NumberUtils.classify(-3);
        assertEquals(List.of("奇数", "负数"), result);
    }

    @Test
    void classify_zero_shouldReturnEvenAndZero() {
        List<String> result = NumberUtils.classify(0);
        assertEquals(List.of("偶数", "零"), result);
    }
}

class PermissionCheckerTest {

    private final PermissionChecker checker = new PermissionChecker();

    @Test
    void canAccessResource_nullUser_returnsFalse() {
        assertFalse(checker.canAccessResource(null, new Resource("doc", false)));
    }

    @Test
    void canAccessResource_inactiveUser_returnsFalse() {
        User user = new User(false);
        assertFalse(checker.canAccessResource(user, new Resource("doc", false)));
    }

    @Test
    void canAccessResource_publicResource_returnsTrue() {
        User user = new User(true);
        Resource resource = new Resource("doc", true);
        assertTrue(checker.canAccessResource(user, resource));
    }

    @Test
    void canAccessResource_userWithPermission_returnsTrue() {
        User user = createUserWithPermission("doc", "read");
        Resource resource = new Resource("doc", false);
        assertTrue(checker.canAccessResource(user, resource));
    }
}
```

### Python 测试

```python
import pytest
from config_loader import load_config


def test_load_config_success(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"database": {"host": "localhost", "port": 5432}}')

    config = load_config(str(config_file))

    assert config["database"]["host"] == "localhost"
    assert config["database"]["port"] == 5432


def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError, match="配置文件不存在"):
        load_config("nonexistent.json")


def test_load_config_default_values(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"app_name": "demo"}')

    config = load_config(str(config_file))

    # 使用 dict.get 获取默认值，无需自建默认值框架
    db_host = config.get("database", {}).get("host", "localhost")
    assert db_host == "localhost"
```

### TypeScript 测试

```typescript
import { describe, it, expect } from "vitest";
import { validateRegistrationForm } from "./validation";

describe("validateRegistrationForm", () => {
    it("should return no errors for valid input", () => {
        const errors = validateRegistrationForm({
            email: "user@example.com",
            password: "MyPass123"
        });
        expect(Object.keys(errors)).toHaveLength(0);
    });

    it("should return error for empty email", () => {
        const errors = validateRegistrationForm({
            email: "",
            password: "MyPass123"
        });
        expect(errors.email).toBe("邮箱不能为空");
    });

    it("should return error for invalid email", () => {
        const errors = validateRegistrationForm({
            email: "not-an-email",
            password: "MyPass123"
        });
        expect(errors.email).toBe("邮箱格式错误");
    });

    it("should return error for short password", () => {
        const errors = validateRegistrationForm({
            email: "user@example.com",
            password: "short"
        });
        expect(errors.password).toBe("密码最少需要8个字符");
    });

    it("should return multiple errors", () => {
        const errors = validateRegistrationForm({
            email: "",
            password: ""
        });
        expect(errors.email).toBeDefined();
        expect(errors.password).toBeDefined();
    });
});
```

---

## 总结

### KISS 核心决策流程

```
面对一个设计决策时：

1. 最简单的方案是什么？
2. 这个方案能满足当前需求吗？
   → 能：用它
   → 不能：找次简单的方案，回到步骤 2
3. 不要问"未来可能需要什么"，只关注当前明确的需求
```

### 何时可以增加复杂度

| 场景 | 增加复杂度的理由 |
|------|----------------|
| 有 3+ 个已知的变体 | 策略/工厂模式有实际价值 |
| 多个团队独立开发 | 接口抽象有协作价值 |
| 外部依赖可能替换 | 适配器抽象有防护价值 |
| 性能是硬性要求 | 缓存、池化等设计有必要 |
| 安全是硬性要求 | 验证、加密等层次有必要 |

### 关键原则

```
1. 先写能工作的最简单版本
2. 只在遇到具体问题时才重构
3. 优先使用标准库和成熟的第三方库
4. 每个抽象层都必须有明确的当前价值
5. 代码的可读性比"优雅"更重要
6. 如果你需要写注释解释设计的意图，也许设计本身太复杂了
```
