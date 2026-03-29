---
name: 观察者模式
description: "定义对象间的一对多关系。在需要事件通知或发布订阅时使用。"
license: MIT
---

# 观察者模式 (Observer Pattern)

## 概述

观察者模式定义了对象间的一对多关系。当一个对象改变状态时，它的所有依赖者都会自动收到通知。

**核心原则**: 发布-订阅，对象通信解耦。

## 何时使用

**始终:**
- 事件处理系统
- MVC 模式更新
- 网页推送通知
- 发布订阅系统
- 属性变更通知

**触发短语:**
- "事件通知"
- "发布-订阅"
- "属性变更"
- "观察者"

## 观察者模式的优缺点

### 优点 ✅
- 发布者和订阅者解耦
- 动态建立联系
- 支持主动通知
- 易于建立通知链

### 缺点 ❌
- 订阅者收到所有消息
- 通知顺序不确定
- 如果观察者处理缓慢会拖累发布者

## 实现方式

### 事件发布者
```java
public class Subject {
    private List<Observer> observers = new ArrayList<>();
    private String state;
    
    public void attach(Observer observer) {
        observers.add(observer);
    }
    
    public void detach(Observer observer) {
        observers.remove(observer);
    }
    
    public void notifyObservers() {
        for (Observer observer : observers) {
            observer.update(this);
        }
    }
    
    public void setState(String state) {
        this.state = state;
        notifyObservers();
    }
}

public interface Observer {
    void update(Subject subject);
}

public class ConcreteObserver implements Observer {
    @Override
    public void update(Subject subject) {
        System.out.println("State changed to " + subject.state);
    }
}
```

## 典型应用场景

### 1. GUI 事件系统
```java
button.addEventListener("click", event -> {
    // 处理点击
});
```

### 2. MVC 框架
```java
// 模型变化通知视图
dataModel.addListener(view);
```

### 3. 异步任务通知
```java
task.addProgressListener(progressBar::update);
```

## 最佳实践

1. ✅ 使用弱引用避免内存泄漏
2. ✅ 提供 add/remove 观察者方法
3. ✅ 异常观察者不影响其他观察者
4. ✅ 文档说明通知顺序和内容

## Java 内置观察者

### Observable/Observer
```java
public class Model extends Observable {
    public void setState(String state) {
        setChanged();
        notifyObservers(state);
    }
}
```

### PropertyChangeListener
```java
bean.addPropertyChangeListener("name", evt -> {
    System.out.println("Name changed to " + evt.getNewValue());
});
```

## 何时避免使用

- 只有一个发布者和订阅者
- 通知关系简单
- 不需要解耦
