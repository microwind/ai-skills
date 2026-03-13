---
name: API文档生成与管理
description: "当生成API文档时，分析文档结构，优化文档质量，解决版本同步。验证文档架构，设计自动化流程，和最佳实践。"
license: MIT
---

# API文档生成与管理技能

## 概述

API文档是接口开发的重要组成部分，高质量的文档能够提高开发效率、降低沟通成本、提升用户体验。不当的文档管理会导致信息过时、维护困难、协作效率低下。

**核心原则**: 好的API文档应该准确完整、易于理解、及时更新、自动化生成。坏的文档会导致使用困难、错误频发、维护成本高。

## 何时使用

**始终:**
- 开发RESTful API时
- 设计GraphQL接口时
- 维护微服务架构时
- 对接第三方接口时
- 版本发布管理时
- 团队协作开发时

**触发短语:**
- "如何生成API文档？"
- "文档自动更新"
- "OpenAPI规范"
- "Swagger配置"
- "文档版本管理"
- "接口文档同步"

## API文档生成与管理技能功能

### 文档生成
- OpenAPI/Swagger规范
- 自动化文档生成
- 注解驱动文档
- 代码示例生成
- 交互式文档界面
- 多格式导出

### 文档管理
- 版本控制集成
- 多环境文档
- 文档同步机制
- 变更日志管理
- 权限控制
- 文档发布流程

### 质量保证
- 文档完整性检查
- 示例代码验证
- 接口一致性验证
- 文档格式规范
- 自动化测试
- 质量报告

### 用户体验
- 交互式API测试
- 代码示例生成
- SDK自动生成
- 错误响应说明
- 认证授权指南
- 快速入门教程

## 常见问题

**❌ 文档信息过时**
- 代码变更未同步文档
- 版本发布未更新文档
- 示例代码错误
- 参数说明不准确

**❌ 文档质量差**
- 缺少关键信息
- 描述不清晰
- 示例代码不完整
- 错误处理说明不足

**❌ 维护成本高**
- 手动更新文档
- 多格式同步困难
- 版本管理混乱
- 团队协作低效

**❌ 用户体验差**
- 文档查找困难
- 缺少交互功能
- 示例代码不可用
- 学习曲线陡峭

## 代码示例

### OpenAPI 3.0规范配置

