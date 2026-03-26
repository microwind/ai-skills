# 堆栈跟踪分析器参考文档

## 堆栈跟踪分析器概述

### 什么是堆栈跟踪分析器
堆栈跟踪分析器是一个专门用于分析软件错误、异常堆栈跟踪和崩溃报告的工具。该工具支持多种编程语言和错误类型，提供智能错误识别、根因分析、解决方案推荐和预防措施，帮助开发者快速定位问题、理解错误本质并实施有效修复。

### 主要功能
- **多语言支持**: 支持Python、Java、JavaScript、C++、C#、Go、Rust等主流编程语言
- **智能错误识别**: 自动识别常见错误模式和异常类型
- **根因分析**: 深入分析错误产生的根本原因
- **解决方案推荐**: 提供针对性的修复建议和最佳实践
- **代码示例**: 提供修复代码示例和重构建议
- **预防措施**: 建议避免类似错误的编码实践
- **调试工具集成**: 支持与主流调试器的集成
- **性能分析**: 分析性能瓶颈和资源使用问题

## 核心分析引擎

### 堆栈跟踪解析器
```python
# stack_trace_parser.py
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

class ErrorType(Enum):
    NULL_POINTER = "null_pointer"
    ARRAY_INDEX = "array_index"
    TYPE_CAST = "type_cast"
    MEMORY_LEAK = "memory_leak"
    DEADLOCK = "deadlock"
    RACE_CONDITION = "race_condition"
    RESOURCE_LEAK = "resource_leak"
    STACK_OVERFLOW = "stack_overflow"
    DIVISION_BY_ZERO = "division_by_zero"
    FILE_NOT_FOUND = "file_not_found"
    NETWORK_ERROR = "network_error"
    CUSTOM_ERROR = "custom_error"

class ProgrammingLanguage(Enum):
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    UNKNOWN = "unknown"

@dataclass
class StackFrame:
    file_name: str
    line_number: int
    function_name: str
    class_name: Optional[str] = None
    module_name: Optional[str] = None
    code_snippet: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None

@dataclass
class ErrorInfo:
    error_type: ErrorType
    error_message: str
    exception_name: str
    language: ProgrammingLanguage
    stack_frames: List[StackFrame]
    timestamp: datetime
    context: Dict[str, Any] = None

@dataclass
class AnalysisResult:
    error_info: ErrorInfo
    root_cause: str
    severity: str
    confidence: float
    solutions: List[str]
    code_examples: List[str]
    prevention_tips: List[str]
    related_patterns: List[str]

class StackTraceParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.patterns = self._init_patterns()
    
    def _init_patterns(self) -> Dict[str, Dict]:
        """初始化错误模式"""
        return {
            'python': {
                'null_pointer': [
                    r'AttributeError: \'NoneType\' object has no attribute \'.+\'',
                    r'TypeError: \'NoneType\' object is not .+',
                    r'UnboundLocalError: local variable \'.+\' referenced before assignment'
                ],
                'array_index': [
                    r'IndexError: list index out of range',
                    r'IndexError: .+ index out of range',
                    r'KeyError: .+'
                ],
                'type_cast': [
                    r'TypeError: .+ must be .+, not .+',
                    r'ValueError: invalid literal for .+\(\) with base .+: .+',
                    r'AttributeError: .+ object has no attribute .+'
                ],
                'memory_leak': [
                    r'MemoryError: Unable to allocate .+ bytes',
                    r'ResourceWarning: unclosed .+'
                ],
                'stack_overflow': [
                    r'RecursionError: maximum recursion depth exceeded'
                ]
            },
            'java': {
                'null_pointer': [
                    r'NullPointerException: .+',
                    r'java\.lang\.NullPointerException: .+'
                ],
                'array_index': [
                    r'ArrayIndexOutOfBoundsException: .+',
                    r'java\.lang\.ArrayIndexOutOfBoundsException: .+',
                    r'IndexOutOfBoundsException: .+'
                ],
                'type_cast': [
                    r'ClassCastException: .+',
                    r'java\.lang\.ClassCastException: .+'
                ],
                'memory_leak': [
                    r'OutOfMemoryError: .+',
                    r'java\.lang\.OutOfMemoryError: .+'
                ],
                'stack_overflow': [
                    r'StackOverflowError: .+',
                    r'java\.lang\.StackOverflowError: .+'
                ]
            },
            'javascript': {
                'null_pointer': [
                    r'TypeError: Cannot read property .+ of (null|undefined)',
                    r'TypeError: .+ is (null|undefined)',
                    r'ReferenceError: .+ is not defined'
                ],
                'type_cast': [
                    r'TypeError: .+ is not a function',
                    r'TypeError: .+ is not .+'
                ]
            }
        }
    
    def parse_stack_trace(self, stack_trace: str, language: str = 'auto') -> ErrorInfo:
        """解析堆栈跟踪"""
        # 检测编程语言
        if language == 'auto':
            language = self._detect_language(stack_trace)
        
        lang_enum = ProgrammingLanguage(language)
        
        # 提取错误信息
        error_type, error_message, exception_name = self._extract_error_info(
            stack_trace, lang_enum
        )
        
        # 解析堆栈帧
        stack_frames = self._parse_stack_frames(stack_trace, lang_enum)
        
        # 创建错误信息对象
        error_info = ErrorInfo(
            error_type=error_type,
            error_message=error_message,
            exception_name=exception_name,
            language=lang_enum,
            stack_frames=stack_frames,
            timestamp=datetime.now(),
            context=self._extract_context(stack_trace)
        )
        
        return error_info
    
    def _detect_language(self, stack_trace: str) -> str:
        """检测编程语言"""
        if 'Traceback (most recent call last):' in stack_trace:
            return 'python'
        elif 'Exception in thread' in stack_trace or 'at ' in stack_trace:
            return 'java'
        elif 'TypeError:' in stack_trace or 'ReferenceError:' in stack_trace:
            return 'javascript'
        elif 'std::' in stack_trace or '0x' in stack_trace:
            return 'cpp'
        else:
            return 'unknown'
    
    def _extract_error_info(self, stack_trace: str, language: ProgrammingLanguage) -> Tuple[ErrorType, str, str]:
        """提取错误信息"""
        lines = stack_trace.strip().split('\n')
        error_line = lines[-1] if lines else ""
        
        # 根据语言模式匹配错误类型
        patterns = self.patterns.get(language.value, {})
        
        for error_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, error_line, re.IGNORECASE):
                    return ErrorType(error_type), error_line, self._extract_exception_name(error_line)
        
        return ErrorType.CUSTOM_ERROR, error_line, self._extract_exception_name(error_line)
    
    def _extract_exception_name(self, error_line: str) -> str:
        """提取异常名称"""
        match = re.search(r'^(\w+):', error_line)
        if match:
            return match.group(1)
        return "Unknown"
    
    def _parse_stack_frames(self, stack_trace: str, language: ProgrammingLanguage) -> List[StackFrame]:
        """解析堆栈帧"""
        frames = []
        lines = stack_trace.strip().split('\n')
        
        if language == ProgrammingLanguage.PYTHON:
            frames = self._parse_python_frames(lines)
        elif language == ProgrammingLanguage.JAVA:
            frames = self._parse_java_frames(lines)
        elif language == ProgrammingLanguage.JAVASCRIPT:
            frames = self._parse_javascript_frames(lines)
        else:
            frames = self._parse_generic_frames(lines)
        
        return frames
    
    def _parse_python_frames(self, lines: List[str]) -> List[StackFrame]:
        """解析Python堆栈帧"""
        frames = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 匹配文件行 "  File "path", line N, in function"
            file_match = re.match(r'File "([^"]+)", line (\d+)', line)
            if file_match:
                file_name = file_match.group(1)
                line_number = int(file_match.group(2))
                
                # 下一行是函数名
                if i + 1 < len(lines):
                    function_line = lines[i + 1].strip()
                    function_match = re.match(r'(\w+)', function_line)
                    function_name = function_match.group(1) if function_match else "unknown"
                    
                    frame = StackFrame(
                        file_name=file_name,
                        line_number=line_number,
                        function_name=function_name
                    )
                    frames.append(frame)
                    i += 2
                    continue
            
            i += 1
        
        return frames
    
    def _parse_java_frames(self, lines: List[str]) -> List[StackFrame]:
        """解析Java堆栈帧"""
        frames = []
        
        for line in lines:
            # 匹配 "at package.Class.method(Class.java:123)"
            match = re.search(r'at\s+([\w.]+)\.(\w+)\(([^:]+):(\d+)\)', line)
            if match:
                class_name = match.group(1)
                function_name = match.group(2)
                file_name = match.group(3)
                line_number = int(match.group(4))
                
                frame = StackFrame(
                    file_name=file_name,
                    line_number=line_number,
                    function_name=function_name,
                    class_name=class_name
                )
                frames.append(frame)
        
        return frames
    
    def _parse_javascript_frames(self, lines: List[str]) -> List[StackFrame]:
        """解析JavaScript堆栈帧"""
        frames = []
        
        for line in lines:
            # 匹配 "at functionName (path:line:column)"
            match = re.search(r'at\s+(\w+)\s+\(([^:]+):(\d+):\d+\)', line)
            if match:
                function_name = match.group(1)
                file_name = match.group(2)
                line_number = int(match.group(3))
                
                frame = StackFrame(
                    file_name=file_name,
                    line_number=line_number,
                    function_name=function_name
                )
                frames.append(frame)
        
        return frames
    
    def _parse_generic_frames(self, lines: List[str]) -> List[StackFrame]:
        """解析通用堆栈帧"""
        frames = []
        
        for line in lines:
            # 通用模式匹配
            if ':' in line and any(char.isdigit() for char in line):
                parts = line.split(':')
                if len(parts) >= 2:
                    file_name = parts[0].strip()
                    try:
                        line_number = int(parts[1].strip())
                        function_name = "unknown"
                        
                        frame = StackFrame(
                            file_name=file_name,
                            line_number=line_number,
                            function_name=function_name
                        )
                        frames.append(frame)
                    except ValueError:
                        continue
        
        return frames
    
    def _extract_context(self, stack_trace: str) -> Dict[str, Any]:
        """提取上下文信息"""
        context = {}
        
        # 提取时间戳
        time_patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})',
            r'(\w{3} \d{2} \d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, stack_trace)
            if match:
                context['timestamp'] = match.group(1)
                break
        
        # 提取线程信息
        thread_match = re.search(r'Thread-\d+|Thread\["[^"]+"\]', stack_trace)
        if thread_match:
            context['thread'] = thread_match.group(0)
        
        # 提取进程信息
        process_match = re.search(r'PID:\d+|Process:\d+', stack_trace)
        if process_match:
            context['process'] = process_match.group(0)
        
        return context

# 使用示例
parser = StackTraceParser()

# Python示例
python_trace = """Traceback (most recent call last):
  File "app.py", line 42, in main
    result = process_data(data)
  File "utils.py", line 15, in process_data
    return data.items()
AttributeError: 'NoneType' object has no attribute 'items'"""

error_info = parser.parse_stack_trace(python_trace)
print(f"错误类型: {error_info.error_type}")
print(f"错误消息: {error_info.error_message}")
print(f"堆栈帧数量: {len(error_info.stack_frames)}")
```

