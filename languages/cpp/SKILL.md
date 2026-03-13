---
name: C++编程
description: "当使用C++编程时，分析面向对象设计，优化模板编程，解决复杂问题。验证代码架构，设计高性能系统，和最佳实践。"
license: MIT
---

# C++编程技能

## 概述
C++是一门多范式的编程语言，支持过程式、面向对象、泛型和函数式编程。C++在C语言的基础上增加了类、模板、异常处理、STL等特性，使其成为构建复杂系统的高效工具。不当的C++编程会导致内存泄漏、性能问题、代码复杂。

**核心原则**: 好的C++代码应该类型安全、内存安全、性能优良、可维护性强。坏的C++代码会滥用指针、内存泄漏、模板膨胀。

## 何时使用

**始终:**
- 开发大型系统软件时
- 需要高性能计算时
- 构建游戏引擎时
- 开发嵌入式系统时
- 实现算法库时
- 需要底层控制时

**触发短语:**
- "C++智能指针怎么用？"
- "模板元编程应用"
- "C++性能优化技巧"
- "STL容器选择指南"
- "C++多线程编程"
- "C++最佳实践"

## C++编程技能功能

### 面向对象编程
- 类和对象设计
- 继承和多态
- 虚函数和纯虚函数
- 抽象类和接口
- 访问控制

### 模板编程
- 函数模板
- 类模板
- 模板特化
- SFINAE技术
- 模板元编程

### 内存管理
- 智能指针
- RAII原则
- 移动语义
- 完美转发
- 内存池技术

### STL容器和算法
- 序列容器
- 关联容器
- 无序容器
- 算法库
- 迭代器

## 常见问题

### 内存问题
- **问题**: 内存泄漏
- **原因**: 原始指针管理不当
- **解决**: 使用智能指针，遵循RAII原则

- **问题**: 悬空指针
- **原因**: 指针指向已销毁的对象
- **解决**: 使用weak_ptr，避免循环引用

### 性能问题
- **问题**: 过度拷贝
- **原因**: 不理解移动语义
- **解决**: 使用移动语义和完美转发

- **问题**: 模板实例化开销
- **原因**: 模板使用不当
- **解决**: 合理使用模板特化

### 并发问题
- **问题**: 数据竞争
- **原因**: 共享数据访问不当
- **解决**: 使用原子操作和互斥锁

- **问题**: 死锁
- **原因**: 锁的获取顺序不当
- **解决**: 使用std::lock，避免嵌套锁

## 代码示例

### 类和对象设计
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>

// 基础类定义
class Person {
private:
    std::string name;
    int age;
    
public:
    // 构造函数
    Person(const std::string& name, int age) 
        : name(name), age(age) {
        std::cout << "Person构造函数: " << name << std::endl;
    }
    
    // 拷贝构造函数
    Person(const Person& other) 
        : name(other.name), age(other.age) {
        std::cout << "Person拷贝构造函数: " << name << std::endl;
    }
    
    // 移动构造函数
    Person(Person&& other) noexcept
        : name(std::move(other.name)), age(other.age) {
        std::cout << "Person移动构造函数: " << name << std::endl;
    }
    
    // 析构函数
    virtual ~Person() {
        std::cout << "Person析构函数: " << name << std::endl;
    }
    
    // 虚函数
    virtual void display() const {
        std::cout << "姓名: " << name << ", 年龄: " << age << std::endl;
    }
    
    // Getter和Setter
    const std::string& getName() const { return name; }
    void setName(const std::string& newName) { name = newName; }
    
    int getAge() const { return age; }
    void setAge(int newAge) { age = newAge; }
};

// 继承和多态
class Student : public Person {
private:
    std::string studentId;
    double gpa;
    
public:
    Student(const std::string& name, int age, 
            const std::string& studentId, double gpa)
        : Person(name, age), studentId(studentId), gpa(gpa) {
        std::cout << "Student构造函数: " << name << std::endl;
    }
    
    // 重写虚函数
    void display() const override {
        Person::display();
        std::cout << "学号: " << studentId << ", GPA: " << gpa << std::endl;
    }
    
    // 新增方法
    void study() {
        std::cout << getName() << " 正在学习" << std::endl;
    }
    
    // Getter
    const std::string& getStudentId() const { return studentId; }
    double getGPA() const { return gpa; }
};

