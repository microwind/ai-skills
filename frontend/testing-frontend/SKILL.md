---
name: 前端测试
description: "当编写前端测试时，设计测试策略，优化测试覆盖率，解决测试问题。验证测试架构，实施自动化测试，和最佳实践。"
license: MIT
---

# 前端测试技能

## 概述
前端测试是确保Web应用质量的重要手段，包括单元测试、集成测试、端到端测试等多个层次。不当的测试策略会导致测试覆盖率低、维护困难、质量保障不足。

**核心原则**: 好的前端测试应该覆盖全面、执行快速、维护简单、反馈及时。坏的测试会导致测试脆弱、执行缓慢、难以维护。

## 何时使用

**始终:**
- 开发新功能时
- 重构代码时
- 修复bug时
- 优化性能时
- 部署上线前
- 代码审查时

**触发短语:**
- "如何测试React组件？"
- "前端测试最佳实践"
- "测试覆盖率怎么提高？"
- "端到端测试怎么写？"
- "Mock数据怎么处理？"
- "测试性能优化方案"

## 前端测试技能功能

### 测试类型分析
- 单元测试（Unit Testing）
- 集成测试（Integration Testing）
- 端到端测试（E2E Testing）
- 组件测试（Component Testing）
- 视觉回归测试（Visual Regression）

### 测试框架应用
- Jest测试框架
- React Testing Library
- Cypress端到端测试
- Playwright自动化测试
- Vitest现代测试框架

### 测试策略设计
- 测试金字塔原则
- 测试驱动开发（TDD）
- 行为驱动开发（BDD）
- 测试覆盖率分析
- 持续集成测试

## 常见问题

### 测试设计问题
- **问题**: 测试过于依赖实现细节
- **原因**: 测试关注组件内部实现而非用户行为
- **解决**: 使用React Testing Library，测试用户交互

- **问题**: 测试脆弱易碎
- **原因**: 测试与实现细节耦合过紧
- **解决**: 关注行为而非实现，使用更稳定的测试策略

- **问题**: Mock数据管理混乱
- **原因**: 缺乏统一的Mock数据管理策略
- **解决**: 使用MSW或Jest Mock统一管理

### 性能问题
- **问题**: 测试执行缓慢
- **原因**: 测试包含过多异步操作和DOM操作
- **解决**: 优化测试结构，使用轻量级测试工具

- **问题**: 内存泄漏
- **原因**: 测试后未正确清理资源
- **解决**: 实现测试清理机制，避免内存泄漏

## 代码示例

### Jest单元测试基础
```javascript
// utils/mathUtils.js
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;
export const multiply = (a, b) => a * b;
export const divide = (a, b) => {
    if (b === 0) {
        throw new Error('Division by zero');
    }
    return a / b;
};

export const calculateDiscount = (price, discount) => {
    if (discount < 0 || discount > 100) {
        throw new Error('Invalid discount percentage');
    }
    return price * (1 - discount / 100);
};
```

```javascript
// utils/mathUtils.test.js
import { 
    add, 
    subtract, 
    multiply, 
    divide, 
    calculateDiscount 
} from './mathUtils';

describe('Math Utils', () => {
    describe('add', () => {
        test('should return sum of two positive numbers', () => {
            expect(add(2, 3)).toBe(5);
        });

        test('should handle negative numbers', () => {
            expect(add(-2, 3)).toBe(1);
            expect(add(-2, -3)).toBe(-5);
        });

        test('should handle zero', () => {
            expect(add(0, 5)).toBe(5);
            expect(add(0, 0)).toBe(0);
        });
    });

    describe('subtract', () => {
        test('should return difference of two numbers', () => {
            expect(subtract(5, 3)).toBe(2);
        });

        test('should handle negative results', () => {
            expect(subtract(3, 5)).toBe(-2);
        });
    });

    describe('multiply', () => {
        test('should return product of two numbers', () => {
            expect(multiply(3, 4)).toBe(12);
        });

        test('should handle zero', () => {
            expect(multiply(5, 0)).toBe(0);
        });

        test('should handle negative numbers', () => {
            expect(multiply(-2, 3)).toBe(-6);
            expect(multiply(-2, -3)).toBe(6);
        });
    });

    describe('divide', () => {
        test('should return quotient of two numbers', () => {
            expect(divide(10, 2)).toBe(5);
        });

        test('should handle decimal results', () => {
            expect(divide(5, 2)).toBe(2.5);
        });

        test('should throw error when dividing by zero', () => {
            expect(() => divide(10, 0)).toThrow('Division by zero');
        });
    });

    describe('calculateDiscount', () => {
        test('should calculate discounted price correctly', () => {
            expect(calculateDiscount(100, 20)).toBe(80);
            expect(calculateDiscount(50, 10)).toBe(45);
        });

        test('should handle zero discount', () => {
            expect(calculateDiscount(100, 0)).toBe(100);
        });

        test('should handle 100% discount', () => {
            expect(calculateDiscount(100, 100)).toBe(0);
        });

        test('should throw error for negative discount', () => {
            expect(() => calculateDiscount(100, -10)).toThrow('Invalid discount percentage');
        });

        test('should throw error for discount over 100%', () => {
            expect(() => calculateDiscount(100, 110)).toThrow('Invalid discount percentage');
        });
    });
});
```

