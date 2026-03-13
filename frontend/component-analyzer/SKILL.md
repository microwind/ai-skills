---
name: 组件分析器
description: "当审查React/Vue/Angular组件、规划组件架构、组件可重用性审计或性能优化时，分析前端组件设计。"
license: MIT
---

# 组件分析器技能

## 概述
好的组件是可重用、可测试和可组合的。坏的组件是脆弱且难以维护的。

**核心原则**: 好的组件是可重用、可测试和可组合的。坏的组件是脆弱且难以维护的。

## 何时使用

**始终:**
- 审查React/Vue/Angular组件
- 规划组件架构
- 组件可重用性审计
- 性能优化
- 代码重构
- 组件设计评审

**触发短语:**
- "分析组件设计"
- "组件架构评审"
- "组件性能优化"
- "组件可重用性"
- "组件重构建议"
- "组件最佳实践"

## 组件分析功能

### 设计分析
- 组件结构检查
- 职责单一性验证
- 接口设计评估
- 状态管理分析
- 依赖关系检查

### 可重用性
- 组件通用性评估
- 参数配置分析
- 样式封装检查
- 主题适配性
- 国际化支持

### 性能优化
- 渲染性能分析
- 内存使用检查
- 重渲染优化
- 懒加载建议
- 缓存策略

## 常见组件问题

### 组件职责过重
```
问题:
单个组件承担过多职责

错误示例:
- 用户组件同时处理数据获取、UI渲染、表单验证
- 组件内部包含复杂的业务逻辑
- 组件直接操作DOM

解决方案:
1. 拆分为多个小组件
2. 提取业务逻辑到服务层
3. 使用自定义Hook
4. 实现关注点分离
```

### 组件耦合度过高
```
问题:
组件之间依赖关系复杂

错误示例:
- 组件直接访问其他组件的内部状态
- 全局状态滥用
- 组件间直接调用方法
- 循环依赖

解决方案:
1. 使用状态管理工具
2. 实现事件驱动架构
3. 通过props传递数据
4. 使用Context API
```

### 组件性能问题
```
问题:
组件渲染效率低下

错误示例:
- 不必要的重渲染
- 内联函数创建
- 缺少React.memo
- 大量DOM操作

解决方案:
1. 使用React.memo优化
2. 提取常量和函数
3. 实现虚拟滚动
4. 使用useMemo和useCallback
```

## 代码实现示例

