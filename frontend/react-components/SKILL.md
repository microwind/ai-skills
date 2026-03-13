---
name: React组件最佳实践
description: "当开发React组件时，设计组件架构，实现状态管理，优化性能。处理组件通信，实现复用逻辑，和最佳实践应用。"
license: MIT
---

# React组件最佳实践技能

## 概述
React组件开发是前端开发的核心技能。不当的组件设计会导致代码重复、性能问题、维护困难。需要系统性的组件设计和优化方法。

**核心原则**: 好的React组件应该单一职责、可复用、可测试、性能优良。坏的组件会职责混乱、难以复用、测试困难、性能低下。

## 何时使用

**始终:**
- 设计新组件时
- 重构现有组件时
- 优化组件性能时
- 处理组件通信时
- 实现复用逻辑时
- 测试组件功能时

**触发短语:**
- "React组件最佳实践"
- "组件设计模式"
- "状态管理策略"
- "组件性能优化"
- "组件通信方案"
- "复用逻辑实现"

## React组件功能

### 组件设计
- 单一职责原则
- 组件层次结构
- 接口设计规范
- 可复用性设计
- 可测试性考虑

### 状态管理
- 本地状态管理
- 全局状态方案
- 状态提升策略
- 状态同步处理
- 状态持久化

### 性能优化
- 渲染优化
- 内存管理
- 组件懒加载
- 虚拟化处理
- 防抖节流

### 组件通信
- 属性传递
- 回调函数
- Context API
- 状态管理库
- 事件总线

## 常见React组件问题

### 组件职责混乱
```
问题:
组件承担过多职责，代码复杂难维护

错误示例:
- 一个组件处理UI、业务逻辑、数据获取
- 组件内部包含过多不相关的功能
- 组件依赖过多外部状态
- 组件接口设计不合理

解决方案:
1. 遵循单一职责原则
2. 拆分复杂组件
3. 提取业务逻辑
4. 设计清晰的组件接口
```

### 性能问题
```
问题:
组件渲染性能差，用户体验不佳

错误示例:
- 不必要的重新渲染
- 缺少React.memo优化
- 状态更新过于频繁
- 大量DOM操作

解决方案:
1. 使用React.memo优化
2. 合理使用useMemo和useCallback
3. 优化状态更新策略
4. 减少不必要的渲染
```

### 状态管理混乱
```
问题:
组件状态管理复杂，数据流不清晰

错误示例:
- 状态分散在各个组件
- 状态同步困难
- 状态更新逻辑混乱
- 缺少统一的状态管理

解决方案:
1. 使用合适的状态管理方案
2. 明确数据流向
3. 统一状态更新逻辑
4. 实现状态持久化
```

### 组件复用困难
```
问题:
组件难以复用，代码重复严重

错误示例:
- 组件耦合度过高
- 缺少抽象层
- 配置不够灵活
- 硬编码过多

解决方案:
1. 降低组件耦合度
2. 提取公共逻辑
3. 增强组件配置性
4. 使用高阶组件和Hook
```

## 代码实现示例

