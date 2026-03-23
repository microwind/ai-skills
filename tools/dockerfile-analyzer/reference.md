# Dockerfile分析器参考文档

## Dockerfile分析器概述

### 什么是Dockerfile分析器
Dockerfile分析器是一个专门用于分析Dockerfile文件的工具，它能够检查Dockerfile的安全性、性能、最佳实践合规性，并提供优化建议。该工具支持多种分析维度，包括基础镜像检查、指令分析、依赖关系分析、安全漏洞扫描等。

### 主要功能
- **Dockerfile解析**: 完整解析Dockerfile语法和结构
- **安全分析**: 检测安全漏洞、敏感信息泄露、权限配置问题
- **性能分析**: 分析镜像大小、构建时间、运行时性能
- **最佳实践检查**: 检查Dockerfile是否符合行业最佳实践
- **依赖分析**: 分析包依赖、层依赖、服务依赖关系
- **报告生成**: 生成详细的分析报告和可视化图表

## Dockerfile解析

### 基础解析器
```python
# dockerfile_parser.py
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class InstructionType(Enum):
    FROM = "FROM"
    RUN = "RUN"
    CMD = "CMD"
    LABEL = "LABEL"
    EXPOSE = "EXPOSE"
    ENV = "ENV"
    ADD = "ADD"
    COPY = "COPY"
    ENTRYPOINT = "ENTRYPOINT"
    VOLUME = "VOLUME"
    USER = "USER"
    WORKDIR = "WORKDIR"
    ARG = "ARG"
    ONBUILD = "ONBUILD"
    STOPSIGNAL = "STOPSIGNAL"
    HEALTHCHECK = "HEALTHCHECK"
    SHELL = "SHELL"

@dataclass
class DockerfileInstruction:
    instruction: str
    arguments: List[str]
    line_number: int
    raw_line: str
    comment: Optional[str] = None

@dataclass
class DockerfileInfo:
    instructions: List[DockerfileInstruction]
    stages: List[str]
    variables: Dict[str, str]
    exposed_ports: List[int]
    volumes: List[str]
    from_images: List[str]

class DockerfileParser:
    def __init__(self):
        self.instruction_pattern = re.compile(r'^\s*(?P<instruction>[A-Z]+)\s+(?P<arguments>.+?)(?:\s+#\s*(?P<comment>.*))?\s*$')
        self.comment_pattern = re.compile(r'^\s*#\s*(?P<comment>.*)$')
        self.continuation_pattern = re.compile(r'\\\s*$')
        self.env_pattern = re.compile(r'^(?P<key>\w+)=(?P<value>.+)$')
        self.arg_pattern = re.compile(r'^(?P<key>\w+)(?:=(?P<value>.+))?$')
    
    def parse_dockerfile(self, dockerfile_path: str) -> DockerfileInfo:
        """解析Dockerfile"""
        try:
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self._parse_content(content)
            
        except Exception as e:
            raise ValueError(f"解析Dockerfile失败: {e}")
    
    def parse_dockerfile_content(self, content: str) -> DockerfileInfo:
        """解析Dockerfile内容"""
        return self._parse_content(content)
    
    def _parse_content(self, content: str) -> DockerfileInfo:
        """解析Dockerfile内容"""
        lines = content.split('\n')
        instructions = []
        current_instruction = None
        continuation_lines = []
        
        for line_num, line in enumerate(lines, 1):
            # 处理注释行
            comment_match = self.comment_pattern.match(line)
            if comment_match:
                if current_instruction:
                    current_instruction.comment = comment_match.group('comment')
                continue
            
            # 处理空行
            if not line.strip():
                if current_instruction:
                    instructions.append(current_instruction)
                    current_instruction = None
                continue
            
            # 处理续行
            if self.continuation_pattern.search(line):
                if current_instruction:
                    continuation_lines.append(line.rstrip('\\'))
                else:
                    # 开始新的指令
                    instruction_match = self.instruction_pattern.match(line)
                    if instruction_match:
                        current_instruction = DockerfileInstruction(
                            instruction=instruction_match.group('instruction'),
                            arguments=[instruction_match.group('arguments').rstrip('\\')],
                            line_number=line_num,
                            raw_line=line
                        )
                continue
            
            # 处理普通指令行
            if continuation_lines:
                # 这是续行的结束
                if current_instruction:
                    current_instruction.arguments.append(line.strip())
                    current_instruction.arguments = [''.join(continuation_lines + [line.strip()])]
                    instructions.append(current_instruction)
                    current_instruction = None
                    continuation_lines = []
            else:
                # 新的指令
                if current_instruction:
                    instructions.append(current_instruction)
                
                instruction_match = self.instruction_pattern.match(line)
                if instruction_match:
                    current_instruction = DockerfileInstruction(
                        instruction=instruction_match.group('instruction'),
                        arguments=[instruction_match.group('arguments')],
                        line_number=line_num,
                        raw_line=line,
                        comment=instruction_match.group('comment')
                    )
                else:
                    # 无效的指令行
                    raise ValueError(f"第{line_num}行: 无效的指令格式")
        
        # 添加最后一个指令
        if current_instruction:
            instructions.append(current_instruction)
        
        # 分析Dockerfile信息
        return self._analyze_dockerfile_info(instructions)
    
    def _analyze_dockerfile_info(self, instructions: List[DockerfileInstruction]) -> DockerfileInfo:
        """分析Dockerfile信息"""
        stages = []
        variables = {}
        exposed_ports = []
        volumes = []
        from_images = []
        
        for instruction in instructions:
            if instruction.instruction == InstructionType.FROM.value:
                # 解析FROM指令
                from_image = instruction.arguments[0].split()[0]
                from_images.append(from_image)
                
                # 检查是否是多阶段构建
                if len(instruction.arguments) > 1 and instruction.arguments[1] == "as":
                    stage_name = instruction.arguments[2] if len(instruction.arguments) > 2 else f"stage{len(stages)}"
                    stages.append(stage_name)
            
            elif instruction.instruction == InstructionType.ENV.value:
                # 解析ENV指令
                for arg in instruction.arguments:
                    env_match = self.env_pattern.match(arg)
                    if env_match:
                        variables[env_match.group('key')] = env_match.group('value')
            
            elif instruction.instruction == InstructionType.ARG.value:
                # 解析ARG指令
                for arg in instruction.arguments:
                    arg_match = self.arg_pattern.match(arg)
                    if arg_match:
                        key = arg_match.group('key')
                        value = arg_match.group('value') or ''
                        variables[key] = f"${{{key}}}" + (f":{value}" if value else "")
            
            elif instruction.instruction == InstructionType.EXPOSE.value:
                # 解析EXPOSE指令
                for arg in instruction.arguments:
                    ports = arg.split()
                    for port in ports:
                        try:
                            if '/' in port:
                                port_num = int(port.split('/')[0])
                            else:
                                port_num = int(port)
                            if port_num not in exposed_ports:
                                exposed_ports.append(port_num)
                        except ValueError:
                            continue
            
            elif instruction.instruction == InstructionType.VOLUME.value:
                # 解析VOLUME指令
                for arg in instruction.arguments:
                    # 移除方括号
                    volume_path = arg.strip('[]')
                    if volume_path not in volumes:
                        volumes.append(volume_path)
        
        return DockerfileInfo(
            instructions=instructions,
            stages=stages,
            variables=variables,
            exposed_ports=exposed_ports,
            volumes=volumes,
            from_images=from_images
        )

# 使用示例
parser = DockerfileParser()

# 解析Dockerfile
try:
    dockerfile_info = parser.parse_dockerfile('Dockerfile')
    print(f"解析成功，共{len(dockerfile_info.instructions)}条指令")
    print(f"基础镜像: {dockerfile_info.from_images}")
    print(f"构建阶段: {dockerfile_info.stages}")
    print(f"环境变量: {dockerfile_info.variables}")
    print(f"暴露端口: {dockerfile_info.exposed_ports}")
except Exception as e:
    print(f"解析失败: {e}")
```