### 组件分析器
```javascript
const fs = require('fs');
const path = require('path');
const { parse } = require('@babel/parser');
const traverse = require('@babel/traverse').default;

class ComponentAnalyzer {
    constructor(options = {}) {
        this.options = {
            framework: 'react', // react, vue, angular
            componentPath: './src/components',
            ...options
        };
        this.analysisResults = [];
        this.metrics = {
            totalComponents: 0,
            averageSize: 0,
            couplingScore: 0,
            reusabilityScore: 0
        };
    }

    async analyze() {
        console.log('开始分析组件...');
        
        // 扫描组件文件
        const componentFiles = this.scanComponentFiles();
        
        // 分析每个组件
        for (const file of componentFiles) {
            const analysis = await this.analyzeComponent(file);
            this.analysisResults.push(analysis);
        }
        
        // 计算总体指标
        this.calculateMetrics();
        
        // 生成报告
        this.generateReport();
        
        return this.analysisResults;
    }

    scanComponentFiles() {
        const files = [];
        
        function scanDirectory(dir) {
            const items = fs.readdirSync(dir);
            
            for (const item of items) {
                const fullPath = path.join(dir, item);
                const stat = fs.statSync(fullPath);
                
                if (stat.isDirectory()) {
                    scanDirectory(fullPath);
                } else if (isComponentFile(item)) {
                    files.push(fullPath);
                }
            }
        }
        
        function isComponentFile(fileName) {
            const ext = path.extname(fileName);
            const name = path.basename(fileName, ext);
            
            // React组件
            if (ext === '.jsx' || ext === '.tsx') {
                return name[0] === name[0].toUpperCase();
            }
            
            // Vue组件
            if (ext === '.vue') {
                return true;
            }
            
            // Angular组件
            if (ext === '.ts' && name.includes('.component')) {
                return true;
            }
            
            return false;
        }
        
        scanDirectory(this.options.componentPath);
        return files;
    }

    async analyzeComponent(filePath) {
        const content = fs.readFileSync(filePath, 'utf8');
        const fileName = path.basename(filePath);
        
        const analysis = {
            name: this.extractComponentName(fileName),
            path: filePath,
            size: content.length,
            lines: content.split('\n').length,
            framework: this.options.framework,
            metrics: {},
            issues: [],
            recommendations: []
        };

        // 解析代码
        const ast = this.parseCode(content, filePath);
        if (!ast) {
            return analysis;
        }

        // 分析不同方面
        switch (this.options.framework) {
            case 'react':
                this.analyzeReactComponent(ast, analysis);
                break;
            case 'vue':
                this.analyzeVueComponent(content, analysis);
                break;
            case 'angular':
                this.analyzeAngularComponent(ast, analysis);
                break;
        }

        // 通用分析
        this.analyzeComponentStructure(ast, analysis);
        this.analyzeDependencies(ast, analysis);
        this.analyzePerformance(ast, analysis);
        this.analyzeReusability(ast, analysis);

        return analysis;
    }

    parseCode(content, filePath) {
        try {
            const ext = path.extname(filePath);
            
            if (ext === '.vue') {
                // Vue文件需要特殊处理
                return this.parseVueFile(content);
            }
            
            return parse(content, {
                sourceType: 'module',
                plugins: [
                    'jsx',
                    'typescript',
                    'classProperties',
                    'objectRestSpread'
                ]
            });
        } catch (error) {
            console.error(`解析文件失败: ${filePath}`, error);
            return null;
        }
    }

    parseVueFile(content) {
        // 简化的Vue文件解析
        const scriptMatch = content.match(/<script[^>]*>([\s\S]*?)<\/script>/);
        if (!scriptMatch) return null;
        
        return parse(scriptMatch[1], {
            sourceType: 'module',
            plugins: ['typescript']
        });
    }

    extractComponentName(fileName) {
        const name = path.basename(fileName, path.extname(fileName));
        
        // 移除文件名中的后缀
        if (name.includes('.component')) {
            return name.replace('.component', '');
        }
        
        return name;
    }

    analyzeReactComponent(ast, analysis) {
        let hasHooks = false;
        let hasClassComponent = false;
        let propCount = 0;
        let stateCount = 0;
        let effectCount = 0;

        traverse(ast, {
            // 函数组件
            FunctionDeclaration(path) {
                if (this.isReactComponent(path.node)) {
                    analysis.type = 'function';
                }
            },
            
            // Arrow函数组件
            ArrowFunctionExpression(path) {
                if (this.isReactComponent(path.node)) {
                    analysis.type = 'arrow';
                }
            },
            
            // 类组件
            ClassDeclaration(path) {
                if (this.isReactComponent(path.node)) {
                    hasClassComponent = true;
                    analysis.type = 'class';
                }
            },
            
            // Hooks
            CallExpression(path) {
                if (this.isHook(path.node.callee)) {
                    hasHooks = true;
                    
                    const hookName = path.node.callee.name;
                    if (hookName === 'useState') stateCount++;
                    if (hookName === 'useEffect') effectCount++;
                }
            },
            
            // Props解构
            ObjectPattern(path) {
                if (path.parent.type === 'FunctionDeclaration' || 
                    path.parent.type === 'ArrowFunctionExpression') {
                    propCount += path.node.properties.length;
                }
            }
        });

        analysis.metrics = {
            ...analysis.metrics,
            hasHooks,
            hasClassComponent,
            propCount,
            stateCount,
            effectCount
        };

        // 检查问题
        if (hasClassComponent && hasHooks) {
            analysis.issues.push({
                type: 'pattern',
                severity: 'medium',
                message: '类组件中使用了Hooks，建议迁移到函数组件'
            });
        }

        if (stateCount > 5) {
            analysis.issues.push({
                type: 'complexity',
                severity: 'high',
                message: `组件使用了${stateCount}个状态，考虑拆分或使用useReducer`
            });
        }

        if (effectCount > 3) {
            analysis.issues.push({
                type: 'complexity',
                severity: 'medium',
                message: `组件使用了${effectCount}个副作用，考虑拆分逻辑`
            });
        }
    }

    analyzeVueComponent(content, analysis) {
        analysis.type = 'vue';
        
        // 提取template、script、style
        const templateMatch = content.match(/<template[^>]*>([\s\S]*?)<\/template>/);
        const scriptMatch = content.match(/<script[^>]*>([\s\S]*?)<\/script>/);
        const styleMatch = content.match(/<style[^>]*>([\s\S]*?)<\/style>/);
        
        analysis.metrics = {
            ...analysis.metrics,
            hasTemplate: !!templateMatch,
            hasScript: !!scriptMatch,
            hasStyle: !!styleMatch,
            templateSize: templateMatch ? templateMatch[1].length : 0,
            scriptSize: scriptMatch ? scriptMatch[1].length : 0,
            styleSize: styleMatch ? styleMatch[1].length : 0
        };

        // 分析template复杂度
        if (templateMatch) {
            const template = templateMatch[1];
            const elementCount = (template.match(/<[a-zA-Z][^>]*>/g) || []).length;
            analysis.metrics.elementCount = elementCount;
            
            if (elementCount > 50) {
                analysis.issues.push({
                    type: 'complexity',
                    severity: 'medium',
                    message: `模板包含${elementCount}个元素，考虑拆分组件`
                });
            }
        }

        // 检查scoped样式
        if (styleMatch && !styleMatch[0].includes('scoped')) {
            analysis.issues.push({
                type: 'style',
                severity: 'medium',
                message: '样式未使用scoped，可能造成样式污染'
            });
        }
    }

    analyzeAngularComponent(ast, analysis) {
        analysis.type = 'angular';
        
        let decoratorCount = 0;
        let inputCount = 0;
        let outputCount = 0;
        let methodCount = 0;

        traverse(ast, {
            // 装饰器
            Decorator(path) {
                decoratorCount++;
                
                if (path.node.expression.name === 'Component') {
                    // 分析Component装饰器
                    this.analyzeAngularComponentDecorator(path, analysis);
                }
            },
            
            // 输入属性
            PropertyDeclaration(path) {
                if (this.hasDecorator(path.node, 'Input')) {
                    inputCount++;
                }
                if (this.hasDecorator(path.node, 'Output')) {
                    outputCount++;
                }
            },
            
            // 方法
            MethodDeclaration(path) {
                methodCount++;
            }
        });

        analysis.metrics = {
            ...analysis.metrics,
            decoratorCount,
            inputCount,
            outputCount,
            methodCount
        };

        // 检查问题
        if (inputCount > 10) {
            analysis.issues.push({
                type: 'interface',
                severity: 'high',
                message: `组件有${inputCount}个输入属性，考虑使用接口或拆分`
            });
        }

        if (methodCount > 20) {
            analysis.issues.push({
                type: 'complexity',
                severity: 'medium',
                message: `组件有${methodCount}个方法，考虑拆分服务`
            });
        }
    }

    analyzeComponentStructure(ast, analysis) {
        let functionCount = 0;
        let classCount = 0;
        let importCount = 0;
        let exportCount = 0;

        traverse(ast, {
            FunctionDeclaration() { functionCount++; },
            FunctionExpression() { functionCount++; },
            ArrowFunctionExpression() { functionCount++; },
            ClassDeclaration() { classCount++; },
            ImportDeclaration() { importCount++; },
            ExportDeclaration() { exportCount++; },
            ExportNamedDeclaration() { exportCount++; }
        });

        analysis.metrics = {
            ...analysis.metrics,
            functionCount,
            classCount,
            importCount,
            exportCount
        };

        // 计算复杂度
        const complexity = this.calculateComplexity(functionCount, classCount, analysis.lines);
        analysis.metrics.complexity = complexity;

        if (complexity > 10) {
            analysis.issues.push({
                type: 'complexity',
                severity: 'high',
                message: `组件复杂度过高(${complexity})，建议拆分`
            });
        }
    }

    analyzeDependencies(ast, analysis) {
        const dependencies = new Set();
        let externalDeps = 0;
        let internalDeps = 0;

        traverse(ast, {
            ImportDeclaration(path) {
                const source = path.node.source.value;
                dependencies.add(source);
                
                if (source.startsWith('.')) {
                    internalDeps++;
                } else {
                    externalDeps++;
                }
            }
        });

        analysis.metrics = {
            ...analysis.metrics,
            dependencyCount: dependencies.size,
            externalDeps,
            internalDeps
        };

        // 检查依赖过多
        if (dependencies.size > 15) {
            analysis.issues.push({
                type: 'dependency',
                severity: 'medium',
                message: `组件依赖过多(${dependencies.size}个)，考虑优化`
            });
        }

        // 检查外部依赖比例
        const externalRatio = externalDeps / dependencies.size;
        if (externalRatio > 0.8) {
            analysis.issues.push({
                type: 'dependency',
                severity: 'low',
                message: '外部依赖比例过高，可能影响bundle大小'
            });
        }
    }

    analyzePerformance(ast, analysis) {
        let inlineFunctions = 0;
        let anonymousFunctions = 0;
        let conditionalRenders = 0;

        traverse(ast, {
            // 内联函数
            FunctionExpression(path) {
                if (this.isInlineFunction(path)) {
                    inlineFunctions++;
                }
            },
            
            ArrowFunctionExpression(path) {
                if (this.isInlineFunction(path)) {
                    inlineFunctions++;
                }
                if (!path.node.id) {
                    anonymousFunctions++;
                }
            },
            
            // 条件渲染
            ConditionalExpression(path) {
                if (this.isInRenderMethod(path)) {
                    conditionalRenders++;
                }
            },
            
            IfStatement(path) {
                if (this.isInRenderMethod(path)) {
                    conditionalRenders++;
                }
            }
        });

        analysis.metrics = {
            ...analysis.metrics,
            inlineFunctions,
            anonymousFunctions,
            conditionalRenders
        };

        // 性能建议
        if (inlineFunctions > 5) {
            analysis.recommendations.push({
                type: 'performance',
                message: '发现多个内联函数，建议提取到组件外部或使用useCallback'
            });
        }

        if (conditionalRenders > 10) {
            analysis.recommendations.push({
                type: 'performance',
                message: '条件渲染过多，考虑使用组件映射或提取子组件'
            });
        }
    }

    analyzeReusability(ast, analysis) {
        let hardcodedValues = 0;
        let propInterfaces = 0;
        let defaultExports = 0;

        traverse(ast, {
            // 硬编码值
            Literal(path) {
                if (this.isHardcodedValue(path)) {
                    hardcodedValues++;
                }
            },
            
            // TypeScript接口
            TSInterfaceDeclaration(path) {
                if (path.node.name.name.includes('Props')) {
                    propInterfaces++;
                }
            },
            
            // 默认导出
            ExportDefaultDeclaration() {
                defaultExports++;
            }
        });

        const reusabilityScore = this.calculateReusabilityScore(
            propInterfaces,
            hardcodedValues,
            analysis.metrics.propCount || 0
        );

        analysis.metrics = {
            ...analysis.metrics,
            hardcodedValues,
            propInterfaces,
            defaultExports,
            reusabilityScore
        };

        // 可重用性建议
        if (reusabilityScore < 0.5) {
            analysis.recommendations.push({
                type: 'reusability',
                message: '组件可重用性较低，建议提取配置参数'
            });
        }

        if (hardcodedValues > 10) {
            analysis.recommendations.push({
                type: 'reusability',
                message: '发现多个硬编码值，建议通过props传递'
            });
        }
    }

    // 辅助方法
    isReactComponent(node) {
        if (node.id && node.id.name) {
            return node.id.name[0] === node.id.name[0].toUpperCase();
        }
        return false;
    }

    isHook(callee) {
        if (callee.type === 'Identifier' && callee.name.startsWith('use')) {
            return true;
        }
        return false;
    }

    isInlineFunction(path) {
        return path.parent.type === 'CallExpression' || 
               path.parent.type === 'ReturnStatement' ||
               path.parent.type === 'ConditionalExpression';
    }

    isInRenderMethod(path) {
        // 简化实现，实际需要更复杂的逻辑
        return true;
    }

    isHardcodedValue(path) {
        const value = path.node.value;
        return typeof value === 'string' && value.length > 5;
    }

    hasDecorator(node, decoratorName) {
        if (!node.decorators) return false;
        return node.decorators.some(dec => 
            dec.expression.type === 'Identifier' && 
            dec.expression.name === decoratorName
        );
    }

    calculateComplexity(functionCount, classCount, lines) {
        const normalizedLines = lines / 50; // 标准化行数
        return Math.round((functionCount + classCount * 2 + normalizedLines) / 3);
    }

    calculateReusabilityScore(propInterfaces, hardcodedValues, propCount) {
        const interfaceScore = Math.min(propInterfaces / 2, 1);
        const hardcodedPenalty = Math.max(0, 1 - hardcodedValues / 10);
        const propScore = Math.min(propCount / 5, 1);
        
        return (interfaceScore + hardcodedPenalty + propScore) / 3;
    }

    calculateMetrics() {
        const total = this.analysisResults.length;
        if (total === 0) return;

        this.metrics.totalComponents = total;
        this.metrics.averageSize = this.analysisResults.reduce((sum, r) => sum + r.size, 0) / total;
        this.metrics.couplingScore = this.calculateAverageCoupling();
        this.metrics.reusabilityScore = this.calculateAverageReusability();
    }

    calculateAverageCoupling() {
        const totalDeps = this.analysisResults.reduce((sum, r) => 
            sum + (r.metrics.dependencyCount || 0), 0);
        return totalDeps / this.analysisResults.length;
    }

    calculateAverageReusability() {
        const scores = this.analysisResults.map(r => r.metrics.reusabilityScore || 0);
        return scores.reduce((sum, score) => sum + score, 0) / scores.length;
    }

    generateReport() {
        const report = {
            summary: this.metrics,
            components: this.analysisResults,
            recommendations: this.generateGlobalRecommendations(),
            issues: this.categorizeIssues()
        };

        const reportPath = './component-analysis-report.json';
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        
        console.log(`组件分析报告已生成: ${reportPath}`);
        this.printSummary(report);
    }

    generateGlobalRecommendations() {
        const recommendations = [];
        
        // 基于总体指标的建议
        if (this.metrics.averageSize > 5000) {
            recommendations.push({
                type: 'size',
                message: '平均组件大小过大，建议拆分大组件'
            });
        }
        
        if (this.metrics.couplingScore > 10) {
            recommendations.push({
                type: 'coupling',
                message: '组件耦合度过高，建议优化依赖关系'
            });
        }
        
        if (this.metrics.reusabilityScore < 0.6) {
            recommendations.push({
                type: 'reusability',
                message: '组件可重用性较低，建议提高组件通用性'
            });
        }
        
        return recommendations;
    }

    categorizeIssues() {
        const issues = {
            critical: [],
            high: [],
            medium: [],
            low: []
        };

        for (const component of this.analysisResults) {
            for (const issue of component.issues) {
                const severity = issue.severity || 'medium';
                issues[severity].push({
                    component: component.name,
                    ...issue
                });
            }
        }

        return issues;
    }

    printSummary(report) {
        console.log('\n=== 组件分析总结 ===');
        console.log(`总组件数: ${report.summary.totalComponents}`);
        console.log(`平均大小: ${Math.round(report.summary.averageSize)} bytes`);
        console.log(`平均耦合度: ${report.summary.couplingScore.toFixed(2)}`);
        console.log(`平均可重用性: ${(report.summary.reusabilityScore * 100).toFixed(1)}%`);
        
        console.log('\n=== 问题统计 ===');
        Object.entries(report.issues).forEach(([severity, issues]) => {
            if (issues.length > 0) {
                console.log(`${severity.toUpperCase()}: ${issues.length} 个`);
            }
        });
        
        console.log('\n=== 全局建议 ===');
        report.recommendations.forEach(rec => {
            console.log(`- ${rec.message}`);
        });
    }
}

// 使用示例
async function main() {
    const analyzer = new ComponentAnalyzer({
        framework: 'react',
        componentPath: './src/components'
    });

    try {
        const results = await analyzer.analyze();
        console.log(`分析了 ${results.length} 个组件`);
    } catch (error) {
        console.error('分析失败:', error);
    }
}

module.exports = ComponentAnalyzer;

if (require.main === module) {
    main();
}
```

