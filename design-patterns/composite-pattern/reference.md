# Composite - 完整参考实现

##Java实现- 文件系统

```java
public interface FileSystemComponent {
    void display(int depth);
    int getSize();
}

public class File implements FileSystemComponent {
    private String name;
    private int size;
    
    public File(String n, int s) { name = n; size = s; }
    
    @Override
    public void display(int d) {
        System.out.println("  ".repeat(d) + "📄 " + name);
    }
    
    @Override
    public int getSize() { return size; }
}

public class Directory implements FileSystemComponent {
    private String name;
    private List<FileSystemComponent> items = new ArrayList<>();
    
    public Directory(String n) { name = n; }
    public void add(FileSystemComponent c) { items.add(c); }
    
    @Override
    public void display(int d) {
        System.out.println("  ".repeat(d) + "📁 " + name);
        items.forEach(i -> i.display(d+1));
    }
    
    @Override
    public int getSize() {
        return items.stream().mapToInt(FileSystemComponent::getSize).sum();
    }
}

// 使用
Directory root = new Directory("root");
Directory docs = new Directory("Documents");
docs.add(new File("file1.txt", 100));
root.add(docs);
root.display(0);
System.out.println("Total: " + root.getSize());
```

## Python实现

```python
from abc import ABC, abstractmethod

class Node(ABC):
    @abstractmethod
    def display(self, depth=0):
        pass
    
    @abstractmethod
    def get_size(self):
        pass

class Leaf(Node):
    def __init__(self, name, size):
        self.name = name
        self.size = size
    
    def display(self, depth=0):
        print("  " * depth + f"📄 {self.name}")
    
    def get_size(self):
        return self.size

class Composite(Node):
    def __init__(self, name):
        self.name = name
        self.children = []
    
    def add(self, child):
        self.children.append(child)
    
    def display(self, depth=0):
        print("  " * depth + f"📁 {self.name}")
        for child in self.children:
            child.display(depth + 1)
    
    def get_size(self):
        return sum(c.get_size() for c in self.children)

# 使用
root = Composite("root")
docs = Composite("Documents")
docs.add(Leaf("file1.txt", 100))
root.add(docs)
root.display()
print(f"Total: {root.get_size()}")
```

## TypeScript实现

```typescript
interface Node {
    display(depth: number): void;
    getSize(): number;
}

class Leaf implements Node {
    constructor(private name: string, private size: number) {}
    
    display(depth: number): void {
        console.log("  ".repeat(depth) + "📄 " + this.name);
    }
    
    getSize(): number {
        return this.size;
    }
}

class Composite implements Node {
    private children: Node[] = [];
    
    constructor(private name: string) {}
    
    add(child: Node): void {
        this.children.push(child);
    }
    
    display(depth: number): void {
        console.log("  ".repeat(depth) + "📁 " + this.name);
        this.children.forEach(c => c.display(depth + 1));
    }
    
    getSize(): number {
        return this.children.reduce((sum, c) => sum + c.getSize(), 0);
    }
}
```

## 单元测试

### Java

```java
@Test
public void testFileSystem() {
    Directory root = new Directory("root");
    File f1 = new File("test.txt", 100);
    root.add(f1);
    
    assertEquals(100, root.getSize());
    assertDoesNotThrow(() -> root.display(0));
}

@Test
public void testCyclicDetection() {
    Directory d1 = new Directory("d1");
    Directory d2 = new Directory("d2");
    d1.add(d2);
    
    assertThrows(Exception.class, () -> d2.add(d1));
}
```

### Python

```python
def test_size():
    root = Composite("root")
    root.add(Leaf("f1", 100))
    assert root.get_size() == 100

def test_nested():
    root = Composite("root")
    sub = Composite("sub")
    sub.add(Leaf("f", 50))
    root.add(sub)
    assert root.get_size() == 50
```

## 性能对比

| 操作 | 透明组合 | 安全组合 |
|------|---------|---------|
| 添加 | O(1) | O(1) |
| 删除 | O(n) | O(n) |
| 遍历 | O(n) | O(n) |
| 大小 | O(n) | O(n) |

## 常见问题

- Q1: 如何防止循环? A: 检测元素是否已在树中
- Q2: 大树如何优化? A: 迭代遍历、缓存结果、分层加载
- Q3: 内存溢出? A: 定期清理、限制深度

---

## 进阶案例 1: DOM 树结构