### 错误分析器
```python
# error_analyzer.py
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.solution_templates = self._init_solution_templates()
        self.prevention_tips = self._init_prevention_tips()
    
    def analyze_error(self, error_info: ErrorInfo) -> AnalysisResult:
        """分析错误"""
        # 根因分析
        root_cause = self._analyze_root_cause(error_info)
        
        # 严重性评估
        severity = self._assess_severity(error_info)
        
        # 置信度计算
        confidence = self._calculate_confidence(error_info)
        
        # 生成解决方案
        solutions = self._generate_solutions(error_info)
        
        # 生成代码示例
        code_examples = self._generate_code_examples(error_info)
        
        # 生成预防建议
        prevention_tips = self._generate_prevention_tips(error_info)
        
        # 识别相关模式
        related_patterns = self._identify_related_patterns(error_info)
        
        return AnalysisResult(
            error_info=error_info,
            root_cause=root_cause,
            severity=severity.value,
            confidence=confidence,
            solutions=solutions,
            code_examples=code_examples,
            prevention_tips=prevention_tips,
            related_patterns=related_patterns
        )
    
    def _analyze_root_cause(self, error_info: ErrorInfo) -> str:
        """分析根本原因"""
        if error_info.error_type == ErrorType.NULL_POINTER:
            return "变量未正确初始化或方法返回了null值"
        elif error_info.error_type == ErrorType.ARRAY_INDEX:
            return "数组访问索引超出了有效范围"
        elif error_info.error_type == ErrorType.TYPE_CAST:
            return "尝试将对象转换为不兼容的类型"
        elif error_info.error_type == ErrorType.MEMORY_LEAK:
            return "内存未正确释放或资源管理不当"
        elif error_info.error_type == ErrorType.DEADLOCK:
            return "多个线程相互等待对方释放资源"
        elif error_info.error_type == ErrorType.RACE_CONDITION:
            return "多个线程同时访问共享资源导致数据不一致"
        else:
            return "需要进一步分析代码逻辑和执行环境"
    
    def _assess_severity(self, error_info: ErrorInfo) -> Severity:
        """评估严重性"""
        if error_info.error_type in [ErrorType.NULL_POINTER, ErrorType.ARRAY_INDEX]:
            return Severity.MEDIUM
        elif error_info.error_type in [ErrorType.MEMORY_LEAK, ErrorType.DEADLOCK]:
            return Severity.HIGH
        elif error_info.error_type == ErrorType.STACK_OVERFLOW:
            return Severity.CRITICAL
        else:
            return Severity.LOW
    
    def _calculate_confidence(self, error_info: ErrorInfo) -> float:
        """计算置信度"""
        confidence = 0.5  # 基础置信度
        
        # 根据堆栈帧数量调整
        if len(error_info.stack_frames) > 0:
            confidence += 0.2
        
        # 根据错误信息完整性调整
        if error_info.error_message and error_info.exception_name:
            confidence += 0.2
        
        # 根据已知模式匹配调整
        if error_info.error_type != ErrorType.CUSTOM_ERROR:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_solutions(self, error_info: ErrorInfo) -> List[str]:
        """生成解决方案"""
        solutions = []
        
        if error_info.error_type == ErrorType.NULL_POINTER:
            solutions = [
                "在访问对象属性前进行空值检查",
                "使用Optional/Nullable类型明确表示可能为空的值",
                "确保变量在使用前已正确初始化",
                "添加防御性编程检查输入参数"
            ]
        elif error_info.error_type == ErrorType.ARRAY_INDEX:
            solutions = [
                "在访问数组前检查索引范围",
                "使用安全的循环边界条件",
                "考虑使用异常处理捕获越界异常",
                "使用动态数组或集合类避免固定大小限制"
            ]
        elif error_info.error_type == ErrorType.TYPE_CAST:
            solutions = [
                "使用类型检查函数（如isinstance）验证类型",
                "避免强制类型转换，使用多态或泛型",
                "添加异常处理处理类型转换失败",
                "设计类型安全的API接口"
            ]
        
        return solutions
    
    def _generate_code_examples(self, error_info: ErrorInfo) -> List[str]:
        """生成代码示例"""
        examples = []
        
        if error_info.language == ProgrammingLanguage.PYTHON:
            if error_info.error_type == ErrorType.NULL_POINTER:
                examples.append("""
# 空值检查示例
def safe_access(data):
    if data is not None:
        return data.items()
    else:
        return []

# 使用Optional类型
from typing import Optional, List

def process_data(data: Optional[Dict]) -> List:
    if data is None:
        return []
    return list(data.items())
""")
            elif error_info.error_type == ErrorType.ARRAY_INDEX:
                examples.append("""
# 数组边界检查示例
def safe_array_access(arr, index):
    if 0 <= index < len(arr):
        return arr[index]
    else:
        raise IndexError(f"Index {index} out of range")

# 使用try-except处理
def safe_get_item(arr, index, default=None):
    try:
        return arr[index]
    except IndexError:
        return default
""")
        
        elif error_info.language == ProgrammingLanguage.JAVA:
            if error_info.error_type == ErrorType.NULL_POINTER:
                examples.append("""
// 空值检查示例
public List<String> safeGetItems(Map<String, List<String>> data) {
    if (data != null) {
        return data.get("items");
    }
    return Collections.emptyList();
}

// 使用Optional
public Optional<List<String>> getItems(Map<String, List<String>> data) {
    return Optional.ofNullable(data)
                    .map(map -> map.get("items"))
                    .orElse(Collections.emptyList());
}
""")
        
        return examples
    
    def _generate_prevention_tips(self, error_info: ErrorInfo) -> List[str]:
        """生成预防建议"""
        tips = []
        
        if error_info.error_type == ErrorType.NULL_POINTER:
            tips = [
                "使用单元测试验证所有可能的输入情况",
                "采用契约编程明确方法的前置条件",
                "使用静态分析工具检测潜在的空指针问题",
                "建立代码审查流程检查空值处理"
            ]
        elif error_info.error_type == ErrorType.ARRAY_INDEX:
            tips = [
                "使用增强for循环而非索引循环",
                "考虑使用集合框架的内置方法",
                "添加边界测试用例",
                "使用断言验证数组参数"
            ]
        
        return tips
    
    def _identify_related_patterns(self, error_info: ErrorInfo) -> List[str]:
        """识别相关模式"""
        patterns = []
        
        if error_info.error_type == ErrorType.NULL_POINTER:
            patterns = [
                "未初始化变量模式",
                "方法返回null模式",
                "链式调用模式",
                "外部输入验证缺失模式"
            ]
        elif error_info.error_type == ErrorType.ARRAY_INDEX:
            patterns = [
                "循环边界错误模式",
                "数组长度计算错误模式",
                "多维数组访问模式",
                "动态数组扩容模式"
            ]
        
        return patterns
    
    def _init_solution_templates(self) -> Dict[str, List[str]]:
        """初始化解决方案模板"""
        return {
            'null_pointer': [
                "添加空值检查",
                "使用Optional类型",
                "初始化变量",
                "验证输入参数"
            ],
            'array_index': [
                "检查数组边界",
                "使用安全循环",
                "异常处理",
                "使用动态集合"
            ],
            'type_cast': [
                "类型检查",
                "避免强制转换",
                "异常处理",
                "类型安全设计"
            ]
        }
    
    def _init_prevention_tips(self) -> Dict[str, List[str]]:
        """初始化预防建议"""
        return {
            'null_pointer': [
                "单元测试",
                "契约编程",
                "静态分析",
                "代码审查"
            ],
            'array_index': [
                "增强for循环",
                "集合框架",
                "边界测试",
                "断言验证"
            ],
            'type_cast': [
                "类型安全API",
                "泛型编程",
                "输入验证",
                "文档规范"
            ]
        }

# 使用示例
analyzer = ErrorAnalyzer()
result = analyzer.analyze_error(error_info)
print(f"根本原因: {result.root_cause}")
print(f"严重性: {result.severity}")
print(f"置信度: {result.confidence}")
print(f"解决方案: {result.solutions}")
```

