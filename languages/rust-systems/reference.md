# Rust系统编程参考文档

## Rust语言特性

### 核心特性
Rust是一门系统编程语言，具有以下核心特性：
- **内存安全**: 通过所有权系统和借用检查器保证内存安全
- **零成本抽象**: 高级抽象在运行时没有额外开销
- **并发安全**: 编译时防止数据竞争
- **性能**: 与C/C++相媲美的性能
- **类型安全**: 强类型系统和类型推导

### 所有权系统
```rust
// 所有权基本规则
fn main() {
    // 1. 每个值都有一个所有者
    let s1 = String::from("hello");
    let s2 = s1; // s1的所有权移动到s2
    // println!("{}", s1); // 编译错误：s1不再有效
    
    // 2. 只能有一个所有者
    let s3 = s2.clone(); // 深拷贝
    println!("{}", s2); // s2仍然有效
    println!("{}", s3); // s3也有效
    
    // 3. 所有者离开作用域时值被丢弃
    {
        let s4 = String::from("world");
    } // s4在这里被丢弃
}

// 函数中的所有权转移
fn takes_ownership(some_string: String) {
    println!("{}", some_string);
} // some_string在这里被丢弃

fn gives_ownership() -> String {
    let some_string = String::from("yours");
    some_string // 返回值所有权转移给调用者
}

fn main() {
    let s1 = String::from("hello");
    takes_ownership(s1); // s1的所有权被转移
    
    let s2 = gives_ownership(); // s2获得所有权
}
```

### 借用与引用
```rust
// 不可变借用
fn calculate_length(s: &String) -> usize {
    s.len()
} // s离开作用域，但没有所有权，所以不会丢弃

// 可变借用
fn change(some_string: &mut String) {
    some_string.push_str(", world");
}

fn main() {
    let mut s1 = String::from("hello");
    
    let len = calculate_length(&s1); // 不可变借用
    println!("Length of '{}' is {}.", s1, len);
    
    change(&mut s1); // 可变借用
    println!("{}", s1);
}

// 借用规则
fn borrowing_rules() {
    let mut s = String::from("hello");
    
    // 可以有多个不可变借用
    let r1 = &s;
    let r2 = &s;
    println!("{} and {}", r1, r2);
    
    // 只能有一个可变借用
    let r3 = &mut s;
    println!("{}", r3);
    
    // 不可变借用和可变借用不能同时存在
    // let r4 = &s; // 错误
    // let r5 = &mut s; // 错误
}
```

## 内存管理

### 智能指针

#### Box<T>
```rust
// Box用于在堆上分配内存
fn box_example() {
    let b = Box::new(5);
    println!("b = {}", b);
} // b在这里被自动释放

// 递归类型需要Box
enum List {
    Cons(i32, Box<List>),
    Nil,
}

use List::{Cons, Nil};

fn recursive_type_example() {
    let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));
}
```

#### Rc<T> 和 Arc<T>
```rust
use std::rc::Rc;

// Rc用于共享所有权（单线程）
fn rc_example() {
    let a = Rc::new(Cons(5, Rc::new(Cons(10, Rc::new(Nil)))));
    println!("count after creating a = {}", Rc::strong_count(&a));
    
    let b = Cons(3, Rc::clone(&a));
    println!("count after creating b = {}", Rc::strong_count(&a));
    
    {
        let c = Cons(4, Rc::clone(&a));
        println!("count after creating c = {}", Rc::strong_count(&a));
        println!("count after c goes out of scope = {}", Rc::strong_count(&a));
    }
}

use std::sync::Arc;
use std::thread;

// Arc用于跨线程共享所有权
fn arc_example() {
    let a = Arc::new(Cons(5, Arc::new(Cons(10, Arc::new(Nil)))));
    
    let mut handles = vec![];
    
    for _ in 0..10 {
        let a = Arc::clone(&a);
        let handle = thread::spawn(move || {
            println!("count = {}", Arc::strong_count(&a));
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}
```

