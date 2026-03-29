# C++ 静态分析与配置表单

## 基础编译配置

### C++ 标准选择 (C++ Standard)
- **目标规范**:
  - [ ] C++11 (基线标准，包含 move semantic，auto 和智能指针)
  - [ ] C++14 (主要修复与补充，如泛型 Lambda，make_unique)
  - [ ] C++17 (引入 std::optional，std::variant，结构化绑定等企业首选)
  - [ ] C++20 (引入 Concepts, 协程 Coroutines, Modules，极大改变用法)
  - [ ] C++23 (最新的标准预研)

### 编译器与架构 (Compiler & Arch)
- **编译前端前端**:
  - [ ] GCC (适合于大多数 Linux 环境，推荐 gcc-9 及以上)
  - [ ] Clang (LLVM 系，编译快，报错友好，推荐 clang-10 及以上)
  - [ ] MSVC (Windows 原生，VS2019/2022)
  - [ ] Intel ICC / ICPC (针对高度优化的数学/HPC计算)

- **目标架构**:
  - [ ] x86_64
  - [ ] ARM64 (AArch64)

## 静态分析与安全配置

### LLVM Clang-Tidy 扫描
- **核心扫描集**:
  - [ ] `modernize-*` () (更新古老代码到新标准特性，如基于范围的 for 循环)
  - [ ] `cppcoreguidelines-*` (C++ Core Guidelines 官方指引审查)
  - [ ] `bugprone-*` (易出错的代码模式检测)
  - [ ] `performance-*` (按值拷贝，没必要的多余对象生成)
  - [ ] `readability-*` (命名、标识、常量魔法数字)
  - [ ] `misc-throw-by-value-catch-by-reference` (异常必须按引用捕获)

### 内存管理策略 (RAII)
- [ ] 禁止使用显式的 `new` 和 `delete` 操作（必须全部使用 `std::make_unique` 和 `std::make_shared`）。
- [ ] 检测到类拥有指针成员或系统句柄时，强制应用 The Rule of Three/Five/Zero 定理。
- [ ] 对返回栈上局部变量指针或引用的现象做致命报错。
- [ ] 检查 `std::unique_ptr` 被使用后的转移 (Use-After-Move)。

### 异常处理策略 (Exception Handling)
- [ ] 所有不应该抛出异常的析构函数、移动构造和移动赋值运算符必须标记为 `noexcept`。
- [ ] 只允许使用引用捕获异常 `catch (const std::exception& e)`，严禁传值。
- [ ] 禁用异常环境开关 `-fno-exceptions` (用于部分特殊的低延迟或游戏引擎业务)。

## 性能与架构级评测

### 优化参数配置 (Optimization)
- **常见发布配置**:
  - [ ] `-O2` (稳定且安全的极致优化)
  - [ ] `-O3` (包含内联、多级循环展开)
  - [ ] `-flto` (链接时优化，减小程序尺寸并能跨编译单元内联)
  - [ ] `-march=native` (为当前 CPU 提供深度底层向量优化)

### 拷贝与移动诊断 (Copy & Move Semantics)
- [ ] 在仅作只读传递时，要求对象参数一律使用 `const auto&`。
- [ ] 当返回局部对象时，禁止显式使用 `return std::move(obj)` 以防御负优化（阻碍 RVO 返回值优化）。
- [ ] 当实现接口传参并接管所有权时，要求声明为传值并内部使用 `std::move` 或直接传入右值引用。

## 测试与质量保障配置

### 单元测试框架集成
- [ ] Google Test (GTest / GMock - 最广泛的行业选择)
- [ ] Catch2 (对模板代码极为友好的 Header-only 测试库)
- [ ] Boost.Test (Boost 生态)

### Sanitizer 动态检测集成
编译并执行高强度的内存审计：
- [ ] AddressSanitizer (ASan): `-fsanitize=address` (侦测 Use-After-Free 和越界行为)
- [ ] UndefinedBehaviorSanitizer (UBSan): `-fsanitize=undefined` (侦测整型溢出、类型误导等 C++ 禁忌)
- [ ] ThreadSanitizer (TSan): `-fsanitize=thread` (侦测由于没有加锁导致的变量数据竞争)
- [ ] MemorySanitizer (MSan): `-fsanitize=memory` (侦测未初始化的变量使用)

## 开发工具链集成

### CMake 与项目环境
- [ ] 在 CMake 中开启 `set(CMAKE_EXPORT_COMPILE_COMMANDS ON)` 供 IDE (ccls, clangd) 实现深度解析。
- [ ] `clang-format` 支持（规定项目级 `.clang-format` 统一缩进与括号换行机制）。
- [ ] 结合 `ccache` 以加速重复构建的时间。

### 包管理器整合
- [ ] vpkg (由 Microsoft 研发提供的现代化跨平台依赖安装方案)
- [ ] conan (去中心化且极其强大的工业化选择)
- [ ] git submodules (作为第三方源代码的备份引入)

## 指标度量报告

### 输出机制
- [ ] SonarQube C++ 插件结合输出
- [ ] gcov / lcov / llvm-cov 覆盖率报告支持
- [ ] HTML 结果高亮展示 (CI)
- [ ] 阻止 Merge Request / Pull Request 合并 (若出现 HIGH 或 CRITICAL 警告)
