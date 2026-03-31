# Flyweight 模式 - 完整参考实现

## 核心原理

**Flyweight** 通过共享大量对象的公共部分来节省内存。将对象状态分为：
- **内在状态**: 不变、可共享的
- **外在状态**: 变化、由外界传入

## UML结构

```
┌────────────────────┐
│ FlyweightFactory   │
│ - flyweights: Map  │
│ + getFlyweight()   │
└────────────────────┘
        │ creates
        ▼
┌────────────────────┐
│ Flyweight (共享)   │
│ - intrinsicState   │
│ + operation(ext)   │
└────────────────────┘
```

## Java完整实现 - 字体对象池

```java
// Flyweight: 字体
public final class Font {
    private final String name;
    private final int size;
    private final String style;
    private final# Flyweight 模式 - 完整参考实现

## 核心原理

**Flyweight** 通过共享大量?a
## 核心原理

**Flyweight** 通过   
**Flyweight** = - **内在状态**: 不变、可共享的
- **外在状态**: 变化、由外界传入

## UML v- **外在状态**: 变化、由外界? 
## UML结构

```
┌─────── (%d,%d)%n", 
       │ FlyweightFactory   │
│ - flyweights: Map  │
│ + getFl@O│ - flyweights: Map  ? │ + getFlyweight()   ? └───────?r        │ creates
        ?(Font) o;
        return size == f.si        ▼
