---
name: 堆栈跟踪分析器
description: "当用户遇到堆栈跟踪、错误日志、崩溃报告或异常消息时，分析堆栈跟踪并提供调试指导。"
license: MIT
---

# 堆栈跟踪分析器技能

## 概述
分析堆栈跟踪并提供调试指导。需要建立完善的错误分析和调试机制。

**核心原则**: 理解错误根本原因，快速定位问题，提供有效解决方案。

## 何时使用

**触发短语:**
- "这个错误是什么意思？"
- "调试这个崩溃"
- "帮助处理这个异常"
- "分析这个堆栈跟踪"
- "修复这个错误"
- "程序崩溃了"
- "空指针异常"
- "内存泄漏"

## 堆栈跟踪分析功能

### 错误分类
- 运行时异常
- 编译时错误
- 逻辑错误
- 内存错误
- 并发问题
- 网络错误

### 调试策略
- 自顶向下分析
- 自底向上追踪
- 症状到原因
- 数据流分析
- 控制流分析

## 常见错误模式

### 空指针异常
```
问题:
NullPointerException / AttributeError

特征:
- 访问null对象的属性或方法
- 未初始化的变量
- 方法返回null值

解决方案:
- 添加空值检查
- 使用Optional/Nullable类型
- 初始化变量
- 验证输入参数
```

### 数组越界
```
问题:
ArrayIndexOutOfBoundsException / IndexError

特征:
- 访问超出数组范围的索引
- 负数索引
- 循环边界错误

解决方案:
- 检查数组长度
- 验证索引范围
- 使用安全的数据结构
- 添加边界检查
```

### 类型转换错误
```
问题:
ClassCastException / TypeError

特征:
- 不兼容的类型转换
- 强制转换失败
- 泛型类型错误

解决方案:
- 使用instanceof检查
- 避免强制转换
- 使用泛型
- 类型安全设计
```

## 代码实现示例

