# Flask轻量级应用参考文档

## Flask框架概述

### 什么是Flask
Flask是一个轻量级的Python Web框架，基于Werkzeug工具箱和Jinja2模板引擎。它被称为"微框架"，因为它保持核心简单但易于扩展。Flask提供了Web开发所需的基本功能，同时允许开发者自由选择数据库、表单验证等组件。

### Flask核心特性
- **轻量级**: 核心简单，不强制使用特定工具
- **灵活性强**: 可自由选择数据库、模板引擎等组件
- **易于扩展**: 丰富的扩展生态系统
- **内置开发服务器**: 方便开发和测试
- **RESTful支持**: 原生支持RESTful API开发
- **Jinja2集成**: 强大的模板引擎
- **Werkzeug集成**: 强大的WSGI工具包

## Flask应用基础架构

### 基础应用结构
```python
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return f'<User {self.username}>'

# 路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/users')
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'username': user.username} for user in users])

@app.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### 蓝图模块化架构
```python
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

# app/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)
```

## 路由和API设计

### RESTful API路由
```python
# app/api/routes.py
from flask import Blueprint, jsonify, request
from app.models import User, Post
from app import db

bp = Blueprint('api', __name__)

# 用户资源
@bp.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    })

@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or not 'username' in data or not 'email' in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = User(username=data['username'], email=data['email'])
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

# 文章资源
@bp.route('/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    author_id = request.args.get('author_id', type=int)
    
    query = Post.query
    if author_id:
        query = query.filter_by(author_id=author_id)
    
    posts = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'posts': [post.to_dict() for post in posts.items],
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page
    })

@bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())

@bp.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    
    if not data or not 'title' in data or not 'content' in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    post = Post(
        title=data['title'],
        content=data['content'],
        author_id=data.get('author_id', 1)
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post.to_dict()), 201
```

### 动态路由和参数处理
```python
# app/main/routes.py
from flask import render_template, request, redirect, url_for
from app.models import User, Post
from app import db

# 动态路由参数
@app.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user/profile.html', user=user)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post/show.html', post=post)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter(
        Post.title.contains(query) | 
        Post.content.contains(query)
    ).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('search/results.html', 
                         posts=posts, query=query)

# 多参数路由
@app.route('/category/<category_name>/tag/<tag_name>')
def category_tag_posts(category_name, tag_name):
    posts = Post.query.join(Post.categories).filter(
        Category.name == category_name
    ).join(Post.tags).filter(
        Tag.name == tag_name
    ).all()
    
    return render_template('posts/list.html', 
                         posts=posts, 
                         category=category_name, 
                         tag=tag_name)

# 路由转换器
from werkzeug.routing import BaseConverter

class ListConverter(BaseConverter):
    def to_python(self, value):
        return value.split('+')
    
    def to_url(self, values):
        return '+'.join(BaseConverter.to_url(value) for value in values)

app.url_map.converters['list'] = ListConverter

@app.route('/tags/<list:tag_names>')
def posts_by_tags(tag_names):
    posts = Post.query.join(Post.tags).filter(
        Tag.name.in_(tag_names)
    ).all()
    
    return render_template('posts/by_tags.html', 
                         posts=posts, tags=tag_names)
```

## 数据库集成

### SQLAlchemy模型设计
```python
# app/models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# 用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

# 文章模型
class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='post_tags', backref='posts', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'author_id': self.author_id,
            'author': self.author.username,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': [tag.name for tag in self.tags]
        }

# 评论模型
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author': self.author.username,
            'post_id': self.post_id,
            'created_at': self.created_at.isoformat()
        }

