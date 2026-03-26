# 重构模式参考文档

## 重构模式概述

### 什么是重构
重构是在不改变代码外部行为的前提下，通过改善代码内部结构来提高代码质量的过程。重构的目的是使代码更容易理解、修改和维护，同时消除代码异味，改善设计，提高开发效率。

### 重构价值
- **提高代码质量**: 改善代码结构、可读性和可维护性
- **降低维护成本**: 减少代码复杂度，简化维护工作
- **提升开发效率**: 更好的代码结构加速新功能开发
- **减少技术债务**: 消除代码异味，改善系统设计
- **增强团队协作**: 统一的代码风格和结构

### 重构原则
- **小步重构**: 每次重构只做小的改动
- **频繁测试**: 每次重构后都要运行测试
- **保持功能**: 重构不能改变外部行为
- **渐进式**: 逐步改善，避免大规模改动
- **有目的**: 每次重构都有明确的目标

## 重构模式核心实现

### 代码分析引擎
```python
# refactoring_patterns.py
import ast
import os
import re
import json
import time
import logging
import difflib
import subprocess
from typing import Dict, List, Any, Optional, Union, Callable, Type, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
import git

class RefactoringType(Enum):
    """重构类型枚举"""
    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    INLINE_METHOD = "inline_method"
    MOVE_METHOD = "move_method"
    RENAME = "rename"
    INTRODUCE_PARAMETER = "introduce_parameter"
    REMOVE_PARAMETER = "remove_parameter"

class CodeSmellType(Enum):
    """代码异味类型枚举"""
    LONG_METHOD = "long_method"
    LARGE_CLASS = "large_class"
    LONG_PARAMETER_LIST = "long_parameter_list"
    DUPLICATE_CODE = "duplicate_code"
    FEATURE_ENVY = "feature_envy"
    DATA_CLUMPS = "data_clumps"
    PRIMITIVE_OBSSESSION = "primitive_obsession"
    SWITCH_STATEMENT = "switch_statement"

@dataclass
class CodeSmell:
    """代码异味"""
    smell_type: CodeSmellType
    file_path: str
    line_number: int
    description: str
    severity: str  # low, medium, high, critical
    suggestion: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RefactoringOpportunity:
    """重构机会"""
    refactoring_type: RefactoringType
    file_path: str
    line_number: int
    description: str
    confidence: float  # 0.0 - 1.0
    effort: str  # low, medium, high
    benefit: str  # low, medium, high
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RefactoringPlan:
    """重构计划"""
    project_name: str
    opportunities: List[RefactoringOpportunity]
    code_smells: List[CodeSmell]
    priority_order: List[int]  # opportunities的索引顺序
    estimated_effort: str
    estimated_benefit: str
    risks: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

class CodeAnalyzer:
    """代码分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.code_smells = []
        self.refactoring_opportunities = []
        self.metrics = {}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 分析代码异味
            file_smells = self._detect_code_smells(tree, file_path, content)
            self.code_smells.extend(file_smells)
            
            # 分析重构机会
            file_opportunities = self._detect_refactoring_opportunities(tree, file_path, content)
            self.refactoring_opportunities.extend(file_opportunities)
            
            # 计算代码指标
            file_metrics = self._calculate_metrics(tree, content)
            
            return {
                'file_path': file_path,
                'code_smells': file_smells,
                'refactoring_opportunities': file_opportunities,
                'metrics': file_metrics
            }
        
        except Exception as e:
            self.logger.error(f"分析文件失败 {file_path}: {e}")
            return {}
    
    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """分析目录中的所有Python文件"""
        all_results = {}
        
        for root, dirs, files in os.walk(directory_path):
            # 跳过__pycache__目录
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    result = self.analyze_file(file_path)
                    if result:
                        all_results[file_path] = result
        
        return all_results
    
    def _detect_code_smells(self, tree: ast.AST, file_path: str, content: str) -> List[CodeSmell]:
        """检测代码异味"""
        smells = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检测长方法
                smell = self._detect_long_method(node, file_path, lines)
                if smell:
                    smells.append(smell)
                
                # 检测长参数列表
                smell = self._detect_long_parameter_list(node, file_path)
                if smell:
                    smells.append(smell)
                
                # 检测重复代码
                smells.extend(self._detect_duplicate_code(node, file_path, content))
            
            elif isinstance(node, ast.ClassDef):
                # 检测大类
                smell = self._detect_large_class(node, file_path, lines)
                if smell:
                    smells.append(smell)
        
        return smells
    
    def _detect_long_method(self, node: ast.FunctionDef, file_path: str, lines: List[str]) -> Optional[CodeSmell]:
        """检测长方法"""
        if node.end_lineno and node.lineno:
            method_lines = node.end_lineno - node.lineno + 1
            
            if method_lines > 20:  # 超过20行认为是长方法
                severity = "critical" if method_lines > 50 else "high" if method_lines > 30 else "medium"
                
                return CodeSmell(
                    smell_type=CodeSmellType.LONG_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    description=f"方法 '{node.name}' 过长 ({method_lines} 行)",
                    severity=severity,
                    suggestion=f"考虑将方法 '{node.name}' 拆分为多个小方法",
                    metadata={'method_name': node.name, 'line_count': method_lines}
                )
        
        return None
    
    def _detect_long_parameter_list(self, node: ast.FunctionDef, file_path: str) -> Optional[CodeSmell]:
        """检测长参数列表"""
        param_count = len(node.args.args)
        
        if param_count > 5:  # 超过5个参数认为是长参数列表
            severity = "critical" if param_count > 8 else "high" if param_count > 6 else "medium"
            
            return CodeSmell(
                smell_type=CodeSmellType.LONG_PARAMETER_LIST,
                file_path=file_path,
                line_number=node.lineno,
                description=f"方法 '{node.name}' 参数过多 ({param_count} 个)",
                severity=severity,
                suggestion=f"考虑将参数封装为对象或使用参数对象模式",
                metadata={'method_name': node.name, 'parameter_count': param_count}
            )
        
        return None
    
    def _detect_large_class(self, node: ast.ClassDef, file_path: str, lines: List[str]) -> Optional[CodeSmell]:
        """检测大类"""
        if node.end_lineno and node.lineno:
            class_lines = node.end_lineno - node.lineno + 1
            method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
            
            if class_lines > 100 or method_count > 15:  # 超过100行或15个方法
                severity = "critical" if class_lines > 200 or method_count > 25 else "high"
                
                return CodeSmell(
                    smell_type=CodeSmellType.LARGE_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    description=f"类 '{node.name}' 过大 ({class_lines} 行, {method_count} 个方法)",
                    severity=severity,
                    suggestion=f"考虑将类 '{node.name}' 拆分为多个职责单一的类",
                    metadata={'class_name': node.name, 'line_count': class_lines, 'method_count': method_count}
                )
        
        return None
    
    def _detect_duplicate_code(self, node: ast.FunctionDef, file_path: str, content: str) -> List[CodeSmell]:
        """检测重复代码"""
        smells = []
        
        # 简单的重复代码检测：检查相似的代码块
        if node.body and len(node.body) > 3:
            # 提取方法体的字符串表示
            method_body_lines = []
            for stmt in node.body:
                if hasattr(stmt, 'lineno') and hasattr(stmt, 'end_lineno'):
                    method_body_lines.extend(content.split('\n')[stmt.lineno-1:stmt.end_lineno])
            
            if method_body_lines:
                method_body = '\n'.join(method_body_lines)
                
                # 在整个文件中搜索相似的代码块
                similar_blocks = self._find_similar_code_blocks(method_body, content, node.lineno)
                
                for similarity, start_line in similar_blocks:
                    if similarity > 0.8:  # 相似度超过80%
                        smells.append(CodeSmell(
                            smell_type=CodeSmellType.DUPLICATE_CODE,
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"方法 '{node.name}' 存在重复代码 (相似度: {similarity:.2f})",
                            severity="medium",
                            suggestion=f"考虑提取公共方法或使用模板方法模式",
                            metadata={'method_name': node.name, 'similarity': similarity, 'similar_line': start_line}
                        ))
        
        return smells
    
    def _find_similar_code_blocks(self, target_block: str, content: str, exclude_line: int) -> List[Tuple[float, int]]:
        """查找相似的代码块"""
        similar_blocks = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if i + 1 == exclude_line:  # 跳过目标代码块所在的行
                continue
            
            # 简单的相似度检测
            similarity = difflib.SequenceMatcher(None, target_block, line).ratio()
            if similarity > 0.5:
                similar_blocks.append((similarity, i + 1))
        
        # 按相似度排序
        similar_blocks.sort(key=lambda x: x[0], reverse=True)
        
        return similar_blocks[:5]  # 返回前5个最相似的代码块
    
    def _detect_refactoring_opportunities(self, tree: ast.AST, file_path: str, content: str) -> List[RefactoringOpportunity]:
        """检测重构机会"""
        opportunities = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检测提取方法的机会
                opportunity = self._detect_extract_method_opportunity(node, file_path, content)
                if opportunity:
                    opportunities.append(opportunity)
                
                # 检测内联方法的机会
                opportunity = self._detect_inline_method_opportunity(node, file_path, content)
                if opportunity:
                    opportunities.append(opportunity)
            
            elif isinstance(node, ast.ClassDef):
                # 检测提取类的机会
                opportunity = self._detect_extract_class_opportunity(node, file_path, content)
                if opportunity:
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_extract_method_opportunity(self, node: ast.FunctionDef, file_path: str, content: str) -> Optional[RefactoringOpportunity]:
        """检测提取方法的机会"""
        if node.end_lineno and node.lineno:
            method_lines = node.end_lineno - node.lineno + 1
            
            # 长方法有机会提取
            if method_lines > 15:
                confidence = min(0.9, method_lines / 50.0)
                effort = "high" if method_lines > 30 else "medium"
                benefit = "high" if method_lines > 25 else "medium"
                
                return RefactoringOpportunity(
                    refactoring_type=RefactoringType.EXTRACT_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    description=f"方法 '{node.name}' 可以提取为多个小方法",
                    confidence=confidence,
                    effort=effort,
                    benefit=benefit,
                    metadata={'method_name': node.name, 'line_count': method_lines}
                )
        
        return None
    
    def _detect_inline_method_opportunity(self, node: ast.FunctionDef, file_path: str, content: str) -> Optional[RefactoringOpportunity]:
        """检测内联方法的机会"""
        if node.end_lineno and node.lineno:
            method_lines = node.end_lineno - node.lineno + 1
            
            # 简单方法有机会内联
            if method_lines <= 3 and len(node.args.args) <= 2:
                confidence = 0.7
                effort = "low"
                benefit = "low"
                
                return RefactoringOpportunity(
                    refactoring_type=RefactoringType.INLINE_METHOD,
                    file_path=file_path,
                    line_number=node.lineno,
                    description=f"简单方法 '{node.name}' 可以内联",
                    confidence=confidence,
                    effort=effort,
                    benefit=benefit,
                    metadata={'method_name': node.name, 'line_count': method_lines}
                )
        
        return None
    
    def _detect_extract_class_opportunity(self, node: ast.ClassDef, file_path: str, content: str) -> Optional[RefactoringOpportunity]:
        """检测提取类的机会"""
        if node.end_lineno and node.lineno:
            class_lines = node.end_lineno - node.lineno + 1
            method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
            
            # 大类有机会拆分
            if class_lines > 80 or method_count > 12:
                confidence = min(0.9, (class_lines / 200.0 + method_count / 30.0) / 2.0)
                effort = "high" if class_lines > 150 or method_count > 20 else "medium"
                benefit = "high" if class_lines > 100 or method_count > 15 else "medium"
                
                return RefactoringOpportunity(
                    refactoring_type=RefactoringType.EXTRACT_CLASS,
                    file_path=file_path,
                    line_number=node.lineno,
                    description=f"大类 '{node.name}' 可以拆分为多个小类",
                    confidence=confidence,
                    effort=effort,
                    benefit=benefit,
                    metadata={'class_name': node.name, 'line_count': class_lines, 'method_count': method_count}
                )
        
        return None
    
    def _calculate_metrics(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """计算代码指标"""
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        blank_lines = total_lines - code_lines - comment_lines
        
        # 计算复杂度指标
        complexity = self._calculate_cyclomatic_complexity(tree)
        
        # 统计类和方法数量
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'comment_ratio': comment_lines / code_lines if code_lines > 0 else 0,
            'cyclomatic_complexity': complexity,
            'class_count': len(classes),
            'function_count': len(functions),
            'avg_function_length': code_lines / len(functions) if functions else 0
        }
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity

class RefactoringEngine:
    """重构引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.refactoring_history = []
    
    def apply_refactoring(self, file_path: str, refactoring_type: RefactoringType, 
                         line_number: int, **kwargs) -> Dict[str, Any]:
        """应用重构"""
        try:
            # 读取原文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 解析AST
            tree = ast.parse(original_content)
            
            # 根据重构类型执行相应的重构操作
            if refactoring_type == RefactoringType.EXTRACT_METHOD:
                new_content = self._extract_method(original_content, tree, line_number, **kwargs)
            elif refactoring_type == RefactoringType.INLINE_METHOD:
                new_content = self._inline_method(original_content, tree, line_number, **kwargs)
            elif refactoring_type == RefactoringType.EXTRACT_CLASS:
                new_content = self._extract_class(original_content, tree, line_number, **kwargs)
            elif refactoring_type == RefactoringType.RENAME:
                new_content = self._rename(original_content, tree, line_number, **kwargs)
            else:
                raise ValueError(f"不支持的重构类型: {refactoring_type}")
            
            # 备份原文件
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # 写入新内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # 记录重构历史
            refactoring_record = {
                'timestamp': time.time(),
                'file_path': file_path,
                'refactoring_type': refactoring_type.value,
                'line_number': line_number,
                'backup_path': backup_path,
                'kwargs': kwargs
            }
            self.refactoring_history.append(refactoring_record)
            
            self.logger.info(f"成功应用重构 {refactoring_type.value} 到 {file_path}:{line_number}")
            
            return {
                'success': True,
                'backup_path': backup_path,
                'changes': self._calculate_changes(original_content, new_content)
            }
        
        except Exception as e:
            self.logger.error(f"重构失败 {file_path}:{line_number}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_method(self, content: str, tree: ast.AST, line_number: int, **kwargs) -> str:
        """提取方法"""
        # 这里是简化的实现，实际需要更复杂的AST操作
        lines = content.split('\n')
        
        # 找到目标方法
        target_method = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.lineno == line_number:
                target_method = node
                break
        
        if not target_method:
            raise ValueError(f"在行 {line_number} 未找到方法")
        
        # 简单的提取方法示例：将方法的前几行提取为新方法
        if target_method.body and len(target_method.body) > 5:
            # 提取前3行作为新方法
            extract_lines = []
            for i in range(min(3, len(target_method.body))):
                stmt = target_method.body[i]
                if hasattr(stmt, 'lineno') and hasattr(stmt, 'end_lineno'):
                    extract_lines.extend(lines[stmt.lineno-1:stmt.end_lineno])
            
            # 生成新方法名
            new_method_name = f"extracted_{target_method.name}"
            
            # 构建新方法
            new_method = f"    def {new_method_name}(self):\n"
            for line in extract_lines:
                new_method += f"        {line}\n"
            
            # 在原方法中替换提取的代码
            new_lines = lines.copy()
            insert_pos = target_method.lineno  # 在原方法开始处插入新方法
            
            # 插入新方法
            new_lines.insert(insert_pos - 1, new_method)
            
            # 在原方法中添加对新方法的调用
            call_line = f"        self.{new_method_name}()"
            new_lines.insert(target_method.lineno + 3, call_line)
            
            return '\n'.join(new_lines)
        
        return content
    
    def _inline_method(self, content: str, tree: ast.AST, line_number: int, **kwargs) -> str:
        """内联方法"""
        # 简化的内联方法实现
        lines = content.split('\n')
        
        # 找到目标方法
        target_method = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.lineno == line_number:
                target_method = node
                break
        
        if not target_method:
            raise ValueError(f"在行 {line_number} 未找到方法")
        
        # 简单的内联：如果方法只有一行，直接替换调用
        if len(target_method.body) == 1:
            method_body = lines[target_method.lineno]
            
            # 查找方法调用并替换
            new_lines = []
            for line in lines:
                if f"{target_method.name}(" in line:
                    # 简单替换为方法体
                    new_lines.append(method_body.replace('return ', '').strip())
                else:
                    new_lines.append(line)
            
            return '\n'.join(new_lines)
        
        return content
    
    def _extract_class(self, content: str, tree: ast.AST, line_number: int, **kwargs) -> str:
        """提取类"""
        # 简化的提取类实现
        lines = content.split('\n')
        
        # 找到目标类
        target_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.lineno == line_number:
                target_class = node
                break
        
        if not target_class:
            raise ValueError(f"在行 {line_number} 未找到类")
        
        # 简单的类提取：将类的一部分方法提取到新类
        methods = [n for n in target_class.body if isinstance(n, ast.FunctionDef)]
        
        if len(methods) > 5:
            # 提取后3个方法到新类
            extract_methods = methods[-3:]
            new_class_name = f"Extracted{target_class.name}"
            
            # 构建新类
            new_class = f"\nclass {new_class_name}:\n"
            for method in extract_methods:
                method_lines = lines[method.lineno-1:method.end_lineno]
                for line in method_lines:
                    new_class += f"    {line}\n"
            
            # 从原类中移除提取的方法
            new_lines = []
            skip_lines = set()
            for method in extract_methods:
                skip_lines.update(range(method.lineno-1, method.end_lineno))
            
            for i, line in enumerate(lines):
                if i not in skip_lines:
                    new_lines.append(line)
            
            # 在文件末尾添加新类
            new_lines.append(new_class)
            
            return '\n'.join(new_lines)
        
        return content
    
    def _rename(self, content: str, tree: ast.AST, line_number: int, **kwargs) -> str:
        """重命名"""
        old_name = kwargs.get('old_name')
        new_name = kwargs.get('new_name')
        
        if not old_name or not new_name:
            raise ValueError("重命名需要提供 old_name 和 new_name 参数")
        
        # 简单的重命名：替换所有出现的名称
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # 简单的字符串替换（实际需要更精确的AST操作）
            new_line = line.replace(old_name, new_name)
            new_lines.append(new_line)
        
        return '\n'.join(new_lines)
    
    def _calculate_changes(self, original: str, modified: str) -> Dict[str, Any]:
        """计算变更统计"""
        original_lines = original.split('\n')
        modified_lines = modified.split('\n')
        
        diff = list(difflib.unified_diff(original_lines, modified_lines, lineterm=''))
        
        added_lines = 0
        removed_lines = 0
        
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                added_lines += 1
            elif line.startswith('-') and not line.startswith('---'):
                removed_lines += 1
        
        return {
            'added_lines': added_lines,
            'removed_lines': removed_lines,
            'total_changes': added_lines + removed_lines,
            'diff_lines': diff
        }

class RefactoringPlanner:
    """重构规划器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_refactoring_plan(self, project_name: str, 
                               opportunities: List[RefactoringOpportunity],
                               code_smells: List[CodeSmell]) -> RefactoringPlan:
        """创建重构计划"""
        # 按优先级排序重构机会
        prioritized_opportunities = self._prioritize_opportunities(opportunities, code_smells)
        
        # 估算总体工作量和收益
        total_effort = self._estimate_total_effort(prioritized_opportunities)
        total_benefit = self._estimate_total_benefit(prioritized_opportunities)
        
        # 识别风险
        risks = self._identify_risks(prioritized_opportunities, code_smells)
        
        return RefactoringPlan(
            project_name=project_name,
            opportunities=prioritized_opportunities,
            code_smells=code_smells,
            priority_order=list(range(len(prioritized_opportunities))),
            estimated_effort=total_effort,
            estimated_benefit=total_benefit,
            risks=risks,
            metadata={
                'created_at': time.time(),
                'opportunity_count': len(opportunities),
                'smell_count': len(code_smells)
            }
        )
    
    def _prioritize_opportunities(self, opportunities: List[RefactoringOpportunity], 
                                code_smells: List[CodeSmell]) -> List[RefactoringOpportunity]:
        """按优先级排序重构机会"""
        # 计算每个机会的优先级分数
        scored_opportunities = []
        
        for opportunity in opportunities:
            score = 0
            
            # 基于置信度
            score += opportunity.confidence * 30
            
            # 基于收益
            benefit_scores = {'low': 10, 'medium': 20, 'high': 30}
            score += benefit_scores.get(opportunity.benefit, 0)
            
            # 基于工作量（工作量越低优先级越高）
            effort_scores = {'low': 20, 'medium': 10, 'high': 0}
            score += effort_scores.get(opportunity.effort, 0)
            
            # 基于相关代码异味的严重程度
            related_smells = [smell for smell in code_smells 
                            if smell.file_path == opportunity.file_path and 
                            abs(smell.line_number - opportunity.line_number) < 10]
            
            severity_scores = {'low': 5, 'medium': 10, 'high': 20, 'critical': 30}
            for smell in related_smells:
                score += severity_scores.get(smell.severity, 0)
            
            scored_opportunities.append((opportunity, score))
        
        # 按分数排序
        scored_opportunities.sort(key=lambda x: x[1], reverse=True)
        
        return [opportunity for opportunity, score in scored_opportunities]
    
    def _estimate_total_effort(self, opportunities: List[RefactoringOpportunity]) -> str:
        """估算总体工作量"""
        effort_counts = Counter(op.effort for op in opportunities)
        
        # 简单的工作量估算
        total_effort_days = (
            effort_counts.get('low', 0) * 0.5 +
            effort_counts.get('medium', 0) * 2 +
            effort_counts.get('high', 0) * 5
        )
        
        if total_effort_days < 1:
            return "low"
        elif total_effort_days < 5:
            return "medium"
        else:
            return "high"
    
    def _estimate_total_benefit(self, opportunities: List[RefactoringOpportunity]) -> str:
        """估算总体收益"""
        benefit_counts = Counter(op.benefit for op in opportunities)
        
        # 简单的收益估算
        total_benefit_score = (
            benefit_counts.get('low', 0) * 1 +
            benefit_counts.get('medium', 0) * 3 +
            benefit_counts.get('high', 0) * 5
        )
        
        if total_benefit_score < 5:
            return "low"
        elif total_benefit_score < 15:
            return "medium"
        else:
            return "high"
    
    def _identify_risks(self, opportunities: List[RefactoringOpportunity], 
                       code_smells: List[CodeSmell]) -> List[str]:
        """识别风险"""
        risks = []
        
        # 高复杂度的重构风险
        high_effort_count = sum(1 for op in opportunities if op.effort == 'high')
        if high_effort_count > 3:
            risks.append(f"存在 {high_effort_count} 个高工作量重构，风险较高")
        
        # 严重代码异味风险
        critical_smells = sum(1 for smell in code_smells if smell.severity == 'critical')
        if critical_smells > 5:
            risks.append(f"存在 {critical_smells} 个严重代码异味，需要优先处理")
        
        # 文件重构集中风险
        file_counts = Counter(op.file_path for op in opportunities)
        high_risk_files = [file for file, count in file_counts.items() if count > 5]
        if high_risk_files:
            risks.append(f"文件 {', '.join(high_risk_files)} 需要大量重构，风险集中")
        
        return risks

# 使用示例
if __name__ == "__main__":
    # 创建代码分析器
    analyzer = CodeAnalyzer()
    
    # 分析代码
    results = analyzer.analyze_directory("src")
    
    print(f"分析了 {len(results)} 个文件")
    
    # 统计代码异味
    total_smells = len(analyzer.code_smells)
    print(f"发现 {total_smells} 个代码异味")
    
    # 统计重构机会
    total_opportunities = len(analyzer.refactoring_opportunities)
    print(f"发现 {total_opportunities} 个重构机会")
    
    # 创建重构计划
    planner = RefactoringPlanner()
    plan = planner.create_refactoring_plan(
        project_name="MyProject",
        opportunities=analyzer.refactoring_opportunities,
        code_smells=analyzer.code_smells
    )
    
    print(f"重构计划: {plan.project_name}")
    print(f"估算工作量: {plan.estimated_effort}")
    print(f"估算收益: {plan.estimated_benefit}")
    print(f"风险数量: {len(plan.risks)}")
    
    # 应用重构（示例）
    if plan.opportunities:
        engine = RefactoringEngine()
        first_opportunity = plan.opportunities[0]
        
        result = engine.apply_refactoring(
            file_path=first_opportunity.file_path,
            refactoring_type=first_opportunity.refactoring_type,
            line_number=first_opportunity.line_number
        )
        
        if result['success']:
            print(f"成功应用重构: {first_opportunity.refactoring_type.value}")
        else:
            print(f"重构失败: {result['error']}")
```