// 抽象类
class Shape {
public:
    // 纯虚函数
    virtual double area() const = 0;
    virtual double perimeter() const = 0;
    
    // 虚函数
    virtual void display() const {
        std::cout << "这是一个形状" << std::endl;
    }
    
    // 虚析构函数
    virtual ~Shape() = default;
};

// 具体类
class Circle : public Shape {
private:
    double radius;
    
public:
    explicit Circle(double r) : radius(r) {}
    
    double area() const override {
        return 3.14159 * radius * radius;
    }
    
    double perimeter() const override {
        return 2 * 3.14159 * radius;
    }
    
    void display() const override {
        Shape::display();
        std::cout << "圆形，半径: " << radius << std::endl;
    }
};

class Rectangle : public Shape {
private:
    double width, height;
    
public:
    Rectangle(double w, double h) : width(w), height(h) {}
    
    double area() const override {
        return width * height;
    }
    
    double perimeter() const override {
        return 2 * (width + height);
    }
    
    void display() const override {
        Shape::display();
        std::cout << "矩形，宽: " << width << ", 高: " << height << std::endl;
    }
};
```

### 智能指针和内存管理
```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <string>

// RAII原则示例
class FileHandler {
private:
    FILE* file;
    
public:
    explicit FileHandler(const char* filename, const char* mode) {
        file = fopen(filename, mode);
        if (!file) {
            throw std::runtime_error("无法打开文件");
        }
        std::cout << "文件已打开" << std::endl;
    }
    
    ~FileHandler() {
        if (file) {
            fclose(file);
            std::cout << "文件已关闭" << std::endl;
        }
    }
    
    // 禁止拷贝
    FileHandler(const FileHandler&) = delete;
    FileHandler& operator=(const FileHandler&) = delete;
    
    // 允许移动
    FileHandler(FileHandler&& other) noexcept : file(other.file) {
        other.file = nullptr;
    }
    
    FileHandler& operator=(FileHandler&& other) noexcept {
        if (this != &other) {
            if (file) fclose(file);
            file = other.file;
            other.file = nullptr;
        }
        return *this;
    }
    
    void write(const std::string& text) {
        if (file) {
            fprintf(file, "%s\n", text.c_str());
        }
    }
    
    std::string readLine() {
        if (!file) return "";
        
        char buffer[256];
        if (fgets(buffer, sizeof(buffer), file)) {
            return std::string(buffer);
        }
        return "";
    }
};

// 智能指针使用示例
void smart_pointer_examples() {
    // unique_ptr - 独占所有权
    std::unique_ptr<Person> person1 = std::make_unique<Person>("张三", 25);
    person1->display();
    
    // unique_ptr可以移动
    std::unique_ptr<Person> person2 = std::move(person1);
    if (!person1) {
        std::cout << "person1已为空" << std::endl;
    }
    person2->display();
    
    // shared_ptr - 共享所有权
    std::shared_ptr<Person> person3 = std::make_shared<Person>("李四", 30);
    std::shared_ptr<Person> person4 = person3; // 引用计数增加到2
    
    std::cout << "引用计数: " << person3.use_count() << std::endl;
    
    // weak_ptr - 弱引用，避免循环引用
    std::weak_ptr<Person> weak_person = person3;
    std::cout << "弱引用计数: " << weak_person.use_count() << std::endl;
    
    person3.reset(); // person3和person4的引用计数减少
    std::cout << "弱引用计数: " << weak_person.use_count() << std::endl;
    
    // 检查weak_ptr是否有效
    if (auto locked = weak_person.lock()) {
        locked->display();
    } else {
        std::cout << "对象已被销毁" << std::endl;
    }
}

// 自定义删除器
void custom_deleter() {
    // 数组删除器
    auto array_deleter = [](int* ptr) {
        std::cout << "自定义数组删除器" << std::endl;
        delete[] ptr;
    };
    
    std::unique_ptr<int[], decltype(array_deleter)> 
        int_array(new int[10], array_deleter);
    
    // 文件删除器
    auto file_deleter = [](FILE* file) {
        if (file) {
            std::cout << "自定义文件删除器" << std::endl;
            fclose(file);
        }
    };
    
    std::unique_ptr<FILE, decltype(file_deleter)> 
        file_ptr(fopen("test.txt", "w"), file_deleter);
    
    if (file_ptr) {
        fprintf(file_ptr.get(), "Hello, World!\n");
    }
}
```

### 模板编程
```cpp
#include <iostream>
#include <type_traits>
#include <vector>

