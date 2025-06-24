# MindSpore Downloader

这是一个用于下载 MindSpore whl 包的工具，现在使用 pypdl 库提供更强大的下载功能。

## 特性

- ✨ 使用 pypdl 进行多线程分段下载，大幅提升下载速度
- 🔄 自动重试机制，确保下载成功
- 📊 实时进度显示和下载速度统计
- 🎯 支持按 Python 版本过滤下载
- 📁 自动组织文件结构
- 🛡️ ETag 校验确保文件完整性
- 🔒 自动禁用 SSL 验证，确保网络兼容性
- 🌐 支持 Linux 标准代理环境变量

## 环境要求

- Python 3.12+
- uv (包管理工具)

## 安装

使用 uv 安装依赖：

```bash
uv sync
```

## 使用方法

### 基本使用

```bash
uv run python ms_downloader/ms_downloader.py --start_date 20241201 --end_date 20241202
```

### 高级选项

```bash
uv run python ms_downloader/ms_downloader.py \
  --start_date 20241201 \
  --end_date 20241205 \
  --download_dir downloads \
  --num_process 5 \
  --python_version cp311
```

### 参数说明

- `--start_date`: 起始日期，格式为 YYYYMMDD
- `--end_date`: 结束日期，格式为 YYYYMMDD  
- `--download_dir`: 下载目录，默认为 `downloads`
- `--num_process`: 并行下载数，默认为 3
- `--python_version`: 指定 Python 版本（如 cp39, cp310, cp311），默认下载所有版本

## 文件结构

下载的文件将按以下结构组织：

```text
downloads/
├── 20241201/
│   ├── master_20241201010138_xxx_newest/
│   │   └── mindspore-xxx.whl
│   └── master_20241201160016_xxx_newest/
│       └── mindspore-xxx.whl
└── 20241202/
    └── master_20241202010018_xxx_newest/
        └── mindspore-xxx.whl
```

## 技术栈

- **pypdl**: 高性能多线程下载库
- **requests**: HTTP 请求处理
- **BeautifulSoup4**: HTML 解析
- **rich**: 美观的命令行界面
- **uv**: 现代 Python 包管理

## 性能优化

- 使用 pypdl 的多段下载技术
- 优化的并发控制
- 智能重试机制
- 缓存和校验机制
- 禁用 SSL 验证以提高网络兼容性

## 代理支持

本工具完全支持 Linux 标准代理环境变量：

```bash
# 设置 HTTP 代理
export HTTP_PROXY=http://proxy.company.com:8080
export http_proxy=http://proxy.company.com:8080

# 设置 HTTPS 代理
export HTTPS_PROXY=http://proxy.company.com:8080
export https_proxy=http://proxy.company.com:8080

# 设置通用代理（如果未设置具体协议代理）
export ALL_PROXY=http://proxy.company.com:8080
export all_proxy=http://proxy.company.com:8080

# 设置不使用代理的地址
export NO_PROXY=localhost,127.0.0.1,.local
export no_proxy=localhost,127.0.0.1,.local
```

工具会自动检测并使用这些环境变量中的代理设置。

## 安全说明

本工具默认禁用了 SSL 证书验证（`ssl=False`），这是为了确保在各种网络环境下都能正常工作。如果您需要启用 SSL 验证，请修改代码中的 `ssl` 参数为 `True`。
