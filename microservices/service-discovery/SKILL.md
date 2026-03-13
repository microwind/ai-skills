---
name: 服务治理与发现
description: "当实现服务发现时，分析注册机制，优化负载均衡，解决服务治理问题。验证服务架构，设计动态发现，和最佳实践。"
license: MIT
---

# 服务治理与发现技能

## 概述
服务发现是微服务架构中的核心组件，负责服务的注册、发现和负载均衡。服务发现使得服务能够动态地找到彼此，无需硬编码网络地址，提高了系统的灵活性和可扩展性。不当的服务发现实现会导致单点故障、性能瓶颈、服务不可用。

**核心原则**: 好的服务发现应该高可用、高性能、自动故障转移、负载均衡。坏的服务发现会成为系统瓶颈，影响整体可用性。

## 何时使用

**始终:**
- 构建微服务架构时
- 需要动态服务发现时
- 实现负载均衡时
- 处理服务故障转移时
- 构建弹性系统时
- 实现服务治理时

**触发短语:**
- "如何实现服务发现？"
- "服务注册中心选型"
- "负载均衡策略配置"
- "服务健康检查机制"
- "服务故障转移"
- "微服务治理方案"

## 服务治理与发现技能功能

### 服务注册
- 服务实例注册
- 健康检查上报
- 元数据管理
- 服务分组管理
- 自动注销机制

### 服务发现
- 服务查询接口
- 实时服务列表
- 服务版本管理
- 环境隔离
- 多数据中心支持

### 负载均衡
- 轮询策略
- 权重轮询
- 最少连接
- 一致性哈希
- 故障转移

### 服务治理
- 服务依赖管理
- 配置管理
- 流量控制
- 服务降级
- 监控告警

## 常见问题

### 可用性问题
- **问题**: 注册中心单点故障
- **原因**: 缺乏高可用设计
- **解决**: 集群部署，数据复制

- **问题**: 服务实例不可用
- **原因**: 健康检查失败，网络分区
- **解决**: 完善健康检查，故障转移

### 性能问题
- **问题**: 服务发现延迟高
- **原因**: 网络延迟，查询效率低
- **解决**: 本地缓存，批量查询

- **问题**: 注册中心负载过高
- **原因**: 频繁注册，查询量大
- **解决**: 批量操作，缓存优化

### 一致性问题
- **问题**: 服务列表不一致
- **原因**: 数据同步延迟，网络分区
- **解决**: 最终一致性，数据复制

## 代码示例

