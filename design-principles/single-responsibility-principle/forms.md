# 单一职责原则 - 诊断与规划表

## 第1步: 需求诊断 - 你的类是否需要拆分？

### 🔍 快速检查清单

```
□ 类中有超过10个公共方法
□ 类有多于一个改变的理由
□ 类名包含 Manager、Helper、Processor、Service、Util 等宽泛词汇
□ 难以用一句话清晰描述这个类的职责
□ 类中的不同方法操作完全不同的数据
□ 修改一个功能时，需要同时改动该类的多个不相关部分
□ 单元测试需要mock超过3个外部依赖
□ 类的代码行数超过200行
□ 该类与超过5个其他类有强耦合
```

**诊断标准**:
- ✅ 勾选 0-1 项 → **很好，职责清晰**
- ⚠️ 勾选 2-4 项 → **应该考虑拆分**
- ❌ 勾选 5 项以上 → **必须立即重构，职责混乱**

### 🎯 具体场景评估矩阵

| 类型示例 | 是否违反SRP | 改变理由数 | 建议 | 优先级 |
|---------|-----------|----------|------|--------|
| User（只有名字、邮箱、ID） | ✅否 | 1 | 保持原样 | N/A |
| UserManager（创建、删除、验证、邮件、密码） | ❌是 | 5+ | 立即拆分 | ⭐⭐⭐⭐⭐ |
| OrderProcessor（创建订单、支付、库存、发货） | ❌是 | 4 | 立即拆分 | ⭐⭐⭐⭐⭐ |
| UserRepository（只有数据库操作） | ✅否 | 1 | 保持原样 | N/A |
| PaymentService（处理支付、生成账单、发邮件） | ❌是 | 3 | 立即拆分 | ⭐⭐⭐⭐ |

---

## 第2步: 职责识别 - 5个识别方法

### 方法1: 改变理由分析法

```
找出这个类可能被修改的所有理由，每一个理由就是一个职责：

当前类：UserValidator

可能被修改的理由：
1. □ 邮箱验证规则改变（邮箱格式标准升级）
2. □ 密码强度规则改变（安全要求提高）
3. □ 用户名验证规则改变（支持更多字符）
4. □ 数据库保存方式改变（从SQL改为NoSQL）

结论：有4个不同的改变理由 → 需要拆分为：
- EmailValidator
- PasswordValidator
- UsernameValidator
- UserRepository
```

**清单**：
```
当前类名: ___________________________

可能被修改的理由（列出所有）:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________
4. _______________________________________________
5. _______________________________________________

理由数 = _____ 个

□ 如果 > 1 → 需要拆分
```

### 方法2: 类名分析法

```
坏的类名（指示职责混乱）：
□ UserManager       （Manager什么？管理用户？验证？保存？）
□ OrderProcessor    （处理订单的什么？支付？库存？）
□ ServiceHelper     （帮助什么服务？）
□ DataHandler       （处理什么数据？读？写？验证？）

好的类名（职责清晰）：
□ EmailValidator    （就是验证邮箱格式）
□ UserRepository    （就是用户数据持久化）
□ PaymentProcessor  （就是处理支付）
□ PasswordEncryptor （就是加密密码）

你的类名: _______________________________

是否是坏类名？ YES / NO
```

### 方法3: 内聚力分析法

```
检查类中所有方法是否都操作同一组核心数据：

类：OrderManager

方法及其操作数据：
1. createOrder()          → 操作 {orderId, items, customer} ✓
2. calculateTotal()       → 操作 {items, prices} ✓
3. processPayment()       → 操作 {paymentInfo, amount} ❌ 不相关！
4. updateInventory()      → 操作 {inventory, items} ❌ 不相关！
5. createShipment()       → 操作 {shipmentInfo} ❌ 不相关！

结论：只有2个方法操作订单核心数据，其他都不相关 → 需要拆分
```

**清单**：
```
当前类名: ___________________________

类的核心数据属性（1-3个）:
- _______________________________
- _______________________________
- _______________________________

类中的所有公开方法及它们操作的数据：
1. __________ () → 操作 {__________} ✓/❌
2. __________ () → 操作 {__________} ✓/❌
3. __________ () → 操作 {__________} ✓/❌
4. __________ () → 操作 {__________} ✓/❌
5. __________ () → 操作 {__________} ✓/❌

有多少方法✓操作核心数据？ _____ / _____
有多少方法❌操作其他数据？ _____ / _____

□ 如果超过30%的方法不操作核心数据 → 需要拆分
```

