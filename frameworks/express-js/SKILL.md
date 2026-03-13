---
name: Express.js服务
description: "当开发Express.js应用时，分析路由设计，优化中间件配置，解决性能问题。验证API架构，设计RESTful服务，和最佳实践。"
license: MIT
---

# Express.js服务技能

## 概述
Express.js是Node.js最流行的Web框架。不当的Express应用设计会导致性能问题、安全漏洞和维护困难。在开发Express应用前需要仔细分析架构需求。

**核心原则**: 好的Express应用应该模块化、高性能、安全可靠。坏的Express应用会导致代码混乱、性能瓶颈和安全风险。

## 何时使用

**始终:**
- 设计RESTful API时
- 构建Web应用后端时
- 实现微服务架构时
- 处理HTTP请求路由时
- 配置中间件和错误处理时

**触发短语:**
- "Express.js应用设计"
- "Node.js API开发"
- "Express中间件配置"
- "RESTful服务架构"
- "Express性能优化"
- "Node.js Web框架"

## Express.js服务功能

### 路由设计
- RESTful路由规划
- 动态路由参数
- 路由中间件配置
- 错误处理路由
- API版本管理

### 中间件管理
- 请求处理中间件
- 身份验证中间件
- 日志记录中间件
- 错误处理中间件
- 自定义中间件开发

### 性能优化
- 响应时间优化
- 内存使用优化
- 并发处理优化
- 缓存策略配置
- 数据库连接池

### 安全配置
- CORS跨域配置
- 安全头设置
- 输入验证和清理
- 会话管理
- 防护攻击配置

## 常见Express.js问题

### 路由设计不当
```
问题:
路由结构混乱，缺乏一致性

错误示例:
- 路由命名不规范
- 缺乏RESTful设计
- 参数验证缺失
- 错误处理不统一

解决方案:
1. 遵循RESTful设计原则
2. 统一路由命名规范
3. 实施参数验证中间件
4. 建立统一错误处理机制
```

### 中间件滥用
```
问题:
中间件配置过多或顺序不当

错误示例:
- 不必要的中间件加载
- 中间件执行顺序错误
- 同步中间件阻塞
- 中间件依赖混乱

解决方案:
1. 只加载必要的中间件
2. 正确配置中间件顺序
3. 使用异步中间件
4. 清理中间件依赖关系
```

### 性能瓶颈
```
问题:
应用响应慢，并发能力差

错误示例:
- 同步阻塞操作
- 内存泄漏
- 数据库连接未复用
- 缺乏缓存机制

解决方案:
1. 使用异步操作避免阻塞
2. 实施内存监控和清理
3. 配置数据库连接池
4. 添加适当的缓存策略
```

## 代码实现示例