┌─f.┌──?y│ Flyweight (共享)   │
│ - intrinsicState   │
│ + opeod│ - intrinsicState   │
ti│ + ope.hash(name, size, └───────?g```

## Java完整实现 - 字体对象池

```java
// Flyweight:<S
#ing
```java
// Flyweight: 字体
publ   pr// Flystpublic final class mi    private final Stringc     private final int size;
 me    private final String s{
    private final# Flyweight ? 
## 核心原理

**Flyweight** 通过共享大量?a
#)) 
**Flyweight**hit## 核心原?  return cache.get(key);
        }
   **Flyweight** = - **?F- **外在状态**: 变化、由外界传入

## UML v- t(
## UML v- **外在状态**: 变化、由?  ## UML结构

```
┌─────── (%d,%de rate = (double?t       │ FlyweightFactory   │
?u│ - flyweights: Map  │
│ +Hi│ + getFl@O│ - flyweid\        ?(Font) o;
        return size == f.si        ▼
┌─f.┌──?y│ Flyweight (共享)   │
│ ng   args) {
        f┌─f.┌──?y│ Flyweight (? │ - intrinsicState   │
│ + opeod│ - int"B│ + opeod│ - intrinsierti│ + ope.hash(name, size, └─? 
## Java完整实现 - 字体对象池

```java
// Flyweig - 
```java
// Flyweight:<S
#ing
```javype// Flyde#ing
```java
/f,```me// Flye,publ   pr// Flystpuel me    private final String s{
    private final# Flyweight ? 
## 核心原理

**Flyweigb"    private final# Flyweight h_## 核心原理

**Flyweight** el
**Flyweight**alu#)) 
**Flyweight**hit## 核心原?)**F          }
   **Flyweight** = - **?F- **外在状?     self.val
## UML v- t(
## UML v- **外在状态**: 变化、由?  ## UML结?  ## UML v- *0

```
┌──────? get_piece(cls, name, value, s?o?u│ - flyweights: Map  │
│ +Hi│ + getFl@O│ - flyweid\        ?(Font) ohi│ +Hi│ + getFl@O│ - flys.        return size == f.si        ▼
┌─f.┌? ┌─f.┌──?y│ Flyweight (?
│ ng   args) {
        f┌─f.┌──?y?i        f┌─la│ + opeod│ - int"B│ + opeod│ - intrinsierti│ + ope.hash(name, s  ## Java完整实现 - 字体对象池

```java
// Flyweig - 
```java
// Flyweight:<S
#Mi
```java
// Flyweig - 
```java
// Fl:.1// Fly
#```java
// Fi // Flyge#ing
```javypewn```Pi```java
/f,```me// F("/f,``` 1    private final# Flyweight ? 
## 核心原?t实现 - 连接池?# 核心原理

**Flyweigb"   ec
**Flyweigb"     
**Flyweight** el
**Flyweight**alu#)) 
**Flyweight**hit#t: **Flyweight**aly **Flyweight**hit## nl   **Flyweight** = - **?F- **外在状? ll## UML v- t(
## UML v- **外在状态**: 变化、由?u## UML v- *ho
```
┌──────? get_piece(cls, name, value, s?o?u│te ?t│ +Hi│ + getFl@O│ - flyweid\        ?(Font) ohi│ +Hi│ + getFl@O│ - flys.    ┌─f.┌? ┌─f.┌──?y│ Flyweight (?
│ ng   args) {
        f┌─f.┌──?y?i        f┌─la?t│ ng   args) {
        f┌─f.┌──?y?i   an        f┌─  
```java
// Flyweig - 
```java
// Flyweight:<S
#Mi
```java
// Flyweig - 
```java
// Fl:.1// Fly
#```java
// Fi // Flyge#ing
```javypewn```Pi```java
/f,```me// F   // Flyst```java
// F  // Fly  #Mi
```java
//ca``e.// Flyy)```java
// F
 // Fl: 
#```java
// Fst// Fi /se```javypewn```Pi`t /f,```me// F("/f,``` 1nC## 核心原?t实现 - 连接池?# 核心原理

*nf
**Flyweigb"   ec
**Flyweigb"     
**Flyweight** tat**Flyweigb"    onst total = this.s**Flyweight**als.stats.misses;
       ## UML v- **外在状态**: 变化、由?u## UML v- *ho
```
┌──────? get_piece(cls, name, value,  $```
┌──────? get_piece(cls, name, value,av?u│ ng   args) {
        f┌─f.┌──?y?i        f┌─la?t│ ng   args) {
        f┌─f.┌──?y?i   an        f┌─  
```java
// Flyweig - 
```java
// Flyweight:<S
#Mi
```java
// Flyweig - f1        f┌─??       f┌─f.┌──?y?i   an        f┌─  
```java
// Fl  ```java
// Flyweig - 
```java
// Flyweight:<S
#Mi
```ct// FlytF```java
// F 1// Flyld#Mi
```java
//  ``  // Fly??```java
// F 9// Fl   #```java
// Fes// Fi /ub```javypewn```Pi`ry/f,```me// 
        // 1// F  // Fly  #Mi
```java
//c =```java
//ca``e.
 //c}
}
`// F
 // Fl: 
#```java ?//??#```javly// ght | 
*nf
**Flyweigb"   ec
**Flyweigb"     
**Flyweight** tat**Flyweigb"    onst total = this.s**Flyweight**als.✅**
|**Flyweigb"     5**Flyweight** t??       ## UML v- **外在状态**: 变化、由?u## UML v- *ho
```
┌──??``
┌──────? get_piece(cls, name, value,  $```
--?-┌──────? get_piece(cls, name, value,av? ?       f┌─f.┌──?y?i        f┌─la?t│ ng   args) {
    C        f┌─f.┌──?y?i   an        f┌─  
```java
// Fl
*```java
// Flyweig - 
```java
// Flyweight:<S
#Mi
```?>// Fly*Q```java
// F??// Fly?Mi
```java
//: ``??/ Fl修```java
// Fl  ```java
// Flyweig - 
```java
// Flyweight:<S
#Mi
```ct// FlytF```java??// Fl ?/ Flyweig - ??``java
// F: // Flycu#Mi
```ct// Fl?s``ch// F 1// Flyld#Mi
`?`???**  
A: Flywe//  ``??/ F 9// Fl  ?，对象?/ Fes// Fi /ub```jav销毁
