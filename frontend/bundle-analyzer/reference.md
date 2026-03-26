# 打包分析器技术参考

## 概述

打包分析器是前端开发中的重要工具，用于分析和优化JavaScript应用的打包结果。本文档详细介绍了打包分析的核心概念、工具使用、优化技巧和最佳实践。

## 核心概念

### 打包分析基础
- **Bundle**: 将多个模块打包成单个或多个文件的过程
- **Chunk**: 打包后的代码块，可以是同步或异步加载
- **Module**: 应用中的单个模块文件
- **Dependency**: 模块之间的依赖关系

### 分析维度
- **大小分析**: 分析打包文件的大小和组成
- **依赖分析**: 分析模块间的依赖关系
- **性能分析**: 分析加载和执行性能
- **质量分析**: 分析代码质量和安全性

## Webpack Bundle Analyzer

### 基础配置
```javascript
// webpack.config.js
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'server', // server, static, json, disabled
      analyzerHost: '127.0.0.1',
      analyzerPort: 8888,
      reportFilename: 'bundle-report.html',
      defaultSizes: 'parsed', // parsed, gzip, brotli
      openAnalyzer: true,
      generateStatsFile: true,
      statsFilename: 'bundle-stats.json',
      statsOptions: null,
      excludeAssets: null,
      logLevel: 'info'
    })
  ]
};
```

### 高级配置
```javascript
// 高级配置示例
new BundleAnalyzerPlugin({
  // 分析器模式
  analyzerMode: 'static',
  
  // 输出配置
  reportFilename: path.resolve(__dirname, 'reports/bundle-report.html'),
  statsFilename: path.resolve(__dirname, 'reports/bundle-stats.json'),
  
  // 过滤配置
  excludeAssets: [/node_modules/],
  
  // 大小单位
  defaultSizes: 'gzip',
  
  // 自定义选项
  statsOptions: {
    source: false,
    modules: true,
    chunks: true,
    chunkModules: true
  }
})
```

### 命令行使用
```bash
# 基本使用
npx webpack-bundle-analyzer dist/bundle.js

# 指定输出文件
npx webpack-bundle-analyzer dist/bundle.js -r reports/bundle-report.html

# 静态模式
npx webpack-bundle-analyzer dist/bundle.js -m static

# JSON模式
npx webpack-bundle-analyzer dist/bundle.js -m json -o bundle-stats.json

# 指定端口
npx webpack-bundle-analyzer dist/bundle.js -p 9999
```

## Rollup Bundle Analysis

### Rollup Plugin Visualizer
```javascript
// rollup.config.js
import { visualizer } from 'rollup-plugin-visualizer';

export default {
  plugins: [
    visualizer({
      filename: 'bundle-analysis.html',
      open: true,
      gzipSize: true,
      brotliSize: true,
      template: 'treemap' // treemap, sunburst, network, raw-data
    })
  ]
};
```

### Rollup Analysis Options
```javascript
// 分析配置
visualizer({
  // 输出文件
  filename: 'analysis/bundle-analysis.html',
  
  // 自动打开浏览器
  open: true,
  
  // 大小计算
  gzipSize: true,
  brotliSize: true,
  
  // 可视化模板
  template: 'sunburst',
  
  // 项目标题
  title: 'Bundle Analysis Report',
  
  // 项目根目录
  projectRoot: process.cwd(),
  
  // 颜色主题
  colorScheme: {
    primary: '#ff6b6b',
    secondary: '#4ecdc4',
    tertiary: '#45b7d1'
  }
})
```

## Vite Bundle Analysis

### Vite Bundle Analyzer
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ]
});
```

### Vite Built-in Analysis
```javascript
// vite.config.js
export default defineConfig({
  build: {
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    
    // 构建报告
    reportCompressedSize: true,
    
    // chunk 大小警告限制
    chunkSizeWarningLimit: 1000,
    
    // Rollup 配置
    rollupOptions: {
      output: {
        // 手动分包
        manualChunks: {
          vendor: ['vue', 'vue-router'],
          utils: ['lodash', 'axios']
        }
      }
    }
  }
});
```

## 代码分析技术

### 依赖图分析
```javascript
// 依赖图分析器
class DependencyAnalyzer {
  constructor(bundleStats) {
    this.stats = bundleStats;
    this.modules = this.extractModules();
    this.dependencies = this.buildDependencyGraph();
  }
  
