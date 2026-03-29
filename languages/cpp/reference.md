# C++ 现代开发代码参考与安全规范

## 概述

从 C++11 引爆"现代 C++"开始，开发者拥有了对极大复杂性的驯服利器。此文档集合了企业级核心模块如何防范内存泄露、无拷贝传递、移动语义、并发安全等场景的最佳实践和经典模式参考。

## 智能指针与资源获取 (RAII)

如果您的项目中能搜到 `new` / `delete`，那它就是古董或充满漏洞的。

### `std::unique_ptr`：永远的首选
它是唯一拥有目标资源的所有者。离开作用域立即销毁，不带任何引用计数，**性能开销为零**，等同于裸指针。

```cpp
#include <iostream>
#include <memory>
#include <string>

class HeavyResource {
public:
    HeavyResource(std::string name) : id(name) { std::cout << id << " Acquired\n"; }
    ~HeavyResource() { std::cout << id << " Destroyed\n"; }
    void work() { std::cout << id << " working...\n"; }
private:
    std::string id;
};

// 正确示例：返回独占智能指针
std::unique_ptr<HeavyResource> makeResource(const std::string& name) {
    // 永远使用 make_unique。它能在一个异常安全的环境分配内存。
    return std::make_unique<HeavyResource>(name); 
}

void uniquePtrDemo() {
    auto res = makeResource("Worker1");
    res->work();
    
    // 如果要转移所有权，必须显式 move
    std::unique_ptr<HeavyResource> another = std::move(res);
    
    // 此时 res 已经是 nullptr，再次调用会导致段错误
    if (res == nullptr) {
        std::cout << "Ownership transferred safely.\n";
    }
} // 离开大括号，another 自动销毁 Worker1
```

### `std::shared_ptr` / `std::weak_ptr`：有限度的共享
带有引用计数的分配器。必须谨慎使用，以防造成循环引用（Cyclic Dependency），以及过度分配带来的原子操作（Atomic overhead）。

```cpp
#include <iostream>
#include <memory>

class TreeNode {
public:
    int value;
    std::shared_ptr<TreeNode> left;
    std::shared_ptr<TreeNode> right;
    
    // 关键！如果要指向上级，必须用 weak_ptr，否则会导致内存泄漏！
    std::weak_ptr<TreeNode> parent; 

    TreeNode(int v) : value(v) { std::cout << "Node " << value << "\n"; }
    ~TreeNode() { std::cout << "~Node " << value << "\n"; }
};

void createTree() {
    // 强制使用 make_shared：它将控制块和对象本体一起分配，只消耗一次 malloc
    auto root = std::make_shared<TreeNode>(1);
    auto child = std::make_shared<TreeNode>(2);
    
    root->left = child;
    child->parent = root; // weak_ptr 不增加引用计数
    
    // 如果想要通过 weak_ptr 访问，必须通过 lock() 提升为 shared_ptr 保证安全
    if (auto p = child->parent.lock()) {
        std::cout << "Child's parent is: " << p->value << "\n";
    }
} // 离开作用域，完美析构所有节点
```

## 拷贝、移动与传参策略 (Move Semantics & Passing)

错误的值传递是 C++ 新手写出慢代码的罪魁祸首。

### 传参法则表
1. **基础类型 (int, float, char*)**: 传值 (Pass-by-value)。
2. **需要读大型对象 (std::string, std::vector) 但不接管所有权**: 传 `const Type&`（常量引用）。
3. **需要接管大型对象所有权并且存储它**: 传值，然后内部 `std::move`。
4. **内部局部变量作为返回值输出**: 直接传值，**千万不要在 return 前加 `std::move`**（它会阻止编译器进行 RVO 返回值优化，起到反作用）。

```cpp
#include <string>
#include <vector>
#include <iostream>

class Record {
    std::string name;
    std::vector<int> data;
public:
    // 情况 3：接收所有权
    // sink argument（接收者参数），通过传值进来，然后直接 move 进去，这是最优解。
    Record(std::string str_sink, std::vector<int> vec_sink) 
        : name(std::move(str_sink)), data(std::move(vec_sink)) 
    {}
    
    // 情况 2：只读访问
    void printName(const std::string& prefix) const {
        std::cout << prefix << ": " << name << "\n";
    }
    
    // 情况 4：返回值
    std::string generateReport() const {
        std::string report = "Report for " + name;
        // 正确：直接 return 局部变量
        // 错误：return std::move(report);
        return report;
    }
};
```

## 现代并发 (Threading and Synchronization)

C++11 提供了属于语言原生的跨平台并发支持，而无需调用 pthread 或者 Windows API。

### 使用 `std::scoped_lock` 解决防呆上锁与死锁
如果函数有多个 return 出口，或有抛出异常的风险，手动 `lock()/unlock()` 必将泄露互斥锁。

