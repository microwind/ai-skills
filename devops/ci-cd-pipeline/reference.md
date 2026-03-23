# CI/CD流水线参考文档

## CI/CD基础概念

### 持续集成 (Continuous Integration)
- **定义**: 开发人员频繁地将代码集成到主干分支
- **核心原则**:
  - 频繁提交代码
  - 自动化构建和测试
  - 快速反馈机制
  - 保持代码库健康
- **价值**: 减少集成风险，提高代码质量，加快交付速度

### 持续交付 (Continuous Delivery)
- **定义**: 自动化构建、测试和部署到预生产环境
- **核心原则**:
  - 自动化部署流程
  - 环境一致性
  - 随时可发布
  - 手动触发生产部署
- **价值**: 降低部署风险，提高发布频率

### 持续部署 (Continuous Deployment)
- **定义**: 自动化部署到生产环境
- **核心原则**:
  - 完全自动化流程
  - 自动化测试覆盖
  - 监控和回滚机制
  - 渐进式发布
- **价值**: 最快交付速度，快速反馈循环

## 流水线设计模式

### 流水线阶段设计

#### 基础流水线结构
```yaml
# GitLab CI/CD 示例
stages:
  - build
  - test
  - security
  - deploy

variables:
  NODE_VERSION: "18"
  DOCKER_REGISTRY: "registry.example.com"

build:
  stage: build
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour

test:
  stage: test
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npm run test:unit
    - npm run test:e2e
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

security:
  stage: security
  image: owasp/zap2docker-stable
  script:
    - mkdir -p /zap/wrk/
    - /zap/zap-baseline.py -t http://example.com -J gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json

deploy:
  stage: deploy
  image: docker:latest
  script:
    - docker build -t ${DOCKER_REGISTRY}/myapp:${CI_COMMIT_SHA} .
    - docker push ${DOCKER_REGISTRY}/myapp:${CI_COMMIT_SHA}
    - kubectl set image deployment/myapp myapp=${DOCKER_REGISTRY}/myapp:${CI_COMMIT_SHA}
  only:
    - main
```

#### GitHub Actions 示例
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm run test:coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info

  security-scan:
    runs-on: ubuntu-latest
    needs: build-and-test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  deploy:
    runs-on: ubuntu-latest
    needs: [build-and-test, security-scan]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          myapp:latest
          myapp:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
