# Spring Boot参数配置表单

## 项目基本信息
- **项目名称**: _________________________
- **项目版本**: _________________________
- **Java版本**: 
  - [ ] Java 8
  - [ ] Java 11
  - [ ] Java 17
  - [ ] Java 21
- **Spring Boot版本**: _________________________

## 项目配置

### 依赖管理
- **构建工具**:
  - [ ] Maven
  - [ ] Gradle
- **核心依赖**:
  - [ ] spring-boot-starter-web
  - [ ] spring-boot-starter-data-jpa
  - [ ] spring-boot-starter-security
  - [ ] spring-boot-starter-validation
  - [ ] spring-boot-starter-cache
  - [ ] spring-boot-starter-actuator
- **数据库依赖**:
  - [ ] MySQL Connector
  - [ ] PostgreSQL
  - [ ] H2 (内存数据库)
  - [ ] Redis
  - [ ] MongoDB
- **其他依赖**:
  - [ ] Lombok
  - [ ] MapStruct
  - [ ] Swagger/OpenAPI
  - [ ] Testcontainers

### 应用配置
- **服务器配置**:
  - **端口**: ______ (默认8080)
  - **上下文路径**: ______ (默认/)
  - **SSL启用**: [ ] 是 [ ] 否
- **数据库配置**:
  - **URL**: _________________________
  - **用户名**: _________________________
  - **密码**: _________________________
  - **连接池**: HikariCP (默认) [ ] Tomcat JDBC [ ] 其他
- **日志配置**:
  - **日志级别**: 
    - [ ] TRACE
    - [ ] DEBUG
    - [ ] INFO (默认)
    - [ ] WARN
    - [ ] ERROR
  - **日志框架**: Logback (默认) [ ] Log4j2 [ ] 其他

## 架构配置

### 分层架构
- **Controller层**:
  - [ ] @RestController
  - [ ] @RequestMapping
  - [ ] 异常处理
  - [ ] 参数验证
- **Service层**:
  - [ ] @Service
  - [ ] 事务管理 (@Transactional)
  - [ ] 业务逻辑封装
  - [ ] 接口抽象
- **Repository层**:
  - [ ] JpaRepository
  - [ ] 自定义查询
  - [ ] 分页排序
  - [ ] 性能优化

### 配置管理
- **配置文件格式**:
  - [ ] application.properties
  - [ ] application.yml
- **环境配置**:
  - [ ] 开发环境 (dev)
  - [ ] 测试环境 (test)
  - [ ] 生产环境 (prod)
- **外部配置**:
  - [ ] 环境变量
  - [ ] 命令行参数
  - [ ] 配置中心

## 安全配置

### 认证方式
- **认证类型**:
  - [ ] JWT Token
  - [ ] Session
  - [ ] OAuth2
  - [ ] Basic Auth
- **JWT配置**:
  - **密钥**: _________________________
  - **过期时间**: ______ 小时
  - **刷新策略**: [ ] 支持 [ ] 不支持

### 权限控制
- **权限模式**:
  - [ ] 基于角色的访问控制 (RBAC)
  - [ ] 基于资源的访问控制
  - [ ] 方法级安全 (@PreAuthorize)
- **端点保护**:
  - [ ] 公开端点: _________________________
  - [ ] 受保护端点: _________________________

## 数据库配置

### JPA配置
- **DDL策略**:
  - [ ] none (生产环境推荐)
  - [ ] validate
  - [ ] update
  - [ ] create
  - [ ] create-drop
- **SQL方言**:
  - [ ] MySQL5InnoDBDialect
  - [ ] PostgreSQLDialect
  - [ ] H2Dialect
- **显示SQL**: [ ] 是 [ ] 否

### 连接池配置
- **HikariCP设置**:
  - **最大连接数**: ______ (默认10)
  - **最小空闲连接**: ______ (默认10)
  - **连接超时**: ______ ms (默认30000)
  - **空闲超时**: ______ ms (默认600000)

## 缓存配置

### 缓存类型
- **缓存实现**:
  - [ ] Caffeine (本地缓存)
  - [ ] Redis (分布式缓存)
  - [ ] Ehcache
  - [ ] Guava Cache
- **缓存策略**:
  - [ ] 基于TTL过期
  - [ ] 基于LRU淘汰
  - [ ] 手动清理

### 缓存配置
- **默认TTL**: ______ 秒
- **最大大小**: ______ 条目
- **缓存名称**: _________________________

## 监控配置

### Actuator端点
- **启用端点**:
  - [ ] /health (健康检查)
  - [ ] /info (应用信息)
  - [ ] /metrics (指标)
  - [ ] /env (环境信息)
  - [ ] /loggers (日志管理)
  - [ ] /threaddump (线程转储)
- **端点暴露**:
  - [ ] 仅本地访问
  - [ ] 远程访问
  - [ ] 需要认证

### 健康检查
- **检查项目**:
  - [ ] 数据库连接
  - [ ] Redis连接
  - [ ] 外部服务
  - [ ] 磁盘空间
- **自定义健康检查**: [ ] 是 [ ] 否

## 测试配置

### 测试框架
- **单元测试**:
  - [ ] JUnit 5
  - [ ] Mockito
  - [ ] AssertJ
- **集成测试**:
  - [ ] @SpringBootTest
  - [ ] @WebMvcTest
  - [ ] @DataJpaTest
  - [ ] Testcontainers

### 测试配置
- **测试数据库**: 
  - [ ] H2内存数据库
  - [ ] Testcontainers
  - [ ] 独立测试数据库
- **测试环境**:
  - [ ] application-test.properties
  - [ ] @TestPropertySource
  - [ ] 测试配置文件

## 部署配置

### 打包方式
- **打包类型**:
  - [ ] JAR (推荐)
  - [ ] WAR
- **打包工具**:
  - [ ] Maven Package
  - [ ] Gradle Build
  - [ ] Docker镜像

### Docker配置
- **基础镜像**: 
  - [ ] openjdk:8-jre-alpine
  - [ ] openjdk:11-jre-slim
  - [ ] openjdk:17-jre-slim
- **镜像优化**:
  - [ ] 多阶段构建
  - [ ] 层缓存优化
  - [ ] 最小化镜像

## 校验规则

### 必填项检查
- [ ] 项目基本信息已填写
- [ ] 核心依赖已选择
- [ ] 数据库配置已设置
- [ ] 安全配置已定义

### 配置合理性检查
- [ ] Java版本与Spring Boot版本兼容
- [ ] 数据库连接参数正确
- [ ] 安全配置符合要求
- [ ] 生产环境配置合理

### 最佳实践检查
- [ ] 使用了适当的分层架构
- [ ] 配置了日志级别
- [ ] 启用了监控端点
- [ ] 配置了测试环境

## 使用说明

1. **配置顺序**: 按照项目配置 → 架构配置 → 安全配置 → 数据库配置的顺序填写
2. **环境区分**: 不同环境使用不同的配置文件
3. **安全考虑**: 生产环境必须启用安全配置和监控
4. **性能优化**: 根据实际需求调整连接池和缓存配置
5. **测试验证**: 配置完成后运行测试验证功能正常
