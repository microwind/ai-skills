# Prototype Pattern - 完整参考实现

## 核心原理回顾

**Prototype** 模式通过克隆现有实例来创建对象，避免复杂的初始化过程。

**关键决策**: 浅拷贝 vs 深拷贝
- 浅拷贝：快速，但嵌套对象被共享
- 深拷贝：安全，确保完全独立

---

## Java 完整实现

### 1. 领域对象

```java
// 地址 - 被User引用的复杂对象
public class Address implements Cloneable {
    private String city;
    private String street;
    private String zipCode;
    
    public Address(String city, String street, String zipCode) {
        this.city = city;
        this.street = street;
        this.zipCode = zipCode;
    }
    
    // Copy Constructor - 支持深拷贝
    public Address(Address other) {
        this.city = other.city;
        this.street = other.street;
        this.zipCode = other.zipCode;
    }
    
    public Address clone() {
        try {
            return (Address) super.clone();
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }
    
    // Getters and setters
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    public String getStreet() { return street; }
    public void setStreet(String street) { this.street = street; }
    
    @Override
    public String toString() {
        return String.format("Address{city='%s', street='%s'}", city, street);
    }
}

// 角色
public class Role {
    private String roleName;
    private String permission;
    
    public Role(String roleName, String permission) {
        this.roleName = roleName;
        this.permission = permission;
    }
    
    // Copy Constructor
    public Role(Role other) {
        this.roleName = other.roleName;
        this.permission = other.permission;
    }
    
    public String getRoleName() { return roleName; }
    public String getPermission() { return permission; }
    
    @Override
    public String toString() {
        return String.format("Role{name='%s'}", roleName);
    }
}
```

### 2. 原型对象（主类）

```java
// 方案A: Copy Constructor方式（推荐深拷贝）
public class UserWithCopyConstructor {
    private int id;
    private String name;
    private String email;
    private Address address;
    private List<Role> roles;
    private Date createdAt;
    
    public UserWithCopyConstructor(
        int id, String name, String email, 
        Address address, List<Role> roles) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.address = address;
        this.roles = roles;
        this.createdAt = new Date();
    }
    
    // ✅ Copy Constructor - 深拷贝
    public UserWithCopyConstructor(UserWithCopyConstructor original) {
        this.id = original.id;
        this.name = original.name;
        this.email = original.email;
        
        // 深拷贝Address
        this.address = original.address == null ? 
            null : 
            new Address(original.address);
        
        // 深拷贝List<Role>
        this.roles = original.roles == null ?
            null :
            original.roles.stream()
                .map(Role::new)
                .collect(Collectors.toList());
        
        // 深拷贝Date
        this.createdAt = original.createdAt == null ?
            null :
            new Date(original.createdAt.getTime());
    }
    
    public UserWithCopyConstructor clone() {
        return new UserWithCopyConstructor(this);
    }
    
    // Getters
    public int getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public Address getAddress() { return address; }
    public List<Role> getRoles() { return roles; }
    
    // 修改用于测试
    public void setName(String name) { this.name = name; }
}

// 方案B: Cloneable接口（浅拷贝）
public class UserShallowClone implements Cloneable {
    private int id;
    private String name;
    private Address address;
    private List<Role> roles;
    
    public UserShallowClone(int id, String name, Address address, List<Role> roles) {
        this.id = id;
        this.name = name;
        this.address = address;
        this.roles = roles;
    }
    
    @Override
    public UserShallowClone clone() {
        try {
            return (UserShallowClone) super.clone();  // 浅拷贝！
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }
}

// 方案C: Builder模式 + 克隆（支持部分修改）
public class UserWithBuilder {
    private final int id;
    private final String name;
    private final String email;
    private final Address address;
    private final List<Role> roles;
    
    private UserWithBuilder(UserBuilder builder) {
        this.id = builder.id;
        this.name = builder.name;
        this.email = builder.email;
        this.address = builder.address;
        this.roles = builder.roles;
    }
    
    // 通过Builder实现克隆
    public UserWithBuilder clone() {
        return new UserBuilder(this).build();
    }
    
    // Builder类
    public static class UserBuilder {
        private int id;
        private String name;
        private String email;
        private Address address;
        private List<Role> roles;
        
        public UserBuilder(int id) {
            this.id = id;
            this.roles = new ArrayList<>();
        }
        
        // 从现有对象构建（克隆）
        public UserBuilder(UserWithBuilder original) {
            this.id = original.id;
            this.name = original.name;
            this.email = original.email;
            // 深拷贝
            this.address = original.address == null ?
                null :
                new Address(original.address);
            this.roles = original.roles == null ?
                null :
                original.roles.stream()
                    .map(Role::new)
                    .collect(Collectors.toList());
        }
        
        public UserBuilder name(String name) {
            this.name = name;
            return this;
        }
        
        public UserBuilder email(String email) {
            this.email = email;
            return this;
        }
        
        public UserBuilder address(Address address) {
            this.address = address;
            return this;
        }
        
        public UserBuilder addRole(Role role) {
            this.roles.add(role);
            return this;
        }
        
        public UserWithBuilder build() {
            return new UserWithBuilder(this);
        }
    }
    
    // Getters
    public int getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public Address getAddress() { return address; }
    public List<Role> getRoles() { return roles; }
}

// 方案D: 序列化克隆（通用，处理复杂关系）
public class UserSerializable implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private int id;
    private String name;
    private Address address;
    
    public UserSerializable(int id, String name, Address address) {
        this.id = id;
        this.name = name;
        this.address = address;
    }
    
    // 通过序列化实现深拷贝
    public UserSerializable deepClone() {
        try {
            // 序列化
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(baos);
            oos.writeObject(this);
            oos.close();
            
            // 反序列化
            ByteArrayInputStream bais = 
                new ByteArrayInputStream(baos.toByteArray());
            ObjectInputStream ois = new ObjectInputStream(bais);
            UserSerializable cloned = (UserSerializable) ois.readObject();
            ois.close();
            
            return cloned;
        } catch (IOException | ClassNotFoundException e) {
            throw new RuntimeException("克隆失败", e);
        }
    }
}
```

