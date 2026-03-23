# Kubernetes基础参考文档

## 核心概念

### Kubernetes架构

#### 集群组件
- **Master节点**:
  - **API Server**: 集群控制中心，提供RESTful API
  - **etcd**: 分布式键值存储，保存集群状态
  - **Scheduler**: 负责Pod调度到合适的节点
  - **Controller Manager**: 运行各种控制器
- **Worker节点**:
  - **kubelet**: 节点代理，管理Pod生命周期
  - **kube-proxy**: 网络代理，实现Service负载均衡
  - **Container Runtime**: 容器运行时 (Docker/containerd)

#### 工作流程
```
用户请求 → API Server → Controller Manager → Scheduler → Kubelet → Container Runtime
```

### 核心资源对象

#### Pod
- **定义**: Kubernetes中最小的部署单元
- **特点**: 
  - 共享网络和存储
  - 生命周期短暂
  - 包含一个或多个容器
- **YAML示例**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.20
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

#### Service
- **定义**: 为一组Pod提供稳定的网络访问
- **类型**:
  - **ClusterIP**: 集群内部访问
  - **NodePort**: 通过节点端口访问
  - **LoadBalancer**: 通过外部负载均衡器访问
  - **ExternalName**: 映射到外部DNS名称
- **YAML示例**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
```

#### Deployment
- **定义**: 声明式管理Pod和ReplicaSet
- **功能**:
  - 滚动更新
  - 回滚
  - 扩缩容
  - 停机维护
- **YAML示例**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 资源管理

### 资源请求和限制

#### CPU资源
- **单位**:
  - **1 CPU**: 1个vCPU/core
  - **500m**: 0.5个CPU
  - **100m**: 0.1个CPU (最小单位)
- **配置示例**:
```yaml
resources:
  requests:
    cpu: "100m"    # 请求0.1个CPU
  limits:
    cpu: "500m"    # 限制0.5个CPU
```

#### 内存资源
- **单位**:
  - **Ki**: Kibibyte (1024字节)
  - **Mi**: Mebibyte (1024 Ki)
  - **Gi**: Gibibyte (1024 Mi)
- **配置示例**:
```yaml
resources:
  requests:
    memory: "64Mi"   # 请求64MB内存
  limits:
    memory: "128Mi"  # 限制128MB内存
```

#### 资源质量
- **Guaranteed**: requests == limits (保证质量)
- **Burstable**: 有requests且requests < limits (可突发)
- **BestEffort**: 没有requests和limits (尽力而为)

### 存储管理

#### Volume类型
- **emptyDir**: Pod生命周期内临时存储
- **hostPath**: 主机文件系统路径
- **configMap**: 配置文件存储
- **secret**: 敏感信息存储
- **persistentVolumeClaim**: 持久存储

#### PersistentVolume (PV)
- **静态PV**: 预先创建的存储卷
- **动态PV**: 基于StorageClass动态创建
- **访问模式**:
  - **ReadWriteOnce (RWO)**: 单节点读写
  - **ReadOnlyMany (ROX)**: 多节点只读
  - **ReadWriteMany (RWX)**: 多节点读写

#### StorageClass配置
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
reclaimPolicy: Delete
allowVolumeExpansion: true
```

## 网络配置

### 网络模型

#### Pod网络
- **IP地址**: 每个Pod获得唯一的IP地址
- **网络命名空间**: Pod内容器共享网络命名空间
- **CNI插件**: 容器网络接口 (Flannel、Calico、Weave)

#### Service网络
- **ClusterIP**: 虚拟IP，仅在集群内可访问
- **kube-proxy**: 实现Service负载均衡
- **代理模式**:
  - **iptables**: 基于iptables规则
  - **ipvs**: 基于IPVS负载均衡
  - **userspace**: 用户空间代理

### Ingress配置

#### Ingress Controller
- **nginx-ingress**: 基于Nginx的Ingress控制器
- **traefik**: 现代化的反向代理和负载均衡器
- **istio-ingressgateway**: Service Mesh网关

#### Ingress规则配置
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - example.com
    secretName: tls-secret
  rules:
  - host: example.com
    http:
      paths:
      - path: /app
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
```

### 网络策略

#### 网络隔离
- **默认拒绝**: 默认情况下Pod间网络通信被拒绝
- **选择性允许**: 通过NetworkPolicy允许特定流量
- **标签选择器**: 基于Pod标签控制网络访问

#### 网络策略示例
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

## 安全配置

### RBAC (基于角色的访问控制)

#### 核心组件
- **ServiceAccount**: Pod使用的身份
- **Role**: 命名空间级别的权限
- **ClusterRole**: 集群级别的权限
- **RoleBinding**: 角色绑定到用户/服务账户
- **ClusterRoleBinding**: 集群角色绑定

#### Role配置示例
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### 安全上下文

#### Pod安全上下文
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    runAsNonRoot: true
  containers:
  - name: secure-container
    image: nginx:1.20
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
```

#### Pod安全策略
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## 配置管理

