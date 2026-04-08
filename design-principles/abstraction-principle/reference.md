# 抽象原则 - 完整参考实现

## 核心原理

抽象是管理复杂性的核心工具：**捕获事物的本质特征，隐藏不必要的细节，提供更简单的理解模型**。

### 关键设计要点

| 要点 | 说明 | 应用场景 |
|------|------|---------|
| 分层抽象 | 每层只处理一个复杂度级别 | 系统架构设计 |
| 接口稳定 | 抽象不因实现变化而改变 | API 设计 |
| 信息隐藏 | 隐藏不必要的实现细节 | 模块设计 |
| 适度抽象 | 不过度也不不足 | 重构决策 |

---

## Java 完整参考实现

### 场景：数据访问抽象

```java
// ✅ 遵循抽象原则的设计

// 1. 数据访问抽象接口（高层抽象）
public interface UserRepository {
    User findById(Long id);
    List<User> findByName(String name);
    void save(User user);
    void delete(Long id);
}

// 2. MySQL 实现（底层细节被隐藏）
public class MySQLUserRepository implements UserRepository {
    private final DataSource dataSource;

    public MySQLUserRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public User findById(Long id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setLong(1, id);
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                return mapToUser(rs);
            }
            return null;
        } catch (SQLException e) {
            throw new DataAccessException("Failed to find user", e);
        }
    }

    @Override
    public List<User> findByName(String name) {
        String sql = "SELECT * FROM users WHERE name LIKE ?";
        List<User> users = new ArrayList<>();
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, "%" + name + "%");
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                users.add(mapToUser(rs));
            }
        } catch (SQLException e) {
            throw new DataAccessException("Failed to find users", e);
        }
        return users;
    }

    @Override
    public void save(User user) {
        String sql = "INSERT INTO users (name, email) VALUES (?, ?) "
                   + "ON DUPLICATE KEY UPDATE name = ?, email = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, user.getName());
            stmt.setString(2, user.getEmail());
            stmt.setString(3, user.getName());
            stmt.setString(4, user.getEmail());
            stmt.executeUpdate();
        } catch (SQLException e) {
            throw new DataAccessException("Failed to save user", e);
        }
    }

    @Override
    public void delete(Long id) {
        String sql = "DELETE FROM users WHERE id = ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setLong(1, id);
            stmt.executeUpdate();
        } catch (SQLException e) {
            throw new DataAccessException("Failed to delete user", e);
        }
    }

    private User mapToUser(ResultSet rs) throws SQLException {
        return new User(rs.getLong("id"), rs.getString("name"), rs.getString("email"));
    }
}

// 3. 内存实现（用于测试）
public class InMemoryUserRepository implements UserRepository {
    private final Map<Long, User> store = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    @Override
    public User findById(Long id) {
        return store.get(id);
    }

    @Override
    public List<User> findByName(String name) {
        return store.values().stream()
            .filter(u -> u.getName().contains(name))
            .collect(Collectors.toList());
    }

    @Override
    public void save(User user) {
        if (user.getId() == null) {
            user.setId(idGenerator.getAndIncrement());
        }
        store.put(user.getId(), user);
    }

    @Override
    public void delete(Long id) {
        store.remove(id);
    }
}

// 4. 业务层 - 只依赖抽象
public class UserService {
    private final UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = repository;
    }

    public User getUser(Long id) {
        User user = repository.findById(id);
        if (user == null) {
            throw new UserNotFoundException("User not found: " + id);
        }
        return user;
    }

    public void registerUser(String name, String email) {
        User user = new User(null, name, email);
        repository.save(user);
    }
}

// 5. 使用示例
public class Demo {
    public static void main(String[] args) {
        // 生产环境使用 MySQL
        UserRepository prodRepo = new MySQLUserRepository(dataSource);
        UserService prodService = new UserService(prodRepo);

        // 测试环境使用内存
        UserRepository testRepo = new InMemoryUserRepository();
        UserService testService = new UserService(testRepo);
    }
}
```

---

## Python 完整参考实现

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from dataclasses import dataclass

@dataclass
class User:
    id: Optional[int]
    name: str
    email: str

