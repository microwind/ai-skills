---
name: C++编程
description: "当进行C++开发、性能优化、内存管理或现代C++应用时，分析代码质量、设计模式和最佳实践。"
license: MIT
---

# C++编程技能

## 概述
C++是高度灵活且强大的语言，支持多种编程范式。现代C++（C++11及以后）引入了大量改进的特性，使得代码更安全、更高效。不当的指针使用、资源管理和设计会导致内存泄漏、性能问题和代码难以维护。

**核心原则**: 好的C++代码应该高效安全、资源管理清晰、易于维护、充分利用现代特性。坏的C++代码会内存泄漏、性能低下、代码混乱。

## 何时使用

**始终:**
- C++项目代码审查
- 性能关键代码优化
- 内存管理和资源生命周期分析
- 现代C++特性应用
- 设计模式实现
- 并发编程

**触发短语:**
- "C++性能优化"
- "智能指针使用规范"
- "RAII资源管理"
- "C++17/20特性应用"
- "STL容器最佳实践"
- "C++多线程编程"

## C++编程技能功能

### 内存管理
- 智能指针（unique_ptr, shared_ptr）使用
- RAII原则应用
- 内存泄漏检测
- 析构函数管理
- 复制和移动语义

### 现代C++特性
- auto类型推导
- 范围for循环
- Lambda表达式
- 可变模板
- constexpr编程

### STL和标准库
- 容器选择和使用
- 算法应用
- 迭代器模式
- 异常处理
- 字符串和流处理

### 并发编程
- std::thread使用
- 互斥锁和同步
- 原子操作
- 条件变量
- 线程安全的设计

### 面向对象设计
- 类设计和继承
- 虚函数和多态
- 运算符重载
- 友元类和函数
- 模板编程

## 常见问题

### 内存和资源问题
- **问题**: 智能指针循环引用
- **原因**: shared_ptr之间互相引用
- **解决**: 使用weak_ptr打破循环引用或重新设计所有权

- **问题**: 混合使用裸指针和智能指针
- **原因**: 新旧代码混合
- **解决**: 逐步迁移到智能指针，避免混合使用

- **问题**: 异常安全问题
- **原因**: 不遵循RAII原则
- **解决**: 确保所有资源在构造函数初始化，析构函数清理

### 性能问题
- **问题**: 过度复制和不必要的内存分配
- **原因**: 没有使用移动语义和引用
- **解决**: 使用std::move、右值引用和移动构造

- **问题**: 虚函数开销
- **原因**: 过度使用虚函数或热点代码路径
- **解决**: 性能分析，避免关键路径使用虚函数

### 并发问题
- **问题**: 数据竞争
- **原因**: 多线程访问共享数据没有同步
- **解决**: 使用mutex、atomic或其他同步机制

## 代码示例

### 现代C++内存管理
```cpp
#include <memory>
#include <vector>

// 使用智能指针而不是裸指针
class DataManager {
private:
    std::unique_ptr<int[]> data;
    std::vector<std::shared_ptr<std::string>> strings;
    
public:
    DataManager(size_t size) 
        : data(std::make_unique<int[]>(size)) {}
    
    // 析构函数自动释放资源（虽然这里不需要显式写出来）
    ~DataManager() = default;
    
    // 添加字符串
    void add_string(const std::string& str) {
        strings.push_back(std::make_shared<std::string>(str));
    }
    
    // 获取字符串数量
    size_t string_count() const {
        return strings.size();
    }
};

// 使用示例
int main() {
    auto manager = std::make_unique<DataManager>(100);
    manager->add_string("Hello");
    manager->add_string("World");
    // 自动清理，无需手动delete
    return 0;
}
```

### Lambda表达式和算法
```cpp
#include <algorithm>
#include <vector>
#include <iostream>

void lambda_and_algorithm_demo() {
    std::vector<int> nums = {3, 1, 4, 1, 5, 9, 2, 6};
    
    // 排序
    std::sort(nums.begin(), nums.end());
    
    // 使用lambda过滤
    auto even_count = std::count_if(
        nums.begin(), 
        nums.end(),
        [](int n) { return n % 2 == 0; }
    );
    std::cout << "Even numbers: " << even_count << std::endl;
    
    // 使用lambda转换
    std::vector<int> squared;
    std::transform(
        nums.begin(), 
        nums.end(),
        std::back_inserter(squared),
        [](int n) { return n * n; }
    );
    
    // 范围for循环（C++11）
    for (int num : squared) {
        std::cout << num << " ";
    }
    std::cout << std::endl;
}
```

### RAII原则应用
```cpp
#include <fstream>
#include <iostream>

// RAII - Resource Acquisition Is Initialization
class FileHandler {
private:
    std::ifstream file;
    
public:
    // 构造函数获取资源
    explicit FileHandler(const std::string& filename) 
        : file(filename) {
        if (!file.is_open()) {
            throw std::runtime_error("Cannot open file: " + filename);
        }
    }
    
    // 析构函数释放资源
    ~FileHandler() {
        if (file.is_open()) {
            file.close();
        }
    }
    
    // 删除复制
    FileHandler(const FileHandler&) = delete;
    FileHandler& operator=(const FileHandler&) = delete;
    
    // 支持移动
    FileHandler(FileHandler&& other) noexcept 
        : file(std::move(other.file)) {}
    
    FileHandler& operator=(FileHandler&& other) noexcept {
        if (this != &other) {
            file = std::move(other.file);
        }
        return *this;
    }
    
    // 读取内容
    std::string read_all() {
        return std::string((std::istreambuf_iterator<char>(file)),
                          std::istreambuf_iterator<char>());
    }
};

// 使用示例
int main() {
    try {
        FileHandler handler("data.txt");
        std::string content = handler.read_all();
        std::cout << content << std::endl;
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
    }
    // 文件自动关闭
    return 0;
}
```

### 可变模板和完美转发
```cpp
#include <iostream>
#include <utility>

// 通用的日志函数
template<typename... Args>
void log(const char* format, Args&&... args) {
    // 这是一个演示，实际应该使用更复杂的格式化
    std::cout << format << std::endl;
}

// 使用示例
int main() {
    log("Simple message");
    
    int value = 42;
    log("Value: ", value);
    
    return 0;
}
```

### 多线程编程
```cpp
#include <thread>
#include <mutex>
#include <atomic>
#include <vector>

class ThreadSafeCounter {
private:
    mutable std::mutex mtx;
    int count = 0;
    
public:
    void increment() {
        std::lock_guard<std::mutex> lock(mtx);
        count++;
    }
    
    int get_value() const {
        std::lock_guard<std::mutex> lock(mtx);
        return count;
    }
};

// 使用示例
int main() {
    ThreadSafeCounter counter;
    
    auto worker = [&counter]() {
        for (int i = 0; i < 1000; ++i) {
            counter.increment();
        }
    };
    
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back(worker);
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    std::cout << "Final count: " << counter.get_value() << std::endl;
    return 0;
}
```
