---
name: 密码生成器
description: "当生成安全密码、创建随机字符串、管理密码策略、验证密码强度或批量生成密码时，提供全面的密码生成和安全管理解决方案。"
license: MIT
---

# 密码生成器技能

## 概述
密码生成器是信息安全的基础工具，用于创建强随机密码、验证密码强度、实施密码策略和管理密码生命周期。它帮助用户和系统管理员创建符合安全标准的密码，降低密码被破解的风险。

**核心原则**: 随机性、复杂性、唯一性、可管理性、安全性。

## 何时使用

**始终:**
- 生成用户账户密码
- 创建API密钥和令牌
- 生成随机安全码
- 验证密码强度
- 批量密码生成
- 密码策略实施
- 安全令牌创建
- 加密密钥生成

**触发短语:**
- "生成安全密码"
- "密码强度检查"
- "随机密码生成"
- "密码策略设置"
- "批量密码创建"
- "密码验证工具"
- "安全令牌生成"
- "密码管理最佳实践"

## 密码安全标准

### 强度要求
- **长度**: 至少12-16个字符
- **复杂度**: 包含大小写字母、数字、特殊字符
- **随机性**: 使用密码学安全的随机数生成器
- **唯一性**: 每个密码都应该是唯一的
- **定期更换**: 定期更新密码

### 密码类型
- **用户密码**: 用于系统登录
- **API密钥**: 用于API认证
- **会话令牌**: 临时访问凭证
- **加密密钥**: 数据加密用途
- **一次性密码**: 短期验证码

## 常见密码问题

### 弱密码问题
```
问题:
使用简单、易猜测的密码

症状:
- 密码长度过短
- 缺乏字符多样性
- 使用常见词汇
- 包含个人信息
- 键盘模式密码

解决方案:
- 增加密码长度
- 使用字符组合
- 避免字典词汇
- 排除个人信息
- 使用随机生成
```

### 密码复用问题
```
问题:
在多个系统中使用相同密码

症状:
- 一处泄露，处处危险
- 密码管理困难
- 安全风险累积
- 合规性问题

解决方案:
- 为每个系统使用唯一密码
- 使用密码管理器
- 实施单点登录
- 定期轮换密码
- 使用多因素认证
```

### 存储安全问题
```
问题:
密码存储不安全

症状:
- 明文存储密码
- 使用弱哈希算法
- 缺少盐值
- 密码可逆加密

解决方案:
- 使用强哈希算法
- 添加随机盐值
- 实施密钥拉伸
- 使用专用密码库
- 定期更新存储方法
```

## 代码实现示例

