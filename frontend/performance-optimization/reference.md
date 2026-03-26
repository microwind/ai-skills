# 前端性能优化技术参考

## 概述

前端性能优化是提升Web应用用户体验的核心技术，涵盖加载性能、运行时性能、渲染性能等多个方面。通过系统性的优化策略，可以显著提升应用的响应速度和用户满意度。

## 性能指标

### Core Web Vitals
- **LCP (Largest Contentful Paint)**: 最大内容绘制时间，衡量主要内容的加载速度
- **FID (First Input Delay)**: 首次输入延迟，衡量交互响应速度
- **CLS (Cumulative Layout Shift)**: 累积布局偏移，衡量视觉稳定性

```javascript
// 示例： Web Vitals监控
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

### 其他重要指标
- **FCP (First Contentful Paint)**: 首次内容绘制时间
- **TTI (Time to Interactive)**: 可交互时间
- **TBT (Total Blocking Time)**: 总阻塞时间

## 加载性能优化

### 资源压缩
```javascript
// Webpack配置示例
module.exports = {
  optimization: {
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
            drop_debugger: true
          }
        }
      }),
      new CssMinimizerPlugin()
    ]
  }
};
```

### 代码分割
```javascript
// 路由级别的代码分割
import { lazy, Suspense } from 'react';

const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </Suspense>
  );
}

// 组件级别的代码分割
const HeavyComponent = lazy(() => 
  import('./HeavyComponent').then(module => ({
    default: module.HeavyComponent
  }))
);
```

### 预加载和预取
```html
<!-- 预加载关键资源 -->
<link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/critical.css" as="style">

<!-- 预取未来可能需要的资源 -->
<link rel="prefetch" href="/next-page.js" as="script">
<link rel="prefetch" href="/next-page.css" as="style">

<!-- DNS预解析 -->
<link rel="dns-prefetch" href="//api.example.com">
```

### 图片优化
```javascript
// 响应式图片
<img 
  src="image-800w.jpg"
  srcset="image-400w.jpg 400w, image-800w.jpg 800w, image-1200w.jpg 1200w"
  sizes="(max-width: 400px) 400px, (max-width: 800px) 800px, 1200px"
  alt="Description"
  loading="lazy"
/>

// 现代图片格式
<picture>
  <source srcset="image.webp" type="image/webp">
  <source srcset="image.avif" type="image/avif">
  <img src="image.jpg" alt="Description" loading="lazy">
</picture>
```

## 运行时性能优化

### 虚拟滚动
```javascript
// 虚拟滚动实现示例
import { FixedSizeList as List } from 'react-window';

const Row = ({ index, style }) => (
  <div style={style}>
    Row {index}
  </div>
);

const VirtualizedList = () => (
  <List
    height={600}
    itemCount={10000}
    itemSize={35}
    width={300}
  >
    {Row}
  </List>
);
```

### 防抖和节流
```javascript
// 防抖函数
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

// 节流函数
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// 使用示例
const handleSearch = debounce((query) => {
  searchAPI(query);
}, 300);

const handleScroll = throttle(() => {
  updateScrollPosition();
}, 100);
```

### 内存管理
```javascript
// 避免内存泄漏
class Component {
  constructor() {
    this.handleClick = this.handleClick.bind(this);
    this.addEventListeners();
  }
  
  addEventListeners() {
    window.addEventListener('scroll', this.handleScroll);
    window.addEventListener('resize', this.handleResize);
  }
  
