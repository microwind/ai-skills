# Express.js服务参考文档

## Express.js框架概述

### 什么是Express.js
Express.js是Node.js最流行、最成熟的Web应用框架。它提供了简洁而强大的API来构建Web应用和API服务，通过中间件系统实现高度的可扩展性和灵活性。

### Express.js核心特性
- **极简主义**: 最小化的核心，功能通过中间件扩展
- **中间件系统**: 强大的请求处理管道
- **路由系统**: 灵活的路由定义和处理
- **HTTP工具**: 便捷的HTTP请求和响应处理
- **模板引擎支持**: 支持多种模板引擎
- **高性能**: 基于Node.js的非阻塞I/O模型

## Express应用基础架构

### 基础应用结构
```javascript
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// 基础中间件
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// 基础路由
app.get('/', (req, res) => {
    res.json({ message: 'Welcome to Express.js API' });
});

// 错误处理中间件
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

module.exports = app;
```

### 模块化应用架构
```javascript
// app.js - 主应用文件
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

// 路由模块
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const postRoutes = require('./routes/posts');

// 中间件
const errorHandler = require('./middleware/errorHandler');
const rateLimiter = require('./middleware/rateLimiter');

const app = express();

// 安全中间件
app.use(helmet());
app.use(cors());
app.use(rateLimiter);

// 日志中间件
app.use(morgan('combined'));

// 解析中间件
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// API路由
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/posts', postRoutes);

// 健康检查
app.get('/health', (req, res) => {
    res.status(200).json({ 
        status: 'OK', 
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// 404处理
app.use('*', (req, res) => {
    res.status(404).json({ error: 'Route not found' });
});

// 错误处理
app.use(errorHandler);

module.exports = app;
```

## 路由设计和实现

### RESTful API路由设计
```javascript
// routes/users.js
const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const auth = require('../middleware/auth');
const validate = require('../middleware/validate');
const { userValidation } = require('../validators/userValidator');

// GET /api/users - 获取用户列表
router.get('/', userController.getUsers);

// GET /api/users/:id - 获取单个用户
router.get('/:id', validate.id, userController.getUserById);

// POST /api/users - 创建用户
router.post('/', 
    validate(userValidation.create), 
    userController.createUser
);

// PUT /api/users/:id - 更新用户
router.put('/:id', 
    auth.authenticate,
    validate.id,
    validate(userValidation.update),
    userController.updateUser
);

// DELETE /api/users/:id - 删除用户
router.delete('/:id', 
    auth.authenticate,
    validate.id,
    userController.deleteUser
);

// PATCH /api/users/:id/profile - 更新用户资料
router.patch('/:id/profile', 
    auth.authenticate,
    validate.id,
    validate(userValidation.updateProfile),
    userController.updateProfile
);

module.exports = router;
```

### 动态路由和参数验证
```javascript
// middleware/validate.js
const { validationResult } = require('express-validator');
const mongoose = require('mongoose');

const validate = (validations) => {
    return async (req, res, next) => {
        await Promise.all(validations.map(validation => validation.run(req)));
        
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({
                error: 'Validation failed',
                details: errors.array()
            });
        }
        next();
    };
};

// 验证MongoDB ObjectId
validate.id = (req, res, next) => {
    if (!mongoose.Types.ObjectId.isValid(req.params.id)) {
        return res.status(400).json({ error: 'Invalid ID format' });
    }
    next();
};

module.exports = validate;
```

## 中间件开发

### 认证中间件
```javascript
// middleware/auth.js
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const config = require('../config');

const authenticate = async (req, res, next) => {
    try {
        const token = req.header('Authorization')?.replace('Bearer ', '');
        
        if (!token) {
            return res.status(401).json({ error: 'Access denied. No token provided.' });
        }

        const decoded = jwt.verify(token, config.jwt.secret);
        const user = await User.findById(decoded.id).select('-password');
        
        if (!user) {
            return res.status(401).json({ error: 'Invalid token.' });
        }

        req.user = user;
        next();
    } catch (error) {
        res.status(401).json({ error: 'Invalid token.' });
    }
};

const authorize = (...roles) => {
    return (req, res, next) => {
        if (!req.user) {
            return res.status(401).json({ error: 'Access denied.' });
        }

        if (roles.length && !roles.includes(req.user.role)) {
            return res.status(403).json({ error: 'Insufficient permissions.' });
        }

        next();
    };
};

module.exports = { authenticate, authorize };
```

