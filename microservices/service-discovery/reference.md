# 服务发现参考文档

## 服务发现概述

### 什么是服务发现
服务发现是微服务架构中的核心组件，用于自动检测和定位网络中的服务实例。它允许服务之间动态地找到彼此，而不需要硬编码的网络地址。

### 服务发现的类型

#### 客户端发现
客户端负责查询服务注册表，选择可用的服务实例，并发起请求。

```python
# 客户端发现示例
import requests
import random
from typing import List, Dict

class ClientDiscovery:
    def __init__(self, registry_url: str):
        self.registry_url = registry_url
        self.service_cache = {}
        self.cache_ttl = 30  # 缓存30秒
    
    def get_service_instances(self, service_name: str) -> List[Dict]:
        """获取服务实例列表"""
        # 检查缓存
        if service_name in self.service_cache:
            cache_entry = self.service_cache[service_name]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['instances']
        
        # 从注册中心获取
        try:
            response = requests.get(f"{self.registry_url}/services/{service_name}")
            if response.status_code == 200:
                instances = response.json()
                # 更新缓存
                self.service_cache[service_name] = {
                    'instances': instances,
                    'timestamp': time.time()
                }
                return instances
        except Exception as e:
            print(f"获取服务实例失败: {e}")
            # 返回缓存中的实例（如果存在）
            if service_name in self.service_cache:
                return self.service_cache[service_name]['instances']
        
        return []
    
    def discover_service(self, service_name: str) -> Dict:
        """发现一个服务实例"""
        instances = self.get_service_instances(service_name)
        if not instances:
            raise Exception(f"服务 {service_name} 没有可用实例")
        
        # 负载均衡：随机选择
        return random.choice(instances)
    
    def call_service(self, service_name: str, endpoint: str, method='GET', data=None):
        """调用服务"""
        instance = self.discover_service(service_name)
        url = f"{instance['url']}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)
            else:
                response = requests.request(method, url, json=data)
            
            return response.json()
        except Exception as e:
            # 标记实例为不健康
            self.mark_instance_unhealthy(service_name, instance['id'])
            raise e
    
    def mark_instance_unhealthy(self, service_name: str, instance_id: str):
        """标记实例为不健康"""
        try:
            requests.post(f"{self.registry_url}/services/{service_name}/instances/{instance_id}/unhealthy")
        except Exception as e:
            print(f"标记实例不健康失败: {e}")

# 使用示例
discovery = ClientDiscovery("http://registry-server:8080")

# 调用用户服务
try:
    user_data = discovery.call_service("user-service", "/users/123")
    print(f"用户数据: {user_data}")
except Exception as e:
    print(f"调用用户服务失败: {e}")
```

#### 服务端发现
客户端将请求发送到负载均衡器或API网关，由其负责请求路由。

```python
# 服务端发现示例
from flask import Flask, request, jsonify
import requests
import random

app = Flask(__name__)

class ServerDiscovery:
    def __init__(self):
        self.registry_url = "http://registry-server:8080"
        self.load_balancer = LoadBalancer()
    
    def route_request(self, service_name: str, path: str):
        """路由请求到服务实例"""
        instances = self.get_service_instances(service_name)
        if not instances:
            return jsonify({"error": "服务不可用"}), 503
        
        # 选择实例
        instance = self.load_balancer.select_instance(instances)
        
        # 转发请求
        try:
            url = f"{instance['url']}{path}"
            response = requests.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                data=request.get_data(),
                params=request.args
            )
            
            return response.content, response.status_code, dict(response.headers)
        except Exception as e:
            # 标记实例为不健康
            self.mark_instance_unhealthy(service_name, instance['id'])
            return jsonify({"error": "服务调用失败"}), 500
    
    def get_service_instances(self, service_name: str):
        """获取服务实例"""
        try:
            response = requests.get(f"{self.registry_url}/services/{service_name}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"获取服务实例失败: {e}")
        return []
    
    def mark_instance_unhealthy(self, service_name: str, instance_id: str):
        """标记实例为不健康"""
        try:
            requests.post(f"{self.registry_url}/services/{service_name}/instances/{instance_id}/unhealthy")
        except Exception as e:
            print(f"标记实例不健康失败: {e}")

class LoadBalancer:
    def select_instance(self, instances):
        """负载均衡选择实例"""
        # 简单的轮询算法
        return random.choice(instances)

@app.route('/<service_name>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_request(service_name, path):
    discovery = ServerDiscovery()
    return discovery.route_request(service_name, path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

## Eureka服务发现

### Eureka Server配置

#### Spring Boot Eureka Server
```java
// EurekaServerApplication.java
@SpringBootApplication
@EnableEurekaServer
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}

