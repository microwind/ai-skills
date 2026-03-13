---
name: Go语言模式
description: "当应用Go语言设计模式时，分析并发模式，优化性能策略，解决架构问题。验证模式实现，设计系统架构，和最佳实践。"
license: MIT
---

# Go语言模式技能

## 概述
Go语言提供了独特的并发模型和简洁的语法结构，使得某些设计模式在Go中有着特殊的实现方式。不当的模式应用会导致代码复杂、性能低下、维护困难。在选择和实现设计模式前需要仔细分析Go语言特性。

**核心原则**: 好的Go模式应该简洁明了、并发安全、性能优良、易于维护。坏的Go模式会过度抽象、性能损耗、难以理解。

## 何时使用

**始终:**
- 设计系统架构时
- 处理并发编程时
- 优化代码结构时
- 提升代码复用时
- 解决设计问题时
- 团队协作开发时

**触发短语:**
- "Go中如何实现单例模式？"
- "Go并发模式最佳实践"
- "Go语言设计模式应用"
- "如何处理Go中的错误？"
- "Go性能优化模式"
- "Go微服务架构模式"

## Go语言模式技能功能

### 创建型模式
- 单例模式（Singleton）
- 工厂模式（Factory）
- 建造者模式（Builder）
- 原型模式（Prototype）
- 依赖注入（Dependency Injection）

### 结构型模式
- 适配器模式（Adapter）
- 装饰器模式（Decorator）
- 代理模式（Proxy）
- 组合模式（Composite）
- 外观模式（Facade）

### 行为型模式
- 观察者模式（Observer）
- 策略模式（Strategy）
- 命令模式（Command）
- 状态模式（State）
- 责任链模式（Chain of Responsibility）

### Go特有模式
- Goroutine模式
- Channel模式
- Select模式
- Context模式
- Error处理模式

## 常见问题

### 并发问题
- **问题**: Goroutine泄漏
- **原因**: Goroutine没有正确的退出机制
- **解决**: 使用Context控制Goroutine生命周期

- **问题**: 数据竞争
- **原因**: 多个Goroutine同时访问共享数据
- **解决**: 使用Mutex或Channel进行同步

- **问题**: 死锁
- **原因**: 不当的锁顺序或Channel使用
- **解决**: 遵循一致的锁获取顺序，避免循环依赖

### 设计问题
- **问题**: 过度使用全局变量
- **原因**: 缺乏依赖注入意识
- **解决**: 使用依赖注入模式管理对象生命周期

- **问题**: 错误处理不一致
- **原因**: 缺乏统一的错误处理策略
- **解决**: 实现统一的错误处理模式

## 代码示例

### 单例模式实现
```go
package singleton

import (
    "sync"
)

// 单例结构体
type DatabaseConnection struct {
    connection string
}

// 私有变量
var (
    instance *DatabaseConnection
    once     sync.Once
)

// 获取单例实例
func GetDatabaseConnection() *DatabaseConnection {
    once.Do(func() {
        instance = &DatabaseConnection{
            connection: "mysql://localhost:3306/mydb",
        }
    })
    return instance
}

// 使用示例
func ExampleSingleton() {
    db1 := GetDatabaseConnection()
    db2 := GetDatabaseConnection()
    
    // db1 和 db2 是同一个实例
    println(db1 == db2) // true
}
```

### 工厂模式实现
```go
package factory

import "fmt"

// 动物接口
type Animal interface {
    Speak() string
}

// 狗实现
type Dog struct{}

func (d Dog) Speak() string {
    return "汪汪"
}

// 猫实现
type Cat struct{}

func (c Cat) Speak() string {
    return "喵喵"
}

// 工厂函数
func CreateAnimal(animalType string) Animal {
    switch animalType {
    case "dog":
        return Dog{}
    case "cat":
        return Cat{}
    default:
        return nil
    }
}

// 使用示例
func ExampleFactory() {
    dog := CreateAnimal("dog")
    cat := CreateAnimal("cat")
    
    fmt.Println(dog.Speak()) // 汪汪
    fmt.Println(cat.Speak()) // 喵喵
}
```

