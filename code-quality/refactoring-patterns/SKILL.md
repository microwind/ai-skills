---
name: 重构模式
description: "当重构代码时，分析代码结构，识别重构机会，应用重构模式。验证重构效果，设计重构策略，和最佳实践。"
license: MIT
---

# 重构模式技能

## 概述
重构是改善代码设计而不改变其外部行为的过程。不当的重构会引入新的bug，增加复杂性，甚至降低代码质量。需要系统性的重构方法和模式。

**核心原则**: 好的重构应该提升代码可读性、可维护性和扩展性。坏的重构会增加不必要的复杂性，破坏现有功能。

## 何时使用

**始终:**
- 代码出现坏味道时
- 添加新功能困难时
- 修复bug需要理解复杂逻辑时
- 代码审查发现设计问题时
- 性能优化需要结构调整时
- 技术债务积累过多时

**触发短语:**
- "重构模式"
- "代码重构技巧"
- "设计模式应用"
- "代码结构优化"
- "技术债务清理"
- "代码质量提升"

## 重构模式功能

### 结构重构
- 提取方法/类/接口
- 内联方法/类
- 移动方法/字段
- 重命名元素
- 引入参数对象

### 设计模式应用
- 策略模式重构
- 工厂模式重构
- 观察者模式重构
- 装饰器模式重构
- 模板方法模式重构

### 简化重构
- 消除重复代码
- 简化条件表达式
- 简化方法调用
- 分解复杂表达式
- 统一接口设计

### 数据重构
- 封装字段
- 提取类
- 引入值对象
- 合并类
- 分解数据结构

## 常见重构问题

### 重构过度问题
```
问题:
过度重构导致代码复杂化

错误示例:
- 过早抽象
- 过度设计
- 不必要的接口
- 过度分解

解决方案:
1. 按需重构
2. 保持简单
3. 避免过度抽象
4. 评估重构价值
```

### 重构风险问题
```
问题:
重构引入新的bug和风险

错误示例:
- 缺少测试保护
- 大规模重构
- 缺少回滚计划
- 忽视依赖关系

解决方案:
1. 建立测试覆盖
2. 小步重构
3. 制定回滚策略
4. 分析影响范围
```

### 重构时机问题
```
问题:
选择不合适的重构时机

错误示例:
- 紧急修复时重构
- 发布前重构
- 缺少时间时重构
- 团队不同意时重构

解决方案:
1. 选择合适时机
2. 获得团队支持
3. 规划重构时间
4. 分阶段实施
```

### 重构效果问题
```
问题:
重构后效果不明显

错误示例:
- 重构目标不明确
- 重构范围过大
- 重构方法不当
- 缺少效果评估

解决方案:
1. 明确重构目标
2. 限制重构范围
3. 选择合适方法
4. 评估重构效果
```

## 代码实现示例