### Eureka服务注册与发现
```java
// Eureka服务器配置
@SpringBootApplication
@EnableEurekaServer
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}

// Eureka服务器配置文件
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

// 服务提供者配置
@SpringBootApplication
@EnableEurekaClient
public class UserServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
    }
}

// 服务提供者配置文件
server:
  port: 8081

spring:
  application:
    name: user-service

eureka:
  instance:
    hostname: localhost
    prefer-ip-address: true
    lease-renewal-interval-in-seconds: 30
    lease-expiration-duration-in-seconds: 90
    metadata-map:
      version: 1.0.0
      environment: production
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
    register-with-eureka: true
    fetch-registry: true
    registry-fetch-interval-seconds: 30

// 服务消费者配置
@SpringBootApplication
@EnableEurekaClient
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}

// 服务消费者配置文件
server:
  port: 8082

spring:
  application:
    name: order-service

eureka:
  instance:
    hostname: localhost
    prefer-ip-address: true
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
    register-with-eureka: true
    fetch-registry: true
    registry-fetch-interval-seconds: 10

// 服务调用客户端
@Service
public class UserServiceClient {
    
    private final LoadBalancerClient loadBalancerClient;
    private final RestTemplate restTemplate;
    
    public UserServiceClient(LoadBalancerClient loadBalancerClient,
                           RestTemplate restTemplate) {
        this.loadBalancerClient = loadBalancerClient;
        this.restTemplate = restTemplate;
    }
    
    public User getUserById(String userId) {
        // 通过服务发现获取服务实例
        ServiceInstance instance = loadBalancerClient.choose("user-service");
        
        if (instance == null) {
            throw new RuntimeException("No available user-service instances");
        }
        
        String url = String.format("http://%s:%d/api/users/%s",
            instance.getHost(), instance.getPort(), userId);
        
        return restTemplate.getForObject(url, User.class);
    }
    
    public List<User> getAllUsers() {
        ServiceInstance instance = loadBalancerClient.choose("user-service");
        
        if (instance == null) {
            throw new RuntimeException("No available user-service instances");
        }
        
        String url = String.format("http://%s:%d/api/users",
            instance.getHost(), instance.getPort());
        
        return restTemplate.exchange(url, HttpMethod.GET, null,
            new ParameterizedTypeReference<List<User>>() {}).getBody();
    }
}

// 自定义负载均衡策略
@Component
public class CustomLoadBalancer implements IRule {
    
    private final Random random = new Random();
    
    @Override
    public Server choose(Object key) {
        List<Server> servers = getLoadBalancer().getReachableServers();
        
        if (servers.isEmpty()) {
            return null;
        }
        
        // 基于权重的随机选择
        return chooseByWeight(servers);
    }
    
    private Server chooseByWeight(List<Server> servers) {
        int totalWeight = servers.stream()
            .mapToInt(server -> getServerWeight(server))
            .sum();
        
        if (totalWeight == 0) {
            return servers.get(random.nextInt(servers.size()));
        }
        
        int randomWeight = random.nextInt(totalWeight);
        int currentWeight = 0;
        
        for (Server server : servers) {
            currentWeight += getServerWeight(server);
            if (randomWeight < currentWeight) {
                return server;
            }
        }
        
        return servers.get(0);
    }
    
    private int getServerWeight(Server server) {
        // 从服务器元数据获取权重
        Map<String, String> metadata = server.getMetaInfo().getMetadata();
        return Integer.parseInt(metadata.getOrDefault("weight", "1"));
    }
    
    @Override
    public void initWithNiwsConfig(IClientConfig clientConfig) {
        // 初始化配置
    }
    
    @Override
    public void setLoadBalancer(ILoadBalancer lb) {
        // 设置负载均衡器
    }
    
    @Override
    public ILoadBalancer getLoadBalancer() {
        // 获取负载均衡器
        return null;
    }
}
```

