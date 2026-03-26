# Django Web框架参考文档

## Django框架概述

### 什么是Django
Django是一个高级Python Web框架，遵循MTV（Model-Template-View）架构模式。它提供了完整的Web开发解决方案，包括ORM、模板引擎、用户认证、管理后台等功能，帮助开发者快速构建安全、可维护的Web应用。

### Django核心特性
- **MTV架构**: 清晰的模型-模板-视图分离
- **ORM系统**: 强大的对象关系映射
- **自动管理后台**: 基于模型的自动管理界面
- **用户认证系统**: 完整的用户认证和权限管理
- **模板系统**: 强大的模板引擎和继承机制
- **中间件系统**: 灵活的请求处理管道
- **缓存系统**: 多种缓存后端支持
- **国际化**: 完整的多语言支持

## MTV架构详解

### 模型层(Model)

#### 模型定义
```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """分类模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name="分类名称")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Article(models.Model):
    """文章模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="标题")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL别名")
    content = models.TextField(verbose_name="内容")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="摘要")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="分类")
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="标签")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="状态")
    view_count = models.PositiveIntegerField(default=0, verbose_name="浏览次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="发布时间")
    
    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

class Tag(models.Model):
    """标签模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name="标签名称")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="颜色")
    
    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"
    
    def __str__(self):
        return self.name
```

#### ORM查询优化
```python
from django.db import models
from django.db.models import Q, F, Count, Avg, Sum
from django.core.paginator import Paginator

class ArticleRepository:
    """文章数据访问层"""
    
    @staticmethod
    def get_published_articles():
        """获取已发布的文章"""
        return Article.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags')
    
    @staticmethod
    def search_articles(query):
        """搜索文章"""
        return Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct().select_related('author', 'category')
    
    @staticmethod
    def get_articles_by_category(category_id):
        """根据分类获取文章"""
        return Article.objects.filter(
            category_id=category_id,
            status='published'
        ).select_related('author', 'category')
    
    @staticmethod
    def get_popular_articles(limit=10):
        """获取热门文章"""
        return Article.objects.filter(
            status='published'
        ).order_by('-view_count')[:limit]
    
    @staticmethod
    def get_article_statistics():
        """获取文章统计信息"""
        return Article.objects.aggregate(
            total_articles=Count('id'),
            published_articles=Count('id', filter=Q(status='published')),
            total_views=Sum('view_count'),
            avg_views=Avg('view_count')
        )

class ArticleService:
    """文章业务逻辑层"""
    
    def __init__(self):
        self.repository = ArticleRepository()
    
    def get_article_list(self, page=1, per_page=10, category=None):
        """获取文章列表"""
        articles = self.repository.get_published_articles()
        
        if category:
            articles = articles.filter(category=category)
        
        paginator = Paginator(articles, per_page)
        return paginator.get_page(page)
    
    def get_article_detail(self, slug):
        """获取文章详情"""
        article = self.repository.get_published_articles().filter(slug=slug).first()
        if article:
            # 增加浏览次数
            Article.objects.filter(id=article.id).update(view_count=F('view_count') + 1)
        return article
```

### 视图层(View)

#### 基于类的视图
```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages

class ArticleListView(ListView):
    """文章列表视图"""
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset.filter(status='published').select_related('author', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        return context

class ArticleDetailView(DetailView):
    """文章详情视图"""
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Article.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取相关文章
        article = self.get_object()
        context['related_articles'] = Article.objects.filter(
            category=article.category,
            status='published'
        ).exclude(id=article.id)[:5]
        return context

class ArticleCreateView(LoginRequiredMixin, CreateView):
    """创建文章视图"""
    model = Article
    template_name = 'articles/article_form.html'
    fields = ['title', 'slug', 'content', 'excerpt', 'category', 'tags']
    success_url = reverse_lazy('article_list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, '文章创建成功！')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '创建文章'
        context['categories'] = Category.objects.all()
        return context

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """更新文章视图"""
    model = Article
    template_name = 'articles/article_form.html'
    fields = ['title', 'slug', 'content', 'excerpt', 'category', 'tags']
    success_url = reverse_lazy('article_list')
    
    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, '文章更新成功！')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '编辑文章'
        context['categories'] = Category.objects.all()
        return context
```

#### API视图
```python
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

class ArticleViewSet(viewsets.ModelViewSet):
    """文章API视图集"""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'status', 'author']
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            queryset = queryset.filter(status='published')
        return queryset.select_related('author', 'category').prefetch_related('tags')
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞文章"""
        article = self.get_object()
        user = request.user
        
        if user in article.likes.all():
            article.likes.remove(user)
            return Response({'liked': False})
        else:
            article.likes.add(user)
            return Response({'liked': True})
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """获取热门文章"""
        articles = self.get_queryset().order_by('-view_count')[:10]
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)
```

### 模板层(Template)

#### 模板继承和包含
```html
<!-- base.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Django Blog{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/bootstrap.min.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header>
        {% include 'includes/navbar.html' %}
    </header>
    
    <main class="container mt-4">
        {% messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endmessages %}
        
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        {% include 'includes/footer.html' %}
    </footer>
    
    <script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

```html
<!-- article_list.html -->
{% extends 'base.html' %}
{% load static %}

