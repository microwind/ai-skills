# JavaScript Analyzer 技术参考

## 概述

JavaScript Analyzer 是一个专门用于分析 JavaScript 代码质量的工具，提供静态代码分析、性能优化建议、安全漏洞检测和代码规范检查功能。

## 核心功能

### 静态代码分析
- **语法检查**: 检测 JavaScript 语法错误和潜在问题
- **代码质量**: 分析代码复杂度、可维护性和可读性
- **最佳实践**: 检查是否遵循 JavaScript 最佳实践
- **代码规范**: 验证代码风格和格式规范

### 性能分析
- **执行效率**: 分析代码执行性能瓶颈
- **内存使用**: 检测内存泄漏和优化建议
- **依赖分析**: 分析模块依赖关系和循环依赖
- **包大小分析**: 分析打包后的文件大小和优化建议

### 安全检查
- **XSS 漏洞**: 检测跨站脚本攻击风险
- **注入攻击**: 检查 SQL 注入和其他注入攻击
- **敏感信息**: 识别硬编码的敏感数据
- **依赖安全**: 检查第三方依赖的安全漏洞

## 配置指南

### 基础配置
```json
{
  "javascript-analyzer": {
    "enabled": true,
    "rules": {
      "syntax": {
        "enabled": true,
        "strict": true,
        "ecmaVersion": 2022,
        "sourceType": "module"
      },
      "quality": {
        "enabled": true,
        "complexity": {
          "max": 10,
          "threshold": "warning"
        },
        "maintainability": {
          "min": 70,
          "threshold": "error"
        }
      },
      "security": {
        "enabled": true,
        "xss": true,
        "injection": true,
        "sensitive-data": true
      }
    },
    "ignore": [
      "node_modules/**",
      "dist/**",
      "coverage/**"
    ]
  }
}
```

### 高级配置
```json
{
  "javascript-analyzer": {
    "advanced": {
      "performance": {
        "enabled": true,
        "profiling": true,
        "memory-analysis": true,
        "bundle-analysis": true
      },
      "custom-rules": [
        {
          "name": "no-console-in-production",
          "pattern": "console\\.(log|warn|error)",
          "severity": "warning",
          "message": "Console statements should not be used in production"
        },
        {
          "name": "require-await-in-async",
          "pattern": "async\\s+function[^{]*\\{[^}]*await",
          "severity": "error",
          "message": "Async functions should contain await"
        }
      ],
      "formatters": {
        "eslint": true,
        "prettier": true,
        "custom": "./custom-formatter.js"
      }
    }
  }
}
```

## API 参考

### 分析 API
```javascript
// 分析器主类
class JavaScriptAnalyzer {
  constructor(config = {}) {
    this.config = new Config(config);
    this.rules = new RuleManager(this.config);
    this.parser = new JavaScriptParser(this.config);
  }

  // 分析文件
  async analyzeFile(filePath) {
    const content = await fs.readFile(filePath, 'utf8');
    const ast = this.parser.parse(content, filePath);
    const issues = await this.rules.analyze(ast, content, filePath);
    
    return new AnalysisResult({
      file: filePath,
      issues,
      metrics: this.calculateMetrics(ast, content),
      timestamp: new Date()
    });
  }

  // 分析目录
  async analyzeDirectory(dirPath) {
    const files = await this.getJavaScriptFiles(dirPath);
    const results = await Promise.all(
      files.map(file => this.analyzeFile(file))
    );
    
    return new DirectoryAnalysisResult({
      directory: dirPath,
      files: results,
      summary: this.generateSummary(results)
    });
  }

  // 实时分析
  startWatching(paths, callback) {
    const watcher = chokidar.watch(paths, {
      ignored: this.config.ignore,
      persistent: true
    });

    watcher.on('change', async (filePath) => {
      const result = await this.analyzeFile(filePath);
      callback(result);
    });

    return watcher;
  }
}
```