### React组件测试
```javascript
// components/UserCard.jsx
import React from 'react';
import './UserCard.css';

const UserCard = ({ user, onEdit, onDelete, isLoading = false }) => {
    if (isLoading) {
        return <div className="user-card loading">加载中...</div>;
    }

    if (!user) {
        return <div className="user-card empty">用户信息不可用</div>;
    }

    const handleEdit = () => {
        if (onEdit) {
            onEdit(user.id);
        }
    };

    const handleDelete = () => {
        if (onDelete && window.confirm('确定要删除这个用户吗？')) {
            onDelete(user.id);
        }
    };

    return (
        <div className="user-card" data-testid="user-card">
            <div className="user-avatar">
                <img 
                    src={user.avatar || '/default-avatar.png'} 
                    alt={`${user.name}的头像`}
                    onError={(e) => {
                        e.target.src = '/default-avatar.png';
                    }}
                />
            </div>
            <div className="user-info">
                <h3 className="user-name">{user.name}</h3>
                <p className="user-email">{user.email}</p>
                <p className="user-role">{user.role}</p>
                {user.department && (
                    <p className="user-department">{user.department}</p>
                )}
            </div>
            <div className="user-actions">
                <button 
                    className="btn-edit"
                    onClick={handleEdit}
                    aria-label={`编辑用户${user.name}`}
                >
                    编辑
                </button>
                <button 
                    className="btn-delete"
                    onClick={handleDelete}
                    aria-label={`删除用户${user.name}`}
                >
                    删除
                </button>
            </div>
        </div>
    );
};

export default UserCard;
```

