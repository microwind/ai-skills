# Claude Code 实战指南

> 专注实战场景，提升开发效率的实用指南

## 快速开始

Claude Code 是 Anthropic 推出的 AI 编程助手，通过自然语言对话帮你完成代码编写、调试、优化等任务。

### 基本使用

```bash
# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 基础对话
claude "帮我写一个快速排序算法"

# 分析特定文件
claude --file src/utils/sort.js

# 后台运行耗时任务
claude --background "运行完整测试套件"
```

---

## 实战场景

### 场景 1：快速原型开发

**需求**：2小时内完成一个产品展示页面

```bash
claude "
用 React + Tailwind CSS 创建产品展示页面：
- 响应式网格布局
- 产品卡片（图片、标题、价格、评分）
- 搜索和筛选功能
- 购物车功能
- 使用 TypeScript
"
```

**Claude 输出**：
```typescript
// ProductCard.tsx
interface Product {
  id: string;
  title: string;
  price: number;
  image: string;
  rating: number;
}

export const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow">
      <img src={product.image} alt={product.title} className="w-full h-48 object-cover" />
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2">{product.title}</h3>
        <div className="flex justify-between items-center">
          <span className="text-2xl font-bold text-blue-600">${product.price}</span>
          <div className="flex items-center">
            <span className="text-yellow-400">{'★'.repeat(Math.floor(product.rating))}</span>
            <span className="text-gray-400">{'★'.repeat(5 - Math.floor(product.rating))}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
```

**后续优化**：
```bash
claude "添加图片懒加载和加载动画"
claude "实现价格筛选和评分排序"
```

---

### 场景 2：Bug 快速修复

**问题**：用户反馈登录后页面闪白

```bash
claude "
React 应用登录后页面会闪一下才显示内容。
相关文件：
- src/hooks/useAuth.ts
- src/pages/Dashboard.tsx

帮我定位问题并提供修复方案。
"
```

**问题诊断**：
```typescript
// 问题代码
export const Dashboard = () => {
  const { user } = useAuth();
  
  // 问题：user 可能为 undefined，导致闪白
  return <h1>欢迎, {user.name}</h1>;
};

// 修复方案
export const Dashboard = () => {
  const { user, isLoading } = useAuth();
  
  if (isLoading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" />;
  
  return <h1>欢迎, {user.name}</h1>;
};
```

---

### 场景 3：API 接口开发

**需求**：开发用户管理 REST API

```bash
claude "
用 Express.js 开发用户管理 API：
- GET /api/users - 获取用户列表
- GET /api/users/:id - 获取单个用户
- POST /api/users - 创建用户
- PUT /api/users/:id - 更新用户
- DELETE /api/users/:id - 删除用户
- 使用 MongoDB + Mongoose
- 包含输入验证和错误处理
- 添加 JWT 认证中间件
"
```

**核心代码生成**：
```typescript
// users.controller.ts
export class UsersController {
  async getUsers(req: Request, res: Response) {
    try {
      const { page = 1, limit = 10, search } = req.query;
      const filter = search ? { name: { $regex: search, $options: 'i' } } : {};
      
      const users = await User.find(filter)
        .limit(Number(limit))
        .skip((Number(page) - 1) * Number(limit));
      
      res.json({
        success: true,
        data: users,
        total: await User.countDocuments(filter)
      });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  }

  async createUser(req: Request, res: Response) {
    try {
      const { name, email, password } = req.body;
      
      // 验证
      if (!name || !email || !password) {
        return res.status(400).json({ 
          success: false, 
          error: '缺少必填字段' 
        });
      }
      
      const user = new User({ name, email, password });
      await user.save();
      
      res.status(201).json({ success: true, data: user });
    } catch (error) {
      if (error.code === 11000) {
        return res.status(400).json({ 
          success: false, 
          error: '邮箱已存在' 
        });
      }
      res.status(500).json({ success: false, error: error.message });
    }
  }
}
```

---

### 场景 4：测试用例生成

**需求**：为购物车功能编写完整测试

```bash
claude "
为购物车服务生成全面的单元测试：
src/services/CartService.ts

要求：
- 覆盖所有 CRUD 操作
- 包含边界情况测试
- 性能测试（1000+ 商品）
- 使用 Jest
"
```