### 规则系统
```javascript
// 自定义规则基类
class BaseRule {
  constructor(config) {
    this.config = config;
    this.severity = config.severity || 'warning';
  }

  analyze(node, context) {
    throw new Error('analyze method must be implemented');
  }

  report(node, message, severity = this.severity) {
    return {
      rule: this.constructor.name,
      message,
      severity,
      line: node.loc?.start?.line,
      column: node.loc?.start?.column,
      source: context.getSource(node)
    };
  }
}

// 具体规则实现
class NoConsoleRule extends BaseRule {
  analyze(node, context) {
    const issues = [];
    
    if (node.type === 'CallExpression' &&
        node.callee.type === 'MemberExpression' &&
        node.callee.object.name === 'console') {
      
      issues.push(this.report(
        node,
        'Console statements should not be used in production',
        'warning'
      ));
    }
    
    return issues;
  }
}

class ComplexityRule extends BaseRule {
  analyze(node, context) {
    const complexity = this.calculateComplexity(node);
    const threshold = this.config.maxComplexity || 10;
    
    if (complexity > threshold) {
      return [this.report(
        node,
        `Function complexity (${complexity}) exceeds threshold (${threshold})`,
        'error'
      )];
    }
    
    return [];
  }

  calculateComplexity(node) {
    let complexity = 1;
    
    // 计算圈复杂度
    const complexityNodes = [
      'IfStatement', 'WhileStatement', 'ForStatement',
      'SwitchStatement', 'ConditionalExpression', 'LogicalExpression'
    ];
    
    const traverse = (node) => {
      if (complexityNodes.includes(node.type)) {
        complexity++;
      }
      
      for (const child of Object.values(node)) {
        if (Array.isArray(child)) {
          child.forEach(traverse);
        } else if (child && typeof child === 'object') {
          traverse(child);
        }
      }
    };
    
    traverse(node);
    return complexity;
  }
}
```

### 性能分析
```javascript
// 性能分析器
class PerformanceAnalyzer {
  constructor() {
    this.metrics = new Map();
    this.profiler = new Profiler();
  }

  // 分析函数性能
  analyzeFunctionPerformance(ast) {
    const functions = this.extractFunctions(ast);
    const performanceIssues = [];

    for (const func of functions) {
      const metrics = this.analyzeFunction(func);
      
      if (metrics.complexity > 10) {
        performanceIssues.push({
          type: 'high-complexity',
          function: func.name,
          complexity: metrics.complexity,
          suggestion: 'Consider breaking down this function into smaller functions'
        });
      }

      if (metrics.params.length > 5) {
        performanceIssues.push({
          type: 'too-many-parameters',
          function: func.name,
          paramCount: metrics.params.length,
          suggestion: 'Consider using an options object instead of multiple parameters'
        });
      }
    }

    return performanceIssues;
  }

  // 分析内存使用
  analyzeMemoryUsage(code) {
    const memoryIssues = [];
    
    // 检测潜在的内存泄漏
    const leakPatterns = [
      {
        pattern: /addEventListener.*\{[^}]*\}/g,
        issue: 'potential-memory-leak',
        suggestion: 'Ensure event listeners are properly removed'
      },
      {
        pattern: /setInterval.*\{[^}]*\}/g,
        issue: 'interval-not-cleared',
        suggestion: 'Store interval ID and clear it when no longer needed'
      }
    ];

    for (const { pattern, issue, suggestion } of leakPatterns) {
      const matches = code.match(pattern);
      if (matches) {
        memoryIssues.push({
          type: issue,
          matches: matches.length,
          suggestion
        });
      }
    }

    return memoryIssues;
  }

  // 分析包大小
  analyzeBundleSize(bundlePath) {
    const stats = fs.statSync(bundlePath);
    const size = stats.size;
    const issues = [];

    if (size > 1024 * 1024) { // 1MB
      issues.push({
        type: 'large-bundle',
        size: this.formatBytes(size),
        suggestion: 'Consider code splitting and tree shaking'
      });
    }

    return {
      size: this.formatBytes(size),
      issues
    };
  }

  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
```

## 安全检查

