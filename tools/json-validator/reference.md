# JSON Validator 技术参考

## 概述

JSON Validator 是一个专门用于验证 JSON 数据格式和结构的工具，提供 JSON Schema 验证、数据类型检查、格式验证和自定义规则验证功能。

## 核心功能

### JSON Schema 验证
- **结构验证**: 根据 JSON Schema 验证数据结构
- **类型检查**: 验证数据类型是否符合要求
- **格式验证**: 检查日期、邮箱、URL 等格式
- **约束验证**: 验证数值范围、字符串长度等约束

### 自定义验证
- **自定义规则**: 定义自定义验证规则
- **条件验证**: 基于条件的动态验证
- **异步验证**: 支持异步数据验证
- **批量验证**: 批量验证多个 JSON 对象

### 错误报告
- **详细错误**: 提供详细的错误信息和位置
- **多语言支持**: 支持多种语言的错误消息
- **自定义消息**: 自定义错误提示消息
- **格式化输出**: 多种输出格式支持

## 配置指南

### 基础配置
```json
{
  "json-validator": {
    "enabled": true,
    "strict": true,
    "schemas": {
      "user": "./schemas/user.json",
      "product": "./schemas/product.json"
    },
    "validation": {
      "type-checking": true,
      "format-validation": true,
      "required-fields": true,
      "additional-properties": false
    },
    "error-reporting": {
      "language": "zh-CN",
      "detailed": true,
      "include-path": true
    }
  }
}
```

### 高级配置
```json
{
  "json-validator": {
    "advanced": {
      "custom-rules": [
        {
          "name": "unique-email",
          "type": "function",
          "validator": "./validators/unique-email.js",
          "message": "邮箱地址必须唯一"
        },
        {
          "name": "password-strength",
          "type": "regex",
          "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d@$!%*?&]{8,}$",
          "message": "密码必须包含大小写字母和数字，至少8位"
        }
      ],
      "async-validation": {
        "enabled": true,
        "timeout": 5000,
        "concurrent": 10
      },
      "performance": {
        "cache-schemas": true,
        "pre-compile": true,
        "batch-size": 100
      }
    }
  }
}
```

## API 参考

### 验证器主类
```javascript
class JsonValidator {
  constructor(config = {}) {
    this.config = new Config(config);
    this.schemas = new SchemaManager(this.config);
    this.rules = new RuleManager(this.config);
    this.formatter = new ErrorFormatter(this.config);
  }

  // 验证 JSON 数据
  async validate(data, schemaName, options = {}) {
    try {
      const schema = await this.schemas.getSchema(schemaName);
      const validator = this.compileValidator(schema);
      
      const result = await validator.validate(data, {
        strict: options.strict ?? this.config.strict,
        customRules: options.customRules ?? true,
        asyncValidation: options.asyncValidation ?? true
      });

      return new ValidationResult({
        valid: result.valid,
        errors: result.errors,
        data: result.data,
        schema: schemaName,
        timestamp: new Date()
      });
    } catch (error) {
      throw new ValidationError(`Validation failed: ${error.message}`, error);
    }
  }

  // 批量验证
  async validateBatch(dataArray, schemaName, options = {}) {
    const results = [];
    const batchSize = options.batchSize || this.config.batchSize;
    
    for (let i = 0; i < dataArray.length; i += batchSize) {
      const batch = dataArray.slice(i, i + batchSize);
      const batchResults = await Promise.allSettled(
        batch.map(data => this.validate(data, schemaName, options))
      );
      
      results.push(...batchResults);
    }
    
    return new BatchValidationResult({
      total: dataArray.length,
      results,
      summary: this.generateBatchSummary(results)
    });
  }

  // 编译验证器
  compileValidator(schema) {
    const cacheKey = this.generateSchemaKey(schema);
    
    if (this.config.cacheSchemas && this.validatorCache.has(cacheKey)) {
      return this.validatorCache.get(cacheKey);
    }

    const validator = new CompiledValidator(schema, this.config);
    
    if (this.config.cacheSchemas) {
      this.validatorCache.set(cacheKey, validator);
    }
    
    return validator;
  }
}
```