**测试代码**：
```typescript
// CartService.test.ts
describe('CartService', () => {
  let cartService: CartService;

  beforeEach(() => {
    cartService = new CartService();
  });

  describe('addItem', () => {
    test('应该能添加商品到空购物车', () => {
      cartService.addItem('PROD-001', 2);
      expect(cartService.getItems()).toHaveLength(1);
      expect(cartService.getItems()[0].quantity).toBe(2);
    });

    test('应该能增加已存在商品的数量', () => {
      cartService.addItem('PROD-001', 2);
      cartService.addItem('PROD-001', 3);
      expect(cartService.getItems()[0].quantity).toBe(5);
    });

    test('应该拒绝无效数量', () => {
      expect(() => cartService.addItem('PROD-001', -1))
        .toThrow('数量必须大于0');
      expect(() => cartService.addItem('PROD-001', 0))
        .toThrow('数量必须大于0');
    });
  });

  describe('calculateTotal', () => {
    test('应该正确计算总价', () => {
      cartService.addItem('PROD-001', 2, 10); // $20
      cartService.addItem('PROD-002', 1, 30); // $30
      expect(cartService.calculateTotal()).toBe(50);
    });

    test('空购物车应该返回0', () => {
      expect(cartService.calculateTotal()).toBe(0);
    });
  });

  describe('performance', () => {
    test('应该能处理大量商品', () => {
      const start = performance.now();
      
      for (let i = 0; i < 1000; i++) {
        cartService.addItem(`PROD-${i}`, 1, Math.random() * 100);
      }
      
      const end = performance.now();
      expect(end - start).toBeLessThan(100); // 100ms 内完成
    });
  });
});
```

---

### 场景 5：代码重构优化

**需求**：优化遗留代码性能

```bash
claude "
分析并优化这个函数的性能问题：

function findDuplicates(arr) {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j] && !duplicates.includes(arr[i])) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}

要求：
1. 分析时间复杂度
2. 提供优化方案
3. 对比性能差异
4. 添加类型定义
"
```

**优化结果**：
```typescript
// 原始版本：O(n²)
function findDuplicatesNaive<T>(arr: T[]): T[] {
  const duplicates: T[] = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j] && !duplicates.includes(arr[i])) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}

// 优化版本：O(n)
function findDuplicatesOptimized<T>(arr: T[]): T[] {
  const seen = new Set<T>();
  const duplicates = new Set<T>();
  
  for (const item of arr) {
    if (seen.has(item)) {
      duplicates.add(item);
    } else {
      seen.add(item);
    }
  }
  
  return Array.from(duplicates);
}

// 性能测试
const testArray = Array.from({ length: 10000 }, (_, i) => i % 1000);

console.time('Naive');
findDuplicatesNaive(testArray);
console.timeEnd('Naive'); // ~200ms

console.time('Optimized');
findDuplicatesOptimized(testArray);
console.timeEnd('Optimized'); // ~2ms
```

---

### 场景 6：全栈 Web 应用开发

**需求**：构建一个完整的任务管理系统

```bash
claude "
帮我构建一个全栈任务管理系统：

前端要求：
- React + TypeScript + Vite
- 使用 Tailwind CSS
- 包含登录/注册页面
- 任务列表（增删改查）
- 拖拽排序功能
- 实时更新

后端要求：
- Node.js + Express + TypeScript
- PostgreSQL 数据库
- JWT 认证
- Socket.io 实时通信
- RESTful API 设计

部署要求：
- Docker 容器化
- docker-compose 一键启动
- 包含环境变量配置
"
```

**项目结构生成**：
```
task-manager/
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── components/      # 组件
│   │   ├── pages/          # 页面
│   │   ├── hooks/          # 自定义 hooks
│   │   ├── services/       # API 服务
│   │   └── types/          # TypeScript 类型
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # Node.js 后端
│   ├── src/
│   │   ├── controllers/    # 控制器
│   │   ├── middleware/     # 中间件
│   │   ├── models/         # 数据模型
│   │   ├── routes/         # 路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml       # Docker 编排
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

**核心功能实现**：

```typescript
// 前端：TaskList 组件
import { useQuery, useMutation } from '@tanstack/react-query';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