### React组件设计器
```python
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ComponentType(Enum):
    """组件类型"""
    FUNCTIONAL = "functional"
    CLASS = "class"
    HOC = "hoc"
    CUSTOM_HOOK = "custom_hook"

class StateManagementType(Enum):
    """状态管理类型"""
    LOCAL_STATE = "local_state"
    CONTEXT = "context"
    REDUX = "redux"
    MOBX = "mobx"
    ZUSTAND = "zustand"

@dataclass
class ComponentSpec:
    """组件规格"""
    name: str
    type: ComponentType
    props: List[Dict[str, Any]]
    state: List[Dict[str, Any]]
    methods: List[Dict[str, Any]]
    lifecycle: List[str]
    dependencies: List[str]

@dataclass
class PerformanceOptimization:
    """性能优化配置"""
    use_memo: List[str]
    use_callback: List[str]
    memo_wrap: bool
    lazy_load: bool
    virtualize: bool

class ReactComponentDesigner:
    def __init__(self):
        self.component_templates = {}
        self.optimization_strategies = {}
        
    def design_component(self, spec: ComponentSpec, 
                        state_management: StateManagementType = StateManagementType.LOC_STATE,
                        performance_config: Optional[PerformanceOptimization] = None) -> str:
        """设计React组件"""
        
        # 生成组件代码
        if spec.type == ComponentType.FUNCTIONAL:
            component_code = self._generate_functional_component(spec, state_management, performance_config)
        elif spec.type == ComponentType.CLASS:
            component_code = self._generate_class_component(spec, state_management, performance_config)
        else:
            raise ValueError(f"不支持的组件类型: {spec.type}")
        
        return component_code
    
    def _generate_functional_component(self, spec: ComponentSpec, 
                                    state_management: StateManagementType,
                                    performance_config: Optional[PerformanceOptimization]) -> str:
        """生成函数组件"""
        imports = self._generate_imports(spec, state_management, performance_config)
        
        # 组件定义
        component_lines = []
        
        # Props接口定义
        if spec.props:
            props_interface = self._generate_props_interface(spec.props)
            component_lines.append(props_interface)
        
        # 组件函数
        component_lines.append(f"function {spec.name}({{") if spec.props else f"function {spec.name}() {{")
        
        # Hook导入
        hook_imports = self._generate_hook_imports(state_management, performance_config)
        component_lines.extend(hook_imports)
        
        # 状态定义
        state_definitions = self._generate_state_definitions(spec.state, state_management)
        component_lines.extend(state_definitions)
        
        # 性能优化Hook
        if performance_config:
            optimizations = self._generate_performance_optimizations(performance_config, spec)
            component_lines.extend(optimizations)
        
        # 事件处理函数
        event_handlers = self._generate_event_handlers(spec.methods)
        component_lines.extend(event_handlers)
        
        # 副作用
        effects = self._generate_effects(spec.lifecycle, spec.state, spec.dependencies)
        component_lines.extend(effects)
        
        # 渲染逻辑
        render_logic = self._generate_render_logic(spec)
        component_lines.extend(render_logic)
        
        component_lines.append("}")
        
        # 组件导出
        if performance_config and performance_config.memo_wrap:
            component_lines.append(f"export default React.memo({spec.name});")
        else:
            component_lines.append(f"export default {spec.name};")
        
        return '\n'.join([imports] + component_lines)
    
    def _generate_class_component(self, spec: ComponentSpec,
                                state_management: StateManagementType,
                                performance_config: Optional[PerformanceOptimization]) -> str:
        """生成类组件"""
        imports = self._generate_imports(spec, state_management, performance_config)
        
        component_lines = []
        
        # Props接口定义
        if spec.props:
            props_interface = self._generate_props_interface(spec.props)
            component_lines.append(props_interface)
        
        # 组件类定义
        component_lines.append(f"class {spec.name} extends React.Component {{")
        
        # 构造函数
        if spec.state:
            constructor = self._generate_constructor(spec.state)
            component_lines.append(constructor)
        
        # 生命周期方法
        lifecycle_methods = self._generate_lifecycle_methods(spec.lifecycle, spec.state, spec.dependencies)
        component_lines.extend(lifecycle_methods)
        
        # 事件处理方法
        event_handlers = self._generate_class_methods(spec.methods)
        component_lines.extend(event_handlers)
        
        # 渲染方法
        render_method = self._generate_class_render(spec)
        component_lines.append(render_method)
        
        component_lines.append("}")
        
        # 组件导出
        component_lines.append(f"export default {spec.name};")
        
        return '\n'.join([imports] + component_lines)
    
    def _generate_imports(self, spec: ComponentSpec, 
                         state_management: StateManagementType,
                         performance_config: Optional[PerformanceOptimization]) -> str:
        """生成导入语句"""
        imports = ["import React;"]
        
        # 状态管理相关导入
        if state_management == StateManagementType.CONTEXT:
            imports.append("import React, { useContext };")
        elif state_management == StateManagementType.REDUX:
            imports.extend(["import { useSelector, useDispatch } from 'react-redux';"])
        elif state_management == StateManagementType.ZUSTAND:
            imports.append("import { useStore } from 'zustand';")
        
        # 性能优化相关导入
        if performance_config:
            if performance_config.use_memo or performance_config.use_callback:
                imports.append("import React, { useMemo, useCallback };")
            if performance_config.lazy_load:
                imports.append("import React, { lazy, Suspense };")
            if performance_config.virtualize:
                imports.append("import { FixedSizeList as List } from 'react-window';")
        
        return '\n'.join(imports)
    
    def _generate_props_interface(self, props: List[Dict[str, Any]]) -> str:
        """生成Props接口"""
        interface_lines = ["interface Props {"]
        
        for prop in props:
            prop_name = prop['name']
            prop_type = prop['type']
            optional = prop.get('optional', False)
            default_value = prop.get('default', None)
            
            optional_mark = "?" if optional else ""
            line = f"  {prop_name}{optional_mark}: {prop_type};"
            
            if default_value is not None:
                line += f" // 默认值: {default_value}"
            
            interface_lines.append(line)
        
        interface_lines.append("}")
        
        return '\n'.join(interface_lines)
    
    def _generate_hook_imports(self, state_management: StateManagementType,
                              performance_config: Optional[PerformanceOptimization]) -> List[str]:
        """生成Hook导入"""
        imports = []
        
        # 基础Hook
        imports.append("  const [count, setCount] = React.useState(0);")
        imports.append("  const [data, setData] = React.useState(null);")
        
        # 状态管理Hook
        if state_management == StateManagementType.CONTEXT:
            imports.append("  const context = useContext(MyContext);")
        elif state_management == StateManagementType.REDUX:
            imports.append("  const dispatch = useDispatch();")
            imports.append("  const state = useSelector(state => state.myReducer);")
        elif state_management == StateManagementType.ZUSTAND:
            imports.append("  const { state, actions } = useStore();")
        
        return imports
    
    def _generate_state_definitions(self, state_specs: List[Dict[str, Any]], 
                                  state_management: StateManagementType) -> List[str]:
        """生成状态定义"""
        definitions = []
        
        for state_spec in state_specs:
            state_name = state_spec['name']
            state_type = state_spec['type']
            initial_value = state_spec.get('initial', None)
            
            if initial_value is not None:
                definition = f"  const [{state_name}, set{state_name.capitalize()}] = React.useState({initial_value});"
            else:
                definition = f"  const [{state_name}, set{state_name.capitalize()}] = React.useState<{state_type}>();"
            
            definitions.append(definition)
        
        return definitions
    
    def _generate_performance_optimizations(self, config: PerformanceOptimization, 
                                          spec: ComponentSpec) -> List[str]:
        """生成性能优化代码"""
        optimizations = []
        
        # useMemo优化
        for memo_item in config.use_memo:
            optimizations.append(f"  const memoized{memo_item} = useMemo(() => {{")
            optimizations.append(f"    // 计算{memo_item}的逻辑")
            optimizations.append(f"    return compute{memo_item}();")
            optimizations.append(f"  }}, [/* 依赖项 */]);")
        
        # useCallback优化
        for callback_item in config.use_callback:
            optimizations.append(f"  const handle{callback_item} = useCallback(() => {{")
            optimizations.append(f"    // 处理{callback_item}的逻辑")
            optimizations.append(f"  }}, [/* 依赖项 */]);")
        
        return optimizations
    
    def _generate_event_handlers(self, methods: List[Dict[str, Any]]) -> List[str]:
        """生成事件处理函数"""
        handlers = []
        
        for method in methods:
            method_name = method['name']
            method_params = method.get('params', [])
            method_body = method.get('body', f"// {method_name}实现逻辑")
            
            params_str = ", ".join(method_params)
            handlers.append(f"  const {method_name} = ({params_str}) => {{")
            handlers.append(f"    {method_body}")
            handlers.append(f"  }};")
        
        return handlers
    
    def _generate_effects(self, lifecycle: List[str], state: List[Dict[str, Any]], 
                         dependencies: List[str]) -> List[str]:
        """生成副作用Hook"""
        effects = []
        
        # 基础useEffect
        if 'componentDidMount' in lifecycle or 'useEffect' in lifecycle:
            effects.append("  React.useEffect(() => {")
            effects.append("    // 组件挂载后的逻辑")
            effects.append("    console.log('组件已挂载');")
            effects.append("  }, []);")
        
        # 状态更新effect
        for state_spec in state:
            state_name = state_spec['name']
            effects.append(f"  React.useEffect(() => {{")
            effects.append(f"    // {state_name}变化时的逻辑")
            effects.append(f"    console.log('{state_name} changed:', {state_name});")
            effects.append(f"  }}, [{state_name}]);")
        
        return effects
    
    def _generate_render_logic(self, spec: ComponentSpec) -> List[str]:
        """生成渲染逻辑"""
        render_lines = ["  return ("]
        render_lines.append("    <div>")
        render_lines.append(f"      <h1>{spec.name}组件</h1>")
        
        # 渲染props
        for prop in spec.props:
            prop_name = prop['name']
            render_lines.append(f"      <div>{{props.{prop_name}}}</div>")
        
        # 渲染状态
        for state_spec in spec.state:
            state_name = state_spec['name']
            render_lines.append(f"      <div>状态: {{{state_name}}}</div>")
        
        # 渲染按钮
        for method in spec.methods:
            method_name = method['name']
            render_lines.append(f"      <button onClick={{{method_name}}}>触发{method_name}</button>")
        
        render_lines.append("    </div>")
        render_lines.append("  );")
        
        return render_lines
    
    def _generate_constructor(self, state_specs: List[Dict[str, Any]]) -> str:
        """生成构造函数"""
        constructor_lines = ["  constructor(props) {"]
        constructor_lines.append("    super(props);")
        constructor_lines.append("    this.state = {")
        
        for state_spec in state_specs:
            state_name = state_spec['name']
            initial_value = state_spec.get('initial', 'null')
            constructor_lines.append(f"      {state_name}: {initial_value},")
        
        constructor_lines.append("    };")
        constructor_lines.append("  }")
        
        return '\n'.join(constructor_lines)
    
    def _generate_lifecycle_methods(self, lifecycle: List[str], state: List[Dict[str, Any]], 
                                   dependencies: List[str]) -> List[str]:
        """生成生命周期方法"""
        methods = []
        
        if 'componentDidMount' in lifecycle:
            methods.append("  componentDidMount() {")
            methods.append("    // 组件挂载后的逻辑")
            methods.append("    console.log('组件已挂载');")
            methods.append("  }")
        
        if 'componentDidUpdate' in lifecycle:
            methods.append("  componentDidUpdate(prevProps, prevState) {")
            methods.append("    // 组件更新后的逻辑")
            methods.append("    console.log('组件已更新');")
            methods.append("  }")
        
        if 'componentWillUnmount' in lifecycle:
            methods.append("  componentWillUnmount() {")
            methods.append("    // 组件卸载前的清理逻辑")
            methods.append("    console.log('组件即将卸载');")
            methods.append("  }")
        
        return methods
    
    def _generate_class_methods(self, methods: List[Dict[str, Any]]) -> List[str]:
        """生成类方法"""
        class_methods = []
        
        for method in methods:
            method_name = method['name']
            method_params = method.get('params', [])
            method_body = method.get('body', f"// {method_name}实现逻辑")
            
            params_str = ", ".join(method_params)
            class_methods.append(f"  {method_name}({params_str}) {{")
            class_methods.append(f"    {method_body}")
            class_methods.append(f"  }}")
        
        return class_methods
    
    def _generate_class_render(self, spec: ComponentSpec) -> str:
        """生成类组件render方法"""
        render_lines = ["  render() {"]
        render_lines.append("    return (")
        render_lines.append("      <div>")
        render_lines.append(f"        <h1>{spec.name}组件</h1>")
        
        # 渲染props
        for prop in spec.props:
            prop_name = prop['name']
            render_lines.append(f"        <div>{{this.props.{prop_name}}}</div>")
        
        # 渲染状态
        for state_spec in spec.state:
            state_name = state_spec['name']
            render_lines.append(f"        <div>状态: {{this.state.{state_name}}}</div>")
        
        # 渲染按钮
        for method in spec.methods:
            method_name = method['name']
            render_lines.append(f"        <button onClick={{this.{method_name}}}>触发{method_name}</button>")
        
        render_lines.append("      </div>")
        render_lines.append("    );")
        render_lines.append("  }")
        
        return '\n'.join(render_lines)

# React组件分析器
class ReactComponentAnalyzer:
    def __init__(self):
        self.analysis_rules = {}
        
    def analyze_component(self, component_code: str) -> Dict[str, Any]:
        """分析React组件代码"""
        analysis = {
            'component_type': self._detect_component_type(component_code),
            'complexity_score': 0,
            'issues': [],
            'recommendations': [],
            'metrics': {}
        }
        
        # 分析复杂度
        analysis['complexity_score'] = self._calculate_complexity(component_code)
        
        # 检测问题
        analysis['issues'] = self._detect_issues(component_code)
        
        # 生成建议
        analysis['recommendations'] = self._generate_recommendations(analysis['issues'])
        
        # 计算指标
        analysis['metrics'] = self._calculate_metrics(component_code)
        
        return analysis
    
    def _detect_component_type(self, code: str) -> str:
        """检测组件类型"""
        if 'class' in code and 'extends React.Component' in code:
            return 'class'
        elif 'function' in code or 'const' in code and '=>' in code:
            return 'functional'
        elif 'React.memo' in code:
            return 'memo'
        else:
            return 'unknown'
    
    def _calculate_complexity(self, code: str) -> int:
        """计算组件复杂度"""
        complexity = 0
        
        # 基于行数
        lines = code.split('\n')
        complexity += len(lines) // 10
        
        # 基于状态数量
        state_count = code.count('useState') + code.count('this.state')
        complexity += state_count * 2
        
        # 基于方法数量
        method_count = code.count('const ') + code.count('function') + code.count('  ')
        complexity += method_count
        
        # 基于嵌套层级
        nesting_level = max(line.count('  ') for line in lines) // 2
        complexity += nesting_level
        
        return complexity
    
    def _detect_issues(self, code: str) -> List[str]:
        """检测代码问题"""
        issues = []
        
        # 检查性能问题
        if 'useState' in code and 'useMemo' not in code and 'useCallback' not in code:
            issues.append("可能存在不必要的重新渲染，建议使用useMemo或useCallback优化")
        
        # 检查状态管理
        if code.count('useState') > 5:
            issues.append("状态过多，建议考虑使用useReducer或状态管理库")
        
        # 检查组件大小
        lines = len(code.split('\n'))
        if lines > 200:
            issues.append("组件过大，建议拆分为更小的组件")
        
        # 检查Props数量
        props_count = code.count('props.')
        if props_count > 10:
            issues.append("Props过多，建议使用对象或配置")
        
        # 检查内联函数
        if 'onClick={() =>' in code:
            issues.append("存在内联函数，建议使用useCallback优化")
        
        # 检查直接修改状态
        if 'this.state.' in code and '=' in code:
            issues.append("直接修改state，应该使用setState")
        
        return issues
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for issue in issues:
            if '重新渲染' in issue:
                recommendations.append("使用React.memo、useMemo和useCallback优化渲染性能")
            elif '状态过多' in issue:
                recommendations.append("考虑使用useReducer或引入状态管理库如Redux、Zustand")
            elif '组件过大' in issue:
                recommendations.append("将大组件拆分为多个小组件，提高可维护性")
            elif 'Props过多' in issue:
                recommendations.append("使用配置对象或Context API减少Props传递")
            elif '内联函数' in issue:
                recommendations.append("将内联函数提取为useCallback或组件方法")
            elif '直接修改state' in issue:
                recommendations.append("使用setState或状态更新函数来修改状态")
        
        return list(set(recommendations))  # 去重
    
    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """计算代码指标"""
        metrics = {}
        
        lines = code.split('\n')
        
        # 基础指标
        metrics['total_lines'] = len(lines)
        metrics['code_lines'] = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
        metrics['comment_lines'] = len([line for line in lines if line.strip().startswith('//')])
        
        # Hook使用
        metrics['hooks_used'] = {
            'useState': code.count('useState'),
            'useEffect': code.count('useEffect'),
            'useMemo': code.count('useMemo'),
            'useCallback': code.count('useCallback'),
            'useContext': code.count('useContext'),
            'useReducer': code.count('useReducer')
        }
        
        # 组件特征
        metrics['props_count'] = code.count('props.')
        metrics['state_count'] = code.count('useState') + code.count('this.state')
        metrics['method_count'] = code.count('const ') + code.count('function')
        
        return metrics

# 使用示例
def main():
    print("=== React组件设计器 ===")
    
    # 创建组件设计器
    designer = ReactComponentDesigner()
    
    # 定义组件规格
    component_spec = ComponentSpec(
        name="UserProfile",
        type=ComponentType.FUNCTIONAL,
        props=[
            {'name': 'userId', 'type': 'string', 'optional': False},
            {'name': 'onUpdate', 'type': '() => void', 'optional': True},
            {'name': 'theme', 'type': "'light' | 'dark'", 'optional': True, 'default': "'light'"}
        ],
        state=[
            {'name': 'user', 'type': 'User | null', 'initial': 'null'},
            {'name': 'loading', 'type': 'boolean', 'initial': 'true'},
            {'name': 'error', 'type': 'string | null', 'initial': 'null'}
        ],
        methods=[
            {'name': 'fetchUser', 'params': ['id: string'], 'body': 'console.log("获取用户数据");'},
            {'name': 'handleUpdate', 'params': [], 'body': 'console.log("处理更新");'}
        ],
        lifecycle=['useEffect', 'componentDidMount'],
        dependencies=['axios', 'react-query']
    )
    
    # 性能优化配置
    performance_config = PerformanceOptimization(
        use_memo=['user'],
        use_callback=['handleUpdate'],
        memo_wrap=True,
        lazy_load=False,
        virtualize=False
    )
    
    # 生成组件代码
    component_code = designer.design_component(
        component_spec, 
        StateManagementType.LOCAL_STATE, 
        performance_config
    )
    
    print("生成的React组件代码:")
    print(component_code)
    
    print("\n=== 组件分析 ===")
    
    # 分析组件
    analyzer = ReactComponentAnalyzer()
    analysis = analyzer.analyze_component(component_code)
    
    print("组件分析结果:")
    print(f"组件类型: {analysis['component_type']}")
    print(f"复杂度评分: {analysis['complexity_score']}")
    
    if analysis['issues']:
        print("\n发现的问题:")
        for issue in analysis['issues']:
            print(f"- {issue}")
    
    if analysis['recommendations']:
        print("\n优化建议:")
        for rec in analysis['recommendations']:
            print(f"- {rec}")
    
    print("\n代码指标:")
    for metric, value in analysis['metrics'].items():
        if isinstance(value, dict):
            print(f"- {metric}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"- {metric}: {value}")

if __name__ == '__main__':
    main()
```