#### Cell<T> 和 RefCell<T>
```rust
use std::cell::RefCell;

// Cell用于内部可变性（Copy类型）
fn cell_example() {
    let c = Cell::new(5);
    println!("c = {}", c.get());
    c.set(10);
    println!("c = {}", c.get());
}

// RefCell用于运行时借用检查
#[derive(Debug)]
struct Messenger {
    messages: RefCell<Vec<String>>,
}

impl Messenger {
    fn new() -> Messenger {
        Messenger {
            messages: RefCell::new(vec![]),
        }
    }
    
    fn send(&self, message: &str) {
        self.messages.borrow_mut().push(String::from(message));
    }
    
    fn get_messages(&self) -> Vec<String> {
        self.messages.borrow().clone()
    }
}

fn refcell_example() {
    let messenger = Messenger::new();
    messenger.send("Hello");
    messenger.send("World");
    
    for message in messenger.get_messages() {
        println!("{}", message);
    }
}
```

### 生命周期

#### 生命周期标注
```rust
// 显式生命周期标注
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

// 结构体中的生命周期
struct ImportantExcerpt<'a> {
    part: &'a str,
}

impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 {
        3
    }
    
    fn announce_and_return_part<'b>(&self, announcement: &'b str) -> &'b str
    where
        'a: 'b, // 'a至少和'b一样长
    {
        println!("Attention please: {}", announcement);
        self.part
    }
}

// 生命周期省略规则
fn first_word(s: &str) -> &str {
    // 等价于: fn first_word<'a>(s: &'a str) -> &'a str
    let bytes = s.as_bytes();
    
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    
    &s[..]
}

// 静态生命周期
static STATIC_STR: &str = "I have a static lifetime";

fn static_lifetime_example() -> &'static str {
    STATIC_STR
}
```

## 并发编程

### 线程

#### 基础线程使用
```rust
use std::thread;
use std::time::Duration;

fn basic_thread() {
    let handle = thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {} from the spawned thread!", i);
            thread::sleep(Duration::from_millis(1));
        }
    });
    
    for i in 1..5 {
        println!("hi number {} from the main thread!", i);
        thread::sleep(Duration::from_millis(1));
    }
    
    handle.join().unwrap();
}

// 使用move闭包
fn move_closure_thread() {
    let v = vec![1, 2, 3];
    
    let handle = thread::spawn(move || {
        println!("Here's a vector: {:?}", v);
    });
    
    handle.join().unwrap();
    // println!("{:?}", v); // 错误：v已被移动
}
```

#### 通道通信
```rust
use std::sync::mpsc;
use std::thread;

fn channel_example() {
    let (tx, rx) = mpsc::channel();
    
    thread::spawn(move || {
        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("thread"),
        ];
        
        for val in vals {
            tx.send(val).unwrap();
            thread::sleep(Duration::from_millis(1));
        }
    });
    
    for received in rx {
        println!("Got: {}", received);
    }
}

// 多生产者单消费者
fn multiple_producers() {
    let (tx, rx) = mpsc::channel();
    
    let tx1 = tx.clone();
    thread::spawn(move || {
        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("thread"),
        ];
        
        for val in vals {
            tx1.send(val).unwrap();
            thread::sleep(Duration::from_millis(1));
        }
    });
    
    thread::spawn(move || {
        let vals = vec![
            String::from("more"),
            String::from("messages"),
            String::from("for"),
            String::from("you"),
        ];
        
        for val in vals {
            tx.send(val).unwrap();
            thread::sleep(Duration::from_millis(1));
        }
    });
    
    for received in rx {
        println!("Got: {}", received);
    }
}
```

### 共享状态

#### Mutex和Arc
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn mutex_arc_example() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    
    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("Result: {}", *counter.lock().unwrap());
}

// 死锁示例
fn deadlock_example() {
    let data = Mutex::new(0);
    
    {
        let mut d = data.lock().unwrap();
        *d = 1;
        // 如果在这里尝试再次锁定，会导致死锁
        // let d2 = data.lock().unwrap(); // 死锁！
    }
    
    println!("Data: {}", *data.lock().unwrap());
}
```

### 原子操作
```rust
use std::sync::atomic::{AtomicI32, Ordering};
use std::sync::Arc;
use std::thread;