export const TaskList: React.FC = () => {
  const { data: tasks, refetch } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => taskService.getTasks()
  });

  const updateTaskOrder = useMutation({
    mutationFn: taskService.updateTaskOrder,
    onSuccess: () => refetch()
  });

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;
    
    const items = Array.from(tasks || []);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    
    updateTaskOrder.mutate(items);
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <Droppable droppableId="tasks">
        {(provided) => (
          <div {...provided.droppableProps} ref={provided.innerRef}>
            {tasks?.map((task, index) => (
              <Draggable key={task.id} draggableId={task.id} index={index}>
                {(provided) => (
                  <TaskItem 
                    task={task} 
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    {...provided.dragHandleProps}
                  />
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </DragDropContext>
  );
};
```

```typescript
// 后端：Socket.io 实时更新
import { Server } from 'socket.io';
import { TaskService } from './services/TaskService';

export const initializeSocket = (httpServer: any) => {
  const io = new Server(httpServer, {
    cors: { origin: process.env.FRONTEND_URL }
  });

  io.on('connection', (socket) => {
    console.log('用户连接:', socket.id);

    socket.on('join-room', (roomId: string) => {
      socket.join(roomId);
    });

    socket.on('task-updated', async (data) => {
      await TaskService.updateTask(data.taskId, data.updates);
      
      // 广播更新给房间内所有用户
      socket.to(data.roomId).emit('task-update', {
        taskId: data.taskId,
        updates: data.updates
      });
    });
  });

  return io;
};
```

**Docker 配置**：
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/taskmanager
      JWT_SECRET: your-secret-key
    depends_on:
      - postgres
    volumes:
      - ./backend:/app
      - /app/node_modules

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

### 场景 7：移动应用开发

**需求**：跨平台任务管理 App

```bash
claude "
使用 React Native + Expo 开发移动应用：

功能要求：
- 跨平台（iOS/Android）
- 离线优先设计
- 推送通知
- 生物识别认证
- 手势操作（滑动删除、长按菜单）
- 深色模式支持

技术要求：
- Expo SDK 50+
- TypeScript
- React Navigation 6
- AsyncStorage 本地存储
- Expo Notifications
- React Query 数据管理
"
```

**核心实现**：

```typescript
// App.tsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';

const Stack = createNativeStackNavigator();
const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <NavigationContainer>
            <Stack.Navigator>
              <Stack.Screen name="Login" component={LoginScreen} />
              <Stack.Screen name="Tasks" component={TaskListScreen} />
              <Stack.Screen name="TaskDetail" component={TaskDetailScreen} />
            </Stack.Navigator>
          </NavigationContainer>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
```

```typescript
// 离线优先的数据同步
import { useQuery, useMutation } from '@tanstack/react-query';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

export const useOfflineTasks = () => {
  const { data: onlineTasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: taskService.getTasks,
    enabled: false // 默认禁用，根据网络状态启用
  });

  const syncTasks = async () => {
    const netInfo = await NetInfo.fetch();
    if (netInfo.isConnected) {
      // 在线时同步数据
      const offlineTasks = await AsyncStorage.getItem('offlineTasks');
      if (offlineTasks) {
        await taskService.syncTasks(JSON.parse(offlineTasks));
        await AsyncStorage.removeItem('offlineTasks');
      }
    }
  };

  const createTaskOffline = useMutation({
    mutationFn: async (task: Task) => {
      const netInfo = await NetInfo.fetch();
      
      if (netInfo.isConnected) {
        return taskService.createTask(task);
      } else {
        // 离线时存储到本地
        const existingTasks = await AsyncStorage.getItem('offlineTasks');
        const tasks = existingTasks ? JSON.parse(existingTasks) : [];
        tasks.push({ ...task, id: Date.now().toString(), pending: true });
        await AsyncStorage.setItem('offlineTasks', JSON.stringify(tasks));
        return task;
      }
    },
    onSuccess: () => syncTasks()
  });

  return { createTaskOffline };
};
```

---

### 场景 8：微服务架构设计

**需求**：设计可扩展的电商系统

```bash
claude "
设计微服务架构的电商系统：

服务拆分：
- 用户服务（注册、登录、个人信息）
- 商品服务（商品管理、库存、分类）
- 订单服务（订单创建、状态管理）
- 支付服务（支付处理、退款）
- 通知服务（邮件、短信、推送）

技术要求：
- Node.js + NestJS 框架
- Docker + Kubernetes 部署
- Redis 缓存
- RabbitMQ 消息队列
- PostgreSQL 数据库
- API Gateway 统一入口
- 分布式追踪（Jaeger）
- 服务发现（Consul）
"
```

**架构设计**：

```typescript
// API Gateway 配置
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import * as proxy from 'express-http-proxy';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // 全局验证管道
  app.useGlobalPipes(new ValidationPipe());
  
  // Swagger 文档
  const config = new DocumentBuilder()
    .setTitle('E-commerce API Gateway')
    .setVersion('1.0')
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document);
  
  // 微服务代理
  app.use('/api/users', proxy('http://user-service:3001'));
  app.use('/api/products', proxy('http://product-service:3002'));
  app.use('/api/orders', proxy('http://order-service:3003'));
  app.use('/api/payments', proxy('http://payment-service:3004'));
  
  await app.listen(3000);
}
```

```typescript
// 分布式事件处理
import { Controller } from '@nestjs/common';
import { EventPattern, Payload } from '@nestjs/microservices';
import { OrderService } from './order.service';

@Controller()
export class OrderController {
  constructor(private readonly orderService: OrderService) {}

  @EventPattern('order_created')
  async handleOrderCreated(@Payload() data: any) {
    // 处理订单创建事件
    await this.orderService.processOrder(data);
    
    // 发布库存扣减事件
    await this.orderService.publishEvent('inventory_reserved', {
      productId: data.productId,
      quantity: data.quantity,
      orderId: data.orderId
    });
  }

  @EventPattern('payment_completed')
  async handlePaymentCompleted(@Payload() data: any) {
    // 支付完成，更新订单状态
    await this.orderService.updateOrderStatus(data.orderId, 'PAID');
    
    // 发布发货通知事件
    await this.orderService.publishEvent('order_shipped', {
      orderId: data.orderId,
      userId: data.userId
    });
  }
}
```

**Kubernetes 部署**：
```yaml
# k8s/user-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:latest
        ports:
        - containerPort: 3001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - port: 3001
    targetPort: 3001
```

---

### 场景 9：AI 驱动的智能系统

**需求**：构建智能客服系统

```bash
claude "
构建 AI 智能客服系统：

核心功能：
- 自然语言理解（NLU）
- 意图识别和实体提取
- 多轮对话管理
- 知识库检索
- 情感分析
- 智能路由

技术栈：
- Python + FastAPI
- LangChain 框架
- OpenAI/Claude API
- Elasticsearch 搜索
- Redis 会话存储
- WebSocket 实时通信
- React 前端界面
"
```

**智能对话引擎**：

```python
# conversation_engine.py
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import ElasticsearchStore
from typing import Dict, List

class ConversationEngine:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = ElasticsearchStore(
            es_url="http://localhost:9200",
            index_name="knowledge_base",
            embedding=self.embeddings
        )
        self.memory = ConversationBufferWindowMemory(
            k=5, 
            return_messages=True,
            memory_key="chat_history"
        )
        
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model="gpt-4"),
            retriever=self.vectorstore.as_retriever(),
            memory=self.memory,
            verbose=True
        )
    
    async def process_message(self, 
                             user_id: str, 
                             message: str) -> Dict[str, any]:
        # 意图识别
        intent = await self.detect_intent(message)
        
        # 情感分析
        sentiment = await self.analyze_sentiment(message)
        
        # 生成回复
        if intent == "complaint":
            response = await self.handle_complaint(message)
        elif intent == "inquiry":
            response = await self.chain({"question": message})
            response = response["answer"]
        else:
            response = await self.generate_general_response(message)
        
        # 保存对话历史
        await self.save_conversation(user_id, message, response)
        
        return {
            "response": response,
            "intent": intent,
            "sentiment": sentiment,
            "confidence": 0.85
        }
    
    async def detect_intent(self, message: str) -> str:
        # 使用分类模型识别意图
        intents = {
            "complaint": ["投诉", "不满", "问题", "错误"],
            "inquiry": ["查询", "怎么", "如何", "什么"],
            "greeting": ["你好", "您好", "早上好"],
            "farewell": ["再见", "谢谢", "感谢"]
        }
        
        for intent, keywords in intents.items():
            if any(keyword in message for keyword in keywords):
                return intent
        
        return "general"
