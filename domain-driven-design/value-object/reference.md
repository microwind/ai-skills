# 值对象 - 参考实现

## Java 完整例子

```java
@Value  // Lombok: 自动生成不可变
public class Email {
    String value;

    public Email(String value) {
        if (!isValidEmail(value)) {
            throw new IllegalArgumentException("Invalid email");
        }
        this.value = value;
    }

    private static boolean isValidEmail(String email) {
        return email != null && email.matches("^[^@]+@[^@]+\\.[^@]+$");
    }
}

@Value
public class PhoneNumber {
    String value;

    public PhoneNumber(String value) {
        if (!isValidPhone(value)) {
            throw new IllegalArgumentException("Invalid phone");
        }
        this.value = value;
    }

    private static boolean isValidPhone(String phone) {
        return phone != null && phone.matches("^\\d{10,}$");
    }
}

// 使用
Email email1 = new Email("john@example.com");
Email email2 = new Email("john@example.com");
assertEquals(email1, email2);  // 值相等
```

## Python 完整例子

```python
from dataclasses import dataclass
from typing import NamedTuple

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    zip_code: str

    def __post_init__(self):
        if not self.zip_code:
            raise ValueError("ZIP code required")

# 使用
addr1 = Address("123 Main St", "New York", "10001")
addr2 = Address("123 Main St", "New York", "10001")
assert addr1 == addr2  # 值相等
```

## TypeScript 完整例子

```typescript
class Email {
    private readonly value: string;

    constructor(value: string) {
        if (!this.isValid(value)) {
            throw new Error("Invalid email");
        }
        this.value = value;
    }

    private isValid(email: string): boolean {
        return /^[^@]+@[^@]+\.[^@]+$/.test(email);
    }

    getValue(): string { return this.value; }

    equals(other: Email): boolean {
        return this.value === other.value;
    }

    hashCode(): number {
        return this.value.length;
    }
}
```

值对象通过不可变和值相等提高代码安全性。
