# Go语言设计模式参考文档

## Go语言特性

### 语言特点
Go语言是一门静态类型的编译型语言，具有以下特点：
- **简洁语法**: 25个关键字，语法简洁明了
- **并发支持**: 原生支持Goroutine和Channel
- **垃圾回收**: 自动内存管理
- **静态类型**: 编译时类型检查
- **跨平台**: 支持多平台编译

### 设计哲学
- **少即是多**: 简单的语法和特性
- **明确优于隐式**: 代码意图清晰
- **组合优于继承**: 通过组合实现代码复用
- **并发是核心**: 并发编程内置支持

## 创建型模式

### 单例模式

#### 线程安全单例
```go
package singleton

import "sync"

type Singleton struct {
    data string
}

var (
    instance *Singleton
    once     sync.Once
)

// GetInstance 返回单例实例
func GetInstance() *Singleton {
    once.Do(func() {
        instance = &Singleton{data: "singleton data"}
    })
    return instance
}

// 懒加载单例
func (s *Singleton) GetData() string {
    return s.data
}

func (s *Singleton) SetData(data string) {
    s.data = data
}
```

#### 使用示例
```go
package main

import (
    "fmt"
    "./singleton"
)

func main() {
    // 获取单例实例
    s1 := singleton.GetInstance()
    s2 := singleton.GetInstance()
    
    fmt.Println(s1 == s2) // true
    
    s1.SetData("new data")
    fmt.Println(s2.GetData()) // "new data"
}
```

### 工厂模式

#### 简单工厂
```go
package factory

// Animal 接口
type Animal interface {
    Speak() string
}

// Dog 结构体
type Dog struct{}

func (d Dog) Speak() string {
    return "Woof!"
}

// Cat 结构体
type Cat struct{}

func (c Cat) Speak() string {
    return "Meow!"
}

// AnimalFactory 工厂
type AnimalFactory struct{}

func (af AnimalFactory) CreateAnimal(animalType string) Animal {
    switch animalType {
    case "dog":
        return Dog{}
    case "cat":
        return Cat{}
    default:
        return nil
    }
}
```

#### 抽象工厂
```go
package factory

// GUIFactory 抽象工厂接口
type GUIFactory interface {
    CreateButton() Button
    CreateCheckbox() Checkbox
}

// Button 接口
type Button interface {
    Paint()
}

// Checkbox 接口
type Checkbox interface {
    Check()
}

// WindowsFactory Windows风格工厂
type WindowsFactory struct{}

func (wf WindowsFactory) CreateButton() Button {
    return WindowsButton{}
}

func (wf WindowsFactory) CreateCheckbox() Checkbox {
    return WindowsCheckbox{}
}

// WindowsButton Windows按钮
type WindowsButton struct{}

func (wb WindowsButton) Paint() {
    fmt.Println("Windows button painted")
}

// WindowsCheckbox Windows复选框
type WindowsCheckbox struct{}

func (wc WindowsCheckbox) Check() {
    fmt.Println("Windows checkbox checked")
}

// MacFactory Mac风格工厂
type MacFactory struct{}

func (mf MacFactory) CreateButton() Button {
    return MacButton{}
}

func (mf MacFactory) CreateCheckbox() Checkbox {
    return MacCheckbox{}
}
```

### 建造者模式