# 标签模型
class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 文章标签关联表
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)
```

### 数据库操作和查询
```python
# app/services/user_service.py
from app.models import User, Post
from app import db
from sqlalchemy import or_, and_, desc
from datetime import datetime, timedelta

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_username(username):
        """根据用户名获取用户"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email):
        """根据邮箱获取用户"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def create_user(username, email, password, is_admin=False):
        """创建用户"""
        user = User(
            username=username,
            email=email,
            is_admin=is_admin
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """更新用户信息"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        return user
    
    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def search_users(query, page=1, per_page=10):
        """搜索用户"""
        users = User.query.filter(
            or_(
                User.username.contains(query),
                User.email.contains(query)
            )
        ).paginate(page=page, per_page=per_page, error_out=False)
        return users
    
    @staticmethod
    def get_active_users(days=30):
        """获取活跃用户"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return User.query.filter(
            User.last_login >= cutoff_date
        ).all()

class PostService:
    @staticmethod
    def get_post_by_id(post_id):
        """根据ID获取文章"""
        return Post.query.get(post_id)
    
    @staticmethod
    def get_published_posts(page=1, per_page=10):
        """获取已发布的文章"""
        return Post.query.filter_by(is_published=True).order_by(
            desc(Post.created_at)
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_user_posts(user_id, page=1, per_page=10):
        """获取用户的文章"""
        return Post.query.filter_by(author_id=user_id).order_by(
            desc(Post.created_at)
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def create_post(title, content, author_id, summary=None, is_published=False):
        """创建文章"""
        post = Post(
            title=title,
            content=content,
            summary=summary,
            author_id=author_id,
            is_published=is_published
        )
        db.session.add(post)
        db.session.commit()
        return post
    
    @staticmethod
    def update_post(post_id, **kwargs):
        """更新文章"""
        post = Post.query.get(post_id)
        if not post:
            return None
        
        for key, value in kwargs.items():
            if hasattr(post, key):
                setattr(post, key, value)
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        return post
    
    @staticmethod
    def delete_post(post_id):
        """删除文章"""
        post = Post.query.get(post_id)
        if post:
            db.session.delete(post)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def search_posts(query, page=1, per_page=10):
        """搜索文章"""
        return Post.query.filter(
            or_(
                Post.title.contains(query),
                Post.content.contains(query),
                Post.summary.contains(query)
            )
        ).order_by(desc(Post.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_posts_by_tag(tag_name, page=1, per_page=10):
        """根据标签获取文章"""
        from app.models import Tag
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag:
            return tag.posts.order_by(desc(Post.created_at)).paginate(
                page=page, per_page=per_page, error_out=False
            )
        return None
```

## 中间件和请求处理

### 请求中间件
```python
# app/middleware.py
from flask import request, g, jsonify
from app import db
from app.models import User
import time
import logging

logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    """请求前处理"""
    g.start_time = time.time()
    
    # 记录请求信息
    logger.info(f"Request started: {request.method} {request.url}")
    
    # 设置用户信息
    if request.endpoint and request.endpoint.startswith('api.'):
        # API请求需要认证
        token = request.headers.get('Authorization')
        if token:
            # 验证JWT token
            try:
                user_id = verify_jwt_token(token)
                g.current_user = User.query.get(user_id)
            except:
                g.current_user = None
        else:
            g.current_user = None

@app.after_request
def after_request(response):
    """请求后处理"""
    # 计算响应时间
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        response.headers['X-Response-Time'] = str(duration)
        
        # 记录慢请求
        if duration > 1.0:
            logger.warning(f"Slow request: {request.method} {request.url} - {duration:.2f}s")
    
    # 添加安全头
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

@app.teardown_appcontext
def teardown_db(exception):
    """应用上下文销毁时处理"""
    if exception:
        logger.error(f"Application context error: {exception}")
    
    # 关闭数据库连接
    db.session.remove()

# 认证中间件
def require_auth(f):
    """认证装饰器"""
    from functools import wraps
    from flask import jsonify
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user is None:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """管理员权限装饰器"""
    from functools import wraps
    from flask import jsonify
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user is None:
            return jsonify({'error': 'Authentication required'}), 401
        if not g.current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    
    return decorated_function

# 限流中间件
from collections import defaultdict
from time import time

rate_limit_cache = defaultdict(list)

def rate_limit(max_requests=100, window=60):
    """限流装饰器"""
    def decorator(f):
        from functools import wraps
        from flask import jsonify
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            now = time()
            
            # 清理过期记录
            rate_limit_cache[client_ip] = [
                timestamp for timestamp in rate_limit_cache[client_ip]
                if now - timestamp < window
            ]
            
            # 检查是否超过限制
            if len(rate_limit_cache[client_ip]) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # 记录当前请求
            rate_limit_cache[client_ip].append(now)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
```

## 认证和授权

### Session认证
```python
# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=4, max=20)
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=8, max=128)
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), EqualTo('password')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

# app/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)
```

### JWT认证
```python
# app/auth/jwt_auth.py
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.models import User

def generate_jwt_token(user_id, expires_in=3600):
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def verify_jwt_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(f):
    """JWT认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从Header获取token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        user_id = verify_jwt_token(token)
        if not user_id:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # 设置当前用户
        g.current_user = User.query.get(user_id)
        if not g.current_user:
            return jsonify({'error': 'User not found'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# app/api/auth.py
from flask import Blueprint, request, jsonify
from app.models import User
from app.auth.jwt_auth import generate_jwt_token
from app import db

bp = Blueprint('auth_api', __name__)

@bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    
    if not data or not 'username' in data or not 'password' in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user is None or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 401
    
    # 生成JWT令牌
    token = generate_jwt_token(user.id)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    })

@bp.route('/refresh', methods=['POST'])
@jwt_required
def refresh_token():
    """刷新令牌"""
    token = generate_jwt_token(g.current_user.id)
    return jsonify({'token': token})

@bp.route('/me', methods=['GET'])
@jwt_required
def get_current_user():
    """获取当前用户信息"""
    return jsonify(g.current_user.to_dict())
```

## 模板引擎

### Jinja2模板配置
```python
# app/__init__.py
from flask import Flask
from jinja2 import Environment

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 自定义Jinja2配置
    app.jinja_env.auto_reload = True
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    
    # 添加全局函数
    @app.template_global()
    def format_datetime(value, format='medium'):
        if value is None:
            return ''
        return value.strftime('%Y-%m-%d %H:%M:%S')
    
    @app.template_global()
    def format_currency(value, currency='USD'):
        return f"{currency} {value:,.2f}"
    
    # 添加过滤器
    @app.template_filter('truncate_words')
    def truncate_words(s, length=50, suffix='...'):
        if len(s) <= length:
            return s
        return ' '.join(s.split()[:length]) + suffix
    
    @app.template_filter('markdown')
    def markdown_filter(text):
        import markdown
        return markdown.markdown(text)
    
    return app

# app/template_filters.py
from flask import Blueprint
from datetime import datetime
import humanize

bp = Blueprint('template_filters', __name__)

@bp.app_template_filter('humanize')
def humanize_filter(value):
    """人性化显示时间"""
    if isinstance(value, datetime):
        return humanize.naturaltime(value)
    return value

@bp.app_template_filter('slugify')
def slugify_filter(text):
    """URL友好化"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')
```

### 模板继承和组件
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Flask App{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/app.css') }}" rel="stylesheet">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('main.index') }}">Flask App</a>
            
            <div class="navbar-nav ms-auto">
                {% if current_user.is_authenticated %}
                    <span class="navbar-text me-3">
                        {{ current_user.username }}
                    </span>
                    <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                {% else %}
                    <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                    <a class="nav-link" href="{{ url_for('auth.register') }}">Register</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <main class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <footer class="bg-light mt-5 py-3">
        <div class="container text-center">
            <p>&copy; 2024 Flask App. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>

<!-- templates/post/list.html -->
{% extends "base.html" %}

{% block title %}文章列表{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h1>文章列表</h1>
        
        {% for post in posts.items %}
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">
                        <a href="{{ url_for('main.show_post', post_id=post.id) }}">
                            {{ post.title }}
                        </a>
                    </h5>
                    <p class="card-text">{{ post.summary or post.content[:200] }}...</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            作者: {{ post.author.username }} | 
                            发布时间: {{ post.created_at|format_datetime }}
                        </small>
                        <div>
                            {% for tag in post.tags %}
                                <span class="badge bg-secondary">{{ tag.name }}</span>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        {% endfor %}

        <!-- 分页 -->
        {% if posts.pages > 1 %}
            <nav>
                <ul class="pagination justify-content-center">
                    {% if posts.has_prev %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('main.index', page=posts.prev_num) }}">上一页</a>
                        </li>
                    {% endif %}
                    
                    {% for page_num in posts.iter_pages() %}
                        {% if page_num %}
                            {% if page_num != posts.page %}
                                <li class="page-item">
                                    <a class="page-link" href="{{ url_for('main.index', page=page_num) }}">{{ page_num }}</a>
                                </li>
                            {% else %}
                                <li class="page-item active">
                                    <span class="page-link">{{ page_num }}</span>
                                </li>
                            {% endif %}
                        {% else %}
                            <li class="page-item disabled">
                                <span class="page-link">...</span>
                            </li>
                        {% endif %}
                    {% endfor %}
                    
                    {% if posts.has_next %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('main.index', page=posts.next_num) }}">下一页</a>
                        </li>
                    {% endif %}
                </ul>
            </nav>
        {% endif %}
    </div>

    <div class="col-md-4">
        {% include 'sidebar.html' %}
    </div>
</div>
{% endblock %}

<!-- templates/macros.html -->
{% macro render_field(field, class='form-control') %}
    <div class="mb-3">
        {{ field.label(class="form-label") }}
        {{ field(class=class, **kwargs) }}
        {% if field.errors %}
            <div class="invalid-feedback d-block">
                {% for error in field.errors %}
                    {{ error }}
                {% endfor %}
            </div>
        {% endif %}
    </div>
{% endmacro %}

{% macro render_nav_item(title, endpoint, icon='') %}
    <li class="nav-item">
        <a class="nav-link {% if request.endpoint == endpoint %}active{% endif %}" 
           href="{{ url_for(endpoint) }}">
            {% if icon %}<i class="bi {{ icon }}"></i>{% endif %}
            {{ title }}
        </a>
    </li>
{% endmacro %}
```

## 错误处理

### 全局错误处理
```python
# app/errors.py
from flask import render_template, request, jsonify, current_app
from app import db
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logger.error(f"Internal server error: {error}")
        
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Access forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Unauthorized'}), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(400)
    def bad_request_error(error):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Bad request'}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理未捕获的异常"""
        db.session.rollback()
        
        # 记录错误日志
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        
        # 在开发环境中显示详细错误
        if current_app.debug:
            raise error
        
        # 在生产环境中返回通用错误信息
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

# 自定义异常类
class ValidationError(Exception):
    """验证错误"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

class NotFoundError(Exception):
    """资源未找到错误"""
    def __init__(self, message="Resource not found"):
        super().__init__()
        self.message = message
        self.status_code = 404

class UnauthorizedError(Exception):
    """未授权错误"""
    def __init__(self, message="Unauthorized"):
        super().__init__()
        self.message = message
        self.status_code = 401

class ForbiddenError(Exception):
    """禁止访问错误"""
    def __init__(self, message="Access forbidden"):
        super().__init__()
        self.message = message
        self.status_code = 403

# API错误处理器
def register_api_error_handlers(app):
    """注册API错误处理器"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({
            'error': error.message,
            'status_code': error.status_code,
            'payload': error.payload
        }), error.status_code
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        return jsonify({
            'error': error.message,
            'status_code': error.status_code
        }), error.status_code
    
    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized_error(error):
        return jsonify({
            'error': error.message,
            'status_code': error.status_code
        }), error.status_code
    
    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(error):
        return jsonify({
            'error': error.message,
            'status_code': error.status_code
        }), error.status_code
```

## 性能优化

### 缓存实现
```python
# app/cache.py
from flask_caching import Cache
from functools import wraps
import json
import hashlib

# 初始化缓存
cache = Cache()

def cache_key(*args, **kwargs):
    """生成缓存键"""
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()

def cached_view(timeout=300, key_prefix=''):
    """视图缓存装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key_name = f"{key_prefix}:{cache_key(*args, **kwargs)}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key_name)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = f(*args, **kwargs)
            cache.set(cache_key_name, result, timeout=timeout)
            
            return result
        return decorated_function
    return decorator

def memoize(timeout=300):
    """函数结果缓存装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key_name = f"memoize:{f.__name__}:{cache_key(*args, **kwargs)}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key_name)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = f(*args, **kwargs)
            cache.set(cache_key_name, result, timeout=timeout)
            
            return result
        return decorated_function
    return decorator

# 使用示例
@app.route('/popular-posts')
@cached_view(timeout=600, key_prefix='popular_posts')
def popular_posts():
    """热门文章页面"""
    posts = Post.query.order_by(Post.views.desc()).limit(10).all()
    return render_template('posts/popular.html', posts=posts)

@memoize(timeout=300)
def get_user_stats(user_id):
    """获取用户统计信息"""
    user = User.query.get(user_id)
    return {
        'posts_count': user.posts.count(),
        'comments_count': user.comments.count(),
        'last_login': user.last_login
    }
```

### 数据库优化
```python
# app/db_optimization.py
from sqlalchemy import event, Index
from sqlalchemy.orm import joinedload, selectinload, subqueryload
from app import db

# 添加数据库索引
def add_indexes():
    """添加数据库索引"""
    # 用户表索引
    Index('idx_users_username', User.username)
    Index('idx_users_email', User.email)
    Index('idx_users_created_at', User.created_at)
    
    # 文章表索引
    Index('idx_posts_author_id', Post.author_id)
    Index('idx_posts_created_at', Post.created_at)
    Index('idx_posts_is_published', Post.is_published)
    Index('idx_posts_title', Post.title)
    
    # 评论表索引
    Index('idx_comments_post_id', Comment.post_id)
    Index('idx_comments_author_id', Comment.author_id)
    Index('idx_comments_created_at', Comment.created_at)

# 查询优化
class OptimizedPostService:
    @staticmethod
    def get_posts_with_author(page=1, per_page=10):
        """获取文章及其作者信息（优化版）"""
        return Post.query.options(
            joinedload(Post.author)
        ).filter_by(is_published=True).order_by(
            Post.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_post_with_comments(post_id):
        """获取文章及其评论（优化版）"""
        return Post.query.options(
            joinedload(Post.author),
            joinedload(Post.comments).joinedload(Comment.author)
        ).filter_by(id=post_id).first()
    
    @staticmethod
    def get_user_with_stats(user_id):
        """获取用户及其统计信息（优化版）"""
        from sqlalchemy import func
        
        user = User.query.options(
            subqueryload(User.posts),
            subqueryload(User.comments)
        ).filter_by(id=user_id).first()
        
        if user:
            # 使用聚合查询获取统计信息
            stats = db.session.query(
                func.count(Post.id).label('posts_count'),
                func.count(Comment.id).label('comments_count')
            ).filter(
                Post.author_id == user_id
            ).union_all(
                db.session.query(
                    func.count(Post.id).label('posts_count'),
                    func.count(Comment.id).label('comments_count')
                ).filter(
                    Comment.author_id == user_id
                )
            ).all()
            
            user.stats = {
                'posts_count': sum(stat.posts_count for stat in stats),
                'comments_count': sum(stat.comments_count for stat in stats)
            }
        
        return user

# 数据库连接池优化
def configure_database_pool(app):
    """配置数据库连接池"""
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 20
    }

# 批量操作
def bulk_create_posts(posts_data):
    """批量创建文章"""
    posts = []
    for data in posts_data:
        post = Post(
            title=data['title'],
            content=data['content'],
            author_id=data['author_id'],
            is_published=data.get('is_published', False)
        )
        posts.append(post)
    
    db.session.bulk_save_objects(posts)
    db.session.commit()
    return posts

def bulk_update_posts(updates):
    """批量更新文章"""
    db.session.bulk_update_mappings(Post, updates)
    db.session.commit()
```

## 测试实现

### 测试配置和工具
```python
# tests/conftest.py
import pytest
from app import create_app, db
from app.models import User, Post
from config import TestConfig

@pytest.fixture(scope='session')
def app():
    """创建测试应用"""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """创建CLI测试运行器"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """认证头"""
    # 创建测试用户
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    
    # 登录获取token
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def sample_user():
    """示例用户"""
    user = User(
        username='sampleuser',
        email='sample@example.com',
        is_admin=False
    )
    user.set_password('samplepass')
    return user

@pytest.fixture
def sample_post(sample_user):
    """示例文章"""
    return Post(
        title='Sample Post',
        content='This is a sample post content.',
        author=sample_user,
        is_published=True
    )

# tests/test_models.py
def test_user_model():
    """测试用户模型"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpass')
    
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpass')
    assert not user.check_password('wrongpass')
    assert user.is_active is True
    assert user.is_admin is False

def test_post_model(sample_user):
    """测试文章模型"""
    post = Post(
        title='Test Post',
        content='Test content',
        author=sample_user
    )
    
    assert post.title == 'Test Post'
    assert post.content == 'Test content'
    assert post.author == sample_user
    assert post.is_published is False

def test_post_to_dict(sample_post):
    """测试文章序列化"""
    data = sample_post.to_dict()
    
    assert 'id' in data
    assert 'title' in data
    assert 'content' in data
    assert 'author' in data
    assert data['author'] == 'sampleuser'

# tests/test_api.py
def test_get_users(client):
    """测试获取用户列表"""
    response = client.get('/api/users')
    assert response.status_code == 200
    assert 'users' in response.json

def test_create_user(client):
    """测试创建用户"""
    user_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpass'
    }
    
    response = client.post('/api/users', json=user_data)
    assert response.status_code == 201
    assert response.json['username'] == 'newuser'
    assert response.json['email'] == 'newuser@example.com'
    assert 'password' not in response.json

def test_login_api(client, sample_user):
    """测试API登录"""
    db.session.add(sample_user)
    db.session.commit()
    
    response = client.post('/api/auth/login', json={
        'username': 'sampleuser',
        'password': 'samplepass'
    })
    
    assert response.status_code == 200
    assert 'token' in response.json
    assert 'user' in response.json

def test_protected_endpoint(client, auth_headers):
    """测试受保护的端点"""
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['username'] == 'testuser'

def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get('/api/auth/me')
    assert response.status_code == 401
    assert response.json['error'] == 'Token is missing'

# tests/test_views.py
def test_index_page(client):
    """测试首页"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_login_page(client):
    """测试登录页面"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data

def test_register_page(client):
    """测试注册页面"""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_user_registration(client):
    """测试用户注册"""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpass',
        'password2': 'newpass'
    })
    
    assert response.status_code == 302  # 重定向到登录页面

def test_user_login(client, sample_user):
    """测试用户登录"""
    db.session.add(sample_user)
    db.session.commit()
    
    response = client.post('/auth/login', data={
        'username': 'sampleuser',
        'password': 'samplepass',
        'remember_me': True
    })
    
    assert response.status_code == 302  # 重定向到首页

def test_logout(client, sample_user):
    """测试用户登出"""
    db.session.add(sample_user)
    db.session.commit()
    
    # 先登录
    client.post('/auth/login', data={
        'username': 'sampleuser',
        'password': 'samplepass'
    })
    
    # 再登出
    response = client.get('/auth/logout')
    assert response.status_code == 302
```

这个Flask参考文档提供了完整的轻量级应用开发指南，包括基础架构、路由设计、数据库集成、认证授权、模板引擎、错误处理、性能优化和测试实现，帮助开发者构建现代化的Flask应用。
