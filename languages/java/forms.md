# 现代 Java & Spring Boot 配置审查表单

## 项目基本环境与架构

### Java 里程碑版本 (JDK Version)
- **目标规范**:
  - [ ] Java 8 (长期维护遗留系统，注意垃圾回收与 LocalDate API)
  - [ ] Java 11 (首个模块化后 LTS，引入 HttpClient)
  - [ ] Java 17 (目前最主流企业级 LTS，包含 Sealed Classes, Switch Expression)
  - [ ] Java 21 (最新的前沿 LTS，原生虚拟线程，ZGC 终极进化，首选性能之星)

### 主流框架选型 (Core Frameworks)
- **微服务底座**:
  - [ ] Spring Boot 3.2+ (必须搭配 Java 17 以上)
  - [ ] Spring Boot 2.x (老系统)
  - [ ] Quarkus (专为云原生及 GraalVM 原生镜像 AOT 编译设计的极速框架)
  - [ ] Micronaut (零反射的轻量级框架)
- **数据访问与缓存 (ORM / Cache)**:
  - [ ] MyBatis / MyBatis-Plus (国内全量采用)
  - [ ] Hibernate / Spring Data JPA
  - [ ] Redis (Lettuce / Redisson 分布式锁配置)
  - [ ] Caffeine (本地极速缓存)

## 代码结构与架构规范

### 领域驱动设计 (DDD) 或 传统 MVC 分层
- [ ] Controller (网关接入层，严禁任何业务代码，只处理包装)
- [ ] Application / Service (应用包装层，处理流程编排与事务控制 `@Transactional`)
- [ ] Domain / Entity (核心业务模型，充血模型，禁止使用带有 `@Setter` 的贫血数据)
- [ ] Infrastructure / DAO (防腐层与持久化实现，只做对接)
- **参数传输模型**:
  - [ ] 严格拆分 DTO (外部出入参), BO (内部流转), PO (数据库映射)。禁止直接将实体投递给前端。
  - [ ] Java 14+ 优先选择使用 `record Dto(...)` 替代带有大量 Lombok 注解的 POJO。

### 依赖与 Bean 配置 (@Autowired 验证)
- [ ] 拒绝字段级注入 (`@Autowired` on Object)，全面拥抱构造函数注入 (Constructor Injection)。
- [ ] 确保单例 (Singleton) Bean 中没有非 `final` 的有状态属性 (会导致严重线程安全问题)。

## JVM 垃圾回收与容器化配置

### 内存布局与 GC 参数 (GC Tuning)
- **分配比例与选择**:
  - [ ] `UseG1GC` (Java 9+ 默认)，配置预期停顿参数：`-XX:MaxGCPauseMillis=200`
  - [ ] `UseZGC` (Java 21+ 极限低延迟)，必须打开分代支持：`-XX:+ZGenerational`
- **容器环境 (Docker/K8s) 约束**:
  - [ ] 设置基于容器配额的百分比初始堆和最大堆 (`-XX:InitialRAMPercentage=75.0 -XX:MaxRAMPercentage=75.0`)
  - [ ] 关闭遗留的固定大小 `Xms/Xmx` 参数 (除非是直接部署在虚拟机上)

### 诊断排障开关
- **死亡与转储**:
  - [ ] `-XX:+HeapDumpOnOutOfMemoryError` 开启故障快照 (OOM 时强制生成 .hprof 以便 MAT/JProfiler 分析)
  - [ ] 配置生成转储路径 `-XX:HeapDumpPath=/log/heapdump.hprof`
- **GC 审计**:
  - [ ] JDK 9+ 的统一日志接口 `-Xlog:gc*=info:file=/log/gc.log:time,tags,uptime:filecount=10,filesize=50M`

## 并发与高并发架构检查

### 虚拟线程 (Java 21 Virtual Threads) 与线程池管理
- [ ] 全局替换老旧的 `Executors.newFixedThreadPool(...)`，使用 `Executors.newVirtualThreadPerTaskExecutor()` (如果底层是 Java 21)。
- **防止 Pinning (绑定阻塞)**:
  - [ ] 全文搜索并剔除 `synchronized` 关键字块。涉及持久化 IO 时全部替换为 `ReentrantLock` 结构。
- **自定义 ThreadPoolExecutor**:
  - [ ] (仅针对 Java 8-17) 是否定义了明确的有界队列 (如 `LinkedBlockingQueue(500)`) 以防止无界队列 `Out Of Memory` 问题？
  - [ ] 是否设置了合理的拒绝策略 (`CallerRunsPolicy` 还是抛弃) 及前缀命名工厂 (`ThreadFactory`)？

### 严重漏洞：ThreadLocal 与内存泄漏
- [ ] 确保所有的 `ThreadLocal.set()` 都伴随着 `finally { ThreadLocal.remove() }`。
- [ ] 或在现代系统中升级使用 `Scoped Values` (Java 21+ 规范)。

## Spring Boot 并发安全与异常防护

### 全局错误拦截 (Exception Handling)
- [ ] `@ControllerAdvice` + `@ExceptionHandler` 统一收口返回标准 JSON Code（例如 `Result<T>`）。
- [ ] 禁止将数据库完整的 `SQL Exception` 或 `Stack Trace` 直接暴露到外部 Response 以免产生信息泄漏漏洞。
- [ ] 空气捕获检查：强制所有的 `catch(Exception e)` 必须记入 SLF4J (`log.error("context", e)`)。禁止执行 `catch{}` 放过。

### 事务一致性与锁设计 (@Transactional)
- [ ] 判断 `@Transactional` 是否使用了 `rollbackFor = Exception.class`，否则非运行时异常将不会回滚。
- [ ] 判断锁的粒度是否过大：缓存更新失败、异步短信发送等第三方 RPC 严禁穿杂在大型数据库事务方法内部。它会长期霸占数据库连接池 (Connection Pool) 引发雪崩。
- [ ] 幂等性校验 (分布式锁 Redisson 的使用是否释放正常？)

## 测试与静态源码分析 (CI/CD)

### 扫描策略 (SonarQube 集成)
- [ ] SpotBugs (用于捕捉常见的并发编程恶行，如非最终常量的静态共享、错误重组 `equals`/`hashCode`)
- [ ] PMD (提供复杂的类设计度量)
- [ ] Checkstyle (统一全团队大中小括号与空行缩进规范，通常配置在 Maven Plugin 中，不符合规范即无法通过编译)

### 单元全链路测试框架
- [ ] 支持 JUnit 5 的自动环境注入，并禁用 JUnit 4 原有的 `@RunWith`，替代为 `@ExtendWith(SpringExtension.class)`。
- [ ] 基于 Mockito (`@MockBean`) 将不相关的 RPC/DB 调用截断隔离测试核心业务逻辑算法。
- [ ] 如果使用内存型 DB 进行联调，选择 Testcontainers 拉起真正的 PostgreSQL/MySQL 镜像，而不是具有明显版本特性差异的 H2。