  extractModules() {
    const modules = [];
    
    function traverseModules(module, path = []) {
      modules.push({
        id: module.id,
        name: module.name,
        size: module.size,
        path: [...path, module.name],
        dependencies: module.dependencies || []
      });
      
      if (module.modules) {
        for (const child of module.modules) {
          traverseModules(child, [...path, module.name]);
        }
      }
    }
    
    for (const chunk of this.stats.chunks) {
      traverseModules(chunk);
    }
    
    return modules;
  }
  
  buildDependencyGraph() {
    const graph = new Map();
    
    for (const module of this.modules) {
      graph.set(module.id, {
        ...module,
        dependents: [],
        depth: this.calculateDepth(module)
      });
    }
    
    // 建立反向依赖
    for (const module of this.modules) {
      for (const dep of module.dependencies) {
        if (graph.has(dep)) {
          graph.get(dep).dependents.push(module.id);
        }
      }
    }
    
    return graph;
  }
  
  calculateDepth(module) {
    let maxDepth = 0;
    
    function visit(moduleId, visited = new Set()) {
      if (visited.has(moduleId)) return 0;
      visited.add(moduleId);
      
      const current = this.modules.find(m => m.id === moduleId);
      if (!current) return 0;
      
      let depth = 0;
      for (const dep of current.dependencies) {
        depth = Math.max(depth, visit(dep, visited));
      }
      
      return depth + 1;
    }
    
    return visit(module.id);
  }
  
  findCircularDependencies() {
    const visited = new Set();
    const recursionStack = new Set();
    const cycles = [];
    
    function dfs(moduleId, path = []) {
      if (recursionStack.has(moduleId)) {
        const cycleStart = path.indexOf(moduleId);
        cycles.push(path.slice(cycleStart));
        return;
      }
      
      if (visited.has(moduleId)) return;
      
      visited.add(moduleId);
      recursionStack.add(moduleId);
      
      const module = this.modules.find(m => m.id === moduleId);
      if (module) {
        for (const dep of module.dependencies) {
          dfs(dep, [...path, moduleId]);
        }
      }
      
      recursionStack.delete(moduleId);
    }
    
    for (const module of this.modules) {
      dfs(module.id);
    }
    
    return cycles;
  }
}
```

### 大小分析
```javascript
// 大小分析器
class SizeAnalyzer {
  constructor(bundleStats) {
    this.stats = bundleStats;
  }
  
  analyzeByType() {
    const analysis = {
      javascript: 0,
      css: 0,
      images: 0,
      fonts: 0,
      other: 0
    };
    
    function analyzeAssets(assets) {
      for (const asset of assets) {
        if (asset.name.endsWith('.js')) {
          analysis.javascript += asset.size;
        } else if (asset.name.endsWith('.css')) {
          analysis.css += asset.size;
        } else if (/\.(png|jpg|jpeg|gif|svg)$/i.test(asset.name)) {
          analysis.images += asset.size;
        } else if (/\.(woff|woff2|ttf|eot)$/i.test(asset.name)) {
          analysis.fonts += asset.size;
        } else {
          analysis.other += asset.size;
        }
      }
    }
    
    for (const chunk of this.stats.chunks) {
      if (chunk.assets) {
        analyzeAssets(chunk.assets);
      }
    }
    
    return analysis;
  }
  
  analyzeByModule() {
    const modules = [];
    
    for (const chunk of this.stats.chunks) {
      for (const module of chunk.modules || []) {
        modules.push({
          name: module.name,
          size: module.size,
          gzipSize: module.gzipSize || 0,
          brotliSize: module.brotliSize || 0
        });
      }
    }
    
    return modules.sort((a, b) => b.size - a.size);
  }
  
  getDuplicateModules() {
    const moduleMap = new Map();
    const duplicates = [];
    
    for (const chunk of this.stats.chunks) {
      for (const module of chunk.modules || []) {
        if (moduleMap.has(module.name)) {
          moduleMap.get(module.name).push({
            chunk: chunk.id,
            size: module.size
          });
        } else {
          moduleMap.set(module.name, [{
            chunk: chunk.id,
            size: module.size
          }]);
        }
      }
    }
    
    for (const [name, occurrences] of moduleMap) {
      if (occurrences.length > 1) {
        duplicates.push({
          name,
          occurrences,
          totalSize: occurrences.reduce((sum, occ) => sum + occ.size, 0)
        });
      }
    }
    
    return duplicates;
  }
}
```

## 性能优化技术

### Tree Shaking
```javascript
// Tree Shaking 配置
module.exports = {
  mode: 'production', // 启用生产模式
  optimization: {
    usedExports: true, // 标记未使用的导出
    sideEffects: false, // 无副作用的模块
    minimize: true // 启用压缩
  },
  resolve: {
    // 优先使用 ES 模块
    mainFields: ['browser', 'module', 'main'],
    // 解析扩展名
    extensions: ['.mjs', '.js', '.json']
  }
};

