# 架构分析器参考文档

## 架构分析器概述

### 什么是架构分析器
架构分析器是一个专门用于分析软件系统架构质量和设计模式的工具。该工具通过静态代码分析、依赖关系映射、设计模式识别和质量评估，帮助开发团队发现架构问题、改进设计方案、提升代码质量和系统可维护性。

### 核心分析能力
- **组件结构分析**: 识别系统组件、评估职责分离、检查内聚性
- **依赖关系分析**: 映射依赖关系、检测循环依赖、评估耦合度
- **设计模式识别**: 识别设计模式、发现反模式、提供改进建议
- **质量评估**: 评估可读性、可维护性、可扩展性等质量指标
- **安全架构分析**: 检查安全层次、评估安全模式、验证合规性

## 组件分析引擎

### 组件识别算法

```python
import ast
import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum

class ComponentType(Enum):
    CONTROLLER = "controller"
    SERVICE = "service"
    REPOSITORY = "repository"
    MODEL = "model"
    UTILITY = "utility"
    CONFIGURATION = "configuration"

@dataclass
class Component:
    name: str
    type: ComponentType
    file_path: str
    lines_of_code: int
    dependencies: Set[str]
    responsibilities: List[str]

class ComponentAnalyzer:
    def __init__(self):
        self.component_patterns = {
            ComponentType.CONTROLLER: [
                r'.*Controller.*',
                r'.*Controller$',
                r'.*RestController.*'
            ],
            ComponentType.SERVICE: [
                r'.*Service.*',
                r'.*Service$',
                r'.*Business.*'
            ],
            ComponentType.REPOSITORY: [
                r'.*Repository.*',
                r'.*Repository$',
                r'.*DAO.*',
                r'.*Dao.*'
            ],
            ComponentType.MODEL: [
                r'.*Model.*',
                r'.*Entity.*',
                r'.*DTO.*'
            ],
            ComponentType.UTILITY: [
                r'.*Util.*',
                r'.*Helper.*',
                r'.*Tool.*'
            ]
        }
    
    def identify_components(self, file_paths: List[str]) -> List[Component]:
        """识别项目中的组件"""
        components = []
        
        for file_path in file_paths:
            if not file_path.endswith(('.py', '.java', '.js', '.ts')):
                continue
                
            component = self._analyze_file(file_path)
            if component:
                components.append(component)
        
        return components
    
    def _analyze_file(self, file_path: str) -> Component:
        """分析单个文件识别组件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取类名和函数名
            class_names = self._extract_class_names(content)
            function_names = self._extract_function_names(content)
            
            # 识别组件类型
            component_type = self._identify_component_type(file_path, class_names)
            
            # 分析依赖关系
            dependencies = self._extract_dependencies(content)
            
            # 分析职责
            responsibilities = self._analyze_responsibilities(content, class_names, function_names)
            
            # 计算代码行数
            lines_of_code = len([line for line in content.split('\n') if line.strip()])
            
            return Component(
                name=class_names[0] if class_names else function_names[0] if function_names else "Unknown",
                type=component_type,
                file_path=file_path,
                lines_of_code=lines_of_code,
                dependencies=dependencies,
                responsibilities=responsibilities
            )
            
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            return None
    
    def _extract_class_names(self, content: str) -> List[str]:
        """提取类名"""
        class_names = []
        
        # Python类
        python_classes = re.findall(r'class\s+(\w+)', content)
        class_names.extend(python_classes)
        
        # Java类
        java_classes = re.findall(r'public\s+class\s+(\w+)', content)
        class_names.extend(java_classes)
        
        # JavaScript/TypeScript类
        js_classes = re.findall(r'class\s+(\w+)', content)
        class_names.extend(js_classes)
        
        return class_names
    
    def _extract_function_names(self, content: str) -> List[str]:
        """提取函数名"""
        function_names = []
        
        # Python函数
        python_functions = re.findall(r'def\s+(\w+)', content)
        function_names.extend(python_functions)
        
        # Java方法
        java_methods = re.findall(r'public\s+\w+\s+(\w+)\s*\(', content)
        function_names.extend(java_methods)
        
        # JavaScript函数
        js_functions = re.findall(r'function\s+(\w+)', content)
        function_names.extend(js_functions)
        
        return function_names
    
    def _identify_component_type(self, file_path: str, class_names: List[str]) -> ComponentType:
        """识别组件类型"""
        file_name = file_path.split('/')[-1].lower()
        
        # 基于文件名识别
        for component_type, patterns in self.component_patterns.items():
            for pattern in patterns:
                if re.search(pattern, file_name, re.IGNORECASE):
                    return component_type
        
        # 基于类名识别
        for class_name in class_names:
            for component_type, patterns in self.component_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, class_name, re.IGNORECASE):
                        return component_type
        
        return ComponentType.UTILITY  # 默认为工具类
    
    def _extract_dependencies(self, content: str) -> Set[str]:
        """提取依赖关系"""
        dependencies = set()
        
        # Python imports
        python_imports = re.findall(r'from\s+(\w+)|import\s+(\w+)', content)
        for match in python_imports:
            dependencies.add(match[0] or match[1])
        
        # Java imports
        java_imports = re.findall(r'import\s+([\w.]+);', content)
        dependencies.update(java_imports)
        
        # JavaScript imports
        js_imports = re.findall(r'import.*from\s+[\'"]([^\'"]+)[\'"]', content)
        dependencies.update(js_imports)
        
        return dependencies
    
    def _analyze_responsibilities(self, content: str, class_names: List[str], function_names: List[str]) -> List[str]:
        """分析组件职责"""
        responsibilities = []
        
        # 基于方法名分析职责
        responsibility_keywords = {
            'create': '创建数据',
            'read': '读取数据',
            'update': '更新数据',
            'delete': '删除数据',
            'validate': '验证数据',
            'process': '处理业务逻辑',
            'calculate': '计算',
            'render': '渲染视图',
            'handle': '处理请求',
            'send': '发送数据',
            'receive': '接收数据',
            'parse': '解析数据',
            'format': '格式化数据'
        }
        
        for func_name in function_names:
            for keyword, responsibility in responsibility_keywords.items():
                if keyword.lower() in func_name.lower():
                    responsibilities.append(responsibility)
                    break
        
        # 基于类名分析职责
        if any('Controller' in name for name in class_names):
            responsibilities.append('处理HTTP请求')
            responsibilities.append('协调业务逻辑')
        
        if any('Service' in name for name in class_names):
            responsibilities.append('实现业务逻辑')
            responsibilities.append('协调数据访问')
        
        if any('Repository' in name or 'DAO' in name for name in class_names):
            responsibilities.append('数据持久化')
            responsibilities.append('数据库操作')
        
        return list(set(responsibilities))  # 去重

# 使用示例
def analyze_project_architecture(project_path: str):
    """分析项目架构"""
    import os
    
    # 获取所有源代码文件
    source_files = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith(('.py', '.java', '.js', '.ts')):
                source_files.append(os.path.join(root, file))
    
    # 分析组件
    analyzer = ComponentAnalyzer()
    components = analyzer.identify_components(source_files)
    
    # 生成分析报告
    print(f"发现 {len(components)} 个组件:")
    for component in components:
        print(f"- {component.name} ({component.type.value})")
        print(f"  文件: {component.file_path}")
        print(f"  代码行数: {component.lines_of_code}")
        print(f"  职责: {', '.join(component.responsibilities)}")
        print(f"  依赖: {', '.join(component.dependencies)}")
        print()

if __name__ == "__main__":
    analyze_project_architecture("./sample_project")
```

