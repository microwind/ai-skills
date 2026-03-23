# 前端组件分析器参考文档

## 组件设计原则

### 单一职责原则
- **定义**: 每个组件只负责一个功能
- **好处**: 提高可维护性、可测试性和可复用性
- **示例**:
```jsx
// 好的示例 - 单一职责
const UserProfile = ({ user }) => {
  return (
    <div className="user-profile">
      <Avatar src={user.avatar} />
      <UserInfo name={user.name} email={user.email} />
    </div>
  );
};

// 不好的示例 - 多重职责
const UserComponent = ({ user, onLogin, onLogout, theme }) => {
  // 混合了UI渲染、认证逻辑、主题管理
  return (
    <div>
      <UserProfile user={user} />
      <LoginButton onLogin={onLogin} />
      <ThemeToggle theme={theme} />
    </div>
  );
};
```

### 组合优于继承
- **原则**: 通过组合小组件构建复杂组件
- **好处**: 提高灵活性和可复用性
- **示例**:
```jsx
// 组合模式
const Card = ({ children, title, footer }) => {
  return (
    <div className="card">
      {title && <div className="card-header">{title}</div>}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
};

// 使用组合
const UserCard = ({ user }) => {
  return (
    <Card title="用户信息">
      <UserInfo user={user} />
      <Card footer={<EditButton userId={user.id} />} />
    </Card>
  );
};
```

## React组件模式

### 函数组件最佳实践

#### 组件定义
```jsx
// 推荐的函数组件结构
const MyComponent = ({ 
  prop1, 
  prop2, 
  onAction,
  ...restProps 
}) => {
  // 1. 状态定义
  const [state, setState] = useState(initialState);
  
  // 2. 副作用
  useEffect(() => {
    // 副作用逻辑
    return () => {
      // 清理逻辑
    };
  }, [dependencies]);
  
  // 3. 事件处理函数
  const handleAction = useCallback(() => {
    onAction(state);
  }, [state, onAction]);
  
  // 4. 计算属性
  const computedValue = useMemo(() => {
    return expensiveCalculation(state);
  }, [state]);
  
  // 5. 渲染
  return (
    <div {...restProps}>
      {/* JSX内容 */}
    </div>
  );
};

// PropTypes或TypeScript类型定义
MyComponent.propTypes = {
  prop1: PropTypes.string.isRequired,
  prop2: PropTypes.number,
  onAction: PropTypes.func
};
```

#### 自定义Hook模式
```jsx
// 自定义Hook示例
const useApi = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(url, options);
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [url, options]);
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  return { data, loading, error, refetch: fetchData };
};

// 使用自定义Hook
const UserList = () => {
  const { data: users, loading, error } = useApi('/api/users');
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
};
```

### 高阶组件模式

#### 基础高阶组件
```jsx
// 高阶组件工厂
const withLoading = (WrappedComponent) => {
  const WithLoadingComponent = ({ isLoading, ...props }) => {
    if (isLoading) {
      return <LoadingSpinner />;
    }
    return <WrappedComponent {...props} />;
  };
  
  WithLoadingComponent.displayName = `withLoading(${WrappedComponent.displayName || 'Component'})`;
  
  return WithLoadingComponent;
};

// 使用高阶组件
const UserList = ({ users }) => {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
};

const UserListWithLoading = withLoading(UserList);

// 应用
const App = () => {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    fetchUsers().then(data => {
      setUsers(data);
      setIsLoading(false);
    });
  }, []);
  
  return <UserListWithLoading users={users} isLoading={isLoading} />;
};
```

#### 属性代理高阶组件
```jsx
const withLogger = (WrappedComponent) => {
  const WithLoggerComponent = (props) => {
    useEffect(() => {
      console.log(`${WrappedComponent.displayName} props:`, props);
    }, [props]);
    
    return <WrappedComponent {...props} />;
  };
  
  WithLoggerComponent.displayName = `withLogger(${WrappedComponent.displayName || 'Component'})`;
  
  return WithLoggerComponent;
};
```

### Render Props模式

```jsx
// Render Props组件
const DataProvider = ({ url, children }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    setLoading(true);
    fetch(url)
      .then(response => response.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, [url]);
  
  return children({ data, loading });
};

// 使用Render Props
const UserList = () => {
  return (
    <DataProvider url="/api/users">
      {({ data, loading }) => {
        if (loading) return <LoadingSpinner />;
        return (
          <ul>
            {data?.map(user => (
              <li key={user.id}>{user.name}</li>
            ))}
          </ul>
        );
      }}
    </DataProvider>
  );
};
```

## Vue组件模式

### 组件定义最佳实践