// package.json 配置
{
  "sideEffects": [
    "*.css",
    "*.scss",
    "./src/style/index.js"
  ]
}
```

### 代码分割
```javascript
// 动态导入
const loadModule = () => import('./heavy-module.js');

// 路由级别分割
const routes = [
  {
    path: '/dashboard',
    component: () => import('./views/Dashboard.vue')
  },
  {
    path: '/profile',
    component: () => import('./views/Profile.vue')
  }
];

// 组件级别分割
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));

// Webpack 分割配置
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      minSize: 20000,
      maxSize: 244000,
      minChunks: 1,
      maxAsyncRequests: 30,
      maxInitialRequests: 30,
      automaticNameDelimiter: '~',
      cacheGroups: {
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          priority: -10
        },
        default: {
          minChunks: 2,
          priority: -20,
          reuseExistingChunk: true
        }
      }
    }
  }
};
```

### 缓存优化
```javascript
// 长期缓存配置
module.exports = {
  output: {
    filename: '[name].[contenthash].js',
    chunkFilename: '[name].[contenthash].chunk.js'
  },
  optimization: {
    runtimeChunk: 'single',
    moduleIds: 'deterministic',
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        }
      }
    }
  }
};
```

## 监控和度量

### 构建监控
```javascript
// 构建监控器
class BuildMonitor {
  constructor() {
    this.metrics = {
      buildTime: 0,
      bundleSize: 0,
      chunkCount: 0,
      moduleCount: 0
    };
  }
  
  startBuild() {
    this.startTime = Date.now();
  }
  
  endBuild(stats) {
    this.metrics.buildTime = Date.now() - this.startTime;
    this.metrics.bundleSize = this.calculateTotalSize(stats);
    this.metrics.chunkCount = stats.chunks.length;
    this.metrics.moduleCount = this.countModules(stats);
    
    this.reportMetrics();
  }
  
  calculateTotalSize(stats) {
    let totalSize = 0;
    
    for (const chunk of stats.chunks) {
      for (const asset of chunk.assets || []) {
        totalSize += asset.size;
      }
    }
    
    return totalSize;
  }
  
  countModules(stats) {
    let count = 0;
    
    for (const chunk of stats.chunks) {
      count += chunk.modules ? chunk.modules.length : 0;
    }
    
    return count;
  }
  
  reportMetrics() {
    console.log('Build Metrics:');
    console.log(`Build Time: ${this.metrics.buildTime}ms`);
    console.log(`Bundle Size: ${this.formatSize(this.metrics.bundleSize)}`);
    console.log(`Chunk Count: ${this.metrics.chunkCount}`);
    console.log(`Module Count: ${this.metrics.moduleCount}`);
    
    // 检查性能阈值
    this.checkThresholds();
  }
  
  checkThresholds() {
    const thresholds = {
      buildTime: 30000, // 30秒
      bundleSize: 1024 * 1024, // 1MB
      chunkCount: 50
    };
    
    if (this.metrics.buildTime > thresholds.buildTime) {
      console.warn(`Build time exceeded threshold: ${this.metrics.buildTime}ms`);
    }
    
    if (this.metrics.bundleSize > thresholds.bundleSize) {
      console.warn(`Bundle size exceeded threshold: ${this.formatSize(this.metrics.bundleSize)}`);
    }
    
    if (this.metrics.chunkCount > thresholds.chunkCount) {
      console.warn(`Too many chunks: ${this.metrics.chunkCount}`);
    }
  }
  