#### 建造者实现
```go
package builder

// Computer 产品结构
type Computer struct {
    CPU     string
    Memory  int
    Storage int
    GPU     string
    Screen  string
}

// ComputerBuilder 建造者接口
type ComputerBuilder interface {
    SetCPU(cpu string) ComputerBuilder
    SetMemory(memory int) ComputerBuilder
    SetStorage(storage int) ComputerBuilder
    SetGPU(gpu string) ComputerBuilder
    SetScreen(screen string) ComputerBuilder
    Build() Computer
}

// ConcreteBuilder 具体建造者
type ConcreteBuilder struct {
    computer Computer
}

func NewConcreteBuilder() *ConcreteBuilder {
    return &ConcreteBuilder{
        computer: Computer{},
    }
}

func (cb *ConcreteBuilder) SetCPU(cpu string) ComputerBuilder {
    cb.computer.CPU = cpu
    return cb
}

func (cb *ConcreteBuilder) SetMemory(memory int) ComputerBuilder {
    cb.computer.Memory = memory
    return cb
}

func (cb *ConcreteBuilder) SetStorage(storage int) ComputerBuilder {
    cb.computer.Storage = storage
    return cb
}

func (cb *ConcreteBuilder) SetGPU(gpu string) ComputerBuilder {
    cb.computer.GPU = gpu
    return cb
}

func (cb *ConcreteBuilder) SetScreen(screen string) ComputerBuilder {
    cb.computer.Screen = screen
    return cb
}

func (cb *ConcreteBuilder) Build() Computer {
    return cb.computer
}

// Director 指挥者
type Director struct {
    builder ComputerBuilder
}

func NewDirector(builder ComputerBuilder) *Director {
    return &Director{builder: builder}
}

func (d *Director) ConstructGamingComputer() Computer {
    return d.builder.
        SetCPU("Intel i9").
        SetMemory(32).
        SetStorage(1000).
        SetGPU("RTX 3080").
        SetScreen("4K").
        Build()
}

func (d *Director) ConstructOfficeComputer() Computer {
    return d.builder.
        SetCPU("Intel i5").
        SetMemory(16).
        SetStorage(512).
        SetGPU("Integrated").
        SetScreen("1080p").
        Build()
}
```

## 结构型模式

### 适配器模式

#### 接口适配
```go
package adapter

// LegacyAdaptee 遗留系统接口
type LegacyAdaptee struct{}

func (la LegacyAdaptee) SpecificRequest() string {
    return "Legacy specific request"
}

// Target 目标接口
type Target interface {
    Request() string
}

// Adapter 适配器
type Adapter struct {
    adaptee LegacyAdaptee
}

func NewAdapter(adaptee LegacyAdaptee) *Adapter {
    return &Adapter{adaptee: adaptee}
}

func (a *Adapter) Request() string {
    result := a.adaptee.SpecificRequest()
    return fmt.Sprintf("Adapter: (TRANSLATED) %s", result)
}
```

### 装饰器模式

#### 功能装饰
```go
package decorator

// Component 组件接口
type Component interface {
    Operation() string
}

// ConcreteComponent 具体组件
type ConcreteComponent struct{}

func (cc ConcreteComponent) Operation() string {
    return "ConcreteComponent"
}

// Decorator 装饰器基类
type Decorator struct {
    component Component
}

func (d *Decorator) Operation() string {
    return d.component.Operation()
}

// ConcreteDecoratorA 具体装饰器A
type ConcreteDecoratorA struct {
    Decorator
    addedState string
}

func NewConcreteDecoratorA(component Component) *ConcreteDecoratorA {
    return &ConcreteDecoratorA{
        Decorator:    Decorator{component: component},
        addedState: "New State",
    }
}

func (cda *ConcreteDecoratorA) Operation() string {
    return fmt.Sprintf("%s + ConcreteDecoratorA(%s)", 
        cda.Decorator.Operation(), cda.addedState)
}

// ConcreteDecoratorB 具体装饰器B
type ConcreteDecoratorB struct {
    Decorator
}

func NewConcreteDecoratorB(component Component) *ConcreteDecoratorB {
    return &ConcreteDecoratorB{Decorator: Decorator{component: component}}
}

func (cdb *ConcreteDecoratorB) Operation() string {
    return fmt.Sprintf("%s + ConcreteDecoratorB", cdb.Decorator.Operation())
}
```

### 代理模式

#### 远程代理
```go
package proxy

// Subject 主题接口
type Subject interface {
    Request() string
}

// RealSubject 真实主题
type RealSubject struct{}

func (rs RealSubject) Request() string {
    return "RealSubject: Handling request"
}

// Proxy 代理
type Proxy struct {
    realSubject RealSubject
    cache       string
    cacheValid  bool
}

func NewProxy() *Proxy {
    return &Proxy{
        realSubject: RealSubject{},
        cacheValid:  false,
    }
}

func (p *Proxy) Request() string {
    if !p.cacheValid {
        fmt.Println("Proxy: Loading real subject")
        p.cache = p.realSubject.Request()
        p.cacheValid = true
    } else {
        fmt.Println("Proxy: Using cached result")
    }
    
    return fmt.Sprintf("Proxy: %s", p.cache)
}
```