fn atomic_example() {
    let counter = Arc::new(AtomicI32::new(0));
    let mut handles = vec![];
    
    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..1000 {
                counter.fetch_add(1, Ordering::Relaxed);
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("Counter: {}", counter.load(Ordering::Relaxed));
}

// 内存顺序
fn memory_ordering_example() {
    use std::sync::atomic::{AtomicBool, Ordering};
    
    static READY: AtomicBool = AtomicBool::new(false);
    static DATA: AtomicI32 = AtomicI32::new(0);
    
    let producer = thread::spawn(|| {
        DATA.store(42, Ordering::Release);
        READY.store(true, Ordering::Release);
    });
    
    let consumer = thread::spawn(|| {
        while !READY.load(Ordering::Acquire) {
            thread::yield_now();
        }
        println!("Data: {}", DATA.load(Ordering::Relaxed));
    });
    
    producer.join().unwrap();
    consumer.join().unwrap();
}
```

## 异步编程

### async/await基础

#### 异步函数
```rust
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};

// 自定义Future
struct SimpleFuture {
    state: i32,
}

impl Future for SimpleFuture {
    type Output = i32;
    
    fn poll(mut self: Pin<&mut Self>, _cx: &mut Context) -> Poll<Self::Output> {
        if self.state < 10 {
            self.state += 1;
            Poll::Pending
        } else {
            Poll::Ready(self.state)
        }
    }
}

// 使用async/await
async fn async_function() -> i32 {
    let mut sum = 0;
    for i in 1..=10 {
        sum += i;
    }
    sum
}

async fn async_example() {
    let result = async_function().await;
    println!("Result: {}", result);
}
```

#### Tokio运行时
```rust
use tokio::time::{sleep, Duration};

async fn tokio_example() {
    println!("Hello");
    sleep(Duration::from_secs(1)).await;
    println!("World");
}

#[tokio::main]
async fn main() {
    tokio_example().await;
}

// 并发任务
async fn concurrent_tasks() {
    let task1 = async {
        sleep(Duration::from_secs(1)).await;
        "Task 1 completed"
    };
    
    let task2 = async {
        sleep(Duration::from_secs(2)).await;
        "Task 2 completed"
    };
    
    tokio::join!(task1, task2);
}
```

### 异步trait
```rust
use async_trait::async_trait;

#[async_trait]
trait AsyncProcessor {
    async fn process(&self, data: &str) -> String;
}

struct MyProcessor;

#[async_trait]
impl AsyncProcessor for MyProcessor {
    async fn process(&self, data: &str) -> String {
        format!("Processed: {}", data)
    }
}

async fn trait_example() {
    let processor = MyProcessor;
    let result = processor.process("Hello").await;
    println!("{}", result);
}
```

## 错误处理

### Result和Option

#### Result类型
```rust
use std::fs::File;
use std::io::{self, Read};

// 基本Result使用
fn read_file_contents() -> Result<String, io::Error> {
    let mut f = File::open("hello.txt")?;
    let mut contents = String::new();
    f.read_to_string(&mut contents)?;
    Ok(contents)
}

// 自定义错误类型
#[derive(Debug)]
enum AppError {
    Io(io::Error),
    Parse(std::num::ParseIntError),
}

impl From<io::Error> for AppError {
    fn from(err: io::Error) -> Self {
        AppError::Io(err)
    }
}

impl From<std::num::ParseIntError> for AppError {
    fn from(err: std::num::ParseIntError) -> Self {
        AppError::Parse(err)
    }
}

fn parse_number(s: &str) -> Result<i32, AppError> {
    let num: i32 = s.parse()?;
    Ok(num)
}

// 使用?操作符
fn chain_operations() -> Result<(), AppError> {
    let contents = read_file_contents()?;
    let number = parse_number(&contents)?;
    println!("Number: {}", number);
    Ok(())
}
```

#### Option类型
```rust
// Option基本使用
fn find_first_even(numbers: &[i32]) -> Option<i32> {
    for &num in numbers {
        if num % 2 == 0 {
            return Some(num);
        }
    }
    None
}

