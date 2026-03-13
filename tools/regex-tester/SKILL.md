---
name: 正则表达式测试器
description: "当测试正则表达式、验证模式、调试正则表达式问题或优化正则表达式性能时，在生产环境使用前测试正则表达式。"
license: MIT
---

# 正则表达式测试器技能

## 概述
正则表达式功能强大但很脆弱。一个拼写错误就会完全破坏模式。在部署前彻底测试正则表达式。

**核心原则**: 如果你没有用边界情况测试，这个正则表达式就是错的。

## 何时使用

**始终:**
- 在验证中使用正则表达式之前
- 优化正则表达式性能
- 调试"不匹配"问题
- 测试边界情况
- 验证复杂模式
- 调试性能问题

**触发短语:**
- "测试这个正则表达式"
- "为什么这个正则不匹配？"
- "优化正则表达式性能"
- "验证正则模式"
- "正则表达式调试"
- "边界情况测试"

## 正则表达式测试功能

### 模式验证
- 语法检查
- 语义验证
- 性能分析
- 兼容性检查
- 复杂度评估

### 测试用例
- 正面测试
- 负面测试
- 边界情况
- 性能测试
- 压力测试

### 调试工具
- 匹配可视化
- 分组分析
- 回溯追踪
- 性能分析
- 错误诊断

## 常见正则表达式问题

### 贪婪匹配问题
```
问题:
贪婪量词会匹配尽可能多的字符

错误示例:
pattern: /<div>.*<\/div>/
text: <div>第一个</div><div>第二个</div>
匹配结果: <div>第一个</div><div>第二个</div>  ← 匹配过多

解决方案:
使用非贪婪量词或精确匹配
pattern: /<div>.*?<\/div>/
或 pattern: /<div>[^<]*<\/div>/
```

### 回溯灾难
```
问题:
嵌套量词导致指数级时间复杂度

错误示例:
pattern: /(a+)+b/
text: aaaaaaaaaaaaaaaaaaaaaaa
结果: 长时间无响应

解决方案:
避免嵌套量词，使用原子分组
pattern: /(?>a+)+b/
或 pattern: /a+b/
```

### Unicode处理
```
问题:
正则表达式无法正确处理Unicode字符

错误示例:
pattern: /\w+/  ← 只匹配ASCII单词字符
text: 你好世界123
匹配结果: 只匹配"123"

解决方案:
使用Unicode属性或标志
pattern: /[\p{L}\p{N}]+/u
或 pattern: /[^\W\d_]+/
```

## 代码实现示例