## 依赖关系分析器

### 依赖图构建

```python
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Set
from collections import defaultdict

class DependencyAnalyzer:
    def __init__(self, components: List[Component]):
        self.components = components
        self.dependency_graph = nx.DiGraph()
        self._build_dependency_graph()
    
    def _build_dependency_graph(self):
        """构建依赖关系图"""
        # 添加节点
        for component in self.components:
            self.dependency_graph.add_node(
                component.name,
                type=component.type.value,
                file_path=component.file_path,
                lines_of_code=component.lines_of_code
            )
        
        # 添加边（依赖关系）
        for component in self.components:
            for dependency in component.dependencies:
                # 查找依赖对应的组件
                target_component = self._find_component_by_name(dependency)
                if target_component:
                    self.dependency_graph.add_edge(
                        component.name,
                        target_component.name,
                        dependency_type="import"
                    )
    
    def _find_component_by_name(self, name: str) -> str:
        """根据名称查找组件"""
        for component in self.components:
            if name.lower() in component.name.lower():
                return component.name
        return None
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """检测循环依赖"""
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            return cycles
        except:
            return []
    
    def calculate_coupling_metrics(self) -> Dict[str, Dict]:
        """计算耦合度指标"""
        metrics = {}
        
        for component in self.components:
            # 出度（该组件依赖其他组件的数量）
            afferent_coupling = self.dependency_graph.out_degree(component.name)
            
            # 入度（其他组件依赖该组件的数量）
            efferent_coupling = self.dependency_graph.in_degree(component.name)
            
            # 不稳定性指标 I = Ce / (Ce + Ca)
            instability = efferent_coupling / (afferent_coupling + efferent_coupling) if (afferent_coupling + efferent_coupling) > 0 else 0
            
            metrics[component.name] = {
                'afferent_coupling': afferent_coupling,
                'efferent_coupling': efferent_coupling,
                'instability': instability,
                'total_dependencies': afferent_coupling + efferent_coupling
            }
        
        return metrics
    
    def analyze_dependency_levels(self) -> Dict[str, int]:
        """分析依赖层次"""
        try:
            levels = {}
            for component in self.components:
                # 计算到根节点的最长路径
                level = 0
                try:
                    level = nx.shortest_path_length(self.dependency_graph, component.name, reverse=True)
                except:
                    level = 0
                levels[component.name] = level
            return levels
        except:
            return {comp.name: 0 for comp in self.components}
    
    def visualize_dependency_graph(self, output_file: str = "dependency_graph.png"):
        """可视化依赖关系图"""
        plt.figure(figsize=(12, 8))
        
        # 设置布局
        pos = nx.spring_layout(self.dependency_graph, k=2, iterations=50)
        
        # 绘制节点
        node_colors = []
        for component in self.components:
            if component.type == ComponentType.CONTROLLER:
                node_colors.append('lightblue')
            elif component.type == ComponentType.SERVICE:
                node_colors.append('lightgreen')
            elif component.type == ComponentType.REPOSITORY:
                node_colors.append('lightyellow')
            elif component.type == ComponentType.MODEL:
                node_colors.append('lightcoral')
            else:
                node_colors.append('lightgray')
        
        nx.draw_networkx_nodes(
            self.dependency_graph, pos,
            node_color=node_colors,
            node_size=1000,
            alpha=0.7
        )
        
        # 绘制边
        nx.draw_networkx_edges(
            self.dependency_graph, pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            alpha=0.5
        )
        
        # 绘制标签
        nx.draw_networkx_labels(
            self.dependency_graph, pos,
            font_size=8,
            font_weight='bold'
        )
        
        plt.title("组件依赖关系图")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_dependency_report(self) -> str:
        """生成依赖分析报告"""
        report = []
        report.append("# 依赖关系分析报告\n")
        
        # 循环依赖检测
        cycles = self.detect_circular_dependencies()
        if cycles:
            report.append("## 循环依赖问题\n")
            for i, cycle in enumerate(cycles, 1):
                report.append(f"### 循环依赖 {i}")
                report.append(f"依赖链: {' -> '.join(cycle)} -> {cycle[0]}")
                report.append("建议: 引入接口抽象或重构以打破循环依赖\n")
        
        # 耦合度分析
        coupling_metrics = self.calculate_coupling_metrics()
        report.append("## 耦合度分析\n")
        report.append("| 组件 | 出度 | 入度 | 不稳定性 | 总依赖数 |")
        report.append("|------|------|------|----------|----------|")
        
        for component_name, metrics in coupling_metrics.items():
            report.append(f"| {component_name} | {metrics['afferent_coupling']} | "
                         f"{metrics['efferent_coupling']} | {metrics['instability']:.2f} | "
                         f"{metrics['total_dependencies']} |")
        
        # 依赖层次分析
        levels = self.analyze_dependency_levels()
        report.append("\n## 依赖层次分析\n")
        level_groups = defaultdict(list)
        for component, level in levels.items():
            level_groups[level].append(component)
        
        for level in sorted(level_groups.keys()):
            report.append(f"### 层次 {level}")
            for component in level_groups[level]:
                report.append(f"- {component}")
            report.append("")
        
        return "\n".join(report)

# 使用示例
def analyze_dependencies(components: List[Component]):
    """分析组件依赖关系"""
    analyzer = DependencyAnalyzer(components)
    
    # 生成报告
    report = analyzer.generate_dependency_report()
    print(report)
    
    # 可视化
    analyzer.visualize_dependency_graph()
    
    return analyzer
```

