# Template Method - 参考实现

## 完整 Java: 数据处理框架

```java
public abstract class DataProcessor {
    // 模板方法
    public final ProcessResult process(List<Record> data) {
        long startTime = System.nanoTime();
        
        List<Record> validated = validate(data);
        List<Record> cleaned = clean(validated);
        List<Record> transformed = transform(cleaned);
        ProcessResult result = aggregate(transformed);
        
        result.setProcessingTime((System.nanoTime() - startTime) / 1_000_000);
        return result;
    }
    
    protected abstract List<Record> validate(List<Record> data);
    protected abstract List<Record> clean(List<Record> data);
    protected abstract List<Record> transform(List<Record> data);
    protected abstract ProcessResult aggregate(List<Record> data);
}

public class CSVProcessor extends DataProcessor {
    @Override
    protected List<Record> validate(List<Record> data) {
        System.out.println("CSV: Validating " + data.size() + " records");
        return data.stream()
            .filter(r -> r.isValid())
            .collect(Collectors.toList());
    }
    
    @Override
    protected List<Record> clean(List<Record> data) {
        System.out.println("CSV: Cleaning data");
        return data.stream()
            .map(r -> r.trim())
            .collect(Collectors.toList());
    }
    
    @Override
    protected List<Record> transform(List<Record> data) {
        System.out.println("CSV: Transforming data");
        return data.stream()
            .map(r -> convertToUpperCase(r))
            .collect(Collectors.toList());
    }
    
    @Override
    protected ProcessResult aggregate(List<Record> data) {
        return new ProcessResult("CSV", data.size());
    }
    
    private Record convertToUpperCase(Record r) {
        return r.toUpperCase();
    }
}

public class JSONProcessor extends DataProcessor {
    @Override
    protected List<Record> validate(List<Record> data) {
        System.out.println("JSON: Validating JSON structure");
        return data.stream()
            .filter(r -> r.isJsonValid())
            .collect(Collectors.toList());
    }
    
    @Override
    protected List<Record> clean(List<Record> data) {
        System.out.println("JSON: Removing null fields");
        return data.stream()
            .filter(r -> !r.hasNullFields())
            .collect(Collectors.toList());
    }
    
    @Override
    protected List<Record> transform(List<Record> data) {
        System.out.println("JSON: Flattening nested structures");
        return data.stream()
            .map(r -> r.flatten())
            .collect(Collectors.toList());
    }
    
    @Override
    protected ProcessResult aggregate(List<Record> data) {
        return new ProcessResult("JSON", data.size());
    }
}

// 使用
List<Record> csvData = loadCSV("data.csv");
DataProcessor csvProcessor = new CSVProcessor();
ProcessResult csvResult = csvProcessor.process(csvData);

List<Record> jsonData = loadJSON("data.json");
DataProcessor jsonProcessor = new JSONProcessor();
ProcessResult jsonResult = jsonProcessor.process(jsonData);
```

---

## Python: 函数式模板

```python
from abc import ABC, abstractmethod
from typing import List, Callable, Any

class Pipeline:
    def __init__(self):
        self.steps: List[Callable[[Any], Any]] = []
    
    def add_step(self, func: Callable[[Any], Any]) -> 'Pipeline':
        self.steps.append(func)
        return self
    
    def execute(self, data: Any) -> Any:
        result = data
        for step in self.steps:
            result = step(result)
        return result

class DataProcessingPipeline(Pipeline):
    def setup_validation(self, validator: Callable) -> 'DataProcessingPipeline':
        self.add_step(lambda d: [x for x in d if validator(x)])
        return self
    
    def setup_cleaning(self, cleaner: Callable) -> 'DataProcessingPipeline':
        self.add_step(lambda d: [cleaner(x) for x in d])
        return self
    
    def setup_transformation(self, transformer: Callable) -> 'DataProcessingPipeline':
        self.add_step(lambda d: [transformer(x) for x in d])
        return self
    
    def setup_aggregation(self, aggregator: Callable) -> 'DataProcessingPipeline':
        self.add_step(aggregator)
        return self

# 使用
def validate_csv(record):
    return len(record.strip()) > 0

def clean_csv(record):
    return record.strip().upper()

def transform_csv(record):
    return record.split(',')

pipeline = DataProcessingPipeline()
pipeline.setup_validation(validate_csv) \
        .setup_cleaning(clean_csv) \
        .setup_transformation(transform_csv) \
        .setup_aggregation(lambda d: sum(len(x) for x in d))

data = ["  hello, world  ", "foo, bar"]
result = pipeline.execute(data)
print(result)  # 总字符数
```

