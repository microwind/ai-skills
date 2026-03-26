# 密码生成器参考文档

## 密码生成器概述

### 什么是密码生成器
密码生成器是一个专门用于创建安全、随机、高强度密码的工具。该工具支持多种密码规则、安全级别、字符类型和生成模式，提供密码质量评估、安全检查、批量生成和记忆辅助等功能，帮助用户创建符合安全标准的密码，保护账户和数据安全。

### 主要功能
- **多规则支持**: 支持长度、字符类型、字符分布、排除规则等多种密码规则
- **安全级别**: 提供低、中、高、极高四个安全级别，适应不同安全需求
- **质量评估**: 实时评估密码强度，提供质量评分和改进建议
- **批量生成**: 支持批量密码生成，提高效率
- **记忆辅助**: 提供易记密码生成和记忆提示功能

## 密码生成引擎

### 核心生成器
```python
# password_generator.py
import os
import random
import secrets
import string
import hashlib
import hmac
import json
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime
import statistics

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class CharType(Enum):
    LOWERCASE = "lowercase"
    UPPERCASE = "uppercase"
    DIGITS = "digits"
    SPECIAL = "special"

class GenerationType(Enum):
    RANDOM = "random"
    MEMORABLE = "memorable"
    PATTERN = "pattern"
    PRONOUNCEABLE = "pronounceable"

@dataclass
class PasswordConfig:
    # 基础配置
    length: int = 12
    min_length: int = 8
    max_length: int = 32
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    
    # 字符类型
    include_lowercase: bool = True
    include_uppercase: bool = True
    include_digits: bool = True
    include_special: bool = True
    
    # 字符集
    lowercase_chars: str = string.ascii_lowercase
    uppercase_chars: str = string.ascii_uppercase
    digit_chars: str = string.digits
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # 排除字符
    exclude_chars: str = ""
    exclude_similar: bool = True
    exclude_ambiguous: bool = False
    
    # 强制包含
    force_lowercase: int = 1
    force_uppercase: int = 1
    force_digits: int = 1
    force_special: int = 1
    
    # 高级配置
    no_repeating: bool = True
    no_sequential: bool = True
    no_keyboard_patterns: bool = True
    
    # 生成配置
    generation_type: GenerationType = GenerationType.RANDOM
    random_source: str = "secrets"  # secrets, random, custom
    seed: Optional[str] = None
    
    # 输出配置
    output_format: str = "text"  # text, json, csv
    include_metadata: bool = False

@dataclass
class PasswordResult:
    password: str
    strength_score: float
    quality_level: str
    entropy: float
    character_distribution: Dict[str, int]
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class PasswordGenerator:
    def __init__(self, config: PasswordConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.quality_checker = PasswordQualityChecker()
        self.pattern_detector = PatternDetector()
        
        # 初始化字符集
        self._init_charsets()
        
        # 初始化随机数生成器
        self._init_random_generator()
    
    def _init_charsets(self):
        """初始化字符集"""
        # 处理排除字符
        self.lowercase_set = self._remove_excluded_chars(
            self.config.lowercase_chars, self.config.exclude_chars
        )
        self.uppercase_set = self._remove_excluded_chars(
            self.config.uppercase_chars, self.config.exclude_chars
        )
        self.digit_set = self._remove_excluded_chars(
            self.config.digit_chars, self.config.exclude_chars
        )
        self.special_set = self._remove_excluded_chars(
            self.config.special_chars, self.config.exclude_chars
        )
        
        # 处理相似字符
        if self.config.exclude_similar:
            similar_chars = "0Ol1I"
            for char in similar_chars:
                self.lowercase_set = self.lowercase_set.replace(char, "")
                self.uppercase_set = self.uppercase_set.replace(char, "")
                self.digit_set = self.digit_set.replace(char, "")
        
        # 构建完整字符集
        self.full_charset = ""
        if self.config.include_lowercase:
            self.full_charset += self.lowercase_set
        if self.config.include_uppercase:
            self.full_charset += self.uppercase_set
        if self.config.include_digits:
            self.full_charset += self.digit_set
        if self.config.include_special:
            self.full_charset += self.special_set
    
    def _remove_excluded_chars(self, charset: str, excluded: str) -> str:
        """移除排除的字符"""
        return ''.join(char for char in charset if char not in excluded)
    
    def _init_random_generator(self):
        """初始化随机数生成器"""
        if self.config.random_source == "secrets":
            self.random_func = secrets.choice
            self.random_bytes = secrets.token_bytes
        elif self.config.random_source == "random":
            self.random_func = random.choice
            self.random_bytes = os.urandom
        else:
            self.random_func = secrets.choice
            self.random_bytes = secrets.token_bytes
        
        # 设置种子
        if self.config.seed:
            random.seed(self.config.seed)
    
    def generate_password(self) -> PasswordResult:
        """生成密码"""
        try:
            # 根据生成类型生成密码
            if self.config.generation_type == GenerationType.RANDOM:
                password = self._generate_random_password()
            elif self.config.generation_type == GenerationType.MEMORABLE:
                password = self._generate_memorable_password()
            elif self.config.generation_type == GenerationType.PATTERN:
                password = self._generate_pattern_password()
            elif self.config.generation_type == GenerationType.PRONOUNCEABLE:
                password = self._generate_pronounceable_password()
            else:
                password = self._generate_random_password()
            
            # 验证密码
            password = self._validate_and_fix_password(password)
            
            # 评估质量
            quality_result = self.quality_checker.evaluate_password(password)
            
            # 检测模式
            patterns = self.pattern_detector.detect_patterns(password)
            
            # 构建结果
            result = PasswordResult(
                password=password,
                strength_score=quality_result.score,
                quality_level=quality_result.level,
                entropy=self._calculate_entropy(password),
                character_distribution=self._analyze_character_distribution(password),
                issues=quality_result.issues + patterns,
                suggestions=quality_result.suggestions,
                metadata={
                    "generation_time": datetime.now().isoformat(),
                    "config_hash": self._hash_config(),
                    "charset_size": len(self.full_charset)
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"生成密码失败: {e}")
            raise
    
    def _generate_random_password(self) -> str:
        """生成随机密码"""
        password = []
        
        # 强制包含指定类型的字符
        if self.config.force_lowercase > 0:
            password.extend(self._random_chars(self.lowercase_set, self.config.force_lowercase))
        if self.config.force_uppercase > 0:
            password.extend(self._random_chars(self.uppercase_set, self.config.force_uppercase))
        if self.config.force_digits > 0:
            password.extend(self._random_chars(self.digit_set, self.config.force_digits))
        if self.config.force_special > 0:
            password.extend(self._random_chars(self.special_set, self.config.force_special))
        
        # 填充剩余长度
        remaining_length = self.config.length - len(password)
        if remaining_length > 0:
            password.extend(self._random_chars(self.full_charset, remaining_length))
        
        # 打乱顺序
        random.shuffle(password)
        
        return ''.join(password)
    
    def _generate_memorable_password(self) -> str:
        """生成易记密码"""
        # 使用单词组合生成易记密码
        words = self._get_random_words(3)
        
        # 添加数字和特殊字符
        password_parts = []
        for i, word in enumerate(words):
            password_parts.append(word)
            if i < len(words) - 1:
                # 在单词之间添加分隔符
                if self.config.include_digits:
                    password_parts.append(str(random.randint(0, 99)))
                if self.config.include_special:
                    password_parts.append(random.choice(self.special_set))
        
        password = ''.join(password_parts)
        
        # 调整长度
        if len(password) > self.config.length:
            password = password[:self.config.length]
        elif len(password) < self.config.length:
            # 添加随机字符填充
            needed = self.config.length - len(password)
            password += self._random_chars(self.full_charset, needed)
        
        return password
    
    def _generate_pattern_password(self) -> str:
        """生成模式密码"""
        # 定义密码模式，如：LlDdSs (大写字母+小写字母+数字+数字+特殊字符+小写字母)
        patterns = [
            "LlDdSs",  # 大写+小写+数字+数字+特殊+小写
            "DdLlSs",  # 数字+数字+大写+小写+特殊+小写
            "SsLlDd",  # 特殊+小写+大写+小写+数字+数字
            "LlSsDd",  # 大写+小写+特殊+小写+数字+数字
        ]
        
        pattern = random.choice(patterns)
        password = []
        
        for char_type in pattern:
            if char_type == 'L':
                password.append(random.choice(self.uppercase_set))
            elif char_type == 'l':
                password.append(random.choice(self.lowercase_set))
            elif char_type == 'D':
                password.append(random.choice(self.digit_set))
            elif char_type == 'S':
                password.append(random.choice(self.special_set))
        
        # 如果需要更长的密码，重复模式
        while len(password) < self.config.length:
            extra_pattern = random.choice(patterns)
            for char_type in extra_pattern:
                if len(password) >= self.config.length:
                    break
                
                if char_type == 'L':
                    password.append(random.choice(self.uppercase_set))
                elif char_type == 'l':
                    password.append(random.choice(self.lowercase_set))
                elif char_type == 'D':
                    password.append(random.choice(self.digit_set))
                elif char_type == 'S':
                    password.append(random.choice(self.special_set))
        
        return ''.join(password[:self.config.length])
    
    def _generate_pronounceable_password(self) -> str:
        """生成可发音密码"""
        # 使用音节生成可发音密码
        consonants = "bcdfghjklmnpqrstvwxyz"
        vowels = "aeiou"
        
        password = ""
        syllable_count = max(3, self.config.length // 3)
        
        for i in range(syllable_count):
            # 生成音节：辅音+元音 或 元音+辅音
            if random.choice([True, False]):
                syllable = random.choice(consonants) + random.choice(vowels)
            else:
                syllable = random.choice(vowels) + random.choice(consonants)
            
            # 随机大小写
            if self.config.include_uppercase and random.choice([True, False]):
                syllable = syllable.capitalize()
            
            password += syllable
            
            # 添加数字或特殊字符
            if i < syllable_count - 1 and random.choice([True, False]):
                if self.config.include_digits and random.choice([True, False]):
                    password += str(random.randint(0, 9))
                elif self.config.include_special:
                    password += random.choice(self.special_set)
        
        # 调整长度
        if len(password) > self.config.length:
            password = password[:self.config.length]
        elif len(password) < self.config.length:
            needed = self.config.length - len(password)
            password += self._random_chars(self.full_charset, needed)
        
        return password
    
    def _random_chars(self, charset: str, count: int) -> List[str]:
        """生成随机字符列表"""
        if not charset:
            return []
        
        chars = []
        for _ in range(count):
            chars.append(self.random_func(charset))
        
        return chars
    
    def _get_random_words(self, count: int) -> List[str]:
        """获取随机单词"""
        # 简化的单词列表
        word_list = [
            "apple", "banana", "orange", "grape", "lemon",
            "computer", "keyboard", "mouse", "screen", "monitor",
            "happy", "smile", "laugh", "joy", "fun",
            "mountain", "river", "ocean", "forest", "desert",
            "coffee", "water", "juice", "milk", "tea"
        ]
        
        return [random.choice(word_list).capitalize() for _ in range(count)]
    
    def _validate_and_fix_password(self, password: str) -> str:
        """验证并修复密码"""
        # 检查长度
        if len(password) < self.config.min_length:
            needed = self.config.min_length - len(password)
            password += self._random_chars(self.full_charset, needed)
        elif len(password) > self.config.max_length:
            password = password[:self.config.max_length]
        
        # 检查强制包含
        char_counts = self._analyze_character_distribution(password)
        
        # 添加缺失的字符类型
        if (self.config.force_lowercase > 0 and 
            char_counts.get('lowercase', 0) < self.config.force_lowercase):
            needed = self.config.force_lowercase - char_counts.get('lowercase', 0)
            password += self._random_chars(self.lowercase_set, needed)
        
        if (self.config.force_uppercase > 0 and 
            char_counts.get('uppercase', 0) < self.config.force_uppercase):
            needed = self.config.force_uppercase - char_counts.get('uppercase', 0)
            password += self._random_chars(self.uppercase_set, needed)
        
        if (self.config.force_digits > 0 and 
            char_counts.get('digits', 0) < self.config.force_digits):
            needed = self.config.force_digits - char_counts.get('digits', 0)
            password += self._random_chars(self.digit_set, needed)
        
        if (self.config.force_special > 0 and 
            char_counts.get('special', 0) < self.config.force_special):
            needed = self.config.force_special - char_counts.get('special', 0)
            password += self._random_chars(self.special_set, needed)
        
        # 检查重复字符
        if self.config.no_repeating:
            password = self._remove_repeating_chars(password)
        
        # 检查序列字符
        if self.config.no_sequential:
            password = self._remove_sequential_chars(password)
        
        # 检查键盘模式
        if self.config.no_keyboard_patterns:
            password = self._remove_keyboard_patterns(password)
        
        # 调整最终长度
        if len(password) != self.config.length:
            if len(password) > self.config.length:
                password = password[:self.config.length]
            else:
                needed = self.config.length - len(password)
                password += self._random_chars(self.full_charset, needed)
        
        return password
    
    def _remove_repeating_chars(self, password: str) -> str:
        """移除重复字符"""
        result = []
        prev_char = None
        
        for char in password:
            if char != prev_char:
                result.append(char)
            prev_char = char
        
        return ''.join(result)
    
    def _remove_sequential_chars(self, password: str) -> str:
        """移除序列字符"""
        # 检查连续的数字或字母
        for i in range(len(password) - 2):
            if (password[i].isdigit() and password[i+1].isdigit() and password[i+2].isdigit()):
                # 检查是否为连续数字
                try:
                    n1, n2, n3 = int(password[i]), int(password[i+1]), int(password[i+2])
                    if (n2 == n1 + 1 and n3 == n2 + 1) or (n2 == n1 - 1 and n3 == n2 - 1):
                        # 替换中间的字符
                        password = password[:i+1] + random.choice(self.digit_set) + password[i+2:]
                except ValueError:
                    pass
        
        return password
    
    def _remove_keyboard_patterns(self, password: str) -> str:
        """移除键盘模式"""
        # 定义键盘序列
        keyboard_patterns = [
            "qwerty", "asdf", "zxcv", "123", "456", "789",
            "qwe", "asd", "zxc", "123", "456", "789"
        ]
        
        password_lower = password.lower()
        
        for pattern in keyboard_patterns:
            if pattern in password_lower:
                # 替换模式中的字符
                start_idx = password_lower.find(pattern)
                replacement = self._random_chars(self.full_charset, len(pattern))
                password = password[:start_idx] + ''.join(replacement) + password[start_idx+len(pattern):]
                password_lower = password.lower()
        
        return password
    
    def _calculate_entropy(self, password: str) -> float:
        """计算密码熵"""
        charset_size = len(self.full_charset)
        if charset_size == 0:
            return 0.0
        
        entropy = len(password) * (charset_size.bit_length() - 1)
        return entropy
    
    def _analyze_character_distribution(self, password: str) -> Dict[str, int]:
        """分析字符分布"""
        distribution = {
            'lowercase': 0,
            'uppercase': 0,
            'digits': 0,
            'special': 0
        }
        
        for char in password:
            if char in self.lowercase_set:
                distribution['lowercase'] += 1
            elif char in self.uppercase_set:
                distribution['uppercase'] += 1
            elif char in self.digit_set:
                distribution['digits'] += 1
            elif char in self.special_set:
                distribution['special'] += 1
        
        return distribution
    
    def _hash_config(self) -> str:
        """计算配置哈希"""
        config_str = json.dumps(asdict(self.config), sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def generate_batch(self, count: int) -> List[PasswordResult]:
        """批量生成密码"""
        results = []
        
        for i in range(count):
            try:
                result = self.generate_password()
                results.append(result)
            except Exception as e:
                self.logger.error(f"批量生成第{i+1}个密码失败: {e}")
                # 添加失败结果
                results.append(PasswordResult(
                    password="",
                    strength_score=0.0,
                    quality_level="failed",
                    entropy=0.0,
                    character_distribution={},
                    issues=[f"生成失败: {e}"],
                    suggestions=[],
                    metadata={"error": str(e)}
                ))
        
        return results

class PasswordQualityChecker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.common_passwords = self._load_common_passwords()
    
    def _load_common_passwords(self) -> set:
        """加载常见密码列表"""
        # 简化的常见密码列表
        return {
            "password", "123456", "12345678", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey",
            "1234567890", "password1", "123123", "dragon", "master"
        }
    
    def evaluate_password(self, password: str) -> 'QualityResult':
        """评估密码质量"""
        score = 0
        issues = []
        suggestions = []
        
        # 长度评分
        length_score = self._evaluate_length(password)
        score += length_score[0]
        if length_score[1]:
            issues.extend(length_score[1])
        if length_score[2]:
            suggestions.extend(length_score[2])
        
        # 字符多样性评分
        diversity_score = self._evaluate_character_diversity(password)
        score += diversity_score[0]
        if diversity_score[1]:
            issues.extend(diversity_score[1])
        if diversity_score[2]:
            suggestions.extend(diversity_score[2])
        
        # 复杂度评分
        complexity_score = self._evaluate_complexity(password)
        score += complexity_score[0]
        if complexity_score[1]:
            issues.extend(complexity_score[1])
        if complexity_score[2]:
            suggestions.extend(complexity_score[2])
        
        # 常见密码检查
        common_check = self._check_common_passwords(password)
        if common_check[0]:
            score -= 20
            issues.extend(common_check[1])
            suggestions.extend(common_check[2])
        
        # 确定质量等级
        level = self._determine_quality_level(score)
        
        return QualityResult(
            score=max(0, min(100, score)),
            level=level,
            issues=issues,
            suggestions=suggestions
        )
    
    def _evaluate_length(self, password: str) -> Tuple[float, List[str], List[str]]:
        """评估密码长度"""
        score = 0
        issues = []
        suggestions = []
        
        length = len(password)
        
        if length < 8:
            score = 0
            issues.append("密码长度太短，少于8个字符")
            suggestions.append("建议密码长度至少12个字符")
        elif length < 12:
            score = 20
            issues.append("密码长度较短，少于12个字符")
            suggestions.append("建议密码长度至少12个字符")
        elif length < 16:
            score = 30
        elif length < 20:
            score = 40
        else:
            score = 50
        
        return score, issues, suggestions
    
    def _evaluate_character_diversity(self, password: str) -> Tuple[float, List[str], List[str]]:
        """评估字符多样性"""
        score = 0
        issues = []
        suggestions = []
        
        has_lowercase = any(c.islower() for c in password)
        has_uppercase = any(c.isupper() for c in password)
        has_digits = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        diversity_count = sum([has_lowercase, has_uppercase, has_digits, has_special])
        
        if diversity_count == 1:
            score = 0
            issues.append("密码字符类型单一")
            suggestions.append("建议使用大小写字母、数字和特殊字符的组合")
        elif diversity_count == 2:
            score = 10
            issues.append("密码字符类型较少")
            suggestions.append("建议增加更多字符类型")
        elif diversity_count == 3:
            score = 20
        elif diversity_count == 4:
            score = 30
        
        return score, issues, suggestions
    
    def _evaluate_complexity(self, password: str) -> Tuple[float, List[str], List[str]]:
        """评估密码复杂度"""
        score = 0
        issues = []
        suggestions = []
        
        # 检查重复字符
        has_repeating = len(set(password)) < len(password) * 0.8
        if has_repeating:
            score -= 5
            issues.append("密码包含重复字符")
            suggestions.append("避免使用重复字符")
        
        # 检查序列字符
        has_sequential = self._has_sequential_chars(password)
        if has_sequential:
            score -= 5
            issues.append("密码包含序列字符")
            suggestions.append("避免使用连续的字符序列")
        
        # 检查键盘模式
        has_keyboard = self._has_keyboard_patterns(password)
        if has_keyboard:
            score -= 5
            issues.append("密码包含键盘模式")
            suggestions.append("避免使用键盘上的连续字符")
        
        # 基础复杂度分数
        base_score = 20
        
        return base_score + score, issues, suggestions
    
    def _has_sequential_chars(self, password: str) -> bool:
        """检查是否有序列字符"""
        password_lower = password.lower()
        
        for i in range(len(password_lower) - 2):
            # 检查字母序列
            if (password_lower[i].isalpha() and 
                password_lower[i+1].isalpha() and 
                password_lower[i+2].isalpha()):
                
                if (ord(password_lower[i+1]) == ord(password_lower[i]) + 1 and
                    ord(password_lower[i+2]) == ord(password_lower[i+1]) + 1):
                    return True
                
                if (ord(password_lower[i+1]) == ord(password_lower[i]) - 1 and
                    ord(password_lower[i+2]) == ord(password_lower[i+1]) - 1):
                    return True
            
            # 检查数字序列
            if (password_lower[i].isdigit() and 
                password_lower[i+1].isdigit() and 
                password_lower[i+2].isdigit()):
                
                try:
                    n1, n2, n3 = int(password_lower[i]), int(password_lower[i+1]), int(password_lower[i+2])
                    if (n2 == n1 + 1 and n3 == n2 + 1) or (n2 == n1 - 1 and n3 == n2 - 1):
                        return True
                except ValueError:
                    pass
        
        return False
    
    def _has_keyboard_patterns(self, password: str) -> bool:
        """检查是否有键盘模式"""
        keyboard_patterns = [
            "qwerty", "asdf", "zxcv", "qwertyuiop", "asdfghjkl", "zxcvbnm",
            "1234567890", "12345678", "1234567", "123456", "12345",
            "qwe", "asd", "zxc", "123", "456", "789"
        ]
        
        password_lower = password.lower()
        
        for pattern in keyboard_patterns:
            if pattern in password_lower:
                return True
        
        return False
    
    def _check_common_passwords(self, password: str) -> Tuple[bool, List[str], List[str]]:
        """检查常见密码"""
        issues = []
        suggestions = []
        
        password_lower = password.lower()
        
        if password_lower in self.common_passwords:
            issues.append("密码过于常见，容易被破解")
            suggestions.append("避免使用常见密码")
            return True, issues, suggestions
        
        # 检查常见密码的变体
        for common in self.common_passwords:
            if (common in password_lower or 
                password_lower in common or
                self._is_common_variant(password_lower, common)):
                issues.append("密码与常见密码过于相似")
                suggestions.append("避免使用与常见密码相似的密码")
                return True, issues, suggestions
        
        return False, issues, suggestions
    
    def _is_common_variant(self, password: str, common: str) -> bool:
        """检查是否为常见密码的变体"""
        # 简单的变体检查
        if len(password) != len(common):
            return False
        
        diff_count = sum(1 for a, b in zip(password, common) if a != b)
        return diff_count <= 2
    
    def _determine_quality_level(self, score: float) -> str:
        """确定质量等级"""
        if score < 20:
            return "very_weak"
        elif score < 40:
            return "weak"
        elif score < 60:
            return "medium"
        elif score < 80:
            return "strong"
        else:
            return "very_strong"

@dataclass
class QualityResult:
    score: float
    level: str
    issues: List[str]
    suggestions: List[str]

class PatternDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_patterns(self, password: str) -> List[str]:
        """检测密码中的模式"""
        patterns = []
        
        # 检测重复模式
        repeating_patterns = self._detect_repeating_patterns(password)
        patterns.extend(repeating_patterns)
        
        # 检测对称模式
        symmetry_patterns = self._detect_symmetry_patterns(password)
        patterns.extend(symmetry_patterns)
        
        # 检测日期模式
        date_patterns = self._detect_date_patterns(password)
        patterns.extend(date_patterns)
        
        return patterns
    
    def _detect_repeating_patterns(self, password: str) -> List[str]:
        """检测重复模式"""
        patterns = []
        
        # 检查重复的子串
        for length in range(2, len(password) // 2 + 1):
            for i in range(len(password) - length * 2 + 1):
                substring = password[i:i+length]
                if substring in password[i+length:]:
                    patterns.append(f"重复模式: {substring}")
        
        return patterns
    
    def _detect_symmetry_patterns(self, password: str) -> List[str]:
        """检测对称模式"""
        patterns = []
        
        # 检查回文
        if password == password[::-1]:
            patterns.append("回文模式")
        
        # 检查部分回文
        for i in range(len(password) - 2):
            for j in range(i + 2, len(password)):
                substring = password[i:j]
                if substring == substring[::-1] and len(substring) > 2:
                    patterns.append(f"部分回文: {substring}")
        
        return patterns
    
    def _detect_date_patterns(self, password: str) -> List[str]:
        """检测日期模式"""
        patterns = []
        
        # 检查常见的日期格式
        date_patterns = [
            r'\d{4}',  # 年份
            r'\d{2}/\d{2}/\d{2}',  # MM/DD/YY
            r'\d{2}-\d{2}-\d{2}',  # MM-DD-YY
            r'\d{8}',  # 8位数字日期
        ]
        
        import re
        for pattern in date_patterns:
            if re.search(pattern, password):
                patterns.append(f"日期模式: {pattern}")
        
        return patterns

# 使用示例
config = PasswordConfig(
    length=16,
    security_level=SecurityLevel.HIGH,
    include_lowercase=True,
    include_uppercase=True,
    include_digits=True,
    include_special=True,
    force_lowercase=2,
    force_uppercase=2,
    force_digits=2,
    force_special=2,
    no_repeating=True,
    no_sequential=True,
    no_keyboard_patterns=True,
    generation_type=GenerationType.RANDOM
)

generator = PasswordGenerator(config)

# 生成单个密码
result = generator.generate_password()

print(f"生成的密码: {result.password}")
print(f"强度评分: {result.strength_score:.1f}")
print(f"质量等级: {result.quality_level}")
print(f"密码熵: {result.entropy:.1f}")
print(f"字符分布: {result.character_distribution}")

if result.issues:
    print("问题:")
    for issue in result.issues:
        print(f"  - {issue}")

if result.suggestions:
    print("建议:")
    for suggestion in result.suggestions:
        print(f"  - {suggestion}")

# 批量生成密码
batch_results = generator.generate_batch(5)

print(f"\n批量生成 {len(batch_results)} 个密码:")
for i, result in enumerate(batch_results, 1):
    print(f"{i}. {result.password} (强度: {result.strength_score:.1f})")
```

