# 响应式设计技术参考

## 概述

响应式设计是一种Web设计方法，旨在使网站在各种设备和屏幕尺寸上提供最佳的浏览体验。本文档详细介绍了响应式设计的核心技术、最佳实践、工具使用和实际应用案例。

## 核心概念

### 响应式设计基础
- **移动优先**: 从移动端开始设计，逐步增强到桌面端
- **渐进增强**: 确保基础功能在所有设备上可用
- **弹性布局**: 使用相对单位和弹性布局系统
- **媒体查询**: 根据设备特性应用不同样式

### 设计原则
- **内容优先**: 保持内容在不同设备上的可访问性
- **性能优先**: 优化加载速度和运行时性能
- **用户体验**: 专注于用户交互和可用性
- **可访问性**: 确保所有用户都能使用网站

## CSS 基础

### 相对单位
```css
/* rem - 相对于根元素字体大小 */
.container {
  font-size: 1rem; /* 16px (默认) */
  padding: 2rem;   /* 32px */
  margin: 1.5rem;  /* 24px */
}

/* em - 相对于父元素字体大小 */
.text-small {
  font-size: 0.875em; /* 父元素字体大小的 87.5% */
}

/* 百分比 - 相对于父元素 */
.sidebar {
  width: 25%;
  margin-left: 5%;
}

/* 视口单位 */
.hero {
  height: 100vh;        /* 视口高度 */
  font-size: 4vw;       /* 视口宽度的 4% */
  padding: 2vh 1vw;     /* 混合使用 */
}

/* calc() 计算 */
.responsive-padding {
  padding: calc(1rem + 2vw);
  margin: calc(5% - 20px);
}
```

### 弹性布局
```css
/* Flexbox 响应式布局 */
.flex-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.flex-item {
  flex: 1 1 300px;      /* 增长 收缩 基础宽度 */
  min-width: 250px;
}

/* Grid 响应式布局 */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 2rem;
}

/* 复杂网格布局 */
.complex-grid {
  display: grid;
  grid-template-areas: 
    "header header header"
    "sidebar main main"
    "footer footer footer";
  grid-template-columns: 250px 1fr 200px;
  grid-template-rows: auto 1fr auto;
  gap: 1rem;
}

@media (max-width: 768px) {
  .complex-grid {
    grid-template-areas: 
      "header"
      "main"
      "sidebar"
      "footer";
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto auto;
  }
}
```

## 媒体查询

### 基础媒体查询
```css
/* 移动优先方法 */
/* 基础样式 (移动端) */
.container {
  padding: 1rem;
  font-size: 16px;
}

/* 平板设备 */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
    font-size: 18px;
  }
}

/* 桌面设备 */
@media (min-width: 1024px) {
  .container {
    padding: 3rem;
    font-size: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }
}

/* 大屏幕设备 */
@media (min-width: 1440px) {
  .container {
    max-width: 1400px;
  }
}
```

### 高级媒体查询
```css
/* 范围查询 */
@media (min-width: 768px) and (max-width: 1024px) {
  /* 仅适用于平板设备 */
}

/* 高度查询 */
@media (min-height: 800px) {
  .sidebar {
    position: fixed;
    height: 100vh;
  }
}

/* 方向查询 */
@media (orientation: portrait) {
  .landscape-content {
    display: none;
  }
}

@media (orientation: landscape) {
  .portrait-content {
    display: none;
  }
}

/* 分辨率查询 */
@media (-webkit-min-device-pixel-ratio: 2),
       (min-resolution: 192dpi) {
  .logo {
    background-image: url('logo@2x.png');
  }
}

/* 设备特性查询 */
@media (hover: hover) and (pointer: fine) {
  .button:hover {
    transform: translateY(-2px);
  }
}

@media (pointer: coarse) {
  .button {
    min-height: 44px;
    min-width: 44px;
  }
}
```

### 环境媒体查询
```css
/* 深色模式 */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-color: #1a1a1a;
    --text-color: #ffffff;
    --primary-color: #4a9eff;
  }
  
  body {
    background-color: var(--bg-color);
    color: var(--text-color);
  }
}

/* 减少动画 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 高对比度 */
@media (prefers-contrast: high) {
  .button {
    border: 2px solid currentColor;
  }
}

/* 强制颜色模式 */
@media (forced-colors: active) {
  .button {
    border: 2px solid ButtonText;
    background-color: ButtonFace;
    color: ButtonText;
  }
}
```

## 响应式图片