### Schema 管理
```javascript
class SchemaManager {
  constructor(config) {
    this.config = config;
    this.schemas = new Map();
    this.loaders = new Map();
    
    this.registerDefaultLoaders();
  }

  // 注册 Schema 加载器
  registerDefaultLoaders() {
    this.registerLoader('file', new FileSchemaLoader());
    this.registerLoader('http', new HttpSchemaLoader());
    this.registerLoader('json-pointer', new JsonPointerLoader());
  }

  // 注册自定义加载器
  registerLoader(name, loader) {
    this.loaders.set(name, loader);
  }

  // 获取 Schema
  async getSchema(schemaName) {
    if (this.schemas.has(schemaName)) {
      return this.schemas.get(schemaName);
    }

    const schemaConfig = this.config.schemas[schemaName];
    if (!schemaConfig) {
      throw new Error(`Schema '${schemaName}' not found`);
    }

    const loader = this.getLoader(schemaConfig);
    const schema = await loader.load(schemaConfig);
    
    // 解析 $ref 引用
    const resolvedSchema = await this.resolveReferences(schema);
    
    // 缓存 Schema
    this.schemas.set(schemaName, resolvedSchema);
    
    return resolvedSchema;
  }

  // 解析 $ref 引用
  async resolveReferences(schema, basePath = '') {
    if (!schema || typeof schema !== 'object') {
      return schema;
    }

    if (schema.$ref) {
      const refPath = this.resolveRefPath(schema.$ref, basePath);
      const refSchema = await this.getSchema(refPath);
      return refSchema;
    }

    const resolved = {};
    for (const [key, value] of Object.entries(schema)) {
      if (Array.isArray(value)) {
        resolved[key] = await Promise.all(
          value.map(item => this.resolveReferences(item, basePath))
        );
      } else if (typeof value === 'object') {
        resolved[key] = await this.resolveReferences(value, basePath);
      } else {
        resolved[key] = value;
      }
    }

    return resolved;
  }

  // 获取加载器
  getLoader(schemaConfig) {
    const type = this.detectSchemaType(schemaConfig);
    const loader = this.loaders.get(type);
    
    if (!loader) {
      throw new Error(`No loader found for schema type: ${type}`);
    }
    
    return loader;
  }

  // 检测 Schema 类型
  detectSchemaType(schemaConfig) {
    if (typeof schemaConfig === 'string') {
      if (schemaConfig.startsWith('http://') || schemaConfig.startsWith('https://')) {
        return 'http';
      } else if (schemaConfig.startsWith('#')) {
        return 'json-pointer';
      } else {
        return 'file';
      }
    }
    
    return 'object';
  }
}
```

### 自定义规则
```javascript
class CustomRuleManager {
  constructor(config) {
    this.config = config;
    this.rules = new Map();
    this.loadCustomRules();
  }

  // 加载自定义规则
  async loadCustomRules() {
    const customRules = this.config.customRules || [];
    
    for (const ruleConfig of customRules) {
      await this.loadRule(ruleConfig);
    }
  }

  // 加载单个规则
  async loadRule(ruleConfig) {
    let rule;
    
    switch (ruleConfig.type) {
      case 'function':
        rule = await this.loadFunctionRule(ruleConfig);
        break;
      case 'regex':
        rule = this.loadRegexRule(ruleConfig);
        break;
      case 'async':
        rule = await this.loadAsyncRule(ruleConfig);
        break;
      default:
        throw new Error(`Unknown rule type: ${ruleConfig.type}`);
    }
    
    this.rules.set(ruleConfig.name, rule);
  }

  // 加载函数规则
  async loadFunctionRule(ruleConfig) {
    const module = await import(ruleConfig.validator);
    const validator = module.default || module;
    
    return {
      name: ruleConfig.name,
      type: 'function',
      validator,
      message: ruleConfig.message
    };
  }

  // 加载正则表达式规则
  loadRegexRule(ruleConfig) {
    const pattern = new RegExp(ruleConfig.pattern);
    
    return {
      name: ruleConfig.name,
      type: 'regex',
      validator: (value) => pattern.test(value),
      message: ruleConfig.message
    };
  }

  // 加载异步规则
  async loadAsyncRule(ruleConfig) {
    const module = await import(ruleConfig.validator);
    const validator = module.default || module;
    
    return {
      name: ruleConfig.name,
      type: 'async',
      validator,
      message: ruleConfig.message,
      timeout: ruleConfig.timeout || 5000
    };
  }

  // 执行规则
  async executeRule(ruleName, value, context) {
    const rule = this.rules.get(ruleName);
    if (!rule) {
      throw new Error(`Rule '${ruleName}' not found`);
    }

    try {
      let result;
      
      if (rule.type === 'async') {
        result = await this.executeWithTimeout(
          rule.validator(value, context),
          rule.timeout
        );
      } else {
        result = rule.validator(value, context);
      }
      
      return {
        valid: result,
        message: result ? null : rule.message
      };
    } catch (error) {
      return {
        valid: false,
        message: `Rule execution failed: ${error.message}`
      };
    }
  }

  // 带超时的执行
  executeWithTimeout(promise, timeout) {
    return Promise.race([
      promise,
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Rule execution timeout')), timeout)
      )
    ]);
  }
}
```

