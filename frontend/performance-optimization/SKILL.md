---
name: 前端性能优化
description: "当优化前端性能时，分析页面加载速度，识别性能瓶颈，实施优化策略。监控性能指标，优化资源加载，和用户体验提升。"
license: MIT
---

# 前端性能优化技能

## 概述
前端性能优化是提升用户体验的关键。不当的性能优化会导致页面加载缓慢、交互延迟、用户流失。需要系统性的性能分析和优化方法。

**核心原则**: 好的性能优化应该显著提升加载速度、减少资源消耗、改善用户体验。坏的性能优化会过度复杂化、收效甚微、增加维护成本。

## 何时使用

**始终:**
- 页面加载缓慢时
- 用户交互延迟时
- 资源加载过多时
- 移动端体验差时
- SEO排名下降时
- 用户反馈卡顿时

**触发短语:**
- "前端性能优化"
- "页面加载优化"
- "性能瓶颈分析"
- "资源加载优化"
- "用户体验提升"
- "性能监控分析"

## 性能优化功能

### 加载优化
- 资源压缩合并
- 懒加载预加载
- CDN加速分发
- 缓存策略优化
- 关键渲染路径

### 运行时优化
- JavaScript优化
- CSS渲染优化
- DOM操作优化
- 内存管理
- 事件处理优化

### 网络优化
- HTTP请求优化
- 协议升级
- 连接复用
- 数据压缩
- 资源优先级

### 用户体验优化
- 首屏渲染优化
- 交互响应优化
- 动画性能优化
- 滚动性能优化
- 触摸响应优化

## 常见性能问题

### 加载速度慢
```
问题:
页面首次加载时间过长，用户等待时间久

错误示例:
- 资源未压缩
- 阻塞渲染的CSS/JS
- 图片体积过大
- 缺少缓存策略

解决方案:
1. 压缩静态资源
2. 优化关键渲染路径
3. 图片懒加载和压缩
4. 实施合理缓存策略
```

### 运行时卡顿
```
问题:
页面交互时出现卡顿，响应不流畅

错误示例:
- 频繁的DOM操作
- 大量同步JavaScript
- 内存泄漏
- 强制重排重绘

解决方案:
1. 减少DOM操作
2. 使用异步处理
3. 优化内存使用
4. 避免强制布局
```

### 内存占用高
```
问题:
页面内存占用过高，可能导致崩溃

错误示例:
- 事件监听器未清理
- 大量对象未释放
- 定时器未清除
- 闭包引用过多

解决方案:
1. 及时清理事件监听
2. 释放不需要的对象
3. 清除定时器
4. 优化闭包使用
```

### 网络请求多
```
问题:
页面发起过多网络请求，影响加载速度

错误示例:
- 资源未合并
- 缺少预加载
- 重复请求
- 未使用CDN

解决方案:
1. 合并相关资源
2. 使用预加载技术
3. 避免重复请求
4. 利用CDN加速
```

## 代码实现示例