{% block title %}文章列表 - Django Blog{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h1>文章列表</h1>
        
        {% for article in articles %}
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">
                    <a href="{% url 'article_detail' article.slug %}">{{ article.title }}</a>
                </h5>
                <p class="card-text">{{ article.excerpt|default:article.content|truncatewords:30 }}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                        作者: {{ article.author.username }} | 
                        分类: {{ article.category.name }} |
                        发布时间: {{ article.published_at|date:"Y-m-d" }}
                    </small>
                    <div>
                        {% for tag in article.tags.all %}
                        <span class="badge bg-secondary">{{ tag.name }}</span>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
        {% empty %}
        <p>暂无文章</p>
        {% endfor %}
        
        <!-- 分页 -->
        {% if is_paginated %}
        <nav>
            <ul class="pagination justify-content-center">
                {% if page_obj.has_previous %}
                <li class="page-item">
                    <a class="page-link" href="?page=1">首页</a>
                </li>
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.previous_page_number }}">上一页</a>
                </li>
                {% endif %}
                
                {% for num in page_obj.paginator.page_range %}
                {% if page_obj.number == num %}
                <li class="page-item active">
                    <span class="page-link">{{ num }}</span>
                </li>
                {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ num }}">{{ num }}</a>
                </li>
                {% endif %}
                {% endfor %}
                
                {% if page_obj.has_next %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.next_page_number }}">下一页</a>
                </li>
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}">末页</a>
                </li>
                {% endif %}
            </ul>
        </nav>
        {% endif %}
    </div>
    
    <div class="col-md-4">
        {% include 'includes/sidebar.html' %}
    </div>
</div>
{% endblock %}
```

#### 自定义模板标签和过滤器
```python
# templatetags/article_tags.py
from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.filter
def markdown_to_html(value):
    """Markdown转HTML"""
    return mark_safe(markdown.markdown(value))

@register.filter
def truncate_words_html(value, arg):
    """截断单词并保留HTML标签"""
    try:
        length = int(arg)
    except ValueError:
        return value
    
    from django.utils.text import Truncator
    return Truncator(value).words(length, html=True)

@register.inclusion_tag('articles/article_card.html')
def article_card(article):
    """文章卡片标签"""
    return {'article': article}

@register.simple_tag
def get_article_count():
    """获取文章总数"""
    return Article.objects.filter(status='published').count()
```

## 用户认证系统

### 自定义用户模型
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """自定义用户模型"""
    email = models.EmailField(unique=True, verbose_name="邮箱")
    phone = models.CharField(max_length=20, blank=True, verbose_name="手机号")
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name="头像")
    bio = models.TextField(max_length=500, blank=True, verbose_name="个人简介")
    website = models.URLField(blank=True, verbose_name="个人网站")
    location = models.CharField(max_length=100, blank=True, verbose_name="所在地")
    birth_date = models.DateField(null=True, blank=True, verbose_name="生日")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
    
    def __str__(self):
        return self.email

class UserProfile(models.Model):
    """用户配置文件"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="用户")
    theme = models.CharField(max_length=20, default='light', verbose_name="主题")
    language = models.CharField(max_length=10, default='zh-cn', verbose_name="语言")
    timezone = models.CharField(max_length=50, default='Asia/Shanghai', verbose_name="时区")
    email_notifications = models.BooleanField(default=True, verbose_name="邮件通知")
    
    class Meta:
        verbose_name = "用户配置"
        verbose_name_plural = "用户配置"
```

### 认证视图
```python
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages

class CustomLoginForm(AuthenticationForm):
    """自定义登录表单"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': '邮箱'})
        self.fields['password'].widget.attrs.update({'placeholder': '密码'})

def login_view(request):
    """登录视图"""
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '登录成功！')
                return redirect('home')
            else:
                messages.error(request, '用户名或密码错误')
    else:
        form = CustomLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    """登出视图"""
    logout(request)
    messages.info(request, '您已成功登出')
    return redirect('login')

class RegisterView(CreateView):
    """注册视图"""
    model = CustomUser
    template_name = 'auth/register.html'
    fields = ['username', 'email', 'password1', 'password2']
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '注册成功！请登录')
        return response
```

## 中间件系统

### 自定义中间件
```python
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import time
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """请求日志中间件"""
    
    def process_request(self, request):
        request.start_time = time.time()
        logger.info(f"Request: {request.method} {request.path}")
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f"Response: {response.status_code} - {duration:.3f}s")
        return response

class PerformanceMiddleware(MiddlewareMixin):
    """性能监控中间件"""
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # 记录慢请求
            if duration > 1.0:
                logger.warning(f"Slow request: {request.path} - {duration:.3f}s")
            
            # 添加性能头
            response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response

class SecurityHeadersMiddleware(MiddlewareMixin):
    """安全头中间件"""
    
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
```

## 缓存系统

### 缓存配置和使用
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'django_cache',
        'TIMEOUT': 300,  # 5分钟
    },
    'session': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'session_cache',
    }
}

# 视图中使用缓存
from django.views.decorators.cache import cache_page
from django.core.cache import cache

@cache_page(60 * 15)  # 缓存15分钟
def article_list_view(request):
    # 视图逻辑
    pass

# 手动缓存
def get_popular_articles():
    cache_key = 'popular_articles'
    articles = cache.get(cache_key)
    
    if articles is None:
        articles = Article.objects.filter(status='published').order_by('-view_count')[:10]
        cache.set(cache_key, articles, 60 * 30)  # 缓存30分钟
    
    return articles

# 模板片段缓存
{% load cache %}
{% cache 500 sidebar %}
    <!-- 侧边栏内容 -->
{% endcache %}
```

## 部署配置

### Docker配置
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=dbname
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

这个Django参考文档提供了完整的框架使用指南，包括MTV架构、用户认证、中间件、缓存和部署配置，帮助开发者构建高质量的Django应用。
