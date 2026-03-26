# Regex 测试器技术参考

## 概述

Regex 测试器是一个专门用于测试和调试正则表达式的工具，提供实时匹配、分组捕获、替换操作和性能分析功能。

## 核心功能

### 正则表达式引擎
- **多引擎支持**: JavaScript、Python、PCRE、.NET、Java 正则引擎
- **语法高亮**: 实时高亮正则表达式语法
- **错误提示**: 语法错误实时检测和提示
- **自动完成**: 常用模式自动完成

### 测试功能
- **实时匹配**: 输入文本实时显示匹配结果
- **分组捕获**: 显示所有捕获组和命名分组
- **替换操作**: 测试正则表达式替换功能
- **批量测试**: 支持多个测试用例批量测试

### 性能分析
- **执行时间**: 测量正则表达式执行时间
- **回溯分析**: 分析正则表达式的回溯行为
- **优化建议**: 提供正则表达式优化建议
- **压力测试**: 大文本和复杂表达式压力测试

## 配置指南

### 基础配置
```json
{
  "regex-tester": {
    "engine": "javascript",
    "flags": {
      "global": true,
      "ignore-case": false,
      "multiline": false,
      "dot-all": false,
      "unicode": true
    },
    "display": {
      "highlight-matches": true,
      "show-groups": true,
      "show-positions": true,
      "show-match-count": true
    },
    "performance": {
      "enable-profiling": true,
      "timeout": 5000,
      "max-test-size": 1000000
    }
  }
}
```

### 高级配置
```json
{
  "regex-tester": {
    "advanced": {
      "engines": {
        "javascript": {
          "enabled": true,
          "flavor": "es2022"
        },
        "python": {
          "enabled": true,
          "version": "3.10"
        },
        "pcre": {
          "enabled": true,
          "version": "8.45"
        }
      },
      "testing": {
        "auto-save": true,
        "test-sets": true,
        "benchmark-mode": false,
        "memory-limit": "512MB"
      },
      "debugging": {
        "step-by-step": true,
        "backtracking-visualization": true,
        "tree-view": true,
        "performance-graph": true
      }
    }
  }
}
```

## API 参考

### 正则测试器主类
```javascript
class RegexTester {
  constructor(config = {}) {
    this.config = new Config(config);
    this.engine = this.createEngine();
    this.tester = new RegexEngine(this.engine);
    this.analyzer = new PerformanceAnalyzer();
  }

  // 测试正则表达式
  test(pattern, text, flags = {}) {
    try {
      const regex = this.engine.compile(pattern, flags);
      const results = this.tester.execute(regex, text);
      
      return new TestResult({
        pattern,
        text,
        matches: results.matches,
        groups: results.groups,
        positions: results.positions,
        executionTime: results.executionTime,
        valid: true
      });
    } catch (error) {
      return new TestResult({
        pattern,
        text,
        error: error.message,
        valid: false
      });
    }
  }

  // 批量测试
  batchTest(pattern, testCases, flags = {}) {
    const results = [];
    
    for (const testCase of testCases) {
      const result = this.test(pattern, testCase.text, flags);
      results.push({
        name: testCase.name,
        expected: testCase.expected,
        actual: result.matches,
        passed: this.compareResults(result.matches, testCase.expected)
      });
    }
    
    return new BatchTestResult(results);
  }

  // 性能测试
  performanceTest(pattern, text, iterations = 1000) {
    const regex = this.engine.compile(pattern);
    const startTime = performance.now();
    
    for (let i = 0; i < iterations; i++) {
      this.tester.execute(regex, text);
    }
    
    const endTime = performance.now();
    const totalTime = endTime - startTime;
    
    return new PerformanceResult({
      pattern,
      textLength: text.length,
      iterations,
      totalTime,
      averageTime: totalTime / iterations,
      matchesPerSecond: iterations / (totalTime / 1000)
    });
  }

  // 替换测试
  replaceTest(pattern, text, replacement, flags = {}) {
    try {
      const regex = this.engine.compile(pattern, flags);
      const result = this.tester.replace(regex, text, replacement);
      
      return new ReplaceResult({
        pattern,
        text,
        replacement,
        result,
        replacements: this.getReplacementCount(regex, text),
        valid: true
      });
    } catch (error) {
      return new ReplaceResult({
        pattern,
        text,
        replacement,
        error: error.message,
        valid: false
      });
    }
  }
}
```

