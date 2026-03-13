---
name: Docker Compose编排
description: "当编排容器时，分析服务依赖，优化配置管理，解决网络问题。验证容器架构，设计部署策略，和最佳实践。"
license: MIT
---

# Docker Compose编排技能

## 概述

Docker Compose是定义和运行多容器Docker应用程序的工具，通过YAML文件配置服务、网络和卷，实现容器化应用的快速部署和管理。不当的Compose配置会导致服务启动失败、资源浪费、网络通信问题。

**核心原则**: 好的Compose配置应该服务独立、依赖明确、资源合理、网络清晰。坏的配置会导致服务耦合、启动顺序混乱、资源冲突。

## 何时使用

**始终:**
- 开发环境搭建时
- 微服务本地测试时
- CI/CD流水线构建时
- 多服务应用部署时
- 环境隔离管理时
- 服务编排测试时

**触发短语:**
- "如何配置Docker Compose？"
- "服务依赖管理"
- "容器网络配置"
- "数据卷持久化"
- "环境变量管理"
- "服务健康检查"

## Docker Compose编排技能功能

### 服务配置
- 镜像构建管理
- 容器启动配置
- 环境变量设置
- 端口映射管理
- 资源限制配置
- 健康检查设置

### 依赖管理
- 服务依赖关系
- 启动顺序控制
- 等待条件设置
- 依赖检查机制
- 故障恢复策略
- 重启策略配置

### 网络配置
- 自定义网络创建
- 服务发现配置
- 网络隔离设置
- 端口暴露管理
- 负载均衡配置
- DNS解析设置

### 数据管理
- 数据卷创建
- 持久化存储
- 备份恢复策略
- 数据同步机制
- 权限管理设置
- 存储优化配置

## 常见问题

**❌ 服务启动失败**
- 镜像拉取失败
- 端口冲突
- 环境变量错误
- 依赖服务未就绪
- 资源不足

**❌ 网络通信问题**
- 服务间无法通信
- DNS解析失败
- 端口映射错误
- 网络隔离配置错误
- 防火墙阻拦

**❌ 数据持久化问题**
- 数据丢失
- 权限错误
- 存储空间不足
- 备份策略缺失
- 数据同步失败

**❌ 资源管理问题**
- 内存溢出
- CPU使用过高
- 磁盘空间不足
- 容器重启频繁
- 性能瓶颈

## 代码示例

### 基础Web应用Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Web应用服务
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
      args:
        NODE_ENV: production
    image: myapp/web:latest
    container_name: myapp-web
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - API_URL=http://api:8000
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./web/logs:/app/logs
      - web_uploads:/app/uploads
    depends_on:
      api:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

  # API服务
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    image: myapp/api:latest
    container_name: myapp-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/myapp
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - DEBUG=false
    volumes:
      - ./api/logs:/app/logs
      - api_data:/app/data
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network
      - db-network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: myapp-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init:/docker-entrypoint-initdb.d
      - ./postgres/config/postgresql.conf:/etc/postgresql/postgresql.conf
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - db-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: myapp-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 30s
    networks:
      - app-network
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M
        reservations:
          cpus: '0.1'
          memory: 128M

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: myapp-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - web
      - api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    networks:
      - app-network
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 128M
        reservations:
          cpus: '0.1'
          memory: 64M

# 网络配置
networks:
  app-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
  
  db-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16
          gateway: 172.21.0.1
    internal: true  # 内部网络，不能访问外网

# 数据卷配置
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/postgres
  
  redis_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/redis
  
  web_uploads:
    driver: local
  
  api_data:
    driver: local
  
  nginx_logs:
    driver: local
