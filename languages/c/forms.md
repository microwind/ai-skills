# C语言分析器与开发规范配置表单

## 基础编译配置

### 编译器设置
- **默认编译器选择**:
  - [ ] GCC (GNU Compiler Collection)
  - [ ] Clang (LLVM 系)
  - [ ] MSVC (Windows 平台)
  - [ ] ARM GCC / Keil (嵌入式环境)

- **C语言标准 (Standard)**:
  - [ ] C89/C90 (ANSI C - 极端遗留系统)
  - [ ] C99 (主流支持 - 允许可变长数组VLA与行内注释)
  - [ ] C11 (现代支持 - 引入原子操作 `<stdatomic.h>` 与线程)
  - [ ] C18 (修复部分C11缺陷，无新增语言特性)
  - [ ] C23 (最新标准)

- **目标平台架构 (Architecture)**:
  - [ ] x86_64 (桌面/服务器端)
  - [ ] ARMv7/ARMv8 (移动端/嵌入式)
  - [ ] WebAssembly (跨平台二进制)
  - [ ] 裸机 (Bare Metal - 无操作系统)

### 基础警告与代码质量
- **通用分析级别**:
  - [ ] 启用基础分析模块
  - [ ] 启用深度性能剖析
  - [ ] 启用系统安全检查
  - [ ] 启用供应链依赖扫描

- **警告覆盖范围**:
  - [ ] `-Wall` (开启所有主要警告)
  - [ ] `-Wextra` (开启额外的敏感警告)
  - [ ] `-Wpedantic` (强制符合ISO C标准)
  - [ ] `-Werror` (将所有警告视为编译错误)
  - [ ] `-Wshadow` (局部变量遮蔽全局变量警告)

## 静态分析与安全配置

### 漏洞扫描 (Clang-Tidy / Cppcheck)
- **安全漏洞预防**:
  - [ ] 禁用危险函数输入 (gets, strcpy, sprintf)
  - [ ] 强制检查数组越界读写 (Out-of-bounds)
  - [ ] 检测带符号整数溢出 (Signed Integer Overflow)
  - [ ] 检查格式化字符串漏洞 (Format String Attack)

- **健壮性分析**:
  - [ ] 变量必须显式初始化 (Uninitialized Variables)
  - [ ] 未使用的变量、函数或参数警告
  - [ ] 死代码去除 (Dead Code elimination)
  - [ ] 头文件包含循环 (Circular includes)

### 内存管理稽核
- **内存泄漏检查**:
  - [ ] 验证 `malloc`, `calloc`, `realloc` 与 `free` 的数量匹配
  - [ ] 定位隐式退出路径 (`return`/`continue`) 中的未释放内存
  - [ ] 防止悬空指针写入 (Dangling pointer write)
  - [ ] 捕获双重释放错误 (Double Free)

- **指针安全**:
  - [ ] 强制禁止隐式将整数转换为指针
  - [ ] 限制使用晦涩的指针多重解引用 (`int ****p`)
  - [ ] 函数返回指向局部栈变量的指针时产生严重警告

## 性能与编译期优化配置

### 优化等级 (Optimization Levels)
- **调试阶段 (Debug)**:
  - [ ] `-O0`: 完全不优化，保证断点与源码行严格对应
  - [ ] `-Og`: 专为调试开启的安全优化级别，提升调试速度
- **发布阶段 (Release)**:
  - [ ] `-O1`: 适度优化
  - [ ] `-O2`: 主流安全优化级别 (生产首选)
  - [ ] `-O3`: 激进优化 (包含循环展开、向量化，可能使二进制膨胀)
  - [ ] `-Os`: 优化二进制文件体积 (常用于嵌入式)
  - [ ] `-flto`: 启用链接时优化 (Link-Time Optimization)

### 硬件特性对齐
- **指定指令集**:
  - [ ] `-march=native` (针对当前编译母机深度优化)
  - [ ] 启用 AVX / SSE 向量指令集支持