### React组件优化器
```python
from typing import Dict, Any, List, Optional
import re

class ReactComponentOptimizer:
    def __init__(self):
        self.optimization_rules = {}
    
    def optimize_component(self, component_code: str) -> Dict[str, Any]:
        """优化React组件"""
        optimization_result = {
            'original_code': component_code,
            'optimized_code': component_code,
            'optimizations_applied': [],
            'performance_improvements': []
        }
        
        optimized_code = component_code
        
        # 应用各种优化
        optimized_code, optimizations = self._apply_performance_optimizations(optimized_code)
        optimization_result['optimizations_applied'].extend(optimizations)
        
        optimized_code, state_optimizations = self._optimize_state_management(optimized_code)
        optimization_result['optimizations_applied'].extend(state_optimizations)
        
        optimized_code, render_optimizations = self._optimize_rendering(optimized_code)
        optimization_result['optimizations_applied'].extend(render_optimizations)
        
        optimized_code, code_optimizations = self._optimize_code_structure(optimized_code)
        optimization_result['optimizations_applied'].extend(code_optimizations)
        
        optimization_result['optimized_code'] = optimized_code
        
        return optimization_result
    
    def _apply_performance_optimizations(self, code: str) -> tuple:
        """应用性能优化"""
        optimizations = []
        optimized_code = code
        
        # 添加React.memo包装
        if 'export default' in code and 'React.memo' not in code:
            # 提取组件名
            component_match = re.search(r'function (\w+)|const (\w+)', code)
            if component_match:
                component_name = component_match.group(1) or component_match.group(2)
                optimized_code = optimized_code.replace(
                    f'export default {component_name};',
                    f'export default React.memo({component_name});'
                )
                optimizations.append("添加React.memo优化")
        
        # 优化内联函数
        inline_functions = re.findall(r'onClick=\{(\(\) => [^}]+)\}', code)
        for func in inline_functions:
            optimizations.append("提取内联函数为useCallback")
        
        # 添加useMemo优化
        if 'useState' in code and 'useMemo' not in code:
            # 简化实现：在组件开头添加useMemo示例
            useMemo_code = """
  // 优化计算密集型操作
  const expensiveValue = useMemo(() => {
    return computeExpensiveValue(data);
  }, [data]);
"""
            
            # 在第一个useState后插入
            useState_pos = optimized_code.find('useState(')
            if useState_pos != -1:
                insert_pos = optimized_code.find('\n', useState_pos)
                optimized_code = optimized_code[:insert_pos] + useMemo_code + optimized_code[insert_pos:]
                optimizations.append("添加useMemo优化")
        
        return optimized_code, optimizations
    
    def _optimize_state_management(self, code: str) -> tuple:
        """优化状态管理"""
        optimizations = []
        optimized_code = code
        
        # 检查状态数量，建议使用useReducer
        useState_count = code.count('useState')
        if useState_count > 3 and 'useReducer' not in code:
            optimizations.append("建议使用useReducer替代多个useState")
        
        # 合并相关状态
        if useState_count > 2:
            optimizations.append("考虑合并相关状态为对象")
        
        # 检查状态更新模式
        if 'set' in code and 'prev' not in code:
            optimizations.append("建议使用函数式状态更新")
        
        return optimized_code, optimizations
    
    def _optimize_rendering(self, code: str) -> tuple:
        """优化渲染"""
        optimizations = []
        optimized_code = code
        
        # 检查条件渲染优化
        if '&&' in code and 'React.Fragment' not in code:
            optimizations.append("考虑使用React.Fragment优化条件渲染")
        
        # 检查列表渲染优化
        if '.map(' in code and 'key=' not in code:
            optimizations.append("列表渲染缺少key属性")
        
        # 检查样式优化
        if 'style={{' in code:
            optimizations.append("考虑使用CSS类替代内联样式")
        
        return optimized_code, optimizations
    
    def _optimize_code_structure(self, code: str) -> tuple:
        """优化代码结构"""
        optimizations = []
        optimized_code = code
        
        # 检查组件大小
        lines = code.split('\n')
        if len(lines) > 150:
            optimizations.append("组件过大，建议拆分")
        
        # 检查自定义Hook提取机会
        if 'useEffect' in code and 'useCustom' not in code:
            optimizations.append("考虑提取自定义Hook")
        
        # 检查类型定义
        if 'interface' not in code and 'type' not in code:
            optimizations.append("建议添加TypeScript类型定义")
        
        return optimized_code, optimizations

# React组件测试生成器
class ReactComponentTestGenerator:
    def __init__(self):
        self.test_templates = {}
    
    def generate_tests(self, component_code: str) -> str:
        """生成组件测试代码"""
        # 提取组件信息
        component_info = self._extract_component_info(component_code)
        
        # 生成测试代码
        test_code = self._generate_test_file(component_info)
        
        return test_code
    
    def _extract_component_info(self, code: str) -> Dict[str, Any]:
        """提取组件信息"""
        info = {
            'name': 'Component',
            'props': [],
            'methods': [],
            'state': []
        }
        
        # 提取组件名
        component_match = re.search(r'function (\w+)|const (\w+)|class (\w+)', code)
        if component_match:
            info['name'] = component_match.group(1) or component_match.group(2) or component_match.group(3)
        
        # 提取Props
        props_match = re.search(r'interface Props \{([^}]+)\}', code, re.DOTALL)
        if props_match:
            props_content = props_match.group(1)
            prop_lines = [line.strip() for line in props_content.split('\n') if line.strip()]
            info['props'] = [line.split(':')[0].replace('?', '').strip() for line in prop_lines]
        
        # 提取方法
        method_matches = re.findall(r'const (\w+) = \([^)]*\) =>', code)
        info['methods'] = method_matches
        
        # 提取状态
        state_matches = re.findall(r'const \[(\w+), set\w+\] = useState', code)
        info['state'] = state_matches
        
        return info
    
    def _generate_test_file(self, component_info: Dict[str, Any]) -> str:
        """生成测试文件"""
        component_name = component_info['name']
        
        test_lines = [
            "import React from 'react';",
            "import { render, screen, fireEvent, waitFor } from '@testing-library/react';",
            f"import {component_name} from './{component_name}';",
            "",
            f"describe('{component_name}', () => {{",
            "  it('应该正确渲染', () => {",
            f"    render(<{component_name} />);",
            f"    expect(screen.getByText('{component_name}组件')).toBeInTheDocument();",
            "  });",
            ""
        ]
        
        # Props测试
        if component_info['props']:
            test_lines.extend([
                f"  it('应该正确处理Props', () => {{",
                f"    const mockProps = {{"
            ])
            
            for prop in component_info['props'][:3]:  # 只测试前3个props
                test_lines.append(f"      {prop}: 'test-{prop}',")
            
            test_lines.extend([
                "    };",
                f"    render(<{component_name} {{...mockProps}} />);",
                "    // 添加Props相关的断言",
                "  });",
                ""
            ])
        
        # 事件测试
        if component_info['methods']:
            for method in component_info['methods'][:2]:  # 只测试前2个方法
                test_lines.extend([
                    f"  it('应该正确处理{method}事件', () => {{",
                    f"    render(<{component_name} />);",
                    f"    const button = screen.getByText('触发{method}');",
                    "    fireEvent.click(button);",
                    "    // 添加事件相关的断言",
                    "  });",
                    ""
                ])
        
        # 状态测试
        if component_info['state']:
            test_lines.extend([
                "  it('应该正确管理状态', async () => {",
                f"    render(<{component_name} />);",
                "    // 添加状态相关的测试",
                "    await waitFor(() => {",
                "      // 等待状态更新",
                "    });",
                "  });",
                ""
            ])
        
        test_lines.extend([
            "  it('应该处理错误情况', () => {",
            f"    render(<{component_name} />);",
            "    // 添加错误处理测试",
            "  });",
            "});"
        ])
        
        return '\n'.join(test_lines)

# 使用示例
def main():
    print("=== React组件优化器 ===")
    
    optimizer = ReactComponentOptimizer()
    
    # 示例组件代码
    sample_component = '''
import React from 'react';

function UserProfile({ userId, onUpdate }) {
  const [user, setUser] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  const fetchUser = (id) => {
    console.log("获取用户数据");
  };

  const handleUpdate = () => {
    console.log("处理更新");
  };

  React.useEffect(() => {
    fetchUser(userId);
  }, [userId]);

  return (
    <div>
      <h1>UserProfile组件</h1>
      <div>用户ID: {userId}</div>
      <div>状态: {loading ? '加载中...' : '已加载'}</div>
      <button onClick={() => handleUpdate()}>触发handleUpdate</button>
    </div>
  );
}

export default UserProfile;
'''
    
    # 优化组件
    optimization_result = optimizer.optimize_component(sample_component)
    
    print("优化结果:")
    print("应用的优化措施:")
    for opt in optimization_result['optimizations_applied']:
        print(f"- {opt}")
    
    print("\n优化后的代码:")
    print(optimization_result['optimized_code'])
    
    print("\n=== 测试代码生成 ===")
    
    test_generator = ReactComponentTestGenerator()
    test_code = test_generator.generate_tests(sample_component)
    
    print("生成的测试代码:")
    print(test_code)

if __name__ == '__main__':
    main()
```

