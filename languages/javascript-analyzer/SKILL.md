---
name: JavaScript分析器
description: "当进行JavaScript代码审查、性能优化、浏览器兼容性检查或安全审计时，分析JavaScript代码质量和最佳实践。"
license: MIT
---

# JavaScript分析器技能

## 概述
JavaScript的灵活性是一把双刃剑。分析代码以防止运行时意外。

**核心原则**: JavaScript的灵活性是一把双刃剑。分析代码以防止运行时意外。

## 何时使用

**始终:**
- JavaScript代码审查
- 性能优化
- 浏览器兼容性检查
- 安全审计
- 代码重构
- 架构设计评审

**触发短语:**
- "分析JavaScript代码"
- "JavaScript性能优化"
- "代码质量检查"
- "JavaScript最佳实践"
- "浏览器兼容性"
- "安全漏洞检查"

## JavaScript分析功能

### 代码质量
- ESLint规则检查
- 代码风格统一
- 复杂度分析
- 重复代码检测
- 最佳实践验证

### 性能分析
- 执行时间测量
- 内存泄漏检测
- DOM操作优化
- 网络请求分析
- 渲染性能检查

### 安全检查
- XSS漏洞检测
- CSRF防护验证
- 输入验证检查
- 依赖安全扫描
- 敏感信息泄露

## 常见JavaScript问题

### 异步处理问题
```
问题:
异步操作处理不当

错误示例:
- 回调地狱
- Promise未正确处理
- async/await滥用
- 错误处理缺失

解决方案:
1. 使用async/await替代回调
2. 正确处理Promise错误
3. 避免阻塞主线程
4. 实现错误边界
```

### 内存泄漏
```
问题:
内存使用不当导致泄漏

错误示例:
- 事件监听器未移除
- 定时器未清理
- 闭包引用过多
- DOM节点引用未释放

解决方案:
1. 及时清理事件监听器
2. 清理定时器和间隔器
3. 避免不必要的闭包
4. 使用WeakMap/WeakSet
```

### 类型安全问题
```
问题:
JavaScript动态类型导致错误

错误示例:
- 类型转换错误
- 未定义属性访问
- 参数类型不匹配
- 返回值类型不确定

解决方案:
1. 使用TypeScript
2. 添加JSDoc类型注解
3. 运行时类型检查
4. 使用PropTypes
```

## 代码实现示例

