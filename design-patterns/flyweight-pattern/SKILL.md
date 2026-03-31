---
name: Flyweight
description: "使用共享来有效支持大量细粒度的对象"
license: MIT
---

# Flyweight Pattern (享元模式)

## 核心概念

**Flyweight** 是一种**结构型设计模式**，通过共享细粒度对象来节省内存。

### 核心思想
- 💾 **内存优化** - 消除重复对象
- ⚡ **性能提升** - 减少GC压力、减少创建开销
- 🔄 **状态分离** - 内部状态(共享) vs 外部状态(不共享)
- 🎯 **对象池** - 复用而非频繁创建销毁

### 适用条件
- 对象数量很大（数百万级）
- 创建对象成本高
- 对象之间有大量重复状态
- 可以接受共享

## 何时使用

1. **大量细粒度对象** - 文本编辑器中的字符、游戏中的粒子、图形系统中的图元
2. **内存是瓶颈** - 对象数量多导致GC频繁
3. **对象有可复用的内容** - 如"字体"对象可被共享
4. **需要高效缓存** - 对象池的实现
5. **支持数据库连接池、线程池** - 连接/线程可复用

## 实现方式

### 方法1: 经典对象池

```java
// 享元对象 - immutable
public class Character {
    private char value;
    private String font;
    private int size;
    
    public Character(char v, String f, int s) {
        this.value = v;
        this.font = f;
        this.size = s;
    }
    
    public void display(int x, int y) {
        // 渲染
    }
}

// 享元工厂 - 管理对象池
public class CharacterFactory {
    private Map<String, Character> pool = new HashMap<>();
    
    public Character getCharacter(char c, String font, int size) {
        String key = c + "-" + font + "-" + size;
        
        return pool.computeIfAbsent(key, k -> 
            new Character(c, font, size)
        );
    }
    
    public int poolSize() {
        return pool.size();
    }
}

// 使用
CharacterFactory factory = new CharacterFactory();
Character a1 = factory.getCharacter('A', "Arial", 12);
Character a2 = factory.getCharacter('A', "Arial", 12);
assert a1 == a2;  // 同一对象！
```

### 方法2: 分类对象池

```java
public class CategorizedFlyweightFactory {
    private Map<Class<?>, Map<String, Object>> pools = new HashMap<>();
    
    public <T> T get(Class<T> type, String key, Supplier<T> supplier) {
        Map<String, Object> pool = pools.computeIfAbsent(
            type, 
            k -> new ConcurrentHashMap<>()
        );
        
        return type.cast(pool.computeIfAbsent(key, k -> supplier.get()));
    }
}

// 使用
CategorizedFlyweightFactory factory = new CategorizedFlyweightFactory();
Font arial12 = factory.get(Font.class, "Arial-12", () -> 
    new Font("Arial", 12)
);
```

### 方法3: 弱引用池（自动清理）

```java
public class WeakReferenceFlyweightFactory {
    private Map<String, WeakReference<Flyweight>> pool = new WeakHashMap<>();
    
    public Flyweight get(String key, Supplier<Flyweight> supplier) {
        WeakReference<Flyweight> ref = pool.get(key);
        Flyweight obj = ref != null ? ref.get() : null;
        
        if (obj == null) {
            obj = supplier.get();
            pool.put(key, new WeakReference<>(obj));
        }
        
        return obj;
    }
}
```

### 方法4: LRU缓存池

```java
public class LRUFlyweightFactory {
    private final int maxSize;
    private LinkedHashMap<String, Flyweight> cache;
    
    public LRUFlyweightFactory(int size) {
        this.maxSize = size;
        this.cache = new LinkedHashMap<String, Flyweight>(size, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry eldest) {
                return size() > maxSize;
            }
        };
    }
    
    public Flyweight get(String key, Supplier<Flyweight> supplier) {
        return cache.computeIfAbsent(key, k -> supplier.get());
    }
}
```