## JSON Schema 示例

### 用户 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/schemas/user.json",
  "title": "User",
  "description": "用户信息",
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "用户ID",
      "minimum": 1
    },
    "username": {
      "type": "string",
      "description": "用户名",
      "minLength": 3,
      "maxLength": 50,
      "pattern": "^[a-zA-Z0-9_]+$"
    },
    "email": {
      "type": "string",
      "description": "邮箱地址",
      "format": "email",
      "customRules": ["unique-email"]
    },
    "password": {
      "type": "string",
      "description": "密码",
      "minLength": 8,
      "customRules": ["password-strength"]
    },
    "profile": {
      "$ref": "#/definitions/Profile"
    },
    "roles": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Role"
      },
      "minItems": 1
    },
    "createdAt": {
      "type": "string",
      "format": "date-time"
    },
    "updatedAt": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["id", "username", "email", "password"],
  "additionalProperties": false,
  "definitions": {
    "Profile": {
      "type": "object",
      "properties": {
        "firstName": {
          "type": "string",
          "minLength": 1,
          "maxLength": 50
        },
        "lastName": {
          "type": "string",
          "minLength": 1,
          "maxLength": 50
        },
        "age": {
          "type": "integer",
          "minimum": 0,
          "maximum": 150
        },
        "avatar": {
          "type": "string",
          "format": "uri"
        }
      },
      "required": ["firstName", "lastName"]
    },
    "Role": {
      "type": "object",
      "properties": {
        "id": {
          "type": "integer"
        },
        "name": {
          "type": "string"
        },
        "permissions": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      },
      "required": ["id", "name"]
    }
  }
}
```

### 产品 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/schemas/product.json",
  "title": "Product",
  "description": "产品信息",
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "产品ID",
      "pattern": "^PROD-[0-9]{8}$"
    },
    "name": {
      "type": "string",
      "description": "产品名称",
      "minLength": 1,
      "maxLength": 200
    },
    "description": {
      "type": "string",
      "description": "产品描述",
      "maxLength": 1000
    },
    "price": {
      "type": "number",
      "description": "价格",
      "minimum": 0,
      "exclusiveMinimum": true
    },
    "currency": {
      "type": "string",
      "description": "货币",
      "enum": ["USD", "EUR", "CNY", "JPY"]
    },
    "category": {
      "$ref": "#/definitions/Category"
    },
    "variants": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/ProductVariant"
      }
    },
    "images": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/ProductImage"
      },
      "minItems": 1
    },
    "stock": {
      "$ref": "#/definitions/StockInfo"
    },
    "metadata": {
      "type": "object",
      "additionalProperties": {
        "type": ["string", "number", "boolean"]
      }
    }
  },
  "required": ["id", "name", "price", "currency", "category"],
  "additionalProperties": false,
  "definitions": {
    "Category": {
      "type": "object",
      "properties": {
        "id": {
          "type": "integer"
        },
        "name": {
          "type": "string"
        },
        "parentId": {
          "type": "integer"
        }
      },
      "required": ["id", "name"]
    },
    "ProductVariant": {
      "type": "object",
      "properties": {
        "id": {
          "type": "string"
        },
        "name": {
          "type": "string"
        },
        "price": {
          "type": "number",
          "minimum": 0
        },
        "attributes": {
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        }
      },
      "required": ["id", "name", "price"]
    },
    "ProductImage": {
      "type": "object",
      "properties": {
        "url": {
          "type": "string",
          "format": "uri"
        },
        "alt": {
          "type": "string"
        },
        "width": {
          "type": "integer",
          "minimum": 1
        },
        "height": {
          "type": "integer",
          "minimum": 1
        }
      },
      "required": ["url"]
    },
    "StockInfo": {
      "type": "object",
      "properties": {
        "quantity": {
          "type": "integer",
          "minimum": 0
        },
        "reserved": {
          "type": "integer",
          "minimum": 0
        },
        "available": {
          "type": "integer",
          "minimum": 0
        },
        "lowStockThreshold": {
          "type": "integer",
          "minimum": 0
        }
      },
      "required": ["quantity", "available"]
    }
  }
}
```