## 常见错误模式库

### Python错误模式
```python
# python_error_patterns.py
class PythonErrorPatterns:
    """Python常见错误模式"""
    
    @staticmethod
    def get_null_pointer_patterns():
        return [
            {
                'pattern': r'AttributeError: \'NoneType\' object has no attribute \'.+\'',
                'description': '尝试访问None对象的属性',
                'example': 'data.items() 当data为None时',
                'solution': '添加空值检查: if data is not None: data.items()'
            },
            {
                'pattern': r'TypeError: \'NoneType\' object is not .+',
                'description': '尝试对None对象进行不支持的操作',
                'example': 'len(None) 或 None + 1',
                'solution': '确保对象不为None或提供默认值'
            }
        ]
    
    @staticmethod
    def get_array_index_patterns():
        return [
            {
                'pattern': r'IndexError: list index out of range',
                'description': '列表索引超出范围',
                'example': 'arr[10] 当arr长度小于11时',
                'solution': '检查索引范围: if 0 <= index < len(arr)'
            },
            {
                'pattern': r'KeyError: .+',
                'description': '字典键不存在',
                'example': 'data["missing_key"]',
                'solution': '使用get()方法或检查键是否存在'
            }
        ]
    
    @staticmethod
    def get_type_cast_patterns():
        return [
            {
                'pattern': r'TypeError: .+ must be .+, not .+',
                'description': '类型不匹配错误',
                'example': 'len(123) 当参数应为字符串时',
                'solution': '使用类型检查函数或转换函数'
            },
            {
                'pattern': r'ValueError: invalid literal for .+\(\) with base .+: .+',
                'description': '值转换错误',
                'example': 'int("abc")',
                'solution': '添加异常处理或验证输入格式'
            }
        ]
```