### 错误处理中间件
```javascript
// middleware/errorHandler.js
const logger = require('../utils/logger');

const errorHandler = (err, req, res, next) => {
    let error = { ...err };
    error.message = err.message;

    // 记录错误日志
    logger.error(err);

    // Mongoose验证错误
    if (err.name === 'ValidationError') {
        const message = Object.values(err.errors).map(val => val.message);
        error = {
            statusCode: 400,
            message: 'Validation Error',
            details: message
        };
    }

    // Mongoose重复键错误
    if (err.code === 11000) {
        const field = Object.keys(err.keyValue)[0];
        error = {
            statusCode: 400,
            message: `${field} already exists`,
            field: field
        };
    }

    // Mongoose转换错误
    if (err.name === 'CastError') {
        error = {
            statusCode: 400,
            message: 'Resource not found'
        };
    }

    // JWT错误
    if (err.name === 'JsonWebTokenError') {
        error = {
            statusCode: 401,
            message: 'Invalid token'
        };
    }

    // JWT过期错误
    if (err.name === 'TokenExpiredError') {
        error = {
            statusCode: 401,
            message: 'Token expired'
        };
    }

    res.status(error.statusCode || 500).json({
        success: false,
        error: error.message || 'Server Error',
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    });
};

module.exports = errorHandler;
```

### 限流中间件
```javascript
// middleware/rateLimiter.js
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const redis = require('../config/redis');

// 通用限流
const generalLimiter = rateLimit({
    store: new RedisStore({
        client: redis,
        prefix: 'rl:general:'
    }),
    windowMs: 15 * 60 * 1000, // 15分钟
    max: 100, // 限制每个IP 15分钟内最多100个请求
    message: {
        error: 'Too many requests from this IP, please try again later.'
    },
    standardHeaders: true,
    legacyHeaders: false,
});

// 登录限流
const loginLimiter = rateLimit({
    store: new RedisStore({
        client: redis,
        prefix: 'rl:login:'
    }),
    windowMs: 15 * 60 * 1000, // 15分钟
    max: 5, // 限制每个IP 15分钟内最多5次登录尝试
    skipSuccessfulRequests: true,
    message: {
        error: 'Too many login attempts, please try again later.'
    },
});

// API限流
const apiLimiter = rateLimit({
    store: new RedisStore({
        client: redis,
        prefix: 'rl:api:'
    }),
    windowMs: 1 * 60 * 1000, // 1分钟
    max: 30, // 限制每个IP 1分钟内最多30个API请求
    keyGenerator: (req) => {
        return req.user ? `user:${req.user.id}` : req.ip;
    },
});

module.exports = {
    generalLimiter,
    loginLimiter,
    apiLimiter
};
```

## 数据库集成

### MongoDB集成示例
```javascript
// models/User.js
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const userSchema = new mongoose.Schema({
    username: {
        type: String,
        required: [true, 'Username is required'],
        unique: true,
        trim: true,
        minlength: [3, 'Username must be at least 3 characters'],
        maxlength: [30, 'Username cannot exceed 30 characters']
    },
    email: {
        type: String,
        required: [true, 'Email is required'],
        unique: true,
        lowercase: true,
        match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
    },
    password: {
        type: String,
        required: [true, 'Password is required'],
        minlength: [6, 'Password must be at least 6 characters'],
        select: false // 默认查询时不返回密码
    },
    role: {
        type: String,
        enum: ['user', 'admin', 'moderator'],
        default: 'user'
    },
    profile: {
        firstName: String,
        lastName: String,
        avatar: String,
        bio: String,
        website: String,
        location: String
    },
    isActive: {
        type: Boolean,
        default: true
    },
    lastLogin: Date,
    emailVerified: {
        type: Boolean,
        default: false
    },
    emailVerificationToken: String,
    passwordResetToken: String,
    passwordResetExpires: Date
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});

// 虚拟字段
userSchema.virtual('fullName').get(function() {
    return `${this.profile.firstName} ${this.profile.lastName}`;
});

// 索引
userSchema.index({ email: 1 });
userSchema.index({ username: 1 });
userSchema.index({ 'profile.firstName': 'text', 'profile.lastName': 'text' });

// 密码加密中间件
userSchema.pre('save', async function(next) {
    // 只有密码被修改时才加密
    if (!this.isModified('password')) return next();
    
    try {
        const salt = await bcrypt.genSalt(12);
        this.password = await bcrypt.hash(this.password, salt);
        next();
    } catch (error) {
        next(error);
    }
});

// 实例方法：验证密码
userSchema.methods.comparePassword = async function(candidatePassword) {
    return await bcrypt.compare(candidatePassword, this.password);
};

// 实例方法：生成JWT令牌
userSchema.methods.getSignedJwtToken = function() {
    return jwt.sign(
        { id: this._id, role: this.role },
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRE }
    );
};

// 实例方法：生成密码重置令牌
userSchema.methods.getResetPasswordToken = function() {
    const resetToken = require('crypto').randomBytes(20).toString('hex');
    
    this.passwordResetToken = require('crypto')
        .createHash('sha256')
        .update(resetToken)
        .digest('hex');
    
    this.passwordResetExpires = Date.now() + 10 * 60 * 1000; // 10分钟
    
    return resetToken;
};

// 静态方法：根据邮箱或用户名查找用户
userSchema.statics.findByEmailOrUsername = function(identifier) {
    return this.findOne({
        $or: [
            { email: identifier },
            { username: identifier }
        ]
    }).select('+password');
};

module.exports = mongoose.model('User', userSchema);
```

