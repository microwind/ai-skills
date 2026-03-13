---
name: 代码审查与标准
description: "当进行代码审查时，分析代码质量，检查编码规范，发现潜在问题。验证代码架构，设计审查流程，和最佳实践。"
license: MIT
---

# 代码审查与标准技能

## 概述
代码审查是保证软件质量的重要环节。不当的审查流程会导致问题遗漏、效率低下和团队冲突。需要建立完善的代码审查机制和标准。

**核心原则**: 好的代码审查应该发现问题、促进学习、保持一致性。坏的审查会导致形式主义、浪费时间、影响团队士气。

## 何时使用

**始终:**
- 提交代码变更时
- 合并分支前审查
- 设计架构评审时
- 发布版本前检查
- 培训新团队成员时
- 制定编码标准时

**触发短语:**
- "代码审查与标准"
- "代码质量检查"
- "编码规范验证"
- "代码架构审查"
- "最佳实践检查"
- "代码评审流程"

## 代码审查功能

### 质量检查
- 代码风格检查
- 编码规范验证
- 最佳实践检查
- 安全漏洞扫描
- 性能问题识别

### 架构审查
- 设计模式验证
- 模块耦合分析
- 接口设计检查
- 扩展性评估
- 可维护性分析

### 流程管理
- 审查流程设计
- 审查者分配
- 审查进度跟踪
- 问题反馈管理
- 审查报告生成

### 团队协作
- 知识分享机制
- 最佳实践传播
- 技能提升培训
- 标准制定参与
- 团队文化建设

## 常见代码审查问题

### 审查效率问题
```
问题:
代码审查效率低下，影响开发进度

错误示例:
- 审查流程过于复杂
- 审查者时间不足
- 反馈意见不明确
- 审查标准不统一

解决方案:
1. 简化审查流程
2. 合理安排审查时间
3. 提供明确的反馈模板
4. 建立统一的审查标准
```

### 审查质量问题
```
问题:
代码审查流于形式，无法发现真正问题

错误示例:
- 只关注代码风格
- 忽略架构设计
- 缺少深度分析
- 审查者经验不足

解决方案:
1. 建立多维度审查标准
2. 培养资深审查者
3. 使用自动化工具辅助
4. 定期更新审查清单
```

### 团队协作问题
```
问题:
代码审查引发团队冲突和抵触情绪

错误示例:
- 批评过于严厉
- 缺少建设性意见
- 审查者态度傲慢
- 忽视作者感受

解决方案:
1. 建设性反馈文化
2. 培养沟通技巧
3. 强调团队目标
4. 定期团队建设
```

### 标准执行问题
```
问题:
编码标准执行不一致，质量参差不齐

错误示例:
- 标准定义不明确
- 执行力度不够
- 缺少监督机制
- 标准更新不及时

解决方案:
1. 明确标准定义
2. 加强执行监督
3. 建立奖惩机制
4. 定期更新标准
```

## 代码实现示例