```javascript
// components/UserCard.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UserCard from './UserCard';

// Mock window.confirm
const mockConfirm = jest.fn();
Object.defineProperty(window, 'confirm', {
    writable: true,
    value: mockConfirm,
});

describe('UserCard Component', () => {
    const mockUser = {
        id: 1,
        name: '张三',
        email: 'zhangsan@example.com',
        role: '前端开发',
        department: '技术部',
        avatar: '/avatar1.jpg'
    };

    beforeEach(() => {
        mockConfirm.mockClear();
    });

    describe('正常状态渲染', () => {
        test('应该显示用户信息', () => {
            render(<UserCard user={mockUser} />);
            
            expect(screen.getByText('张三')).toBeInTheDocument();
            expect(screen.getByText('zhangsan@example.com')).toBeInTheDocument();
            expect(screen.getByText('前端开发')).toBeInTheDocument();
            expect(screen.getByText('技术部')).toBeInTheDocument();
        });

        test('应该显示用户头像', () => {
            render(<UserCard user={mockUser} />);
            
            const avatar = screen.getByAltText('张三的头像');
            expect(avatar).toBeInTheDocument();
            expect(avatar).toHaveAttribute('src', '/avatar1.jpg');
        });

        test('应该显示编辑和删除按钮', () => {
            render(<UserCard user={mockUser} />);
            
            expect(screen.getByRole('button', { name: '编辑用户张三' })).toBeInTheDocument();
            expect(screen.getByRole('button', { name: '删除用户张三' })).toBeInTheDocument();
        });
    });

    describe('加载状态', () => {
        test('应该显示加载状态', () => {
            render(<UserCard user={mockUser} isLoading={true} />);
            
            expect(screen.getByText('加载中...')).toBeInTheDocument();
            expect(screen.getByTestId('user-card')).toHaveClass('loading');
        });

        test('不应该显示用户信息', () => {
            render(<UserCard user={mockUser} isLoading={true} />);
            
            expect(screen.queryByText('张三')).not.toBeInTheDocument();
            expect(screen.queryByRole('button')).not.toBeInTheDocument();
        });
    });

    describe('空状态', () => {
        test('应该显示空状态消息', () => {
            render(<UserCard user={null} />);
            
            expect(screen.getByText('用户信息不可用')).toBeInTheDocument();
            expect(screen.getByTestId('user-card')).toHaveClass('empty');
        });
    });

    describe('用户交互', () => {
        test('点击编辑按钮应该调用onEdit回调', async () => {
            const mockOnEdit = jest.fn();
            const user = userEvent.setup();
            
            render(<UserCard user={mockUser} onEdit={mockOnEdit} />);
            
            await user.click(screen.getByRole('button', { name: '编辑用户张三' }));
            
            expect(mockOnEdit).toHaveBeenCalledWith(1);
            expect(mockOnEdit).toHaveBeenCalledTimes(1);
        });

        test('点击删除按钮应该显示确认对话框', async () => {
            mockConfirm.mockReturnValue(false);
            const mockOnDelete = jest.fn();
            const user = userEvent.setup();
            
            render(<UserCard user={mockUser} onDelete={mockOnDelete} />);
            
            await user.click(screen.getByRole('button', { name: '删除用户张三' }));
            
            expect(mockConfirm).toHaveBeenCalledWith('确定要删除这个用户吗？');
            expect(mockOnDelete).not.toHaveBeenCalled();
        });

        test('确认删除应该调用onDelete回调', async () => {
            mockConfirm.mockReturnValue(true);
            const mockOnDelete = jest.fn();
            const user = userEvent.setup();
            
            render(<UserCard user={mockUser} onDelete={mockOnDelete} />);
            
            await user.click(screen.getByRole('button', { name: '删除用户张三' }));
            
            expect(mockConfirm).toHaveBeenCalledWith('确定要删除这个用户吗？');
            expect(mockOnDelete).toHaveBeenCalledWith(1);
            expect(mockOnDelete).toHaveBeenCalledTimes(1);
        });
    });

    describe('边界情况', () => {
        test('没有department字段时不应该显示部门信息', () => {
            const userWithoutDept = { ...mockUser };
            delete userWithoutDept.department;
            
            render(<UserCard user={userWithoutDept} />);
            
            expect(screen.queryByText('技术部')).not.toBeInTheDocument();
        });

        test('没有avatar时应该使用默认头像', () => {
            const userWithoutAvatar = { ...mockUser };
            delete userWithoutAvatar.avatar;
            
            render(<UserCard user={userWithoutAvatar} />);
            
            const avatar = screen.getByAltText('张三的头像');
            expect(avatar).toHaveAttribute('src', '/default-avatar.png');
        });

        test('头像加载失败时应该显示默认头像', async () => {
            render(<UserCard user={mockUser} />);
            
            const avatar = screen.getByAltText('张三的头像');
            
            // 模拟图片加载失败
            fireEvent.error(avatar);
            
            await waitFor(() => {
                expect(avatar).toHaveAttribute('src', '/default-avatar.png');
            });
        });

        test('没有回调函数时不应该报错', async () => {
            const user = userEvent.setup();
            
            render(<UserCard user={mockUser} />);
            
            // 点击按钮不应该抛出错误
            await user.click(screen.getByRole('button', { name: '编辑用户张三' }));
            await user.click(screen.getByRole('button', { name: '删除用户张三' }));
        });
    });
});
```

