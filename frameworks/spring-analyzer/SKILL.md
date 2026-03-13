---
name: Spring框架分析器
description: "当分析Spring框架应用时，检查Bean配置，优化性能，审查安全设置。验证Spring Boot配置，分析依赖注入，和最佳实践。"
license: MIT
---

# Spring框架分析器技能

## 概述
Spring框架提供了企业级功能，但错误的配置会导致性能低下、难以维护的代码。需要建立完善的Spring应用分析和优化机制。

**核心原则**: Spring启用企业功能，但错误配置导致缓慢、不可维护的代码。

## 何时使用

**始终:**
- 审查Spring代码
- Spring Boot配置
- 性能优化
- 依赖注入审查
- Spring应用安全审计
- 数据库访问优化

**触发短语:**
- "审查Spring模式"
- "优化Spring性能"
- "Spring Data JPA分析"
- "检查Spring安全配置"
- "Spring事务处理"
- "分析Spring Bean配置"

## Spring框架分析功能

### Bean配置分析
- 依赖注入模式检查
- Bean生命周期分析
- Singleton vs Prototype作用域
- 循环依赖检测
- Bean作用域配置验证

### 性能分析
- 懒加载策略检查
- 数据库连接池配置
- 缓存配置分析
- 查询优化建议
- 内存使用分析

### 最佳实践验证
- 异常处理模式
- 日志配置检查
- 单元测试模式
- 集成测试设置
- 代码结构分析

## 常见Spring配置问题

### 循环依赖
```
问题:
Bean之间存在循环依赖关系

后果:
- 应用启动失败
- Bean创建异常
- 内存泄漏
- 性能下降

解决方案:
- 重构Bean依赖关系
- 使用@Lazy注解
- 引入接口抽象
- 使用ApplicationContextAware
```

### 作用域配置错误
```
问题:
Bean作用域配置不当

后果:
- 状态共享问题
- 内存泄漏
- 并发安全问题
- 性能影响

解决方案:
- 正确选择作用域
- 避免Singleton状态
- 使用@Scope注解
- 考虑线程安全
```

### 事务配置问题
```
问题:
事务传播行为配置错误

后果:
- 数据不一致
- 事务回滚失败
- 死锁问题
- 性能问题

解决方案:
- 正确配置传播行为
- 设置合适的隔离级别
- 处理异常回滚
- 优化事务边界
```

## Spring优化策略

### Bean配置优化
```
懒加载:
- 减少启动时间
- 按需加载Bean
- 避免不必要的依赖
- 提升应用性能

作用域管理:
- 合理使用Singleton
- 谨慎使用Prototype
- 考虑Request作用域
- 避免状态共享
```

### 性能优化技巧
```
数据库优化:
- 连接池配置
- 批处理操作
- 查询缓存
- N+1问题解决

缓存策略:
- Spring Cache配置
- 多级缓存设计
- 缓存失效策略
- 分布式缓存
```

## 代码实现示例