## React组件最佳实践

### 组件设计原则
1. **单一职责**: 每个组件只负责一个功能
2. **可复用性**: 设计通用的组件接口
3. **可测试性**: 编写易于测试的组件
4. **性能优先**: 考虑渲染性能优化
5. **可维护性**: 保持代码清晰易懂

### 状态管理策略
1. **本地状态**: 使用useState管理组件内部状态
2. **复杂状态**: 使用useReducer管理复杂状态逻辑
3. **全局状态**: 使用Context或状态管理库
4. **服务器状态**: 使用React Query或SWR
5. **表单状态**: 使用专门的表单库

### 性能优化技巧
1. **React.memo**: 避免不必要的重新渲染
2. **useMemo**: 缓存计算结果
3. **useCallback**: 缓存函数引用
4. **代码分割**: 使用lazy和Suspense
5. **虚拟化**: 处理大量数据列表

### 组件通信模式
1. **Props传递**: 父子组件通信
2. **回调函数**: 子父组件通信
3. **Context API**: 跨层级组件通信
4. **状态管理**: 全局状态共享
5. **事件总线**: 兄弟组件通信

## 相关技能

- **component-analyzer** - 组件分析器
- **form-handling** - 表单处理与验证
- **performance-optimization** - 性能优化
- **css-validator** - CSS验证器