### 密码生成器核心类
```python
import secrets
import string
import hashlib
import base64
import re
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timedelta
import pyotp  # 需要安装: pip install pyotp
import cryptography.fernet  # 需要安装: pip install cryptography

class PasswordStrength(Enum):
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    FAIR = "fair"
    GOOD = "good"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

class PasswordType(Enum):
    USER_PASSWORD = "user_password"
    API_KEY = "api_key"
    SESSION_TOKEN = "session_token"
    ENCRYPTION_KEY = "encryption_key"
    ONE_TIME_PASSWORD = "one_time_password"

@dataclass
class PasswordPolicy:
    """密码策略"""
    min_length: int = 12
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    exclude_ambiguous: bool = True
    exclude_similar: bool = True
    max_consecutive_chars: int = 2
    no_common_patterns: bool = True
    custom_excluded_chars: str = ""

@dataclass
class PasswordAnalysis:
    """密码分析结果"""
    password: str
    strength: PasswordStrength
    score: int  # 0-100
    issues: List[str]
    suggestions: List[str]
    entropy: float
    crack_time: str

class SecurePasswordGenerator:
    """安全密码生成器"""
    
    def __init__(self, policy: PasswordPolicy = None):
        self.policy = policy or PasswordPolicy()
        
        # 字符集定义
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # 易混淆字符
        self.ambiguous_chars = "0O1lI"
        self.similar_chars = "ilLo0O"
        
        # 常见密码模式
        self.common_patterns = [
            r".*123.*", r".*abc.*", r".*qwe.*", r".*asd.*",
            r".*password.*", r".*admin.*", r".*user.*",
            r"(.)\1{2,}",  # 重复字符
            r"(?:123|abc|qwe|asd)",  # 键盘模式
        ]
    
    def generate_password(self, length: int = None, password_type: PasswordType = PasswordType.USER_PASSWORD) -> str:
        """生成安全密码"""
        if length is None:
            length = self.policy.min_length
        
        length = max(length, self.policy.min_length)
        length = min(length, self.policy.max_length)
        
        if password_type == PasswordType.USER_PASSWORD:
            return self._generate_user_password(length)
        elif password_type == PasswordType.API_KEY:
            return self._generate_api_key(length)
        elif password_type == PasswordType.SESSION_TOKEN:
            return self._generate_session_token()
        elif password_type == PasswordType.ENCRYPTION_KEY:
            return self._generate_encryption_key()
        elif password_type == PasswordType.ONE_TIME_PASSWORD:
            return self._generate_one_time_password()
        else:
            return self._generate_user_password(length)
    
    def _generate_user_password(self, length: int) -> str:
        """生成用户密码"""
        # 构建字符集
        charset = ""
        required_chars = []
        
        if self.policy.require_lowercase:
            charset += self.lowercase
            required_chars.append(secrets.choice(self.lowercase))
        
        if self.policy.require_uppercase:
            charset += self.uppercase
            required_chars.append(secrets.choice(self.uppercase))
        
        if self.policy.require_digits:
            charset += self.digits
            required_chars.append(secrets.choice(self.digits))
        
        if self.policy.require_special:
            charset += self.special
            required_chars.append(secrets.choice(self.special))
        
        # 移除易混淆字符
        if self.policy.exclude_ambiguous:
            charset = ''.join(c for c in charset if c not in self.ambiguous_chars)
        
        # 移除自定义排除字符
        if self.policy.custom_excluded_chars:
            charset = ''.join(c for c in charset if c not in self.policy.custom_excluded_chars)
        
        # 确保字符集不为空
        if not charset:
            charset = string.ascii_letters + string.digits
        
        # 生成剩余字符
        remaining_length = length - len(required_chars)
        password_chars = required_chars + [secrets.choice(charset) for _ in range(remaining_length)]
        
        # 打乱字符顺序
        secrets.SystemRandom().shuffle(password_chars)
        
        password = ''.join(password_chars)
        
        # 验证生成的密码
        if not self._validate_password(password):
            # 如果验证失败，重新生成
            return self._generate_user_password(length)
        
        return password
    
    def _generate_api_key(self, length: int = 32) -> str:
        """生成API密钥"""
        # API密钥通常使用Base64编码的随机字节
        random_bytes = secrets.token_bytes(length)
        api_key = base64.urlsafe_b64encode(random_bytes).decode('ascii').rstrip('=')
        
        return api_key
    
    def _generate_session_token(self) -> str:
        """生成会话令牌"""
        # 生成32字节的随机令牌
        token = secrets.token_urlsafe(32)
        return token
    
    def _generate_encryption_key(self) -> str:
        """生成加密密钥"""
        # 生成32字节(256位)的加密密钥
        key = base64.b64encode(secrets.token_bytes(32)).decode('ascii')
        return key
    
    def _generate_one_time_password(self, digits: int = 6) -> str:
        """生成一次性密码"""
        # 生成数字OTP
        otp = ''.join(str(secrets.randbelow(10)) for _ in range(digits))
        return otp
    
    def _validate_password(self, password: str) -> bool:
        """验证密码是否符合策略"""
        # 检查长度
        if len(password) < self.policy.min_length or len(password) > self.policy.max_length:
            return False
        
        # 检查字符要求
        if self.policy.require_uppercase and not any(c.isupper() for c in password):
            return False
        
        if self.policy.require_lowercase and not any(c.islower() for c in password):
            return False
        
        if self.policy.require_digits and not any(c.isdigit() for c in password):
            return False
        
        if self.policy.require_special and not any(c in self.special for c in password):
            return False
        
        # 检查排除字符
        if self.policy.exclude_ambiguous and any(c in self.ambiguous_chars for c in password):
            return False
        
        if self.policy.custom_excluded_chars and any(c in self.policy.custom_excluded_chars for c in password):
            return False
        
        # 检查连续字符
        if self._has_consecutive_chars(password, self.policy.max_consecutive_chars):
            return False
        
        # 检查常见模式
        if self.policy.no_common_patterns and self._has_common_patterns(password):
            return False
        
        return True
    
    def _has_consecutive_chars(self, password: str, max_consecutive: int) -> bool:
        """检查连续字符"""
        for i in range(len(password) - max_consecutive):
            if all(password[i + j] == password[i] for j in range(max_consecutive + 1)):
                return True
        return False
    
    def _has_common_patterns(self, password: str) -> bool:
        """检查常见模式"""
        password_lower = password.lower()
        for pattern in self.common_patterns:
            if re.match(pattern, password_lower):
                return True
        return False
    
    def analyze_password(self, password: str) -> PasswordAnalysis:
        """分析密码强度"""
        issues = []
        suggestions = []
        
        # 计算熵
        entropy = self._calculate_entropy(password)
        
        # 检查长度
        length_score = min(len(password) / 20, 1.0) * 20
        if len(password) < 8:
            issues.append("密码长度过短，建议至少12个字符")
            suggestions.append("增加密码长度以提高安全性")
        elif len(password) < 12:
            issues.append("密码长度较短")
            suggestions.append("考虑使用更长的密码")
        
        # 检查字符多样性
        char_diversity = 0
        if any(c.islower() for c in password):
            char_diversity += 1
        else:
            issues.append("缺少小写字母")
            suggestions.append("添加小写字母")
        
        if any(c.isupper() for c in password):
            char_diversity += 1
        else:
            issues.append("缺少大写字母")
            suggestions.append("添加大写字母")
        
        if any(c.isdigit() for c in password):
            char_diversity += 1
        else:
            issues.append("缺少数字")
            suggestions.append("添加数字")
        
        if any(c in self.special for c in password):
            char_diversity += 1
        else:
            issues.append("缺少特殊字符")
            suggestions.append("添加特殊字符")
        
        diversity_score = (char_diversity / 4) * 25
        
        # 检查常见模式
        pattern_penalty = 0
        if self._has_common_patterns(password):
            pattern_penalty = 20
            issues.append("密码包含常见模式，容易被猜测")
            suggestions.append("避免使用常见词汇和键盘模式")
        
        # 检查连续字符
        if self._has_consecutive_chars(password, 3):
            pattern_penalty += 10
            issues.append("包含连续重复字符")
            suggestions.append("避免连续重复字符")
        
        # 计算总分
        score = int(length_score + diversity_score - pattern_penalty)
        score = max(0, min(100, score))
        
        # 确定强度等级
        if score < 20:
            strength = PasswordStrength.VERY_WEAK
        elif score < 40:
            strength = PasswordStrength.WEAK
        elif score < 60:
            strength = PasswordStrength.FAIR
        elif score < 80:
            strength = PasswordStrength.GOOD
        elif score < 90:
            strength = PasswordStrength.STRONG
        else:
            strength = PasswordStrength.VERY_STRONG
        
        # 估算破解时间
        crack_time = self._estimate_crack_time(entropy)
        
        return PasswordAnalysis(
            password=password,
            strength=strength,
            score=score,
            issues=issues,
            suggestions=suggestions,
            entropy=entropy,
            crack_time=crack_time
        )
    
    def _calculate_entropy(self, password: str) -> float:
        """计算密码熵"""
        charset_size = 0
        
        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(c in self.special for c in password):
            charset_size += len(self.special)
        
        if charset_size == 0:
            return 0
        
        import math
        entropy = len(password) * math.log2(charset_size)
        return entropy
    
    def _estimate_crack_time(self, entropy: float) -> str:
        """估算破解时间"""
        # 假设每秒尝试10^12次密码
        attempts_per_second = 10**12
        total_combinations = 2 ** entropy
        seconds = total_combinations / attempts_per_second
        
        if seconds < 1:
            return "瞬间"
        elif seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            return f"{int(seconds/60)}分钟"
        elif seconds < 86400:
            return f"{int(seconds/3600)}小时"
        elif seconds < 2592000:
            return f"{int(seconds/86400)}天"
        elif seconds < 31536000:
            return f"{int(seconds/2592000)}个月"
        elif seconds < 315360000:
            return f"{int(seconds/31536000)}年"
        else:
            return "数千年"
    
    def batch_generate(self, count: int, length: int = None, 
                      password_type: PasswordType = PasswordType.USER_PASSWORD) -> List[str]:
        """批量生成密码"""
        passwords = []
        
        for _ in range(count):
            password = self.generate_password(length, password_type)
            passwords.append(password)
        
        return passwords
    
    def generate_passphrase(self, word_count: int = 6, separator: str = "-", 
                          capitalize: bool = True, include_numbers: bool = False) -> str:
        """生成密码短语"""
        # 常用单词列表（简化版本）
        word_list = [
            "apple", "banana", "orange", "grape", "lemon", "peach",
            "coffee", "water", "juice", "milk", "tea", "soda",
            "happy", "smile", "laugh", "joy", "fun", "play",
            "computer", "keyboard", "mouse", "screen", "data", "code",
            "mountain", "ocean", "river", "forest", "desert", "island",
            "dragon", "phoenix", "wizard", "magic", "spell", "power"
        ]
        
        words = []
        for _ in range(word_count):
            word = secrets.choice(word_list)
            if capitalize:
                word = word.capitalize()
            if include_numbers and secrets.randbelow(3) == 0:
                word += str(secrets.randbelow(100))
            words.append(word)
        
        return separator.join(words)

class PasswordManager:
    """密码管理器"""
    
    def __init__(self, master_password: str):
        self.master_password = master_password
        self.encrypted_vault = {}
        self.fernet = self._create_fernet_key(master_password)
    
    def _create_fernet_key(self, password: str) -> cryptography.fernet.Fernet:
        """从主密码创建加密密钥"""
        # 使用PBKDF2从主密码派生密钥
        import os
        salt = b'salt_for_password_manager'  # 在实际应用中应该使用随机盐
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return cryptography.fernet.Fernet(key)
    
    def store_password(self, service: str, username: str, password: str) -> bool:
        """存储密码"""
        try:
            data = {
                'username': username,
                'password': password,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            encrypted_data = self.fernet.encrypt(json.dumps(data).encode())
            self.encrypted_vault[service] = encrypted_data
            return True
        except Exception as e:
            print(f"存储密码失败: {str(e)}")
            return False
    
    def retrieve_password(self, service: str) -> Optional[Dict]:
        """检索密码"""
        try:
            encrypted_data = self.encrypted_vault.get(service)
            if encrypted_data:
                decrypted_data = self.fernet.decrypt(encrypted_data).decode()
                return json.loads(decrypted_data)
            return None
        except Exception as e:
            print(f"检索密码失败: {str(e)}")
            return None
    
    def list_services(self) -> List[str]:
        """列出所有服务"""
        return list(self.encrypted_vault.keys())
    
    def delete_password(self, service: str) -> bool:
        """删除密码"""
        if service in self.encrypted_vault:
            del self.encrypted_vault[service]
            return True
        return False
    
    def change_master_password(self, new_password: str) -> bool:
        """更改主密码"""
        try:
            new_fernet = self._create_fernet_key(new_password)
            
            # 重新加密所有密码
            new_vault = {}
            for service, encrypted_data in self.encrypted_vault.items():
                decrypted_data = self.fernet.decrypt(encrypted_data).decode()
                reencrypted_data = new_fernet.encrypt(decrypted_data.encode())
                new_vault[service] = reencrypted_data
            
            self.fernet = new_fernet
            self.encrypted_vault = new_vault
            self.master_password = new_password
            return True
        except Exception as e:
            print(f"更改主密码失败: {str(e)}")
            return False

class TOTPGenerator:
    """TOTP（基于时间的一次性密码）生成器"""
    
    @staticmethod
    def generate_secret() -> str:
        """生成TOTP密钥"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(secret: str, issuer: str = "MyApp", account_name: str = "user@example.com") -> str:
        """生成QR码URL"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(account_name, issuer_name=issuer)
    
    @staticmethod
    def generate_totp(secret: str) -> str:
        """生成当前TOTP"""
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    @staticmethod
    def verify_totp(secret: str, token: str, valid_window: int = 1) -> bool:
        """验证TOTP"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=valid_window)

# 使用示例
def main():
    """示例使用"""
    print("🔐 安全密码生成器启动")
    print("=" * 50)
    
    # 创建密码生成器
    policy = PasswordPolicy(
        min_length=16,
        require_uppercase=True,
        require_lowercase=True,
        require_digits=True,
        require_special=True,
        exclude_ambiguous=True
    )
    
    generator = SecurePasswordGenerator(policy)
    
    # 生成用户密码
    print("\n👤 生成用户密码:")
    user_password = generator.generate_password(16, PasswordType.USER_PASSWORD)
    print(f"  密码: {user_password}")
    
    # 分析密码强度
    analysis = generator.analyze_password(user_password)
    print(f"  强度: {analysis.strength.value}")
    print(f"  评分: {analysis.score}/100")
    print(f"  熵值: {analysis.entropy:.2f}")
    print(f"  破解时间: {analysis.crack_time}")
    
    if analysis.issues:
        print("  问题:")
        for issue in analysis.issues:
            print(f"    - {issue}")
    
    # 生成API密钥
    print(f"\n🔑 生成API密钥:")
    api_key = generator.generate_password(32, PasswordType.API_KEY)
    print(f"  API密钥: {api_key}")
    
    # 生成会话令牌
    print(f"\n🎫 生成会话令牌:")
    session_token = generator.generate_password(0, PasswordType.SESSION_TOKEN)
    print(f"  会话令牌: {session_token}")
    
    # 生成加密密钥
    print(f"\n🔒 生成加密密钥:")
    encryption_key = generator.generate_password(0, PasswordType.ENCRYPTION_KEY)
    print(f"  加密密钥: {encryption_key}")
    
    # 生成一次性密码
    print(f"\n📱 生成一次性密码:")
    otp = generator.generate_password(6, PasswordType.ONE_TIME_PASSWORD)
    print(f"  OTP: {otp}")
    
    # 批量生成密码
    print(f"\n📦 批量生成密码:")
    batch_passwords = generator.batch_generate(5, 12)
    for i, pwd in enumerate(batch_passwords, 1):
        print(f"  {i}: {pwd}")
    
    # 生成密码短语
    print(f"\n📝 生成密码短语:")
    passphrase = generator.generate_passphrase(4, "-", True, False)
    print(f"  密码短语: {passphrase}")
    
    # 密码管理器演示
    print(f"\n🗄️  密码管理器演示:")
    manager = PasswordManager("master_password_123")
    
    # 存储密码
    manager.store_password("github.com", "username", user_password)
    manager.store_password("google.com", "user@gmail.com", "another_password")
    
    # 列出服务
    services = manager.list_services()
    print(f"  存储的服务: {', '.join(services)}")
    
    # 检索密码
    stored_password = manager.retrieve_password("github.com")
    if stored_password:
        print(f"  GitHub密码: {stored_password['password'][:8]}...")
    
    # TOTP演示
    print(f"\n📱 TOTP演示:")
    totp_secret = TOTPGenerator.generate_secret()
    print(f"  TOTP密钥: {totp_secret}")
    
    current_totp = TOTPGenerator.generate_totp(totp_secret)
    print(f"  当前TOTP: {current_totp}")
    
    print("\n✅ 密码生成器演示完成!")

if __name__ == "__main__":
    main()
```

