---
name: NestJS企业架构
description: "当开发NestJS企业应用时，分析模块设计，优化依赖注入，解决架构问题。验证微服务架构，设计企业级应用，和最佳实践。"
license: MIT
---

# NestJS企业架构技能

## 概述
NestJS是构建企业级Node.js应用的渐进式框架。不当的NestJS架构设计会导致代码混乱、性能问题和企业级功能缺失。在设计企业级应用前需要仔细分析架构需求。

**核心原则**: 好的NestJS架构应该模块化、可扩展、可测试、可维护。坏的NestJS架构会导致代码耦合、性能瓶颈和维护困难。

## 何时使用

**始终:**
- 设计企业级应用架构时
- 构建微服务系统时
- 实现依赖注入模式时
- 处理复杂业务逻辑时
- 配置企业级功能时

**触发短语:**
- "NestJS企业架构"
- "Node.js企业应用"
- "依赖注入设计"
- "微服务架构"
- "NestJS模块设计"
- "TypeScript企业开发"

## NestJS企业架构功能

### 模块系统设计
- 模块依赖管理
- 动态模块配置
- 模块生命周期
- 全局模块设置
- 模块重构策略

### 依赖注入系统
- 服务提供者配置
- 作用域管理
- 循环依赖处理
- 自定义装饰器
- 依赖注入最佳实践

### 微服务架构
- 服务间通信
- 消息队列集成
- 服务发现机制
- 负载均衡配置
- 分布式事务处理

### 企业级功能
- 身份验证授权
- 缓存策略配置
- 日志记录系统
- 监控告警机制
- 配置管理中心

## 常见NestJS架构问题

### 模块设计不当
```
问题:
模块结构混乱，依赖关系复杂

错误示例:
- 模块职责不清晰
- 循环依赖问题
- 模块过度耦合
- 缺乏模块边界

解决方案:
1. 明确模块职责边界
2. 使用依赖注入解耦
3. 实施模块化设计原则
4. 建立清晰的模块层次
```

### 依赖注入滥用
```
问题:
依赖注入配置复杂，性能影响

错误示例:
- 不必要的服务注入
- 作用域配置错误
- 循环依赖未处理
- 服务生命周期管理不当

解决方案:
1. 合理设计服务依赖
2. 正确配置作用域
3. 处理循环依赖问题
4. 优化服务生命周期
```

### 微服务通信问题
```
问题:
服务间通信不稳定，数据一致性问题

错误示例:
- 同步通信阻塞
- 缺乏重试机制
- 数据一致性缺失
- 服务发现失效

解决方案:
1. 使用异步通信模式
2. 实施重试和熔断机制
3. 保证数据一致性
4. 完善服务发现机制
```

## 代码实现示例

