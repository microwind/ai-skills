---
name: 数据库迁移验证
description: "当执行数据库迁移时，验证迁移脚本安全性，分析性能影响，检查数据完整性。制定回滚策略，评估风险，和最佳实践应用。"
license: MIT
---

# 数据库迁移验证技能

## 概述
数据库迁移是系统演进的关键环节。不当的迁移会导致数据丢失、系统停机、性能问题。需要在执行前全面验证迁移方案。

**核心原则**: 好的迁移应该安全可靠、影响可控、可回滚、性能优良。坏的迁移会锁定生产、丢失数据、导致停机。

## 何时使用

**始终:**
- 执行数据库迁移前
- 审查迁移代码时
- 规划零停机部署
- 测试数据转换
- 验证模式变更
- 调查迁移失败

**触发短语:**
- "这个迁移安全吗？"
- "验证数据库迁移"
- "检查数据转换"
- "会导致停机吗？"
- "如何安全执行迁移？"
- "审查迁移策略"

## 迁移验证功能

### 安全检查
- 数据丢失检测
- 锁定分析
- 停机时间估算
- 回滚策略
- 备份验证

### 数据验证
- 数据类型兼容性
- 约束违规检测
- 数据转换正确性
- 空值处理
- 索引重建影响

### 性能影响
- 表锁定时间
- 索引重建时间
- 磁盘空间需求
- 查询性能影响
- 连接池影响

### 风险评估
- 迁移复杂度分析
- 失败概率评估
- 影响范围评估
- 回滚可行性
- 业务影响分析

## 常见迁移问题

### 长时间运行的迁移
```
问题:
在10亿行表上执行ALTER TABLE MODIFY COLUMN类型变更（数小时的表锁定）

后果:
- 生产数据库被锁定
- 所有查询被阻塞
- 系统停机

解决方案:
使用在线模式迁移工具或影子迁移
```

### 数据丢失迁移
```
问题:
在没有备份数据的情况下执行ALTER TABLE DROP COLUMN

后果:
- 数据永久丢失
- 无法恢复
- 违反合规要求

解决方案:
先备份数据，删除前验证
```

### 不可转换数据
```
问题:
在没有验证的情况下将字符串列转换为整数

后果:
- 非数值无法转换
- 迁移失败
- 部分数据丢失

解决方案:
转换前验证数据，创建临时列
```

### 索引重建问题
```
问题:
在大表上添加或删除索引导致长时间锁定

后果:
- 写操作被阻塞
- 查询性能下降
- 系统响应缓慢

解决方案:
使用在线索引创建或分批重建
```

## 代码实现示例