## 深入讲解：内部状态 vs 外部状态

### 核心概念澄清

**内部状态(Intrinsic State)**：
- 📌 **不可变** (immutable)
- 🔄 **可共享** (shareable)
- 📦 **体积小** (compact)
- 例：Font对象、Texture对象、颜色配置

**外部状态(Extrinsic State)**：
- 🔀 **易变** (mutable)
- 🚫 **不可共享** (unshareable)
- 📐 **通常是坐标、位置、临时数据**
- 例：屏幕坐标(x, y)、对象ID、操作参数

### 判断标准 - 状态分离矩阵

```
属性            是否共享    是否可变    应该存储在
─────────────────────────────────────────────
字体名称         共享       不变       内部状态✅
字体大小         共享       不变       内部状态✅
文字内容         不共享     可变       外部状态✅
屏幕位置(x, y)   不共享     可变       外部状态✅
颜色             共享       不变       内部状态✅
样式(粗体/斜体)  共享       不变       内部状态✅
用户输入数据     不共享     可变       外部状态✅
```

### 实战例子：文本编辑器

```java
// ❌ 非享元方式 - 100万字符，每个都是独立对象
public class CharacterNormal {
    private char value;
    private String fontName;      // 重复！
    private int fontSize;         // 重复！
    private Color color;          // 重复！
    private int positionX;        // 不同
    private int positionY;        // 不同
    
    // 每个字符占用: ~200bytes（假设）
    // 100万个: 200MB! 太大了
}

// ✅ 享元方式 - 100万字符，但字体对象共享
public class CharacterFlyweight {
    // 内部状态 - 共享
    private final char value;
    private final Font font;      // 共享Font对象
    private final Color color;    // 共享Color对象
    
    // 字符只占: ~64bytes
    // 100万个: 64MB ✅ 减少了70%
    
    public CharacterFlyweight(char v, Font f, Color c) {
        this.value = v;
        this.font = f;
        this.color = c;
    }
}

// 外部状态 - 单独维护
public class TextLine {
    private List<CharacterFlyweight> characters;
    private Map<Integer, Integer> positionMap;  // 字符位置
    
    public void display(Graphics g) {
        for (int i = 0; i < characters.size(); i++) {
            CharacterFlyweight ch = characters.get(i);
            int x = positionMap.get(i);  // 外部位置
            int y = currentLine * fontSize;
            
            g.drawCharacter(ch, x, y);
        }
    }
}
```

---

## 4种对象池实现方案

### 方案1: 基础HashMap池（简单场景）

```java
public class BasicFlyweightPool {
    private Map<String, Flyweight> pool = new HashMap<>();
    
    public Flyweight get(String key) {
        return pool.computeIfAbsent(key, k -> 
            createFlyweight(k)
        );
    }
    
    private Flyweight createFlyweight(String key) {
        // 解析key并创建
        // key格式: "Arial-12-Black"
        String[] parts = key.split("-");
        return new Flyweight(parts[0], Integer.parseInt(parts[1]), parts[2]);
    }
    
    public int getPoolSize() {
        return pool.size();
    }
}

// 使用
BasicFlyweightPool pool = new BasicFlyweightPool();
Flyweight f1 = pool.get("Arial-12-Black");
Flyweight f2 = pool.get("Arial-12-Black");
assert f1 == f2;  // 完全相同的对象
```

**优缺点**:
- ✅ 简单直接
- ✅ 高效查找(O(1))
- ❌ 内存泄漏风险（对象永不释放）
- ❌ 不适合大量短生命周期对象

### 方案2: 弱引用池（自动清理）