### Express应用分析器
```javascript
const express = require('express');
const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');

class ExpressAppAnalyzer {
    constructor(appPath) {
        this.appPath = appPath;
        this.issues = [];
        this.metrics = {
            routes: [],
            middlewares: [],
            controllers: [],
            performance: {}
        };
    }

    analyzeApplication() {
        try {
            // 分析路由结构
            this.analyzeRoutes();
            
            // 分析中间件配置
            this.analyzeMiddlewares();
            
            // 分析控制器代码
            this.analyzeControllers();
            
            // 性能分析
            this.analyzePerformance();
            
            // 生成分析报告
            return this.generateReport();
            
        } catch (error) {
            return { error: `分析失败: ${error.message}` };
        }
    }

    analyzeRoutes() {
        try {
            const routesPath = path.join(this.appPath, 'routes');
            if (!fs.existsSync(routesPath)) {
                this.issues.push({
                    severity: 'medium',
                    type: 'structure',
                    message: '缺少routes目录',
                    suggestion: '创建routes目录并按模块组织路由文件'
                });
                return;
            }

            const routeFiles = fs.readdirSync(routesPath).filter(file => file.endsWith('.js'));
            
            for (const file of routeFiles) {
                const filePath = path.join(routesPath, file);
                const content = fs.readFileSync(filePath, 'utf8');
                
                this.analyzeRouteFile(file, content);
            }
            
        } catch (error) {
            this.issues.push({
                severity: 'high',
                type: 'analysis',
                message: `路由分析失败: ${error.message}`,
                suggestion: '检查路由文件格式和权限'
            });
        }
    }

    analyzeRouteFile(fileName, content) {
        const routeInfo = {
            file: fileName,
            routes: [],
            issues: []
        };

        // 检查RESTful路由设计
        const httpMethods = ['get', 'post', 'put', 'delete', 'patch'];
        const routePatterns = [];
        
        for (const method of httpMethods) {
            const regex = new RegExp(`router\\.${method}\\s*\\(\\s*['"]([^'"]+)['"]`, 'g');
            let match;
            
            while ((match = regex.exec(content)) !== null) {
                routePatterns.push({
                    method: method.toUpperCase(),
                    path: match[1],
                    line: content.substring(0, match.index).split('\n').length
                });
            }
        }

        routeInfo.routes = routePatterns;

        // 检查路由命名规范
        for (const route of routePatterns) {
            if (!this.isValidRoutePath(route.path)) {
                routeInfo.issues.push({
                    severity: 'medium',
                    type: 'naming',
                    message: `路由路径不规范: ${route.method} ${route.path}`,
                    suggestion: '使用名词复数形式，避免动词，遵循RESTful规范'
                });
            }
        }

        // 检查参数验证
        if (content.includes('req.params') || content.includes('req.query') || content.includes('req.body')) {
            if (!content.includes('express-validator') && !content.includes('joi') && !content.includes('yup')) {
                routeInfo.issues.push({
                    severity: 'high',
                    type: 'security',
                    message: '缺少输入验证',
                    suggestion: '添加express-validator或joi进行输入验证'
                });
            }
        }

        this.metrics.routes.push(routeInfo);
        this.issues.push(...routeInfo.issues);
    }

    isValidRoutePath(path) {
        // 检查路径是否符合RESTful规范
        if (path.includes('/get/') || path.includes('/post/') || path.includes('/put/') || path.includes('/delete/')) {
            return false;
        }
        
        // 检查是否使用名词复数
        const pathParts = path.split('/').filter(part => part && !part.startsWith(':'));
        for (const part of pathParts) {
            if (part.endsWith('s') || part === 'login' || part === 'logout') {
                continue;
            }
            // 允许一些特殊情况
            if (['profile', 'settings', 'search'].includes(part)) {
                continue;
            }
            return false;
        }
        
        return true;
    }

    analyzeMiddlewares() {
        try {
            const appFile = path.join(this.appPath, 'app.js');
            const serverFile = path.join(this.appPath, 'server.js');
            
            let mainFile = null;
            if (fs.existsSync(appFile)) {
                mainFile = appFile;
            } else if (fs.existsSync(serverFile)) {
                mainFile = serverFile;
            }

            if (!mainFile) {
                this.issues.push({
                    severity: 'high',
                    type: 'structure',
                    message: '缺少主应用文件(app.js或server.js)',
                    suggestion: '创建主应用文件并配置Express应用'
                });
                return;
            }

            const content = fs.readFileSync(mainFile, 'utf8');
            this.analyzeMiddlewareUsage(content);
            
        } catch (error) {
            this.issues.push({
                severity: 'high',
                type: 'analysis',
                message: `中间件分析失败: ${error.message}`,
                suggestion: '检查主应用文件格式'
            });
        }
    }

    analyzeMiddlewareUsage(content) {
        const middlewareInfo = {
            file: 'main',
            middlewares: [],
            issues: []
        };

        // 检查常用中间件
        const commonMiddlewares = [
            { name: 'cors', pattern: /cors\(\)/, severity: 'high' },
            { name: 'helmet', pattern: /helmet\(\)/, severity: 'high' },
            { name: 'morgan', pattern: /morgan\(/, severity: 'medium' },
            { name: 'body-parser', pattern: /body-parser|express\.json|express\.urlencoded/, severity: 'high' },
            { name: 'compression', pattern: /compression\(\)/, severity: 'medium' }
        ];

        for (const middleware of commonMiddlewares) {
            if (!middleware.pattern.test(content)) {
                middlewareInfo.issues.push({
                    severity: middleware.severity,
                    type: 'security',
                    message: `缺少${middleware.name}中间件`,
                    suggestion: `添加${middleware.name}中间件提升安全性或性能`
                });
            } else {
                middlewareInfo.middlewares.push(middleware.name);
            }
        }

        // 检查错误处理中间件
        if (!content.includes('app.use(') || !content.includes('err, req, res, next')) {
            middlewareInfo.issues.push({
                severity: 'high',
                type: 'error_handling',
                message: '缺少错误处理中间件',
                suggestion: '添加错误处理中间件捕获和处理应用错误'
            });
        }

        // 检查中间件顺序
        const lines = content.split('\n');
        const middlewareLines = [];
        
        lines.forEach((line, index) => {
            if (line.includes('app.use(') && !line.includes('//')) {
                middlewareLines.push({
                    line: index + 1,
                    content: line.trim()
                });
            }
        });

        // 验证中间件顺序
        this.validateMiddlewareOrder(middlewareLines, middlewareInfo);

        this.metrics.middlewares.push(middlewareInfo);
        this.issues.push(...middlewareInfo.issues);
    }

    validateMiddlewareOrder(middlewareLines, middlewareInfo) {
        // 检查路由是否在错误处理之前
        let hasErrorHandling = false;
        let hasRoutesAfterError = false;

        for (const middleware of middlewareLines) {
            if (middleware.content.includes('err, req, res, next')) {
                hasErrorHandling = true;
            } else if (hasErrorHandling && (middleware.content.includes('require('./routes')') || middleware.content.includes('app.use(\'/'))) {
                hasRoutesAfterError = true;
            }
        }

        if (hasRoutesAfterError) {
            middlewareInfo.issues.push({
                severity: 'high',
                type: 'order',
                message: '路由定义在错误处理中间件之后',
                suggestion: '确保错误处理中间件在所有路由之后定义'
            });
        }
    }

    analyzeControllers() {
        try {
            const controllersPath = path.join(this.appPath, 'controllers');
            if (!fs.existsSync(controllersPath)) {
                this.issues.push({
                    severity: 'medium',
                    type: 'structure',
                    message: '缺少controllers目录',
                    suggestion: '创建controllers目录并按模块组织控制器文件'
                });
                return;
            }

            const controllerFiles = fs.readdirSync(controllersPath).filter(file => file.endsWith('.js'));
            
            for (const file of controllerFiles) {
                const filePath = path.join(controllersPath, file);
                const content = fs.readFileSync(filePath, 'utf8');
                
                this.analyzeControllerFile(file, content);
            }
            
        } catch (error) {
            this.issues.push({
                severity: 'medium',
                type: 'analysis',
                message: `控制器分析失败: ${error.message}`,
                suggestion: '检查控制器文件格式和权限'
            });
        }
    }

    analyzeControllerFile(fileName, content) {
        const controllerInfo = {
            file: fileName,
            functions: [],
            issues: []
        };

        // 检查函数命名和结构
        const functionPattern = /(?:exports\.|module\.exports\.|const\s+\w+\s*=\s*)(?:async\s+)?(\w+)\s*=\s*(?:async\s+)?\(?\s*req\s*,\s*res\s*(?:,\s*next)?\s*\)?/g;
        let match;

        while ((match = functionPattern.exec(content)) !== null) {
            controllerInfo.functions.push({
                name: match[1],
                line: content.substring(0, match.index).split('\n').length
            });
        }

        // 检查错误处理
        if (content.includes('try') && content.includes('catch')) {
            // 有错误处理
        } else if (controllerInfo.functions.length > 0) {
            controllerInfo.issues.push({
                severity: 'high',
                type: 'error_handling',
                message: '控制器函数缺少错误处理',
                suggestion: '添加try-catch块或使用异步错误处理中间件'
            });
        }

        // 检查响应格式
        if (!content.includes('res.json') && !content.includes('res.send')) {
            controllerInfo.issues.push({
                severity: 'medium',
                type: 'response',
                message: '控制器函数缺少响应',
                suggestion: '确保每个控制器函数都发送响应'
            });
        }

        // 检查状态码使用
        if (content.includes('res.status(200)') && !content.includes('res.status(201)') && !content.includes('res.status(204)')) {
            // 只有200状态码，可能需要更多状态码
        }

        this.metrics.controllers.push(controllerInfo);
        this.issues.push(...controllerInfo.issues);
    }

    analyzePerformance() {
        try {
            const packageJsonPath = path.join(this.appPath, 'package.json');
            
            if (!fs.existsSync(packageJsonPath)) {
                this.issues.push({
                    severity: 'high',
                    type: 'dependency',
                    message: '缺少package.json文件',
                    suggestion: '创建package.json文件并添加必要依赖'
                });
                return;
            }

            const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
            
            // 检查依赖版本
            this.checkDependencies(packageJson);
            
            // 检查性能相关依赖
            this.checkPerformanceDependencies(packageJson);
            
        } catch (error) {
            this.issues.push({
                severity: 'medium',
                type: 'analysis',
                message: `性能分析失败: ${error.message}`,
                suggestion: '检查package.json文件格式'
            });
        }
    }

    checkDependencies(packageJson) {
        const dependencies = packageJson.dependencies || {};
        const devDependencies = packageJson.devDependencies || {};

        // 检查Express版本
        const expressVersion = dependencies.express;
        if (expressVersion) {
            if (expressVersion.startsWith('3.') || expressVersion.startsWith('2.')) {
                this.issues.push({
                    severity: 'high',
                    type: 'dependency',
                    message: `Express版本过旧: ${expressVersion}`,
                    suggestion: '升级到Express 4.x或更新版本'
                });
            }
        }

        // 检查安全相关依赖
        const securityDeps = ['helmet', 'bcrypt', 'jsonwebtoken', 'express-rate-limit'];
        for (const dep of securityDeps) {
            if (!dependencies[dep] && !devDependencies[dep]) {
                this.issues.push({
                    severity: 'medium',
                    type: 'security',
                    message: `缺少安全依赖: ${dep}`,
                    suggestion: `添加${dep}增强应用安全性`
                });
            }
        }
    }

    checkPerformanceDependencies(packageJson) {
        const dependencies = packageJson.dependencies || {};
        const devDependencies = packageJson.devDependencies || {};

        // 检查性能相关依赖
        const performanceDeps = ['compression', 'cluster', 'pm2', 'newrelic'];
        for (const dep of performanceDeps) {
            if (!dependencies[dep] && !devDependencies[dep]) {
                this.issues.push({
                    severity: 'low',
                    type: 'performance',
                    message: `缺少性能依赖: ${dep}`,
                    suggestion: `考虑添加${dep}提升应用性能`
                });
            }
        }
    }

    generateReport() {
        const summary = {
            total_issues: this.issues.length,
            critical_issues: this.issues.filter(i => i.severity === 'critical').length,
            high_issues: this.issues.filter(i => i.severity === 'high').length,
            medium_issues: this.issues.filter(i => i.severity === 'medium').length,
            low_issues: this.issues.filter(i => i.severity === 'low').length
        };

        const recommendations = this.generateRecommendations();

        return {
            summary,
            metrics: this.metrics,
            issues: this.issues,
            recommendations,
            health_score: this.calculateHealthScore(summary)
        };
    }

    generateRecommendations() {
        const recommendations = [];
        const issueTypes = {};

        // 统计问题类型
        this.issues.forEach(issue => {
            issueTypes[issue.type] = (issueTypes[issue.type] || 0) + 1;
        });

        // 基于问题类型生成建议
        if (issueTypes.security > 0) {
            recommendations.push({
                priority: 'high',
                type: 'security',
                message: `发现${issueTypes.security}个安全问题`,
                suggestion: '优先修复安全漏洞，添加必要的安全中间件'
            });
        }

        if (issueTypes.performance > 0) {
            recommendations.push({
                priority: 'medium',
                type: 'performance',
                message: `发现${issueTypes.performance}个性能问题`,
                suggestion: '优化代码结构，添加性能监控和缓存'
            });
        }

        if (issueTypes.structure > 0) {
            recommendations.push({
                priority: 'medium',
                type: 'structure',
                message: `发现${issueTypes.structure}个结构问题`,
                suggestion: '重构代码结构，遵循Express最佳实践'
            });
        }

        return recommendations;
    }

    calculateHealthScore(summary) {
        let score = 100;
        
        score -= summary.critical_issues * 20;
        score -= summary.high_issues * 10;
        score -= summary.medium_issues * 5;
        score -= summary.low_issues * 2;
        
        return Math.max(0, score);
    }
}

// Express应用优化器
class ExpressAppOptimizer {
    constructor(appPath) {
        this.appPath = appPath;
    }

    optimizeApplication() {
        const optimizations = [];

        // 检查并优化package.json
        const packageOptimization = this.optimizePackageJson();
        if (packageOptimization) {
            optimizations.push(packageOptimization);
        }

        // 检查并优化中间件配置
        const middlewareOptimization = this.optimizeMiddlewares();
        if (middlewareOptimization) {
            optimizations.push(middlewareOptimization);
        }

        // 检查并优化路由结构
        const routeOptimization = this.optimizeRoutes();
        if (routeOptimization) {
            optimizations.push(routeOptimization);
        }

        return {
            optimizations,
            summary: {
                total_optimizations: optimizations.length,
                estimated_improvements: this.estimateImprovements(optimizations)
            }
        };
    }

    optimizePackageJson() {
        try {
            const packageJsonPath = path.join(this.appPath, 'package.json');
            
            if (!fs.existsSync(packageJsonPath)) {
                return {
                    type: 'dependency',
                    message: '创建package.json文件',
                    suggestion: '添加必要的依赖和脚本'
                };
            }

            const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
            const optimizations = [];

            // 检查并建议性能依赖
            const performanceDeps = ['compression', 'cluster', 'pm2'];
            for (const dep of performanceDeps) {
                if (!packageJson.dependencies[dep] && !packageJson.devDependencies[dep]) {
                    optimizations.push(dep);
                }
            }

            if (optimizations.length > 0) {
                return {
                    type: 'dependency',
                    message: `建议添加性能依赖: ${optimizations.join(', ')}`,
                    suggestion: '这些依赖可以显著提升应用性能'
                };
            }

        } catch (error) {
            return {
                type: 'dependency',
                message: 'package.json格式错误',
                suggestion: '修复JSON格式错误'
            };
        }

        return null;
    }

    optimizeMiddlewares() {
        try {
            const appFile = path.join(this.appPath, 'app.js');
            const serverFile = path.join(this.appPath, 'server.js');
            
            let mainFile = null;
            if (fs.existsSync(appFile)) {
                mainFile = appFile;
            } else if (fs.existsSync(serverFile)) {
                mainFile = serverFile;
            }

            if (!mainFile) {
                return {
                    type: 'middleware',
                    message: '缺少主应用文件',
                    suggestion: '创建app.js或server.js文件'
                };
            }

            const content = fs.readFileSync(mainFile, 'utf8');
            const optimizations = [];

            // 检查压缩中间件
            if (!content.includes('compression')) {
                optimizations.push('compression');
            }

            // 检查集群支持
            if (!content.includes('cluster')) {
                optimizations.push('cluster');
            }

            if (optimizations.length > 0) {
                return {
                    type: 'middleware',
                    message: `建议添加中间件: ${optimizations.join(', ')}`,
                    suggestion: '这些中间件可以提升性能和可靠性'
                };
            }

        } catch (error) {
            return {
                type: 'middleware',
                message: '中间件检查失败',
                suggestion: '检查主应用文件格式'
            };
        }

        return null;
    }

    optimizeRoutes() {
        try {
            const routesPath = path.join(this.appPath, 'routes');
            
            if (!fs.existsSync(routesPath)) {
                return {
                    type: 'structure',
                    message: '缺少routes目录',
                    suggestion: '创建routes目录并组织路由文件'
                };
            }

            const routeFiles = fs.readdirSync(routesPath).filter(file => file.endsWith('.js'));
            
            if (routeFiles.length === 0) {
                return {
                    type: 'structure',
                    message: 'routes目录为空',
                    suggestion: '添加路由文件并定义API路由'
                };
            }

            // 检查路由文件大小
            for (const file of routeFiles) {
                const filePath = path.join(routesPath, file);
                const stats = fs.statSync(filePath);
                
                if (stats.size > 10000) { // 10KB
                    return {
                        type: 'structure',
                        message: `路由文件过大: ${file}`,
                        suggestion: '拆分大型路由文件为多个小文件'
                    };
                }
            }

        } catch (error) {
            return {
                type: 'structure',
                message: '路由检查失败',
                suggestion: '检查routes目录结构'
            };
        }

        return null;
    }

    estimateImprovements(optimizations) {
        const improvements = {
            performance: 0,
            security: 0,
            maintainability: 0
        };

        optimizations.forEach(opt => {
            switch (opt.type) {
                case 'dependency':
                    improvements.performance += 20;
                    break;
                case 'middleware':
                    improvements.performance += 15;
                    improvements.security += 10;
                    break;
                case 'structure':
                    improvements.maintainability += 25;
                    break;
            }
        });

        return improvements;
    }
}

// 使用示例
function main() {
    const analyzer = new ExpressAppAnalyzer('./my-express-app');
    const report = analyzer.analyzeApplication();
    
    console.log('Express应用分析报告:');
    console.log(`健康评分: ${report.health_score}`);
    console.log(`问题总数: ${report.summary.total_issues}`);
    console.log(`严重问题: ${report.summary.critical_issues}`);
    
    console.log('\n优化建议:');
    report.recommendations.forEach(rec => {
        console.log(`- ${rec.message}: ${rec.suggestion}`);
    });
    
    const optimizer = new ExpressAppOptimizer('./my-express-app');
    const optimization = optimizer.optimizeApplication();
    
    console.log('\n优化建议:');
    optimization.optimizations.forEach(opt => {
        console.log(`- ${opt.message}: ${opt.suggestion}`);
    });
}

module.exports = { ExpressAppAnalyzer, ExpressAppOptimizer };
```

### Express性能监控器
```javascript
const express = require('express');
const { performance } = require('perf_hooks');

class ExpressPerformanceMonitor {
    constructor(app) {
        this.app = app;
        this.metrics = {
            requests: [],
            responseTimes: [],
            errorCounts: {},
            routeStats: {}
        };
        this.setupMonitoring();
    }

    setupMonitoring() {
        // 请求计时中间件
        this.app.use((req, res, next) => {
            const start = performance.now();
            
            res.on('finish', () => {
                const duration = performance.now() - start;
                this.recordRequest(req, res, duration);
            });
            
            next();
        });

        // 错误监控中间件
        this.app.use((err, req, res, next) => {
            this.recordError(err, req);
            next(err);
        });
    }

    recordRequest(req, res, duration) {
        const requestInfo = {
            method: req.method,
            url: req.url,
            statusCode: res.statusCode,
            duration: duration,
            timestamp: new Date().toISOString(),
            userAgent: req.get('User-Agent'),
            ip: req.ip || req.connection.remoteAddress
        };

        this.metrics.requests.push(requestInfo);
        this.metrics.responseTimes.push(duration);

        // 记录路由统计
        const routeKey = `${req.method} ${req.route ? req.route.path : req.url}`;
        if (!this.metrics.routeStats[routeKey]) {
            this.metrics.routeStats[routeKey] = {
                count: 0,
                totalDuration: 0,
                avgDuration: 0,
                errors: 0
            };
        }

        const stats = this.metrics.routeStats[routeKey];
        stats.count++;
        stats.totalDuration += duration;
        stats.avgDuration = stats.totalDuration / stats.count;

        if (res.statusCode >= 400) {
            stats.errors++;
        }

        // 保持最近1000个请求
        if (this.metrics.requests.length > 1000) {
            this.metrics.requests.shift();
        }

        if (this.metrics.responseTimes.length > 1000) {
            this.metrics.responseTimes.shift();
        }
    }

    recordError(err, req) {
        const errorKey = err.name || 'UnknownError';
        this.metrics.errorCounts[errorKey] = (this.metrics.errorCounts[errorKey] || 0) + 1;
    }

    getMetrics() {
        const responseTimeStats = this.calculateResponseTimeStats();
        const errorRate = this.calculateErrorRate();
        const topRoutes = this.getTopRoutes();

        return {
            totalRequests: this.metrics.requests.length,
            responseTimeStats,
            errorRate,
            errorCounts: this.metrics.errorCounts,
            topRoutes,
            timestamp: new Date().toISOString()
        };
    }

    calculateResponseTimeStats() {
        const times = this.metrics.responseTimes;
        if (times.length === 0) {
            return { avg: 0, min: 0, max: 0, p95: 0, p99: 0 };
        }

        const sorted = times.sort((a, b) => a - b);
        const len = sorted.length;

        return {
            avg: times.reduce((sum, time) => sum + time, 0) / len,
            min: sorted[0],
            max: sorted[len - 1],
            p95: sorted[Math.floor(len * 0.95)],
            p99: sorted[Math.floor(len * 0.99)]
        };
    }

    calculateErrorRate() {
        const totalRequests = this.metrics.requests.length;
        const errorRequests = this.metrics.requests.filter(req => req.statusCode >= 400).length;
        
        return totalRequests > 0 ? (errorRequests / totalRequests) * 100 : 0;
    }

    getTopRoutes() {
        const routes = Object.entries(this.metrics.routeStats);
        return routes
            .sort(([,a], [,b]) => b.count - a.count)
            .slice(0, 10)
            .map(([route, stats]) => ({ route, ...stats }));
    }
}

module.exports = ExpressPerformanceMonitor;
```

## Express.js服务最佳实践

### 应用结构
1. **模块化设计**: 按功能模块组织代码
2. **分层架构**: 控制器、服务、数据层分离
3. **配置管理**: 环境变量和配置文件分离
4. **错误处理**: 统一的错误处理机制
5. **日志记录**: 结构化日志和监控

### 路由设计
1. **RESTful规范**: 遵循REST API设计原则
2. **资源命名**: 使用名词复数形式
3. **HTTP方法**: 正确使用GET、POST、PUT、DELETE
4. **状态码**: 返回适当的HTTP状态码
5. **版本控制**: API版本管理策略

### 中间件配置
1. **安全中间件**: helmet、cors、rate limiting
2. **日志中间件**: morgan、winston
3. **解析中间件**: body-parser、cookie-parser
4. **性能中间件**: compression、cluster
5. **自定义中间件**: 业务逻辑中间件

### 性能优化
1. **异步操作**: 避免阻塞I/O操作
2. **缓存策略**: 内存缓存和Redis缓存
3. **数据库优化**: 连接池和查询优化
4. **集群模式**: 使用cluster模块
5. **监控告警**: 性能监控和告警

## 相关技能

- **restful-api-design** - RESTful API设计
- **api-validator** - API验证器
- **nodejs-development** - Node.js开发
- **microservices** - 微服务架构
