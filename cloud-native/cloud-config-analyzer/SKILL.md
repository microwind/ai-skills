---
name: 云配置分析器
description: "当分析云配置、审查基础设施、优化成本或审计安全时，在部署前验证云资源配置。"
license: MIT
---

# 云配置分析器技能

## 概述
云配置是云原生应用的基础。错误的配置会导致数据泄露、成本浪费和安全漏洞。

**核心原则**: 错误的云资源配置会泄露数据、浪费资金并暴露安全漏洞。

## 何时使用

**始终:**
- 部署到云环境之前
- 审查云基础设施
- 优化云成本
- 云资源安全审计
- 配置合规性检查
- 多云环境管理

**触发短语:**
- "分析云配置"
- "检查云安全"
- "优化云成本"
- "云配置审计"
- "多云配置管理"
- "云合规检查"

## 云配置分析功能

### 配置验证
- 云资源配置检查
- 安全策略验证
- 网络配置分析
- 存储配置审查
- 访问权限检查

### 成本优化
- 资源使用分析
- 成本趋势监控
- 优化建议生成
- 预算超支预警
- 资源规模调整

### 安全审计
- 安全配置检查
- 权限审计
- 网络安全分析
- 数据加密验证
- 合规性检查

## 常见云配置问题

### 安全配置错误
```
问题:
云资源安全配置不当

错误示例:
- 存储桶公开访问
- 安全组规则过于宽松
- 密钥硬编码在配置中
- 未启用加密

解决方案:
1. 实施最小权限原则
2. 启用默认加密
3. 使用密钥管理服务
4. 定期安全审计
```

### 成本浪费
```
问题:
云资源配置过度导致成本浪费

错误示例:
- 开发环境使用生产级实例
- 未使用自动缩放
- 闲置资源未清理
- 存储数据冗余

解决方案:
1. 使用合适的实例类型
2. 配置自动缩放
3. 定期清理闲置资源
4. 实施生命周期管理
```

### 网络配置错误
```
问题:
网络配置导致性能或安全问题

错误示例:
- 跨区域流量未优化
- 防火墙规则冲突
- DNS配置错误
- 负载均衡配置不当

解决方案:
1. 优化网络拓扑
2. 使用CDN加速
3. 配置健康检查
4. 实施网络分段
```

## 代码实现示例