// Option链式操作
fn option_chain_example() {
    let numbers = vec![1, 3, 5, 7];
    let result = find_first_even(&numbers)
        .map(|n| n * 2)
        .filter(|&n| n > 10)
        .unwrap_or(0);
    
    println!("Result: {}", result);
}

// Option和Result的组合
fn combine_option_result() -> Result<i32, String> {
    let opt_num = find_first_even(&[2, 4, 6]);
    
    match opt_num {
        Some(num) => Ok(num),
        None => Err("No even number found".to_string()),
    }
}
```

### 错误处理库

#### thiserror
```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum MyError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Parse error: {0}")]
    Parse(#[from] std::num::ParseIntError),
    
    #[error("Custom error: {message}")]
    Custom { message: String },
    
    #[error("Validation error: {field} is invalid")]
    Validation { field: String },
}

fn thiserror_example() -> Result<(), MyError> {
    let content = std::fs::read_to_string("config.txt")?;
    let number: i32 = content.parse()?;
    
    if number < 0 {
        return Err(MyError::Validation {
            field: "number".to_string(),
        });
    }
    
    Ok(())
}
```

#### anyhow
```rust
use anyhow::{Context, Result};

fn anyhow_example() -> Result<()> {
    let content = std::fs::read_to_string("config.txt")
        .context("Failed to read configuration file")?;
    
    let number: i32 = content.parse()
        .context("Failed to parse configuration as number")?;
    
    if number < 0 {
        anyhow::bail!("Number must be positive, got {}", number);
    }
    
    Ok(())
}

// 错误链
fn error_chain_example() -> Result<()> {
    anyhow_example()
        .context("Failed to process configuration")?;
    Ok(())
}
```

## 系统编程

### 文件系统操作

#### 基本文件操作
```rust
use std::fs::{self, File, OpenOptions};
use std::io::{self, Read, Write, BufReader, BufWriter};
use std::path::Path;

// 读取文件
fn read_file<P: AsRef<Path>>(path: P) -> io::Result<String> {
    fs::read_to_string(path)
}

// 写入文件
fn write_file<P: AsRef<Path>>(path: P, content: &str) -> io::Result<()> {
    fs::write(path, content)
}

// 缓冲读写
fn buffered_io_example() -> io::Result<()> {
    // 写入
    let file = File::create("output.txt")?;
    let mut writer = BufWriter::new(file);
    writer.write_all(b"Hello, ")?;
    writer.write_all(b"World!")?;
    writer.flush()?;
    
    // 读取
    let file = File::open("output.txt")?;
    let mut reader = BufReader::new(file);
    let mut contents = String::new();
    reader.read_to_string(&mut contents)?;
    
    println!("Contents: {}", contents);
    Ok(())
}

// 文件元数据
fn file_metadata<P: AsRef<Path>>(path: P) -> io::Result<()> {
    let metadata = fs::metadata(path)?;
    
    println!("File size: {} bytes", metadata.len());
    println!("Is file: {}", metadata.is_file());
    println!("Is directory: {}", metadata.is_dir());
    
    if let Ok(modified) = metadata.modified() {
        println!("Last modified: {:?}", modified);
    }
    
    Ok(())
}
```

#### 目录操作
```rust
use std::fs;

fn directory_operations() -> io::Result<()> {
    // 创建目录
    fs::create_dir("test_dir")?;
    fs::create_dir_all("test_dir/subdir1/subdir2")?;
    
    // 读取目录
    let entries = fs::read_dir(".")?;
    for entry in entries {
        let entry = entry?;
        let path = entry.path();
        
        if path.is_dir() {
            println!("Directory: {:?}", path);
        } else {
            println!("File: {:?}", path);
        }
    }
    
    // 删除目录
    fs::remove_dir("test_dir")?;
    fs::remove_dir_all("test_dir")?;
    
    Ok(())
}

// 文件监控
use notify::{Watcher, RecursiveMode, watcher, Config};

