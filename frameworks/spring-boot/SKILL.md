---
name: Spring Boot应用开发
description: "当开发Spring Boot应用时，分析自动配置，优化依赖管理，解决启动问题。验证微服务架构，设计企业级应用，和最佳实践。"
license: MIT
---

# Spring Boot应用开发技能

## 概述
Spring Boot是Java企业级应用开发的领先框架。不当的Spring Boot配置会导致启动缓慢、内存泄漏和性能问题。在开发Spring Boot应用前需要仔细分析架构需求。

**核心原则**: 好的Spring Boot应用应该快速启动、配置简单、易于部署、生产就绪。坏的Spring Boot应用会导致配置复杂、性能瓶颈和维护困难。

## 何时使用

**始终:**
- 开发企业级Java应用时
- 构建微服务架构时
- 实现RESTful API时
- 配置自动装配时
- 处理依赖注入时

**触发短语:**
- "Spring Boot应用开发"
- "Java企业应用"
- "微服务架构设计"
- "自动配置优化"
- "Spring Boot性能调优"
- "依赖注入管理"

## Spring Boot应用开发功能

### 自动配置管理
- 条件注解配置
- 自动装配机制
- 配置属性绑定
- 自定义启动器
- 配置元数据生成

### 依赖注入系统
- 组件扫描配置
- Bean生命周期管理
- 作用域配置
- 循环依赖处理
- 条件化Bean创建

### 微服务支持
- 服务注册发现
- 配置中心集成
- 负载均衡配置
- 熔断器模式
- 分布式链路追踪

### 生产就绪功能
- 健康检查端点
- 指标监控收集
- 应用信息暴露
- 外部化配置
- 日志配置管理

## 常见Spring Boot问题

### 启动性能问题
```
问题:
应用启动缓慢，内存占用高

错误示例:
- 不必要的自动配置
- 类路径扫描过多
- Bean初始化耗时
- 配置加载缓慢

解决方案:
1. 禁用不必要的自动配置
2. 优化组件扫描范围
3. 延迟加载非关键Bean
4. 使用条件化配置
```

### 依赖冲突问题
```
问题:
版本冲突，类加载异常

错误示例:
- 传递依赖版本不匹配
- 多版本jar包冲突
- 缺失必要依赖
- 依赖范围配置错误

解决方案:
1. 使用dependencyManagement管理版本
2. 排除冲突依赖
3. 明确指定依赖版本
4. 分析依赖树结构
```

### 配置管理问题
```
问题:
配置分散，环境切换困难

错误示例:
- 硬编码配置值
- 配置文件混乱
- 环境配置缺失
- 敏感信息暴露

解决方案:
1. 使用外部化配置
2. 分环境配置文件
3. 配置中心集成
4. 敏感信息加密
```

## 代码实现示例