### 3. 原型注册表

```java
// 原型工厂 - 管理和克隆原型
public class UserPrototypeRegistry {
    private static final Map<String, UserWithCopyConstructor> prototypes = 
        new ConcurrentHashMap<>();
    
    // 注册原型
    public static void registerPrototype(String key, UserWithCopyConstructor prototype) {
        prototypes.put(key, prototype);
    }
    
    // 克隆原型
    public static UserWithCopyConstructor createUser(String key) {
        UserWithCopyConstructor prototype = prototypes.get(key);
        if (prototype == null) {
            throw new IllegalArgumentException("未知的原型: " + key);
        }
        return prototype.clone();  // 深拷贝
    }
    
    // 列出所有原型
    public static Set<String> listPrototypes() {
        return prototypes.keySet();
    }
}

// 初始化示例
class PrototypeInitializer {
    public static void initializePrototypes() {
        // 管理员用户原型
        UserWithCopyConstructor admin = new UserWithCopyConstructor(
            999,
            "Admin",
            "admin@company.com",
            new Address("Beijing", "Main Street", "100000"),
            Arrays.asList(
                new Role("ADMIN", "all"),
                new Role("USER", "basic")
            )
        );
        UserPrototypeRegistry.registerPrototype("admin", admin);
        
        // 普通用户原型
        UserWithCopyConstructor user = new UserWithCopyConstructor(
            1,
            "User",
            "user@company.com",
            new Address("Shanghai", "Park Avenue", "200000"),
            Collections.singletonList(new Role("USER", "basic"))
        );
        UserPrototypeRegistry.registerPrototype("user", user);
        
        // 访客原型
        UserWithCopyConstructor guest = new UserWithCopyConstructor(
            0,
            "Guest",
            "guest@company.com",
            null,
            Collections.emptyList()
        );
        UserPrototypeRegistry.registerPrototype("guest", guest);
    }
}
```