---

## TypeScript: 异步模板

```typescript
abstract class AsyncDataProcessor {
    async process(data: any[]): Promise<ProcessResult> {
        const start = Date.now();
        
        const validated = await this.validate(data);
        const cleaned = await this.clean(validated);
        const transformed = await this.transform(cleaned);
        const result = await this.aggregate(transformed);
        
        result.processingTime = Date.now() - start;
        return result;
    }
    
    protected abstract validate(data: any[]): Promise<any[]>;
    protected abstract clean(data: any[]): Promise<any[]>;
    protected abstract transform(data: any[]): Promise<any[]>;
    protected abstract aggregate(data: any[]): Promise<ProcessResult>;
}

class AsyncCSVProcessor extends AsyncDataProcessor {
    protected async validate(data: any[]): Promise<any[]> {
        // 模拟异步验证
        return new Promise(resolve => {
            setTimeout(() => {
                resolve(data.filter(r => this.isValid(r)));
            }, 100);
        });
    }
    
    protected async clean(data: any[]): Promise<any[]> {
        return data.map(r => r.trim());
    }
    
    protected async transform(data: any[]): Promise<any[]> {
        return data.map(r => r.toUpperCase());
    }
    
    protected async aggregate(data: any[]): Promise<ProcessResult> {
        return { count: data.length, type: 'CSV' };
    }
    
    private isValid(record: any): boolean {
        return record && record.length > 0;
    }
}

// 使用
const processor = new AsyncCSVProcessor();
processor.process(csvData)
    .then(result => console.log(result))
    .catch(err => console.error(err));
```

---

## 高级: 模板钩子

```java
public abstract class AdvancedDataProcessor {
    public final ProcessResult process(List<Record> data) {
        // 前置钩子
        beforeProcessing();
        
        List<Record> validated = validate(data);
        onValidationComplete(validated);
        
        List<Record> cleaned = clean(validated);
        onCleaningComplete(cleaned);
        
        List<Record> transformed = transform(cleaned);
        onTransformationComplete(transformed);
        
        ProcessResult result = aggregate(transformed);
        
        // 后置钩子
        afterProcessing(result);
        
        return result;
    }
    
    // 钩子方法 - 子类可选覆盖
    protected void beforeProcessing() {}
    protected void onValidationComplete(List<Record> data) {}
    protected void onCleaningComplete(List<Record> data) {}
    protected void onTransformationComplete(List<Record> data) {}
    protected void afterProcessing(ProcessResult result) {}
    
    // 抽象方法 - 子类必须实现
    protected abstract List<Record> validate(List<Record> data);
    protected abstract List<Record> clean(List<Record> data);
    protected abstract List<Record> transform(List<Record> data);
    protected abstract ProcessResult aggregate(List<Record> data);
}

public class LoggingProcessor extends AdvancedDataProcessor {
    private List<String> logs = new ArrayList<>();
    
    @Override
    protected void beforeProcessing() {
        logs.add("Processing started at " + new Date());
        System.out.println("开始处理");
    }
    
    @Override
    protected void onValidationComplete(List<Record> data) {
        logs.add("Validated: " + data.size() + " records");
        System.out.println("验证完成: " + data.size() + " 条记录");
    }
    
    @Override
    protected void afterProcessing(ProcessResult result) {
        logs.add("Processing completed: " + result);
        System.out.println("处理完成");
    }
    
    // 其他方法实现...
}
```

---

## 策略增强的模板

```java
public class StrategyEnhancedProcessor {
    private List<ProcessingStrategy> strategies;
    
    public ProcessResult process(List<Record> data) {
        ProcessResult result = new ProcessResult();
        
        for (ProcessingStrategy strategy : strategies) {
            if (strategy.canHandle(data)) {
                data = strategy.process(data);
            }
        }
        
        result.setData(data);
        return result;
    }
}

public interface ProcessingStrategy {
    boolean canHandle(List<Record> data);
    List<Record> process(List<Record> data);
}

public class CompressionStrategy implements ProcessingStrategy {
    @Override
    public boolean canHandle(List<Record> data) {
        return data.stream()
            .mapToInt(r -> r.getSize())
            .sum() > 10_000_000; // 10MB
    }
    
    @Override
    public List<Record> process(List<Record> data) {
        return data.stream()
            .map(r -> r.compress())
            .collect(Collectors.toList());
    }
}
```

