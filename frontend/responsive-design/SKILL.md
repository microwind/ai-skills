---
name: responsive-design
description: "Use when building mobile-friendly responsive layouts, configuring CSS media queries and breakpoints, debugging cross-device compatibility, or optimizing viewport and fluid grid behavior. 当需要实现响应式设计、媒体查询断点配置、移动端适配、流式布局或跨设备兼容性调试时使用。"
license: MIT
---

# 响应式设计技能

## 实施工作流

1. **审查视口配置** — 确认 `<meta name="viewport" content="width=device-width, initial-scale=1.0">` 存在
2. **定义断点体系** — 移动端 `<768px`、平板 `768-1024px`、桌面 `>1024px`；按内容需要添加自定义断点
3. **采用移动优先编写** — 基础样式面向最小屏幕，使用 `min-width` 媒体查询逐步增强
4. **选择布局方案** — Flexbox 用于一维排列，CSS Grid 用于二维网格，Container Queries 用于组件级响应
5. **处理响应式资源** — 图片使用 `srcset`/`sizes`，背景图按断点切换，视频使用 `max-width:100%`
6. **验证** — 用 DevTools 设备模拟逐断点检查；确认触摸目标 ≥ 44px；测试横竖屏切换

## 响应式设计技能功能

### 布局策略分析
- 流式网格布局（Fluid Grid）
- 弹性盒子布局（Flexbox）
- 网格布局（CSS Grid）
- 响应式容器（Container Queries）
- 多列布局（Multi-column）

### 断点设计管理
- 移动设备断点（< 768px）
- 平板设备断点（768px - 1024px）
- 桌面设备断点（> 1024px）
- 自定义断点策略
- 断点优化建议

### 媒体查询应用
- 媒体类型检测（media-type）
- 媒体特性查询（media-feature）
- 逻辑操作符组合
- 嵌套媒体查询
- 性能优化考虑

## 常见问题与修复

| 问题 | 修复 |
|------|------|
| 移动端布局溢出 | `width: 100%; max-width: 100%; overflow-x: hidden;` 替换固定 px 宽度 |
| 图片超出容器 | `img { max-width: 100%; height: auto; }` |
| 触摸目标过小 | `min-width: 44px; min-height: 44px; padding: 12px;` |
| 移动端加载慢 | `<img srcset="sm.jpg 480w, md.jpg 768w" sizes="(max-width:768px) 100vw, 50vw">` |
| 导航在小屏不可用 | 768px 以下隐藏菜单列表，显示汉堡按钮，切换 `.active` 类展开 |
| 文字在大屏过宽 | `max-width: 65ch;` 限制段落行宽 |

## 代码示例

### 基础响应式布局
```css
/* 基础样式 */
* {
    box-sizing: border-box;
}

.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* 网格系统 */
.row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -10px;
}

.col {
    flex: 1;
    padding: 0 10px;
}

/* 移动优先响应式 */
@media (min-width: 768px) {
    .col-md-6 { flex: 0 0 50%; }
    .col-md-4 { flex: 0 0 33.333%; }
    .col-md-3 { flex: 0 0 25%; }
}

@media (min-width: 1024px) {
    .col-lg-4 { flex: 0 0 33.333%; }
    .col-lg-3 { flex: 0 0 25%; }
    .col-lg-2 { flex: 0 0 16.666%; }
}
```

### 响应式图片处理
```css
/* 响应式图片基础样式 */
img {
    max-width: 100%;
    height: auto;
    display: block;
}

/* 图片容器 */
.image-container {
    position: relative;
    overflow: hidden;
}

/* 响应式背景图片 */
.hero-section {
    background-image: url('image-small.jpg');
    background-size: cover;
    background-position: center;
    height: 300px;
}

@media (min-width: 768px) {
    .hero-section {
        background-image: url('image-medium.jpg');
        height: 400px;
    }
}

@media (min-width: 1024px) {
    .hero-section {
        background-image: url('image-large.jpg');
        height: 500px;
    }
}
```