```java
public class WeakReferenceFlyweightPool {
    // WeakHashMap: key被GC时自动移除
    private Map<String, WeakReference<Flyweight>> pool = 
        new WeakHashMap<>();
    
    public Flyweight get(String key) {
        WeakReference<Flyweight> ref = pool.get(key);
        Flyweight flyweight = (ref != null) ? ref.get() : null;
        
        if (flyweight == null) {
            // 对象被GC了，重新创建
            flyweight = createFlyweight(key);
            pool.put(key, new WeakReference<>(flyweight));
        }
        
        return flyweight;
    }
    
    private Flyweight createFlyweight(String key) {
        // 创建逻辑
    }
}

// 使用
WeakReferenceFlyweightPool pool = new WeakReferenceFlyweightPool();
Flyweight f1 = pool.get("Arial-12");

// f1没有其他引用时，会被GC回收
// 下次get时，会重新创建
```

**优缺点**:
- ✅ 自动清理内存
- ✅ 无内存泄漏风险
- ❌ GC不确定性（可能频繁重建）
- ❌ 适合内存充足的场景

### 方案3: LRU缓存池（限制大小）

```java
public class LRUFlyweightPool {
    private static final int POOL_SIZE = 1000;
    
    // LinkedHashMap + 访问顺序保证LRU
    private LinkedHashMap<String, Flyweight> cache = 
        new LinkedHashMap<String, Flyweight>(
            POOL_SIZE, 
            0.75f,
            true  // accessOrder=true → LRU
        ) {
            @Override
            protected boolean removeEldestEntry(Map.Entry eldest) {
                // 超过容量时移除最旧的
                return size() > POOL_SIZE;
            }
        };
    
    public synchronized Flyweight get(String key) {
        return cache.computeIfAbsent(key, k -> 
            createFlyweight(k)
        );
    }
    
    private Flyweight createFlyweight(String key) {
        // 创建逻辑
    }
    
    public int getHitRate() {
        // 统计命中率
    }
}

// 使用
LRUFlyweightPool pool = new LRUFlyweightPool();
for (int i = 0; i < 10000; i++) {
    String key = "Font-" + (i % 500);  // 500种字体
    Flyweight f = pool.get(key);
}

System.out.println("缓存大小: " + pool.getSize());      // 最多1000
System.out.println("命中率: " + pool.getHitRate());      // > 90%
```

**优缺点**:
- ✅ 可控的内存占用
- ✅ 高命中率
- ⚠️ 需要同步保护
- ⚠️ 较复杂的实现

### 方案4: 分类对象池（多类型管理）

```java
public class CategorizedFlyweightPool {
    private Map<Class<?>, Map<String, Object>> pools = 
        new ConcurrentHashMap<>();
    
    public <T> T get(Class<T> type, String key, Supplier<T> creator) {
        // 为每个类型维护独立的池
        Map<String, Object> typePool = pools.computeIfAbsent(
            type,
            k -> new ConcurrentHashMap<>()
        );
        
        // 在该类型的池中查询
        Object obj = typePool.computeIfAbsent(key, k -> creator.get());
        return type.cast(obj);
    }
    
    public void clearPool(Class<?> type) {
        pools.remove(type);
    }
    
    public int getPoolSize(Class<?> type) {
        return pools.getOrDefault(type, Collections.emptyMap()).size();
    }
}

// 使用
CategorizedFlyweightPool pool = new CategorizedFlyweightPool();

// 字体池
Font arial12 = pool.get(
    Font.class, 
    "Arial-12", 
    () -> new Font("Arial", 12)
);

// 颜色池
Color red = pool.get(
    Color.class,
    "RED",
    () -> new Color(255, 0, 0)
);

// 音频池
AudioClip bark = pool.get(
    AudioClip.class,
    "dog-bark.wav",
    () -> new AudioClip(loadWav("dog-bark.wav"))
);

// 统计
System.out.println("Font池大小: " + pool.getPoolSize(Font.class));
System.out.println("Color池大小: " + pool.getPoolSize(Color.class));
```

**优缺点**:
- ✅ 灵活的类型管理
- ✅ 类型隔离
- ✅ 易于扩展
- ⚠️ 实现相对复杂

---

## 4个常见问题的深度解决

