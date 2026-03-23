# Spring Boot参考文档

## 核心概念

### Spring Boot自动配置原理

#### @EnableAutoConfiguration机制
```java
@SpringBootApplication
// 等价于:
// @SpringBootConfiguration
// @EnableAutoConfiguration
// @ComponentScan
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

#### 条件注解体系
- **@ConditionalOnClass**: 类路径中存在指定类时生效
- **@ConditionalOnMissingClass**: 类路径中不存在指定类时生效
- **@ConditionalOnBean**: 容器中存在指定Bean时生效
- **@ConditionalOnMissingBean**: 容器中不存在指定Bean时生效
- **@ConditionalOnProperty**: 配置属性满足条件时生效
- **@ConditionalOnWebApplication**: Web应用环境下生效

#### 自动配置示例
```java
@Configuration
@ConditionalOnClass(DataSource.class)
@ConditionalOnProperty(prefix = "spring.datasource", name = "url")
@EnableConfigurationProperties(DataSourceProperties.class)
public class DataSourceAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource(DataSourceProperties properties) {
        return properties.initializeDataSourceBuilder().build();
    }
}
```

### 启动过程详解

#### SpringApplication启动流程
1. **创建SpringApplication实例**
2. **加载ApplicationContextInitializer**
3. **加载ApplicationListener**
4. **推断主类**
5. **运行run方法**:
   - 创建ApplicationContext
   - 准备Environment
   - 初始化Banner
   - 初始化ApplicationContext
   - 刷新ApplicationContext
   - 调用Runner

#### 事件发布顺序
- **ApplicationStartingEvent**: 应用开始启动
- **ApplicationEnvironmentPreparedEvent**: 环境准备完成
- **ApplicationContextInitializedEvent**: 上下文初始化完成
- **ApplicationPreparedEvent**: 上下文准备完成
- **ApplicationStartedEvent**: 应用启动完成
- **ApplicationReadyEvent**: 应用就绪
- **ApplicationFailedEvent**: 应用启动失败

## 配置管理

### 配置文件优先级

#### 配置文件加载顺序
1. **命令行参数**
2. **Java系统属性**
3. **操作系统环境变量**
4. **外部配置文件**
5. **打包在jar中的配置文件**
6. **@PropertySource注解**
7. **默认属性**

#### 多环境配置
```yaml
# application.yml
spring:
  profiles:
    active: dev

---
spring:
  config:
    activate:
      on-profile: dev
server:
  port: 8080
logging:
  level:
    root: DEBUG

---
spring:
  config:
    activate:
      on-profile: prod
server:
  port: 80
logging:
  level:
    root: INFO
```

### 配置属性绑定

#### @ConfigurationProperties
```java
@ConfigurationProperties(prefix = "app")
@Component
@Data
public class AppProperties {
    private String name;
    private String version;
    private Security security = new Security();
    
    @Data
    public static class Security {
        private String jwtSecret;
        private long jwtExpiration = 3600;
    }
}
```

#### 配置文件
```yaml
app:
  name: MyApplication
  version: 1.0.0
  security:
    jwt-secret: mySecretKey
    jwt-expiration: 7200