#### Vue 3 Composition API
```vue
<template>
  <div class="user-list">
    <div v-if="loading" class="loading">加载中...</div>
    <ul v-else-if="users.length">
      <li v-for="user in users" :key="user.id">
        {{ user.name }}
      </li>
    </ul>
    <div v-else class="empty">暂无数据</div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { fetchUsers } from '@/api/users';

// 响应式数据
const users = ref([]);
const loading = ref(false);

// 计算属性
const userCount = computed(() => users.value.length);

// 生命周期
onMounted(async () => {
  loading.value = true;
  try {
    users.value = await fetchUsers();
  } finally {
    loading.value = false;
  }
});

// 方法
const refreshUsers = async () => {
  loading.value = true;
  try {
    users.value = await fetchUsers();
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.user-list {
  padding: 16px;
}

.loading {
  text-align: center;
  color: #666;
}

.empty {
  text-align: center;
  color: #999;
}
</style>
```

#### 自定义Composition函数
```javascript
// useApi.js
import { ref, onMounted } from 'vue';

export function useApi(url, options = {}) {
  const data = ref(null);
  const loading = ref(false);
  const error = ref(null);
  
  const fetchData = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await fetch(url, options);
      data.value = await response.json();
    } catch (err) {
      error.value = err;
    } finally {
      loading.value = false;
    }
  };
  
  onMounted(fetchData);
  
  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
}

// 使用自定义Composition函数
<template>
  <div>
    <div v-if="loading">加载中...</div>
    <div v-else-if="error">{{ error.message }}</div>
    <ul v-else>
      <li v-for="user in data" :key="user.id">
        {{ user.name }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { useApi } from '@/composables/useApi';

const { data: users, loading, error } = useApi('/api/users');
</script>
```

## 性能优化策略

### React性能优化

#### 避免不必要的重渲染
```jsx
// 问题代码 - 每次渲染都创建新函数
const Parent = ({ items }) => {
  return (
    <div>
      {items.map(item => (
        <Child 
          key={item.id} 
          onClick={() => handleClick(item)} // 每次都创建新函数
        />
      ))}
    </div>
  );
};

// 优化方案1 - 使用useCallback
const Parent = ({ items }) => {
  const handleItemClick = useCallback((item) => {
    handleClick(item);
  }, []);
  
  return (
    <div>
      {items.map(item => (
        <Child 
          key={item.id} 
          onClick={() => handleItemClick(item)} // 仍然有问题
        />
      ))}
    </div>
  );
};

// 优化方案2 - 传递item ID
const Parent = ({ items }) => {
  const handleItemClick = useCallback((itemId) => {
    const item = items.find(i => i.id === itemId);
    handleClick(item);
  }, [items]);
  
  return (
    <div>
      {items.map(item => (
        <Child 
          key={item.id} 
          itemId={item.id}
          onClick={handleItemClick}
        />
      ))}
    </div>
  );
};

// 优化方案3 - 数据提升
const Parent = ({ items }) => {
  return (
    <div>
      {items.map(item => (
        <Child 
          key={item.id} 
          item={item}
          onClick={handleClick}
        />
      ))}
    </div>
  );
};
```

#### 使用React.memo
```jsx
// 组件记忆化
const ExpensiveComponent = ({ data, onAction }) => {
  const processedData = useMemo(() => {
    return expensiveDataProcessing(data);
  }, [data]);
  
  return (
    <div>
      {processedData.map(item => (
        <Item key={item.id} item={item} />
      ))}
    </div>
  );
};

// 使用React.memo
const MemoizedExpensiveComponent = React.memo(ExpensiveComponent, (prevProps, nextProps) => {
  // 自定义比较函数
  return (
    prevProps.data.length === nextProps.data.length &&
    prevProps.data.every((item, index) => item.id === nextProps.data[index]?.id)
  );
});
```

#### 虚拟化长列表
```jsx
// 使用react-window
import { FixedSizeList as List } from 'react-window';

const VirtualizedList = ({ items }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      {items[index].name}
    </div>
  );
  
  return (
    <List
      height={400}
      itemCount={items.length}
      itemSize={35}
    >
      {Row}
    </List>
  );
};
```

### Vue性能优化

#### 计算属性缓存
```vue
<template>
  <div>
    <input v-model="searchQuery" placeholder="搜索用户..." />
    <ul>
      <li v-for="user in filteredUsers" :key="user.id">
        {{ user.name }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const users = ref([]);
const searchQuery = ref('');

// 计算属性自动缓存，只有依赖变化时才重新计算
const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value;
  
  return users.value.filter(user => 
    user.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});
</script>
```