### 迁移验证器
```python
import re
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class MigrationRisk(Enum):
    """迁移风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MigrationType(Enum):
    """迁移类型"""
    SCHEMA_CHANGE = "schema_change"
    DATA_MIGRATION = "data_migration"
    INDEX_OPERATION = "index_operation"
    CONSTRAINT_CHANGE = "constraint_change"

@dataclass
class MigrationIssue:
    """迁移问题"""
    severity: MigrationRisk
    type: str
    description: str
    suggestion: str
    line_number: Optional[int] = None

@dataclass
class MigrationValidation:
    """迁移验证结果"""
    migration_id: str
    is_safe: bool
    risk_level: MigrationRisk
    issues: List[MigrationIssue]
    estimated_downtime: float
    estimated_duration: float
    rollback_complexity: str

class DatabaseMigrationValidator:
    def __init__(self):
        self.risk_patterns = {
            'DROP TABLE': MigrationRisk.CRITICAL,
            'DROP COLUMN': MigrationRisk.HIGH,
            'ALTER TABLE.*MODIFY.*COLUMN': MigrationRisk.HIGH,
            'ALTER TABLE.*ADD.*INDEX': MigrationRisk.MEDIUM,
            'ALTER TABLE.*DROP.*INDEX': MigrationRisk.MEDIUM,
            'DELETE FROM.*WHERE': MigrationRisk.MEDIUM,
            'UPDATE.*SET.*WHERE': MigrationRisk.LOW,
        }
        
        self.lock_patterns = {
            'ALTER TABLE': '表级锁定',
            'CREATE INDEX': '表级锁定',
            'DROP INDEX': '表级锁定',
            'TRUNCATE TABLE': '表级锁定',
        }
    
    def validate_migration(self, migration_sql: str, table_info: Dict[str, Any]) -> MigrationValidation:
        """验证迁移SQL"""
        migration_id = self._generate_migration_id()
        issues = []
        
        # 解析SQL语句
        statements = self._parse_sql_statements(migration_sql)
        
        # 分析每个语句
        for i, statement in enumerate(statements, 1):
            statement_issues = self._analyze_statement(statement, table_info, i)
            issues.extend(statement_issues)
        
        # 计算风险等级
        risk_level = self._calculate_risk_level(issues)
        
        # 估算影响
        estimated_downtime = self._estimate_downtime(statements, table_info)
        estimated_duration = self._estimate_duration(statements, table_info)
        rollback_complexity = self._assess_rollback_complexity(statements)
        
        # 判断是否安全
        is_safe = risk_level in [MigrationRisk.LOW, MigrationRisk.MEDIUM] and len([i for i in issues if i.severity == MigrationRisk.CRITICAL]) == 0
        
        return MigrationValidation(
            migration_id=migration_id,
            is_safe=is_safe,
            risk_level=risk_level,
            issues=issues,
            estimated_downtime=estimated_downtime,
            estimated_duration=estimated_duration,
            rollback_complexity=rollback_complexity
        )
    
    def _parse_sql_statements(self, sql: str) -> List[str]:
        """解析SQL语句"""
        # 移除注释和多余空白
        cleaned_sql = re.sub(r'--.*?\n', '\n', sql)
        cleaned_sql = re.sub(r'/\*.*?\*/', '', cleaned_sql, flags=re.DOTALL)
        cleaned_sql = re.sub(r'\s+', ' ', cleaned_sql).strip()
        
        # 分割语句
        statements = []
        current_statement = ""
        in_quotes = False
        quote_char = None
        
        for char in cleaned_sql:
            if char in ["'", '"'] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == ';' and not in_quotes:
                if current_statement.strip():
                    statements.append(current_statement.strip())
                current_statement = ""
                continue
            
            current_statement += char
        
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return statements
    
    def _analyze_statement(self, statement: str, table_info: Dict[str, Any], line_number: int) -> List[MigrationIssue]:
        """分析单个SQL语句"""
        issues = []
        statement_upper = statement.upper()
        
        # 检查风险模式
        for pattern, risk in self.risk_patterns.items():
            if re.search(pattern, statement_upper):
                issue = self._create_risk_issue(pattern, risk, statement, line_number)
                issues.append(issue)
        
        # 检查数据丢失风险
        if 'DROP' in statement_upper:
            if 'DROP TABLE' in statement_upper:
                issues.append(MigrationIssue(
                    severity=MigrationRisk.CRITICAL,
                    type='data_loss',
                    description='删除表可能导致数据永久丢失',
                    suggestion='确保已备份数据，考虑使用软删除',
                    line_number=line_number
                ))
            elif 'DROP COLUMN' in statement_upper:
                issues.append(MigrationIssue(
                    severity=MigrationRisk.HIGH,
                    type='data_loss',
                    description='删除列可能导致数据丢失',
                    suggestion='先备份数据，验证后再删除',
                    line_number=line_number
                ))
        
        # 检查锁定风险
        for pattern, lock_type in self.lock_patterns.items():
            if re.search(pattern, statement_upper):
                table_size = table_info.get('estimated_rows', 0)
                if table_size > 1000000:  # 100万行
                    issues.append(MigrationIssue(
                        severity=MigrationRisk.HIGH,
                        type='locking',
                        description=f'大表操作可能导致长时间{lock_type}',
                        suggestion='考虑使用在线迁移工具或分批处理',
                        line_number=line_number
                    ))
        
        # 检查数据类型转换
        if 'ALTER TABLE' in statement_upper and 'MODIFY' in statement_upper and 'COLUMN' in statement_upper:
            issues.append(MigrationIssue(
                severity=MigrationRisk.MEDIUM,
                type='data_conversion',
                description='列类型变更可能导致数据转换问题',
                suggestion='验证数据兼容性，考虑使用临时列',
                line_number=line_number
            ))
        
        # 检查索引操作
        if 'CREATE INDEX' in statement_upper or 'DROP INDEX' in statement_upper:
            issues.append(MigrationIssue(
                severity=MigrationRisk.MEDIUM,
                type='index_operation',
                description='索引操作可能影响查询性能',
                suggestion='在低峰期执行，监控性能影响',
                line_number=line_number
            ))
        
        return issues
    
    def _create_risk_issue(self, pattern: str, risk: MigrationRisk, statement: str, line_number: int) -> MigrationIssue:
        """创建风险问题"""
        descriptions = {
            'DROP TABLE': '删除表是高风险操作，可能导致数据永久丢失',
            'DROP COLUMN': '删除列可能导致数据丢失',
            'ALTER TABLE.*MODIFY.*COLUMN': '修改列类型可能导致长时间锁定',
            'ALTER TABLE.*ADD.*INDEX': '添加索引可能影响写性能',
            'ALTER TABLE.*DROP.*INDEX': '删除索引可能影响查询性能',
            'DELETE FROM.*WHERE': '批量删除可能影响性能',
            'UPDATE.*SET.*WHERE': '批量更新可能影响性能',
        }
        
        suggestions = {
            'DROP TABLE': '确保已备份数据，考虑使用软删除策略',
            'DROP COLUMN': '先备份数据，验证数据完整性后再删除',
            'ALTER TABLE.*MODIFY.*COLUMN': '使用在线迁移工具或分批处理',
            'ALTER TABLE.*ADD.*INDEX': '在低峰期执行，考虑使用CONCURRENTLY',
            'ALTER TABLE.*DROP.*INDEX': '在低峰期执行，监控查询性能',
            'DELETE FROM.*WHERE': '分批删除，避免长时间锁定',
            'UPDATE.*SET.*WHERE': '分批更新，减少锁定时间',
        }
        
        return MigrationIssue(
            severity=risk,
            type='pattern_match',
            description=descriptions.get(pattern, f'检测到风险模式: {pattern}'),
            suggestion=suggestions.get(pattern, '仔细评估操作风险'),
            line_number=line_number
        )
    
    def _calculate_risk_level(self, issues: List[MigrationIssue]) -> MigrationRisk:
        """计算整体风险等级"""
        if not issues:
            return MigrationRisk.LOW
        
        critical_count = len([i for i in issues if i.severity == MigrationRisk.CRITICAL])
        high_count = len([i for i in issues if i.severity == MigrationRisk.HIGH])
        medium_count = len([i for i in issues if i.severity == MigrationRisk.MEDIUM])
        
        if critical_count > 0:
            return MigrationRisk.CRITICAL
        elif high_count > 2:
            return MigrationRisk.HIGH
        elif high_count > 0 or medium_count > 3:
            return MigrationRisk.MEDIUM
        else:
            return MigrationRisk.LOW
    
    def _estimate_downtime(self, statements: List[str], table_info: Dict[str, Any]) -> float:
        """估算停机时间（分钟）"""
        total_downtime = 0
        table_size = table_info.get('estimated_rows', 0)
        
        for statement in statements:
            statement_upper = statement.upper()
            
            if 'DROP TABLE' in statement_upper:
                total_downtime += 5
            elif 'ALTER TABLE' in statement_upper and 'MODIFY' in statement_upper:
                # 基于表大小估算
                if table_size > 10000000:  # 1000万行
                    total_downtime += 60
                elif table_size > 1000000:  # 100万行
                    total_downtime += 30
                else:
                    total_downtime += 10
            elif 'CREATE INDEX' in statement_upper or 'DROP INDEX' in statement_upper:
                if table_size > 1000000:
                    total_downtime += 20
                else:
                    total_downtime += 5
            elif 'DELETE FROM' in statement_upper or 'UPDATE' in statement_upper:
                total_downtime += 2
        
        return total_downtime
    
    def _estimate_duration(self, statements: List[str], table_info: Dict[str, Any]) -> float:
        """估算执行时间（分钟）"""
        total_duration = 0
        table_size = table_info.get('estimated_rows', 0)
        
        for statement in statements:
            statement_upper = statement.upper()
            
            if 'DROP TABLE' in statement_upper:
                total_duration += 2
            elif 'ALTER TABLE' in statement_upper:
                total_duration += self._estimate_alter_time(statement_upper, table_size)
            elif 'CREATE INDEX' in statement_upper:
                total_duration += self._estimate_index_time(table_size)
            elif 'DROP INDEX' in statement_upper:
                total_duration += 5
            elif 'DELETE FROM' in statement_upper:
                total_duration += 10
            elif 'UPDATE' in statement_upper:
                total_duration += 15
        
        return total_duration
    
    def _estimate_alter_time(self, statement: str, table_size: int) -> float:
        """估算ALTER TABLE时间"""
        if 'MODIFY' in statement and 'COLUMN' in statement:
            # 修改列类型
            if table_size > 10000000:
                return 120  # 2小时
            elif table_size > 1000000:
                return 60   # 1小时
            else:
                return 15   # 15分钟
        elif 'ADD' in statement and 'COLUMN' in statement:
            return 5
        elif 'DROP' in statement and 'COLUMN' in statement:
            return 10
        else:
            return 20
    
    def _estimate_index_time(self, table_size: int) -> float:
        """估算索引操作时间"""
        if table_size > 10000000:
            return 90  # 1.5小时
        elif table_size > 1000000:
            return 45  # 45分钟
        else:
            return 10  # 10分钟
    
    def _assess_rollback_complexity(self, statements: List[str]) -> str:
        """评估回滚复杂度"""
        complexity_score = 0
        
        for statement in statements:
            statement_upper = statement.upper()
            
            if 'DROP TABLE' in statement_upper:
                complexity_score += 10
            elif 'DROP COLUMN' in statement_upper:
                complexity_score += 8
            elif 'ALTER TABLE' in statement_upper and 'MODIFY' in statement_upper:
                complexity_score += 6
            elif 'DELETE FROM' in statement_upper:
                complexity_score += 5
            elif 'UPDATE' in statement_upper:
                complexity_score += 3
        
        if complexity_score >= 20:
            return "复杂"
        elif complexity_score >= 10:
            return "中等"
        else:
            return "简单"
    
    def _generate_migration_id(self) -> str:
        """生成迁移ID"""
        timestamp = int(time.time())
        return f"migration_{timestamp}"
    
    def generate_rollback_script(self, migration_sql: str) -> str:
        """生成回滚脚本"""
        statements = self._parse_sql_statements(migration_sql)
        rollback_statements = []
        
        # 反向处理语句
        for statement in reversed(statements):
            rollback = self._generate_statement_rollback(statement)
            if rollback:
                rollback_statements.append(rollback)
        
        return '\n'.join(rollback_statements)
    
    def _generate_statement_rollback(self, statement: str) -> Optional[str]:
        """为单个语句生成回滚"""
        statement_upper = statement.upper()
        
        if 'CREATE TABLE' in statement_upper:
            # 回滚：删除表
            table_match = re.search(r'CREATE TABLE\s+(\w+)', statement_upper)
            if table_match:
                table_name = table_match.group(1)
                return f"DROP TABLE {table_name};"
        
        elif 'DROP TABLE' in statement_upper:
            # 回滚：需要从备份恢复
            return "-- 需要从备份恢复表数据"
        
        elif 'ALTER TABLE' in statement_upper:
            # 回滚ALTER TABLE比较复杂，需要具体分析
            return "-- ALTER TABLE回滚需要根据具体变更生成"
        
        elif 'CREATE INDEX' in statement_upper:
            # 回滚：删除索引
            index_match = re.search(r'CREATE INDEX\s+(\w+)', statement_upper)
            if index_match:
                index_name = index_match.group(1)
                return f"DROP INDEX {index_name};"
        
        elif 'DROP INDEX' in statement_upper:
            # 回滚：重新创建索引
            return "-- 需要重新创建索引"
        
        return None

# 迁移计划生成器
class MigrationPlanGenerator:
    def __init__(self):
        self.validator = DatabaseMigrationValidator()
    
    def generate_migration_plan(self, migration_sql: str, table_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成迁移计划"""
        # 验证迁移
        validation = self.validator.validate_migration(migration_sql, table_info)
        
        # 生成回滚脚本
        rollback_script = self.validator.generate_rollback_script(migration_sql)
        
        # 生成执行计划
        execution_plan = self._generate_execution_plan(validation, table_info)
        
        # 生成检查清单
        checklist = self._generate_checklist(validation)
        
        return {
            'validation': validation,
            'rollback_script': rollback_script,
            'execution_plan': execution_plan,
            'checklist': checklist,
            'recommendations': self._generate_recommendations(validation)
        }
    
    def _generate_execution_plan(self, validation: MigrationValidation, table_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行计划"""
        plan = {
            'phases': [],
            'total_duration': validation.estimated_duration,
            'estimated_downtime': validation.estimated_downtime,
            'risk_level': validation.risk_level.value
        }
        
        if validation.risk_level == MigrationRisk.CRITICAL:
            plan['phases'].append({
                'phase': 'preparation',
                'description': '准备阶段',
                'actions': [
                    '创建完整数据备份',
                    '在测试环境验证迁移',
                    '准备回滚脚本',
                    '通知相关团队'
                ],
                'duration': 60
            })
        
        plan['phases'].append({
            'phase': 'execution',
            'description': '执行阶段',
            'actions': [
                '在低峰期执行',
                '监控系统性能',
                '记录执行日志',
                '验证结果'
            ],
            'duration': validation.estimated_duration
        })
        
        if validation.estimated_downtime > 0:
            plan['phases'].append({
                'phase': 'downtime',
                'description': '停机窗口',
                'actions': [
                    '通知用户停机',
                    '停止相关服务',
                    '执行迁移',
                    '验证系统',
                    '恢复服务'
                ],
                'duration': validation.estimated_downtime
            })
        
        plan['phases'].append({
            'phase': 'verification',
            'description': '验证阶段',
            'actions': [
                '验证数据完整性',
                '检查应用功能',
                '监控系统性能',
                '确认无异常'
            ],
            'duration': 30
        })
        
        return plan
    
    def _generate_checklist(self, validation: MigrationValidation) -> List[str]:
        """生成检查清单"""
        checklist = [
            "□ 已创建数据库备份",
            "□ 在测试环境验证通过",
            "□ 已准备回滚脚本",
            "□ 已通知相关人员",
            f"□ 风险等级: {validation.risk_level.value}",
            f"□ 预计停机时间: {validation.estimated_downtime}分钟",
            f"□ 预计执行时间: {validation.estimated_duration}分钟",
        ]
        
        if validation.issues:
            checklist.append("□ 已检查所有风险问题:")
            for issue in validation.issues:
                checklist.append(f"  - {issue.description}")
        
        checklist.extend([
            "□ 系统监控已就位",
            "□ 回滚计划已确认",
            "□ 应急联系人已通知",
            "□ 文档已更新"
        ])
        
        return checklist
    
    def _generate_recommendations(self, validation: MigrationValidation) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if validation.risk_level == MigrationRisk.CRITICAL:
            recommendations.append("建议重新设计迁移方案，降低风险等级")
            recommendations.append("考虑分多个小步骤执行")
            recommendations.append("必须在维护窗口期间执行")
        
        if validation.estimated_downtime > 30:
            recommendations.append("建议寻找零停机迁移方案")
            recommendations.append("考虑使用蓝绿部署策略")
        
        if validation.rollback_complexity == "复杂":
            recommendations.append("建议简化回滚策略")
            recommendations.append("准备详细的回滚文档")
        
        critical_issues = [i for i in validation.issues if i.severity == MigrationRisk.CRITICAL]
        if critical_issues:
            recommendations.append("必须解决所有关键风险问题才能执行")
        
        if validation.is_safe:
            recommendations.append("迁移相对安全，可以按计划执行")
            recommendations.append("建议在低峰期执行")
        
        return recommendations

# 使用示例
def main():
    print("=== 数据库迁移验证器 ===")
    
    # 创建验证器
    validator = DatabaseMigrationValidator()
    
    # 示例迁移SQL
    migration_sql = """
    -- 添加新列
    ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
    
    -- 创建索引
    CREATE INDEX idx_users_email ON users(email);
    
    -- 更新数据
    UPDATE users SET email_verified = TRUE WHERE email IS NOT NULL;
    """
    
    # 表信息
    table_info = {
        'table_name': 'users',
        'estimated_rows': 5000000,  # 500万行
        'table_size_gb': 10,
        'indexes': ['PRIMARY KEY', 'idx_username']
    }
    
    # 验证迁移
    validation = validator.validate_migration(migration_sql, table_info)
    
    print("迁移验证结果:")
    print(f"迁移ID: {validation.migration_id}")
    print(f"是否安全: {'是' if validation.is_safe else '否'}")
    print(f"风险等级: {validation.risk_level.value}")
    print(f"预计停机时间: {validation.estimated_downtime}分钟")
    print(f"预计执行时间: {validation.estimated_duration}分钟")
    print(f"回滚复杂度: {validation.rollback_complexity}")
    
    if validation.issues:
        print("\n发现的问题:")
        for i, issue in enumerate(validation.issues, 1):
            print(f"{i}. [{issue.severity.value.upper()}] {issue.description}")
            print(f"   建议: {issue.suggestion}")
            if issue.line_number:
                print(f"   行号: {issue.line_number}")
    
    # 生成回滚脚本
    rollback_script = validator.generate_rollback_script(migration_sql)
    print(f"\n回滚脚本:")
    print(rollback_script)
    
    # 生成完整迁移计划
    plan_generator = MigrationPlanGenerator()
    migration_plan = plan_generator.generate_migration_plan(migration_sql, table_info)
    
    print(f"\n=== 迁移执行计划 ===")
    execution_plan = migration_plan['execution_plan']
    print(f"总执行时间: {execution_plan['total_duration']}分钟")
    print(f"预计停机时间: {execution_plan['estimated_downtime']}分钟")
    print(f"风险等级: {execution_plan['risk_level']}")
    
    print("\n执行阶段:")
    for phase in execution_plan['phases']:
        print(f"- {phase['phase']}: {phase['description']} ({phase['duration']}分钟)")
        for action in phase['actions']:
            print(f"  • {action}")
    
    print(f"\n=== 检查清单 ===")
    for item in migration_plan['checklist']:
        print(item)
    
    print(f"\n=== 建议 ===")
    for recommendation in migration_plan['recommendations']:
        print(f"- {recommendation}")

if __name__ == '__main__':
    main()
```