```

### 开发环境配置

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  web:
    build:
      context: ./web
      dockerfile: Dockerfile.dev
    image: myapp/web:dev
    container_name: myapp-web-dev
    ports:
      - "3000:3000"
      - "9229:9229"  # Node.js调试端口
    environment:
      - NODE_ENV=development
      - API_URL=http://localhost:8000
      - REDIS_URL=redis://localhost:6379
    volumes:
      - ./web:/app
      - /app/node_modules  # 防止node_modules被覆盖
      - web_dev_logs:/app/logs
    command: npm run dev
    depends_on:
      - api
      - redis
    networks:
      - dev-network

  api:
    build:
      context: ./api
      dockerfile: Dockerfile.dev
    image: myapp/api:dev
    container_name: myapp-api-dev
    ports:
      - "8000:8000"
      - "5678:5678"  # Python调试端口
    environment:
      - DATABASE_URL=postgresql://dev:dev@postgres-dev:5432/myapp_dev
      - REDIS_URL=redis://redis-dev:6379
      - JWT_SECRET=dev-secret
      - DEBUG=true
    volumes:
      - ./api:/app
      - api_dev_data:/app/data
      - api_dev_logs:/app/logs
    command: python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      postgres-dev:
        condition: service_healthy
      redis-dev:
        condition: service_started
    networks:
      - dev-network

  postgres-dev:
    image: postgres:15-alpine
    container_name: myapp-postgres-dev
    ports:
      - "5433:5432"  # 不同端口避免冲突
    environment:
      - POSTGRES_DB=myapp_dev
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=dev
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./postgres/init-dev:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev -d myapp_dev"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - dev-network

  redis-dev:
    image: redis:7-alpine
    container_name: myapp-redis-dev
    ports:
      - "6380:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_dev_data:/data
    networks:
      - dev-network

  # 开发工具容器
  adminer:
    image: adminer:latest
    container_name: myapp-adminer
    ports:
      - "8080:8080"
    environment:
      - ADMINER_DEFAULT_SERVER=postgres-dev
    depends_on:
      - postgres-dev
    networks:
      - dev-network

  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: myapp-redis-commander
    ports:
      - "8081:8081"
    environment:
      - REDIS_HOSTS=local:redis-dev:6379
    depends_on:
      - redis-dev
    networks:
      - dev-network

networks:
  dev-network:
    driver: bridge

volumes:
  postgres_dev_data:
  redis_dev_data:
  web_dev_logs:
  api_dev_data:
  api_dev_logs:
```

### 生产环境配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    image: myapp/web:${VERSION}
    container_name: myapp-web-prod
    restart: always
    environment:
      - NODE_ENV=production
      - API_URL=https://api.myapp.com
      - REDIS_URL=redis://redis:6379
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
        monitor: 60s
        max_failure_ratio: 0.3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - prod-network

  api:
    image: myapp/api:${VERSION}
    container_name: myapp-api-prod
    restart: always
    environment:
      - DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@postgres:5432/myapp_prod
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - DEBUG=false
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '1.0'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
        monitor: 60s
        max_failure_ratio: 0.3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - prod-network
      - db-network

  postgres:
    image: postgres:15-alpine
    container_name: myapp-postgres-prod
    restart: always
    environment:
      - POSTGRES_DB=myapp_prod
      - POSTGRES_USER=prod_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U prod_user -d myapp_prod"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - db-network

  redis:
    image: redis:7-alpine
    container_name: myapp-redis-prod
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_prod_data:/data
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - prod-network

  nginx:
    image: nginx:alpine
    container_name: myapp-nginx-prod
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_prod_logs:/var/log/nginx
    depends_on:
      - web
      - api
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 128M
        reservations:
          cpus: '0.25'
          memory: 64M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - prod-network

networks:
  prod-network:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: prod-network
  
  db-network:
    driver: bridge
    internal: true

volumes:
  postgres_prod_data:
    driver: local
  redis_prod_data:
    driver: local
  nginx_prod_logs:
    driver: local
```

### 自动化部署脚本

```bash
#!/bin/bash
# deploy.sh - Docker Compose自动化部署脚本

set -e

# 配置变量
PROJECT_NAME="myapp"
ENVIRONMENT=${1:-development}
VERSION=${2:-latest}
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.${ENVIRONMENT}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装"
        exit 1
    fi
    
    # 检查Docker是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行"
        exit 1
    fi
    
    log_info "依赖检查通过"
}

# 加载环境变量
load_environment() {
    log_info "加载环境变量: $ENVIRONMENT"
    
    if [ -f "$ENV_FILE" ]; then
        export $(cat $ENV_FILE | grep -v '^#' | xargs)
        log_info "环境变量加载完成"
    else
        log_warn "环境文件不存在: $ENV_FILE"
    fi
    
    export VERSION=$VERSION
    export ENVIRONMENT=$ENVIRONMENT
}

# 构建镜像
build_images() {
    log_info "构建镜像..."
    
    case $ENVIRONMENT in
        "development")
            docker-compose -f docker-compose.dev.yml build
            ;;
        "production")
            docker-compose -f docker-compose.prod.yml build
            ;;
        *)
            docker-compose build
            ;;
    esac
    
    log_info "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    case $ENVIRONMENT in
        "development")
            docker-compose -f docker-compose.dev.yml up -d
            ;;
        "production")
            docker-compose -f docker-compose.prod.yml up -d
            ;;
        *)
            docker-compose up -d
            ;;
    esac
    
    log_info "服务启动完成"
}