### 4. 单元测试

```java
public class PrototypePatternTest {
    
    @BeforeClass
    public static void setup() {
        PrototypeInitializer.initializePrototypes();
    }
    
    // 测试深拷贝
    @Test
    public void testDeepClone() {
        UserWithCopyConstructor original = new UserWithCopyConstructor(
            1, "Alice", "alice@example.com",
            new Address("Shanghai", "Nanjing Rd", "200001"),
            Arrays.asList(new Role("USER", "basic"))
        );
        
        UserWithCopyConstructor clone = original.clone();
        
        // 验证字段相同
        assertEquals(original.getId(), clone.getId());
        assertEquals(original.getName(), clone.getName());
        
        // 验证不是同一对象
        assertNotSame(original, clone);
        assertNotSame(original.getAddress(), clone.getAddress());
        assertNotSame(original.getRoles(), clone.getRoles());
        
        // 修改克隆，原对象不受影响
        clone.getAddress().setCity("Beijing");
        assertNotEquals(
            original.getAddress().getCity(),
            clone.getAddress().getCity()
        );
    }
    
    // 测试浅拷贝问题
    @Test
    public void testShallowCloneProblem() {
        Address address = new Address("Shanghai", "Nanjing Rd", "200001");
        UserShallowClone original = new UserShallowClone(
            1, "Alice", address, new ArrayList<>()
        );
        
        UserShallowClone clone = original.clone();
        
        // 浅拷贝：address是共享的！
        assertSame(original.address, clone.address);
        
        // 修改会影响原对象
        clone.address.setCity("Beijing");
        assertEquals("Beijing", original.address.getCity());
    }
    
    // 测试Builder克隆 + 修改
    @Test
    public void testBuilderClone() {
        UserWithBuilder original = new UserWithBuilder.UserBuilder(1)
            .name("Alice")
            .email("alice@example.com")
            .address(new Address("Shanghai", "Park Ave", "200001"))
            .addRole(new Role("USER", "basic"))
            .build();
        
        // 克隆并修改
        UserWithBuilder modified = original.clone();  // 先克隆
        // 通过Builder修改特定字段
        UserWithBuilder newUser = new UserWithBuilder.UserBuilder(original)
            .name("Bob")
            .addRole(new Role("ADMIN", "all"))
            .build();
        
        assertEquals("Alice", original.getName());
        assertEquals("Bob", newUser.getName());
    }
    
    // 测试原型注册表
    @Test
    public void testPrototypeRegistry() {
        // 从注册表获取克隆
        UserWithCopyConstructor admin1 = UserPrototypeRegistry.createUser("admin");
        UserWithCopyConstructor admin2 = UserPrototypeRegistry.createUser("admin");
        
        // 验证是不同的对象
        assertNotSame(admin1, admin2);
        
        // 验证内容相同
        assertEquals(admin1.getName(), admin2.getName());
        assertEquals(admin1.getRoles().size(), admin2.getRoles().size());
    }
    
    // 性能测试
    @Test
    public void testPerformance() {
        UserWithCopyConstructor original = UserPrototypeRegistry.createUser("user");
        
        long startTime = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            UserWithCopyConstructor clone = original.clone();
        }
        long duration = System.nanoTime() - startTime;
        
        System.out.println("100000次克隆耗时: " + duration/1000000 + "ms");
        System.out.println("平均每次: " + duration/100000 + "ns");
        
        // 断言性能在可接受范围
        assertTrue(duration < 100_000_000_000L);  // 100毫秒
    }
}
```

---

## Python 实现