### 迁移监控器
```python
import time
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class MigrationMetrics:
    """迁移指标"""
    start_time: float
    current_statement: str
    completed_statements: int
    total_statements: int
    estimated_remaining_time: float
    current_progress: float

class MigrationMonitor:
    def __init__(self):
        self.active_migrations: Dict[str, Dict[str, Any]] = {}
        self.monitoring_thread = None
        self.is_monitoring = False
    
    def start_migration(self, migration_id: str, statements: List[str]) -> str:
        """开始监控迁移"""
        self.active_migrations[migration_id] = {
            'statements': statements,
            'start_time': time.time(),
            'current_statement_index': 0,
            'completed_statements': 0,
            'status': 'running',
            'metrics': None
        }
        
        if not self.is_monitoring:
            self.start_monitoring()
        
        return migration_id
    
    def update_progress(self, migration_id: str, current_statement_index: int):
        """更新迁移进度"""
        if migration_id in self.active_migrations:
            migration = self.active_migrations[migration_id]
            migration['current_statement_index'] = current_statement_index
            migration['completed_statements'] = current_statement_index + 1
    
    def complete_migration(self, migration_id: str, success: bool):
        """完成迁移"""
        if migration_id in self.active_migrations:
            migration = self.active_migrations[migration_id]
            migration['status'] = 'completed' if success else 'failed'
            migration['end_time'] = time.time()
    
    def get_migration_metrics(self, migration_id: str) -> Optional[MigrationMetrics]:
        """获取迁移指标"""
        if migration_id not in self.active_migrations:
            return None
        
        migration = self.active_migrations[migration_id]
        statements = migration['statements']
        current_index = migration['current_statement_index']
        
        elapsed_time = time.time() - migration['start_time']
        
        if current_index > 0:
            avg_statement_time = elapsed_time / current_index
            remaining_statements = len(statements) - current_index
            estimated_remaining_time = avg_statement_time * remaining_statements
        else:
            estimated_remaining_time = 0
        
        progress = (current_index / len(statements)) * 100 if statements else 0
        
        return MigrationMetrics(
            start_time=migration['start_time'],
            current_statement=statements[current_index] if current_index < len(statements) else "",
            completed_statements=current_index,
            total_statements=len(statements),
            estimated_remaining_time=estimated_remaining_time,
            current_progress=progress
        )
    
    def start_monitoring(self):
        """开始监控"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            for migration_id, migration in self.active_migrations.items():
                if migration['status'] == 'running':
                    metrics = self.get_migration_metrics(migration_id)
                    migration['metrics'] = metrics
                    
                    # 打印进度
                    print(f"迁移 {migration_id}: {metrics.current_progress:.1f}% 完成")
                    print(f"当前语句: {metrics.current_statement[:50]}...")
                    print(f"预计剩余时间: {metrics.estimated_remaining_time:.1f}秒")
            
            time.sleep(5)  # 每5秒更新一次

# 使用示例
def main():
    print("=== 迁移监控器 ===")
    
    # 创建监控器
    monitor = MigrationMonitor()
    
    # 模拟迁移
    migration_statements = [
        "ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;",
        "CREATE INDEX idx_users_email ON users(email);",
        "UPDATE users SET email_verified = TRUE WHERE email IS NOT NULL;",
    ]
    
    # 开始监控
    migration_id = monitor.start_migration("test_migration", migration_statements)
    print(f"开始监控迁移: {migration_id}")
    
    # 模拟执行过程
    for i in range(len(migration_statements)):
        print(f"\n执行语句 {i+1}: {migration_statements[i][:50]}...")
        time.sleep(2)  # 模拟执行时间
        monitor.update_progress(migration_id, i)
    
    # 完成迁移
    monitor.complete_migration(migration_id, True)
    print("\n迁移完成!")
    
    # 获取最终指标
    final_metrics = monitor.get_migration_metrics(migration_id)
    if final_metrics:
        print(f"总执行时间: {time.time() - final_metrics.start_time:.1f}秒")
        print(f"完成语句数: {final_metrics.completed_statements}")
    
    monitor.stop_monitoring()

if __name__ == '__main__':
    main()
```