### 观察者模式实现
```go
package observer

import (
    "fmt"
    "sync"
)

// 观察者接口
type Observer interface {
    Update(data interface{})
}

// 主题接口
type Subject interface {
    Register(observer Observer)
    Unregister(observer Observer)
    Notify(data interface{})
}

// 具体主题
type WeatherStation struct {
    observers []Observer
    mutex     sync.RWMutex
    temperature float64
}

func NewWeatherStation() *WeatherStation {
    return &WeatherStation{
        observers: make([]Observer, 0),
    }
}

func (ws *WeatherStation) Register(observer Observer) {
    ws.mutex.Lock()
    defer ws.mutex.Unlock()
    ws.observers = append(ws.observers, observer)
}

func (ws *WeatherStation) Unregister(observer Observer) {
    ws.mutex.Lock()
    defer ws.mutex.Unlock()
    
    for i, obs := range ws.observers {
        if obs == observer {
            ws.observers = append(ws.observers[:i], ws.observers[i+1:]...)
            break
        }
    }
}

func (ws *WeatherStation) Notify(data interface{}) {
    ws.mutex.RLock()
    defer ws.mutex.RUnlock()
    
    for _, observer := range ws.observers {
        observer.Update(data)
    }
}

func (ws *WeatherStation) SetTemperature(temp float64) {
    ws.temperature = temp
    ws.Notify(ws.temperature)
}

// 具体观察者
type TemperatureDisplay struct {
    name string
}

func (td TemperatureDisplay) Update(data interface{}) {
    fmt.Printf("%s: 当前温度 %.1f°C\n", td.name, data.(float64))
}

// 使用示例
func ExampleObserver() {
    station := NewWeatherStation()
    
    display1 := TemperatureDisplay{name: "显示器1"}
    display2 := TemperatureDisplay{name: "显示器2"}
    
    station.Register(display1)
    station.Register(display2)
    
    station.SetTemperature(25.5)
    // 输出:
    // 显示器1: 当前温度 25.5°C
    // 显示器2: 当前温度 25.5°C
}
```

### Worker Pool模式
```go
package workerpool

import (
    "fmt"
    "sync"
    "time"
)

// 任务接口
type Task interface {
    Execute() error
}

// 具体任务
type PrintTask struct {
    message string
}

func (pt PrintTask) Execute() error {
    fmt.Println(pt.message)
    return nil
}

// Worker Pool
type WorkerPool struct {
    tasks    chan Task
    workers  int
    wg       sync.WaitGroup
    quit     chan bool
}

func NewWorkerPool(workers int) *WorkerPool {
    return &WorkerPool{
        tasks:   make(chan Task, workers*2),
        workers: workers,
        quit:    make(chan bool),
    }
}

func (wp *WorkerPool) Start() {
    for i := 0; i < wp.workers; i++ {
        wp.wg.Add(1)
        go wp.worker(i)
    }
}

func (wp *WorkerPool) worker(id int) {
    defer wp.wg.Done()
    
    for {
        select {
        case task := <-wp.tasks:
            if err := task.Execute(); err != nil {
                fmt.Printf("Worker %d 执行任务失败: %v\n", id, err)
            }
        case <-wp.quit:
            fmt.Printf("Worker %d 退出\n", id)
            return
        }
    }
}

func (wp *WorkerPool) Submit(task Task) {
    wp.tasks <- task
}

func (wp *WorkerPool) Stop() {
    close(wp.quit)
    wp.wg.Wait()
    close(wp.tasks)
}

// 使用示例
func ExampleWorkerPool() {
    pool := NewWorkerPool(3)
    pool.Start()
    defer pool.Stop()
    
    // 提交任务
    for i := 0; i < 10; i++ {
        task := PrintTask{message: fmt.Sprintf("任务 %d", i)}
        pool.Submit(task)
    }
    
    time.Sleep(time.Second) // 等待任务完成
}
```