// application.yml
server:
  port: 8761

eureka:
  instance:
    hostname: localhost
  client:
    register-with-eureka: false
    fetch-registry: false
    service-url:
      defaultZone: http://${eureka.instance.hostname}:${server.port}/eureka/
  server:
    enable-self-preservation: false
    eviction-interval-timer-in-ms: 5000
    renewal-percent-threshold: 0.85

spring:
  application:
    name: eureka-server
```

#### Eureka Server高可用配置
```yaml
# application-peer1.yml
server:
  port: 8761

eureka:
  instance:
    hostname: peer1
  client:
    service-url:
      defaultZone: http://peer2:8762/eureka/
    register-with-eureka: true
    fetch-registry: true

spring:
  application:
    name: eureka-server
  profiles: peer1

---
# application-peer2.yml
server:
  port: 8762

eureka:
  instance:
    hostname: peer2
  client:
    service-url:
      defaultZone: http://peer1:8761/eureka/
    register-with-eureka: true
    fetch-registry: true

spring:
  application:
    name: eureka-server
  profiles: peer2
```

### Eureka Client配置

#### Spring Boot Eureka Client
```java
// UserServiceApplication.java
@SpringBootApplication
@EnableEurekaClient
@RestController
public class UserServiceApplication {
    
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable String id) {
        // 业务逻辑
        return new User(id, "John Doe", "john@example.com");
    }
    
    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
    }
}

// application.yml
server:
  port: 8080

spring:
  application:
    name: user-service

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
    register-with-eureka: true
    fetch-registry: true
    registry-fetch-interval-seconds: 30
  instance:
    prefer-ip-address: true
    lease-renewal-interval-in-seconds: 30
    lease-expiration-duration-in-seconds: 90
    metadata-map:
      version: 1.0.0
      environment: production

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: always
```

#### 服务间调用
```java
// OrderServiceApplication.java
@SpringBootApplication
@EnableEurekaClient
@RestController
public class OrderServiceApplication {
    
    @Autowired
    private DiscoveryClient discoveryClient;
    
    @Autowired
    private RestTemplate restTemplate;
    
    @GetMapping("/orders/{id}/user")
    public User getOrderUser(@PathVariable String id) {
        // 使用服务名调用
        String userServiceUrl = "http://user-service/users/" + id;
        return restTemplate.getForObject(userServiceUrl, User.class);
    }
    
    @GetMapping("/service-instances")
    public List<ServiceInstance> getServiceInstances() {
        return discoveryClient.getInstances("user-service");
    }
    
    @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
    
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}

// application.yml
server:
  port: 8081

spring:
  application:
    name: order-service

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    prefer-ip-address: true

# 启用Ribbon负载均衡
ribbon:
  eureka:
    enabled: true
```

## Consul服务发现

### Consul配置

#### Docker部署Consul
```bash
# 启动Consul
docker run -d --name consul \
    -p 8500:8500 \
    -p 8600:8600/udp \
    -e CONSUL_BIND_INTERFACE=eth0 \
    consul agent -server -ui -node=server-1 -bootstrap-expect=1 -client=0.0.0.0
```

#### Spring Boot Consul集成
```java
// ConsulApplication.java
@SpringBootApplication
@EnableDiscoveryClient
@RestController
public class ConsulApplication {
    
    @Value("${spring.application.name}")
    private String serviceName;
    
    @GetMapping("/info")
    public Map<String, String> info() {
        return Map.of(
            "service", serviceName,
            "timestamp", Instant.now().toString()
        );
    }
    
    public static void main(String[] args) {
        SpringApplication.run(ConsulApplication.class, args);
    }
}

// application.yml
server:
  port: 8080

spring:
  application:
    name: consul-service
  cloud:
    consul:
      host: localhost
      port: 8500
      discovery:
        service-name: ${spring.application.name}
        health-check-path: /actuator/health
        health-check-interval: 15s
        prefer-ip-address: true
        instance-id: ${spring.application.name}:${spring.cloud.client.ip-address}:${server.port}
        metadata:
          version: 1.0.0
          environment: production

