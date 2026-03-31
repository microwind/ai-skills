# Facade 模式 - 完整参考实现

## 核心原理与设计

### 模式定义

**外观模式** 为复杂子系统提供一个统一的、简化的高层接口。模式的核心思想是使用单个统一的接口隐藏系统的复杂性。

**核心优势**:
- 🎭 **简化复杂性**: 多个类的协作变成一个简单调用
- 📦 **解耦客户端**: 客户端只依赖Facade，不知道子系统
- 🔒 **隐藏变化**: 子系统改动对客户端无影响
- 🎯 **代码复用**: 不同客户端复用相同的Facade逻辑

### UML结构

```
┌─────────────────────────────────┐
│  Subsystem Classes              │
├─────────────────────────────────┤
│  Database / Auth / Email / Log  │
└─────────────────────────────────┘
         △    △    △    △
         │    │    │    │
    ┌────┴────┴────┴────┴─────┐
    │       Facade            │
    ├───────────────────────────┤
    │ - database                │
    │ - auth                    │
    │ - email                   │
    │ + registerUser()          │
    │ + loginUser()             │
    └──────────────┬────────────┘
                   │ uses
            ┌──────▼──────┐
            │   Client    │
            └─────────────┘
```

---

## Java 实现 - 电影预订系统

```java
/**
 * 完整的电影预订Facade系统
 * 隐藏复杂的票务系统细节
 */

// ===== 子系统1: 影片信息 =====
public class Movie {
    private String id, title, director;
    private int duration;
    private double price;
    
    public Movie(String id, String title, String director, int duration, double price) {
        this.id = id;
        this.title = title;
        this.director = director;
        this.duration = duration;
        this.price = price;
    }
    
    public String getInfo() {
        return String.format("[%s] %s by %s (%d mins) - $%.2f", 
                           id, title, director, duration, price);
    }
    
    public double getPrice() { return price; }
    public String getId() { return id; }
}

// ===== 子系统2: 座位预订 =====
public class SeatBooking {
    private Map<String, boolean[]> movieSeats = new HashMap<>();
    
    public void initializeSeats(String movieId) {
        movieSeats.put(movieId, new boolean[16]);
    }
    
    public boolean checkSeat(String movieId, int seatNumber) {
        boolean[] seats = movieSeats.get(movieId);
        return seats != null && !seats[seatNumber];
    }
    
    public void reserveSeat(String movieId, int seatNumber) throws Exception {
        boolean[] seats = movieSeats.get(movieId);
        if (seats == null || seats[seatNumber]) {
            throw new Exception("Seat unavailable");
        }
        seats[seatNumber] = true;
    }
    
    public String getStatus(String movieId) {
        boolean[] seats = movieSeats.get(movieId);
        int available = (int)java.util.Arrays.stream(seats).filter(s -> !s).count();
        return available + "/16 available";
    }
}

// ===== 子系统3: 支付 =====
public class PaymentProcessor {
    public String processPayment(String customerId, double amount) {
        System.out.println("[Payment] Processing $" + amount);
        if (amount <= 0) throw new RuntimeException("Invalid amount");
        return "TXN-" + System.currentTimeMillis();
    }
}

// ===== 子系统4: 邮件通知 =====
public class EmailService {
    public void sendConfirmation(String email, String movie, int seat, double price) {
        System.out.println("[Email] Confirmation: " + movie + ", Seat " + seat + ", $" + price);
    }
}

// ===== 子系统5: 用户数据库 =====
public class UserDatabase {
    private Map<String, String> users = new HashMap<>();
    
    public void addUser(String customerId, String email) {
        users.put(customerId, email);
    }
}

// ===== 外观模式: MovieTicketFacade ✨ =====
public class MovieTicketFacade {
    private SeatBooking seatBooking = new SeatBooking();
    private PaymentProcessor payment = new PaymentProcessor();
    private EmailService email = new EmailService();
    private UserDatabase userDB = new UserDatabase();
    
    public String bookTicket(String customerId, String emailAddr, String movieTitle, int seat) {
        try {
            Movie movie = new Movie("001", movieTitle, "Director", 120, 12.50);
            
            if (seatBooking.movieSeats.get(movie.getId()) == null) {
                seatBooking.initializeSeats(movie.getId());
            }
            
            if (!seatBooking.checkSeat(movie.getId(), seat)) {
                throw new Exception("Seat unavailable");
            }
            
            String transactionId = payment.processPayment(customerId, movie.getPrice());
            seatBooking.reserveSeat(movie.getId(), seat);
            userDB.addUser(customerId, emailAddr);
            email.sendConfirmation(emailAddr, movieTitle, seat, movie.getPrice());
            
            return "✅ Booking confirmed! Transaction: " + transactionId;
        } catch (Exception e) {
            return "❌ Booking failed: " + e.getMessage();
        }
    }
}
```

---

## Python 实现 - 家庭剧院系统

