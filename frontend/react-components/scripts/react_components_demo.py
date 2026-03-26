#!/usr/bin/env python3
"""
React组件开发演示 - 模拟React组件的生命周期和状态管理
"""

import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

class ComponentType(Enum):
    """组件类型"""
    FUNCTIONAL = "functional"
    CLASS = "class"
    HOOK = "hook"

class ComponentState(Enum):
    """组件状态"""
    MOUNTING = "mounting"
    MOUNTED = "mounted"
    UPDATING = "updating"
    UNMOUNTING = "unmounting"
    UNMOUNTED = "unmounted"

@dataclass
class Props:
    """组件属性"""
    children: List[Any] = None
    className: str = ""
    style: Dict[str, str] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.style is None:
            self.style = {}

@dataclass
class Component:
    """React组件"""
    name: str
    type: ComponentType
    state: Dict[str, Any]
    props: Props
    current_state: ComponentState = ComponentState.UNMOUNTED
    lifecycle_hooks: Dict[str, List[Callable]] = None
    
    def __post_init__(self):
        if self.lifecycle_hooks is None:
            self.lifecycle_hooks = {
                'componentDidMount': [],
                'componentDidUpdate': [],
                'componentWillUnmount': [],
                'shouldComponentUpdate': []
            }

class ReactRenderer:
    """React渲染器"""
    
    def __init__(self):
        self.components: Dict[str, Component] = []
        self.virtual_dom: List[Dict] = []
        self.render_count = 0
    
    def create_component(self, name: str, component_type: ComponentType, 
                       initial_state: Dict = None, props: Props = None) -> Component:
        """创建组件"""
        if initial_state is None:
            initial_state = {}
        if props is None:
            props = Props()
        
        component = Component(
            name=name,
            type=component_type,
            state=initial_state,
            props=props
        )
        
        self.components.append(component)
        return component
    
    def mount_component(self, component: Component):
        """挂载组件"""
        print(f"🔄 挂载组件: {component.name}")
        
        # 设置组件状态
        component.current_state = ComponentState.MOUNTING
        
        # 执行挂载前钩子
        self._execute_lifecycle_hook(component, 'componentWillMount')
        
        # 渲染组件
        rendered = self._render_component(component)
        self.virtual_dom.append(rendered)
        
        # 更新组件状态
        component.current_state = ComponentState.MOUNTED
        
        # 执行挂载后钩子
        self._execute_lifecycle_hook(component, 'componentDidMount')
        
        self.render_count += 1
        print(f"✅ 组件挂载完成: {component.name}")
        
        return rendered
    
    def update_component(self, component: Component, new_state: Dict = None, new_props: Props = None):
        """更新组件"""
        if component.current_state != ComponentState.MOUNTED:
            return
        
        print(f"🔄 更新组件: {component.name}")
        
        # 检查是否应该更新
        should_update = self._should_component_update(component, new_state, new_props)
        if not should_update:
            print(f"⏸️  组件跳过更新: {component.name}")
            return
        
        component.current_state = ComponentState.UPDATING
        
        # 更新状态和属性
        if new_state:
            old_state = component.state.copy()
            component.state.update(new_state)
            
            # 执行更新前钩子
            self._execute_lifecycle_hook_with_params(
                component, 'componentWillUpdate', old_state, new_state
            )
        
        if new_props:
            component.props = new_props
        
        # 重新渲染
        old_rendered = self._find_component_in_vdom(component)
        new_rendered = self._render_component(component)
        
        # 更新虚拟DOM
        if old_rendered:
            index = self.virtual_dom.index(old_rendered)
            self.virtual_dom[index] = new_rendered
        
        component.current_state = ComponentState.MOUNTED
        
        # 执行更新后钩子
        self._execute_lifecycle_hook(component, 'componentDidUpdate')
        
        print(f"✅ 组件更新完成: {component.name}")
    
    def unmount_component(self, component: Component):
        """卸载组件"""
        if component.current_state != ComponentState.MOUNTED:
            return
        
        print(f"🔄 卸载组件: {component.name}")
        
        component.current_state = ComponentState.UNMOUNTING
        
        # 执行卸载前钩子
        self._execute_lifecycle_hook(component, 'componentWillUnmount')
        
        # 从虚拟DOM中移除
        rendered = self._find_component_in_vdom(component)
        if rendered:
            self.virtual_dom.remove(rendered)
        
        component.current_state = ComponentState.UNMOUNTED
        
        print(f"✅ 组件卸载完成: {component.name}")
    
    def _render_component(self, component: Component) -> Dict:
        """渲染组件"""
        return {
            'type': component.type.value,
            'name': component.name,
            'props': asdict(component.props),
            'state': component.state,
            'render_time': time.time()
        }
    
    def _find_component_in_vdom(self, component: Component) -> Optional[Dict]:
        """在虚拟DOM中查找组件"""
        for rendered in self.virtual_dom:
            if rendered['name'] == component.name:
                return rendered
        return None
    
    def _should_component_update(self, component: Component, new_state: Dict, new_props: Props) -> bool:
        """判断是否应该更新组件"""
        # 执行shouldComponentUpdate钩子
        hooks = component.lifecycle_hooks.get('shouldComponentUpdate', [])
        for hook in hooks:
            result = hook(component.state, new_state, component.props, new_props)
            if result is False:
                return False
        
        # 默认行为：状态或属性发生变化时更新
        if new_state and new_state != component.state:
            return True
        
        if new_props and asdict(new_props) != asdict(component.props):
            return True
        
        return False
    
    def _execute_lifecycle_hook(self, component: Component, hook_name: str):
        """执行生命周期钩子"""
        hooks = component.lifecycle_hooks.get(hook_name, [])
        for hook in hooks:
            try:
                hook(component)
            except Exception as e:
                print(f"❌ 生命周期钩子执行失败: {hook_name} - {e}")
    
    def _execute_lifecycle_hook_with_params(self, component: Component, hook_name: str, *args):
        """执行带参数的生命周期钩子"""
        hooks = component.lifecycle_hooks.get(hook_name, [])
        for hook in hooks:
            try:
                hook(component, *args)
            except Exception as e:
                print(f"❌ 生命周期钩子执行失败: {hook_name} - {e}")
    
    def add_lifecycle_hook(self, component: Component, hook_name: str, hook_func: Callable):
        """添加生命周期钩子"""
        if hook_name in component.lifecycle_hooks:
            component.lifecycle_hooks[hook_name].append(hook_func)
    
    def get_virtual_dom(self) -> List[Dict]:
        """获取虚拟DOM"""
        return self.virtual_dom.copy()
    
    def print_virtual_dom(self):
        """打印虚拟DOM"""
        print("\n🌲 虚拟DOM:")
        for i, node in enumerate(self.virtual_dom, 1):
            print(f"  {i}. {node['name']} ({node['type']})")
            print(f"     State: {json.dumps(node['state'], indent=6)}")
            print(f"     Props: {json.dumps(node['props'], indent=6)}")

