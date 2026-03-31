# Iterator Pattern - 完整参考实现

## Java实现 - 自定义集合迭代器 (120行)

```java
package com.example.iterator;

// 迭代器接口
public interface Iterator<T> {
    boolean hasNext();
    T next();
    void remove();
}

// 集合接口
public interface Iterable<T> {
    Iterator<T> iterator();
}

// 自定义集合
public class MyList<T> implements Iterable<T> {
    private T[] items;
    private int size = 0;
    private static final int DEFAULT_CAPACITY = 10;
    
    @SuppressWarnings("unchecked")
    public MyList() {
        items = (T[]) new Object[DEFAULT_CAPACITY];
    }
    
    public void add(T item) {
        if (size == items.length) {
            ensureCapacity();
        }
        items[size++] = item;
    }
    
    @SuppressWarnings("unchecked")
    private void ensureCapacity() {
        T[] newItems = (T[]) new Object[items.length * 2];
        System.arraycopy(items, 0, newItems, 0, size);
        items = newItems;
    }
    
    public T get(int index) {
        if (index >= size) throw new IndexOutOfBoundsException();
        return items[index];
    }
    
    public int size() {
        return size;
    }
    
    @Override
    public Iterator<T> iterator() {
        return new MyListIterator();
    }
    
    // 内部迭代器类
    private class MyListIterator implements Iterator<T> {
        private int currentIndex = 0;
        private int lastReturnedIndex = -1;
        private int expectedModCount = 0;
        
        @Override
        public boolean hasNext() {
            checkForComodification();
            return currentIndex < size;
        }
        
        @Override
        public T next() {
            checkForComodification();
            if (!hasNext()) {
                throw new NoSuchElementException("No more elements");
            }
            lastReturnedIndex = currentIndex;
            return items[currentIndex++];
        }
        
        @Override
        public void remove() {
            if (lastReturnedIndex < 0) {
                throw new IllegalStateException("No next() called yet");
            }
            checkForComodification();
            
            // 移除元素
            System.arraycopy(items, lastReturnedIndex + 1, items, lastReturnedIndex, size - lastReturnedIndex - 1);
            size--;
            currentIndex--;
            lastReturnedIndex = -1;
            expectedModCount++;
        }
        
        private void checkForComodification() {
            // 简化版本 - 完整实现中需要实际的modCount
        }
    }
}

// 反向迭代器
public class ReverseIterator<T> implements Iterator<T> {
    private MyList<T> list;
    private int currentIndex;
    
    public ReverseIterator(MyList<T> list) {
        this.list = list;
        this.currentIndex = list.size() - 1;
    }
    
    @Override
    public boolean hasNext() {
        return currentIndex >= 0;
    }
    
    @Override
    public T next() {
        if (!hasNext()) throw new NoSuchElementException();
        return list.get(currentIndex--);
    }
    
    @Override
    public void remove() {
        throw new UnsupportedOperationException("Remove not supported in reverse iteration");
    }
}

// 使用示例
public class Main {
    public static void main(String[] args) {
        MyList<String> list = new MyList<>();
        list.add("Apple");
        list.add("Banana");
        list.add("Cherry");
        
        // 正向迭代
        System.out.println("Forward iteration:");
        Iterator<String> iter = list.iterator();
        while (iter.hasNext()) {
            System.out.println(iter.next());
        }
        
        // 反向迭代
        System.out.println("\nReverse iteration:");
        ReverseIterator<String> revIter = new ReverseIterator<>(list);
        while (revIter.hasNext()) {
            System.out.println(revIter.next());
        }
    }
}
```

---

## Python实现 - 生成器与异步迭代 (115行)