### 方法4: 测试依赖分析法

```
写单元测试时，需要mock多少个外部依赖？

测试 UserManager.registerUser():
需要mock：
1. □ DatabaseConnection  (保存用户)
2. □ PasswordEncryptor   (加密密码)
3. □ EmailService        (发送欢迎邮件)
4. □ PasswordValidator   (验证密码)
5. □ Logger              (记录日志)

总计需要mock 5个依赖 → 职责太多！应该拆分
```

**清单**：
```
当前类名: ___________________________

要测试这个类的一个主要方法，需要mock：
□ _____________ (原因：_______________)
□ _____________ (原因：_______________)
□ _____________ (原因：_______________)
□ _____________ (原因：_______________)
□ _____________ (原因：_______________)

mock依赖数 = _____ 个

□ 如果 > 3 个 → 职责太多，需要拆分
```

### 方法5: 关键词分析法

```
观察类中方法名和职责描述，是否包含多个不同的关键词？

坏例子 - UserManager:
方法和职责：
- validateEmail()        (验证)
- validatePassword()     (验证)
- encryptPassword()      (加密)
- createUser()           (创建)
- deleteUser()           (删除)
- sendWelcomeEmail()     (邮件)
- logUserAction()        (日志)
- updateDatabase()       (数据库)

关键词：验证、加密、创建、删除、邮件、日志、数据库 → 7个不同的关键词！

好例子 - PasswordValidator:
方法和职责：
- validate()             (验证)
- isStrong()             (验证)
- validateLength()       (验证)
- validateComplexity()   (验证)

关键词：验证 → 1个关键词！
```

**清单**：
```
当前类名: ___________________________

类的所有公开方法:
1. ___________________________
2. ___________________________
3. ___________________________
4. ___________________________
5. ___________________________

这些方法涉及的不同概念/关键词：
□ ________________  (出现在方法：___)
□ ________________  (出现在方法：___)
□ ________________  (出现在方法：___)
□ ________________  (出现在方法：___)

不同概念数 = _____ 个

□ 如果 > 2 个 → 可能职责混乱，需要拆分
```

---

## 第3步: 拆分规划 - 5个关键步骤

### ✏️ 步骤1: 列出所有职责

```
当前类名: UserManager

职责列表（从诊断中提取）：
1. □ 验证用户数据（邮箱、密码、用户名）
   相关方法：validateEmail(), validatePassword()
   预计代码行数：50-100

2. □ 用户信息管理（创建、更新、查询）
   相关方法：createUser(), updateUser(), getUser()
   预计代码行数：100-150

3. □ 密码处理（加密、验证、重置）
   相关方法：encryptPassword(), checkPassword(), resetPassword()
   预计代码行数：80-120

4. □ 数据库操作（CRUD）
   相关方法：save(), delete(), load()
   预计代码行数：60-100

5. □ 邮件发送（欢迎邮件、重置邮件）
   相关方法：sendWelcomeEmail(), sendResetEmail()
   预计代码行数：40-60
```

### ✏️ 步骤2: 设计新的类结构

```
当前不合理的结构：
UserManager（职责太多）
  ├── validate*()
  ├── encrypt*()
  ├── create/update/get
  ├── save/delete/load
  └── send*()

拆分后的清晰结构：

User （用户信息）
  ├── name, email
  ├── getId(), getName()

UserValidator （验证）
  ├── validateEmail()
  ├── validatePassword()
  ├── validateUsername()

PasswordEncryptor （密码加密）
  ├── encrypt()
  ├── compare()

UserRepository （数据持久化）
  ├── save()
  ├── findById()
  ├── delete()

UserNotificationService （邮件通知）
  ├── sendWelcomeEmail()
  ├── sendPasswordReset()

UserService （业务流程聚合）
  ├── registerUser()
  ├── resetPassword()
  ├── deleteUser()
```

### ✏️ 步骤3: 分配职责到新类