## 数据库迁移验证最佳实践

### 迁移策略
1. **分批执行**: 将大迁移拆分为多个小步骤
2. **蓝绿部署**: 使用零停机迁移策略
3. **影子迁移**: 在不影响生产的情况下验证
4. **功能开关**: 使用功能开关控制新功能
5. **回滚计划**: 准备详细的回滚方案

### 安全保障
1. **数据备份**: 执行前必须备份相关数据
2. **测试验证**: 在测试环境充分验证
3. **监控告警**: 实时监控迁移过程
4. **权限控制**: 限制迁移执行权限
5. **审计日志**: 记录所有迁移操作

### 风险控制
1. **风险评估**: 全面评估迁移风险
2. **影响分析**: 分析对系统的影响
3. **应急预案**: 准备应急处理方案
4. **团队协作**: 确保团队沟通顺畅
5. **时间窗口**: 选择合适的执行时间

### 质量保证
1. **代码审查**: 严格审查迁移代码
2. **自动化测试**: 编写自动化测试
3. **性能测试**: 测试迁移性能影响
4. **数据验证**: 验证数据完整性
5. **文档更新**: 及时更新相关文档

## 相关技能

- **backup-recovery** - 备份与恢复
- **sql-optimization** - SQL优化
- **transaction-management** - 事务管理
- **database-query-analyzer** - 数据库查询分析