### Mock数据和API测试
```javascript
// __mocks__/api.js
export const mockUsers = [
    {
        id: 1,
        name: '张三',
        email: 'zhangsan@example.com',
        role: '前端开发',
        department: '技术部'
    },
    {
        id: 2,
        name: '李四',
        email: 'lisi@example.com',
        role: '后端开发',
        department: '技术部'
    }
];

export const userApi = {
    getUsers: jest.fn(),
    getUserById: jest.fn(),
    createUser: jest.fn(),
    updateUser: jest.fn(),
    deleteUser: jest.fn()
};

// 设置默认返回值
userApi.getUsers.mockResolvedValue(mockUsers);
userApi.getUserById.mockImplementation((id) => 
    Promise.resolve(mockUsers.find(user => user.id === id))
);
userApi.createUser.mockImplementation((userData) => 
    Promise.resolve({ id: Date.now(), ...userData })
);
userApi.updateUser.mockImplementation((id, updates) => 
    Promise.resolve({ id, ...mockUsers.find(user => user.id === id), ...updates })
);
userApi.deleteUser.mockResolvedValue({ success: true });
```

```javascript
// hooks/useUsers.test.js
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import useUsers from './useUsers';
import { userApi } from '../__mocks__/api';

// 创建测试用的QueryClient
const createTestQueryClient = () => new QueryClient({
    defaultOptions: {
        queries: {
            retry: false,
            gcTime: 0,
        },
    },
});

const wrapper = ({ children }) => (
    <QueryClientProvider client={createTestQueryClient()}>
        {children}
    </QueryClientProvider>
);

describe('useUsers Hook', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('应该成功获取用户列表', async () => {
        userApi.getUsers.mockResolvedValue([
            { id: 1, name: '张三', email: 'zhangsan@example.com' }
        ]);

        const { result } = renderHook(() => useUsers(), { wrapper });

        expect(result.current.isLoading).toBe(true);

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.data).toEqual([
            { id: 1, name: '张三', email: 'zhangsan@example.com' }
        ]);
        expect(result.current.error).toBeNull();
        expect(userApi.getUsers).toHaveBeenCalledTimes(1);
    });

    test('应该处理API错误', async () => {
        const errorMessage = '网络错误';
        userApi.getUsers.mockRejectedValue(new Error(errorMessage));

        const { result } = renderHook(() => useUsers(), { wrapper });

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        expect(result.current.data).toBeUndefined();
        expect(result.current.error).toBe(errorMessage);
    });

    test('应该支持创建用户', async () => {
        const newUser = { name: '王五', email: 'wangwu@example.com' };
        userApi.getUsers.mockResolvedValue([]);
        userApi.createUser.mockResolvedValue({ id: 1, ...newUser });

        const { result } = renderHook(() => useUsers(), { wrapper });

        await waitFor(() => {
            expect(result.current.isLoading).toBe(false);
        });

        await result.current.createUser(newUser);

        expect(userApi.createUser).toHaveBeenCalledWith(newUser);
    });
});
```

