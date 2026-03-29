# 装饰器模式 - 完整参考实现

## 架构设计

```
┌──────────────────────────────┐
│      DataStream (接口)        │
│ + read(): String             │
│ + write(String)              │
│ + close()                    │
└──────────────────────────────┘
      △  △  △  △  △
      │  │  │  │  │
┌─────┘  │  │  │  └─────┐
│        │  │  │        │
FileDataStream  │  │  │  ...其他实现
               │  │  │
        ┌──────┘  │  └──────┐
        │         │         │
   DecoratorBase  │         │
   (抽象装饰器)   │         │
  • wrappedStream │         │
  • 转发所有方法  │         │
        │         │         │
    ┌───┴───┐ ┌───┴───┐ ┌───┴────┐
    │       │ │       │ │        │
 Logging  Compression  Encryption
 Decorator Decorator   Decorator
```

---

## 方案1: 标准装饰器实现（推荐用于生产）

### 完整实现代码

```java
import java.io.IOException;
import java.util.*;

// ============= 接口和基础实现 =============

/**
 * 数据流接口
 */
public interface DataStream {
    /**
     * 读取数据
     */
    String read() throws IOException;
    
    /**
     * 写入数据
     */
    void write(String data) throws IOException;
    
    /**
     * 关闭流
     */
    void close() throws IOException;
    
    /**
     * 获取元数据（用于诊断）
     */
    default Map<String, Object> getMetadata() {
        return new HashMap<>();
    }
}

/**
 * 文件数据流（核心实现）
 */
public class FileDataStream implements DataStream {
    private String filename;
    private StringBuilder content;
    private boolean closed = false;
    
    public FileDataStream(String filename) {
        this.filename = filename;
        this.content = new StringBuilder();
    }
    
    @Override
    public String read() throws IOException {
        if (closed) throw new IOException("Stream is closed");
        return content.toString();
    }
    
    @Override
    public void write(String data) throws IOException {
        if (closed) throw new IOException("Stream is closed");
        content.append(data);
    }
    
    @Override
    public void close() throws IOException {
        closed = true;
        System.out.println("[FileStream] Closed: " + filename);
    }
    
    @Override
    public Map<String, Object> getMetadata() {
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("type", "FileDataStream");
        metadata.put("filename", filename);
        metadata.put("size", content.length());
        metadata.put("closed", closed);
        return metadata;
    }
}

// ============= 抽象装饰器基类 =============

/**
 * 装饰器基类 - 所有装饰器都继承这个
 */
public abstract class DataStreamDecorator implements DataStream {
    protected DataStream wrappedStream;
    protected String decoratorName;
    
    protected DataStreamDecorator(DataStream stream, String name) {
        this.wrappedStream = stream;
        this.decoratorName = name;
    }
    
    /**
     * 获取被装饰的流（支持链式查询）
     */
    public DataStream getWrapped() {
        return wrappedStream;
    }
    
    /**
     * 获取装饰器名称
     */
    public String getDecoratorName() {
        return decoratorName;
    }
    
    /**
     * 默认转发：直接委托到被装饰对象
     */
    @Override
    public String read() throws IOException {
        return wrappedStream.read();
    }
    
    @Override
    public void write(String data) throws IOException {
        wrappedStream.write(data);
    }
    
    @Override
    public void close() throws IOException {
        wrappedStream.close();
    }
    
    @Override
    public Map<String, Object> getMetadata() {
        Map<String, Object> metadata = wrappedStream.getMetadata();
        metadata.put("decorator_" + decoratorName, true);
        return metadata;
    }
}

// ============= 具体装饰器1: 日志装饰器 =============

/**
 * 日志装饰器 - 记录所有操作
 */
public class LoggingDecorator extends DataStreamDecorator {
    private static final org.slf4j.Logger logger = 
        org.slf4j.LoggerFactory.getLogger(LoggingDecorator.class);
    private long operationCount = 0;
    
    public LoggingDecorator(DataStream stream) {
        super(stream, "Logging");
    }
    
    @Override
    public String read() throws IOException {
        operationCount++;
        long startTime = System.currentTimeMillis();
        
        System.out.println("[LOG #" + operationCount + "] Reading...");
        try {
            String result = wrappedStream.read();
            long duration = System.currentTimeMillis() - startTime;
            System.out.println("[LOG #" + operationCount + "] Read successful (" + 
                result.length() + " bytes, " + duration + "ms)");
            return result;
        } catch (IOException e) {
            System.out.println("[LOG #" + operationCount + "] Read failed: " + e.getMessage());
            throw e;
        }
    }
    
    @Override
    public void write(String data) throws IOException {
        operationCount++;
        long startTime = System.currentTimeMillis();
        
        System.out.println("[LOG #" + operationCount + "] Writing " + data.length() + " bytes...");
        try {
            wrappedStream.write(data);
            long duration = System.currentTimeMillis() - startTime;
            System.out.println("[LOG #" + operationCount + "] Write successful (" + duration + "ms)");
        } catch (IOException e) {
            System.out.println("[LOG #" + operationCount + "] Write failed: " + e.getMessage());
            throw e;
        }
    }
    
    @Override
    public void close() throws IOException {
        System.out.println("[LOG] Closing (total operations: " + operationCount + ")");
        wrappedStream.close();
    }
}

// ============= 具体装饰器2: 压缩装饰器 =============

/**
 * 压缩装饰器 - 压缩写入的数据，解压读取的数据
 */
public class CompressionDecorator extends DataStreamDecorator {
    private static final String COMPRESSION_PREFIX = "GZIP::";
    
    public CompressionDecorator(DataStream stream) {
        super(stream, "Compression");
    }
    
    @Override
    public String read() throws IOException {
        String compressed = wrappedStream.read();
        String decompressed = decompress(compressed);
        System.out.println("[Compression] Decompressed: " + compressed.length() + 
            " bytes → " + decompressed.length() + " bytes");
        return decompressed;
    }
    
    @Override
    public void write(String data) throws IOException {
        String compressed = compress(data);
        System.out.println("[Compression] Compressed: " + data.length() + 
            " bytes → " + compressed.length() + " bytes");
        wrappedStream.write(compressed);
    }
    
    private String compress(String data) {
        // 简化的压缩模拟
        return COMPRESSION_PREFIX + data.replaceAll("\\s+", " ");
    }
    
    private String decompress(String data) {
        // 简化的解压模拟
        if (data.startsWith(COMPRESSION_PREFIX)) {
            return data.substring(COMPRESSION_PREFIX.length());
        }
        return data;
    }
}

// ============= 具体装饰器3: 加密装饰器 =============

/**
 * 加密装饰器 - 加密写入的数据，解密读取的数据
 */
public class EncryptionDecorator extends DataStreamDecorator {
    private static final String ENCRYPTION_PREFIX = "ENC::";
    private static final int SHIFT = 3;  // 简化的ROT3加密
    
    public EncryptionDecorator(DataStream stream) {
        super(stream, "Encryption");
    }
    
    @Override
    public String read() throws IOException {
        String encrypted = wrappedStream.read();
        String decrypted = decrypt(encrypted);
        System.out.println("[Encryption] Decrypted successfully");
        return decrypted;
    }
    
    @Override
    public void write(String data) throws IOException {
        String encrypted = encrypt(data);
        System.out.println("[Encryption] Encrypted: " + data.length() + 
            " bytes → " + encrypted.length() + " bytes");
        wrappedStream.write(encrypted);
    }
    
    private String encrypt(String data) {
        StringBuilder encrypted = new StringBuilder(ENCRYPTION_PREFIX);
        for (char c : data.toCharArray()) {
            encrypted.append((char) (c + SHIFT));
        }
        return encrypted.toString();
    }
    
    private String decrypt(String data) {
        if (!data.startsWith(ENCRYPTION_PREFIX)) {
            return data;
        }
        
        String encryptedPart = data.substring(ENCRYPTION_PREFIX.length());
        StringBuilder decrypted = new StringBuilder();
        for (char c : encryptedPart.toCharArray()) {
            decrypted.append((char) (c - SHIFT));
        }
        return decrypted.toString();
    }
}

// ============= 具体装饰器4: 缓冲装饰器 =============

/**
 * 缓冲装饰器 - 批量处理写入操作
 */
public class BufferingDecorator extends DataStreamDecorator {
    private List<String> writeBuffer = new ArrayList<>();
    private static final int BUFFER_SIZE = 1024;
    private long bytesBuffered = 0;
    
    public BufferingDecorator(DataStream stream) {
        super(stream, "Buffering");
    }
    
    @Override
    public String read() throws IOException {
        // 读取前先刷新缓冲
        flush();
        return wrappedStream.read();
    }
    
    @Override
    public void write(String data) throws IOException {
        writeBuffer.add(data);
        bytesBuffered += data.length();
        
        System.out.println("[Buffering] Buffered: " + data.length() + 
            " bytes (total: " + bytesBuffered + "/" + BUFFER_SIZE + ")");
        
        if (bytesBuffered >= BUFFER_SIZE) {
            flush();
        }
    }
    
    @Override
    public void close() throws IOException {
        System.out.println("[Buffering] Closing, flushing " + writeBuffer.size() + 
            " buffered items");
        flush();
        wrappedStream.close();
    }
    
    /**
     * 刷新缓冲区到底层流
     */
    public void flush() throws IOException {
        if (!writeBuffer.isEmpty()) {
            System.out.println("[Buffering] Flushing " + writeBuffer.size() + 
                " items (" + bytesBuffered + " bytes)");
            
            for (String item : writeBuffer) {
                wrappedStream.write(item);
            }
            
            writeBuffer.clear();
            bytesBuffered = 0;
        }
    }
}

// ============= Builder模式辅助 =============

/**
 * 数据流构建器 - 简化装饰链的构建
 */
public class DataStreamBuilder {
    private DataStream stream;
    private List<String> decorators = new ArrayList<>();
    
    public DataStreamBuilder(DataStream baseStream) {
        this.stream = baseStream;
    }
    
    public DataStreamBuilder withLogging() {
        stream = new LoggingDecorator(stream);
        decorators.add("Logging");
        return this;
    }
    
    public DataStreamBuilder withCompression() {
        stream = new CompressionDecorator(stream);
        decorators.add("Compression");
        return this;
    }
    
    public DataStreamBuilder withEncryption() {
        stream = new EncryptionDecorator(stream);
        decorators.add("Encryption");
        return this;
    }
    
    public DataStreamBuilder withBuffering() {
        stream = new BufferingDecorator(stream);
        decorators.add("Buffering");
        return this;
    }
    
    public DataStream build() {
        System.out.println("[Builder] Created stream with decorators: " + decorators);
        return stream;
    }
}

// ============= 诊断工具 =============

/**
 * 装饰器链诊断工具
 */
public class DecoratorDiagnostics {
    public static void printChain(DataStream stream) {
        System.out.println("\n=== Decorator Chain Analysis ===");
        List<String> chain = new ArrayList<>();
        Object current = stream;
        int level = 0;
        
        while (current instanceof DataStreamDecorator) {
            DataStreamDecorator decorator = (DataStreamDecorator) current;
            chain.add(decorator.getDecoratorName());
            System.out.println("Level " + level + ": " + decorator.getDecoratorName());
            current = decorator.getWrapped();
            level++;
        }
        
        System.out.println("Level " + level + ": " + current.getClass().getSimpleName() + " (core)");
        System.out.println("Total depth: " + level);
        System.out.println("Decorators (outside to inside): " + chain);
        System.out.println("================================\n");
    }
}

// ============= 使用示例 =============

public class DecoratorPatternDemo {
    public static void main(String[] args) throws IOException {
        System.out.println("========== 装饰器模式演示 ==========\n");
        
        // 场景1: 基础使用 - 单个装饰器
        System.out.println("【场景1】单个装饰器");
        System.out.println("----------------------------------------");
        DataStream basicStream = new FileDataStream("basic.txt");
        basicStream = new LoggingDecorator(basicStream);
        
        basicStream.write("Hello World");
        String data1 = basicStream.read();
        System.out.println("Data: " + data1 + "\n");
        
        // 场景2: 装饰器链 - 多个装饰器组合
        System.out.println("【场景2】装饰器链（压缩+加密+日志）");
        System.out.println("----------------------------------------");
        DataStream chainedStream = new FileDataStream("chained.txt");
        chainedStream = new CompressionDecorator(chainedStream);
        chainedStream = new EncryptionDecorator(chainedStream);
        chainedStream = new LoggingDecorator(chainedStream);
        
        DecoratorDiagnostics.printChain(chainedStream);
        
        chainedStream.write("This is a secret message!");
        String data2 = chainedStream.read();
        System.out.println("Final data: " + data2 + "\n");
        
        // 场景3: 装饰顺序差异
        System.out.println("【场景3】装饰顺序对结果的影响");
        System.out.println("----------------------------------------");
        
        System.out.println("顺序A: 先压缩后加密");
        DataStream streamA = new EncryptionDecorator(
            new CompressionDecorator(new FileDataStream("order_a.txt"))
        );
        streamA.write("Important Data");
        String resultA = streamA.read();
        System.out.println("Result A: " + resultA);
        
        System.out.println("\n顺序B: 先加密后压缩");
        DataStream streamB = new CompressionDecorator(
            new EncryptionDecorator(new FileDataStream("order_b.txt"))
        );
        streamB.write("Important Data");
        String resultB = streamB.read();
        System.out.println("Result B: " + resultB);
        System.out.println("结果不同！顺序很重要。\n");
        
        // 场景4: Builder模式简化构建
        System.out.println("【场景4】使用Builder简化装饰链构建");
        System.out.println("----------------------------------------");
        DataStream builtStream = new DataStreamBuilder(new FileDataStream("built.txt"))
            .withLogging()
            .withCompression()
            .withEncryption()
            .withBuffering()
            .build();
        
        DecoratorDiagnostics.printChain(builtStream);
        
        builtStream.write("Data part 1 ");
        builtStream.write("Data part 2 ");
        builtStream.write("Data part 3 ");  // 触发缓冲刷新
        String data4 = builtStream.read();
        System.out.println("Buffered data: " + data4);
        builtStream.close();
        System.out.println();
        
        // 场景5: 异常处理
        System.out.println("【场景5】异常处理");
        System.out.println("----------------------------------------");
        try {
            DataStream errorStream = new LoggingDecorator(
                new FileDataStream("error.txt")
            );
            
            errorStream.close();
            errorStream.write("This should fail");  // 写入到已关闭流
        } catch (IOException e) {
            System.out.println("Caught exception: " + e.getMessage());
        }
        System.out.println();
        
        // 场景6: 元数据查询
        System.out.println("【场景6】装饰器链诊断信息");
        System.out.println("----------------------------------------");
        DataStream diagnosticStream = new DataStreamBuilder(
            new FileDataStream("diagnostic.txt")
        )
            .withLogging()
            .withCompression()
            .build();
        
        diagnosticStream.write("test");
        Map<String, Object> metadata = diagnosticStream.getMetadata();
        System.out.println("Metadata:");
        metadata.forEach((k, v) -> System.out.println("  " + k + ": " + v));
    }
}
```