### srcset 和 sizes
```html
<!-- 基础响应式图片 -->
<img 
  src="image-800w.jpg"
  srcset="image-400w.jpg 400w,
          image-800w.jpg 800w,
          image-1200w.jpg 1200w,
          image-1600w.jpg 1600w"
  sizes="(max-width: 600px) 100vw,
         (max-width: 1200px) 50vw,
         33vw"
  alt="描述文字"
  loading="lazy"
>

<!-- 艺术指导 -->
<picture>
  <source media="(max-width: 600px)" srcset="image-mobile.jpg">
  <source media="(max-width: 1200px)" srcset="image-tablet.jpg">
  <source srcset="image-desktop.jpg">
  <img src="image-fallback.jpg" alt="描述文字">
</picture>

<!-- 格式选择 -->
<picture>
  <source srcset="image.webp" type="image/webp">
  <source srcset="image.avif" type="image/avif">
  <img src="image.jpg" alt="描述文字">
</picture>
```

### CSS 响应式图片
```css
/* 背景图片响应式 */
.hero-banner {
  background-image: url('hero-mobile.jpg');
  background-size: cover;
  background-position: center;
  min-height: 300px;
}

@media (min-width: 768px) {
  .hero-banner {
    background-image: url('hero-tablet.jpg');
    min-height: 400px;
  }
}

@media (min-width: 1024px) {
  .hero-banner {
    background-image: url('hero-desktop.jpg');
    min-height: 500px;
  }
}

/* 图标响应式 */
.icon {
  width: 16px;
  height: 16px;
  background-image: url('icon.svg');
}

@media (min-resolution: 2dppx) {
  .icon {
    background-image: url('icon@2x.svg');
    width: 32px;
    height: 32px;
  }
}
```

## 现代CSS技术

### CSS Grid 高级用法
```css
/* 自动适应网格 */
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

/* 容器查询 */
@container (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 1rem;
  }
}

/* 子网格 */
.parent-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.child-grid {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: span 3;
}
```

### CSS 自定义属性
```css
:root {
  --primary-color: #007bff;
  --font-size-base: 16px;
  --spacing-unit: 1rem;
  --breakpoint-mobile: 768px;
  --breakpoint-tablet: 1024px;
}

/* 响应式变量 */
@media (min-width: 768px) {
  :root {
    --font-size-base: 18px;
    --spacing-unit: 1.25rem;
  }
}

@media (min-width: 1024px) {
  :root {
    --font-size-base: 20px;
    --spacing-unit: 1.5rem;
  }
}

/* 使用变量 */
.component {
  font-size: var(--font-size-base);
  padding: var(--spacing-unit);
  color: var(--primary-color);
}
```

### 容器查询
```css
/* 定义容器 */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* 容器查询 */
@container card (min-width: 300px) {
  .card {
    display: flex;
    flex-direction: row;
  }
  
  .card-image {
    width: 120px;
    height: 120px;
  }
}

@container card (min-width: 500px) {
  .card {
    flex-direction: column;
  }
  
  .card-image {
    width: 100%;
    height: 200px;
  }
}
```

## JavaScript 响应式技术

### 窗口大小检测
```javascript
// 防抖窗口大小检测
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 窗口大小监听
const handleResize = debounce(() => {
  const width = window.innerWidth;
  const height = window.innerHeight;
  
  // 更新布局
  if (width < 768) {
    document.body.classList.add('mobile');
    document.body.classList.remove('tablet', 'desktop');
  } else if (width < 1024) {
    document.body.classList.add('tablet');
    document.body.classList.remove('mobile', 'desktop');
  } else {
    document.body.classList.add('desktop');
    document.body.classList.remove('mobile', 'tablet');
  }
  
  // 触发自定义事件
  window.dispatchEvent(new CustomEvent('responsive-change', {
    detail: { width, height }
  }));
}, 250);

window.addEventListener('resize', handleResize);
handleResize(); // 初始调用
```

### 媒体查询API
```javascript
// 使用 MatchMedia API
const mobileQuery = window.matchMedia('(max-width: 767px)');
const tabletQuery = window.matchMedia('(min-width: 768px) and (max-width: 1023px)');
const desktopQuery = window.matchMedia('(min-width: 1024px)');

function handleMediaChange(query) {
  if (query.matches) {
    console.log('媒体查询匹配:', query.media);
    // 执行相应的逻辑
  }
}

// 添加监听器
mobileQuery.addListener(handleMediaChange);
tabletQuery.addListener(handleMediaChange);
desktopQuery.addListener(handleMediaChange);

// 检查当前状态
if (mobileQuery.matches) {
  console.log('移动设备');
}

// 现代浏览器支持 addEventListener
if (mobileQuery.addEventListener) {
  mobileQuery.addEventListener('change', handleMediaChange);
}
```