### 正则引擎接口
```javascript
class RegexEngine {
  constructor(type) {
    this.type = type;
    this.supportedFlags = this.getSupportedFlags();
  }

  // 编译正则表达式
  compile(pattern, flags = {}) {
    const compiledFlags = this.buildFlags(flags);
    
    switch (this.type) {
      case 'javascript':
        return new RegExp(pattern, compiledFlags);
      case 'python':
        return this.compilePython(pattern, flags);
      case 'pcre':
        return this.compilePCRE(pattern, flags);
      default:
        throw new Error(`Unsupported engine type: ${this.type}`);
    }
  }

  // 执行匹配
  execute(regex, text) {
    const matches = [];
    let match;
    
    if (regex.global) {
      while ((match = regex.exec(text)) !== null) {
        matches.push(this.processMatch(match));
      }
    } else {
      match = regex.exec(text);
      if (match !== null) {
        matches.push(this.processMatch(match));
      }
    }
    
    return {
      matches,
      groups: this.extractGroups(matches),
      positions: this.extractPositions(matches)
    };
  }

  // 替换操作
  replace(regex, text, replacement) {
    return text.replace(regex, replacement);
  }

  // 处理匹配结果
  processMatch(match) {
    return {
      full: match[0],
      groups: match.slice(1),
      index: match.index,
      length: match[0].length,
      input: match.input
    };
  }

  // 提取分组信息
  extractGroups(matches) {
    const groups = {};
    
    matches.forEach((match, index) => {
      match.groups.forEach((group, groupIndex) => {
        if (!groups[groupIndex]) {
          groups[groupIndex] = [];
        }
        groups[groupIndex].push(group);
      });
    });
    
    return groups;
  }

  // 构建标志字符串
  buildFlags(flags) {
    const flagMap = {
      'global': 'g',
      'ignore-case': 'i',
      'multiline': 'm',
      'dot-all': 's',
      'unicode': 'u',
      'sticky': 'y'
    };
    
    return Object.entries(flags)
      .filter(([key, value]) => value && flagMap[key])
      .map(([key, value]) => flagMap[key])
      .join('');
  }
}
```

### 性能分析器
```javascript
class PerformanceAnalyzer {
  constructor() {
    this.metrics = new Map();
    this.profiler = new Profiler();
  }

  // 分析正则表达式性能
  analyze(pattern, text, options = {}) {
    const analysis = {
      complexity: this.calculateComplexity(pattern),
      backtracking: this.analyzeBacktracking(pattern),
      optimizations: this.suggestOptimizations(pattern),
      benchmarks: this.runBenchmarks(pattern, text, options)
    };
    
    return new PerformanceAnalysis(analysis);
  }

  // 计算复杂度
  calculateComplexity(pattern) {
    let complexity = 1;
    
    // 分析嵌套量词
    const nestedQuantifiers = pattern.match(/\*.*\*|\+.*\+|\{.*\}.*\{/g);
    if (nestedQuantifiers) {
      complexity += nestedQuantifiers.length * 2;
    }
    
    // 分析交替分支
    const alternations = pattern.match(/\|/g);
    if (alternations) {
      complexity += alternations.length;
    }
    
    // 分析字符类
    const characterClasses = pattern.match(/\[.*?\]/g);
    if (characterClasses) {
      complexity += characterClasses.length * 0.5;
    }
    
    return Math.round(complexity);
  }

  // 分析回溯风险
  analyzeBacktracking(pattern) {
    const risks = [];
    
    // 检测嵌套量词
    if (/\*.*\*|\+.*\+/.test(pattern)) {
      risks.push({
        type: 'nested_quantifiers',
        severity: 'high',
        description: '嵌套量词可能导致指数级回溯'
      });
    }
    
    // 检测交替重叠
    if (/\|.*\|/.test(pattern)) {
      risks.push({
        type: 'overlapping_alternation',
        severity: 'medium',
        description: '交替分支重叠可能导致回溯'
      });
    }
    
    // 检测贪婪量词
    if (/.*\*.*|.*\+./.test(pattern)) {
      risks.push({
        type: 'greedy_quantifiers',
        severity: 'low',
        description: '贪婪量词可能影响性能'
      });
    }
    
    return risks;
  }

  // 建议优化
  suggestOptimizations(pattern) {
    const optimizations = [];
    
    // 建议使用原子分组
    if (/\(.*\*.*\)|\(.*\+.*\)/.test(pattern)) {
      optimizations.push({
        type: 'atomic_grouping',
        suggestion: '考虑使用原子分组 (?>...) 避免回溯',
        example: pattern.replace(/\(([^)]*[*+][^)]*)\)/g, '(?>$1)')
      });
    }
    
    // 建议使用占有量词
    if (/\*|\+/.test(pattern) && !/\*\+|\+\*/.test(pattern)) {
      optimizations.push({
        type: 'possessive_quantifiers',
        suggestion: '考虑使用占有量词 (*+, ++, ?+) 提高性能',
        example: pattern.replace(/\*/g, '*+').replace(/\+/g, '++')
      });
    }
    
    // 建议字符类优化
    if (/\.\*|\.\+/.test(pattern)) {
      optimizations.push({
        type: 'character_class',
        suggestion: '使用字符类替代点号通配符',
        example: pattern.replace(/\./g, '[^\\n]')
      });
    }
    
    return optimizations;
  }

  // 运行基准测试
  runBenchmarks(pattern, text, options = {}) {
    const iterations = options.iterations || 1000;
    const engines = options.engines || ['javascript', 'python'];
    
    const results = {};
    
    engines.forEach(engine => {
      const tester = new RegexTester({ engine });
      const startTime = performance.now();
      
      for (let i = 0; i < iterations; i++) {
        tester.test(pattern, text);
      }
      
      const endTime = performance.now();
      results[engine] = {
        totalTime: endTime - startTime,
        averageTime: (endTime - startTime) / iterations,
        iterationsPerSecond: iterations / ((endTime - startTime) / 1000)
      };
    });
    
    return results;
  }
}
```