### 密码强度测试器
```python
class PasswordStrengthTester:
    """密码强度测试器"""
    
    def __init__(self):
        self.common_passwords = self._load_common_passwords()
        self.dictionary_words = self._load_dictionary_words()
    
    def _load_common_passwords(self) -> set:
        """加载常见密码列表"""
        # 简化版本，实际应该从文件加载
        return {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234567890', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm'
        }
    
    def _load_dictionary_words(self) -> set:
        """加载字典词汇"""
        # 简化版本
        return {
            'apple', 'banana', 'orange', 'computer', 'internet',
            'website', 'database', 'security', 'network', 'system'
        }
    
    def comprehensive_test(self, password: str) -> Dict:
        """全面密码测试"""
        results = {
            'length_test': self._test_length(password),
            'character_test': self._test_character_diversity(password),
            'pattern_test': self._test_patterns(password),
            'common_password_test': self._test_common_passwords(password),
            'dictionary_test': self._test_dictionary_words(password),
            'entropy_test': self._test_entropy(password),
            'overall_score': 0
        }
        
        # 计算总分
        total_score = sum(test['score'] for test in results.values() if 'score' in test)
        results['overall_score'] = total_score / 6
        
        return results
    
    def _test_length(self, password: str) -> Dict:
        """测试密码长度"""
        length = len(password)
        
        if length < 8:
            score = 0
            feedback = "密码长度过短"
        elif length < 12:
            score = 40
            feedback = "密码长度较短"
        elif length < 16:
            score = 70
            feedback = "密码长度适中"
        elif length < 20:
            score = 90
            feedback = "密码长度良好"
        else:
            score = 100
            feedback = "密码长度优秀"
        
        return {
            'score': score,
            'length': length,
            'feedback': feedback
        }
    
    def _test_character_diversity(self, password: str) -> Dict:
        """测试字符多样性"""
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        diversity_score = sum([has_lower, has_upper, has_digit, has_special])
        
        score = diversity_score * 25
        
        missing_types = []
        if not has_lower:
            missing_types.append("小写字母")
        if not has_upper:
            missing_types.append("大写字母")
        if not has_digit:
            missing_types.append("数字")
        if not has_special:
            missing_types.append("特殊字符")
        
        feedback = f"使用了{diversity_score}/4种字符类型"
        if missing_types:
            feedback += f"，缺少: {', '.join(missing_types)}"
        
        return {
            'score': score,
            'diversity': diversity_score,
            'missing_types': missing_types,
            'feedback': feedback
        }
    
    def _test_patterns(self, password: str) -> Dict:
        """测试密码模式"""
        issues = []
        score = 100
        
        # 检查重复字符
        if re.search(r'(.)\1{2,}', password):
            issues.append("包含连续重复字符")
            score -= 20
        
        # 检查键盘模式
        keyboard_patterns = [
            r'123456', r'qwerty', r'asdfgh', r'zxcvbn',
            r'qwertyuiop', r'asdfghjkl', r'zxcvbnm'
        ]
        
        password_lower = password.lower()
        for pattern in keyboard_patterns:
            if pattern in password_lower:
                issues.append("包含键盘模式")
                score -= 30
                break
        
        # 检查序列字符
        if re.search(r'(?:abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password_lower):
            issues.append("包含字母序列")
            score -= 15
        
        if re.search(r'(?:123|234|345|456|567|678|789)', password):
            issues.append("包含数字序列")
            score -= 15
        
        feedback = "未发现明显模式" if not issues else f"发现模式: {', '.join(issues)}"
        
        return {
            'score': max(0, score),
            'issues': issues,
            'feedback': feedback
        }
    
    def _test_common_passwords(self, password: str) -> Dict:
        """测试常见密码"""
        password_lower = password.lower()
        
        if password_lower in self.common_passwords:
            score = 0
            feedback = "这是常见密码，非常不安全"
        elif any(common in password_lower for common in self.common_passwords):
            score = 20
            feedback = "包含常见密码元素"
        else:
            score = 100
            feedback = "不是常见密码"
        
        return {
            'score': score,
            'is_common': password_lower in self.common_passwords,
            'feedback': feedback
        }
    
    def _test_dictionary_words(self, password: str) -> Dict:
        """测试字典词汇"""
        password_lower = password.lower()
        
        found_words = []
        for word in self.dictionary_words:
            if word in password_lower:
                found_words.append(word)
        
        if found_words:
            score = max(20, 100 - len(found_words) * 20)
            feedback = f"包含字典词汇: {', '.join(found_words)}"
        else:
            score = 100
            feedback = "未包含常见字典词汇"
        
        return {
            'score': score,
            'found_words': found_words,
            'feedback': feedback
        }
    
    def _test_entropy(self, password: str) -> Dict:
        """测试密码熵"""
        charset_size = 0
        
        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            charset_size += 23
        
        if charset_size == 0:
            entropy = 0
            score = 0
        else:
            import math
            entropy = len(password) * math.log2(charset_size)
            
            # 根据熵值评分
            if entropy < 40:
                score = 20
            elif entropy < 60:
                score = 40
            elif entropy < 80:
                score = 60
            elif entropy < 100:
                score = 80
            else:
                score = 100
        
        return {
            'score': score,
            'entropy': entropy,
            'feedback': f"密码熵值: {entropy:.2f} bits"
        }

# 使用示例
def main():
    tester = PasswordStrengthTester()
    print("密码强度测试器已准备就绪!")

if __name__ == "__main__":
    main()
```