### 问题1: 内部状态修改导致共享破坏

**症状**: 一个享元对象的状态被修改，影响了所有使用者

**反面示例（❌ 错误）**:
```java
public class MutableFlyweight {
    private String fontName;
    private int fontSize;
    
    // ❌ 提供了setter - 破坏了享元原则
    public void setFontSize(int size) {
        this.fontSize = size;
    }
}

// 使用中的灾难
Flyweight f1 = pool.get("Arial-12");
// 此时1000000个享元对象都指向这个字体

f1.setFontSize(24);  // ❌ 修改了！
// 结果：所有1000000个字符的字体都变了！
```

**解决方案（✅ 正确）**:
```java
public final class ImmutableFlyweight {
    private final String fontName;
    private final int fontSize;
    private final Color color;
    
    // ✅ 使用final - 无法修改
    public ImmutableFlyweight(String name, int size, Color c) {
        this.fontName = name;
        this.fontSize = size;
        this.color = c;
    }
    
    // ✅ 只有getter，没有setter
    public String getFontName() { return fontName; }
    public int getFontSize() { return fontSize; }
    public Color getColor() { return color; }
    
    // ✅ 如果需要"修改"，返回新对象
    public ImmutableFlyweight withFontSize(int newSize) {
        return new ImmutableFlyweight(fontName, newSize, color);
    }
}

// 使用
Flyweight f1 = pool.get("Arial-12");
Flyweight f2 = f1.withFontSize(24);  // 返回新对象，不修改原对象
```

### 问题2: 外部状态泄漏

**症状**: 外部状态被存储在享元对象中，破坏了设计

**反面示例（❌ 错误）**:
```java
// ❌ 外部状态混入享元
public class BadFlyweight {
    // 享元应该共享的
    private Font font;
    
    // 外部状态，不应该在这里！
    private int positionX;     // ❌
    private int positionY;     // ❌
    private String content;    // ❌
    private long timestamp;    // ❌
}

// 后果：
// - 享元对象体积不再小
// - 不能真正共享
// - GC压力未减少
```

**正确做法（✅）**:
```java
// ✅ 享元类只包含内部状态
public class Flyweight {
    private final Font font;
    private final Color color;
    
    // 没有任何外部状态！
}

// ✅ 外部状态单独维护
public class TextPosition {
    private Flyweight flyweight;  // 指向享元
    private int x, y;              // 外部：位置
    private String content;        // 外部：内容
    
    public void render(Graphics g) {
        g.drawText(flyweight, x, y, content);
    }
}

// ✅ 或者用Map维护
Map<FlyweightKey, ExternalState> externalStates;
```

### 问题3: 线程安全问题

**症状**: 多线程并发访问享元对象池时出现冲突

**反面示例（❌ 不安全）**:
```java
// ❌ 非线程安全
public class UnsafeFlyweightPool {
    private Map<String, Flyweight> pool = new HashMap<>();
    
    public Flyweight get(String key) {
        if (pool.containsKey(key)) {
            return pool.get(key);
        }
        
        // ❌ 两个线程可能同时执行到这里
        Flyweight f = createFlyweight(key);
        pool.put(key, f);  // 重复创建！
        return f;
    }
}

// 场景：
// Thread1: 不存在，创建了Flyweight1
// Thread2: 同时在创建，创建了Flyweight2
// 结果：两个相同的对象，违反享元原则
```

**解决方案1: 同步方法**:
```java
public class SynchronizedFlyweightPool {
    private Map<String, Flyweight> pool = new HashMap<>();
    
    public synchronized Flyweight get(String key) {
        return pool.computeIfAbsent(key, k -> createFlyweight(k));
    }
}
// 缺点：所有get操作都要等待，性能低
```