## 安全增强模块

### 加密存储
```python
# security_enhancer.py
import os
import hashlib
import hmac
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, List, Any, Optional, Tuple
import logging

class PasswordSecurityEnhancer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[str, bytes]:
        """哈希密码"""
        if salt is None:
            salt = os.urandom(32)
        
        # 使用PBKDF2进行密码哈希
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        hashed = kdf.derive(password.encode())
        return base64.b64encode(hashed).decode(), salt
    
    def verify_password(self, password: str, hashed: str, salt: bytes) -> bool:
        """验证密码"""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            hashed_bytes = base64.b64decode(hashed)
            new_hashed = kdf.derive(password.encode())
            
            return hmac.compare_digest(hashed_bytes, new_hashed)
        
        except Exception as e:
            self.logger.error(f"密码验证失败: {e}")
            return False
    
    def encrypt_password(self, password: str, key: Optional[bytes] = None) -> Tuple[str, bytes]:
        """加密密码"""
        if key is None:
            key = Fernet.generate_key()
        
        f = Fernet(key)
        encrypted = f.encrypt(password.encode())
        
        return base64.b64encode(encrypted).decode(), key
    
    def decrypt_password(self, encrypted: str, key: bytes) -> Optional[str]:
        """解密密码"""
        try:
            f = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted)
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"密码解密失败: {e}")
            return None
    
    def generate_secure_key(self, length: int = 32) -> bytes:
        """生成安全密钥"""
        return secrets.token_bytes(length)
    
    def calculate_password_strength(self, password: str) -> Dict[str, Any]:
        """计算密码强度指标"""
        metrics = {
            'length': len(password),
            'has_lowercase': any(c.islower() for c in password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_digits': any(c.isdigit() for c in password),
            'has_special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password),
            'unique_chars': len(set(password)),
            'repeated_chars': len(password) - len(set(password)),
            'entropy': self._calculate_entropy(password),
            'crack_time': self._estimate_crack_time(password)
        }
        
        return metrics
    
    def _calculate_entropy(self, password: str) -> float:
        """计算密码熵"""
        charset_size = 0
        
        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            charset_size += 26
        
        if charset_size == 0:
            return 0.0
        
        return len(password) * (charset_size.bit_length() - 1)
    
    def _estimate_crack_time(self, password: str) -> str:
        """估算破解时间"""
        entropy = self._calculate_entropy(password)
        
        # 假设每秒10^12次尝试
        attempts_per_second = 10**12
        total_attempts = 2 ** entropy
        seconds = total_attempts / attempts_per_second
        
        if seconds < 1:
            return "瞬间"
        elif seconds < 60:
            return f"{seconds:.1f} 秒"
        elif seconds < 3600:
            return f"{seconds/60:.1f} 分钟"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} 小时"
        elif seconds < 2592000:
            return f"{seconds/86400:.1f} 天"
        elif seconds < 31536000:
            return f"{seconds/2592000:.1f} 月"
        elif seconds < 3153600000:
            return f"{seconds/31536000:.1f} 年"
        else:
            return "数千年"

# 使用示例
enhancer = PasswordSecurityEnhancer()

# 哈希密码
password = "MySecurePassword123!"
hashed, salt = enhancer.hash_password(password)

print(f"原始密码: {password}")
print(f"哈希密码: {hashed}")
print(f"盐值: {base64.b64encode(salt).decode()}")

# 验证密码
is_valid = enhancer.verify_password(password, hashed, salt)
print(f"密码验证: {'成功' if is_valid else '失败'}")

# 加密密码
encrypted, key = enhancer.encrypt_password(password)
print(f"加密密码: {encrypted}")
print(f"加密密钥: {base64.b64encode(key).decode()}")

# 解密密码
decrypted = enhancer.decrypt_password(encrypted, key)
print(f"解密密码: {decrypted}")

# 计算强度指标
metrics = enhancer.calculate_password_strength(password)
print(f"强度指标:")
for key, value in metrics.items():
    print(f"  {key}: {value}")
```

## 参考资源

### 密码安全
- [NIST密码指南](https://pages.nist.gov/800-63-3/)
- [OWASP密码存储](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [密码强度测试](https://www.passwordmeter.com/)
- [常见密码列表](https://github.com/danielmiessler/SecLists)

### 随机数生成
- [Python secrets模块](https://docs.python.org/3/library/secrets.html)
- [Python random模块](https://docs.python.org/3/library/random.html)
- [密码学随机数](https://cryptography.io/en/latest/random_numbers/)
- [真随机数生成](https://www.random.org/)

### 密码分析
- [密码熵计算](https://en.wikipedia.org/wiki/Password_strength)
- [密码破解时间估算](https://www.security.org/how-secure-is-my-password/)
- [密码模式检测](https://github.com/dropbox/zxcvbn)
- [密码质量评估](https://haveibeenpwned.com/Passwords)

### 加密算法
- [PBKDF2](https://en.wikipedia.org/wiki/PBKDF2)
- [bcrypt](https://en.wikipedia.org/wiki/Bcrypt)
- [scrypt](https://en.wikipedia.org/wiki/Scrypt)
- [Argon2](https://en.wikipedia.org/wiki/Argon2)