```yaml
# openapi.yaml
openapi: 3.0.3
info:
  title: 用户管理API
  description: 用户注册、登录、信息管理等功能的RESTful API
  version: 1.0.0
  contact:
    name: API支持团队
    email: api-support@example.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.example.com/v1
    description: 生产环境
  - url: https://staging-api.example.com/v1
    description: 测试环境
  - url: http://localhost:3000/v1
    description: 开发环境

tags:
  - name: 用户管理
    description: 用户相关操作
  - name: 认证授权
    description: 登录注册相关

paths:
  /users:
    get:
      tags:
        - 用户管理
      summary: 获取用户列表
      description: 分页获取用户列表，支持搜索和过滤
      operationId: getUsers
      parameters:
        - name: page
          in: query
          description: 页码
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          description: 每页数量
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: search
          in: query
          description: 搜索关键词
          required: false
          schema:
            type: string
      responses:
        '200':
          description: 成功返回用户列表
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      tags:
        - 用户管理
      summary: 创建新用户
      description: 创建新的用户账户
      operationId: createUser
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: 用户创建成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'
        '409':
          description: 用户已存在
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /users/{userId}:
    get:
      tags:
        - 用户管理
      summary: 获取用户详情
      description: 根据用户ID获取详细信息
      operationId: getUserById
      parameters:
        - name: userId
          in: path
          required: true
          description: 用户ID
          schema:
            type: integer
            format: int64
      responses:
        '200':
          description: 成功返回用户信息
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'

    put:
      tags:
        - 用户管理
      summary: 更新用户信息
      description: 更新指定用户的信息
      operationId: updateUser
      parameters:
        - name: userId
          in: path
          required: true
          description: 用户ID
          schema:
            type: integer
            format: int64
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateUserRequest'
      responses:
        '200':
          description: 更新成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'
        '404':
          $ref: '#/components/responses/NotFound'

  /auth/login:
    post:
      tags:
        - 认证授权
      summary: 用户登录
      description: 用户登录获取访问令牌
      operationId: login
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
      responses:
        '200':
          description: 登录成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
        '401':
          description: 登录失败
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
          format: int64
          description: 用户ID
          example: 12345
        username:
          type: string
          description: 用户名
          example: johndoe
        email:
          type: string
          format: email
          description: 邮箱地址
          example: john@example.com
        fullName:
          type: string
          description: 全名
          example: John Doe
        avatar:
          type: string
          format: uri
          description: 头像URL
          example: https://example.com/avatars/john.jpg
        createdAt:
          type: string
          format: date-time
          description: 创建时间
        updatedAt:
          type: string
          format: date-time
          description: 更新时间
      required:
        - id
        - username
        - email
        - fullName

    CreateUserRequest:
      type: object
      properties:
        username:
          type: string
          minLength: 3
          maxLength: 50
          description: 用户名
          example: johndoe
        email:
          type: string
          format: email
          description: 邮箱地址
          example: john@example.com
        password:
          type: string
          minLength: 8
          description: 密码
          example: securePassword123
        fullName:
          type: string
          maxLength: 100
          description: 全名
          example: John Doe
      required:
        - username
        - email
        - password
        - fullName

    UpdateUserRequest:
      type: object
      properties:
        email:
          type: string
          format: email
          description: 邮箱地址
          example: john.new@example.com
        fullName:
          type: string
          maxLength: 100
          description: 全名
          example: John Smith
        avatar:
          type: string
          format: uri
          description: 头像URL
          example: https://example.com/avatars/john-new.jpg

    LoginRequest:
      type: object
      properties:
        username:
          type: string
          description: 用户名或邮箱
          example: johndoe
        password:
          type: string
          description: 密码
          example: securePassword123
      required:
        - username
        - password

    LoginResponse:
      type: object
      properties:
        accessToken:
          type: string
          description: 访问令牌
          example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        refreshToken:
          type: string
          description: 刷新令牌
          example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        expiresIn:
          type: integer
          description: 令牌过期时间(秒)
          example: 3600
        user:
          $ref: '#/components/schemas/User'

    Pagination:
      type: object
      properties:
        page:
          type: integer
          description: 当前页码
          example: 1
        limit:
          type: integer
          description: 每页数量
          example: 20
        total:
          type: integer
          description: 总记录数
          example: 100
        totalPages:
          type: integer
          description: 总页数
          example: 5

    Error:
      type: object
      properties:
        code:
          type: string
          description: 错误代码
          example: VALIDATION_ERROR
        message:
          type: string
          description: 错误信息
          example: 请求参数验证失败
        details:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
                description: 错误字段
              message:
                type: string
                description: 字段错误信息
      required:
        - code
        - message

  responses:
    BadRequest:
      description: 请求参数错误
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    Unauthorized:
      description: 未授权访问
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    NotFound:
      description: 资源不存在
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
```

### Spring Boot + Swagger集成