### 数据库连接配置
```javascript
// config/database.js
const mongoose = require('mongoose');
const logger = require('../utils/logger');

const connectDB = async () => {
    try {
        const conn = await mongoose.connect(process.env.MONGODB_URI, {
            useNewUrlParser: true,
            useUnifiedTopology: true,
            maxPoolSize: 10,
            serverSelectionTimeoutMS: 5000,
            socketTimeoutMS: 45000,
            bufferCommands: false,
            bufferMaxEntries: 0
        });

        logger.info(`MongoDB Connected: ${conn.connection.host}`);
        
        // 监听连接事件
        mongoose.connection.on('error', (err) => {
            logger.error('MongoDB connection error:', err);
        });

        mongoose.connection.on('disconnected', () => {
            logger.warn('MongoDB disconnected');
        });

        mongoose.connection.on('reconnected', () => {
            logger.info('MongoDB reconnected');
        });

    } catch (error) {
        logger.error('Database connection failed:', error);
        process.exit(1);
    }
};

// 优雅关闭数据库连接
process.on('SIGINT', async () => {
    try {
        await mongoose.connection.close();
        logger.info('MongoDB connection closed through app termination');
        process.exit(0);
    } catch (error) {
        logger.error('Error closing MongoDB connection:', error);
        process.exit(1);
    }
});

module.exports = connectDB;
```

## 控制器实现

