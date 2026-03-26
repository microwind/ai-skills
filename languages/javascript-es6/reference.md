# ES6+ JavaScript技术参考

## 概述

ES6 (ECMAScript 2015) 是JavaScript语言的重大更新，引入了许多现代编程特性。这些特性显著提升了代码的可读性、可维护性和开发效率。

## 变量声明

### let和const
```javascript
// let - 块级作用域变量
function example() {
  let x = 10;
  if (true) {
    let x = 20; // 不同作用域
    console.log(x); // 20
  }
  console.log(x); // 10
}

// const - 常量声明
const PI = 3.14159;
const API_URL = 'https://api.example.com';

// 对象和数组的const
const user = { name: 'John', age: 30 };
user.age = 31; // 允许修改属性
// user = {}; // 错误：不能重新赋值

const numbers = [1, 2, 3];
numbers.push(4); // 允许修改数组
// numbers = []; // 错误：不能重新赋值
```

### 暂时性死区
```javascript
// 暂时性死区示例
function example() {
  // console.log(x); // ReferenceError: Cannot access 'x' before initialization
  let x = 10;
}

// 与var的区别
console.log(varVar); // undefined (hoisted)
var varVar = 'var variable';

// console.log(letVar); // ReferenceError
let letVar = 'let variable';
```

## 箭头函数

### 基本语法
```javascript
// 传统函数
function add(a, b) {
  return a + b;
}

// 箭头函数
const add = (a, b) => a + b;

// 单参数可以省略括号
const double = x => x * 2;

// 无参数需要括号
const getRandom = () => Math.random();

// 多行函数体需要花括号和return
const calculate = (a, b, operation) => {
  switch (operation) {
    case 'add': return a + b;
    case 'subtract': return a - b;
    case 'multiply': return a * b;
    default: return 0;
  }
};
```

### this绑定
```javascript
// 传统函数的this
function Person() {
  this.age = 0;
  setInterval(function() {
    this.age++; // this指向全局对象或undefined
  }, 1000);
}

// 箭头函数的this
function Person() {
  this.age = 0;
  setInterval(() => {
    this.age++; // this指向Person实例
  }, 1000);
}

// 对象方法中的this
const obj = {
  name: 'Object',
  traditionalMethod: function() {
    console.log(this.name); // 'Object'
  },
  arrowMethod: () => {
    console.log(this.name); // undefined (this指向全局)
  }
};
```

## 模板字符串

### 基本用法
```javascript
const name = 'John';
const age = 30;

// 模板字符串
const message = `Hello, my name is ${name} and I'm ${age} years old.`;

// 多行字符串
const html = `
  <div class="user">
    <h2>${name}</h2>
    <p>Age: ${age}</p>
  </div>
`;

// 表达式计算
const price = 100;
const tax = 0.08;
const total = `Total: $${(price * (1 + tax)).toFixed(2)}`;

// 函数调用
const upperName = (name) => name.toUpperCase();
const greeting = `Hello, ${upperName(name)}!`;
```

### 标签模板
```javascript
// 自定义标签函数
function highlight(strings, ...values) {
  return strings.reduce((result, str, i) => {
    const value = values[i] || '';
    return result + str + `<mark>${value}</mark>`;
  }, '');
}

const name = 'John';
const age = 30;
const highlighted = highlight`Name: ${name}, Age: ${age}`;
// 结果: "Name: <mark>John</mark>, Age: <mark>30</mark>"

// SQL模板标签
function sql(strings, ...values) {
  return strings.reduce((result, str, i) => {
    const value = values[i] ? `'${values[i].replace(/'/g, "''")}'` : '';
    return result + str + value;
  }, '');
}

const query = sql`SELECT * FROM users WHERE name = ${name} AND age > ${age}`;
```

## 解构赋值

### 对象解构
```javascript
// 基本解构
const user = {
  name: 'John',
  age: 30,
  email: 'john@example.com'
};

const { name, age, email } = user;

// 重命名
const { name: userName, age: userAge } = user;

// 默认值
const { name, age, city = 'Unknown' } = user;

// 嵌套解构
const person = {
  name: 'John',
  address: {
    street: '123 Main St',
    city: 'New York',
    country: 'USA'
  }
};

const { 
  name, 
  address: { 
    street, 
    city, 
    country 
  } 
} = person;

// 函数参数解构
function greet({ name, age = 25 }) {
  console.log(`Hello ${name}, you are ${age} years old`);
}

