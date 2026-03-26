# 前端测试技术参考

## 概述

前端测试是确保Web应用质量的关键环节，涵盖单元测试、集成测试、端到端测试等多个层面。良好的测试策略能够提高代码质量、减少bug、增强开发效率。

## 测试类型

### 单元测试
单元测试是最小粒度的测试，针对单个函数、组件或模块进行测试。

#### Jest框架
```javascript
// 示例： Jest单元测试
describe('MathUtils', () => {
  test('should add two numbers correctly', () => {
    expect(add(2, 3)).toBe(5);
  });
  
  test('should handle negative numbers', () => {
    expect(add(-2, 3)).toBe(1);
  });
});
```

#### Vitest框架
```javascript
// 示例： Vitest单元测试
import { describe, it, expect } from 'vitest';
import { calculateTotal } from './utils';

describe('calculateTotal', () => {
  it('should calculate total with tax', () => {
    const result = calculateTotal(100, 0.1);
    expect(result).toBe(110);
  });
});
```

### 组件测试
组件测试针对React、Vue等UI组件进行测试。

#### React Testing Library
```javascript
// 示例： React组件测试
import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button';

test('renders button with text', () => {
  render(<Button>Click me</Button>);
  const button = screen.getByRole('button', { name: /click me/i });
  expect(button).toBeInTheDocument();
});

test('calls onClick when clicked', () => {
  const handleClick = jest.fn();
  render(<Button onClick={handleClick}>Click me</Button>);
  
  fireEvent.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

#### Vue Test Utils
```javascript
// 示例： Vue组件测试
import { mount } from '@vue/test-utils';
import MyComponent from './MyComponent.vue';

describe('MyComponent', () => {
  test('renders correctly', () => {
    const wrapper = mount(MyComponent);
    expect(wrapper.find('.title').text()).toBe('Hello World');
  });
  
  test('emits event when button clicked', async () => {
    const wrapper = mount(MyComponent);
    await wrapper.find('button').trigger('click');
    
    expect(wrapper.emitted().buttonClick).toBeTruthy();
  });
});
```

### 集成测试
集成测试测试多个组件或模块之间的交互。

```javascript
// 示例： 集成测试
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from './store';
import UserList from './UserList';

test('should display users from API', async () => {
  render(
    <Provider store={store}>
      <UserList />
    </Provider>
  );
  
  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

### 端到端测试
端到端测试模拟真实用户操作，测试完整的应用流程。

#### Cypress
```javascript
// 示例： Cypress E2E测试
describe('User Login', () => {
  it('should login successfully with valid credentials', () => {
    cy.visit('/login');
    
    cy.get('[data-testid="email-input"]').type('user@example.com');
    cy.get('[data-testid="password-input"]').type('password123');
    cy.get('[data-testid="login-button"]').click();
    
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="welcome-message"]').should('contain', 'Welcome');
  });
});
```

#### Playwright
```javascript
// 示例： Playwright E2E测试
import { test, expect } from '@playwright/test';

test('user can add item to cart', async ({ page }) => {
  await page.goto('/');
  
  await page.click('[data-testid="product-1"]');
  await page.click('[data-testid="add-to-cart"]');
  
  await expect(page.locator('[data-testid="cart-count"]')).toHaveText('1');
});
```

## 测试工具和框架

### 测试运行器
- **Jest**: 全功能JavaScript测试框架
- **Vitest**: 基于Vite的快速测试框架
- **Mocha**: 灵活的JavaScript测试框架
- **Jasmine**: 行为驱动开发框架

### 断言库
- **Chai**: BDD/TDD断言库
- **Expect.js**: 轻量级断言库
- **Should.js**: 语义化断言库

### Mock和Spy
```javascript
// 示例： Jest Mock
import { fetchData } from './api';
import apiClient from './apiClient';

jest.mock('./apiClient');
const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

test('should fetch data successfully', async () => {
  mockedApiClient.get.mockResolvedValue({ data: 'test data' });
  
  const result = await fetchData();
  expect(result).toBe('test data');
});
```

### 测试覆盖率
```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

## 测试最佳实践

### 测试命名规范
```javascript
// 好的测试命名
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', () => {
      // 测试逻辑
    });
    
    it('should throw error with invalid email', () => {
      // 测试逻辑
    });
  });
});
```

### 测试组织结构
```
src/
├── components/
│   ├── Button/
│   │   ├── Button.jsx
│   │   ├── Button.test.jsx
│   │   └── Button.stories.jsx
│   └── Form/
│       ├── Form.jsx
│       ├── Form.test.jsx
│       └── Form.stories.jsx
├── utils/
│   ├── validation.js
│   └── validation.test.js
└── __tests__/
    └── integration/
        └── user-flow.test.js
