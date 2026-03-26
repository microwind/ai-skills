# Version Manager 技术参考

## 概述

Version Manager 是一个专门用于管理软件版本的工具，提供版本号生成、语义化版本控制、版本发布管理和版本历史跟踪功能。

## 核心功能

### 版本号管理
- **语义化版本**: 遵循 SemVer 规范的版本号管理
- **自动递增**: 根据变更类型自动递增版本号
- **版本比较**: 支持版本号比较和排序
- **版本范围**: 支持版本范围匹配和依赖解析

### 发布管理
- **发布流程**: 自动化的发布流程管理
- **发布笔记**: 自动生成发布说明
- **标签管理**: Git 标签的创建和管理
- **分支策略**: 支持多种分支发布策略

### 变更跟踪
- **变更分析**: 分析代码变更确定版本类型
- **提交解析**: 解析提交信息提取变更内容
- **变更分类**: 按照功能、修复、破坏性变更分类
- **历史记录**: 完整的版本变更历史

## 配置指南

### 基础配置
```json
{
  "version-manager": {
    "versioning": {
      "scheme": "semver",
      "prefix": "v",
      "auto-increment": true,
      "pre-release-identifier": "alpha"
    },
    "release": {
      "create-tag": true,
      "push-tag": true,
      "create-branch": false,
      "branch-prefix": "release/"
    },
    "changelog": {
      "enabled": true,
      "template": "default",
      "include-commits": true,
      "sort-by": "type"
    }
  }
}
```

### 高级配置
```json
{
  "version-manager": {
    "advanced": {
      "commit-analysis": {
        "patterns": {
          "major": ["BREAKING CHANGE:", "major:"],
          "minor": ["feat:", "feature:"],
          "patch": ["fix:", "patch:"]
        },
        "default-type": "patch",
        "case-sensitive": false
      },
      "branch-strategy": {
        "main": "main",
        "develop": "develop",
        "feature": "feature/*",
        "release": "release/*",
        "hotfix": "hotfix/*"
      },
      "hooks": {
        "pre-release": ["npm test", "npm run build"],
        "post-release": ["npm publish", "git push"],
        "pre-version": ["npm run lint"],
        "post-version": ["git add package.json"]
      }
    }
  }
}
```

## API 参考

### 版本管理器
```python
class VersionManager:
    def __init__(self, config=None):
        self.config = Config(config or {})
        self.version_parser = VersionParser()
        self.git_handler = GitHandler()
        self.changelog_generator = ChangelogGenerator(self.config)
    
    def get_current_version(self):
        """获取当前版本"""
        try:
            # 从 package.json 读取
            if os.path.exists('package.json'):
                with open('package.json', 'r') as f:
                    package_data = json.load(f)
                    return package_data.get('version', '0.0.0')
            
            # 从 Git 标签读取
            tags = self.git_handler.get_tags()
            if tags:
                return self.version_parser.parse(tags[0])
            
            return "0.0.0"
        except Exception as e:
            raise VersionError(f"Failed to get current version: {e}")
    
    def increment_version(self, increment_type='patch'):
        """递增版本号"""
        current_version = self.get_current_version()
        version = self.version_parser.parse(current_version)
        
        if increment_type == 'major':
            version.increment_major()
        elif increment_type == 'minor':
            version.increment_minor()
        elif increment_type == 'patch':
            version.increment_patch()
        else:
            raise ValueError(f"Invalid increment type: {increment_type}")
        
        return str(version)
    
    def determine_increment_type(self, since_version=None):
        """根据变更确定递增类型"""
        if not since_version:
            since_version = self.get_current_version()
        
        commits = self.git_handler.get_commits_since(since_version)
        patterns = self.config.get('advanced.commit-analysis.patterns', {})
        
        increment_type = self.config.get('advanced.commit-analysis.default-type', 'patch')
        
        for commit in commits:
            message = commit['message']
            
            # 检查主要版本变更
            for pattern in patterns.get('major', []):
                if re.search(pattern, message, re.IGNORECASE):
                    return 'major'
            
            # 检查次要版本变更
            for pattern in patterns.get('minor', []):
                if re.search(pattern, message, re.IGNORECASE):
                    increment_type = 'minor'
        
        return increment_type
    
    def release(self, increment_type=None, version=None, dry_run=False):
        """执行发布流程"""
        if not version:
            if increment_type:
                version = self.increment_version(increment_type)
            else:
                increment_type = self.determine_increment_type()
                version = self.increment_version(increment_type)
        
        if dry_run:
            return {
                'version': version,
                'increment_type': increment_type,
                'actions': self._get_release_actions(version)
            }
        
        # 执行发布前钩子
        self._run_hooks('pre-release')
        
        # 更新版本文件
        self._update_version_files(version)
        
        # 生成变更日志
        changelog = self.changelog_generator.generate(since_version=self.get_current_version())
        
        # 创建 Git 标签
        if self.config.get('release.create-tag', True):
            tag_name = f"{self.config.get('versioning.prefix', 'v')}{version}"
            self.git_handler.create_tag(tag_name, changelog)
        
        # 推送标签
        if self.config.get('release.push-tag', True):
            self.git_handler.push_tags()
        
        # 执行发布后钩子
        self._run_hooks('post-release')
        
        return {
            'version': version,
            'increment_type': increment_type,
            'changelog': changelog
        }
```