### Context模式实现
```go
package contextpattern

import (
    "context"
    "fmt"
    "time"
)

// 长时间运行的操作
func LongRunningOperation(ctx context.Context, duration time.Duration) error {
    select {
    case <-time.After(duration):
        fmt.Println("操作完成")
        return nil
    case <-ctx.Done():
        fmt.Println("操作被取消:", ctx.Err())
        return ctx.Err()
    }
}

// 带超时的操作
func OperationWithTimeout(timeout time.Duration) error {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()
    
    return LongRunningOperation(ctx, 2*time.Second)
}

// 带取消的操作
func OperationWithCancel() error {
    ctx, cancel := context.WithCancel(context.Background())
    
    // 模拟在1秒后取消操作
    go func() {
        time.Sleep(1 * time.Second)
        cancel()
    }()
    
    return LongRunningOperation(ctx, 5*time.Second)
}

// 使用示例
func ExampleContext() {
    fmt.Println("=== 带超时的操作 ===")
    err := OperationWithTimeout(1 * time.Second)
    if err != nil {
        fmt.Println("操作失败:", err)
    }
    
    fmt.Println("\n=== 带取消的操作 ===")
    err = OperationWithCancel()
    if err != nil {
        fmt.Println("操作失败:", err)
    }
}
```

### 错误处理模式
```go
package errorpattern

import (
    "errors"
    "fmt"
)

// 自定义错误类型
type AppError struct {
    Code    int
    Message string
    Cause   error
}

func (e AppError) Error() string {
    if e.Cause != nil {
        return fmt.Sprintf("Code: %d, Message: %s, Cause: %v", 
            e.Code, e.Message, e.Cause)
    }
    return fmt.Sprintf("Code: %d, Message: %s", e.Code, e.Message)
}

func (e AppError) Unwrap() error {
    return e.Cause
}

// 错误码常量
const (
    ErrCodeNotFound     = 404
    ErrCodeInvalidInput = 400
    ErrCodeInternal     = 500
)

// 创建特定错误
func NewNotFoundError(message string, cause error) error {
    return AppError{
        Code:    ErrCodeNotFound,
        Message: message,
        Cause:   cause,
    }
}

func NewInvalidInputError(message string) error {
    return AppError{
        Code:    ErrCodeInvalidInput,
        Message: message,
    }
}

// 业务逻辑
func FindUser(id int) (string, error) {
    if id <= 0 {
        return "", NewInvalidInputError("用户ID必须大于0")
    }
    
    if id == 999 {
        return "", NewNotFoundError("用户不存在", errors.New("数据库查询失败"))
    }
    
    return fmt.Sprintf("用户%d", id), nil
}

// 错误处理包装器
func HandleError(err error) {
    if err == nil {
        return
    }
    
    var appErr AppError
    if errors.As(err, &appErr) {
        switch appErr.Code {
        case ErrCodeNotFound:
            fmt.Printf("404错误: %s\n", appErr.Message)
        case ErrCodeInvalidInput:
            fmt.Printf("400错误: %s\n", appErr.Message)
        case ErrCodeInternal:
            fmt.Printf("500错误: %s\n", appErr.Message)
        default:
            fmt.Printf("未知错误: %s\n", appErr.Message)
        }
    } else {
        fmt.Printf("系统错误: %v\n", err)
    }
}

// 使用示例
func ExampleErrorHandling() {
    fmt.Println("=== 错误处理示例 ===")
    
    // 正常情况
    user, err := FindUser(1)
    if err != nil {
        HandleError(err)
    } else {
        fmt.Println("找到用户:", user)
    }
    
    // 无效输入
    _, err = FindUser(-1)
    HandleError(err)
    
    // 用户不存在
    _, err = FindUser(999)
    HandleError(err)
}
```