```python
from copy import copy, deepcopy
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime

# 领域模型
class Address:
    def __init__(self, city, street, zip_code):
        self.city = city
        self.street = street
        self.zip_code = zip_code
    
    def __repr__(self):
        return f"Address(city='{self.city}', street='{self.street}')"

class Role:
    def __init__(self, name, permission):
        self.name = name
        self.permission = permission
    
    def __repr__(self):
        return f"Role('{self.name}')"

# 方案1: 浅拷贝
class UserShallowCopy:
    def __init__(self, id, name, email, address, roles):
        self.id = id
        self.name = name
        self.email = email
        self.address = address  # 复杂对象
        self.roles = roles      # 列表
        self.created_at = datetime.now()
    
    def clone(self):
        return copy(self)  # 浅拷贝 ⚠️

# 方案2: 深拷贝（推荐）
class UserDeepCopy:
    def __init__(self, id, name, email, address=None, roles=None):
        self.id = id
        self.name = name
        self.email = email
        self.address = address
        self.roles = roles or []
        self.created_at = datetime.now()
    
    def clone(self):
        # 使用copy module的deepcopy ✅
        return deepcopy(self)
    
    def clone_with_modifications(self, **kwargs):
        """克隆并修改某些字段"""
        cloned = deepcopy(self)
        for key, value in kwargs.items():
            setattr(cloned, key, value)
        return cloned

# 方案3: 手动深拷贝（比deepcopy更快，更可控）
class UserManualDeepClone:
    def __init__(self, id, name, email, address=None, roles=None):
        self.id = id
        self.name = name
        self.email = email
        self.address = address
        self.roles = roles or []
        self.created_at = datetime.now()
    
    def clone(self):
        """手动实现深拷贝"""
        cloned = UserManualDeepClone(
            id=self.id,
            name=self.name,
            email=self.email,
            # 深拷贝Address
            address=Address(
                self.address.city,
                self.address.street,
                self.address.zip_code
            ) if self.address else None,
            # 深拷贝List<Role>
            roles=[Role(r.name, r.permission) for r in self.roles]
        )
        # 深拷贝datetime
        cloned.created_at = datetime.fromisoformat(
            self.created_at.isoformat()
        )
        return cloned

# 方案4: Prototype注册表
class PrototypeRegistry:
    _prototypes = {}
    
    @classmethod
    def register(cls, key, prototype):
        cls._prototypes[key] = prototype
    
    @classmethod
    def create(cls, key):
        prototype = cls._prototypes.get(key)
        if not prototype:
            raise ValueError(f"Unknown prototype: {key}")
        return prototype.clone()

# 初始化
admin_prototype = UserDeepCopy(
    999,
    "Admin",
    "admin@company.com",
    Address("Beijing", "Main St", "100000"),
    [Role("ADMIN", "all"), Role("USER", "basic")]
)
PrototypeRegistry.register("admin", admin_prototype)

user_prototype = UserDeepCopy(
    1,
    "User",
    "user@company.com",
    Address("Shanghai", "Park Ave", "200000"),
    [Role("USER", "basic")]
)
PrototypeRegistry.register("user", user_prototype)

# 使用示例
if __name__ == "__main__":
    # 从注册表克隆
    new_admin = PrototypeRegistry.create("admin")
    new_user = PrototypeRegistry.create("user")
    
    # 克隆并修改
    modified_user = user_prototype.clone_with_modifications(
        name="Bob",
        email="bob@company.com"
    )
    
    print(f"原始用户: {user_prototype.name}, {user_prototype.email}")
    print(f"修改用户: {modified_user.name}, {modified_user.email}")
    
    # 验证独立性
    user_prototype.address.city = "Hangzhou"
    print(f"原始地址: {user_prototype.address.city}")
    print(f"克隆地址: {new_user.address.city}")  # 不变✅
```

---

## TypeScript 实现