#### v-memo指令
```vue
<template>
  <div>
    <!-- 使用v-memo避免不必要的重渲染 -->
    <div v-for="item in expensiveList" :key="item.id" v-memo="[item.id, item.name]">
      <ExpensiveComponent :item="item" />
    </div>
  </div>
</template>
```

## 可访问性最佳实践

### 语义化HTML
```jsx
// 语义化组件
const Article = ({ title, content, author, publishDate }) => {
  return (
    <article aria-labelledby="article-title">
      <header>
        <h1 id="article-title">{title}</h1>
        <div className="article-meta">
          <time dateTime={publishDate}>
            {new Date(publishDate).toLocaleDateString()}
          </time>
          <address>
            作者: <span className="author">{author}</span>
          </address>
        </div>
      </header>
      <main>
        {content}
      </main>
    </article>
  );
};
```

### ARIA属性使用
```jsx
const Button = ({ children, onClick, variant = 'primary', disabled = false }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
      aria-disabled={disabled}
      aria-label={typeof children === 'string' ? children : undefined}
      role="button"
    >
      {children}
    </button>
  );
};

// 模态框组件
const Modal = ({ isOpen, onClose, title, children }) => {
  return (
    <>
      {isOpen && (
        <div 
          className="modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
        >
          <div className="modal-content">
            <header>
              <h2 id="modal-title">{title}</h2>
              <button 
                onClick={onClose}
                aria-label="关闭对话框"
                className="close-button"
              >
                ×
              </button>
            </header>
            <main>
              {children}
            </main>
          </div>
        </div>
      )}
    </>
  );
};
```

### 键盘导航支持
```jsx
const Menu = ({ items, onSelect }) => {
  const [focusedIndex, setFocusedIndex] = useState(-1);
  
  const handleKeyDown = (event) => {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setFocusedIndex(prev => 
          prev < items.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        event.preventDefault();
        setFocusedIndex(prev => 
          prev > 0 ? prev - 1 : items.length - 1
        );
        break;
      case 'Enter':
      case ' ':
        if (focusedIndex >= 0) {
          onSelect(items[focusedIndex]);
        }
        break;
      case 'Escape':
        setFocusedIndex(-1);
        break;
    }
  };
  
  return (
    <ul 
      className="menu"
      onKeyDown={handleKeyDown}
      role="menu"
    >
      {items.map((item, index) => (
        <li
          key={item.id}
          className={focusedIndex === index ? 'focused' : ''}
          role="menuitem"
          tabIndex={focusedIndex === index ? 0 : -1}
          onClick={() => onSelect(item)}
        >
          {item.label}
        </li>
      ))}
    </ul>
  );
};
```

## 测试策略

### React Testing Library最佳实践

#### 组件渲染测试
```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import UserList from '../UserList';

describe('UserList', () => {
  const mockUsers = [
    { id: 1, name: '张三' },
    { id: 2, name: '李四' }
  ];
  
  test('应该正确渲染用户列表', () => {
    render(<UserList users={mockUsers} />);
    
    expect(screen.getByText('张三')).toBeInTheDocument();
    expect(screen.getByText('李四')).toBeInTheDocument();
  });
  
  test('应该显示加载状态', () => {
    render(<UserList users={[]} isLoading={true} />);
    
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });
  
  test('应该处理用户点击', async () => {
    const onUserClick = jest.fn();
    render(<UserList users={mockUsers} onUserClick={onUserClick} />);
    
    fireEvent.click(screen.getByText('张三'));
    
    await waitFor(() => {
      expect(onUserClick).toHaveBeenCalledWith(mockUsers[0]);
    });
  });
});
```

#### 自定义Hook测试
```jsx
import { renderHook, act } from '@testing-library/react';
import { useApi } from '../useApi';

// Mock fetch
global.fetch = jest.fn();

describe('useApi', () => {
  beforeEach(() => {
    fetch.mockClear();
  });
  
  test('应该正确获取数据', async () => {
    const mockData = { users: [] };
    fetch.mockResolvedValueOnce({
      json: () => Promise.resolve(mockData)
    });
    
    const { result } = renderHook(() => useApi('/api/users'));
    
    expect(result.current.loading).toBe(true);
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toEqual(mockData);
  });
});
```

### Vue测试最佳实践