### 性能监控器
```python
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class MetricType(Enum):
    """指标类型"""
    PAGE_LOAD = "page_load"
    FIRST_PAINT = "first_paint"
    FIRST_CONTENTFUL_PAINT = "first_contentful_paint"
    LARGEST_CONTENTFUL_PAINT = "largest_contentful_paint"
    TIME_TO_INTERACTIVE = "time_to_interactive"
    CUMULATIVE_LAYOUT_SHIFT = "cumulative_layout_shift"
    FIRST_INPUT_DELAY = "first_input_delay"

@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: float
    threshold: float
    is_good: bool

@dataclass
class PerformanceReport:
    """性能报告"""
    url: str
    timestamp: float
    metrics: List[PerformanceMetric]
    score: float
    recommendations: List[str]

class PerformanceMonitor:
    def __init__(self):
        self.metrics_history: List[PerformanceMetric] = []
        self.thresholds = {
            MetricType.PAGE_LOAD: 3000,  # 3秒
            MetricType.FIRST_PAINT: 1000,  # 1秒
            MetricType.FIRST_CONTENTFUL_PAINT: 1800,  # 1.8秒
            MetricType.LARGEST_CONTENTFUL_PAINT: 2500,  # 2.5秒
            MetricType.TIME_TO_INTERACTIVE: 3800,  # 3.8秒
            MetricType.CUMULATIVE_LAYOUT_SHIFT: 0.1,  # 0.1
            MetricType.FIRST_INPUT_DELAY: 100  # 100ms
        }
    
    def measure_page_load(self, url: str) -> Dict[str, Any]:
        """测量页面加载性能"""
        start_time = time.time()
        
        # 模拟页面加载测量
        metrics = self._simulate_page_metrics(start_time)
        
        # 计算性能评分
        score = self._calculate_performance_score(metrics)
        
        # 生成建议
        recommendations = self._generate_recommendations(metrics)
        
        report = PerformanceReport(
            url=url,
            timestamp=start_time,
            metrics=metrics,
            score=score,
            recommendations=recommendations
        )
        
        return asdict(report)
    
    def _simulate_page_metrics(self, start_time: float) -> List[PerformanceMetric]:
        """模拟页面指标测量"""
        metrics = []
        
        # 模拟各种性能指标
        metrics.append(PerformanceMetric(
            name=MetricType.PAGE_LOAD.value,
            value=2500.0,  # 模拟值
            unit="ms",
            timestamp=start_time,
            threshold=self.thresholds[MetricType.PAGE_LOAD],
            is_good=True
        ))
        
        metrics.append(PerformanceMetric(
            name=MetricType.FIRST_PAINT.value,
            value=800.0,
            unit="ms",
            timestamp=start_time + 0.8,
            threshold=self.thresholds[MetricType.FIRST_PAINT],
            is_good=True
        ))
        
        metrics.append(PerformanceMetric(
            name=MetricType.FIRST_CONTENTFUL_PAINT.value,
            value=1500.0,
            unit="ms",
            timestamp=start_time + 1.5,
            threshold=self.thresholds[MetricType.FIRST_CONTENTFUL_PAINT],
            is_good=True
        ))
        
        metrics.append(PerformanceMetric(
            name=MetricType.LARGEST_CONTENTFUL_PAINT.value,
            value=2200.0,
            unit="ms",
            timestamp=start_time + 2.2,
            threshold=self.thresholds[MetricType.LARGEST_CONTENTFUL_PAINT],
            is_good=True
        ))
        
        metrics.append(PerformanceMetric(
            name=MetricType.TIME_TO_INTERACTIVE.value,
            value=3500.0,
            unit="ms",
            timestamp=start_time + 3.5,
            threshold=self.thresholds[MetricType.TIME_TO_INTERACTIVE],
            is_good=True
        ))
        
        metrics.append(PerformanceMetric(
            name=MetricType.CUMULATIVE_LAYOUT_SHIFT.value,
            value=0.05,
            unit="",
            timestamp=start_time + 2.0,
            threshold=self.thresholds[MetricType.CUMULATIVE_LAYOUT_SHIFT],
            is_good=True
        ))
        
        metrics.append(PerformanceMetric(
            name=MetricType.FIRST_INPUT_DELAY.value,
            value=80.0,
            unit="ms",
            timestamp=start_time + 3.0,
            threshold=self.thresholds[MetricType.FIRST_INPUT_DELAY],
            is_good=True
        ))
        
        return metrics
    
    def _calculate_performance_score(self, metrics: List[PerformanceMetric]) -> float:
        """计算性能评分"""
        total_score = 0
        weight_sum = 0
        
        weights = {
            MetricType.PAGE_LOAD: 0.15,
            MetricType.FIRST_PAINT: 0.10,
            MetricType.FIRST_CONTENTFUL_PAINT: 0.15,
            MetricType.LARGEST_CONTENTFUL_PAINT: 0.25,
            MetricType.TIME_TO_INTERACTIVE: 0.20,
            MetricType.CUMULATIVE_LAYOUT_SHIFT: 0.10,
            MetricType.FIRST_INPUT_DELAY: 0.05
        }
        
        for metric in metrics:
            metric_type = MetricType(metric.name)
            weight = weights.get(metric_type, 0.1)
            
            # 计算单个指标得分
            if metric.is_good:
                score = 100
            else:
                # 根据超出阈值的程度计算得分
                ratio = metric.value / metric.threshold
                score = max(0, 100 - (ratio - 1) * 50)
            
            total_score += score * weight
            weight_sum += weight
        
        return total_score / weight_sum if weight_sum > 0 else 0
    
    def _generate_recommendations(self, metrics: List[PerformanceMetric]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for metric in metrics:
            if not metric.is_good:
                if metric.name == MetricType.PAGE_LOAD.value:
                    recommendations.append("页面加载时间过长，建议优化资源加载和缓存策略")
                elif metric.name == MetricType.FIRST_PAINT.value:
                    recommendations.append("首次绘制时间过长，建议优化关键渲染路径")
                elif metric.name == MetricType.FIRST_CONTENTFUL_PAINT.value:
                    recommendations.append("首次内容绘制时间过长，建议减少阻塞资源")
                elif metric.name == MetricType.LARGEST_CONTENTFUL_PAINT.value:
                    recommendations.append("最大内容绘制时间过长，建议优化图片和字体加载")
                elif metric.name == MetricType.TIME_TO_INTERACTIVE.value:
                    recommendations.append("可交互时间过长，建议优化JavaScript执行")
                elif metric.name == MetricType.CUMULATIVE_LAYOUT_SHIFT.value:
                    recommendations.append("累积布局偏移过大，建议为图片和广告预留空间")
                elif metric.name == MetricType.FIRST_INPUT_DELAY.value:
                    recommendations.append("首次输入延迟过长，建议减少主线程阻塞")
        
        return recommendations
    
    def analyze_resource_loading(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析资源加载"""
        analysis = {
            'total_resources': len(resources),
            'total_size': 0,
            'resource_types': {},
            'optimization_suggestions': []
        }
        
        for resource in resources:
            size = resource.get('size', 0)
            resource_type = resource.get('type', 'unknown')
            
            analysis['total_size'] += size
            
            if resource_type not in analysis['resource_types']:
                analysis['resource_types'][resource_type] = {
                    'count': 0,
                    'total_size': 0
                }
            
            analysis['resource_types'][resource_type]['count'] += 1
            analysis['resource_types'][resource_type]['total_size'] += size
        
        # 生成优化建议
        if analysis['total_size'] > 5 * 1024 * 1024:  # 5MB
            analysis['optimization_suggestions'].append("页面总资源过大，建议压缩图片和代码")
        
        js_size = analysis['resource_types'].get('javascript', {}).get('total_size', 0)
        if js_size > 1024 * 1024:  # 1MB
            analysis['optimization_suggestions'].append("JavaScript文件过大，建议代码分割和懒加载")
        
        css_size = analysis['resource_types'].get('css', {}).get('total_size', 0)
        if css_size > 500 * 1024:  # 500KB
            analysis['optimization_suggestions'].append("CSS文件过大，建议移除未使用样式")
        
        img_count = analysis['resource_types'].get('image', {}).get('count', 0)
        if img_count > 50:
            analysis['optimization_suggestions'].append("图片数量过多，建议使用图片懒加载")
        
        return analysis

# 资源优化器
class ResourceOptimizer:
    def __init__(self):
        self.optimization_strategies = {}
    
    def optimize_images(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """优化图片资源"""
        optimized_images = []
        
        for image in images:
            optimized = image.copy()
            
            # 模拟图片优化
            original_size = image.get('size', 0)
            
            # 压缩图片
            if original_size > 100 * 1024:  # 100KB
                optimized['size'] = int(original_size * 0.7)  # 压缩30%
                optimized['optimizations'] = image.get('optimizations', [])
                optimized['optimizations'].append('compressed')
            
            # 转换格式
            if image.get('format') == 'png' and original_size > 50 * 1024:
                optimized['format'] = 'webp'
                optimized['size'] = int(optimized['size'] * 0.8)  # 再压缩20%
                optimized['optimizations'].append('format_converted')
            
            # 添加懒加载
            if image.get('lazy_load', False) == False:
                optimized['lazy_load'] = True
                optimized['optimizations'].append('lazy_load')
            
            optimized_images.append(optimized)
        
        return optimized_images
    
    def optimize_javascript(self, scripts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """优化JavaScript资源"""
        optimized_scripts = []
        
        for script in scripts:
            optimized = script.copy()
            
            # 压缩代码
            original_size = script.get('size', 0)
            if original_size > 10 * 1024:  # 10KB
                optimized['size'] = int(original_size * 0.6)  # 压缩40%
                optimized['optimizations'] = script.get('optimizations', [])
                optimized['optimizations'].append('minified')
            
            # 添加异步加载
            if script.get('async', False) == False and script.get('defer', False) == False:
                # 根据脚本类型决定加载方式
                if script.get('critical', False):
                    optimized['defer'] = True
                else:
                    optimized['async'] = True
                optimized['optimizations'].append('async_loaded')
            
            optimized_scripts.append(optimized)
        
        return optimized_scripts
    
    def optimize_css(self, styles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """优化CSS资源"""
        optimized_styles = []
        
        for style in styles:
            optimized = style.copy()
            
            # 压缩CSS
            original_size = style.get('size', 0)
            if original_size > 5 * 1024:  # 5KB
                optimized['size'] = int(original_size * 0.7)  # 压缩30%
                optimized['optimizations'] = style.get('optimizations', [])
                optimized['optimizations'].append('minified')
            
            # 关键CSS内联
            if style.get('critical', False):
                optimized['inline'] = True
                optimized['optimizations'].append('inlined')
            
            optimized_styles.append(optimized)
        
        return optimized_styles

# 缓存策略管理器
class CacheStrategyManager:
    def __init__(self):
        self.cache_rules = {}
    
    def generate_cache_headers(self, resource_type: str, resource: Dict[str, Any]) -> Dict[str, str]:
        """生成缓存头"""
        headers = {}
        
        if resource_type == 'image':
            if resource.get('versioned', False):
                # 版本化图片可以长期缓存
                headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            else:
                headers['Cache-Control'] = 'public, max-age=86400'
        elif resource_type == 'javascript':
            if resource.get('versioned', False):
                headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            else:
                headers['Cache-Control'] = 'public, max-age=3600'
        elif resource_type == 'css':
            if resource.get('versioned', False):
                headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            else:
                headers['Cache-Control'] = 'public, max-age=3600'
        else:
            # 默认缓存策略
            headers['Cache-Control'] = 'public, max-age=3600'
        
        return headers
    
    def generate_service_worker(self, resources: List[Dict[str, Any]]) -> str:
        """生成Service Worker代码"""
        js_parts = []
        
        js_parts.append("""
// Service Worker for performance optimization
const CACHE_NAME = 'performance-cache-v1';
const urlsToCache = [
""")
        
        # 添加需要缓存的资源
        for resource in resources:
            if resource.get('cacheable', True):
                url = resource.get('url', '')
                if url:
                    js_parts.append(f"  '{url}',")
        
        js_parts.append("""
];

// Install event - cache resources
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve from cache
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache hit - return response
                if (response) {
                    return response;
                }
                
                // Network request
                return fetch(event.request).then(
                    response => {
                        // Check if valid response
                        if(!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone response
                        const responseToCache = response.clone();
                        
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    }
                );
            })
    );
});
        """)
        
        return '\n'.join(js_parts)

# 使用示例
def main():
    print("=== 性能监控分析 ===")
    
    # 创建性能监控器
    monitor = PerformanceMonitor()
    
    # 测量页面性能
    performance_report = monitor.measure_page_load("https://example.com")
    
    print("性能报告:")
    print(f"URL: {performance_report['url']}")
    print(f"评分: {performance_report['score']:.1f}")
    print(f"时间戳: {performance_report['timestamp']}")
    
    print("\n性能指标:")
    for metric in performance_report['metrics']:
        status = "✓" if metric['is_good'] else "✗"
        print(f"- {metric['name']}: {metric['value']}{metric['unit']} {status}")
        if not metric['is_good']:
            print(f"  阈值: {metric['threshold']}{metric['unit']}")
    
    if performance_report['recommendations']:
        print("\n优化建议:")
        for rec in performance_report['recommendations']:
            print(f"- {rec}")
    
    print("\n=== 资源加载分析 ===")
    
    # 模拟资源数据
    resources = [
        {'url': '/app.js', 'type': 'javascript', 'size': 1500000, 'critical': False},
        {'url': '/style.css', 'type': 'css', 'size': 800000, 'critical': True},
        {'url': '/image1.jpg', 'type': 'image', 'size': 200000, 'format': 'jpeg'},
        {'url': '/image2.png', 'type': 'image', 'size': 300000, 'format': 'png'},
        {'url': '/image3.jpg', 'type': 'image', 'size': 150000, 'format': 'jpeg'},
    ]
    
    resource_analysis = monitor.analyze_resource_loading(resources)
    
    print("资源分析结果:")
    print(f"总资源数: {resource_analysis['total_resources']}")
    print(f"总大小: {resource_analysis['total_size'] / 1024:.1f} KB")
    
    print("\n按类型统计:")
    for resource_type, stats in resource_analysis['resource_types'].items():
        print(f"- {resource_type}: {stats['count']} 个, {stats['total_size'] / 1024:.1f} KB")
    
    if resource_analysis['optimization_suggestions']:
        print("\n优化建议:")
        for suggestion in resource_analysis['optimization_suggestions']:
            print(f"- {suggestion}")
    
    print("\n=== 资源优化 ===")
    
    optimizer = ResourceOptimizer()
    
    # 优化图片
    images = [r for r in resources if r['type'] == 'image']
    optimized_images = optimizer.optimize_images(images)
    
    print("图片优化结果:")
    for original, optimized in zip(images, optimized_images):
        size_reduction = (original['size'] - optimized['size']) / original['size'] * 100
        print(f"- {original['url']}: {size_reduction:.1f}% 大小减少")
        if 'optimizations' in optimized:
            print(f"  优化措施: {', '.join(optimized['optimizations'])}")
    
    # 优化JavaScript
    scripts = [r for r in resources if r['type'] == 'javascript']
    optimized_scripts = optimizer.optimize_javascript(scripts)
    
    print("\nJavaScript优化结果:")
    for original, optimized in zip(scripts, optimized_scripts):
        size_reduction = (original['size'] - optimized['size']) / original['size'] * 100
        print(f"- {original['url']}: {size_reduction:.1f}% 大小减少")
        if 'optimizations' in optimized:
            print(f"  优化措施: {', '.join(optimized['optimizations'])}")
    
    print("\n=== 缓存策略 ===")
    
    cache_manager = CacheStrategyManager()
    
    print("缓存头设置:")
    for resource in resources:
        headers = cache_manager.generate_cache_headers(resource['type'], resource)
        print(f"- {resource['url']}:")
        for header, value in headers.items():
            print(f"  {header}: {value}")
    
    # 生成Service Worker
    service_worker = cache_manager.generate_service_worker(resources)
    
    print("\n生成的Service Worker代码:")
    print(service_worker)

if __name__ == '__main__':
    main()
```