### 正则表达式测试器
```python
import re
import time
from typing import Dict, List, Any, Optional, Tuple, Pattern
from dataclasses import dataclass
from enum import Enum
import unicodedata

class TestResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class RegexTestCase:
    """正则表达式测试用例"""
    name: str
    input_text: str
    expected_matches: List[str]
    expected_groups: List[Dict[str, Any]] = None
    should_match: bool = True
    description: str = ""

@dataclass
class RegexTestResult:
    """测试结果"""
    test_case: RegexTestCase
    result: TestResult
    actual_matches: List[str]
    actual_groups: List[Dict[str, Any]]
    execution_time: float
    error_message: str = ""

@dataclass
class RegexAnalysis:
    """正则表达式分析"""
    pattern: str
    flags: List[str]
    complexity: str
    performance_score: int
    potential_issues: List[str]
    optimization_suggestions: List[str]

class RegexTester:
    """正则表达式测试器"""
    
    def __init__(self):
        self.test_timeout = 5.0  # 测试超时时间（秒）
        self.performance_threshold = 1000  # 性能阈值（毫秒）
        self.complexity_rules = self._initialize_complexity_rules()
    
    def test_regex_pattern(self, pattern: str, test_cases: List[RegexTestCase], 
                          flags: int = 0) -> Tuple[List[RegexTestResult], RegexAnalysis]:
        """测试正则表达式模式"""
        results = []
        
        try:
            # 编译正则表达式
            compiled_pattern = re.compile(pattern, flags)
            
            # 分析正则表达式
            analysis = self._analyze_regex(pattern, flags)
            
            # 运行测试用例
            for test_case in test_cases:
                result = self._run_single_test(compiled_pattern, test_case)
                results.append(result)
            
        except re.error as e:
            # 正则表达式编译错误
            analysis = RegexAnalysis(
                pattern=pattern,
                flags=self._flags_to_list(flags),
                complexity="unknown",
                performance_score=0,
                potential_issues=[f"编译错误: {str(e)}"],
                optimization_suggestions=[]
            )
            
            # 为所有测试用例创建错误结果
            for test_case in test_cases:
                results.append(RegexTestResult(
                    test_case=test_case,
                    result=TestResult.ERROR,
                    actual_matches=[],
                    actual_groups=[],
                    execution_time=0.0,
                    error_message=str(e)
                ))
        
        return results, analysis
    
    def _run_single_test(self, compiled_pattern: Pattern, test_case: RegexTestCase) -> RegexTestResult:
        """运行单个测试用例"""
        start_time = time.time()
        
        try:
            # 执行匹配
            matches = list(compiled_pattern.finditer(test_case.input_text))
            
            # 提取匹配结果
            actual_matches = [match.group(0) for match in matches]
            actual_groups = []
            
            for match in matches:
                groups = {}
                for i, group in enumerate(match.groups()):
                    groups[f"group_{i+1}"] = group
                for name, group in match.groupdict().items():
                    groups[name] = group
                
                if groups:
                    actual_groups.append(groups)
            
            execution_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 验证结果
            if test_case.should_match:
                if not actual_matches:
                    result = TestResult.FAIL
                    error_message = "期望匹配但未匹配到任何内容"
                elif self._compare_matches(actual_matches, test_case.expected_matches):
                    result = TestResult.PASS
                    error_message = ""
                else:
                    result = TestResult.FAIL
                    error_message = f"匹配结果不匹配。期望: {test_case.expected_matches}，实际: {actual_matches}"
            else:
                if actual_matches:
                    result = TestResult.FAIL
                    error_message = f"期望不匹配但匹配到: {actual_matches}"
                else:
                    result = TestResult.PASS
                    error_message = ""
            
            return RegexTestResult(
                test_case=test_case,
                result=result,
                actual_matches=actual_matches,
                actual_groups=actual_groups,
                execution_time=execution_time,
                error_message=error_message
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return RegexTestResult(
                test_case=test_case,
                result=TestResult.ERROR,
                actual_matches=[],
                actual_groups=[],
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _compare_matches(self, actual: List[str], expected: List[str]) -> bool:
        """比较匹配结果"""
        if len(actual) != len(expected):
            return False
        
        return all(a == b for a, b in zip(actual, expected))
    
    def _analyze_regex(self, pattern: str, flags: int) -> RegexAnalysis:
        """分析正则表达式"""
        potential_issues = []
        optimization_suggestions = []
        
        # 检查复杂度
        complexity = self._calculate_complexity(pattern)
        
        # 检查潜在问题
        issues = self._check_potential_issues(pattern)
        potential_issues.extend(issues)
        
        # 生成优化建议
        suggestions = self._generate_optimization_suggestions(pattern, issues)
        optimization_suggestions.extend(suggestions)
        
        # 计算性能评分
        performance_score = self._calculate_performance_score(pattern, complexity, issues)
        
        return RegexAnalysis(
            pattern=pattern,
            flags=self._flags_to_list(flags),
            complexity=complexity,
            performance_score=performance_score,
            potential_issues=potential_issues,
            optimization_suggestions=optimization_suggestions
        )
    
    def _calculate_complexity(self, pattern: str) -> str:
        """计算正则表达式复杂度"""
        score = 0
        
        # 基本元素计分
        score += len(re.findall(r'\.', pattern)) * 1  # 点号
        score += len(re.findall(r'\*', pattern)) * 2  # 星号
        score += len(re.findall(r'\+', pattern)) * 2  # 加号
        score += len(re.findall(r'\?', pattern)) * 1  # 问号
        score += len(re.findall(r'\{', pattern)) * 3  # 量词
        score += len(re.findall(r'\(', pattern)) * 2  # 分组
        score += len(re.findall(r'\[', pattern)) * 2  # 字符类
        
        # 复杂结构计分
        score += len(re.findall(r'\(\?\!', pattern)) * 5  # 负向前瞻
        score += len(re.findall(r'\(\?\=', pattern)) * 5  # 正向前瞻
        score += len(re.findall(r'\(\?\<', pattern)) * 5  # 后瞻
        score += len(re.findall(r'\(\?\>', pattern)) * 4  # 原子分组
        
        if score < 10:
            return "low"
        elif score < 25:
            return "medium"
        elif score < 50:
            return "high"
        else:
            return "very_high"
    
    def _check_potential_issues(self, pattern: str) -> List[str]:
        """检查潜在问题"""
        issues = []
        
        # 检查嵌套量词
        if re.search(r'(\*|\+|\?|\{[\d,]+\})\s*(\*|\+|\?|\{[\d,]+\})', pattern):
            issues.append("存在嵌套量词，可能导致回溯灾难")
        
        # 检查过度回溯
        if re.search(r'\.\*\.\*', pattern) or re.search(r'\.\+\.\+', pattern):
            issues.append("存在过度回溯风险，建议使用更精确的模式")
        
        # 检查贪婪量词
        if re.search(r'\.\*[^\?]', pattern) or re.search(r'\.\+[^\?]', pattern):
            issues.append("使用了贪婪量词，可能导致过度匹配")
        
        # 检查未转义的特殊字符
        special_chars = r'.^$*+?{}[]\|()'
        for char in special_chars:
            if pattern.count(char) > pattern.count(f'\\{char}'):
                issues.append(f"字符 '{char}' 可能需要转义")
        
        # 检查Unicode处理
        if not re.search(r'/[gimsuy]*u', pattern) and re.search(r'[\u4e00-\u9fff]', pattern):
            issues.append("包含非ASCII字符但未启用Unicode标志")
        
        return issues
    
    def _generate_optimization_suggestions(self, pattern: str, issues: List[str]) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 基于问题生成建议
        for issue in issues:
            if "嵌套量词" in issue:
                suggestions.append("考虑使用原子分组 (?>) 或重新设计模式避免嵌套")
            elif "回溯" in issue:
                suggestions.append("使用更精确的字符类替代 .* 或 .+")
            elif "贪婪量词" in issue:
                suggestions.append("考虑使用非贪婪量词 (*? +? ??) 或原子分组")
            elif "转义" in issue:
                suggestions.append("检查特殊字符是否正确转义")
            elif "Unicode" in issue:
                suggestions.append("添加Unicode标志 (u) 或使用Unicode属性类")
        
        # 通用优化建议
        if len(pattern) > 100:
            suggestions.append("考虑将复杂模式拆分为多个简单模式")
        
        if pattern.count('(') > 10:
            suggestions.append("考虑使用非捕获分组 (?:) 减少内存使用")
        
        if re.search(r'\[\^.\]', pattern):
            suggestions.append("考虑使用具体的否定字符类替代 [^.]")
        
        return suggestions
    
    def _calculate_performance_score(self, pattern: str, complexity: str, issues: List[str]) -> int:
        """计算性能评分"""
        base_score = 100
        
        # 复杂度扣分
        complexity_penalty = {
            "low": 0,
            "medium": 10,
            "high": 25,
            "very_high": 40
        }
        base_score -= complexity_penalty.get(complexity, 0)
        
        # 问题扣分
        for issue in issues:
            if "回溯灾难" in issue:
                base_score -= 30
            elif "过度回溯" in issue:
                base_score -= 20
            elif "贪婪量词" in issue:
                base_score -= 10
            elif "嵌套量词" in issue:
                base_score -= 25
            else:
                base_score -= 5
        
        return max(0, base_score)
    
    def _flags_to_list(self, flags: int) -> List[str]:
        """将标志转换为列表"""
        flag_map = {
            re.IGNORECASE: "i",
            re.MULTILINE: "m",
            re.DOTALL: "s",
            re.VERBOSE: "x",
            re.ASCII: "a",
            re.LOCALE: "l"
        }
        
        return [flag_map[flag] for flag in flag_map if flags & flag]
    
    def _initialize_complexity_rules(self) -> Dict[str, Any]:
        """初始化复杂度规则"""
        return {
            "simple_patterns": [r'\d', r'\w', r'\s'],
            "moderate_patterns": [r'[a-zA-Z]', r'[0-9]+'],
            "complex_patterns": [r'(?!...)', r'(?<=...)'],
            "very_complex_patterns": [r'(.*)+\1', r'(?>(.*))+']
        }
    
    def generate_test_report(self, results: List[RegexTestResult], analysis: RegexAnalysis) -> str:
        """生成测试报告"""
        report = ["=== 正则表达式测试报告 ===\n"]
        
        # 基本信息
        report.append(f"模式: {analysis.pattern}")
        report.append(f"标志: {', '.join(analysis.flags)}")
        report.append(f"复杂度: {analysis.complexity}")
        report.append(f"性能评分: {analysis.performance_score}/100\n")
        
        # 测试结果统计
        total_tests = len(results)
        passed_tests = len([r for r in results if r.result == TestResult.PASS])
        failed_tests = len([r for r in results if r.result == TestResult.FAIL])
        error_tests = len([r for r in results if r.result == TestResult.ERROR])
        
        report.append("=== 测试结果统计 ===")
        report.append(f"总测试数: {total_tests}")
        report.append(f"通过: {passed_tests}")
        report.append(f"失败: {failed_tests}")
        report.append(f"错误: {error_tests}")
        report.append(f"成功率: {passed_tests/total_tests*100:.1f}%\n")
        
        # 详细测试结果
        report.append("=== 详细测试结果 ===")
        for result in results:
            status_icon = {
                TestResult.PASS: "✅",
                TestResult.FAIL: "❌",
                TestResult.ERROR: "💥",
                TestResult.TIMEOUT: "⏰"
            }.get(result.result, "❓")
            
            report.append(f"{status_icon} {result.test_case.name}")
            report.append(f"   描述: {result.test_case.description}")
            report.append(f"   输入: {repr(result.test_case.input_text)}")
            report.append(f"   期望: {result.test_case.expected_matches}")
            report.append(f"   实际: {result.actual_matches}")
            report.append(f"   执行时间: {result.execution_time:.2f}ms")
            
            if result.error_message:
                report.append(f"   错误: {result.error_message}")
            
            report.append("")
        
        # 分析结果
        report.append("=== 正则表达式分析 ===")
        
        if analysis.potential_issues:
            report.append("潜在问题:")
            for issue in analysis.potential_issues:
                report.append(f"  - {issue}")
            report.append("")
        
        if analysis.optimization_suggestions:
            report.append("优化建议:")
            for suggestion in analysis.optimization_suggestions:
                report.append(f"  - {suggestion}")
            report.append("")
        
        # 性能分析
        avg_time = sum(r.execution_time for r in results) / len(results) if results else 0
        report.append(f"平均执行时间: {avg_time:.2f}ms")
        
        if avg_time > self.performance_threshold:
            report.append("⚠️ 性能警告: 执行时间超过阈值")
        else:
            report.append("✅ 性能良好")
        
        return '\n'.join(report)

# 使用示例
def main():
    tester = RegexTester()
    
    # 测试用例
    test_cases = [
        RegexTestCase(
            name="邮箱验证",
            input_text="user@example.com",
            expected_matches=["user@example.com"],
            should_match=True,
            description="验证标准邮箱格式"
        ),
        RegexTestCase(
            name="无效邮箱",
            input_text="invalid-email",
            expected_matches=[],
            should_match=False,
            description="测试无效邮箱格式"
        ),
        RegexTestCase(
            name="多个邮箱",
            input_text="a@b.com c@d.net",
            expected_matches=["a@b.com", "c@d.net"],
            should_match=True,
            description="测试多个邮箱匹配"
        )
    ]
    
    # 测试正则表达式
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    results, analysis = tester.test_regex_pattern(pattern, test_cases)
    
    # 生成报告
    report = tester.generate_test_report(results, analysis)
    print(report)

if __name__ == "__main__":
    main()
```