### 响应式组件
```javascript
class ResponsiveComponent {
  constructor(element) {
    this.element = element;
    this.breakpoints = {
      mobile: 767,
      tablet: 1023,
      desktop: 1024
    };
    this.currentBreakpoint = this.getCurrentBreakpoint();
    
    this.init();
  }
  
  init() {
    this.setupEventListeners();
    this.updateLayout();
  }
  
  getCurrentBreakpoint() {
    const width = window.innerWidth;
    
    if (width <= this.breakpoints.mobile) {
      return 'mobile';
    } else if (width <= this.breakpoints.tablet) {
      return 'tablet';
    } else {
      return 'desktop';
    }
  }
  
  setupEventListeners() {
    window.addEventListener('resize', debounce(() => {
      const newBreakpoint = this.getCurrentBreakpoint();
      
      if (newBreakpoint !== this.currentBreakpoint) {
        this.currentBreakpoint = newBreakpoint;
        this.updateLayout();
        
        this.element.dispatchEvent(new CustomEvent('breakpoint-change', {
          detail: { breakpoint: newBreakpoint }
        }));
      }
    }, 250));
  }
  
  updateLayout() {
    // 移除所有断点类
    Object.keys(this.breakpoints).forEach(bp => {
      this.element.classList.remove(bp);
    });
    
    // 添加当前断点类
    this.element.classList.add(this.currentBreakpoint);
    
    // 执行断点特定的逻辑
    switch (this.currentBreakpoint) {
      case 'mobile':
        this.setupMobileLayout();
        break;
      case 'tablet':
        this.setupTabletLayout();
        break;
      case 'desktop':
        this.setupDesktopLayout();
        break;
    }
  }
  
  setupMobileLayout() {
    // 移动端布局逻辑
    console.log('设置移动端布局');
  }
  
  setupTabletLayout() {
    // 平板端布局逻辑
    console.log('设置平板端布局');
  }
  
  setupDesktopLayout() {
    // 桌面端布局逻辑
    console.log('设置桌面端布局');
  }
}

// 使用示例
const responsiveElement = new ResponsiveComponent(document.body);
```

## 框架集成

### React 响应式
```jsx
import React, { useState, useEffect } from 'react';

// 自定义 Hook
function useBreakpoint() {
  const [breakpoint, setBreakpoint] = useState('mobile');
  
  useEffect(() => {
    const getBreakpoint = () => {
      const width = window.innerWidth;
      if (width < 768) return 'mobile';
      if (width < 1024) return 'tablet';
      return 'desktop';
    };
    
    const handleResize = () => {
      setBreakpoint(getBreakpoint());
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return breakpoint;
}

// 响应式组件
function ResponsiveLayout({ children }) {
  const breakpoint = useBreakpoint();
  
  return (
    <div className={`layout ${breakpoint}`}>
      {breakpoint === 'mobile' && (
        <MobileLayout>{children}</MobileLayout>
      )}
      {breakpoint === 'tablet' && (
        <TabletLayout>{children}</TabletLayout>
      )}
      {breakpoint === 'desktop' && (
        <DesktopLayout>{children}</DesktopLayout>
      )}
    </div>
  );
}

// 使用媒体查询 Hook
function useMediaQuery(query) {
  const [matches, setMatches] = useState(false);
  
  useEffect(() => {
    const media = window.matchMedia(query);
    
    if (media.matches !== matches) {
      setMatches(media.matches);
    }
    
    const listener = () => setMatches(media.matches);
    media.addListener(listener);
    
    return () => media.removeListener(listener);
  }, [matches, query]);
  
  return matches;
}

// 使用示例
function MyComponent() {
  const isMobile = useMediaQuery('(max-width: 767px)');
  const isDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  
  return (
    <div className={isMobile ? 'mobile' : 'desktop'}>
      <h1>{isMobile ? '移动端' : '桌面端'}</h1>
      <p>{isDarkMode ? '深色模式' : '浅色模式'}</p>
    </div>
  );
}
```

