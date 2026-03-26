# TypeScript最佳实践参考文档

## TypeScript概述

### 什么是TypeScript
TypeScript是JavaScript的超集，添加了静态类型检查和现代JavaScript特性。它由Microsoft开发，编译成纯JavaScript代码，可以在任何支持JavaScript的环境中运行。

### 核心特性
- **静态类型检查**: 在编译时发现类型错误
- **现代JavaScript特性**: 支持ES6+语法
- **强大的工具支持**: 优秀的IDE集成和自动补全
- **渐进式采用**: 可以逐步引入类型检查
- **跨平台**: 支持浏览器、Node.js等多种环境

### TypeScript优势
- **代码质量**: 类型检查减少运行时错误
- **开发效率**: 智能提示和自动补全
- **代码维护**: 更好的代码可读性和可维护性
- **重构安全**: 类型系统确保重构的安全性
- **团队协作**: 统一的类型定义提高协作效率

## 编译器配置

### tsconfig.json配置

#### 基础配置
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "lib": ["ES2020", "DOM"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

#### 严格模式配置
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  }
}
```

#### 高级配置
```json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "resolveJsonModule": true,
    "allowSyntheticDefaultImports": true,
    "allowJs": true,
    "checkJs": false,
    "jsx": "react-jsx",
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@components/*": ["components/*"],
      "@utils/*": ["utils/*"],
      "@types/*": ["types/*"]
    },
    "typeRoots": ["./node_modules/@types", "./src/types"],
    "types": ["node", "jest", "react"]
  }
}
```

### 编译选项详解

#### 目标版本 (target)
- **ES3**: 最广泛兼容，但缺少现代特性
- **ES5**: 良好的浏览器兼容性
- **ES6+**: 现代JavaScript特性支持
- **ESNext**: 最新JavaScript特性

#### 模块系统 (module)
- **CommonJS**: Node.js默认模块系统
- **ES6/ESNext**: 现代模块系统，支持tree-shaking
- **AMD**: RequireJS等AMD加载器
- **UMD**: 通用模块定义，支持多种环境

#### 严格模式选项
```typescript
// noImplicitAny: 禁止隐式any类型
function processData(data: any) { // 错误：隐式any
  return data.toString();
}

function processData(data: unknown) { // 正确：使用unknown
  if (typeof data === 'string') {
    return data.toUpperCase();
  }
  return String(data);
}

// strictNullChecks: 严格空检查
const user: User | null = getUser();
console.log(user.name); // 错误：可能为null

if (user) {
  console.log(user.name); // 正确：已检查非空
}

// strictFunctionTypes: 严格函数类型
type EventHandler = (event: Event) => void;

const handler: EventHandler = (event: CustomEvent) => {
  console.log(event.detail); // 错误：参数类型不匹配
};
```

## 类型系统

### 基础类型

#### 原始类型
```typescript
// 基础类型
let name: string = "John";
let age: number = 30;
let isActive: boolean = true;
let data: null = null;
let value: undefined = undefined;

// 数值类型
let integer: number = 42;
let float: number = 3.14;
let hex: number = 0xf00d;
let binary: number = 0b1010;
let octal: number = 0o744;

// 字符串类型
let singleQuote: string = 'single';
let doubleQuote: string = "double";
let template: string = `template ${name}`;

// 数组类型
let numbers: number[] = [1, 2, 3];
let strings: Array<string> = ['a', 'b', 'c'];
let mixed: (string | number)[] = [1, 'two', 3];
```

#### 对象类型
```typescript
// 接口定义
interface User {
  id: number;
  name: string;
  email?: string; // 可选属性
  readonly createdAt: Date; // 只读属性
}

// 类型别名
type Product = {
  id: string;
  name: string;
  price: number;
  category: Category;
};

// 联合类型
type Status = 'pending' | 'approved' | 'rejected';
type Result = Success | Error;

// 交叉类型
type Person = {
  name: string;
  age: number;
};

type Employee = Person & {
  id: string;
  department: string;
};
```

### 高级类型

#### 泛型
```typescript
// 基础泛型
function identity<T>(arg: T): T {
  return arg;
}

const result = identity<string>("hello"); // 显式类型
const result2 = identity(42); // 类型推断

// 泛型接口
interface Collection<T> {
  add(item: T): void;
  remove(item: T): boolean;
  find(predicate: (item: T) => boolean): T | undefined;
}

// 泛型类
class Stack<T> {
  private items: T[] = [];
  
  push(item: T): void {
    this.items.push(item);
  }
  
  pop(): T | undefined {
    return this.items.pop();
  }
  
  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }
}

// 泛型约束
interface Lengthwise {
  length: number;
}

function logLength<T extends Lengthwise>(arg: T): void {
  console.log(arg.length);
}

logLength("hello"); // 正确
logLength(42); // 错误：没有length属性
```

#### 条件类型
```typescript
// 基础条件类型
type IsString<T> = T extends string ? true : false;

type Test1 = IsString<string>; // true
type Test2 = IsString<number>; // false

// 条件类型与泛型
type NonNullable<T> = T extends null | undefined ? never : T;

type StringOrNumber = string | number;
type Result = NonNullable<StringOrNumber | null>; // string | number

// 条件类型与映射
type Getters<T> = {
  [K in keyof T as T[K] extends Function ? never : K]: () => T[K];
};

interface User {
  id: number;
  name: string;
  getName(): string;
}

type UserGetters = Getters<User>;
// {
//   id: () => number;
//   name: () => string;
// }
```

#### 映射类型
```typescript
// 基础映射类型
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

// 自定义映射类型
type Stringify<T> = {
  [K in keyof T]: string;
};

interface User {
  id: number;
  name: string;
  active: boolean;
}

type StringifiedUser = Stringify<User>;
// {
//   id: string;
//   name: string;
//   active: string;
// }

// 条件映射类型
type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

type UserWithOptionalName = Optional<User, 'name'>;
// {
//   id: number;
//   name?: string;
//   active: boolean;
// }
```

## 函数类型

### 函数声明

#### 基础函数类型
```typescript
// 函数声明
function add(a: number, b: number): number {
  return a + b;
}

// 函数表达式
const multiply = (a: number, b: number): number => a * b;

// 函数类型别名
type Calculator = (a: number, b: number) => number;

const divide: Calculator = (a, b) => a / b;

// 可选参数
function greet(name: string, greeting?: string): string {
  return greeting ? `${greeting}, ${name}` : `Hello, ${name}`;
}

// 默认参数
function createCounter(initial = 0): () => number {
  let count = initial;
  return () => ++count;
}

// 剩余参数
function sum(...numbers: number[]): number {
  return numbers.reduce((total, num) => total + num, 0);
}
```

#### 函数重载
```typescript
// 函数重载声明
function processInput(input: string): string;
function processInput(input: number): number;
function processInput(input: boolean): boolean;

function processInput(input: string | number | boolean): string | number | boolean {
  if (typeof input === 'string') {
    return input.toUpperCase();
  }
  if (typeof input === 'number') {
    return input * 2;
  }
  return !input;
}

// 使用重载
const result1 = processInput("hello"); // string
const result2 = processInput(42); // number
const result3 = processInput(true); // boolean
```

#### 高级函数类型
```typescript
// 高阶函数
function withLogging<T extends (...args: any[]) => any>(
  fn: T
): T {
  return ((...args: any[]) => {
    console.log(`Calling ${fn.name} with args:`, args);
    const result = fn(...args);
    console.log(`Result:`, result);
    return result;
  }) as T;
}

const loggedAdd = withLogging(add);

// 柯里化
function curry<A, B, C>(fn: (a: A, b: B) => C): (a: A) => (b: B) => C {
  return (a) => (b) => fn(a, b);
}

const curriedAdd = curry(add);
const add5 = curriedAdd(5);
const result = add5(3); // 8

// 函数组合
function compose<A, B, C>(f: (b: B) => C, g: (a: A) => B): (a: A) => C {
  return (a) => f(g(a));
}

const double = (x: number) => x * 2;
const toString = (x: number) => x.toString();
const doubleToString = compose(toString, double);
```

## 类和接口

### 类定义

#### 基础类
```typescript
class Person {
  // 属性声明
  private name: string;
  protected age: number;
  public email: string;
  
  // 只读属性
  readonly id: string;
  
  // 静态属性
  static species = 'Homo sapiens';
  
  // 构造函数
  constructor(name: string, age: number, email: string) {
    this.name = name;
    this.age = age;
    this.email = email;
    this.id = generateId();
  }
  
  // 方法
  public introduce(): string {
    return `Hi, I'm ${this.name} and I'm ${this.age} years old.`;
  }
  
  // 受保护方法
  protected calculateBirthYear(): number {
    return new Date().getFullYear() - this.age;
  }
  
  // 静态方法
  static createAdult(name: string, email: string): Person {
    return new Person(name, 18, email);
  }
  
  // 访问器
  get fullName(): string {
    return this.name;
  }
  
  set fullName(value: string) {
    if (value.trim().length > 0) {
      this.name = value;
    }
  }
}
```

#### 继承和多态
```typescript
// 基类
abstract class Animal {
  protected name: string;
  
  constructor(name: string) {
    this.name = name;
  }
  
  abstract makeSound(): void;
  
  public move(): void {
    console.log(`${this.name} is moving`);
  }
}

// 派生类
class Dog extends Animal {
  private breed: string;
  
  constructor(name: string, breed: string) {
    super(name);
    this.breed = breed;
  }
  
  public makeSound(): void {
    console.log(`${this.name} barks`);
  }
  
  public wagTail(): void {
    console.log(`${this.name} wags tail`);
  }
}

class Cat extends Animal {
  private color: string;
  
  constructor(name: string, color: string) {
    super(name);
    this.color = color;
  }
  
  public makeSound(): void {
    console.log(`${this.name} meows`);
  }
  
  public purr(): void {
    console.log(`${this.name} purrs`);
  }
}

// 多态使用
function makeAnimalSound(animal: Animal): void {
  animal.makeSound();
}

const dog = new Dog("Buddy", "Golden Retriever");
const cat = new Cat("Whiskers", "orange");

makeAnimalSound(dog); // Buddy barks
makeAnimalSound(cat); // Whiskers meows
```

#### 接口实现
```typescript
// 接口定义
interface Drawable {
  draw(): void;
  area(): number;
}

interface Resizable {
  resize(factor: number): void;
}

// 类实现接口
class Rectangle implements Drawable, Resizable {
  private width: number;
  private height: number;
  
  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
  }
  
  public draw(): void {
    console.log(`Drawing ${this.width}x${this.height} rectangle`);
  }
  
  public area(): number {
    return this.width * this.height;
  }
  
  public resize(factor: number): void {
    this.width *= factor;
    this.height *= factor;
  }
}

// 接口继承
interface Shape extends Drawable {
  perimeter(): number;
}

class Circle implements Shape {
  private radius: number;
  
  constructor(radius: number) {
    this.radius = radius;
  }
  
  public draw(): void {
    console.log(`Drawing circle with radius ${this.radius}`);
  }
  
  public area(): number {
    return Math.PI * this.radius * this.radius;
  }
  
  public perimeter(): number {
    return 2 * Math.PI * this.radius;
  }
}
```

## 模块和命名空间

### ES6模块

#### 导出和导入
```typescript
// math.ts - 导出
export const PI = 3.14159;

export function add(a: number, b: number): number {
  return a + b;
}

export function multiply(a: number, b: number): number {
  return a * b;
}

// 默认导出
export default class Calculator {
  private history: number[] = [];
  
  public add(value: number): this {
    this.history.push(value);
    return this;
  }
  
  public getResult(): number {
    return this.history.reduce((sum, val) => sum + val, 0);
  }
}

// utils.ts - 重新导出
export { add, multiply } from './math';
export { Logger } from './logger';
export * from './constants';

// main.ts - 导入
import Calculator, { add, multiply, PI } from './math';
import { Logger } from './utils';

const calc = new Calculator();
const result = calc.add(5).add(3).getResult();
console.log(`Result: ${result}, PI: ${PI}`);
```

#### 动态导入
```typescript
// 动态导入模块
async function loadModule() {
  try {
    const module = await import('./math');
    console.log(module.add(2, 3));
  } catch (error) {
    console.error('Failed to load module:', error);
  }
}

// 条件导入
async function loadFeature(feature: string) {
  switch (feature) {
    case 'math':
      const math = await import('./math');
      return math;
    case 'utils':
      const utils = await import('./utils');
      return utils;
    default:
      throw new Error(`Unknown feature: ${feature}`);
  }
}
```

### 命名空间

#### 命名空间定义
```typescript
// 命名空间
namespace Geometry {
  export interface Point {
    x: number;
    y: number;
  }
  
  export class Circle {
    constructor(public center: Point, public radius: number) {}
    
    public area(): number {
      return Math.PI * this.radius * this.radius;
    }
  }
  
  export namespace Shapes {
    export class Rectangle {
      constructor(
        public topLeft: Point,
        public width: number,
        public height: number
      ) {}
      
      public area(): number {
        return this.width * this.height;
      }
    }
  }
}

// 使用命名空间
const point: Geometry.Point = { x: 0, y: 0 };
const circle = new Geometry.Circle(point, 5);
const rectangle = new Geometry.Shapes.Rectangle(point, 10, 5);

console.log(circle.area());
console.log(rectangle.area());
```

## 错误处理

### 类型安全的错误处理

#### Result类型
```typescript
// Result类型定义
type Result<T, E = Error> = Success<T> | Failure<E>;

class Success<T> {
  constructor(public value: T) {}
  
  isSuccess(): this is Success<T> {
    return true;
  }
  
  isFailure(): this is Failure<never> {
    return false;
  }
}

class Failure<E> {
  constructor(public error: E) {}
  
  isSuccess(): this is Success<never> {
    return false;
  }
  
  isFailure(): this is Failure<E> {
    return true;
  }
}

// 使用Result类型
function divide(a: number, b: number): Result<number, string> {
  if (b === 0) {
    return new Failure("Division by zero");
  }
  return new Success(a / b);
}

const result = divide(10, 2);

if (result.isSuccess()) {
  console.log(`Result: ${result.value}`);
} else {
  console.error(`Error: ${result.error}`);
}
```

#### 异步错误处理
```typescript
// 异步Result类型
type AsyncResult<T, E = Error> = Promise<Result<T, E>>;

async function fetchData(url: string): AsyncResult<Data, NetworkError> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      return new Failure(new NetworkError(`HTTP ${response.status}`));
    }
    const data = await response.json();
    return new Success(data);
  } catch (error) {
    return new Failure(new NetworkError(error.message));
  }
}

// 使用异步Result
async function processData() {
  const result = await fetchData('https://api.example.com/data');
  
  if (result.isFailure()) {
    console.error('Failed to fetch data:', result.error);
    return;
  }
  
  const data = result.value;
  // 处理数据
}
```

## 装饰器

### 类装饰器
```typescript
// 类装饰器
function logged<T extends { new(...args: any[]): {} }>(constructor: T) {
  return class extends constructor {
    constructor(...args: any[]) {
      super(...args);
      console.log(`Creating instance of ${constructor.name}`);
    }
  };
}

@logged
class UserService {
  constructor(private name: string) {}
  
  public getName(): string {
    return this.name;
  }
}

// 属性装饰器
function required(target: any, propertyKey: string | symbol) {
  let value: any;
  
  const getter = () => value;
  const setter = (newValue: any) => {
    if (newValue === null || newValue === undefined) {
      throw new Error(`${propertyKey.toString()} is required`);
    }
    value = newValue;
  };
  
  Object.defineProperty(target, propertyKey, {
    get: getter,
    set: setter,
    enumerable: true,
    configurable: true
  });
}

class User {
  @required
  public name: string;
  
  constructor(name: string) {
    this.name = name;
  }
}

// 方法装饰器
function measure(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  
  descriptor.value = function(...args: any[]) {
    const start = performance.now();
    const result = originalMethod.apply(this, args);
    const end = performance.now();
    console.log(`${propertyKey} took ${end - start} milliseconds`);
    return result;
  };
  
  return descriptor;
}

class Calculator {
  @measure
  public complexCalculation(): number {
    // 复杂计算
    let sum = 0;
    for (let i = 0; i < 1000000; i++) {
      sum += Math.random();
    }
    return sum;
  }
}
```

## 性能优化

### 编译性能

#### 增量编译
```json
{
  "compilerOptions": {
    "incremental": true,
    "tsBuildInfoFile": "./.tsbuildinfo"
  }
}
```

#### 项目引用
```json
// tsconfig.json
{
  "compilerOptions": {
    "composite": true,
    "declaration": true,
    "declarationMap": true
  },
  "references": [
    { "path": "./src/core" },
    { "path": "./src/utils" },
    { "path": "./src/components" }
  ]
}

// src/core/tsconfig.json
{
  "compilerOptions": {
    "composite": true,
    "outDir": "../../dist/core"
  }
}
```

### 运行时性能

#### 类型断言优化
```typescript
// 避免不必要的类型断言
interface User {
  name: string;
  age: number;
}

function processUser(user: User) {
  // 避免
  const name = (user as any).name;
  
  // 推荐
  const name = user.name;
}

// 使用类型守卫
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function processValue(value: unknown) {
  if (isString(value)) {
    // TypeScript知道value是string
    return value.toUpperCase();
  }
}
```

#### 内存优化
```typescript
// 使用WeakMap避免内存泄漏
class UserManager {
  private userMetadata = new WeakMap<User, Metadata>();
  
  public setMetadata(user: User, metadata: Metadata): void {
    this.userMetadata.set(user, metadata);
  }
  
  public getMetadata(user: User): Metadata | undefined {
    return this.userMetadata.get(user);
  }
}

// 使用对象池
class ObjectPool<T> {
  private pool: T[] = [];
  private createFn: () => T;
  private resetFn: (obj: T) => void;
  
  constructor(createFn: () => T, resetFn: (obj: T) => void) {
    this.createFn = createFn;
    this.resetFn = resetFn;
  }
  
  public acquire(): T {
    if (this.pool.length > 0) {
      return this.pool.pop()!;
    }
    return this.createFn();
  }
  
  public release(obj: T): void {
    this.resetFn(obj);
    this.pool.push(obj);
  }
}
```

## 最佳实践

### 代码组织

#### 文件结构
```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   ├── Button.styles.ts
│   │   └── index.ts
│   └── index.ts
├── utils/
│   ├── date.ts
│   ├── string.ts
│   └── index.ts
├── types/
│   ├── api.ts
│   ├── user.ts
│   └── index.ts
├── services/
│   ├── api.ts
│   ├── auth.ts
│   └── index.ts
└── index.ts
```

#### 模块组织
```typescript
// 统一导出
export { Button, Input, Select } from './components';
export { formatDate, parseDate } from './utils/date';
export { User, Product, Order } from './types';

// barrel exports
// components/index.ts
export { default as Button } from './Button';
export { default as Input } from './Input';
export { default as Select } from './Select';

// types/index.ts
export type { User } from './user';
export type { Product } from './product';
export type { Order } from './order';
```

### 类型设计

#### 类型优先设计
```typescript
// 类型优先设计
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

interface User {
  id: string;
  name: string;
  email: string;
}

type UserResponse = ApiResponse<User>;

// 使用类型
async function fetchUser(id: string): Promise<UserResponse> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}
```

#### 避免类型滥用
```typescript
// 避免
type AnyFunction = (...args: any[]) => any;
type AnyObject = { [key: string]: any };

// 推荐
type TypedFunction<T extends any[], R> = (...args: T) => R;
type TypedObject<T extends Record<string, any>> = T;
```

### 错误处理

#### 类型安全的错误处理
```typescript
// 定义错误类型
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500
  ) {
    super(message);
    this.name = 'AppError';
  }
}

class ValidationError extends AppError {
  constructor(message: string, public readonly field: string) {
    super(message, 'VALIDATION_ERROR', 400);
  }
}

// 错误处理函数
function handleError(error: unknown): never {
  if (error instanceof ValidationError) {
    console.error(`Validation error in ${error.field}: ${error.message}`);
  } else if (error instanceof AppError) {
    console.error(`App error (${error.code}): ${error.message}`);
  } else if (error instanceof Error) {
    console.error(`Unexpected error: ${error.message}`);
  } else {
    console.error('Unknown error occurred');
  }
  
  throw error;
}
```

## 参考资源

### 官方文档
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [TypeScript Playground](https://www.typescriptlang.org/play/)
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)

### 工具和库
- [ESLint TypeScript Plugin](https://typescript-eslint.io/)
- [Prettier](https://prettier.io/)
- [Jest TypeScript Support](https://jestjs.io/docs/getting-started#using-typescript)
- [TypeDoc](https://typedoc.org/)

### 最佳实践指南
- [TypeScript Best Practices](https://typescript-eslint.io/rules/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [Node.js TypeScript Best Practices](https://github.com/microsoft/TypeScript-Node-Starter)

### 社区资源
- [TypeScript GitHub](https://github.com/microsoft/TypeScript)
- [TypeScript Discord](https://discord.com/typescript)
- [Stack Overflow TypeScript](https://stackoverflow.com/questions/tagged/typescript)