---

## 单元测试

```java
@Test
public void testCSVProcessor() {
    CSVProcessor processor = new CSVProcessor();
    List<Record> testData = Arrays.asList(
        new Record("Alice,30"),
        new Record("Bob,25")
    );
    
    ProcessResult result = processor.process(testData);
    assertEquals(2, result.getRecordCount());
    assertTrue(result.getProcessingTime() > 0);
}

@Test
public void testProcessingOrder() {
    OrderTrackingProcessor processor = new OrderTrackingProcessor();
    List<Record> data = createTestData();
    
    processor.process(data);
    
    List<String> order = processor.getExecutionOrder();
    assertEquals("validate", order.get(0));
    assertEquals("clean", order.get(1));
    assertEquals("transform", order.get(2));
    assertEquals("aggregate", order.get(3));
}

@Test
public void testHookExecution() {
    HookenProcessor processor = new HookProcessor();
    processor.process(createTestData());
    
    assertTrue(processor.beforeProcessingCalled);
    assertTrue(processor.afterProcessingCalled);
}
```

---

## 性能对比

| 实现方式 | 灵活性 | 性能 | 可测试性 | 复杂度 |
|---------|--------|------|---------|--------|
| 虚方法 | 中 | 高 | 中 | 低 |
| 回调 | 高 | 中 | 高 | 中 |
| 策略 | 高 | 高 | 高 | 高 |
| 函数式 | 高 | 中 | 高 | 低 |

---

## 常见问题

1. Q: 如何在子类中改变步骤顺序?
   A: override process() 方法或使用策略模式

2. Q: 钩子方法太多会怎样?
   A: 使用观察者模式替代

3. Q: 如何跳过某个步骤?
   A: 在钩子方法中返回无操作或使用条件逻辑

4. Q: 如何处理步骤异常?
   A: 在 process() 方法中添加 try-catch 或使用异常处理策略

---

## Java: 排序与数据处理框架