### 响应式导航菜单
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>响应式导航</title>
    <style>
        /* 导航样式 */
        .navbar {
            background: #333;
            padding: 1rem 0;
        }

        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .nav-logo {
            color: white;
            font-size: 1.5rem;
            text-decoration: none;
        }

        .nav-menu {
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
        }

        .nav-item {
            margin-left: 2rem;
        }

        .nav-link {
            color: white;
            text-decoration: none;
            transition: color 0.3s;
        }

        .nav-link:hover {
            color: #ffd700;
        }

        /* 汉堡菜单按钮 */
        .nav-toggle {
            display: none;
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }

        /* 移动端样式 */
        @media (max-width: 768px) {
            .nav-toggle {
                display: block;
            }

            .nav-menu {
                display: none;
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: #333;
                flex-direction: column;
                padding: 1rem 0;
            }

            .nav-menu.active {
                display: flex;
            }

            .nav-item {
                margin: 0;
                text-align: center;
                padding: 0.5rem 0;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="#" class="nav-logo">Logo</a>
            <button class="nav-toggle" onclick="toggleMenu()">☰</button>
            <ul class="nav-menu" id="navMenu">
                <li class="nav-item"><a href="#" class="nav-link">首页</a></li>
                <li class="nav-item"><a href="#" class="nav-link">关于</a></li>
                <li class="nav-item"><a href="#" class="nav-link">服务</a></li>
                <li class="nav-item"><a href="#" class="nav-link">联系</a></li>
            </ul>
        </div>
    </nav>

    <script>
        function toggleMenu() {
            const navMenu = document.getElementById('navMenu');
            navMenu.classList.toggle('active');
        }
    </script>
</body>
</html>
```

### 现代CSS Grid响应式布局
```css
/* CSS Grid响应式布局 */
.grid-container {
    display: grid;
    gap: 20px;
    padding: 20px;
    grid-template-columns: 1fr;
}

/* 卡片样式 */
.card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.3s;
}

.card:hover {
    transform: translateY(-2px);
}

/* 平板端布局 */
@media (min-width: 768px) {
    .grid-container {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* 桌面端布局 */
@media (min-width: 1024px) {
    .grid-container {
        grid-template-columns: repeat(3, 1fr);
    }
}

/* 大屏幕布局 */
@media (min-width: 1200px) {
    .grid-container {
        grid-template-columns: repeat(4, 1fr);
        max-width: 1200px;
        margin: 0 auto;
    }
}
```

### JavaScript响应式检测
```javascript
// 响应式断点检测
class ResponsiveDetector {
    constructor() {
        this.breakpoints = {
            mobile: 768,
            tablet: 1024,
            desktop: 1200
        };
        this.currentDevice = this.getCurrentDevice();
        this.init();
    }

    getCurrentDevice() {
        const width = window.innerWidth;
        if (width < this.breakpoints.mobile) return 'mobile';
        if (width < this.breakpoints.tablet) return 'tablet';
        if (width < this.breakpoints.desktop) return 'desktop';
        return 'large-desktop';
    }

    init() {
        // 监听窗口大小变化
        window.addEventListener('resize', () => {
            const newDevice = this.getCurrentDevice();
            if (newDevice !== this.currentDevice) {
                this.currentDevice = newDevice;
                this.onDeviceChange(newDevice);
            }
        });

        // 初始化设备特定功能
        this.initDeviceFeatures();
    }

    onDeviceChange(device) {
        console.log(`设备类型变更: ${device}`);
        
        // 触发设备变更事件
        const event = new CustomEvent('deviceChange', {
            detail: { device }
        });
        document.dispatchEvent(event);
    }

    initDeviceFeatures() {
        switch (this.currentDevice) {
            case 'mobile':
                this.initMobileFeatures();
                break;
            case 'tablet':
                this.initTabletFeatures();
                break;
            case 'desktop':
                this.initDesktopFeatures();
                break;
        }
    }

    initMobileFeatures() {
        // 移动端特定功能
        document.body.classList.add('mobile-device');
        console.log('初始化移动端功能');
    }

    initTabletFeatures() {
        // 平板端特定功能
        document.body.classList.add('tablet-device');
        console.log('初始化平板端功能');
    }

    initDesktopFeatures() {
        // 桌面端特定功能
        document.body.classList.add('desktop-device');
        console.log('初始化桌面端功能');
    }

    isMobile() {
        return this.currentDevice === 'mobile';
    }

    isTablet() {
        return this.currentDevice === 'tablet';
    }

    isDesktop() {
        return this.currentDevice === 'desktop';
    }
}

// 使用示例
const detector = new ResponsiveDetector();

// 监听设备变更
document.addEventListener('deviceChange', (event) => {
    const { device } = event.detail;
    
    // 根据设备类型调整UI
    switch (device) {
        case 'mobile':
            // 移动端UI调整
            break;
        case 'tablet':
            // 平板端UI调整
            break;
        case 'desktop':
            // 桌面端UI调整
            break;
    }
});

// 在组件中使用
function getResponsiveValue(mobileValue, tabletValue, desktopValue) {
    if (detector.isMobile()) return mobileValue;
    if (detector.isTablet()) return tabletValue;
    return desktopValue;
}

// 示例：根据设备类型设置不同的配置
const config = {
    itemsPerPage: getResponsiveValue(5, 10, 20),
    animationDuration: getResponsiveValue(200, 300, 400),
    showSidebar: !detector.isMobile()
};
```

## 最佳实践

### 设计原则
1. **移动优先**: 从小屏幕开始设计，逐步增强
2. **内容优先**: 确保重要内容在所有设备上可见
3. **触摸友好**: 设计适合触摸操作的界面元素
4. **性能优化**: 针对移动设备优化加载性能

### 技术实现
1. **相对单位**: 使用rem、em、%、vw、vh等相对单位
2. **弹性布局**: 使用Flexbox和Grid实现灵活布局
3. **媒体查询**: 合理设置断点，避免过度使用
4. **响应式图片**: 使用srcset和sizes属性优化图片加载

### 用户体验
1. **一致性**: 保持不同设备上的体验一致性
2. **可访问性**: 确保响应式设计不影响可访问性
3. **加载优化**: 优先加载关键内容
4. **交互反馈**: 提供清晰的交互反馈

## 相关技能

- **component-analyzer** - 组件分析与设计
- **performance-optimization** - 前端性能优化
- **css-validator** - CSS验证与优化
- **bundle-analyzer** - 包分析与优化
- **form-handling** - 表单处理与验证
