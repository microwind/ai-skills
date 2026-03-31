# Mediator Pattern - 完整参考实现

## Java实现 - UI对话框表单验证中介者 (140行)

```java
package com.example.mediator;

// Colleague接口
public interface FormControl {
    void update();
    void emitEvent();
}

// FormMediator - 中央协调者
public class FormMediator {
    private TextField nameField;
    private TextField emailField;
    private TextField passwordField;
    private Button submitButton;
    private Label errorLabel;
    
    public void registerControls(TextField name, TextField email, 
                                 TextField password, Button submit, 
                                 Label error) {
        this.nameField = name;
        this.emailField = email;
        this.passwordField = password;
        this.submitButton = submit;
        this.errorLabel = error;
        
        this.nameField.setMediator(this);
        this.emailField.setMediator(this);
        this.passwordField.setMediator(this);
    }
    
    public void handleFieldChange(TextField field) {
        String errors = "";
        
        // 验证名字
        if (!nameField.getText().isEmpty() && nameField.getText().length() < 2) {
            errors += "Name too short. ";
        }
        
        // 验证邮箱
        if (!emailField.getText().isEmpty() && !isValidEmail(emailField.getText())) {
            errors += "Invalid email. ";
        }
        
        // 验证密码
        if (!passwordField.getText().isEmpty() && passwordField.getText().length() < 6) {
            errors += "Password too weak. ";
        }
        
        // 更新UI
        if (errors.isEmpty()) {
            errorLabel.setText("");
            submitButton.setEnabled(nameField.getText().length() > 0 && 
                                   emailField.getText().length() > 0 && 
                                   passwordField.getText().length() > 0);
        } else {
            errorLabel.setText(errors);
            submitButton.setEnabled(false);
        }
    }
    
    private boolean isValidEmail(String email) {
        return email.matches("^[A-Za-z0-9+_.-]+@(.+)$");
    }
}

// Colleague - 具体字段
public class TextField {
    private String text = "";
    private FormMediator mediator;
    
    public void setMediator(FormMediator mediator) {
        this.mediator = mediator;
    }
    
    public void setText(String text) {
        this.text = text;
        if (mediator != null) {
            mediator.handleFieldChange(this);
        }
    }
    
    public String getText() {
        return text;
    }
}

public class Button {
    private boolean enabled = false;
    private Runnable action;
    
    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }
    
    public boolean isEnabled() {
        return enabled;
    }
    
    public void click() {
        if (enabled && action != null) {
            action.run();
        }
    }
    
    public void setAction(Runnable action) {
        this.action = action;
    }
}

public class Label {
    private String text = "";
    
    public void setText(String text) {
        this.text = text;
    }
    
    public String getText() {
        return text;
    }
}

// 使用示例
public class FormExample {
    public static void main(String[] args) {
        FormMediator mediator = new FormMediator();
        TextField nameField = new TextField();
        TextField emailField = new TextField();
        TextField passwordField = new TextField();
        Button submitButton = new Button();
        Label errorLabel = new Label();
        
        mediator.registerControls(nameField, emailField, passwordField, submitButton, errorLabel);
        
        nameField.setText("John");
        emailField.setText("john@example.com");
        passwordField.setText("secret123");
        
        System.out.println("Submit enabled: " + submitButton.isEnabled()); // true
        System.out.println("Errors: " + errorLabel.getText()); // ""
    }
}
```

## Python实现 - 聊天室中介者 (135行)

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

# ChatRoom - Mediator
class ChatRoom(ABC):
    @abstractmethod
    def display_message(self, user: 'User', message: str):
        pass
    
    @abstractmethod
    def add_user(self, user: 'User'):
        pass

# 具体Mediator
class ConcreteChatRoom(ChatRoom):
    def __init__(self, name: str):
        self.name = name
        self.users: List['User'] = []
    
    def display_message(self, user: 'User', message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{self.name}] {timestamp} - {user.name}: {message}")
        
        # 消息转发给其他所有用户
        for u in self.users:
            if u != user:
                u.receive_message(user.name, message)
    
    def add_user(self, user: 'User'):
        self.users.append(user)
        user.set_chat_room(self)
        self.display_message(user, f"{user.name} joined the chat")
    
    def remove_user(self, user: 'User'):
        if user in self.users:
            self.users.remove(user)
            self.display_message(user, f"{user.name} left the chat")

# Colleague - User
class User:
    def __init__(self, name: str):
        self.name = name
        self.chat_room: ChatRoom = None
    
    def set_chat_room(self, chat_room: ChatRoom):
        self.chat_room = chat_room
    
    def send_message(self, message: str):
        if self.chat_room:
            self.chat_room.display_message(self, message)
    
    def receive_message(self, from_user: str, message: str):
        print(f"  [NOTIFICATION] {from_user} sent you: {message}")