### 云配置分析器
```python
import json
import yaml
import boto3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime, timedelta

class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ALIBABA = "alibaba"

class ResourceType(Enum):
    EC2 = "ec2"
    S3 = "s3"
    RDS = "rds"
    LAMBDA = "lambda"
    VPC = "vpc"
    SECURITY_GROUP = "security_group"
    IAM = "iam"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CloudResource:
    """云资源"""
    id: str
    type: ResourceType
    provider: CloudProvider
    region: str
    config: Dict[str, Any]
    tags: Dict[str, str]
    created_at: datetime

@dataclass
class SecurityIssue:
    """安全问题"""
    resource_id: str
    issue_type: str
    description: str
    risk_level: RiskLevel
    recommendation: str

@dataclass
class CostIssue:
    """成本问题"""
    resource_id: str
    issue_type: str
    description: str
    potential_savings: float
    recommendation: str

@dataclass
class ComplianceIssue:
    """合规问题"""
    resource_id: str
    standard: str
    requirement: str
    status: str
    remediation: str

class CloudConfigAnalyzer:
    """云配置分析器"""
    
    def __init__(self, provider: CloudProvider = CloudProvider.AWS):
        self.provider = provider
        self.client = self._initialize_client()
        self.security_rules = self._load_security_rules()
        self.cost_rules = self._load_cost_rules()
        self.compliance_rules = self._load_compliance_rules()
    
    def _initialize_client(self):
        """初始化云客户端"""
        if self.provider == CloudProvider.AWS:
            return boto3.client('ec2')
        elif self.provider == CloudProvider.AZURE:
            # Azure client initialization
            pass
        elif self.provider == CloudProvider.GCP:
            # GCP client initialization
            pass
        return None
    
    def analyze_security(self, resources: List[CloudResource]) -> List[SecurityIssue]:
        """分析安全配置"""
        issues = []
        
        for resource in resources:
            # 检查特定资源类型的安全问题
            if resource.type == ResourceType.S3:
                issues.extend(self._analyze_s3_security(resource))
            elif resource.type == ResourceType.EC2:
                issues.extend(self._analyze_ec2_security(resource))
            elif resource.type == ResourceType.SECURITY_GROUP:
                issues.extend(self._analyze_security_group(resource))
            elif resource.type == ResourceType.IAM:
                issues.extend(self._analyze_iam_security(resource))
        
        return issues
    
    def _analyze_s3_security(self, resource: CloudResource) -> List[SecurityIssue]:
        """分析S3安全配置"""
        issues = []
        config = resource.config
        
        # 检查公开访问
        if config.get('public_read', False):
            issues.append(SecurityIssue(
                resource_id=resource.id,
                issue_type="public_access",
                description="S3存储桶配置了公开读取访问",
                risk_level=RiskLevel.HIGH,
                recommendation="禁用公开访问，使用IAM策略控制访问"
            ))
        
        # 检查加密
        if not config.get('encryption_enabled', False):
            issues.append(SecurityIssue(
                resource_id=resource.id,
                issue_type="encryption_disabled",
                description="S3存储桶未启用加密",
                risk_level=RiskLevel.MEDIUM,
                recommendation="启用S3默认加密"
            ))
        
        # 检查版本控制
        if not config.get('versioning_enabled', False):
            issues.append(SecurityIssue(
                resource_id=resource.id,
                issue_type="versioning_disabled",
                description="S3存储桶未启用版本控制",
                risk_level=RiskLevel.MEDIUM,
                recommendation="启用S3版本控制以防止意外删除"
            ))
        
        # 检查访问日志
        if not config.get('access_logging_enabled', False):
            issues.append(SecurityIssue(
                resource_id=resource.id,
                issue_type="logging_disabled",
                description="S3存储桶未启用访问日志",
                risk_level=RiskLevel.LOW,
                recommendation="启用S3访问日志以监控访问模式"
            ))
        
        return issues
    
    def _analyze_ec2_security(self, resource: CloudResource) -> List[SecurityIssue]:
        """分析EC2安全配置"""
        issues = []
        config = resource.config
        
        # 检查公开端口
        public_ports = config.get('public_ports', [])
        dangerous_ports = [22, 3389, 3306, 5432, 1433]
        
        for port in public_ports:
            if port in dangerous_ports:
                issues.append(SecurityIssue(
                    resource_id=resource.id,
                    issue_type="dangerous_public_port",
                    description=f"EC2实例公开了危险端口: {port}",
                    risk_level=RiskLevel.HIGH,
                    recommendation=f"限制端口{port}的访问，仅允许特定IP访问"
                ))
        
        # 检查IAM角色
        if not config.get('iam_role_attached', False):
            issues.append(SecurityIssue(
                resource_id=resource.id,
                issue_type="no_iam_role",
                description="EC2实例未附加IAM角色",
                risk_level=RiskLevel.MEDIUM,
                recommendation="为EC2实例附加适当的IAM角色"
            ))
        
        # 检查监控
        if not config.get('detailed_monitoring', False):
            issues.append(SecurityIssue(
                resource_id=resource.id,
                issue_type="no_detailed_monitoring",
                description="EC2实例未启用详细监控",
                risk_level=RiskLevel.LOW,
                recommendation="启用详细监控以获得更好的性能洞察"
            ))
        
        return issues
    
    def _analyze_security_group(self, resource: CloudResource) -> List[SecurityIssue]:
        """分析安全组配置"""
        issues = []
        config = resource.config
        
        # 检查0.0.0.0/0规则
        rules = config.get('rules', [])
        for rule in rules:
            if rule.get('cidr') == '0.0.0.0/0' and rule.get('port') in [22, 3389]:
                issues.append(SecurityIssue(
                    resource_id=resource.id,
                    issue_type="wide_open_admin_port",
                    description=f"管理端口{rule.get('port')}对所有IP开放",
                    risk_level=RiskLevel.CRITICAL,
                    recommendation=f"限制端口{rule.get('port')}仅访问特定IP"
                ))
        
        return issues
    
    def _analyze_iam_security(self, resource: CloudResource) -> List[SecurityIssue]:
        """分析IAM安全配置"""
        issues = []
        config = resource.config
        
        # 检查管理员权限
        if config.get('has_admin_privileges', False):
            issues.append(SecurityIssue(
                resource_id=resource.id,
                issue_type="excessive_privileges",
                description="IAM用户/角色拥有管理员权限",
                risk_level=RiskLevel.HIGH,
                recommendation="遵循最小权限原则，仅授予必要权限"
            ))
        
        # 检查MFA
        if not config.get('mfa_enabled', False):
            issues.append(SecurityIssue(
                resource_id=resource.id,
                issue_type="no_mfa",
                description="IAM用户未启用多因素认证",
                risk_level=RiskLevel.HIGH,
                recommendation="为所有IAM用户启用MFA"
            ))
        
        # 检查访问密钥
        if config.get('has_access_keys', False) and config.get('key_age_days', 0) > 90:
            issues.append(SecurityIssue(
                resource_id=resource.id,
                issue_type="old_access_keys",
                description="访问密钥使用时间超过90天",
                risk_level=RiskLevel.MEDIUM,
                recommendation="定期轮换访问密钥"
            ))
        
        return issues
    
    def analyze_costs(self, resources: List[CloudResource]) -> List[CostIssue]:
        """分析成本配置"""
        issues = []
        
        for resource in resources:
            if resource.type == ResourceType.EC2:
                issues.extend(self._analyze_ec2_costs(resource))
            elif resource.type == ResourceType.S3:
                issues.extend(self._analyze_s3_costs(resource))
            elif resource.type == ResourceType.RDS:
                issues.extend(self._analyze_rds_costs(resource))
        
        return issues
    
    def _analyze_ec2_costs(self, resource: CloudResource) -> List[CostIssue]:
        """分析EC2成本"""
        issues = []
        config = resource.config
        
        # 检查实例类型
        instance_type = config.get('instance_type', '')
        if instance_type.startswith('t2') and config.get('environment') == 'production':
            issues.append(CostIssue(
                resource_id=resource.id,
                issue_type="burstable_instance_in_prod",
                description="生产环境使用突发性能实例",
                potential_savings=50.0,
                recommendation="在生产环境使用固定性能实例"
            ))
        
        # 检查利用率
        cpu_utilization = config.get('cpu_utilization', 0)
        if cpu_utilization < 10:
            issues.append(CostIssue(
                resource_id=resource.id,
                issue_type="low_utilization",
                description=f"EC2实例CPU利用率过低: {cpu_utilization}%",
                potential_savings=80.0,
                recommendation="考虑缩小实例规模或使用自动缩放"
            ))
        
        # 检查未使用实例
        if config.get('status') == 'stopped' and config.get('stopped_days', 0) > 7:
            issues.append(CostIssue(
                resource_id=resource.id,
                issue_type="unused_instance",
                description=f"EC2实例已停止{config.get('stopped_days')}天",
                potential_savings=100.0,
                recommendation="终止未使用的实例或使用实例计划"
            ))
        
        return issues
    
    def _analyze_s3_costs(self, resource: CloudResource) -> List[CostIssue]:
        """分析S3成本"""
        issues = []
        config = resource.config
        
        # 检查存储类别
        storage_class = config.get('storage_class', 'STANDARD')
        last_access_days = config.get('last_access_days', 0)
        
        if storage_class == 'STANDARD' and last_access_days > 30:
            issues.append(CostIssue(
                resource_id=resource.id,
                issue_type="infrequent_access",
                description="数据超过30天未访问但仍使用标准存储",
                potential_savings=40.0,
                recommendation="将不常访问的数据迁移到低频访问存储"
            ))
        
        # 检查生命周期策略
        if not config.get('lifecycle_policy_enabled', False):
            issues.append(CostIssue(
                resource_id=resource.id,
                issue_type="no_lifecycle_policy",
                description="S3存储桶未配置生命周期策略",
                potential_savings=60.0,
                recommendation="配置生命周期策略自动转换存储类别"
            ))
        
        return issues
    
    def _analyze_rds_costs(self, resource: CloudResource) -> List[CostIssue]:
        """分析RDS成本"""
        issues = []
        config = resource.config
        
        # 检查实例大小
        instance_size = config.get('instance_class', '')
        cpu_utilization = config.get('cpu_utilization', 0)
        
        if 'db.t3' in instance_size and cpu_utilization < 20:
            issues.append(CostIssue(
                resource_id=resource.id,
                issue_type="oversized_rds",
                description="RDS实例配置过大",
                potential_savings=40.0,
                recommendation="缩小RDS实例规模"
            ))
        
        # 检查多AZ
        if config.get('multi_az', False) and config.get('environment') == 'development':
            issues.append(CostIssue(
                resource_id=resource.id,
                issue_type="unnecessary_multi_az",
                description="开发环境启用了多AZ部署",
                potential_savings=50.0,
                recommendation="在开发环境禁用多AZ部署"
            ))
        
        return issues
    
    def analyze_compliance(self, resources: List[CloudResource]) -> List[ComplianceIssue]:
        """分析合规性"""
        issues = []
        
        for resource in resources:
            # GDPR合规检查
            if resource.tags.get('contains_pii', 'false').lower() == 'true':
                issues.extend(self._check_gdpr_compliance(resource))
            
            # HIPAA合规检查
            if resource.tags.get('contains_phi', 'false').lower() == 'true':
                issues.extend(self._check_hipaa_compliance(resource))
            
            # SOC 2合规检查
            if resource.tags.get('soc2_required', 'false').lower() == 'true':
                issues.extend(self._check_soc2_compliance(resource))
        
        return issues
    
    def _check_gdpr_compliance(self, resource: CloudResource) -> List[ComplianceIssue]:
        """检查GDPR合规性"""
        issues = []
        config = resource.config
        
        # 检查数据加密
        if not config.get('encryption_at_rest', False):
            issues.append(ComplianceIssue(
                resource_id=resource.id,
                standard="GDPR",
                requirement="Article 32 - Security of processing",
                status="NON_COMPLIANT",
                remediation="启用静态数据加密"
            ))
        
        # 检查数据位置
        if config.get('region') not in ['eu-west-1', 'eu-central-1', 'eu-west-2']:
            issues.append(ComplianceIssue(
                resource_id=resource.id,
                standard="GDPR",
                requirement="Article 45 - Transfers",
                status="NON_COMPLIANT",
                remediation="将个人数据存储在欧盟境内"
            ))
        
        return issues
    
    def _check_hipaa_compliance(self, resource: CloudResource) -> List[ComplianceIssue]:
        """检查HIPAA合规性"""
        issues = []
        config = resource.config
        
        # 检查访问控制
        if not config.get('access_controls_enabled', False):
            issues.append(ComplianceIssue(
                resource_id=resource.id,
                standard="HIPAA",
                requirement="164.312(a)(1) - Access Control",
                status="NON_COMPLIANT",
                remediation="实施适当的访问控制机制"
            ))
        
        # 检查审计日志
        if not config.get('audit_logging_enabled', False):
            issues.append(ComplianceIssue(
                resource_id=resource.id,
                standard="HIPAA",
                requirement="164.312(b) - Audit Controls",
                status="NON_COMPLIANT",
                remediation="启用详细的审计日志记录"
            ))
        
        return issues
    
    def _check_soc2_compliance(self, resource: CloudResource) -> List[ComplianceIssue]:
        """检查SOC 2合规性"""
        issues = []
        config = resource.config
        
        # 检查网络安全
        if not config.get('network_security_enabled', False):
            issues.append(ComplianceIssue(
                resource_id=resource.id,
                standard="SOC 2",
                requirement="CC6.1 - Logical Access Controls",
                status="NON_COMPLIANT",
                remediation="实施网络安全控制措施"
            ))
        
        return issues
    
    def generate_report(self, security_issues: List[SecurityIssue],
                       cost_issues: List[CostIssue],
                       compliance_issues: List[ComplianceIssue]) -> str:
        """生成分析报告"""
        report = ["=== 云配置分析报告 ===\n"]
        
        # 安全问题统计
        security_stats = {}
        for level in RiskLevel:
            count = len([issue for issue in security_issues if issue.risk_level == level])
            security_stats[level.value] = count
        
        report.append("=== 安全问题统计 ===")
        for level, count in security_stats.items():
            report.append(f"{level.upper()}: {count}")
        report.append(f"总计: {len(security_issues)}\n")
        
        # 成本节约统计
        total_savings = sum(issue.potential_savings for issue in cost_issues)
        report.append("=== 成本优化 ===")
        report.append(f"潜在月度节约: ${total_savings:.2f}")
        report.append(f"优化建议数: {len(cost_issues)}\n")
        
        # 合规性统计
        compliance_stats = {}
        for issue in compliance_issues:
            compliance_stats[issue.standard] = compliance_stats.get(issue.standard, 0) + 1
        
        report.append("=== 合规性检查 ===")
        for standard, count in compliance_stats.items():
            report.append(f"{standard}: {count} 个问题")
        report.append("")
        
        # 高优先级问题
        critical_issues = [issue for issue in security_issues if issue.risk_level == RiskLevel.CRITICAL]
        if critical_issues:
            report.append("=== 关键安全问题 ===")
            for issue in critical_issues:
                report.append(f"资源: {issue.resource_id}")
                report.append(f"问题: {issue.description}")
                report.append(f"建议: {issue.recommendation}")
                report.append("")
        
        # 高成本节约建议
        high_savings = sorted(cost_issues, key=lambda x: x.potential_savings, reverse=True)[:5]
        if high_savings:
            report.append("=== 高成本节约建议 ===")
            for issue in high_savings:
                report.append(f"资源: {issue.resource_id}")
                report.append(f"问题: {issue.description}")
                report.append(f"潜在节约: ${issue.potential_savings:.2f}/月")
                report.append(f"建议: {issue.recommendation}")
                report.append("")
        
        return '\n'.join(report)
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """加载安全规则"""
        return {
            's3': {
                'public_access_forbidden': True,
                'encryption_required': True,
                'versioning_required': True,
                'logging_required': True
            },
            'ec2': {
                'public_ports_restricted': True,
                'iam_role_required': True,
                'monitoring_required': True
            },
            'iam': {
                'mfa_required': True,
                'admin_privileges_restricted': True,
                'key_rotation_required': True
            }
        }
    
    def _load_cost_rules(self) -> Dict[str, Any]:
        """加载成本规则"""
        return {
            'ec2': {
                'min_cpu_utilization': 10,
                'max_stopped_days': 7,
                'burstable_in_prod_forbidden': True
            },
            's3': {
                'infrequent_access_threshold': 30,
                'lifecycle_policy_required': True
            },
            'rds': {
                'max_cpu_utilization': 80,
                'multi_az_dev_forbidden': True
            }
        }
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """加载合规规则"""
        return {
            'gdpr': {
                'encryption_required': True,
                'eu_regions_only': True,
                'data_retention_policy': True
            },
            'hipaa': {
                'access_controls_required': True,
                'audit_logging_required': True,
                'encryption_required': True
            },
            'soc2': {
                'network_security_required': True,
                'access_controls_required': True,
                'monitoring_required': True
            }
        }

# 使用示例
def main():
    analyzer = CloudConfigAnalyzer(CloudProvider.AWS)
    
    # 模拟云资源
    resources = [
        CloudResource(
            id="i-1234567890abcdef0",
            type=ResourceType.EC2,
            provider=CloudProvider.AWS,
            region="us-east-1",
            config={
                "public_ports": [22, 80],
                "iam_role_attached": False,
                "cpu_utilization": 5,
                "instance_type": "t2.micro"
            },
            tags={"environment": "production"},
            created_at=datetime.now()
        ),
        CloudResource(
            id="my-bucket-123",
            type=ResourceType.S3,
            provider=CloudProvider.AWS,
            region="us-east-1",
            config={
                "public_read": True,
                "encryption_enabled": False,
                "versioning_enabled": False
            },
            tags={},
            created_at=datetime.now()
        )
    ]
    
    # 分析安全
    security_issues = analyzer.analyze_security(resources)
    
    # 分析成本
    cost_issues = analyzer.analyze_costs(resources)
    
    # 分析合规性
    compliance_issues = analyzer.analyze_compliance(resources)
    
    # 生成报告
    report = analyzer.generate_report(security_issues, cost_issues, compliance_issues)
    print(report)

if __name__ == "__main__":
    main()
```