greet({ name: 'Alice', age: 28 });
greet({ name: 'Bob' }); // age使用默认值25
```

### 数组解构
```javascript
// 基本解构
const numbers = [1, 2, 3, 4, 5];
const [first, second, third] = numbers;

// 跳过元素
const [, , , fourth, fifth] = numbers;

// 剩余元素
const [head, ...rest] = numbers;
console.log(head); // 1
console.log(rest); // [2, 3, 4, 5]

// 默认值
const [a, b, c = 3] = [1, 2];
console.log(c); // 3

// 交换变量
let x = 10, y = 20;
[x, y] = [y, x];

// 函数返回值解构
function getCoordinates() {
  return [10, 20, 30];
}

const [x, y, z] = getCoordinates();
```

## 扩展运算符

### 数组扩展
```javascript
// 数组合并
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2]; // [1, 2, 3, 4, 5, 6]

// 数组复制
const original = [1, 2, 3];
const copy = [...original];

// 数组添加元素
const numbers = [2, 3, 4];
const withStart = [1, ...numbers]; // [1, 2, 3, 4]
const withEnd = [...numbers, 5]; // [2, 3, 4, 5]

// 函数参数
function sum(...numbers) {
  return numbers.reduce((total, num) => total + num, 0);
}

sum(1, 2, 3, 4, 5); // 15

// Math.max应用
const max = Math.max(...[1, 5, 3, 9, 2]); // 9
```

### 对象扩展
```javascript
// 对象合并
const obj1 = { a: 1, b: 2 };
const obj2 = { c: 3, d: 4 };
const merged = { ...obj1, ...obj2 }; // { a: 1, b: 2, c: 3, d: 4 }

// 对象复制
const original = { name: 'John', age: 30 };
const copy = { ...original };

// 对象更新
const updated = { ...original, age: 31 }; // { name: 'John', age: 31 }

// 对象添加属性
const withEmail = { ...original, email: 'john@example.com' };

// 部分更新
const user = { name: 'John', age: 30, city: 'New York' };
const partialUpdate = { age: 31, country: 'USA' };
const updatedUser = { ...user, ...partialUpdate };
// { name: 'John', age: 31, city: 'New York', country: 'USA' }
```

## 类

### 基本类语法
```javascript
class Person {
  // 构造函数
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }

  // 实例方法
  greet() {
    return `Hello, my name is ${this.name}`;
  }

  // 访问器属性
  get info() {
    return `${this.name} is ${this.age} years old`;
  }

  set info(value) {
    const [name, age] = value.split(' is ');
    this.name = name;
    this.age = parseInt(age);
  }

  // 静态方法
  static createAnonymous() {
    return new Person('Anonymous', 0);
  }
}

// 使用类
const john = new Person('John', 30);
console.log(john.greet()); // "Hello, my name is John"
console.log(john.info); // "John is 30 years old"

john.info = 'Alice is 25 years old';
console.log(john.name); // "Alice"

const anonymous = Person.createAnonymous();
```

### 继承
```javascript
class Animal {
  constructor(name) {
    this.name = name;
  }

  speak() {
    return `${this.name} makes a sound`;
  }
}

class Dog extends Animal {
  constructor(name, breed) {
    super(name); // 调用父类构造函数
    this.breed = breed;
  }

  speak() {
    return `${this.name} barks`;
  }

  // 重写父类方法
  static getSpecies() {
    return 'Canine';
  }
}

// 使用继承
const dog = new Dog('Rex', 'German Shepherd');
console.log(dog.speak()); // "Rex barks"
console.log(dog.name); // "Rex"
console.log(Dog.getSpecies()); // "Canine"
```

## 模块

### 导入和导出
```javascript
// math.js - 导出模块
export const PI = 3.14159;

export function add(a, b) {
  return a + b;
}

export function multiply(a, b) {
  return a * b;
}

// 默认导出
export default class Calculator {
  constructor() {
    this.result = 0;
  }
  
  add(value) {
    this.result += value;
    return this;
  }
  
  getResult() {
    return this.result;
  }
}

// main.js - 导入模块
import Calculator, { PI, add, multiply } from './math.js';

const calc = new Calculator();
calc.add(5).add(3);
console.log(calc.getResult()); // 8

console.log(PI); // 3.14159
console.log(add(2, 3)); // 5
console.log(multiply(4, 5)); // 20