### 前端优化工具
```python
from typing import Dict, Any, List, Optional
import re

class HTMLOptimizer:
    def __init__(self):
        self.optimizations = []
    
    def optimize_html(self, html_content: str) -> Dict[str, Any]:
        """优化HTML内容"""
        optimized = html_content
        optimizations = []
        
        # 移除注释
        original_size = len(optimized)
        optimized = re.sub(r'<!--.*?-->', '', optimized, flags=re.DOTALL)
        if len(optimized) < original_size:
            optimizations.append("移除HTML注释")
        
        # 压缩空白
        optimized = re.sub(r'\s+', ' ', optimized)
        optimized = re.sub(r'>\s+<', '><', optimized)
        optimizations.append("压缩空白字符")
        
        # 优化图片
        optimized, img_optimizations = self._optimize_images(optimized)
        optimizations.extend(img_optimizations)
        
        # 添加关键CSS内联
        optimized, css_optimizations = self._inline_critical_css(optimized)
        optimizations.extend(css_optimizations)
        
        # 延迟加载非关键资源
        optimized, lazy_optimizations = self._add_lazy_loading(optimized)
        optimizations.extend(lazy_optimizations)
        
        return {
            'optimized_html': optimized,
            'optimizations': optimizations,
            'size_reduction': original_size - len(optimized),
            'compression_ratio': (original_size - len(optimized)) / original_size * 100
        }
    
    def _optimize_images(self, html: str) -> tuple:
        """优化HTML中的图片"""
        optimizations = []
        
        # 为图片添加loading="lazy"
        img_pattern = r'<img([^>]*?)>'
        def add_lazy_loading(match):
            img_tag = match.group(1)
            if 'loading=' not in img_tag:
                optimizations.append("添加图片懒加载")
                return f'<img{img_tag} loading="lazy">'
            return match.group(0)
        
        html = re.sub(img_pattern, add_lazy_loading, html)
        
        return html, optimizations
    
    def _inline_critical_css(self, html: str) -> tuple:
        """内联关键CSS"""
        optimizations = []
        
        # 简化实现：移除阻塞CSS并添加预加载
        css_pattern = r'<link[^>]*rel=["\']stylesheet["\'][^>]*>'
        
        def optimize_css_link(match):
            css_tag = match.group(0)
            if 'media=' not in css_tag:  # 非关键CSS
                optimizations.append("非关键CSS异步加载")
                # 转换为预加载
                href_match = re.search(r'href=["\']([^"\']+)["\']', css_tag)
                if href_match:
                    href = href_match.group(1)
                    return f'<link rel="preload" href="{href}" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">'
            return css_tag
        
        html = re.sub(css_pattern, optimize_css_link, html)
        
        return html, optimizations
    
    def _add_lazy_loading(self, html: str) -> tuple:
        """添加懒加载"""
        optimizations = []
        
        # 为脚本添加defer/async
        script_pattern = r'<script([^>]*?)>'
        def optimize_script(match):
            script_attrs = match.group(1)
            if 'src=' in script_attrs and 'async=' not in script_attrs and 'defer=' not in script_attrs:
                optimizations.append("脚本异步加载")
                return f'<script{script_attrs} defer>'
            return match.group(0)
        
        html = re.sub(script_pattern, optimize_script, html)
        
        return html, optimizations

class BundleAnalyzer:
    def __init__(self):
        self.bundles = []
    
    def analyze_bundle(self, bundle_path: str, bundle_content: str) -> Dict[str, Any]:
        """分析打包文件"""
        analysis = {
            'size': len(bundle_content),
            'modules': [],
            'dependencies': [],
            'optimization_suggestions': []
        }
        
        # 简化的模块分析
        lines = bundle_content.split('\n')
        
        # 查找模块导入
        import_pattern = r'import.*from\s+[\'"]([^\'"]+)[\'"]'
        for line_num, line in enumerate(lines, 1):
            match = re.search(import_pattern, line)
            if match:
                module = match.group(1)
                analysis['dependencies'].append({
                    'module': module,
                    'line': line_num
                })
        
        # 分析模块大小（简化）
        if analysis['size'] > 1024 * 1024:  # 1MB
            analysis['optimization_suggestions'].append("打包文件过大，建议代码分割")
        
        if len(analysis['dependencies']) > 50:
            analysis['optimization_suggestions'].append("依赖模块过多，建议优化导入")
        
        # 检查重复依赖
        module_counts = {}
        for dep in analysis['dependencies']:
            module = dep['module']
            module_counts[module] = module_counts.get(module, 0) + 1
        
        duplicates = [module for module, count in module_counts.items() if count > 1]
        if duplicates:
            analysis['optimization_suggestions'].append(f"发现重复依赖: {', '.join(duplicates)}")
        
        return analysis

class PerformanceAuditor:
    def __init__(self):
        self.audits = []
    
    def audit_performance(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """性能审计"""
        audit_results = {
            'score': 0,
            'issues': [],
            'recommendations': [],
            'categories': {}
        }
        
        # 审计各个性能类别
        audit_results['categories']['loading'] = self._audit_loading_performance(page_data)
        audit_results['categories']['interactivity'] = self._audit_interactivity(page_data)
        audit_results['categories']['visual_stability'] = self._audit_visual_stability(page_data)
        audit_results['categories']['accessibility'] = self._audit_accessibility(page_data)
        audit_results['categories']['best_practices'] = self._audit_best_practices(page_data)
        
        # 计算总分
        category_scores = []
        for category, result in audit_results['categories'].items():
            category_scores.append(result['score'])
            audit_results['issues'].extend(result['issues'])
            audit_results['recommendations'].extend(result['recommendations'])
        
        audit_results['score'] = sum(category_scores) / len(category_scores) if category_scores else 0
        
        return audit_results
    
    def _audit_loading_performance(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """审计加载性能"""
        result = {'score': 0, 'issues': [], 'recommendations': []}
        
        # 检查关键指标
        metrics = page_data.get('metrics', {})
        
        fcp = metrics.get('first_contentful_paint', 0)
        if fcp > 1800:
            result['issues'].append(f"首次内容绘制时间过长: {fcp}ms")
            result['recommendations'].append("优化关键渲染路径，减少阻塞资源")
            result['score'] -= 20
        else:
            result['score'] += 20
        
        lcp = metrics.get('largest_contentful_paint', 0)
        if lcp > 2500:
            result['issues'].append(f"最大内容绘制时间过长: {lcp}ms")
            result['recommendations'].append("优化图片和字体加载")
            result['score'] -= 25
        else:
            result['score'] += 25
        
        return result
    
    def _audit_interactivity(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """审计交互性"""
        result = {'score': 0, 'issues': [], 'recommendations': []}
        
        metrics = page_data.get('metrics', {})
        
        tti = metrics.get('time_to_interactive', 0)
        if tti > 3800:
            result['issues'].append(f"可交互时间过长: {tti}ms")
            result['recommendations'].append("优化JavaScript执行，减少主线程阻塞")
            result['score'] -= 30
        else:
            result['score'] += 30
        
        fid = metrics.get('first_input_delay', 0)
        if fid > 100:
            result['issues'].append(f"首次输入延迟过长: {fid}ms")
            result['recommendations'].append("减少长任务，优化代码执行")
            result['score'] -= 20
        else:
            result['score'] += 20
        
        return result
    
    def _audit_visual_stability(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """审计视觉稳定性"""
        result = {'score': 0, 'issues': [], 'recommendations': []}
        
        metrics = page_data.get('metrics', {})
        
        cls = metrics.get('cumulative_layout_shift', 0)
        if cls > 0.1:
            result['issues'].append(f"累积布局偏移过大: {cls}")
            result['recommendations'].append("为图片和广告预留空间，避免布局偏移")
            result['score'] -= 25
        else:
            result['score'] += 25
        
        return result
    
    def _audit_accessibility(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """审计可访问性"""
        result = {'score': 0, 'issues': [], 'recommendations': []}
        
        # 简化的可访问性检查
        html_content = page_data.get('html', '')
        
        # 检查alt属性
        img_tags = re.findall(r'<img[^>]*>', html_content)
        missing_alt = 0
        for img in img_tags:
            if 'alt=' not in img:
                missing_alt += 1
        
        if missing_alt > 0:
            result['issues'].append(f"发现{missing_alt}个图片缺少alt属性")
            result['recommendations'].append("为所有图片添加描述性的alt属性")
            result['score'] -= 15
        else:
            result['score'] += 15
        
        return result
    
    def _audit_best_practices(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """审计最佳实践"""
        result = {'score': 0, 'issues': [], 'recommendations': []}
        
        # 检查HTTPS使用
        url = page_data.get('url', '')
        if not url.startswith('https://'):
            result['issues'].append("网站未使用HTTPS")
            result['recommendations'].append("启用HTTPS以提高安全性")
            result['score'] -= 20
        else:
            result['score'] += 20
        
        # 检查响应式设计
        html_content = page_data.get('html', '')
        if 'viewport' not in html_content:
            result['issues'].append("缺少viewport meta标签")
            result['recommendations'].append("添加viewport meta标签以支持移动设备")
            result['score'] -= 10
        else:
            result['score'] += 10
        
        return result

# 使用示例
def main():
    print("=== 前端优化工具 ===")
    
    # HTML优化
    html_optimizer = HTMLOptimizer()
    
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Example Page</title>
        <!-- This is a comment -->
        <link rel="stylesheet" href="style.css">
        <script src="app.js"></script>
    </head>
    <body>
        <img src="image.jpg" alt="Example Image">
        <img src="large-image.jpg">
        <div>Content here</div>
    </body>
    </html>
    """
    
    html_result = html_optimizer.optimize_html(sample_html)
    
    print("HTML优化结果:")
    print(f"大小减少: {html_result['size_reduction']} bytes")
    print(f"压缩率: {html_result['compression_ratio']:.1f}%")
    print("优化措施:")
    for opt in html_result['optimizations']:
        print(f"- {opt}")
    
    print("\n=== 打包分析 ===")
    
    bundle_analyzer = BundleAnalyzer()
    
    sample_bundle = """
    import React from 'react';
    import ReactDOM from 'react-dom';
    import axios from 'axios';
    import lodash from 'lodash';
    import React from 'react';  // 重复导入
    import moment from 'moment';
    
    // 大量代码...
    """ * 1000  # 模拟大文件
    
    bundle_result = bundle_analyzer.analyze_bundle("app.js", sample_bundle)
    
    print("打包分析结果:")
    print(f"文件大小: {bundle_result['size']} bytes")
    print(f"依赖数量: {len(bundle_result['dependencies'])}")
    
    if bundle_result['optimization_suggestions']:
        print("优化建议:")
        for suggestion in bundle_result['optimization_suggestions']:
            print(f"- {suggestion}")
    
    print("\n=== 性能审计 ===")
    
    auditor = PerformanceAuditor()
    
    page_data = {
        'url': 'http://example.com',
        'html': sample_html,
        'metrics': {
            'first_contentful_paint': 2000,
            'largest_contentful_paint': 3000,
            'time_to_interactive': 4000,
            'first_input_delay': 150,
            'cumulative_layout_shift': 0.15
        }
    }
    
    audit_result = auditor.audit_performance(page_data)
    
    print("性能审计结果:")
    print(f"总分: {audit_result['score']:.1f}")
    
    if audit_result['issues']:
        print("\n发现的问题:")
        for issue in audit_result['issues']:
            print(f"- {issue}")
    
    if audit_result['recommendations']:
        print("\n改进建议:")
        for rec in audit_result['recommendations']:
            print(f"- {rec}")
    
    print("\n各类别得分:")
    for category, result in audit_result['categories'].items():
        print(f"- {category}: {result['score']}")

if __name__ == '__main__':
    main()
```