### Spring Boot应用分析器
```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.type.classreading.MetadataReader;
import org.springframework.core.type.classreading.MetadataReaderFactory;
import org.springframework.core.type.filter.TypeFilter;
import org.springframework.util.ClassUtils;
import org.springframework.util.ReflectionUtils;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.*;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;
import java.util.stream.Collectors;

public class SpringBootAnalyzer {
    
    private final String applicationPath;
    private AnalysisResult result;
    
    public SpringBootAnalyzer(String applicationPath) {
        this.applicationPath = applicationPath;
        this.result = new AnalysisResult();
    }
    
    public AnalysisResult analyzeApplication() {
        try {
            // 分析应用结构
            analyzeApplicationStructure();
            
            // 分析依赖配置
            analyzeDependencies();
            
            // 分析自动配置
            analyzeAutoConfiguration();
            
            // 分析性能配置
            analyzePerformanceConfiguration();
            
            // 分析安全配置
            analyzeSecurityConfiguration();
            
            // 生成分析报告
            return generateReport();
            
        } catch (Exception e) {
            result.addError("分析失败: " + e.getMessage());
            return result;
        }
    }
    
    private void analyzeApplicationStructure() {
        File appDir = new File(applicationPath);
        if (!appDir.exists()) {
            result.addIssue("critical", "structure", "应用目录不存在: " + applicationPath);
            return;
        }
        
        // 检查标准目录结构
        checkStandardStructure(appDir);
        
        // 检查主应用类
        findMainApplicationClass(appDir);
        
        // 分析配置文件
        analyzeConfigurationFiles(appDir);
    }
    
    private void checkStandardStructure(File appDir) {
        String[] requiredDirs = {"src/main/java", "src/main/resources", "src/test/java"};
        
        for (String dir : requiredDirs) {
            File requiredDir = new File(appDir, dir);
            if (!requiredDir.exists()) {
                result.addIssue("medium", "structure", "缺少标准目录: " + dir);
            }
        }
        
        // 检查Maven/Gradle构建文件
        File pomFile = new File(appDir, "pom.xml");
        File buildGradleFile = new File(appDir, "build.gradle");
        
        if (!pomFile.exists() && !buildGradleFile.exists()) {
            result.addIssue("high", "structure", "缺少构建文件(pom.xml或build.gradle)");
        }
    }
    
    private void findMainApplicationClass(File appDir) {
        File javaDir = new File(appDir, "src/main/java");
        if (!javaDir.exists()) {
            return;
        }
        
        List<String> mainClasses = findMainClasses(javaDir);
        
        if (mainClasses.isEmpty()) {
            result.addIssue("high", "structure", "未找到主应用类");
        } else if (mainClasses.size() > 1) {
            result.addIssue("medium", "structure", "发现多个主应用类: " + mainClasses);
        } else {
            result.setMainApplicationClass(mainClasses.get(0));
            
            // 验证主应用类注解
            validateMainApplicationClass(mainClasses.get(0));
        }
    }
    
    private List<String> findMainClasses(File javaDir) {
        List<String> mainClasses = new ArrayList<>();
        findMainClassesRecursive(javaDir, "", mainClasses);
        return mainClasses;
    }
    
    private void findMainClassesRecursive(File dir, String packageName, List<String> mainClasses) {
        File[] files = dir.listFiles();
        if (files == null) return;
        
        for (File file : files) {
            if (file.isDirectory()) {
                findMainClassesRecursive(file, packageName + file.getName() + ".", mainClasses);
            } else if (file.getName().endsWith(".java")) {
                String className = packageName + file.getName().replace(".java", "");
                if (hasMainMethod(file)) {
                    mainClasses.add(className);
                }
            }
        }
    }
    
    private boolean hasMainMethod(File javaFile) {
        try {
            String content = new String(java.io.Files.readAllBytes(javaFile.toPath()));
            return content.contains("public static void main(String[] args)") &&
                   content.contains("SpringApplication.run");
        } catch (IOException e) {
            return false;
        }
    }
    
    private void validateMainApplicationClass(String className) {
        try {
            Class<?> clazz = Class.forName(className);
            SpringBootApplication annotation = clazz.getAnnotation(SpringBootApplication.class);
            
            if (annotation == null) {
                result.addIssue("high", "annotation", "主应用类缺少@SpringBootApplication注解");
            }
            
            // 检查包结构
            String basePackage = clazz.getPackage().getName();
            if (basePackage.equals("default") || basePackage.isEmpty()) {
                result.addIssue("medium", "package", "建议使用具体的包名而非default包");
            }
            
        } catch (ClassNotFoundException e) {
            result.addIssue("medium", "class", "无法加载主应用类: " + className);
        }
    }
    
    private void analyzeConfigurationFiles(File appDir) {
        File resourcesDir = new File(appDir, "src/main/resources");
        if (!resourcesDir.exists()) {
            return;
        }
        
        // 检查application.properties/yml
        File propertiesFile = new File(resourcesDir, "application.properties");
        File yamlFile = new File(resourcesDir, "application.yml");
        
        if (!propertiesFile.exists() && !yamlFile.exists()) {
            result.addIssue("medium", "configuration", "缺少主配置文件");
        } else {
            analyzeMainConfiguration(propertiesFile.exists() ? propertiesFile : yamlFile);
        }
        
        // 检查环境特定配置
        analyzeEnvironmentConfigurations(resourcesDir);
    }
    
    private void analyzeMainConfiguration(File configFile) {
        try {
            String content = new String(java.io.Files.readAllBytes(configFile.toPath()));
            
            // 检查服务器配置
            if (!content.contains("server.port")) {
                result.addIssue("low", "configuration", "未配置服务器端口");
            }
            
            // 检查数据库配置
            if (!content.contains("spring.datasource")) {
                result.addIssue("low", "configuration", "未配置数据库连接");
            }
            
            // 检查日志配置
            if (!content.contains("logging")) {
                result.addIssue("low", "configuration", "未配置日志级别");
            }
            
            // 检查生产环境配置
            if (!content.contains("spring.profiles.active")) {
                result.addIssue("low", "configuration", "未配置活动profile");
            }
            
        } catch (IOException e) {
            result.addIssue("medium", "configuration", "无法读取配置文件: " + e.getMessage());
        }
    }
    
    private void analyzeEnvironmentConfigurations(File resourcesDir) {
        String[] environments = {"dev", "test", "prod"};
        
        for (String env : environments) {
            File devConfig = new File(resourcesDir, "application-" + env + ".properties");
            File devYaml = new File(resourcesDir, "application-" + env + ".yml");
            
            if (!devConfig.exists() && !devYaml.exists()) {
                result.addIssue("low", "configuration", "缺少" + env + "环境配置文件");
            }
        }
    }
    
    private void analyzeDependencies() {
        File pomFile = new File(applicationPath, "pom.xml");
        File buildGradleFile = new File(applicationPath, "build.gradle");
        
        if (pomFile.exists()) {
            analyzeMavenDependencies(pomFile);
        } else if (buildGradleFile.exists()) {
            analyzeGradleDependencies(buildGradleFile);
        }
    }
    
    private void analyzeMavenDependencies(File pomFile) {
        try {
            String content = new String(java.io.Files.readAllBytes(pomFile.toPath()));
            
            // 检查Spring Boot版本
            if (!content.contains("spring-boot-starter-parent")) {
                result.addIssue("high", "dependency", "未继承spring-boot-starter-parent");
            }
            
            // 检查必要依赖
            String[] requiredStarters = {
                "spring-boot-starter-web",
                "spring-boot-starter-test",
                "spring-boot-starter-actuator"
            };
            
            for (String starter : requiredStarters) {
                if (!content.contains(starter)) {
                    result.addIssue("medium", "dependency", "建议添加依赖: " + starter);
                }
            }
            
            // 检查版本管理
            if (!content.contains("<dependencyManagement>")) {
                result.addIssue("low", "dependency", "建议使用dependencyManagement管理版本");
            }
            
        } catch (IOException e) {
            result.addIssue("medium", "dependency", "无法读取pom.xml: " + e.getMessage());
        }
    }
    
    private void analyzeGradleDependencies(File buildGradleFile) {
        try {
            String content = new String(java.io.Files.readAllBytes(buildGradleFile.toPath()));
            
            // 检查Spring Boot插件
            if (!content.contains("org.springframework.boot")) {
                result.addIssue("high", "dependency", "未应用Spring Boot插件");
            }
            
            // 检查必要依赖
            String[] requiredStarters = {
                "spring-boot-starter-web",
                "spring-boot-starter-test",
                "spring-boot-starter-actuator"
            };
            
            for (String starter : requiredStarters) {
                if (!content.contains(starter)) {
                    result.addIssue("medium", "dependency", "建议添加依赖: " + starter);
                }
            }
            
        } catch (IOException e) {
            result.addIssue("medium", "dependency", "无法读取build.gradle: " + e.getMessage());
        }
    }
    
    private void analyzeAutoConfiguration() {
        // 分析自动配置类
        result.addInfo("自动配置分析", "Spring Boot自动配置已启用");
        
        // 检查常见的自动配置优化
        checkAutoConfigurationOptimizations();
    }
    
    private void checkAutoConfigurationOptimizations() {
        // 检查是否需要排除某些自动配置
        result.addIssue("low", "autoconfig", "考虑排除不必要的自动配置以提升启动性能");
        
        // 检查条件注解使用
        result.addIssue("low", "autoconfig", "建议使用@Conditional注解实现条件化配置");
    }
    
    private void analyzePerformanceConfiguration() {
        File resourcesDir = new File(applicationPath, "src/main/resources");
        if (!resourcesDir.exists()) {
            return;
        }
        
        File configFile = new File(resourcesDir, "application.properties");
        if (!configFile.exists()) {
            configFile = new File(resourcesDir, "application.yml");
        }
        
        if (configFile.exists()) {
            analyzePerformanceSettings(configFile);
        }
    }
    
    private void analyzePerformanceSettings(File configFile) {
        try {
            String content = new String(java.io.Files.readAllBytes(configFile.toPath()));
            
            // 检查连接池配置
            if (!content.contains("hikari") && !content.contains("tomcat")) {
                result.addIssue("medium", "performance", "未配置数据库连接池");
            }
            
            // 检查缓存配置
            if (!content.contains("cache")) {
                result.addIssue("low", "performance", "未配置缓存");
            }
            
            // 检查线程池配置
            if (!content.contains("thread")) {
                result.addIssue("low", "performance", "未配置线程池");
            }
            
        } catch (IOException e) {
            result.addIssue("medium", "performance", "无法分析性能配置: " + e.getMessage());
        }
    }
    
    private void analyzeSecurityConfiguration() {
        File resourcesDir = new File(applicationPath, "src/main/resources");
        if (!resourcesDir.exists()) {
            return;
        }
        
        // 检查安全依赖
        File pomFile = new File(applicationPath, "pom.xml");
        File buildGradleFile = new File(applicationPath, "build.gradle");
        
        boolean hasSecurity = false;
        
        if (pomFile.exists()) {
            try {
                String content = new String(java.io.Files.readAllBytes(pomFile.toPath()));
                hasSecurity = content.contains("spring-boot-starter-security");
            } catch (IOException e) {
                // 忽略
            }
        } else if (buildGradleFile.exists()) {
            try {
                String content = new String(java.io.Files.readAllBytes(buildGradleFile.toPath()));
                hasSecurity = content.contains("spring-boot-starter-security");
            } catch (IOException e) {
                // 忽略
            }
        }
        
        if (!hasSecurity) {
            result.addIssue("medium", "security", "未集成Spring Security");
        }
    }
    
    private AnalysisResult generateReport() {
        result.calculateSummary();
        result.generateRecommendations();
        result.calculateHealthScore();
        return result;
    }
    
    // 分析结果类
    public static class AnalysisResult {
        private List<Issue> issues = new ArrayList<>();
        private List<String> infos = new ArrayList<>();
        private List<String> errors = new ArrayList<>();
        private String mainApplicationClass;
        private Summary summary;
        private List<Recommendation> recommendations = new ArrayList<>();
        private int healthScore;
        
        public void addIssue(String severity, String type, String message) {
            issues.add(new Issue(severity, type, message));
        }
        
        public void addInfo(String category, String message) {
            infos.add(category + ": " + message);
        }
        
        public void addError(String error) {
            errors.add(error);
        }
        
        public void setMainApplicationClass(String mainApplicationClass) {
            this.mainApplicationClass = mainApplicationClass;
        }
        
        public void calculateSummary() {
            summary = new Summary();
            summary.totalIssues = issues.size();
            summary.criticalIssues = (int) issues.stream().filter(i -> i.severity.equals("critical")).count();
            summary.highIssues = (int) issues.stream().filter(i -> i.severity.equals("high")).count();
            summary.mediumIssues = (int) issues.stream().filter(i -> i.severity.equals("medium")).count();
            summary.lowIssues = (int) issues.stream().filter(i -> i.severity.equals("low")).count();
        }
        
        public void generateRecommendations() {
            Map<String, Long> issueTypes = issues.stream()
                .collect(Collectors.groupingBy(i -> i.type, Collectors.counting()));
            
            for (Map.Entry<String, Long> entry : issueTypes.entrySet()) {
                recommendations.add(new Recommendation(
                    getPriorityByType(entry.getKey()),
                    entry.getKey(),
                    "发现" + entry.getValue() + "个" + entry.getKey() + "问题",
                    getSuggestionByType(entry.getKey())
                ));
            }
        }
        
        private String getPriorityByType(String type) {
            switch (type) {
                case "structure":
                case "dependency":
                    return "high";
                case "configuration":
                case "security":
                    return "medium";
                default:
                    return "low";
            }
        }
        
        private String getSuggestionByType(String type) {
            switch (type) {
                case "structure":
                    return "遵循Spring Boot标准项目结构";
                case "dependency":
                    return "合理配置依赖版本和范围";
                case "configuration":
                    return "完善应用配置管理";
                case "security":
                    return "加强应用安全配置";
                case "performance":
                    return "优化性能相关配置";
                default:
                    return "参考Spring Boot最佳实践";
            }
        }
        
        public void calculateHealthScore() {
            int score = 100;
            score -= summary.criticalIssues * 20;
            score -= summary.highIssues * 10;
            score -= summary.mediumIssues * 5;
            score -= summary.lowIssues * 2;
            healthScore = Math.max(0, score);
        }
        
        // Getters
        public List<Issue> getIssues() { return issues; }
        public List<String> getInfos() { return infos; }
        public List<String> getErrors() { return errors; }
        public String getMainApplicationClass() { return mainApplicationClass; }
        public Summary getSummary() { return summary; }
        public List<Recommendation> getRecommendations() { return recommendations; }
        public int getHealthScore() { return healthScore; }
    }
    
    public static class Issue {
        public final String severity;
        public final String type;
        public final String message;
        
        public Issue(String severity, String type, String message) {
            this.severity = severity;
            this.type = type;
            this.message = message;
        }
    }
    
    public static class Summary {
        public int totalIssues;
        public int criticalIssues;
        public int highIssues;
        public int mediumIssues;
        public int lowIssues;
    }
    
    public static class Recommendation {
        public final String priority;
        public final String type;
        public final String message;
        public final String suggestion;
        
        public Recommendation(String priority, String type, String message, String suggestion) {
            this.priority = priority;
            this.type = type;
            this.message = message;
            this.suggestion = suggestion;
        }
    }
}

// Spring Boot应用优化器
public class SpringBootOptimizer {
    
    private final String applicationPath;
    
    public SpringBootOptimizer(String applicationPath) {
        this.applicationPath = applicationPath;
    }
    
    public OptimizationResult optimizeApplication() {
        OptimizationResult result = new OptimizationResult();
        
        // 优化依赖配置
        optimizeDependencies(result);
        
        // 优化配置文件
        optimizeConfiguration(result);
        
        // 优化启动性能
        optimizeStartupPerformance(result);
        
        // 优化生产环境配置
        optimizeProductionConfiguration(result);
        
        return result;
    }
    
    private void optimizeDependencies(OptimizationResult result) {
        File pomFile = new File(applicationPath, "pom.xml");
        
        if (pomFile.exists()) {
            try {
                String content = new String(java.io.Files.readAllBytes(pomFile.toPath()));
                
                // 检查是否需要添加性能优化依赖
                if (!content.contains("spring-boot-starter-cache")) {
                    result.addOptimization("dependency", "添加缓存依赖", "添加spring-boot-starter-cache提升性能");
                }
                
                if (!content.contains("micrometer")) {
                    result.addOptimization("dependency", "添加监控依赖", "添加micrometer进行应用监控");
                }
                
            } catch (IOException e) {
                result.addError("优化依赖失败: " + e.getMessage());
            }
        }
    }
    
    private void optimizeConfiguration(OptimizationResult result) {
        File resourcesDir = new File(applicationPath, "src/main/resources");
        if (!resourcesDir.exists()) {
            return;
        }
        
        File configFile = new File(resourcesDir, "application.properties");
        if (!configFile.exists()) {
            configFile = new File(resourcesDir, "application.yml");
        }
        
        if (configFile.exists()) {
            try {
                String content = new String(java.io.Files.readAllBytes(configFile.toPath()));
                
                // 检查性能配置
                if (!content.contains("server.tomcat.max-threads")) {
                    result.addOptimization("performance", "优化线程池配置", "配置Tomcat最大线程数");
                }
                
                if (!content.contains("spring.datasource.hikari")) {
                    result.addOptimization("performance", "优化连接池配置", "配置HikariCP连接池参数");
                }
                
            } catch (IOException e) {
                result.addError("优化配置失败: " + e.getMessage());
            }
        }
    }
    
    private void optimizeStartupPerformance(OptimizationResult result) {
        result.addOptimization("startup", "延迟加载配置", "使用@Lazy注解延迟加载非关键Bean");
        result.addOptimization("startup", "组件扫描优化", "限制@ComponentScan范围减少启动时间");
        result.addOptimization("startup", "自动配置优化", "排除不必要的自动配置类");
    }
    
    private void optimizeProductionConfiguration(OptimizationResult result) {
        result.addOptimization("production", "添加Actuator端点", "配置生产环境监控端点");
        result.addOptimization("production", "配置日志管理", "使用Logback配置生产环境日志");
        result.addOptimization("production", "健康检查配置", "完善应用健康检查机制");
    }
    
    public static class OptimizationResult {
        private List<Optimization> optimizations = new ArrayList<>();
        private List<String> errors = new ArrayList<>();
        
        public void addOptimization(String type, String message, String suggestion) {
            optimizations.add(new Optimization(type, message, suggestion));
        }
        
        public void addError(String error) {
            errors.add(error);
        }
        
        public Map<String, Object> estimateImprovements() {
            Map<String, Object> improvements = new HashMap<>();
            
            int performanceGain = 0;
            int securityGain = 0;
            int maintainabilityGain = 0;
            
            for (Optimization opt : optimizations) {
                switch (opt.type) {
                    case "dependency":
                    case "performance":
                        performanceGain += 20;
                        break;
                    case "configuration":
                        maintainabilityGain += 15;
                        break;
                    case "production":
                        securityGain += 25;
                        break;
                }
            }
            
            improvements.put("performance", performanceGain);
            improvements.put("security", securityGain);
            improvements.put("maintainability", maintainabilityGain);
            
            return improvements;
        }
        
        // Getters
        public List<Optimization> getOptimizations() { return optimizations; }
        public List<String> getErrors() { return errors; }
    }
    
    public static class Optimization {
        public final String type;
        public final String message;
        public final String suggestion;
        
        public Optimization(String type, String message, String suggestion) {
            this.type = type;
            this.message = message;
            this.suggestion = suggestion;
        }
    }
}

// 使用示例
public class SpringBootAnalysisExample {
    public static void main(String[] args) {
        // 分析Spring Boot应用
        SpringBootAnalyzer analyzer = new SpringBootAnalyzer("./my-spring-boot-app");
        SpringBootAnalyzer.AnalysisResult result = analyzer.analyzeApplication();
        
        System.out.println("Spring Boot应用分析报告:");
        System.out.println("健康评分: " + result.getHealthScore());
        System.out.println("主应用类: " + result.getMainApplicationClass());
        System.out.println("问题总数: " + result.getSummary().totalIssues);
        
        System.out.println("\n优化建议:");
        for (SpringBootAnalyzer.Recommendation rec : result.getRecommendations()) {
            System.out.println("- " + rec.message + ": " + rec.suggestion);
        }
        
        // 优化应用
        SpringBootOptimizer optimizer = new SpringBootOptimizer("./my-spring-boot-app");
        SpringBootOptimizer.OptimizationResult optimization = optimizer.optimizeApplication();
        
        System.out.println("\n优化建议:");
        for (SpringBootOptimizer.Optimization opt : optimization.getOptimizations()) {
            System.out.println("- " + opt.message + ": " + opt.suggestion);
        }
        
        System.out.println("\n预期改进:");
        Map<String, Object> improvements = optimization.estimateImprovements();
        improvements.forEach((key, value) -> 
            System.out.println(key + ": " + value + "%"));
    }
}
```

