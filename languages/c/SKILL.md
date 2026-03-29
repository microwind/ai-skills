---
name: C语言编程
description: "当进行C语言开发、性能优化、内存管理或系统编程时，分析代码质量、设计模式和最佳实践。"
license: MIT
---

# C语言编程技能

## 概述
C语言是系统编程的基础，提供了接近硬件的能力和极高的性能。不当的内存管理、指针使用和资源管理会导致严重的安全问题、内存泄漏和崩溃。

**核心原则**: 好的C代码应该高效可靠、内存安全、资源管理清晰、易于维护。坏的C代码会内存泄漏、指针混乱、安全漏洞百出。

## 何时使用

**始终:**
- 系统编程和嵌入式开发
- 性能关键代码优化
- 内存管理审查
- 指针和资源生命周期分析
- 代码质量检查
- 安全审计

**触发短语:**
- "C内存管理最佳实践"
- "如何避免内存泄漏？"
- "指针使用规范"
- "C性能优化技巧"
- "资源管理模式"
- "C安全编码"

## C语言技能功能

### 内存管理
- malloc/free正确性检查
- 内存泄漏检测
- 缓冲区溢出防护
- 野指针识别
- 内存对齐优化

### 指针操作
- 指针声明和定义规范
- 指针算术安全
- 二级指针应用
- 函数指针使用
- 指针转换规范

### 资源管理
- 文件I/O管理
- 动态内存分配
- 资源生命周期
- RAII模式（变通实现）
- 异常安全

### 代码质量
- 复杂度分析
- 循环和条件优化
- 重复代码检测
- 命名规范检查
- 代码风格统一

### 并发与线程
- POSIX线程概念
- 临界区保护
- 互斥锁使用
- 条件变量
- 竞态条件检测

## 常见问题

### 内存问题
- **问题**: 内存泄漏
- **原因**: malloc后没有正确free
- **解决**: 配对检查malloc/free，使用工具检测

- **问题**: 缓冲区溢出
- **原因**: 数组越界访问
- **解决**: 使用数组长度检查，避免strcpy等不安全函数

- **问题**: 野指针访问
- **原因**: 使用已释放的指针
- **解决**: 释放后立即设置为NULL，避免重复释放

### 指针问题
- **问题**: 指针错用
- **原因**: 不清楚指针和数组的关系
- **解决**: 明确区分指针和数组，避免混淆

- **问题**: 指针转换不当
- **原因**: 类型和大小不匹配
- **解决**: 进行显式转换检查，使用sizeof验证

## 代码示例

### 安全的内存管理
```c
// 安全的动态数组分配
int* create_array(size_t size) {
    if (size == 0 || size > 1000000) {
        return NULL;  // 防止过大分配
    }
    int* array = (int*)malloc(size * sizeof(int));
    if (array == NULL) {
        perror("malloc failed");
        return NULL;
    }
    return array;
}

// 安全的字符串处理
void safe_string_copy(char* dest, const char* src, size_t dest_size) {
    if (dest == NULL || src == NULL || dest_size == 0) {
        return;
    }
    strncpy(dest, src, dest_size - 1);
    dest[dest_size - 1] = '\0';  // 确保null terminator
}

// 使用示例
int main() {
    int* array = create_array(100);
    if (array == NULL) return 1;
    
    // 使用数组
    for (int i = 0; i < 100; i++) {
        array[i] = i * i;
    }
    
    // 记得释放
    free(array);
    array = NULL;  // 防止野指针
    
    return 0;
}
```

### 文件I/O安全管理
```c
// 文件读取安全处理
int read_file_safely(const char* filename, char* buffer, size_t buffer_size) {
    FILE* fp = fopen(filename, "r");
    if (fp == NULL) {
        perror("fopen failed");
        return -1;
    }
    
    // 使用fgets确保缓冲区安全
    if (fgets(buffer, buffer_size, fp) == NULL) {
        perror("fgets failed");
        fclose(fp);
        return -1;
    }
    
    fclose(fp);
    return 0;
}

// 结构体和指针组合
typedef struct {
    char name[50];
    int age;
    float salary;
} Employee;

Employee* create_employee(const char* name, int age, float salary) {
    Employee* emp = (Employee*)malloc(sizeof(Employee));
    if (emp == NULL) return NULL;
    
    safe_string_copy(emp->name, name, sizeof(emp->name));
    emp->age = age;
    emp->salary = salary;
    
    return emp;
}

void free_employee(Employee* emp) {
    free(emp);  // 释放直接释放结构体本身
}
```

### 指针和数组关系
```c
// 理解指针和数组
void pointer_and_array_demo() {
    int arr[5] = {1, 2, 3, 4, 5};
    int* ptr = arr;
    
    // 数组最常见的是使用指针的形式访问
    printf("arr[0] = %d\n", arr[0]);    // 1
    printf("*ptr = %d\n", *ptr);        // 1
    printf("ptr[0] = %d\n", ptr[0]);    // 1
    printf("*(ptr+1) = %d\n", *(ptr+1)); // 2
    
    // 但是 sizeof会给出不同结果
    printf("sizeof(arr) = %lu\n", sizeof(arr));  // 20 (5*4)
    printf("sizeof(ptr) = %lu\n", sizeof(ptr));  // 8 (指针大小)
}

// 函数参数中数组退化为指针
void print_array(int arr[], size_t size) {
    // 注意：在函数参数中，arr是指针，不是数组
    // 所以必须单独传递size参数
    for (size_t i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}
```