### 云配置监控器
```python
import time
import threading
from typing import Dict, List, Any
import schedule

class CloudConfigMonitor:
    """云配置监控器"""
    
    def __init__(self, analyzer: CloudConfigAnalyzer):
        self.analyzer = analyzer
        self.monitoring = False
        self.alert_thresholds = {
            'critical_issues': 0,
            'high_risk_issues': 5,
            'cost_savings_threshold': 100.0
        }
    
    def start_monitoring(self, interval_minutes: int = 60):
        """开始监控"""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    self.run_monitoring_cycle()
                except Exception as e:
                    print(f"监控错误: {str(e)}")
                
                time.sleep(interval_minutes * 60)
        
        thread = threading.Thread(target=monitor_loop)
        thread.daemon = True
        thread.start()
        print(f"云配置监控已启动，检查间隔: {interval_minutes}分钟")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        print("云配置监控已停止")
    
    def run_monitoring_cycle(self):
        """运行监控周期"""
        print(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 开始监控周期 ===")
        
        # 获取当前资源
        resources = self._get_current_resources()
        
        # 运行分析
        security_issues = self.analyzer.analyze_security(resources)
        cost_issues = self.analyzer.analyze_costs(resources)
        compliance_issues = self.analyzer.analyze_compliance(resources)
        
        # 检查告警条件
        self._check_alerts(security_issues, cost_issues, compliance_issues)
        
        # 记录指标
        self._record_metrics(security_issues, cost_issues, compliance_issues)
    
    def _get_current_resources(self) -> List[CloudResource]:
        """获取当前云资源"""
        # 这里应该调用云API获取实际资源
        # 为了演示，返回模拟数据
        return []
    
    def _check_alerts(self, security_issues: List[SecurityIssue],
                     cost_issues: List[CostIssue],
                     compliance_issues: List[ComplianceIssue]):
        """检查告警条件"""
        # 检查关键安全问题
        critical_count = len([issue for issue in security_issues if issue.risk_level == RiskLevel.CRITICAL])
        if critical_count > self.alert_thresholds['critical_issues']:
            self._send_alert("CRITICAL", f"发现 {critical_count} 个关键安全问题")
        
        # 检查高风险问题
        high_count = len([issue for issue in security_issues if issue.risk_level == RiskLevel.HIGH])
        if high_count > self.alert_thresholds['high_risk_issues']:
            self._send_alert("WARNING", f"发现 {high_count} 个高风险安全问题")
        
        # 检查成本节约机会
        total_savings = sum(issue.potential_savings for issue in cost_issues)
        if total_savings > self.alert_thresholds['cost_savings_threshold']:
            self._send_alert("INFO", f"发现 ${total_savings:.2f} 的成本节约机会")
        
        # 检查合规问题
        if compliance_issues:
            self._send_alert("COMPLIANCE", f"发现 {len(compliance_issues)} 个合规问题")
    
    def _send_alert(self, level: str, message: str):
        """发送告警"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
        
        # 这里可以集成实际的告警系统
        # 例如发送邮件、Slack通知、PagerDuty等
    
    def _record_metrics(self, security_issues: List[SecurityIssue],
                       cost_issues: List[CostIssue],
                       compliance_issues: List[ComplianceIssue]):
        """记录指标"""
        metrics = {
            'timestamp': datetime.now(),
            'security_issues_count': len(security_issues),
            'critical_issues_count': len([issue for issue in security_issues if issue.risk_level == RiskLevel.CRITICAL]),
            'high_issues_count': len([issue for issue in security_issues if issue.risk_level == RiskLevel.HIGH]),
            'cost_savings_total': sum(issue.potential_savings for issue in cost_issues),
            'compliance_issues_count': len(compliance_issues)
        }
        
        # 这里可以发送到监控系统
        print(f"指标记录: {metrics}")

# 使用示例
def main():
    analyzer = CloudConfigAnalyzer(CloudProvider.AWS)
    monitor = CloudConfigMonitor(analyzer)
    
    # 启动监控
    monitor.start_monitoring(interval_minutes=30)
    
    try:
        # 保持运行
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()
```

## 云配置最佳实践

### 安全配置
1. **最小权限**: 仅授予必要的权限
2. **默认加密**: 启用所有数据的默认加密
3. **网络隔离**: 使用VPC和安全组隔离资源
4. **定期审计**: 定期检查和更新安全配置

### 成本优化
1. **合适规模**: 根据实际需求选择资源规模
2. **自动缩放**: 使用自动缩放应对负载变化
3. **预留实例**: 对稳定工作负载使用预留实例
4. **生命周期管理**: 自动清理闲置资源

### 合规管理
1. **数据分类**: 根据敏感度分类数据
2. **区域限制**: 确保数据存储在合规区域
3. **访问日志**: 记录所有访问和修改
4. **定期评估**: 定期评估合规状态

## 相关技能

- **infrastructure-as-code** - 基础设施即代码
- **cloud-security** - 云安全
- **cost-optimization** - 成本优化
- **compliance-management** - 合规管理