### 管道模式实现
```go
package pipeline

import (
    "fmt"
    "sync"
)

// 管道阶段函数类型
type PipelineFunc func(interface{}) (interface{}, error)

// 管道
type Pipeline struct {
    stages []PipelineFunc
}

func NewPipeline() *Pipeline {
    return &Pipeline{
        stages: make([]PipelineFunc, 0),
    }
}

func (p *Pipeline) AddStage(stage PipelineFunc) *Pipeline {
    p.stages = append(p.stages, stage)
    return p
}

func (p *Pipeline) Execute(input interface{}) (interface{}, error) {
    var err error
    result := input
    
    for i, stage := range p.stages {
        result, err = stage(result)
        if err != nil {
            return nil, fmt.Errorf("阶段 %d 执行失败: %w", i, err)
        }
    }
    
    return result, nil
}

// 并发管道
type ConcurrentPipeline struct {
    stages []PipelineFunc
    workers int
}

func NewConcurrentPipeline(workers int) *ConcurrentPipeline {
    return &ConcurrentPipeline{
        stages:  make([]PipelineFunc, 0),
        workers: workers,
    }
}

func (cp *ConcurrentPipeline) AddStage(stage PipelineFunc) *ConcurrentPipeline {
    cp.stages = append(cp.stages, stage)
    return cp
}

func (cp *ConcurrentPipeline) Execute(inputs []interface{}) ([]interface{}, error) {
    var wg sync.WaitGroup
    results := make([]interface{}, len(inputs))
    errors := make([]error, len(inputs))
    
    // 创建工作通道
    workChan := make(chan int, len(inputs))
    
    // 启动工作协程
    for i := 0; i < cp.workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for index := range workChan {
                result, err := cp.processInput(inputs[index])
                results[index] = result
                errors[index] = err
            }
        }()
    }
    
    // 分发工作
    for i := range inputs {
        workChan <- i
    }
    close(workChan)
    
    wg.Wait()
    
    // 检查错误
    for _, err := range errors {
        if err != nil {
            return nil, err
        }
    }
    
    return results, nil
}

func (cp *ConcurrentPipeline) processInput(input interface{}) (interface{}, error) {
    result := input
    var err error
    
    for _, stage := range cp.stages {
        result, err = stage(result)
        if err != nil {
            return nil, err
        }
    }
    
    return result, nil
}

// 示例阶段函数
func ValidateInput(input interface{}) (interface{}, error) {
    str, ok := input.(string)
    if !ok {
        return nil, fmt.Errorf("输入必须是字符串")
    }
    if str == "" {
        return nil, fmt.Errorf("输入不能为空")
    }
    return str, nil
}

func Transform(input interface{}) (interface{}, error) {
    str := input.(string)
    return fmt.Sprintf("处理后的: %s", str), nil
}

func FormatOutput(input interface{}) (interface{}, error) {
    str := input.(string)
    return fmt.Sprintf("最终结果: [%s]", str), nil
}

// 使用示例
func ExamplePipeline() {
    fmt.Println("=== 顺序管道示例 ===")
    
    pipeline := NewPipeline()
    pipeline.AddStage(ValidateInput)
    pipeline.AddStage(Transform)
    pipeline.AddStage(FormatOutput)
    
    result, err := pipeline.Execute("Hello World")
    if err != nil {
        fmt.Println("管道执行失败:", err)
    } else {
        fmt.Println("结果:", result)
    }
    
    fmt.Println("\n=== 并发管道示例 ===")
    
    inputs := []interface{}{
        "输入1", "输入2", "输入3", "输入4", "输入5",
    }
    
    concurrentPipeline := NewConcurrentPipeline(3)
    concurrentPipeline.AddStage(ValidateInput)
    concurrentPipeline.AddStage(Transform)
    concurrentPipeline.AddStage(FormatOutput)
    
    results, err := concurrentPipeline.Execute(inputs)
    if err != nil {
        fmt.Println("并发管道执行失败:", err)
    } else {
        for i, result := range results {
            fmt.Printf("结果%d: %v\n", i+1, result)
        }
    }
}
```

## 最佳实践

### 模式选择原则
1. **简洁优先**: 选择最简单有效的解决方案
2. **Go语言特性**: 充分利用Go的并发和接口特性
3. **性能考虑**: 避免不必要的抽象和性能损耗
4. **可读性**: 代码应该易于理解和维护

### 并发编程
1. **Goroutine管理**: 使用Context控制生命周期
2. **Channel使用**: 避免死锁和数据竞争
3. **同步机制**: 合理使用Mutex和WaitGroup
4. **错误处理**: 在并发中正确处理错误

### 代码组织
1. **包设计**: 保持包的职责单一
2. **接口设计**: 接口应该小而专注
3. **依赖管理**: 使用依赖注入减少耦合
4. **测试覆盖**: 为模式实现编写充分测试

## 相关技能

- **rust-systems** - 系统编程模式
- **python-advanced** - 高级编程模式
- **javascript-es6** - 现代JavaScript模式
- **backend** - 后端架构模式
- **performance-optimization** - 性能优化策略
