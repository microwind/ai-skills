# C语言编程 技术参考文档

## 概述

C语言是系统编程的基石，被广泛应用于操作系统、编译器、数据库、网络工具等领域。这份文档提供了C语言编程的核心参考资料。

## 核心特性

### 基本类型和操作符
| 类型 | 大小(典型) | 范围 |
|------|----------|------|
| char | 1字节 | -128 至 127 |
| short | 2字节 | -32768 至 32767 |
| int | 4字节 | -2147483648 至 2147483647 |
| long | 4-8字节 | 取决于平台 |
| float | 4字节 | IEEE 754单精度 |
| double | 8字节 | IEEE 754双精度 |
| pointer | 4-8字节 | 取决于平台 |

### 内存管理函数

| 函数 | 说明 | 注意事项 |
|------|------|---------|
| malloc(size) | 分配内存块 | 必须检查返回值；必须free释放 |
| calloc(num, size) | 分配并初始化为0 | 比malloc慢，但内存已清零 |
| realloc(ptr, size) | 重新分配内存 | 可能移动内存地址 |
| free(ptr) | 释放内存 | 释放后应设置为NULL |

### 字符串处理函数（不安全的）

| 函数 | 问题 | 替代方案 |
|------|------|---------|
| strcpy(dest, src) | 没有边界检查 | strncpy(dest, src, n) |
| strcat(dest, src) | 没有边界检查 | strncat(dest, src, n) |
| sprintf(buff, fmt, ...) | 缓冲区溢出 | snprintf(buff, size, fmt, ...) |
| scanf("%s", buff) | 缓冲区溢出 | scanf("%99s", buff) 指定宽度 |
| gets(buff) | 完全不安全 | fgets(buff, size, stdin) |

## 编程模式

### RAII变通实现

虽然C没有原生RAII支持，但可以手动实现类似的模式：

```c
// 资源分配函数
FILE* open_file(const char* filename) {
    FILE* fp = fopen(filename, "r");
    if (!fp) {
        perror("fopen failed");
    }
    return fp;
}

// 资源释放函数
void close_file(FILE** fp) {
    if (fp && *fp) {
        fclose(*fp);
        *fp = NULL;
    }
}

// 使用示例
int main() {
    FILE* fp = open_file("data.txt");
    if (!fp) return 1;
    
    // 使用文件
    char buffer[256];
    if (fgets(buffer, sizeof(buffer), fp)) {
        printf("%s", buffer);
    }
    
    close_file(&fp);  // 确保释放
    return 0;
}
```

## 常见陷阱和最佳实践

### 内存相关

1. **缓冲区溢出**
   - 问题：写入超过分配的内存
   - 防护：检查大小，使用有界函数

2. **内存泄漏**
   - 问题：malloc后忘记free
   - 防护：配对检查，使用工具检测（Valgrind）

3. **野指针**
   - 问题：使用已释放的指针
   - 防护：释放后设置为NULL，检查null指针

### 指针技巧

```c
// 指针vs数组：不同的sizeof结果
int arr[10];
int* ptr = arr;

printf("%zu\n", sizeof(arr));  // 40 (10 * 4)
printf("%zu\n", sizeof(ptr));  // 8 (指针大小)

// 函数参数中数组退化为指针
void print_size(int arr[10]) {
    // 在这里sizeof(arr)返回指针大小，不是数组大小！
    printf("%zu\n", sizeof(arr));  // 8
}

// 二级指针用法
void increment_by_pointer(int* ptr) {
    (*ptr)++;
}

void increment_by_double_pointer(int** ptr) {
    (**ptr)++;
}
```

### 并发编程

```c
// POSIX线程基本操作
#include <pthread.h>

void* thread_function(void* arg) {
    int* value = (int*)arg;
    printf("Thread value: %d\n", *value);
    return NULL;
}

int main() {
    pthread_t thread_id;
    int value = 42;
    
    // 创建线程
    if (pthread_create(&thread_id, NULL, thread_function, &value) != 0) {
        perror("pthread_create");
        return 1;
    }
    
    // 等待线程完成
    if (pthread_join(thread_id, NULL) != 0) {
        perror("pthread_join");
        return 1;
    }
    
    return 0;
}
```