// 导入整个模块
import * as MathUtils from './math.js';
console.log(MathUtils.add(1, 2));
```

### 动态导入
```javascript
// 动态导入模块
async function loadModule() {
  try {
    const module = await import('./math.js');
    console.log(module.add(2, 3));
  } catch (error) {
    console.error('Failed to load module:', error);
  }
}

// 条件导入
if (process.env.NODE_ENV === 'development') {
  import('./dev-tools.js').then(module => {
    module.initDevTools();
  });
}
```

## Promise和异步编程

### Promise基础
```javascript
// 创建Promise
const promise = new Promise((resolve, reject) => {
  setTimeout(() => {
    const success = Math.random() > 0.5;
    if (success) {
      resolve('Operation successful');
    } else {
      reject('Operation failed');
    }
  }, 1000);
});

// 使用Promise
promise
  .then(result => console.log(result))
  .catch(error => console.error(error))
  .finally(() => console.log('Promise completed'));

// Promise链
function fetchUserData(userId) {
  return fetch(`/api/users/${userId}`)
    .then(response => response.json())
    .then(user => {
      return fetch(`/api/posts/${user.id}`)
        .then(response => response.json())
        .then(posts => ({ user, posts }));
    });
}
```

### async/await
```javascript
// async函数
async function fetchUserData(userId) {
  try {
    const userResponse = await fetch(`/api/users/${userId}`);
    const user = await userResponse.json();
    
    const postsResponse = await fetch(`/api/posts/${user.id}`);
    const posts = await postsResponse.json();
    
    return { user, posts };
  } catch (error) {
    console.error('Error fetching user data:', error);
    throw error;
  }
}

// 使用async/await
async function main() {
  try {
    const data = await fetchUserData(1);
    console.log('User:', data.user);
    console.log('Posts:', data.posts);
  } catch (error) {
    console.error('Main error:', error);
  }
}

// 并行执行
async function fetchMultipleUsers(userIds) {
  const promises = userIds.map(id => fetch(`/api/users/${id}`).then(r => r.json()));
  const users = await Promise.all(promises);
  return users;
}
```

## 新的数据结构

### Map
```javascript
// 创建Map
const map = new Map();

// 设置值
map.set('name', 'John');
map.set(123, 'Number key');
map.set({ key: 'object' }, 'Object key');

// 获取值
console.log(map.get('name')); // 'John'
console.log(map.get(123)); // 'Number key'

// 检查键是否存在
console.log(map.has('name')); // true
console.log(map.has('age')); // false

// 删除键
map.delete('name');

// 获取大小
console.log(map.size); // 2

// 遍历Map
for (const [key, value] of map) {
  console.log(`${key}: ${value}`);
}

// 从数组创建Map
const entries = [['name', 'John'], ['age', 30]];
const userMap = new Map(entries);
```

### Set
```javascript
// 创建Set
const set = new Set();

// 添加值
set.add(1);
set.add(2);
set.add(3);
set.add(2); // 重复值会被忽略

// 检查值是否存在
console.log(set.has(2)); // true
console.log(set.has(4)); // false

// 删除值
set.delete(2);

// 获取大小
console.log(set.size); // 2

// 遍历Set
for (const value of set) {
  console.log(value);
}

// 数组去重
const numbers = [1, 2, 2, 3, 3, 4, 4, 5];
const uniqueNumbers = [...new Set(numbers)]; // [1, 2, 3, 4, 5]
```

### WeakMap和WeakSet
```javascript
// WeakMap - 键必须是对象
const weakMap = new WeakMap();
const obj1 = { name: 'Object 1' };
const obj2 = { name: 'Object 2' };

weakMap.set(obj1, 'Value for object 1');
weakMap.set(obj2, 'Value for object 2');

console.log(weakMap.get(obj1)); // 'Value for object 1'

// WeakSet - 值必须是对象
const weakSet = new WeakSet();
weakSet.add(obj1);
weakSet.add(obj2);

console.log(weakSet.has(obj1)); // true
```

## 迭代器和生成器

### 迭代器
```javascript
// 自定义迭代器
class Range {
  constructor(start, end) {
    this.start = start;
    this.end = end;
  }

  [Symbol.iterator]() {
    let current = this.start;
    const end = this.end;
    
    return {
      next() {
        if (current <= end) {
          return { value: current++, done: false };
        } else {
          return { done: true };
        }
      }
    };
  }
}