  formatSize(bytes) {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(2)} ${units[unitIndex]}`;
  }
}
```

### 性能基准测试
```javascript
// 性能基准测试
class PerformanceBenchmark {
  constructor() {
    this.benchmarks = new Map();
  }
  
  async runBenchmark(name, testFn) {
    const start = performance.now();
    await testFn();
    const end = performance.now();
    
    const duration = end - start;
    this.recordBenchmark(name, duration);
    
    return duration;
  }
  
  recordBenchmark(name, duration) {
    if (!this.benchmarks.has(name)) {
      this.benchmarks.set(name, []);
    }
    
    this.benchmarks.get(name).push({
      duration,
      timestamp: Date.now()
    });
  }
  
  getBenchmarkStats(name) {
    const records = this.benchmarks.get(name) || [];
    
    if (records.length === 0) {
      return null;
    }
    
    const durations = records.map(r => r.duration);
    const avg = durations.reduce((sum, d) => sum + d, 0) / durations.length;
    const min = Math.min(...durations);
    const max = Math.max(...durations);
    
    return {
      count: records.length,
      average: avg,
      min,
      max,
      latest: durations[durations.length - 1]
    };
  }
  
  compareBenchmarks(name, threshold) {
    const stats = this.getBenchmarkStats(name);
    
    if (!stats) {
      return { passed: false, reason: 'No benchmark data' };
    }
    
    if (stats.average > threshold) {
      return {
        passed: false,
        reason: `Average ${stats.average}ms exceeds threshold ${threshold}ms`
      };
    }
    
    return { passed: true, stats };
  }
}
```

## 实际应用案例

### React应用优化
```javascript
// React应用打包优化
const path = require('path');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = {
  mode: 'production',
  entry: {
    app: './src/index.js',
    vendor: ['react', 'react-dom']
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    chunkFilename: '[name].[contenthash].chunk.js',
    publicPath: '/'
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: 'react',
          chunks: 'all'
        },
        router: {
          test: /[\\/]node_modules[\\/]react-router[\\/]/,
          name: 'router',
          chunks: 'all'
        },
        utils: {
          test: /[\\/]node_modules[\\/](lodash|axios|moment)[\\/]/,
          name: 'utils',
          chunks: 'all'
        }
      }
    }
  },
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      reportFilename: 'bundle-report.html',
      openAnalyzer: false
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
};
```

### Vue应用优化
```javascript
// Vue应用打包优化
const path = require('path');

module.exports = {
  configureWebpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vue: {
            test: /[\\/]node_modules[\\/](vue|vue-router|vuex)[\\/]/,
            name: 'vue',
            chunks: 'all'
          },
          element: {
            test: /[\\/]node_modules[\\/]element-ui[\\/]/,
            name: 'element',
            chunks: 'all'
          }
        }
      }
    },
    plugins: [
      new BundleAnalyzerPlugin({
        analyzerMode: 'server',
        openAnalyzer: true
      })
    ]
  },
  chainWebpack: config => {
    // 生产环境配置
    if (process.env.NODE_ENV === 'production') {
      config.optimization.minimize(true);
      
      // 移除 console.log
      config.optimization.minimizer('terser').tap(options => {
        options[0].terserOptions.compress.drop_console = true;
        return options;
      });
    }
  }
};
```

## 最佳实践

### 分析策略
1. **定期分析**: 每次构建后自动生成分析报告
2. **对比分析**: 比较不同版本间的变化
3. **阈值监控**: 设置性能阈值，超出时告警
4. **团队共享**: 将分析报告分享给团队成员

### 优化策略
1. **代码分割**: 按功能模块分割代码
2. **Tree Shaking**: 移除未使用的代码
3. **依赖优化**: 优化第三方库的使用
4. **缓存策略**: 利用浏览器缓存机制

### 监控策略
1. **构建监控**: 监控构建时间和大小
2. **性能监控**: 监控运行时性能
3. **质量监控**: 监控代码质量指标
4. **趋势分析**: 分析性能变化趋势

## 相关资源

### 官方文档
- [Webpack Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)
- [Rollup Plugin Visualizer](https://github.com/btd/rollup-plugin-visualizer)
- [Vite Bundle Analysis](https://vitejs.dev/guide/build.html#build-analysis)

### 工具和库
- [webpack-bundle-analyzer](https://www.npmjs.com/package/webpack-bundle-analyzer)
- [rollup-plugin-visualizer](https://www.npmjs.com/package/rollup-plugin-visualizer)
- [source-map-explorer](https://www.npmjs.com/package/source-map-explorer)
- [bundlephobia](https://bundlephobia.com/)

### 学习资源
- [Webpack Performance](https://webpack.js.org/guides/build-performance/)
- [Rollup Configuration](https://rollupjs.org/guide/en/)
- [Vite Build Optimization](https://vitejs.dev/guide/build.html#build-optimizations)
- [JavaScript Bundle Size Optimization](https://web.dev/bundle-size/)