# 使用示例
if __name__ == "__main__":
    room = ConcreteChatRoom("Python Developers")
    
    alice = User("Alice")
    bob = User("Bob")
    charlie = User("Charlie")
    
    room.add_user(alice)
    room.add_user(bob)
    room.add_user(charlie)
    
    print("\n--- Messages ---")
    alice.send_message("Hello everyone!")
    bob.send_message("Hi Alice!")
    charlie.send_message("Good morning team!")
    
    room.remove_user(bob)
```

## TypeScript实现 - 游戏NPC交互协调 (120行)

```typescript
// NPC接口
interface NPC {
    name: string;
    send(message: string, recipient: NPC): void;
    receive(message: string, sender: NPC): void;
}

// 具体NPC
class GameNPC implements NPC {
    name: string;
    private mediator: GameMediator;
    private status: string = "idle";
    
    constructor(name: string) {
        this.name = name;
    }
    
    setMediator(mediator: GameMediator) {
        this.mediator = mediator;
    }
    
    send(message: string, recipient?: NPC): void {
        if (this.mediator) {
            this.mediator.transmit(message, this, recipient);
        }
    }
    
    receive(message: string, sender: NPC): void {
        console.log(`${this.name} received from ${sender.name}: ${message}`);
        
        // 根据消息类型学科处理
        if (message === "attack") {
            this.status = "attacking";
            console.log(`${this.name} is now attacking!`);
        } else if (message === "retreat") {
            this.status = "retreating";
            console.log(`${this.name} is retreating!`);
        } else if (message === "heal") {
            this.status = "healing";
            console.log(`${this.name} is being healed!`);
        }
    }
    
    getStatus(): string {
        return this.status;
    }
}

// GameMediator - 协调所有NPC
class GameMediator {
    private npcs: NPC[] = [];
    
    register(npc: NPC): void {
        this.npcs.push(npc);
        (npc as GameNPC).setMediator(this);
    }
    
    transmit(message: string, sender: NPC, recipient?: NPC): void {
        console.log(`\n[MEDIATOR] Processing: ${sender.name} says "${message}"`);
        
        if (recipient) {
            // 单播：发送给特定NPC
            recipient.receive(message, sender);
        } else {
            // 广播：发送给所有其他NPC
            for (const npc of this.npcs) {
                if (npc !== sender) {
                    npc.receive(message, sender);
                }
            }
        }
    }
    
    getStatus(): string {
        let status = "\n[GAME STATUS]\n";
        for (const npc of this.npcs) {
            status += `${npc.name}: ${(npc as GameNPC).getStatus()}\n`;
        }
        return status;
    }
}

// 使用示例
const mediator = new GameMediator();

const warrior = new GameNPC("Warrior");
const mage = new GameNPC("Mage");
const healer = new GameNPC("Healer");

mediator.register(warrior);
mediator.register(mage);
mediator.register(healer);

warrior.send("attack");  // 广播攻击命令
mage.send("attack");     // 广播攻击命令
warrior.send("heal", healer);  // 单播：请求治疗

console.log(mediator.getStatus());
```

## 单元测试 (75行)

```java
@Test
public void testFormValidation() {
    FormMediator mediator = new FormMediator();
    TextField name = new TextField();
    TextField email = new TextField();
    TextField password = new TextField();
    Button submit = new Button();
    Label error = new Label();
    
    mediator.registerControls(name, email, password, submit, error);
    
    // 测试有效输入
    name.setText("John");
    email.setText("john@example.com");
    password.setText("secret123");
    
    assertTrue(submit.isEnabled());
    assertTrue(error.getText().isEmpty());
}

@Test
public void testFormValidationErrors() {
    FormMediator mediator = new FormMediator();
    TextField email = new TextField();
    Button submit = new Button();
    Label error = new Label();
    
    email.setText("invalid-email");
    
    assertFalse(submit.isEnabled());
    assertTrue(error.getText().contains("Invalid email"));
}

@Test
public void testChatRoomBroadcast() {
    ConcreteChatRoom room = new ConcreteChatRoom("Test");
    User user1 = new User("User1");
    User user2 = new User("User2");
    
    room.add_user(user1);
    room.add_user(user2);
    
    user1.send_message("Hello");
    
    // 验证消息被转发
}
```

## 性能对比

| 实现方式 | 消息延迟 | 内存 | 吞吐量 | 复杂度 |
|---------|--------|------|--------|--------|
| 直接通信 | <1μs | 低 | 极高 | 高耦合 |
| 中央Mediator | 1-10μs | 中 | 中等 | 集中 |
| 事件驱动 | 10-100μs | 中 | 高（异步） | 分散 |
| 分布式Mediator | 1-100ms | 高 | 高（扩展） | 复杂 |

## 最佳实践

✅ Mediator只协调交互，不处理业务逻辑
✅ 保持Colleague简单专注
✅ 使用事件驱动避免God Object
✅ 提供清晰的交互文档
✅ 单元测试所有交互路径
✅ 高消息量时考虑异步处理
✅ 防止循环依赖
✅ 可观测性