```

**实时 WebSocket 通信**：

```python
# websocket_handler.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import redis

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # 加载历史对话
        history = self.redis_client.get(f"chat_history:{user_id}")
        if history:
            await websocket.send_text(json.dumps({
                "type": "history",
                "data": json.loads(history)
            }))
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    engine = ConversationEngine()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "message":
                response = await engine.process_message(
                    user_id, 
                    message["content"]
                )
                
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "data": response
                }))
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
```

---

### 场景 10：DevOps 自动化平台

**需求**：构建 CI/CD 自动化平台

```bash
claude "
构建 DevOps 自动化平台：

功能模块：
- Git 仓库管理集成
- 自动化构建和测试
- 容器镜像管理
- 部署流水线设计
- 监控和告警系统
- 日志聚合和分析

技术实现：
- Node.js + Express 后端
- React + TypeScript 前端
- Docker 容器化
- GitHub Actions CI/CD
- Prometheus + Grafana 监控
- ELK Stack 日志处理
- Kubernetes 部署
"
```

**CI/CD 流水线配置**：

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker tag myapp:${{ github.sha }} myapp:latest
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push myapp:${{ github.sha }}
          docker push myapp:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: |
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig
          
          # 更新镜像版本
          sed -i "s/myapp:latest/myapp:${{ github.sha }}/g" k8s/deployment.yaml
          
          # 应用更新
          kubectl apply -f k8s/
          
          # 等待部署完成
          kubectl rollout status deployment/myapp
```

