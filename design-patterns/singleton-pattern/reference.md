# 单例模式参考实现

## Java 实现

### 懒汉式（最安全的实现）- Bill Pugh 单例
```java
public class Singleton {
    private Singleton() {}
    
    // 静态内部类
    private static class SingletonHolder {
        private static final Singleton INSTANCE = new Singleton();
    }
    
    public static Singleton getInstance() {
        return SingletonHolder.INSTANCE;
    }
}
```

### 双检查锁定
```java
public class Singleton {
    private static volatile Singleton instance;
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

### 枚举实现（防止反射）
```java
public enum Singleton {
    INSTANCE;
    
    public void operation() {
        System.out.println("Operation");
    }
}
```

## Python 实现

### 装饰器方式
```python
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class MyClass:
    pass
```

### 元类方式
```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    pass
```

## 最佳实践

1. ✅ 私有构造函数
2. ✅ 线程安全初始化
3. ✅ 防止序列化破坏
4. ✅ 防止反射创建多实例

## 测试方法

```java
@Test
public void testSingletonIdentity() {
    Singleton s1 = Singleton.getInstance();
    Singleton s2 = Singleton.getInstance();
    assertTrue(s1 == s2);
}
```

## 常见问题

### Q: 线程安全吗？
**A**: 使用 Bill Pugh 单例或枚举实现完全线程安全。

### Q: 支持序列化吗？
**A**: 枚举实现支持，其他实现需要实现 readResolve() 方法。

### Q: 可以反射创建多实例吗？
**A**: 使用枚举实现无法被反射破坏。