### 用户控制器
```javascript
// controllers/userController.js
const User = require('../models/User');
const asyncHandler = require('../middleware/async');
const ErrorResponse = require('../utils/errorResponse');

// @desc    获取所有用户
// @route   GET /api/users
// @access  Private/Admin
exports.getUsers = asyncHandler(async (req, res) => {
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 10;
    const startIndex = (page - 1) * limit;

    // 构建查询条件
    const query = {};
    
    if (req.query.role) {
        query.role = req.query.role;
    }
    
    if (req.query.isActive !== undefined) {
        query.isActive = req.query.isActive === 'true';
    }

    // 搜索功能
    if (req.query.search) {
        query.$or = [
            { username: { $regex: req.query.search, $options: 'i' } },
            { email: { $regex: req.query.search, $options: 'i' } },
            { 'profile.firstName': { $regex: req.query.search, $options: 'i' } },
            { 'profile.lastName': { $regex: req.query.search, $options: 'i' } }
        ];
    }

    const users = await User.find(query)
        .select('-password')
        .sort({ createdAt: -1 })
        .skip(startIndex)
        .limit(limit);

    const total = await User.countDocuments(query);

    res.status(200).json({
        success: true,
        count: users.length,
        total,
        pagination: {
            page,
            limit,
            pages: Math.ceil(total / limit),
            hasNext: page < Math.ceil(total / limit),
            hasPrev: page > 1
        },
        data: users
    });
});

// @desc    获取单个用户
// @route   GET /api/users/:id
// @access  Private
exports.getUserById = asyncHandler(async (req, res) => {
    const user = await User.findById(req.params.id).select('-password');
    
    if (!user) {
        return next(new ErrorResponse(`User not found with id of ${req.params.id}`, 404));
    }

    // 权限检查：只有管理员或用户本人可以查看
    if (req.user.role !== 'admin' && req.user.id !== user._id.toString()) {
        return next(new ErrorResponse('Not authorized to access this user', 403));
    }

    res.status(200).json({
        success: true,
        data: user
    });
});

// @desc    创建用户
// @route   POST /api/users
// @access  Private/Admin
exports.createUser = asyncHandler(async (req, res) => {
    const { username, email, password, role, profile } = req.body;

    // 检查用户是否已存在
    const existingUser = await User.findOne({
        $or: [{ email }, { username }]
    });

    if (existingUser) {
        return next(new ErrorResponse('User with this email or username already exists', 400));
    }

    const user = await User.create({
        username,
        email,
        password,
        role: role || 'user',
        profile: profile || {}
    });

    // 生成JWT令牌
    const token = user.getSignedJwtToken();

    res.status(201).json({
        success: true,
        data: {
            id: user._id,
            username: user.username,
            email: user.email,
            role: user.role,
            profile: user.profile,
            token
        }
    });
});

// @desc    更新用户
// @route   PUT /api/users/:id
// @access  Private
exports.updateUser = asyncHandler(async (req, res) => {
    const user = await User.findById(req.params.id);
    
    if (!user) {
        return next(new ErrorResponse(`User not found with id of ${req.params.id}`, 404));
    }

    // 权限检查
    if (req.user.role !== 'admin' && req.user.id !== user._id.toString()) {
        return next(new ErrorResponse('Not authorized to update this user', 403));
    }

    // 过滤可更新的字段
    const allowedFields = ['username', 'email', 'profile'];
    if (req.user.role === 'admin') {
        allowedFields.push('role', 'isActive');
    }

    const updateData = {};
    allowedFields.forEach(field => {
        if (req.body[field] !== undefined) {
            updateData[field] = req.body[field];
        }
    });

    // 如果更新邮箱或用户名，检查唯一性
    if (updateData.email || updateData.username) {
        const existingUser = await User.findOne({
            _id: { $ne: user._id },
            $or: [
                ...(updateData.email ? [{ email: updateData.email }] : []),
                ...(updateData.username ? [{ username: updateData.username }] : [])
            ]
        });

        if (existingUser) {
            return next(new ErrorResponse('Email or username already exists', 400));
        }
    }

    const updatedUser = await User.findByIdAndUpdate(
        user._id,
        updateData,
        { new: true, runValidators: true }
    ).select('-password');

    res.status(200).json({
        success: true,
        data: updatedUser
    });
});

// @desc    删除用户
// @route   DELETE /api/users/:id
// @access  Private/Admin
exports.deleteUser = asyncHandler(async (req, res) => {
    const user = await User.findById(req.params.id);
    
    if (!user) {
        return next(new ErrorResponse(`User not found with id of ${req.params.id}`, 404));
    }

    // 不能删除自己
    if (req.user.id === user._id.toString()) {
        return next(new ErrorResponse('You cannot delete your own account', 400));
    }

    await user.remove();

    res.status(200).json({
        success: true,
        data: {}
    });
});
```

## 性能优化策略

### 缓存实现
```javascript
// middleware/cache.js
const redis = require('../config/redis');
const crypto = require('crypto');

const cache = (duration = 300) => {
    return async (req, res, next) => {
        if (req.method !== 'GET') {
            return next();
        }

        // 生成缓存键
        const key = `cache:${crypto.createHash('md5')
            .update(req.originalUrl + JSON.stringify(req.query))
            .digest('hex')}`;

        try {
            // 尝试从缓存获取数据
            const cachedData = await redis.get(key);
            
            if (cachedData) {
                const data = JSON.parse(cachedData);
                res.set('X-Cache', 'HIT');
                return res.json(data);
            }

            // 重写res.json以缓存响应
            const originalJson = res.json;
            res.json = function(data) {
                // 只缓存成功响应
                if (res.statusCode === 200) {
                    redis.setex(key, duration, JSON.stringify(data));
                }
                res.set('X-Cache', 'MISS');
                return originalJson.call(this, data);
            };

            next();
        } catch (error) {
            // 缓存错误时继续处理请求
            next();
        }
    };
};

// 清除缓存
const clearCache = async (pattern) => {
    try {
        const keys = await redis.keys(pattern);
        if (keys.length > 0) {
            await redis.del(...keys);
        }
    } catch (error) {
        console.error('Cache clear error:', error);
    }
};

module.exports = { cache, clearCache };
```

### 压缩和优化中间件
```javascript
// middleware/performance.js
const compression = require('compression');
const helmet = require('helmet');

// 压缩中间件配置
const compressionMiddleware = compression({
    filter: (req, res) => {
        if (req.headers['x-no-compression']) {
            return false;
        }
        return compression.filter(req, res);
    },
    level: 6,
    threshold: 1024,
    windowBits: 15,
    memLevel: 8
});

// 安全头配置
const securityMiddleware = helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
            fontSrc: ["'self'", "https://fonts.gstatic.com"],
            imgSrc: ["'self'", "data:", "https:"],
            scriptSrc: ["'self'"],
            connectSrc: ["'self'"],
            frameSrc: ["'none'"],
            objectSrc: ["'none'"]
        }
    },
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
    }
});

// 响应时间中间件
const responseTime = (req, res, next) => {
    const start = Date.now();
    
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`${req.method} ${req.originalUrl} - ${res.statusCode} - ${duration}ms`);
    });
    
    next();
};

module.exports = {
    compressionMiddleware,
    securityMiddleware,
    responseTime
};
```