```python
# ===== 子系统 =====
class Light:
    def dim(self, level):
        print(f"[Light] Dimmed to {level}%")
    def on(self):
        print("[Light] On")
    def off(self):
        print("[Light] Off")

class Projector:
    def on(self):
        print("[Projector] On")
    def off(self):
        print("[Projector] Off")
    def set_input(self, source):
        print(f"[Projector] Input: {source}")

class SoundSystem:
    def on(self):
        print("[Sound] On")
    def off(self):
        print("[Sound] Off")
    def set_volume(self, level):
        print(f"[Sound] Volume: {level}")

class Curtains:
    def open(self):
        print("[Curtains] Opened")
    def close(self):
        print("[Curtains] Closed")

# ===== Facade: 家庭剧院 ✨ =====
class HomeTheaterFacade:
    def __init__(self):
        self.light = Light()
        self.projector = Projector()
        self.sound = SoundSystem()
        self.curtains = Curtains()
    
    def watch_movie(self, movie_name):
        """一键看电影"""
        print(f"\n🎬 Starting: {movie_name}\n")
        self.curtains.close()
        self.light.dim(10)
        self.projector.on()
        self.projector.set_input("Blu-ray")
        self.sound.on()
        self.sound.set_volume(80)
        print("✅ Theater ready!\n")
    
    def end_movie(self):
        """电影结束"""
        print("\n🎬 Ending session\n")
        self.projector.off()
        self.sound.off()
        self.light.on()
        self.curtains.open()
        print("✅ Theater closed\n")

# 使用
theater = HomeTheaterFacade()
theater.watch_movie("Inception")
theater.end_movie()
```

---

## TypeScript 实现 - 快餐订单系统

```typescript
// ===== 子系统 =====
class Menu {
    private items = [
        { id: "1", name: "Burger", price: 8.99 },
        { id: "2", name: "Fries", price: 3.99 },
        { id: "3", name: "Drink", price: 2.99 }
    ];
    getItem(id: string) {
        return this.items.find(i => i.id === id);
    }
}

class Inventory {
    private stock = new Map([["1", 50], ["2", 100], ["3", 200]]);
    check(itemId: string) { return (this.stock.get(itemId) || 0) > 0; }
    decrease(itemId: string) {
        this.stock.set(itemId, (this.stock.get(itemId) || 0) - 1);
    }
}

class PaymentGateway {
    process(amount: number): boolean {
        console.log(`[Payment] $${amount}`);
        return Math.random() > 0.1;
    }
}

class OrderTracker {
    createOrder(items: string[]): string {
        const id = "ORD-" + Date.now();
        console.log(`[Order] Created: ${id}`);
        return id;
    }
}

// ===== Facade: 快餐订单 ✨ =====
class FastFoodOrderFacade {
    private menu = new Menu();
    private inventory = new Inventory();
    private payment = new PaymentGateway();
    private tracker = new OrderTracker();
    
    placeOrder(itemIds: string[], paymentMethod: string): string {
        try {
            let total = 0;
            for (const id of itemIds) {
                const item = this.menu.getItem(id);
                if (!item || !this.inventory.check(id)) {
                    throw new Error("Item unavailable");
                }
                total += item.price;
            }
            
            if (!this.payment.process(total)) {
                throw new Error("Payment failed");
            }
            
            for (const id of itemIds) {
                this.inventory.decrease(id);
            }
            
            return "✅ Order: " + this.tracker.createOrder(itemIds);
        } catch (e: any) {
            return "❌ " + e.message;
        }
    }
}
```

---

## 单元测试

```java
public class MovieTicketFacadeTest {
    private MovieTicketFacade facade;
    
    @Before
    public void setup() {
        facade = new MovieTicketFacade();
    }
    
    @Test
    public void testSuccessfulBooking() {
        String result = facade.bookTicket("C001", "test@example.com", "Test", 5);
        assertTrue(result.contains("✅"));
    }
    
    @Test
    public void testSeatUnavailable() {
        facade.bookTicket("C001", "a@example.com", "Test", 5);
        String result = facade.bookTicket("C002", "b@example.com", "Test", 5);
        assertTrue(result.contains("❌"));
    }
}
```

---

## 性能对比

| 场景 | 直接调用 | 使用Facade | 优势 |
|------|---------|-----------|------|
| 代码行数 | 30-40行 | 1-2行 | 减少95% |
| API复杂度 | 5+个接口 | 1个接口 | 简化80% |
| 子系统升级时影响 | 修改多处 | 只改Facade | 风险降低 |
| 测试复杂度 | 5个Mock | 1个Mock | 简化75% |

---

## 与其他模式的关系

| 模式 | 区别 | 结合 |
|------|------|------|
| **Adapter** | Adapter转换接口，Facade简化复杂性 | 先Facade后Adapter |
| **Factory** | Factory创建对象，Facade协调调用 | Factory创建Facade |
| **Strategy** | Strategy选择算法，Facade隐藏流程 | Facade中使用Strategy |
| **Decorator** | Decorator添加功能，Facade隐藏复杂 | 分离关切 |

---

## 常见问题 Q&A

1. **Q: Facade 能暴露子系统给高级用户吗？**
   A: 不推荐。应该为不同用户提供不同的Facade而不是暴露子系统。

2. **Q: Facade会成为性能瓶颈吗？**
   A: 不会。Facade只转发调用，开销<1%。

3. **Q: 多层Facade如何组织？**
   A: 顶层 → 中层(按功能) → 底层子系统

4. **Q: 如何处理异常？**
   A: 统一为一个FacadeException或返回Result对象。

5. **Q: 何时避免使用Facade？**
   A: 系统简单(<3类)且客户端需要细粒度控制时。

6. **Q: 运行时能切换子系统吗？**
   A: 可以，通过在Facade中注入不同的子系统实现。

7. **Q: Facade和Helper类的区别？**
   A: Facade协调复杂流程，Helper提供工具方法。
