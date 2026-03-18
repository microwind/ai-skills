# 项目 1：Java 用户登录系统

**完整的用户认证系统**：包括登录页面、后台 API、数据库集成。

**技术栈**：Java 17 + Spring Boot 3.x + PostgreSQL + React + TypeScript

---

## 项目概览

完成后你将拥有：

- ✅ 完整的后端 API（登录、注册、Token 刷新、个人资料）
- ✅ React + TypeScript 前端（登录页、个人资料页）
- ✅ PostgreSQL 数据库设计
- ✅ JWT 认证系统
- ✅ 完整的单元和集成测试
- ✅ API 文档（Swagger）

---

## 使用工作流开发

### 推荐工作流

```
需求整理 → 数据库设计 → 后端实现 → 前端实现 → 测试 → 文档
```

### 初始提示词

```bash
$ claude "
我需要用 Java + Spring Boot + PostgreSQL 构建一个用户登录系统。

要求：
1. **后端 API**：
   - POST /api/auth/register - 用户注册
   - POST /api/auth/login - 用户登录
   - POST /api/auth/refresh - 刷新 Token
   - GET /api/auth/profile - 获取用户信息
   - POST /api/auth/logout - 登出

2. **安全要求**：
   - 密码使用 bcrypt 加密
   - JWT token 认证（有效期 15 分钟）
   - 刷新 token（有效期 7 天）
   - 防止 CSRF 攻击

3. **前端页面**：
   - 登录页面（邮箱 + 密码）
   - 个人资料页面
   - 响应式设计

4. **数据库**：
   - User 表（id, email, password_hash, created_at）
   - RefreshToken 表（token, user_id, expires_at）

5. **完整的测试**：
   - 单元测试
   - 集成测试

请按顺序提供：
1. 数据库初始化脚本
2. User 和 RefreshToken 实体类
3. AuthService 和 AuthController
4. JWT Token 工具类
5. 前端登录页面（React + Tailwind）
6. 完整的测试套件
7. API 文档

每个部分包括详细的注释和最佳实践。
"
```

---

## 第一步：数据库设计

### 提示词

```bash
$ claude "
设计 PostgreSQL 数据库：
1. User 表 - 用户信息（包括必要的索引）
2. RefreshToken 表 - Token 管理
3. 添加必要的外键和约束
生成完整的 DDL 脚本
"
```

### 数据库脚本示例

```sql
-- User 表
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_email (email)
);

-- RefreshToken 表
CREATE TABLE refresh_tokens (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token VARCHAR(500) NOT NULL UNIQUE,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_token (token)
);
```

---

## 第二步：后端实体类

### 提示词

```bash
$ claude "
基于数据库设计生成 Spring Boot 实体类：
1. User 实体（JPA）- 包含验证注解
2. RefreshToken 实体（JPA）
3. UserDTO 和 AuthResponse DTO
包括所有必要的注解和方法
"
```

详见 `code/User.java`

---

## 第三步：JWT 工具类

### 提示词

```bash
$ claude "
实现 JWT Token 处理（io.jsonwebtoken:jjwt）：
1. token 生成（包含 user id 和 email）
2. token 验证
3. token 过期时间管理
4. 刷新 token 逻辑

代码要包括完整的异常处理
"
```

详见 `code/JwtTokenProvider.java`

---

## 第四步：认证服务

### 提示词

```bash
$ claude "
实现 AuthService：
- register(RegisterRequest) - 注册
- login(LoginRequest) - 登录，返回 access + refresh token
- refreshToken(RefreshTokenRequest) - 刷新 token
- logout(userId) - 登出
- getProfile(userId) - 获取个人资料

包括完整的验证和错误处理
"
```

详见 `code/AuthService.java`

---

## 第五步：REST API 控制器

### 提示词

```bash
$ claude "
实现 AuthController（Spring REST）：
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh
- POST /api/auth/logout (需要认证)
- GET /api/auth/profile (需要认证)

包括：
- 请求验证
- 完整的异常处理
- HTTP 状态码
- 错误响应格式
"
```

详见 `code/AuthController.java`

---

## 第六步：认证中间件

### 提示词

```bash
$ claude "
实现 JWT 验证中间件：
- 拦截 HTTP 请求
- 验证 Authorization header 中的 token
- 将用户信息放入 SecurityContext
- 处理无效 token 和过期 token

使用 Spring Security
"
```

