---
name: TypeScript编程
description: "当使用TypeScript编程时，分析类型系统，优化代码结构，解决类型安全问题。验证类型设计，构建大型应用，和最佳实践。"
license: MIT
---

# TypeScript编程技能

## 概述
TypeScript是JavaScript的超集，添加了静态类型检查、类、接口、泛型等特性。TypeScript通过编译时类型检查提高了代码的可维护性和开发效率，特别适合构建大型、复杂的前端和后端应用。不当的TypeScript使用会导致类型冗余、编译错误、开发效率降低。

**核心原则**: 好的TypeScript代码应该类型安全、结构清晰、可维护性强、开发效率高。坏的TypeScript代码会过度类型化、类型滥用、编译复杂。

## 何时使用

**始终:**
- 构建大型前端应用时
- 开发企业级后端服务时
- 需要类型安全保障时
- 团队协作开发时
- 重构现有JavaScript代码时
- 构建类型安全的API时

**触发短语:**
- "TypeScript类型怎么定义？"
- "泛型使用最佳实践"
- "TypeScript接口设计"
- "类型推断vs显式类型"
- "TypeScript配置优化"
- "类型体操技巧"

## TypeScript编程技能功能

### 类型系统
- 基础类型和高级类型
- 接口和类型别名
- 泛型编程
- 联合类型和交叉类型
- 条件类型和映射类型

### 面向对象
- 类和继承
- 访问修饰符
- 抽象类和接口
- 装饰器
- 模块和命名空间

### 工具类型
- 内置工具类型
- 自定义工具类型
- 类型推导
- 类型守卫
- 类型断言

### 配置和构建
- tsconfig.json配置
- 编译选项优化
- 声明文件编写
- 模块解析策略
- 构建工具集成

## 常见问题

### 类型问题
- **问题**: 类型过于复杂
- **原因**: 过度使用高级类型
- **解决**: 简化类型定义，使用类型别名

- **问题**: 类型推断失败
- **原因**: 类型信息不足
- **解决**: 添加类型注解，使用类型断言

### 编译问题
- **问题**: 编译速度慢
- **原因**: 项目规模大，配置不当
- **解决**: 优化tsconfig配置，使用增量编译

- **问题**: 类型检查过于严格
- **原因**: 编译选项设置不当
- **解决**: 调整strict相关选项

### 开发效率
- **问题**: 类型定义冗余
- **原因**: 过度显式类型注解
- **解决**: 依赖类型推断，简化类型定义

## 代码示例

### 基础类型和接口
```typescript
// 基础类型
let isDone: boolean = false;
let decimal: number = 6;
let color: string = "blue";
let list: number[] = [1, 2, 3];
let x: [string, number] = ["hello", 10];

// 枚举
enum Color {
    Red,
    Green,
    Blue
}
let c: Color = Color.Green;

// any和unknown
let notSure: any = 4;
let value: unknown = 4;

// void和never
function warnUser(): void {
    console.log("This is a warning message");
}

function error(message: string): never {
    throw new Error(message);
}

// 对象类型
interface Person {
    name: string;
    age: number;
    email?: string; // 可选属性
    readonly id: number; // 只读属性
}

// 函数类型
interface SearchFunc {
    (source: string, subString: string): boolean;
}

let mySearch: SearchFunc = function(source: string, subString: string) {
    return source.search(subString) > -1;
};

// 索引签名
interface StringArray {
    [index: number]: string;
}

let myArray: StringArray = ["Bob", "Fred"];

let myStr: string = myArray[0];

// 类
class Student {
    fullName: string;
    constructor(public firstName: string, public middleInitial: string, public lastName: string) {
        this.fullName = firstName + " " + middleInitial + " " + lastName;
    }
}

interface Person {
    firstName: string;
    lastName: string;
}

function greeter(person: Person) {
    return "Hello, " + person.firstName + " " + person.lastName;
}

let user = new Student("Jane", "M.", "User");

console.log(greeter(user));
```