### Consul服务发现
```java
// Consul配置
@Configuration
public class ConsulConfig {
    
    @Bean
    public ConsulClient consulClient() {
        return ConsulClient.builder()
            .host("localhost")
            .port(8500)
            .build();
    }
    
    @Bean
    public ServiceRegistry consulServiceRegistry(ConsulClient consulClient) {
        return new ConsulServiceRegistry(consulClient);
    }
    
    @Bean
    public DiscoveryClient consulDiscoveryClient(ConsulClient consulClient) {
        return new ConsulDiscoveryClient(consulClient);
    }
}

// Consul服务注册
@Service
public class ConsulServiceRegistry implements ServiceRegistry {
    
    private final ConsulClient consulClient;
    
    public ConsulServiceRegistry(ConsulClient consulClient) {
        this.consulClient = consulClient;
    }
    
    @Override
    public void register(Registration registration) {
        ConsulRegistration consulRegistration = (ConsulRegistration) registration;
        
        NewService newService = ImmutableNewService.builder()
            .id(consulRegistration.getServiceId())
            .name(consulRegistration.getServiceName())
            .address(consulRegistration.getHost())
            .port(consulRegistration.getPort())
            .tags(consulRegistration.getTags())
            .meta(consulRegistration.getMetadata())
            .check(ImmutableHttpServiceCheck.builder()
                .url(String.format("http://%s:%d/actuator/health",
                    consulRegistration.getHost(), consulRegistration.getPort()))
                .interval("10s")
                .timeout("5s")
                .build())
            .build();
        
        consulClient.agentServiceRegister(newService);
    }
    
    @Override
    public void deregister(Registration registration) {
        ConsulRegistration consulRegistration = (ConsulRegistration) registration;
        consulClient.agentServiceDeregister(consulRegistration.getServiceId());
    }
    
    @Override
    public void close() {
        // 清理资源
    }
    
    @Override
    public void setStatus(Registration registration, String status) {
        // 设置服务状态
    }
    
    @Override
    public Object getStatus(Registration registration) {
        // 获取服务状态
        return "UP";
    }
}

// Consul服务发现
@Service
public class ConsulDiscoveryClient implements DiscoveryClient {
    
    private final ConsulClient consulClient;
    
    public ConsulDiscoveryClient(ConsulClient consulClient) {
        this.consulClient = consulClient;
    }
    
    @Override
    public String description() {
        return "Consul Discovery Client";
    }
    
    @Override
    public List<ServiceInstance> getInstances(String serviceId) {
        try {
            Response<List<HealthService>> response = consulClient.getHealthServices(
                serviceId, QueryOptions.DEFAULT);
            
            return response.getValue().stream()
                .map(this::convertToServiceInstance)
                .collect(Collectors.toList());
        } catch (Exception e) {
            throw new RuntimeException("Failed to get service instances", e);
        }
    }
    
    @Override
    public List<String> getServices() {
        try {
            Response<List<String>> response = consulClient.getCatalogServices(
                QueryOptions.DEFAULT);
            
            return response.getValue();
        } catch (Exception e) {
            throw new RuntimeException("Failed to get services", e);
        }
    }
    
    private ServiceInstance convertToServiceInstance(HealthService healthService) {
        HealthService.Service service = healthService.getService();
        HealthService.Node node = healthService.getNode();
        
        return DefaultServiceInstance.builder()
            .serviceId(service.getService())
            .host(service.getAddress())
            .port(service.getPort())
            .metadata(service.getMeta())
            .uri(String.format("http://%s:%d", service.getAddress(), service.getPort()))
            .scheme("http")
            .build();
    }
}

// 服务健康检查
@RestController
public class HealthController {
    
    private final UserService userService;
    private final DatabaseHealthIndicator databaseHealthIndicator;
    
    public HealthController(UserService userService,
                          DatabaseHealthIndicator databaseHealthIndicator) {
        this.userService = userService;
        this.databaseHealthIndicator = databaseHealthIndicator;
    }
    
    @GetMapping("/actuator/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> health = new HashMap<>();
        
        try {
            // 检查数据库连接
            Health dbHealth = databaseHealthIndicator.health();
            health.put("database", dbHealth.getStatus().getCode());
            
            // 检查核心业务功能
            userService.healthCheck();
            health.put("business", "UP");
            
            // 整体状态
            boolean isHealthy = "UP".equals(dbHealth.getStatus().getCode());
            health.put("status", isHealthy ? "UP" : "DOWN");
            
            return ResponseEntity.ok(health);
        } catch (Exception e) {
            health.put("status", "DOWN");
            health.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(health);
        }
    }
}

// 数据库健康检查
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    private final JdbcTemplate jdbcTemplate;
    
    public DatabaseHealthIndicator(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }
    
    @Override
    public Health health() {
        try {
            // 执行简单查询检查数据库连接
            jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            return Health.up().withDetail("database", "Available").build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("database", "Unavailable")
                .withException(e)
                .build();
        }
    }
}
```