```cpp
#include <iostream>
#include <thread>
#include <mutex>
#include <vector>

std::mutex g_mutex;
int shared_resource = 0;

void incrementAction() {
    for (int i = 0; i < 10000; ++i) {
        // C++17 提供的 scoped_lock 可接受一个或多个锁，不仅 RAII 保证了安全，更能用无死锁算法一次上多个锁
        std::scoped_lock lock(g_mutex); 
        shared_resource++;

        // 如果中间抛异常或是 return，lock 将自动析构并正确解锁。
        if (i == 5000) {
            // throw std::runtime_error("Oops"); // 安全
        }
    }
}

void runConcurrency() {
    std::vector<std::thread> threadPool;
    for (int i= 0; i < 5; ++i) {
        threadPool.emplace_back(incrementAction); // 现代做法，原地构造线程
    }
    
    for (auto& t : threadPool) {
        t.join(); // 必须 join，否则 std::thread 析构时会产生 std::terminate 致命崩溃
    }
    std::cout << "Resource value (Expect 50000): " << shared_resource << "\n";
}
```

### 原子操作代替加锁 (Atomic Types)
对于只执行简单操作的数据，使用原子类型代替粗粒度的 `mutex` 能极大提升并发性能。

```cpp
#include <atomic>

std::atomic<int> simple_counter{0};

void fastIncrement() {
    // 底层直接翻译为 lock xadd （x86 架构无锁原语）
    for(int i = 0; i < 10000; ++i) {
        simple_counter.fetch_add(1, std::memory_order_relaxed);
    }
}
```

## Lambda 与 STL 算法体系 (Algorithms First)

绝不手写繁琐的 `for` 循环。STL 的语义不仅能够直接告知读者代码的真正意图，更能利用编译器的 SIMD 进行无缝优化。

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

void modernAlgorithms() {
    std::vector<int> nums = {4, 7, 2, 8, 5, 9};

    // 1. 删除偶数 (Erase-Remove Idiom, C++20 前写法)
    nums.erase(
        std::remove_if(nums.begin(), nums.end(), [](int n) { return n % 2 == 0; }), 
        nums.end()
    );

    // C++20 可以更极简：
    // std::erase_if(nums, [](int n) { return n % 2 == 0; });

    // 2. 验证全是奇数
    bool all_odds = std::all_of(nums.begin(), nums.end(), [](int n) {
        return n % 2 != 0;
    });

    // 3. 排序 (Lambda 提供降序)
    std::sort(nums.begin(), nums.end(), [](int a, int b) {
        return a > b;
    });

    // 4. 只寻找某一个特征对象
    auto it = std::find_if(nums.begin(), nums.end(), [](int n) {
        return n == 7;
    });
    
    if (it != nums.end()) {
        std::cout << "Found 7!\n";
    }
}
```

## 设计模式：CRTP (静态多态)

相比于传统的虚函数 (Virtual Function) 产生运行时的指针间接跳转和缓存失效（vtable lookup penalty），CRTP (Curiously Recurring Template Pattern) 利用模板特化在编译期完成多态。极大运用在对游戏引擎、高频交易等极限性能的模块。

```cpp
#include <iostream>

// 它的类型签名接收派生类自己作为模板参数
template <typename Derived>
class BaseEntity {
public:
    void execute() {
        // 在这，我们强制向下转为具体的子类，并且在编译期间解析完成！
        static_cast<Derived*>(this)->internalBehavior();
    }
    
    // 默认行为，如果子类不重写。
    void internalBehavior() {
        std::cout << "Default Base Behavior\n";
    }
};

class FastPlayer : public BaseEntity<FastPlayer> {
public:
    // 无需 virtual 声明，也没有类额外多出来的 8 字节虚指针！
    void internalBehavior() {
        std::cout << "Player moves fast without virtual v-table overhead!\n";
    }
};

template <typename T>
void triggerEntity(BaseEntity<T>& obj) {
    obj.execute();
}

int main() {
    FastPlayer p;
    triggerEntity(p); // 将完美展开并在编译时调用 FastPlayer::internalBehavior
    return 0;
}
```

## 企业级 CMake 构建文件参考

这是一个极为标准的针对现代 C++ 的 `CMakeLists.txt`。

```cmake
cmake_minimum_required(VERSION 3.20)

project(EnterpriseCppProject
    VERSION 1.0.0
    DESCRIPTION "A secure and high performance modern C++ benchmark"
    LANGUAGES CXX
)

# 确保以 C++17 编译，且移除 GCC 私有扩展
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)
set(CMAKE_CXX_EXTENSIONS FALSE)

# 无论何处用到这个模块，自动包含此路径下的 .h
add_library(CoreModule src/engine.cpp)
target_include_directories(CoreModule PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

# 严格的警告机制
target_compile_options(CoreModule PRIVATE
    $<$<CXX_COMPILER_ID:Clang,AppleClang,GNU>:
        -Wall -Wextra -Wpedantic -Wshadow -Wnon-virtual-dtor 
        -Wold-style-cast -Wcast-align -Woverloaded-virtual
    >
    $<$<CXX_COMPILER_ID:MSVC>:
        /W4
    >
)

# 构建可执行文件
add_executable(App main.cpp)
target_link_libraries(App PRIVATE CoreModule)

# 并发支持 (跨平台方案)
find_package(Threads REQUIRED)
target_link_libraries(App PRIVATE Threads::Threads)
```