# 1. 数据访问抽象
class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> List[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass

# 2. 内存实现
class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._store: Dict[int, User] = {}
        self._next_id = 1

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self._store.get(user_id)

    def find_by_name(self, name: str) -> List[User]:
        return [u for u in self._store.values() if name in u.name]

    def save(self, user: User) -> None:
        if user.id is None:
            user.id = self._next_id
            self._next_id += 1
        self._store[user.id] = user

    def delete(self, user_id: int) -> None:
        self._store.pop(user_id, None)

# 3. 业务层 - 只依赖抽象
class UserService:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    def get_user(self, user_id: int) -> User:
        user = self._repository.find_by_id(user_id)
        if user is None:
            raise ValueError(f"User not found: {user_id}")
        return user

    def register_user(self, name: str, email: str) -> None:
        user = User(id=None, name=name, email=email)
        self._repository.save(user)

# 4. 使用示例
if __name__ == "__main__":
    repo = InMemoryUserRepository()
    service = UserService(repo)

    service.register_user("Alice", "alice@example.com")
    user = service.get_user(1)
    print(f"Found: {user}")
```

---

## TypeScript 完整参考实现

```typescript
// 1. 数据访问抽象
interface UserRepository {
    findById(id: number): User | null;
    findByName(name: string): User[];
    save(user: User): void;
    delete(id: number): void;
}

interface User {
    id?: number;
    name: string;
    email: string;
}

// 2. 内存实现
class InMemoryUserRepository implements UserRepository {
    private store: Map<number, User> = new Map();
    private nextId = 1;

    findById(id: number): User | null {
        return this.store.get(id) ?? null;
    }

    findByName(name: string): User[] {
        return Array.from(this.store.values())
            .filter(u => u.name.includes(name));
    }

    save(user: User): void {
        if (!user.id) {
            user.id = this.nextId++;
        }
        this.store.set(user.id, user);
    }

    delete(id: number): void {
        this.store.delete(id);
    }
}

// 3. 业务层 - 只依赖抽象
class UserService {
    constructor(private repository: UserRepository) {}

    getUser(id: number): User {
        const user = this.repository.findById(id);
        if (!user) throw new Error(`User not found: ${id}`);
        return user;
    }

    registerUser(name: string, email: string): void {
        this.repository.save({ name, email });
    }
}

// 4. 使用示例
const repo = new InMemoryUserRepository();
const service = new UserService(repo);
service.registerUser("Alice", "alice@example.com");
console.log(service.getUser(1));
```

---

## 单元测试示例

### Java JUnit

```java
@Test
public void testUserService() {
    UserRepository repo = new InMemoryUserRepository();
    UserService service = new UserService(repo);

    service.registerUser("Alice", "alice@example.com");
    User user = service.getUser(1);
    assertEquals("Alice", user.getName());
}

@Test
public void testRepositoryAbstraction() {
    // 可以轻松替换实现进行测试
    UserRepository repo = new InMemoryUserRepository();
    repo.save(new User(null, "Bob", "bob@example.com"));
    assertNotNull(repo.findById(1));
    assertEquals(1, repo.findByName("Bob").size());
}
```

### Python pytest

```python
def test_user_service():
    repo = InMemoryUserRepository()
    service = UserService(repo)

    service.register_user("Alice", "alice@example.com")
    user = service.get_user(1)
    assert user.name == "Alice"

def test_repository_abstraction():
    repo = InMemoryUserRepository()
    repo.save(User(id=None, name="Bob", email="bob@example.com"))
    assert repo.find_by_id(1) is not None
    assert len(repo.find_by_name("Bob")) == 1
```

---

## 总结

**抽象原则核心实现**：

1. **定义清晰的抽象接口** - 隐藏实现细节，暴露简单接口
2. **分层抽象** - 每层只处理一个复杂度级别
3. **依赖抽象** - 上层只依赖抽象，不依赖具体实现
4. **可替换实现** - 底层实现可自由替换而不影响上层

**效果**：
- 可以轻松替换底层实现（如从 MySQL 切换到 PostgreSQL）
- 业务逻辑不受基础设施变化影响
- 测试时可使用内存实现替代真实数据库
- 系统更加灵活、可维护
