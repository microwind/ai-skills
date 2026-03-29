# C++编程 技术参考文档

## 概述

C++是一门多范式编程语言，支持过程式、面向对象和函数式编程。从C++11开始，语言引入了大量现代特性，使得代码更安全、更高效、更易维护。

## 核心特性演进

### C++标准对比

| 特性 | C++98 | C++11 | C++17 | C++20 |
|------|-------|-------|-------|-------|
| auto类型推导 | 固定类型 | ✓ | ✓ | ✓ |
| Lambda表达式 | ✗ | ✓ | ✓ | ✓ |
| 智能指针 | ✗ | ✓ | ✓ | ✓ |
| 范围for循环 | ✗ | ✓ | ✓ | ✓ |
| 可变模板 | ✗ | ✓ | ✓ | ✓ |
| 结构化绑定 | ✗ | ✗ | ✓ | ✓ |
| Concepts | ✗ | ✗ | ✗ | ✓ |
| Coroutines | ✗ | ✗ | ✗ | ✓ |

## 智能指针

### unique_ptr - 独占所有权
```cpp
std::unique_ptr<MyClass> ptr(new MyClass());
// 或C++14+
auto ptr = std::make_unique<MyClass>();

// 转移所有权
std::unique_ptr<MyClass> ptr2 = std::move(ptr);
// ptr现在是nullptr
```

### shared_ptr - 共享所有权
```cpp
std::shared_ptr<MyClass> ptr1 = std::make_shared<MyClass>();
std::shared_ptr<MyClass> ptr2 = ptr1;  // 引用计数+1

std::cout << ptr1.use_count() << std::endl;  // 2
// 当所有shared_ptr超出作用域时，对象被删除
```

### weak_ptr - 打破循环引用
```cpp
class Node {
public:
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> prev;  // 避免循环引用
};
```

## STL容器

### 序列容器

| 容器 | 特点 | 时间复杂度(随机访问/插入末尾) |
|------|------|---------------------------|
| std::vector | 动态数组，连续内存 | O(1) / O(1)* |
| std::deque | 双端队列 | O(1) / O(1) |
| std::list | 双向链表 | O(n) / O(1) |
| std::forward_list | 单向链表 | O(n) / O(n) |

### 关联容器

| 容器 | 结构 | 查找时间 | 有序性 |
|------|------|-------|------|
| std::map | 红黑树 | O(log n) | ✓ |
| std::unordered_map | 哈希表 | O(1)* | ✗ |
| std::set | 红黑树 | O(log n) | ✓ |
| std::unordered_set | 哈希表 | O(1)* | ✗ |

## 现代C++特性

### auto类型推导
```cpp
auto x = 5;              // int
auto y = 3.14;           // double
auto ptr = std::make_unique<int>();  // std::unique_ptr<int>
auto lambda = [](int x) { return x * 2; };  // lambda

// 在循环中
for (auto it = vec.begin(); it != vec.end(); ++it) {
    // it的类型自动推导
}
```

### 范围for循环
```cpp
std::vector<int> vec = {1, 2, 3, 4, 5};

// 替代传统for循环
for (int v : vec) {
    std::cout << v << " ";
}

// 引用版本（可修改容器元素）
for (int& v : vec) {
    v *= 2;
}

// 自定义容器需要提供begin()和end()
```

### Lambda表达式
```cpp
// 基本lambda
auto add = [](int a, int b) { return a + b; };
std::cout << add(3, 4) << std::endl;  // 7

// 捕获变量
int x = 10;
auto addX = [x](int a) { return a + x; };
std::cout << addX(5) << std::endl;  // 15

// 按引用捕获
int count = 0;
auto increment = [&count]() { count++; };

// 通用lambda（C++14）
auto multiply = [](auto a, auto b) { return a * b; };
```

### 结构化绑定（C++17）
```cpp
std::pair<int, std::string> p = {1, "hello"};
auto [id, name] = p;  // 自动解包

std::map<std::string, int> ages = {{"Alice", 30}, {"Bob", 25}};
for (auto [name, age] : ages) {
    std::cout << name << ": " << age << std::endl;
}
```

## 异常安全性

### RAII - Resource Acquisition Is Initialization
```cpp
class FileHandler {
private:
    FILE* file;
    
public:
    FileHandler(const std::string& filename) {
        file = fopen(filename.c_str(), "r");
        if (!file) throw std::runtime_error("Cannot open file");
    }
    
    ~FileHandler() {  // 析构函数确保资源释放
        if (file) fclose(file);
    }
    
    // 禁用复制
    FileHandler(const FileHandler&) = delete;
    FileHandler& operator=(const FileHandler&) = delete;
};
```

### noexcept规范
```cpp
// 声明函数不抛异常
void safe_function() noexcept {
    // 如果这里抛异常，程序将终止
}

// 条件性noexcept
template<typename T>
void process(T* ptr) noexcept(std::is_nothrow_copy_constructible_v<T>) {
    // 实现
}
```

## 模板编程

### 函数模板
```cpp
template<typename T>
T max_value(T a, T b) {
    return (a > b) ? a : b;
}

// 使用
int max_int = max_value(5, 10);
double max_double = max_value(3.14, 2.71);
```

### 类模板
```cpp
template<typename T>
class Stack {
private:
    std::vector<T> elements;
    
public:
    void push(const T& value) {
        elements.push_back(value);
    }
    
    T pop() {
        T value = elements.back();
        elements.pop_back();
        return value;
    }
};

// 使用
Stack<int> intStack;
Stack<std::string> stringStack;
```

### 可变模板（Variadic Templates）
```cpp
// 递归和参数包
template<typename T>
void print(T value) {
    std::cout << value << std::endl;
}

template<typename T, typename... Args>
void print(T first, Args... rest) {
    std::cout << first << " ";
    print(rest...);
}

// 调用
print(1, 2, 3, "hello");  // 输出: 1 2 3 hello
```

## 编译和链接

### 编译命令
```bash
# 简单编译
g++ -std=c++17 file.cpp -o program

# 优化
g++ -std=c++17 -O2 file.cpp -o program

# 调试
g++ -std=c++17 -g file.cpp -o program

# 警告
g++ -std=c++17 -Wall -Wextra file.cpp -o program

# 链接库
g++ -std=c++17 file.cpp -o program -lm -lpthread
```

### 静态库创建
```bash
# 编译为目标文件
g++ -c -fPIC util.cpp

# 创建静态库
ar rcs libutil.a util.o

# 使用
g++ main.cpp -o program -L. -lutil
```

## 性能优化建议

1. **使用const和constexpr**
   - 编译时计算（constexpr）
   - 避免不必要的复制

2. **使用引用而不是复制**
   ```cpp
   void process(const std::vector<int>& data);  // 避免复制
   ```

3. **移动语义**
   ```cpp
   std::vector<int> create_vector() {
       std::vector<int> v(1000000);
       return v;  // 使用移动而不是复制
   }
   ```

4. **选择合适的容器**
   - 频繁随机访问：std::vector
   - 频繁插入/删除：std::list或std::deque
   - 需要查找：std::unordered_map

5. **内联优化**
   ```cpp
   inline int add(int a, int b) {
       return a + b;
   }
   ```

## 编码规范清单

- [ ] 使用RAII管理资源
- [ ] 优先使用智能指针而不是裸指针
- [ ] 使用const和constexpr
- [ ] 避免全局变量
- [ ] 使用适当的名称空间
- [ ] 避免使用宏（优先使用const或constexpr）
- [ ] 正确处理异常
- [ ] 使用std::optional处理null情况
- [ ] 文档化公开接口
- [ ] 提供单元测试