class HookManager:
    """Hook管理器"""
    
    def __init__(self):
        self.hooks: Dict[str, List] = {}
        self.current_component: Optional[Component] = None
    
    def use_state(self, component: Component, initial_value: Any) -> tuple:
        """useState Hook"""
        state_key = f"{component.name}_state"
        
        if state_key not in self.hooks:
            self.hooks[state_key] = [initial_value]
        
        current_value = self.hooks[state_key][0]
        
        def set_value(new_value):
            self.hooks[state_key][0] = new_value
            # 触发重新渲染
            if hasattr(component, 'renderer'):
                component.renderer.update_component(component, {state_key: new_value})
        
        return current_value, set_value
    
    def use_effect(self, component: Component, effect_func: Callable, deps: List = None):
        """useEffect Hook"""
        effect_key = f"{component.name}_effect"
        
        if effect_key not in self.hooks:
            self.hooks[effect_key] = []
        
        # 检查依赖是否变化
        old_deps = self.hooks[effect_key][-1] if self.hooks[effect_key] else None
        
        if old_deps != deps:
            # 执行清理函数
            if len(self.hooks[effect_key]) > 1:
                cleanup = self.hooks[effect_key][-2]
                if callable(cleanup):
                    cleanup()
            
            # 执行effect
            cleanup = effect_func()
            self.hooks[effect_key].append(deps)
            
            # 保存清理函数
            if callable(cleanup):
                self.hooks[effect_key].append(cleanup)
    
    def use_context(self, component: Component, context: Dict) -> Any:
        """useContext Hook"""
        return context.get('value', None)

