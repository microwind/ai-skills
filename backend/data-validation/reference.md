# 数据验证参考文档

## 数据验证概述

### 什么是数据验证
数据验证是一种确保数据完整性、准确性和安全性的技术手段，通过定义和执行各种验证规则来检查输入数据是否符合预期的格式、类型和业务逻辑要求。该技能涵盖了多种数据类型验证、复杂对象验证、自定义验证规则、错误处理、性能优化和安全防护等功能，帮助开发者构建可靠、高效、安全的数据验证系统。

### 主要功能
- **多类型数据验证**: 支持字符串、数值、日期、布尔值、数组、对象等多种数据类型验证
- **验证规则引擎**: 提供条件验证、跨字段验证、自定义验证等灵活的验证规则
- **错误处理机制**: 包含详细的错误消息、多级错误分类和异常处理
- **性能优化**: 支持并发验证、缓存策略、快速失败等性能优化技术
- **安全防护**: 提供SQL注入、XSS攻击等安全威胁检测和防护

## 数据验证引擎核心

### 验证管理器
```python
# data_validation.py
import re
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, date, time
from abc import ABC, abstractmethod
import hashlib
import time

class ValidationType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"
    FILE = "file"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"

class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationOperator(Enum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    REGEX = "regex"
    IN = "in"
    NOT_IN = "not_in"

@dataclass
class ValidationRule:
    name: str
    field: str
    type: ValidationType
    required: bool = True
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    custom_validator: Optional[Callable] = None
    error_message: str = "验证失败"
    error_level: ValidationLevel = ValidationLevel.ERROR
    priority: int = 0

@dataclass
class ValidationError:
    field: str
    rule: str
    message: str
    level: ValidationLevel
    value: Any = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)
    execution_time: float = 0.0
    validated_fields: List[str] = field(default_factory=list)

@dataclass
class ValidationConfig:
    # 基础配置
    strict_mode: bool = True
    fast_fail: bool = False
    parallel_validation: bool = True
    max_workers: int = 4
    
    # 缓存配置
    enable_cache: bool = True
    cache_size: int = 1000
    cache_ttl: int = 300
    
    # 安全配置
    enable_security_checks: bool = True
    sql_injection_check: bool = True
    xss_check: bool = True
    
    # 性能配置
    timeout: float = 30.0
    batch_size: int = 100
    
    # 日志配置
    enable_logging: bool = True
    log_level: str = "INFO"

class Validator(ABC):
    """验证器抽象基类"""
    
    @abstractmethod
    def validate(self, value: Any, rule: ValidationRule) -> Optional[ValidationError]:
        pass

class StringValidator(Validator):
    """字符串验证器"""
    
    def validate(self, value: Any, rule: ValidationRule) -> Optional[ValidationError]:
        if not isinstance(value, str):
            return ValidationError(
                field=rule.field,
                rule=rule.name,
                message=f"{rule.field}必须是字符串类型",
                level=ValidationLevel.ERROR,
                value=value
            )
        
        # 长度验证
        for condition in rule.conditions:
            if condition.get('type') == 'length':
                min_length = condition.get('min_length')
                max_length = condition.get('max_length')
                exact_length = condition.get('exact_length')
                
                if exact_length is not None and len(value) != exact_length:
                    return ValidationError(
                        field=rule.field,
                        rule=rule.name,
                        message=f"{rule.field}长度必须为{exact_length}个字符",
                        level=rule.error_level,
                        value=value
                    )
                
                if min_length is not None and len(value) < min_length:
                    return ValidationError(
                        field=rule.field,
                        rule=rule.name,
                        message=f"{rule.field}长度不能少于{min_length}个字符",
                        level=rule.error_level,
                        value=value
                    )
                
                if max_length is not None and len(value) > max_length:
                    return ValidationError(
                        field=rule.field,
                        rule=rule.name,
                        message=f"{rule.field}长度不能超过{max_length}个字符",
                        level=rule.error_level,
                        value=value
                    )
        
        # 格式验证
        for condition in rule.conditions:
            if condition.get('type') == 'format':
                format_type = condition.get('format_type')
                custom_pattern = condition.get('custom_pattern')
                
                if format_type == 'email':
                    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                elif format_type == 'phone':
                    pattern = r'^1[3-9]\d{9}$'
                elif format_type == 'url':
                    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
                elif custom_pattern:
                    pattern = custom_pattern
                else:
                    continue
                
                if not re.match(pattern, value):
                    format_name = {
                        'email': '邮箱',
                        'phone': '手机号',
                        'url': 'URL'
                    }.get(format_type, '指定格式')
                    
                    return ValidationError(
                        field=rule.field,
                        rule=rule.name,
                        message=f"{rule.field}必须是有效的{format_name}格式",
                        level=rule.error_level,
                        value=value
                    )
        
        # 字符限制验证
        for condition in rule.conditions:
            if condition.get('type') == 'character_set':
                allowed_chars = condition.get('allowed_chars')
                disallowed_chars = condition.get('disallowed_chars')
                
                if allowed_chars:
                    for char in value:
                        if char not in allowed_chars:
                            return ValidationError(
                                field=rule.field,
                                rule=rule.name,
                                message=f"{rule.field}包含不允许的字符: {char}",
                                level=rule.error_level,
                                value=value
                            )
                
                if disallowed_chars:
                    for char in value:
                        if char in disallowed_chars:
                            return ValidationError(
                                field=rule.field,
                                rule=rule.name,
                                message=f"{rule.field}包含禁止的字符: {char}",
                                level=rule.error_level,
                                value=value
                            )
        
        return None

class NumberValidator(Validator):
    """数值验证器"""
    
    def validate(self, value: Any, rule: ValidationRule) -> Optional[ValidationError]:
        # 类型检查
        if rule.type == ValidationType.INTEGER:
            if not isinstance(value, int) or isinstance(value, bool):
                return ValidationError(
                    field=rule.field,
                    rule=rule.name,
                    message=f"{rule.field}必须是整数类型",
                    level=ValidationLevel.ERROR,
                    value=value
                )
        elif rule.type == ValidationType.FLOAT:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return ValidationError(
                    field=rule.field,
                    rule=rule.name,
                    message=f"{rule.field}必须是数值类型",
                    level=ValidationLevel.ERROR,
                    value=value
                )
        
        # 范围验证
        for condition in rule.conditions:
            if condition.get('type') == 'range':
                min_value = condition.get('min_value')
                max_value = condition.get('max_value')
                include_min = condition.get('include_min', True)
                include_max = condition.get('include_max', True)
                
                if min_value is not None:
                    if include_min:
                        if value < min_value:
                            return ValidationError(
                                field=rule.field,
                                rule=rule.name,
                                message=f"{rule.field}不能小于{min_value}",
                                level=rule.error_level,
                                value=value
                            )
                    else:
                        if value <= min_value:
                            return ValidationError(
                                field=rule.field,
                                rule=rule.name,
                                message=f"{rule.field}必须大于{min_value}",
                                level=rule.error_level,
                                value=value
                            )
                
                if max_value is not None:
                    if include_max:
                        if value > max_value:
                            return ValidationError(
                                field=rule.field,
                                rule=rule.name,
                                message=f"{rule.field}不能大于{max_value}",
                                level=rule.error_level,
                                value=value
                            )
                    else:
                        if value >= max_value:
                            return ValidationError(
                                field=rule.field,
                                rule=rule.name,
                                message=f"{rule.field}必须小于{max_value}",
                                level=rule.error_level,
                                value=value
                            )
        
        # 精度验证（浮点数）
        if rule.type == ValidationType.FLOAT:
            for condition in rule.conditions:
                if condition.get('type') == 'precision':
                    decimal_places = condition.get('decimal_places')
                    if decimal_places is not None:
                        str_value = str(value)
                        if '.' in str_value:
                            actual_decimal_places = len(str_value.split('.')[1])
                            if actual_decimal_places > decimal_places:
                                return ValidationError(
                                    field=rule.field,
                                    rule=rule.name,
                                    message=f"{rule.field}小数位数不能超过{decimal_places}位",
                                    level=rule.error_level,
                                    value=value
                                )
        
        return None

class DateValidator(Validator):
    """日期验证器"""
    
    def validate(self, value: Any, rule: ValidationRule) -> Optional[ValidationError]:
        # 类型检查和转换
        if isinstance(value, str):
            # 格式验证
            for condition in rule.conditions:
                if condition.get('type') == 'format':
                    format_type = condition.get('format_type')
                    custom_format = condition.get('custom_format')
                    
                    if format_type == 'YYYY-MM-DD':
                        date_format = '%Y-%m-%d'
                    elif format_type == 'DD/MM/YYYY':
                        date_format = '%d/%m/%Y'
                    elif format_type == 'MM/DD/YYYY':
                        date_format = '%m/%d/%Y'
                    elif custom_format:
                        date_format = custom_format
                    else:
                        date_format = '%Y-%m-%d'
                    
                    try:
                        value = datetime.strptime(value, date_format).date()
                    except ValueError:
                        return ValidationError(
                            field=rule.field,
                            rule=rule.name,
                            message=f"{rule.field}日期格式不正确，应为{format_type}",
                            level=rule.error_level,
                            value=value
                        )
                    break
            else:
                # 默认格式
                try:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    return ValidationError(
                        field=rule.field,
                        rule=rule.name,
                        message=f"{rule.field}必须是有效的日期格式(YYYY-MM-DD)",
                        level=ValidationLevel.ERROR,
                        value=value
                    )
        
        if not isinstance(value, (date, datetime)):
            return ValidationError(
                field=rule.field,
                rule=rule.name,
                message=f"{rule.field}必须是日期类型",
                level=ValidationLevel.ERROR,
                value=value
            )
        
        # 范围验证
        for condition in rule.conditions:
            if condition.get('type') == 'date_range':
                min_date = condition.get('min_date')
                max_date = condition.get('max_date')
                
                if min_date:
                    if isinstance(min_date, str):
                        min_date = datetime.strptime(min_date, '%Y-%m-%d').date()
                    
                    if value < min_date:
                        return ValidationError(
                            field=rule.field,
                            rule=rule.name,
                            message=f"{rule.field}不能早于{min_date}",
                            level=rule.error_level,
                            value=value
                        )
                
                if max_date:
                    if isinstance(max_date, str):
                        max_date = datetime.strptime(max_date, '%Y-%m-%d').date()
                    
                    if value > max_date:
                        return ValidationError(
                            field=rule.field,
                            rule=rule.name,
                            message=f"{rule.field}不能晚于{max_date}",
                            level=rule.error_level,
                            value=value
                        )
        
        return None

class ArrayValidator(Validator):
    """数组验证器"""
    
    def validate(self, value: Any, rule: ValidationRule) -> Optional[ValidationError]:
        if not isinstance(value, (list, tuple)):
            return ValidationError(
                field=rule.field,
                rule=rule.name,
                message=f"{rule.field}必须是数组类型",
                level=ValidationLevel.ERROR,
                value=value
            )
        
        # 长度验证
        for condition in rule.conditions:
            if condition.get('type') == 'length':
                min_length = condition.get('min_length')
                max_length = condition.get('max_length')
                exact_length = condition.get('exact_length')
                
                if exact_length is not None and len(value) != exact_length:
                    return ValidationError(
                        field=rule.field,
                        rule=rule.name,
                        message=f"{rule.field}必须包含{exact_length}个元素",
                        level=rule.error_level,
                        value=value
                    )
                
                if min_length is not None and len(value) < min_length:
                    return ValidationError(
                        field=rule.field,
                        rule=rule.name,
                        message=f"{rule.field}至少需要{min_length}个元素",
                        level=rule.error_level,
                        value=value
                    )
                
                if max_length is not None and len(value) > max_length:
                    return ValidationError(
                        field=rule.field,
                        rule=rule.name,
                        message=f"{rule.field}最多只能有{max_length}个元素",
                        level=rule.error_level,
                        value=value
                    )
        
        # 唯一性验证
        for condition in rule.conditions:
            if condition.get('type') == 'uniqueness':
                unique_field = condition.get('unique_field')
                
                if unique_field:
                    # 检查对象数组中指定字段的唯一性
                    seen_values = set()
                    for item in value:
                        if isinstance(item, dict) and unique_field in item:
                            field_value = item[unique_field]
                            if field_value in seen_values:
                                return ValidationError(
                                    field=rule.field,
                                    rule=rule.name,
                                    message=f"{rule.field}中{unique_field}字段值必须唯一",
                                    level=rule.error_level,
                                    value=value
                                )
                            seen_values.add(field_value)
                else:
                    # 检查数组元素的唯一性
                    if len(set(value)) != len(value):
                        return ValidationError(
                            field=rule.field,
                            rule=rule.name,
                            message=f"{rule.field}中的元素必须唯一",
                            level=rule.error_level,
                            value=value
                        )
        
        return None

class ObjectValidator(Validator):
    """对象验证器"""
    
    def validate(self, value: Any, rule: ValidationRule) -> Optional[ValidationError]:
        if not isinstance(value, dict):
            return ValidationError(
                field=rule.field,
                rule=rule.name,
                message=f"{rule.field}必须是对象类型",
                level=ValidationLevel.ERROR,
                value=value
            )
        
        # 必需字段验证
        for condition in rule.conditions:
            if condition.get('type') == 'required_fields':
                required_fields = condition.get('fields', [])
                for field in required_fields:
                    if field not in value:
                        return ValidationError(
                            field=rule.field,
                            rule=rule.name,
                            message=f"{rule.field}缺少必需字段: {field}",
                            level=rule.error_level,
                            value=value
                        )
        
        # 禁止字段验证
        for condition in rule.conditions:
            if condition.get('type') == 'forbidden_fields':
                forbidden_fields = condition.get('fields', [])
                for field in forbidden_fields:
                    if field in value:
                        return ValidationError(
                            field=rule.field,
                            rule=rule.name,
                            message=f"{rule.field}包含禁止字段: {field}",
                            level=rule.error_level,
                            value=value
                        )
        
        return None

class SecurityValidator:
    """安全验证器"""
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """检查SQL注入"""
        sql_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
            r"(\b(or|and)\s+\d+\s*=\s*\d+)",
            r"(['\"]\s*;\s*\w+)",
            r"(\b(waitfor\s+delay\s+\")",
            r"(\b(cast|convert)\s*\()",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def check_xss(value: str) -> bool:
        """检查XSS攻击"""
        xss_patterns = [
            r"<\s*script[^>]*>.*?<\s*/\s*script\s*>",
            r"<\s*img[^>]*src[^>]*>",
            r"javascript\s*:",
            r"on\w+\s*=",
            r"<\s*iframe[^>]*>",
            r"<\s*object[^>]*>",
            r"<\s*embed[^>]*>",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

class DataValidationManager:
    """数据验证管理器"""
    
    def __init__(self, config: ValidationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._validators = self._init_validators()
        self._cache = {} if config.enable_cache else None
        self._lock = threading.RLock()
    
    def _init_validators(self) -> Dict[ValidationType, Validator]:
        """初始化验证器"""
        return {
            ValidationType.STRING: StringValidator(),
            ValidationType.INTEGER: NumberValidator(),
            ValidationType.FLOAT: NumberValidator(),
            ValidationType.DATE: DateValidator(),
            ValidationType.ARRAY: ArrayValidator(),
            ValidationType.OBJECT: ObjectValidator(),
        }
    
    def validate(self, data: Dict[str, Any], rules: List[ValidationRule]) -> ValidationResult:
        """验证数据"""
        start_time = time.time()
        result = ValidationResult(is_valid=True)
        
        try:
            if self.config.parallel_validation:
                result = self._validate_parallel(data, rules)
            else:
                result = self._validate_sequential(data, rules)
            
            result.execution_time = time.time() - start_time
            
            if self.config.enable_logging:
                self._log_validation_result(result)
            
            return result
        
        except Exception as e:
            self.logger.error(f"验证过程异常: {e}")
            error = ValidationError(
                field="system",
                rule="validation_error",
                message=f"验证过程发生错误: {str(e)}",
                level=ValidationLevel.ERROR
            )
            result.errors.append(error)
            result.is_valid = False
            return result
    
    def _validate_sequential(self, data: Dict[str, Any], rules: List[ValidationRule]) -> ValidationResult:
        """顺序验证"""
        result = ValidationResult(is_valid=True)
        
        for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
            if self.config.fast_fail and not result.is_valid:
                break
            
            field_result = self._validate_field(data, rule)
            result.errors.extend(field_result.errors)
            result.warnings.extend(field_result.warnings)
            result.info.extend(field_result.info)
            
            if field_result.errors:
                result.is_valid = False
            else:
                result.validated_fields.append(rule.field)
        
        return result
    
    def _validate_parallel(self, data: Dict[str, Any], rules: List[ValidationRule]) -> ValidationResult:
        """并行验证"""
        import concurrent.futures
        
        result = ValidationResult(is_valid=True)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_rule = {
                executor.submit(self._validate_field, data, rule): rule
                for rule in rules
            }
            
            for future in concurrent.futures.as_completed(future_to_rule):
                field_result = future.result()
                result.errors.extend(field_result.errors)
                result.warnings.extend(field_result.warnings)
                result.info.extend(field_result.info)
                
                if field_result.errors:
                    result.is_valid = False
                else:
                    rule = future_to_rule[future]
                    result.validated_fields.append(rule.field)
        
        return result
    
    def _validate_field(self, data: Dict[str, Any], rule: ValidationRule) -> ValidationResult:
        """验证单个字段"""
        result = ValidationResult(is_valid=True)
        
        # 检查字段是否存在
        if rule.field not in data:
            if rule.required:
                error = ValidationError(
                    field=rule.field,
                    rule=rule.name,
                    message=f"缺少必需字段: {rule.field}",
                    level=ValidationLevel.ERROR
                )
                result.errors.append(error)
                result.is_valid = False
            return result
        
        value = data[rule.field]
        
        # 检查空值
        if value is None:
            if rule.required:
                error = ValidationError(
                    field=rule.field,
                    rule=rule.name,
                    message=f"{rule.field}不能为空",
                    level=ValidationLevel.ERROR
                )
                result.errors.append(error)
                result.is_valid = False
            return result
        
        # 缓存检查
        if self._cache:
            cache_key = self._generate_cache_key(rule, value)
            if cache_key in self._cache:
                cached_result = self._cache[cache_key]
                if time.time() - cached_result['timestamp'] < self.config.cache_ttl:
                    return cached_result['result']
        
        # 执行验证
        validator = self._validators.get(rule.type)
        if validator:
            error = validator.validate(value, rule)
            if error:
                if error.level == ValidationLevel.ERROR:
                    result.errors.append(error)
                    result.is_valid = False
                elif error.level == ValidationLevel.WARNING:
                    result.warnings.append(error)
                else:
                    result.info.append(error)
        
        # 自定义验证
        if rule.custom_validator and callable(rule.custom_validator):
            try:
                custom_result = rule.custom_validator(value, rule)
                if isinstance(custom_result, ValidationError):
                    if custom_result.level == ValidationLevel.ERROR:
                        result.errors.append(custom_result)
                        result.is_valid = False
                    elif custom_result.level == ValidationLevel.WARNING:
                        result.warnings.append(custom_result)
                    else:
                        result.info.append(custom_result)
            except Exception as e:
                error = ValidationError(
                    field=rule.field,
                    rule=rule.name,
                    message=f"自定义验证失败: {str(e)}",
                    level=ValidationLevel.ERROR
                )
                result.errors.append(error)
                result.is_valid = False
        
        # 安全检查
        if self.config.enable_security_checks and isinstance(value, str):
            if self.config.sql_injection_check and SecurityValidator.check_sql_injection(value):
                error = ValidationError(
                    field=rule.field,
                    rule="security",
                    message=f"{rule.field}包含潜在的SQL注入风险",
                    level=ValidationLevel.ERROR,
                    value=value
                )
                result.errors.append(error)
                result.is_valid = False
            
            if self.config.xss_check and SecurityValidator.check_xss(value):
                error = ValidationError(
                    field=rule.field,
                    rule="security",
                    message=f"{rule.field}包含潜在的XSS攻击风险",
                    level=ValidationLevel.ERROR,
                    value=value
                )
                result.errors.append(error)
                result.is_valid = False
        
        # 缓存结果
        if self._cache:
            cache_key = self._generate_cache_key(rule, value)
            self._cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
            
            # 清理过期缓存
            if len(self._cache) > self.config.cache_size:
                self._cleanup_cache()
        
        return result
    
    def _generate_cache_key(self, rule: ValidationRule, value: Any) -> str:
        """生成缓存键"""
        key_data = f"{rule.field}:{rule.type}:{str(value)}:{hash(str(rule.conditions))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, cached_data in self._cache.items()
            if current_time - cached_data['timestamp'] > self.config.cache_ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        # 如果缓存仍然过大，删除最旧的条目
        if len(self._cache) > self.config.cache_size:
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            excess_count = len(self._cache) - self.config.cache_size
            for key, _ in sorted_items[:excess_count]:
                del self._cache[key]
    
    def _log_validation_result(self, result: ValidationResult):
        """记录验证结果"""
        if result.is_valid:
            self.logger.info(f"验证成功，验证字段: {result.validated_fields}")
        else:
            error_messages = [error.message for error in result.errors]
            self.logger.error(f"验证失败，错误: {error_messages}")
        
        if result.warnings:
            warning_messages = [warning.message for warning in result.warnings]
            self.logger.warning(f"验证警告: {warning_messages}")

# 验证装饰器
def validate_data(rules: List[ValidationRule], config: Optional[ValidationConfig] = None):
    """数据验证装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取要验证的数据（假设第一个参数是数据字典）
            if args and isinstance(args[0], dict):
                data = args[0]
            else:
                # 从kwargs中获取数据
                data = kwargs.get('data', {})
            
            # 创建验证管理器
            validation_config = config or ValidationConfig()
            validator = DataValidationManager(validation_config)
            
            # 执行验证
            result = validator.validate(data, rules)
            
            if not result.is_valid:
                error_messages = [error.message for error in result.errors]
                raise ValueError(f"数据验证失败: {', '.join(error_messages)}")
            
            # 验证通过，执行原函数
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 全局验证管理器
validation_manager = None

def init_validation(config: ValidationConfig):
    """初始化验证管理器"""
    global validation_manager
    validation_manager = DataValidationManager(config)

def get_validator() -> DataValidationManager:
    """获取验证管理器"""
    return validation_manager

# 使用示例
# 配置验证
config = ValidationConfig(
    strict_mode=True,
    fast_fail=False,
    parallel_validation=True,
    max_workers=4,
    enable_cache=True,
    cache_size=1000,
    cache_ttl=300,
    enable_security_checks=True,
    sql_injection_check=True,
    xss_check=True,
    timeout=30.0,
    batch_size=100,
    enable_logging=True,
    log_level="INFO"
)

# 初始化验证管理器
init_validation(config)

# 定义验证规则
user_validation_rules = [
    ValidationRule(
        name="username_validation",
        field="username",
        type=ValidationType.STRING,
        required=True,
        conditions=[
            {"type": "length", "min_length": 3, "max_length": 20},
            {"type": "format", "format_type": "custom_pattern", "custom_pattern": r"^[a-zA-Z0-9_]+$"},
        ],
        error_message="用户名必须是3-20位的字母数字下划线",
        error_level=ValidationLevel.ERROR
    ),
    ValidationRule(
        name="email_validation",
        field="email",
        type=ValidationType.STRING,
        required=True,
        conditions=[
            {"type": "format", "format_type": "email"},
        ],
        error_message="邮箱格式不正确",
        error_level=ValidationLevel.ERROR
    ),
    ValidationRule(
        name="age_validation",
        field="age",
        type=ValidationType.INTEGER,
        required=True,
        conditions=[
            {"type": "range", "min_value": 18, "max_value": 120},
        ],
        error_message="年龄必须在18-120岁之间",
        error_level=ValidationLevel.ERROR
    ),
    ValidationRule(
        name="birth_date_validation",
        field="birth_date",
        type=ValidationType.DATE,
        required=False,
        conditions=[
            {"type": "format", "format_type": "YYYY-MM-DD"},
            {"type": "date_range", "min_date": "1900-01-01", "max_date": "2020-12-31"},
        ],
        error_message="出生日期格式不正确或超出范围",
        error_level=ValidationLevel.WARNING
    ),
    ValidationRule(
        name="tags_validation",
        field="tags",
        type=ValidationType.ARRAY,
        required=False,
        conditions=[
            {"type": "length", "min_length": 1, "max_length": 10},
            {"type": "uniqueness"},
        ],
        error_message="标签数组长度必须在1-10之间且元素唯一",
        error_level=ValidationLevel.WARNING
    ),
]

# 测试数据
test_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "age": 25,
    "birth_date": "1995-06-15",
    "tags": ["developer", "python", "web"]
}

# 执行验证
validator = get_validator()
result = validator.validate(test_data, user_validation_rules)

print(f"验证结果: {result.is_valid}")
print(f"执行时间: {result.execution_time:.3f}秒")
print(f"验证字段: {result.validated_fields}")

if result.errors:
    print("错误:")
    for error in result.errors:
        print(f"  - {error.field}: {error.message}")

if result.warnings:
    print("警告:")
    for warning in result.warnings:
        print(f"  - {warning.field}: {warning.message}")

if result.info:
    print("信息:")
    for info in result.info:
        print(f"  - {info.field}: {info.message}")

# 使用装饰器验证
@validate_data(user_validation_rules, config)
def create_user(data):
    """创建用户"""
    print(f"创建用户成功: {data['username']}")
    return {"status": "success", "user": data}

# 测试装饰器
try:
    result = create_user(test_data)
    print(f"装饰器验证结果: {result}")
except ValueError as e:
    print(f"验证失败: {e}")
```

## 参考资源

### 数据验证技术
- [Python数据验证库](https://pydantic-docs.helpmanual.io/)
- [JSON Schema验证](https://json-schema.org/)
- [XML Schema验证](https://www.w3.org/XML/Schema)
- [正则表达式教程](https://regexlearn.com/)

### 验证框架
- [Marshmallow数据序列化](https://marshmallow.readthedocs.io/)
- [Cerberus验证库](http://docs.python-cerberus.org/)
- [Voluptuous数据验证](https://github.com/alecthomas/voluptuous)
- [Schema验证库](https://github.com/keleshev/schema)

### 安全验证
- [OWASP数据验证](https://owasp.org/www-project-cheat-sheets/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [SQL注入防护](https://owasp.org/www-community/attacks/SQL_Injection)
- [XSS防护](https://owasp.org/www-project-cheat-sheets/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [输入验证最佳实践](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

### 性能优化
- [验证性能优化](https://docs.python.org/3/library/re.html#re.compile)
- [并发验证技术](https://docs.python.org/3/library/concurrent.futures.html)
- [缓存策略](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [异步验证](https://docs.python.org/3/library/asyncio.html)