### 指令分析器
```python
# instruction_analyzer.py
from typing import Dict, List, Any, Optional
from dockerfile_parser import DockerfileInfo, DockerfileInstruction, InstructionType

class InstructionAnalyzer:
    def __init__(self):
        self.security_patterns = {
            'sensitive_commands': [
                'password', 'passwd', 'pwd',
                'secret', 'key', 'token',
                'credential', 'auth',
                'private', 'confidential'
            ],
            'dangerous_commands': [
                'chmod 777', 'chmod -R 777',
                'sudo', 'su',
                'wget', 'curl',
                'rm -rf', 'sudo rm'
            ],
            'insecure_protocols': [
                'http://', 'ftp://',
                'telnet://', 'rsync://'
            ]
        }
        
        self.optimization_patterns = {
            'cache_breakers': [
                'apt-get update', 'yum update',
                'pip install', 'npm install',
                'git clone', 'wget'
            ],
            'cleanup_commands': [
                'apt-get clean', 'yum clean',
                'rm -rf /var/lib/apt/lists/*',
                'npm cache clean'
            ]
        }
    
    def analyze_instructions(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """分析Dockerfile指令"""
        analysis = {
            'instruction_analysis': self._analyze_instruction_types(dockerfile_info),
            'security_analysis': self._analyze_security(dockerfile_info),
            'optimization_analysis': self._analyze_optimization(dockerfile_info),
            'best_practices': self._analyze_best_practices(dockerfile_info),
            'layer_analysis': self._analyze_layers(dockerfile_info)
        }
        
        return analysis
    
    def _analyze_instruction_types(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """分析指令类型分布"""
        instruction_counts = {}
        instruction_details = {}
        
        for instruction in dockerfile_info.instructions:
            inst_type = instruction.instruction
            instruction_counts[inst_type] = instruction_counts.get(inst_type, 0) + 1
            
            if inst_type not in instruction_details:
                instruction_details[inst_type] = []
            
            instruction_details[inst_type].append({
                'line': instruction.line_number,
                'arguments': instruction.arguments,
                'comment': instruction.comment
            })
        
        return {
            'instruction_counts': instruction_counts,
            'instruction_details': instruction_details,
            'total_instructions': len(dockerfile_info.instructions)
        }
    
    def _analyze_security(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """安全性分析"""
        security_issues = []
        security_score = 100
        
        for instruction in dockerfile_info.instructions:
            # 检查敏感信息
            if instruction.instruction in ['RUN', 'ENV', 'ARG']:
                for arg in instruction.arguments:
                    for pattern in self.security_patterns['sensitive_commands']:
                        if pattern.lower() in arg.lower():
                            security_issues.append({
                                'type': 'sensitive_information',
                                'severity': 'high',
                                'line': instruction.line_number,
                                'instruction': instruction.instruction,
                                'pattern': pattern,
                                'content': arg,
                                'message': f'可能包含敏感信息: {pattern}'
                            })
                            security_score -= 20
            
            # 检查危险命令
            if instruction.instruction == 'RUN':
                for arg in instruction.arguments:
                    for dangerous in self.security_patterns['dangerous_commands']:
                        if dangerous in arg:
                            security_issues.append({
                                'type': 'dangerous_command',
                                'severity': 'medium',
                                'line': instruction.line_number,
                                'instruction': instruction.instruction,
                                'command': dangerous,
                                'content': arg,
                                'message': f'使用危险命令: {dangerous}'
                            })
                            security_score -= 10
            
            # 检查不安全协议
            for arg in instruction.arguments:
                for protocol in self.security_patterns['insecure_protocols']:
                    if protocol in arg.lower():
                        security_issues.append({
                            'type': 'insecure_protocol',
                            'severity': 'medium',
                            'line': instruction.line_number,
                            'instruction': instruction.instruction,
                            'protocol': protocol,
                            'content': arg,
                            'message': f'使用不安全协议: {protocol}'
                        })
                        security_score -= 15
        
        # 检查用户权限
        user_instructions = [inst for inst in dockerfile_info.instructions if inst.instruction == 'USER']
        if not user_instructions:
            security_issues.append({
                'type': 'root_user',
                'severity': 'high',
                'line': 0,
                'instruction': 'USER',
                'message': '未设置非root用户运行'
            })
            security_score -= 25
        
        return {
            'security_score': max(0, security_score),
            'security_issues': security_issues,
            'recommendations': self._get_security_recommendations(security_issues)
        }
    
    def _analyze_optimization(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """优化分析"""
        optimization_issues = []
        optimization_score = 100
        
        # 检查缓存优化
        cache_breakers_found = []
        cleanup_commands_found = []
        
        for instruction in dockerfile_info.instructions:
            if instruction.instruction == 'RUN':
                for arg in instruction.arguments:
                    # 检查缓存破坏者
                    for breaker in self.optimization_patterns['cache_breakers']:
                        if breaker in arg:
                            cache_breakers_found.append({
                                'line': instruction.line_number,
                                'command': breaker,
                                'content': arg
                            })
                    
                    # 检查清理命令
                    for cleanup in self.optimization_patterns['cleanup_commands']:
                        if cleanup in arg:
                            cleanup_commands_found.append({
                                'line': instruction.line_number,
                                'command': cleanup,
                                'content': arg
                            })
        
        # 检查是否有多阶段构建
        multi_stage = len(dockerfile_info.stages) > 1
        if not multi_stage:
            optimization_issues.append({
                'type': 'single_stage',
                'severity': 'medium',
                'line': 0,
                'message': '未使用多阶段构建，镜像可能较大'
            })
            optimization_score -= 15
        
        # 检查RUN指令合并
        run_instructions = [inst for inst in dockerfile_info.instructions if inst.instruction == 'RUN']
        if len(run_instructions) > 3:
            optimization_issues.append({
                'type': 'run_instructions_not_merged',
                'severity': 'low',
                'line': 0,
                'count': len(run_instructions),
                'message': f'发现{len(run_instructions)}个RUN指令，建议合并以减少层数'
            })
            optimization_score -= 5
        
        # 检查COPY指令顺序
        copy_instructions = [inst for inst in dockerfile_info.instructions if inst.instruction == 'COPY']
        run_instructions = [inst for inst in dockerfile_info.instructions if inst.instruction == 'RUN']
        
        if copy_instructions and run_instructions:
            first_copy_line = min(inst.line_number for inst in copy_instructions)
            last_run_line = max(inst.line_number for inst in run_instructions)
            
            if first_copy_line < last_run_line:
                optimization_issues.append({
                    'type': 'copy_order',
                    'severity': 'low',
                    'line': first_copy_line,
                    'message': 'COPY指令在RUN指令之前，可能影响缓存效率'
                })
                optimization_score -= 5
        
        return {
            'optimization_score': max(0, optimization_score),
            'optimization_issues': optimization_issues,
            'cache_breakers': cache_breakers_found,
            'cleanup_commands': cleanup_commands_found,
            'multi_stage_build': multi_stage,
            'recommendations': self._get_optimization_recommendations(optimization_issues)
        }
    
    def _analyze_best_practices(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """最佳实践分析"""
        best_practice_issues = []
        best_practice_score = 100
        
        # 检查FROM指令
        from_instructions = [inst for inst in dockerfile_info.instructions if inst.instruction == 'FROM']
        for inst in from_instructions:
            for arg in inst.arguments:
                if 'latest' in arg.lower():
                    best_practice_issues.append({
                        'type': 'latest_tag',
                        'severity': 'medium',
                        'line': inst.line_number,
                        'instruction': 'FROM',
                        'content': arg,
                        'message': '使用latest标签，可能导致构建不一致'
                    })
                    best_practice_score -= 10
        
        # 检查LABEL指令
        label_instructions = [inst for inst in dockerfile_info.instructions if inst.instruction == 'LABEL']
        if not label_instructions:
            best_practice_issues.append({
                'type': 'missing_label',
                'severity': 'low',
                'line': 0,
                'instruction': 'LABEL',
                'message': '缺少LABEL指令，建议添加维护者信息'
            })
            best_practice_score -= 5
        
        # 检查EXPOSE指令
        if not dockerfile_info.exposed_ports:
            best_practice_issues.append({
                'type': 'missing_expose',
                'severity': 'low',
                'line': 0,
                'instruction': 'EXPOSE',
                'message': '缺少EXPOSE指令，建议明确暴露端口'
            })
            best_practice_score -= 5
        
        # 检查WORKDIR指令
        workdir_instructions = [inst for inst in dockerfile_info.instructions if inst.instruction == 'WORKDIR']
        if not workdir_instructions:
            best_practice_issues.append({
                'type': 'missing_workdir',
                'severity': 'low',
                'line': 0,
                'instruction': 'WORKDIR',
                'message': '缺少WORKDIR指令，建议设置工作目录'
            })
            best_practice_score -= 5
        
        # 检查ADD vs COPY
        add_instructions = [inst for inst in dockerfile_info.instructions if inst.instruction == 'ADD']
        for inst in add_instructions:
            for arg in inst.arguments:
                if not any(url in arg for url in ['http://', 'https://', 'ftp://']):
                    best_practice_issues.append({
                        'type': 'add_vs_copy',
                        'severity': 'low',
                        'line': inst.line_number,
                        'instruction': 'ADD',
                        'content': arg,
                        'message': '使用ADD指令复制本地文件，建议使用COPY'
                    })
                    best_practice_score -= 3
        
        return {
            'best_practice_score': max(0, best_practice_score),
            'best_practice_issues': best_practice_issues,
            'recommendations': self._get_best_practice_recommendations(best_practice_issues)
        }
    
    def _analyze_layers(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """层分析"""
        layer_info = []
        
        for instruction in dockerfile_info.instructions:
            layer_size_estimate = self._estimate_layer_size(instruction)
            
            layer_info.append({
                'instruction': instruction.instruction,
                'line': instruction.line_number,
                'arguments': instruction.arguments,
                'estimated_size': layer_size_estimate,
                'cache_impact': self._assess_cache_impact(instruction)
            })
        
        # 计算总层数
        total_layers = len(layer_info)
        
        # 分析层分布
        layer_distribution = {}
        for layer in layer_info:
            inst_type = layer['instruction']
            layer_distribution[inst_type] = layer_distribution.get(inst_type, 0) + 1
        
        return {
            'total_layers': total_layers,
            'layer_distribution': layer_distribution,
            'layer_details': layer_info,
            'layer_optimization_suggestions': self._get_layer_optimization_suggestions(layer_info)
        }
    
    def _estimate_layer_size(self, instruction: DockerfileInstruction) -> str:
        """估算层大小"""
        if instruction.instruction == 'FROM':
            return 'large'
        elif instruction.instruction == 'RUN':
            # 检查是否包含包安装
            for arg in instruction.arguments:
                if any(cmd in arg for cmd in ['apt-get', 'yum', 'apk', 'pip', 'npm']):
                    return 'medium-large'
            return 'medium'
        elif instruction.instruction in ['COPY', 'ADD']:
            return 'medium'
        elif instruction.instruction in ['ENV', 'ARG', 'LABEL', 'EXPOSE']:
            return 'small'
        else:
            return 'small'
    
    def _assess_cache_impact(self, instruction: DockerfileInstruction) -> str:
        """评估缓存影响"""
        if instruction.instruction == 'FROM':
            return 'high'
        elif instruction.instruction == 'RUN':
            for arg in instruction.arguments:
                if any(breaker in arg for breaker in self.optimization_patterns['cache_breakers']):
                    return 'high'
            return 'medium'
        elif instruction.instruction in ['COPY', 'ADD']:
            return 'medium'
        else:
            return 'low'
    
    def _get_security_recommendations(self, issues: List[Dict]) -> List[str]:
        """获取安全建议"""
        recommendations = []
        
        if any(issue['type'] == 'sensitive_information' for issue in issues):
            recommendations.append('避免在Dockerfile中硬编码敏感信息，使用环境变量或密钥管理')
        
        if any(issue['type'] == 'root_user' for issue in issues):
            recommendations.append('使用非root用户运行容器，添加USER指令')
        
        if any(issue['type'] == 'dangerous_command' for issue in issues):
            recommendations.append('谨慎使用危险命令，确保操作安全')
        
        if any(issue['type'] == 'insecure_protocol' for issue in issues):
            recommendations.append('使用安全的协议（HTTPS）替代不安全协议')
        
        return recommendations
    
    def _get_optimization_recommendations(self, issues: List[Dict]) -> List[str]:
        """获取优化建议"""
        recommendations = []
        
        if any(issue['type'] == 'single_stage' for issue in issues):
            recommendations.append('使用多阶段构建减少最终镜像大小')
        
        if any(issue['type'] == 'run_instructions_not_merged' for issue in issues):
            recommendations.append('合并相关的RUN指令以减少层数')
        
        if any(issue['type'] == 'copy_order' for issue in issues):
            recommendations.append('将COPY指令放在依赖安装之后，提高缓存效率')
        
        return recommendations
    
    def _get_best_practice_recommendations(self, issues: List[Dict]) -> List[str]:
        """获取最佳实践建议"""
        recommendations = []
        
        if any(issue['type'] == 'latest_tag' for issue in issues):
            recommendations.append('使用具体的版本标签而非latest标签')
        
        if any(issue['type'] == 'missing_label' for issue in issues):
            recommendations.append('添加LABEL指令，包含维护者信息')
        
        if any(issue['type'] == 'missing_expose' for issue in issues):
            recommendations.append('使用EXPOSE指令明确暴露端口')
        
        if any(issue['type'] == 'missing_workdir' for issue in issues):
            recommendations.append('使用WORKDIR指令设置工作目录')
        
        if any(issue['type'] == 'add_vs_copy' for issue in issues):
            recommendations.append('对于本地文件复制，使用COPY而非ADD')
        
        return recommendations
    
    def _get_layer_optimization_suggestions(self, layer_info: List[Dict]) -> List[str]:
        """获取层优化建议"""
        suggestions = []
        
        run_layers = [layer for layer in layer_info if layer['instruction'] == 'RUN']
        if len(run_layers) > 5:
            suggestions.append('RUN指令较多，考虑合并相关操作')
        
        large_layers = [layer for layer in layer_info if layer['estimated_size'] in ['large', 'medium-large']]
        if len(large_layers) > 3:
            suggestions.append('大层数量较多，考虑使用多阶段构建优化')
        
        return suggestions

# 使用示例
analyzer = InstructionAnalyzer()

# 分析Dockerfile
try:
    dockerfile_info = parser.parse_dockerfile('Dockerfile')
    analysis_result = analyzer.analyze_instructions(dockerfile_info)
    
    print("指令分析结果:")
    print(f"安全分数: {analysis_result['security_analysis']['security_score']}")
    print(f"优化分数: {analysis_result['optimization_analysis']['optimization_score']}")
    print(f"最佳实践分数: {analysis_result['best_practices']['best_practice_score']}")
    print(f"总层数: {analysis_result['layer_analysis']['total_layers']}")
    
except Exception as e:
    print(f"分析失败: {e}")
```

