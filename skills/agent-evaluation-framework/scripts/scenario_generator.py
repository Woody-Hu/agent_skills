import json
import os
import argparse
from typing import Dict, Any, List
import re

# 尝试导入 spaCy 作为小模型辅助
spacy_available = False
try:
    import spacy
    spacy_available = True
    # 加载中文小模型
    nlp = spacy.load("zh_core_web_sm")
except ImportError:
    print("spaCy 未安装，使用规则引擎进行场景信息提取")

class ScenarioGenerator:
    """智能场景生成器"""
    
    def __init__(self, config_dir="config", scripts_dir="generated_scripts"):
        """
        初始化场景生成器
        
        Args:
            config_dir: 配置文件目录
            scripts_dir: 评估脚本目录
        """
        self.config_dir = config_dir
        self.scripts_dir = scripts_dir
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
    
    def generate_config(self, scenario_name: str, scenario_description: str, 
                        core_functions: List[str], performance_requirements: List[str],
                        technical_constraints: List[str]) -> str:
        """
        生成场景配置文件
        
        Args:
            scenario_name: 场景名称
            scenario_description: 场景描述
            core_functions: 核心功能列表
            performance_requirements: 性能要求列表
            technical_constraints: 技术约束列表
            
        Returns:
            配置文件路径
        """
        # 基于场景复杂度设置模型调用次数
        complexity_level = self._estimate_complexity(core_functions, performance_requirements)
        
        # 根据复杂度调整模型调用次数
        model_calls_config = self._get_model_calls_config(complexity_level)
        
        config = {
            "scene": scenario_name,
            "description": scenario_description,
            "core_functions": core_functions,
            "performance_requirements": performance_requirements,
            "technical_constraints": technical_constraints,
            "complexity_level": complexity_level,
            "model_calls": model_calls_config,
            "execution": {
                "iterations": 5,
                "concurrency": 1,
                "timeout": 30
            },
            "metrics": {
                "model_calls_weight": 0.3,
                "execution_time_weight": 0.4,
                "token_usage_weight": 0.3
            }
        }
        
        # 生成配置文件路径
        config_file = os.path.join(self.config_dir, f"{scenario_name}_config.json")
        
        # 保存配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return config_file
    
    def generate_evaluator_script(self, scenario_name: str, scenario_description: str,
                                 core_functions: List[str], technical_constraints: List[str]) -> str:
        """
        生成评估脚本
        
        Args:
            scenario_name: 场景名称
            scenario_description: 场景描述
            core_functions: 核心功能列表
            technical_constraints: 技术约束列表
            
        Returns:
            脚本文件路径
        """
        # 生成工具函数代码
        tools_code = self._generate_tools_code(core_functions)
        
        # 生成测试用例
        test_cases = self._generate_test_cases(core_functions)
        
        # 生成评估脚本模板
        script_template = '''
import time
import json
import random
import os
from typing import Dict, Any
from langchain.agents import create_agent
from langchain.tools import tool

class {0}Evaluator:
    """{1}评估器"""

    def __init__(self, config_file=None):
        self.results = {{}}
        self.config = self._load_config(config_file)

    def _load_config(self, config_file):
        """加载评估配置文件"""
        default_config = {{
            "model_calls": {{
                "direct_tool": {{
                    "simple": 1,
                    "medium": 2,
                    "complex": 3
                }},
                "mcp": {{
                    "simple": 1,
                    "medium": 2,
                    "complex": 4
                }},
                "skill": {{
                    "simple": 1,
                    "medium": 3,
                    "complex": 5
                }}
            }},
            "execution": {{
                "iterations": 5,
                "concurrency": 1,
                "timeout": 30
            }}
        }}

        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_config

    def _generate_tools(self):
        """生成场景所需的工具"""
        tools = []

        {2}

        return tools

    def _get_task_complexity(self, task):
        """根据任务内容判断复杂度"""
        task = task.lower()
        if any(keyword in task for keyword in ["复杂", "推荐", "分析", "多步", "详细", "综合", "评估"]):
            return "complex"
        elif any(keyword in task for keyword in ["查询", "获取", "简单", "基础"]):
            return "simple"
        else:
            return "medium"

    def evaluate_direct_tool(self, task: str, iterations: int = None) -> Dict[str, Any]:
        """评估直接Tool方案"""
        tools = self._generate_tools()
        iterations = iterations or self.config["execution"]["iterations"]

        # 模拟执行或真实执行
        total_time = 0
        model_calls = 0

        # 获取任务复杂度
        complexity = self._get_task_complexity(task)
        # 从配置获取模型调用次数
        calls_per_iteration = self.config["model_calls"]["direct_tool"][complexity]

        for i in range(iterations):
            # 模拟执行
            exec_time = random.uniform(0.5, 0.8)
            total_time += exec_time
            model_calls += calls_per_iteration
            time.sleep(0.1)  # 避免执行过快

        return {{
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": total_time / iterations,
            "iterations": iterations,
            "complexity": complexity,
            "calls_per_iteration": calls_per_iteration
        }}

    def evaluate_mcp(self, task: str, iterations: int = None) -> Dict[str, Any]:
        """评估MCP方案"""
        iterations = iterations or self.config["execution"]["iterations"]

        total_time = 0
        model_calls = 0

        # 获取任务复杂度
        complexity = self._get_task_complexity(task)
        # 从配置获取模型调用次数
        calls_per_iteration = self.config["model_calls"]["mcp"][complexity]

        for i in range(iterations):
            # 模拟执行
            exec_time = random.uniform(0.4, 0.7)
            total_time += exec_time
            model_calls += calls_per_iteration
            time.sleep(0.1)

        return {{
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": total_time / iterations,
            "iterations": iterations,
            "complexity": complexity,
            "calls_per_iteration": calls_per_iteration
        }}

    def evaluate_skill(self, task: str, iterations: int = None) -> Dict[str, Any]:
        """评估Skill方案"""
        iterations = iterations or self.config["execution"]["iterations"]

        total_time = 0
        model_calls = 0

        # 获取任务复杂度
        complexity = self._get_task_complexity(task)
        # 从配置获取模型调用次数
        calls_per_iteration = self.config["model_calls"]["skill"][complexity]

        for i in range(iterations):
            # 模拟执行
            exec_time = random.uniform(0.6, 0.9)
            total_time += exec_time
            model_calls += calls_per_iteration
            time.sleep(0.1)

        return {{
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": total_time / iterations,
            "iterations": iterations,
            "complexity": complexity,
            "calls_per_iteration": calls_per_iteration
        }}

    def run_evaluation(self, test_cases):
        """运行完整评估"""
        results = {{}}

        for test_case in test_cases:
            task = test_case.get("input", "")

            print(f"执行测试用例: {{test_case.get('name', '默认测试')}}")
            print(f"输入: {{task}}")

            # 评估三种方案
            direct_tool_result = self.evaluate_direct_tool(task)
            mcp_result = self.evaluate_mcp(task)
            skill_result = self.evaluate_skill(task)

            results[test_case.get('name', 'default')] = {{
                "direct_tool": direct_tool_result,
                "mcp": mcp_result,
                "skill": skill_result
            }}

        # 汇总结果
        summary = {{
            "direct_tool": {{
                "model_calls": sum(r["direct_tool"]["model_calls"] for r in results.values()),
                "total_time": sum(r["direct_tool"]["total_time"] for r in results.values()),
                "average_time": sum(r["direct_tool"]["average_time"] for r in results.values()) / len(results)
            }},
            "mcp": {{
                "model_calls": sum(r["mcp"]["model_calls"] for r in results.values()),
                "total_time": sum(r["mcp"]["total_time"] for r in results.values()),
                "average_time": sum(r["mcp"]["average_time"] for r in results.values()) / len(results)
            }},
            "skill": {{
                "model_calls": sum(r["skill"]["model_calls"] for r in results.values()),
                "total_time": sum(r["skill"]["total_time"] for r in results.values()),
                "average_time": sum(r["skill"]["average_time"] for r in results.values()) / len(results)
            }}
        }}

        return summary

if __name__ == "__main__":
    # 加载配置文件（如果存在）
    import sys
    config_file = None
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = os.path.join("config", "{3}_config.json")

    evaluator = {0}Evaluator(config_file)

    # 测试用例
    test_cases = {4}

    # 运行评估
    results = evaluator.run_evaluation(test_cases)
    print(json.dumps(results, ensure_ascii=False, indent=2))
'''.format(
            scenario_name.capitalize().replace('_', ''),
            scenario_name,
            tools_code,
            scenario_name,
            test_cases
        )

        # 生成脚本文件路径
        script_file = os.path.join(self.scripts_dir, "{0}_evaluator.py".format(scenario_name))

        # 保存脚本文件
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_template)

        return script_file
    
    def _estimate_complexity(self, core_functions: List[str], performance_requirements: List[str]) -> str:
        """
        估算场景复杂度
        
        Args:
            core_functions: 核心功能列表
            performance_requirements: 性能要求列表
            
        Returns:
            复杂度级别: simple, medium, complex
        """
        complexity_score = 0
        
        # 基于功能数量和复杂度
        complexity_score += len(core_functions)
        
        # 基于功能复杂度
        for func in core_functions:
            if any(keyword in func.lower() for keyword in ["复杂", "推荐", "分析", "多步", "详细", "综合", "评估"]):
                complexity_score += 2
            elif any(keyword in func.lower() for keyword in ["查询", "获取", "简单", "基础"]):
                complexity_score += 0.5
            else:
                complexity_score += 1
        
        # 基于性能要求复杂度
        for req in performance_requirements:
            if any(keyword in req.lower() for keyword in ["并发", "实时", "毫秒", "高吞吐量", "低延迟"]):
                complexity_score += 2
            elif any(keyword in req.lower() for keyword in ["秒", "响应时间", "稳定"]):
                complexity_score += 1
        
        if complexity_score >= 10:
            return "complex"
        elif complexity_score >= 5:
            return "medium"
        else:
            return "simple"
    
    def _get_model_calls_config(self, complexity_level: str) -> Dict[str, Dict[str, int]]:
        """
        根据复杂度级别获取模型调用次数配置
        
        Args:
            complexity_level: 复杂度级别
            
        Returns:
            模型调用次数配置
        """
        base_config = {
            "direct_tool": {
                "simple": 1,
                "medium": 2,
                "complex": 3
            },
            "mcp": {
                "simple": 1,
                "medium": 2,
                "complex": 4
            },
            "skill": {
                "simple": 1,
                "medium": 3,
                "complex": 5
            }
        }
        
        # 根据复杂度级别调整配置
        if complexity_level == "complex":
            return {
                "direct_tool": {
                    "simple": 1,
                    "medium": 3,
                    "complex": 5
                },
                "mcp": {
                    "simple": 1,
                    "medium": 3,
                    "complex": 6
                },
                "skill": {
                    "simple": 1,
                    "medium": 4,
                    "complex": 8
                }
            }
        elif complexity_level == "medium":
            return {
                "direct_tool": {
                    "simple": 1,
                    "medium": 2,
                    "complex": 4
                },
                "mcp": {
                    "simple": 1,
                    "medium": 2,
                    "complex": 5
                },
                "skill": {
                    "simple": 1,
                    "medium": 3,
                    "complex": 6
                }
            }
        else:
            return base_config
    
    def _generate_tools_code(self, core_functions: List[str]) -> str:
        """
        生成工具函数代码
        
        Args:
            core_functions: 核心功能列表
            
        Returns:
            工具函数代码
        """
        tools_code = []
        
        for i, func in enumerate(core_functions[:5]):  # 最多生成5个工具
            # 生成工具名称
            tool_name = f"tool_{i+1}"
            
            # 生成工具描述
            tool_description = func
            
            # 生成参数名称
            param_name = "parameter"
            if "查询" in func or "获取" in func:
                param_name = "query"
            elif "分析" in func or "评估" in func:
                param_name = "data"
            elif "推荐" in func:
                param_name = "user_preferences"
            
            # 生成工具实现
            tool_implementation = f"return f\"{{tool_description}} 执行结果\""
            if "查询" in func or "获取" in func:
                tool_implementation = f"return f\"查询结果: {{parameter}}\""
            elif "分析" in func or "评估" in func:
                tool_implementation = f"return f\"分析结果: {{parameter}} 的详细分析\""
            elif "推荐" in func:
                tool_implementation = f"return f\"推荐结果: 基于 {{parameter}} 的个性化推荐\""
            
            # 生成工具代码
            tool_code = '''
        @tool
        def {0}({1}: str) -> str:
            """{2}"""
            # 工具实现
            {3}
        tools.append({0})
            '''.format(tool_name, param_name, tool_description, tool_implementation)
            tools_code.append(tool_code)
        
        return ''.join(tools_code)
    
    def _generate_test_cases(self, core_functions: List[str]) -> str:
        """
        生成测试用例
        
        Args:
            core_functions: 核心功能列表
            
        Returns:
            测试用例代码
        """
        test_cases = []
        
        for i, func in enumerate(core_functions[:3]):  # 最多生成3个测试用例
            test_case = {
                "name": f"测试用例{i+1}",
                "input": func,
                "expected_output": f"期望结果{i+1}"
            }
            test_cases.append(test_case)
        
        # 如果没有足够的测试用例，添加默认测试用例
        if len(test_cases) < 1:
            test_cases.append({
                "name": "默认测试用例",
                "input": "测试任务",
                "expected_output": "期望结果"
            })
        
        return json.dumps(test_cases, ensure_ascii=False, indent=4)
    
    def generate_from_context(self, context: str) -> Dict[str, str]:
        """
        从上下文生成场景配置和评估脚本
        
        Args:
            context: 包含业务场景描述的上下文
            
        Returns:
            生成的文件路径
        """
        # 从上下文提取场景信息
        scene_info = self._extract_scene_info(context)
        
        # 生成配置文件
        config_file = self.generate_config(
            scene_info["scenario_name"],
            scene_info["scenario_description"],
            scene_info["core_functions"],
            scene_info["performance_requirements"],
            scene_info["technical_constraints"]
        )
        
        # 生成评估脚本
        script_file = self.generate_evaluator_script(
            scene_info["scenario_name"],
            scene_info["scenario_description"],
            scene_info["core_functions"],
            scene_info["technical_constraints"]
        )
        
        return {
            "config_file": config_file,
            "script_file": script_file
        }
    
    def _extract_with_spacy(self, context: str) -> Dict[str, Any]:
        """
        使用 spaCy 小模型提取场景信息
        
        Args:
            context: 上下文文本
            
        Returns:
            场景信息
        """
        scene_info = {
            "scenario_name": "custom_scenario",
            "scenario_description": "自定义业务场景",
            "core_functions": [],
            "performance_requirements": [],
            "technical_constraints": []
        }

        # 使用 spaCy 处理文本
        doc = nlp(context)

        # 定义关键词列表
        section_keywords = {
            "业务场景": ["业务场景", "场景描述", "业务需求", "业务目标"],
            "核心功能": ["核心功能", "功能", "能力", "特性"],
            "性能要求": ["性能要求", "要求", "性能", "响应时间", "速度", "稳定"],
            "技术约束": ["技术约束", "约束", "技术", "限制", "依赖"]
        }

        # 功能相关关键词
        function_keywords = ["查询", "获取", "分析", "推荐", "处理", "管理", "生成", "计算", "验证"]
        # 性能相关关键词
        performance_keywords = ["响应时间", "速度", "稳定", "并发", "吞吐量", "延迟", "时间"]
        # 技术相关关键词
        technical_keywords = ["技术", "框架", "库", "依赖", "版本", "平台", "语言"]

        current_section = None
        sentences = list(doc.sents)

        for i, sentence in enumerate(sentences):
            sentence_text = sentence.text.strip()
            if not sentence_text:
                continue

            # 检查章节切换
            for section, keywords in section_keywords.items():
                if any(keyword in sentence_text for keyword in keywords):
                    if section == "业务场景":
                        # 提取业务场景描述
                        scene_info["scenario_description"] = sentence_text
                        scene_info["scenario_name"] = self._extract_scenario_name(sentence_text)
                    elif section == "核心功能":
                        current_section = "core_functions"
                    elif section == "性能要求":
                        current_section = "performance_requirements"
                    elif section == "技术约束":
                        current_section = "technical_constraints"
                    break

            # 提取内容
            if current_section:
                # 检查是否为列表项
                list_match = re.match(r"^(\d+[.、])\s*(.*)", sentence_text)
                if list_match:
                    item_content = list_match.group(2).strip()
                    scene_info[current_section].append(item_content)
                else:
                    # 使用 spaCy 的实体识别和关键词匹配
                    has_relevant_keyword = False
                    if current_section == "core_functions":
                        has_relevant_keyword = any(keyword in sentence_text for keyword in function_keywords)
                    elif current_section == "performance_requirements":
                        has_relevant_keyword = any(keyword in sentence_text for keyword in performance_keywords)
                    elif current_section == "technical_constraints":
                        has_relevant_keyword = any(keyword in sentence_text for keyword in technical_keywords)

                    # 检查是否包含动词短语（可能是功能描述）
                    has_verb = any(token.pos_ == "VERB" for token in sentence)

                    if has_relevant_keyword or has_verb:
                        scene_info[current_section].append(sentence_text)

        return scene_info

    def _extract_scene_info(self, context: str) -> Dict[str, Any]:
        """
        从上下文提取场景信息
        
        Args:
            context: 上下文文本
            
        Returns:
            场景信息
        """
        # 初始化场景信息
        scene_info = {
            "scenario_name": "custom_scenario",
            "scenario_description": "自定义业务场景",
            "core_functions": [],
            "performance_requirements": [],
            "technical_constraints": []
        }

        # 优先使用 spaCy 小模型提取
        if spacy_available:
            print("使用 spaCy 小模型提取场景信息...")
            scene_info = self._extract_with_spacy(context)
        else:
            # 使用传统规则引擎
            print("使用规则引擎提取场景信息...")
            # 标准化文本
            context = context.strip()
            lines = context.split('\n')

            # 状态变量
            current_section = None

            # 正则表达式模式
            section_patterns = {
                "业务场景": r"业务场景[：:]\s*(.*)",
                "场景描述": r"场景描述[：:]\s*(.*)",
                "核心功能": r"核心功能[：:]",
                "性能要求": r"性能要求[：:]",
                "技术约束": r"技术约束[：:]",
                "功能": r"功能[：:]",
                "要求": r"要求[：:]",
                "约束": r"约束[：:]",
                "目标": r"目标[：:]",
                "需求": r"需求[：:]",
            }

            # 解析文本
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 检查是否为章节标题
                section_match = False
                for section_name, pattern in section_patterns.items():
                    match = re.match(pattern, line)
                    if match:
                        if section_name in ["业务场景", "场景描述"]:
                            # 提取业务场景或场景描述
                            content = match.group(1).strip()
                            # 只取第一行作为描述，避免包含后续的核心功能等信息
                            content = content.split('\n')[0].strip()
                            if section_name == "业务场景":
                                # 提取场景名称
                                scene_info["scenario_name"] = self._extract_scenario_name(content)
                                scene_info["scenario_description"] = content
                            elif section_name == "场景描述":
                                scene_info["scenario_description"] = content
                        else:
                            # 设置当前章节
                            if section_name in ["核心功能", "功能"]:
                                current_section = "core_functions"
                            elif section_name in ["性能要求", "要求", "目标", "需求"]:
                                current_section = "performance_requirements"
                            elif section_name in ["技术约束", "约束"]:
                                current_section = "technical_constraints"
                        section_match = True
                        break

                if not section_match:
                    # 检查是否为列表项
                    list_match = re.match(r"^(\d+[.、])\s*(.*)", line)
                    if list_match:
                        # 提取列表项内容
                        item_content = list_match.group(2).strip()
                        if current_section:
                            scene_info[current_section].append(item_content)
                    elif current_section:
                        # 检查是否为段落内容
                        if line and not line.startswith('#') and not line.startswith('='):
                            # 检查是否为新的章节开始
                            if not any(keyword in line for keyword in ["业务场景", "场景描述", "核心功能", "性能要求", "技术约束", "功能", "要求", "约束", "目标", "需求"]):
                                # 添加到当前章节
                                scene_info[current_section].append(line)

        # 清理和标准化场景信息
        scene_info = self._clean_scene_info(scene_info)

        return scene_info
    
    def _extract_scenario_name(self, description: str) -> str:
        """
        从场景描述中提取场景名称
        
        Args:
            description: 场景描述
            
        Returns:
            场景名称（小写，下划线分隔，有效的文件名）
        """
        # 移除换行符和特殊字符
        name = description.replace('\n', ' ').replace('\r', ' ')
        # 移除标点符号和无效字符
        name = re.sub(r'[，。！？；："\'\(\)\[\]、.]+', ' ', name)
        # 提取前几个词
        words = name.split()[:3]
        
        # 生成场景名称
        if words:
            # 使用英文前缀 + 单词数量的简单方案
            scenario_name = "scene_"
            # 添加词的数量作为标识
            scenario_name += str(len(words))
            # 如果有英文词，使用第一个英文词
            for word in words:
                if all(ord(c) <= 127 for c in word):
                    scenario_name += "_" + word.lower()
                    break
        else:
            scenario_name = "custom_scenario"
        
        # 移除所有非字母数字下划线字符
        scenario_name = re.sub(r'[^a-z0-9_]', '', scenario_name)
        # 限制长度
        scenario_name = scenario_name[:50]
        # 确保名称有效
        if not scenario_name:
            scenario_name = "custom_scenario"
        return scenario_name
    
    def _clean_scene_info(self, scene_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理和标准化场景信息
        
        Args:
            scene_info: 场景信息
            
        Returns:
            清理后的场景信息
        """
        # 清理核心功能
        scene_info["core_functions"] = [func for func in scene_info["core_functions"] if func and len(func) > 1]
        
        # 清理性能要求
        scene_info["performance_requirements"] = [req for req in scene_info["performance_requirements"] if req and len(req) > 1]
        
        # 清理技术约束
        scene_info["technical_constraints"] = [constraint for constraint in scene_info["technical_constraints"] if constraint and len(constraint) > 1]
        
        # 如果没有核心功能，添加默认功能
        if not scene_info["core_functions"]:
            scene_info["core_functions"] = ["基本功能1", "基本功能2"]
        
        # 如果没有性能要求，添加默认要求
        if not scene_info["performance_requirements"]:
            scene_info["performance_requirements"] = ["响应时间合理", "稳定运行"]
        
        # 如果没有技术约束，添加默认约束
        if not scene_info["technical_constraints"]:
            scene_info["technical_constraints"] = ["使用标准框架"]
        
        return scene_info


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能场景生成器")
    parser.add_argument('--context', type=str, help='包含业务场景描述的上下文')
    parser.add_argument('--name', type=str, help='场景名称')
    parser.add_argument('--description', type=str, help='场景描述')
    parser.add_argument('--functions', type=str, nargs='+', help='核心功能列表')
    parser.add_argument('--performance', type=str, nargs='+', help='性能要求列表')
    parser.add_argument('--constraints', type=str, nargs='+', help='技术约束列表')
    
    args = parser.parse_args()
    
    generator = ScenarioGenerator()
    
    if args.context:
        # 从上下文生成
        result = generator.generate_from_context(args.context)
        print(f"从上下文生成场景：")
        print(f"配置文件：{result['config_file']}")
        print(f"评估脚本：{result['script_file']}")
    elif args.name and args.functions:
        # 从参数生成
        config_file = generator.generate_config(
            args.name,
            args.description or f"{args.name} 场景",
            args.functions,
            args.performance or [],
            args.constraints or []
        )
        
        script_file = generator.generate_evaluator_script(
            args.name,
            args.description or f"{args.name} 场景",
            args.functions,
            args.constraints or []
        )
        
        print(f"生成场景：")
        print(f"配置文件：{config_file}")
        print(f"评估脚本：{script_file}")
    else:
        print("请提供上下文或场景参数")


if __name__ == "__main__":
    main()