### 组件重构建议器
```javascript
class ComponentRefactorer {
    constructor() {
        this.refactorRules = this.loadRefactorRules();
    }

    analyzeForRefactoring(component) {
        const suggestions = [];
        
        // 检查组件大小
        if (component.size > 10000) {
            suggestions.push({
                type: 'split',
                priority: 'high',
                description: '组件过大，建议拆分',
                actions: this.generateSplitActions(component)
            });
        }
        
        // 检查复杂度
        if (component.metrics.complexity > 8) {
            suggestions.push({
                type: 'simplify',
                priority: 'medium',
                description: '组件复杂度过高，建议简化',
                actions: this.generateSimplifyActions(component)
            });
        }
        
        // 检查性能问题
        const performanceIssues = this.analyzePerformanceIssues(component);
        suggestions.push(...performanceIssues);
        
        // 检查可重用性
        const reusabilityIssues = this.analyzeReusabilityIssues(component);
        suggestions.push(...reusabilityIssues);
        
        return suggestions.sort((a, b) => this.getPriorityWeight(b.priority) - this.getPriorityWeight(a.priority));
    }

    generateSplitActions(component) {
        const actions = [];
        
        // 基于组件类型生成拆分建议
        if (component.framework === 'react') {
            actions.push({
                action: 'extract_custom_hooks',
                description: '提取自定义Hook',
                example: 'const useUserData = () => { ... };'
            });
            
            if (component.metrics.stateCount > 3) {
                actions.push({
                    action: 'use_reducer',
                    description: '使用useReducer管理复杂状态',
                    example: 'const [state, dispatch] = useReducer(reducer, initialState);'
                });
            }
        }
        
        // 提取子组件
        actions.push({
            action: 'extract_subcomponents',
            description: '提取UI子组件',
            example: 'const UserCard = ({ user }) => { ... };'
        });
        
        return actions;
    }

    generateSimplifyActions(component) {
        const actions = [];
        
        // 简化条件渲染
        if (component.metrics.conditionalRenders > 5) {
            actions.push({
                action: 'extract_render_logic',
                description: '提取渲染逻辑',
                example: 'const renderContent = () => { ... };'
            });
        }
        
        // 简化事件处理
        actions.push({
            action: 'extract_event_handlers',
            description: '提取事件处理函数',
            example: 'const handleSubmit = useCallback(() => { ... }, []);'
        });
        
        return actions;
    }

    analyzePerformanceIssues(component) {
        const issues = [];
        
        // 内联函数问题
        if (component.metrics.inlineFunctions > 3) {
            issues.push({
                type: 'performance',
                priority: 'medium',
                description: '内联函数过多，影响性能',
                actions: [
                    {
                        action: 'use_callback',
                        description: '使用useCallback优化',
                        example: 'const handleClick = useCallback(() => { ... }, []);'
                    },
                    {
                        action: 'extract_functions',
                        description: '提取函数到组件外部',
                        example: 'const helperFunction = () => { ... };'
                    }
                ]
            });
        }
        
        // 重渲染问题
        if (component.metrics.effectCount > 2) {
            issues.push({
                type: 'performance',
                priority: 'low',
                description: '可能存在不必要的重渲染',
                actions: [
                    {
                        action: 'use_memo',
                        description: '使用useMemo优化计算',
                        example: 'const memoizedValue = useMemo(() => computeValue(a, b), [a, b]);'
                    },
                    {
                        action: 'react_memo',
                        description: '使用React.memo包装组件',
                        example: 'export default React.memo(MyComponent);'
                    }
                ]
            });
        }
        
        return issues;
    }

    analyzeReusabilityIssues(component) {
        const issues = [];
        
        // 硬编码值问题
        if (component.metrics.hardcodedValues > 5) {
            issues.push({
                type: 'reusability',
                priority: 'medium',
                description: '硬编码值过多，影响可重用性',
                actions: [
                    {
                        action: 'extract_constants',
                        description: '提取常量',
                        example: 'const DEFAULT_CONFIG = { ... };'
                    },
                    {
                        action: 'add_props',
                        description: '通过props传递配置',
                        example: '<MyComponent config={config} />'
                    }
                ]
            });
        }
        
        // 缺少接口定义
        if (component.framework === 'react' && !component.metrics.propInterfaces) {
            issues.push({
                type: 'reusability',
                priority: 'low',
                description: '缺少Props接口定义',
                actions: [
                    {
                        action: 'add_typescript_interface',
                        description: '添加TypeScript接口',
                        example: 'interface MyComponentProps { name: string; age: number; }'
                    }
                ]
            });
        }
        
        return issues;
    }

    getPriorityWeight(priority) {
        const weights = { critical: 4, high: 3, medium: 2, low: 1 };
        return weights[priority] || 1;
    }

    loadRefactorRules() {
        return {
            maxComponentSize: 10000,
            maxComplexity: 8,
            maxInlineFunctions: 3,
            maxHardcodedValues: 5,
            maxDependencies: 10
        };
    }

    generateRefactoringPlan(components) {
        const plan = {
            phases: [],
            estimatedEffort: 0,
            risks: [],
            benefits: []
        };
        
        // 按优先级分组
        const criticalComponents = components.filter(c => 
            c.issues.some(i => i.severity === 'critical')
        );
        
        const highPriorityComponents = components.filter(c => 
            c.issues.some(i => i.severity === 'high')
        );
        
        const mediumPriorityComponents = components.filter(c => 
            c.issues.some(i => i.severity === 'medium')
        );
        
        // 生成重构阶段
        if (criticalComponents.length > 0) {
            plan.phases.push({
                name: '紧急修复',
                components: criticalComponents,
                estimatedDays: criticalComponents.length * 2,
                description: '修复关键问题，确保系统稳定'
            });
        }
        
        if (highPriorityComponents.length > 0) {
            plan.phases.push({
                name: '高优先级重构',
                components: highPriorityComponents,
                estimatedDays: highPriorityComponents.length * 3,
                description: '重构高优先级组件，提升性能'
            });
        }
        
        if (mediumPriorityComponents.length > 0) {
            plan.phases.push({
                name: '优化改进',
                components: mediumPriorityComponents,
                estimatedDays: mediumPriorityComponents.length * 2,
                description: '优化组件结构，提高可维护性'
            });
        }
        
        // 计算总工作量
        plan.estimatedEffort = plan.phases.reduce((sum, phase) => sum + phase.estimatedDays, 0);
        
        // 识别风险
        plan.risks = this.identifyRisks(components);
        
        // 评估收益
        plan.benefits = this.estimateBenefits(components);
        
        return plan;
    }

    identifyRisks(components) {
        const risks = [];
        
        const largeComponents = components.filter(c => c.size > 15000);
        if (largeComponents.length > 0) {
            risks.push({
                type: 'complexity',
                description: '大组件重构风险较高',
                mitigation: '分阶段重构，保持向后兼容'
            });
        }
        
        const coupledComponents = components.filter(c => c.metrics.dependencyCount > 15);
        if (coupledComponents.length > 0) {
            risks.push({
                type: 'dependency',
                description: '高耦合组件重构可能影响其他模块',
                mitigation: '建立完整的测试覆盖，逐步解耦'
            });
        }
        
        return risks;
    }

    estimateBenefits(components) {
        const benefits = [];
        
        const totalSize = components.reduce((sum, c) => sum + c.size, 0);
        const avgComplexity = components.reduce((sum, c) => sum + (c.metrics.complexity || 0), 0) / components.length;
        
        if (totalSize > 50000) {
            benefits.push({
                type: 'performance',
                description: '减少bundle大小，提升加载速度',
                impact: 'high'
            });
        }
        
        if (avgComplexity > 7) {
            benefits.push({
                type: 'maintainability',
                description: '降低代码复杂度，提高可维护性',
                impact: 'medium'
            });
        }
        
        benefits.push({
            type: 'developer_experience',
            description: '改善开发体验，提高开发效率',
            impact: 'medium'
        });
        
        return benefits;
    }
}

module.exports = {
    ComponentAnalyzer,
    ComponentRefactorer
};
```

## 组件设计最佳实践

### 单一职责
1. **功能专注**: 每个组件只做一件事
2. **UI分离**: 业务逻辑与UI展示分离
3. **数据管理**: 数据获取与组件渲染分离
4. **事件处理**: 事件处理逻辑独立

### 接口设计
1. **清晰Props**: 明确定义组件接口
2. **默认值**: 提供合理的默认值
3. **类型检查**: 使用TypeScript或PropTypes
4. **文档完整**: 编写组件文档

### 性能优化
1. **避免重渲染**: 使用React.memo等优化
2. **懒加载**: 大组件使用懒加载
3. **虚拟化**: 长列表使用虚拟滚动
4. **缓存策略**: 合理使用缓存

## 相关技能

- **react-patterns** - React模式
- **vue-architecture** - Vue架构
- **angular-best-practices** - Angular最佳实践
- **frontend-architecture** - 前端架构