## 密码管理最佳实践

### 密码生成
1. **使用密码生成器**: 避免人工创建密码
2. **足够的长度**: 至少12-16个字符
3. **字符多样性**: 包含所有字符类型
4. **避免个人信息**: 不使用生日、姓名等
5. **定期更换**: 定期更新密码

### 密码存储
1. **强哈希算法**: 使用bcrypt、Argon2等
2. **添加盐值**: 每个密码使用唯一盐值
3. **密钥拉伸**: 增加计算成本
4. **专用库**: 使用成熟的密码库
5. **定期更新**: 跟进最佳实践

### 密码管理
1. **密码管理器**: 使用专业工具管理
2. **主密码强保护**: 主密码要足够强大
3. **双因素认证**: 启用2FA/MFA
4. **定期审计**: 检查密码安全性
5. **应急计划**: 制定密码恢复策略

## 密码工具推荐

### 密码生成器
- **KeePass**: 开源密码管理器
- **1Password**: 商业密码管理器
- **Bitwarden**: 开源密码管理器
- **LastPass**: 在线密码管理器

### 安全工具
- **Have I Been Pwned**: 密码泄露检查
- **zxcvbn**: 密码强度评估
- **Hashcat**: 密码破解工具
- **John the Ripper**: 密码破解工具

### 开发库
- **bcrypt**: 密码哈希库
- **Argon2**: 现代密码哈希
- **PyOTP**: Python OTP库
- **cryptography**: Python加密库

## 相关技能

- **cryptography** - 密码学基础
- **authentication** - 身份认证
- **security-auditing** - 安全审计
- **encryption** - 数据加密
- **identity-management** - 身份管理
- **security-policy** - 安全策略