### JavaScript代码分析器
```javascript
const fs = require('fs');
const path = require('path');
const { parse } = require('@babel/parser');
const traverse = require('@babel/traverse').default;

class JavaScriptAnalyzer {
    constructor(options = {}) {
        this.options = {
            ecmaVersion: 2020,
            sourceType: 'module',
            plugins: [
                'jsx',
                'typescript',
                'decorators-legacy',
                'classProperties',
                'objectRestSpread',
                'asyncGenerators',
                'functionBind',
                'exportDefaultFrom',
                'exportNamespaceFrom',
                'dynamicImport',
                'nullishCoalescingOperator',
                'optionalChaining'
            ],
            ...options
        };
        this.issues = [];
        this.metrics = {
            totalFiles: 0,
            totalLines: 0,
            totalFunctions: 0,
            totalClasses: 0,
            complexityScore: 0,
            maintainabilityIndex: 0
        };
    }

    analyzeFile(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const ast = this.parseCode(content, filePath);
            
            if (!ast) {
                return {
                    file: filePath,
                    error: 'Failed to parse',
                    issues: []
                };
            }

            // 重置问题列表
            this.issues = [];

            // 执行各种分析
            this.analyzeCodeQuality(ast, filePath);
            this.analyzePerformance(ast, filePath);
            this.analyzeSecurity(ast, filePath);
            this.analyzeComplexity(ast, filePath);
            this.analyzeBestPractices(ast, filePath);

            return {
                file: filePath,
                issues: this.issues,
                metrics: this.calculateFileMetrics(ast, content)
            };

        } catch (error) {
            return {
                file: filePath,
                error: error.message,
                issues: [{
                    type: 'parse_error',
                    severity: 'error',
                    message: `解析错误: ${error.message}`,
                    line: error.loc?.line || 0,
                    column: error.loc?.column || 0
                }]
            };
        }
    }

    analyzeDirectory(directory) {
        const results = [];
        const allIssues = [];

        function scanDirectory(dir) {
            const items = fs.readdirSync(dir);
            
            for (const item of items) {
                const fullPath = path.join(dir, item);
                const stat = fs.statSync(fullPath);
                
                if (stat.isDirectory()) {
                    // 跳过node_modules等目录
                    if (!item.startsWith('.') && item !== 'node_modules') {
                        scanDirectory(fullPath);
                    }
                } else if (isJavaScriptFile(item)) {
                    const result = this.analyzeFile(fullPath);
                    results.push(result);
                    allIssues.push(...(result.issues || []));
                }
            }
        }

        function isJavaScriptFile(fileName) {
            const ext = path.extname(fileName);
            return ['.js', '.jsx', '.ts', '.tsx', '.mjs'].includes(ext);
        }

        scanDirectory.call(this, directory);

        return {
            directory,
            files: results,
            summary: this.generateSummary(allIssues),
            recommendations: this.generateRecommendations(allIssues)
        };
    }

    parseCode(content, filePath) {
        try {
            return parse(content, {
                ...this.options,
                filename: filePath
            });
        } catch (error) {
            console.error(`解析文件失败: ${filePath}`, error);
            return null;
        }
    }

    analyzeCodeQuality(ast, filePath) {
        // 检查变量命名
        this.checkVariableNaming(ast, filePath);
        
        // 检查函数长度
        this.checkFunctionLength(ast, filePath);
        
        // 检查代码重复
        this.checkCodeDuplication(ast, filePath);
        
        // 检查未使用变量
        this.checkUnusedVariables(ast, filePath);
    }

    checkVariableNaming(ast, filePath) {
        const namingPatterns = {
            camelCase: /^[a-z][a-zA-Z0-9]*$/,
            PascalCase: /^[A-Z][a-zA-Z0-9]*$/,
            UPPER_CASE: /^[A-Z][A-Z0-9_]*$/,
            snake_case: /^[a-z][a-z0-9_]*$/
        };

        traverse(ast, {
            VariableDeclarator(path) {
                const id = path.node.id;
                if (id.type === 'Identifier') {
                    const name = id.name;
                    
                    // 检查常量命名
                    if (path.parent.kind === 'const') {
                        if (!namingPatterns.UPPER_CASE.test(name) && name !== name.toLowerCase()) {
                            this.issues.push({
                                type: 'naming',
                                severity: 'warning',
                                message: `常量"${name}"应使用UPPER_CASE命名`,
                                line: id.loc?.line || 0,
                                column: id.loc?.column || 0,
                                suggestion: `改为${name.toUpperCase()}`
                            });
                        }
                    }
                    // 检查变量命名
                    else if (path.parent.kind === 'let' || path.parent.kind === 'var') {
                        if (!namingPatterns.camelCase.test(name)) {
                            this.issues.push({
                                type: 'naming',
                                severity: 'info',
                                message: `变量"${name}"应使用camelCase命名`,
                                line: id.loc?.line || 0,
                                column: id.loc?.column || 0,
                                suggestion: `改为${this.toCamelCase(name)}`
                            });
                        }
                    }
                }
            }
        });
    }

    checkFunctionLength(ast, filePath) {
        traverse(ast, {
            FunctionDeclaration(path) {
                this.checkFunctionSize(path, filePath);
            },
            FunctionExpression(path) {
                this.checkFunctionSize(path, filePath);
            },
            ArrowFunctionExpression(path) {
                this.checkFunctionSize(path, filePath);
            }
        });
    }

    checkFunctionSize(path, filePath) {
        const functionNode = path.node;
        const startLine = functionNode.loc?.start.line || 0;
        const endLine = functionNode.loc?.end.line || 0;
        const lines = endLine - startLine + 1;

        if (lines > 50) {
            const functionName = functionNode.id?.name || '匿名函数';
            this.issues.push({
                type: 'complexity',
                severity: 'warning',
                message: `函数"${functionName}"过长(${lines}行)，建议拆分`,
                line: startLine,
                column: 0,
                suggestion: '将函数拆分为更小的函数'
            });
        }
    }

    checkCodeDuplication(ast, filePath) {
        // 简化实现：检查重复的函数调用
        const functionCalls = new Map();
        
        traverse(ast, {
            CallExpression(path) {
                const callee = path.node.callee;
                if (callee.type === 'Identifier') {
                    const name = callee.name;
                    const line = callee.loc?.line || 0;
                    
                    if (!functionCalls.has(name)) {
                        functionCalls.set(name, []);
                    }
                    functionCalls.get(name).push(line);
                }
            }
        });

        // 检查是否有重复调用
        for (const [name, lines] of functionCalls) {
            if (lines.length > 5) {
                this.issues.push({
                    type: 'duplication',
                    severity: 'info',
                    message: `函数"${name}"被调用${lines.length}次，考虑提取为常量或缓存`,
                    line: Math.min(...lines),
                    column: 0,
                    suggestion: '考虑缓存函数结果或提取为常量'
                });
            }
        }
    }

    checkUnusedVariables(ast, filePath) {
        const declaredVariables = new Map();
        const usedVariables = new Set();

        // 收集声明的变量
        traverse(ast, {
            VariableDeclarator(path) {
                const id = path.node.id;
                if (id.type === 'Identifier') {
                    declaredVariables.set(id.name, {
                        line: id.loc?.line || 0,
                        column: id.loc?.column || 0
                    });
                }
            }
        });

        // 收集使用的变量
        traverse(ast, {
            Identifier(path) {
                if (path.isReferencedIdentifier()) {
                    usedVariables.add(path.node.name);
                }
            }
        });

        // 检查未使用的变量
        for (const [name, location] of declaredVariables) {
            if (!usedVariables.has(name) && !name.startsWith('_')) {
                this.issues.push({
                    type: 'unused_variable',
                    severity: 'warning',
                    message: `变量"${name}"已声明但未使用`,
                    line: location.line,
                    column: location.column,
                    suggestion: '删除未使用的变量或添加前缀_'
                });
            }
        }
    }

    analyzePerformance(ast, filePath) {
        this.checkDOMOperations(ast, filePath);
        this.checkAsyncOperations(ast, filePath);
        this.checkMemoryLeaks(ast, filePath);
    }

    checkDOMOperations(ast, filePath) {
        traverse(ast, {
            CallExpression(path) {
                const callee = path.node.callee;
                
                // 检查频繁的DOM查询
                if (callee.type === 'MemberExpression') {
                    const object = callee.object;
                    const property = callee.property;
                    
                    if (object.type === 'Identifier' && object.name === 'document') {
                        if (property.type === 'Identifier' && 
                            ['querySelector', 'querySelectorAll', 'getElementById'].includes(property.name)) {
                            
                            this.issues.push({
                                type: 'performance',
                                severity: 'info',
                                message: '频繁的DOM查询可能影响性能',
                                line: property.loc?.line || 0,
                                column: property.loc?.column || 0,
                                suggestion: '缓存DOM查询结果'
                            });
                        }
                    }
                }
            }
        });
    }

    checkAsyncOperations(ast, filePath) {
        traverse(ast, {
            CallExpression(path) {
                const callee = path.node.callee;
                
                // 检查setTimeout/setInterval
                if (callee.type === 'Identifier' && 
                    ['setTimeout', 'setInterval'].includes(callee.name)) {
                    
                    this.issues.push({
                        type: 'performance',
                        severity: 'warning',
                        message: `使用${callee.name}时确保清理定时器`,
                        line: callee.loc?.line || 0,
                        column: callee.loc?.column || 0,
                        suggestion: '在组件卸载时清理定时器'
                    });
                }
            }
        });
    }

    checkMemoryLeaks(ast, filePath) {
        traverse(ast, {
            CallExpression(path) {
                const callee = path.node.callee;
                
                // 检查事件监听器
                if (callee.type === 'MemberExpression') {
                    const property = callee.property;
                    if (property.type === 'Identifier' && property.name === 'addEventListener') {
                        this.issues.push({
                            type: 'memory_leak',
                            severity: 'warning',
                            message: '添加事件监听器时确保在适当时候移除',
                            line: property.loc?.line || 0,
                            column: property.loc?.column || 0,
                            suggestion: '在组件卸载时调用removeEventListener'
                        });
                    }
                }
            }
        });
    }

    analyzeSecurity(ast, filePath) {
        this.checkXSSVulnerabilities(ast, filePath);
        this.checkEvalUsage(ast, filePath);
        this.checkInputValidation(ast, filePath);
    }

    checkXSSVulnerabilities(ast, filePath) {
        traverse(ast, {
            CallExpression(path) {
                const callee = path.node.callee;
                
                // 检查innerHTML使用
                if (callee.type === 'MemberExpression') {
                    const property = callee.property;
                    if (property.type === 'Identifier' && property.name === 'innerHTML') {
                        this.issues.push({
                            type: 'security',
                            severity: 'error',
                            message: '使用innerHTML可能导致XSS攻击',
                            line: property.loc?.line || 0,
                            column: property.loc?.column || 0,
                            suggestion: '使用textContent或进行输入验证'
                        });
                    }
                }
            }
        });
    }

    checkEvalUsage(ast, filePath) {
        traverse(ast, {
            CallExpression(path) {
                const callee = path.node.callee;
                
                if (callee.type === 'Identifier' && callee.name === 'eval') {
                    this.issues.push({
                        type: 'security',
                        severity: 'error',
                        message: '使用eval存在安全风险',
                        line: callee.loc?.line || 0,
                        column: callee.loc?.column || 0,
                        suggestion: '避免使用eval，使用JSON.parse等替代方案'
                    });
                }
            }
        });
    }

    checkInputValidation(ast, filePath) {
        // 简化实现：检查用户输入处理
        traverse(ast, {
            CallExpression(path) {
                const callee = path.node.callee;
                
                // 检查可能的用户输入处理
                if (callee.type === 'MemberExpression') {
                    const object = callee.object;
                    const property = callee.property;
                    
                    if (object.type === 'Identifier' && object.name === 'document') {
                        if (property.type === 'Identifier' && property.name === 'getElementById') {
                            this.issues.push({
                                type: 'security',
                                severity: 'info',
                                message: '处理DOM输入时进行验证',
                                line: property.loc?.line || 0,
                                column: property.loc?.column || 0,
                                suggestion: '验证用户输入以防止注入攻击'
                            });
                        }
                    }
                }
            }
        });
    }

    analyzeComplexity(ast, filePath) {
        this.calculateCyclomaticComplexity(ast, filePath);
        this.checkNestingDepth(ast, filePath);
    }

    calculateCyclomaticComplexity(ast, filePath) {
        traverse(ast, {
            FunctionDeclaration(path) {
                const complexity = this.computeComplexity(path.node);
                const functionName = path.node.id?.name || '匿名函数';
                
                if (complexity > 10) {
                    this.issues.push({
                        type: 'complexity',
                        severity: 'warning',
                        message: `函数"${functionName}"圈复杂度过高(${complexity})`,
                        line: path.node.loc?.start.line || 0,
                        column: 0,
                        suggestion: '简化函数逻辑或拆分为多个函数'
                    });
                }
            }
        });
    }

    computeComplexity(node) {
        let complexity = 1; // 基础复杂度
        
        for (const child of node.body || []) {
            complexity += this.computeNodeComplexity(child);
        }
        
        return complexity;
    }

    computeNodeComplexity(node) {
        let complexity = 0;
        
        switch (node.type) {
            case 'IfStatement':
            case 'WhileStatement':
            case 'ForStatement':
            case 'ForInStatement':
            case 'ForOfStatement':
            case 'SwitchCase':
            case 'CatchClause':
                complexity += 1;
                break;
            case 'LogicalExpression':
                if (node.operator === '&&' || node.operator === '||') {
                    complexity += 1;
                }
                break;
        }
        
        // 递归计算子节点复杂度
        for (const key in node) {
            if (node[key] && typeof node[key] === 'object') {
                if (Array.isArray(node[key])) {
                    for (const child of node[key]) {
                        complexity += this.computeNodeComplexity(child);
                    }
                } else {
                    complexity += this.computeNodeComplexity(node[key]);
                }
            }
        }
        
        return complexity;
    }

    checkNestingDepth(ast, filePath) {
        traverse(ast, {
            IfStatement(path) {
                const depth = this.calculateNestingDepth(path);
                if (depth > 4) {
                    this.issues.push({
                        type: 'complexity',
                        severity: 'warning',
                        message: `嵌套层次过深(${depth}层)`,
                        line: path.node.loc?.start.line || 0,
                        column: 0,
                        suggestion: '使用早期返回或提取函数'
                    });
                }
            }
        });
    }

    calculateNestingDepth(path, currentDepth = 0) {
        let maxDepth = currentDepth;
        
        for (const child of path.get('body').get('body') || []) {
            if (child.isIfStatement() || child.isWhileStatement() || child.isForStatement()) {
                const childDepth = this.calculateNestingDepth(child, currentDepth + 1);
                maxDepth = Math.max(maxDepth, childDepth);
            }
        }
        
        return maxDepth;
    }

    analyzeBestPractices(ast, filePath) {
        this.checkConsoleUsage(ast, filePath);
        this.checkErrorHandling(ast, filePath);
        this.checkStrictMode(ast, filePath);
    }

    checkConsoleUsage(ast, filePath) {
        traverse(ast, {
            CallExpression(path) {
                const callee = path.node.callee;
                
                if (callee.type === 'MemberExpression') {
                    const object = callee.object;
                    const property = callee.property;
                    
                    if (object.type === 'Identifier' && object.name === 'console') {
                        this.issues.push({
                            type: 'best_practice',
                            severity: 'info',
                            message: '生产环境应移除console语句',
                            line: property.loc?.line || 0,
                            column: property.loc?.column || 0,
                            suggestion: '使用适当的日志库或条件编译'
                        });
                    }
                }
            }
        });
    }

    checkErrorHandling(ast, filePath) {
        traverse(ast, {
            CallExpression(path) {
                const callee = path.node.callee;
                
                // 检查Promise链
                if (callee.type === 'MemberExpression' && 
                    callee.property.type === 'Identifier' && 
                    callee.property.name === 'then') {
                    
                    // 检查是否有catch
                    const parent = path.parentPath;
                    let hasCatch = false;
                    
                    if (parent && parent.type === 'CallExpression') {
                        const parentCallee = parent.node.callee;
                        if (parentCallee.type === 'MemberExpression' && 
                            parentCallee.property.type === 'Identifier' && 
                            parentCallee.property.name === 'catch') {
                            hasCatch = true;
                        }
                    }
                    
                    if (!hasCatch) {
                        this.issues.push({
                            type: 'best_practice',
                            severity: 'warning',
                            message: 'Promise链缺少错误处理',
                            line: callee.property.loc?.line || 0,
                            column: callee.property.loc?.column || 0,
                            suggestion: '添加catch块处理错误'
                        });
                    }
                }
            }
        });
    }

    checkStrictMode(ast, filePath) {
        // 检查是否使用严格模式
        let hasStrictMode = false;
        
        traverse(ast, {
            ExpressionStatement(path) {
                const expression = path.node.expression;
                if (expression.type === 'Literal' && expression.value === 'use strict') {
                    hasStrictMode = true;
                }
            }
        });

        if (!hasStrictMode) {
            this.issues.push({
                type: 'best_practice',
                severity: 'info',
                message: '建议使用严格模式',
                line: 1,
                column: 0,
                suggestion: '在文件顶部添加"use strict";'
            });
        }
    }

    calculateFileMetrics(ast, content) {
        const lines = content.split('\n').length;
        let functions = 0;
        let classes = 0;
        let complexity = 0;

        traverse(ast, {
            FunctionDeclaration() { functions++; },
            FunctionExpression() { functions++; },
            ArrowFunctionExpression() { functions++; },
            ClassDeclaration() { classes++; }
        });

        return {
            lines,
            functions,
            classes,
            complexity
        };
    }

    generateSummary(issues) {
        const summary = {
            total: issues.length,
            byType: {},
            bySeverity: {
                error: 0,
                warning: 0,
                info: 0
            }
        };

        for (const issue of issues) {
            summary.bySeverity[issue.severity]++;
            
            if (!summary.byType[issue.type]) {
                summary.byType[issue.type] = 0;
            }
            summary.byType[issue.type]++;
        }

        return summary;
    }

    generateRecommendations(issues) {
        const recommendations = [];
        const issueCounts = {};

        // 统计问题类型
        for (const issue of issues) {
            if (!issueCounts[issue.type]) {
                issueCounts[issue.type] = 0;
            }
            issueCounts[issue.type]++;
        }

        // 生成建议
        if (issueCounts.complexity > 3) {
            recommendations.push({
                priority: 'high',
                message: '发现多个复杂度问题，建议重构代码',
                action: '拆分大函数，简化逻辑，减少嵌套'
            });
        }

        if (issueCounts.security > 0) {
            recommendations.push({
                priority: 'critical',
                message: '发现安全问题，需要立即修复',
                action: '修复XSS漏洞，替换eval使用，添加输入验证'
            });
        }

        if (issueCounts.performance > 5) {
            recommendations.push({
                priority: 'medium',
                message: '发现多个性能问题，建议优化',
                action: '缓存DOM查询，优化异步操作，清理内存泄漏'
            });
        }

        if (issueCounts.best_practice > 3) {
            recommendations.push({
                priority: 'low',
                message: '建议遵循最佳实践',
                action: '移除console语句，添加错误处理，使用严格模式'
            });
        }

        return recommendations;
    }

    toCamelCase(str) {
        return str.replace(/_([a-z])/g, (match, letter) => letter.toUpperCase());
    }
}

// 使用示例
function main() {
    const analyzer = new JavaScriptAnalyzer();
    
    // 分析单个文件
    const fileResult = analyzer.analyzeFile('./example.js');
    console.log(`文件: ${fileResult.file}`);
    console.log(`问题数: ${fileResult.issues.length}`);
    
    // 分析整个目录
    const directoryResult = analyzer.analyzeDirectory('./src');
    console.log(`目录: ${directoryResult.directory}`);
    console.log(`总问题数: ${directoryResult.summary.total}`);
    
    // 打印建议
    console.log('\n建议:');
    for (const rec of directoryResult.recommendations) {
        console.log(`- [${rec.priority.toUpperCase()}] ${rec.message}`);
        console.log(`  建议: ${rec.action}`);
    }
}

module.exports = JavaScriptAnalyzer;

if (require.main === module) {
    main();
}
```