## 内置模式库

### 常用模式
```javascript
const CommonPatterns = {
  // 邮箱地址
  email: {
    pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    description: '匹配邮箱地址',
    example: 'user@example.com'
  },
  
  // URL
  url: {
    pattern: /^https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$/,
    description: '匹配 HTTP/HTTPS URL',
    example: 'https://www.example.com/path?query=value#fragment'
  },
  
  // IP 地址
  ipAddress: {
    pattern: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
    description: '匹配 IPv4 地址',
    example: '192.168.1.1'
  },
  
  // 电话号码
  phoneNumber: {
    pattern: /^\+?(\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}$/,
    description: '匹配电话号码',
    example: '+1 (555) 123-4567'
  },
  
  // 日期
  date: {
    pattern: /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/,
    description: '匹配 YYYY-MM-DD 格式日期',
    example: '2023-12-25'
  },
  
  // 用户名
  username: {
    pattern: /^[a-zA-Z0-9_]{3,20}$/,
    description: '匹配用户名（3-20个字符）',
    example: 'john_doe123'
  },
  
  // 密码强度
  strongPassword: {
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
    description: '匹配强密码（至少8位，包含大小写字母、数字和特殊字符）',
    example: 'StrongP@ssw0rd'
  },
  
  // 十六进制颜色
  hexColor: {
    pattern: /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/,
    description: '匹配十六进制颜色值',
    example: '#FF5733'
  }
};
```

## 集成指南

### Web 应用集成
```html
<!DOCTYPE html>
<html>
<head>
    <title>Regex Tester</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="app">
        <div class="input-section">
            <div class="pattern-input">
                <label for="pattern">正则表达式:</label>
                <input type="text" id="pattern" placeholder="输入正则表达式">
                <div class="flags">
                    <label><input type="checkbox" id="global"> 全局 (g)</label>
                    <label><input type="checkbox" id="ignore-case"> 忽略大小写 (i)</label>
                    <label><input type="checkbox" id="multiline"> 多行 (m)</label>
                </div>
            </div>
            
            <div class="test-input">
                <label for="test-text">测试文本:</label>
                <textarea id="test-text" rows="10" placeholder="输入要测试的文本"></textarea>
            </div>
        </div>
        
        <div class="results-section">
            <div class="matches">
                <h3>匹配结果</h3>
                <div id="match-results"></div>
            </div>
            
            <div class="groups">
                <h3>捕获分组</h3>
                <div id="group-results"></div>
            </div>
            
            <div class="performance">
                <h3>性能分析</h3>
                <div id="performance-results"></div>
            </div>
        </div>
    </div>
    
    <script src="regex-tester.js"></script>
    <script src="app.js"></script>
</body>
</html>
```