### 重构工具集
```python
import ast
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class RefactoringType(Enum):
    """重构类型"""
    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    INLINE_METHOD = "inline_method"
    MOVE_METHOD = "move_method"
    RENAME = "rename"
    INTRODUCE_PARAMETER = "introduce_parameter"
    REMOVE_PARAMETER = "remove_parameter"

@dataclass
class RefactoringSuggestion:
    """重构建议"""
    type: RefactoringType
    file_path: str
    line_number: int
    description: str
    reason: str
    confidence: float
    effort: str  # low, medium, high

@dataclass
class CodeSmell:
    """代码坏味道"""
    type: str
    file_path: str
    line_number: int
    description: str
    severity: str
    suggested_refactoring: RefactoringType

class CodeAnalyzer:
    def __init__(self):
        self.code_smells = []
        self.suggestions = []
        
    def analyze_file(self, file_path: str, code: str) -> List[RefactoringSuggestion]:
        """分析文件并提供重构建议"""
        self.code_smells = []
        self.suggestions = []
        
        try:
            tree = ast.parse(code)
            
            # 检测各种代码坏味道
            self._detect_long_methods(tree, file_path, code)
            self._detect_large_classes(tree, file_path, code)
            self._detect_duplicate_code(tree, file_path, code)
            self._detect_long_parameter_lists(tree, file_path, code)
            self._detect_complex_conditions(tree, file_path, code)
            self._detect_feature_envy(tree, file_path, code)
            self._detect_data_clumps(tree, file_path, code)
            
            # 生成重构建议
            self._generate_refactoring_suggestions()
            
        except SyntaxError as e:
            print(f"语法错误: {e}")
        
        return self.suggestions
    
    def _detect_long_methods(self, tree: ast.AST, file_path: str, code: str) -> None:
        """检测过长方法"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算方法长度
                method_lines = self._count_method_lines(node, code)
                
                if method_lines > 20:
                    self.code_smells.append(CodeSmell(
                        type="long_method",
                        file_path=file_path,
                        line_number=node.lineno,
                        description=f"方法过长 ({method_lines} 行)",
                        severity="high",
                        suggested_refactoring=RefactoringType.EXTRACT_METHOD
                    ))
    
    def _detect_large_classes(self, tree: ast.AST, file_path: str, code: str) -> None:
        """检测过大类"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 计算类的方法数量
                method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                
                if method_count > 15:
                    self.code_smells.append(CodeSmell(
                        type="large_class",
                        file_path=file_path,
                        line_number=node.lineno,
                        description=f"类过大 ({method_count} 个方法)",
                        severity="high",
                        suggested_refactoring=RefactoringType.EXTRACT_CLASS
                    ))
    
    def _detect_duplicate_code(self, tree: ast.AST, file_path: str, code: str) -> None:
        """检测重复代码"""
        lines = code.split('\n')
        
        # 简化的重复代码检测
        for i, line1 in enumerate(lines):
            if len(line1.strip()) < 10:  # 跳过短行
                continue
                
            for j, line2 in enumerate(lines[i+1:], i+1):
                if line1.strip() == line2.strip():
                    self.code_smells.append(CodeSmell(
                        type="duplicate_code",
                        file_path=file_path,
                        line_number=i+1,
                        description=f"重复代码 (第{i+1}行和第{j+1}行)",
                        severity="medium",
                        suggested_refactoring=RefactoringType.EXTRACT_METHOD
                    ))
                    break
    
    def _detect_long_parameter_lists(self, tree: ast.AST, file_path: str, code: str) -> None:
        """检测过长参数列表"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                
                if param_count > 5:
                    self.code_smells.append(CodeSmell(
                        type="long_parameter_list",
                        file_path=file_path,
                        line_number=node.lineno,
                        description=f"参数列表过长 ({param_count} 个参数)",
                        severity="medium",
                        suggested_refactoring=RefactoringType.INTRODUCE_PARAMETER
                    ))
    
    def _detect_complex_conditions(self, tree: ast.AST, file_path: str, code: str) -> None:
        """检测复杂条件表达式"""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # 简化的复杂条件检测
                condition_complexity = self._calculate_condition_complexity(node.test)
                
                if condition_complexity > 3:
                    self.code_smells.append(CodeSmell(
                        type="complex_condition",
                        file_path=file_path,
                        line_number=node.lineno,
                        description=f"条件表达式过于复杂 (复杂度: {condition_complexity})",
                        severity="medium",
                        suggested_refactoring=RefactoringType.EXTRACT_METHOD
                    ))
    
    def _detect_feature_envy(self, tree: ast.AST, file_path: str, code: str) -> None:
        """检测特性嫉妒"""
        # 简化实现：检测方法中使用其他类的方法频率
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                external_calls = self._count_external_calls(node, tree)
                
                if external_calls > 5:
                    self.code_smells.append(CodeSmell(
                        type="feature_envy",
                        file_path=file_path,
                        line_number=node.lineno,
                        description=f"方法可能存在特性嫉妒 (外部调用: {external_calls})",
                        severity="medium",
                        suggested_refactoring=RefactoringType.MOVE_METHOD
                    ))
    
    def _detect_data_clumps(self, tree: ast.AST, file_path: str, code: str) -> None:
        """检测数据泥团"""
        # 简化实现：检测经常一起出现的参数
        parameter_groups = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_names = [arg.arg for arg in node.args.args]
                
                if len(param_names) >= 2:
                    for i in range(len(param_names)-1):
                        group = tuple(param_names[i:i+2])
                        parameter_groups[group] = parameter_groups.get(group, 0) + 1
        
        # 找出经常一起出现的参数组合
        for group, count in parameter_groups.items():
            if count >= 3:
                self.code_smells.append(CodeSmell(
                    type="data_clumps",
                    file_path=file_path,
                    line_number=1,
                    description=f"数据泥团: 参数组合 {group} 出现 {count} 次",
                    severity="low",
                    suggested_refactoring=RefactoringType.INTRODUCE_PARAMETER
                ))
    
    def _count_method_lines(self, node: ast.FunctionDef, code: str) -> int:
        """计算方法行数"""
        lines = code.split('\n')
        start_line = node.lineno - 1
        end_line = node.end_lineno - 1 if hasattr(node, 'end_lineno') else start_line
        
        return end_line - start_line + 1
    
    def _calculate_condition_complexity(self, node: ast.AST) -> int:
        """计算条件复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.Compare):
                complexity += len(child.ops) - 1
        
        return complexity
    
    def _count_external_calls(self, node: ast.FunctionDef, tree: ast.AST) -> int:
        """计算外部方法调用次数"""
        external_calls = 0
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    external_calls += 1
        
        return external_calls
    
    def _generate_refactoring_suggestions(self) -> None:
        """生成重构建议"""
        for smell in self.code_smells:
            suggestion = self._create_suggestion(smell)
            if suggestion:
                self.suggestions.append(suggestion)
    
    def _create_suggestion(self, smell: CodeSmell) -> Optional[RefactoringSuggestion]:
        """创建重构建议"""
        confidence = self._calculate_confidence(smell)
        effort = self._estimate_effort(smell)
        
        return RefactoringSuggestion(
            type=smell.suggested_refactoring,
            file_path=smell.file_path,
            line_number=smell.line_number,
            description=smell.description,
            reason=self._get_refactoring_reason(smell),
            confidence=confidence,
            effort=effort
        )
    
    def _calculate_confidence(self, smell: CodeSmell) -> float:
        """计算建议置信度"""
        base_confidence = 0.8
        
        if smell.severity == "high":
            base_confidence += 0.1
        elif smell.severity == "low":
            base_confidence -= 0.2
        
        return min(1.0, max(0.0, base_confidence))
    
    def _estimate_effort(self, smell: CodeSmell) -> str:
        """估算重构工作量"""
        if smell.type in ["long_method", "duplicate_code"]:
            return "medium"
        elif smell.type in ["large_class", "feature_envy"]:
            return "high"
        else:
            return "low"
    
    def _get_refactoring_reason(self, smell: CodeSmell) -> str:
        """获取重构原因"""
        reasons = {
            "long_method": "提高代码可读性和可维护性",
            "large_class": "遵循单一职责原则，降低类复杂度",
            "duplicate_code": "消除重复，遵循DRY原则",
            "long_parameter_list": "简化方法签名，提高可读性",
            "complex_condition": "提高条件逻辑的可读性",
            "feature_envy": "改善类之间的职责分配",
            "data_clumps": "创建值对象，提高数据内聚性"
        }
        
        return reasons.get(smell.type, "改善代码设计")

# 重构执行器
class RefactoringExecutor:
    def __init__(self):
        self.refactoring_history = []
        
    def apply_refactoring(self, file_path: str, code: str, suggestion: RefactoringSuggestion) -> str:
        """应用重构建议"""
        try:
            if suggestion.type == RefactoringType.EXTRACT_METHOD:
                return self._extract_method(code, suggestion)
            elif suggestion.type == RefactoringType.EXTRACT_CLASS:
                return self._extract_class(code, suggestion)
            elif suggestion.type == RefactoringType.INLINE_METHOD:
                return self._inline_method(code, suggestion)
            elif suggestion.type == RefactoringType.MOVE_METHOD:
                return self._move_method(code, suggestion)
            elif suggestion.type == RefactoringType.RENAME:
                return self._rename_element(code, suggestion)
            else:
                return code
                
        except Exception as e:
            print(f"重构失败: {e}")
            return code
    
    def _extract_method(self, code: str, suggestion: RefactoringSuggestion) -> str:
        """提取方法"""
        lines = code.split('\n')
        
        # 简化实现：在指定行附近提取代码块
        start_line = suggestion.line_number - 1
        end_line = min(start_line + 10, len(lines))
        
        # 提取的代码块
        extracted_code = lines[start_line:end_line]
        
        # 生成新方法名
        method_name = f"extracted_method_{suggestion.line_number}"
        
        # 创建新方法
        new_method = f"    def {method_name}(self):\n"
        for line in extracted_code:
            new_method += f"        {line}\n"
        
        # 在原位置添加方法调用
        method_call = f"        self.{method_name}()  # 重构: 提取方法"
        
        # 重构代码
        new_lines = lines[:start_line] + [method_call] + lines[end_line:]
        
        # 在类末尾添加新方法
        class_end = len(new_lines)
        new_lines.insert(class_end, "")
        new_lines.insert(class_end + 1, new_method)
        
        refactored_code = '\n'.join(new_lines)
        
        # 记录重构历史
        self.refactoring_history.append({
            'type': 'extract_method',
            'file_path': suggestion.file_path,
            'line_number': suggestion.line_number,
            'method_name': method_name
        })
        
        return refactored_code
    
    def _extract_class(self, code: str, suggestion: RefactoringSuggestion) -> str:
        """提取类"""
        # 简化实现
        lines = code.split('\n')
        
        new_class = f"class ExtractedClass{suggestion.line_number}:\n"
        new_class += "    def __init__(self):\n"
        new_class += "        pass\n"
        
        refactored_code = code + f"\n\n# 重构: 提取类\n{new_class}"
        
        self.refactoring_history.append({
            'type': 'extract_class',
            'file_path': suggestion.file_path,
            'line_number': suggestion.line_number
        })
        
        return refactored_code
    
    def _inline_method(self, code: str, suggestion: RefactoringSuggestion) -> str:
        """内联方法"""
        # 简化实现
        return code + f"\n# 重构: 内联方法 (第{suggestion.line_number}行)"
    
    def _move_method(self, code: str, suggestion: RefactoringSuggestion) -> str:
        """移动方法"""
        # 简化实现
        return code + f"\n# 重构: 移动方法 (第{suggestion.line_number}行)"
    
    def _rename_element(self, code: str, suggestion: RefactoringSuggestion) -> str:
        """重命名元素"""
        # 简化实现
        return code + f"\n# 重构: 重命名元素 (第{suggestion.line_number}行)"

# 使用示例
def main():
    # 示例代码
    sample_code = '''
class OrderProcessor:
    def process_order(self, customer_id, product_id, quantity, price, discount, shipping_address, billing_address, payment_method):
        # 验证客户
        if customer_id <= 0:
            raise ValueError("无效的客户ID")
        
        # 验证产品
        if product_id <= 0:
            raise ValueError("无效的产品ID")
        
        # 计算总价
        total_price = quantity * price
        if discount > 0:
            total_price = total_price * (1 - discount / 100)
        
        # 处理支付
        if payment_method == "credit_card":
            # 处理信用卡支付
            pass
        elif payment_method == "paypal":
            # 处理PayPal支付
            pass
        
        # 发送确认邮件
        # 发送邮件逻辑
        
        return total_price
    
    def validate_customer(self, customer_id):
        return customer_id > 0
    
    def validate_product(self, product_id):
        return product_id > 0
'''
    
    # 创建分析器
    analyzer = CodeAnalyzer()
    
    # 分析代码
    suggestions = analyzer.analyze_file("order_processor.py", sample_code)
    
    print("重构建议:")
    for suggestion in suggestions:
        print(f"- {suggestion.description}")
        print(f"  类型: {suggestion.type.value}")
        print(f"  位置: 第{suggestion.line_number}行")
        print(f"  原因: {suggestion.reason}")
        print(f"  置信度: {suggestion.confidence:.2f}")
        print(f"  工作量: {suggestion.effort}")
        print()
    
    # 应用重构
    if suggestions:
        executor = RefactoringExecutor()
        refactored_code = executor.apply_refactoring("order_processor.py", sample_code, suggestions[0])
        
        print("重构后的代码:")
        print(refactored_code)

if __name__ == '__main__':
    main()
```