## 设计模式识别器

### 模式检测算法

```python
import ast
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class DesignPattern(Enum):
    SINGLETON = "singleton"
    FACTORY = "factory"
    BUILDER = "builder"
    ADAPTER = "adapter"
    DECORATOR = "decorator"
    PROXY = "proxy"
    OBSERVER = "observer"
    STRATEGY = "strategy"
    COMMAND = "command"
    FACADE = "facade"

@dataclass
class PatternInstance:
    pattern: DesignPattern
    classes: List[str]
    methods: List[str]
    confidence: float
    description: str

class DesignPatternDetector:
    def __init__(self):
        self.pattern_detectors = {
            DesignPattern.SINGLETON: self._detect_singleton,
            DesignPattern.FACTORY: self._detect_factory,
            DesignPattern.ADAPTER: self._detect_adapter,
            DesignPattern.OBSERVER: self._detect_observer,
            DesignPattern.STRATEGY: self._detect_strategy
        }
    
    def detect_patterns(self, file_path: str) -> List[PatternInstance]:
        """检测设计模式"""
        patterns = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 检测各种模式
            for pattern, detector in self.pattern_detectors.items():
                pattern_instances = detector(tree, content)
                patterns.extend(pattern_instances)
        
        except Exception as e:
            print(f"Error detecting patterns in {file_path}: {e}")
        
        return patterns
    
    def _detect_singleton(self, tree: ast.AST, content: str) -> List[PatternInstance]:
        """检测单例模式"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查单例模式的特征
                has_private_constructor = False
                has_static_instance = False
                has_get_instance_method = False
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # 检查构造函数
                        if item.name == '__init__':
                            # 检查是否有私有属性
                            for stmt in item.body:
                                if isinstance(stmt, ast.Assign):
                                    for target in stmt.targets:
                                        if isinstance(target, ast.Name) and target.id.startswith('_'):
                                            has_private_constructor = True
                        
                        # 检查获取实例方法
                        elif item.name in ['get_instance', 'getInstance', 'instance']:
                            has_get_instance_method = True
                    
                    elif isinstance(item, ast.Assign):
                        # 检查静态实例
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id in ['_instance', '__instance']:
                                has_static_instance = True
                
                # 评估置信度
                confidence = 0.0
                if has_private_constructor:
                    confidence += 0.3
                if has_static_instance:
                    confidence += 0.4
                if has_get_instance_method:
                    confidence += 0.3
                
                if confidence >= 0.6:
                    patterns.append(PatternInstance(
                        pattern=DesignPattern.SINGLETON,
                        classes=[node.name],
                        methods=[item.name for item in node.body if isinstance(item, ast.FunctionDef)],
                        confidence=confidence,
                        description=f"类 {node.name} 实现了单例模式"
                    ))
        
        return patterns
    
    def _detect_factory(self, tree: ast.AST, content: str) -> List[PatternInstance]:
        """检测工厂模式"""
        patterns = []
        
        factory_classes = []
        product_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查工厂类
                if any(keyword in node.name.lower() for keyword in ['factory', 'creator', 'builder']):
                    factory_classes.append(node.name)
                    
                    # 检查是否有创建方法
                    create_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if any(keyword in item.name.lower() for keyword in ['create', 'make', 'build', 'get']):
                                create_methods.append(item.name)
                    
                    if create_methods:
                        patterns.append(PatternInstance(
                            pattern=DesignPattern.FACTORY,
                            classes=[node.name],
                            methods=create_methods,
                            confidence=0.8,
                            description=f"类 {node.name} 实现了工厂模式"
                        ))
                
                # 检查产品类
                elif any(keyword in node.name.lower() for keyword in ['product', 'item', 'entity']):
                    product_classes.append(node.name)
        
        return patterns
    
    def _detect_adapter(self, tree: ast.AST, content: str) -> List[PatternInstance]:
        """检测适配器模式"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查适配器类
                if any(keyword in node.name.lower() for keyword in ['adapter', 'wrapper', 'converter']):
                    # 检查是否继承或实现接口
                    has_inheritance = len(node.bases) > 0
                    
                    # 检查是否有适配方法
                    adapter_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            adapter_methods.append(item.name)
                    
                    if has_inheritance and adapter_methods:
                        patterns.append(PatternInstance(
                            pattern=DesignPattern.ADAPTER,
                            classes=[node.name],
                            methods=adapter_methods,
                            confidence=0.7,
                            description=f"类 {node.name} 实现了适配器模式"
                        ))
        
        return patterns
    
    def _detect_observer(self, tree: ast.AST, content: str) -> List[PatternInstance]:
        """检测观察者模式"""
        patterns = []
        
        observer_classes = []
        subject_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查观察者类
                if any(keyword in node.name.lower() for keyword in ['observer', 'listener', 'subscriber']):
                    observer_classes.append(node.name)
                
                # 检查主题类
                elif any(keyword in node.name.lower() for keyword in ['subject', 'observable', 'publisher']):
                    # 检查是否有通知方法
                    notify_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if any(keyword in item.name.lower() for keyword in ['notify', 'update', 'publish']):
                                notify_methods.append(item.name)
                    
                    if notify_methods:
                        subject_classes.append(node.name)
        
        # 如果同时有观察者和主题类，可能实现了观察者模式
        if observer_classes and subject_classes:
            patterns.append(PatternInstance(
                pattern=DesignPattern.OBSERVER,
                classes=observer_classes + subject_classes,
                methods=[],
                confidence=0.6,
                description=f"发现观察者模式: 主题类 {', '.join(subject_classes)}, 观察者类 {', '.join(observer_classes)}"
            ))
        
        return patterns
    
    def _detect_strategy(self, tree: ast.AST, content: str) -> List[PatternInstance]:
        """检测策略模式"""
        patterns = []
        
        strategy_classes = []
        context_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查策略类
                if any(keyword in node.name.lower() for keyword in ['strategy']):
                    strategy_classes.append(node.name)
                
                # 检查上下文类
                elif any(keyword in node.name.lower() for keyword in ['context']):
                    context_classes.append(node.name)
        
        if strategy_classes and context_classes:
            patterns.append(PatternInstance(
                pattern=DesignPattern.STRATEGY,
                classes=strategy_classes + context_classes,
                methods=[],
                confidence=0.7,
                description=f"发现策略模式: 策略类 {', '.join(strategy_classes)}, 上下文类 {', '.join(context_classes)}"
            ))
        
        return patterns

# 使用示例
def detect_design_patterns(project_path: str):
    """检测项目中的设计模式"""
    import os
    
    all_patterns = []
    
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                detector = DesignPatternDetector()
                patterns = detector.detect_patterns(file_path)
                all_patterns.extend(patterns)
    
    # 生成报告
    print("## 设计模式检测报告\n")
    
    pattern_groups = {}
    for pattern in all_patterns:
        if pattern.pattern not in pattern_groups:
            pattern_groups[pattern.pattern] = []
        pattern_groups[pattern.pattern].append(pattern)
    
    for pattern_type, instances in pattern_groups.items():
        print(f"### {pattern_type.value.upper()} 模式")
        for instance in instances:
            print(f"- {instance.description}")
            print(f"  置信度: {instance.confidence:.2f}")
            print(f"  涉及类: {', '.join(instance.classes)}")
        print()

if __name__ == "__main__":
    detect_design_patterns("./sample_project")
```