fn file_watcher_example() -> notify::Result<()> {
    let (tx, rx) = std::sync::mpsc::channel();
    
    let mut watcher = watcher(tx, Config::default())?;
    watcher.watch(".", RecursiveMode::Recursive)?;
    
    while let Ok(event) = rx.recv() {
        println!("{:?}", event);
    }
    
    Ok(())
}
```

### 网络编程

#### TCP服务器
```rust
use std::net::{TcpListener, TcpStream};
use std::io::{Read, Write};
use std::thread;

fn tcp_server() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080")?;
    
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                thread::spawn(|| {
                    handle_client(stream);
                });
            }
            Err(e) => {
                eprintln!("Error accepting connection: {}", e);
            }
        }
    }
    
    Ok(())
}

fn handle_client(mut stream: TcpStream) {
    let mut buffer = [0; 1024];
    
    match stream.read(&mut buffer) {
        Ok(size) => {
            let request = String::from_utf8_lossy(&buffer[..size]);
            println!("Received: {}", request);
            
            let response = "HTTP/1.1 200 OK\r\n\r\nHello, World!";
            stream.write_all(response.as_bytes()).unwrap();
        }
        Err(e) => {
            eprintln!("Error reading from client: {}", e);
        }
    }
}
```

#### 异步网络编程
```rust
use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn async_tcp_server() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    
    loop {
        let (socket, addr) = listener.accept().await?;
        tokio::spawn(async move {
            handle_async_client(socket, addr).await;
        });
    }
}

async fn handle_async_client(mut socket: TcpStream, addr: std::net::SocketAddr) {
    let mut buffer = [0; 1024];
    
    match socket.read(&mut buffer).await {
        Ok(size) => {
            let request = String::from_utf8_lossy(&buffer[..size]);
            println!("Received from {}: {}", addr, request);
            
            let response = "HTTP/1.1 200 OK\r\n\r\nHello, Async World!";
            socket.write_all(response.as_bytes()).await.unwrap();
        }
        Err(e) => {
            eprintln!("Error reading from {}: {}", addr, e);
        }
    }
}
```

## 嵌入式开发

### no_std环境

#### 基础no_std程序
```rust
#![no_std]
#![no_main]

use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

#[no_mangle]
pub extern "C" fn _start() -> ! {
    // 嵌入式程序入口点
    loop {}
}
```

#### 硬件抽象层
```rust
// 简单的GPIO抽象
pub trait Gpio {
    fn set_high(&self);
    fn set_low(&self);
    fn is_high(&self) -> bool;
}

struct LedPin;

impl Gpio for LedPin {
    fn set_high(&self) {
        // 硬件特定的LED开启代码
    }
    
    fn set_low(&self) {
        // 硬件特定的LED关闭代码
    }
    
    fn is_high(&self) -> bool {
        // 读取LED状态
        true
    }
}

// 延迟抽象
pub trait Delay {
    fn delay_ms(&mut self, ms: u32);
}

struct SimpleDelay;

impl Delay for SimpleDelay {
    fn delay_ms(&mut self, ms: u32) {
        // 简单的延迟实现
        for _ in 0..ms * 1000 {
            // 空操作循环
        }
    }
}
```

### 中断处理

#### 中断向量表
```rust
use cortex_m_rt::entry;

#[entry]
fn main() -> ! {
    // 初始化代码
    init();
    
    // 主循环
    loop {
        // 主程序逻辑
    }
}

fn init() {
    // 硬件初始化
}

// 中断处理函数
#[cortex_m_rt::interrupt]
fn EXTI0() {
    // 外部中断0处理
}

#[cortex_m_rt::interrupt]
fn TIM2() {
    // 定时器2中断处理
}
```

## 性能优化

### 编译优化

#### 编译配置
```toml
# Cargo.toml
[profile.dev]
opt-level = 0
debug = true
overflow-checks = true

[profile.release]
opt-level = 3
debug = false
lto = true
codegen-units = 1
panic = "abort"