## 安全分析

### 安全扫描器
```python
# security_scanner.py
import re
import hashlib
from typing import Dict, List, Any, Optional, Set
from dockerfile_parser import DockerfileInfo, DockerfileInstruction

class SecurityScanner:
    def __init__(self):
        self.vulnerability_database = self._load_vulnerability_database()
        self.sensitive_patterns = self._load_sensitive_patterns()
        self.insecure_commands = self._load_insecure_commands()
        self.cis_benchmarks = self._load_cis_benchmarks()
    
    def scan_security(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """执行安全扫描"""
        scan_results = {
            'vulnerability_scan': self._scan_vulnerabilities(dockerfile_info),
            'sensitive_data_scan': self._scan_sensitive_data(dockerfile_info),
            'insecure_commands_scan': self._scan_insecure_commands(dockerfile_info),
            'cis_benchmark_scan': self._scan_cis_benchmarks(dockerfile_info),
            'security_score': 0,
            'risk_level': 'low',
            'recommendations': []
        }
        
        # 计算总体安全分数
        total_score = 0
        score_count = 0
        
        for scan_type, result in scan_results.items():
            if scan_type in ['vulnerability_scan', 'sensitive_data_scan', 'insecure_commands_scan', 'cis_benchmark_scan']:
                if 'score' in result:
                    total_score += result['score']
                    score_count += 1
        
        if score_count > 0:
            scan_results['security_score'] = total_score / score_count
        
        # 确定风险级别
        score = scan_results['security_score']
        if score >= 80:
            scan_results['risk_level'] = 'low'
        elif score >= 60:
            scan_results['risk_level'] = 'medium'
        else:
            scan_results['risk_level'] = 'high'
        
        # 生成综合建议
        scan_results['recommendations'] = self._generate_security_recommendations(scan_results)
        
        return scan_results
    
    def _scan_vulnerabilities(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """扫描漏洞"""
        vulnerabilities = []
        score = 100
        
        # 扫描基础镜像漏洞
        for image in dockerfile_info.from_images:
            image_vulns = self._check_image_vulnerabilities(image)
            vulnerabilities.extend(image_vulns)
        
        # 扫描包依赖漏洞
        package_vulns = self._scan_package_dependencies(dockerfile_info)
        vulnerabilities.extend(package_vulns)
        
        # 计算分数
        for vuln in vulnerabilities:
            if vuln['severity'] == 'critical':
                score -= 30
            elif vuln['severity'] == 'high':
                score -= 20
            elif vuln['severity'] == 'medium':
                score -= 10
            elif vuln['severity'] == 'low':
                score -= 5
        
        return {
            'vulnerabilities': vulnerabilities,
            'score': max(0, score),
            'total_vulnerabilities': len(vulnerabilities),
            'critical_count': len([v for v in vulnerabilities if v['severity'] == 'critical']),
            'high_count': len([v for v in vulnerabilities if v['severity'] == 'high']),
            'medium_count': len([v for v in vulnerabilities if v['severity'] == 'medium']),
            'low_count': len([v for v in vulnerabilities if v['severity'] == 'low'])
        }
    
    def _scan_sensitive_data(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """扫描敏感数据"""
        sensitive_findings = []
        score = 100
        
        for instruction in dockerfile_info.instructions:
            # 检查环境变量中的敏感信息
            if instruction.instruction in ['ENV', 'ARG']:
                for arg in instruction.arguments:
                    for pattern_name, pattern in self.sensitive_patterns.items():
                        matches = re.finditer(pattern, arg, re.IGNORECASE)
                        for match in matches:
                            sensitive_findings.append({
                                'type': 'sensitive_data',
                                'pattern': pattern_name,
                                'line': instruction.line_number,
                                'instruction': instruction.instruction,
                                'content': arg,
                                'matched_text': match.group(),
                                'severity': 'high'
                            })
                            score -= 15
            
            # 检查RUN命令中的敏感信息
            elif instruction.instruction == 'RUN':
                for arg in instruction.arguments:
                    for pattern_name, pattern in self.sensitive_patterns.items():
                        matches = re.finditer(pattern, arg, re.IGNORECASE)
                        for match in matches:
                            sensitive_findings.append({
                                'type': 'sensitive_data',
                                'pattern': pattern_name,
                                'line': instruction.line_number,
                                'instruction': instruction.instruction,
                                'content': arg,
                                'matched_text': match.group(),
                                'severity': 'medium'
                            })
                            score -= 10
        
        return {
            'sensitive_findings': sensitive_findings,
            'score': max(0, score),
            'total_findings': len(sensitive_findings)
        }
    
    def _scan_insecure_commands(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """扫描不安全命令"""
        insecure_findings = []
        score = 100
        
        for instruction in dockerfile_info.instructions:
            if instruction.instruction == 'RUN':
                for arg in instruction.arguments:
                    for command_name, command_info in self.insecure_commands.items():
                        if command_info['pattern'].search(arg):
                            insecure_findings.append({
                                'type': 'insecure_command',
                                'command': command_name,
                                'line': instruction.line_number,
                                'instruction': instruction.instruction,
                                'content': arg,
                                'severity': command_info['severity'],
                                'description': command_info['description']
                            })
                            score -= command_info['score_penalty']
        
        return {
            'insecure_findings': insecure_findings,
            'score': max(0, score),
            'total_findings': len(insecure_findings)
        }
    
    def _scan_cis_benchmarks(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """扫描CIS基准"""
        benchmark_findings = []
        score = 100
        
        for benchmark_id, benchmark in self.cis_benchmarks.items():
            if benchmark['check_function'](dockerfile_info):
                benchmark_findings.append({
                    'type': 'cis_benchmark',
                    'benchmark_id': benchmark_id,
                    'title': benchmark['title'],
                    'description': benchmark['description'],
                    'severity': benchmark['severity'],
                    'remediation': benchmark['remediation']
                })
                score -= benchmark['score_penalty']
        
        return {
            'benchmark_findings': benchmark_findings,
            'score': max(0, score),
            'total_findings': len(benchmark_findings)
        }
    
    def _check_image_vulnerabilities(self, image: str) -> List[Dict]:
        """检查镜像漏洞"""
        vulnerabilities = []
        
        # 这里应该调用实际的漏洞数据库API
        # 为了演示，我们使用模拟数据
        mock_vulnerabilities = {
            'ubuntu:18.04': [
                {
                    'cve_id': 'CVE-2021-3711',
                    'severity': 'high',
                    'description': 'OpenSSL vulnerability',
                    'package': 'openssl',
                    'fixed_version': '1.1.1f-1ubuntu2.8'
                }
            ],
            'alpine:3.12': [
                {
                    'cve_id': 'CVE-2021-36084',
                    'severity': 'medium',
                    'description': 'BusyBox vulnerability',
                    'package': 'busybox',
                    'fixed_version': '1.32.1-r6'
                }
            ]
        }
        
        if image in mock_vulnerabilities:
            for vuln in mock_vulnerabilities[image]:
                vulnerabilities.append({
                    'type': 'image_vulnerability',
                    'image': image,
                    **vuln
                })
        
        return vulnerabilities
    
    def _scan_package_dependencies(self, dockerfile_info: DockerfileInfo) -> List[Dict]:
        """扫描包依赖漏洞"""
        vulnerabilities = []
        
        for instruction in dockerfile_info.instructions:
            if instruction.instruction == 'RUN':
                for arg in instruction.arguments:
                    # 检查apt-get安装的包
                    if 'apt-get install' in arg:
                        packages = self._extract_packages_from_apt(arg)
                        for package in packages:
                            package_vulns = self._check_package_vulnerabilities(package, 'apt')
                            vulnerabilities.extend(package_vulns)
                    
                    # 检查pip安装的包
                    elif 'pip install' in arg:
                        packages = self._extract_packages_from_pip(arg)
                        for package in packages:
                            package_vulns = self._check_package_vulnerabilities(package, 'pip')
                            vulnerabilities.extend(package_vulns)
        
        return vulnerabilities
    
    def _extract_packages_from_apt(self, command: str) -> List[str]:
        """从apt命令中提取包名"""
        packages = []
        # 简化的包名提取逻辑
        if 'apt-get install' in command:
            install_part = command.split('apt-get install')[1]
            # 移除常见的选项
            install_part = re.sub(r'-y|--yes|--assume-yes', '', install_part)
            packages = [pkg.strip() for pkg in install_part.split() if pkg.strip() and not pkg.startswith('-')]
        
        return packages
    
    def _extract_packages_from_pip(self, command: str) -> List[str]:
        """从pip命令中提取包名"""
        packages = []
        if 'pip install' in command:
            install_part = command.split('pip install')[1]
            packages = [pkg.strip() for pkg in install_part.split() if pkg.strip() and not pkg.startswith('-')]
        
        return packages
    
    def _check_package_vulnerabilities(self, package: str, manager: str) -> List[Dict]:
        """检查包漏洞"""
        vulnerabilities = []
        
        # 模拟漏洞数据
        mock_package_vulns = {
            'apt': {
                'curl': [
                    {
                        'cve_id': 'CVE-2021-22945',
                        'severity': 'medium',
                        'description': 'curl vulnerability',
                        'fixed_version': '7.68.0-4ubuntu1'
                    }
                ]
            },
            'pip': {
                'requests': [
                    {
                        'cve_id': 'CVE-2021-33503',
                        'severity': 'high',
                        'description': 'requests library vulnerability',
                        'fixed_version': '2.25.1'
                    }
                ]
            }
        }
        
        if manager in mock_package_vulns and package in mock_package_vulns[manager]:
            for vuln in mock_package_vulns[manager][package]:
                vulnerabilities.append({
                    'type': 'package_vulnerability',
                    'package': package,
                    'manager': manager,
                    **vuln
                })
        
        return vulnerabilities
    
    def _load_vulnerability_database(self) -> Dict:
        """加载漏洞数据库"""
        # 这里应该从实际的漏洞数据库加载数据
        # 为了演示，返回空字典
        return {}
    
    def _load_sensitive_patterns(self) -> Dict[str, str]:
        """加载敏感数据模式"""
        return {
            'api_key': r'(api[_-]?key|apikey)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{16,}["\']?',
            'password': r'(password|passwd|pwd)\s*[:=]\s*["\']?[^\s"\']{6,}["\']?',
            'secret': r'(secret|token|auth)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{16,}["\']?',
            'private_key': r'-----BEGIN (RSA |OPENSSH |DSA |EC |PGP )?PRIVATE KEY-----',
            'database_url': r'(database|db|mongo|redis)_url\s*[:=]\s*["\']?[a-zA-Z0-9_-]+://[^\s"\']+["\']?'
        }
    
    def _load_insecure_commands(self) -> Dict[str, Dict]:
        """加载不安全命令"""
        return {
            'chmod_777': {
                'pattern': re.compile(r'chmod\s+777', re.IGNORECASE),
                'severity': 'high',
                'description': '使用777权限过于宽松',
                'score_penalty': 20
            },
            'sudo_without_password': {
                'pattern': re.compile(r'sudo\s+.*NOPASSWD', re.IGNORECASE),
                'severity': 'critical',
                'description': '无密码sudo配置',
                'score_penalty': 30
            },
            'wget_insecure': {
                'pattern': re.compile(r'wget\s+.*--no-check-certificate', re.IGNORECASE),
                'severity': 'medium',
                'description': '禁用证书验证的wget',
                'score_penalty': 10
            },
            'curl_insecure': {
                'pattern': re.compile(r'curl\s+.*-k\s+|--insecure', re.IGNORECASE),
                'severity': 'medium',
                'description': '禁用证书验证的curl',
                'score_penalty': 10
            }
        }
    
    def _load_cis_benchmarks(self) -> Dict[str, Dict]:
        """加载CIS基准"""
        return {
            '4.1': {
                'title': 'Create a user for the container',
                'description': 'Containers should run as a non-root user',
                'severity': 'high',
                'score_penalty': 25,
                'remediation': 'Add USER instruction to Dockerfile',
                'check_function': lambda df: not any(inst.instruction == 'USER' for inst in df.instructions)
            },
            '4.5': {
                'title': 'Use CONTENT_TRUST flag',
                'description': 'Enable Docker Content Trust for image operations',
                'severity': 'medium',
                'score_penalty': 10,
                'remediation': 'Use DOCKER_CONTENT_TRUST=1 environment variable',
                'check_function': lambda df: True  # 简化检查
            },
            '4.6': {
                'title': 'Add HEALTHCHECK instruction',
                'description': 'Add HEALTHCHECK instruction to docker container image',
                'severity': 'low',
                'score_penalty': 5,
                'remediation': 'Add HEALTHCHECK instruction to Dockerfile',
                'check_function': lambda df: not any(inst.instruction == 'HEALTHCHECK' for inst in df.instructions)
            }
        }
    
    def _generate_security_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """生成安全建议"""
        recommendations = []
        
        # 基于漏洞扫描结果的建议
        vuln_scan = scan_results.get('vulnerability_scan', {})
        if vuln_scan.get('critical_count', 0) > 0:
            recommendations.append('立即修复关键漏洞，更新基础镜像和依赖包')
        
        if vuln_scan.get('high_count', 0) > 2:
            recommendations.append('优先修复高危漏洞，制定漏洞管理计划')
        
        # 基于敏感数据扫描结果的建议
        sensitive_scan = scan_results.get('sensitive_data_scan', {})
        if sensitive_scan.get('total_findings', 0) > 0:
            recommendations.append('移除Dockerfile中的敏感信息，使用环境变量或密钥管理')
        
        # 基于不安全命令扫描结果的建议
        insecure_scan = scan_results.get('insecure_commands_scan', {})
        if insecure_scan.get('total_findings', 0) > 0:
            recommendations.append('审查并替换不安全的命令，遵循最小权限原则')
        
        # 基于CIS基准扫描结果的建议
        benchmark_scan = scan_results.get('cis_benchmark_scan', {})
        if benchmark_scan.get('total_findings', 0) > 0:
            recommendations.append('遵循CIS Docker基准，加强容器安全配置')
        
        # 基于总体分数的建议
        security_score = scan_results.get('security_score', 0)
        if security_score < 60:
            recommendations.append('安全分数较低，建议进行全面的安全加固')
        elif security_score < 80:
            recommendations.append('安全分数中等，建议继续改进安全配置')
        
        return recommendations

# 使用示例
scanner = SecurityScanner()

# 扫描Dockerfile安全性
try:
    dockerfile_info = parser.parse_dockerfile('Dockerfile')
    security_scan = scanner.scan_security(dockerfile_info)
    
    print("安全扫描结果:")
    print(f"安全分数: {security_scan['security_score']}")
    print(f"风险级别: {security_scan['risk_level']}")
    print(f"漏洞数量: {security_scan['vulnerability_scan']['total_vulnerabilities']}")
    print(f"敏感数据发现: {security_scan['sensitive_data_scan']['total_findings']}")
    print(f"不安全命令: {security_scan['insecure_commands_scan']['total_findings']}")
    print(f"CIS基准问题: {security_scan['cis_benchmark_scan']['total_findings']}")
    
    print("\n安全建议:")
    for recommendation in security_scan['recommendations']:
        print(f"- {recommendation}")
    
except Exception as e:
    print(f"安全扫描失败: {e}")
```

