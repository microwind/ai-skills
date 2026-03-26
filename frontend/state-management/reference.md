# 状态管理技术参考

## 概述

状态管理是现代前端应用的核心概念，本文档详细介绍了各种状态管理方案的设计模式、最佳实践、性能优化和实际应用案例。

## 核心概念

### 状态管理基础
- **状态**: 应用在特定时间点的数据快照
- **不可变性**: 状态不能直接修改，只能通过action更新
- **单向数据流**: 数据从状态流向视图，用户操作触发action更新状态
- **时间旅行**: 能够回溯和重放状态变化

### 状态管理原则
- **单一数据源**: 整个应用的状态存储在单一store中
- **状态只读**: 唯一修改状态的方式是触发action
- **纯函数修改**: 使用纯函数来执行状态修改

## Redux Toolkit详解

### Store配置
```javascript
import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import userSlice from './slices/userSlice';
import apiSlice from './api/apiSlice';

const store = configureStore({
  reducer: {
    user: userSlice,
    api: apiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }).concat(apiSlice.middleware),
  devTools: process.env.NODE_ENV !== 'production',
});

setupListeners(store.dispatch);

export default store;
```

### Slice创建
```javascript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// 异步thunk
export const fetchUser = createAsyncThunk(
  'user/fetchUser',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/users/${userId}`);
      return response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// 用户slice
const userSlice = createSlice({
  name: 'user',
  initialState: {
    currentUser: null,
    loading: false,
    error: null,
  },
  reducers: {
    setUser: (state, action) => {
      state.currentUser = action.payload;
    },
    clearUser: (state) => {
      state.currentUser = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.loading = false;
        state.currentUser = action.payload;
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { setUser, clearUser } = userSlice.actions;
export default userSlice.reducer;
```

### RTK Query
```javascript
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api',
    prepareHeaders: (headers, { getState }) => {
      const token = getState().auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['User', 'Post'],
  endpoints: (builder) => ({
    getUsers: builder.query({
      query: () => 'users',
      providesTags: ['User'],
    }),
    createUser: builder.mutation({
      query: (userData) => ({
        url: 'users',
        method: 'POST',
        body: userData,
      }),
      invalidatesTags: ['User'],
    }),
    updateUser: builder.mutation({
      query: ({ id, ...userData }) => ({
        url: `users/${id}`,
        method: 'PUT',
        body: userData,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'User', id }],
    }),
  }),
});

export const {
  useGetUsersQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
} = apiSlice;
```

## Zustand详解

### 基础Store
```javascript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// 基础store
const useUserStore = create(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        loading: false,
        error: null,
        
        // Actions
        setUser: (user) => set({ user }),
        clearUser: () => set({ user: null }),
        
        // 异步actions
        fetchUser: async (userId) => {
          set({ loading: true, error: null });
          try {
            const response = await fetch(`/api/users/${userId}`);
            const user = await response.json();
            set({ user, loading: false });
          } catch (error) {
            set({ error: error.message, loading: false });
          }
        },
        
        // Computed values
        isAuthenticated: () => {
          const { user } = get();
          return !!user;
        },
      }),
      {
        name: 'user-store',
        partialize: (state) => ({ user: state.user }),
      }
    )
  )
);

export default useUserStore;
```

### 高级模式
```javascript
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

// 多store组合
const useAppStore = create(
  subscribeWithSelector(
    devtools(
      (set, get) => ({
        // 用户状态
        user: useUserStore.getState(),
        
        // 应用状态
        theme: 'light',
        sidebarOpen: true,
        
        // Actions
        setTheme: (theme) => set({ theme }),
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        
        // 复杂actions
        initializeApp: async () => {
          const user = JSON.parse(localStorage.getItem('user') || 'null');
          if (user) {
            set({ user });
          }
        },
        
        // 派生状态
        isDarkMode: () => {
          const { theme } = get();
          return theme === 'dark';
        },
      })
    )
  )
);

// 自定义hooks
export const useTheme = () => useAppStore((state) => state.theme);
export const useSidebar = () => useAppStore((state) => state.sidebarOpen);
export const useUser = () => useAppStore((state) => state.user);
```

### 中间件开发
```javascript
// 自定义日志中间件
const logger = (config) => (set, get, api) => config(
  (...args) => {
    console.log('  applying', args);
    set(...args);
    console.log('  new state', get());
  },
  get,
  api
);

// 性能监控中间件
const performanceMonitor = (config) => (set, get, api) => {
  const originalSet = set;
  
  return config(
    (...args) => {
      const start = performance.now();
      originalSet(...args);
      const end = performance.now();
      console.log(`State update took ${end - start} milliseconds`);
    },
    get,
    api
  );
};

