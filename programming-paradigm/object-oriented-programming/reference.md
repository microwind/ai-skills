# 面向对象编程 - 参考实现

## Java 完整实现

```java
// 基类：通用属性和行为
public abstract class Shape {
    protected String color;
    protected String id;

    public Shape(String color) {
        this.color = color;
        this.id = UUID.randomUUID().toString();
    }

    public abstract double getArea();
    public abstract double getPerimeter();
    public abstract void draw();

    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }
}

// 子类1：圆形
public class Circle extends Shape {
    private double radius;

    public Circle(double radius, String color) {
        super(color);
        this.radius = radius;
    }

    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }

    @Override
    public double getPerimeter() {
        return 2 * Math.PI * radius;
    }

    @Override
    public void draw() {
        System.out.println(String.format(
            "Drawing circle [radius=%.2f, color=%s]", radius, color));
    }
}

// 子类2：矩形
public class Rectangle extends Shape {
    private double width, height;

    public Rectangle(double width, double height, String color) {
        super(color);
        this.width = width;
        this.height = height;
    }

    @Override
    public double getArea() {
        return width * height;
    }

    @Override
    public double getPerimeter() {
        return 2 * (width + height);
    }

    @Override
    public void draw() {
        System.out.println(String.format(
            "Drawing rectangle [width=%.2f, height=%.2f, color=%s]",
            width, height, color));
    }
}

// 应用：几何图形管理器
public class ShapeManager {
    private List<Shape> shapes = new ArrayList<>();

    public void addShape(Shape shape) {
        shapes.add(shape);
    }

    public double getTotalArea() {
        return shapes.stream()
            .mapToDouble(Shape::getArea)
            .sum();
    }

    public void drawAll() {
        shapes.forEach(Shape::draw);
    }

    public void printReport() {
        System.out.println("=== Shape Report ===");
        for (Shape shape : shapes) {
            System.out.println(String.format(
                "Shape: %s, Area: %.2f, Perimeter: %.2f",
                shape.getClass().getSimpleName(),
                shape.getArea(),
                shape.getPerimeter()));
        }
        System.out.println("Total Area: " + getTotalArea());
    }
}

// 使用
public class Demo {
    public static void main(String[] args) {
        ShapeManager manager = new ShapeManager();

        manager.addShape(new Circle(5, "RED"));
        manager.addShape(new Rectangle(10, 20, "BLUE"));
        manager.addShape(new Circle(3, "GREEN"));

        manager.drawAll();
        manager.printReport();
    }
}
```

## Python 实现

```python
from abc import ABC, abstractmethod
import uuid

class Shape(ABC):
    def __init__(self, color):
        self.color = color
        self.id = str(uuid.uuid4())

    @abstractmethod
    def get_area(self):
        pass

    @abstractmethod
    def get_perimeter(self):
        pass

    @abstractmethod
    def draw(self):
        pass

class Circle(Shape):
    def __init__(self, radius, color):
        super().__init__(color)
        self.radius = radius

    def get_area(self):
        return 3.14159 * self.radius ** 2

    def get_perimeter(self):
        return 2 * 3.14159 * self.radius

    def draw(self):
        print(f"Drawing circle [radius={self.radius}, color={self.color}]")

class Rectangle(Shape):
    def __init__(self, width, height, color):
        super().__init__(color)
        self.width = width
        self.height = height

    def get_area(self):
        return self.width * self.height

    def get_perimeter(self):
        return 2 * (self.width + self.height)

    def draw(self):
        print(f"Drawing rectangle [w={self.width}, h={self.height}, color={self.color}]")

class ShapeManager:
    def __init__(self):
        self.shapes = []

    def add_shape(self, shape):
        self.shapes.append(shape)

    def get_total_area(self):
        return sum(shape.get_area() for shape in self.shapes)

    def draw_all(self):
        for shape in self.shapes:
            shape.draw()

# 使用
manager = ShapeManager()
manager.add_shape(Circle(5, "RED"))
manager.add_shape(Rectangle(10, 20, "BLUE"))
manager.draw_all()
print(f"Total area: {manager.get_total_area():.2f}")
```

## TypeScript 实现

```typescript
abstract class Shape {
    id: string = Math.random().toString();

    constructor(public color: string) {}

    abstract getArea(): number;
    abstract getPerimeter(): number;
    abstract draw(): void;
}

class Circle extends Shape {
    constructor(private radius: number, color: string) {
        super(color);
    }

    getArea(): number {
        return Math.PI * this.radius ** 2;
    }

    getPerimeter(): number {
        return 2 * Math.PI * this.radius;
    }

    draw(): void {
        console.log(`Drawing circle [radius=${this.radius}, color=${this.color}]`);
    }
}

class Rectangle extends Shape {
    constructor(
        private width: number,
        private height: number,
        color: string
    ) {
        super(color);
    }

    getArea(): number {
        return this.width * this.height;
    }

    getPerimeter(): number {
        return 2 * (this.width + this.height);
    }

    draw(): void {
        console.log(
            `Drawing rectangle [w=${this.width}, h=${this.height}, color=${this.color}]`
        );
    }
}

class ShapeManager {
    private shapes: Shape[] = [];

    addShape(shape: Shape): void {
        this.shapes.push(shape);
    }

    getTotalArea(): number {
        return this.shapes.reduce((sum, shape) => sum + shape.getArea(), 0);
    }

    drawAll(): void {
        this.shapes.forEach(shape => shape.draw());
    }
}

// 使用
const manager = new ShapeManager();
manager.addShape(new Circle(5, "RED"));
manager.addShape(new Rectangle(10, 20, "BLUE"));
manager.drawAll();
console.log(`Total area: ${manager.getTotalArea().toFixed(2)}`);
```

## 单元测试示例

```java
@Test
public void testCircleArea() {
    Circle circle = new Circle(5, "RED");
    assertEquals(Math.PI * 25, circle.getArea(), 0.01);
}

@Test
public void testRectangleArea() {
    Rectangle rect = new Rectangle(10, 20, "BLUE");
    assertEquals(200, rect.getArea(), 0.01);
}

@Test
public void testShapeManager() {
    ShapeManager manager = new ShapeManager();
    manager.addShape(new Circle(5, "RED"));
    manager.addShape(new Rectangle(10, 20, "BLUE"));

    double expected = Math.PI * 25 + 200;
    assertEquals(expected, manager.getTotalArea(), 0.01);
}
```

---

## 核心原则

### 1. 单一职责
每个类只有一个改变的理由。

### 2. 开闭原则
对扩展开放，对修改关闭。

### 3. 里氏替换
子类可以替代父类而不破坏程序。

### 4. 接口隔离
依赖最小化的接口。

### 5. 依赖倒置
高层不依赖低层，都依赖抽象。

---

## 总结

**OOP的核心优势**：
- 通过继承复用代码
- 通过多态实现灵活性
- 通过封装隐藏复杂性
- 自然的问题分解

**最佳实践**：
- 优先组合而非继承
- 继承深度 ≤ 3 层
- 面向接口编程
- 遵循SOLID原则

OOP 对于复杂业务系统来说是最成熟、最广泛的范式。