**监控和告警系统**：

```typescript
// monitoring-service.ts
import express from 'express';
import prometheus from 'prom-client';
import { logger } from './utils/logger';

// 创建指标
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

const httpRequestTotal = new prometheus.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new prometheus.Gauge({
  name: 'websocket_connections_active',
  help: 'Number of active WebSocket connections'
});

// 中间件：收集指标
export const metricsMiddleware = (req: express.Request, res: express.Response, next: express.NextFunction) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route?.path || req.path;
    
    httpRequestDuration
      .labels(req.method, route, res.statusCode.toString())
      .observe(duration);
    
    httpRequestTotal
      .labels(req.method, route, res.statusCode.toString())
      .inc();
  });
  
  next();
};

// 告警规则
export const checkAlerts = async () => {
  const metrics = await prometheus.register.getMetricsAsJSON();
  
  // 检查错误率
  const errorRate = calculateErrorRate(metrics);
  if (errorRate > 0.05) { // 5% 错误率阈值
    await sendAlert({
      level: 'critical',
      message: `错误率过高: ${(errorRate * 100).toFixed(2)}%`,
      metric: 'error_rate',
      value: errorRate
    });
  }
  
  // 检查响应时间
  const avgResponseTime = calculateAvgResponseTime(metrics);
  if (avgResponseTime > 1000) { // 1秒阈值
    await sendAlert({
      level: 'warning',
      message: `平均响应时间过长: ${avgResponseTime}ms`,
      metric: 'response_time',
      value: avgResponseTime
    });
  }
};

// 告警发送
const sendAlert = async (alert: Alert) => {
  // 发送到 Slack
  await fetch(process.env.SLACK_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: `🚨 ${alert.level.toUpperCase()}: ${alert.message}`,
      attachments: [{
        color: alert.level === 'critical' ? 'danger' : 'warning',
        fields: [
          { title: '指标', value: alert.metric },
          { title: '当前值', value: alert.value.toString() }
        ]
      }]
    })
  });
  
  // 记录日志
  logger.warn('Alert triggered', alert);
};
```

---

## 高效工作流

### 1. 渐进式开发

```bash
# 步骤 1：定义接口
claude "设计用户管理 API 的接口规范"

# 步骤 2：实现核心逻辑
claude "基于刚才的接口规范实现后端服务"

# 步骤 3：添加测试
claude "为用户管理 API 编写单元测试"

# 步骤 4：生成文档
claude "生成 API 文档，包含示例代码"
```

### 2. 错误处理工作流

```bash
# 步骤 1：复现错误
claude "这个 API 返回 500 错误，帮我分析日志"

# 步骤 2：定位问题
claude "根据错误信息，定位可能的问题原因"

# 步骤 3：修复方案
claude "提供具体的修复代码"

# 步骤 4：预防措施
claude "添加监控和告警，防止类似问题"
```

### 4. Plan 模式工作流

先规划后执行，避免返工：

```bash
# 进入 Plan 模式（按两次 Shift+Tab）
# 详细描述需求，让 Claude 制定方案

# 方案确认后，切换回执行模式
# 使用 Auto-accept 一次性完成
```

### 5. 多 Agent 协作

复杂任务分而治之：

```bash
# 终端 1：前端 Agent
claude --session frontend "实现 React 组件"

# 终端 2：后端 Agent  
claude --session backend "开发 API 接口"

# 终端 3：测试 Agent
claude --session testing "编写测试用例"

# 主终端：协调 Agent
claude "整合前后端，确保接口对接正确"
```

---

## 实用技巧

### 1. 精准提问

**不好**：
```bash
claude "优化这个函数"
```