```
职责 1：用户信息管理
新类名：User
方法：
  □ __getName()
  □ __getEmail()
  □ __updateProfile()
依赖：无（纯数据对象）
测试复杂度：低

职责 2：用户数据验证
新类名：UserValidator
方法：
  □ __validateEmail()
  □ __validatePassword()
  □ __validate()
依赖：无
测试复杂度：低

职责 3：用户数据持久化
新类名：UserRepository
方法：
  □ __save()
  □ __findById()
  □ __delete()
依赖：数据库连接（注入）
测试复杂度：中

职责 4：邮件通知
新类名：UserNotificationService
方法：
  □ __sendWelcomeEmail()
  □ __sendPasswordReset()
依赖：邮件服务（注入）
测试复杂度：中

职责 5：业务流程协调
新类名：UserRegistrationService
方法：
  □ __registerUser()
  □ __resetPassword()
依赖：上面所有的类（通过构造注入）
测试复杂度：高（但可以mock）
```

### ✏️ 步骤4: 识别类之间的依赖

```
新结构中的依赖关系：

UserRegistrationService
  ├─> 依赖 User (创建)
  ├─> 依赖 UserValidator (验证)
  ├─> 依赖 UserRepository (保存)
  └─> 依赖 UserNotificationService (邮件)

依赖规则（检查）：
□ User 不依赖任何其他类（纯数据）
□ UserValidator 不依赖其他业务类（纯验证）
□ UserRepository 只依赖数据库（基础设施）
□ UserNotificationService 只依赖邮件（基础设施）
□ UserRegistrationService 依赖上述所有（业务协调）

✓ 依赖关系清晰，形成合理的分层
```

### ✏️ 步骤5: 迁移计划

```
迁移步骤：

第1步：创建新类文件（不删除旧类）
  □ User.java
  □ UserValidator.java
  □ UserRepository.java
  □ UserNotificationService.java
  □ UserRegistrationService.java

第2步：在新类中实现所有逻辑
  预计时间：2-3 天
  评审标准：100% 单元测试覆盖

第3步：将现有代码迁移到使用新类
  逐步迁移，不一次性改大量代码
  预计时间：1-2 天

第4步：更新所有单元测试
  预计时间：1-2 天

第5步：删除旧的 UserManager 类
  前提：所有调用都已迁移
  预计时间：1-2 小时

总时间估计：5-9 天
```

---

## 第4步: 测试计划

### 单位测试覆盖计划

```
对于每个新类，编写单元测试：

1. User 类
   □ 测试 updateProfile() 正确更新名字
   □ 测试 updateProfile() 正确更新邮箱
   □ 测试 getId() 返回正确的ID
   覆盖率：100%

2. UserValidator 类
   □ 测试 validateEmail() 接受有效邮箱
   □ 测试 validateEmail() 拒绝无效邮箱
   □ 测试 validatePassword() 检查长度
   □ 测试 validatePassword() 检查复杂性
   覆盖率：100%

3. UserRepository 类
   □ 测试 save() 正确保存用户
   □ 测试 findById() 返回正确用户
   □ 测试 findById() 缺失用户返回null
   □ 测试 delete() 成功删除用户
   覆盖率：100%

4. UserNotificationService 类
   □ 测试 sendWelcomeEmail() 正确发送
   □ 测试 sendPasswordReset() 正确发送
   覆盖率：100% (mock 邮件服务)

5. UserRegistrationService 类
   □ 测试注册流程完整性
   □ 测试邮件发送调用
   □ 测试验证失败时的处理
   覆盖率：100% (mock 所有依赖)
```

### 集成测试

```
□ 测试整个用户注册流程
□ 测试用户更新流程
□ 测试用户删除流程
□ 验证数据库状态正确
□ 验证邮件已发送
```

### 重构验证

```
□ 所有现有功能保持不变（行为兼容）
□ 性能没有退化
□ 内存占用没有增加
□ 代码覆盖率 ≥ 85%
```

---

## 第5步: 代码审查指南

### 审查检查清单

对每个新类进行审查时：