```java
public interface DOMNode {
    void render();
    void addChild(DOMNode child);
    void removeChild(DOMNode child);
    List<DOMNode> getChildren();
}

public class TextNode implements DOMNode {
    private String content;
    
    public TextNode(String content) {
        this.content = content;
    }
    
    @Override
    public void render() {
        System.out.println(content);
    }
    
    @Override
    public void addChild(DOMNode child) {
        throw new UnsupportedOperationException("Text node cannot have children");
    }
    
    @Override
    public void removeChild(DOMNode child) {}
    
    @Override
    public List<DOMNode> getChildren() {
        return Collections.emptyList();
    }
}

public class Element implements DOMNode {
    private String tagName;
    private List<DOMNode> children = new ArrayList<>();
    private Map<String, String> attributes = new HashMap<>();
    
    public Element(String tagName) {
        this.tagName = tagName;
    }
    
    public void setAttribute(String name, String value) {
        attributes.put(name, value);
    }
    
    @Override
    public void render() {
        System.out.print("<" + tagName);
        attributes.forEach((k, v) -> System.out.print(" " + k + "=\"" + v + "\""));
        System.out.println(">");
        
        children.forEach(DOMNode::render);
        
        System.out.println("</" + tagName + ">");
    }
    
    @Override
    public void addChild(DOMNode child) {
        children.add(child);
    }
    
    @Override
    public void removeChild(DOMNode child) {
        children.remove(child);
    }
    
    @Override
    public List<DOMNode> getChildren() {
        return new ArrayList<>(children);
    }
}

// 使用
Element html = new Element("html");
Element head = new Element("head");
Element body = new Element("body");

Element title = new Element("title");
title.addChild(new TextNode("My Page"));
head.addChild(title);

Element h1 = new Element("h1");
h1.setAttribute("class", "header");
h1.addChild(new TextNode("Welcome"));
body.addChild(h1);

html.addChild(head);
html.addChild(body);
html.render();
```

---

## 进阶案例 2: 组织结构

```java
public abstract class Employee {
    protected String name;
    protected double salary;
    protected List<Employee> subordinates = new ArrayList<>();
    
    public Employee(String name, double salary) {
        this.name = name;
        this.salary = salary;
    }
    
    public void add(Employee emp) {
        subordinates.add(emp);
    }
    
    public void remove(Employee emp) {
        subordinates.remove(emp);
    }
    
    public List<Employee> getSubordinates() {
        return new ArrayList<>(subordinates);
    }
    
    public double getTotalSalary() {
        return salary + subordinates.stream()
            .mapToDouble(Employee::getTotalSalary).sum();
    }
    
    public abstract void display(int depth);
    
    public void displayAll(int depth) {
        display(depth);
        subordinates.forEach(e -> e.displayAll(depth + 1));
    }
}

public class Manager extends Employee {
    private String department;
    
    public Manager(String name, double salary, String dept) {
        super(name, salary);
        this.department = dept;
    }
    
    @Override
    public void display(int depth) {
        System.out.println("  ".repeat(depth) + 
            "👔 [Manager] " + name + " - " + department);
    }
}

public class Developer extends Employee {
    private String language;
    
    public Developer(String name, double salary, String lang) {
        super(name, salary);
        this.language = lang;
    }
    
    @Override
    public void display(int depth) {
        System.out.println("  ".repeat(depth) + 
            "💻 [Dev] " + name + " (" + language + ")");
    }
}

// 使用
Manager ceo = new Manager("Alice", 100000, "Executive");
Manager techLead = new Manager("Bob", 80000, "Technology");
Developer dev1 = new Developer("Charlie", 60000, "Java");
Developer dev2 = new Developer("Diana", 55000, "Python");

techLead.add(dev1);
techLead.add(dev2);
ceo.add(techLead);

ceo.displayAll(0);
System.out.println("Total salary: $" + ceo.getTotalSalary());
```

---

## 进阶案例 3: 菜单系统

```java
public interface MenuItem {
    void display(int depth);
    void click();
}

public class Menu implements MenuItem {
    private String name;
    private List<MenuItem> items = new ArrayList<>();
    
    public Menu(String name) {
        this.name = name;
    }
    
    public void addItem(MenuItem item) {
        items.add(item);
    }
    
    @Override
    public void display(int depth) {
        System.out.println("  ".repeat(depth) + "📂 " + name);
        items.forEach(i -> i.display(depth + 1));
    }
    
    @Override
    public void click() {
        System.out.println("Menu: " + name + " clicked");
        items.forEach(MenuItem::click);
    }
}

public class Action implements MenuItem {
    private String label;
    private Runnable handler;
    
    public Action(String label, Runnable handler) {
        this.label = label;
        this.handler = handler;
    }
    
    @Override
    public void display(int depth) {
        System.out.println("  ".repeat(depth) + "▶ " + label);
    }
    
    @Override
    public void click() {
        System.out.println("Action: " + label);
        handler.run();
    }
}

// 使用
Menu mainMenu = new Menu("Main");
Menu fileMenu = new Menu("File");
Menu editMenu = new Menu("Edit");

fileMenu.addItem(new Action("New", () -> System.out.println("Creating new file")));
fileMenu.addItem(new Action("Open", () -> System.out.println("Opening file")));
fileMenu.addItem(new Action("Save", () -> System.out.println("Saving file")));

editMenu.addItem(new Action("Undo", () -> System.out.println("Undoing")));
editMenu.addItem(new Action("Redo", () -> System.out.println("Redoing")));

mainMenu.addItem(fileMenu);
mainMenu.addItem(editMenu);

mainMenu.display(0);
mainMenu.click();
```