## 行为型模式

### 策略模式

#### 算法封装
```go
package strategy

// Strategy 策略接口
type Strategy interface {
    Execute(a, b int) int
}

// ConcreteStrategyA 具体策略A
type ConcreteStrategyA struct{}

func (csa ConcreteStrategyA) Execute(a, b int) int {
    return a + b
}

// ConcreteStrategyB 具体策略B
type ConcreteStrategyB struct{}

func (csb ConcreteStrategyB) Execute(a, b int) int {
    return a - b
}

// ConcreteStrategyC 具体策略C
type ConcreteStrategyC struct{}

func (csc ConcreteStrategyC) Execute(a, b int) int {
    return a * b
}

// Context 上下文
type Context struct {
    strategy Strategy
}

func NewContext(strategy Strategy) *Context {
    return &Context{strategy: strategy}
}

func (c *Context) SetStrategy(strategy Strategy) {
    c.strategy = strategy
}

func (c *Context) ExecuteStrategy(a, b int) int {
    return c.strategy.Execute(a, b)
}
```

### 观察者模式

#### 事件驱动
```go
package observer

// Observer 观察者接口
type Observer interface {
    Update(data string)
}

// Subject 主题接口
type Subject interface {
    Attach(observer Observer)
    Detach(observer Observer)
    Notify(data string)
}

// ConcreteSubject 具体主题
type ConcreteSubject struct {
    observers []Observer
}

func NewConcreteSubject() *ConcreteSubject {
    return &ConcreteSubject{
        observers: make([]Observer, 0),
    }
}

func (cs *ConcreteSubject) Attach(observer Observer) {
    cs.observers = append(cs.observers, observer)
}

func (cs *ConcreteSubject) Detach(observer Observer) {
    for i, obs := range cs.observers {
        if obs == observer {
            cs.observers = append(cs.observers[:i], cs.observers[i+1:]...)
            break
        }
    }
}

func (cs *ConcreteSubject) Notify(data string) {
    for _, observer := range cs.observers {
        observer.Update(data)
    }
}

// ConcreteObserver 具体观察者
type ConcreteObserver struct {
    name string
}

func NewConcreteObserver(name string) *ConcreteObserver {
    return &ConcreteObserver{name: name}
}

func (co *ConcreteObserver) Update(data string) {
    fmt.Printf("Observer %s received: %s\n", co.name, data)
}
```

### 命令模式

#### 命令封装
```go
package command

// Command 命令接口
type Command interface {
    Execute()
    Undo()
}

// Receiver 接收者
type Receiver struct{}

func (r *Receiver) Action() {
    fmt.Println("Receiver: executing action")
}

func (r *Receiver) UndoAction() {
    fmt.Println("Receiver: undoing action")
}

// ConcreteCommand 具体命令
type ConcreteCommand struct {
    receiver *Receiver
}

func NewConcreteCommand(receiver *Receiver) *ConcreteCommand {
    return &ConcreteCommand{receiver: receiver}
}

func (cc *ConcreteCommand) Execute() {
    cc.receiver.Action()
}

func (cc *ConcreteCommand) Undo() {
    cc.receiver.UndoAction()
}

// Invoker 调用者
type Invoker struct {
    commands []Command
    history  []Command
}

func NewInvoker() *Invoker {
    return &Invoker{
        commands: make([]Command, 0),
        history:  make([]Command, 0),
    }
}

func (i *Invoker) SetCommand(command Command) {
    i.commands = append(i.commands, command)
}

func (i *Invoker) ExecuteCommands() {
    for _, command := range i.commands {
        command.Execute()
        i.history = append(i.history, command)
    }
    i.commands = i.commands[:0] // 清空命令列表
}

func (i *Invoker) UndoLastCommand() {
    if len(i.history) > 0 {
        lastCommand := i.history[len(i.history)-1]
        lastCommand.Undo()
        i.history = i.history[:len(i.history)-1]
    }
}
```