### Spring配置分析器
```java
package com.example.spring.analyzer;

import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.context.annotation.ClassPathScanningCandidateComponentProvider;
import org.springframework.core.type.filter.AnnotationTypeFilter;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;
import org.springframework.stereotype.Repository;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.*;
import java.util.stream.Collectors;

public class SpringConfigurationAnalyzer {
    
    private final ApplicationContext applicationContext;
    private final Map<String, List<String>> issues = new HashMap<>();
    private final Map<String, Object> metrics = new HashMap<>();
    
    public SpringConfigurationAnalyzer(ApplicationContext applicationContext) {
        this.applicationContext = applicationContext;
    }
    
    public AnalysisReport analyzeConfiguration() {
        AnalysisReport report = new AnalysisReport();
        
        // 分析Bean定义
        analyzeBeanDefinitions(report);
        
        // 检查循环依赖
        checkCircularDependencies(report);
        
        // 分析作用域配置
        analyzeScopes(report);
        
        // 检查自动装配
        analyzeAutowired(report);
        
        // 分析事务配置
        analyzeTransactionConfiguration(report);
        
        // 检查安全配置
        analyzeSecurityConfiguration(report);
        
        // 性能分析
        analyzePerformance(report);
        
        return report;
    }
    
    private void analyzeBeanDefinitions(AnalysisReport report) {
        String[] beanNames = applicationContext.getBeanDefinitionNames();
        
        Map<String, Integer> annotationCounts = new HashMap<>();
        Map<String, List<String>> beansByAnnotation = new HashMap<>();
        
        for (String beanName : beanNames) {
            try {
                Class<?> beanClass = applicationContext.getType(beanName);
                if (beanClass != null) {
                    // 检查注解
                    if (beanClass.isAnnotationPresent(Component.class)) {
                        addAnnotation(annotationCounts, beansByAnnotation, "Component", beanName);
                    }
                    if (beanClass.isAnnotationPresent(Service.class)) {
                        addAnnotation(annotationCounts, beansByAnnotation, "Service", beanName);
                    }
                    if (beanClass.isAnnotationPresent(Repository.class)) {
                        addAnnotation(annotationCounts, beansByAnnotation, "Repository", beanName);
                    }
                    if (beanClass.isAnnotationPresent(Configuration.class)) {
                        addAnnotation(annotationCounts, beansByAnnotation, "Configuration", beanName);
                    }
                    if (beanClass.isAnnotationPresent(RestController.class)) {
                        addAnnotation(annotationCounts, beansByAnnotation, "RestController", beanName);
                    }
                }
            } catch (Exception e) {
                report.addIssue("Bean分析", "无法分析Bean: " + beanName + " - " + e.getMessage());
            }
        }
        
        report.setMetric("总Bean数量", beanNames.length);
        report.setMetric("注解分布", annotationCounts);
        report.setMetric("Bean按注解分组", beansByAnnotation);
    }
    
    private void addAnnotation(Map<String, Integer> counts, Map<String, List<String>> grouping, 
                              String annotation, String beanName) {
        counts.put(annotation, counts.getOrDefault(annotation, 0) + 1);
        grouping.computeIfAbsent(annotation, k -> new ArrayList<>()).add(beanName);
    }
    
    private void checkCircularDependencies(AnalysisReport report) {
        String[] beanNames = applicationContext.getBeanDefinitionNames();
        Map<String, Set<String>> dependencyGraph = new HashMap<>();
        
        // 构建依赖图
        for (String beanName : beanNames) {
            try {
                Class<?> beanClass = applicationContext.getType(beanName);
                if (beanClass != null) {
                    Set<String> dependencies = new HashSet<>();
                    
                    // 检查字段注入
                    for (Field field : beanClass.getDeclaredFields()) {
                        if (field.isAnnotationPresent(Autowired.class)) {
                            dependencies.add(field.getType().getName());
                        }
                    }
                    
                    // 检查方法注入
                    for (Method method : beanClass.getDeclaredMethods()) {
                        if (method.isAnnotationPresent(Autowired.class)) {
                            for (Class<?> paramType : method.getParameterTypes()) {
                                dependencies.add(paramType.getName());
                            }
                        }
                    }
                    
                    dependencyGraph.put(beanName, dependencies);
                }
            } catch (Exception e) {
                report.addIssue("循环依赖检查", "无法检查Bean: " + beanName + " - " + e.getMessage());
            }
        }
        
        // 检测循环依赖
        Set<String> visited = new HashSet<>();
        Set<String> recursionStack = new HashSet<>();
        
        for (String beanName : dependencyGraph.keySet()) {
            if (!visited.contains(beanName)) {
                if (hasCircularDependency(beanName, dependencyGraph, visited, recursionStack)) {
                    report.addIssue("循环依赖", "检测到循环依赖，涉及Bean: " + beanName);
                }
            }
        }
    }
    
    private boolean hasCircularDependency(String beanName, Map<String, Set<String>> dependencyGraph,
                                       Set<String> visited, Set<String> recursionStack) {
        visited.add(beanName);
        recursionStack.add(beanName);
        
        Set<String> dependencies = dependencyGraph.get(beanName);
        if (dependencies != null) {
            for (String dependency : dependencies) {
                if (!visited.contains(dependency) && 
                    hasCircularDependency(dependency, dependencyGraph, visited, recursionStack)) {
                    return true;
                } else if (recursionStack.contains(dependency)) {
                    return true;
                }
            }
        }
        
        recursionStack.remove(beanName);
        return false;
    }
    
    private void analyzeScopes(AnalysisReport report) {
        String[] beanNames = applicationContext.getBeanDefinitionNames();
        Map<String, Integer> scopeCounts = new HashMap<>();
        List<String> prototypeBeans = new ArrayList<>();
        
        for (String beanName : beanNames) {
            try {
                BeanDefinition beanDefinition = applicationContext.getBeanFactory().getBeanDefinition(beanName);
                String scope = beanDefinition.getScope();
                
                scopeCounts.put(scope, scopeCounts.getOrDefault(scope, 0) + 1);
                
                if ("prototype".equals(scope)) {
                    prototypeBeans.add(beanName);
                }
            } catch (Exception e) {
                report.addIssue("作用域分析", "无法获取Bean作用域: " + beanName + " - " + e.getMessage());
            }
        }
        
        report.setMetric("作用域分布", scopeCounts);
        
        // 检查Prototype Bean的最佳实践
        for (String prototypeBean : prototypeBeans) {
            try {
                Class<?> beanClass = applicationContext.getType(prototypeBean);
                if (beanClass != null) {
                    // 检查是否有状态
                    boolean hasState = hasStatefulFields(beanClass);
                    if (hasState) {
                        report.addIssue("作用域问题", "Prototype Bean包含状态字段: " + prototypeBean);
                    }
                }
            } catch (Exception e) {
                report.addIssue("作用域分析", "无法分析Prototype Bean: " + prototypeBean);
            }
        }
    }
    
    private boolean hasStatefulFields(Class<?> clazz) {
        for (Field field : clazz.getDeclaredFields()) {
            if (!field.getType().isPrimitive() && 
                !field.getType().equals(String.class) &&
                !field.isAnnotationPresent(Autowired.class)) {
                return true;
            }
        }
        return false;
    }
    
    private void analyzeAutowired(AnalysisReport report) {
        String[] beanNames = applicationContext.getBeanDefinitionNames();
        int fieldAutowiredCount = 0;
        int methodAutowiredCount = 0;
        List<String> constructorInjectionBeans = new ArrayList<>();
        
        for (String beanName : beanNames) {
            try {
                Class<?> beanClass = applicationContext.getType(beanName);
                if (beanClass != null) {
                    boolean hasFieldAutowired = false;
                    boolean hasMethodAutowired = false;
                    boolean hasConstructorInjection = false;
                    
                    // 检查字段注入
                    for (Field field : beanClass.getDeclaredFields()) {
                        if (field.isAnnotationPresent(Autowired.class)) {
                            hasFieldAutowired = true;
                            fieldAutowiredCount++;
                        }
                    }
                    
                    // 检查方法注入
                    for (Method method : beanClass.getDeclaredMethods()) {
                        if (method.isAnnotationPresent(Autowired.class)) {
                            hasMethodAutowired = true;
                            methodAutowiredCount++;
                        }
                    }
                    
                    // 检查构造函数注入
                    for (Constructor<?> constructor : beanClass.getConstructors()) {
                        if (constructor.isAnnotationPresent(Autowired.class) || 
                            constructor.getParameterCount() > 0) {
                            hasConstructorInjection = true;
                            constructorInjectionBeans.add(beanName);
                            break;
                        }
                    }
                    
                    // 推荐最佳实践
                    if (hasFieldAutowired && !hasConstructorInjection) {
                        report.addRecommendation("依赖注入", 
                            "建议使用构造函数注入替代字段注入: " + beanName);
                    }
                }
            } catch (Exception e) {
                report.addIssue("依赖注入分析", "无法分析Bean: " + beanName + " - " + e.getMessage());
            }
        }
        
        report.setMetric("字段注入数量", fieldAutowiredCount);
        report.setMetric("方法注入数量", methodAutowiredCount);
        report.setMetric("构造函数注入Bean", constructorInjectionBeans);
    }
    
    private void analyzeTransactionConfiguration(AnalysisReport report) {
        // 检查事务管理器配置
        try {
            if (applicationContext.containsBean("transactionManager")) {
                report.setMetric("事务管理器", "已配置");
            } else {
                report.addIssue("事务配置", "未找到事务管理器配置");
            }
        } catch (Exception e) {
            report.addIssue("事务配置", "检查事务管理器失败: " + e.getMessage());
        }
        
        // 分析事务注解使用
        String[] beanNames = applicationContext.getBeanDefinitionNames();
        int transactionalMethodCount = 0;
        List<String> transactionalBeans = new ArrayList<>();
        
        for (String beanName : beanNames) {
            try {
                Class<?> beanClass = applicationContext.getType(beanName);
                if (beanClass != null) {
                    boolean hasTransactional = false;
                    
                    for (Method method : beanClass.getDeclaredMethods()) {
                        if (method.isAnnotationPresent(org.springframework.transaction.annotation.Transactional.class)) {
                            hasTransactional = true;
                            transactionalMethodCount++;
                        }
                    }
                    
                    if (hasTransactional) {
                        transactionalBeans.add(beanName);
                    }
                }
            } catch (Exception e) {
                report.addIssue("事务分析", "无法分析Bean事务: " + beanName + " - " + e.getMessage());
            }
        }
        
        report.setMetric("事务方法数量", transactionalMethodCount);
        report.setMetric("事务Bean列表", transactionalBeans);
    }
    
    private void analyzeSecurityConfiguration(AnalysisReport report) {
        // 检查Spring Security配置
        try {
            String[] securityBeans = applicationContext.getBeanNamesForType(
                org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter.class);
            
            if (securityBeans.length > 0) {
                report.setMetric("安全配置", "已配置");
            } else {
                report.addRecommendation("安全配置", "考虑配置Spring Security");
            }
        } catch (Exception e) {
            // Security可能不在类路径中
        }
    }
    
    private void analyzePerformance(AnalysisReport report) {
        // 分析Bean数量
        String[] beanNames = applicationContext.getBeanDefinitionNames();
        report.setMetric("Bean总数", beanNames.length);
        
        if (beanNames.length > 1000) {
            report.addIssue("性能", "Bean数量过多，可能影响启动性能");
        }
        
        // 分析懒加载使用
        int lazyBeanCount = 0;
        for (String beanName : beanNames) {
            try {
                BeanDefinition beanDefinition = applicationContext.getBeanFactory().getBeanDefinition(beanName);
                if (beanDefinition.isLazyInit()) {
                    lazyBeanCount++;
                }
            } catch (Exception e) {
                // 忽略错误
            }
        }
        
        report.setMetric("懒加载Bean数量", lazyBeanCount);
        report.setMetric("懒加载比例", (double) lazyBeanCount / beanNames.length * 100);
    }
    
    public static class AnalysisReport {
        private final Map<String, List<String>> issues = new HashMap<>();
        private final Map<String, List<String>> recommendations = new HashMap<>();
        private final Map<String, Object> metrics = new HashMap<>();
        
        public void addIssue(String category, String issue) {
            issues.computeIfAbsent(category, k -> new ArrayList<>()).add(issue);
        }
        
        public void addRecommendation(String category, String recommendation) {
            recommendations.computeIfAbsent(category, k -> new ArrayList<>()).add(recommendation);
        }
        
        public void setMetric(String name, Object value) {
            metrics.put(name, value);
        }
        
        // Getters
        public Map<String, List<String>> getIssues() { return issues; }
        public Map<String, List<String>> getRecommendations() { return recommendations; }
        public Map<String, Object> getMetrics() { return metrics; }
        
        public void printReport() {
            System.out.println("=== Spring配置分析报告 ===");
            
            System.out.println("\n--- 指标 ---");
            metrics.forEach((key, value) -> {
                System.out.println(key + ": " + value);
            });
            
            System.out.println("\n--- 问题 ---");
            issues.forEach((category, issueList) -> {
                System.out.println(category + ":");
                issueList.forEach(issue -> System.out.println("  - " + issue));
            });
            
            System.out.println("\n--- 建议 ---");
            recommendations.forEach((category, recList) -> {
                System.out.println(category + ":");
                recList.forEach(rec -> System.out.println("  - " + rec));
            });
        }
    }
}

// 使用示例
@Component
class SpringAnalysisService {
    
    @Autowired
    private ApplicationContext applicationContext;
    
    public void analyzeAndReport() {
        SpringConfigurationAnalyzer analyzer = new SpringConfigurationAnalyzer(applicationContext);
        SpringConfigurationAnalyzer.AnalysisReport report = analyzer.analyzeConfiguration();
        
        report.printReport();
        
        // 可以将报告保存到文件或发送到监控系统
        saveReportToFile(report);
    }
    
    private void saveReportToFile(SpringConfigurationAnalyzer.AnalysisReport report) {
        // 实现报告保存逻辑
    }
}
```

