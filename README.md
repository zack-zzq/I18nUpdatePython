# Minecraft模组汉化包更新器 (i18n-updater-cn)

[![PyPI version](https://img.shields.io/pypi/v/i18n-updater-cn.svg)](https://pypi.org/project/i18n-updater-cn/)
[![Python Version](https://img.shields.io/pypi/pyversions/i18n-updater-cn.svg)](https://pypi.org/project/i18n-updater-cn/)
[![Tests](https://github.com/kressety/I18nUpdatePython/actions/workflows/test.yml/badge.svg)](https://github.com/kressety/I18nUpdatePython/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/kressety/I18nUpdatePython)](LICENSE)

这个 Python 软件包是 [I18nUpdateMod](https://github.com/CFPAOrg/I18nUpdateMod3) 的 Python 实现版本，用于自动下载、合并和转换由 [CFPAOrg 团队](http://cfpa.team/) 维护的 Minecraft 模组汉化包。

汉化资源包使用 [Minecraft Mod Language Package](https://github.com/CFPAOrg/Minecraft-Mod-Language-Package) 项目中的文件，适用于各种 Minecraft 版本。

## 安装

使用 pip 安装:

```bash
pip install i18n-updater-cn
```

或使用 uv:

```bash
uv pip install i18n-updater-cn
```

## 使用方法

### 命令行使用

基本用法（下载到当前目录）:

```bash
i18n-updater-cn 1.20.4
```

指定 Mod 加载器:

```bash
i18n-updater-cn 1.18.2 --loader Fabric
```

指定输出目录:

```bash
i18n-updater-cn 1.16.5 --output D:/Downloads
```

启用调试模式:

```bash
i18n-updater-cn 1.20.4 --debug
```

查看完整帮助:

```bash
i18n-updater-cn --help
```

### 作为 Python 库使用

```python
from i18n_updater_cn import download_or_convert_language_pack

# 下载并转换汉化包
result = download_or_convert_language_pack(
    minecraft_version="1.20.4",
    loader="Forge",
    output_dir="D:/Downloads",
    debug=True,
)

# 检查结果
if result["success"]:
    print(f"汉化包已保存到: {result['output_file']}")
else:
    print(f"下载失败: {result['error']}")
```

## 支持的版本

- **Minecraft**: 1.6.1 ~ 1.21.10 所有版本
- **Mod 加载器**: Forge、NeoForge、Fabric、Quilt
- **Python**: 3.10 及以上版本

## 核心特性

- **镜像竞速**: 并行测试多个下载源，自动选择最快的镜像
- **GitHub Release 支持**: 支持从 GitHub Release 直接下载资源包
- **增量更新**: MD5 校验 + 24 小时更新检查间隔，避免重复下载
- **跨版本合并**: 自动合并近邻版本的翻译包，最大化翻译覆盖
- **缓存共享**: 临时目录与游戏目录双向同步，支持多实例共享

## 开发

```bash
# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest tests/ -v
```

## 相关项目

- [I18nUpdateMod3](https://github.com/CFPAOrg/I18nUpdateMod3) - 本项目的 Java 版本原型
- [Minecraft-Mod-Language-Package](https://github.com/CFPAOrg/Minecraft-Mod-Language-Package) - 中文汉化资源包项目