### NestJS架构分析器
```typescript
import { readFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join, extname } from 'path';
import { parse } from '@typescript-eslint/parser';
import { TSESTree } from '@typescript-eslint/utils';

interface ModuleInfo {
  name: string;
  file: string;
  imports: string[];
  providers: string[];
  controllers: string[];
  exports: string[];
  issues: string[];
}

interface ServiceInfo {
  name: string;
  file: string;
  injectable: boolean;
  scope: string;
  dependencies: string[];
  issues: string[];
}

interface ArchitectureIssue {
  severity: 'critical' | 'high' | 'medium' | 'low';
  type: string;
  file: string;
  message: string;
  suggestion: string;
  line?: number;
}

class NestJSArchitectureAnalyzer {
  private modules: ModuleInfo[] = [];
  private services: ServiceInfo[] = [];
  private issues: ArchitectureIssue[] = [];

  constructor(private projectPath: string) {}

  analyzeArchitecture(): {
    summary: any;
    modules: ModuleInfo[];
    services: ServiceInfo[];
    issues: ArchitectureIssue[];
    recommendations: any[];
    healthScore: number;
  } {
    try {
      // 扫描TypeScript文件
      this.scanTypeScriptFiles();

      // 分析模块依赖
      this.analyzeModuleDependencies();

      // 分析服务依赖
      this.analyzeServiceDependencies();

      // 检查架构问题
      this.checkArchitectureIssues();

      // 生成分析报告
      return this.generateReport();
    } catch (error) {
      return {
        summary: { error: '分析失败' },
        modules: [],
        services: [],
        issues: [],
        recommendations: [],
        healthScore: 0
      };
    }
  }

  private scanTypeScriptFiles(): void {
    const scanDirectory = (dir: string): string[] => {
      const files: string[] = [];
      
      try {
        const items = readdirSync(dir);
        
        for (const item of items) {
          const fullPath = join(dir, item);
          const stat = statSync(fullPath);
          
          if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
            files.push(...scanDirectory(fullPath));
          } else if (stat.isFile() && extname(item) === '.ts') {
            files.push(fullPath);
          }
        }
      } catch (error) {
        console.warn(`无法扫描目录: ${dir}`);
      }
      
      return files;
    };

    const tsFiles = scanDirectory(this.projectPath);
    
    for (const file of tsFiles) {
      this.analyzeTypeScriptFile(file);
    }
  }

  private analyzeTypeScriptFile(filePath: string): void {
    try {
      const content = readFileSync(filePath, 'utf8');
      const ast = parse(content, {
        sourceType: 'module',
        ecmaVersion: 2020,
        project: true
      });

      this.extractModuleInfo(ast, filePath);
      this.extractServiceInfo(ast, filePath);
    } catch (error) {
      this.issues.push({
        severity: 'medium',
        type: 'parse',
        file: filePath,
        message: `文件解析失败: ${error.message}`,
        suggestion: '检查TypeScript语法和配置'
      });
    }
  }

  private extractModuleInfo(ast: TSESTree.Program, filePath: string): void {
    const visitNode = (node: TSESTree.Node) => {
      if (node.type === 'ClassDeclaration' && this.isModuleClass(node)) {
        const moduleInfo = this.parseModuleClass(node, filePath);
        if (moduleInfo) {
          this.modules.push(moduleInfo);
        }
      }
    };

    this.traverseAST(ast, visitNode);
  }

  private extractServiceInfo(ast: TSESTree.Program, filePath: string): void {
    const visitNode = (node: TSESTree.Node) => {
      if (node.type === 'ClassDeclaration' && this.isServiceClass(node)) {
        const serviceInfo = this.parseServiceClass(node, filePath);
        if (serviceInfo) {
          this.services.push(serviceInfo);
        }
      }
    };

    this.traverseAST(ast, visitNode);
  }

  private isModuleClass(node: TSESTree.ClassDeclaration): boolean {
    if (!node.decorators) return false;
    
    return node.decorators.some(decorator => {
      if (decorator.expression.type === 'Identifier') {
        return decorator.expression.name === 'Module';
      }
      if (decorator.expression.type === 'CallExpression' && 
          decorator.expression.callee.type === 'Identifier') {
        return decorator.expression.callee.name === 'Module';
      }
      return false;
    });
  }

  private isServiceClass(node: TSESTree.ClassDeclaration): boolean {
    if (!node.decorators) return false;
    
    return node.decorators.some(decorator => {
      if (decorator.expression.type === 'Identifier') {
        return decorator.expression.name === 'Injectable';
      }
      if (decorator.expression.type === 'CallExpression' && 
          decorator.expression.callee.type === 'Identifier') {
        return decorator.expression.callee.name === 'Injectable';
      }
      return false;
    });
  }

  private parseModuleClass(node: TSESTree.ClassDeclaration, filePath: string): ModuleInfo | null {
    if (!node.id) return null;

    const moduleInfo: ModuleInfo = {
      name: node.id.name,
      file: filePath,
      imports: [],
      providers: [],
      controllers: [],
      exports: [],
      issues: []
    };

    // 解析Module装饰器参数
    const moduleDecorator = node.decorators?.find(d => this.isModuleClass({ 
      ...node, 
      decorators: [d] 
    } as TSESTree.ClassDeclaration));

    if (moduleDecorator && moduleDecorator.expression.type === 'CallExpression') {
      const decoratorArg = moduleDecorator.expression.arguments[0];
      if (decoratorArg && decoratorArg.type === 'ObjectExpression') {
        this.parseModuleDecoratorProperties(decoratorArg, moduleInfo);
      }
    }

    return moduleInfo;
  }

  private parseModuleDecoratorProperties(node: TSESTree.ObjectExpression, moduleInfo: ModuleInfo): void {
    for (const property of node.properties) {
      if (property.type === 'Property' && property.key.type === 'Identifier') {
        const propertyName = property.key.name;
        
        if (property.value.type === 'ArrayExpression') {
          const elements = property.value.elements
            .filter(el => el && el.type === 'Identifier')
            .map(el => (el as TSESTree.Identifier).name);

          switch (propertyName) {
            case 'imports':
              moduleInfo.imports.push(...elements);
              break;
            case 'providers':
              moduleInfo.providers.push(...elements);
              break;
            case 'controllers':
              moduleInfo.controllers.push(...elements);
              break;
            case 'exports':
              moduleInfo.exports.push(...elements);
              break;
          }
        }
      }
    }
  }

  private parseServiceClass(node: TSESTree.ClassDeclaration, filePath: string): ServiceInfo | null {
    if (!node.id) return null;

    const serviceInfo: ServiceInfo = {
      name: node.id.name,
      file: filePath,
      injectable: false,
      scope: 'DEFAULT',
      dependencies: [],
      issues: []
    };

    // 检查Injectable装饰器
    const injectableDecorator = node.decorators?.find(d => this.isServiceClass({ 
      ...node, 
      decorators: [d] 
    } as TSESTree.ClassDeclaration));

    if (injectableDecorator) {
      serviceInfo.injectable = true;
      
      // 解析作用域
      if (injectableDecorator.expression.type === 'CallExpression') {
        const decoratorArg = injectableDecorator.expression.arguments[0];
        if (decoratorArg && decoratorArg.type === 'ObjectExpression') {
          this.parseInjectableScope(decoratorArg, serviceInfo);
        }
      }
    }

    // 解析构造函数依赖
    this.parseConstructorDependencies(node, serviceInfo);

    return serviceInfo;
  }

  private parseInjectableScope(node: TSESTree.ObjectExpression, serviceInfo: ServiceInfo): void {
    for (const property of node.properties) {
      if (property.type === 'Property' && 
          property.key.type === 'Identifier' && 
          property.key.name === 'scope' &&
          property.value.type === 'Identifier') {
        serviceInfo.scope = property.value.name;
      }
    }
  }

  private parseConstructorDependencies(node: TSESTree.ClassDeclaration, serviceInfo: ServiceInfo): void {
    if (!node.body) return;

    for (const member of node.body.body) {
      if (member.type === 'MethodDefinition' && 
          member.kind === 'constructor' &&
          member.value.type === 'FunctionExpression' &&
          member.value.params) {
        
        for (const param of member.value.params) {
          if (param.type === 'Parameter' && 
              param.typeAnnotation &&
              param.typeAnnotation.typeAnnotation.type === 'TypeReference' &&
              param.typeAnnotation.typeAnnotation.typeName.type === 'Identifier') {
            
            const dependencyType = param.typeAnnotation.typeAnnotation.typeName.name;
            serviceInfo.dependencies.push(dependencyType);
          }
        }
      }
    }
  }

  private analyzeModuleDependencies(): void {
    // 检查循环依赖
    const moduleGraph = this.buildModuleGraph();
    const cycles = this.detectCycles(moduleGraph);
    
    for (const cycle of cycles) {
      this.issues.push({
        severity: 'high',
        type: 'circular_dependency',
        file: cycle[0],
        message: `模块循环依赖: ${cycle.join(' -> ')} -> ${cycle[0]}`,
        suggestion: '重构模块依赖关系，消除循环依赖'
      });
    }

    // 检查未使用的导入
    for (const module of this.modules) {
      for (const imp of module.imports) {
        if (!this.isModuleUsed(imp)) {
          module.issues.push(`未使用的导入模块: ${imp}`);
          this.issues.push({
            severity: 'medium',
            type: 'unused_import',
            file: module.file,
            message: `未使用的导入模块: ${imp}`,
            suggestion: '移除未使用的导入模块'
          });
        }
      }
    }
  }

  private analyzeServiceDependencies(): void {
    // 检查服务依赖注入问题
    for (const service of this.services) {
      if (!service.injectable) {
        service.issues.push('服务未标记为Injectable');
        this.issues.push({
          severity: 'high',
          type: 'not_injectable',
          file: service.file,
          message: `服务未标记为Injectable: ${service.name}`,
          suggestion: '添加@Injectable()装饰器'
        });
      }

      // 检查依赖是否可注入
      for (const dep of service.dependencies) {
        const depService = this.services.find(s => s.name === dep);
        if (depService && !depService.injectable) {
          service.issues.push(`依赖服务不可注入: ${dep}`);
          this.issues.push({
            severity: 'high',
            type: 'dependency_not_injectable',
            file: service.file,
            message: `依赖服务不可注入: ${dep}`,
            suggestion: '确保依赖服务标记为Injectable'
          });
        }
      }
    }
  }

  private checkArchitectureIssues(): void {
    // 检查模块大小
    for (const module of this.modules) {
      const totalElements = module.imports.length + 
                          module.providers.length + 
                          module.controllers.length + 
                          module.exports.length;
      
      if (totalElements > 20) {
        module.issues.push('模块过大，考虑拆分');
        this.issues.push({
          severity: 'medium',
          type: 'large_module',
          file: module.file,
          message: `模块过大: ${module.name} (${totalElements}个元素)`,
          suggestion: '考虑拆分大模块为多个小模块'
        });
      }
    }

    // 检查服务作用域配置
    for (const service of this.services) {
      if (service.scope === 'REQUEST' && service.dependencies.length > 5) {
        service.issues.push('REQUEST作用域服务依赖过多');
        this.issues.push({
          severity: 'medium',
          type: 'request_scope_with_many_deps',
          file: service.file,
          message: `REQUEST作用域服务依赖过多: ${service.name}`,
          suggestion: '考虑使用DEFAULT作用域或减少依赖'
        });
      }
    }
  }

  private buildModuleGraph(): Map<string, string[]> {
    const graph = new Map<string, string[]>();
    
    for (const module of this.modules) {
      graph.set(module.name, module.imports);
    }
    
    return graph;
  }

  private detectCycles(graph: Map<string, string[]>): string[][] {
    const cycles: string[][] = [];
    const visited = new Set<string>();
    const recursionStack = new Set<string>();
    const path: string[] = [];

    const dfs = (node: string): boolean => {
      if (recursionStack.has(node)) {
        const cycleStart = path.indexOf(node);
        cycles.push([...path.slice(cycleStart), node]);
        return true;
      }

      if (visited.has(node)) {
        return false;
      }

      visited.add(node);
      recursionStack.add(node);
      path.push(node);

      const neighbors = graph.get(node) || [];
      for (const neighbor of neighbors) {
        if (dfs(neighbor)) {
          return true;
        }
      }

      recursionStack.delete(node);
      path.pop();
      return false;
    };

    for (const node of graph.keys()) {
      if (!visited.has(node)) {
        dfs(node);
      }
    }

    return cycles;
  }

  private isModuleUsed(moduleName: string): boolean {
    return this.modules.some(m => 
      m.imports.includes(moduleName) || 
      m.providers.includes(moduleName) ||
      m.controllers.includes(moduleName) ||
      m.exports.includes(moduleName)
    );
  }

  private traverseAST(node: TSESTree.Node, visitor: (node: TSESTree.Node) => void): void {
    visitor(node);
    
    for (const key in node) {
      const child = (node as any)[key];
      if (Array.isArray(child)) {
        for (const item of child) {
          if (item && typeof item === 'object' && item.type) {
            this.traverseAST(item, visitor);
          }
        }
      } else if (child && typeof child === 'object' && child.type) {
        this.traverseAST(child, visitor);
      }
    }
  }

  private generateReport() {
    const summary = {
      totalModules: this.modules.length,
      totalServices: this.services.length,
      totalIssues: this.issues.length,
      criticalIssues: this.issues.filter(i => i.severity === 'critical').length,
      highIssues: this.issues.filter(i => i.severity === 'high').length,
      mediumIssues: this.issues.filter(i => i.severity === 'medium').length,
      lowIssues: this.issues.filter(i => i.severity === 'low').length
    };

    const recommendations = this.generateRecommendations();
    const healthScore = this.calculateHealthScore(summary);

    return {
      summary,
      modules: this.modules,
      services: this.services,
      issues: this.issues,
      recommendations,
      healthScore
    };
  }

  private generateRecommendations(): any[] {
    const recommendations: any[] = [];
    const issueTypes = new Map<string, number>();

    for (const issue of this.issues) {
      issueTypes.set(issue.type, (issueTypes.get(issue.type) || 0) + 1);
    }

    if (issueTypes.get('circular_dependency') > 0) {
      recommendations.push({
        priority: 'high',
        type: 'architecture',
        message: `发现${issueTypes.get('circular_dependency')}个循环依赖问题`,
        suggestion: '重构模块依赖关系，消除循环依赖'
      });
    }

    if (issueTypes.get('not_injectable') > 0) {
      recommendations.push({
        priority: 'high',
        type: 'dependency',
        message: `发现${issueTypes.get('not_injectable')}个服务未标记为可注入`,
        suggestion: '为所有服务添加@Injectable()装饰器'
      });
    }

    if (issueTypes.get('large_module') > 0) {
      recommendations.push({
        priority: 'medium',
        type: 'structure',
        message: `发现${issueTypes.get('large_module')}个过大模块`,
        suggestion: '拆分大模块为多个功能单一的小模块'
      });
    }

    return recommendations;
  }

  private calculateHealthScore(summary: any): number {
    let score = 100;
    
    score -= summary.criticalIssues * 20;
    score -= summary.highIssues * 10;
    score -= summary.mediumIssues * 5;
    score -= summary.lowIssues * 2;
    
    return Math.max(0, score);
  }
}

// NestJS架构优化器
class NestJSArchitectureOptimizer {
  constructor(private projectPath: string) {}

  optimizeArchitecture(): {
    optimizations: any[];
    summary: any;
  } {
    const optimizations: any[] = [];

    // 检查模块结构优化
    const moduleOptimization = this.optimizeModuleStructure();
    if (moduleOptimization) {
      optimizations.push(moduleOptimization);
    }

    // 检查依赖注入优化
    const diOptimization = this.optimizeDependencyInjection();
    if (diOptimization) {
      optimizations.push(diOptimization);
    }

    // 检查微服务架构优化
    const microserviceOptimization = this.optimizeMicroserviceArchitecture();
    if (microserviceOptimization) {
      optimizations.push(microserviceOptimization);
    }

    return {
      optimizations,
      summary: {
        totalOptimizations: optimizations.length,
        estimatedImprovements: this.estimateImprovements(optimizations)
      }
    };
  }

  private optimizeModuleStructure(): any | null {
    // 检查是否存在shared模块
    const sharedModulePath = join(this.projectPath, 'src', 'shared', 'shared.module.ts');
    
    if (!existsSync(sharedModulePath)) {
      return {
        type: 'structure',
        message: '创建共享模块',
        suggestion: '创建SharedModule用于共享通用服务和组件'
      };
    }

    return null;
  }

  private optimizeDependencyInjection(): any | null {
    // 检查是否存在配置模块
    const configModulePath = join(this.projectPath, 'src', 'config', 'config.module.ts');
    
    if (!existsSync(configModulePath)) {
      return {
        type: 'dependency',
        message: '创建配置模块',
        suggestion: '创建ConfigModule统一管理应用配置'
      };
    }

    return null;
  }

  private optimizeMicroserviceArchitecture(): any | null {
    // 检查是否存在微服务相关文件
    const mainTsPath = join(this.projectPath, 'src', 'main.ts');
    
    if (existsSync(mainTsPath)) {
      try {
        const content = readFileSync(mainTsPath, 'utf8');
        
        if (!content.includes('createMicroservice') && !content.includes('ClientProxy')) {
          return {
            type: 'microservice',
            message: '考虑微服务架构',
            suggestion: '评估是否需要采用微服务架构提升可扩展性'
          };
        }
      } catch (error) {
        // 忽略读取错误
      }
    }

    return null;
  }

  private estimateImprovements(optimizations: any[]): {
    architecture: number;
    performance: number;
    maintainability: number;
  } {
    const improvements = {
      architecture: 0,
      performance: 0,
      maintainability: 0
    };

    for (const opt of optimizations) {
      switch (opt.type) {
        case 'structure':
          improvements.architecture += 25;
          improvements.maintainability += 20;
          break;
        case 'dependency':
          improvements.architecture += 20;
          improvements.performance += 10;
          break;
        case 'microservice':
          improvements.architecture += 30;
          improvements.performance += 25;
          break;
      }
    }

    return improvements;
  }
}

// 使用示例
function main() {
  const analyzer = new NestJSArchitectureAnalyzer('./my-nestjs-project');
  const report = analyzer.analyzeArchitecture();
  
  console.log('NestJS架构分析报告:');
  console.log(`健康评分: ${report.healthScore}`);
  console.log(`模块总数: ${report.summary.totalModules}`);
  console.log(`服务总数: ${report.summary.totalServices}`);
  console.log(`问题总数: ${report.summary.totalIssues}`);
  
  console.log('\n优化建议:');
  for (const rec of report.recommendations) {
    console.log(`- ${rec.message}: ${rec.suggestion}`);
  }
  
  const optimizer = new NestJSArchitectureOptimizer('./my-nestjs-project');
  const optimization = optimizer.optimizeArchitecture();
  
  console.log('\n架构优化建议:');
  for (const opt of optimization.optimizations) {
    console.log(`- ${opt.message}: ${opt.suggestion}`);
  }
}

export { NestJSArchitectureAnalyzer, NestJSArchitectureOptimizer };
```