## 性能分析

### 性能分析器
```python
# performance_analyzer.py
from typing import Dict, List, Any, Optional
from dockerfile_parser import DockerfileInfo, DockerfileInstruction
import re

class PerformanceAnalyzer:
    def __init__(self):
        self.layer_size_estimates = {
            'FROM': 50000000,  # 50MB
            'RUN': 5000000,    # 5MB
            'COPY': 10000000,  # 10MB
            'ADD': 15000000,   # 15MB
            'ENV': 1000,       # 1KB
            'ARG': 1000,       # 1KB
            'LABEL': 1000,     # 1KB
            'EXPOSE': 1000,    # 1KB
            'VOLUME': 1000,    # 1KB
            'USER': 1000,      # 1KB
            'WORKDIR': 1000,   # 1KB
            'CMD': 1000,       # 1KB
            'ENTRYPOINT': 1000, # 1KB
            'HEALTHCHECK': 1000 # 1KB
        }
        
        self.build_time_estimates = {
            'FROM': 5,         # 5秒
            'RUN': 30,         # 30秒
            'COPY': 10,        # 10秒
            'ADD': 15,         # 15秒
            'ENV': 1,          # 1秒
            'ARG': 1,          # 1秒
            'LABEL': 1,        # 1秒
            'EXPOSE': 1,       # 1秒
            'VOLUME': 1,       # 1秒
            'USER': 1,         # 1秒
            'WORKDIR': 1,      # 1秒
            'CMD': 1,          # 1秒
            'ENTRYPOINT': 1,   # 1秒
            'HEALTHCHECK': 1   # 1秒
        }
    
    def analyze_performance(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """分析Dockerfile性能"""
        performance_analysis = {
            'size_analysis': self._analyze_size(dockerfile_info),
            'build_time_analysis': self._analyze_build_time(dockerfile_info),
            'cache_analysis': self._analyze_cache_efficiency(dockerfile_info),
            'layer_analysis': self._analyze_layer_performance(dockerfile_info),
            'optimization_suggestions': [],
            'performance_score': 0
        }
        
        # 计算性能分数
        performance_analysis['performance_score'] = self._calculate_performance_score(performance_analysis)
        
        # 生成优化建议
        performance_analysis['optimization_suggestions'] = self._generate_optimization_suggestions(performance_analysis)
        
        return performance_analysis
    
    def _analyze_size(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """分析镜像大小"""
        layer_sizes = []
        total_size = 0
        
        for instruction in dockerfile_info.instructions:
            base_size = self.layer_size_estimates.get(instruction.instruction, 1000000)
            
            # 根据指令内容调整大小估算
            adjusted_size = self._adjust_size_estimate(instruction, base_size)
            
            layer_sizes.append({
                'instruction': instruction.instruction,
                'line': instruction.line_number,
                'estimated_size': adjusted_size,
                'size_category': self._categorize_size(adjusted_size)
            })
            
            total_size += adjusted_size
        
        # 分析大小分布
        size_distribution = {}
        for layer in layer_sizes:
            category = layer['size_category']
            size_distribution[category] = size_distribution.get(category, 0) + 1
        
        return {
            'total_estimated_size': total_size,
            'total_estimated_size_mb': total_size / (1024 * 1024),
            'layer_sizes': layer_sizes,
            'size_distribution': size_distribution,
            'largest_layers': sorted(layer_sizes, key=lambda x: x['estimated_size'], reverse=True)[:5],
            'size_optimization_potential': self._calculate_size_optimization_potential(layer_sizes)
        }
    
    def _analyze_build_time(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """分析构建时间"""
        build_times = []
        total_time = 0
        
        for instruction in dockerfile_info.instructions:
            base_time = self.build_time_estimates.get(instruction.instruction, 5)
            
            # 根据指令内容调整时间估算
            adjusted_time = self._adjust_time_estimate(instruction, base_time)
            
            build_times.append({
                'instruction': instruction.instruction,
                'line': instruction.line_number,
                'estimated_time': adjusted_time,
                'time_category': self._categorize_time(adjusted_time)
            })
            
            total_time += adjusted_time
        
        # 分析时间分布
        time_distribution = {}
        for step in build_times:
            category = step['time_category']
            time_distribution[category] = time_distribution.get(category, 0) + 1
        
        return {
            'total_estimated_time': total_time,
            'total_estimated_time_minutes': total_time / 60,
            'build_times': build_times,
            'time_distribution': time_distribution,
            'slowest_steps': sorted(build_times, key=lambda x: x['estimated_time'], reverse=True)[:5],
            'time_optimization_potential': self._calculate_time_optimization_potential(build_times)
        }
    
    def _analyze_cache_efficiency(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """分析缓存效率"""
        cache_analysis = {
            'cache_hit_score': 0,
            'cache_issues': [],
            'cache_optimizations': []
        }
        
        # 检查指令顺序对缓存的影响
        copy_instructions = [inst for inst in dockerfile_info.instructions if inst.instruction == 'COPY']
        run_instructions = [inst for inst in dockerfile_info.instructions if inst.instruction == 'RUN']
        
        # 检查COPY是否在依赖安装之前
        if copy_instructions and run_instructions:
            first_copy_line = min(inst.line_number for inst in copy_instructions)
            last_run_line = max(inst.line_number for inst in run_instructions)
            
            if first_copy_line < last_run_line:
                cache_analysis['cache_issues'].append({
                    'type': 'copy_before_dependencies',
                    'line': first_copy_line,
                    'description': 'COPY指令在依赖安装之前，可能降低缓存效率',
                    'impact': 'medium'
                })
        
        # 检查RUN指令合并
        run_count = len(run_instructions)
        if run_count > 3:
            cache_analysis['cache_issues'].append({
                'type': 'unmerged_run_instructions',
                'count': run_count,
                'description': f'发现{run_count}个RUN指令，建议合并以提高缓存效率',
                'impact': 'low'
            })
        
        # 检查缓存破坏者
        cache_breakers = []
        for instruction in dockerfile_info.instructions:
            if instruction.instruction == 'RUN':
                for arg in instruction.arguments:
                    if self._is_cache_breaker(arg):
                        cache_breakers.append({
                            'line': instruction.line_number,
                            'instruction': arg,
                            'type': self._get_cache_breaker_type(arg)
                        })
        
        cache_analysis['cache_breakers'] = cache_breakers
        
        # 计算缓存效率分数
        cache_analysis['cache_hit_score'] = self._calculate_cache_hit_score(cache_analysis)
        
        return cache_analysis
    
    def _analyze_layer_performance(self, dockerfile_info: DockerfileInfo) -> Dict[str, Any]:
        """分析层性能"""
        layer_performance = {
            'total_layers': len(dockerfile_info.instructions),
            'layer_efficiency': 0,
            'layer_recommendations': []
        }
        
        # 分析层效率
        efficient_layers = 0
        for instruction in dockerfile_info.instructions:
            if self._is_efficient_layer(instruction):
                efficient_layers += 1
        
        if layer_performance['total_layers'] > 0:
            layer_performance['layer_efficiency'] = (efficient_layers / layer_performance['total_layers']) * 100
        
        # 检查多阶段构建
        multi_stage = len(dockerfile_info.stages) > 1
        layer_performance['multi_stage_build'] = multi_stage
        
        if not multi_stage:
            layer_performance['layer_recommendations'].append({
                'type': 'multi_stage_build',
                'description': '考虑使用多阶段构建减少最终镜像大小',
                'priority': 'medium'
            })
        
        # 检查层数量
        if layer_performance['total_layers'] > 15:
            layer_performance['layer_recommendations'].append({
                'type': 'too_many_layers',
                'description': f'层数过多({layer_performance["total_layers"]})，考虑合并相关指令',
                'priority': 'low'
            })
        
        return layer_performance
    
    def _adjust_size_estimate(self, instruction: DockerfileInstruction, base_size: int) -> int:
        """根据指令内容调整大小估算"""
        if instruction.instruction == 'FROM':
            # 检查基础镜像大小
            for arg in instruction.arguments:
                if 'alpine' in arg.lower():
                    return base_size // 5  # Alpine镜像较小
                elif 'scratch' in arg.lower():
                    return base_size // 50  # Scratch镜像最小
                elif 'ubuntu' in arg.lower() or 'centos' in arg.lower():
                    return base_size * 2  # 完整发行版较大
        
        elif instruction.instruction == 'RUN':
            # 检查包安装
            for arg in instruction.arguments:
                if 'apt-get install' in arg or 'yum install' in arg:
                    package_count = len(arg.split()) - 3  # 估算包数量
                    return base_size + (package_count * 2000000)  # 每个包约2MB
                elif 'pip install' in arg:
                    package_count = len(arg.split()) - 2
                    return base_size + (package_count * 500000)  # Python包较小
        
        elif instruction.instruction in ['COPY', 'ADD']:
            # 检查复制文件大小（简化）
            return base_size * 2  # 假设复制文件较大
        
        return base_size
    
    def _adjust_time_estimate(self, instruction: DockerfileInstruction, base_time: int) -> int:
        """根据指令内容调整时间估算"""
        if instruction.instruction == 'RUN':
            # 检查网络操作
            for arg in instruction.arguments:
                if 'wget' in arg or 'curl' in arg or 'git clone' in arg:
                    return base_time * 3  # 网络操作耗时
                elif 'apt-get update' in arg or 'yum update' in arg:
                    return base_time * 2  # 更新操作耗时
                elif 'make' in arg or 'cmake' in arg:
                    return base_time * 5  # 编译操作耗时
        
        elif instruction.instruction in ['COPY', 'ADD']:
            # 检查大文件复制
            return base_time * 2
        
        return base_time
    
    def _categorize_size(self, size: int) -> str:
        """分类大小"""
        if size < 1000000:  # < 1MB
            return 'small'
        elif size < 10000000:  # < 10MB
            return 'medium'
        elif size < 50000000:  # < 50MB
            return 'large'
        else:
            return 'xlarge'
    
    def _categorize_time(self, time: int) -> str:
        """分类时间"""
        if time < 10:
            return 'fast'
        elif time < 30:
            return 'medium'
        elif time < 60:
            return 'slow'
        else:
            return 'xslow'
    
    def _is_cache_breaker(self, command: str) -> bool:
        """判断是否为缓存破坏者"""
        cache_breakers = [
            'apt-get update', 'yum update', 'apk update',
            'pip install', 'npm install', 'gem install',
            'git clone', 'wget', 'curl',
            'ADD', 'COPY'
        ]
        
        return any(breaker in command for breaker in cache_breakers)
    
    def _get_cache_breaker_type(self, command: str) -> str:
        """获取缓存破坏者类型"""
        if 'update' in command:
            return 'package_update'
        elif 'install' in command:
            return 'package_install'
        elif any(cmd in command for cmd in ['wget', 'curl', 'git clone']):
            return 'download'
        else:
            return 'other'
    
    def _calculate_cache_hit_score(self, cache_analysis: Dict) -> int:
        """计算缓存命中率分数"""
        score = 100
        
        for issue in cache_analysis['cache_issues']:
            if issue['impact'] == 'high':
                score -= 20
            elif issue['impact'] == 'medium':
                score -= 10
            elif issue['impact'] == 'low':
                score -= 5
        
        return max(0, score)
    
    def _calculate_size_optimization_potential(self, layer_sizes: List[Dict]) -> int:
        """计算大小优化潜力"""
        potential = 0
        
        # 检查大层数量
        large_layers = [layer for layer in layer_sizes if layer['size_category'] in ['large', 'xlarge']]
        potential += len(large_layers) * 10
        
        # 检查可优化的指令
        for layer in layer_sizes:
            if layer['instruction'] == 'RUN':
                potential += 5  # RUN指令通常可以优化
        
        return min(potential, 100)
    
    def _calculate_time_optimization_potential(self, build_times: List[Dict]) -> int:
        """计算时间优化潜力"""
        potential = 0
        
        # 检查慢步骤数量
        slow_steps = [step for step in build_times if step['time_category'] in ['slow', 'xslow']]
        potential += len(slow_steps) * 15
        
        # 检查网络操作
        for step in build_times:
            if step['instruction'] == 'RUN':
                potential += 8  # RUN步骤通常可以优化
        
        return min(potential, 100)
    
    def _is_efficient_layer(self, instruction: DockerfileInstruction) -> bool:
        """判断是否为高效层"""
        # 简单的效率判断逻辑
        if instruction.instruction in ['ENV', 'ARG', 'LABEL', 'EXPOSE']:
            return True
        elif instruction.instruction == 'RUN':
            # 检查是否合并了多个操作
            return len(instruction.arguments) > 1
        else:
            return False
    
    def _calculate_performance_score(self, performance_analysis: Dict) -> int:
        """计算性能分数"""
        size_score = 100 - (performance_analysis['size_analysis']['size_optimization_potential'] // 2)
        time_score = 100 - (performance_analysis['build_time_analysis']['time_optimization_potential'] // 2)
        cache_score = performance_analysis['cache_analysis']['cache_hit_score']
        layer_score = performance_analysis['layer_analysis']['layer_efficiency']
        
        overall_score = (size_score + time_score + cache_score + layer_score) / 4
        
        return round(overall_score, 1)
    
    def _generate_optimization_suggestions(self, performance_analysis: Dict) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 基于大小分析的建议
        size_analysis = performance_analysis['size_analysis']
        if size_analysis['total_estimated_size_mb'] > 500:
            suggestions.append('镜像大小较大，考虑使用多阶段构建或更小的基础镜像')
        
        if size_analysis['size_optimization_potential'] > 50:
            suggestions.append('大小优化潜力较高，建议审查大层并进行优化')
        
        # 基于构建时间分析的建议
        time_analysis = performance_analysis['build_time_analysis']
        if time_analysis['total_estimated_time_minutes'] > 10:
            suggestions.append('构建时间较长，考虑优化网络操作和编译步骤')
        
        if time_analysis['time_optimization_potential'] > 50:
            suggestions.append('时间优化潜力较高，建议并行化构建操作')
        
        # 基于缓存分析的建议
        cache_analysis = performance_analysis['cache_analysis']
        if cache_analysis['cache_hit_score'] < 70:
            suggestions.append('缓存效率较低，建议优化指令顺序和合并RUN指令')
        
        # 基于层分析的建议
        layer_analysis = performance_analysis['layer_analysis']
        if not layer_analysis['multi_stage_build']:
            suggestions.append('考虑使用多阶段构建减少最终镜像大小')
        
        if layer_analysis['total_layers'] > 15:
            suggestions.append('层数过多，考虑合并相关指令以减少层数')
        
        # 基于总体分数的建议
        overall_score = performance_analysis['performance_score']
        if overall_score < 60:
            suggestions.append('性能分数较低，建议进行全面优化')
        elif overall_score < 80:
            suggestions.append('性能分数中等，仍有改进空间')
        
        return suggestions

# 使用示例
performance_analyzer = PerformanceAnalyzer()

# 分析Dockerfile性能
try:
    dockerfile_info = parser.parse_dockerfile('Dockerfile')
    performance_analysis = performance_analyzer.analyze_performance(dockerfile_info)
    
    print("性能分析结果:")
    print(f"性能分数: {performance_analysis['performance_score']}")
    print(f"估算镜像大小: {performance_analysis['size_analysis']['total_estimated_size_mb']:.1f} MB")
    print(f"估算构建时间: {performance_analysis['build_time_analysis']['total_estimated_time_minutes']:.1f} 分钟")
    print(f"缓存效率分数: {performance_analysis['cache_analysis']['cache_hit_score']}")
    print(f"层效率: {performance_analysis['layer_analysis']['layer_efficiency']:.1f}%")
    
    print("\n优化建议:")
    for suggestion in performance_analysis['optimization_suggestions']:
        print(f"- {suggestion}")
    
except Exception as e:
    print(f"性能分析失败: {e}")
```