### Spring性能优化器
```java
package com.example.spring.optimizer;

import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.transaction.annotation.EnableTransactionManagement;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Configuration
@EnableCaching
@EnableTransactionManagement
public class SpringPerformanceOptimizer {
    
    private final ApplicationContext applicationContext;
    private final Map<String, PerformanceMetrics> performanceMetrics = new ConcurrentHashMap<>();
    
    public SpringPerformanceOptimizer(ApplicationContext applicationContext) {
        this.applicationContext = applicationContext;
    }
    
    @Bean
    @ConditionalOnProperty(name = "spring.performance.monitoring", havingValue = "true")
    public PerformanceMonitor performanceMonitor() {
        return new PerformanceMonitor(applicationContext);
    }
    
    @Bean
    @ConditionalOnProperty(name = "spring.performance.optimization", havingValue = "true")
    public PerformanceOptimizer performanceOptimizer() {
        return new PerformanceOptimizer(applicationContext);
    }
    
    public static class PerformanceMonitor {
        
        private final ApplicationContext applicationContext;
        
        public PerformanceMonitor(ApplicationContext applicationContext) {
            this.applicationContext = applicationContext;
        }
        
        public Map<String, Object> collectMetrics() {
            Map<String, Object> metrics = new HashMap<>();
            
            // Bean启动时间
            metrics.put("beanStartupTime", measureBeanStartupTime());
            
            // 内存使用
            metrics.put("memoryUsage", getMemoryUsage());
            
            // Bean数量统计
            metrics.put("beanStatistics", getBeanStatistics());
            
            // 依赖复杂度
            metrics.put("dependencyComplexity", calculateDependencyComplexity());
            
            return metrics;
        }
        
        private long measureBeanStartupTime() {
            long startTime = System.currentTimeMillis();
            applicationContext.getBeanDefinitionNames();
            return System.currentTimeMillis() - startTime;
        }
        
        private Map<String, Object> getMemoryUsage() {
            Runtime runtime = Runtime.getRuntime();
            Map<String, Object> memory = new HashMap<>();
            memory.put("totalMemory", runtime.totalMemory());
            memory.put("freeMemory", runtime.freeMemory());
            memory.put("usedMemory", runtime.totalMemory() - runtime.freeMemory());
            memory.put("maxMemory", runtime.maxMemory());
            return memory;
        }
        
        private Map<String, Object> getBeanStatistics() {
            String[] beanNames = applicationContext.getBeanDefinitionNames();
            Map<String, Object> stats = new HashMap<>();
            
            stats.put("totalBeans", beanNames.length);
            
            Map<String, Integer> scopeDistribution = new HashMap<>();
            for (String beanName : beanNames) {
                try {
                    BeanDefinition beanDefinition = applicationContext.getBeanFactory()
                        .getBeanDefinition(beanName);
                    String scope = beanDefinition.getScope();
                    scopeDistribution.put(scope, scopeDistribution.getOrDefault(scope, 0) + 1);
                } catch (Exception e) {
                    // 忽略错误
                }
            }
            
            stats.put("scopeDistribution", scopeDistribution);
            return stats;
        }
        
        private double calculateDependencyComplexity() {
            String[] beanNames = applicationContext.getBeanDefinitionNames();
            int totalDependencies = 0;
            
            for (String beanName : beanNames) {
                try {
                    Class<?> beanClass = applicationContext.getType(beanName);
                    if (beanClass != null) {
                        // 计算依赖数量
                        int dependencies = 0;
                        for (Field field : beanClass.getDeclaredFields()) {
                            if (field.isAnnotationPresent(Autowired.class)) {
                                dependencies++;
                            }
                        }
                        totalDependencies += dependencies;
                    }
                } catch (Exception e) {
                    // 忽略错误
                }
            }
            
            return beanNames.length > 0 ? (double) totalDependencies / beanNames.length : 0;
        }
    }
    
    public static class PerformanceOptimizer {
        
        private final ApplicationContext applicationContext;
        
        public PerformanceOptimizer(ApplicationContext applicationContext) {
            this.applicationContext = applicationContext;
        }
        
        public List<OptimizationSuggestion> generateOptimizations() {
            List<OptimizationSuggestion> suggestions = new ArrayList<>();
            
            // 检查懒加载优化
            suggestions.addAll(checkLazyLoadingOptimization());
            
            // 检查作用域优化
            suggestions.addAll(checkScopeOptimization());
            
            // 检查依赖注入优化
            suggestions.addAll(checkDependencyInjectionOptimization());
            
            // 检查缓存优化
            suggestions.addAll(checkCacheOptimization());
            
            return suggestions;
        }
        
        private List<OptimizationSuggestion> checkLazyLoadingOptimization() {
            List<OptimizationSuggestion> suggestions = new ArrayList<>();
            String[] beanNames = applicationContext.getBeanDefinitionNames();
            
            int eagerBeans = 0;
            List<String> candidatesForLazy = new ArrayList<>();
            
            for (String beanName : beanNames) {
                try {
                    BeanDefinition beanDefinition = applicationContext.getBeanFactory()
                        .getBeanDefinition(beanName);
                    
                    if (!beanDefinition.isLazyInit()) {
                        eagerBeans++;
                        
                        // 检查是否适合懒加载
                        Class<?> beanClass = applicationContext.getType(beanName);
                        if (beanClass != null && isCandidateForLazyLoading(beanClass)) {
                            candidatesForLazy.add(beanName);
                        }
                    }
                } catch (Exception e) {
                    // 忽略错误
                }
            }
            
            if (eagerBeans > beanNames.length * 0.8) {
                suggestions.add(new OptimizationSuggestion(
                    "懒加载优化",
                    "建议将非核心Bean配置为懒加载以提升启动性能",
                    candidatesForLazy,
                    "medium"
                ));
            }
            
            return suggestions;
        }
        
        private boolean isCandidateForLazyLoading(Class<?> beanClass) {
            // 检查是否为工具类或可选组件
            String packageName = beanClass.getPackage().getName();
            return packageName.contains(".util.") || 
                   packageName.contains(".helper.") ||
                   packageName.contains(".optional.") ||
                   beanClass.isAnnotationPresent(org.springframework.stereotype.Component.class);
        }
        
        private List<OptimizationSuggestion> checkScopeOptimization() {
            List<OptimizationSuggestion> suggestions = new ArrayList<>();
            String[] beanNames = applicationContext.getBeanDefinitionNames();
            
            for (String beanName : beanNames) {
                try {
                    BeanDefinition beanDefinition = applicationContext.getBeanFactory()
                        .getBeanDefinition(beanName);
                    
                    if ("singleton".equals(beanDefinition.getScope())) {
                        Class<?> beanClass = applicationContext.getType(beanName);
                        if (beanClass != null && hasStatefulFields(beanClass)) {
                            suggestions.add(new OptimizationSuggestion(
                                "作用域优化",
                                "Bean包含状态，考虑使用prototype作用域: " + beanName,
                                Arrays.asList(beanName),
                                "high"
                            ));
                        }
                    }
                } catch (Exception e) {
                    // 忽略错误
                }
            }
            
            return suggestions;
        }
        
        private boolean hasStatefulFields(Class<?> clazz) {
            for (Field field : clazz.getDeclaredFields()) {
                if (!field.getType().isPrimitive() && 
                    !field.getType().equals(String.class) &&
                    !field.isAnnotationPresent(Autowired.class)) {
                    return true;
                }
            }
            return false;
        }
        
        private List<OptimizationSuggestion> checkDependencyInjectionOptimization() {
            List<OptimizationSuggestion> suggestions = new ArrayList<>();
            String[] beanNames = applicationContext.getBeanDefinitionNames();
            
            for (String beanName : beanNames) {
                try {
                    Class<?> beanClass = applicationContext.getType(beanName);
                    if (beanClass != null) {
                        List<Field> fieldInjected = new ArrayList<>();
                        
                        for (Field field : beanClass.getDeclaredFields()) {
                            if (field.isAnnotationPresent(Autowired.class)) {
                                fieldInjected.add(field);
                            }
                        }
                        
                        if (fieldInjected.size() > 3) {
                            suggestions.add(new OptimizationSuggestion(
                                "依赖注入优化",
                                "Bean字段注入过多，建议使用构造函数注入: " + beanName,
                                Arrays.asList(beanName),
                                "medium"
                            ));
                        }
                    }
                } catch (Exception e) {
                    // 忽略错误
                }
            }
            
            return suggestions;
        }
        
        private List<OptimizationSuggestion> checkCacheOptimization() {
            List<OptimizationSuggestion> suggestions = new ArrayList<>();
            
            // 检查是否有缓存管理器
            try {
                applicationContext.getBean(org.springframework.cache.CacheManager.class);
            } catch (Exception e) {
                suggestions.add(new OptimizationSuggestion(
                    "缓存优化",
                    "建议配置缓存管理器以提升性能",
                    Collections.emptyList(),
                    "low"
                ));
            }
            
            return suggestions;
        }
    }
    
    public static class OptimizationSuggestion {
        private final String category;
        private final String description;
        private final List<String> affectedBeans;
        private final String priority;
        
        public OptimizationSuggestion(String category, String description, 
                                    List<String> affectedBeans, String priority) {
            this.category = category;
            this.description = description;
            this.affectedBeans = affectedBeans;
            this.priority = priority;
        }
        
        // Getters
        public String getCategory() { return category; }
        public String getDescription() { return description; }
        public List<String> getAffectedBeans() { return affectedBeans; }
        public String getPriority() { return priority; }
    }
}
```

## Spring最佳实践

### 配置管理
1. **外部化配置**: 使用application.properties/yml
2. **Profile管理**: 开发、测试、生产环境分离
3. **Bean命名**: 使用有意义的Bean名称
4. **条件装配**: 使用@Conditional注解

### 依赖注入
1. **构造函数注入**: 推荐的主要方式
2. **避免字段注入**: 除非必要
3. **接口编程**: 依赖接口而非实现
4. **循环依赖**: 避免设计循环依赖

### 性能优化
1. **懒加载**: 非核心组件使用懒加载
2. **作用域选择**: 合理选择Bean作用域
3. **缓存策略**: 适当使用Spring Cache
4. **连接池**: 配置数据库连接池

## 相关技能

- **api-validator** - API接口验证和设计
- **database-query-analyzer** - 数据库查询分析
- **security-scanner** - 安全漏洞扫描
- **performance-profiler** - 性能分析和监控