### NestJS性能监控器
```typescript
import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { performance } from 'perf_hooks';

interface RequestMetrics {
  method: string;
  url: string;
  statusCode: number;
  duration: number;
  timestamp: number;
  userAgent: string;
  ip: string;
}

interface PerformanceMetrics {
  cpuUsage: number;
  memoryUsage: NodeJS.MemoryUsage;
  activeConnections: number;
  requestsPerSecond: number;
}

@Injectable()
export class NestJSPerformanceMonitor implements OnModuleInit, OnModuleDestroy {
  private requests: RequestMetrics[] = [];
  private startTime = performance.now();
  private metricsInterval: NodeJS.Timeout;

  onModuleInit() {
    // 启动性能指标收集
    this.startMetricsCollection();
  }

  onModuleDestroy() {
    // 清理资源
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval);
    }
  }

  recordRequest(req: any, res: any, duration: number) {
    const metrics: RequestMetrics = {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration,
      timestamp: Date.now(),
      userAgent: req.headers['user-agent'] || '',
      ip: req.ip || req.connection.remoteAddress || ''
    };

    this.requests.push(metrics);

    // 保持最近1000个请求
    if (this.requests.length > 1000) {
      this.requests.shift();
    }
  }

  getMetrics(): {
    timestamp: number;
    uptime: number;
    requestStats: any;
    performanceStats: PerformanceMetrics;
    routeStats: any[];
  } {
    const requestStats = this.calculateRequestStats();
    const performanceStats = this.getPerformanceStats();
    const routeStats = this.calculateRouteStats();

    return {
      timestamp: Date.now(),
      uptime: performance.now() - this.startTime,
      requestStats,
      performanceStats,
      routeStats
    };
  }

  private calculateRequestStats() {
    if (this.requests.length === 0) {
      return {
        totalRequests: 0,
        requestsPerSecond: 0,
        averageResponseTime: 0,
        errorRate: 0,
        p95ResponseTime: 0,
        p99ResponseTime: 0
      };
    }

    const totalRequests = this.requests.length;
    const uptime = performance.now() - this.startTime;
    const requestsPerSecond = totalRequests / (uptime / 1000);

    const responseTimes = this.requests.map(r => r.duration);
    const averageResponseTime = responseTimes.reduce((sum, time) => sum + time, 0) / totalRequests;

    const errorRequests = this.requests.filter(r => r.statusCode >= 400);
    const errorRate = (errorRequests.length / totalRequests) * 100;

    return {
      totalRequests,
      requestsPerSecond,
      averageResponseTime,
      errorRate,
      p95ResponseTime: this.calculatePercentile(responseTimes, 95),
      p99ResponseTime: this.calculatePercentile(responseTimes, 99)
    };
  }

  private getPerformanceStats(): PerformanceMetrics {
    const memUsage = process.memoryUsage();
    
    return {
      cpuUsage: process.cpuUsage().user / 1000000, // 转换为秒
      memoryUsage: memUsage,
      activeConnections: 0, // 需要根据具体实现获取
      requestsPerSecond: this.calculateCurrentRPS()
    };
  }

  private calculateRouteStats() {
    const routeStats = new Map<string, any>();

    for (const req of this.requests) {
      const routeKey = `${req.method} ${req.url}`;
      
      if (!routeStats.has(routeKey)) {
        routeStats.set(routeKey, {
          count: 0,
          totalDuration: 0,
          averageDuration: 0,
          errors: 0
        });
      }

      const stats = routeStats.get(routeKey);
      stats.count++;
      stats.totalDuration += req.duration;
      stats.averageDuration = stats.totalDuration / stats.count;

      if (req.statusCode >= 400) {
        stats.errors++;
      }
    }

    // 转换为数组并按请求量排序
    return Array.from(routeStats.entries())
      .map(([route, stats]) => ({ route, ...stats }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10); // 返回前10个最繁忙的路由
  }

  private calculatePercentile(values: number[], percentile: number): number {
    if (values.length === 0) return 0;

    const sorted = values.sort((a, b) => a - b);
    const index = Math.floor(sorted.length * (percentile / 100));
    return sorted[Math.min(index, sorted.length - 1)];
  }

  private calculateCurrentRPS(): number {
    const now = performance.now();
    const recentRequests = this.requests.filter(r => now - r.timestamp < 60000); // 最近1分钟
    return recentRequests.length / 60; // 每秒请求数
  }

  private startMetricsCollection() {
    // 每30秒收集一次系统指标
    this.metricsInterval = setInterval(() => {
      this.collectSystemMetrics();
    }, 30000);
  }

  private collectSystemMetrics() {
    // 收集系统级性能指标
    const metrics = this.getPerformanceStats();
    
    // 可以在这里发送到监控系统
    console.log('System Metrics:', {
      memory: metrics.memoryUsage,
      cpu: metrics.cpuUsage,
      rps: metrics.requestsPerSecond
    });
  }
}

// 性能监控中间件
export function PerformanceMonitorMiddleware(monitor: NestJSPerformanceMonitor) {
  return (req: any, res: any, next: any) => {
    const startTime = performance.now();

    res.on('finish', () => {
      const duration = performance.now() - startTime;
      monitor.recordRequest(req, res, duration);
    });

    next();
  };
}

// 使用示例
import { Module } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { NestJSPerformanceMonitor, PerformanceMonitorMiddleware } from './performance-monitor';

@Module({
  providers: [
    NestJSPerformanceMonitor,
    {
      provide: APP_INTERCEPTOR,
      useFactory: (monitor: NestJSPerformanceMonitor) => {
        return PerformanceMonitorMiddleware(monitor);
      },
      inject: [NestJSPerformanceMonitor]
    }
  ]
})
export class PerformanceModule {}
```