## 并发模式

### Worker池模式

#### 并发任务处理
```go
package pool

import (
    "sync"
    "time"
)

// Task 任务接口
type Task interface {
    Execute() error
}

// Worker Worker结构
type Worker struct {
    id       int
    taskChan chan Task
    quit     chan bool
    wg       *sync.WaitGroup
}

func NewWorker(id int, taskChan chan Task, wg *sync.WaitGroup) *Worker {
    return &Worker{
        id:       id,
        taskChan: taskChan,
        quit:     make(chan bool),
        wg:       wg,
    }
}

func (w *Worker) Start() {
    go func() {
        defer w.wg.Done()
        
        for {
            select {
            case task := <-w.taskChan:
                if err := task.Execute(); err != nil {
                    fmt.Printf("Worker %d task error: %v\n", w.id, err)
                }
            case <-w.quit:
                fmt.Printf("Worker %d stopping\n", w.id)
                return
            }
        }
    }()
}

func (w *Worker) Stop() {
    close(w.quit)
}

// WorkerPool Worker池
type WorkerPool struct {
    workers    []*Worker
    taskChan   chan Task
    workerWg   sync.WaitGroup
    quitChan   chan bool
    maxWorkers int
}

func NewWorkerPool(maxWorkers int) *WorkerPool {
    return &WorkerPool{
        taskChan:   make(chan Task, maxWorkers*2),
        quitChan:   make(chan bool),
        maxWorkers: maxWorkers,
    }
}

func (wp *WorkerPool) Start() {
    for i := 0; i < wp.maxWorkers; i++ {
        worker := NewWorker(i, wp.taskChan, &wp.workerWg)
        wp.workers = append(wp.workers, worker)
        wp.workerWg.Add(1)
        worker.Start()
    }
}

func (wp *WorkerPool) Stop() {
    close(wp.quitChan)
    for _, worker := range wp.workers {
        worker.Stop()
    }
    wp.workerWg.Wait()
}

func (wp *WorkerPool) Submit(task Task) {
    select {
    case wp.taskChan <- task:
    case <-wp.quitChan:
        fmt.Println("Worker pool is shutting down, task rejected")
    }
}
```

### Fan-in/Fan-out模式

#### 数据流处理
```go
package fan

import (
    "sync"
    "time"
)

// Generator 数据生成器
func Generator(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

// Square 计算平方
func Square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            time.Sleep(100 * time.Millisecond) // 模拟耗时操作
            out <- n * n
        }
    }()
    return out
}

// Fan-in 合并多个channel
func FanIn(inputs ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    out := make(chan int)
    
    output := func(c <-chan int) {
        defer wg.Done()
        for n := range c {
            out <- n
        }
    }
    
    wg.Add(len(inputs))
    for _, input := range inputs {
        go output(input)
    }
    
    go func() {
        wg.Wait()
        close(out)
    }()
    
    return out
}

// Fan-out 分发到多个worker
func FanOut(input <-chan int, workers int) []<-chan int {
    outputs := make([]<-chan int, workers)
    
    for i := 0; i < workers; i++ {
        outputs[i] = Square(input)
    }
    
    return outputs
}
```

### Pipeline模式