```java
// SwaggerConfig.java
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class SwaggerConfig {
    
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("用户管理API")
                        .description("用户注册、登录、信息管理等功能的RESTful API")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("API支持团队")
                                .email("api-support@example.com"))
                        .license(new License()
                                .name("MIT")
                                .url("https://opensource.org/licenses/MIT")))
                .servers(List.of(
                        new Server().url("https://api.example.com/v1").description("生产环境"),
                        new Server().url("https://staging-api.example.com/v1").description("测试环境"),
                        new Server().url("http://localhost:3000/v1").description("开发环境")
                ))
                .addSecurityItem(new SecurityRequirement().addList("BearerAuth"))
                .components(new io.swagger.v3.oas.models.Components()
                        .addSecuritySchemes("BearerAuth", new SecurityScheme()
                                .type(SecurityScheme.Type.HTTP)
                                .scheme("bearer")
                                .bearerFormat("JWT")));
    }
}

// UserController.java
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/v1/users")
@SecurityRequirement(name = "BearerAuth")
public class UserController {
    
    private final UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    @GetMapping
    @Operation(
            summary = "获取用户列表",
            description = "分页获取用户列表，支持搜索和过滤"
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "成功返回用户列表",
                    content = @Content(
                            mediaType = "application/json",
                            schema = @Schema(implementation = UserListResponse.class)
                    )
            ),
            @ApiResponse(
                    responseCode = "400",
                    description = "请求参数错误",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))
            ),
            @ApiResponse(
                    responseCode = "401",
                    description = "未授权访问",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))
            )
    })
    public ResponseEntity<UserListResponse> getUsers(
            @Parameter(description = "页码", example = "1")
            @RequestParam(defaultValue = "1") int page,
            
            @Parameter(description = "每页数量", example = "20")
            @RequestParam(defaultValue = "20") int limit,
            
            @Parameter(description = "搜索关键词", example = "john")
            @RequestParam(required = false) String search
    ) {
        UserListResponse response = userService.getUsers(page, limit, search);
        return ResponseEntity.ok(response);
    }
    
    @PostMapping
    @Operation(
            summary = "创建新用户",
            description = "创建新的用户账户"
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "201",
                    description = "用户创建成功",
                    content = @Content(schema = @Schema(implementation = User.class))
            ),
            @ApiResponse(
                    responseCode = "400",
                    description = "请求参数错误",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))
            ),
            @ApiResponse(
                    responseCode = "409",
                    description = "用户已存在",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))
            )
    })
    public ResponseEntity<User> createUser(
            @Parameter(description = "用户信息", required = true)
            @Valid @RequestBody CreateUserRequest request
    ) {
        User user = userService.createUser(request);
        return ResponseEntity.status(201).body(user);
    }
    
    @GetMapping("/{userId}")
    @Operation(
            summary = "获取用户详情",
            description = "根据用户ID获取详细信息"
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "成功返回用户信息",
                    content = @Content(schema = @Schema(implementation = User.class))
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "用户不存在",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))
            )
    })
    public ResponseEntity<User> getUserById(
            @Parameter(description = "用户ID", required = true, example = "12345")
            @PathVariable Long userId
    ) {
        User user = userService.getUserById(userId);
        return ResponseEntity.ok(user);
    }
    
    @PutMapping("/{userId}")
    @Operation(
            summary = "更新用户信息",
            description = "更新指定用户的信息"
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "更新成功",
                    content = @Content(schema = @Schema(implementation = User.class))
            ),
            @ApiResponse(
                    responseCode = "400",
                    description = "请求参数错误",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "用户不存在",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))
            )
    })
    public ResponseEntity<User> updateUser(
            @Parameter(description = "用户ID", required = true, example = "12345")
            @PathVariable Long userId,
            
            @Parameter(description = "更新信息", required = true)
            @Valid @RequestBody UpdateUserRequest request
    ) {
        User user = userService.updateUser(userId, request);
        return ResponseEntity.ok(user);
    }
}

// DTO类
import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "用户信息")
public class User {
    @Schema(description = "用户ID", example = "12345")
    private Long id;
    
    @Schema(description = "用户名", example = "johndoe")
    private String username;
    
    @Schema(description = "邮箱地址", example = "john@example.com")
    private String email;
    
    @Schema(description = "全名", example = "John Doe")
    private String fullName;
    
    @Schema(description = "头像URL", example = "https://example.com/avatars/john.jpg")
    private String avatar;
    
    @Schema(description = "创建时间")
    private LocalDateTime createdAt;
    
    @Schema(description = "更新时间")
    private LocalDateTime updatedAt;
    
    // getters and setters
}

@Schema(description = "创建用户请求")
public class CreateUserRequest {
    @Schema(description = "用户名", required = true, minLength = 3, maxLength = 50, example = "johndoe")
    private String username;
    
    @Schema(description = "邮箱地址", required = true, format = "email", example = "john@example.com")
    private String email;
    
    @Schema(description = "密码", required = true, minLength = 8, example = "securePassword123")
    private String password;
    
    @Schema(description = "全名", required = true, maxLength = 100, example = "John Doe")
    private String fullName;
    
    // getters and setters
}
```

### 自动化文档生成脚本