## NestJS企业架构最佳实践

### 模块设计原则
1. **单一职责**: 每个模块只负责一个功能领域
2. **松耦合**: 模块间依赖最小化
3. **高内聚**: 相关功能集中在同一模块
4. **清晰边界**: 明确的模块接口和边界
5. **可测试性**: 模块易于单元测试

### 依赖注入最佳实践
1. **接口抽象**: 使用接口定义服务契约
2. **作用域选择**: 根据需求选择合适的作用域
3. **循环依赖**: 避免和解决循环依赖问题
4. **工厂模式**: 使用工厂模式创建复杂依赖
5. **生命周期**: 正确管理服务生命周期

### 微服务架构
1. **服务拆分**: 按业务边界拆分服务
2. **通信模式**: 选择合适的通信模式
3. **数据一致性**: 保证分布式数据一致性
4. **服务发现**: 实现自动服务发现
5. **容错处理**: 实现熔断和重试机制

### 企业级功能
1. **身份验证**: 统一身份验证和授权
2. **配置管理**: 集中配置管理
3. **日志记录**: 结构化日志记录
4. **监控告警**: 全链路监控和告警
5. **缓存策略**: 多层缓存架构

## 相关技能

- **microservices** - 微服务架构
- **typescript-development** - TypeScript开发
- **api-design** - API设计
- **dependency-injection** - 依赖注入