```

## Web开发

### RESTful API开发

#### Controller最佳实践
```java
@RestController
@RequestMapping("/api/v1/users")
@Validated
@Slf4j
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public ResponseEntity<Page<UserDTO>> getUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String sort) {
        
        Pageable pageable = PageRequest.of(page, size, 
            Sort.by(sort != null ? sort : "id"));
        Page<UserDTO> users = userService.findAll(pageable);
        
        return ResponseEntity.ok(users);
    }
    
    @PostMapping
    public ResponseEntity<UserDTO> createUser(
            @Valid @RequestBody CreateUserRequest request) {
        
        UserDTO user = userService.create(request);
        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(user.getId())
            .toUri();
            
        return ResponseEntity.created(location).body(user);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<UserDTO> getUser(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<UserDTO> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UpdateUserRequest request) {
        
        return userService.update(id, request)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        if (userService.delete(id)) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
```

#### 全局异常处理
```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(
            MethodArgumentNotValidException ex) {
        
        List<String> errors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(error -> error.getField() + ": " + error.getDefaultMessage())
            .collect(Collectors.toList());
            
        ErrorResponse errorResponse = ErrorResponse.builder()
            .timestamp(LocalDateTime.now())
            .status(HttpStatus.BAD_REQUEST.value())
            .error("Validation Failed")
            .message(errors)
            .path(getRequestPath())
            .build();
            
        return ResponseEntity.badRequest().body(errorResponse);
    }
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFoundException(
            ResourceNotFoundException ex) {
        
        ErrorResponse errorResponse = ErrorResponse.builder()
            .timestamp(LocalDateTime.now())
            .status(HttpStatus.NOT_FOUND.value())
            .error("Resource Not Found")
            .message(ex.getMessage())
            .path(getRequestPath())
            .build();
            
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(errorResponse);
    }
}
```

### 数据验证

#### Bean Validation
```java
@Data
public class CreateUserRequest {
    
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 50, message = "用户名长度必须在3-50之间")
    private String username;
    
    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;
    
    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 20, message = "密码长度必须在6-20之间")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).+$", 
             message = "密码必须包含大小写字母和数字")
    private String password;
    
    @NotNull(message = "年龄不能为空")
    @Min(value = 18, message = "年龄必须大于等于18")
    @Max(value = 100, message = "年龄必须小于等于100")
    private Integer age;
}
```

#### 自定义验证器
```java
@Component
public class UniqueUsernameValidator implements 
        ConstraintValidator<UniqueUsername, String> {
    
    @Autowired
    private UserRepository userRepository;
    
    @Override
    public boolean isValid(String username, 
                         ConstraintValidatorContext context) {
        return !userRepository.existsByUsername(username);
    }
}

@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = UniqueUsernameValidator.class)
public @interface UniqueUsername {
    String message() default "用户名已存在";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

## 数据访问

### JPA最佳实践

#### Repository设计
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // 基于方法名的查询
    Optional<User> findByUsername(String username);
    List<User> findByEmailContaining(String email);
    
    // @Query注解查询
    @Query("SELECT u FROM User u WHERE u.username = ?1 AND u.active = true")
    Optional<User> findActiveUserByUsername(String username);
    
    // 原生SQL查询
    @Query(value = "SELECT * FROM users WHERE created_at > ?1", 
           nativeQuery = true)
    List<User> findUsersCreatedAfter(LocalDateTime dateTime);
    
    // 分页查询
    Page<User> findByActiveTrue(Pageable pageable);
    