## 测试实现

### 测试配置
```javascript
// tests/setup.js
const mongoose = require('mongoose');
const request = require('supertest');
const app = require('../app');
const User = require('../models/User');

// 测试数据库连接
beforeAll(async () => {
    const testUri = process.env.MONGODB_TEST_URI || 'mongodb://localhost:27017/test';
    await mongoose.connect(testUri);
});

// 清理测试数据
beforeEach(async () => {
    await User.deleteMany({});
});

// 关闭测试数据库连接
afterAll(async () => {
    await mongoose.connection.close();
});

// 测试工具函数
const createTestUser = async (userData = {}) => {
    const defaultUser = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
        role: 'user'
    };
    
    return await User.create({ ...defaultUser, ...userData });
};

const getAuthToken = async (user) => {
    return user.getSignedJwtToken();
};

module.exports = {
    app,
    request,
    createTestUser,
    getAuthToken
};
```

### API测试示例
```javascript
// tests/users.test.js
const { app, request, createTestUser, getAuthToken } = require('./setup');

describe('Users API', () => {
    describe('GET /api/users', () => {
        it('should return 401 for unauthenticated request', async () => {
            const response = await request(app)
                .get('/api/users')
                .expect(401);
            
            expect(response.body).toHaveProperty('error');
        });

        it('should return users for authenticated admin', async () => {
            const admin = await createTestUser({ role: 'admin' });
            const token = getAuthToken(admin);
            
            await createTestUser();
            await createTestUser();
            
            const response = await request(app)
                .get('/api/users')
                .set('Authorization', `Bearer ${token}`)
                .expect(200);
            
            expect(response.body).toHaveProperty('success', true);
            expect(response.body).toHaveProperty('data');
            expect(Array.isArray(response.body.data)).toBe(true);
            expect(response.body.data.length).toBe(3);
        });

        it('should paginate results', async () => {
            const admin = await createTestUser({ role: 'admin' });
            const token = getAuthToken(admin);
            
            // 创建15个用户
            for (let i = 0; i < 15; i++) {
                await createTestUser({ 
                    username: `user${i}`,
                    email: `user${i}@example.com`
                });
            }
            
            const response = await request(app)
                .get('/api/users?page=1&limit=10')
                .set('Authorization', `Bearer ${token}`)
                .expect(200);
            
            expect(response.body.data.length).toBe(10);
            expect(response.body.pagination.page).toBe(1);
            expect(response.body.pagination.hasNext).toBe(true);
        });
    });

    describe('POST /api/users', () => {
        it('should create a new user', async () => {
            const admin = await createTestUser({ role: 'admin' });
            const token = getAuthToken(admin);
            
            const userData = {
                username: 'newuser',
                email: 'newuser@example.com',
                password: 'password123',
                profile: {
                    firstName: 'New',
                    lastName: 'User'
                }
            };
            
            const response = await request(app)
                .post('/api/users')
                .set('Authorization', `Bearer ${token}`)
                .send(userData)
                .expect(201);
            
            expect(response.body.success).toBe(true);
            expect(response.body.data).toHaveProperty('id');
            expect(response.body.data).toHaveProperty('token');
            expect(response.body.data.username).toBe(userData.username);
            expect(response.body.data.email).toBe(userData.email);
        });

        it('should return 400 for duplicate email', async () => {
            const admin = await createTestUser({ role: 'admin' });
            const token = getAuthToken(admin);
            
            const existingUser = await createTestUser({
                email: 'existing@example.com'
            });
            
            const userData = {
                username: 'newuser',
                email: 'existing@example.com',
                password: 'password123'
            };
            
            const response = await request(app)
                .post('/api/users')
                .set('Authorization', `Bearer ${token}`)
                .send(userData)
                .expect(400);
            
            expect(response.body).toHaveProperty('error');
        });
    });
});
```

这个Express.js参考文档提供了完整的框架使用指南，包括应用架构、路由设计、中间件开发、数据库集成、性能优化和测试实现，帮助开发者构建高质量的Express应用。