#### 组件测试
```javascript
import { mount } from '@vue/test-utils';
import UserList from '../UserList.vue';

describe('UserList.vue', () => {
  const mockUsers = [
    { id: 1, name: '张三' },
    { id: 2, name: '李四' }
  ];
  
  test('应该正确渲染用户列表', () => {
    const wrapper = mount(UserList, {
      props: { users: mockUsers }
    });
    
    expect(wrapper.text()).toContain('张三');
    expect(wrapper.text()).toContain('李四');
  });
  
  test('应该处理用户点击', async () => {
    const wrapper = mount(UserList, {
      props: { users: mockUsers }
    });
    
    await wrapper.find('[data-test="user-item"]').trigger('click');
    
    expect(wrapper.emitted('user-click')).toBeTruthy();
    expect(wrapper.emitted('user-click')[0]).toEqual([mockUsers[0]]);
  });
});
```

## 代码质量检查

### ESLint配置

#### React项目配置
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "plugins": ["react", "react-hooks"],
  "rules": {
    "react/prop-types": "error",
    "react/jsx-uses-react": "error",
    "react/jsx-uses-vars": "error",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "no-unused-vars": "error",
    "no-console": "warn"
  }
}
```

#### Vue项目配置
```json
{
  "extends": [
    "plugin:vue/vue3-recommended",
    "eslint:recommended"
  ],
  "plugins": ["vue"],
  "rules": {
    "vue/multi-word-component-names": "error",
    "vue/no-unused-components": "error",
    "vue/no-unused-vars": "error",
    "vue/require-default-prop": "error",
    "vue/no-mutating-props": "error"
  }
}
```

### TypeScript配置

#### 严格类型检查
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noImplicitThis": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true
  }
}
```

## 常见问题和解决方案

### 性能问题

#### 问题1: 不必要的重渲染
```jsx
// 问题代码
const Parent = ({ items }) => {
  return (
    <div>
      {items.map(item => (
        <Child key={item.id} onClick={() => handleAction(item)} />
      ))}
    </div>
  );
};

// 解决方案
const Parent = ({ items }) => {
  const handleAction = useCallback((item) => {
    // 处理逻辑
  }, []);
  
  return (
    <div>
      {items.map(item => (
        <Child key={item.id} item={item} onAction={handleAction} />
      ))}
    </div>
  );
};
```

#### 问题2: 大列表渲染性能
```jsx
// 问题代码
const LongList = ({ items }) => {
  return (
    <div>
      {items.map(item => (
        <Item key={item.id} item={item} />
      ))}
    </div>
  );
};

// 解决方案 - 使用虚拟化
import { FixedSizeList as List } from 'react-window';

const VirtualizedList = ({ items }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <Item item={items[index]} />
    </div>
  );
  
  return (
    <List
      height={400}
      itemCount={items.length}
      itemSize={50}
    >
      {Row}
    </List>
  );
};
```

### 可访问性问题

#### 问题1: 缺少语义化
```jsx
// 问题代码
const Card = ({ title, content }) => {
  return (
    <div>
      <div className="title">{title}</div>
      <div className="content">{content}</div>
    </div>
  );
};

// 解决方案
const Card = ({ title, content }) => {
  return (
    <article>
      <header>
        <h2>{title}</h2>
      </header>
      <main>{content}</main>
    </article>
  );
};
```

#### 问题2: 缺少键盘导航
```jsx
// 问题代码
const Dropdown = ({ options, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>
        选择
      </button>
      {isOpen && (
        <ul>
          {options.map(option => (
            <li key={option.value} onClick={() => onSelect(option)}>
              {option.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

// 解决方案
const Dropdown = ({ options, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  
  const handleKeyDown = (event) => {
    // 键盘导航逻辑
  };
  
  return (
    <div onKeyDown={handleKeyDown}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        选择
      </button>
      {isOpen && (
        <ul role="listbox">
          {options.map((option, index) => (
            <li
              key={option.value}
              role="option"
              tabIndex={focusedIndex === index ? 0 : -1}
              onClick={() => onSelect(option)}
            >
              {option.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
```

## 参考资源

### 官方文档
- [React Documentation](https://reactjs.org/docs/)
- [Vue Documentation](https://vuejs.org/guide/)
- [Angular Documentation](https://angular.io/docs)
- [Web Components MDN](https://developer.mozilla.org/en-US/docs/Web/Web_Components)

### 最佳实践指南
- [React Best Practices](https://reactjs.org/docs/thinking-in-react.html)
- [Vue Style Guide](https://vuejs.org/style-guide/)
- [Angular Style Guide](https://angular.io/guide/styleguide)

### 测试资源
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Vue Test Utils](https://vue-test-utils.vuejs.org/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)

### 性能优化
- [React Performance](https://reactjs.org/docs/optimizing-performance.html)
- [Vue Performance](https://vuejs.org/guide/performance.html)
- [Web Performance Best Practices](https://web.dev/performance/)