// 使用迭代器
const range = new Range(1, 5);
for (const num of range) {
  console.log(num); // 1, 2, 3, 4, 5
}
```

### 生成器
```javascript
// 生成器函数
function* numberGenerator() {
  yield 1;
  yield 2;
  yield 3;
}

// 使用生成器
const gen = numberGenerator();
console.log(gen.next().value); // 1
console.log(gen.next().value); // 2
console.log(gen.next().value); // 3
console.log(gen.next().done); // true

// 无限序列生成器
function* fibonacci() {
  let [a, b] = [0, 1];
  while (true) {
    yield a;
    [a, b] = [b, a + b];
  }
}

const fib = fibonacci();
console.log(fib.next().value); // 0
console.log(fib.next().value); // 1
console.log(fib.next().value); // 1
console.log(fib.next().value); // 2

// 异步生成器
async function* asyncGenerator() {
  const data = await fetch('/api/data');
  const items = await data.json();
  
  for (const item of items) {
    yield item;
  }
}
```

## 新的内置方法

### 数组方法
```javascript
// Array.from - 从类数组对象创建数组
const arrayLike = { 0: 'a', 1: 'b', 2: 'c', length: 3 };
const array = Array.from(arrayLike); // ['a', 'b', 'c']

// Array.of - 创建数组
const arr1 = Array.of(1, 2, 3); // [1, 2, 3]
const arr2 = Array(3); // [empty × 3]

// find - 查找元素
const numbers = [1, 5, 10, 15];
const found = numbers.find(x => x > 10); // 15

// findIndex - 查找索引
const index = numbers.findIndex(x => x > 10); // 3

// includes - 检查包含
const hasTen = numbers.includes(10); // true

// keys, values, entries
const keys = numbers.keys(); // ArrayIterator
const values = numbers.values(); // ArrayIterator
const entries = numbers.entries(); // ArrayIterator

for (const key of keys) {
  console.log(key); // 0, 1, 2, 3
}
```

### 对象方法
```javascript
// Object.assign - 对象合并
const obj1 = { a: 1, b: 2 };
const obj2 = { c: 3, d: 4 };
const merged = Object.assign({}, obj1, obj2);

// Object.keys, Object.values, Object.entries
const obj = { a: 1, b: 2, c: 3 };
const keys = Object.keys(obj); // ['a', 'b', 'c']
const values = Object.values(obj); // [1, 2, 3]
const entries = Object.entries(obj); // [['a', 1], ['b', 2], ['c', 3]]

// Object.is - 值比较
console.log(Object.is(NaN, NaN)); // true
console.log(Object.is(+0, -0)); // false

// Object.getOwnPropertyDescriptors
const descriptors = Object.getOwnPropertyDescriptors(obj);
```

### 字符串方法
```javascript
// includes - 检查包含
const str = 'Hello World';
console.log(str.includes('World')); // true

// startsWith, endsWith
console.log(str.startsWith('Hello')); // true
console.log(str.endsWith('World')); // true

// repeat - 重复字符串
console.log('abc'.repeat(3)); // 'abcabcabc'

// padStart, padEnd
console.log('5'.padStart(3, '0')); // '005'
console.log('test'.padEnd(10, '-')); // 'test------'

// 模板字面量中的标签函数
function tag(strings, ...values) {
  console.log(strings); // ['Hello ', ', you are ', ' years old']
  console.log(values); // ['John', 30]
  return strings.reduce((result, str, i) => result + str + (values[i] || ''), '');
}

const name = 'John';
const age = 30;
const result = tag`Hello ${name}, you are ${age} years old`;
```

## 相关资源

### 官方文档
- [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [ECMAScript Specification](https://tc39.es/ecma262/)
- [JavaScript.info](https://javascript.info/)

### 学习资源
- [Exploring ES6](http://exploringjs.com/es6/)
- [You Don't Know JS](https://github.com/getify/You-Dont-Know-JS)
- [ES6 Features](https://github.com/lukehoban/es6features)

### 在线工具
- [Babel REPL](https://babeljs.io/repl/)
- [TypeScript Playground](https://www.typescriptlang.org/play/)
- [ES6 Compatibility Table](https://kangax.github.io/compat-table/es6/)

### 社区资源
- [Stack Overflow - JavaScript](https://stackoverflow.com/questions/tagged/javascript)
- [Reddit - r/javascript](https://www.reddit.com/r/javascript/)
- [JavaScript Weekly](https://javascriptweekly.com/)