### 安全规则
```javascript
// 安全分析器
class SecurityAnalyzer {
  constructor() {
    this.vulnerabilityPatterns = [
      {
        name: 'xss-vulnerability',
        pattern: /innerHTML\s*=\s*.*\+/g,
        severity: 'high',
        description: 'Potential XSS vulnerability'
      },
      {
        name: 'sql-injection',
        pattern: /query\s*\(\s*.*\+/g,
        severity: 'critical',
        description: 'Potential SQL injection'
      },
      {
        name: 'hardcoded-secret',
        pattern: /(password|secret|token)\s*=\s*['"][^'"]{8,}['"]/g,
        severity: 'high',
        description: 'Hardcoded secret detected'
      }
    ];
  }

  analyzeCode(code) {
    const vulnerabilities = [];

    for (const pattern of this.vulnerabilityPatterns) {
      const matches = code.match(pattern.pattern);
      if (matches) {
        vulnerabilities.push({
          type: pattern.name,
          severity: pattern.severity,
          description: pattern.description,
          occurrences: matches.length,
          matches: matches.slice(0, 3) // Show first 3 matches
        });
      }
    }

    return vulnerabilities;
  }

  analyzeDependencies(packageJson) {
    const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
    const vulnerabilities = [];

    // 这里可以集成已知的漏洞数据库
    const knownVulnerabilities = this.getKnownVulnerabilities();
    
    for (const [name, version] of Object.entries(dependencies)) {
      const vulns = knownVulnerabilities[name];
      if (vulns && this.isVersionVulnerable(version, vulns)) {
        vulnerabilities.push({
          package: name,
          version,
          vulnerabilities: vulns.filter(v => this.isVersionVulnerable(version, [v]))
        });
      }
    }

    return vulnerabilities;
  }

  isVersionVulnerable(version, vulnerabilities) {
    return vulnerabilities.some(vuln => {
      return semver.satisfies(version, vuln.affectedVersions);
    });
  }
}
```

## 集成指南

### CLI 工具
```javascript
#!/usr/bin/env node

const { Command } = require('commander');
const JavaScriptAnalyzer = require('./lib/analyzer');

const program = new Command();

program
  .name('js-analyzer')
  .description('JavaScript code analyzer')
  .version('1.0.0');

program
  .command('analyze')
  .description('Analyze JavaScript files')
  .argument('<path>', 'File or directory to analyze')
  .option('-c, --config <config>', 'Configuration file')
  .option('-f, --format <format>', 'Output format (json, table, markdown)')
  .option('-o, --output <output>', 'Output file')
  .action(async (path, options) => {
    const analyzer = new JavaScriptAnalyzer(options.config);
    const result = await analyzer.analyzeDirectory(path);
    
    const formatter = getFormatter(options.format);
    const output = formatter.format(result);
    
    if (options.output) {
      await fs.writeFile(options.output, output);
    } else {
      console.log(output);
    }
  });

program
  .command('watch')
  .description('Watch files for changes')
  .argument('<path>', 'Directory to watch')
  .option('-c, --config <config>', 'Configuration file')
  .action(async (path, options) => {
    const analyzer = new JavaScriptAnalyzer(options.config);
    
    analyzer.startWatching(path, (result) => {
      console.log(`Issues found in ${result.file}:`);
      result.issues.forEach(issue => {
        console.log(`  ${issue.severity}: ${issue.message}`);
      });
    });
    
    console.log(`Watching ${path} for changes...`);
  });

program.parse();
```

### VS Code 扩展
```typescript
import * as vscode from 'vscode';
import { JavaScriptAnalyzer } from './analyzer';

export function activate(context: vscode.ExtensionContext) {
  const analyzer = new JavaScriptAnalyzer();
  
  // 诊断提供者
  const diagnosticCollection = vscode.languages.createDiagnosticCollection('js-analyzer');
  context.subscriptions.push(diagnosticCollection);

  // 分析当前文档
  const analyzeDocument = async (document: vscode.TextDocument) => {
    if (document.languageId !== 'javascript' && document.languageId !== 'typescript') {
      return;
    }

    const result = await analyzer.analyzeFile(document.uri.fsPath);
    const diagnostics = result.issues.map(issue => {
      const range = new vscode.Range(
        new vscode.Position(issue.line - 1, issue.column - 1),
        new vscode.Position(issue.line - 1, issue.column - 1)
      );
      
      return new vscode.Diagnostic(
        range,
        issue.message,
        issue.severity === 'error' ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning
      );
    });

    diagnosticCollection.set(document.uri, diagnostics);
  };

  // 注册事件监听器
  vscode.workspace.onDidOpenTextDocument(analyzeDocument);
  vscode.workspace.onDidChangeTextDocument(async (event) => {
    await analyzeDocument(event.document);
  });

  // 分析所有打开的文档
  vscode.workspace.textDocuments.forEach(analyzeDocument);

  // 注册命令
  const analyzeCommand = vscode.commands.registerCommand('js-analyzer.analyze', async () => {
    const editor = vscode.window.activeTextEditor;
    if (editor) {
      await analyzeDocument(editor.document);
      vscode.window.showInformationMessage('Analysis complete!');
    }
  });

  context.subscriptions.push(analyzeCommand);
}
```