### Spring Boot性能监控器
```java
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.boot.actuate.metrics.MetricsEndpoint;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.management.MBeanServer;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.ThreadMXBean;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Component
public class SpringBootPerformanceMonitor implements HealthIndicator {
    
    private final Map<String, RequestMetrics> requestMetrics = new ConcurrentHashMap<>();
    private final AtomicLong totalRequests = new AtomicLong(0);
    private final long startTime = System.currentTimeMillis();
    
    @Autowired(required = false)
    private MetricsEndpoint metricsEndpoint;
    
    public void recordRequest(String method, String path, int statusCode, long duration) {
        String key = method + " " + path;
        
        requestMetrics.compute(key, (k, metrics) -> {
            if (metrics == null) {
                metrics = new RequestMetrics();
            }
            metrics.addRequest(duration, statusCode);
            return metrics;
        });
        
        totalRequests.incrementAndGet();
    }
    
    @Override
    public Health health() {
        Map<String, Object> details = new HashMap<>();
        
        // 系统指标
        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        details.put("memory_used", memoryBean.getHeapMemoryUsage().getUsed());
        details.put("memory_max", memoryBean.getHeapMemoryUsage().getMax());
        
        ThreadMXBean threadBean = ManagementFactory.getThreadMXBean();
        details.put("thread_count", threadBean.getThreadCount());
        
        // 应用指标
        details.put("uptime", System.currentTimeMillis() - startTime);
        details.put("total_requests", totalRequests.get());
        details.put("request_metrics_size", requestMetrics.size());
        
        // 计算平均响应时间
        double avgResponseTime = requestMetrics.values().stream()
            .mapToDouble(RequestMetrics::getAverageResponseTime)
            .average()
            .orElse(0.0);
        details.put("average_response_time", avgResponseTime);
        
        // 计算错误率
        long totalErrorRequests = requestMetrics.values().stream()
            .mapToLong(RequestMetrics::getErrorCount)
            .sum();
        double errorRate = totalRequests.get() > 0 ? 
            (double) totalErrorRequests / totalRequests.get() * 100 : 0.0;
        details.put("error_rate", errorRate);
        
        // 健康状态判断
        if (errorRate > 10 || avgResponseTime > 5000) {
            return Health.down()
                .withDetails(details)
                .withDetail("reason", "高错误率或响应时间过长")
                .build();
        }
        
        if (errorRate > 5 || avgResponseTime > 2000) {
            return Health.unknown()
                .withDetails(details)
                .withDetail("reason", "错误率或响应时间需要关注")
                .build();
        }
        
        return Health.up()
            .withDetails(details)
            .build();
    }
    
    @RestController
    public static class PerformanceController {
        
        @Autowired
        private SpringBootPerformanceMonitor monitor;
        
        @GetMapping("/actuator/performance")
        public Map<String, Object> getPerformanceMetrics() {
            Map<String, Object> metrics = new HashMap<>();
            
            // 系统指标
            MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
            metrics.put("memory", Map.of(
                "used", memoryBean.getHeapMemoryUsage().getUsed(),
                "max", memoryBean.getHeapMemoryUsage().getMax(),
                "usage", (double) memoryBean.getHeapMemoryUsage().getUsed() / 
                        memoryBean.getHeapMemoryUsage().getMax() * 100
            ));
            
            ThreadMXBean threadBean = ManagementFactory.getThreadMXBean();
            metrics.put("threads", Map.of(
                "count", threadBean.getThreadCount(),
                "peak", threadBean.getPeakThreadCount()
            ));
            
            // JVM指标
            MBeanServer mBeanServer = ManagementFactory.getPlatformMBeanServer();
            try {
                Object cpuUsage = mBeanServer.getAttribute(
                    ManagementFactory.getOperatingSystemMXBean().getObjectName(), 
                    "ProcessCpuLoad"
                );
                metrics.put("cpu_usage", cpuUsage);
            } catch (Exception e) {
                metrics.put("cpu_usage", 0.0);
            }
            
            // 应用指标
            metrics.put("application", Map.of(
                "uptime", System.currentTimeMillis() - monitor.startTime,
                "total_requests", monitor.totalRequests.get(),
                "error_rate", monitor.calculateErrorRate(),
                "average_response_time", monitor.calculateAverageResponseTime()
            ));
            
            // 路由指标
            metrics.put("routes", monitor.getTopRoutes(10));
            
            return metrics;
        }
        
        @GetMapping("/actuator/request-metrics")
        public Map<String, Object> getRequestMetrics() {
            Map<String, Object> metrics = new HashMap<>();
            
            for (Map.Entry<String, RequestMetrics> entry : monitor.requestMetrics.entrySet()) {
                RequestMetrics rm = entry.getValue();
                metrics.put(entry.getKey(), Map.of(
                    "count", rm.getRequestCount(),
                    "average_response_time", rm.getAverageResponseTime(),
                    "max_response_time", rm.getMaxResponseTime(),
                    "min_response_time", rm.getMinResponseTime(),
                    "error_count", rm.getErrorCount(),
                    "error_rate", rm.getErrorRate()
                ));
            }
            
            return metrics;
        }
    }
    
    private double calculateErrorRate() {
        long totalErrorRequests = requestMetrics.values().stream()
            .mapToLong(RequestMetrics::getErrorCount)
            .sum();
        return totalRequests.get() > 0 ? 
            (double) totalErrorRequests / totalRequests.get() * 100 : 0.0;
    }
    
    private double calculateAverageResponseTime() {
        return requestMetrics.values().stream()
            .mapToDouble(RequestMetrics::getAverageResponseTime)
            .average()
            .orElse(0.0);
    }
    
    private Map<String, Object> getTopRoutes(int limit) {
        return requestMetrics.entrySet().stream()
            .sorted((e1, e2) -> Long.compare(e2.getValue().getRequestCount(), e1.getValue().getRequestCount()))
            .limit(limit)
            .collect(HashMap::new, 
                (map, entry) -> map.put(entry.getKey(), Map.of(
                    "count", entry.getValue().getRequestCount(),
                    "average_response_time", entry.getValue().getAverageResponseTime(),
                    "error_rate", entry.getValue().getErrorRate()
                )),
                HashMap::putAll);
    }
    
    // 请求指标类
    public static class RequestMetrics {
        private long requestCount = 0;
        private long totalResponseTime = 0;
        private long minResponseTime = Long.MAX_VALUE;
        private long maxResponseTime = 0;
        private long errorCount = 0;
        
        public synchronized void addRequest(long responseTime, int statusCode) {
            requestCount++;
            totalResponseTime += responseTime;
            
            if (responseTime < minResponseTime) {
                minResponseTime = responseTime;
            }
            
            if (responseTime > maxResponseTime) {
                maxResponseTime = responseTime;
            }
            
            if (statusCode >= 400) {
                errorCount++;
            }
        }
        
        public double getAverageResponseTime() {
            return requestCount > 0 ? (double) totalResponseTime / requestCount : 0.0;
        }
        
        public double getErrorRate() {
            return requestCount > 0 ? (double) errorCount / requestCount * 100 : 0.0;
        }
        
        // Getters
        public long getRequestCount() { return requestCount; }
        public long getMinResponseTime() { return minResponseTime == Long.MAX_VALUE ? 0 : minResponseTime; }
        public long getMaxResponseTime() { return maxResponseTime; }
        public long getErrorCount() { return errorCount; }
    }
}
```