### Java错误模式
```java
// JavaErrorPatterns.java
public class JavaErrorPatterns {
    
    public static class NullPointerPatterns {
        public static final String[] PATTERNS = {
            "NullPointerException: .+",
            "java.lang.NullPointerException: .+"
        };
        
        public static final String[] DESCRIPTIONS = {
            "尝试调用null对象的方法",
            "访问null对象的属性"
        };
        
        public static final String[] SOLUTIONS = {
            "添加空值检查: if (obj != null)",
            "使用Optional类避免null值",
            "确保对象已正确初始化"
        };
    }
    
    public static class ArrayIndexPatterns {
        public static final String[] PATTERNS = {
            "ArrayIndexOutOfBoundsException: .+",
            "java.lang.ArrayIndexOutOfBoundsException: .+"
        };
        
        public static final String[] DESCRIPTIONS = {
            "数组索引超出范围",
            "负数索引访问"
        };
        
        public static final String[] SOLUTIONS = {
            "检查索引范围: if (index >= 0 && index < array.length)",
            "使用增强for循环",
            "添加边界检查"
        };
    }
}
```

## 集成接口

### 调试器集成
```python
# debugger_integration.py
import subprocess
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class DebuggerConfig:
    debugger_type: str
    executable_path: str
    arguments: List[str]
    working_directory: str
    environment: Dict[str, str]

class DebuggerIntegration:
    def __init__(self, config: DebuggerConfig):
        self.config = config
    
    def attach_to_process(self, pid: int) -> bool:
        """附加到进程"""
        try:
            if self.config.debugger_type == "gdb":
                cmd = [self.config.executable_path, "-p", str(pid)]
                subprocess.run(cmd, check=True)
                return True
            elif self.config.debugger_type == "pdb":
                # PDB通常用于Python脚本调试
                return False
        except subprocess.CalledProcessError:
            return False
        return False
    
    def set_breakpoint(self, file_name: str, line_number: int) -> bool:
        """设置断点"""
        try:
            if self.config.debugger_type == "gdb":
                cmd = [self.config.executable_path, "--batch", "--ex", f"break {file_name}:{line_number}"]
                subprocess.run(cmd, check=True)
                return True
        except subprocess.CalledProcessError:
            return False
        return False
    
    def get_variable_value(self, variable_name: str) -> Optional[str]:
        """获取变量值"""
        try:
            if self.config.debugger_type == "gdb":
                cmd = [self.config.executable_path, "--batch", "--ex", f"print {variable_name}"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
        return None
```