### Node.js 集成
```javascript
// regex-cli.js
#!/usr/bin/env node

const { RegexTester } = require('./regex-tester');
const fs = require('fs');
const readline = require('readline');

class RegexCLI {
  constructor() {
    this.tester = new RegexTester();
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async run() {
    console.log('Regex Tester CLI');
    console.log('Enter "help" for commands, "quit" to exit');
    
    while (true) {
      const command = await this.prompt('regex> ');
      
      if (command === 'quit') {
        break;
      }
      
      if (command === 'help') {
        this.showHelp();
        continue;
      }
      
      if (command.startsWith('test ')) {
        const args = command.slice(5).split(' ');
        await this.runTest(args[0], args[1]);
        continue;
      }
      
      if (command.startsWith('file ')) {
        const filename = command.slice(5);
        await this.testFile(filename);
        continue;
      }
      
      console.log('Unknown command. Type "help" for assistance.');
    }
    
    this.rl.close();
  }

  async runTest(pattern, text) {
    if (!pattern || !text) {
      console.log('Usage: test <pattern> <text>');
      return;
    }
    
    const result = this.tester.test(pattern, text);
    
    if (result.valid) {
      console.log(`✓ Pattern valid`);
      console.log(`Matches: ${result.matches.length}`);
      
      result.matches.forEach((match, index) => {
        console.log(`  ${index + 1}. "${match.full}" at position ${match.index}`);
      });
    } else {
      console.log(`✗ Pattern invalid: ${result.error}`);
    }
  }

  async testFile(filename) {
    try {
      const content = fs.readFileSync(filename, 'utf8');
      const lines = content.split('\n');
      
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].trim() && !lines[i].startsWith('#')) {
          const [pattern, text] = lines[i].split('\t');
          if (pattern && text) {
            console.log(`Testing line ${i + 1}: ${pattern}`);
            await this.runTest(pattern, text);
            console.log('');
          }
        }
      }
    } catch (error) {
      console.log(`Error reading file: ${error.message}`);
    }
  }

  showHelp() {
    console.log('Available commands:');
    console.log('  test <pattern> <text>  - Test a regex pattern');
    console.log('  file <filename>        - Test patterns from file');
    console.log('  help                   - Show this help');
    console.log('  quit                   - Exit the program');
  }

  prompt(question) {
    return new Promise(resolve => {
      this.rl.question(question, resolve);
    });
  }
}

// 运行 CLI
if (require.main === module) {
  const cli = new RegexCLI();
  cli.run().catch(console.error);
}
```

## 最佳实践

### 正则表达式优化
1. **避免回溯**: 使用原子分组和占有量词
2. **字符类优化**: 使用具体字符类替代通配符
3. **锚点使用**: 合理使用开始和结束锚点
4. **预编译**: 重复使用的正则表达式预编译

### 测试策略
1. **边界测试**: 测试边界情况和特殊字符
2. **性能测试**: 对大文本进行性能测试
3. **跨引擎测试**: 在不同正则引擎中测试
4. **回归测试**: 保存测试用例防止回归

### 调试技巧
1. **逐步构建**: 从简单模式逐步构建复杂模式
2. **分组分析**: 分析每个分组的匹配内容
3. **可视化工具**: 使用可视化工具理解匹配过程
4. **性能分析**: 使用性能分析器找出瓶颈

## 故障排除

### 常见问题
1. **语法错误**: 检查括号、引号和转义字符
2. **性能问题**: 优化复杂正则表达式
3. **引擎差异**: 注意不同引擎的语法差异
4. **编码问题**: 确保文本编码正确

### 调试工具
1. **在线测试器**: 使用在线正则测试工具
2. **调试模式**: 启用详细的调试输出
3. **性能分析**: 使用性能分析工具
4. **可视化**: 使用正则表达式可视化工具

## 工具和资源

### 在线工具
- **Regex101**: 在线正则表达式测试器
- **RegExr**: 正则表达式学习和测试工具
- **Debuggex**: 正则表达式调试工具
- **Regex Pal**: 简单的正则测试工具

### 开发库
- **JavaScript**: 原生 RegExp 对象
- **Python**: re 模块
- **Java**: java.util.regex 包
- **.NET**: System.Text.RegularExpressions

### 学习资源
- [正则表达式教程](https://www.regular-expressions.info/)
- [MDN 正则表达式](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions)
- [Python 正则文档](https://docs.python.org/3/library/re.html)
- [正则表达式速查](https://cheatography.com/cheat-sheets/regex-cheat-sheet)

### 社区支持
- [Stack Overflow Regex 标签](https://stackoverflow.com/questions/tagged/regex)
- [Reddit 正则表达式社区](https://www.reddit.com/r/regex/)
- [正则表达式论坛](https://regexforums.com/)
- [GitHub 正则表达式项目](https://github.com/topics/regex)