### 正则表达式优化器
```python
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class OptimizationResult:
    """优化结果"""
    original_pattern: str
    optimized_pattern: str
    improvement_type: str
    performance_gain: str
    explanation: str

class RegexOptimizer:
    """正则表达式优化器"""
    
    def __init__(self):
        self.optimization_rules = self._initialize_optimization_rules()
    
    def optimize_pattern(self, pattern: str) -> List[OptimizationResult]:
        """优化正则表达式模式"""
        results = []
        current_pattern = pattern
        
        # 应用优化规则
        for rule_name, rule_func in self.optimization_rules.items():
            optimized_pattern = rule_func(current_pattern)
            if optimized_pattern != current_pattern:
                results.append(OptimizationResult(
                    original_pattern=current_pattern,
                    optimized_pattern=optimized_pattern,
                    improvement_type=rule_name,
                    performance_gain=self._estimate_performance_gain(current_pattern, optimized_pattern),
                    explanation=self._get_explanation(rule_name)
                ))
                current_pattern = optimized_pattern
        
        return results
    
    def _initialize_optimization_rules(self) -> Dict[str, Any]:
        """初始化优化规则"""
        return {
            "avoid_catastrophic_backtracking": self._optimize_catastrophic_backtracking,
            "use_character_classes": self._optimize_character_classes,
            "use_atomic_grouping": self._optimize_atomic_grouping,
            "use_possessive_quantifiers": self._optimize_possessive_quantifiers,
            "avoid_capturing_groups": self._optimize_capturing_groups,
            "use_anchors": self._optimize_anchors,
            "simplify_alternations": self._optimize_alternations
        }
    
    def _optimize_catastrophic_backtracking(self, pattern: str) -> str:
        """优化回溯灾难"""
        # 将 (.*)+ 替换为 (?>.*)
        pattern = re.sub(r'\(\.\*\)\+', '(?>.*)', pattern)
        
        # 将 (.*)* 替换为 .*
        pattern = re.sub(r'\(\.\*\)\*', '.*', pattern)
        
        # 将 (a+)* 替换为 a*
        pattern = re.sub(r'\(([^)]+)\)\*\*', r'\1*', pattern)
        
        return pattern
    
    def _optimize_character_classes(self, pattern: str) -> str:
        """优化字符类"""
        # 将 [0-9] 替换为 \d
        pattern = re.sub(r'\[0-9\]', r'\d', pattern)
        
        # 将 [a-zA-Z0-9_] 替换为 \w
        pattern = re.sub(r'\[a-zA-Z0-9_\]', r'\w', pattern)
        
        # 将 [ \t\r\n\f\v] 替换为 \s
        pattern = re.sub(r'\[ \t\r\n\f\v\]', r'\s', pattern)
        
        # 将 [a-zA-Z] 替换为 [[:alpha:]] (在某些引擎中)
        # 这里保持原样，因为兼容性考虑
        
        return pattern
    
    def _optimize_atomic_grouping(self, pattern: str) -> str:
        """优化原子分组"""
        # 在适当的地方使用原子分组
        # 这是一个简化的实现，实际情况需要更复杂的分析
        
        # 将 (.*)(?=end) 替换为 (?>.*)(?=end)
        pattern = re.sub(r'\(\.\*\)(?=\))', '(?>.*)', pattern)
        
        return pattern
    
    def _optimize_possessive_quantifiers(self, str):
        """优化占有量词"""
        # 在支持占有量词的引擎中使用它们
        # 将 .*+ 替换为 .*+ (如果引擎支持)
        
        # 这里只是示例，实际需要检查引擎支持
        return pattern
    
    def _optimize_capturing_groups(self, pattern: str) -> str:
        """优化捕获分组"""
        # 将不必要的捕获分组改为非捕获分组
        # 简化版本：将 (?:...) 之外的分组改为非捕获
        
        # 这个优化需要更复杂的分析来确定哪些分组是必要的
        # 这里只是一个简单的示例
        
        return pattern
    
    def _optimize_anchors(self, pattern: str) -> str:
        """优化锚点"""
        # 添加适当的锚点来提高匹配效率
        
        # 如果模式以 .* 开始，考虑使用 ^
        if pattern.startswith('.*') and not pattern.startswith('^'):
            pattern = '^' + pattern
        
        # 如果模式以 .* 结束，考虑使用 $
        if pattern.endswith('.*') and not pattern.endswith('$'):
            pattern = pattern + '$'
        
        return pattern
    
    def _optimize_alternations(self, pattern: str) -> str:
        """优化选择分支"""
        # 重新排列选择分支，将更常见的放在前面
        # 这需要统计信息，这里只是示例
        
        return pattern
    
    def _estimate_performance_gain(self, original: str, optimized: str) -> str:
        """估算性能提升"""
        # 简化的性能估算
        original_score = len(original)
        optimized_score = len(optimized)
        
        if optimized_score < original_score:
            improvement = (original_score - optimized_score) / original_score * 100
            return f"约 {improvement:.1f}% 的性能提升"
        else:
            return "无明显性能提升"
    
    def _get_explanation(self, rule_name: str) -> str:
        """获取优化解释"""
        explanations = {
            "avoid_catastrophic_backtracking": "避免回溯灾难，防止指数级时间复杂度",
            "use_character_classes": "使用预定义字符类提高可读性和性能",
            "use_atomic_grouping": "使用原子分组减少回溯",
            "use_possessive_quantifiers": "使用占有量词提高匹配效率",
            "avoid_capturing_groups": "避免不必要的捕获分组减少内存使用",
            "use_anchors": "使用锚点提高匹配效率",
            "simplify_alternations": "优化选择分支顺序提高匹配效率"
        }
        
        return explanations.get(rule_name, "优化正则表达式模式")

# 使用示例
def main():
    optimizer = RegexOptimizer()
    
    # 需要优化的模式
    pattern = r'(.*)(?=end)'
    
    # 优化模式
    results = optimizer.optimize_pattern(pattern)
    
    print("=== 正则表达式优化报告 ===")
    print(f"原始模式: {pattern}")
    print()
    
    for result in results:
        print(f"优化类型: {result.improvement_type}")
        print(f"优化后: {result.optimized_pattern}")
        print(f"性能提升: {result.performance_gain}")
        print(f"说明: {result.explanation}")
        print()

if __name__ == "__main__":
    main()
```

## 正则表达式最佳实践

### 编写原则
1. **简单优先**: 使用最简单的模式完成任务
2. **明确意图**: 使用有意义的模式结构
3. **测试充分**: 覆盖所有边界情况
4. **性能考虑**: 避免回溯灾难

### 调试技巧
1. **逐步构建**: 从简单模式开始逐步增加复杂度
2. **可视化工具**: 使用正则表达式可视化工具
3. **测试用例**: 创建全面的测试用例集
4. **性能分析**: 监控匹配性能

### 常见模式
1. **邮箱验证**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
2. **URL匹配**: `^https?://[^\s/$.?#].[^\s]*$`
3. **IP地址**: `^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$`
4. **手机号**: `^1[3-9]\d{9}$`

## 相关技能

- **string-analyzer** - 字符串分析
- **pattern-matcher** - 模式匹配
- **text-processor** - 文本处理
- **data-validator** - 数据验证