---

## 第七步：React 前端

### 提示词

```bash
$ claude "
用 React + TypeScript + Tailwind CSS 创建登录页面：
1. 邮箱和密码输入框
2. 登录和注册切换
3. 表单验证和错误提示
4. 记住我复选框
5. 响应式设计（手机/平板/桌面）
6. 加载动画
包括 API 调用逻辑
"
```

详见 `code/LoginPage.tsx`

---

## 第八步：集成测试

### 提示词

```bash
$ claude "
写完整的集成测试（JUnit 5 + MockMvc）：
1. 用户注册流程
2. 用户登录流程
3. Token 刷新流程
4. 登出流程
5. 无效 token 处理
6. 边界情况（重复邮箱、弱密码等）

覆盖率要 >90%
"
```

详见 `code/AuthControllerTest.java`

---

## 第九步：项目配置

### 提示词

```bash
$ claude "
生成 Spring Boot 项目配置：
1. pom.xml - 所有必要的依赖
2. application.yml - 数据库、JWT 配置
3. SecurityConfig - Spring Security 配置
4. 环境变量说明

生产和开发环境都要支持
"
```

---

## 第十步：API 文档

### 提示词

```bash
$ claude "
生成 Swagger/OpenAPI 文档：
1. 所有 API 端点
2. 请求和响应格式
3. 认证要求
4. 错误码说明
5. 使用示例

使用 springdoc-openapi 库
"
```

---

## 快速启动命令

```bash
# 1. 克隆项目
git clone <repo>
cd java-auth-system

# 2. 配置数据库
# 编辑 application.yml

# 3. 运行初始化脚本
psql -U postgres -d auth_db -f schema.sql

# 4. 启动后端
mvn spring-boot:run

# 5. 启动前端（另一个终端）
cd frontend
npm install
npm start

# 6. 访问应用
http://localhost:3000

# 7. 查看 API 文档
http://localhost:8080/swagger-ui.html
```

---

## 项目结构

```
java-auth-system/
├── backend/
│   ├── src/main/java/com/auth
│   │   ├── model/
│   │   │   ├── User.java
│   │   │   └── RefreshToken.java
│   │   ├── repository/
│   │   │   ├── UserRepository.java
│   │   │   └── RefreshTokenRepository.java
│   │   ├── service/
│   │   │   └── AuthService.java
│   │   ├── controller/
│   │   │   └── AuthController.java
│   │   ├── security/
│   │   │   ├── JwtTokenProvider.java
│   │   │   ├── JwtAuthenticationFilter.java
│   │   │   └── SecurityConfig.java
│   │   └── Application.java
│   ├── src/test/java/com/auth
│   │   └── AuthControllerTest.java
│   ├── pom.xml
│   └── application.yml
├── frontend/
│   ├── src/
│   │   ├── pages/LoginPage.tsx
│   │   ├── components/
│   │   ├── services/authService.ts
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
├── database/
│   └── schema.sql
└── README.md
```

---

## 测试运行

```bash
# 运行所有测试
mvn test

# 运行单个测试类
mvn test -Dtest=AuthControllerTest

# 生成覆盖率报告
mvn test jacoco:report

# 查看报告
open target/site/jacoco/index.html
```

---

## 常见问题

**Q：数据库怎么初始化？**
A：运行 `schema.sql` 脚本，或用 Flyway/Liquibase 自动迁移。

**Q：JWT token 过期了怎么办？**
A：用 refresh token 获取新的 access token，无需重新登录。

**Q：密码怎么验证？**
A：使用 bcrypt，永远不存储明文密码。

**Q：如何部署到生产？**
A：打包为 JAR，部署到云平台（AWS、阿里云等）。

---

## 扩展建议

完成后可以继续添加：

1. **权限管理**：不同用户角色和权限
2. **社交登录**：OAuth 支持（Google、GitHub）
3. **邮件验证**：验证邮箱真实性
4. **双因素认证**：增强安全性
5. **用户日志**：记录登录历史
6. **前端缓存**：优化性能

---

## 下一个项目

完成了 Java 项目？试试 Go！

→ [Go 用户登录系统](./02-Go登录系统.md)

---

**现在就开始构建你的认证系统吧！** 🚀

