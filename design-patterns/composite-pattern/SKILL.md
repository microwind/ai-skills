---
name: 组合模式
description: "将对象组合成树形结构。在需要处理树形结构或递归组合时使用。"
license: MIT
---

# 组合模式 (Composite Pattern)

## 概述

组合模式将对象组合成树形结构以表示"部分-整体"的层级。这个模式让客户端能以统一的方式处理单个对象和组合对象。

**核心原则**: 树形结构，统一处理。

## 何时使用

**始终:**
- 处理树形结构
- 文件系统目录
- UI 组件层级
- 菜单系统
- 组织结构

**触发短语:**
- "树形结构处理"
- "文件夹和文件"
- "组件嵌套"
- "递归结构"

## 组合模式的优缺点

### 优点 ✅
- 统一处理单对象和组合
- 代码简洁
- 易于添加新组件
- 树形结构规范

### 缺点 ❌
- 对象结构变复杂
- 约束规则难以权衡
- 性能可能受影响

## 实现方式

### 文件系统
```java
public abstract class FileSystemElement {
    protected String name;
    
    public abstract long getSize();
    public abstract void display(int indent);
}

public class File extends FileSystemElement {
    private long size;
    
    @Override
    public long getSize() {
        return size;
    }
    
    @Override
    public void display(int indent) {
        System.out.println(" ".repeat(indent) + "File: " + name);
    }
}

public class Directory extends FileSystemElement {
    private List<FileSystemElement> children = new ArrayList<>();
    
    public void add(FileSystemElement element) {
        children.add(element);
    }
    
    @Override
    public long getSize() {
        return children.stream()
            .mapToLong(FileSystemElement::getSize)
            .sum();
    }
    
    @Override
    public void display(int indent) {
        System.out.println(" ".repeat(indent) + "Dir: " + name);
        children.forEach(c -> c.display(indent + 2));
    }
}
```

## 典型应用场景

### 1. UI 组件树
```java
Panel container = new Panel();
container.add(new Button("Click"));
container.add(new TextField());
Panel subPanel = new Panel();
subPanel.add(new CheckBox());
container.add(subPanel);
```

### 2. 权限树
```java
Permission adminPermission = new CompositePermission("admin");
adminPermission.add(new Permission("read"));
adminPermission.add(new Permission("write"));
adminPermission.add(new Permission("delete"));
```

### 3. 企业组织结构
```java
Organization root = new Organization("Company");
root.add(new Department("Engineering"));
root.add(new Department("Sales"));
root.getEmployeeCount();
```

## 最佳实践

1. ✅ 叶子和组合共享接口
2. ✅ 在叶子中实现 add/remove 是否有意义
3. ✅ 支持遍历接口
4. ✅ 避免循环引用

## 何时避免使用

- 结构简单
- 只有单层
- 对象类型差异大