## 最佳实践

### 代码质量
1. **一致性**: 保持代码风格和格式的一致性
2. **可读性**: 编写清晰、易懂的代码
3. **可维护性**: 遵循 SOLID 原则和设计模式
4. **测试覆盖**: 确保充分的单元测试和集成测试

### 性能优化
1. **懒加载**: 按需加载模块和组件
2. **代码分割**: 将代码拆分为更小的块
3. **缓存策略**: 合理使用缓存机制
4. **异步处理**: 使用异步操作避免阻塞

### 安全防护
1. **输入验证**: 验证所有用户输入
2. **输出编码**: 对输出进行适当的编码
3. **依赖管理**: 定期更新依赖包
4. **权限控制**: 实施适当的访问控制

## 故障排除

### 常见问题
1. **解析错误**: 检查 JavaScript 语法是否正确
2. **性能问题**: 优化分析规则和配置
3. **内存不足**: 调整 JVM 或 Node.js 内存限制
4. **配置错误**: 验证配置文件格式和内容

### 调试技巧
1. **详细日志**: 启用详细的调试日志
2. **分步分析**: 逐步分析问题所在
3. **测试用例**: 创建重现问题的测试用例
4. **性能分析**: 使用性能分析工具

## 扩展开发

### 自定义规则
```javascript
class CustomRule extends BaseRule {
  constructor(config) {
    super(config);
    this.ruleName = config.name || 'custom-rule';
  }

  analyze(node, context) {
    // 实现自定义分析逻辑
    const issues = [];
    
    // 示例：检查函数命名约定
    if (node.type === 'FunctionDeclaration' && 
        !this.isValidFunctionName(node.id.name)) {
      issues.push(this.report(
        node,
        `Function name "${node.id.name}" does not follow naming convention`,
        'warning'
      ));
    }
    
    return issues;
  }

  isValidFunctionName(name) {
    // 实现命名约定检查
    return /^[a-z][a-zA-Z0-9]*$/.test(name);
  }
}
```

### 自定义格式化器
```javascript
class CustomFormatter {
  format(result) {
    const output = [];
    
    output.push(`# Analysis Report for ${result.file}`);
    output.push(`Generated: ${result.timestamp}`);
    output.push(`Total Issues: ${result.issues.length}`);
    output.push('');
    
    if (result.issues.length > 0) {
      output.push('## Issues Found:');
      result.issues.forEach((issue, index) => {
        output.push(`${index + 1}. **${issue.severity.toUpperCase()}** - ${issue.message}`);
        output.push(`   Line: ${issue.line}, Column: ${issue.column}`);
        output.push(`   Rule: ${issue.rule}`);
        output.push('');
      });
    } else {
      output.push('✅ No issues found!');
    }
    
    return output.join('\n');
  }
}
```

## 工具和资源

### 开发工具
- **ESLint**: JavaScript 代码检查工具
- **Prettier**: 代码格式化工具
- **Jest**: JavaScript 测试框架
- **Webpack**: 模块打包工具

### 相关库
- **@babel/parser**: JavaScript 解析器
- **acorn**: JavaScript 解析引擎
- **esprima**: JavaScript 语法分析器
- **semver**: 语义化版本管理

### 学习资源
- [MDN JavaScript 文档](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [ESLint 官方文档](https://eslint.org/docs/)
- [JavaScript 最佳实践](https://github.com/ryanmcdermott/clean-code-javascript)
- [Node.js 官方文档](https://nodejs.org/docs/)

### 社区支持
- [Stack Overflow JavaScript 标签](https://stackoverflow.com/questions/tagged/javascript)
- [JavaScript GitHub 仓库](https://github.com/topics/javascript)
- [JavaScript Weekly](https://javascriptweekly.com/)
- [Node.js 中文社区](https://cnodejs.org/)