```python
#!/usr/bin/env python3
import json
import yaml
import requests
from typing import Dict, List, Any
from pathlib import Path

class APIDocumentationGenerator:
    def __init__(self, config_file: str = "api-docs-config.json"):
        self.config = self.load_config(config_file)
        self.output_dir = Path(self.config.get("output_dir", "docs"))
        self.output_dir.mkdir(exist_ok=True)
    
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.create_default_config(config_file)
    
    def create_default_config(self, config_file: str) -> Dict:
        """创建默认配置"""
        default_config = {
            "output_dir": "docs",
            "formats": ["html", "markdown", "pdf"],
            "api_sources": [
                {
                    "name": "User API",
                    "url": "http://localhost:3000/api-docs",
                    "format": "openapi"
                }
            ],
            "templates": {
                "html": "templates/api-docs.html",
                "markdown": "templates/api-docs.md"
            },
            "validation": {
                "check_examples": True,
                "validate_schemas": True,
                "check_completeness": True
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def fetch_openapi_spec(self, url: str) -> Dict:
        """获取OpenAPI规范"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                return response.json()
            elif 'application/yaml' in content_type or 'text/yaml' in content_type:
                return yaml.safe_load(response.text)
            else:
                # 尝试自动检测格式
                try:
                    return response.json()
                except:
                    return yaml.safe_load(response.text)
        
        except requests.RequestException as e:
            print(f"获取API规范失败: {e}")
            return {}
    
    def validate_spec(self, spec: Dict) -> List[str]:
        """验证API规范"""
        errors = []
        
        if not spec:
            errors.append("API规范为空")
            return errors
        
        # 检查必需字段
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查info字段
        if 'info' in spec:
            info = spec['info']
            info_required = ['title', 'version']
            for field in info_required:
                if field not in info:
                    errors.append(f"info字段缺少: {field}")
        
        # 检查路径
        if 'paths' in spec:
            paths = spec['paths']
            if not paths:
                errors.append("paths字段为空")
            else:
                for path, path_item in paths.items():
                    for method, operation in path_item.items():
                        if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                            if 'summary' not in operation and 'description' not in operation:
                                errors.append(f"路径 {path} {method} 缺少描述")
        
        return errors
    
    def generate_examples(self, spec: Dict) -> Dict:
        """生成示例代码"""
        examples = {}
        
        if 'paths' not in spec:
            return examples
        
        for path, path_item in spec['paths'].items():
            for method, operation in path_item.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    operation_id = operation.get('operationId', f"{method}_{path.replace('/', '_')}")
                    
                    # 生成cURL示例
                    curl_example = self.generate_curl_example(method, path, operation)
                    
                    # 生成JavaScript示例
                    js_example = self.generate_js_example(method, path, operation)
                    
                    # 生成Python示例
                    python_example = self.generate_python_example(method, path, operation)
                    
                    examples[operation_id] = {
                        'curl': curl_example,
                        'javascript': js_example,
                        'python': python_example
                    }
        
        return examples
    
    def generate_curl_example(self, method: str, path: str, operation: Dict) -> str:
        """生成cURL示例"""
        base_url = "https://api.example.com"
        url = f"{base_url}{path}"
        
        curl_cmd = f"curl -X {method.upper()} '{url}'"
        
        # 添加请求头
        headers = []
        if 'parameters' in operation:
            for param in operation['parameters']:
                if param.get('in') == 'header':
                    headers.append(f"-H '{param['name']}: {param.get('example', 'value')}'")
        
        if 'security' in operation:
            headers.append("-H 'Authorization: Bearer YOUR_TOKEN'")
        
        if headers:
            curl_cmd += " \\\n  " + " \\\n  ".join(headers)
        
        # 添加请求体
        if method.upper() in ['POST', 'PUT', 'PATCH'] and 'requestBody' in operation:
            request_body = operation['requestBody']
            if 'content' in request_body:
                content_type = list(request_body['content'].keys())[0]
                headers.append(f"-H 'Content-Type: {content_type}'")
                
                # 生成示例请求体
                example_body = self.generate_example_body(request_body['content'][content_type])
                curl_cmd += f" \\\n  -d '{example_body}'"
        
        return curl_cmd
    
    def generate_js_example(self, method: str, path: str, operation: Dict) -> str:
        """生成JavaScript示例"""
        base_url = "https://api.example.com"
        url = f"{base_url}{path}"
        
        js_code = f"""const response = await fetch('{url}', {{
    method: '{method.upper()}',"""
        
        # 添加请求头
        headers = {}
        if 'security' in operation:
            headers['Authorization'] = 'Bearer YOUR_TOKEN'
        
        if method.upper() in ['POST', 'PUT', 'PATCH'] and 'requestBody' in operation:
            headers['Content-Type'] = 'application/json'
        
        if headers:
            js_code += f"""
    headers: {{
        {', '.join([f"'{k}': '{v}'" for k, v in headers.items()])}
    }},"""
        
        # 添加请求体
        if method.upper() in ['POST', 'PUT', 'PATCH'] and 'requestBody' in operation:
            request_body = operation['requestBody']
            if 'content' in request_body:
                content_type = list(request_body['content'].keys())[0]
                example_body = self.generate_example_body(request_body['content'][content_type])
                js_code += f"""
    body: JSON.stringify({example_body})"""
        
        js_code += """
});

const data = await response.json();
console.log(data);"""
        
        return js_code
    
    def generate_python_example(self, method: str, path: str, operation: Dict) -> str:
        """生成Python示例"""
        base_url = "https://api.example.com"
        url = f"{base_url}{path}"
        
        python_code = f"""import requests
import json

response = requests.{method.lower()}(
    '{url}'"""
        
        # 添加请求头
        headers = {}
        if 'security' in operation:
            headers['Authorization'] = 'Bearer YOUR_TOKEN'
        
        if method.upper() in ['POST', 'PUT', 'PATCH'] and 'requestBody' in operation:
            headers['Content-Type'] = 'application/json'
        
        if headers:
            python_code += f""",
    headers={{{"""
            python_code += ', '.join([f"'{k}': '{v}'" for k, v in headers.items()])
            python_code += "}}"
        
        # 添加请求体
        if method.upper() in ['POST', 'PUT', 'PATCH'] and 'requestBody' in operation:
            request_body = operation['requestBody']
            if 'content' in request_body:
                content_type = list(request_body['content'].keys())[0]
                example_body = self.generate_example_body(request_body['content'][content_type])
                python_code += f""",
    json={example_body}"""
        
        python_code += """
)

data = response.json()
print(data)"""
        
        return python_code
    
    def generate_example_body(self, content_spec: Dict) -> str:
        """生成示例请求体"""
        if 'example' in content_spec:
            return json.dumps(content_spec['example'], indent=2)
        
        if 'schema' in content_spec:
            return self.generate_example_from_schema(content_spec['schema'])
        
        return "{}"
    
    def generate_example_from_schema(self, schema: Dict) -> str:
        """从schema生成示例"""
        if schema.get('type') == 'object':
            example = {}
            properties = schema.get('properties', {})
            for prop_name, prop_spec in properties.items():
                if prop_name not in schema.get('required', []):
                    continue
                example[prop_name] = self.generate_example_from_schema(prop_spec)
            return json.dumps(example, indent=2)
        
        elif schema.get('type') == 'string':
            if 'format' in schema:
                if schema['format'] == 'email':
                    return '"user@example.com"'
                elif schema['format'] == 'date-time':
                    return '"2023-01-01T00:00:00Z"'
            return '"example"'
        
        elif schema.get('type') == 'integer':
            return str(schema.get('example', 123))
        
        elif schema.get('type') == 'boolean':
            return 'true'
        
        elif schema.get('type') == 'array':
            return '[]'
        
        return 'null'
    
    def generate_html_docs(self, spec: Dict, examples: Dict) -> str:
        """生成HTML文档"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - API文档</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css">
    <style>
        body {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .examples {{ margin-top: 30px; }}
        .example {{ margin-bottom: 20px; border: 1px solid #ddd; padding: 15px; }}
        .example h3 {{ margin-top: 0; }}
        pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    
    <div id="swagger-ui"></div>
    
    <div class="examples">
        <h2>代码示例</h2>
        {examples_html}
    </div>
    
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({{
            url: 'data:application/json,{spec_json}',
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.StandalonePreset
            ]
        }});
    </script>
</body>
</html>
        """
        
        # 生成示例HTML
        examples_html = ""
        for operation_id, example_set in examples.items():
            examples_html += f"""
            <div class="example">
                <h3>{operation_id}</h3>
                <h4>cURL</h4>
                <pre>{example_set['curl']}</pre>
                <h4>JavaScript</h4>
                <pre>{example_set['javascript']}</pre>
                <h4>Python</h4>
                <pre>{example_set['python']}</pre>
            </div>
            """
        
        return html_template.format(
            title=spec.get('info', {}).get('title', 'API文档'),
            description=spec.get('info', {}).get('description', ''),
            spec_json=json.dumps(spec).replace('"', '&quot;'),
            examples_html=examples_html
        )
    
    def generate_markdown_docs(self, spec: Dict, examples: Dict) -> str:
        """生成Markdown文档"""
        md_content = f"""# {spec.get('info', {}).get('title', 'API文档')}

{spec.get('info', {}).get('description', '')}

## 基本信息

- **版本**: {spec.get('info', {}).get('version', 'N/A')}
- **基础URL**: https://api.example.com

## 认证

本API使用Bearer Token认证。

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.example.com/endpoint
```