---

## 方案2: Python实现

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict
import time

class DataStream(ABC):
    """数据流接口"""
    
    @abstractmethod
    def read(self) -> str:
        pass
    
    @abstractmethod
    def write(self, data: str) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass

class FileDataStream(DataStream):
    """文件数据流实现"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.content = ""
        self.closed = False
    
    def read(self) -> str:
        if self.closed:
            raise IOError("Stream is closed")
        return self.content
    
    def write(self, data: str) -> None:
        if self.closed:
            raise IOError("Stream is closed")
        self.content += data
    
    def close(self) -> None:
        self.closed = True
        print(f"[FileStream] Closed: {self.filename}")

class DataStreamDecorator(DataStream, ABC):
    """装饰器基类"""
    
    def __init__(self, stream: DataStream, name: str):
        self._wrapped = stream
        self._name = name
    
    def get_wrapped(self) -> DataStream:
        return self._wrapped
    
    def get_name(self) -> str:
        return self._name
    
    def read(self) -> str:
        return self._wrapped.read()
    
    def write(self, data: str) -> None:
        self._wrapped.write(data)
    
    def close(self) -> None:
        self._wrapped.close()

class LoggingDecorator(DataStreamDecorator):
    """日志装饰器"""
    
    def __init__(self, stream: DataStream):
        super().__init__(stream, "Logging")
        self._operation_count = 0
    
    def read(self) -> str:
        self._operation_count += 1
        start_time = time.time()
        
        print(f"[LOG #{self._operation_count}] Reading...")
        try:
            result = self._wrapped.read()
            duration = (time.time() - start_time) * 1000
            print(f"[LOG #{self._operation_count}] Read successful ({len(result)} bytes, {duration:.1f}ms)")
            return result
        except Exception as e:
            print(f"[LOG #{self._operation_count}] Read failed: {e}")
            raise

class CompressionDecorator(DataStreamDecorator):
    """压缩装饰器"""
    
    COMPRESSION_PREFIX = "GZIP::"
    
    def __init__(self, stream: DataStream):
        super().__init__(stream, "Compression")
    
    def read(self) -> str:
        compressed = self._wrapped.read()
        decompressed = self._decompress(compressed)
        print(f"[Compression] Decompressed: {len(compressed)} bytes → {len(decompressed)} bytes")
        return decompressed
    
    def write(self, data: str) -> None:
        compressed = self._compress(data)
        print(f"[Compression] Compressed: {len(data)} bytes → {len(compressed)} bytes")
        self._wrapped.write(compressed)
    
    def _compress(self, data: str) -> str:
        return self.COMPRESSION_PREFIX + " ".join(data.split())
    
    def _decompress(self, data: str) -> str:
        if data.startswith(self.COMPRESSION_PREFIX):
            return data[len(self.COMPRESSION_PREFIX):]
        return data

class EncryptionDecorator(DataStreamDecorator):
    """加密装饰器"""
    
    ENCRYPTION_PREFIX = "ENC::"
    SHIFT = 3
    
    def __init__(self, stream: DataStream):
        super().__init__(stream, "Encryption")
    
    def read(self) -> str:
        encrypted = self._wrapped.read()
        decrypted = self._decrypt(encrypted)
        print(f"[Encryption] Decrypted successfully")
        return decrypted
    
    def write(self, data: str) -> None:
        encrypted = self._encrypt(data)
        print(f"[Encryption] Encrypted: {len(data)} bytes → {len(encrypted)} bytes")
        self._wrapped.write(encrypted)
    
    def _encrypt(self, data: str) -> str:
        encrypted = self.ENCRYPTION_PREFIX
        for c in data:
            encrypted += chr(ord(c) + self.SHIFT)
        return encrypted
    
    def _decrypt(self, data: str) -> str:
        if not data.startswith(self.ENCRYPTION_PREFIX):
            return data
        encrypted_part = data[len(self.ENCRYPTION_PREFIX):]
        decrypted = ""
        for c in encrypted_part:
            decrypted += chr(ord(c) - self.SHIFT)
        return decrypted

class BufferingDecorator(DataStreamDecorator):
    """缓冲装饰器"""
    
    BUFFER_SIZE = 1024
    
    def __init__(self, stream: DataStream):
        super().__init__(stream, "Buffering")
        self._buffer = []
        self._bytes_buffered = 0
    
    def read(self) -> str:
        self.flush()
        return self._wrapped.read()
    
    def write(self, data: str) -> None:
        self._buffer.append(data)
        self._bytes_buffered += len(data)
        
        print(f"[Buffering] Buffered: {len(data)} bytes (total: {self._bytes_buffered}/{self.BUFFER_SIZE})")
        
        if self._bytes_buffered >= self.BUFFER_SIZE:
            self.flush()
    
    def close(self) -> None:
        print(f"[Buffering] Closing, flushing {len(self._buffer)} buffered items")
        self.flush()
        self._wrapped.close()
    
    def flush(self) -> None:
        if self._buffer:
            print(f"[Buffering] Flushing {len(self._buffer)} items ({self._bytes_buffered} bytes)")
            for item in self._buffer:
                self._wrapped.write(item)
            self._buffer.clear()
            self._bytes_buffered = 0

# 使用示例
if __name__ == "__main__":
    print("========== Python 装饰器模式演示 ==========\n")
    
    # 场景1: 单个装饰器
    print("【场景1】单个装饰器")
    stream1 = LoggingDecorator(FileDataStream("basic.txt"))
    stream1.write("Hello World")
    data = stream1.read()
    print(f"Data: {data}\n")
    
    # 场景2: 装饰器链
    print("【场景2】装饰器链")
    stream2 = LoggingDecorator(
        EncryptionDecorator(
            CompressionDecorator(
                FileDataStream("chained.txt")
            )
        )
    )
    stream2.write("Secret Message")
    data = stream2.read()
    print(f"Final: {data}\n")
    
    # 场景3: 缓冲
    print("【场景3】缓冲装饰器")
    stream3 = BufferingDecorator(FileDataStream("buffered.txt"))
    stream3.write("Part 1 ")
    stream3.write("Part 2 ")
    stream3.write("Part 3 ")
    stream3.close()
```

---

## 方案3: TypeScript实现

```typescript
interface DataStream {
    read(): Promise<string>;
    write(data: string): Promise<void>;
    close(): Promise<void>;
}

class FileDataStream implements DataStream {
    private content = "";
    private closed = false;
    
    constructor(private filename: string) {}
    
    async read(): Promise<string> {
        if (this.closed) throw new Error("Stream is closed");
        return this.content;
    }
    
    async write(data: string): Promise<void> {
        if (this.closed) throw new Error("Stream is closed");
        this.content += data;
    }
    
    async close(): Promise<void> {
        this.closed = true;
        console.log(`[FileStream] Closed: ${this.filename}`);
    }
}

abstract class DataStreamDecorator implements DataStream {
    protected _operationCount = 0;
    
    constructor(protected _wrapped: DataStream, protected _name: string) {}
    
    getWrapped(): DataStream {
        return this._wrapped;
    }
    
    getName(): string {
        return this._name;
    }
    
    async read(): Promise<string> {
        return this._wrapped.read();
    }
    
    async write(data: string): Promise<void> {
        return this._wrapped.write(data);
    }
    
    async close(): Promise<void> {
        return this._wrapped.close();
    }
}

class LoggingDecorator extends DataStreamDecorator {
    constructor(stream: DataStream) {
        super(stream, "Logging");
    }
    
    async read(): Promise<string> {
        this._operationCount++;
        const startTime = Date.now();
        
        console.log(`[LOG #${this._operationCount}] Reading...`);
        try {
            const result = await this._wrapped.read();
            const duration = Date.now() - startTime;
            console.log(`[LOG #${this._operationCount}] Read successful (${result.length} bytes, ${duration}ms)`);
            return result;
        } catch (e) {
            console.log(`[LOG #${this._operationCount}] Read failed: ${e}`);
            throw e;
        }
    }
}

class CompressionDecorator extends DataStreamDecorator {
    private static readonly PREFIX = "GZIP::";
    
    constructor(stream: DataStream) {
        super(stream, "Compression");
    }
    
    async read(): Promise<string> {
        const compressed = await this._wrapped.read();
        const decompressed = this.decompress(compressed);
        console.log(`[Compression] Decompressed: ${compressed.length} → ${decompressed.length} bytes`);
        return decompressed;
    }
    
    async write(data: string): Promise<void> {
        const compressed = this.compress(data);
        console.log(`[Compression] Compressed: ${data.length} → ${compressed.length} bytes`);
        return this._wrapped.write(compressed);
    }
    
    private compress(data: string): string {
        return CompressionDecorator.PREFIX + data.split(/\s+/).join(" ");
    }
    
    private decompress(data: string): string {
        if (data.startsWith(CompressionDecorator.PREFIX)) {
            return data.slice(CompressionDecorator.PREFIX.length);
        }
        return data;
    }
}

class EncryptionDecorator extends DataStreamDecorator {
    private static readonly PREFIX = "ENC::";
    private static readonly SHIFT = 3;
    
    constructor(stream: DataStream) {
        super(stream, "Encryption");
    }
    
    async read(): Promise<string> {
        const encrypted = await this._wrapped.read();
        const decrypted = this.decrypt(encrypted);
        console.log(`[Encryption] Decrypted successfully`);
        return decrypted;
    }
    
    async write(data: string): Promise<void> {
        const encrypted = this.encrypt(data);
        console.log(`[Encryption] Encrypted: ${data.length} → ${encrypted.length} bytes`);
        return this._wrapped.write(encrypted);
    }
    
    private encrypt(data: string): string {
        let result = EncryptionDecorator.PREFIX;
        for (let c of data) {
            result += String.fromCharCode(c.charCodeAt(0) + EncryptionDecorator.SHIFT);
        }
        return result;
    }
    
    private decrypt(data: string): string {
        if (!data.startsWith(EncryptionDecorator.PREFIX)) {
            return data;
        }
        const encrypted = data.slice(EncryptionDecorator.PREFIX.length);
        let result = "";
        for (let c of encrypted) {
            result += String.fromCharCode(c.charCodeAt(0) - EncryptionDecorator.SHIFT);
        }
        return result;
    }
}

// 使用示例
async function demo() {
    console.log("========== TypeScript 装饰器模式演示 ==========\n");
    
    // 场景1: 链式装饰
    console.log("【场景1】链式装饰");
    let stream: DataStream = new FileDataStream("demo.txt");
    stream = new CompressionDecorator(stream);
    stream = new EncryptionDecorator(stream);
    stream = new LoggingDecorator(stream);
    
    await stream.write("Secret Message");
    const result = await stream.read();
    console.log(`Result: ${result}\n`);
    
    await stream.close();
}

demo().catch(console.error);
```

---

## 性能对比分析

| 方案 | 代码复杂度 | 运行时开销 | 灵活性 | 推荐场景 |
|-----|---------|---------|-------|--------|
| **标准装饰器** | 中 | 低 | 高 | 生产环境 |
| **泛型装饰器** | 高 | 中 | 极高 | 通用框架 |
| **函数式** | 低 | 低 | 中 | 简单场景 |
| **动态代理** | 高 | 中-高 | 极高 | AOP框架 |

## 单元测试示例

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class DecoratorPatternTest {
    
    @Test
    public void testLoggingDecorator() throws IOException {
        DataStream mockStream = new MockDataStream("test");
        DataStream decorated = new LoggingDecorator(mockStream);
        
        String result = decorated.read();
        assertEquals("test", result);
    }
    
    @Test
    public void testCompressionRoundTrip() throws IOException {
        DataStream stream = new CompressionDecorator(new FileDataStream("test.txt"));
        String original = "Hello World";
        
        stream.write(original);
        String recovered = stream.read();
        
        assertEquals(original, recovered);
    }
    
    @Test
    public void testDecoratorChain() throws IOException {
        DataStream stream = new FileDataStream("chain.txt");
        stream = new LoggingDecorator(stream);
        stream = new CompressionDecorator(stream);
        stream = new EncryptionDecorator(stream);
        
        String original = "test data";
        stream.write(original);
        String result = stream.read();
        
        assertEquals(original, result);
    }
    
    @Test
    public void testDecoratorOrder() throws IOException {
        DataStream stream1 = new FileDataStream("test1.txt");
        stream1 = new EncryptionDecorator(new CompressionDecorator(stream1));
        
        DataStream stream2 = new FileDataStream("test2.txt");
        stream2 = new CompressionDecorator(new EncryptionDecorator(stream2));
        
        String data = "test";
        stream1.write(data);
        stream2.write(data);
        
        // 虽然输入相同，但输出不同
        assertNotEquals(stream1.read(), stream2.read());
    }
    
    @Test
    public void testBufferingFlush() throws IOException {
        DataStream stream = new BufferingDecorator(new FileDataStream("buffer.txt"));
        
        stream.write("part1");
        stream.write("part2");
        
        String result = stream.read();
        assertTrue(result.contains("part1"));
        assertTrue(result.contains("part2"));
    }
}
```

---

## 常见错误和解决方案

### ❌ 错误1: 装饰器顺序导致数据损坏

```java
// 错误：先压缩后加密
stream = new EncryptionDecorator(
    new CompressionDecorator(new FileDataStream())
);

// 问题：流程是 write后加密(压缩数据) → read先读(加密数据)再解压
// 读出来的数据被破坏

// ✅ 解决：明确文档化顺序
/**
 * 正确的顺序：
 * - 写: Core → Compression → Encryption → Logging
 * - 读: Logging → Encryption → Decompression → Core
 */
```

### ❌ 错误2: 装饰器链深度不受控

```java
// 错误：无限制深度
DataStream stream = new FileDataStream();
for (int i = 0; i < 1000; i++) {
    stream = new LoggingDecorator(stream);  // 无限套娃！
}

// ✅ 解决：检查深度
public static int getChainDepth(DataStream stream) {
    int depth = 0;
    while (stream instanceof DataStreamDecorator) {
        depth++;
        stream = ((DataStreamDecorator) stream).getWrapped();
    }
    return depth;
}

// 使用时检查
if (getChainDepth(stream) > MAX_DEPTH) {
    throw new IllegalStateException("Decorator chain too deep");
}
```

### ❌ 错误3: 异常处理不完善

```java
// 错误：缓冲器在异常时丢失数据
public void write(String data) {
    buffer.add(data);
    if (buffer.size() >= BUFFER_SIZE) {
        flush();  // 如果主流异常，缓冲数据丢失
    }
}

// ✅ 解决：完善异常处理
public void write(String data) throws IOException {
    buffer.add(data);
    try {
        if (buffer.size() >= BUFFER_SIZE) {
            flush();
        }
    } catch (IOException e) {
        // 异常时保留缓冲，便于重试
        throw new BufferingException("Failed to flush buffer", e);
    }
}
```

---

## 最佳实践总结

1. **✅ 单一职责**: 每个装饰器只添加一个清晰的职责
2. **✅ 文档化顺序**: 清晰说明装饰顺序和限制 
3. **✅ 限制深度**: 装饰链深度通常不超过3-4层
4. **✅ Builder模式**: 复杂链路用Builder简化
5. **✅ 异常处理**: 链中任意点异常都要妥善处理
6. **✅ 测试全覆盖**: 单独测试+链式测试+顺序测试