  destroy() {
    // 清理事件监听器
    window.removeEventListener('scroll', this.handleScroll);
    window.removeEventListener('resize', this.handleResize);
    
    // 清理定时器
    if (this.timer) {
      clearInterval(this.timer);
    }
    
    // 清理观察器
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}
```

## 渲染性能优化

### React性能优化
```javascript
// 使用React.memo避免不必要的重渲染
const ExpensiveComponent = React.memo(({ data, onUpdate }) => {
  return (
    <div>
      {data.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}, (prevProps, nextProps) => {
  return prevProps.data.length === nextProps.data.length;
});

// 使用useMemo缓存计算结果
const ExpensiveCalculation = ({ items }) => {
  const expensiveValue = useMemo(() => {
    return items.reduce((sum, item) => sum + item.value, 0);
  }, [items]);
  
  return <div>Total: {expensiveValue}</div>;
};

// 使用useCallback缓存函数
const ParentComponent = () => {
  const [count, setCount] = useState(0);
  
  const handleClick = useCallback(() => {
    setCount(c => c + 1);
  }, []);
  
  return <ChildComponent onClick={handleClick} />;
};
```

### CSS性能优化
```css
/* 避免复杂选择器 */
/* 不推荐 */
.container .item .content .title .text {
  color: red;
}

/* 推荐 */
.item-title {
  color: red;
}

/* 使用transform和opacity进行动画 */
.animated-element {
  transform: translateX(0);
  opacity: 1;
  transition: transform 0.3s ease, opacity 0.3s ease;
  will-change: transform, opacity;
}

.animated-element.active {
  transform: translateX(100px);
  opacity: 0.5;
}
```

### DOM操作优化
```javascript
// 批量DOM操作
function updateMultipleElements(elements, data) {
  const fragment = document.createDocumentFragment();
  
  elements.forEach((element, index) => {
    const clone = element.cloneNode(true);
    clone.textContent = data[index];
    fragment.appendChild(clone);
  });
  
  container.innerHTML = '';
  container.appendChild(fragment);
}

// 使用DocumentFragment
function createList(items) {
  const fragment = document.createDocumentFragment();
  
  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    fragment.appendChild(li);
  });
  
  return fragment;
}
```

## 网络性能优化

### HTTP缓存策略
```javascript
// Service Worker缓存策略
self.addEventListener('fetch', event => {
  if (event.request.destination === 'image') {
    event.respondWith(
      caches.match(event.request).then(response => {
        return response || fetch(event.request).then(response => {
          return caches.open('images').then(cache => {
            cache.put(event.request, response.clone());
            return response;
          });
        });
      })
    );
  }
});

// 缓存优先策略
const cacheFirst = async (request) => {
  const cached = await caches.match(request);
  return cached || fetch(request);
};

// 网络优先策略
const networkFirst = async (request) => {
  try {
    const response = await fetch(request);
    const cache = await caches.open('dynamic');
    cache.put(request, response.clone());
    return response;
  } catch (error) {
    return await caches.match(request);
  }
};
```

### API请求优化
```javascript
// 请求合并
class RequestBatcher {
  constructor(batchSize = 10, delay = 100) {
    this.batchSize = batchSize;
    this.delay = delay;
    this.queue = [];
    this.timer = null;
  }
  
  addRequest(request) {
    return new Promise((resolve, reject) => {
      this.queue.push({ request, resolve, reject });
      
      if (this.queue.length >= this.batchSize) {
        this.flush();
      } else if (!this.timer) {
        this.timer = setTimeout(() => this.flush(), this.delay);
      }
    });
  }
  
  async flush() {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    
    const batch = this.queue.splice(0, this.batchSize);
    if (batch.length === 0) return;
    
    try {
      const responses = await this.executeBatch(batch.map(item => item.request));
      batch.forEach((item, index) => {
        item.resolve(responses[index]);
      });
    } catch (error) {
      batch.forEach(item => item.reject(error));
    }
  }
  
  async executeBatch(requests) {
    // 实现批量请求逻辑
    return Promise.all(requests.map(request => fetch(request)));
  }
}
```

## 性能监控

### 性能API使用
```javascript
// Performance Observer API
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('Performance Entry:', entry);
    
    if (entry.entryType === 'navigation') {
      console.log('Page Load Time:', entry.loadEventEnd - entry.loadEventStart);
    }
    
    if (entry.entryType === 'measure') {
      console.log('Custom Measure:', entry.name, entry.duration);
    }
  }
});

observer.observe({ entryTypes: ['navigation', 'measure', 'paint'] });

// 自定义性能测量
performance.mark('operation-start');
// 执行一些操作
performance.mark('operation-end');
performance.measure('operation-duration', 'operation-start', 'operation-end');
```

### 错误监控
```javascript
// 全局错误处理
window.addEventListener('error', (event) => {
  console.error('Global Error:', {
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    error: event.error
  });
  
  // 发送错误报告到监控服务
  sendErrorReport({
    type: 'javascript',
    message: event.message,
    stack: event.error?.stack,
    url: window.location.href
  });
});

