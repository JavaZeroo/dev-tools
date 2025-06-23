# Dev Tools

一个基于 Python 的开发工具集合，提供各种实用的开发和运维工具。

## 🚀 特性

- 📦 使用 `uv` 进行现代化的 Python 包管理
- ⚡ 高性能工具实现，支持并发和异步操作
- 🛠️ 模块化设计，工具可独立使用
- 📊 丰富的日志和进度显示
- 🔧 VS Code 集成，提供任务配置

## 📋 环境要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (推荐的 Python 包管理器)

## 🛠️ 安装

### 1. 克隆仓库

```bash
git clone https://github.com/JavaZeroo/dev-tools.git
cd dev-tools
```

### 2. 使用 uv 安装依赖

```bash
uv sync
```

这将自动创建虚拟环境并安装所有必要的依赖。

### 3. 验证安装

```bash
uv run python -c "import requests, pypdl; print('✅ 依赖安装成功')"
```

## 📁 工具列表

### 🔗 MindSpore Downloader

用于批量下载 MindSpore wheel 包的高性能下载工具。

- **位置**: `ms_downloader/`
- **主要特性**:
  - 🚀 基于 pypdl 的多线程分段下载
  - 📊 实时进度显示和速度统计
  - 🔄 智能重试机制
  - 🎯 支持按 Python 版本过滤
  - 📁 自动文件组织

**快速使用**:

```bash
uv run python ms_downloader/ms_downloader.py --start_date 20241201 --end_date 20241202
```

详细文档请参见: [ms_downloader/README.md](ms_downloader/README.md)

*更多工具正在开发中...*

---

## 🤝 贡献指南

欢迎贡献新的工具或改进现有工具！

### 添加新工具

1. 在项目根目录创建新的工具目录
2. 实现你的工具功能
3. 添加工具的 README.md
4. 更新主 README.md 的工具列表
5. 可选：添加 VS Code 任务配置

### 开发规范

- 使用 `uv` 管理依赖
- 遵循 Python PEP 8 代码规范
- 提供清晰的日志输出
- 包含错误处理和重试机制
- 添加适当的文档和示例

## 📄 许可证

[MIT License](LICENSE)

## 🐛 问题反馈

如果遇到问题或有功能建议，请提交 [Issue](../../issues)。

---

⭐ 如果这个项目对你有帮助，请给它一个 Star！