// 函数模板
template<typename T>
T max_value(T a, T b) {
    return (a > b) ? a : b;
}

// 多参数模板
template<typename T, typename U>
auto add(T a, U b) -> decltype(a + b) {
    return a + b;
}

// 类模板
template<typename T>
class Stack {
private:
    std::vector<T> elements;
    
public:
    void push(const T& element) {
        elements.push_back(element);
    }
    
    void push(T&& element) {
        elements.push_back(std::move(element));
    }
    
    T pop() {
        if (elements.empty()) {
            throw std::runtime_error("栈为空");
        }
        
        T result = std::move(elements.back());
        elements.pop_back();
        return result;
    }
    
    bool empty() const {
        return elements.empty();
    }
    
    size_t size() const {
        return elements.size();
    }
};

// 模板特化
template<>
class Stack<bool> {
private:
    std::vector<unsigned char> buffer;
    
public:
    void push(bool value) {
        buffer.push_back(value);
    }
    
    bool pop() {
        if (buffer.empty()) {
            throw std::runtime_error("栈为空");
        }
        
        bool result = buffer.back();
        buffer.pop_back();
        return result;
    }
    
    bool empty() const {
        return buffer.empty();
    }
    
    size_t size() const {
        return buffer.size();
    }
};

// SFINAE示例
template<typename T>
typename std::enable_if<std::is_integral<T>::value, T>::type
double_value(T value) {
    return value * 2;
}

template<typename T>
typename std::enable_if<std::is_floating_point<T>::value, T>::type
double_value(T value) {
    return value * 2.0;
}

// 模板元编程
template<int N>
struct Factorial {
    static const int value = N * Factorial<N - 1>::value;
};

template<>
struct Factorial<0> {
    static const int value = 1;
};

// 编译时计算
template<typename T, size_t N>
constexpr size_t array_size(T (&)[N]) {
    return N;
}

// 可变参数模板
template<typename... Args>
void print_all(Args... args) {
    ((std::cout << args << " "), ...);
    std::cout << std::endl;
}

// 折叠表达式
template<typename... Args>
auto sum_all(Args... args) {
    return (args + ... + 0);
}

// 模板递归
template<typename T>
void print_tuple(const T& tuple) {
    print_tuple_impl(tuple, std::make_index_sequence<std::tuple_size_v<T>>{});
}

template<typename T, size_t... I>
void print_tuple_impl(const T& tuple, std::index_sequence<I...>) {
    ((std::cout << std::get<I>(tuple) << " "), ...);
    std::cout << std::endl;
}

// 概念约束（C++20）
template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

template<Numeric T>
T multiply(T a, T b) {
    return a * b;
}
```

### STL容器和算法
```cpp
#include <iostream>
#include <vector>
#include <list>
#include <deque>
#include <set>
#include <map>
#include <unordered_map>
#include <algorithm>
#include <numeric>
#include <iterator>

// 序列容器使用
void sequence_containers() {
    // vector
    std::vector<int> vec = {1, 2, 3, 4, 5};
    vec.push_back(6);
    vec.insert(vec.begin() + 2, 99);
    
    std::cout << "Vector: ";
    for (const auto& item : vec) {
        std::cout << item << " ";
    }
    std::cout << std::endl;
    
    // list
    std::list<std::string> lst = {"Hello", "World"};
    lst.push_front("C++");
    lst.push_back("Programming");
    
    std::cout << "List: ";
    for (const auto& item : lst) {
        std::cout << item << " ";
    }
    std::cout << std::endl;
    
    // deque
    std::deque<double> deq;
    deq.push_back(1.1);
    deq.push_back(2.2);
    deq.push_front(0.1);
    
    std::cout << "Deque: ";
    for (const auto& item : deq) {
        std::cout << item << " ";
    }
    std::cout << std::endl;
}