    // 修改操作
    @Modifying
    @Query("UPDATE User u SET u.active = false WHERE u.id = ?1")
    int deactivateUser(Long id);
}
```

#### 实体设计
```java
@Entity
@Table(name = "users")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@EntityListeners(AuditingEntityListener.class)
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true, length = 50)
    private String username;
    
    @Column(nullable = false, unique = true)
    private String email;
    
    @Column(nullable = false)
    private String password;
    
    @Enumerated(EnumType.STRING)
    private UserStatus status = UserStatus.ACTIVE;
    
    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @LastModifiedDate
    private LocalDateTime updatedAt;
    
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, 
                fetch = FetchType.LAZY)
    private List<Order> orders = new ArrayList<>();
    
    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles = new HashSet<>();
}
```

### 事务管理

#### 事务注解使用
```java
@Service
@Transactional
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private RoleRepository roleRepository;
    
    @Transactional(readOnly = true)
    public UserDTO findById(Long id) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("用户不存在"));
        return UserMapper.toDTO(user);
    }
    
    @Transactional(rollbackFor = Exception.class)
    public UserDTO create(CreateUserRequest request) {
        // 创建用户
        User user = User.builder()
            .username(request.getUsername())
            .email(request.getEmail())
            .password(passwordEncoder.encode(request.getPassword()))
            .status(UserStatus.ACTIVE)
            .build();
        
        // 分配默认角色
        Role userRole = roleRepository.findByName("USER")
            .orElseThrow(() -> new RuntimeException("默认角色不存在"));
        user.getRoles().add(userRole);
        
        User savedUser = userRepository.save(user);
        return UserMapper.toDTO(savedUser);
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logUserActivity(Long userId, String activity) {
        // 独立事务记录用户活动
        UserActivityLog log = UserActivityLog.builder()
            .userId(userId)
            .activity(activity)
            .timestamp(LocalDateTime.now())
            .build();
        activityLogRepository.save(log);
    }
}
```

## 安全配置

### Spring Security配置

#### 基础安全配置
```java
@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SecurityConfig {
    
    @Autowired
    private UserDetailsService userDetailsService;
    
    @Autowired
    private JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint;
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
    
    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .exceptionHandling()
                .authenticationEntryPoint(jwtAuthenticationEntryPoint)
            .and()
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .authorizeHttpRequests()
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/users/**").hasAnyRole("USER", "ADMIN")
                .requestMatchers(HttpMethod.POST, "/api/users/**").hasRole("ADMIN")
                .requestMatchers("/actuator/health").permitAll()
                .anyRequest().authenticated()
            .and()
            .addFilterBefore(jwtAuthenticationFilter, 
                           UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }
}
```

#### JWT工具类
```java
@Component
@Slf4j
public class JwtUtils {
    
    @Value("${app.jwtSecret}")
    private String jwtSecret;
    
    @Value("${app.jwtExpirationMs}")
    private int jwtExpirationMs;
    
    public String generateJwtToken(Authentication authentication) {
        UserPrincipal userPrincipal = (UserPrincipal) authentication.getPrincipal();
        
        return Jwts.builder()
            .setSubject(userPrincipal.getUsername())
            .setIssuedAt(new Date())
            .setExpiration(new Date(new Date().getTime() + jwtExpirationMs))
            .signWith(SignatureAlgorithm.HS512, jwtSecret)
            .compact();
    }
    
    public String getUsernameFromJwtToken(String token) {
        return Jwts.parser()
            .setSigningKey(jwtSecret)
            .parseClaimsJws(token)
            .getBody()
            .getSubject();
    }
    
    public boolean validateJwtToken(String authToken) {
        try {
            Jwts.parser().setSigningKey(jwtSecret).parseClaimsJws(authToken);
            return true;
        } catch (SignatureException e) {
            log.error("Invalid JWT signature: {}", e.getMessage());
        } catch (MalformedJwtException e) {
            log.error("Invalid JWT token: {}", e.getMessage());
        } catch (ExpiredJwtException e) {
            log.error("JWT token is expired: {}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            log.error("JWT token is unsupported: {}", e.getMessage());
        } catch (IllegalArgumentException e) {
            log.error("JWT claims string is empty: {}", e.getMessage());
        }
        return false;
    }
}
```

## 测试策略

### 单元测试

#### Service层测试
```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private PasswordEncoder passwordEncoder;
    
    @InjectMocks
    private UserService userService;
    
    @Test
    void create_ShouldReturnUserDTO_WhenValidRequest() {
        // Given
        CreateUserRequest request = CreateUserRequest.builder()
            .username("testuser")
            .email("test@example.com")
            .password("password123")
            .build();
        
        User savedUser = User.builder()
            .id(1L)
            .username("testuser")
            .email("test@example.com")
            .password("encodedPassword")
            .status(UserStatus.ACTIVE)
            .build();
        
        when(userRepository.existsByUsername("testuser")).thenReturn(false);
        when(passwordEncoder.encode("password123")).thenReturn("encodedPassword");
        when(userRepository.save(any(User.class))).thenReturn(savedUser);
        
        // When
        UserDTO result = userService.create(request);
        
        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getUsername()).isEqualTo("testuser");
        assertThat(result.getEmail()).isEqualTo("test@example.com");
        
        verify(userRepository).existsByUsername("testuser");
        verify(passwordEncoder).encode("password123");
        verify(userRepository).save(any(User.class));
    }
}
```

### 集成测试

#### Controller层测试
```java
@SpringBootTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestPropertySource(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb",
    "spring.jpa.hibernate.ddl-auto=create-drop"
})
class UserControllerIntegrationTest {
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    void createUser_ShouldReturn201_WhenValidRequest() {
        // Given
        CreateUserRequest request = CreateUserRequest.builder()
            .username("newuser")
            .email("newuser@example.com")
            .password("password123")
            .build();
        
        // When
        ResponseEntity<UserDTO> response = restTemplate.postForEntity(
            "/api/users", request, UserDTO.class);
        
        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody().getUsername()).isEqualTo("newuser");
        assertThat(response.getBody().getEmail()).isEqualTo("newuser@example.com");
        
        Optional<User> savedUser = userRepository.findByUsername("newuser");
        assertThat(savedUser).isPresent();
    }
}
```

## 性能优化

### JVM调优

#### 堆内存配置
```bash
# 生产环境推荐配置
-Xms2g -Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+PrintGCDetails
-XX:+PrintGCTimeStamps
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/app/
```

#### GC参数优化
```bash
# G1GC配置
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:G1HeapRegionSize=16m
-XX:G1NewSizePercent=30
-XX:G1MaxNewSizePercent=40
-XX:G1MixedGCCountTarget=8
```

### 应用性能优化

#### 连接池优化
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 10
      idle-timeout: 300000
      max-lifetime: 1200000
      connection-timeout: 20000
      leak-detection-threshold: 60000
```

#### 缓存配置
```java
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .expireAfterWrite(10, TimeUnit.MINUTES)
            .maximumSize(1000));
        return cacheManager;
    }
}
```

## 监控和运维

### Actuator配置

#### 健康检查
```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Override
    public Health health() {
        try {
            Connection connection = dataSource.getConnection();
            if (connection != null) {
                connection.close();
                return Health.up()
                    .withDetail("database", "Available")
                    .build();
            }
        } catch (SQLException e) {
            return Health.down()
                .withDetail("database", "Unavailable")
                .withException(e)
                .build();
        }
        return Health.down().withDetail("database", "Unavailable").build();
    }
}
```

#### 自定义指标
```java
@Component
public class UserMetrics {
    
    private final MeterRegistry meterRegistry;
    private final Counter userCreationCounter;
    private final Gauge activeUserGauge;
    
    public UserMetrics(MeterRegistry meterRegistry, UserService userService) {
        this.meterRegistry = meterRegistry;
        this.userCreationCounter = Counter.builder("user.creation.count")
            .description("Number of users created")
            .register(meterRegistry);
        this.activeUserGauge = Gauge.builder("user.active.count")
            .description("Number of active users")
            .register(meterRegistry, userService, UserService::getActiveUserCount);
    }
    
    public void incrementUserCreation() {
        userCreationCounter.increment();
    }
}
```

## 常见问题和解决方案

### 启动问题
- **端口冲突**: 检查端口占用，修改server.port
- **依赖冲突**: 使用mvn dependency:tree分析
- **配置错误**: 检查application.properties语法

### 性能问题
- **内存泄漏**: 使用VisualVM分析堆内存
- **数据库连接池耗尽**: 调整连接池配置
- **GC频繁**: 调整JVM参数和内存分配

### 安全问题
- **认证失败**: 检查JWT配置和密钥
- **权限不足**: 验证角色和权限配置
- **CSRF攻击**: 启用CSRF保护

## 参考资源

### 官方文档
- [Spring Boot Reference Guide](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [Spring Framework Documentation](https://docs.spring.io/spring-framework/docs/current/reference/html/)
- [Spring Security Reference](https://docs.spring.io/spring-security/docs/current/reference/html5/)

### 最佳实践
- [Spring Boot Best Practices](https://spring.io/guides/gs/spring-boot/)
- [Spring Boot Performance Tuning](https://spring.io/blog/2018/09/19/spring-boot-2-1-0-rc1-whats-new)

### 社区资源
- [Spring Boot Samples](https://github.com/spring-projects/spring-boot/tree/main/spring-boot-samples)
- [Spring Initializr](https://start.spring.io/)
- [Spring Boot Admin](https://github.com/codecentric/spring-boot-admin)