### 代码审查工具
```python
import re
import ast
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json

class IssueSeverity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class IssueCategory(Enum):
    """问题类别"""
    STYLE = "style"
    LOGIC = "logic"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    DOCUMENTATION = "documentation"

@dataclass
class CodeIssue:
    """代码问题"""
    file_path: str
    line_number: int
    column: int
    severity: IssueSeverity
    category: IssueCategory
    message: str
    suggestion: str
    rule_id: str

@dataclass
class ReviewResult:
    """审查结果"""
    file_path: str
    issues: List[CodeIssue]
    metrics: Dict[str, Any]
    score: float
    summary: str

class CodeReviewer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules = self._load_review_rules()
        self.style_checker = StyleChecker()
        self.logic_checker = LogicChecker()
        self.security_checker = SecurityChecker()
        self.performance_checker = PerformanceChecker()
        self.architecture_checker = ArchitectureChecker()
        
    def review_code(self, file_path: str, code: str) -> ReviewResult:
        """审查代码文件"""
        try:
            # 解析代码
            tree = ast.parse(code)
            
            # 执行各种检查
            issues = []
            
            # 风格检查
            style_issues = self.style_checker.check(code, file_path)
            issues.extend(style_issues)
            
            # 逻辑检查
            logic_issues = self.logic_checker.check(tree, code, file_path)
            issues.extend(logic_issues)
            
            # 安全检查
            security_issues = self.security_checker.check(tree, code, file_path)
            issues.extend(security_issues)
            
            # 性能检查
            performance_issues = self.performance_checker.check(tree, code, file_path)
            issues.extend(performance_issues)
            
            # 架构检查
            architecture_issues = self.architecture_checker.check(tree, code, file_path)
            issues.extend(architecture_issues)
            
            # 计算指标
            metrics = self._calculate_metrics(tree, code, issues)
            
            # 计算评分
            score = self._calculate_score(issues, metrics)
            
            # 生成摘要
            summary = self._generate_summary(issues, score)
            
            return ReviewResult(
                file_path=file_path,
                issues=issues,
                metrics=metrics,
                score=score,
                summary=summary
            )
            
        except SyntaxError as e:
            return ReviewResult(
                file_path=file_path,
                issues=[CodeIssue(
                    file_path=file_path,
                    line_number=e.lineno or 0,
                    column=e.offset or 0,
                    severity=IssueSeverity.CRITICAL,
                    category=IssueCategory.STYLE,
                    message="语法错误",
                    suggestion=f"修复语法错误: {e.msg}",
                    rule_id="syntax_error"
                )],
                metrics={},
                score=0.0,
                summary="代码存在语法错误，无法进行完整审查"
            )
    
    def _load_review_rules(self) -> Dict[str, Any]:
        """加载审查规则"""
        return {
            'style_rules': {
                'max_line_length': 100,
                'indentation': 4,
                'naming_convention': 'snake_case',
                'import_order': True
            },
            'logic_rules': {
                'max_function_length': 50,
                'max_complexity': 10,
                'require_docstrings': True
            },
            'security_rules': {
                'check_sql_injection': True,
                'check_xss': True,
                'check_hardcoded_secrets': True
            },
            'performance_rules': {
                'check_complex_loops': True,
                'check_memory_usage': True,
                'check_database_queries': True
            }
        }
    
    def _calculate_metrics(self, tree: ast.AST, code: str, issues: List[CodeIssue]) -> Dict[str, Any]:
        """计算代码指标"""
        lines = code.split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
            'blank_lines': len([line for line in lines if not line.strip()]),
            'function_count': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
            'class_count': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
            'import_count': len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]),
            'issues_by_severity': {
                severity.value: len([issue for issue in issues if issue.severity == severity])
                for severity in IssueSeverity
            },
            'issues_by_category': {
                category.value: len([issue for issue in issues if issue.category == category])
                for category in IssueCategory
            }
        }
        
        # 计算复杂度指标
        metrics['cyclomatic_complexity'] = self._calculate_cyclomatic_complexity(tree)
        
        # 计算代码密度
        metrics['code_density'] = metrics['code_lines'] / metrics['total_lines'] if metrics['total_lines'] > 0 else 0
        
        return metrics
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_score(self, issues: List[CodeIssue], metrics: Dict[str, Any]) -> float:
        """计算代码评分"""
        score = 100.0
        
        # 根据问题严重程度扣分
        severity_weights = {
            IssueSeverity.CRITICAL: 20,
            IssueSeverity.HIGH: 10,
            IssueSeverity.MEDIUM: 5,
            IssueSeverity.LOW: 2,
            IssueSeverity.INFO: 0
        }
        
        for issue in issues:
            score -= severity_weights[issue.severity]
        
        # 根据复杂度扣分
        complexity = metrics.get('cyclomatic_complexity', 0)
        if complexity > 10:
            score -= (complexity - 10) * 2
        
        # 根据函数长度扣分
        if metrics.get('function_count', 0) > 0:
            avg_function_length = metrics.get('code_lines', 0) / metrics.get('function_count', 1)
            if avg_function_length > 50:
                score -= (avg_function_length - 50) * 0.5
        
        return max(0, score)
    
    def _generate_summary(self, issues: List[CodeIssue], score: float) -> str:
        """生成审查摘要"""
        if score >= 90:
            quality = "优秀"
        elif score >= 80:
            quality = "良好"
        elif score >= 70:
            quality = "一般"
        elif score >= 60:
            quality = "较差"
        else:
            quality = "很差"
        
        critical_issues = len([i for i in issues if i.severity == IssueSeverity.CRITICAL])
        high_issues = len([i for i in issues if i.severity == IssueSeverity.HIGH])
        
        summary = f"代码质量: {quality} (评分: {score:.1f})\n"
        summary += f"发现问题总数: {len(issues)}\n"
        summary += f"严重问题: {critical_issues}, 高优先级问题: {high_issues}"
        
        return summary

class StyleChecker:
    def __init__(self):
        self.rules = {
            'max_line_length': 100,
            'indentation': 4,
            'naming_convention': 'snake_case'
        }
    
    def check(self, code: str, file_path: str) -> List[CodeIssue]:
        """检查代码风格"""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 检查行长度
            if len(line) > self.rules['max_line_length']:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=self.rules['max_line_length'],
                    severity=IssueSeverity.LOW,
                    category=IssueCategory.STYLE,
                    message=f"行长度超过限制 ({len(line)} > {self.rules['max_line_length']})",
                    suggestion="拆分长行或使用续行符",
                    rule_id="line_length"
                ))
            
            # 检查缩进
            if line.startswith('\t'):
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=0,
                    severity=IssueSeverity.MEDIUM,
                    category=IssueCategory.STYLE,
                    message="使用制表符缩进",
                    suggestion="使用空格缩进",
                    rule_id="indentation"
                ))
        
        return issues

class LogicChecker:
    def check(self, tree: ast.AST, code: str, file_path: str) -> List[CodeIssue]:
        """检查代码逻辑"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数长度
                function_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                if function_lines > 50:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=0,
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.LOGIC,
                        message=f"函数过长 ({function_lines} 行)",
                        suggestion="拆分函数为更小的函数",
                        rule_id="function_length"
                    ))
                
                # 检查文档字符串
                if not ast.get_docstring(node):
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=0,
                        severity=IssueSeverity.LOW,
                        category=IssueCategory.DOCUMENTATION,
                        message="缺少函数文档字符串",
                        suggestion="添加函数文档说明",
                        rule_id="docstring"
                    ))
        
        return issues

class SecurityChecker:
    def check(self, tree: ast.AST, code: str, file_path: str) -> List[CodeIssue]:
        """检查安全问题"""
        issues = []
        
        # 检查硬编码密码
        password_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']'
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern in password_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=line_num,
                        column=0,
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        message="检测到硬编码敏感信息",
                        suggestion="使用环境变量或配置文件存储敏感信息",
                        rule_id="hardcoded_secrets"
                    ))
        
        return issues

class PerformanceChecker:
    def check(self, tree: ast.AST, code: str, file_path: str) -> List[CodeIssue]:
        """检查性能问题"""
        issues = []
        
        for node in ast.walk(tree):
            # 检查循环中的字符串拼接
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            issues.append(CodeIssue(
                                file_path=file_path,
                                line_number=getattr(node, 'lineno', 0),
                                column=0,
                                severity=IssueSeverity.MEDIUM,
                                category=IssueCategory.PERFORMANCE,
                                message="循环中使用字符串拼接",
                                suggestion="使用列表收集后join()方法",
                                rule_id="string_concatenation"
                            ))
        
        return issues

class ArchitectureChecker:
    def check(self, tree: ast.AST, code: str, file_path: str) -> List[CodeIssue]:
        """检查架构问题"""
        issues = []
        
        # 检查类的复杂度
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                if method_count > 20:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=0,
                        severity=IssueSeverity.HIGH,
                        category=IssueCategory.ARCHITECTURE,
                        message=f"类的方法过多 ({method_count})",
                        suggestion="考虑拆分类或使用组合模式",
                        rule_id="class_complexity"
                    ))
        
        return issues

# 使用示例
def main():
    # 示例代码
    sample_code = '''
def process_data(data):
    result = ""
    for item in data:
        result += str(item)  # 性能问题
    return result

password = "secret123"  # 安全问题

class BigClass:
    def method1(self):
        pass
    def method2(self):
        pass
    # ... 更多方法
'''
    
    # 创建代码审查器
    config = {
        'style_rules': {
            'max_line_length': 100,
            'indentation': 4
        }
    }
    
    reviewer = CodeReviewer(config)
    
    # 审查代码
    result = reviewer.review_code('sample.py', sample_code)
    
    print("代码审查结果:")
    print(result.summary)
    print(f"\n发现 {len(result.issues)} 个问题:")
    
    for issue in result.issues:
        print(f"- 第{issue.line_number}行: {issue.message}")
        print(f"  建议: {issue.suggestion}")
        print(f"  严重程度: {issue.severity.value}")
    
    print(f"\n代码指标:")
    for metric, value in result.metrics.items():
        print(f"- {metric}: {value}")

if __name__ == '__main__':
    main()
```