// 关联容器使用
void associative_containers() {
    // set
    std::set<int> s = {3, 1, 4, 1, 5, 9, 2, 6};
    s.insert(7);
    
    std::cout << "Set: ";
    for (const auto& item : s) {
        std::cout << item << " ";
    }
    std::cout << std::endl;
    
    // map
    std::map<std::string, int> age_map;
    age_map["Alice"] = 25;
    age_map["Bob"] = 30;
    age_map["Charlie"] = 35;
    
    std::cout << "Map: ";
    for (const auto& [name, age] : age_map) {
        std::cout << name << ":" << age << " ";
    }
    std::cout << std::endl;
    
    // unordered_map
    std::unordered_map<std::string, double> score_map;
    score_map["Math"] = 95.5;
    score_map["English"] = 87.0;
    score_map["Physics"] = 92.5;
    
    std::cout << "Unordered Map: ";
    for (const auto& [subject, score] : score_map) {
        std::cout << subject << ":" << score << " ";
    }
    std::cout << std::endl;
}

// 算法使用
void algorithm_examples() {
    std::vector<int> numbers = {5, 2, 8, 1, 9, 3, 7, 4, 6};
    
    // 排序
    std::sort(numbers.begin(), numbers.end());
    std::cout << "排序后: ";
    for (int n : numbers) std::cout << n << " ";
    std::cout << std::endl;
    
    // 查找
    auto it = std::find(numbers.begin(), numbers.end(), 5);
    if (it != numbers.end()) {
        std::cout << "找到5在位置: " << std::distance(numbers.begin(), it) << std::endl;
    }
    
    // 二分查找
    bool found = std::binary_search(numbers.begin(), numbers.end(), 7);
    std::cout << "二分查找7: " << (found ? "找到" : "未找到") << std::endl;
    
    // 计数
    int count = std::count(numbers.begin(), numbers.end(), 3);
    std::cout << "3的个数: " << count << std::endl;
    
    // 最大最小值
    auto [min_it, max_it] = std::minmax_element(numbers.begin(), numbers.end());
    std::cout << "最小值: " << *min_it << ", 最大值: " << *max_it << std::endl;
    
    // 累加
    int sum = std::accumulate(numbers.begin(), numbers.end(), 0);
    std::cout << "总和: " << sum << std::endl;
    
    // 转换
    std::vector<int> doubled;
    std::transform(numbers.begin(), numbers.end(), 
                   std::back_inserter(doubled), 
                   [](int x) { return x * 2; });
    
    std::cout << "翻倍后: ";
    for (int n : doubled) std::cout << n << " ";
    std::cout << std::endl;
    
    // 过滤
    std::vector<int> evens;
    std::copy_if(numbers.begin(), numbers.end(),
                std::back_inserter(evens),
                [](int x) { return x % 2 == 0; });
    
    std::cout << "偶数: ";
    for (int n : evens) std::cout << n << " ";
    std::cout << std::endl;
}

// 自定义比较函数
struct Person {
    std::string name;
    int age;
    
    Person(const std::string& n, int a) : name(n), age(a) {}
};

void custom_comparator() {
    std::vector<Person> people = {
        {"Alice", 25},
        {"Bob", 30},
        {"Charlie", 20},
        {"David", 35}
    };
    
    // 按年龄排序
    std::sort(people.begin(), people.end(), 
              [](const Person& a, const Person& b) {
                  return a.age < b.age;
              });
    
    std::cout << "按年龄排序: ";
    for (const auto& person : people) {
        std::cout << person.name << "(" << person.age << ") ";
    }
    std::cout << std::endl;
    
    // 按姓名排序
    std::sort(people.begin(), people.end(),
              [](const Person& a, const Person& b) {
                  return a.name < b.name;
              });
    
    std::cout << "按姓名排序: ";
    for (const auto& person : people) {
        std::cout << person.name << "(" << person.age << ") ";
    }
    std::cout << std::endl;
}
```

### 多线程编程
```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <future>
#include <chrono>