management:
  endpoints:
    web:
      exposure:
        include: health,info
  endpoint:
    health:
      show-details: always
```

#### Go语言Consul客户端
```go
// main.go
package main

import (
    "fmt"
    "log"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    consulapi "github.com/hashicorp/consul/api"
)

type ServiceRegistry struct {
    consul *consulapi.Client
}

func NewServiceRegistry(consulAddr string) (*ServiceRegistry, error) {
    config := consulapi.DefaultConfig()
    config.Address = consulAddr
    
    client, err := consulapi.NewClient(config)
    if err != nil {
        return nil, err
    }
    
    return &ServiceRegistry{consul: client}, nil
}

func (sr *ServiceRegistry) Register(serviceName, serviceID, address string, port int) error {
    registration := &consulapi.AgentServiceRegistration{
        ID:      serviceID,
        Name:    serviceName,
        Address: address,
        Port:    port,
        Check: &consulapi.AgentServiceCheck{
            HTTP:     fmt.Sprintf("http://%s:%d/health", address, port),
            Interval: "10s",
            Timeout:  "3s",
        },
    }
    
    return sr.consul.Agent().ServiceRegister(registration)
}

func (sr *ServiceRegistry) Discover(serviceName string) ([]*consulapi.ServiceEntry, error) {
    services, _, err := sr.consul.Health().Service(serviceName, "", true, nil)
    return services, err
}

func (sr *ServiceRegistry) Deregister(serviceID string) error {
    return sr.consul.Agent().ServiceDeregister(serviceID)
}

func main() {
    // 连接Consul
    registry, err := NewServiceRegistry("localhost:8500")
    if err != nil {
        log.Fatal(err)
    }
    
    // 注册服务
    serviceName := "go-service"
    serviceID := "go-service-1"
    address := "localhost"
    port := 8080
    
    err = registry.Register(serviceName, serviceID, address, port)
    if err != nil {
        log.Fatal(err)
    }
    
    // 延迟注册
    time.Sleep(2 * time.Second)
    
    // 设置路由
    r := gin.Default()
    
    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "healthy"})
    })
    
    r.GET("/services/:name", func(c *gin.Context) {
        name := c.Param("name")
        services, err := registry.Discover(name)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }
        
        c.JSON(200, gin.H{"services": services})
    })
    
    // 启动服务
    go func() {
        log.Fatal(r.Run(":8080"))
    }()
    
    // 优雅关闭
    defer registry.Deregister(serviceID)
    
    // 测试服务发现
    services, err := registry.Discover(serviceName)
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("发现的服务: %+v\n", services)
    
    // 保持运行
    select {}
}
```

## Zookeeper服务发现

### Zookeeper配置

#### Docker部署Zookeeper
```bash
# 启动Zookeeper
docker run -d --name zookeeper \
    -p 2181:2181 \
    -p 2888:2888 \
    -p 3888:3888 \
    zookeeper:3.8
```

#### Java Zookeeper客户端
```java
// ZookeeperServiceRegistry.java
@Component
public class ZookeeperServiceRegistry {
    
    private CuratorFramework client;
    private String servicePath = "/services";
    