```
□ 职责清晰性
  - 能否用一句话清晰描述这个类的职责？
  - 类名是否精确反映职责？

□ 高内聚
  - 所有方法是否都操作同一组核心数据？
  - 有无操作无关数据的方法？

□ 低耦合
  - 类的公开依赖数 ≤ 3 个？
  - 是否有循环依赖？
  - 依赖的具体类是否过多？

□ 单一职责
  - 该类能否仅因一个理由而改变？
  - 是否还有其他改变理由？

□ 可测试性
  - 单元测试是否只需mock ≤ 2 个依赖？
  - 是否易于创建测试用例？

□ 代码质量
  - 方法数 ≤ 10 个
  - 方法长度 ≤ 30 行
  - 代码行数 ≤ 200 行
  - 圈复杂度 ≤ 5
```

### 对比标准

```
重构前后对比：

              重构前          重构后
类数          1              5
平均方法数    25             5
平均行数      800            100
测试mock数    8              2
难度等级      ⭐⭐⭐⭐⭐      ⭐
可复用性      低             高
```

---

## 常见陷阱预防

### 陷阱1: 过度拆分（微粒度职责）

```
❌ 过度拆分：
public class UsernameValidator { }
public class EmailValidator { }
public class PasswordValidator { }
public class PhoneValidator { }
// 四个只有一个方法的类，学习成本高

✅ 合理拆分：
public class UserValidator {
    public void validateUsername(String username) { }
    public void validateEmail(String email) { }
    public void validatePassword(String password) { }
}
// 相关的验证逻辑聚合在一个类中
```

**预防**：
```
□ 如果一个类只有 1-2 个方法，考虑合并
□ 相关度很高的职责可以放在一个类中
□ 每个类至少 3 个以上的方法
```

### 陷阱2: 不完整的拆分

```
❌ 不完整：
拆分了 UserValidator，但 UserManager 仍然存在，
代码中有些地方调用 UserManager，有些调用 UserValidator

✅ 完整：
删除 UserManager，所有地方都统一使用新的类结构
```

**预防**：
```
□ 逐步迁移所有调用点
□ 创建详细的迁移清单
□ 完成前不要删除旧类
□ 使用 @Deprecated 标记过度类
```

### 陷阱3: 忽视职责间的协作

```
❌ 拆分后调用混乱：
UserRegistrationService 中有大量的依赖注入和调用逻辑

✅ 使用 Facade 模式聚合：
UserRegistrationService 作为外观，协调各个单一职责的类
```

**预防**：
```
□ 识别协调类（Service）
□ 从依赖方向看是否形成清晰的分层
□ 避免各类之间的直接调用
```

### 陷阱4: 职责边界模糊

```
❌ 模糊的边界：
UserService 既做创建，又做验证，又做邮件
Validator 既验证格式，又验证业务规则

✅ 清晰的边界：
UserService: 协调业务流程
Validator: 仅验证数据格式和规则
EmailService: 仅发送邮件
```

**预防**：
```
□ 为每个类写一句话的职责说明
□ 定期审查职责是否漂移
□ 记录职责边界决策
```

### 陷阱5: 完全忽视性能影响

```
❌ 盲目拆分导致性能下降：
拆分后调用链变长，对象创建增多

✅ 性能和职责的平衡：
□ 使用享元模式复用对象
□ 使用对象池减少创建
□ 缓存频繁调用的结果
□ 定期性能测试
```

**预防**：
```
□ 拆分前进行基准测试
□ 拆分后进行性能对比
□ 识别性能关键路径，特殊处理
□ 必要时增加缓存层
```

---

## 重构检查表

完成拆分后，使用此检查表验证：

```
代码质量指标：
□ 新类数 = _____ （应该是 3-5 个）
□ 平均方法数 = _____ （应该 ≤ 6）
□ 平均行数 = _____ （应该 ≤ 150）
□ 最长方法 = _____ 行（应该 ≤ 30）
□ 代码覆盖率 = ____% （应该 ≥ 85%）

依赖关系：
□ 最大依赖数 = _____ （应该 ≤ 3）
□ 循环依赖 = _____ （应该 = 0）
□ 分层明确 = YES / NO

可维护性：
□ 所有新类都有 JavaDoc
□ 职责清晰可描述
□ 测试用例完整
□ 无 TODO 注释

性能：
□ 平均响应时间 vs 之前 = ___% （应该 < 110%）
□ 内存占用 vs 之前 = ___% （应该 < 105%）
```