## 质量评估器

### 代码质量指标计算

```python
import radon.metrics as radon_metrics
import radon.complexity as radon_complexity
from typing import Dict, List, Tuple
import subprocess
import os

class QualityAssessment:
    def __init__(self, project_path: str):
        self.project_path = project_path
    
    def calculate_complexity_metrics(self, file_path: str) -> Dict:
        """计算复杂度指标"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 计算圈复杂度
            complexity = radon_complexity.cc_visit(content)
            
            metrics = {
                'cyclomatic_complexity': [],
                'cognitive_complexity': [],
                'halstead_metrics': {},
                'maintainability_index': 0
            }
            
            for item in complexity:
                metrics['cyclomatic_complexity'].append({
                    'name': item.name,
                    'complexity': item.complexity,
                    'rank': item.rank
                })
            
            # 计算可维护性指数
            mi = radon_metrics.mi_visit(content, True)
            metrics['maintainability_index'] = mi
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating complexity for {file_path}: {e}")
            return {}
    
    def analyze_code_structure(self, file_path: str) -> Dict:
        """分析代码结构"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 计算基本指标
            lines = content.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            comment_lines = len([line for line in lines if line.strip().startswith('#')])
            blank_lines = total_lines - code_lines - comment_lines
            
            # 计算函数和类的数量
            import ast
            tree = ast.parse(content)
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
            return {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'comment_lines': comment_lines,
                'blank_lines': blank_lines,
                'comment_ratio': comment_lines / total_lines if total_lines > 0 else 0,
                'function_count': len(functions),
                'class_count': len(classes),
                'functions': functions,
                'classes': classes
            }
            
        except Exception as e:
            print(f"Error analyzing structure for {file_path}: {e}")
            return {}
    
    def assess_test_coverage(self, file_path: str) -> Dict:
        """评估测试覆盖率"""
        try:
            # 使用coverage.py评估测试覆盖率
            result = subprocess.run(
                ['coverage', 'run', '--source', os.path.dirname(file_path), file_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 获取覆盖率报告
                coverage_result = subprocess.run(
                    ['coverage', 'report', '--format=json'],
                    capture_output=True,
                    text=True
                )
                
                if coverage_result.returncode == 0:
                    import json
                    coverage_data = json.loads(coverage_result.stdout)
                    return {
                        'coverage_percentage': coverage_data.get('totals', {}).get('percent_covered', 0),
                        'covered_lines': coverage_data.get('totals', {}).get('covered_lines', 0),
                        'missing_lines': coverage_data.get('totals', {}).get('missing_lines', 0)
                    }
            
            return {'coverage_percentage': 0, 'covered_lines': 0, 'missing_lines': 0}
            
        except Exception as e:
            print(f"Error assessing test coverage for {file_path}: {e}")
            return {'coverage_percentage': 0, 'covered_lines': 0, 'missing_lines': 0}
    
    def generate_quality_report(self, file_path: str) -> str:
        """生成质量评估报告"""
        report = []
        report.append(f"# 代码质量评估报告 - {os.path.basename(file_path)}\n")
        
        # 代码结构分析
        structure = self.analyze_code_structure(file_path)
        report.append("## 代码结构分析\n")
        report.append(f"- 总行数: {structure.get('total_lines', 0)}")
        report.append(f"- 代码行数: {structure.get('code_lines', 0)}")
        report.append(f"- 注释行数: {structure.get('comment_lines', 0)}")
        report.append(f"- 空行数: {structure.get('blank_lines', 0)}")
        report.append(f"- 注释比例: {structure.get('comment_ratio', 0):.2%}")
        report.append(f"- 函数数量: {structure.get('function_count', 0)}")
        report.append(f"- 类数量: {structure.get('class_count', 0)}\n")
        
        # 复杂度分析
        complexity = self.calculate_complexity_metrics(file_path)
        if complexity.get('cyclomatic_complexity'):
            report.append("## 复杂度分析\n")
            report.append("| 函数名 | 圈复杂度 | 等级 |")
            report.append("|--------|----------|------|")
            
            for item in complexity['cyclomatic_complexity']:
                report.append(f"| {item['name']} | {item['complexity']} | {item['rank']} |")
            
            report.append(f"\n可维护性指数: {complexity.get('maintainability_index', 0):.2f}\n")
        
        # 测试覆盖率
        coverage = self.assess_test_coverage(file_path)
        report.append("## 测试覆盖率\n")
        report.append(f"- 覆盖率: {coverage['coverage_percentage']:.2f}%")
        report.append(f"- 覆盖行数: {coverage['covered_lines']}")
        report.append(f"- 未覆盖行数: {coverage['missing_lines']}\n")
        
        # 质量建议
        report.append("## 质量改进建议\n")
        
        if structure.get('comment_ratio', 0) < 0.1:
            report.append("- 建议增加代码注释，当前注释比例过低")
        
        high_complexity = [item for item in complexity.get('cyclomatic_complexity', []) if item['complexity'] > 10]
        if high_complexity:
            report.append(f"- 以下函数复杂度过高，建议重构: {', '.join([item['name'] for item in high_complexity])}")
        
        if coverage['coverage_percentage'] < 80:
            report.append("- 建议提高测试覆盖率到80%以上")
        
        return "\n".join(report)

# 使用示例
def assess_code_quality(project_path: str):
    """评估代码质量"""
    assessor = QualityAssessment(project_path)
    
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                report = assessor.generate_quality_report(file_path)
                print(report)
                print("=" * 50)

if __name__ == "__main__":
    assess_code_quality("./sample_project")
```

这个架构分析器提供了完整的架构分析功能，包括组件识别、依赖关系分析、设计模式检测和质量评估，帮助开发团队全面了解和改进系统架构。