---

## 优化策略

### 1. 性能缓存

```java
public class CachedComposite implements DOMNode {
    private Element delegate;
    private int cachedSize = -1;
    private long cacheTime = 0;
    private static final long CACHE_TTL = 5000; // 5秒
    
    public int getCachedSize() {
        if (System.currentTimeMillis() - cacheTime > CACHE_TTL) {
            cachedSize = calculateSize();
            cacheTime = System.currentTimeMillis();
        }
        return cachedSize;
    }
    
    private int calculateSize() {
        // 计算大小
        return 0;
    }
}
```

### 2. 延迟加载

```java
public class LazyComposite implements DOMNode {
    private List<DOMNode> children;
    private Supplier<List<DOMNode>> loader;
    private boolean loaded = false;
    
    public LazyComposite(Supplier<List<DOMNode>> loader) {
        this.loader = loader;
        this.children = new ArrayList<>();
    }
    
    private void load() {
        if (!loaded) {
            children.addAll(loader.get());
            loaded = true;
        }
    }
    
    public List<DOMNode> getChildren() {
        load();
        return children;
    }
}
```

### 3. 循环检测

```java
public class SafeComposite implements DOMNode {
    private Set<DOMNode> ancestors = new HashSet<>();
    
    public void addChild(DOMNode child) throws CycleException {
        if (ancestors.contains(child)) {
            throw new CycleException("Adding child would create cycle");
        }
        
        // 获取child的所有祖先
        if (child instanceof SafeComposite) {
            SafeComposite sc = (SafeComposite) child;
            if (sc.ancestors.contains(this)) {
                throw new CycleException("Adding child would create cycle");
            }
        }
        
        children.add(child);
    }
}
```

---

## 集成模式

### Composite + Visitor

```java
public class CompositeVisitor {
    public interface NodeVisitor {
        void visit(DOMNode node);
    }
    
    public static void traverse(DOMNode root, NodeVisitor visitor) {
        visitor.visit(root);
        for (DOMNode child : root.getChildren()) {
            traverse(child, visitor);
        }
    }
    
    // 使用
    CompositeVisitor.traverse(html, node -> {
        System.out.println("Visiting: " + node);
    });
}
```

### Composite + Iterator

```java
public class CompositeIterator implements Iterator<DOMNode> {
    private Queue<DOMNode> queue = new LinkedList<>();
    
    public CompositeIterator(DOMNode root) {
        queue.offer(root);
    }
    
    @Override
    public boolean hasNext() {
        return !queue.isEmpty();
    }
    
    @Override
    public DOMNode next() {
        DOMNode node = queue.poll();
        node.getChildren().forEach(queue::offer);
        return node;
    }
}
```

---

## 单元测试增强

```java
@Test
public void testComplexHierarchy() {
    Element root = new Element("div");
    for (int i = 0; i < 100; i++) {
        Element child = new Element("p");
        child.addChild(new TextNode("Paragraph " + i));
        root.addChild(child);
    }
    
    assertEquals(100, root.getChildren().size());
}

@Test
public void testPerformanceTreeTraversal() {
    Element root = buildLargeTree(1000);
    
    long start = System.nanoTime();
    traverseAll(root);
    long end = System.nanoTime();
    
    System.out.println("Traversal time: " + (end - start) / 1_000_000 + "ms");
}

@Test(expected = CycleException.class)
public void testCycleDetection() throws CycleException {
    SafeComposite parent = new SafeComposite("parent");
    SafeComposite child = new SafeComposite("child");
    
    parent.addChild(child);
    child.addChild(parent); // 应该抛出异常
}

@Test
public void testNullSafety() {
    Element root = new Element("div");
    assertDoesNotThrow(() -> root.addChild(null));
    // 或者设置null检查
}
```

---

## 实际应用场景

### 文件浏览器

```java
void showFileBrowser(Directory root) {
    Stack<Directory> stack = new Stack<>();
    stack.push(root);
    
    while (!stack.isEmpty()) {
        Directory current = stack.pop();
        current.display(0);
        
        for (FileSystemComponent item : current.getChildren()) {
            if (item instanceof Directory) {
                stack.push((Directory) item);
            } else {
                item.display(0);
            }
        }
    }
}
```

### 树形表格

```java
public class TreeTableRow implements DOMNode {
    private String[] data;
    private List<TreeTableRow> children;
    
    public void renderToTable(StringBuilder html) {
        html.append("<tr>");
        for (String cell : data) {
            html.append("<td>").append(cell).append("</td>");
        }
        html.append("</tr>");
        
        children.forEach(child -> child.renderToTable(html));
    }
}
```

### 权限树

```java
public class PermissionNode {
    private String permission;
    private List<PermissionNode> children;
    
    public boolean hasPermission(String required) {
        if (permission.equals(required)) return true;
        return children.stream()
            .anyMatch(child -> child.hasPermission(required));
    }
}
```