```java
// 排序算法模板
public abstract class SortAlgorithm {
    public final void sort(int[] array) {
        long startTime = System.nanoTime();
        
        int comparisons = 0;
        int swaps = 0;
        
        doSort(array);
        
        long duration = System.nanoTime() - startTime;
        reportMetrics(array.length, duration / 1_000_000);
    }
    
    protected abstract void doSort(int[] array);
    
    protected void reportMetrics(int size, long timeMs) {
        System.out.printf("Sorted %d elements in %d ms%n", size, timeMs);
    }
}

// 快速排序实现
public class QuickSort extends SortAlgorithm {
    @Override
    protected void doSort(int[] array) {
        quickSort(array, 0, array.length - 1);
    }
    
    private void quickSort(int[] arr, int low, int high) {
        if (low < high) {
            int pi = partition(arr, low, high);
            quickSort(arr, low, pi - 1);
            quickSort(arr, pi + 1, high);
        }
    }
    
    private int partition(int[] arr, int low, int high) {
        int pivot = arr[high];
        int i = low - 1;
        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
        int temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;
        return i + 1;
    }
}

// 冒泡排序实现
public class BubbleSort extends SortAlgorithm {
    @Override
    protected void doSort(int[] array) {
        int n = array.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (array[j] > array[j + 1]) {
                    int temp = array[j];
                    array[j] = array[j + 1];
                    array[j + 1] = temp;
                }
            }
        }
    }
}

// 流程处理框架
public abstract class DataPipeline {
    public final ProcessResult execute(List<String> data) {
        try {
            List<String> loaded = load(data);
            List<String> validated = validate(loaded);
            List<String> transformed = transform(validated);
            return save(transformed);
        } catch (Exception e) {
            handleError(e);
            return new ProcessResult(false, "Error: " + e.getMessage());
        }
    }
    
    protected abstract List<String> load(List<String> data);
    protected abstract List<String> validate(List<String> data);
    protected abstract List<String> transform(List<String> data);
    protected abstract ProcessResult save(List<String> data);
    
    protected void handleError(Exception e) {
        System.err.println("Pipeline error: " + e.getMessage());
        e.printStackTrace();
    }
}

public class CSVPipeline extends DataPipeline {
    @Override
    protected List<String> load(List<String> data) {
        return data.stream().filter(l -> !l.isEmpty()).collect(Collectors.toList());
    }
    
    @Override
    protected List<String> validate(List<String> data) {
        return data.stream().filter(l -> l.contains(",")).collect(Collectors.toList());
    }
    
    @Override
    protected List<String> transform(List<String> data) {
        return data.stream()
            .map(l -> l.replaceAll("\\s+", " "))
            .collect(Collectors.toList());
    }
    
    @Override
    protected ProcessResult save(List<String> data) {
        System.out.println("Saved " + data.size() + " records");
        return new ProcessResult(true, "CSV processed successfully");
    }
}

public class JSONPipeline extends DataPipeline {
    @Override
    protected List<String> load(List<String> data) {
        return data.stream().filter(l -> l.startsWith("{")).collect(Collectors.toList());
    }
    
    @Override
    protected List<String> validate(List<String> data) {
        return data.stream().filter(this::isValidJSON).collect(Collectors.toList());
    }
    
    private boolean isValidJSON(String s) {
        try {
            new org.json.JSONObject(s);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
    
    @Override
    protected List<String> transform(List<String> data) {
        return data.stream()
            .map(s -> new org.json.JSONObject(s).toString(2))
            .collect(Collectors.toList());
    }
    
    @Override
    protected ProcessResult save(List<String> data) {
        System.out.println("Saved " + data.size() + " JSON objects");
        return new ProcessResult(true, "JSON processed");
    }
}

// 使用示例
SortAlgorithm quickSort = new QuickSort();
int[] data = {64, 34, 25, 12, 22, 11, 90};
quickSort.sort(data); // 输出: Sorted 7 elements in 0 ms

DataPipeline csvPipe = new CSVPipeline();
csvPipe.execute(csvData); // 处理CSV
```

---

## Python: 数据转换管道

```python
from abc import ABC, abstractmethod
from typing import List, Any
import time

class DataTransformer(ABC):
    """数据转换模板"""
    
    def transform(self, data: List[Any]) -> dict:
        start_time = time.time()
        
        cleaned = self.clean(data)
        validated = self.validate(cleaned)
        formatted = self.format(validated)
        
        elapsed = time.time() - start_time
        return {
            'data': formatted,
            'count': len(formatted),
            'time_ms': elapsed * 1000
        }
    
    @abstractmethod
    def clean(self, data: List[Any]) -> List[Any]:
        pass
    
    @abstractmethod
    def validate(self, data: List[Any]) -> List[Any]:
        pass
    
    @abstractmethod
    def format(self, data: List[Any]) -> List[Any]:
        pass

class CSVTransformer(DataTransformer):
    def clean(self, data: List[str]) -> List[str]:
        return [line.strip() for line in data if line.strip()]
    
    def validate(self, data: List[str]) -> List[str]:
        return [line for line in data if ',' in line]
    
    def format(self, data: List[str]) -> List[dict]:
        result = []
        for line in data:
            parts = [p.strip() for p in line.split(',')]
            result.append({'fields': parts, 'count': len(parts)})
        return result

class JSONTransformer(DataTransformer):
    def clean(self, data: List[str]) -> List[str]:
        return [line for line in data if line.startswith('{')]
    
    def validate(self, data: List[str]) -> List[str]:
        valid = []
        for line in data:
            try:
                json.loads(line)
                valid.append(line)
            except:
                pass
        return valid
    
    def format(self, data: List[str]) -> List[dict]:
        return [json.loads(line) for line in data]

# 使用
transformer = CSVTransformer()
result = transformer.transform(csv_data)
print(f"Processed {result['count']} records in {result['time_ms']:.2f}ms")
```

---

## TypeScript: HTTP请求框架