class ComponentLibrary:
    """组件库"""
    
    def __init__(self):
        self.components: Dict[str, Callable] = {}
    
    def register_component(self, name: str, component_func: Callable):
        """注册组件"""
        self.components[name] = component_func
        print(f"📦 注册组件: {name}")
    
    def create_button(self, text: str, onClick: Callable = None, style: Dict = None) -> Dict:
        """创建按钮组件"""
        return {
            'type': 'button',
            'props': {
                'text': text,
                'onClick': onClick,
                'style': style or {}
            }
        }
    
    def create_input(self, placeholder: str, value: str = None, onChange: Callable = None) -> Dict:
        """创建输入框组件"""
        return {
            'type': 'input',
            'props': {
                'placeholder': placeholder,
                'value': value,
                'onChange': onChange
            }
        }
    
    def create_list(self, items: List[Any], renderItem: Callable) -> Dict:
        """创建列表组件"""
        return {
            'type': 'list',
            'props': {
                'items': items,
                'renderItem': renderItem
            }
        }

def demonstrate_basic_components():
    """演示基础组件"""
    print("\n🧩 基础组件演示")
    print("=" * 50)
    
    # 创建渲染器
    renderer = ReactRenderer()
    
    # 创建函数组件
    button_component = renderer.create_component(
        "Button", 
        ComponentType.FUNCTIONAL,
        {"text": "Click me", "count": 0},
        Props(className="btn-primary")
    )
    
    # 添加生命周期钩子
    def on_mount(component):
        print(f"🎯 组件挂载: {component.name}")
    
    def on_update(component):
        print(f"🔄 组件更新: {component.name}")
    
    renderer.add_lifecycle_hook(button_component, 'componentDidMount', on_mount)
    renderer.add_lifecycle_hook(button_component, 'componentDidUpdate', on_update)
    
    # 挂载组件
    renderer.mount_component(button_component)
    
    # 更新组件
    renderer.update_component(button_component, {"count": 1})
    renderer.update_component(button_component, {"text": "Clicked!"})
    
    # 显示虚拟DOM
    renderer.print_virtual_dom()
    
    # 卸载组件
    renderer.unmount_component(button_component)

def demonstrate_class_components():
    """演示类组件"""
    print("\n🏗️  类组件演示")
    print("=" * 50)
    
    renderer = ReactRenderer()
    
    # 创建类组件
    class_component = renderer.create_component(
        "Counter",
        ComponentType.CLASS,
        {"count": 0, "step": 1},
        Props(className="counter")
    )
    
    # 添加生命周期钩子
    def will_mount(component):
        print(f"🎯 {component.name} 将要挂载")
    
    def did_mount(component):
        print(f"✅ {component.name} 挂载完成，初始计数: {component.state['count']}")
    
    def should_update(component, new_state, old_props, new_props):
        print(f"🤔 {component.name} 考虑更新: {new_state}")
        return True
    
    def did_update(component):
        print(f"🔄 {component.name} 更新完成，当前计数: {component.state['count']}")
    
    def will_unmount(component):
        print(f"👋 {component.name} 将要卸载")
    
    renderer.add_lifecycle_hook(class_component, 'componentWillMount', will_mount)
    renderer.add_lifecycle_hook(class_component, 'componentDidMount', did_mount)
    renderer.add_lifecycle_hook(class_component, 'shouldComponentUpdate', should_update)
    renderer.add_lifecycle_hook(class_component, 'componentDidUpdate', did_update)
    renderer.add_lifecycle_hook(class_component, 'componentWillUnmount', will_unmount)
    
    # 挂载组件
    renderer.mount_component(class_component)
    
    # 模拟计数器操作
    for i in range(1, 4):
        renderer.update_component(class_component, {"count": i})
        time.sleep(0.1)
    
    # 卸载组件
    renderer.unmount_component(class_component)

