---
name: 包分析器
description: "当优化包大小、性能预算、依赖分析或代码分割规划时，分析JavaScript包并优化加载性能。"
license: MIT
---

# 包分析器技能

## 概述
包大小直接影响页面加载时间。更小的包 = 更快的页面 = 更好的用户体验。

**核心原则**: 包大小直接影响页面加载时间。更小的包 = 更快的页面 = 更好的用户体验。

## 何时使用

**始终:**
- 优化包大小
- 性能预算管理
- 依赖分析
- 代码分割规划
- 构建优化
- 性能监控

**触发短语:**
- "分析包大小"
- "优化JavaScript包"
- "检查依赖"
- "代码分割"
- "包性能分析"
- "构建优化"

## 包分析功能

### 大小分析
- 包大小统计
- 模块大小排序
- 压缩效果分析
- Gzip压缩评估
- Tree shaking效果

### 依赖分析
- 依赖关系图
- 重复依赖检测
- 未使用依赖识别
- 版本冲突分析
- 安全漏洞检查

### 性能优化
- 代码分割建议
- 动态导入优化
- 懒加载策略
- 缓存优化
- 加载性能分析

## 常见包问题

### 包体积过大
```
问题:
JavaScript包体积过大导致加载缓慢

错误示例:
- 未使用的库被包含
- 大型库未按需加载
- 图片资源未优化
- 字体文件重复

解决方案:
1. 使用Tree shaking移除未使用代码
2. 实施代码分割
3. 使用动态导入
4. 优化静态资源
```

### 依赖冲突
```
问题:
不同版本的依赖导致冲突

错误示例:
- React 16和React 18同时存在
- 多个版本的lodash
- 语义版本冲突
- Peer dependency未满足

解决方案:
1. 统一依赖版本
2. 使用resolutions字段
3. 清理重复依赖
4. 更新兼容版本
```

### 构建效率低
```
问题:
构建时间过长，开发体验差

错误示例:
- 每次构建都重新编译所有内容
- 缺少缓存机制
- Source map生成过慢
- 热更新延迟高

解决方案:
1. 启用构建缓存
2. 优化Babel配置
3. 使用更快的工具
4. 分离开发生产配置
```

## 代码实现示例