// 使用中间件
const useStore = create(
  logger(
    performanceMonitor(
      devtools((set) => ({ /* state */ }))
    )
  )
);
```

## Recoil详解

### Atom配置
```javascript
import { atom, selector, atomFamily, selectorFamily } from 'recoil';

// 基础atom
export const userState = atom({
  key: 'userState',
  default: null,
});

export const themeState = atom({
  key: 'themeState',
  default: 'light',
  effects: [
    // 本地存储effect
    ({ onSet }) => {
      onSet((newValue) => {
        localStorage.setItem('theme', newValue);
      });
    },
  ],
});

// atomFamily
export const userByIdState = atomFamily({
  key: 'userByIdState',
  default: null,
});

// selector
export const isAuthenticatedState = selector({
  key: 'isAuthenticatedState',
  get: ({ get }) => {
    const user = get(userState);
    return !!user;
  },
});

// 异步selector
export const currentUserState = selector({
  key: 'currentUserState',
  get: async ({ get }) => {
    const userId = get(currentUserIdState);
    if (!userId) return null;
    
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
  },
});

// selectorFamily
export const userPostsState = selectorFamily({
  key: 'userPostsState',
  get: (userId) => async ({ get }) => {
    const response = await fetch(`/api/users/${userId}/posts`);
    return response.json();
  },
});
```

### 高级模式
```javascript
// atomWithReset
export const searchState = atomWithReset({
  key: 'searchState',
  default: {
    query: '',
    filters: {},
    sortBy: 'relevance',
  },
});

// atomWithStorage
export const preferencesState = atomWithStorage({
  key: 'preferencesState',
  default: {
    language: 'en',
    notifications: true,
    autoSave: true,
  },
  storage: localStorage,
});

// 异步atom
export const asyncUserState = atom({
  key: 'asyncUserState',
  default: null,
  effects: [
    async ({ setSelf, onSet }) => {
      // 初始化时获取数据
      const user = await fetchCurrentUser();
      setSelf(user);
      
      // 监听变化
      onSet(async (newValue) => {
        if (newValue) {
          await updateUser(newValue);
        }
      });
    },
  ],
});
```

## MobX详解

### Observable状态
```javascript
import { makeObservable, observable, action, computed, flow, autorun } from 'mobx';

class UserStore {
  user = null;
  loading = false;
  error = null;
  posts = [];

  constructor() {
    makeObservable(this, {
      user: observable,
      loading: observable,
      error: observable,
      posts: observable,
      
      setUser: action,
      setLoading: action,
      setError: action,
      clearError: action,
      
      fetchUser: flow,
      fetchUserPosts: flow,
      
      isAuthenticated: computed,
      displayName: computed,
      postCount: computed,
    });
  }

  // Actions
  setUser(user) {
    this.user = user;
  }

  setLoading(loading) {
    this.loading = loading;
  }

  setError(error) {
    this.error = error;
  }

  clearError() {
    this.error = null;
  }

  // 异步actions
  *fetchUser(userId) {
    this.setLoading(true);
    this.clearError();
    
    try {
      const response = yield fetch(`/api/users/${userId}`);
      const user = yield response.json();
      this.setUser(user);
    } catch (error) {
      this.setError(error.message);
    } finally {
      this.setLoading(false);
    }
  }

  *fetchUserPosts(userId) {
    try {
      const response = yield fetch(`/api/users/${userId}/posts`);
      const posts = yield response.json();
      this.posts = posts;
    } catch (error) {
      this.setError(error.message);
    }
  }

  // Computed
  get isAuthenticated() {
    return !!this.user;
  }

  get displayName() {
    return this.user ? `${this.user.firstName} ${this.user.lastName}` : 'Guest';
  }

  get postCount() {
    return this.posts.length;
  }
}

export default UserStore;
```

### Reaction和Autorun
```javascript
import { reaction, autorun, when } from 'mobx';

// Reaction - 监听特定状态变化
const disposeReaction = reaction(
  () => userStore.isAuthenticated,
  (isAuthenticated, previousIsAuthenticated) => {
    if (isAuthenticated && !previousIsAuthenticated) {
      console.log('User just logged in');
      // 触发登录后的操作
    } else if (!isAuthenticated && previousIsAuthenticated) {
      console.log('User just logged out');
      // 触发登出后的操作
    }
  }
);

// Autorun - 自动执行副作用
const disposeAutorun = autorun(() => {
  if (userStore.user) {
    console.log(`Current user: ${userStore.displayName}`);
    // 自动保存用户状态
    localStorage.setItem('user', JSON.stringify(userStore.user));
  }
});