### 泛型编程
```typescript
// 泛型函数
function identity<T>(arg: T): T {
    return arg;
}

let output = identity<string>("myString");
let output2 = identity<number>(100);

// 泛型约束
interface Lengthwise {
    length: number;
}

function loggingIdentity<T extends Lengthwise>(arg: T): T {
    console.log(arg.length);
    return arg;
}

loggingIdentity({length: 10, value: 3});

// 泛型类
class GenericNumber<T> {
    zeroValue: T;
    add: (x: T, y: T) => T;
}

let myGenericNumber = new GenericNumber<number>();
myGenericNumber.zeroValue = 0;
myGenericNumber.add = function(x, y) { return x + y; };

// 泛型接口
interface Box<T> {
    contents: T;
}

let box: Box<string> = {
    contents: "hello world"
};

// 条件类型
type IsString<T> = T extends string ? true : false;

type Test1 = IsString<string>; // true
type Test2 = IsString<number>; // false

// 映射类型
type Readonly<T> = {
    readonly [P in keyof T]: T[P]
};

type Partial<T> = {
    [P in keyof T]?: T[P]
};

interface Person {
    name: string;
    age: number;
}

type ReadonlyPerson = Readonly<Person>;
type PartialPerson = Partial<Person>;

// 工具类型
type Required<T> = {
    [P in keyof T]-?: T[P]
};

type Pick<T, K extends keyof T> = {
    [P in K]: T[P]
};

type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;

type PersonPartial = Partial<Person>;
type PersonRequired = Required<Person>;
type PersonNameOnly = Pick<Person, 'name'>;
type PersonWithoutAge = Omit<Person, 'age'>;
```

### 高级类型
```typescript
// 联合类型和交叉类型
type UnionType = string | number;
type IntersectionType = Person & Student;

// 字面量类型
type Direction = "North" | "South" | "East" | "West";

// 函数重载
function padLeft(value: string, padding: string): string;
function padLeft(value: string, padding: number): string;
function padLeft(value: string, padding: string | number): string {
    if (typeof padding === "number") {
        return Array(padding + 1).join(" ") + value;
    }
    if (typeof padding === "string") {
        return padding + value;
    }
    throw new Error("Expected string or number");
}

// 类型守卫
function isString(value: unknown): value is string {
    return typeof value === "string";
}

function processValue(value: unknown) {
    if (isString(value)) {
        console.log(value.toUpperCase()); // TypeScript知道value是string
    }
}

// 类型断言
let someValue: unknown = "this is a string";
let strLength: number = (someValue as string).length;

// 非空断言
function fixed(name: string | null): string {
    return name!;
}

// 可辨识联合
interface Square {
    kind: "square";
    size: number;
}

interface Rectangle {
    kind: "rectangle";
    width: number;
    height: number;
}

interface Circle {
    kind: "circle";
    radius: number;
}

type Shape = Square | Rectangle | Circle;

function area(s: Shape): number {
    switch (s.kind) {
        case "square": return s.size * s.size;
        case "rectangle": return s.width * s.height;
        case "circle": return Math.PI * s.radius ** 2;
    }
}

// 递归类型
interface ListNode {
    value: T;
    next: ListNode | null;
}

// 模板字面量类型
type EventName<T extends string> = `on${Capitalize<T>}`;

type ClickEvent = EventName<'click'>; // "onClick"

// 索引访问类型
type PersonKeys = keyof Person; // "name" | "age" | "email" | "id"

type PersonNameType = Person['name']; // string

// 条件映射类型
type NonNullable = T extends null | undefined ? never : T;

type StringOrNull = string | null;
type StringOnly = NonNullable<StringOrNull>; // string
```

### 装饰器和元编程
```typescript
// 类装饰器
function sealed(constructor: Function) {
    Object.seal(constructor);
    Object.seal(constructor.prototype);
}

@sealed
class Greeter {
    greeting: string;
    constructor(message: string) {
        this.greeting = message;
    }
    greet() {
        return "Hello, " + this.greeting;
    }
}

// 方法装饰器
function enumerable(value: boolean) {
    return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        descriptor.enumerable = value;
    };
}

class Greeter2 {
    greeting: string;
    constructor(message: string) {
        this.greeting = message;
    }

    @enumerable(false)
    greet() {
        return "Hello, " + this.greeting;
    }
}

// 访问器装饰器
function format(prefix: string) {
    return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = function(...args: any[]) {
            const result = originalMethod.apply(this, args);
            return `${prefix}${result}`;
        };
    };
}

class Person {
    private _name: string;
    
    constructor(name: string) {
        this._name = name;
    }
    
    @format("Mr. ")
    get name(): string {
        return this._name;
    }
}

// 参数装饰器
function required(target: any, propertyKey: string | symbol | undefined, parameterIndex: number) {
    console.log(`Parameter ${parameterIndex} of ${String(propertyKey)} is required`);
}

class Greeter3 {
    greeting: string;
    
    constructor(@required greeting: string) {
        this.greeting = greeting;
    }
}

// 属性装饰器
function format(target: any, propertyKey: string) {
    let value: string;
    
    const getter = () => {
        return value;
    };
    
    const setter = (newVal: string) => {
        value = newVal.toUpperCase();
    };
    
    Object.defineProperty(target, propertyKey, {
        get: getter,
        set: setter,
        enumerable: true,
        configurable: true
    });
}

class Product {
    @format
    title: string;
    
    constructor(title: string) {
        this.title = title;
    }
}

const product = new Product("hello world");
console.log(product.title); // HELLO WORLD
product.title = "new title";
console.log(product.title); // NEW TITLE
```