### ConfigMap

#### 创建ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app.properties: |
    database.url=jdbc:mysql://localhost:3306/mydb
    database.username=admin
    database.password=secret
  log4j.properties: |
    log4j.rootLogger=INFO, stdout
    log4j.appender.stdout=org.apache.log4j.ConsoleAppender
```

#### 使用ConfigMap
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    envFrom:
    - configMapRef:
        name: app-config
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

### Secret

#### 创建Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=  # admin (base64)
  password: c2VjcmV0  # secret (base64)
```

#### 使用Secret
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
```

## 监控和日志

### 健康检查

#### 存活探针 (Liveness Probe)
- **目的**: 检测容器是否存活
- **失败处理**: 重启容器
- **配置方式**:
  - **HTTP GET**: 检查HTTP端点
  - **TCP Socket**: 检查TCP端口
  - **Exec**: 执行命令

#### 就绪探针 (Readiness Probe)
- **目的**: 检测容器是否就绪
- **失败处理**: 从Service端点移除
- **配置方式**: 与存活探针相同

#### 探针配置示例
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### 监控指标

#### Prometheus监控
```yaml
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  labels:
    app: prometheus
spec:
  ports:
  - port: 9090
    targetPort: 9090
  selector:
    app: prometheus
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
```

#### 自定义指标
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

## 故障排查

### 常见问题

#### Pod启动失败
- **查看Pod状态**: `kubectl get pods`
- **查看Pod详情**: `kubectl describe pod <pod-name>`
- **查看Pod日志**: `kubectl logs <pod-name>`
- **常见原因**:
  - 镜像拉取失败
  - 资源不足
  - 配置错误
  - 健康检查失败

#### 网络问题
- **查看Service**: `kubectl get svc`
- **查看Endpoints**: `kubectl get endpoints`
- **网络连通性测试**: `kubectl exec -it <pod> -- ping <target>`
- **常见原因**:
  - Service配置错误
  - 网络策略阻止
  - DNS解析问题
  - 防火墙规则

#### 存储问题
- **查看PV**: `kubectl get pv`
- **查看PVC**: `kubectl get pvc`
- **查看存储类**: `kubectl get storageclass`
- **常见原因**:
  - 存储容量不足
  - 访问模式不匹配
  - 存储类配置错误

### 调试命令

#### Pod调试
```bash
# 查看Pod状态
kubectl get pods -o wide

# 查看Pod详情
kubectl describe pod <pod-name>

# 查看Pod日志
kubectl logs <pod-name>

# 进入Pod内部
kubectl exec -it <pod-name> -- /bin/bash

# 端口转发
kubectl port-forward <pod-name> 8080:80
```

#### 资源调试
```bash
# 查看所有资源
kubectl api-resources

# 查看集群事件
kubectl get events --sort-by=.metadata.creationTimestamp

# 查看节点状态
kubectl get nodes -o wide

# 查看集群信息
kubectl cluster-info
```

## 最佳实践

### 资源配置

#### CPU和内存配置
- **设置requests**: 确保Pod获得基本资源
- **设置limits**: 防止资源耗尽
- **监控使用率**: 根据实际使用调整配置
- **资源质量**: 优先使用Guaranteed质量

#### 存储配置
- **使用PVC**: 避免直接使用hostPath
- **设置存储类**: 选择合适的存储类型
- **备份策略**: 重要数据需要备份
- **容量规划**: 预留足够的存储空间

### 安全配置

#### 网络安全
- **启用NetworkPolicy**: 默认拒绝所有流量
- **最小权限原则**: 只开放必要的端口
- **TLS加密**: 敏感数据传输使用HTTPS
- **防火墙规则**: 配置适当的防火墙规则

#### 访问控制
- **使用RBAC**: 基于角色的访问控制
- **ServiceAccount**: 为Pod分配专用身份
- **最小权限**: 只授予必要的权限
- **定期审计**: 定期检查权限配置

### 运维配置

#### 健康检查
- **配置探针**: 设置存活和就绪探针
- **合理超时**: 设置适当的超时时间
- **检查间隔**: 避免过于频繁的检查
- **失败阈值**: 设置合理的失败阈值

#### 监控告警
- **关键指标**: 监控CPU、内存、网络、存储
- **告警规则**: 设置合理的告警阈值
- **日志收集**: 集中收集和分析日志
- **性能分析**: 定期分析性能数据

## 参考资源

### 官方文档
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [Kubernetes GitHub](https://github.com/kubernetes/kubernetes)

### 学习资源
- [Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [Kubernetes Patterns](https://kubernetespatterns.io/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/cluster-administration/)

### 工具和插件
- [kubectl](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands/)
- [Helm](https://helm.sh/)
- [Kustomize](https://kustomize.io/)
- [Lens](https://k8slens.dev/)

### 社区资源
- [Kubernetes Community](https://kubernetes.io/community/)
- [CNCF](https://www.cncf.io/)
- [Kubernetes Blog](https://kubernetes.io/blog/)