# 健康检查
health_check() {
    log_info "等待服务健康检查..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "健康检查尝试 $attempt/$max_attempts"
        
        # 检查主要服务健康状态
        if docker-compose ps | grep -q "Up (healthy)"; then
            log_info "服务健康检查通过"
            return 0
        fi
        
        sleep 10
        ((attempt++))
    done
    
    log_error "健康检查失败"
    docker-compose ps
    return 1
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    case $ENVIRONMENT in
        "development")
            docker-compose -f docker-compose.dev.yml exec -T api python manage.py migrate
            ;;
        "production")
            docker-compose -f docker-compose.prod.yml exec -T api python manage.py migrate
            ;;
        *)
            docker-compose exec -T api python manage.py migrate
            ;;
    esac
    
    log_info "数据库迁移完成"
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."
    
    local backup_dir="./backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/postgres_backup_$timestamp.sql"
    
    mkdir -p $backup_dir
    
    case $ENVIRONMENT in
        "development")
            docker-compose -f docker-compose.dev.yml exec -T postgres pg_dump -U dev myapp_dev > $backup_file
            ;;
        "production")
            docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U prod_user myapp_prod > $backup_file
            ;;
        *)
            docker-compose exec -T postgres pg_dump -U user myapp > $backup_file
            ;;
    esac
    
    log_info "数据库备份完成: $backup_file"
}

# 清理旧镜像
cleanup_images() {
    log_info "清理旧镜像..."
    
    # 删除悬空镜像
    docker image prune -f
    
    # 删除旧版本镜像（保留最近3个版本）
    local images_to_keep=3
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}" | \
        grep "^$PROJECT_NAME/" | \
        tail -n +$((images_to_keep + 1)) | \
        awk '{print $3}' | \
        xargs -r docker rmi
    
    log_info "镜像清理完成"
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    docker-compose ps
    
    log_info "服务日志:"
    docker-compose logs --tail=50
}

# 回滚部署
rollback() {
    local target_version=$1
    
    if [ -z "$target_version" ]; then
        log_error "请指定回滚版本"
        exit 1
    fi
    
    log_warn "回滚到版本: $target_version"
    
    # 停止当前服务
    docker-compose down
    
    # 切换到目标版本
    export VERSION=$target_version
    
    # 重新部署
    build_images
    start_services
    health_check
    
    log_info "回滚完成"
}

# 主函数
main() {
    local command=${1:-deploy}
    
    case $command in
        "deploy")
            check_dependencies
            load_environment
            build_images
            start_services
            health_check
            run_migrations
            show_status
            ;;
        "update")
            check_dependencies
            load_environment
            build_images
            docker-compose up -d
            health_check
            ;;
        "stop")
            log_info "停止服务..."
            docker-compose down
            ;;
        "restart")
            log_info "重启服务..."
            docker-compose restart
            health_check
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "status")
            show_status
            ;;
        "backup")
            backup_database
            ;;
        "cleanup")
            cleanup_images
            ;;
        "rollback")
            rollback $2
            ;;
        "health")
            health_check
            ;;
        *)
            echo "用法: $0 {deploy|update|stop|restart|logs|status|backup|cleanup|rollback|health} [version]"
            exit 1
            ;;
    esac
}

# 脚本入口
main "$@"
```

### 监控和日志管理

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  # Prometheus监控
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - monitoring

  # Grafana可视化
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    depends_on:
      - prometheus
    networks:
      - monitoring

  # Node Exporter系统监控
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - monitoring

  # cAdvisor容器监控
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    networks:
      - monitoring

  # ELK Stack日志收集
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    container_name: elasticsearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - monitoring

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    container_name: logstash
    restart: unless-stopped
    ports:
      - "5044:5044"
    volumes:
      - ./monitoring/logstash/pipeline:/usr/share/logstash/pipeline:ro
      - ./monitoring/logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml:ro
    depends_on:
      - elasticsearch
    networks:
      - monitoring

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    container_name: kibana
    restart: unless-stopped
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
  elasticsearch_data:
```

## 最佳实践

### 配置管理
- **环境分离**: 开发、测试、生产环境分别配置
- **变量管理**: 使用环境变量管理敏感信息
- **版本控制**: 镜像版本标签化管理
- **配置验证**: 启动前验证配置正确性

### 服务设计
- **单一职责**: 每个容器只运行一个主进程
- **无状态设计**: 服务无状态，便于水平扩展
- **优雅关闭**: 处理SIGTERM信号
- **健康检查**: 实现健康检查端点

### 网络安全
- **网络隔离**: 使用自定义网络隔离服务
- **最小权限**: 只开放必要的端口
- **内部通信**: 敏感服务使用内部网络
- **SSL/TLS**: 生产环境启用HTTPS

### 资源优化
- **资源限制**: 设置CPU和内存限制
- **日志管理**: 配置日志轮转和清理
- **镜像优化**: 使用多阶段构建减小镜像大小
- **缓存策略**: 合理使用Docker层缓存

## 相关技能

- [Git工作流管理](./git-workflows/) - 容器化部署流程
- [API文档生成](./api-documentation/) - 服务接口文档
- [版本管理器](./version-manager/) - 版本发布管理
- [安全扫描器](./security-scanner/) - 容器安全检查