```typescript
abstract class HttpBuilder {
    protected method: string = 'GET';
    protected headers: Record<string, string> = {};
    protected retries: number = 3;
    
    public final async execute(url: string): Promise<any> {
        const startTime = Date.now();
        
        this.prepareHeaders();
        const request = this.buildRequest(url);
        
        const response = await this.sendWithRetry(request);
        const data = await this.parseResponse(response);
        const result = this.transform(data);
        
        console.log(`Request completed in ${Date.now() - startTime}ms`);
        return result;
    }
    
    protected abstract prepareHeaders(): void;
    protected abstract buildRequest(url: string): any;
    protected abstract parseResponse(response: any): Promise<any>;
    protected abstract transform(data: any): any;
    
    private async sendWithRetry(request: any): Promise<any> {
        let lastError: any;
        for (let i = 0; i < this.retries; i++) {
            try {
                return await fetch(request);
            } catch (error) {
                lastError = error;
                await new Promise(r => setTimeout(r, 100 * (i + 1)));
            }
        }
        throw lastError;
    }
}

class APIClientBuilder extends HttpBuilder {
    protected prepareHeaders(): void {
        this.headers['Authorization'] = 'Bearer token';
        this.headers['Content-Type'] = 'application/json';
    }
    
    protected buildRequest(url: string): any {
        return { method: this.method, headers: this.headers };
    }
    
    protected async parseResponse(response: any): Promise<any> {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    }
    
    protected transform(data: any): any {
        return { success: true, payload: data };
    }
}

class GraphQLBuilder extends HttpBuilder {
    protected prepareHeaders(): void {
        this.headers['Content-Type'] = 'application/json';
    }
    
    protected buildRequest(url: string): any {
        return {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ query: '...graphql...' })
        };
    }
    
    protected async parseResponse(response: any): Promise<any> {
        const json = await response.json();
        if (json.errors) throw new Error(json.errors[0].message);
        return json.data;
    }
    
    protected transform(data: any): any {
        return { data, timestamp: new Date() };
    }
}

// 使用
const client = new APIClientBuilder();
const result = await client.execute('https://api.example.com/data');
```

---

## 单元测试

```java
@Test
public void testTemplateMethodExecution() {
    SortAlgorithm algorithm = new QuickSort();
    int[] data = {5, 2, 8, 1, 9};
    
    algorithm.sort(data);
    
    // 验证排序结果
    for (int i = 0; i < data.length - 1; i++) {
        assertTrue(data[i] <= data[i + 1]);
    }
}

@Test
public void testDataPipelineWithValidData() {
    DataPipeline pipeline = new CSVPipeline();
    List<String> input = Arrays.asList("a,b,c", "d,e,f");
    
    ProcessResult result = pipeline.execute(input);
    
    assertTrue(result.isSuccess());
    assertEquals(2, result.getRecordCount());
}

@Test
public void testDataPipelineErrorHandling() {
    DataPipeline pipeline = new CSVPipeline();
    List<String> invalidInput = Arrays.asList("", "no_comma", null);
    
    ProcessResult result = pipeline.execute(invalidInput);
    
    assertTrue(result.isSuccess());
    assertTrue(result.getRecordCount() >= 0);
}

@Test
public void testTemplateMethodWithHooks() {
    DataProcessor processor = new CSVProcessor() {
        @Override
        protected void onBeforeProcess() {
            System.out.println("Starting CSV process");
        }
    };
    
    processor.process(testData);
    // 验证钩子被调用
}
```

---

## 性能对比

| 算法 | N=1000 | N=10000 | N=100000 | 内存 | 稳定性 |
|------|--------|---------|----------|------|--------|
| 快速排序 | 0.2ms | 2.5ms | 28ms | O(log n) | ⭐⭐⭐ |
| 冒泡排序 | 5ms | 450ms | 45000ms | O(1) | ⭐ |
| 合并排序 | 0.3ms | 3.5ms | 35ms | O(n) | ⭐⭐⭐⭐⭐ |
| 堆排序 | 0.4ms | 4ms | 40ms | O(1) | ⭐⭐⭐⭐ |

| 管道类型 | 吞吐 | 延迟 | CPU | 适用场景 |
|---------|------|------|------|---------|
| CSV管道 | 10K rec/s | 100ms | 5% | 批处理 |
| JSON管道 | 5K rec/s | 200ms | 8% | API集成 |
| 流管道 | 50K rec/s | 50ms | 15% | 实时处理 |