### 模块和命名空间
```typescript
// 模块导出
// math.ts
export function add(x: number, y: number): number {
    return x + y;
}

export function subtract(x: number, y: number): number {
    return x - y;
}

export default function multiply(x: number, y: number): number {
    return x * y;
}

// 模块导入
import { add, subtract } from './math';
import multiply from './math';

let result = add(5, 3);
let result2 = multiply(4, 5);

// 命名空间
namespace Validation {
    export interface StringValidator {
        isAcceptable(s: string): boolean;
    }
    
    const lettersRegexp = /^[A-Za-z]+$/;
    export class LettersOnlyValidator implements StringValidator {
        isAcceptable(s: string) {
            return lettersRegexp.test(s);
        }
    }
    
    const numberRegexp = /^[0-9]+$/;
    export class ZipCodeValidator implements StringValidator {
        isAcceptable(s: string) {
            return s.length === 5 && numberRegexp.test(s);
        }
    }
}

// 使用命名空间
let strings = ["Hello", "98052", "10123"];
let validators: { [s: string]: Validation.StringValidator } = {};

validators["Hello"] = new Validation.LettersOnlyValidator();
validators["98052"] = new Validation.ZipCodeValidator();
validators["10123"] = new Validation.ZipCodeValidator();

for (let s of strings) {
    console.log(`'${s}' - ${validators[s].isAcceptable(s) ? "matches" : "does not match"}`);
}

// 声明合并
interface Box {
    height: number;
    width: number;
}

interface Box {
    scale: number;
}

let box: Box = {
    height: 5,
    width: 6,
    scale: 10
};

// 混合
class Disposable {
    isDisposed: boolean = false;
    dispose() {
        this.isDisposed = true;
    }
}

class Activatable {
    isActive: boolean = false;
    activate() {
        this.isActive = true;
    }
    deactivate() {
        this.isActive = false;
    }
}

// 混合函数
function mix<T extends Constructor, U extends Constructor>(base: T, mixin: U): T & U {
    return class extends base {
        constructor(...args: any[]) {
            super(...args);
            Object.assign(this, new mixin());
        }
    };
}

class Constructor {
    constructor(...args: any[]) {}
}

class SmartObject implements Disposable, Activatable {
    // ...
}

// 使用混合
let SmartObjectMix = mix(SmartObject, Disposable);
```