### Nacos服务发现
```java
// Nacos配置
@Configuration
public class NacosConfig {
    
    @Value("${spring.cloud.nacos.discovery.server-addr}")
    private String serverAddr;
    
    @Value("${spring.cloud.nacos.discovery.namespace}")
    private String namespace;
    
    @Bean
    public NamingService namingService() throws NacosException {
        Properties properties = new Properties();
        properties.put("serverAddr", serverAddr);
        properties.put("namespace", namespace);
        
        return NamingFactory.createNamingService(properties);
    }
    
    @Bean
    public NacosServiceManager nacosServiceManager(NamingService namingService) {
        NacosServiceManager serviceManager = new NacosServiceManager();
        serviceManager.setNamingService(namingService);
        return serviceManager;
    }
}

// Nacos服务注册
@Service
public class NacosServiceRegistry implements ServiceRegistry {
    
    private final NamingService namingService;
    
    public NacosServiceRegistry(NamingService namingService) {
        this.namingService = namingService;
    }
    
    @Override
    public void register(Registration registration) {
        try {
            Instance instance = new Instance();
            instance.setIp(registration.getHost());
            instance.setPort(registration.getPort());
            instance.setServiceName(registration.getServiceName());
            instance.setClusterName(registration.getMetadata().getOrDefault("cluster", "DEFAULT"));
            instance.setWeight(Double.parseDouble(registration.getMetadata().getOrDefault("weight", "1.0")));
            instance.setEnabled(true);
            instance.setEphemeral(true);
            instance.setMetadata(registration.getMetadata());
            
            namingService.registerInstance(registration.getServiceName(), instance);
        } catch (NacosException e) {
            throw new RuntimeException("Failed to register service", e);
        }
    }
    
    @Override
    public void deregister(Registration registration) {
        try {
            namingService.deregisterInstance(registration.getServiceName(),
                registration.getHost(), registration.getPort());
        } catch (NacosException e) {
            throw new RuntimeException("Failed to deregister service", e);
        }
    }
    
    @Override
    public void close() {
        // 清理资源
    }
    
    @Override
    public void setStatus(Registration registration, String status) {
        try {
            Instance instance = namingService.selectOneHealthyInstance(registration.getServiceName());
            instance.setEnabled("UP".equals(status));
            namingService.registerInstance(registration.getServiceName(), instance);
        } catch (NacosException e) {
            throw new RuntimeException("Failed to set service status", e);
        }
    }
    
    @Override
    public Object getStatus(Registration registration) {
        try {
            Instance instance = namingService.selectOneHealthyInstance(registration.getServiceName());
            return instance.isEnabled() ? "UP" : "DOWN";
        } catch (NacosException e) {
            return "DOWN";
        }
    }
}

// Nacos服务发现
@Service
public class NacosDiscoveryClient implements DiscoveryClient {
    
    private final NamingService namingService;
    
    public NacosDiscoveryClient(NamingService namingService) {
        this.namingService = namingService;
    }
    
    @Override
    public String description() {
        return "Nacos Discovery Client";
    }
    
    @Override
    public List<ServiceInstance> getInstances(String serviceId) {
        try {
            List<Instance> instances = namingService.getAllInstances(serviceId);
            
            return instances.stream()
                .filter(Instance::isHealthy)
                .filter(Instance::isEnabled)
                .map(this::convertToServiceInstance)
                .collect(Collectors.toList());
        } catch (NacosException e) {
            throw new RuntimeException("Failed to get service instances", e);
        }
    }
    
    @Override
    public List<String> getServices() {
        try {
            ListView<String> services = namingService.getServicesOfServer(1, 1000);
            return services.getData();
        } catch (NacosException e) {
            throw new RuntimeException("Failed to get services", e);
        }
    }
    
    private ServiceInstance convertToServiceInstance(Instance instance) {
        return DefaultServiceInstance.builder()
            .serviceId(instance.getServiceName())
            .host(instance.getIp())
            .port(instance.getPort())
            .metadata(instance.getMetadata())
            .uri(String.format("http://%s:%d", instance.getIp(), instance.getPort()))
            .scheme("http")
            .build();
    }
}

// Nacos配置管理
@Service
public class NacosConfigService {
    
    private final ConfigService configService;
    
    public NacosConfigService() throws NacosException {
        Properties properties = new Properties();
        properties.put("serverAddr", "localhost:8848");
        properties.put("namespace", "public");
        
        this.configService = ConfigFactory.createConfigService(properties);
    }
    
    public String getConfig(String dataId, String group) throws NacosException {
        return configService.getConfig(dataId, group, 5000);
    }
    
    public void publishConfig(String dataId, String group, String content) throws NacosException {
        configService.publishConfig(dataId, group, content);
    }
    
    public void addListener(String dataId, String group, Listener listener) throws NacosException {
        configService.addListener(dataId, group, listener);
    }
}

// 配置监听器
@Component
public class ConfigListener {
    
    @PostConstruct
    public void init() throws NacosException {
        NacosConfigService configService = new NacosConfigService();
        
        configService.addListener("user-service.properties", "DEFAULT_GROUP", new Listener() {
            @Override
            public void receiveConfigInfo(String configInfo) {
                System.out.println("Received config: " + configInfo);
                // 处理配置变更
                handleConfigChange(configInfo);
            }
            
            @Override
            public Executor getExecutor() {
                return Executors.newSingleThreadExecutor();
            }
        });
    }
    
    private void handleConfigChange(String configInfo) {
        // 解析配置并更新应用配置
        Properties properties = new Properties();
        try {
            properties.load(new StringReader(configInfo));
            
            // 更新数据库连接配置
            updateDatabaseConfig(properties);
            
            // 更新缓存配置
            updateCacheConfig(properties);
            
            // 更新其他配置
            updateOtherConfig(properties);
            
        } catch (IOException e) {
            throw new RuntimeException("Failed to parse config", e);
        }
    }
    
    private void updateDatabaseConfig(Properties properties) {
        // 更新数据库配置
    }
    
    private void updateCacheConfig(Properties properties) {
        // 更新缓存配置
    }
    
    private void updateOtherConfig(Properties properties) {
        // 更新其他配置
    }
}
```

