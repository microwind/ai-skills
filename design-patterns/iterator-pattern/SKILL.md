---
name: 迭代器模式
description: "顺序访问聚合元素而不暴露结构。在需要遍历集合时使用。"
license: MIT
---

# 迭代器模式 (Iterator Pattern)

## 概述

迭代器模式提供一种方法顺序地访问一个聚合对象中的各个元素，而不需要暴露该对象的底层表示。

**核心原则**: 访问遍历，隐藏结构。

## 何时使用

**始终:**
- 需要遍历集合
- 不想暴露集合结构
- 支持多种遍历方式
- 链表、树、图遍历

**触发短语:**
- "遍历集合"
- "不同遍历方式"
- "隐藏结构"
- "顺序访问"

## 迭代器的优缺点

### 优点 ✅
- 隐藏集合内部结构
- 支持多种遍历方式
- 统一集合访问接口
- 将迭代职责分离

### 缺点 ❌
- 对于简单集合过度设计
- 添加新遍历方式需要新迭代器
- 性能可能有轻微影响

## 实现方式

### 集合遍历
```java
public interface Collection<E> {
    Iterator<E> iterator();
}

public interface Iterator<E> {
    boolean hasNext();
    E next();
}

public class ListCollection<E> implements Collection<E> {
    private List<E> items = new ArrayList<>();
    
    @Override
    public Iterator<E> iterator() {
        return new ListIterator();
    }
    
    private class ListIterator implements Iterator<E> {
        private int index = 0;
        
        @Override
        public boolean hasNext() {
            return index < items.size();
        }
        
        @Override
        public E next() {
            return items.get(index++);
        }
    }
}
```

## 典型应用场景

### 1. Java 集合框架
```java
List<String> list = new ArrayList<>();
Iterator<String> iter = list.iterator();
while (iter.hasNext()) {
    System.out.println(iter.next());
}
```

### 2. 增强 for 循环
```java
for (String item : collection) {
    System.out.println(item);
}
```

### 3. 反向遍历
```java
// 返回 ReverseIterator
Collection<E> reversed = collection.reverseIterator();
```

### 4. 树遍历
```java
// 前序遍历
TreeIterator preOrder = tree.preOrderIterator();
// 中序遍历
TreeIterator inOrder = tree.inOrderIterator();
```

## 最佳实践

1. ✅ Iterator 接口简洁
2. ✅ 支持多种遍历方式
3. ✅ 处理并发修改
4. ✅ 提供 remove() 方法

## Java 迭代器接口

```java
public interface Iterator<E> {
    boolean hasNext();
    E next();
    default void remove() {
        throw new UnsupportedOperationException();
    }
    default void forEachRemaining(Consumer<? super E> action) {
        // 默认实现
    }
}
```

## 何时避免使用

- 只有一种遍历方式
- 集合结构简单
- 直接访问性能关键