### JavaScript性能分析器
```javascript
class JavaScriptPerformanceAnalyzer {
    constructor() {
        this.metrics = new Map();
        this.observers = new Map();
    }

    // 函数性能监控
    profileFunction(name, fn) {
        const wrappedFn = async (...args) => {
            const startTime = performance.now();
            const startMemory = this.getMemoryUsage();
            
            try {
                const result = await fn(...args);
                const endTime = performance.now();
                const endMemory = this.getMemoryUsage();
                
                this.recordMetric(name, {
                    executionTime: endTime - startTime,
                    memoryDelta: endMemory - startMemory,
                    success: true
                });
                
                return result;
            } catch (error) {
                const endTime = performance.now();
                const endMemory = this.getMemoryUsage();
                
                this.recordMetric(name, {
                    executionTime: endTime - startTime,
                    memoryDelta: endMemory - startMemory,
                    success: false,
                    error: error.message
                });
                
                throw error;
            }
        };
        
        return wrappedFn;
    }

    // DOM性能监控
    observeDOMPerformance(container) {
        if (!window.PerformanceObserver) {
            console.warn('PerformanceObserver not supported');
            return;
        }

        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'measure') {
                    this.recordMetric('dom_operation', {
                        name: entry.name,
                        duration: entry.duration,
                        startTime: entry.startTime
                    });
                }
            }
        });

        observer.observe({ entryTypes: ['measure'] });
        this.observers.set('dom', observer);

        return {
            startMeasure: (name) => performance.mark(`${name}-start`),
            endMeasure: (name) => {
                performance.mark(`${name}-end`);
                performance.measure(name, `${name}-start`, `${name}-end`);
            }
        };
    }

    // 网络性能监控
    observeNetworkPerformance() {
        if (!window.PerformanceObserver) {
            return null;
        }

        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'resource') {
                    this.recordMetric('network_request', {
                        name: entry.name,
                        duration: entry.duration,
                        size: entry.transferSize || 0,
                        type: this.getResourceType(entry.name)
                    });
                }
            }
        });

        observer.observe({ entryTypes: ['resource'] });
        this.observers.set('network', observer);

        return observer;
    }

    // 内存监控
    observeMemoryUsage() {
        if (!window.performance || !window.performance.memory) {
            console.warn('Memory monitoring not supported');
            return null;
        }

        const checkInterval = setInterval(() => {
            const memory = {
                used: window.performance.memory.usedJSHeapSize,
                total: window.performance.memory.totalJSHeapSize,
                limit: window.performance.memory.jsHeapSizeLimit
            };

            this.recordMetric('memory_usage', {
                used: memory.used,
                total: memory.total,
                limit: memory.limit,
                usageRatio: memory.used / memory.limit
            });

            // 内存使用率过高警告
            if (memory.usageRatio > 0.9) {
                console.warn('High memory usage detected:', memory.usageRatio);
            }
        }, 5000);

        return () => clearInterval(checkInterval);
    }

    // 记录指标
    recordMetric(type, data) {
        if (!this.metrics.has(type)) {
            this.metrics.set(type, []);
        }
        
        this.metrics.get(type).push({
            timestamp: Date.now(),
            ...data
        });

        // 保持最近100条记录
        const records = this.metrics.get(type);
        if (records.length > 100) {
            records.shift();
        }
    }

    // 获取内存使用情况
    getMemoryUsage() {
        if (window.performance && window.performance.memory) {
            return window.performance.memory.usedJSHeapSize;
        }
        return 0;
    }

    // 获取资源类型
    getResourceType(url) {
        const extension = url.split('.').pop().toLowerCase();
        const typeMap = {
            'js': 'script',
            'css': 'stylesheet',
            'png': 'image',
            'jpg': 'image',
            'jpeg': 'image',
            'gif': 'image',
            'svg': 'image',
            'woff': 'font',
            'woff2': 'font',
            'ttf': 'font'
        };
        
        return typeMap[extension] || 'other';
    }

    // 生成性能报告
    generateReport() {
        const report = {
            timestamp: Date.now(),
            metrics: {},
            summary: {},
            recommendations: []
        };

        // 处理各类指标
        for (const [type, records] of this.metrics) {
            report.metrics[type] = this.analyzeMetrics(type, records);
        }

        // 生成摘要
        report.summary = this.generateSummary(report.metrics);

        // 生成建议
        report.recommendations = this.generateRecommendations(report.metrics);

        return report;
    }

    analyzeMetrics(type, records) {
        if (records.length === 0) {
            return { count: 0 };
        }

        const analysis = {
            count: records.length,
            latest: records[records.length - 1],
            average: {},
            min: {},
            max: {}
        };

        // 根据类型分析不同指标
        switch (type) {
            case 'function_call':
                this.analyzeFunctionMetrics(records, analysis);
                break;
            case 'dom_operation':
                this.analyzeDOMMetrics(records, analysis);
                break;
            case 'network_request':
                this.analyzeNetworkMetrics(records, analysis);
                break;
            case 'memory_usage':
                this.analyzeMemoryMetrics(records, analysis);
                break;
        }

        return analysis;
    }

    analyzeFunctionMetrics(records, analysis) {
        const times = records.map(r => r.executionTime);
        const memoryDeltas = records.map(r => r.memoryDelta);
        const successRate = records.filter(r => r.success).length / records.length;

        analysis.average = {
            executionTime: this.average(times),
            memoryDelta: this.average(memoryDeltas),
            successRate: successRate
        };

        analysis.min = {
            executionTime: Math.min(...times),
            memoryDelta: Math.min(...memoryDeltas)
        };

        analysis.max = {
            executionTime: Math.max(...times),
            memoryDelta: Math.max(...memoryDeltas)
        };
    }

    analyzeDOMMetrics(records, analysis) {
        const durations = records.map(r => r.duration);
        
        analysis.average = {
            duration: this.average(durations)
        };

        analysis.min = {
            duration: Math.min(...durations)
        };

        analysis.max = {
            duration: Math.max(...durations)
        };

        // 找出最慢的DOM操作
        analysis.slowest = records.reduce((slowest, current) => 
            current.duration > (slowest?.duration || 0) ? current : slowest, null);
    }

    analyzeNetworkMetrics(records, analysis) {
        const durations = records.map(r => r.duration);
        const sizes = records.map(r => r.size);
        
        analysis.average = {
            duration: this.average(durations),
            size: this.average(sizes)
        };

        analysis.min = {
            duration: Math.min(...durations),
            size: Math.min(...sizes)
        };

        analysis.max = {
            duration: Math.max(...durations),
            size: Math.max(...sizes)
        };

        // 按类型分组
        analysis.byType = this.groupByType(records);
    }

    analyzeMemoryMetrics(records, analysis) {
        const usageRatios = records.map(r => r.usageRatio);
        
        analysis.average = {
            usageRatio: this.average(usageRatios),
            usedMB: this.average(records.map(r => r.used / 1024 / 1024))
        };

        analysis.min = {
            usageRatio: Math.min(...usageRatios)
        };

        analysis.max = {
            usageRatio: Math.max(...usageRatios)
        };

        // 内存趋势
        analysis.trend = this.calculateTrend(records.map(r => r.used));
    }

    groupByType(records) {
        const grouped = {};
        
        for (const record of records) {
            if (!grouped[record.type]) {
                grouped[record.type] = [];
            }
            grouped[record.type].push(record);
        }

        // 计算每组的平均值
        for (const type in grouped) {
            const typeRecords = grouped[type];
            grouped[type] = {
                count: typeRecords.length,
                averageDuration: this.average(typeRecords.map(r => r.duration)),
                averageSize: this.average(typeRecords.map(r => r.size))
            };
        }

        return grouped;
    }

    calculateTrend(values) {
        if (values.length < 2) return 'stable';
        
        const first = values[0];
        const last = values[values.length - 1];
        const change = (last - first) / first;
        
        if (change > 0.1) return 'increasing';
        if (change < -0.1) return 'decreasing';
        return 'stable';
    }

    average(values) {
        return values.reduce((sum, val) => sum + val, 0) / values.length;
    }

    generateSummary(metrics) {
        const summary = {
            totalIssues: 0,
            performanceScore: 100,
            criticalIssues: []
        };

        // 评估函数性能
        if (metrics.function_call) {
            const fnMetrics = metrics.function_call;
            if (fnMetrics.average.executionTime > 100) {
                summary.criticalIssues.push({
                    type: 'slow_functions',
                    message: '函数执行时间过长',
                    value: fnMetrics.average.executionTime
                });
                summary.performanceScore -= 20;
            }
        }

        // 评估DOM性能
        if (metrics.dom_operation) {
            const domMetrics = metrics.dom_operation;
            if (domMetrics.average.duration > 50) {
                summary.criticalIssues.push({
                    type: 'slow_dom',
                    message: 'DOM操作过慢',
                    value: domMetrics.average.duration
                });
                summary.performanceScore -= 15;
            }
        }

        // 评估网络性能
        if (metrics.network_request) {
            const netMetrics = metrics.network_request;
            if (netMetrics.average.duration > 1000) {
                summary.criticalIssues.push({
                    type: 'slow_network',
                    message: '网络请求过慢',
                    value: netMetrics.average.duration
                });
                summary.performanceScore -= 25;
            }
        }

        // 评估内存使用
        if (metrics.memory_usage) {
            const memMetrics = metrics.memory_usage;
            if (memMetrics.average.usageRatio > 0.8) {
                summary.criticalIssues.push({
                    type: 'high_memory',
                    message: '内存使用率过高',
                    value: memMetrics.average.usageRatio
                });
                summary.performanceScore -= 30;
            }
        }

        summary.totalIssues = summary.criticalIssues.length;
        return summary;
    }

    generateRecommendations(metrics) {
        const recommendations = [];

        // 函数性能建议
        if (metrics.function_call && metrics.function_call.average.executionTime > 100) {
            recommendations.push({
                type: 'function',
                priority: 'high',
                message: '优化函数执行性能',
                suggestions: [
                    '使用缓存避免重复计算',
                    '优化算法复杂度',
                    '考虑使用Web Workers'
                ]
            });
        }

        // DOM性能建议
        if (metrics.dom_operation && metrics.dom_operation.average.duration > 50) {
            recommendations.push({
                type: 'dom',
                priority: 'medium',
                message: '优化DOM操作性能',
                suggestions: [
                    '减少DOM查询次数',
                    '使用DocumentFragment批量操作',
                    '避免强制同步布局'
                ]
            });
        }

        // 网络性能建议
        if (metrics.network_request && metrics.network_request.average.duration > 1000) {
            recommendations.push({
                type: 'network',
                priority: 'high',
                message: '优化网络请求性能',
                suggestions: [
                    '启用资源压缩',
                    '使用CDN加速',
                    '实现资源缓存',
                    '优化图片大小'
                ]
            });
        }

        // 内存使用建议
        if (metrics.memory_usage && metrics.memory_usage.average.usageRatio > 0.8) {
            recommendations.push({
                type: 'memory',
                priority: 'critical',
                message: '优化内存使用',
                suggestions: [
                    '及时清理事件监听器',
                    '避免内存泄漏',
                    '使用对象池复用对象',
                    '优化数据结构'
                ]
            });
        }

        return recommendations;
    }

    // 清理资源
    cleanup() {
        for (const observer of this.observers.values()) {
            observer.disconnect();
        }
        this.observers.clear();
        this.metrics.clear();
    }
}

// 使用示例
const perfAnalyzer = new JavaScriptPerformanceAnalyzer();

// 性能监控示例
const slowFunction = perfAnalyzer.profileFunction('slow_function', async () => {
    // 模拟慢操作
    await new Promise(resolve => setTimeout(resolve, 100));
    return Math.random();
});

// DOM性能监控
const domMonitor = perfAnalyzer.observeDOMPerformance(document.body);
domMonitor.startMeasure('dom-update');
// ... DOM操作
domMonitor.endMeasure('dom-update');

// 生成报告
setTimeout(() => {
    const report = perfAnalyzer.generateReport();
    console.log('性能报告:', report);
}, 5000);

module.exports = JavaScriptPerformanceAnalyzer;
```

## JavaScript最佳实践

### 代码质量
1. **ESLint配置**: 使用ESLint保证代码质量
2. **Prettier格式化**: 统一代码风格
3. **TypeScript**: 添加类型安全
4. **单元测试**: 保证代码可靠性

### 性能优化
1. **懒加载**: 按需加载资源
2. **代码分割**: 减少初始加载时间
3. **缓存策略**: 合理使用缓存
4. **防抖节流**: 优化事件处理

### 安全实践
1. **输入验证**: 验证所有用户输入
2. **CSP策略**: 实施内容安全策略
3. **HTTPS**: 使用安全传输
4. **依赖审计**: 定期检查依赖安全

## 相关技能

- **typescript-analyzer** - TypeScript分析
- **react-analyzer** - React分析
- **nodejs-analyzer** - Node.js分析
- **web-performance** - Web性能优化
