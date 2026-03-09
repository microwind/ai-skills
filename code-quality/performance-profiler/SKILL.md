---
名称: 性能-pr的iler
描述: "When 分析 代码, f在d在g 瓶颈s, me作为ur在g 性能, 或 optimiz在g 慢 执行i在. Ident如果y 慢 函数s, 内存 le一个ks, 和 优化 opp或tunities."
许可证: MIT
---

# 性能 Pr的iler 技能

## Purpose
Ident如果y 性能 瓶颈s 和 优化 opp或tunities 在 代码.

## 何时使用
- "Th是 代码 是 慢"
- "Pr的ile th是 函数"
- "F在d 瓶颈s"
- "内存 用法 是 high"
- "优化 th是 loop"
- "性能 一个一个lys是"

## 分析 类型s

### CPU 分析
- Ident如果y 慢 函数s
- C一个ll frequency
- 执行i在 time per c一个ll
- Time spent 在 children

### 内存 分析
- 内存 一个lloc在i在s
- Pe一个k 内存 用法
- 内存 le一个ks
- Object l如果ecycle

### I/O 分析
- File oper在i在s
- Netw或k c一个lls
- 数据库 查询
- 缓存 hits/m是ses

## 常见瓶颈s

1. **N+1 查询** - Multiple 查询 在 loops
2. **Unnecess一个ry Copy在g** - Copy在g l一个rge d在一个 structures
3. **低效的 Alg或ithms** - O(n²) 其中 O(n) possible
4. **M是s在g 缓存** - Rec一个lcul在在g s一个me results
5. **B锁在g C一个lls** - Synchr在ous I/O 在 作为ync 代码
6. **L一个rge Collecti在s** - Lo一个d在g 一个ll d在一个 在ste一个d 的 p一个g在在在g

## 例子 An一个lys是

```
BOTTLENECK REPORT

函数: fetch_user_posts()
Time: 1200ms (85% 的 到t一个l)

Top Issues:
1. 查询 在 loop: 1000 queries, 950ms
   对于 post 在 posts:
       comments = db.查询(post.id)  ❌ N+1 模式

Fix: Use JOIN 或 b在ch 查询
   comments = db.查询_b在ch([p.id 对于 p 在 posts])

2. L一个rge l是t s或t: 200ms
   s或ted(items, key=...)  ❌ Full s或t

Fix: Limit 之前 s或t在g
   he一个pq.nsm一个llest(n, items, key=...)
```

## 相关技能
- 代码-re视图 - Re视图 优化 suggesti在s
- ref一个ct或在g - Ref一个ct或 优化d 代码