### Cypress端到端测试
```javascript
// cypress/e2e/user-management.cy.js
describe('用户管理', () => {
    beforeEach(() => {
        // 登录
        cy.visit('/login');
        cy.get('[data-testid="username-input"]').type('admin');
        cy.get('[data-testid="password-input"]').type('password');
        cy.get('[data-testid="login-button"]').click();
        
        // 等待跳转到用户管理页面
        cy.url().should('include', '/users');
    });

    it('应该显示用户列表', () => {
        cy.get('[data-testid="user-list"]').should('be.visible');
        cy.get('[data-testid="user-card"]').should('have.length.greaterThan', 0);
    });

    it('应该能够搜索用户', () => {
        cy.get('[data-testid="search-input"]').type('张三');
        cy.get('[data-testid="search-button"]').click();
        
        cy.get('[data-testid="user-card"]').should('have.length', 1);
        cy.get('[data-testid="user-card"]').first().should('contain', '张三');
    });

    it('应该能够创建新用户', () => {
        cy.get('[data-testid="add-user-button"]').click();
        
        cy.get('[data-testid="user-form"]').should('be.visible');
        cy.get('[data-testid="name-input"]').type('测试用户');
        cy.get('[data-testid="email-input"]').type('test@example.com');
        cy.get('[data-testid="role-select"]').select('前端开发');
        cy.get('[data-testid="submit-button"]').click();
        
        cy.get('[data-testid="success-message"]').should('contain', '用户创建成功');
        cy.get('[data-testid="user-card"]').should('contain', '测试用户');
    });

    it('应该能够编辑用户', () => {
        cy.get('[data-testid="user-card"]').first().within(() => {
            cy.get('[data-testid="edit-button"]').click();
        });
        
        cy.get('[data-testid="user-form"]').should('be.visible');
        cy.get('[data-testid="name-input"]').clear().type('更新后的用户名');
        cy.get('[data-testid="submit-button"]').click();
        
        cy.get('[data-testid="success-message"]').should('contain', '用户更新成功');
        cy.get('[data-testid="user-card"]').first().should('contain', '更新后的用户名');
    });

    it('应该能够删除用户', () => {
        cy.get('[data-testid="user-card"]').first().within(() => {
            cy.get('[data-testid="delete-button"]').click();
        });
        
        cy.get('[data-testid="confirm-dialog"]').should('be.visible');
        cy.get('[data-testid="confirm-button"]').click();
        
        cy.get('[data-testid="success-message"]').should('contain', '用户删除成功');
        
        // 验证用户已从列表中移除
        cy.get('[data-testid="user-card"]').should('have.length.lessThan', 
            cy.get('[data-testid="user-card"]').its('length'));
    });

    it('应该处理表单验证错误', () => {
        cy.get('[data-testid="add-user-button"]').click();
        
        // 提交空表单
        cy.get('[data-testid="submit-button"]').click();
        
        cy.get('[data-testid="error-message"]').should('be.visible');
        cy.get('[data-testid="name-input"]').should('have.class', 'error');
        cy.get('[data-testid="email-input"]').should('have.class', 'error');
    });

    it('应该处理网络错误', () => {
        // 模拟网络错误
        cy.intercept('POST', '/api/users', { forceNetworkError: true });
        
        cy.get('[data-testid="add-user-button"]').click();
        cy.get('[data-testid="name-input"]').type('测试用户');
        cy.get('[data-testid="email-input"]').type('test@example.com');
        cy.get('[data-testid="submit-button"]').click();
        
        cy.get('[data-testid="error-message"]').should('contain', '网络错误');
    });
});
```

### 测试配置文件
```javascript
// jest.config.js
module.exports = {
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
    moduleNameMapping: {
        '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
        '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$':
            '<rootDir>/__mocks__/fileMock.js',
    },
    collectCoverageFrom: [
        'src/**/*.{js,jsx,ts,tsx}',
        '!src/**/*.d.ts',
        '!src/index.js',
        '!src/serviceWorker.js',
    ],
    coverageThreshold: {
        global: {
            branches: 80,
            functions: 80,
            lines: 80,
            statements: 80,
        },
    },
    testMatch: [
        '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
        '<rootDir>/src/**/*.{test,spec}.{js,jsx,ts,tsx}',
    ],
    transform: {
        '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
    },
};
```

```javascript
// src/setupTests.js
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

// 配置Testing Library
configure({ testIdAttribute: 'data-testid' });

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
}));

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
    })),
});
```

## 最佳实践

### 测试策略
1. **测试金字塔**: 更多单元测试，适量集成测试，少量端到端测试
2. **用户行为测试**: 关注用户能看到和交互的行为
3. **测试隔离**: 确保测试之间相互独立
4. **快速反馈**: 优先执行快速测试，提供快速反馈

### 测试编写
1. **描述性测试**: 使用清晰的测试描述
2. **AAA模式**: Arrange（准备）、Act（执行）、Assert（断言）
3. **单一职责**: 每个测试只验证一个功能点
4. **边界测试**: 测试边界条件和异常情况

### 维护优化
1. **定期重构**: 保持测试代码的整洁
2. **覆盖率监控**: 监控测试覆盖率变化
3. **性能优化**: 优化慢速测试
4. **持续集成**: 在CI/CD中集成测试

## 相关技能

- **component-analyzer** - 组件分析与设计
- **performance-optimization** - 前端性能优化
- **form-handling** - 表单处理与验证
- **react-components** - React组件最佳实践
- **code-quality** - 代码质量与测试策略