## 使用示例

### 完整分析流程
```python
# complete_analysis_example.py
from stack_trace_parser import StackTraceParser
from error_analyzer import ErrorAnalyzer
from debugger_integration import DebuggerIntegration

def analyze_stack_trace(stack_trace: str, language: str = 'auto') -> Dict[str, Any]:
    """完整的堆栈跟踪分析流程"""
    
    # 1. 解析堆栈跟踪
    parser = StackTraceParser()
    error_info = parser.parse_stack_trace(stack_trace, language)
    
    # 2. 分析错误
    analyzer = ErrorAnalyzer()
    analysis_result = analyzer.analyze_error(error_info)
    
    # 3. 生成报告
    report = {
        'error_summary': {
            'type': error_info.error_type.value,
            'message': error_info.error_message,
            'exception': error_info.exception_name,
            'language': error_info.language.value,
            'severity': analysis_result.severity,
            'confidence': analysis_result.confidence
        },
        'root_cause': analysis_result.root_cause,
        'solutions': analysis_result.solutions,
        'code_examples': analysis_result.code_examples,
        'prevention_tips': analysis_result.prevention_tips,
        'related_patterns': analysis_result.related_patterns,
        'stack_frames': [
            {
                'file': frame.file_name,
                'line': frame.line_number,
                'function': frame.function_name,
                'class': frame.class_name
            }
            for frame in error_info.stack_frames
        ]
    }
    
    return report

# 使用示例
if __name__ == "__main__":
    # 示例堆栈跟踪
    example_trace = """Traceback (most recent call last):
  File "main.py", line 25, in <module>
    result = process_user_data(user_input)
  File "processor.py", line 18, in process_user_data
    return data.validate()
AttributeError: 'NoneType' object has no attribute 'validate'"""
    
    # 执行分析
    report = analyze_stack_trace(example_trace)
    
    # 输出结果
    print(json.dumps(report, indent=2, ensure_ascii=False))
```