**解决方案2: ConcurrentHashMap**:
```java
public class ConcurrentFlyweightPool {
    private ConcurrentHashMap<String, Flyweight> pool = 
        new ConcurrentHashMap<>();
    
    public Flyweight get(String key) {
        // computeIfAbsent是原子的，不会重复创建
        return pool.computeIfAbsent(key, k -> createFlyweight(k));
    }
}
// 优势：并发性更好，只在必要时同步
```

**解决方案3: 双重检查**:
```java
public class DoubleCheckFlyweightPool {
    private volatile Map<String, Flyweight> pool = 
        new ConcurrentHashMap<>();
    
    public Flyweight get(String key) {
        Flyweight f = pool.get(key);
        
        if (f == null) {
            synchronized (this) {  // 只在第一次创建时同步
                f = pool.get(key);
                if (f == null) {
                    f = createFlyweight(key);
                    pool.put(key, f);
                }
            }
        }
        
        return f;
    }
}
// 折衷方案：性能与安全平衡
```

### 问题4: 内存泄漏风险

**症状**: 享元对象不释放，导致内存持续增长

**反面示例（❌ 泄漏）**:
```java
// ❌ 基本Map池 - 永不释放
public class LeakyPool {
    private Map<String, Flyweight> pool = new HashMap<>();
    
    public Flyweight get(String key) {
        return pool.computeIfAbsent(key, k -> createFlyweight(k));
    }
    
    // ❌ 没有清理机制
}

// 使用场景导致泄漏：
for (int hour = 0; hour < 24; hour++) {
    for (int minute = 0; minute < 60; minute++) {
        // 每分钟创建新的时间戳字符串
        String timestamp = hour + ":" + minute;
        Flyweight f = pool.get("time-" + timestamp);
        // 1440个不同的key，都留在池里！
    }
}
// 结果：内存持续占用
```

**解决方案1: 手动清理**:
```java
public class CleanableFlyweightPool {
    private Map<String, Flyweight> pool = new HashMap<>();
    private long lastCleanupTime = System.currentTimeMillis();
    private static final long CLEANUP_INTERVAL = 60000;  // 1分钟
    
    public Flyweight get(String key) {
        // 定期清理
        if (System.currentTimeMillis() - lastCleanupTime > CLEANUP_INTERVAL) {
            cleanup();
            lastCleanupTime = System.currentTimeMillis();
        }
        
        return pool.computeIfAbsent(key, k -> createFlyweight(k));
    }
    
    private void cleanup() {
        // 保留热门对象，删除冷门对象
        pool.entrySet().removeIf(e -> shouldEvict(e.getKey()));
    }
    
    private boolean shouldEvict(String key) {
        // 根据使用频率、年龄等判断
    }
}
```

**解决方案2: 使用WeakReference**:
```java
public class SelfCleaningPool {
    private Map<String, WeakReference<Flyweight>> pool = 
        new WeakHashMap<>();
    
    public Flyweight get(String key) {
        WeakReference<Flyweight> ref = pool.get(key);
        Flyweight f = (ref != null) ? ref.get() : null;
        
        if (f == null) {
            f = createFlyweight(key);
            pool.put(key, new WeakReference<>(f));
        }
        
        return f;
    }
}
// JVM自动GC，无需手动
```

---

## 使用场景详解

### 场景1: 文本编辑器的字符表示

```java
// Google Docs: 处理数百万字符时的内存优化
public class DocumentCharacter {
    // 内部状态 - 共享
    private final Font font;
    private final Color textColor;
    private final Color backgroundColor;
    
    // 外部状态 - 不共享
    // (由外部Document管理)
}

public class Document {
    private FontPool fontPool = new FontPool();
    private List<DocumentCharacter> characters;
    private int[] characterPositions;
    
    public void insertCharacter(char ch, Font font, int position) {
        DocumentCharacter dc = new DocumentCharacter(
            fontPool.get(font),  // 共享Font对象
            defaultColor,
            backgroundColor
        );
        
        characters.add(dc);
        characterPositions[characters.size()-1] = position;
    }
}
```

### 场景2: 游戏粒子系统