#### 流水线处理
```go
package pipeline

import (
    "fmt"
    "time"
)

// Stage 流水线阶段
type Stage func(in <-chan int) <-chan int

// Pipeline 流水线
func Pipeline(stages ...Stage) <-chan int {
    in := make(chan int)
    go func() {
        defer close(in)
        for i := 1; i <= 10; i++ {
            in <- i
        }
    }()
    
    for _, stage := range stages {
        in = stage(in)
    }
    
    return in
}

// Filter 过滤阶段
func Filter(predicate func(int) bool) Stage {
    return func(in <-chan int) <-chan int {
        out := make(chan int)
        go func() {
            defer close(out)
            for n := range in {
                if predicate(n) {
                    out <- n
                }
            }
        }()
        return out
    }
}

// Map 映射阶段
func Map(transform func(int) int) Stage {
    return func(in <-chan int) <-chan int {
        out := make(chan int)
        go func() {
            defer close(out)
            for n := range in {
                out <- transform(n)
            }
        }()
        return out
    }
}

// Reduce 聚合阶段
func Reduce(reduce func(int, int) int, initial int) Stage {
    return func(in <-chan int) <-chan int {
        out := make(chan int)
        go func() {
            defer close(out)
            result := initial
            for n := range in {
                result = reduce(result, n)
            }
            out <- result
        }()
        return out
    }
}

// 使用示例
func ExamplePipeline() {
    // 创建流水线：过滤偶数 -> 乘以2 -> 求和
    pipeline := Pipeline(
        Filter(func(n int) bool { return n%2 == 1 }), // 过滤奇数
        Map(func(n int) int { return n * 2 }),        // 乘以2
        Reduce(func(a, b int) int { return a + b }, 0), // 求和
    )
    
    result := <-pipeline
    fmt.Printf("Pipeline result: %d\n", result)
}
```

## 错误处理模式

### 错误包装

#### 错误链
```go
package errors

import (
    "fmt"
    "runtime"
)

// WrappedError 包装错误
type WrappedError struct {
    err     error
    message string
    stack   []uintptr
}

func (we *WrappedError) Error() string {
    return fmt.Sprintf("%s: %v", we.message, we.err)
}

func (we *WrappedError) Unwrap() error {
    return we.err
}

func (we *WrappedError) StackTrace() []uintptr {
    return we.stack
}

// Wrap 包装错误
func Wrap(err error, message string) error {
    if err == nil {
        return nil
    }
    
    const depth = 32
    var pcs [depth]uintptr
    n := runtime.Callers(2, pcs[:])
    
    return &WrappedError{
        err:     err,
        message: message,
        stack:   pcs[:n],
    }
}

// New 创建新错误
func New(message string) error {
    return &WrappedError{
        err:     fmt.Errorf(message),
        message: message,
    }
}
```

### 重试模式

#### 指数退避重试
```go
package retry

import (
    "context"
    "fmt"
    "math"
    "time"
)

// RetryFunc 重试函数类型
type RetryFunc func() error

// RetryConfig 重试配置
type RetryConfig struct {
    MaxAttempts int
    InitialDelay time.Duration
    MaxDelay     time.Duration
    Multiplier   float64
}

// Retry 重试函数
func Retry(ctx context.Context, config RetryConfig, fn RetryFunc) error {
    var lastErr error
    delay := config.InitialDelay
    
    for attempt := 1; attempt <= config.MaxAttempts; attempt++ {
        if err := fn(); err == nil {
            return nil
        } else {
            lastErr = err
            if attempt < config.MaxAttempts {
                sleepTime := time.Duration(math.Min(float64(delay), float64(config.MaxDelay)))
                select {
                case <-ctx.Done():
                    return ctx.Err()
                case <-time.After(sleepTime):
                    delay = time.Duration(float64(delay) * config.Multiplier)
                }
            }
        }
    }
    
    return fmt.Errorf("max retry attempts reached, last error: %w", lastErr)
}

// 使用示例
func ExampleRetry() {
    config := RetryConfig{
        MaxAttempts: 3,
        InitialDelay: 100 * time.Millisecond,
        MaxDelay:     1 * time.Second,
        Multiplier:   2.0,
    }
    
    attempt := 0
    err := Retry(context.Background(), config, func() error {
        attempt++
        if attempt < 3 {
            return fmt.Errorf("temporary failure")
        }
        return nil
    })
    
    if err != nil {
        fmt.Printf("Retry failed: %v\n", err)
    } else {
        fmt.Println("Retry succeeded")
    }
}
```

## 性能优化模式

### 对象池模式