## 扩展功能

### 自定义错误模式
```python
# custom_patterns.py
class CustomErrorPattern:
    def __init__(self, name: str, pattern: str, description: str, 
                 solution: str, language: str):
        self.name = name
        self.pattern = pattern
        self.description = description
        self.solution = solution
        self.language = language
    
    def matches(self, error_message: str) -> bool:
        """检查错误消息是否匹配此模式"""
        import re
        return bool(re.search(self.pattern, error_message, re.IGNORECASE))

class PatternRegistry:
    def __init__(self):
        self.patterns = []
    
    def register_pattern(self, pattern: CustomErrorPattern):
        """注册自定义错误模式"""
        self.patterns.append(pattern)
    
    def find_matching_pattern(self, error_message: str, language: str) -> Optional[CustomErrorPattern]:
        """查找匹配的错误模式"""
        for pattern in self.patterns:
            if pattern.language == language and pattern.matches(error_message):
                return pattern
        return None

# 使用示例
registry = PatternRegistry()

# 注册自定义模式
custom_pattern = CustomErrorPattern(
    name="DatabaseConnectionError",
    pattern=r"Database connection failed: .+",
    description="数据库连接失败",
    solution="检查数据库配置和网络连接",
    language="python"
)

registry.register_pattern(custom_pattern)
```