```

### 测试数据管理
```javascript
// 示例： 测试工厂模式
class UserFactory {
  static create(overrides = {}) {
    return {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      ...overrides
    };
  }
  
  static createMany(count, overrides = {}) {
    return Array.from({ length: count }, (_, i) => 
      this.create({ id: String(i + 1), ...overrides })
    );
  }
}
```

## 性能测试

### 组件性能测试
```javascript
// 示例： React性能测试
import { render } from '@testing-library/react';
import { performance } from 'perf_hooks';

test('component should render within performance budget', () => {
  const start = performance.now();
  
  render(<HeavyComponent />);
  
  const end = performance.now();
  const renderTime = end - start;
  
  expect(renderTime).toBeLessThan(100); // 100ms budget
});
```

### 内存泄漏检测
```javascript
// 示例： 内存泄漏测试
test('should not leak memory on component unmount', () => {
  const { unmount } = render(<ComponentWithListeners />);
  
  // 模拟多次挂载和卸载
  for (let i = 0; i < 100; i++) {
    unmount();
    render(<ComponentWithListeners />);
  }
  
  // 检查是否有事件监听器残留
  expect(document.eventListeners?.length).toBe(0);
});
```

## 可访问性测试

```javascript
// 示例： 可访问性测试
import { axe, toHaveNoViolations } from 'jest-axe';
import { render } from '@testing-library/react';

expect.extend(toHaveNoViolations);

test('should be accessible', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  
  expect(results).toHaveNoViolations();
});
```

## 视觉回归测试

```javascript
// 示例： 视觉回归测试
import { render } from '@testing-library/react';
import { matchImageSnapshot } from 'jest-image-snapshot';

test('should match visual snapshot', () => {
  const { container } = render(<MyComponent />);
  
  expect(container).toMatchImageSnapshot();
});
```

## 测试配置

### Jest配置示例
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest',
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{test,spec}.{js,jsx,ts,tsx}'
  ]
};
```

### Vitest配置示例
```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.js'],
    globals: true,
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/setupTests.js'
      ]
    }
  }
});
```

## 持续集成

### GitHub Actions配置
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [16, 18, 20]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - run: npm ci
    - run: npm run test:coverage
    - run: npm run test:e2e
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

## 常见问题和解决方案

### 异步测试
```javascript
// 错误方式
test('should fetch data', () => {
  fetchData().then(data => {
    expect(data).toBe('expected');
  });
});

// 正确方式
test('should fetch data', async () => {
  const data = await fetchData();
  expect(data).toBe('expected');
});

// 或者使用回调
test('should fetch data', (done) => {
  fetchData().then(data => {
    expect(data).toBe('expected');
    done();
  });
});
```

### Mock定时器
```javascript
// 示例： Mock定时器
jest.useFakeTimers();

test('should debounce function calls', () => {
  const mockFn = jest.fn();
  const debouncedFn = debounce(mockFn, 1000);
  
  debouncedFn();
  debouncedFn();
  debouncedFn();
  
  jest.advanceTimersByTime(1000);
  
  expect(mockFn).toHaveBeenCalledTimes(1);
});

jest.useRealTimers();
```

## 相关资源

### 官方文档
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro)
- [Cypress Documentation](https://docs.cypress.io/guides/overview/why-cypress)
- [Playwright Documentation](https://playwright.dev/)

### 教程和指南
- [Testing JavaScript](https://testingjavascript.com/)
- [Frontend Testing Best Practices](https://kentcdodds.com/blog/common-testing-mistakes)
- [Testing Strategies](https://martinfowler.com/articles/testing-strategies.html)

### 社区资源
- [Stack Overflow - Testing](https://stackoverflow.com/questions/tagged/testing)
- [Reddit - r/frontendtesting](https://www.reddit.com/r/frontendtesting/)
- [Testing Library Discord](https://discord.gg/testing-library)

### 相关工具
- **Storybook**: 组件开发和测试环境
- **MSW**: API Mocking工具
- **TestCafe**: 端到端测试框架
- **Puppeteer**: 无头浏览器自动化

### 进阶阅读
- [The Art of Unit Testing](https://www.manning.com/books/the-art-of-unit-testing)
- [Working Effectively with Legacy Code](https://www.amazon.com/Working-Effectively-Legacy-Michael-Feathers/dp/0131177052)
- [xUnit Test Patterns](https://www.amazon.com/xUnit-Test-Patterns-Refactoring-Code/dp/0131495054)
