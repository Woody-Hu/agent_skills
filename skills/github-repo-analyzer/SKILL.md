---
name: github-repo-analyzer
description: GitHub仓库分析与环境配置工具，支持克隆仓库、分析文档、创建虚拟环境、安装依赖和生成调用代码。
---

# GitHub仓库分析与环境配置工具

## 概述

GitHub仓库分析与环境配置工具是一个功能强大的Python脚本，用于自动化分析GitHub仓库并为其创建合适的开发环境。该工具可以：

- 克隆GitHub仓库到本地
- 分析仓库结构和文档（README、examples、docs等）
- 理解仓库功能、安装方法和使用方式
- 自动创建Python虚拟环境
- 在虚拟环境中安装依赖
- 生成调用代码
- 对于Docker部署的仓库，分析Docker配置并创建虚拟环境启动方案

## 功能特性

### 核心功能

- **仓库克隆**: 支持HTTP和SSH两种克隆方式，支持指定分支和标签
- **结构分析**: 自动分析仓库目录结构，识别关键文件和目录
- **文档分析**: 智能解析README、examples和docs目录，提取安装说明和使用示例
- **环境配置**: 自动创建隔离的Python虚拟环境
- **依赖管理**: 智能识别和安装依赖文件（requirements.txt、pyproject.toml、setup.py等）
- **代码生成**: 根据仓库分析结果生成调用代码示例
- **Docker分析**: 解析Dockerfile和docker-compose.yml，提取环境变量和依赖要求
- **报告生成**: 生成详细的JSON和Markdown格式分析报告

### 便捷特性

- **跨平台支持**: 支持Windows、macOS和Linux
- **错误处理**: 完善的错误处理和重试机制
- **详细日志**: 清晰的执行过程和结果输出
- **灵活配置**: 支持自定义输出目录和分支选择
- **智能推导**: 自动识别主要模块和入口点

## 快速开始

### 基本用法

```bash
# 1. 进入skill目录
cd skills/github-repo-analyzer

# 2. 分析GitHub仓库
python scripts/repo_analyzer.py analyze --repo <github-repo-url>
```

### 高级选项

```bash
# 指定分支
python scripts/repo_analyzer.py analyze --repo <url> --branch <branch-name>

# 指定输出目录
python scripts/repo_analyzer.py analyze --repo <url> --output <output-directory>

# 查看帮助
python scripts/repo_analyzer.py --help
```

## 命令行接口

### 分析命令

```
Usage: repo_analyzer.py analyze [OPTIONS]

  分析GitHub仓库

Options:
  --repo TEXT     GitHub仓库URL
  --branch TEXT   分支或标签名称
  --output TEXT   输出目录
  --help          Show this message and exit.
```

## 分析流程

工具会按照以下步骤执行分析：

1. **克隆仓库**: 将GitHub仓库克隆到本地目录
2. **结构分析**: 分析仓库目录结构，识别关键文件
3. **文档分析**: 解析README、examples和docs目录
4. **Docker分析**: 解析Docker配置文件（如果存在）
5. **创建虚拟环境**: 创建隔离的Python虚拟环境
6. **安装依赖**: 在虚拟环境中安装仓库依赖
7. **生成报告**: 生成详细的分析报告
8. **生成代码**: 生成调用代码示例

## 输出结果

分析完成后，工具会在输出目录中生成以下文件：

- **analysis_report.json**: 详细的JSON格式分析报告
- **analysis_report.md**: 美观的Markdown格式分析报告
- **usage_example.py**: 生成的调用代码示例
- **repo/**: 克隆的仓库代码
- **venv/**: 创建的Python虚拟环境

## 报告内容

分析报告包含以下内容：

### 基本信息
- 仓库URL
- 克隆目录
- 虚拟环境目录

### 仓库结构
- 根目录文件
- 目录列表
- README文件
- 文档文件
- 示例文件
- Python文件
- Docker文件
- 依赖文件

### 仓库描述
- 从README中提取的仓库描述

### 安装说明
- 从README中提取的安装步骤

### 使用示例
- 从README和examples目录中提取的使用示例

### 依赖
- 从依赖文件中提取的依赖包列表

### Docker配置
- 是否使用Docker
- Dockerfile路径
- docker-compose文件路径
- 环境变量
- 启动命令

### 总结
- 各项分析结果的汇总

### 使用指南
- 如何激活虚拟环境
- 如何运行应用
- 如何使用生成的示例代码

## 支持的仓库类型

工具支持分析以下类型的GitHub仓库：

- **Python包**: 包含setup.py、pyproject.toml或requirements.txt的Python项目
- **Web应用**: Flask、Django等Web框架项目
- **命令行工具**: 包含CLI入口的Python项目
- **Docker项目**: 使用Dockerfile或docker-compose.yml的项目
- **文档驱动项目**: 包含详细README和文档的项目

## 故障排除

### 常见问题

1. **仓库克隆失败**
   - 检查网络连接
   - 检查GitHub仓库URL是否正确
   - 检查是否有足够的权限访问仓库

2. **虚拟环境创建失败**
   - 检查Python是否正确安装
   - 检查是否有足够的权限创建目录

3. **依赖安装失败**
   - 检查网络连接
   - 检查依赖文件是否存在且格式正确
   - 尝试手动安装依赖以获取详细错误信息

4. **Docker分析失败**
   - 检查Docker配置文件是否存在且格式正确
   - 注意：即使Docker分析失败，工具仍会继续创建虚拟环境

### 日志查看

工具会在执行过程中输出详细的日志信息，帮助您诊断问题。如果需要更详细的信息，可以查看生成的分析报告。

## 依赖关系

### 系统依赖

- **Python 3.8+**: 脚本运行环境
- **Git**: 用于克隆GitHub仓库
- **pip**: 用于安装依赖

### Python依赖

- **argparse**: 命令行参数解析
- **yaml**: 解析Docker Compose文件
- **json**: 生成JSON格式报告
- **pathlib**: 文件路径处理
- **subprocess**: 运行外部命令
- **platform**: 跨平台支持
- **shutil**: 文件和目录操作

## 最佳实践

1. **使用指定分支**: 对于稳定版本，建议指定具体的分支或标签
2. **合理设置输出目录**: 避免使用系统关键目录作为输出目录
3. **定期更新工具**: 保持工具为最新版本以获得最佳分析效果
4. **查看分析报告**: 详细阅读生成的分析报告以了解仓库结构和功能
5. **使用虚拟环境**: 始终通过生成的虚拟环境运行应用，避免依赖冲突

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 版本历史

### v1.0.0
- 初始版本
- 支持仓库克隆和结构分析
- 支持虚拟环境创建和依赖安装
- 支持Docker配置分析
- 支持生成分析报告和调用代码

## 联系信息

如有问题或建议，请提交Issue或联系维护者。