### 机器学习增强
```python
# ml_enhanced_analyzer.py
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.nause import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

class MLErrorAnalyzer:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.pipeline = None
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """加载或训练模型"""
        try:
            self.pipeline = joblib.load('error_classifier_model.pkl')
        except FileNotFoundError:
            # 如果模型不存在，需要训练
            self._train_model()
    
    def _train_model(self):
        """训练错误分类模型"""
        # 这里需要准备训练数据
        # 示例数据格式: [(error_message, error_type), ...]
        training_data = [
            ("NullPointerException: Cannot read property", "null_pointer"),
            ("ArrayIndexOutOfBoundsException: Index 10 out of bounds", "array_index"),
            # ... 更多训练数据
        ]
        
        messages, labels = zip(*training_data)
        
        # 创建管道
        self.pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer()),
            ('classifier', LogisticRegression())
        ])
        
        # 训练模型
        self.pipeline.fit(messages, labels)
        
        # 保存模型
        joblib.dump(self.pipeline, 'error_classifier_model.pkl')
    
    def predict_error_type(self, error_message: str) -> str:
        """预测错误类型"""
        if self.pipeline:
            return self.pipeline.predict([error_message])[0]
        return "unknown"
    
    def get_prediction_confidence(self, error_message: str) -> float:
        """获取预测置信度"""
        if self.pipeline:
            probabilities = self.pipeline.predict_proba([error_message])
            return np.max(probabilities)
        return 0.0
```

这个堆栈跟踪分析器提供了完整的错误分析功能，包括多语言支持、智能错误识别、根因分析、解决方案推荐和预防措施。通过模块化设计，可以轻松扩展新的错误模式和语言支持。