// Promise错误处理
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise Rejection:', event.reason);
  
  sendErrorReport({
    type: 'promise',
    message: event.reason?.message || event.reason,
    stack: event.reason?.stack,
    url: window.location.href
  });
});
```

## 性能测试工具

### Lighthouse配置
```javascript
// 使用Lighthouse进行性能测试
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

async function runLighthouse(url) {
  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });
  const options = {
    logLevel: 'info',
    output: 'json',
    onlyCategories: ['performance'],
    port: chrome.port
  };
  
  const runnerResult = await lighthouse(url, options);
  await chrome.kill();
  
  return runnerResult.lhr;
}

runLighthouse('https://example.com').then(results => {
  console.log('Performance Score:', results.categories.performance.score * 100);
});
```

### 性能基准测试
```javascript
// Benchmark.js示例
import Benchmark from 'benchmark';

const suite = new Benchmark.Suite;

suite
  .add('Array.map', () => {
    [1, 2, 3, 4, 5].map(x => x * 2);
  })
  .add('for loop', () => {
    const result = [];
    for (let i = 1; i <= 5; i++) {
      result.push(i * 2);
    }
  })
  .on('cycle', (event) => {
    console.log(String(event.target));
  })
  .on('complete', function() {
    console.log('Fastest is ' + this.filter('fastest').map('name'));
  })
  .run({ async: true });
```

## 最佳实践

### 性能预算
```javascript
// 性能预算配置
const performanceBudget = {
  // 加载性能预算
  loadTime: 3000, // 3秒
  firstContentfulPaint: 1500, // 1.5秒
  largestContentfulPaint: 2500, // 2.5秒
  
  // 资源大小预算
  totalSize: 1024 * 1024, // 1MB
  imageSize: 512 * 1024, // 512KB
  scriptSize: 256 * 1024, // 256KB
  cssSize: 100 * 1024, // 100KB
  
  // 运行时性能预算
  firstInputDelay: 100, // 100ms
  cumulativeLayoutShift: 0.1
};

// 性能预算检查
function checkPerformanceBudget(metrics) {
  const violations = [];
  
  Object.entries(performanceBudget).forEach(([key, budget]) => {
    if (metrics[key] > budget) {
      violations.push({
        metric: key,
        actual: metrics[key],
        budget: budget,
        exceeded: metrics[key] - budget
      });
    }
  });
  
  return violations;
}
```

### 性能优化检查清单
```markdown
## 加载性能
- [ ] 启用Gzip/Brotli压缩
- [ ] 实现代码分割
- [ ] 优化图片格式和大小
- [ ] 使用CDN加速
- [ ] 实现资源预加载
- [ ] 设置适当的缓存策略

## 运行时性能
- [ ] 实现虚拟滚动
- [ ] 使用防抖和节流
- [ ] 优化事件监听器
- [ ] 避免内存泄漏
- [ ] 使用Web Workers处理重计算

## 渲染性能
- [ ] 优化CSS选择器
- [ ] 使用transform进行动画
- [ ] 避免强制同步布局
- [ ] 实现组件级别的优化
- [ ] 减少DOM操作次数

## 网络性能
- [ ] 减少HTTP请求数量
- [ ] 实现请求合并
- [ ] 使用HTTP/2
- [ ] 优化API响应
- [ ] 实现离线缓存
```

## 相关资源

### 官方文档
- [Web.dev Performance](https://web.dev/performance/)
- [MDN Web Performance](https://developer.mozilla.org/en-US/docs/Web/Performance)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)

### 性能工具
- [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools)
- [WebPageTest](https://www.webpagetest.org/)
- [GTmetrix](https://gtmetrix.com/)

### 学习资源
- [High Performance Browser Networking](https://hpbn.co/)
- [Designing for Performance](https://designingforperformance.com/)
- [Web Performance in Action](https://www.manning.com/books/web-performance-in-action)

### 社区资源
- [Reddit - r/webperf](https://www.reddit.com/r/webperf/)
- [Web Performance Working Group](https://www.w3.org/webperf/)
- [Performance Calendar](https://calendar.perfplanet.com/)