```java
// Unity引擎中的大型粒子效果
public class Particle {
    // 内部状态 - 共享
    private final Mesh mesh;
    private final Material material;
    private final Texture texture;
    private final Shader shader;
    
    // 外部状态 - 不共享
    // (由ParticleEmitter维护)
}

public class ParticleEmitter {
    private ParticlePool particlePool;
    private List<ParticleInstance> activeParticles;
    
    public void emit(int count) {
        for (int i = 0; i < count; i++) {
            Particle particle = particlePool.getParticle("fire");
            ParticleInstance instance = new ParticleInstance(
                particle,
                randomPosition(),  // 外部
                randomVelocity()   // 外部
            );
            activeParticles.add(instance);
        }
    }
}

// 性能对比：
// 不用享元: 1000000 particles × 200bytes = 200MB
// 用享元:   1000 unique particles × 200bytes + 1000000 × 40bytes = 40MB ✅
```

### 场景3: 数据库连接池

```java
// HikariCP连接池
public class ConnectionPool {
    private ConcurrentHashMap<String, Connection> pool = 
        new ConcurrentHashMap<>();
    
    public Connection getConnection(String url) {
        return pool.computeIfAbsent(url, dbUrl -> 
            createConnection(dbUrl)
        );
    }
    
    public void releaseConnection(String url, Connection conn) {
        // 不关闭连接，放回池中复用
        pool.put(url, conn);
    }
}

// 性能收益：
// - 创建DB连接成本高 (1-10ms)
// - 享元复用: 创建1次, 使用1000次
// - 性能提升 100倍+
```

### 场景4: 字符串常量池

```java
// Java String Pool 的享元实现
public class StringPool {
    private static Map<String, String> pool = new HashMap<>();
    
    public static String intern(String str) {
        // String.intern()就是享元模式
        return pool.computeIfAbsent(str, k -> str);
    }
}

// 示例：
String s1 = "hello";
String s2 = "hello";
assert s1 == s2;  // 同一个对象！ 享元

// vs
String s3 = new String("hello");
String s4 = new String("hello");
assert s3 != s4;  // 不同对象
assert s3.equals(s4));  // 内容相同
```

### 场景5: 格式化日期/时间

```java
// SimpleDateFormat复用（享元）
public class DateFormatPool {
    private Map<String, SimpleDateFormat> pool = new ConcurrentHashMap<>();
    
    public String format(Date date, String pattern) {
        SimpleDateFormat sdf = pool.computeIfAbsent(pattern, p -> 
            new SimpleDateFormat(p)
        );
        
        synchronized (sdf) {  // SimpleDateFormat不线程安全
            return sdf.format(date);
        }
    }
}

// 代替每次都new SimpleDateFormat
// 性能提升：构造成本很高 (分析正则表达式等)
```

### 场景6: 图标/图片缓存

```java
// Android/Swing UI框架中的图标共享
public class IconCache {
    private Map<String, Icon> cache = new ConcurrentHashMap<>();
    
    public Icon getIcon(String name) {
        return cache.computeIfAbsent(name, n -> 
            loadIcon(n)  // 磁盘I/O一次
        );
    }
}

// 应用场景：
// 同一个图标被用在100个地方
// 不用享元：加载100次，占用内存100倍
// 用享元：加载1次，所有地方共享 ✅
```

---

## 最佳实践

1. ✅ **享元对象必须immutable** - 使用final字段，无setter
2. ✅ **分离内部/外部状态** - 明确文档化
3. ✅ **线程安全的池** - 使用ConcurrentHashMap
4. ✅ **监控池大小** - 定期检查有无泄漏
5. ✅ **性能验证** - 确实带来了内存/性能收益

## 何时避免使用

- ❌ 对象数量少(<100) - 收益不足
- ❌ 对象状态完全不同 - 难以共享
- ❌ 创建成本很低 - 不值得优化
- ❌ 团队不理解不可变性 - 容易出错