### 实际应用示例
```typescript
// API响应类型定义
interface ApiResponse<T> {
    data: T;
    message: string;
    success: boolean;
}

interface User {
    id: number;
    name: string;
    email: string;
    avatar?: string;
}

// 服务类
class UserService {
    private baseUrl: string;
    
    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }
    
    async getUser(id: number): Promise<ApiResponse<User>> {
        const response = await fetch(`${this.baseUrl}/users/${id}`);
        const data = await response.json();
        
        return {
            data: data,
            message: "User fetched successfully",
            success: true
        };
    }
    
    async createUser(userData: Omit<User, 'id'>): Promise<ApiResponse<User>> {
        const response = await fetch(`${this.baseUrl}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        return {
            data: data,
            message: "User created successfully",
            success: true
        };
    }
    
    async updateUser(id: number, updates: Partial<User>): Promise<ApiResponse<User>> {
        const response = await fetch(`${this.baseUrl}/users/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
        });
        
        const data = await response.json();
        
        return {
            data: data,
            message: "User updated successfully",
            success: true
        };
    }
}

// 状态管理类型
type AppState = {
    user: User | null;
    loading: boolean;
    error: string | null;
};

type AppAction = 
    | { type: 'SET_USER'; payload: User }
    | { type: 'SET_LOADING'; payload: boolean }
    | { type: 'SET_ERROR'; payload: string }
    | { type: 'CLEAR_ERROR' };

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
    switch (action.type) {
        case 'SET_USER':
            return { ...state, user: action.payload, loading: false, error: null };
        case 'SET_LOADING':
            return { ...state, loading: action.payload };
        case 'SET_ERROR':
            return { ...state, error: action.payload, loading: false };
        case 'CLEAR_ERROR':
            return { ...state, error: null };
        default:
            return state;
    }
}

// 表单类型
interface FormField<T = string> {
    value: T;
    error?: string;
    touched: boolean;
}

interface LoginForm {
    email: FormField<string>;
    password: FormField<string>;
    rememberMe: FormField<boolean>;
}

// 表单验证器
type Validator<T> = (value: T) => string | undefined;

interface FormValidators {
    email: Validator<string>;
    password: Validator<string>;
    rememberMe: Validator<boolean>;
}

const validators: FormValidators = {
    email: (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email) ? undefined : 'Invalid email address';
    },
    password: (password) => {
        return password.length >= 8 ? undefined : 'Password must be at least 8 characters';
    },
    rememberMe: () => undefined
};

// 表单处理类
class FormHandler<T extends Record<string, FormField>> {
    private formData: T;
    private validators: Partial<Record<keyof T, Validator>> = {};
    
    constructor(initialData: T) {
        this.formData = { ...initialData };
    }
    
    setValidator<K extends keyof T>(field: K, validator: Validator<T[K]['value']>) {
        this.validators[field] = validator;
    }
    
    setValue<K extends keyof T>(field: K, value: T[K]['value']) {
        this.formData[field] = {
            ...this.formData[field],
            value,
            touched: true
        };
        this.validateField(field);
    }
    
    validateField<K extends keyof T>(field: K): string | undefined {
        const validator = this.validators[field];
        if (!validator) return undefined;
        
        const error = validator(this.formData[field].value);
        this.formData[field] = {
            ...this.formData[field],
            error
        };
        
        return error;
    }
    
    validateAll(): boolean {
        let isValid = true;
        
        for (const field in this.formData) {
            const error = this.validateField(field as keyof T);
            if (error) isValid = false;
        }
        
        return isValid;
    }
    
    getData(): T {
        return this.formData;
    }
}

// 使用示例
const initialLoginForm: LoginForm = {
    email: { value: '', touched: false },
    password: { value: '', touched: false },
    rememberMe: { value: false, touched: false }
};

const formHandler = new FormHandler(initialLoginForm);
formHandler.setValidator('email', validators.email);
formHandler.setValidator('password', validators.password);
formHandler.setValidator('rememberMe', validators.rememberMe);

formHandler.setValue('email', 'test@example.com');
formHandler.setValue('password', 'password123');
formHandler.setValue('rememberMe', true);

const isValid = formHandler.validateAll();
const formData = formHandler.getData();
```

## 最佳实践

### 类型设计
1. **类型优先**: 优先使用类型而非接口
2. **类型推断**: 依赖编译器推断，减少显式注解
3. **类型约束**: 使用泛型约束提高类型安全性
4. **工具类型**: 充分利用内置工具类型

### 代码组织
1. **模块化**: 合理划分模块和命名空间
2. **类型分离**: 将类型定义与实现分离
3. **声明文件**: 为第三方库编写声明文件
4. **导出策略**: 合理使用默认导出和命名导出

### 配置优化
1. **严格模式**: 启用strict相关选项
2. **增量编译**: 使用增量编译提高构建速度
3. **路径映射**: 配置路径映射简化导入
4. **目标选择**: 根据目标环境选择合适配置

### 性能优化
1. **类型简化**: 避免过度复杂的类型定义
2. **编译优化**: 优化tsconfig配置
3. **代码分割**: 合理使用代码分割
4. **类型缓存**: 利用类型缓存提高编译速度

## 相关技能

- **javascript-es6** - 现代JavaScript
- **c** - C语言编程
- **cpp** - C++编程
- **kotlin** - Kotlin编程
- **frontend** - 前端开发