def demonstrate_hooks():
    """演示Hooks"""
    print("\n🪝 Hooks演示")
    print("=" * 50)
    
    renderer = ReactRenderer()
    hook_manager = HookManager()
    
    # 创建使用Hooks的组件
    hooks_component = renderer.create_component(
        "HookComponent",
        ComponentType.HOOK,
        {},
        Props(className="hooks-demo")
    )
    
    # 设置当前组件
    hook_manager.current_component = hooks_component
    hooks_component.renderer = renderer
    
    # 使用useState
    count, set_count = hook_manager.use_state(hooks_component, 0)
    text, set_text = hook_manager.use_state(hooks_component, "Hello")
    
    print(f"📊 初始状态: count={count}, text='{text}'")
    
    # 使用useEffect
    def effect_func():
        print("🎯 Effect执行: 组件挂载或更新")
        def cleanup():
            print("🧹 Effect清理: 组件卸载前")
        return cleanup
    
    hook_manager.use_effect(hooks_component, effect_func, [count])
    
    # 挂载组件
    renderer.mount_component(hooks_component)
    
    # 更新状态
    print("\n🔄 更新状态...")
    set_count(1)
    renderer.update_component(hooks_component, {"count": 1})
    
    set_text("Hello React!")
    renderer.update_component(hooks_component, {"text": "Hello React!"})
    
    # 卸载组件
    renderer.unmount_component(hooks_component)

def demonstrate_component_library():
    """演示组件库"""
    print("\n📚 组件库演示")
    print("=" * 50)
    
    # 创建组件库
    library = ComponentLibrary()
    
    # 创建各种组件
    button = library.create_button(
        "Submit", 
        onClick=lambda: print("按钮被点击!"),
        style={"backgroundColor": "blue", "color": "white"}
    )
    
    input_field = library.create_input(
        "请输入用户名...",
        value="",
        onChange=lambda value: print(f"输入变化: {value}")
    )
    
    list_items = ["项目1", "项目2", "项目3"]
    list_component = library.create_list(
        list_items,
        lambda item: {"type": "li", "content": item}
    )
    
    print("🧩 创建的组件:")
    print(f"  按钮: {json.dumps(button, indent=2, ensure_ascii=False)}")
    print(f"  输入框: {json.dumps(input_field, indent=2, ensure_ascii=False)}")
    print(f"  列表: {json.dumps(list_component, indent=2, ensure_ascii=False)}")

def demonstrate_state_management():
    """演示状态管理"""
    print("\n🗂️  状态管理演示")
    print("=" * 50)
    
    renderer = ReactRenderer()
    
    # 创建父组件
    parent_component = renderer.create_component(
        "Parent",
        ComponentType.CLASS,
        {"message": "来自父组件的消息", "childCount": 0},
        Props(className="parent")
    )
    
    # 创建子组件
    child_component = renderer.create_component(
        "Child",
        ComponentType.FUNCTIONAL,
        {"receivedMessage": ""},
        Props(className="child")
    )
    
    # 挂载组件
    renderer.mount_component(parent_component)
    renderer.mount_component(child_component)
    
    # 模拟父子通信
    print("\n📨 父子组件通信:")
    
    # 父组件向子组件传递消息
    message = "Hello from Parent!"
    renderer.update_component(child_component, {"receivedMessage": message})
    
    # 子组件向父组件报告
    renderer.update_component(parent_component, {"childCount": 1})
    
    # 显示最终状态
    print("\n📊 最终状态:")
    print(f"  父组件: {parent_component.state}")
    print(f"  子组件: {child_component.state}")
    
    renderer.print_virtual_dom()

def main():
    """主函数"""
    print("⚛️  React组件开发演示")
    print("=" * 60)
    
    try:
        demonstrate_basic_components()
        demonstrate_class_components()
        demonstrate_hooks()
        demonstrate_component_library()
        demonstrate_state_management()
        
        print("\n✅ React组件演示完成!")
        print("\n📚 关键概念:")
        print("  - 组件: React的基本构建块")
        print("  - 生命周期: 组件的挂载、更新、卸载过程")
        print("  - 状态: 组件内部的数据管理")
        print("  - 属性: 父组件向子组件传递数据")
        print("  - Hooks: 函数组件的状态和副作用管理")
        print("  - 虚拟DOM: React的高效DOM更新机制")
        print("  - 组件通信: 组件间的数据传递")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")

if __name__ == '__main__':
    main()