### 审查流程管理
```python
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class ReviewStatus(Enum):
    """审查状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"

@dataclass
class ReviewRequest:
    """审查请求"""
    id: str
    author: str
    title: str
    description: str
    files: List[str]
    reviewers: List[str]
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    comments: List[Dict[str, Any]]

@dataclass
class ReviewComment:
    """审查评论"""
    id: str
    author: str
    content: str
    line_number: Optional[int]
    file_path: str
    created_at: datetime
    resolved: bool = False

class ReviewWorkflow:
    def __init__(self):
        self.requests: Dict[str, ReviewRequest] = {}
        self.reviewers: Dict[str, Dict[str, Any]] = {}
        
    def create_review_request(self, author: str, title: str, description: str, 
                            files: List[str], reviewers: List[str]) -> str:
        """创建审查请求"""
        request_id = f"review_{len(self.requests) + 1}"
        
        request = ReviewRequest(
            id=request_id,
            author=author,
            title=title,
            description=description,
            files=files,
            reviewers=reviewers,
            status=ReviewStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            comments=[]
        )
        
        self.requests[request_id] = request
        
        # 通知审查者
        self._notify_reviewers(request)
        
        return request_id
    
    def add_review_comment(self, request_id: str, author: str, content: str, 
                          file_path: str, line_number: Optional[int] = None) -> str:
        """添加审查评论"""
        if request_id not in self.requests:
            raise ValueError("审查请求不存在")
        
        request = self.requests[request_id]
        
        comment_id = f"comment_{len(request.comments) + 1}"
        comment = ReviewComment(
            id=comment_id,
            author=author,
            content=content,
            line_number=line_number,
            file_path=file_path,
            created_at=datetime.now()
        )
        
        request.comments.append({
            'id': comment_id,
            'author': author,
            'content': content,
            'line_number': line_number,
            'file_path': file_path,
            'created_at': comment.created_at.isoformat(),
            'resolved': False
        })
        
        request.updated_at = datetime.now()
        
        return comment_id
    
    def approve_review(self, request_id: str, reviewer: str) -> bool:
        """批准审查"""
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        
        if reviewer not in request.reviewers:
            return False
        
        # 更新状态
        if request.status == ReviewStatus.PENDING:
            request.status = ReviewStatus.APPROVED
        elif request.status == ReviewStatus.CHANGES_REQUESTED:
            # 检查是否所有审查者都已批准
            all_approved = self._check_all_reviewers_approved(request)
            if all_approved:
                request.status = ReviewStatus.APPROVED
        
        request.updated_at = datetime.now()
        
        # 通知作者
        self._notify_author(request, "approved")
        
        return True
    
    def request_changes(self, request_id: str, reviewer: str, comment: str) -> bool:
        """要求修改"""
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        
        if reviewer not in request.reviewers:
            return False
        
        request.status = ReviewStatus.CHANGES_REQUESTED
        request.updated_at = datetime.now()
        
        # 添加评论
        self.add_review_comment(request_id, reviewer, comment, "", None)
        
        # 通知作者
        self._notify_author(request, "changes_requested")
        
        return True
    
    def get_review_statistics(self) -> Dict[str, Any]:
        """获取审查统计"""
        total_requests = len(self.requests)
        pending_requests = len([r for r in self.requests.values() if r.status == ReviewStatus.PENDING])
        approved_requests = len([r for r in self.requests.values() if r.status == ReviewStatus.APPROVED])
        
        # 计算平均审查时间
        completed_requests = [r for r in self.requests.values() if r.status in [ReviewStatus.APPROVED, ReviewStatus.REJECTED]]
        avg_review_time = 0
        if completed_requests:
            total_time = sum((r.updated_at - r.created_at).total_seconds() for r in completed_requests)
            avg_review_time = total_time / len(completed_requests) / 3600  # 转换为小时
        
        return {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'average_review_time_hours': avg_review_time,
            'approval_rate': approved_requests / total_requests if total_requests > 0 else 0
        }
    
    def _notify_reviewers(self, request: ReviewRequest) -> None:
        """通知审查者"""
        # 这里可以实现邮件、Slack等通知
        print(f"通知审查者 {request.reviewers}: 新的审查请求 {request.title}")
    
    def _notify_author(self, request: ReviewRequest, action: str) -> None:
        """通知作者"""
        print(f"通知作者 {request.author}: 审查请求 {request.title} {action}")
    
    def _check_all_reviewers_approved(self, request: ReviewRequest) -> bool:
        """检查是否所有审查者都已批准"""
        # 简化实现，实际应该跟踪每个审查者的状态
        return True

# 使用示例
def main():
    # 创建审查工作流
    workflow = ReviewWorkflow()
    
    # 创建审查请求
    request_id = workflow.create_review_request(
        author="张三",
        title="新功能：用户登录模块",
        description="实现了用户登录功能，包括密码验证和会话管理",
        files=["auth.py", "models.py"],
        reviewers=["李四", "王五"]
    )
    
    print(f"创建审查请求: {request_id}")
    
    # 添加审查评论
    workflow.add_review_comment(
        request_id=request_id,
        author="李四",
        content="建议添加输入验证，防止SQL注入",
        file_path="auth.py",
        line_number=25
    )
    
    workflow.add_review_comment(
        request_id=request_id,
        author="王五",
        content="密码应该使用bcrypt加密存储",
        file_path="models.py",
        line_number=15
    )
    
    # 批准审查
    workflow.approve_review(request_id, "李四")
    workflow.approve_review(request_id, "王五")
    
    # 获取统计信息
    stats = workflow.get_review_statistics()
    print("\n审查统计:")
    for key, value in stats.items():
        print(f"- {key}: {value}")

if __name__ == '__main__':
    main()
```