### 重构模式应用
```python
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

# 策略模式重构示例
class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

class CreditCardPayment(PaymentStrategy):
    def process_payment(self, amount: float) -> bool:
        print(f"处理信用卡支付: ${amount}")
        return True

class PayPalPayment(PaymentStrategy):
    def process_payment(self, amount: float) -> bool:
        print(f"处理PayPal支付: ${amount}")
        return True

class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def process_payment(self, amount: float) -> bool:
        return self.strategy.process_payment(amount)

# 工厂模式重构示例
class PaymentFactory:
    @staticmethod
    def create_payment(method: str) -> PaymentStrategy:
        if method == "credit_card":
            return CreditCardPayment()
        elif method == "paypal":
            return PayPalPayment()
        else:
            raise ValueError(f"不支持的支付方式: {method}")

# 观察者模式重构示例
@dataclass
class Event:
    type: str
    data: Dict[str, Any]

class Observer(ABC):
    @abstractmethod
    def notify(self, event: Event) -> None:
        pass

class EmailNotifier(Observer):
    def notify(self, event: Event) -> None:
        print(f"发送邮件通知: {event.type} - {event.data}")

class SMSNotifier(Observer):
    def notify(self, event: Event) -> None:
        print(f"发送短信通知: {event.type} - {event.data}")

class EventPublisher:
    def __init__(self):
        self.observers: List[Observer] = []
    
    def subscribe(self, observer: Observer) -> None:
        self.observers.append(observer)
    
    def unsubscribe(self, observer: Observer) -> None:
        self.observers.remove(observer)
    
    def publish(self, event: Event) -> None:
        for observer in self.observers:
            observer.notify(event)

# 装饰器模式重构示例
class DataSource(ABC):
    @abstractmethod
    def write_data(self, data: str) -> None:
        pass
    
    @abstractmethod
    def read_data(self) -> str:
        pass

class FileDataSource(DataSource):
    def __init__(self, filename: str):
        self.filename = filename
    
    def write_data(self, data: str) -> None:
        with open(self.filename, 'w') as f:
            f.write(data)
    
    def read_data(self) -> str:
        with open(self.filename, 'r') as f:
            return f.read()

class DataSourceDecorator(DataSource):
    def __init__(self, wrappee: DataSource):
        self.wrappee = wrappee
    
    def write_data(self, data: str) -> None:
        self.wrappee.write_data(data)
    
    def read_data(self) -> str:
        return self.wrappee.read_data()

class EncryptionDecorator(DataSourceDecorator):
    def write_data(self, data: str) -> None:
        encrypted_data = self._encrypt(data)
        super().write_data(encrypted_data)
    
    def read_data(self) -> str:
        encrypted_data = super().read_data()
        return self._decrypt(encrypted_data)
    
    def _encrypt(self, data: str) -> str:
        return f"encrypted_{data}"
    
    def _decrypt(self, data: str) -> str:
        return data.replace("encrypted_", "")

class CompressionDecorator(DataSourceDecorator):
    def write_data(self, data: str) -> None:
        compressed_data = self._compress(data)
        super().write_data(compressed_data)
    
    def read_data(self) -> str:
        compressed_data = super().read_data()
        return self._decompress(compressed_data)
    
    def _compress(self, data: str) -> str:
        return f"compressed_{data}"
    
    def _decompress(self, data: str) -> str:
        return data.replace("compressed_", "")

# 使用示例
def main():
    print("=== 策略模式重构 ===")
    processor = PaymentProcessor(CreditCardPayment())
    processor.process_payment(100.0)
    
    processor.set_strategy(PayPalPayment())
    processor.process_payment(200.0)
    
    print("\n=== 工厂模式重构 ===")
    payment = PaymentFactory.create_payment("credit_card")
    payment.process_payment(150.0)
    
    print("\n=== 观察者模式重构 ===")
    publisher = EventPublisher()
    publisher.subscribe(EmailNotifier())
    publisher.subscribe(SMSNotifier())
    
    event = Event("order_created", {"order_id": 123, "amount": 100.0})
    publisher.publish(event)
    
    print("\n=== 装饰器模式重构 ===")
    source = FileDataSource("data.txt")
    
    # 添加加密功能
    encrypted_source = EncryptionDecorator(source)
    encrypted_source.write_data("敏感数据")
    
    # 添加压缩功能
    compressed_source = CompressionDecorator(encrypted_source)
    compressed_source.write_data("压缩数据")

if __name__ == '__main__':
    main()
```

## 重构模式最佳实践

### 重构准备
1. **测试保护**: 确保有足够的测试覆盖
2. **版本控制**: 建立安全的版本控制
3. **备份策略**: 准备代码备份
4. **团队沟通**: 与团队沟通重构计划
5. **时间规划**: 合理规划重构时间

### 重构执行
1. **小步重构**: 每次只做一个小改动
2. **频繁测试**: 每次重构后运行测试
3. **验证功能**: 确保功能不受影响
4. **记录变更**: 记录重构变更
5. **代码审查**: 重构后进行代码审查

### 重构验证
1. **功能测试**: 验证功能正确性
2. **性能测试**: 检查性能影响
3. **代码质量**: 评估代码质量改善
4. **团队反馈**: 收集团队反馈
5. **文档更新**: 更新相关文档

### 重构策略
1. **优先级排序**: 按影响程度排序
2. **分阶段实施**: 分阶段进行重构
3. **持续改进**: 持续进行小重构
4. **技术债务**: 管理技术债务
5. **度量指标**: 建立重构度量指标

## 相关技能

- **code-optimization** - 代码优化技巧
- **code-review** - 代码审查与标准
- **design-patterns** - 设计模式
- **test-generation** - 测试生成