### Vue 响应式
```vue
<template>
  <div :class="['layout', breakpoint]">
    <component :is="currentLayout" />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import MobileLayout from './MobileLayout.vue';
import TabletLayout from './TabletLayout.vue';
import DesktopLayout from './DesktopLayout.vue';

export default {
  components: {
    MobileLayout,
    TabletLayout,
    DesktopLayout
  },
  
  setup() {
    const breakpoint = ref('mobile');
    let resizeObserver = null;
    
    const getBreakpoint = () => {
      const width = window.innerWidth;
      if (width < 768) return 'mobile';
      if (width < 1024) return 'tablet';
      return 'desktop';
    };
    
    const handleResize = () => {
      breakpoint.value = getBreakpoint();
    };
    
    onMounted(() => {
      handleResize();
      window.addEventListener('resize', handleResize);
    });
    
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize);
    });
    
    const currentLayout = computed(() => {
      switch (breakpoint.value) {
        case 'mobile': return 'MobileLayout';
        case 'tablet': return 'TabletLayout';
        case 'desktop': return 'DesktopLayout';
        default: return 'MobileLayout';
      }
    });
    
    return {
      breakpoint,
      currentLayout
    };
  }
};
</script>
```

## 性能优化

### CSS 优化
```css
/* 关键 CSS 内联 */
<style>
  /* 首屏关键样式 */
  .hero {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .hero-title {
    font-size: 2.5rem;
    color: white;
    text-align: center;
  }
</style>

/* 非关键 CSS 异步加载 */
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="styles.css"></noscript>

/* CSS 代码分割 */
/* mobile.css - 移动端样式 */
@media (max-width: 767px) {
  .navigation {
    position: fixed;
    bottom: 0;
    width: 100%;
  }
}

/* tablet.css - 平板样式 */
@media (min-width: 768px) and (max-width: 1023px) {
  .navigation {
    position: relative;
    top: 0;
  }
}

/* desktop.css - 桌面样式 */
@media (min-width: 1024px) {
  .navigation {
    position: sticky;
    top: 0;
  }
}
```

### JavaScript 优化
```javascript
// 懒加载组件
const loadComponent = async (componentName) => {
  const module = await import(`./components/${componentName}.js`);
  return module.default;
};

// 条件加载
const loadResponsiveComponent = async () => {
  const width = window.innerWidth;
  
  if (width < 768) {
    return await loadComponent('MobileComponent');
  } else if (width < 1024) {
    return await loadComponent('TabletComponent');
  } else {
    return await loadComponent('DesktopComponent');
  }
};

// 图片懒加载
const lazyLoadImages = () => {
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.srcset = img.dataset.srcset;
        img.classList.remove('lazy');
        imageObserver.unobserve(img);
      }
    });
  });
  
  document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
  });
};

// 防抖和节流
const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};
```

## 测试策略

### 视觉回归测试
```javascript
// 使用 Puppeteer 进行视觉测试
const puppeteer = require('puppeteer');

async function testResponsiveLayout(url) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  const viewports = [
    { width: 375, height: 667, name: 'mobile' },
    { width: 768, height: 1024, name: 'tablet' },
    { width: 1200, height: 800, name: 'desktop' }
  ];
  
  for (const viewport of viewports) {
    await page.setViewport(viewport);
    await page.goto(url);
    await page.waitForTimeout(1000); // 等待加载完成
    
    const screenshot = await page.screenshot({
      fullPage: true,
      path: `screenshots/${viewport.name}.png`
    });
    
    console.log(`截图完成: ${viewport.name}`);
  }
  
  await browser.close();
}

// 组件测试
describe('ResponsiveComponent', () => {
  test('should render mobile layout on small screens', () => {
    // 模拟小屏幕
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });
    
    // 触发 resize 事件
    window.dispatchEvent(new Event('resize'));
    
    // 断言
    expect(screen.getByTestId('mobile-layout')).toBeInTheDocument();
  });
  
  test('should render desktop layout on large screens', () => {
    // 模拟大屏幕
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1200,
    });
    
    // 触发 resize 事件
    window.dispatchEvent(new Event('resize'));
    
    // 断言
    expect(screen.getByTestId('desktop-layout')).toBeInTheDocument();
  });
});
```

