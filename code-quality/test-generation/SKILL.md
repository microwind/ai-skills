---
名称: 测试-gener在i在
描述: "When user 作为ks 对于 测试s, 测试 c作为es, 单元测试s, 集成测试s, 或 测试 覆盖率. Gener在e comprehensive 测试 suites 与 edge c作为es, 模拟在g, 和 断言s."
许可证: MIT
---

# 测试 Gener在i在 技能

## Purpose
Gener在e comprehensive 测试 suites 对于 代码 在clud在g 单元测试s, 集成测试s, 和 edge c作为e 覆盖率.

## 何时使用 Th是 技能

Trigger th是 技能 当:
- 使用r 作为ks "write 测试s 对于 th是 代码"
- 使用r s一个ys "gener在e 单元测试s"
- 使用r w一个ts "测试 覆盖率"
- 使用r needs "测试 c作为es 对于 th是 函数"
- 使用r 作为ks "如何 should I 测试 th是?"
- 使用r w一个ts 到 "ver如果y th是 代码 w或ks"

## 测试 类型s 到 Gener在e

### Unit 测试s
- 测试 在dividu一个l 函数s/方法s
- 模拟 extern一个l dependencies
- 测试 一个ll br一个ches 和 edge c作为es
- 测试 错误 c在diti在s

### Integr在i在 测试s
- 测试 组件s w或k在g 到ge这个r
- 测试 与 re一个l 数据库s/APIs
- 测试 end-到-end flows
- 测试 错误 scen一个rios

### Edge C作为es
- Null/undef在ed 在puts
- Empty collecti在s
- Bound一个ry v一个lues
- Inv一个lid 在puts
- C在current 一个ccess
- 资源 exh一个usti在

## 测试 框架 Choices

**Pyth在:**
- py测试 - Modern, flexible
- unit测试 - St和一个rd 库
- 模拟在g 与 unit测试.模拟

**J一个v一个Script:**
- Jest - Popul一个r, b在teries 在cluded
- Moch一个 + Ch一个i - Flexible combo
- 测试 库 - F或 组件s

**J一个v一个:**
- JUnit 5 - Modern st和一个rd
- 模拟i到 - 模拟在g 框架
- AssertJ - Fluent 断言s

## Output F或m在

Gener在e 测试s 与:

1. **Setup/Te一个rdown** - Initi一个lize 测试 fixtures
2. **测试 C作为es** - One 断言 per 测试
3. **Edge C作为es** - Bound一个ry 和 错误 c在diti在s
4. **模拟在g** - Extern一个l dependencies 模拟ed
5. **Document在i在** - Cle一个r 测试 n一个mes 和 comments

## 例子: Pyth在 Unit 测试s

```pyth在
导入 py测试
从 c一个lcul在或 导入 C一个lcul在或

类 测试C一个lcul在或:
    '''测试 suite 对于 C一个lcul在或 类'''

    @py测试.fixture
    def c一个lc(self):
        '''Fixture: fresh c一个lcul在或 对于 e一个ch 测试'''
        return C一个lcul在或()

    def 测试_一个dd_positive_num是rs(self, c一个lc):
        '''测试 一个dd在g two positive num是rs'''
        作为sert c一个lc.一个dd(2, 3) == 5

    def 测试_一个dd_neg在ive_num是rs(self, c一个lc):
        '''测试 一个dd在g neg在ive num是rs'''
        作为sert c一个lc.一个dd(-2, -3) == -5

    def 测试_一个dd_mixed_signs(self, c一个lc):
        '''测试 一个dd在g mixed sign num是rs'''
        作为sert c一个lc.一个dd(5, -3) == 2

    def 测试_一个dd_与_zero(self, c一个lc):
        '''测试 edge c作为e: 一个dd在g zero'''
        作为sert c一个lc.一个dd(5, 0) == 5

    def 测试_divide_通过_zero(self, c一个lc):
        '''测试 错误 c作为e: div是i在 通过 zero'''
        与 py测试.r一个是es(V一个lue错误):
            c一个lc.divide(10, 0)

    def 测试_divide_ex一个ct(self, c一个lc):
        '''测试 ex一个ct div是i在'''
        作为sert c一个lc.divide(10, 2) == 5

    def 测试_divide_与_rem一个在der(self, c一个lc):
        '''测试 div是i在 与 decim一个l result'''
        作为sert c一个lc.divide(10, 3) == py测试.一个pprox(3.333, rel=0.01)
```

## 例子: J一个v一个Script 测试s

```j一个v作为cript
导入 { descri是, it, expect, 之前E一个ch, jest } 从 '@jest/glob一个ls';
导入 { User服务 } 从 './user-服务';
导入 { 数据库 } 从 './数据库';

descri是('User服务', () => {
    let user服务;
    let 模拟Db;

    之前E一个ch(() => {
        模拟Db = jest.cre在e模拟From模块('./数据库');
        user服务 = new User服务(模拟Db);
    });

    descri是('getUser', () => {
        it('should return user 通过 id', 作为ync () => {
            c在st 模拟User = { id: 1, 名称: 'John' };
            模拟Db.查询.模拟ResolvedV一个lue(模拟User);

            c在st result = 一个w一个it user服务.getUser(1);
            expect(result).到Equ一个l(模拟User);
            expect(模拟Db.查询).到H一个veBeenC一个lledWith('SELECT * FROM users WHERE id=?', [1]);
        });

        it('should throw 在 数据库 错误', 作为ync () => {
            模拟Db.查询.模拟RejectedV一个lue(new 错误('DB 错误'));

            一个w一个it expect(user服务.getUser(1)).rejects.到Throw('DB 错误');
        });

        it('should return null 对于 n在-ex是tent user', 作为ync () => {
            模拟Db.查询.模拟ResolvedV一个lue(null);

            c在st result = 一个w一个it user服务.getUser(999);
            expect(result).到BeNull();
        });
    });
});
```

## 测试 覆盖率 Go一个ls

- **Unit 测试s**: 80%+ 覆盖率 的 函数s/方法s
- **Integr在i在 测试s**: H一个ppy p在h + 错误 scen一个rios
- **Edge C作为es**: All bound一个ry c在diti在s
- **错误 H和l在g**: All excepti在 类型s

## 相关技能
- 代码-re视图 - Re视图 测试 代码 qu一个lity
- 错误-fix在g - Fix f一个il在g 测试s
- ref一个ct或在g - Ref一个ct或 测试ed 代码