## 报告生成

### 综合报告生成器
```python
# dockerfile_report_generator.py
import json
from datetime import datetime
from typing import Dict, List, Any
from dockerfile_parser import DockerfileInfo

class DockerfileReportGenerator:
    def __init__(self):
        self.report_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dockerfile分析报告</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #2496ed;
            padding-bottom: 20px;
        }
        .header h1 {
            color: #333;
            margin: 0;
            font-size: 2.5em;
        }
        .header .subtitle {
            color: #666;
            margin-top: 10px;
            font-size: 1.1em;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            font-size: 1.1em;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #333;
            border-bottom: 2px solid #2496ed;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .score-indicator {
            width: 100%;
            height: 30px;
            background-color: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .score-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcf7f);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .table th, .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .table th {
            background-color: #f8f9fa;
            font-weight: bold;
            color: #333;
        }
        .table tr:hover {
            background-color: #f5f5f5;
        }
        .severity-critical {
            color: #d32f2f;
            font-weight: bold;
        }
        .severity-high {
            color: #f57c00;
            font-weight: bold;
        }
        .severity-medium {
            color: #fbc02d;
            font-weight: bold;
        }
        .severity-low {
            color: #388e3c;
            font-weight: bold;
        }
        .code-block {
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .recommendation {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        .recommendation h4 {
            margin: 0 0 5px 0;
            color: #1976d2;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            .summary {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dockerfile分析报告</h1>
            <div class="subtitle">生成时间: {generation_time}</div>
        </div>
        
        {summary_section}
        
        {content_sections}
        
        <div class="footer">
            <p>报告由Dockerfile分析器自动生成 | 生成时间: {generation_time}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def generate_comprehensive_report(self, 
                                     dockerfile_info: DockerfileInfo,
                                     instruction_analysis: Dict,
                                     security_analysis: Dict,
                                     performance_analysis: Dict,
                                     output_path: str) -> bool:
        """生成综合报告"""
        try:
            # 生成摘要部分
            summary_section = self._generate_summary_section(instruction_analysis, security_analysis, performance_analysis)
            
            # 生成内容部分
            content_sections = self._generate_content_sections(instruction_analysis, security_analysis, performance_analysis)
            
            html_content = self.report_template.format(
                generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                summary_section=summary_section,
                content_sections=content_sections
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            print(f"生成报告失败: {e}")
            return False
    
    def _generate_summary_section(self, instruction_analysis: Dict, security_analysis: Dict, performance_analysis: Dict) -> str:
        """生成摘要部分"""
        security_score = security_analysis.get('security_score', 0)
        performance_score = performance_analysis.get('performance_score', 0)
        overall_score = (security_score + performance_score) / 2
        
        risk_level = security_analysis.get('risk_level', 'low')
        total_issues = (security_analysis.get('vulnerability_scan', {}).get('total_vulnerabilities', 0) +
                       security_analysis.get('sensitive_data_scan', {}).get('total_findings', 0) +
                       security_analysis.get('insecure_commands_scan', {}).get('total_findings', 0))
        
        html = f"""
        <div class="summary">
            <div class="summary-card">
                <h3>总体评分</h3>
                <div class="value">{overall_score:.1f}</div>
            </div>
            <div class="summary-card">
                <h3>安全评分</h3>
                <div class="value">{security_score:.1f}</div>
            </div>
            <div class="summary-card">
                <h3>性能评分</h3>
                <div class="value">{performance_score:.1f}</div>
            </div>
            <div class="summary-card">
                <h3>风险级别</h3>
                <div class="value">{risk_level.upper()}</div>
            </div>
            <div class="summary-card">
                <h3>问题总数</h3>
                <div class="value">{total_issues}</div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_content_sections(self, instruction_analysis: Dict, security_analysis: Dict, performance_analysis: Dict) -> str:
        """生成内容部分"""
        sections = []
        
        # Dockerfile概览
        sections.append(self._generate_overview_section(instruction_analysis))
        
        # 安全分析
        sections.append(self._generate_security_section(security_analysis))
        
        # 性能分析
        sections.append(self._generate_performance_section(performance_analysis))
        
        # 最佳实践
        sections.append(self._generate_best_practices_section(instruction_analysis))
        
        # 优化建议
        sections.append(self._generate_recommendations_section(security_analysis, performance_analysis))
        
        return '\n'.join(sections)
    
    def _generate_overview_section(self, instruction_analysis: Dict) -> str:
        """生成概览部分"""
        instruction_counts = instruction_analysis.get('instruction_analysis', {}).get('instruction_counts', {})
        total_instructions = instruction_analysis.get('instruction_analysis', {}).get('total_instructions', 0)
        
        html = """
        <div class="section">
            <h2>Dockerfile概览</h2>
            <div class="metric-grid">
        """
        
        for instruction, count in instruction_counts.items():
            html += f"""
                <div class="metric-card">
                    <h3>{instruction}</h3>
                    <div class="metric-value">{count}</div>
                </div>
            """
        
        html += f"""
            </div>
            <h3>统计信息</h3>
            <table class="table">
                <tr>
                    <th>总指令数</th>
                    <td>{total_instructions}</td>
                </tr>
                <tr>
                    <th>指令类型数</th>
                    <td>{len(instruction_counts)}</td>
                </tr>
            </table>
        </div>
        """
        
        return html
    
    def _generate_security_section(self, security_analysis: Dict) -> str:
        """生成安全分析部分"""
        security_score = security_analysis.get('security_score', 0)
        risk_level = security_analysis.get('risk_level', 'low')
        
        html = f"""
        <div class="section">
            <h2>安全分析</h2>
            <h3>安全评分</h3>
            <div class="score-indicator">
                <div class="score-fill" style="width: {security_score}%">
                    {security_score:.1f}
                </div>
            </div>
            <p>风险级别: <span class="severity-{risk_level}">{risk_level.upper()}</span></p>
        """
        
        # 漏洞扫描结果
        vuln_scan = security_analysis.get('vulnerability_scan', {})
        if vuln_scan.get('total_vulnerabilities', 0) > 0:
            html += f"""
                <h3>漏洞扫描</h3>
                <table class="table">
                    <tr>
                        <th>严重程度</th>
                        <th>数量</th>
                    </tr>
                    <tr>
                        <td class="severity-critical">严重</td>
                        <td>{vuln_scan.get('critical_count', 0)}</td>
                    </tr>
                    <tr>
                        <td class="severity-high">高危</td>
                        <td>{vuln_scan.get('high_count', 0)}</td>
                    </tr>
                    <tr>
                        <td class="severity-medium">中危</td>
                        <td>{vuln_scan.get('medium_count', 0)}</td>
                    </tr>
                    <tr>
                        <td class="severity-low">低危</td>
                        <td>{vuln_scan.get('low_count', 0)}</td>
                    </tr>
                </table>
            """
        
        # 敏感数据发现
        sensitive_scan = security_analysis.get('sensitive_data_scan', {})
        if sensitive_scan.get('total_findings', 0) > 0:
            html += """
                <h3>敏感数据发现</h3>
                <table class="table">
                    <tr>
                        <th>类型</th>
                        <th>行号</th>
                        <th>内容</th>
                    </tr>
            """
            
            for finding in sensitive_scan.get('sensitive_findings', [])[:10]:  # 显示前10个
                html += f"""
                    <tr>
                        <td>{finding.get('pattern', 'N/A')}</td>
                        <td>{finding.get('line', 'N/A')}</td>
                        <td><code>{finding.get('content', 'N/A')[:50]}...</code></td>
                    </tr>
                """
            
            html += "</table>"
        
        html += "</div>"
        return html
    
    def _generate_performance_section(self, performance_analysis: Dict) -> str:
        """生成性能分析部分"""
        performance_score = performance_analysis.get('performance_score', 0)
        size_analysis = performance_analysis.get('size_analysis', {})
        build_time_analysis = performance_analysis.get('build_time_analysis', {})
        cache_analysis = performance_analysis.get('cache_analysis', {})
        
        html = f"""
        <div class="section">
            <h2>性能分析</h2>
            <h3>性能评分</h3>
            <div class="score-indicator">
                <div class="score-fill" style="width: {performance_score}%">
                    {performance_score:.1f}
                </div>
            </div>
            
            <h3>镜像大小分析</h3>
            <table class="table">
                <tr>
                    <th>估算大小</th>
                    <td>{size_analysis.get('total_estimated_size_mb', 0):.1f} MB</td>
                </tr>
                <tr>
                    <th>优化潜力</th>
                    <td>{size_analysis.get('size_optimization_potential', 0)}%</td>
                </tr>
            </table>
            
            <h3>构建时间分析</h3>
            <table class="table">
                <tr>
                    <th>估算时间</th>
                    <td>{build_time_analysis.get('total_estimated_time_minutes', 0):.1f} 分钟</td>
                </tr>
                <tr>
                    <th>优化潜力</th>
                    <td>{build_time_analysis.get('time_optimization_potential', 0)}%</td>
                </tr>
            </table>
            
            <h3>缓存效率</h3>
            <table class="table">
                <tr>
                    <th>缓存命中率</th>
                    <td>{cache_analysis.get('cache_hit_score', 0)}%</td>
                </tr>
                <tr>
                    <th>缓存问题</th>
                    <td>{len(cache_analysis.get('cache_issues', []))}</td>
                </tr>
            </table>
        </div>
        """
        
        return html
    
    def _generate_best_practices_section(self, instruction_analysis: Dict) -> str:
        """生成最佳实践部分"""
        best_practices = instruction_analysis.get('best_practices', {})
        issues = best_practices.get('best_practice_issues', [])
        
        html = """
        <div class="section">
            <h2>最佳实践检查</h2>
        """
        
        if issues:
            html += """
                <h3>发现的问题</h3>
                <table class="table">
                    <tr>
                        <th>类型</th>
                        <th>严重程度</th>
                        <th>行号</th>
                        <th>描述</th>
                    </tr>
            """
            
            for issue in issues:
                severity_class = f"severity-{issue.get('severity', 'low')}"
                html += f"""
                    <tr>
                        <td>{issue.get('type', 'N/A')}</td>
                        <td class="{severity_class}">{issue.get('severity', 'N/A')}</td>
                        <td>{issue.get('line', 'N/A')}</td>
                        <td>{issue.get('message', 'N/A')}</td>
                    </tr>
                """
            
            html += "</table>"
        else:
            html += "<p>未发现最佳实践问题。</p>"
        
        html += "</div>"
        return html
    
    def _generate_recommendations_section(self, security_analysis: Dict, performance_analysis: Dict) -> str:
        """生成优化建议部分"""
        all_recommendations = []
        
        # 收集安全建议
        all_recommendations.extend(security_analysis.get('recommendations', []))
        
        # 收集性能建议
        all_recommendations.extend(performance_analysis.get('optimization_suggestions', []))
        
        # 去重并分类
        unique_recommendations = list(set(all_recommendations))
        
        html = """
        <div class="section">
            <h2>优化建议</h2>
        """
        
        for i, recommendation in enumerate(unique_recommendations, 1):
            html += f"""
                <div class="recommendation">
                    <h4>建议 {i}</h4>
                    <p>{recommendation}</p>
                </div>
            """
        
        html += "</div>"
        return html

# 使用示例
report_generator = DockerfileReportGenerator()

# 生成综合报告
try:
    dockerfile_info = parser.parse_dockerfile('Dockerfile')
    
    # 执行各种分析
    instruction_analyzer = InstructionAnalyzer()
    instruction_analysis = instruction_analyzer.analyze_instructions(dockerfile_info)
    
    security_scanner = SecurityScanner()
    security_analysis = security_scanner.scan_security(dockerfile_info)
    
    performance_analyzer = PerformanceAnalyzer()
    performance_analysis = performance_analyzer.analyze_performance(dockerfile_info)
    
    # 生成报告
    success = report_generator.generate_comprehensive_report(
        dockerfile_info,
        instruction_analysis,
        security_analysis,
        performance_analysis,
        'dockerfile_analysis_report.html'
    )
    
    print(f"报告生成成功: {success}")
    
except Exception as e:
    print(f"生成报告失败: {e}")
```

## 参考资源

### Docker官方文档
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Security](https://docs.docker.com/engine/security/)

### 安全标准
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST Container Security Guide](https://csrc.nist.gov/publications/detail/sp/800-190/final)
- [OWASP Docker Security](https://owasp.org/www-project-docker-security/)

### 性能优化
- [Docker Build Optimization](https://docs.docker.com/build/building/optimize/)
- [Layer Caching Best Practices](https://docs.docker.com/build/cache/)
- [Image Size Optimization](https://docs.docker.com/build/building/optimize/#optimize-your-build-process)

### 工具和库
- [Hadolint - Dockerfile Linter](https://github.com/hadolint/hadolint)
- [Dockerfile Linter](https://github.com/replicatedhq/dockerfilelint)
- [Docker Bench Security](https://github.com/docker/docker-bench-security)
- [Trivy - Container Scanner](https://github.com/aquasecurity/trivy)