// When - 条件触发
const disposeWhen = when(
  () => userStore.isAuthenticated,
  () => {
    console.log('User is authenticated, loading user data...');
    userStore.fetchUserPosts(userStore.user.id);
  }
);

// 清理
// disposeReaction();
// disposeAutorun();
// disposeWhen();
```

### 高级模式
```javascript
import { observable, action, computed, decorate } from 'mobx';

// 使用装饰器
class TodoStore {
  @observable todos = [];
  @observable filter = 'all';

  @computed get filteredTodos() {
    switch (this.filter) {
      case 'completed':
        return this.todos.filter(todo => todo.completed);
      case 'active':
        return this.todos.filter(todo => !todo.completed);
      default:
        return this.todos;
    }
  }

  @computed get completedCount() {
    return this.todos.filter(todo => todo.completed).length;
  }

  @computed get activeCount() {
    return this.todos.filter(todo => !todo.completed).length;
  }

  @action addTodo(text) {
    this.todos.push({
      id: Date.now(),
      text,
      completed: false,
    });
  }

  @action toggleTodo(id) {
    const todo = this.todos.find(todo => todo.id === id);
    if (todo) {
      todo.completed = !todo.completed;
    }
  }

  @action setFilter(filter) {
    this.filter = filter;
  }
}

// 使用makeAutoObservable (MobX 6+)
class CounterStore {
  count = 0;

  constructor() {
    makeAutoObservable(this);
  }

  increment() {
    this.count++;
  }

  decrement() {
    this.count--;
  }

  get doubled() {
    return this.count * 2;
  }
}
```

## 性能优化

### Redux性能优化
```javascript
// 使用reselect进行记忆化
import { createSelector } from '@reduxjs/toolkit';

const selectUserState = (state) => state.user;
const selectPostsState = (state) => state.posts;

// 记忆化选择器
export const selectCurrentUser = createSelector(
  [selectUserState],
  (user) => user.currentUser
);

export const selectUserPosts = createSelector(
  [selectPostsState, selectCurrentUser],
  (posts, currentUser) => {
    if (!currentUser) return [];
    return posts.posts.filter(post => post.userId === currentUser.id);
  }
);

// 参数化选择器
export const selectPostById = createSelector(
  [selectPostsState, (state, postId) => postId],
  (posts, postId) => posts.posts.find(post => post.id === postId)
);

// 使用RTK Query的缓存
export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api',
  }),
  tagTypes: ['Post', 'User'],
  endpoints: (builder) => ({
    getPosts: builder.query({
      query: () => 'posts',
      providesTags: ['Post'],
      keepUnusedDataFor: 60, // 缓存60秒
    }),
  }),
});
```

### Zustand性能优化
```javascript
import { shallow } from 'zustand/shallow';

// 选择性订阅
const useUser = () => useUserStore((state) => state.user);
const useUserActions = () => useUserStore((state) => ({
  setUser: state.setUser,
  clearUser: state.clearUser,
  fetchUser: state.fetchUser,
}));

// 浅比较订阅
const useUserInfo = () => useUserStore(
  (state) => ({
    name: state.user?.name,
    email: state.user?.email,
  }),
  shallow
);

// 自定义比较函数
const useUserWithCustomCompare = () => useUserStore(
  (state) => state.user,
  (prevUser, currentUser) => prevUser?.id === currentUser?.id
);

// 批量更新
const useBatchUpdate = () => {
  const setState = useUserStore.setState;
  
  return useCallback((updates) => {
    setState((state) => ({
      ...state,
      ...updates,
    }));
  }, [setState]);
};
```

### Recoil性能优化
```javascript
// 使用selector的缓存策略
export const expensiveSelectorState = selector({
  key: 'expensiveSelectorState',
  get: ({ get }) => {
    const data = get(largeDataState);
    return expensiveComputation(data);
  },
  cachePolicy_UNSTABLE: {
    eviction: 'most-recent',
  },
});

// 使用atomFamily的缓存
export const userCacheState = atomFamily({
  key: 'userCacheState',
  default: null,
  cachePolicy_UNSTABLE: {
    eviction: 'keep-all',
  },
});