## Spring Boot应用开发最佳实践

### 项目结构
1. **标准目录结构**: 遵循Maven/Gradle标准目录布局
2. **包命名规范**: 使用合理的包层次结构
3. **配置文件组织**: 分环境管理配置文件
4. **测试结构**: 完善的单元测试和集成测试
5. **文档管理**: README和API文档

### 依赖管理
1. **版本管理**: 使用spring-boot-starter-parent管理版本
2. **依赖范围**: 正确配置依赖作用域
3. **可选依赖**: 合理使用可选依赖
4. **依赖排除**: 排除冲突的传递依赖
5. **依赖分析**: 定期分析依赖树

### 配置管理
1. **外部化配置**: 使用外部配置文件
2. **环境配置**: 分环境配置管理
3. **敏感信息**: 加密存储敏感配置
4. **配置验证**: 启用配置验证
5. **配置中心**: 集成配置中心

### 性能优化
1. **启动优化**: 延迟加载和组件扫描优化
2. **连接池配置**: 优化数据库连接池
3. **缓存策略**: 合理使用缓存机制
4. **线程池配置**: 配置合适的线程池
5. **JVM调优**: 优化JVM参数

## 相关技能

- **microservices** - 微服务架构
- **java-development** - Java开发
- **restful-api-design** - RESTful API设计
- **dependency-injection** - 依赖注入
