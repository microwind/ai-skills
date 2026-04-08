# 一致性原则 - 参考实现

## 核心原理与设计

一致性原则的核心：**相似的问题用相似的方式解决，相同的概念用相同的名称表达**。一致性涵盖命名、模式、错误处理、API 格式等多个维度。

---

## Java 参考实现

### 反面示例：不一致的设计

```java
/**
 * ❌ 反面示例：命名、错误处理、返回格式全不一致
 */
public class UserService {
    public User getUser(Long id) { return userRepo.findById(id); }
}

public class OrderService {
    public Order fetchOrder(Long id) { return orderRepo.findById(id); }  // fetch vs get
}

public class ProductService {
    public Product retrieveProduct(Long id) { return productRepo.findById(id); }  // retrieve
}

// 错误处理不一致
public class UserController {
    public ResponseEntity<?> getUser(Long id) {
        User user = userService.getUser(id);
        if (user == null) return ResponseEntity.notFound().build();  // 返回404
        return ResponseEntity.ok(user);  // 直接返回实体
    }
}

public class OrderController {
    public Map<String, Object> getOrder(Long id) {
        try {
            Order order = orderService.fetchOrder(id);
            return Map.of("success", true, "data", order);  // 不同的返回格式
        } catch (Exception e) {
            return Map.of("success", false, "error", e.getMessage());
        }
    }
}
```

### 正面示例：一致的设计

```java
/**
 * ✅ 正面示例：统一的命名、错误处理和响应格式
 */

// 统一响应格式
public class ApiResponse<T> {
    private int code;
    private T data;
    private String message;

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(200, data, "ok");
    }

    public static <T> ApiResponse<T> error(int code, String message) {
        return new ApiResponse<>(code, null, message);
    }
}

// 统一异常体系
public abstract class BusinessException extends RuntimeException {
    private final int code;
    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
    }
    public int getCode() { return code; }
}

public class NotFoundException extends BusinessException {
    public NotFoundException(String resource, Object id) {
        super(404, resource + " not found: " + id);
    }
}

public class ValidationException extends BusinessException {
    public ValidationException(String message) {
        super(400, message);
    }
}

// 统一异常处理
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<?>> handleBusiness(BusinessException e) {
        return ResponseEntity.status(e.getCode())
            .body(ApiResponse.error(e.getCode(), e.getMessage()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<?>> handleUnknown(Exception e) {
        return ResponseEntity.status(500)
            .body(ApiResponse.error(500, "Internal server error"));
    }
}

// 统一命名：所有 Service 用 findById / findAll / create / update / delete
public class UserService {
    public User findById(Long id) {
        return userRepo.findById(id)
            .orElseThrow(() -> new NotFoundException("User", id));
    }

    public List<User> findAll() { return userRepo.findAll(); }

    public User create(CreateUserRequest req) {
        // 统一的验证方式
        if (req.getEmail() == null || req.getEmail().isBlank()) {
            throw new ValidationException("邮箱不能为空");
        }
        return userRepo.save(new User(req.getName(), req.getEmail()));
    }
}

public class OrderService {
    public Order findById(Long id) {
        return orderRepo.findById(id)
            .orElseThrow(() -> new NotFoundException("Order", id));
    }

    public Order create(CreateOrderRequest req) {
        if (req.getItems() == null || req.getItems().isEmpty()) {
            throw new ValidationException("订单项不能为空");
        }
        return orderRepo.save(new Order(req));
    }
}

// 统一控制器模式
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping("/{id}")
    public ApiResponse<User> findById(@PathVariable Long id) {
        return ApiResponse.success(userService.findById(id));
    }

    @PostMapping
    public ApiResponse<User> create(@RequestBody CreateUserRequest req) {
        return ApiResponse.success(userService.create(req));
    }
}

@RestController
@RequestMapping("/api/orders")
public class OrderController {
    @GetMapping("/{id}")
    public ApiResponse<Order> findById(@PathVariable Long id) {
        return ApiResponse.success(orderService.findById(id));
    }

    @PostMapping
    public ApiResponse<Order> create(@RequestBody CreateOrderRequest req) {
        return ApiResponse.success(orderService.create(req));
    }
}
```

---

## Python 参考实现

```python
"""
✅ 一致的 Python 实现
"""
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional

# 统一异常体系
class BusinessError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

class NotFoundError(BusinessError):
    def __init__(self, resource: str, id):
        super().__init__(404, f"{resource} not found: {id}")

class ValidationError(BusinessError):
    def __init__(self, message: str):
        super().__init__(400, message)

# 统一响应格式
@dataclass
class ApiResponse:
    code: int
    data: object
    message: str

    @staticmethod
    def success(data):
        return ApiResponse(code=200, data=data, message="ok")

    @staticmethod
    def error(code: int, message: str):
        return ApiResponse(code=code, data=None, message=message)

# 统一命名的 Service
class UserService:
    def find_by_id(self, id: str):
        user = self.repo.find_by_id(id)
        if not user:
            raise NotFoundError("User", id)
        return user

    def find_all(self): return self.repo.find_all()

    def create(self, data: dict):
        if not data.get("email"):
            raise ValidationError("邮箱不能为空")
        return self.repo.save(data)

class OrderService:
    def find_by_id(self, id: str):
        order = self.repo.find_by_id(id)
        if not order:
            raise NotFoundError("Order", id)
        return order

    def create(self, data: dict):
        if not data.get("items"):
            raise ValidationError("订单项不能为空")
        return self.repo.save(data)

# 统一错误处理中间件（Flask 示例）
@app.errorhandler(BusinessError)
def handle_business_error(e):
    return jsonify({"code": e.code, "data": None, "message": e.message}), e.code
```

---

## TypeScript 参考实现

```typescript
// 统一响应类型
interface ApiResponse<T> {
    code: number;
    data: T | null;
    message: string;
}

function success<T>(data: T): ApiResponse<T> {
    return { code: 200, data, message: 'ok' };
}

function error(code: number, message: string): ApiResponse<null> {
    return { code, data: null, message };
}

// 统一异常
class BusinessError extends Error {
    constructor(public code: number, message: string) { super(message); }
}
class NotFoundError extends BusinessError {
    constructor(resource: string, id: string) { super(404, `${resource} not found: ${id}`); }
}
class ValidationError extends BusinessError {
    constructor(message: string) { super(400, message); }
}

// 统一 Service 命名
class UserService {
    async findById(id: string): Promise<User> {
        const user = await this.repo.findById(id);
        if (!user) throw new NotFoundError('User', id);
        return user;
    }
    async create(data: CreateUserDTO): Promise<User> {
        if (!data.email) throw new ValidationError('邮箱不能为空');
        return this.repo.save(data);
    }
}

// 统一错误处理中间件（Express）
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
    if (err instanceof BusinessError) {
        res.status(err.code).json(error(err.code, err.message));
    } else {
        res.status(500).json(error(500, 'Internal server error'));
    }
});
```

---

## 总结

| 维度 | 不一致 | 一致 |
|------|--------|------|
| 命名 | get/fetch/retrieve 混用 | 统一 findById/create/update/delete |
| 错误处理 | null/异常/错误码混用 | 统一异常体系 + 全局处理 |
| API格式 | 每个端点格式不同 | 统一 ApiResponse |
| 日志 | 格式随意 | 统一格式和级别 |
| 认知成本 | 高（每个模块要重新学习） | 低（学一次，处处适用） |