## 标准库快速参考

### stdio.h - 输入输出
```c
FILE* fopen(const char* filename, const char* mode);
int fclose(FILE* fp);
int fprintf(FILE* fp, const char* format, ...);
char* fgets(char* s, int size, FILE* fp);
int fputs(const char* s, FILE* fp);
```

### stdlib.h - 通用工具
```c
void* malloc(size_t size);
void* calloc(size_t nmemb, size_t size);
void free(void* ptr);
int rand(void);
void exit(int status);
```

### string.h - 字符串处理
```c
char* strcpy(char* dest, const char* src);        // 不安全
char* strncpy(char* dest, const char* src, size_t n);
int strcmp(const char* s1, const char* s2);
int strncmp(const char* s1, const char* s2, size_t n);
size_t strlen(const char* s);
char* strstr(const char* haystack, const char* needle);
```

### math.h - 数学函数
```c
double sqrt(double x);
double pow(double x, double y);
double sin(double x);
double cos(double x);
double tan(double x);
double fabs(double x);
```

### assert.h - 断言
```c
assert(condition);  // 断言条件为真，否则程序中止
```

## 编译和调试

### GCC编译常用选项
```bash
# 基本编译
gcc -c file.c              # 编译为目标文件
gcc file.c -o program      # 编译为可执行文件

# 优化选项
gcc -O0 file.c            # 无优化（调试）
gcc -O2 file.c            # 中级优化
gcc -O3 file.c            # 高级优化

# 调试信息
gcc -g file.c             # 包含调试符号

# 警告级别
gcc -Wall file.c          # 启用所有常见警告
gcc -Wextra file.c        # 启用额外警告
gcc -pedantic file.c      # 严格遵循C标准

# 预处理
gcc -E file.c             # 仅预处理
gcc -DDEBUG file.c        # 定义宏
gcc -Iinclude/ file.c     # 指定include路径
```

### GDB调试

```bash
# 启动调试
gdb ./program
gdb --args ./program arg1 arg2

# GDB命令
(gdb) break main           # 设置断点
(gdb) run                  # 运行程序
(gdb) step                 # 单步执行
(gdb) next                 # 跳过函数
(gdb) continue             # 继续执行
(gdb) print variable       # 打印变量
(gdb) backtrace            # 显示调用栈
(gdb) quit                 # 退出
```

### Valgrind内存检测

```bash
# 检测内存泄漏
valgrind --leak-check=full ./program

# 生成报告
valgrind --leak-check=full --log-file=report.txt ./program

# 详细输出
valgrind --show-leak-kinds=all ./program
```

## 性能优化建议

1. **使用合适的数据结构**
   - 数组：快速随机访问
   - 链表：频繁插入删除
   - 哈希表：快速查找

2. **避免过度分配**
   ```c
   // 不好：多次小分配
   char* str = malloc(10);
   str = realloc(str, 20);
   str = realloc(str, 30);
   
   // 更好：预分配足够空间
   char* str = malloc(100);
   ```

3. **函数内联**
   - 频繁调用的小函数使用inline
   - 但现代编译器通常自动优化

4. **缓冲I/O**
   ```c
   // 使用缓冲读取而不是单字节读取
   char buffer[1024];
   while (fgets(buffer, sizeof(buffer), fp)) {
       // 处理一行
   }
   ```

## 可移植性检查清单

- [ ] 使用固定宽度整数类型 (int32_t, uint64_t等)
- [ ] 不依赖sizeof(int) == 4 的假设
- [ ] 不依赖指针大小
- [ ] 使用 stdint.h 的类型
- [ ] 测试big-endian和little-endian
- [ ] 避免平台特定的头文件
- [ ] 使用条件编译处理平台差异