// 异步selector的错误处理和重试
export const robustAsyncState = selector({
  key: 'robustAsyncState',
  get: async ({ get }) => {
    let retries = 3;
    while (retries > 0) {
      try {
        const response = await fetch('/api/data');
        return response.json();
      } catch (error) {
        retries--;
        if (retries === 0) throw error;
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  },
});
```

## 测试策略

### Redux测试
```javascript
import { configureStore } from '@reduxjs/toolkit';
import userReducer, { fetchUser, setUser } from './userSlice';

// 测试reducer
describe('user reducer', () => {
  const initialState = {
    currentUser: null,
    loading: false,
    error: null,
  };

  test('should handle initial state', () => {
    expect(userReducer(undefined, { type: 'unknown' })).toEqual(initialState);
  });

  test('should handle setUser', () => {
    const user = { id: 1, name: 'John' };
    const actual = userReducer(initialState, setUser(user));
    expect(actual.currentUser).toEqual(user);
  });

  test('should handle fetchUser.pending', () => {
    const actual = userReducer(initialState, fetchUser.pending());
    expect(actual.loading).toBe(true);
    expect(actual.error).toBe(null);
  });

  test('should handle fetchUser.fulfilled', () => {
    const user = { id: 1, name: 'John' };
    const actual = userReducer(
      { ...initialState, loading: true },
      fetchUser.fulfilled(user)
    );
    expect(actual.loading).toBe(false);
    expect(actual.currentUser).toEqual(user);
  });
});

// 测试store
describe('user store', () => {
  let store;

  beforeEach(() => {
    store = configureStore({
      reducer: {
        user: userReducer,
      },
    });
  });

  test('should dispatch fetchUser and update state', async () => {
    const mockUser = { id: 1, name: 'John' };
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve(mockUser),
      })
    );

    await store.dispatch(fetchUser(1));

    const state = store.getState();
    expect(state.user.currentUser).toEqual(mockUser);
    expect(state.user.loading).toBe(false);
  });
});
```

### Zustand测试
```javascript
import { act } from '@testing-library/react';
import useUserStore from './userStore';

// 测试store actions
describe('useUserStore', () => {
  beforeEach(() => {
    useUserStore.setState({
      user: null,
      loading: false,
      error: null,
    });
  });

  test('should set user', () => {
    const user = { id: 1, name: 'John' };
    
    act(() => {
      useUserStore.getState().setUser(user);
    });

    const state = useUserStore.getState();
    expect(state.user).toEqual(user);
  });

  test('should fetch user', async () => {
    const mockUser = { id: 1, name: 'John' };
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve(mockUser),
      })
    );

    await act(async () => {
      await useUserStore.getState().fetchUser(1);
    });

    const state = useUserStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.loading).toBe(false);
  });

  test('should handle fetch error', async () => {
    global.fetch = jest.fn(() =>
      Promise.reject(new Error('Network error'))
    );

    await act(async () => {
      await useUserStore.getState().fetchUser(1);
    });

    const state = useUserStore.getState();
    expect(state.error).toBe('Network error');
    expect(state.loading).toBe(false);
  });
});
```

## 最佳实践

### 状态设计原则
1. **保持状态扁平化**: 避免深度嵌套的状态结构
2. **单一数据源**: 相关状态应该集中管理
3. **不可变更新**: 始终返回新的状态对象
4. **状态规范化**: 使用ID映射表管理集合数据

### 性能优化建议
1. **选择性订阅**: 只订阅需要的状态片段
2. **记忆化计算**: 缓存昂贵的计算结果
3. **批量更新**: 合并多个状态更新操作
4. **懒加载**: 按需加载状态模块

### 代码组织
```javascript
// 推荐的目录结构
src/
├── store/
│   ├── index.js          # Store配置
│   ├── slices/           # Redux slices
│   │   ├── userSlice.js
│   │   └── postsSlice.js
│   ├── api/              # RTK Query APIs
│   │   └── userApi.js
│   ├── selectors/        # 全局选择器
│   │   └── userSelectors.js
│   └── middleware/       # 自定义中间件
│       └── logger.js
├── hooks/                # 自定义hooks
│   ├── useUser.js
│   └── useTheme.js
└── components/           # React组件
    └── UserCard.js
```

## 相关资源

### 官方文档
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [Zustand](https://github.com/pmndrs/zustand)
- [Recoil](https://recoiljs.org/)
- [MobX](https://mobx.js.org/)

### 工具和库
- [Redux DevTools](https://github.com/reduxjs/redux-devtools)
- [Reactotron](https://github.com/infinitered/reactotron)
- [Immer](https://immerjs.github.io/immer/)
- [Reselect](https://github.com/reduxjs/reselect)

### 学习资源
- [Redux Style Guide](https://redux.js.org/style-guide/style-guide)
- [Zustand Documentation](https://docs.pmnd.rs/zustand/getting-started/introduction)
- [Recoil Guide](https://recoiljs.org/docs/introduction/getting-started)
- [MobX Documentation](https://mobx.js.org/README.html)

### 社区资源
- [Reactiflux Discord](https://discord.gg/reactiflux)
- [Reddit r/reactjs](https://www.reddit.com/r/reactjs/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/redux)
- [GitHub Discussions](https://github.com/reduxjs/redux/discussions)