```python
from typing import Iterator, List, Any, AsyncIterator
import asyncio

# 方法1: 生成器 (内部迭代器)
class MyCollection:
    def __init__(self, items: List[Any]):
        self.items = items
    
    def __iter__(self):
        """使用生成器实现迭代"""
        for item in self.items:
            yield item
    
    def reverse_iter(self):
        """反向生成器"""
        for i in range(len(self.items) - 1, -1, -1):
            yield self.items[i]
    
    def filter_iter(self, predicate):
        """条件生成器"""
        for item in self.items:
            if predicate(item):
                yield item

# 方法2: 外部迭代器类
class MyListIterator:
    def __init__(self, items: List[Any]):
        self.items = items
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.items):
            raise StopIteration
        value = self.items[self.index]
        self.index += 1
        return value

# 方法3: 树迭代器 (深度优先)
class TreeNode:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children or []
    
    def dfs(self):
        """深度优先遍历 (递归生成器)"""
        yield self.value
        for child in self.children:
            yield from child.dfs()
    
    def bfs(self):
        """广度优先遍历"""
        queue = [self]
        while queue:
            node = queue.pop(0)
            yield node.value
            queue.extend(node.children)

# 方法4: 异步迭代器 (异步生成器)
class AsyncDataFetcher:
    def __init__(self, urls: List[str]):
        self.urls = urls
    
    async def __aiter__(self):
        return self
    
    async def __anext__(self):
        if not self.urls:
            raise StopAsyncIteration
        url = self.urls.pop(0)
        # 模拟异步HTTP请求
        await asyncio.sleep(0.1)
        return f"Data from {url}"

# 异步生成器
async def fetch_data_async(urls: List[str]):
    """异步生成器"""
    for url in urls:
        await asyncio.sleep(0.1)  # 模拟I/O
        yield f"Fetched: {url}"

# 使用示例
if __name__ == "__main__":
    # 基本迭代
    coll = MyCollection([1, 2, 3, 4, 5])
    print("Forward:", list(coll))
    print("Reverse:", list(coll.reverse_iter()))
    print("Even only:", list(coll.filter_iter(lambda x: x % 2 == 0)))
    
    # 树迭代
    tree = TreeNode(1, [
        TreeNode(2, [TreeNode(4), TreeNode(5)]),
        TreeNode(3, [TreeNode(6)])
    ])
    print("\nDFS:", list(tree.dfs()))
    print("BFS:", list(tree.bfs()))
    
    # 异步迭代
    async def main():
        async for data in fetch_data_async(['url1', 'url2', 'url3']):
            print(data)
    
    asyncio.run(main())
```

---

## TypeScript实现 - 异步迭代器与流处理 (110行)

```typescript
// 基础迭代器接口
interface IIterator<T> {
    hasNext(): boolean;
    next(): T;
}

interface IIterable<T> {
    [Symbol.iterator](): IIterator<T>;
}

// 自定义列表与迭代器
class MyList<T> implements IIterable<T> {
    private items: T[] = [];
    
    add(item: T): void {
        this.items.push(item);
    }
    
    [Symbol.iterator](): IIterator<T> {
        return new MyListIterator(this.items);
    }
    
    // 反向迭代器
    reverseIterator(): IIterator<T> {
        return new ReverseListIterator(this.items);
    }
    
    // 筛选迭代器
    filterIterator(predicate: (item: T) => boolean): IIterator<T> {
        return new FilterIterator(this.items, predicate);
    }
}

// 前向迭代器
class MyListIterator<T> implements IIterator<T> {
    private index = 0;
    
    constructor(private items: T[]) {}
    
    hasNext(): boolean {
        return this.index < this.items.length;
    }
    
    next(): T {
        if (!this.hasNext()) {
            throw new Error('NoSuchElementException');
        }
        return this.items[this.index++];
    }
}

// 反向迭代器
class ReverseListIterator<T> implements IIterator<T> {
    private index: number;
    
    constructor(private items: T[]) {
        this.index = items.length - 1;
    }
    
    hasNext(): boolean {
        return this.index >= 0;
    }
    
    next(): T {
        if (!this.hasNext()) {
            throw new Error('NoSuchElementException');
        }
        return this.items[this.index--];
    }
}

// 筛选迭代器
class FilterIterator<T> implements IIterator<T> {
    private index = 0;
    
    constructor(
        private items: T[],
        private predicate: (item: T) => boolean
    ) {
        this.advanceToNext();
    }
    
    private advanceToNext(): void {
        while (this.index < this.items.length && !this.predicate(this.items[this.index])) {
            this.index++;
        }
    }
    
    hasNext(): boolean {
        return this.index < this.items.length;
    }
    
    next(): T {
        if (!this.hasNext()) {
            throw new Error('NoSuchElementException');
        }
        const item = this.items[this.index++];
        this.advanceToNext();
        return item;
    }
}

// 树节点与树迭代器
interface TreeNode<T> {
    value: T;
    children: TreeNode<T>[];
}

// 深度优先遍历生成器
function* treeDFS<T>(node: TreeNode<T>): Generator<T> {
    yield node.value;
    for (const child of node.children) {
        yield* treeDFS(child);
    }
}

// 广度优先遍历生成器
function* treeBFS<T>(root: TreeNode<T>): Generator<T> {
    const queue: TreeNode<T>[] = [root];
    while (queue.length > 0) {
        const node = queue.shift()!;
        yield node.value;
        queue.push(...node.children);
    }
}

// 异步迭代器 (异步生成器)
async function* fetchDataAsync(urls: string[]): AsyncGenerator<string> {
    for (const url of urls) {
        await new Promise(resolve => setTimeout(resolve, 100));
        yield `Fetched: ${url}`;
    }
}

// 使用示例
async function main() {
    // 基本迭代
    const list = new MyList<number>();
    [1, 2, 3, 4, 5].forEach(n => list.add(n));
    
    console.log('Forward iteration:');
    for (const item of list) {
        console.log(item);
    }
    
    console.log('\nReverse iteration:');
    const revIter = list.reverseIterator();
    while (revIter.hasNext()) {
        console.log(revIter.next());
    }
    
    console.log('\nFiltered iteration (even only):');
    const filterIter = list.filterIterator(n => n % 2 === 0);
    while (filterIter.hasNext()) {
        console.log(filterIter.next());
    }
    
    // 树迭代
    const tree: TreeNode<number> = {
        value: 1,
        children: [
            { value: 2, children: [{ value: 4, children: [] }, { value: 5, children: [] }] },
            { value: 3, children: [{ value: 6, children: [] }] }
        ]
    };
    
    console.log('\nDFS:', [...treeDFS(tree)]);
    console.log('BFS:', [...treeBFS(tree)]);
    
    // 异步迭代
    console.log('\nAsync fetch:');
    for await (const data of fetchDataAsync(['url1', 'url2', 'url3'])) {
        console.log(data);
    }
}

main().catch(console.error);
```