#### 内存池化
```go
package pool

import (
    "sync"
)

// Pool 对象池
type Pool struct {
    pool sync.Pool
    new  func() interface{}
}

func NewPool(newFunc func() interface{}) *Pool {
    return &Pool{
        pool: sync.Pool{
            New: newFunc,
        },
        new: newFunc,
    }
}

func (p *Pool) Get() interface{} {
    return p.pool.Get()
}

func (p *Pool) Put(x interface{}) {
    p.pool.Put(x)
}

// BufferPool 字节缓冲池
type BufferPool struct {
    pool sync.Pool
}

func NewBufferPool() *BufferPool {
    return &BufferPool{
        pool: sync.Pool{
            New: func() interface{} {
                return make([]byte, 0, 1024)
            },
        },
    }
}

func (bp *BufferPool) Get() []byte {
    return bp.pool.Get().([]byte)
}

func (bp *BufferPool) Put(buf []byte) {
    if cap(buf) < 1024 {
        return // 不回收太小的缓冲区
    }
    buf = buf[:0] // 重置长度但保留容量
    bp.pool.Put(buf)
}
```

### 缓存模式

#### LRU缓存
```go
package cache

import (
    "container/list"
    "sync"
)

// CacheItem 缓存项
type CacheItem struct {
    key   interface{}
    value interface{}
}

// LRUCache LRU缓存
type LRUCache struct {
    capacity int
    cache    map[interface{}]*list.Element
    list     *list.List
    mutex    sync.RWMutex
}

func NewLRUCache(capacity int) *LRUCache {
    return &LRUCache{
        capacity: capacity,
        cache:    make(map[interface{}]*list.Element),
        list:     list.New(),
    }
}

func (c *LRUCache) Get(key interface{}) (interface{}, bool) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    
    if elem, exists := c.cache[key]; exists {
        c.list.MoveToFront(elem)
        return elem.Value.(*CacheItem).value, true
    }
    
    return nil, false
}

func (c *LRUCache) Put(key, value interface{}) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    
    if elem, exists := c.cache[key]; exists {
        c.list.MoveToFront(elem)
        elem.Value.(*CacheItem).value = value
        return
    }
    
    if c.list.Len() >= c.capacity {
        c.evict()
    }
    
    item := &CacheItem{key: key, value: value}
    elem := c.list.PushFront(item)
    c.cache[key] = elem
}

func (c *LRUCache) evict() {
    if elem := c.list.Back(); elem != nil {
        c.list.Remove(elem)
        item := elem.Value.(*CacheItem)
        delete(c.cache, item.key)
    }
}

func (c *LRUCache) Remove(key interface{}) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    
    if elem, exists := c.cache[key]; exists {
        c.list.Remove(elem)
        delete(c.cache, key)
    }
}

func (c *LRUCache) Len() int {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    return c.list.Len()
}
```

## Web开发模式

### 中间件模式

#### HTTP中间件
```go
package middleware

import (
    "context"
    "net/http"
    "time"
)

// Middleware 中间件类型
type Middleware func(http.Handler) http.Handler

// Chain 中间件链
func Chain(middlewares ...Middleware) Middleware {
    return func(final http.Handler) http.Handler {
        for i := len(middlewares) - 1; i >= 0; i-- {
            final = middlewares[i](final)
        }
        return final
    }
}

// Logging 日志中间件
func Logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        
        // 创建响应记录器
        recorder := &responseRecorder{
            ResponseWriter: w,
            statusCode:     http.StatusOK,
        }
        
        next.ServeHTTP(recorder, r)
        
        duration := time.Since(start)
        fmt.Printf("%s %s %d %v\n", 
            r.Method, r.URL.Path, recorder.statusCode, duration)
    })
}

// CORS 跨域中间件
func CORS(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
        
        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }
        
        next.ServeHTTP(w, r)
    })
}

// Timeout 超时中间件
func Timeout(timeout time.Duration) Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            ctx, cancel := context.WithTimeout(r.Context(), timeout)
            defer cancel()
            
            r = r.WithContext(ctx)
            
            done := make(chan struct{})
            go func() {
                defer close(done)
                next.ServeHTTP(w, r)
            }()
            
            select {
            case <-done:
                // 请求正常完成
            case <-ctx.Done():
                // 超时
                http.Error(w, "Request timeout", http.StatusRequestTimeout)
            }
        })
    }
}

// responseRecorder 响应记录器
type responseRecorder struct {
    http.ResponseWriter
    statusCode int
}

func (rr *responseRecorder) WriteHeader(code int) {
    rr.statusCode = code
    rr.ResponseWriter.WriteHeader(code)
}
```