**好**：
```bash
claude "
优化这个函数的时间复杂度：
function processData(data) {
  return data.map(item => 
    data.find(d => d.id === item.parentId)
  );
}

当前是 O(n²)，需要优化到 O(n)
"
```

### 2. 提供上下文

**不好**：
```bash
claude "修复登录 bug"
```

**好**：
```bash
claude "
修复登录 bug：
- 使用 React + TypeScript
- 认证库：@auth0/react-auth0
- 错误信息：'Cannot read property of undefined'
- 相关文件：src/components/Login.tsx
"
```

### 3. 分步骤处理复杂任务

```bash
# 第一步：理解需求
claude "分析这个需求的技术要点：..."

# 第二步：设计方案
claude "基于刚才的分析，设计技术方案"

# 第三步：实现代码
claude "按照设计方案实现核心功能"

# 第四步：测试验证
claude "编写测试用例验证功能"
```

### 4. 使用 CLAUDE.md 配置项目

在项目根目录创建 CLAUDE.md：

```markdown
# 项目：电商系统

## 技术栈
- 前端：React 18 + TypeScript + Tailwind CSS
- 后端：Node.js + Express + MongoDB
- 部署：Docker + AWS

## 编码规范
- 使用 ESLint + Prettier
- 组件用 PascalCase
- 文件名用 kebab-case
- 提交信息遵循 Conventional Commits

## 项目结构
```
src/
  components/    # React 组件
  pages/         # 页面组件
  hooks/         # 自定义 hooks
  services/      # API 服务
  utils/         # 工具函数
  types/         # TypeScript 类型
```

## 测试策略
- 单元测试：Jest + React Testing Library
- E2E 测试：Playwright
- 测试覆盖率要求：80%+

## 部署流程
1. 推送到 main 分支触发 CI/CD
2. 自动运行测试和构建
3. 部署到 staging 环境
4. 人工验证后部署到生产
```

---

## 常见问题

### Q: Claude Code 生成的代码可靠吗？

A: Claude Code 生成的代码质量很高，但仍需要人工审查。建议：
- 重要功能一定要写测试
- 关注安全性和性能
- 逐步集成，不要一次性替换大量代码

### Q: 如何让 Claude Code 理解项目结构？

A: 提供项目上下文：
```bash
claude "
我的项目结构：
src/
  components/    # React 组件
  services/      # API 服务
  utils/         # 工具函数
  types/         # TypeScript 类型定义

技术栈：React 18 + TypeScript + Tailwind CSS
"
```

### Q: 如何处理大型项目？

A: 分模块处理：
```bash
# 先处理核心模块
claude "实现用户认证模块"

# 再处理业务模块
claude "基于认证模块实现订单系统"

# 最后集成测试
claude "编写端到端测试"
```

---

## 最佳实践

1. **明确需求**：详细描述功能需求和技术约束
2. **提供上下文**：说明项目结构、技术栈、业务背景
3. **分步进行**：复杂任务拆分为多个小步骤
4. **及时验证**：每步完成后进行测试和验证
5. **持续优化**：基于反馈不断改进代码质量

---

## 进阶使用

### 自定义工作流

创建可重复的开发流程：

```bash
# 保存常用提示词
claude --save "api-development" "
开发 REST API：
1. 设计数据模型
2. 实现控制器
3. 添加验证中间件
4. 编写单元测试
5. 生成 API 文档
"

# 使用保存的工作流
claude --load "api-development" "用户管理模块"
```

### 多文件协作

```bash
# 同时分析多个相关文件
claude --file src/auth/service.ts --file src/auth/middleware.ts "
分析认证系统的完整流程，找出潜在问题
"
```

---

## 总结

Claude Code 是强大的编程助手，关键在于：

- **精准提问**：明确需求，提供充分上下文
- **渐进开发**：分步骤处理复杂任务
- **质量把控**：人工审查 + 自动化测试
- **持续学习**：积累项目特定的最佳实践

通过合理使用 Claude Code，可以显著提升开发效率，让开发者更专注于业务逻辑和架构设计。

---

## 相关资源

- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)
- [Claude Code 从入门到精通](./Claudecode入门参考.md)
- [Claude Code 完整学习系列](./claude-code-guide/README.md)
- [AI 编程核心知识库](https://microwind.github.io)
- [Claude Code Skills 推荐](../skills/Claude-Code-10大Skills推荐.md)
- [51万行代码分析报告](./claude-code-guide/附录-最佳实践.md)