### 版本解析器
```python
class VersionParser:
    def __init__(self):
        self.semver_pattern = r'^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$'
    
    def parse(self, version_string):
        """解析版本字符串"""
        match = re.match(self.semver_pattern, version_string)
        if not match:
            raise ValueError(f"Invalid version format: {version_string}")
        
        major, minor, patch, prerelease, build = match.groups()
        
        return Version(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            prerelease=prerelease or None,
            build=build or None,
            original=version_string
        )
    
    def compare(self, version1, version2):
        """比较两个版本"""
        v1 = self.parse(version1) if isinstance(version1, str) else version1
        v2 = self.parse(version2) if isinstance(version2, str) else version2
        
        # 比较主版本号
        if v1.major != v2.major:
            return 1 if v1.major > v2.major else -1
        
        # 比较次版本号
        if v1.minor != v2.minor:
            return 1 if v1.minor > v2.minor else -1
        
        # 比较修订版本号
        if v1.patch != v2.patch:
            return 1 if v1.patch > v2.patch else -1
        
        # 比较预发布版本
        if v1.prerelease and v2.prerelease:
            return self._compare_prerelease(v1.prerelease, v2.prerelease)
        elif v1.prerelease and not v2.prerelease:
            return -1
        elif not v1.prerelease and v2.prerelease:
            return 1
        
        return 0
    
    def satisfies(self, version, range_string):
        """检查版本是否满足范围要求"""
        # 解析范围字符串
        ranges = self._parse_range(range_string)
        
        for range_op, range_version in ranges:
            comparison = self.compare(version, range_version)
            
            if range_op == '=':
                if comparison != 0:
                    return False
            elif range_op == '>':
                if comparison <= 0:
                    return False
            elif range_op == '>=':
                if comparison < 0:
                    return False
            elif range_op == '<':
                if comparison >= 0:
                    return False
            elif range_op == '<=':
                if comparison > 0:
                    return False
        
        return True

class Version:
    def __init__(self, major, minor, patch, prerelease=None, build=None, original=None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build
        self.original = original
    
    def increment_major(self):
        """递增主版本号"""
        self.major += 1
        self.minor = 0
        self.patch = 0
        self.prerelease = None
        self.build = None
    
    def increment_minor(self):
        """递增次版本号"""
        self.minor += 1
        self.patch = 0
        self.prerelease = None
        self.build = None
    
    def increment_patch(self):
        """递增修订版本号"""
        self.patch += 1
        self.prerelease = None
        self.build = None
    
    def __str__(self):
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version
```

### Git 处理器
```python
class GitHandler:
    def __init__(self, repo_path='.'):
        self.repo = git.Repo(repo_path)
        self.repo_path = repo_path
    
    def get_tags(self):
        """获取所有标签"""
        try:
            tags = [tag.name for tag in self.repo.tags]
            # 按版本号排序
            tags.sort(key=self._sort_version, reverse=True)
            return tags
        except Exception as e:
            raise GitError(f"Failed to get tags: {e}")
    
    def get_commits_since(self, version):
        """获取指定版本以来的提交"""
        try:
            # 找到版本对应的标签
            tag = self._find_tag_by_version(version)
            if not tag:
                return list(self.repo.iter_commits())
            
            # 获取标签以来的提交
            commits = list(self.repo.iter_commits(f"{tag.name}..HEAD"))
            return [{'message': commit.message, 'hash': commit.hexsha} for commit in commits]
        except Exception as e:
            raise GitError(f"Failed to get commits: {e}")
    
    def create_tag(self, tag_name, message):
        """创建标签"""
        try:
            tag = self.repo.create_tag(tag_name, message=message)
            return tag
        except Exception as e:
            raise GitError(f"Failed to create tag: {e}")
    
    def push_tags(self):
        """推送标签到远程仓库"""
        try:
            origin = self.repo.remotes.origin
            origin.push(tags=True)
        except Exception as e:
            raise GitError(f"Failed to push tags: {e}")
    
    def create_release_branch(self, version):
        """创建发布分支"""
        try:
            branch_name = f"release/{version}"
            branch = self.repo.create_head(branch_name)
            return branch
        except Exception as e:
            raise GitError(f"Failed to create release branch: {e}")
    
    def _find_tag_by_version(self, version):
        """根据版本号查找标签"""
        version_without_prefix = version.lstrip('v')
        for tag in self.repo.tags:
            tag_version = tag.name.lstrip('v')
            if tag_version == version_without_prefix:
                return tag
        return None
    
    def _sort_version(self, version):
        """版本号排序辅助函数"""
        try:
            return tuple(map(int, re.findall(r'\d+', version)))
        except:
            return (0,)
```