## 集成指南

### Express.js 集成
```javascript
const express = require('express');
const { JsonValidator } = require('json-validator');

const app = express();
const validator = new JsonValidator(require('./config/validator.json'));

// 中间件：验证请求体
const validateBody = (schemaName) => {
  return async (req, res, next) => {
    try {
      const result = await validator.validate(req.body, schemaName);
      
      if (!result.valid) {
        return res.status(400).json({
          error: 'Validation failed',
          details: result.errors
        });
      }
      
      req.validatedData = result.data;
      next();
    } catch (error) {
      res.status(500).json({
        error: 'Internal server error',
        message: error.message
      });
    }
  };
};

// 使用示例
app.post('/api/users', 
  express.json(),
  validateBody('user'),
  async (req, res) => {
    try {
      const user = await createUser(req.validatedData);
      res.status(201).json(user);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
);
```

### React 集成
```javascript
import React, { useState } from 'react';
import { JsonValidator } from 'json-validator';

const validator = new JsonValidator(require('./config/validator.json'));

function UserForm() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validateField = async (fieldName, value) => {
    try {
      const partialData = { ...formData, [fieldName]: value };
      const result = await validator.validate(partialData, 'user', {
        strict: false,
        partial: true
      });
      
      const fieldErrors = result.errors.filter(error => 
        error.path.includes(fieldName)
      );
      
      setErrors(prev => ({
        ...prev,
        [fieldName]: fieldErrors.length > 0 ? fieldErrors[0].message : null
      }));
    } catch (error) {
      console.error('Validation error:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const result = await validator.validate(formData, 'user');
      
      if (result.valid) {
        // 提交表单
        await submitUser(formData);
      } else {
        // 显示错误
        const errorMap = {};
        result.errors.forEach(error => {
          const fieldName = error.path[0];
          errorMap[fieldName] = error.message;
        });
        setErrors(errorMap);
      }
    } catch (error) {
      console.error('Validation error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>用户名:</label>
        <input
          name="username"
          value={formData.username}
          onChange={handleChange}
          onBlur={(e) => validateField('username', e.target.value)}
        />
        {errors.username && <span className="error">{errors.username}</span>}
      </div>
      
      <div>
        <label>邮箱:</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          onBlur={(e) => validateField('email', e.target.value)}
        />
        {errors.email && <span className="error">{errors.email}</span>}
      </div>
      
      <div>
        <label>密码:</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          onBlur={(e) => validateField('password', e.target.value)}
        />
        {errors.password && <span className="error">{errors.password}</span>}
      </div>
      
      <button type="submit">提交</button>
    </form>
  );
}
```

## 最佳实践

### Schema 设计
1. **清晰的描述**: 为每个属性添加清晰的描述
2. **合理的约束**: 设置适当的数值和长度约束
3. **复用定义**: 使用 definitions 复用通用结构
4. **版本管理**: 为 Schema 添加版本信息

### 性能优化
1. **缓存 Schema**: 缓存编译后的 Schema
2. **批量验证**: 批量验证多个对象
3. **异步验证**: 对耗时验证使用异步方式
4. **预编译**: 在应用启动时预编译 Schema

### 错误处理
1. **详细错误**: 提供清晰的错误信息
2. **多语言**: 支持多语言错误消息
3. **错误分类**: 按严重程度分类错误
4. **日志记录**: 记录验证错误用于调试

## 工具和资源

### 开发工具
- **JSON Schema Validator**: 在线 Schema 验证工具
- **JSON Schema Linter**: Schema 代码检查工具
- **JSON Generator**: 根据 Schema 生成示例数据
- **JSON Editor**: 可视化 Schema 编辑器

### 相关库
- **Ajv**: 高性能 JSON Schema 验证器
- **json-schema**: JSON Schema 工具库
- **tv4**: Tiny Validator for JSON Schema
- **is-my-json-valid**: 快速 JSON Schema 验证器

### 学习资源
- [JSON Schema 官方网站](https://json-schema.org/)
- [JSON Schema 规范](https://json-schema.org/specification.html)
- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/)
- [JSON Schema 最佳实践](https://json-schema.org/best-practices.html)

### 社区支持
- [JSON Schema GitHub](https://github.com/json-schema-org)
- [Stack Overflow JSON Schema 标签](https://stackoverflow.com/questions/tagged/json-schema)
- [JSON Schema 邮件列表](https://groups.google.com/g/json-schema)
- [JSON Schema 规范讨论](https://github.com/json-schema-org/json-schema-spec)