### 包分析器
```javascript
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const gzip = require('gzip-size');
const brotliSize = require('brotli-size');

class BundleAnalyzer {
    constructor(options = {}) {
        this.options = {
            outputPath: './dist',
            analyzePath: './analyze',
            ...options
        };
        this.stats = null;
        this.analysis = null;
    }

    async analyze() {
        console.log('开始分析包...');
        
        // 获取构建统计信息
        this.stats = await this.getBuildStats();
        
        // 分析包内容
        this.analysis = await this.performAnalysis();
        
        // 生成报告
        await this.generateReport();
        
        return this.analysis;
    }

    async getBuildStats() {
        try {
            // 尝试读取webpack stats文件
            const statsPath = path.join(this.options.outputPath, 'stats.json');
            if (fs.existsSync(statsPath)) {
                return JSON.parse(fs.readFileSync(statsPath, 'utf8'));
            }
            
            // 如果没有stats文件，生成一个
            return this.generateStats();
        } catch (error) {
            console.error('获取构建统计失败:', error);
            return null;
        }
    }

    generateStats() {
        try {
            // 使用webpack-bundle-analyzer生成stats
            const stats = execSync(
                `npx webpack-bundle-analyzer ${this.options.outputPath}/*.js --mode=json --output=${this.options.analyzePath}/stats.json`,
                { encoding: 'utf8' }
            );
            return JSON.parse(stats);
        } catch (error) {
            console.error('生成统计失败:', error);
            return null;
        }
    }

    async performAnalysis() {
        if (!this.stats) {
            throw new Error('无法获取构建统计信息');
        }

        const analysis = {
            bundles: [],
            totalSize: 0,
            totalGzipSize: 0,
            totalBrotliSize: 0,
            dependencies: new Map(),
            duplicates: [],
            unused: [],
            recommendations: []
        };

        // 分析每个包
        for (const chunk of this.stats.chunks || []) {
            const bundleAnalysis = await this.analyzeBundle(chunk);
            analysis.bundles.push(bundleAnalysis);
            analysis.totalSize += bundleAnalysis.size;
            analysis.totalGzipSize += bundleAnalysis.gzipSize;
            analysis.totalBrotliSize += bundleAnalysis.brotliSize;
        }

        // 分析依赖
        analysis.dependencies = this.analyzeDependencies();
        
        // 查找重复
        analysis.duplicates = this.findDuplicates();
        
        // 查找未使用的代码
        analysis.unused = this.findUnusedCode();
        
        // 生成建议
        analysis.recommendations = this.generateRecommendations(analysis);

        return analysis;
    }

    async analyzeBundle(chunk) {
        const bundlePath = path.join(this.options.outputPath, chunk.names[0]);
        const buffer = fs.readFileSync(bundlePath);
        
        const analysis = {
            name: chunk.names[0],
            size: buffer.length,
            gzipSize: await gzip(buffer),
            brotliSize: await brotliSize(buffer),
            modules: [],
            assets: []
        };

        // 分析模块
        if (chunk.modules) {
            for (const [moduleId, module] of Object.entries(chunk.modules)) {
                analysis.modules.push({
                    id: moduleId,
                    name: module.name,
                    size: module.size || 0,
                    reason: module.reasons || []
                });
            }
        }

        // 分析资源
        if (chunk.assets) {
            for (const asset of chunk.assets) {
                analysis.assets.push({
                    name: asset.name,
                    size: asset.size || 0,
                    type: this.getAssetType(asset.name)
                });
            }
        }

        return analysis;
    }

    analyzeDependencies() {
        const dependencies = new Map();
        
        if (!this.stats.modules) return dependencies;

        for (const module of this.stats.modules) {
            // 提取依赖信息
            const deps = this.extractDependencies(module);
            
            for (const dep of deps) {
                if (dependencies.has(dep.name)) {
                    const existing = dependencies.get(dep.name);
                    existing.count++;
                    existing.totalSize += dep.size;
                    existing.versions.add(dep.version);
                } else {
                    dependencies.set(dep.name, {
                        name: dep.name,
                        version: dep.version,
                        versions: new Set([dep.version]),
                        count: 1,
                        totalSize: dep.size,
                        type: dep.type
                    });
                }
            }
        }

        return dependencies;
    }

    extractDependencies(module) {
        const dependencies = [];
        
        // 从模块路径提取依赖信息
        if (module.name) {
            // 检测node_modules中的依赖
            const nodeModulesMatch = module.name.match(/node_modules\/([^\/]+)/);
            if (nodeModulesMatch) {
                const depName = nodeModulesMatch[1];
                const version = this.extractVersion(module.name);
                
                dependencies.push({
                    name: depName,
                    version: version,
                    size: module.size || 0,
                    type: this.getDependencyType(depName)
                });
            }
        }

        return dependencies;
    }

    extractVersion(modulePath) {
        // 尝试从路径中提取版本号
        const versionMatch = modulePath.match(/@([^\/]+)/);
        return versionMatch ? versionMatch[1] : 'unknown';
    }

    getDependencyType(name) {
        const devDeps = this.getDevDependencies();
        const peerDeps = this.getPeerDependencies();
        
        if (devDeps.has(name)) return 'dev';
        if (peerDeps.has(name)) return 'peer';
        return 'prod';
    }

    getDevDependencies() {
        try {
            const packageJson = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
            return new Set(Object.keys(packageJson.devDependencies || {}));
        } catch {
            return new Set();
        }
    }

    getPeerDependencies() {
        try {
            const packageJson = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
            return new Set(Object.keys(packageJson.peerDependencies || {}));
        } catch {
            return new Set();
        }
    }

    findDuplicates() {
        const duplicates = [];
        const seen = new Map();
        
        for (const [name, dep] of this.analysis.dependencies) {
            if (dep.versions.size > 1) {
                duplicates.push({
                    name: name,
                    versions: Array.from(dep.versions),
                    totalSize: dep.totalSize,
                    impact: this.calculateDuplicateImpact(dep)
                });
            }
        }
        
        return duplicates.sort((a, b) => b.totalSize - a.totalSize);
    }

    calculateDuplicateImpact(dep) {
        // 计算重复依赖的影响
        const versionCount = dep.versions.size;
        const sizeImpact = dep.totalSize * (versionCount - 1) / versionCount;
        return {
            sizeWasted: sizeImpact,
            complexityIncrease: versionCount - 1,
            riskLevel: sizeImpact > 100000 ? 'high' : sizeImpact > 50000 ? 'medium' : 'low'
        };
    }

    findUnusedCode() {
        const unused = [];
        
        if (!this.stats.modules) return unused;

        for (const module of this.stats.modules) {
            // 检查模块是否被使用
            if (this.isModuleUnused(module)) {
                unused.push({
                    name: module.name,
                    size: module.size || 0,
                    type: this.getModuleType(module.name),
                    reason: '未引用的模块'
                });
            }
        }

        return unused.sort((a, b) => b.size - a.size);
    }

    isModuleUnused(module) {
        // 检查模块是否有引用
        return !module.reasons || module.reasons.length === 0;
    }

    getModuleType(moduleName) {
        if (moduleName.includes('.css')) return 'css';
        if (moduleName.includes('.png') || moduleName.includes('.jpg') || moduleName.includes('.svg')) return 'asset';
        if (moduleName.includes('node_modules')) return 'dependency';
        return 'source';
    }

    getAssetType(fileName) {
        const ext = path.extname(fileName);
        switch (ext) {
            case '.js': return 'javascript';
            case '.css': return 'stylesheet';
            case '.png':
            case '.jpg':
            case '.jpeg':
            case '.gif':
            case '.svg': return 'image';
            case '.woff':
            case '.woff2':
            case '.ttf': return 'font';
            default: return 'other';
        }
    }

    generateRecommendations(analysis) {
        const recommendations = [];

        // 大小建议
        if (analysis.totalSize > 1000000) { // 1MB
            recommendations.push({
                type: 'size',
                priority: 'high',
                title: '包体积过大',
                description: `总包大小为${this.formatSize(analysis.totalSize)}，建议优化`,
                actions: [
                    '实施代码分割',
                    '移除未使用的依赖',
                    '使用动态导入',
                    '压缩静态资源'
                ]
            });
        }

        // 重复依赖建议
        if (analysis.duplicates.length > 0) {
            recommendations.push({
                type: 'duplicates',
                priority: 'medium',
                title: '发现重复依赖',
                description: `发现${analysis.duplicates.length}个重复的依赖包`,
                actions: analysis.duplicates.slice(0, 5).map(dup => 
                    `统一${dup.name}的版本到${dup.versions[0]}`
                )
            });
        }

        // 未使用代码建议
        if (analysis.unused.length > 0) {
            const totalUnusedSize = analysis.unused.reduce((sum, item) => sum + item.size, 0);
            recommendations.push({
                type: 'unused',
                priority: 'medium',
                title: '发现未使用代码',
                description: `发现${analysis.unused.length}个未使用模块，总大小${this.formatSize(totalUnusedSize)}`,
                actions: [
                    '移除未使用的导入',
                    '清理dead code',
                    '优化Tree shaking配置'
                ]
            });
        }

        // 性能建议
        const largestBundle = analysis.bundles.reduce((max, bundle) => 
            bundle.size > max.size ? bundle : max, analysis.bundles[0]);
        
        if (largestBundle && largestBundle.size > 500000) { // 500KB
            recommendations.push({
                type: 'performance',
                priority: 'high',
                title: '大包需要分割',
                description: `最大的包${largestBundle.name}大小为${this.formatSize(largestBundle.size)}`,
                actions: [
                    '实施代码分割',
                    '使用懒加载',
                    '优化第三方库导入'
                ]
            });
        }

        return recommendations;
    }

    formatSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async generateReport() {
        const reportPath = path.join(this.options.analyzePath, 'report.html');
        const reportHtml = this.generateHTMLReport();
        
        fs.writeFileSync(reportPath, reportHtml);
        console.log(`报告已生成: ${reportPath}`);
    }

    generateHTMLReport() {
        return `
<!DOCTYPE html>
<html>
<head>
    <title>包分析报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .recommendation { background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .high-priority { border-left: 4px solid #dc3545; }
        .medium-priority { border-left: 4px solid #ffc107; }
        .low-priority { border-left: 4px solid #28a745; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>包分析报告</h1>
    
    <div class="summary">
        <h2>总览</h2>
        <p>总大小: ${this.formatSize(this.analysis.totalSize)}</p>
        <p>Gzip大小: ${this.formatSize(this.analysis.totalGzipSize)}</p>
        <p>Brotli大小: ${this.formatSize(this.analysis.totalBrotliSize)}</p>
        <p>包数量: ${this.analysis.bundles.length}</p>
        <p>依赖数量: ${this.analysis.dependencies.size}</p>
    </div>

    <div class="section">
        <h2>包详情</h2>
        <table>
            <tr>
                <th>名称</th>
                <th>大小</th>
                <th>Gzip</th>
                <th>Brotli</th>
                <th>模块数</th>
            </tr>
            ${this.analysis.bundles.map(bundle => `
                <tr>
                    <td>${bundle.name}</td>
                    <td>${this.formatSize(bundle.size)}</td>
                    <td>${this.formatSize(bundle.gzipSize)}</td>
                    <td>${this.formatSize(bundle.brotliSize)}</td>
                    <td>${bundle.modules.length}</td>
                </tr>
            `).join('')}
        </table>
    </div>

    <div class="section">
        <h2>优化建议</h2>
        ${this.analysis.recommendations.map(rec => `
            <div class="recommendation ${rec.priority}-priority">
                <h3>${rec.title}</h3>
                <p>${rec.description}</p>
                <ul>
                    ${rec.actions.map(action => `<li>${action}</li>`).join('')}
                </ul>
            </div>
        `).join('')}
    </div>
</body>
</html>`;
    }
}

// 使用示例
async function main() {
    const analyzer = new BundleAnalyzer({
        outputPath: './dist',
        analyzePath: './analyze'
    });

    try {
        const analysis = await analyzer.analyze();
        
        console.log('=== 分析完成 ===');
        console.log(`总大小: ${analyzer.formatSize(analysis.totalSize)}`);
        console.log(`依赖数量: ${analysis.dependencies.size}`);
        console.log(`重复依赖: ${analysis.duplicates.length}`);
        console.log(`未使用模块: ${analysis.unused.length}`);
        console.log(`优化建议: ${analysis.recommendations.length}`);
        
    } catch (error) {
        console.error('分析失败:', error);
    }
}

module.exports = BundleAnalyzer;

if (require.main === module) {
    main();
}
```

### 代码分割优化器
```javascript
class CodeSplittingOptimizer {
    constructor(options = {}) {
        this.options = {
            chunkSizeLimit: 250000, // 250KB
            concurrencyLimit: 10,
            ...options
        };
    }

    optimize(webpackConfig) {
        const optimizations = {
            splitChunks: this.generateSplitChunksConfig(),
            runtimeChunk: this.generateRuntimeChunkConfig(),
            dynamicImports: this.generateDynamicImportConfig()
        };

        return this.mergeConfigs(webpackConfig, optimizations);
    }

    generateSplitChunksConfig() {
        return {
            chunks: 'all',
            cacheGroups: {
                // 第三方库
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    priority: 10,
                    name: 'vendors',
                    chunks: 'all',
                },
                // 公共代码
                common: {
                    name: 'common',
                    minChunks: 2,
                    chunks: 'all',
                    priority: 5,
                    reuseExistingChunk: true,
                },
                // 小模块合并
                mini: {
                    name: 'mini',
                    test: (module) => {
                        return module.size && module.size < 10000; // 小于10KB
                    },
                    priority: 0,
                    minChunks: 5,
                    chunks: 'all',
                }
            }
        };
    }

    generateRuntimeChunkConfig() {
        return {
            name: 'runtime',
            chunks: 'single'
        };
    }

    generateDynamicImportConfig() {
        return {
            // 页面级别的懒加载
            pages: this.generatePageChunks(),
            // 组件级别的懒加载
            components: this.generateComponentChunks(),
            // 路由级别的懒加载
            routes: this.generateRouteChunks()
        };
    }

    generatePageChunks() {
        return {
            test: /[\\/]pages[\\/]/,
            name: 'pages/[name]',
            chunks: 'all',
            priority: 20
        };
    }

    generateComponentChunks() {
        return {
            test: /[\\/]components[\\/]/,
            name: 'components/[name]',
            chunks: 'all',
            priority: 15
        };
    }

    generateRouteChunks() {
        return {
            test: /[\\/]routes[\\/]/,
            name: 'routes/[name]',
            chunks: 'all',
            priority: 25
        };
    }

    mergeConfigs(baseConfig, optimizations) {
        return {
            ...baseConfig,
            optimization: {
                ...baseConfig.optimization,
                ...optimizations
            }
        };
    }

    // 分析动态导入模式
    analyzeDynamicImports(sourceCode) {
        const dynamicImports = [];
        
        // 匹配 import() 语法
        const importRegex = /import\s*\(\s*['"`]([^'"`]+)['"`]\s*\)/g;
        let match;
        
        while ((match = importRegex.exec(sourceCode)) !== null) {
            dynamicImports.push({
                path: match[1],
                type: 'dynamic',
                line: this.getLineNumber(sourceCode, match.index)
            });
        }

        // 匹配 require.ensure 语法
        const ensureRegex = /require\.ensure\s*\(\s*\[[^\]]*\]\s*,\s*function/g;
        while ((match = ensureRegex.exec(sourceCode)) !== null) {
            dynamicImports.push({
                path: 'require.ensure',
                type: 'ensure',
                line: this.getLineNumber(sourceCode, match.index)
            });
        }

        return dynamicImports;
    }

    getLineNumber(source, index) {
        const lines = source.substring(0, index).split('\n');
        return lines.length;
    }

    // 生成懒加载建议
    generateLazyLoadingSuggestions(components) {
        const suggestions = [];

        for (const component of components) {
            if (component.size > 50000) { // 大于50KB
                suggestions.push({
                    component: component.name,
                    reason: '组件过大',
                    suggestion: '使用动态导入进行懒加载',
                    example: `const ${component.name} = lazy(() => import('./${component.name}'));`
                });
            }

            if (component.usage < 0.3) { // 使用率低于30%
                suggestions.push({
                    component: component.name,
                    reason: '使用率低',
                    suggestion: '按需加载',
                    example: `const ${component.name} = lazy(() => import('./${component.name}'));`
                });
            }
        }

        return suggestions;
    }
}

// Webpack插件示例
class BundleAnalyzerPlugin {
    constructor(options = {}) {
        this.options = options;
        this.analyzer = new BundleAnalyzer(options);
    }

    apply(compiler) {
        compiler.hooks.done.tapAsync('BundleAnalyzerPlugin', (stats, callback) => {
            this.analyzer.analyze()
                .then(() => callback())
                .catch(err => callback(err));
        });
    }
}

module.exports = {
    BundleAnalyzer,
    CodeSplittingOptimizer,
    BundleAnalyzerPlugin
};
```

## 包优化最佳实践

### 代码分割
1. **路由分割**: 按页面分割代码
2. **组件分割**: 大组件懒加载
3. **第三方库分离**: 独立打包vendor
4. **功能分割**: 按功能模块分割

### 依赖管理
1. **按需引入**: 只使用需要的部分
2. **版本统一**: 避免版本冲突
3. **定期清理**: 移除未使用依赖
4. **安全更新**: 及时更新有漏洞的包

### 构建优化
1. **Tree Shaking**: 移除未使用代码
2. **压缩优化**: 使用最佳压缩算法
3. **缓存策略**: 合理使用缓存
4. **并行构建**: 提高构建速度

## 相关技能

- **webpack-config** - Webpack配置
- **performance-optimization** - 性能优化
- **frontend-architecture** - 前端架构
- **build-tools** - 构建工具
