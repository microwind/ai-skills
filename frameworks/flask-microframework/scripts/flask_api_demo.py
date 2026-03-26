#!/usr/bin/env python3
"""
Flask轻量级应用 - RESTful API和蓝图架构示例
"""

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# 数据模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author': self.author.username,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 蓝图定义
from flask import Blueprint

# API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = User(username=data['username'], email=data['email'])
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@api_bp.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([post.to_dict() for post in posts])

@api_bp.route('/posts', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()
    
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    post = Post(
        title=data['title'],
        content=data['content'],
        author=current_user
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post.to_dict()), 201

# 认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing credentials'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Login successful', 'user': user.to_dict()})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'})

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

# 主蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return jsonify({
        'message': 'Welcome to Flask Demo API',
        'endpoints': {
            'users': '/api/users',
            'posts': '/api/posts',
            'login': '/auth/login',
            'register': '/auth/register'
        }
    })

@main_bp.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# 中间件示例
@app.before_request
def before_request():
    """请求前处理"""
    if request.endpoint and request.endpoint.startswith('api'):
        # API请求的日志记录
        print(f"API Request: {request.method} {request.path}")

@app.after_request
def after_request(response):
    """请求后处理"""
    response.headers['X-Response-Time'] = '10ms'
    return response

# 注册蓝图
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

def create_sample_data():
    """创建示例数据"""
    with app.app_context():
        db.create_all()
        
        if User.query.count() == 0:
            # 创建示例用户
            users = [
                User(username='alice', email='alice@example.com'),
                User(username='bob', email='bob@example.com'),
                User(username='charlie', email='charlie@example.com')
            ]
            
            for user in users:
                user.set_password('password123')
            
            db.session.add_all(users)
            db.session.commit()
            
            # 创建示例文章
            alice = User.query.filter_by(username='alice').first()
            bob = User.query.filter_by(username='bob').first()
            
            posts = [
                Post(title='Flask入门指南', content='Flask是一个轻量级的Web框架...', author=alice),
                Post(title='SQLAlchemy使用技巧', content='SQLAlchemy是Python中最流行的ORM...', author=bob),
                Post(title='RESTful API设计', content='RESTful API是一种Web服务设计风格...', author=alice),
                Post(title='数据库迁移最佳实践', content='数据库迁移是应用开发中的重要环节...', author=bob)
            ]
            
            db.session.add_all(posts)
            db.session.commit()

def main():
    """Flask应用演示"""
    print("Flask轻量级应用演示")
    print("=" * 50)
    
    # 创建示例数据
    create_sample_data()
    
    print("\n1. 用户管理演示")
    print("-" * 30)
    
    with app.test_client() as client:
        # 获取所有用户
        response = client.get('/api/users')
        users = response.get_json()
        print(f"用户总数: {len(users)}")
        for user in users[:2]:
            print(f"  - {user['username']} ({user['email']})")
        
        print("\n2. 认证演示")
        print("-" * 30)
        
        # 用户登录
        login_data = {'username': 'alice', 'password': 'password123'}
        response = client.post('/auth/login', json=login_data)
        login_result = response.get_json()
        print(f"登录结果: {login_result['message']}")
        
        print("\n3. 文章管理演示")
        print("-" * 30)
        
        # 获取所有文章
        response = client.get('/api/posts')
        posts = response.get_json()
        print(f"文章总数: {len(posts)}")
        for post in posts[:2]:
            print(f"  - {post['title']} (作者: {post['author']})")
        
        print("\n4. 创建新文章演示")
        print("-" * 30)
        
        # 创建新文章 (需要先登录)
        with app.test_client() as client:
            # 先登录
            client.post('/auth/login', json=login_data)
            
            # 创建文章
            post_data = {
                'title': 'Flask蓝图架构详解',
                'content': 'Flask蓝图是一种组织应用的方式...'
            }
            response = client.post('/api/posts', json=post_data)
            if response.status_code == 201:
                new_post = response.get_json()
                print(f"创建文章成功: {new_post['title']}")
            else:
                print("创建文章失败")
        
        print("\n5. 健康检查演示")
        print("-" * 30)
        
        response = client.get('/health')
        health = response.get_json()
        print(f"应用状态: {health['status']}")
        print(f"检查时间: {health['timestamp']}")
    
    print(f"\n\nFlask应用演示完成!")
    print("=" * 50)
    print("提示: 运行 'python flask_demo.py run' 启动Web服务器")
    print("API端点:")
    print("  - GET  http://localhost:5000/api/users")
    print("  - POST http://localhost:5000/auth/login")
    print("  - GET  http://localhost:5000/api/posts")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        # 启动Web服务器
        print("启动Flask开发服务器...")
        print("访问 http://localhost:5000 查看API")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        # 运行演示
        main()