## 代码审查最佳实践

### 审查准备
1. **明确目标**: 确定审查的重点和目标
2. **选择审查者**: 根据专业领域选择合适的审查者
3. **准备材料**: 提供充分的上下文和文档
4. **设定时间**: 合理安排审查时间
5. **工具准备**: 准备必要的审查工具

### 审查执行
1. **全面检查**: 从多个维度检查代码质量
2. **建设性反馈**: 提供具体、可操作的改进建议
3. **关注重点**: 优先关注关键问题
4. **记录问题**: 详细记录发现的问题
5. **讨论沟通**: 与作者进行有效沟通

### 反馈管理
1. **分类整理**: 按严重程度分类问题
2. **优先级排序**: 确定问题处理的优先级
3. **跟踪状态**: 跟踪问题的解决状态
4. **验证修复**: 验证问题是否得到解决
5. **总结经验**: 总结审查经验和教训

### 团队建设
1. **知识分享**: 通过审查分享技术知识
2. **技能提升**: 帮助团队成员提升技能
3. **文化建设**: 建设积极的审查文化
4. **标准制定**: 参与制定和更新编码标准
5. **持续改进**: 持续改进审查流程

## 相关技能

- **code-optimization** - 代码优化技巧
- **refactoring-patterns** - 重构模式
- **documentation-generator** - 文档生成
- **test-generation** - 测试生成