- **内存与缓存**:
  - [ ] 结构体字段按大小排序优化 (Data locality & padding)
  - [ ] __builtin_expect (分支预测 unlikely) 提示分析

## 测试与动态调试配置

### Sanitizers (运行时错误探测)
配合 GCC/Clang 使用以下标志，运行极高代价的测试捕捉错误：
- [ ] **AddressSanitizer (ASan)** (`-fsanitize=address`): 侦测内存越界、Use-After-Free 等
- [ ] **MemorySanitizer (MSan)** (`-fsanitize=memory`): 侦测未初始化内存读取
- [ ] **ThreadSanitizer (TSan)** (`-fsanitize=thread`): 侦测多线程竞态条件和死锁
- [ ] **UndefinedBehaviorSanitizer (UBSan)** (`-fsanitize=undefined`): 侦测整数溢出、空指针解引用

### 调试工具集成
- **调试器**:
  - [ ] GDB (通用场景)
  - [ ] LLDB (优先配合 Clang/macOS)
- **复杂内存排查**:
  - [ ] Valgrind (Memcheck, Callgrind 模块支持)
  - [ ] Heaptrack / Massif (对堆内存分配进行性能刨析)

### 并发与同步检查
- **POSIX Threads (Pthreads)**:
  - [ ] `pthread_mutex_lock` 和 `unlock` 匹配性静态推断
  - [ ] `pthread_join` 防止脱离的僵尸线程
  - [ ] 条件变量的虚假唤醒 (Spurious wakeup) 检查机制 (`while` 循环替代 `if`)

## 代码规范与风格配置

### 命名与格式
- **排版工具**:
  - [ ] 引入 `clang-format` 并在提交前打入钩子 (Pre-commit Hook)
  - [ ] 使用 GNU 风格 （缩进两空格）
  - [ ] 使用 Linux Kernel 风格 （缩进8个 Tab 制表符）
  - [ ] 使用 LLVM / Google 风格

- **命名约束**:
  - [ ] 全局变量前缀 `g_` 或静态化限制作用域
  - [ ] 宏控全大写 (`#define CONST_VALUE`)
  - [ ] 类型定义 `typedef` 以 `_t` 结尾 (`uint32_t`)

## 项目结构与构建系统配置

### 构建工具
- **现代化构建**:
  - [ ] 使用 CMake (推荐配置 `CMakeLists.txt`)
  - [ ] 使用 Meson / Ninja (追求极限构建速度)
  - [ ] 传统 Makefile (定制性极强)

### CI/CD 持续集成集成
- **自动化流**:
  - [ ] 每次 Pull Request 执行 GCC 及 Clang 双重编译检查
  - [ ] GitHub Actions 绑定 Clang-Tidy 给出的 Annotations 警告
  - [ ] 强制生成覆盖率报告 (`gcov` / `lcov`)
  - [ ] SonarQube C/C++ 核心规则静态扫描关联

## 扩展检查项（针对裸机/嵌入式）

### 硬件强相关规范
- [ ] 访问外设寄存器的指针必须声明为 `volatile` 防止内核优化移除读写
- [ ] 强限制中断服务例程 (ISR) 中不能调用 `malloc`/`printf` 等非重入/阻塞函数
- [ ] 堆栈深度静态预估计算 (防止小型单片机 Stack Overflow)
- [ ] 使用特定大小类型的整型 `#include <stdint.h>` (`int` 的大小依环境而异，被禁止)

## 分析器输出配置

### 报告输出格式
- [ ] 控制台色彩输出 (Stdout/Stderr)
- [ ] HTML 美化报告展示
- [ ] JSON / XML (机器友好，便于 CI 解析)
- [ ] JSON Compilation Database (`compile_commands.json`) 支持

### 报告周期
- [ ] 实时按保存报告 (IDE 插件驱动)
- [ ] 本地预提交报告 (Git Pre-Commit Hook)
- [ ] 每日/每周构建综合性能度量 (Nightly Build)