    public ZookeeperServiceRegistry() {
        // 创建Zookeeper客户端
        client = CuratorFrameworkFactory.newClient(
            "localhost:2181",
            new ExponentialBackoffRetry(1000, 3)
        );
        client.start();
        
        try {
            // 创建服务根节点
            if (client.checkExists().forPath(servicePath) == null) {
                client.create().creatingParentsIfNeeded().forPath(servicePath);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public void registerService(String serviceName, String serviceUrl) throws Exception {
        String serviceInstancePath = servicePath + "/" + serviceName + "/instance";
        
        // 创建临时节点
        client.create()
            .withMode(CreateMode.EPHEMERAL)
            .forPath(serviceInstancePath, serviceUrl.getBytes());
    }
    
    public List<String> discoverServices(String serviceName) throws Exception {
        String servicePath = this.servicePath + "/" + serviceName;
        
        if (client.checkExists().forPath(servicePath) == null) {
            return Collections.emptyList();
        }
        
        return client.getChildren().forPath(servicePath);
    }
    
    public void watchService(String serviceName, NodeCacheListener listener) throws Exception {
        String servicePath = this.servicePath + "/" + serviceName;
        
        NodeCache cache = new NodeCache(client, servicePath, false);
        cache.getListenableable().addListener(listener);
        cache.start(true);
    }
}

// ZookeeperController.java
@RestController
public class ZookeeperController {
    
    @Autowired
    private ZookeeperServiceRegistry registry;
    
    @PostMapping("/register")
    public ResponseEntity<String> registerService(
            @RequestParam String serviceName,
            @RequestParam String serviceUrl) {
        try {
            registry.registerService(serviceName, serviceUrl);
            return ResponseEntity.ok("服务注册成功");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("注册失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/discover/{serviceName}")
    public ResponseEntity<List<String>> discoverServices(@PathVariable String serviceName) {
        try {
            List<String> services = registry.discoverServices(serviceName);
            return ResponseEntity.ok(services);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Collections.emptyList());
        }
    }
}
```

## Kubernetes服务发现

### Kubernetes Service配置

#### ClusterIP Service
```yaml
# user-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  type: ClusterIP
  selector:
    app: user-service
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  labels:
    app: user-service
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
        - containerPort: 8080
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "kubernetes"
```

#### Headless Service
```yaml
# user-service-headless.yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service-headless
  labels:
    app: user-service
spec:
  type: ClusterIP
  clusterIP: None  # Headless Service
  selector:
    app: user-service
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
```

#### NodePort Service
```yaml
# user-service-nodeport.yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service-nodeport
  labels:
    app: user-service
spec:
  type: NodePort
  selector:
    app: user-service
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
      protocol: TCP
```

### Kubernetes服务发现实现

#### Java Kubernetes客户端
```java
// KubernetesServiceDiscovery.java
@Component
public class KubernetesServiceDiscovery {
    
    @Value("${kubernetes.namespace:default}")
    private String namespace;
    
    private ApiClient client;
    private CoreV1Api api;
    
    public KubernetesServiceDiscovery() {
        try {
            // 配置Kubernetes客户端
            Config config = Config.fromCluster();
            client = ClientBuilder.kubeconfig(config).build();
            api = new CoreV1Api(client);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public List<String> getServiceEndpoints(String serviceName) throws Exception {
        V1Service service = api.readNamespacedService(serviceName, namespace, null);
        
        if (service.getSpec().getType().equals("ClusterIP")) {
            // ClusterIP服务
            return Arrays.asList(service.getSpec().getClusterIP() + ":" + 
                              service.getSpec().getPorts().get(0).getPort());
        } else if (service.getSpec().getType().equals("NodePort")) {
            // NodePort服务
            V1NodeList nodes = api.listNode(null, null, null, null, null, null, null, null, null, null);
            List<String> endpoints = new ArrayList<>();
            
            for (V1Node node : nodes.getItems()) {
                String nodeIP = node.getStatus().getAddresses().get(0).getAddress();
                int nodePort = service.getSpec().getPorts().get(0).getNodePort();
                endpoints.add(nodeIP + ":" + nodePort);
            }
            
            return endpoints;
        }
        
        return Collections.emptyList();
    }
    
    public List<String> getPodEndpoints(String serviceName) throws Exception {
        V1PodList pods = api.listNamespacedPod(
            namespace, null, null, null, null, null, null, null, null, null, null, null);
        
        List<String> endpoints = new ArrayList<>();
        
        for (V1Pod pod : pods.getItems()) {
            if (pod.getMetadata().getLabels().get("app").equals(serviceName)) {
                String podIP = pod.getStatus().getPodIP();
                endpoints.add(podIP + ":8080");
            }
        }
        
        return endpoints;
    }
}
```

#### Go语言Kubernetes客户端
```go
// kubernetes_discovery.go
package main

import (
    "context"
    "fmt"
    "log"
    "os"

    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
)

type KubernetesDiscovery struct {
    clientset *kubernetes.Clientset
    namespace string
}

func NewKubernetesDiscovery(namespace string) (*KubernetesDiscovery, error) {
    // 创建Kubernetes配置
    config, err := rest.InClusterConfig()
    if err != nil {
        // 如果不在集群中，使用kubeconfig
        kubeconfig := os.Getenv("KUBECONFIG")
        config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
        if err != nil {
            return nil, err
        }
    }
    
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        return nil, err
    }
    
    return &KubernetesDiscovery{
        clientset: clientset,
        namespace: namespace,
    }, nil
}

func (kd *KubernetesDiscovery) GetServiceEndpoints(serviceName string) ([]string, error) {
    service, err := kd.clientset.CoreV1().Services(kd.namespace).Get(
        context.TODO(), serviceName, metav1.GetOptions{})
    if err != nil {
        return nil, err
    }
    
    var endpoints []string
    
    if service.Spec.Type == corev1.ServiceTypeClusterIP {
        // ClusterIP服务
        clusterIP := service.Spec.ClusterIP
        for _, port := range service.Spec.Ports {
            endpoints = append(endpoints, fmt.Sprintf("%s:%d", clusterIP, port.Port))
        }
    } else if service.Spec.Type == corev1.ServiceTypeNodePort {
        // NodePort服务
        nodes, err := kd.clientset.CoreV1().Nodes().List(
            context.TODO(), metav1.ListOptions{})
        if err != nil {
            return nil, err
        }
        
        for _, node := range nodes.Items {
            nodeIP := node.Status.Addresses[0].Address
            for _, port := range service.Spec.Ports {
                endpoints = append(endpoints, fmt.Sprintf("%s:%d", nodeIP, port.NodePort))
            }
        }
    }
    
    return endpoints, nil
}

func (kd *KubernetesDiscovery) GetPodEndpoints(serviceName string) ([]string, error) {
    pods, err := kd.clientset.CoreV1().Pods(kd.namespace).List(
        context.TODO(), metav1.ListOptions{
            LabelSelector: fmt.Sprintf("app=%s", serviceName),
        })
    if err != nil {
        return nil, err
    }
    
    var endpoints []string
    
    for _, pod := range pods.Items {
        if pod.Status.Phase == corev1.PodRunning {
            podIP := pod.Status.PodIP
            endpoints = append(endpoints, fmt.Sprintf("%s:8080", podIP))
        }
    }
    
    return endpoints, nil
}

func main() {
    discovery, err := NewKubernetesDiscovery("default")
    if err != nil {
        log.Fatal(err)
    }
    
    // 获取服务端点
    endpoints, err := discovery.GetServiceEndpoints("user-service")
    if err != nil {
        log.Printf("获取服务端点失败: %v", err)
    } else {
        fmt.Printf("服务端点: %v\n", endpoints)
    }
    
    // 获取Pod端点
    podEndpoints, err := discovery.GetPodEndpoints("user-service")
    if err != nil {
        log.Printf("获取Pod端点失败: %v", err)
    } else {
        fmt.Printf("Pod端点: %v\n", podEndpoints)
    }
}
```

## 自定义服务发现实现

### 基于Redis的服务发现

#### Redis服务注册中心
```python
# redis_service_registry.py
import redis
import json
import time
from typing import List, Dict, Optional
import threading

class RedisServiceRegistry:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.service_key_prefix = "services:"
        self.heartbeat_interval = 30
        self.heartbeat_thread = None
        self.running = False
    
    def register_service(self, service_name: str, service_id: str, 
                        service_url: str, metadata: Dict = None):
        """注册服务"""
        service_data = {
            'id': service_id,
            'url': service_url,
            'metadata': metadata or {},
            'registered_at': time.time(),
            'last_heartbeat': time.time()
        }
        
        # 使用Hash存储服务信息
        key = f"{self.service_key_prefix}{service_name}"
        self.redis_client.hset(key, service_id, json.dumps(service_data))
        
        # 设置过期时间
        self.redis_client.expire(key, self.heartbeat_interval * 2)
        
        print(f"服务 {service_name} ({service_id}) 注册成功")
    
    def deregister_service(self, service_name: str, service_id: str):
        """注销服务"""
        key = f"{self.service_key_prefix}{service_name}"
        self.redis_client.hdel(key, service_id)
        print(f"服务 {service_name} ({service_id}) 注销成功")
    
    def discover_services(self, service_name: str) -> List[Dict]:
        """发现服务"""
        key = f"{self.service_key_prefix}{service_name}"
        services = self.redis_client.hgetall(key)
        
        result = []
        for service_id, service_data in services.items():
            try:
                service_info = json.loads(service_data)
                
                # 检查心跳
                if self.is_service_healthy(service_info):
                    result.append(service_info)
                else:
                    # 移除不健康的服务
                    self.redis_client.hdel(key, service_id)
            except json.JSONDecodeError:
                continue
        
        return result
    
    def is_service_healthy(self, service_info: Dict) -> bool:
        """检查服务健康状态"""
        last_heartbeat = service_info.get('last_heartbeat', 0)
        return time.time() - last_heartbeat < self.heartbeat_interval * 2
    
    def send_heartbeat(self, service_name: str, service_id: str):
        """发送心跳"""
        key = f"{self.service_key_prefix}{service_name}"
        service_data = self.redis_client.hget(key, service_id)
        
        if service_data:
            try:
                service_info = json.loads(service_data)
                service_info['last_heartbeat'] = time.time()
                self.redis_client.hset(key, service_id, json.dumps(service_info))
            except json.JSONDecodeError:
                pass
    
    def start_heartbeat_thread(self, service_name: str, service_id: str):
        """启动心跳线程"""
        self.running = True
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_worker, 
            args=(service_name, service_id)
        )
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
    
    def _heartbeat_worker(self, service_name: str, service_id: str):
        """心跳工作线程"""
        while self.running:
            self.send_heartbeat(service_name, service_id)
            time.sleep(self.heartbeat_interval)
    
    def stop_heartbeat_thread(self):
        """停止心跳线程"""
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join()

# 使用示例
registry = RedisServiceRegistry()

# 注册服务
registry.register_service(
    service_name="user-service",
    service_id="user-service-1",
    service_url="http://localhost:8080",
    metadata={"version": "1.0.0", "environment": "production"}
)

# 启动心跳
registry.start_heartbeat_thread("user-service", "user-service-1")

try:
    # 模拟服务运行
    while True:
        # 发现服务
        services = registry.discover_services("user-service")
        print(f"发现的服务: {services}")
        time.sleep(10)
except KeyboardInterrupt:
    # 清理
    registry.deregister_service("user-service", "user-service-1")
    registry.stop_heartbeat_thread()
```

#### 服务发现客户端
```python
# service_discovery_client.py
import requests
import random
from typing import List, Dict
import time

class ServiceDiscoveryClient:
    def __init__(self, registry_url: str):
        self.registry_url = registry_url
        self.service_cache = {}
        self.cache_ttl = 30
    
    def get_service_instances(self, service_name: str) -> List[Dict]:
        """获取服务实例"""
        # 检查缓存
        if service_name in self.service_cache:
            cache_entry = self.service_cache[service_name]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['instances']
        
        # 从注册中心获取
        try:
            response = requests.get(f"{self.registry_url}/services/{service_name}")
            if response.status_code == 200:
                instances = response.json()
                # 更新缓存
                self.service_cache[service_name] = {
                    'instances': instances,
                    'timestamp': time.time()
                }
                return instances
        except Exception as e:
            print(f"获取服务实例失败: {e}")
            # 返回缓存中的实例（如果存在）
            if service_name in self.service_cache:
                return self.service_cache[service_name]['instances']
        
        return []
    
    def get_random_instance(self, service_name: str) -> Optional[Dict]:
        """获取随机服务实例"""
        instances = self.get_service_instances(service_name)
        if instances:
            return random.choice(instances)
        return None
    
    def get_round_robin_instance(self, service_name: str) -> Optional[Dict]:
        """轮询获取服务实例"""
        instances = self.get_service_instances(service_name)
        if instances:
            # 简单的轮询实现
            if not hasattr(self, '_round_robin_counters'):
                self._round_robin_counters = {}
            
            if service_name not in self._round_robin_counters:
                self._round_robin_counters[service_name] = 0
            
            index = self._round_robin_counters[service_name] % len(instances)
            self._round_robin_counters[service_name] += 1
            
            return instances[index]
        return None
    
    def call_service(self, service_name: str, endpoint: str, method='GET', data=None):
        """调用服务"""
        instance = self.get_random_instance(service_name)
        if not instance:
            raise Exception(f"服务 {service_name} 没有可用实例")
        
        url = f"{instance['url']}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)
            else:
                response = requests.request(method, url, json=data)
            
            return response.json()
        except Exception as e:
            print(f"调用服务失败: {e}")
            raise

# 使用示例
client = ServiceDiscoveryClient("http://localhost:8080")

# 调用服务
try:
    result = client.call_service("user-service", "/users/123")
    print(f"调用结果: {result}")
except Exception as e:
    print(f"调用失败: {e}")
```

## 服务发现最佳实践

### 健康检查策略
```python
# health_check.py
import requests
import time
from typing import Dict, List
import threading

class HealthChecker:
    def __init__(self, check_interval=30):
        self.check_interval = check_interval
        self.running = False
        self.check_thread = None
        self.health_status = {}
    
    def add_service_check(self, service_name: str, service_url: str, 
                         check_endpoint="/health", timeout=5):
        """添加服务健康检查"""
        self.health_status[service_name] = {
            'url': service_url,
            'check_endpoint': check_endpoint,
            'timeout': timeout,
            'healthy': False,
            'last_check': None,
            'error_count': 0
        }
    
    def check_service_health(self, service_name: str) -> bool:
        """检查单个服务健康状态"""
        if service_name not in self.health_status:
            return False
        
        service_info = self.health_status[service_name]
        check_url = f"{service_info['url']}{service_info['check_endpoint']}"
        
        try:
            response = requests.get(check_url, timeout=service_info['timeout'])
            is_healthy = response.status_code == 200
            
            if is_healthy:
                service_info['error_count'] = 0
            else:
                service_info['error_count'] += 1
            
            service_info['healthy'] = is_healthy
            service_info['last_check'] = time.time()
            
            return is_healthy
        except Exception as e:
            service_info['error_count'] += 1
            service_info['healthy'] = False
            service_info['last_check'] = time.time()
            print(f"健康检查失败 {service_name}: {e}")
            return False
    
    def check_all_services(self) -> Dict[str, bool]:
        """检查所有服务健康状态"""
        results = {}
        for service_name in self.health_status:
            results[service_name] = self.check_service_health(service_name)
        return results
    
    def start_continuous_check(self):
        """启动连续健康检查"""
        self.running = True
        self.check_thread = threading.Thread(target=self._check_worker)
        self.check_thread.daemon = True
        self.check_thread.start()
    
    def _check_worker(self):
        """健康检查工作线程"""
        while self.running:
            self.check_all_services()
            time.sleep(self.check_interval)
    
    def stop_continuous_check(self):
        """停止连续健康检查"""
        self.running = False
        if self.check_thread:
            self.check_thread.join()
    
    def get_healthy_services(self) -> List[str]:
        """获取健康的服务列表"""
        return [name for name, info in self.health_status.items() if info['healthy']]
    
    def get_unhealthy_services(self) -> List[str]:
        """获取不健康的服务列表"""
        return [name for name, info in self.health_status.items() if not info['healthy']]

# 使用示例
health_checker = HealthChecker(check_interval=15)

# 添加服务检查
health_checker.add_service_check(
    service_name="user-service",
    service_url="http://localhost:8080",
    check_endpoint="/actuator/health"
)

health_checker.add_service_check(
    service_name="order-service",
    service_url="http://localhost:8081",
    check_endpoint="/actuator/health"
)

# 启动连续检查
health_checker.start_continuous_check()

try:
    while True:
        healthy_services = health_checker.get_healthy_services()
        unhealthy_services = health_checker.get_unhealthy_services()
        
        print(f"健康服务: {healthy_services}")
        print(f"不健康服务: {unhealthy_services}")
        
        time.sleep(30)
except KeyboardInterrupt:
    health_checker.stop_continuous_check()
```

### 负载均衡策略
```python
# load_balancer.py
import random
import time
from typing import List, Dict
from abc import ABC, abstractmethod

class LoadBalancer(ABC):
    @abstractmethod
    def select_instance(self, instances: List[Dict]) -> Dict:
        pass

class RoundRobinLoadBalancer(LoadBalancer):
    def __init__(self):
        self.current_index = 0
    
    def select_instance(self, instances: List[Dict]) -> Dict:
        if not instances:
            raise Exception("没有可用实例")
        
        instance = instances[self.current_index % len(instances)]
        self.current_index += 1
        return instance

class RandomLoadBalancer(LoadBalancer):
    def select_instance(self, instances: List[Dict]) -> Dict:
        if not instances:
            raise Exception("没有可用实例")
        
        return random.choice(instances)

class WeightedRoundRobinLoadBalancer(LoadBalancer):
    def __init__(self):
        self.current_weights = {}
    
    def select_instance(self, instances: List[Dict]) -> Dict:
        if not instances:
            raise Exception("没有可用实例")
        
        # 计算权重总和
        total_weight = sum(instance.get('weight', 1) for instance in instances)
        
        if total_weight == 0:
            return random.choice(instances)
        
        # 选择实例
        random_weight = random.uniform(0, total_weight)
        current_weight = 0
        
        for instance in instances:
            current_weight += instance.get('weight', 1)
            if current_weight >= random_weight:
                return instance
        
        return instances[-1]

class LeastConnectionsLoadBalancer(LoadBalancer):
    def __init__(self):
        self.connection_counts = {}
    
    def select_instance(self, instances: List[Dict]) -> Dict:
        if not instances:
            raise Exception("没有可用实例")
        
        # 获取连接数最少的实例
        min_connections = float('inf')
        selected_instance = None
        
        for instance in instances:
            instance_id = instance.get('id')
            connections = self.connection_counts.get(instance_id, 0)
            
            if connections < min_connections:
                min_connections = connections
                selected_instance = instance
        
        # 增加连接数
        if selected_instance:
            instance_id = selected_instance.get('id')
            self.connection_counts[instance_id] = min_connections + 1
        
        return selected_instance
    
    def release_connection(self, instance_id: str):
        """释放连接"""
        if instance_id in self.connection_counts:
            self.connection_counts[instance_id] -= 1

class ResponseTimeBasedLoadBalancer(LoadBalancer):
    def __init__(self):
        self.response_times = {}
    
    def select_instance(self, instances: List[Dict]) -> Dict:
        if not instances:
            raise Exception("没有可用实例")
        
        # 选择响应时间最短的实例
        min_response_time = float('inf')
        selected_instance = None
        
        for instance in instances:
            instance_id = instance.get('id')
            response_time = self.response_times.get(instance_id, 0)
            
            if response_time < min_response_time:
                min_response_time = response_time
                selected_instance = instance
        
        return selected_instance if selected_instance else instances[0]
    
    def update_response_time(self, instance_id: str, response_time: float):
        """更新响应时间"""
        # 使用指数移动平均
        alpha = 0.3
        current_time = self.response_times.get(instance_id, 0)
        self.response_times[instance_id] = alpha * response_time + (1 - alpha) * current_time

# 使用示例
instances = [
    {'id': 'instance-1', 'url': 'http://localhost:8080', 'weight': 3},
    {'id': 'instance-2', 'url': 'http://localhost:8081', 'weight': 2},
    {'id': 'instance-3', 'url': 'http://localhost:8082', 'weight': 1},
]

# 创建不同的负载均衡器
round_robin_lb = RoundRobinLoadBalancer()
random_lb = RandomLoadBalancer()
weighted_lb = WeightedRoundRobinLoadBalancer()
least_conn_lb = LeastConnectionsLoadBalancer()
response_time_lb = ResponseTimeBasedLoadBalancer()

# 测试负载均衡
print("轮询负载均衡:")
for i in range(5):
    instance = round_robin_lb.select_instance(instances)
    print(f"  选择实例: {instance['id']}")

print("随机负载均衡:")
for i in range(5):
    instance = random_lb.select_instance(instances)
    print(f"  选择实例: {instance['id']}")

print("加权轮询负载均衡:")
for i in range(10):
    instance = weighted_lb.select_instance(instances)
    print(f"  选择实例: {instance['id']}")
```

## 参考资源

### 官方文档
- [Eureka Documentation](https://spring.io/projects/spring-cloud-netflix)
- [Consul Documentation](https://www.consul.io/docs)
- [Zookeeper Documentation](https://zookeeper.apache.org/doc/current/)
- [Kubernetes Documentation](https://kubernetes.io/docs/concepts/services-networking/service/)

### 实现框架
- [Spring Cloud Netflix](https://spring.io/projects/spring-cloud-netflix)
- [Spring Cloud Consul](https://spring.io/projects/spring-cloud-consul)
- [Apache Curator](https://curator.apache.org/)
- [Kubernetes Client Libraries](https://kubernetes.io/docs/reference/using-api/client-libraries/)

### 设计模式
- [Service Discovery Patterns](https://microservices.io/patterns/service-discovery/)
- [Microservices Patterns](https://microservices.io/patterns/)
- [Cloud Design Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/)

### 最佳实践
- [12-Factor App](https://12factor.net/)
- [Microservices Best Practices](https://microservices.io/patterns/)
- [Cloud Native Computing Foundation](https://www.cncf.io/)