```typescript
// JavaScript/TypeScript - 原型链与克隆

// 领域模型
interface IAddress {
    city: string;
    street: string;
    zipCode: string;
}

interface IRole {
    name: string;
    permission: string;
}

interface IUser {
    id: number;
    name: string;
    email: string;
    address?: IAddress;
    roles: IRole[];
    createdAt: Date;
}

// 方案1: Object.assign (浅拷贝)
class UserShallowClone implements IUser {
    id: number;
    name: string;
    email: string;
    address?: IAddress;
    roles: IRole[];
    createdAt: Date;
    
    constructor(user: IUser) {
        Object.assign(this, user);  // ⚠️ 浅拷贝
    }
    
    clone(): UserShallowClone {
        return new UserShallowClone(this);
    }
}

// 方案2: 手动深拷贝 ✅ 推荐
class UserDeepClone implements IUser {
    id: number;
    name: string;
    email: string;
    address?: IAddress;
    roles: IRole[];
    createdAt: Date;
    
    constructor(
        id: number,
        name: string,
        email: string,
        address?: IAddress,
        roles?: IRole[]
    ) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.address = address;
        this.roles = roles || [];
        this.createdAt = new Date();
    }
    
    // 深拷贝实现
    clone(): UserDeepClone {
        const cloned = new UserDeepClone(
            this.id,
            this.name,
            this.email,
            // 深拷贝address
            this.address ? {
                city: this.address.city,
                street: this.address.street,
                zipCode: this.address.zipCode
            } : undefined,
            // 深拷贝roles
            this.roles.map(r => ({
                name: r.name,
                permission: r.permission
            }))
        );
        cloned.createdAt = new Date(this.createdAt);
        return cloned;
    }
}

// 方案3: JSON序列化克隆（通用但有局限）
class UserJSONClone implements IUser {
    id: number;
    name: string;
    email: string;
    address?: IAddress;
    roles: IRole[];
    createdAt: Date;
    
    clone(): UserJSONClone {
        // JSON.parse(JSON.stringify(...)) 通用深拷贝
        return JSON.parse(JSON.stringify(this));
    }
}

// 方案4: Builder模式 + 克隆
class UserBuilder implements IUser {
    id: number;
    name: string;
    email: string;
    address?: IAddress;
    roles: IRole[] = [];
    createdAt: Date;
    
    static fromUser(user: IUser): UserBuilder {
        // 从现有用户构建（克隆）
        const builder = new UserBuilder();
        builder.id = user.id;
        builder.name = user.name;
        builder.email = user.email;
        builder.address = user.address ? {...user.address} : undefined;
        builder.roles = [...user.roles];
        builder.createdAt = new Date(user.createdAt);
        return builder;
    }
    
    withName(name: string): UserBuilder {
        this.name = name;
        return this;
    }
    
    withAddress(address: IAddress): UserBuilder {
        this.address = {...address};
        return this;
    }
    
    addRole(role: IRole): UserBuilder {
        this.roles.push(role);
        return this;
    }
    
    build(): UserBuilder {
        return this;
    }
}

// 原型注册表
class PrototypeRegistry {
    private static prototypes = new Map<string, UserDeepClone>();
    
    static register(key: string, prototype: UserDeepClone) {
        this.prototypes.set(key, prototype);
    }
    
    static create(key: string): UserDeepClone {
        const prototype = this.prototypes.get(key);
        if (!prototype) {
            throw new Error(`Unknown prototype: ${key}`);
        }
        return prototype.clone();
    }
}

// 使用示例
const admin = new UserDeepClone(
    999,
    "Admin",
    "admin@company.com",
    { city: "Beijing", street: "Main St", zipCode: "100000" },
    [
        { name: "ADMIN", permission: "all" },
        { name: "USER", permission: "basic" }
    ]
);

PrototypeRegistry.register("admin", admin);

// 克隆
const newAdmin = PrototypeRegistry.create("admin");
newAdmin.name = "NewAdmin";

console.log(admin.name);      // "Admin"
console.log(newAdmin.name);   // "NewAdmin"

// 使用Builder克隆并修改
const modified = UserBuilder.fromUser(admin)
    .withName("ModifiedAdmin")
    .addRole({ name: "SUPERADMIN", permission: "unlimited" })
    .build();

console.log(modified.name);      // "ModifiedAdmin"
console.log(modified.roles.length); // 3
```

---

## 相关资源

| 资源 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Prototype完整详解 |
| [forms.md](forms.md) | 应用检查表 |
| 其他模式 | Factory、Builder、Singleton |