## 前端性能优化最佳实践

### 加载优化
1. **资源压缩**: 压缩HTML、CSS、JavaScript和图片
2. **关键路径优化**: 优化关键渲染路径
3. **缓存策略**: 合理设置缓存头和Service Worker
4. **CDN加速**: 使用CDN分发静态资源
5. **预加载预连接**: 使用预加载和预连接技术

### 运行时优化
1. **代码分割**: 按需加载代码模块
2. **懒加载**: 延迟加载非关键资源
3. **虚拟滚动**: 处理大量数据列表
4. **防抖节流**: 优化频繁触发的事件
5. **内存管理**: 及时清理不需要的对象

### 渲染优化
1. **减少重排重绘**: 批量DOM操作
2. **CSS优化**: 避免复杂选择器和昂贵的属性
3. **动画优化**: 使用transform和opacity
4. **字体优化**: 优化字体加载策略
5. **图片优化**: 使用合适的格式和尺寸

### 监控分析
1. **性能指标**: 监控核心Web指标
2. **用户体验**: 收集真实用户数据
3. **错误监控**: 监控JavaScript错误
4. **资源分析**: 分析资源加载情况
5. **持续优化**: 建立优化反馈循环

## 相关技能

- **bundle-analyzer** - 包分析器
- **css-validator** - CSS验证器
- **component-analyzer** - 组件分析器
- **accessibility-audit** - 可访问性审计
