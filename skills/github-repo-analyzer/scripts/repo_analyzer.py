#!/usr/bin/env python3
"""
GitHub仓库分析与环境配置工具

功能：
1. 克隆GitHub仓库
2. 分析仓库结构和文档
3. 理解仓库功能、安装方法和使用方式
4. 自动创建Python虚拟环境
5. 在虚拟环境中安装依赖
6. 生成调用代码
7. 对于Docker部署的仓库，分析Docker配置并创建虚拟环境启动方案
"""

import argparse
import os
import subprocess
import sys
import shutil
import tempfile
import json
from pathlib import Path
import platform
import yaml


class RepoAnalyzer:
    """
    GitHub仓库分析器类
    """
    
    def __init__(self, repo_url, branch=None, output_dir=None):
        """
        初始化RepoAnalyzer
        
        Args:
            repo_url (str): GitHub仓库URL
            branch (str): 分支或标签名称
            output_dir (str): 输出目录
        """
        self.repo_url = repo_url
        self.branch = branch
        self.output_dir = output_dir or Path.cwd() / "repo_analysis"
        self.output_dir = Path(self.output_dir)
        self.repo_dir = self.output_dir / "repo"
        self.venv_dir = self.output_dir / "venv"
        self.analysis_results = {}
        
        # 创建输出目录
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def clone_repo(self):
        """
        克隆GitHub仓库
        
        Returns:
            bool: 是否成功
        """
        print(f"\n=== 步骤1/6: 克隆GitHub仓库 ===")
        print(f"仓库URL: {self.repo_url}")
        
        # 清理已存在的仓库目录
        if self.repo_dir.exists():
            print(f"清理已存在的仓库目录: {self.repo_dir}")
            shutil.rmtree(self.repo_dir)
        
        # 构建git clone命令
        cmd = ["git", "clone"]
        if self.branch:
            cmd.extend(["-b", self.branch])
        cmd.extend([self.repo_url, str(self.repo_dir)])
        
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✓ 仓库克隆成功")
            print(f"克隆到目录: {self.repo_dir}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 仓库克隆失败: {e}")
            print(f"错误输出: {e.stderr}")
            return False
        except Exception as e:
            print(f"✗ 克隆过程中发生错误: {e}")
            return False
    
    def analyze_repo_structure(self):
        """
        分析仓库结构
        
        Returns:
            dict: 仓库结构分析结果
        """
        print(f"\n=== 步骤2/6: 分析仓库结构 ===")
        
        structure = {
            "root_files": [],
            "directories": [],
            "readme_files": [],
            "docs_files": [],
            "examples_files": [],
            "python_files": [],
            "docker_files": [],
            "dependency_files": []
        }
        
        # 遍历仓库目录
        for root, dirs, files in os.walk(self.repo_dir):
            rel_path = Path(root).relative_to(self.repo_dir)
            
            # 分析根目录文件
            if rel_path == Path("."):
                structure["root_files"] = files
                structure["directories"] = dirs
            
            # 分析各个类型的文件
            for file in files:
                file_path = Path(root) / file
                rel_file_path = file_path.relative_to(self.repo_dir)
                
                # README文件
                if file.lower().startswith("readme"):
                    structure["readme_files"].append(str(rel_file_path))
                
                # Python文件
                if file.endswith(".py"):
                    structure["python_files"].append(str(rel_file_path))
                
                # Docker相关文件
                if file.lower() in ["dockerfile", "docker-compose.yml", "docker-compose.yaml"]:
                    structure["docker_files"].append(str(rel_file_path))
                
                # 依赖文件
                if file in ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg"]:
                    structure["dependency_files"].append(str(rel_file_path))
            
            # 分析docs和examples目录
            if rel_path.name.lower() == "docs":
                for file in files:
                    structure["docs_files"].append(str(rel_file_path / file))
            elif rel_path.name.lower() == "examples":
                for file in files:
                    structure["examples_files"].append(str(rel_file_path / file))
        
        # 打印分析结果
        print(f"仓库根目录文件: {', '.join(structure['root_files'])}")
        print(f"仓库目录: {', '.join(structure['directories'])}")
        print(f"README文件: {', '.join(structure['readme_files'])}")
        print(f"依赖文件: {', '.join(structure['dependency_files'])}")
        print(f"Python文件: {len(structure['python_files'])}个")
        print(f"Docker文件: {', '.join(structure['docker_files'])}")
        print(f"文档文件: {len(structure['docs_files'])}个")
        print(f"示例文件: {len(structure['examples_files'])}个")
        
        return structure
    
    def analyze_documentation(self):
        """
        分析仓库文档
        
        Returns:
            dict: 文档分析结果
        """
        print(f"\n=== 步骤3/6: 分析仓库文档 ===")
        
        docs = {
            "readme_content": "",
            "installation_instructions": [],
            "usage_examples": [],
            "dependencies": [],
            "description": ""
        }
        
        # 查找并读取README文件
        readme_files = []
        for file in os.listdir(self.repo_dir):
            if file.lower().startswith("readme"):
                readme_files.append(file)
        
        if readme_files:
            # 优先使用README.md
            readme_file = None
            for f in readme_files:
                if f.lower() == "readme.md":
                    readme_file = f
                    break
            if not readme_file:
                readme_file = readme_files[0]
            
            readme_path = self.repo_dir / readme_file
            print(f"读取README文件: {readme_file}")
            
            try:
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    docs["readme_content"] = content
                    
                    # 提取基本描述
                    lines = content.split('\n')
                    for line in lines[:50]:  # 只分析前50行
                        if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('```'):
                            docs["description"] += line.strip() + ' '
                            if len(docs["description"]) > 500:
                                break
                    docs["description"] = docs["description"].strip()
                    
                    # 提取安装说明
                    if 'install' in content.lower():
                        print("✓ 找到安装说明")
                        # 简单提取包含install的段落
                        lines = content.split('\n')
                        in_install_section = False
                        install_lines = []
                        
                        for line in lines:
                            if any(keyword in line.lower() for keyword in ['## installation', '# installation', 'install', 'setup']):
                                in_install_section = True
                            elif in_install_section and line.startswith('#') and not any(keyword in line.lower() for keyword in ['install', 'setup']):
                                break
                            elif in_install_section:
                                install_lines.append(line)
                        
                        if install_lines:
                            docs["installation_instructions"] = install_lines
                    
                    # 提取使用示例
                    if 'example' in content.lower() or 'usage' in content.lower():
                        print("✓ 找到使用示例")
                        # 简单提取包含example或usage的段落
                        lines = content.split('\n')
                        in_example_section = False
                        example_lines = []
                        
                        for line in lines:
                            if any(keyword in line.lower() for keyword in ['## example', '# example', '## usage', '# usage', 'example', 'usage']):
                                in_example_section = True
                            elif in_example_section and line.startswith('#') and not any(keyword in line.lower() for keyword in ['example', 'usage']):
                                break
                            elif in_example_section:
                                example_lines.append(line)
                        
                        if example_lines:
                            docs["usage_examples"] = example_lines
            except Exception as e:
                print(f"✗ 读取README文件失败: {e}")
        else:
            print("⚠ 未找到README文件")
        
        # 分析依赖文件
        dependency_files = [
            "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg"
        ]
        
        for dep_file in dependency_files:
            dep_path = self.repo_dir / dep_file
            if dep_path.exists():
                print(f"分析依赖文件: {dep_file}")
                try:
                    if dep_file == "requirements.txt":
                        with open(dep_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    docs["dependencies"].append(line)
                    elif dep_file == "pyproject.toml":
                        # 简单解析pyproject.toml
                        with open(dep_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'dependencies' in content:
                                print("✓ 找到依赖配置")
                    elif dep_file == "setup.py":
                        # 简单解析setup.py
                        with open(dep_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'install_requires' in content:
                                print("✓ 找到依赖配置")
                except Exception as e:
                    print(f"✗ 分析依赖文件失败: {e}")
        
        return docs
    
    def analyze_docker_config(self):
        """
        分析Docker配置
        
        Returns:
            dict: Docker配置分析结果
        """
        print(f"\n=== 步骤4/6: 分析Docker配置 ===")
        
        docker_config = {
            "has_docker": False,
            "dockerfile": None,
            "docker_compose": None,
            "environment_variables": [],
            "dependencies": [],
            "command": None
        }
        
        # 查找Dockerfile
        dockerfile_paths = [
            self.repo_dir / "Dockerfile",
            self.repo_dir / "dockerfile"
        ]
        
        for path in dockerfile_paths:
            if path.exists():
                docker_config["has_docker"] = True
                docker_config["dockerfile"] = str(path.relative_to(self.repo_dir))
                print(f"找到Dockerfile: {docker_config['dockerfile']}")
                
                # 分析Dockerfile
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for line in lines:
                            line = line.strip()
                            # 提取环境变量
                            if line.startswith('ENV '):
                                parts = line.split(' ', 1)
                                if len(parts) > 1:
                                    docker_config["environment_variables"].append(parts[1])
                            # 提取依赖安装命令
                            elif any(cmd in line for cmd in ['pip install', 'apt-get install', 'yum install']):
                                docker_config["dependencies"].append(line)
                            # 提取启动命令
                            elif line.startswith('CMD '):
                                docker_config["command"] = line
                except Exception as e:
                    print(f"✗ 分析Dockerfile失败: {e}")
                break
        
        # 查找docker-compose.yml
        docker_compose_paths = [
            self.repo_dir / "docker-compose.yml",
            self.repo_dir / "docker-compose.yaml"
        ]
        
        for path in docker_compose_paths:
            if path.exists():
                docker_config["docker_compose"] = str(path.relative_to(self.repo_dir))
                print(f"找到docker-compose文件: {docker_config['docker_compose']}")
                
                # 分析docker-compose.yml
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        compose_data = yaml.safe_load(f)
                        # 提取服务信息
                        if 'services' in compose_data:
                            print(f"✓ 找到{len(compose_data['services'])}个服务")
                except Exception as e:
                    print(f"✗ 分析docker-compose.yml失败: {e}")
                break
        
        if not docker_config["has_docker"]:
            print("⚠ 未找到Docker配置文件")
        
        return docker_config
    
    def create_venv(self):
        """
        创建Python虚拟环境
        
        Returns:
            bool: 是否成功
        """
        print(f"\n=== 步骤5/6: 创建Python虚拟环境 ===")
        
        # 清理已存在的虚拟环境
        if self.venv_dir.exists():
            print(f"清理已存在的虚拟环境: {self.venv_dir}")
            shutil.rmtree(self.venv_dir)
        
        # 确定Python可执行文件路径
        python_exe = sys.executable
        print(f"使用Python: {python_exe}")
        
        # 构建创建虚拟环境的命令
        cmd = [python_exe, "-m", "venv", str(self.venv_dir)]
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✓ 虚拟环境创建成功")
            print(f"虚拟环境目录: {self.venv_dir}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 虚拟环境创建失败: {e}")
            print(f"错误输出: {e.stderr}")
            return False
        except Exception as e:
            print(f"✗ 创建虚拟环境时发生错误: {e}")
            return False
    
    def install_dependencies(self):
        """
        在虚拟环境中安装依赖
        
        Returns:
            bool: 是否成功
        """
        print(f"\n=== 步骤6/6: 安装依赖 ===")
        
        # 确定pip可执行文件路径
        if platform.system() == "Windows":
            pip_exe = self.venv_dir / "Scripts" / "pip.exe"
        else:
            pip_exe = self.venv_dir / "bin" / "pip"
        
        if not pip_exe.exists():
            print(f"✗ 找不到pip可执行文件: {pip_exe}")
            return False
        
        print(f"使用pip: {pip_exe}")
        
        # 升级pip
        print("升级pip到最新版本...")
        try:
            result = subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], 
                                  check=True, capture_output=True, text=True)
            print(f"✓ pip升级成功")
        except subprocess.CalledProcessError as e:
            print(f"⚠ pip升级失败，但继续安装依赖: {e}")
        
        # 查找依赖文件
        dependency_files = [
            ("requirements.txt", [str(pip_exe), "install", "-r"]),
            ("setup.py", [str(pip_exe), "install", "."]),
            ("pyproject.toml", [str(pip_exe), "install", "."])
        ]
        
        installed = False
        
        for dep_file, install_cmd in dependency_files:
            dep_path = self.repo_dir / dep_file
            if dep_path.exists():
                print(f"安装依赖文件: {dep_file}")
                
                if dep_file == "requirements.txt":
                    install_cmd.append(str(dep_path))
                else:
                    # 对于setup.py和pyproject.toml，在仓库目录中安装
                    install_cmd.append(str(self.repo_dir))
                
                print(f"执行命令: {' '.join(install_cmd)}")
                
                try:
                    result = subprocess.run(install_cmd, 
                                          check=True, capture_output=True, text=True)
                    print(f"✓ 依赖安装成功")
                    installed = True
                    break
                except subprocess.CalledProcessError as e:
                    print(f"✗ 依赖安装失败: {e}")
                    print(f"错误输出: {e.stderr}")
                except Exception as e:
                    print(f"✗ 安装过程中发生错误: {e}")
        
        if not installed:
            print("⚠ 未找到标准依赖文件，尝试检查是否有其他安装方式")
            # 检查是否有setup.cfg
            setup_cfg = self.repo_dir / "setup.cfg"
            if setup_cfg.exists():
                print("找到setup.cfg，尝试安装...")
                install_cmd = [str(pip_exe), "install", str(self.repo_dir)]
                try:
                    result = subprocess.run(install_cmd, 
                                          check=True, capture_output=True, text=True)
                    print(f"✓ 依赖安装成功")
                    installed = True
                except Exception as e:
                    print(f"✗ 安装失败: {e}")
        
        return installed
    
    def generate_usage_code(self, repo_info):
        """
        生成调用代码
        
        Args:
            repo_info (dict): 仓库信息
            
        Returns:
            str: 生成的调用代码
        """
        print(f"\n=== 生成调用代码 ===")
        
        # 生成基本的调用代码
        code = """
# 仓库调用示例
# 生成时间: $(date)

"""
        
        # 根据仓库类型生成不同的调用代码
        if repo_info.get("description"):
            code += f"""
# 仓库描述
# {repo_info['description']}

"""
        
        # 添加安装说明
        code += f"""
# 安装说明
# 1. 已创建虚拟环境: {self.venv_dir}
# 2. 已安装依赖

"""
        
        # 添加激活虚拟环境的命令
        if platform.system() == "Windows":
            activate_cmd = f"{self.venv_dir}/Scripts/activate"
        else:
            activate_cmd = f"source {self.venv_dir}/bin/activate"
        
        code += f"""
# 激活虚拟环境
# {activate_cmd}

"""
        
        # 尝试识别主要模块
        python_files = repo_info.get("structure", {}).get("python_files", [])
        main_modules = []
        
        for file in python_files:
            if any(keyword in file.lower() for keyword in ["main", "cli", "app", "run"]):
                main_modules.append(file)
        
        if main_modules:
            code += "# 主要模块\n"
            for module in main_modules[:3]:  # 只显示前3个
                code += f"# - {module}\n"
            code += "\n"
        
        # 生成简单的调用示例
        code += """
# 调用示例
# 根据仓库实际情况修改以下代码

"""
        
        # 保存调用代码到文件
        code_file = self.output_dir / "usage_example.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"✓ 调用代码生成成功: {code_file}")
        return code
    
    def generate_analysis_report(self):
        """
        生成分析报告
        
        Returns:
            dict: 完整的分析报告
        """
        print(f"\n=== 生成分析报告 ===")
        
        # 分析仓库结构
        structure = self.analyze_repo_structure()
        
        # 分析文档
        docs = self.analyze_documentation()
        
        # 分析Docker配置
        docker_config = self.analyze_docker_config()
        
        # 生成报告
        report = {
            "repo_url": self.repo_url,
            "repo_dir": str(self.repo_dir),
            "venv_dir": str(self.venv_dir),
            "structure": structure,
            "documentation": docs,
            "docker_config": docker_config,
            "summary": {
                "has_readme": len(structure["readme_files"]) > 0,
                "has_docs": len(structure["docs_files"]) > 0,
                "has_examples": len(structure["examples_files"]) > 0,
                "has_python_files": len(structure["python_files"]) > 0,
                "has_docker": docker_config["has_docker"],
                "has_dependencies": len(structure["dependency_files"]) > 0
            }
        }
        
        # 保存报告到文件
        report_file = self.output_dir / "analysis_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        report_md_file = self.output_dir / "analysis_report.md"
        self._generate_markdown_report(report, report_md_file)
        
        print(f"✓ 分析报告生成成功")
        print(f"JSON报告: {report_file}")
        print(f"Markdown报告: {report_md_file}")
        
        return report
    
    def _generate_markdown_report(self, report, output_file):
        """
        生成Markdown格式的分析报告
        
        Args:
            report (dict): 分析报告
            output_file (Path): 输出文件路径
        """
        md_content = f"""
# GitHub仓库分析报告

## 基本信息

- **仓库URL**: {report['repo_url']}
- **克隆目录**: {report['repo_dir']}
- **虚拟环境目录**: {report['venv_dir']}

## 仓库结构

### 根目录文件
{', '.join(report['structure']['root_files']) if report['structure']['root_files'] else '无'}

### 目录
{', '.join(report['structure']['directories']) if report['structure']['directories'] else '无'}

### README文件
{', '.join(report['structure']['readme_files']) if report['structure']['readme_files'] else '无'}

### 文档文件
{len(report['structure']['docs_files'])}个文件

### 示例文件
{len(report['structure']['examples_files'])}个文件

### Python文件
{len(report['structure']['python_files'])}个文件

### Docker文件
{', '.join(report['structure']['docker_files']) if report['structure']['docker_files'] else '无'}

### 依赖文件
{', '.join(report['structure']['dependency_files']) if report['structure']['dependency_files'] else '无'}

## 仓库描述

{report['documentation']['description'] if report['documentation']['description'] else '无'}

## 安装说明

{''.join(report['documentation']['installation_instructions']) if report['documentation']['installation_instructions'] else '无'}

## 使用示例

{''.join(report['documentation']['usage_examples']) if report['documentation']['usage_examples'] else '无'}

## 依赖

{', '.join(report['documentation']['dependencies']) if report['documentation']['dependencies'] else '无'}

## Docker配置

### 是否使用Docker
{'是' if report['docker_config']['has_docker'] else '否'}

### Dockerfile
{report['docker_config']['dockerfile'] if report['docker_config']['dockerfile'] else '无'}

### Docker Compose
{report['docker_config']['docker_compose'] if report['docker_config']['docker_compose'] else '无'}

### 环境变量
{', '.join(report['docker_config']['environment_variables']) if report['docker_config']['environment_variables'] else '无'}

### 启动命令
{report['docker_config']['command'] if report['docker_config']['command'] else '无'}

## 总结

- **README文件**: {'✓' if report['summary']['has_readme'] else '✗'}
- **文档目录**: {'✓' if report['summary']['has_docs'] else '✗'}
- **示例目录**: {'✓' if report['summary']['has_examples'] else '✗'}
- **Python文件**: {'✓' if report['summary']['has_python_files'] else '✗'}
- **Docker配置**: {'✓' if report['summary']['has_docker'] else '✗'}
- **依赖文件**: {'✓' if report['summary']['has_dependencies'] else '✗'}

## 使用指南

1. **激活虚拟环境**
   - Windows: `{report['venv_dir']}/Scripts/activate`
   - macOS/Linux: `source {report['venv_dir']}/bin/activate`

2. **运行应用**
   - 根据仓库实际情况运行

3. **查看生成的示例代码**
   - `{self.output_dir}/usage_example.py`
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def analyze(self):
        """
        完整的分析流程
        
        Returns:
            dict: 分析结果
        """
        print(f"开始分析GitHub仓库: {self.repo_url}")
        
        # 1. 克隆仓库
        if not self.clone_repo():
            return {"success": False, "error": "仓库克隆失败"}
        
        # 2. 分析仓库结构
        structure = self.analyze_repo_structure()
        
        # 3. 分析文档
        docs = self.analyze_documentation()
        
        # 4. 分析Docker配置
        docker_config = self.analyze_docker_config()
        
        # 5. 创建虚拟环境
        if not self.create_venv():
            print("⚠ 虚拟环境创建失败，但继续分析")
        
        # 6. 安装依赖
        if not self.install_dependencies():
            print("⚠ 依赖安装失败，但继续分析")
        
        # 7. 生成分析报告
        report = self.generate_analysis_report()
        
        # 8. 生成调用代码
        self.generate_usage_code({"structure": structure, "description": docs.get("description", "")})
        
        print(f"\n🎉 分析完成！")
        print(f"分析结果保存在: {self.output_dir}")
        
        return {"success": True, "report": report, "output_dir": str(self.output_dir)}


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='GitHub仓库分析与环境配置工具')
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # analyze命令
    analyze_parser = subparsers.add_parser('analyze', help='分析GitHub仓库')
    analyze_parser.add_argument('--repo', required=True, help='GitHub仓库URL')
    analyze_parser.add_argument('--branch', help='分支或标签名称')
    analyze_parser.add_argument('--output', help='输出目录')
    
    # 解析参数
    args = parser.parse_args()
    
    if args.command == 'analyze':
        analyzer = RepoAnalyzer(
            repo_url=args.repo,
            branch=args.branch,
            output_dir=args.output
        )
        result = analyzer.analyze()
        
        if result['success']:
            print(f"\n✓ 分析成功！")
            print(f"输出目录: {result['output_dir']}")
            sys.exit(0)
        else:
            print(f"\n✗ 分析失败: {result.get('error', '未知错误')}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