### 依赖注入模式

#### 服务容器
```go
package di

import (
    "fmt"
    "reflect"
    "sync"
)

// Container 依赖容器
type Container struct {
    services map[string]interface{}
    factories map[string]func(*Container) (interface{}, error)
    mutex    sync.RWMutex
}

func NewContainer() *Container {
    return &Container{
        services:  make(map[string]interface{}),
        factories: make(map[string]func(*Container) (interface{}, error)),
    }
}

// Register 注册服务工厂
func (c *Container) Register(name string, factory func(*Container) (interface{}, error)) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.factories[name] = factory
}

// RegisterSingleton 注册单例服务
func (c *Container) RegisterSingleton(name string, factory func(*Container) (interface{}, error)) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    
    var instance interface{}
    var once sync.Once
    
    c.factories[name] = func(container *Container) (interface{}, error) {
        var err error
        once.Do(func() {
            instance, err = factory(container)
        })
        return instance, err
    }
}

// Resolve 解析服务
func (c *Container) Resolve(name string) (interface{}, error) {
    c.mutex.RLock()
    factory, exists := c.factories[name]
    c.mutex.RUnlock()
    
    if !exists {
        return nil, fmt.Errorf("service %s not found", name)
    }
    
    return factory(c)
}

// AutoInject 自动注入
func (c *Container) AutoInject(target interface{}) error {
    targetValue := reflect.ValueOf(target)
    if targetValue.Kind() != reflect.Ptr || targetValue.IsNil() {
        return fmt.Errorf("target must be a non-nil pointer")
    }
    
    targetValue = targetValue.Elem()
    targetType := targetValue.Type()
    
    for i := 0; i < targetType.NumField(); i++ {
        field := targetType.Field(i)
        fieldTag := field.Tag.Get("inject")
        
        if fieldTag != "" {
            service, err := c.Resolve(fieldTag)
            if err != nil {
                return fmt.Errorf("failed to inject %s: %w", fieldTag, err)
            }
            
            fieldValue := targetValue.Field(i)
            if fieldValue.CanSet() {
                fieldValue.Set(reflect.ValueOf(service))
            }
        }
    }
    
    return nil
}
```

## 参考资源

### 官方文档
- [Go Documentation](https://golang.org/doc/)
- [Effective Go](https://golang.org/doc/effective_go.html)
- [Go Memory Model](https://golang.org/ref/mem)

### 设计模式资源
- [Design Patterns in Go](https://github.com/tmrts/go-patterns)
- [Go Design Patterns](https://github.com/lukechampine/go-design-patterns)
- [Clean Architecture in Go](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

### 并发编程
- [Concurrency in Go](https://blog.golang.org/concurrency-is-not-parallelism)
- [Go Concurrency Patterns](https://blog.golang.org/pipelines)
- [Advanced Go Concurrency](https://github.com/golang/go/wiki/LockOSThread)

### 性能优化
- [Go Performance](https://golang.org/pkg/runtime/pprof/)
- [Go Profiling](https://golang.org/pkg/net/http/pprof/)
- [High Performance Go](https://www.ardanlabs.com/blog/2014/01/high-performance-go-workshop-part-1.html)

### Web开发
- [Go Web Programming](https://github.com/astaxie/build-web-application-with-golang)
- [Go Web Examples](https://gowebexamples.com/)
- [Go Microservices](https://microservices.io/patterns/languages/go.html)

### 社区资源
- [Go by Example](https://gobyexample.com/)
- [Awesome Go](https://github.com/avelino/awesome-go)
- [Go Resources](https://golang.org/help/)