// 基础线程使用
void basic_threading() {
    auto worker = [](int id) {
        for (int i = 0; i < 5; ++i) {
            std::cout << "线程 " << id << ": 工作 " << i << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    };
    
    std::thread t1(worker, 1);
    std::thread t2(worker, 2);
    
    t1.join();
    t2.join();
}

// 互斥锁
class Counter {
private:
    int value;
    std::mutex mtx;
    
public:
    Counter() : value(0) {}
    
    void increment() {
        std::lock_guard<std::mutex> lock(mtx);
        ++value;
    }
    
    int get() const {
        std::lock_guard<std::mutex> lock(mtx);
        return value;
    }
};

void mutex_example() {
    Counter counter;
    
    auto worker = [&counter]() {
        for (int i = 0; i < 1000; ++i) {
            counter.increment();
        }
    };
    
    std::thread t1(worker);
    std::thread t2(worker);
    
    t1.join();
    t2.join();
    
    std::cout << "计数器值: " << counter.get() << std::endl;
}

// 条件变量
template<typename T>
class ThreadSafeQueue {
private:
    std::queue<T> queue;
    std::mutex mtx;
    std::condition_variable cv;
    
public:
    void push(const T& item) {
        {
            std::lock_guard<std::mutex> lock(mtx);
            queue.push(item);
        }
        cv.notify_one();
    }
    
    T pop() {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [this] { return !queue.empty(); });
        
        T item = queue.front();
        queue.pop();
        return item;
    }
    
    bool try_pop(T& item) {
        std::lock_guard<std::mutex> lock(mtx);
        if (queue.empty()) return false;
        
        item = queue.front();
        queue.pop();
        return true;
    }
};

void producer_consumer() {
    ThreadSafeQueue<int> queue;
    
    auto producer = [&queue]() {
        for (int i = 0; i < 10; ++i) {
            queue.push(i);
            std::cout << "生产者: 生产了 " << i << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    };
    
    auto consumer = [&queue]() {
        for (int i = 0; i < 10; ++i) {
            int item = queue.pop();
            std::cout << "消费者: 消费了 " << item << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    };
    
    std::thread t1(producer);
    std::thread t2(consumer);
    
    t1.join();
    t2.join();
}

// 原子操作
void atomic_operations() {
    std::atomic<int> counter(0);
    
    auto worker = [&counter]() {
        for (int i = 0; i < 1000; ++i) {
            counter.fetch_add(1, std::memory_order_relaxed);
        }
    };
    
    std::thread t1(worker);
    std::thread t2(worker);
    
    t1.join();
    t2.join();
    
    std::cout << "原子计数器值: " << counter.load() << std::endl;
}

// std::future和std::promise
int async_work(int x) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    return x * x;
}

void future_promise() {
    // std::async
    auto future = std::async(std::launch::async, async_work, 5);
    
    std::cout << "等待异步结果..." << std::endl;
    int result = future.get();
    std::cout << "异步结果: " << result << std::endl;
    
    // std::promise
    std::promise<std::string> promise;
    std::future<std::string> future_string = promise.get_future();
    
    auto worker = [](std::promise<std::string> prom) {
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        prom.set_value("Hello from future!");
    };
    
    std::thread t(worker, std::move(promise));
    
    std::cout << "等待字符串结果..." << std::endl;
    std::string str_result = future_string.get();
    std::cout << "字符串结果: " << str_result << std::endl;
    
    t.join();
}

// std::packaged_task
void packaged_task_example() {
    std::packaged_task<int(int)> task([](int x) {
        return x * x * x;
    });
    
    std::future<int> result = task.get_future();
    
    std::thread t(std::move(task), 5);
    
    std::cout << "等待packaged_task结果..." << std::endl;
    int cube = result.get();
    std::cout << "立方结果: " << cube << std::endl;
    
    t.join();
}
```

## 最佳实践

### 内存管理
1. **RAII原则**: 资源获取即初始化
2. **智能指针**: 优先使用unique_ptr、shared_ptr
3. **移动语义**: 避免不必要的拷贝
4. **完美转发**: 保持参数的值类别

### 模板编程
1. **类型安全**: 使用概念约束模板参数
2. **SFINAE**: 合理使用替换失败不是错误
3. **模板特化**: 为特定类型提供优化实现
4. **编译时计算**: 利用模板元编程优化性能

### 并发编程
1. **数据竞争**: 使用原子操作和同步机制
2. **死锁预防**: 避免嵌套锁，使用std::lock
3. **异步编程**: 使用future、promise、async
4. **线程安全**: 设计线程安全的类和函数

### 性能优化
1. **移动语义**: 减少不必要的拷贝操作
2. **容器选择**: 根据使用场景选择合适的容器
3. **算法优化**: 使用STL算法替代手动实现
4. **编译优化**: 启用适当的编译器优化选项

## 相关技能

- **c** - C语言编程
- **rust-systems** - 系统编程
- **typescript** - TypeScript编程
- **kotlin** - Kotlin编程
- **performance-optimization** - 性能优化