```

### Jenkins Pipeline 示例

#### Declarative Pipeline
```groovy
pipeline {
    agent any
    
    environment {
        NODE_VERSION = '18'
        DOCKER_REGISTRY = 'registry.example.com'
        APP_NAME = 'myapp'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            agent {
                docker {
                    image "node:${NODE_VERSION}"
                }
            }
            steps {
                sh 'npm ci'
                sh 'npm run build'
            }
            post {
                success {
                    archiveArtifacts artifacts: 'dist/**', fingerprint: true
                }
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    agent {
                        docker {
                            image "node:${NODE_VERSION}"
                        }
                    }
                    steps {
                        sh 'npm run test:unit'
                        publishTestResults testResultsPattern: 'test-results.xml'
                        publishCoverage adapters: [coberturaAdapter('coverage/cobertura-coverage.xml')]
                    }
                }
                
                stage('E2E Tests') {
                    agent {
                        docker {
                            image "node:${NODE_VERSION}"
                        }
                    }
                    steps {
                        sh 'npm run test:e2e'
                        publishHTML([
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: 'e2e-report',
                            reportFiles: 'index.html',
                            reportName: 'E2E Test Report'
                        ])
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                script {
                    sh 'npm audit --audit-level high'
                    sh 'docker build -t ${APP_NAME}:${BUILD_NUMBER} .'
                    sh 'trivy image --format json --output trivy-report.json ${APP_NAME}:${BUILD_NUMBER}'
                    archiveArtifacts artifacts: 'trivy-report.json', fingerprint: true
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        sh "docker tag ${APP_NAME}:${BUILD_NUMBER} ${DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}"
                        sh "docker push ${DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}"
                    }
                    
                    withKubeConfig([name: 'kubeconfig']) {
                        sh "kubectl set image deployment/${APP_NAME} ${APP_NAME}=${DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}"
                        sh "kubectl rollout status deployment/${APP_NAME}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            slackSend(
                channel: '#ci-cd',
                color: 'good',
                message: "✅ ${env.JOB_NAME} - ${env.BUILD_NUMBER} 构建成功"
            )
        }
        failure {
            slackSend(
                channel: '#ci-cd',
                color: 'danger',
                message: "❌ ${env.JOB_NAME} - ${env.BUILD_NUMBER} 构建失败"
            )
        }
    }
}
```

## 构建优化策略

### 构建缓存优化

#### Maven构建缓存
```yaml
# GitLab CI/CD Maven缓存
variables:
  MAVEN_OPTS: "-Dmaven.repo.local=${CI_PROJECT_DIR}/.m2/repository"

cache:
  paths:
    - .m2/repository/
    - target/

build:
  stage: build
  script:
    - mvn clean compile
```

#### npm/yarn缓存
```yaml
# Node.js依赖缓存
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/
    - .npm/
    - .yarn/

build:
  stage: build
  before_script:
    - npm ci --cache .npm --prefer-offline
  script:
    - npm run build
```

#### Docker多阶段构建
```dockerfile
# 多阶段Dockerfile优化
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# 生产镜像
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 并行构建优化

#### 矩阵构建策略
```yaml
# GitHub Actions矩阵构建
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node-version: [16.x, 18.x, 20.x]
    include:
      - os: ubuntu-latest
        node-version: 20.x
        coverage: true
      - os: windows-latest
        node-version: 18.x
        windows: true

jobs:
  build:
    runs-on: ${{ matrix.os }}
    steps:
    - uses: actions/checkout@v3
    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
    - name: Install dependencies
      run: npm ci
    - name: Build
      run: npm run build
    - name: Test
      run: npm test
    - name: Coverage
      if: matrix.coverage
      run: npm run coverage
```

## 测试策略

### 测试金字塔

#### 测试分层策略
```
    /\
   /  \     E2E Tests (少量)
  /____\    
 /        \   Integration Tests (适量)
/__________\ Unit Tests (大量)
```

#### 测试配置示例
```yaml
test:
  stage: test
  parallel: 4
  
  script:
    - echo "Running tests in parallel"
    - npm run test:unit
    - npm run test:integration
    - npm run test:e2e
  
  artifacts:
    when: always
    reports:
      junit: test-results/**/*.xml
    paths:
      - coverage/
      - test-reports/
    expire_in: 1 week
  
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  
  only:
    - merge_requests
    - main
    - develop
```

### 测试环境管理

#### Docker Compose测试环境
```yaml
# docker-compose.test.yml
version: '3.8'

services:
  app:
    build: .
    environment:
      - NODE_ENV=test
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    command: npm run test:integration

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=testdb
      - POSTGRES_USER=testuser
      - POSTGRES_PASSWORD=testpass
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

#### Testcontainers集成
```java
// Java Testcontainers示例
@Testcontainers
@SpringBootTest
public class IntegrationTest {
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("testuser")
            .withPassword("testpass");
    
    @Container
    static GenericContainer<?> redis = new GenericContainer<>("redis:7")
            .withExposedPorts(6379);
    
    @Test
    void testDatabaseConnection() {
        // 测试代码
    }
}
```

## 部署策略

### 蓝绿部署

#### Kubernetes蓝绿部署
```yaml
# blue-green-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  replicas: 3
  strategy:
    blueGreen:
      activeService: myapp-active
      previewService: myapp-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
      prePromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: myapp-preview
      postPromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: myapp-active
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-active
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-preview
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
```

### 滚动更新

#### Kubernetes滚动更新配置
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2        # 最多额外创建2个Pod
      maxUnavailable: 1   # 最多1个Pod不可用
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

### 金丝雀发布

#### Istio金丝雀发布
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
  - myapp
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: myapp
        subset: v2
      weight: 100
  - route:
    - destination:
        host: myapp
        subset: v1
      weight: 90
    - destination:
        host: myapp
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

## 监控和告警

### 流水线监控

#### Prometheus监控指标
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'jenkins'
    static_configs:
      - targets: ['jenkins:8080']
    metrics_path: '/prometheus'
    
  - job_name: 'gitlab-runner'
    static_configs:
      - targets: ['gitlab-runner:9252']
      
  - job_name: 'github-actions'
    static_configs:
      - targets: ['github-actions-metrics:8080']
```

#### Grafana仪表板
```json
{
  "dashboard": {
    "title": "CI/CD Pipeline Monitoring",
    "panels": [
      {
        "title": "Build Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(jenkins_builds_success_total[5m])) / sum(rate(jenkins_builds_total[5m])) * 100"
          }
        ]
      },
      {
        "title": "Build Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(jenkins_builds_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

### 告警规则

#### Alertmanager配置
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alerts@example.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#ci-cd-alerts'
    title: 'CI/CD Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

inhibit_rules:
- source_match:
    severity: 'critical'
  target_match:
    severity: 'warning'
  equal: ['alertname', 'dev', 'instance']
```

## 安全最佳实践

### 密钥管理

#### Kubernetes Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ci-cd-secrets
type: Opaque
data:
  docker-username: <base64-encoded-username>
  docker-password: <base64-encoded-password>
  github-token: <base64-encoded-token>
  kubeconfig: <base64-encoded-kubeconfig>
```

#### Vault集成
```yaml
# GitLab CI/CD with Vault
variables:
  VAULT_SERVER_URL: "https://vault.example.com"
  VAULT_AUTH_ROLE: "gitlab-ci"

secrets:
  DATABASE_PASSWORD:
    vault: database/password@secret
    file: false
  API_KEY:
    vault: api/key@secret
    file: false
```

### 安全扫描

#### SonarQube集成
```yaml
sonarqube-check:
  stage: test
  image: sonarsource/sonar-scanner-cli:latest
  variables:
    SONAR_HOST_URL: "https://sonarqube.example.com"
    SONAR_PROJECT_KEY: "myapp"
    SONAR_ORGANIZATION: "myorg"
  script:
    - sonar-scanner
      -Dsonar.projectKey=$SONAR_PROJECT_KEY
      -Dsonar.organization=$SONAR_ORGANIZATION
      -Dsonar.host.url=$SONAR_HOST_URL
      -Dsonar.login=$SONAR_TOKEN
  only:
    - merge_requests
    - main
```

#### OWASP ZAP扫描
```yaml
security-scan:
  stage: security
  image: owasp/zap2docker-stable
  script:
    - mkdir -p /zap/wrk/
    - /zap/zap-baseline.py
        -t http://example.com
        -J gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json
  allow_failure: true
```

## 故障排查

### 常见问题

#### 构建失败排查
```bash
# 查看构建日志
kubectl logs -f deployment/jenkins

# 检查构建状态
gitlab-ci-multi-runner status

# 查看GitHub Actions日志
gh run view --log

# 清理构建缓存
docker system prune -a
```

#### 部署失败排查
```bash
# 查看部署状态
kubectl get deployments
kubectl describe deployment myapp

# 查看Pod日志
kubectl logs -f deployment/myapp

# 回滚部署
kubectl rollout undo deployment/myapp

# 查看事件
kubectl get events --sort-by=.metadata.creationTimestamp
```

### 性能优化

#### 构建性能优化
```yaml
# 并行构建
variables:
  MAVEN_OPTS: "-Dmaven.test.failure.ignore=true -Dmaven.repo.local=${CI_PROJECT_DIR}/.m2/repository"
  GRADLE_OPTS: "-Dorg.gradle.daemon=false -Dorg.gradle.workers.max=2"

# 缓存优化
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .m2/
    - .gradle/
    - node_modules/
    - .npm/
```

#### 部署性能优化
```yaml
# 资源限制
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

# 健康检查优化
readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

## 参考资源

### 官方文档
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Argo CD Documentation](https://argoproj.github.io/argo-cd/)

### 最佳实践指南
- [CI/CD Best Practices](https://about.gitlab.com/topics/ci-cd/)
- [Kubernetes Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### 工具和插件
- [Helm](https://helm.sh/) - Kubernetes包管理器
- [Kustomize](https://kustomize.io/) - Kubernetes配置管理
- [Terraform](https://www.terraform.io/) - 基础设施即代码
- [Ansible](https://www.ansible.com/) - 自动化配置管理

### 社区资源
- [CNCF Landscape](https://landscape.cncf.io/)
- [DevOps Roadmap](https://roadmap.sh/devops)
- [Awesome CI/CD](https://github.com/ligurio/awesome-cicd)