## API端点

"""
        
        # 添加端点信息
        if 'paths' in spec:
            for path, path_item in spec['paths'].items():
                md_content += f"### {path}\n\n"
                
                for method, operation in path_item.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        operation_id = operation.get('operationId', f"{method}_{path}")
                        summary = operation.get('summary', '')
                        description = operation.get('description', '')
                        
                        md_content += f"#### {method.upper()} {path}\n\n"
                        if summary:
                            md_content += f"**摘要**: {summary}\n\n"
                        if description:
                            md_content += f"**描述**: {description}\n\n"
                        
                        # 添加代码示例
                        if operation_id in examples:
                            example_set = examples[operation_id]
                            md_content += "**代码示例**:\n\n"
                            md_content += "```bash\n" + example_set['curl'] + "\n```\n\n"
                            md_content += "```javascript\n" + example_set['javascript'] + "\n```\n\n"
                            md_content += "```python\n" + example_set['python'] + "\n```\n\n"
        
        return md_content
    
    def generate_documentation(self):
        """生成文档"""
        print("开始生成API文档...")
        
        for api_source in self.config.get('api_sources', []):
            print(f"处理API: {api_source['name']}")
            
            # 获取API规范
            spec = self.fetch_openapi_spec(api_source['url'])
            
            # 验证规范
            errors = self.validate_spec(spec)
            if errors:
                print(f"API规范验证失败: {errors}")
                continue
            
            # 生成示例
            examples = self.generate_examples(spec)
            
            # 生成不同格式的文档
            formats = self.config.get('formats', ['html', 'markdown'])
            
            for format_type in formats:
                if format_type == 'html':
                    html_content = self.generate_html_docs(spec, examples)
                    output_file = self.output_dir / f"{api_source['name'].lower().replace(' ', '-')}.html"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"生成HTML文档: {output_file}")
                
                elif format_type == 'markdown':
                    md_content = self.generate_markdown_docs(spec, examples)
                    output_file = self.output_dir / f"{api_source['name'].lower().replace(' ', '-')}.md"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    print(f"生成Markdown文档: {output_file}")
        
        print("文档生成完成！")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='API文档生成器')
    parser.add_argument('--config', default='api-docs-config.json', help='配置文件路径')
    parser.add_argument('--output', help='输出目录')
    
    args = parser.parse_args()
    
    generator = APIDocumentationGenerator(args.config)
    
    if args.output:
        generator.output_dir = Path(args.output)
        generator.output_dir.mkdir(exist_ok=True)
    
    generator.generate_documentation()

if __name__ == "__main__":
    main()
```

## 最佳实践

### 文档设计
- **统一规范**: 使用OpenAPI/Swagger标准
- **完整描述**: 提供详细的参数说明和示例
- **版本管理**: 明确的版本控制和变更日志
- **多语言支持**: 支持中英文文档

### 自动化流程
- **代码生成**: 从注解自动生成文档
- **持续更新**: CI/CD流程中自动更新文档
- **验证检查**: 自动验证文档完整性和准确性
- **多格式输出**: 支持HTML、PDF、Markdown等格式

### 质量保证
- **示例验证**: 确保示例代码可用
- **一致性检查**: 验证文档与实际接口一致性
- **完整性检查**: 确保所有接口都有文档
- **定期审查**: 定期检查和更新文档内容

### 用户体验
- **交互式文档**: 提供在线测试功能
- **代码示例**: 多语言的代码示例
- **快速入门**: 提供快速开始指南
- **错误处理**: 详细的错误响应说明

## 相关技能

- [Git工作流管理](./git-workflows/) - 文档版本控制
- [Docker Compose编排](./docker-compose/) - 文档服务部署
- [代码格式化](./code-formatter/) - 文档代码格式化
- [版本管理器](./version-manager/) - API版本管理