### 堆栈跟踪分析器
```python
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import traceback

class ErrorType(Enum):
    NULL_POINTER = "null_pointer"
    ARRAY_INDEX = "array_index"
    TYPE_CAST = "type_cast"
    FILE_NOT_FOUND = "file_not_found"
    NETWORK_ERROR = "network_error"
    MEMORY_ERROR = "memory_error"
    CONCURRENT_ERROR = "concurrent_error"
    UNKNOWN = "unknown"

@dataclass
class StackFrame:
    """堆栈帧"""
    class_name: str
    method_name: str
    file_name: str
    line_number: int
    code_snippet: str

@dataclass
class ErrorAnalysis:
    """错误分析结果"""
    error_type: ErrorType
    error_message: str
    root_cause: str
    stack_frames: List[StackFrame]
    suggestions: List[str]
    related_patterns: List[str]
    fix_examples: List[str]

class StackTraceAnalyzer:
    """堆栈跟踪分析器"""
    
    def __init__(self):
        self.error_patterns = self._initialize_error_patterns()
        self.fix_suggestions = self._initialize_fix_suggestions()
    
    def analyze_stack_trace(self, stack_trace: str) -> ErrorAnalysis:
        """分析堆栈跟踪"""
        # 解析堆栈跟踪
        parsed_trace = self._parse_stack_trace(stack_trace)
        
        # 识别错误类型
        error_type = self._identify_error_type(stack_trace)
        
        # 提取错误消息
        error_message = self._extract_error_message(stack_trace)
        
        # 分析根本原因
        root_cause = self._analyze_root_cause(parsed_trace, error_type)
        
        # 生成修复建议
        suggestions = self._generate_suggestions(error_type, parsed_trace)
        
        # 识别相关模式
        related_patterns = self._identify_related_patterns(error_type)
        
        # 生成修复示例
        fix_examples = self._generate_fix_examples(error_type, parsed_trace)
        
        return ErrorAnalysis(
            error_type=error_type,
            error_message=error_message,
            root_cause=root_cause,
            stack_frames=parsed_trace,
            suggestions=suggestions,
            related_patterns=related_patterns,
            fix_examples=fix_examples
        )
    
    def _parse_stack_trace(self, stack_trace: str) -> List[StackFrame]:
        """解析堆栈跟踪"""
        frames = []
        
        # 匹配堆栈帧的正则表达式
        frame_pattern = r'at\s+([^.]+)\.([^(]+)\(([^:]+):(\d+)\)'
        
        for line in stack_trace.split('\n'):
            match = re.search(frame_pattern, line)
            if match:
                class_name = match.group(1)
                method_name = match.group(2)
                file_name = match.group(3)
                line_number = int(match.group(4))
                
                # 获取代码片段
                code_snippet = self._get_code_snippet(file_name, line_number)
                
                frame = StackFrame(
                    class_name=class_name,
                    method_name=method_name,
                    file_name=file_name,
                    line_number=line_number,
                    code_snippet=code_snippet
                )
                frames.append(frame)
        
        return frames
    
    def _get_code_snippet(self, file_name: str, line_number: int) -> str:
        """获取代码片段"""
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            start = max(0, line_number - 3)
            end = min(len(lines), line_number + 2)
            
            snippet_lines = []
            for i in range(start, end):
                marker = ">>> " if i == line_number - 1 else "    "
                snippet_lines.append(f"{marker}{i+1}: {lines[i].rstrip()}")
            
            return '\n'.join(snippet_lines)
        except Exception:
            return f"无法读取文件: {file_name}"
    
    def _identify_error_type(self, stack_trace: str) -> ErrorType:
        """识别错误类型"""
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, stack_trace, re.IGNORECASE):
                    return error_type
        
        return ErrorType.UNKNOWN
    
    def _extract_error_message(self, stack_trace: str) -> str:
        """提取错误消息"""
        lines = stack_trace.split('\n')
        for line in lines:
            if line and not line.startswith('at') and not line.startswith('\t'):
                return line.strip()
        return "未找到错误消息"
    
    def _analyze_root_cause(self, frames: List[StackFrame], error_type: ErrorType) -> str:
        """分析根本原因"""
        if not frames:
            return "无法确定根本原因"
        
        # 通常最后一个帧是错误发生的地方
        error_frame = frames[0]
        
        cause_analyses = {
            ErrorType.NULL_POINTER: f"在 {error_frame.class_name}.{error_frame.method_name} 中访问了空对象",
            ErrorType.ARRAY_INDEX: f"在 {error_frame.class_name}.{error_frame.method_name} 中数组索引越界",
            ErrorType.TYPE_CAST: f"在 {error_frame.class_name}.{error_frame.method_name} 中类型转换失败",
            ErrorType.FILE_NOT_FOUND: f"在 {error_frame.class_name}.{error_frame.method_name} 中文件不存在",
            ErrorType.NETWORK_ERROR: f"在 {error_frame.class_name}.{error_frame.method_name} 中网络连接失败",
            ErrorType.MEMORY_ERROR: f"在 {error_frame.class_name}.{error_frame.method_name} 中内存不足",
            ErrorType.CONCURRENT_ERROR: f"在 {error_frame.class_name}.{error_frame.method_name} 中并发冲突",
            ErrorType.UNKNOWN: f"在 {error_frame.class_name}.{error_frame.method_name} 中发生未知错误"
        }
        
        return cause_analyses.get(error_type, "未知错误类型")
    
    def _generate_suggestions(self, error_type: ErrorType, frames: List[StackFrame]) -> List[str]:
        """生成修复建议"""
        suggestions = self.fix_suggestions.get(error_type, [])
        
        # 根据具体上下文添加建议
        if frames:
            error_frame = frames[0]
            
            if error_type == ErrorType.NULL_POINTER:
                suggestions.append(f"在 {error_frame.method_name} 中添加空值检查")
            elif error_type == ErrorType.ARRAY_INDEX:
                suggestions.append(f"在 {error_frame.method_name} 中验证数组索引")
            elif error_type == ErrorType.TYPE_CAST:
                suggestions.append(f"在 {error_frame.method_name} 中使用类型安全转换")
        
        return suggestions
    
    def _identify_related_patterns(self, error_type: ErrorType) -> List[str]:
        """识别相关模式"""
        pattern_map = {
            ErrorType.NULL_POINTER: [
                "防御性编程",
                "空对象模式",
                "Optional类型",
                "输入验证"
            ],
            ErrorType.ARRAY_INDEX: [
                "边界检查",
                "安全数组访问",
                "循环不变式",
                "断言检查"
            ],
            ErrorType.TYPE_CAST: [
                "类型系统",
                "泛型编程",
                "类型推断",
                "接口设计"
            ],
            ErrorType.FILE_NOT_FOUND: [
                "文件系统检查",
                "路径处理",
                "异常处理",
                "资源管理"
            ],
            ErrorType.NETWORK_ERROR: [
                "重试机制",
                "超时处理",
                "连接池",
                "断路器模式"
            ],
            ErrorType.MEMORY_ERROR: [
                "内存管理",
                "垃圾回收",
                "内存泄漏检测",
                "性能优化"
            ],
            ErrorType.CONCURRENT_ERROR: [
                "同步机制",
                "锁策略",
                "原子操作",
                "并发设计模式"
            ]
        }
        
        return pattern_map.get(error_type, [])
    
    def _generate_fix_examples(self, error_type: ErrorType, frames: List[StackFrame]) -> List[str]:
        """生成修复示例"""
        examples = []
        
        if error_type == ErrorType.NULL_POINTER:
            examples.extend([
                "// 添加空值检查",
                "if (object != null) {",
                "    object.doSomething();",
                "} else {",
                "    // 处理空值情况",
                "}",
                "",
                "// 使用Optional",
                "Optional<String> optional = Optional.ofNullable(getValue());",
                "optional.ifPresent(value -> processValue(value));"
            ])
        
        elif error_type == ErrorType.ARRAY_INDEX:
            examples.extend([
                "// 检查数组边界",
                "if (index >= 0 && index < array.length) {",
                "    return array[index];",
                "} else {",
                "    throw new IndexOutOfBoundsException(\"索引越界\");",
                "}",
                "",
                "// 使用安全的循环",
                "for (int i = 0; i < array.length; i++) {",
                "    // 安全访问array[i]",
                "}"
            ])
        
        elif error_type == ErrorType.TYPE_CAST:
            examples.extend([
                "// 安全的类型转换",
                "if (object instanceof String) {",
                "    String str = (String) object;",
                "    // 使用str",
                "}",
                "",
                "// 使用泛型避免转换",
                "List<String> list = new ArrayList<>();",
                "String item = list.get(0); // 无需转换"
            ])
        
        return examples
    
    def _initialize_error_patterns(self) -> Dict[ErrorType, List[str]]:
        """初始化错误模式"""
        return {
            ErrorType.NULL_POINTER: [
                r'NullPointerException',
                r'AttributeError.*NoneType',
                r'object.*null',
                r'undefined.*property'
            ],
            ErrorType.ARRAY_INDEX: [
                r'ArrayIndexOutOfBoundsException',
                r'IndexError.*list.*out.*range',
                r'index.*out.*bounds'
            ],
            ErrorType.TYPE_CAST: [
                r'ClassCastException',
                r'TypeError.*cannot.*convert',
                r'InvalidCastException'
            ],
            ErrorType.FILE_NOT_FOUND: [
                r'FileNotFoundException',
                r'FileNotFoundError',
                r'No such file or directory'
            ],
            ErrorType.NETWORK_ERROR: [
                r'ConnectException',
                r'SocketTimeoutException',
                r'NetworkError',
                r'Connection refused'
            ],
            ErrorType.MEMORY_ERROR: [
                r'OutOfMemoryError',
                r'MemoryError',
                r'Cannot allocate memory'
            ],
            ErrorType.CONCURRENT_ERROR: [
                r'ConcurrentModificationException',
                r'DeadlockError',
                r'Race condition'
            ]
        }
    
    def _initialize_fix_suggestions(self) -> Dict[ErrorType, List[str]]:
        """初始化修复建议"""
        return {
            ErrorType.NULL_POINTER: [
                "添加空值检查",
                "使用Optional/Nullable类型",
                "初始化变量",
                "验证输入参数",
                "使用空对象模式"
            ],
            ErrorType.ARRAY_INDEX: [
                "检查数组长度",
                "验证索引范围",
                "使用安全的数据结构",
                "添加边界检查",
                "使用try-catch处理异常"
            ],
            ErrorType.TYPE_CAST: [
                "使用instanceof检查",
                "避免强制转换",
                "使用泛型",
                "类型安全设计",
                "添加类型验证"
            ],
            ErrorType.FILE_NOT_FOUND: [
                "检查文件是否存在",
                "使用绝对路径",
                "验证文件权限",
                "处理路径分隔符",
                "使用try-catch处理异常"
            ],
            ErrorType.NETWORK_ERROR: [
                "检查网络连接",
                "添加重试机制",
                "设置超时时间",
                "使用连接池",
                "实现断路器模式"
            ],
            ErrorType.MEMORY_ERROR: [
                "优化内存使用",
                "释放不需要的对象",
                "增加堆内存",
                "检查内存泄漏",
                "使用内存分析工具"
            ],
            ErrorType.CONCURRENT_ERROR: [
                "使用同步机制",
                "避免共享状态",
                "使用线程安全的数据结构",
                "正确使用锁",
                "避免死锁"
            ]
        }
    
    def generate_debug_report(self, analysis: ErrorAnalysis) -> str:
        """生成调试报告"""
        report = []
        report.append("=== 堆栈跟踪分析报告 ===\n")
        
        report.append(f"错误类型: {analysis.error_type.value}")
        report.append(f"错误消息: {analysis.error_message}")
        report.append(f"根本原因: {analysis.root_cause}\n")
        
        report.append("堆栈跟踪:")
        for i, frame in enumerate(analysis.stack_frames[:5]):  # 只显示前5帧
            report.append(f"  {i+1}. {frame.class_name}.{frame.method_name}")
            report.append(f"     文件: {frame.file_name}:{frame.line_number}")
            if frame.code_snippet:
                report.append(f"     代码:\n{frame.code_snippet}")
        
        report.append("\n修复建议:")
        for suggestion in analysis.suggestions:
            report.append(f"  - {suggestion}")
        
        report.append("\n相关模式:")
        for pattern in analysis.related_patterns:
            report.append(f"  - {pattern}")
        
        if analysis.fix_examples:
            report.append("\n修复示例:")
            for example in analysis.fix_examples:
                report.append(f"  {example}")
        
        return '\n'.join(report)

# 使用示例
def main():
    analyzer = StackTraceAnalyzer()
    
    # 示例堆栈跟踪
    stack_trace = """
Exception in thread "main" java.lang.NullPointerException
    at com.example.MyClass.processData(MyClass.java:25)
    at com.example.MyClass.main(MyClass.java:10)
    """
    
    # 分析堆栈跟踪
    analysis = analyzer.analyze_stack_trace(stack_trace)
    
    # 生成报告
    report = analyzer.generate_debug_report(analysis)
    print(report)

if __name__ == "__main__":
    main()
```