---

## 单元测试 (80行)

```java
@Test
public void testBasicIteration() {
    MyList<Integer> list = new MyList<>();
    list.add(1); list.add(2); list.add(3);
    
    Iterator<Integer> iter = list.iterator();
    assertEquals(true, iter.hasNext());
    assertEquals(1, iter.next().intValue());
}

@Test
public void testIterationComplete() {
    MyList<String> list = new MyList<>();
    list.add("A"); list.add("B"); list.add("C");
    
    List<String> result = new ArrayList<>();
    for (String item : list) {
        result.add(item);
    }
    
    assertEquals(Arrays.asList("A", "B", "C"), result);
}

@Test(expected = NoSuchElementException.class)
public void testIterationBeyondEnd() {
    MyList<Integer> list = new MyList<>();
    list.add(1);
    
    Iterator<Integer> iter = list.iterator();
    iter.next();
    iter.next(); // Should throw NoSuchElementException
}

@Test
public void testRemoveDuringIteration() {
    MyList<String> list = new MyList<>();
    list.add("A"); list.add("B"); list.add("C");
    
    Iterator<String> iter = list.iterator();
    iter.next();
    iter.remove();
    
    assertEquals(2, list.size());
}

@Test
public void testReverseIteration() {
    MyList<Integer> list = new MyList<>();
    list.add(1); list.add(2); list.add(3);
    
    ReverseIterator<Integer> revIter = new ReverseIterator<>(list);
    assertEquals(3, revIter.next().intValue());
    assertEquals(2, revIter.next().intValue());
    assertEquals(1, revIter.next().intValue());
}

@Test
public void testMultipleIterators() {
    MyList<Integer> list = new MyList<>();
    list.add(1); list.add(2); list.add(3);
    
    Iterator<Integer> iter1 = list.iterator();
    Iterator<Integer> iter2 = list.iterator();
    
    iter1.next();
    assertEquals(1, iter2.next().intValue()); // 独立状态
}

@Test
public void testEmptyListIteration() {
    MyList<String> list = new MyList<>();
    
    Iterator<String> iter = list.iterator();
    assertEquals(false, iter.hasNext());
}
```

---

## 性能对比

| 实现方式 | next()时间 | 内存占用 | 特点 |
|---------|----------|--------|------|
| 数组迭代器 | O(1) | O(1) | 极快，随机访问 |
| 链表迭代器 | O(1) | O(1) | 快速，顺序访问 |
| 树DFS递归 | O(1)摊销 | O(h) | 深度优先，堆栈开销 |
| 树BFS队列 | O(1)摊销 | O(w) | 广度优先，队列开销 |
| 生成器 | O(1)摊销 | O(1) | 极端高效，惰性求值 |
| 异步生成器 | 变长 | 低 | I/O友好，并发 |

---

## 最佳实践

✅ 总是实现hasNext()来检查是否有下一元素
✅ 使用iterator.remove()而不是直接集合修改
✅ 为复杂遍历（树/图）提供多种迭代方式
✅ 生成器优先用于简单遍历（Python）
✅ 异步迭代器用于I/O密集操作
✅ 编写文档说明遍历顺序（DFS/BFS/线性等）
✅ 测试边界情况（空集合、单元素、并发修改）
3. ✅ 实践3

## 参考资源

- SKILL.md - 详细说明
- forms.md - 应用检查清单
- 其他相关模式文档