### 自定义服务发现
```java
// 自定义服务注册中心
@Component
public class CustomServiceRegistry {
    
    private final Map<String, List<ServiceInstance>> serviceRegistry = new ConcurrentHashMap<>();
    private final Map<String, Long> serviceHeartbeats = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    
    @PostConstruct
    public void init() {
        // 启动心跳检查任务
        scheduler.scheduleAtFixedRate(this::checkHeartbeats, 30, 30, TimeUnit.SECONDS);
    }
    
    public void register(ServiceInstance instance) {
        String serviceName = instance.getServiceId();
        
        serviceRegistry.computeIfAbsent(serviceName, k -> new ArrayList<>()).add(instance);
        serviceHeartbeats.put(instance.getInstanceId(), System.currentTimeMillis());
        
        System.out.println("Registered service: " + serviceName + " - " + instance.getInstanceId());
    }
    
    public void deregister(String serviceName, String instanceId) {
        List<ServiceInstance> instances = serviceRegistry.get(serviceName);
        if (instances != null) {
            instances.removeIf(instance -> instance.getInstanceId().equals(instanceId));
            if (instances.isEmpty()) {
                serviceRegistry.remove(serviceName);
            }
        }
        
        serviceHeartbeats.remove(instanceId);
        
        System.out.println("Deregistered service: " + serviceName + " - " + instanceId);
    }
    
    public void heartbeat(String instanceId) {
        serviceHeartbeats.put(instanceId, System.currentTimeMillis());
    }
    
    public List<ServiceInstance> getInstances(String serviceName) {
        List<ServiceInstance> instances = serviceRegistry.get(serviceName);
        return instances != null ? new ArrayList<>(instances) : Collections.emptyList();
    }
    
    public List<String> getServices() {
        return new ArrayList<>(serviceRegistry.keySet());
    }
    
    private void checkHeartbeats() {
        long currentTime = System.currentTimeMillis();
        long timeout = 60000; // 60秒超时
        
        serviceHeartbeats.entrySet().removeIf(entry -> {
            if (currentTime - entry.getValue() > timeout) {
                // 移除超时的服务实例
                String instanceId = entry.getKey();
                removeInstanceById(instanceId);
                return true;
            }
            return false;
        });
    }
    
    private void removeInstanceById(String instanceId) {
        serviceRegistry.values().forEach(instances -> 
            instances.removeIf(instance -> instance.getInstanceId().equals(instanceId)));
    }
    
    @PreDestroy
    public void destroy() {
        scheduler.shutdown();
    }
}

// 负载均衡器
@Component
public class CustomLoadBalancer {
    
    private final AtomicInteger roundRobinCounter = new AtomicInteger(0);
    private final Random random = new Random();
    
    public ServiceInstance choose(String serviceName, List<ServiceInstance> instances) {
        if (instances.isEmpty()) {
            return null;
        }
        
        // 使用轮询策略
        return roundRobinChoose(instances);
    }
    
    public ServiceInstance chooseByWeight(String serviceName, List<ServiceInstance> instances) {
        if (instances.isEmpty()) {
            return null;
        }
        
        // 计算总权重
        int totalWeight = instances.stream()
            .mapToInt(instance -> getInstanceWeight(instance))
            .sum();
        
        if (totalWeight == 0) {
            return instances.get(random.nextInt(instances.size()));
        }
        
        // 随机选择
        int randomWeight = random.nextInt(totalWeight);
        int currentWeight = 0;
        
        for (ServiceInstance instance : instances) {
            currentWeight += getInstanceWeight(instance);
            if (randomWeight < currentWeight) {
                return instance;
            }
        }
        
        return instances.get(0);
    }
    
    private ServiceInstance roundRobinChoose(List<ServiceInstance> instances) {
        int index = roundRobinCounter.getAndIncrement() % instances.size();
        return instances.get(index);
    }
    
    private int getInstanceWeight(ServiceInstance instance) {
        Map<String, String> metadata = instance.getMetadata();
        return Integer.parseInt(metadata.getOrDefault("weight", "1"));
    }
}

// 服务发现客户端
@Service
public class CustomDiscoveryClient implements DiscoveryClient {
    
    private final CustomServiceRegistry serviceRegistry;
    private final CustomLoadBalancer loadBalancer;
    
    public CustomDiscoveryClient(CustomServiceRegistry serviceRegistry,
                                CustomLoadBalancer loadBalancer) {
        this.serviceRegistry = serviceRegistry;
        this.loadBalancer = loadBalancer;
    }
    
    @Override
    public String description() {
        return "Custom Discovery Client";
    }
    
    @Override
    public List<ServiceInstance> getInstances(String serviceId) {
        return serviceRegistry.getInstances(serviceId);
    }
    
    @Override
    public List<String> getServices() {
        return serviceRegistry.getServices();
    }
    
    public ServiceInstance choose(String serviceId) {
        List<ServiceInstance> instances = getInstances(serviceId);
        return loadBalancer.choose(serviceId, instances);
    }
    
    public ServiceInstance chooseByWeight(String serviceId) {
        List<ServiceInstance> instances = getInstances(serviceId);
        return loadBalancer.chooseByWeight(serviceId, instances);
    }
}

// 服务实例
@Data
@Builder
public class CustomServiceInstance implements ServiceInstance {
    private String instanceId;
    private String serviceId;
    private String host;
    private int port;
    private Map<String, String> metadata;
    private boolean secure;
    
    @Override
    public String getScheme() {
        return secure ? "https" : "http";
    }
    
    @Override
    public String getUri() {
        return String.format("%s://%s:%d", getScheme(), host, port);
    }
}
```

## 最佳实践

### 服务注册
1. **健康检查**: 完善的健康检查机制
2. **元数据管理**: 丰富的服务元数据
3. **自动注销**: 及时清理无效实例
4. **分组管理**: 合理的服务分组策略

### 服务发现
1. **本地缓存**: 缓存服务列表减少网络调用
2. **故障转移**: 自动故障转移机制
3. **负载均衡**: 多种负载均衡策略
4. **版本管理**: 服务版本控制

### 高可用设计
1. **集群部署**: 注册中心集群化
2. **数据复制**: 多节点数据同步
3. **故障检测**: 及时发现节点故障
4. **自动恢复**: 自动故障恢复

### 监控治理
1. **服务监控**: 监控服务状态和性能
2. **告警机制**: 及时发现和处理问题
3. **流量控制**: 控制服务访问流量
4. **配置管理**: 集中配置管理

## 相关技能

- **api-gateway** - API网关设计
- **circuit-breaker** - 熔断器模式
- **distributed-tracing** - 分布式追踪
- **service-communication** - 服务间通信
- **backend** - 后端开发