### 错误模式检测器
```python
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ErrorPattern:
    """错误模式"""
    name: str
    pattern: str
    severity: str
    description: str
    fix_suggestion: str

class ErrorPatternDetector:
    """错误模式检测器"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.pattern_statistics = defaultdict(int)
    
    def detect_patterns(self, error_log: str) -> List[ErrorPattern]:
        """检测错误模式"""
        detected_patterns = []
        
        for pattern in self.patterns:
            if re.search(pattern.pattern, error_log, re.IGNORECASE | re.MULTILINE):
                detected_patterns.append(pattern)
                self.pattern_statistics[pattern.name] += 1
        
        return detected_patterns
    
    def analyze_error_trends(self, error_logs: List[str]) -> Dict[str, Any]:
        """分析错误趋势"""
        trend_data = {}
        
        for log in error_logs:
            patterns = self.detect_patterns(log)
            for pattern in patterns:
                if pattern.name not in trend_data:
                    trend_data[pattern.name] = {
                        'count': 0,
                        'severity': pattern.severity,
                        'description': pattern.description
                    }
                trend_data[pattern.name]['count'] += 1
        
        # 按出现频率排序
        sorted_patterns = sorted(
            trend_data.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        return {
            'total_errors': len(error_logs),
            'pattern_frequency': dict(sorted_patterns),
            'most_common': sorted_patterns[0] if sorted_patterns else None,
            'critical_patterns': [
                name for name, data in trend_data.items()
                if data['severity'] == 'critical'
            ]
        }
    
    def _initialize_patterns(self) -> List[ErrorPattern]:
        """初始化错误模式"""
        return [
            ErrorPattern(
                name="空指针异常",
                pattern=r'NullPointerException|AttributeError.*NoneType',
                severity="high",
                description="访问空对象的属性或方法",
                fix_suggestion="添加空值检查或使用Optional类型"
            ),
            ErrorPattern(
                name="数组越界",
                pattern=r'ArrayIndexOutOfBoundsException|IndexError.*list.*index',
                severity="medium",
                description="访问数组或列表的越界索引",
                fix_suggestion="检查索引范围或使用安全的访问方法"
            ),
            ErrorPattern(
                name="类型转换错误",
                pattern=r'ClassCastException|TypeError.*cannot.*convert',
                severity="medium",
                description="不兼容的类型转换",
                fix_suggestion="使用类型检查或避免强制转换"
            ),
            ErrorPattern(
                name="文件不存在",
                pattern=r'FileNotFoundException|FileNotFoundError',
                severity="medium",
                description="尝试访问不存在的文件",
                fix_suggestion="检查文件路径或创建文件"
            ),
            ErrorPattern(
                name="内存不足",
                pattern=r'OutOfMemoryError|MemoryError',
                severity="critical",
                description="内存耗尽",
                fix_suggestion="优化内存使用或增加堆内存"
            ),
            ErrorPattern(
                name="网络连接错误",
                pattern=r'ConnectException|NetworkError|Connection refused',
                severity="high",
                description="网络连接失败",
                fix_suggestion="检查网络连接或添加重试机制"
            ),
            ErrorPattern(
                name="并发修改异常",
                pattern=r'ConcurrentModificationException',
                severity="high",
                description="并发修改集合",
                fix_suggestion="使用同步机制或并发安全的数据结构"
            ),
            ErrorPattern(
                name="死锁",
                pattern=r'DeadlockError|deadlock',
                severity="critical",
                description="线程死锁",
                fix_suggestion="重新设计锁的获取顺序"
            )
        ]
    
    def generate_pattern_report(self, patterns: List[ErrorPattern]) -> str:
        """生成模式报告"""
        if not patterns:
            return "未检测到已知错误模式"
        
        report = ["=== 错误模式检测报告 ===\n"]
        
        # 按严重程度分组
        by_severity = defaultdict(list)
        for pattern in patterns:
            by_severity[pattern.severity].append(pattern)
        
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in by_severity:
                report.append(f"{severity.upper()} 级别:")
                for pattern in by_severity[severity]:
                    report.append(f"  - {pattern.name}")
                    report.append(f"    描述: {pattern.description}")
                    report.append(f"    建议: {pattern.fix_suggestion}")
                report.append("")
        
        return '\n'.join(report)

# 使用示例
def main():
    detector = ErrorPatternDetector()
    
    # 示例错误日志
    error_logs = [
        """
Exception in thread "main" java.lang.NullPointerException
    at com.example.MyClass.processData(MyClass.java:25)
        """,
        """
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException
    at com.example.MyClass.processArray(MyClass.java:30)
        """,
        """
Exception in thread "main" java.lang.NullPointerException
    at com.example.MyClass.validateInput(MyClass.java:15)
        """
    ]
    
    # 分析错误趋势
    trends = detector.analyze_error_trends(error_logs)
    
    print("=== 错误趋势分析 ===")
    print(f"总错误数: {trends['total_errors']}")
    print(f"最常见错误: {trends['most_common'][0] if trends['most_common'] else 'None'}")
    
    print("\n错误频率:")
    for pattern, data in trends['pattern_frequency'].items():
        print(f"  {pattern}: {data['count']} 次")

if __name__ == "__main__":
    main()
```

## 调试最佳实践

### 错误处理策略
1. **快速失败**: 尽早发现和报告错误
2. **明确错误**: 提供清晰的错误信息
3. **日志记录**: 记录详细的错误上下文
4. **异常恢复**: 实现优雅的错误恢复

### 调试技巧
1. **重现问题**: 创建最小重现案例
2. **二分查找**: 逐步缩小问题范围
3. **日志分析**: 分析程序执行日志
4. **调试工具**: 使用专业调试工具

### 代码审查
1. **错误处理**: 检查异常处理是否完整
2. **边界条件**: 验证边界条件处理
3. **资源管理**: 确保资源正确释放
4. **并发安全**: 检查线程安全性

## 相关技能

- **log-analyzer** - 日志分析
- **performance-profiler** - 性能分析
- **code-reviewer** - 代码审查
- **test-automation** - 测试自动化