## 集成指南

### 命令行工具
```bash
#!/bin/bash
# version-manager.sh

# 版本管理命令
version_show() {
    python -m version_manager show
}

version_increment() {
    local type=$1
    python -m version_manager increment --type $type
}

version_release() {
    local type=$1
    local version=$2
    python -m version_manager release --type $type --version $version
}

version_changelog() {
    python -m version_manager changelog
}

# 主函数
case "$1" in
    "show")
        version_show
        ;;
    "increment")
        version_increment $2
        ;;
    "release")
        version_release $2 $3
        ;;
    "changelog")
        version_changelog
        ;;
    *)
        echo "Usage: version-manager {show|increment|release|changelog}"
        exit 1
        ;;
esac
```

### CI/CD 集成
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
      with:
        fetch-depth: 0
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Determine version increment
      id: version
      run: |
        INCREMENT=$(python -m version_manager determine-increment)
        echo "::set-output name=increment::$INCREMENT"
        echo "::set-output name=version::$(python -m version_manager increment --type $INCREMENT)"
    
    - name: Create Release
      run: |
        python -m version_manager release --type ${{ steps.version.outputs.increment }}
    
    - name: Create GitHub Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: v${{ steps.version.outputs.version }}
        release_name: Release ${{ steps.version.outputs.version }}
        body_path: CHANGELOG.md
        draft: false
        prerelease: false
```

## 最佳实践

### 版本号规范
1. **语义化版本**: 严格遵循 SemVer 规范
2. **版本递增**: 根据变更类型正确递增版本号
3. **预发布版本**: 使用有意义的预发布标识符
4. **版本一致性**: 确保所有地方版本号一致

### 发布流程
1. **自动化**: 尽可能自动化发布流程
2. **测试验证**: 发布前运行完整测试套件
3. **变更日志**: 自动生成详细的变更日志
4. **回滚准备**: 准备快速回滚机制

### 分支策略
1. **主分支**: 保持主分支稳定可发布
2. **开发分支**: 集成新功能和修复
3. **功能分支**: 独立的功能开发分支
4. **发布分支**: 专门的发布准备分支

## 故障排除

### 常见问题
1. **版本冲突**: 解决版本号冲突和不一致
2. **标签问题**: 处理 Git 标签创建和推送问题
3. **权限错误**: 解决仓库访问权限问题
4. **依赖解析**: 处理版本依赖解析错误

### 调试技巧
1. **详细日志**: 启用详细的调试日志
2. **干运行**: 使用干运行模式测试发布流程
3. **版本检查**: 手动验证版本号计算
4. **状态检查**: 检查 Git 仓库状态

## 工具和资源

### 开发工具
- **Git**: 版本控制系统
- **Semantic Release**: 自动化语义化版本发布
- **Standard Version**: 标准化版本发布工具
- **Release It**: 通用版本发布工具

### 相关库
- **semver**: 语义化版本解析库
- **GitPython**: Python Git 操作库
- **conventional-commits**: 约定式提交规范
- **commitizen**: 交互式提交工具

### 学习资源
- [语义化版本规范](https://semver.org/)
- [约定式提交](https://www.conventionalcommits.org/)
- [Git 文档](https://git-scm.com/doc)
- [发布最佳实践](https://releases.com/)

### 社区支持
- [Semantic Release GitHub](https://github.com/semantic-release/semantic-release)
- [Standard Version GitHub](https://github.com/conventional-changelog/standard-version)
- [Git 社区](https://git-scm.com/community)
- [版本管理论坛](https://discussions.github.com/)