### 性能测试
```javascript
// Core Web Vitals 测试
const measurePerformance = async () => {
  const metrics = {
    FCP: 0, // First Contentful Paint
    LCP: 0, // Largest Contentful Paint
    FID: 0, // First Input Delay
    CLS: 0, // Cumulative Layout Shift
  };
  
  // FCP
  new PerformanceObserver((entryList) => {
    for (const entry of entryList.getEntries()) {
      if (entry.name === 'first-contentful-paint') {
        metrics.FCP = entry.startTime;
      }
    }
  }).observe({ entryTypes: ['paint'] });
  
  // LCP
  new PerformanceObserver((entryList) => {
    for (const entry of entryList.getEntries()) {
      metrics.LCP = entry.startTime;
    }
  }).observe({ entryTypes: ['largest-contentful-paint'] });
  
  // FID
  new PerformanceObserver((entryList) => {
    for (const entry of entryList.getEntries()) {
      metrics.FID = entry.processingStart - entry.startTime;
    }
  }).observe({ entryTypes: ['first-input'] });
  
  // CLS
  let clsScore = 0;
  new PerformanceObserver((entryList) => {
    for (const entry of entryList.getEntries()) {
      if (!entry.hadRecentInput) {
        clsScore += entry.value;
      }
    }
    metrics.CLS = clsScore;
  }).observe({ entryTypes: ['layout-shift'] });
  
  return metrics;
};

// 网络性能测试
const testNetworkPerformance = async () => {
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  
  if (connection) {
    console.log('网络信息:', {
      effectiveType: connection.effectiveType,
      downlink: connection.downlink,
      rtt: connection.rtt,
      saveData: connection.saveData
    });
  }
  
  // 测试资源加载时间
  const resources = performance.getEntriesByType('resource');
  const imageResources = resources.filter(r => r.initiatorType === 'img');
  const cssResources = resources.filter(r => r.initiatorType === 'link');
  const jsResources = resources.filter(r => r.initiatorType === 'script');
  
  console.log('资源加载统计:', {
    images: imageResources.length,
    css: cssResources.length,
    js: jsResources.length,
    totalLoadTime: performance.timing.loadEventEnd - performance.timing.navigationStart
  });
};
```

## 工具和资源

### 开发工具
- **浏览器开发者工具**: 设备模拟、网络节流、性能分析
- **Responsive Design Checker**: 多设备同时预览
- **BrowserStack**: 真实设备测试
- **Lighthouse**: 性能和可访问性审计

### CSS 框架
- **Tailwind CSS**: 实用优先的 CSS 框架
- **Bootstrap**: 响应式组件库
- **Foundation**: 专业响应式框架
- **Bulma**: 现代 CSS 框架

### JavaScript 库
- **MatchMedia.js**: 媒体查询 Polyfill
- **Enquire.js**: 响应式 JavaScript 库
- **Responsive.js**: 轻量级响应式工具
- **Breakpoint.js**: 断点管理库

## 最佳实践

### 设计原则
1. **移动优先**: 从移动端开始设计，确保核心功能可用
2. **渐进增强**: 逐步增加功能和样式，不破坏基础体验
3. **性能优先**: 优化加载速度和运行时性能
4. **用户体验**: 专注于用户交互和可用性

### 代码规范
1. **语义化 HTML**: 使用正确的 HTML5 语义标签
2. **模块化 CSS**: 采用组件化的 CSS 架构
3. **响应式图片**: 使用适当的图片优化技术
4. **可访问性**: 遵循 WCAG 2.1 标准

### 测试策略
1. **多设备测试**: 在真实设备和模拟器上测试
2. **视觉回归**: 建立自动化视觉测试
3. **性能监控**: 持续监控 Core Web Vitals
4. **用户测试**: 收集真实用户反馈

## 相关资源

### 官方文档
- [MDN Web Docs - Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [W3C Media Queries](https://www.w3.org/TR/mediaqueries-4/)
- [CSS Grid Layout](https://www.w3.org/TR/css-grid-1/)
- [CSS Flexible Box Layout](https://www.w3.org/TR/css-flexbox-1/)

### 学习资源
- [A List Apart - Responsive Web Design](https://alistapart.com/article/responsive-web-design/)
- [Smashing Magazine - Responsive Design](https://www.smashingmagazine.com/category/responsive-design/)
- [CSS-Tricks - Responsive Design](https://css-tricks.com/responsive-design/)
- [Web.dev - Responsive Design](https://web.dev/responsive-web-design-basics/)

### 工具和框架
- [Tailwind CSS](https://tailwindcss.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Foundation](https://get.foundation/)
- [Can I Use](https://caniuse.com/)

### 社区资源
- [Responsive Design Newsletter](https://responsivedesign.is/)
- [Mobile Web Best Practices](https://web.dev/mobile-web-best-practices/)
- [Web Performance Working Group](https://www.w3.org/webperf/)
- [CSS Working Group](https://www.w3.org/Style/CSS/)