[profile.bench]
opt-level = 3
debug = false
lto = true
```

#### 内联函数
```rust
#[inline]
fn inline_function(x: i32) -> i32 {
    x * 2 + 1
}

#[inline(always)]
fn always_inline_function(x: i32) -> i32 {
    x * 2 + 1
}

#[inline(never)]
fn never_inline_function(x: i32) -> i32 {
    // 复杂计算，不应该内联
    let mut result = x;
    for i in 0..1000 {
        result = result.wrapping_mul(i);
    }
    result
}
```

### 零拷贝优化

#### 切片和引用
```rust
// 避免不必要的拷贝
fn process_data(data: &[u8]) -> usize {
    data.len()
}

fn zero_copy_example() {
    let data = vec![1, 2, 3, 4, 5];
    let length = process_data(&data); // 传递引用而不是拷贝
    println!("Length: {}", length);
}

// 字符串切片
fn process_string(s: &str) -> &str {
    &s[..5] // 返回切片而不是新字符串
}
```

#### Cow类型
```rust
use std::borrow::Cow;

fn cow_example(input: &str) -> Cow<str> {
    if input.contains("world") {
        // 需要修改，返回拥有值
        let mut modified = input.to_string();
        modified.push_str("!");
        Cow::Owned(modified)
    } else {
        // 不需要修改，返回借用
        Cow::Borrowed(input)
    }
}
```

## 测试

### 单元测试

#### 基础测试
```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_addition() {
        assert_eq!(2 + 2, 4);
    }
    
    #[test]
    fn test_panic() {
        panic!("This test will fail");
    }
    
    #[test]
    #[should_panic(expected = "Expected error")]
    fn test_expected_panic() {
        panic!("Expected error");
    }
    
    #[test]
    fn test_result() -> Result<(), String> {
        if 2 + 2 != 4 {
            Err(String::from("Two plus two must equal four"))
        } else {
            Ok(())
        }
    }
}
```

#### 参数化测试
```rust
use rstest::rstest;

#[rstest]
#[case(2, 4)]
#[case(3, 9)]
#[case(4, 16)]
fn test_square(#[case] input: i32, #[case] expected: i32) {
    assert_eq!(input * input, expected);
}

#[rstest]
fn test_multiple_cases(
    #[values(1, 2, 3)] a: i32,
    #[values(4, 5, 6)] b: i32,
) {
    assert!(a + b > 0);
}
```

### 集成测试

#### 集成测试示例
```rust
// tests/integration_test.rs
use my_crate::add;

#[test]
fn test_add_integration() {
    assert_eq!(add(2, 3), 5);
}

#[test]
fn test_add_negative() {
    assert_eq!(add(-2, 3), 1);
}
```

### 基准测试

#### Criterion基准测试
```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 1,
        1 => 1,
        n => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

fn criterion_benchmark(c: &mut Criterion) {
    c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
```

## 参考资源

### 官方文档
- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [Rust Reference](https://doc.rust-lang.org/reference/)
- [Rust Standard Library](https://doc.rust-lang.org/std/)

### 系统编程资源
- [Rust Embedded Book](https://docs.rust-embedded.org/book/)
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/)
- [Rust Async Book](https://rust-lang.github.io/async-book/)
- [Tokio Documentation](https://tokio.rs/docs)

### 性能优化
- [Rust Performance Book](https://nnethercote.github.io/perf-book/)
- [Rust Optimizations](https://github.com/jasonwilliams/boa/blob/master/docs/optimizations.md)
- [Criterion Benchmarks](https://bheisler.github.io/criterion.rs/book/)

### 错误处理
- [thiserror Documentation](https://docs.rs/thiserror/)
- [anyhow Documentation](https://docs.rs/anyhow/)
- [Error Handling Guidelines](https://rust-lang.github.io/rust-clippy/master/index.html#error_handling)

### 社区资源
- [Rust Users Forum](https://users.rust-lang.org/)
- [Reddit r/rust](https://www.reddit.com/r/rust/)
- [Rust Blog](https://blog.rust-lang.org/)
- [Awesome Rust](https://github.com/rust-unofficial/awesome-rust)