## 参考资源

### 重构经典著作
- [Refactoring: Improving the Design of Existing Code](https://martinfowler.com/books/refactoring.html) - Martin Fowler
- [Clean Code](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350884) - Robert C. Martin
- [Working Effectively with Legacy Code](https://www.amazon.com/Working-Effectively-Legacy-Michael-Feathers/dp/0131177052) - Michael Feathers

### 重构工具
- [PyCharm Refactoring Tools](https://www.jetbrains.com/pycharm/features/refactoring.html)
- [Eclipse Refactoring Tools](https://www.eclipse.org/eclipse/news/4.20/refactoring-improvements/)
- [Visual Studio Refactoring](https://docs.microsoft.com/en-us/visualstudio/ide/refactoring)
- [IntelliJ IDEA Refactoring](https://www.jetbrains.com/idea/features/refactoring.html)

### 代码质量工具
- [SonarQube](https://www.sonarqube.org/) - 代码质量管理平台
- [CodeClimate](https://codeclimate.com/) - 代码质量分析
- [Coverity](https://www.synopsys.com/software-integrity/security-testing/static-analysis-sast.html) - 静态代码分析
- [Fortify](https://www.microfocus.com/en-us/solutions/application-security) - 应用安全测试

### 重构模式资源
- [Refactoring Catalog](https://refactoring.com/catalog/) - 重构模式目录
- [SourceMaking Refactoring](https://sourcemaking.com/refactoring) - 重构指南
- [Refactoring.guru](https://refactoring.guru/) - 设计模式和重构
- [Clean Code Developer](https://www.clean-code-developer.com/) - 整洁代码开发

### 最佳实践指南
- [Google Style Guides](https://google.github.io/styleguide/) - 代码风格指南
- [Python Code Style](https://peps.python.org/pep-0008/) - PEP 8 代码风格
- [Java Code Conventions](https://www.oracle.com/java/technologies/javase/codeconventions.html) - Java代码约定
- [JavaScript Standard Style](https://standardjs.com/) - JavaScript标准风格
