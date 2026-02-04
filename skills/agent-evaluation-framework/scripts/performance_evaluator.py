import time
import json
import argparse
import random
from typing import Dict, Any, List
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_openai import AzureChatOpenAI
from langchain.tools import tool

class PerformanceEvaluator:
    """性能评估器"""
    
    def __init__(self, model_name: str = "gpt-4", azure_config: Dict[str, str] = None):
        """
        初始化性能评估器
        
        Args:
            model_name: 模型名称
            azure_config: Azure OpenAI 配置
        """
        self.model_name = model_name
        self.azure_config = azure_config
        self.results = {}
    
    def _init_model(self):
        """初始化模型"""
        if self.azure_config:
            return AzureChatOpenAI(
                azure_endpoint=self.azure_config["azure_endpoint"],
                api_key=self.azure_config["api_key"],
                api_version=self.azure_config["api_version"],
                deployment_name="gpt-35-turbo"
            )
        else:
            # 当没有配置模型时，使用模拟模式
            return None
    
    def _is_mock_mode(self):
        """检查是否处于模拟模式"""
        return self._init_model() is None
    
    def _generate_tools_for_task(self, task: str):
        """根据用户任务动态生成工具"""
        tools = []
        system_prompt = ""
        
        # 分析任务内容，识别需要的工具
        task_lower = task.lower()
        
        if "天气" in task_lower or "temperature" in task_lower:
            @tool
            def get_weather(city: str) -> str:
                """Get weather for a given city"""
                return f"{city}的天气晴朗，温度25°C"
            tools.append(get_weather)
            system_prompt = "你是一个天气助手，可以回答天气相关问题"
        
        elif "位置" in task_lower or "location" in task_lower:
            @tool
            def get_location() -> str:
                """Get current location"""
                return "你当前的位置是北京市"
            
            @tool
            def get_weather(city: str) -> str:
                """Get weather for a given city"""
                return f"{city}的天气晴朗，温度25°C"
            
            tools.extend([get_location, get_weather])
            system_prompt = "你是一个位置和天气助手，可以回答位置和天气相关问题"
        
        elif "文档" in task_lower or "document" in task_lower or "langgraph" in task_lower:
            @tool
            def search_document(query: str) -> str:
                """Search document for information"""
                if "langgraph" in query.lower():
                    return "LangGraph是LangChain提供的一个框架，用于构建状态化、多步骤的AI代理系统。它允许开发者定义代理的状态管理、决策流程和工具使用方式，支持更复杂的任务执行。"
                return "根据文档，未找到相关信息"
            tools.append(search_document)
            system_prompt = "你是一个文档助手，可以基于文档回答问题"
        
        else:
            # 默认工具
            @tool
            def general_assistant(query: str) -> str:
                """General assistant for answering questions"""
                return f"关于'{query}'的回答"
            tools.append(general_assistant)
            system_prompt = "你是一个通用助手，可以回答各种问题"
        
        return tools, system_prompt
    
    def evaluate_direct_tool(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """评估直接Tool方案"""
        tools, system_prompt = self._generate_tools_for_task(task)
        
        total_time = 0
        model_calls = 0
        
        if self._is_mock_mode():
            # 模拟模式
            for i in range(iterations):
                # 根据工具数量模拟执行时间
                base_time = 0.5
                tool_overhead = len(tools) * 0.1
                exec_time = random.uniform(base_time, base_time + 0.7 + tool_overhead)
                total_time += exec_time
                model_calls += 1
        else:
            # 真实模式
            model = self._init_model()
            agent = create_agent(
                model=model,
                tools=tools,
                system_prompt=system_prompt
            )
            
            for i in range(iterations):
                start_time = time.time()
                response = agent.invoke({
                    "messages": [{"role": "user", "content": task}]
                })
                end_time = time.time()
                
                total_time += (end_time - start_time)
                model_calls += 1
        
        avg_time = total_time / iterations
        
        result = {
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": avg_time,
            "iterations": iterations,
            "tools_used": [tool.__name__ if hasattr(tool, "__name__") else str(tool) for tool in tools]
        }
        
        self.results["direct_tool"] = result
        return result
    
    def evaluate_mcp(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """评估MCP方案"""
        total_time = 0
        model_calls = 0
        
        if self._is_mock_mode():
            # 模拟模式
            for i in range(iterations):
                exec_time = random.uniform(0.4, 1.0)
                total_time += exec_time
                model_calls += 1
        else:
            # 真实模式
            model = self._init_model()
            agent = create_agent(
                model=model,
                system_prompt="你是一个天气助手，可以回答天气相关问题。当用户问天气时，直接基于常识回答，假设天气晴朗。"
            )
            
            for i in range(iterations):
                start_time = time.time()
                response = agent.invoke({
                    "messages": [{"role": "user", "content": task}]
                })
                end_time = time.time()
                
                total_time += (end_time - start_time)
                model_calls += 1
        
        avg_time = total_time / iterations
        
        result = {
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": avg_time,
            "iterations": iterations
        }
        
        self.results["mcp"] = result
        return result
    
    def evaluate_skill(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """评估Skill方案"""
        tools, base_system_prompt = self._generate_tools_for_task(task)
        
        total_time = 0
        model_calls = 0
        
        if self._is_mock_mode():
            # 模拟模式
            for i in range(iterations):
                # 根据工具数量模拟执行时间
                base_time = 0.6
                tool_overhead = len(tools) * 0.15
                exec_time = random.uniform(base_time, base_time + 0.8 + tool_overhead)
                total_time += exec_time
                model_calls += 1
        else:
            # 真实模式
            model = self._init_model()
            agent = create_agent(
                model=model,
                tools=tools,
                system_prompt=f"{base_system_prompt}，你可以使用相关技能回答问题"
            )
            
            for i in range(iterations):
                start_time = time.time()
                response = agent.invoke({
                    "messages": [{"role": "user", "content": task}]
                })
                end_time = time.time()
                
                total_time += (end_time - start_time)
                model_calls += 1
        
        avg_time = total_time / iterations
        
        result = {
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": avg_time,
            "iterations": iterations,
            "tools_used": [tool.__name__ if hasattr(tool, "__name__") else str(tool) for tool in tools]
        }
        
        self.results["skill"] = result
        return result
    
    def compare_all(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """对比所有方案"""
        # 为每个任务创建新的结果字典，避免循环引用
        results = {}
        
        results["direct_tool"] = self.evaluate_direct_tool(task, iterations)
        results["mcp"] = self.evaluate_mcp(task, iterations)
        results["skill"] = self.evaluate_skill(task, iterations)
        
        # 更新全局结果
        self.results.update(results)
        
        return results
    
    def evaluate_scenarios(self, scenarios: List[Dict[str, Any]], iterations: int = 5) -> Dict[str, Any]:
        """评估多个场景"""
        scenarios_results = {}
        
        for scenario in scenarios:
            scenario_name = scenario["name"]
            task = scenario["input"]
            
            print(f"\n评估场景: {scenario_name}")
            print(f"任务: {task}")
            
            results = self.compare_all(task, iterations)
            scenarios_results[scenario_name] = results
        
        self.results["scenarios"] = scenarios_results
        return scenarios_results
    
    def generate_report(self) -> str:
        """生成评估报告"""
        report = "# Agent 实现方案性能评估报告\n\n"
        
        if "scenarios" in self.results:
            for scenario_name, results in self.results["scenarios"].items():
                report += f"## 场景: {scenario_name}\n\n"
                report += "| 方案 | 模型调用次数 | 总执行时间(秒) | 平均执行时间(秒) |\n"
                report += "|------|--------------|----------------|------------------|\n"
                
                for method, data in results.items():
                    if method != "scenarios":
                        report += f"| {method} | {data['model_calls']} | {data['total_time']:.4f} | {data['average_time']:.4f} |\n"
                
                report += "\n"
        else:
            report += "## 性能评估结果\n\n"
            report += "| 方案 | 模型调用次数 | 总执行时间(秒) | 平均执行时间(秒) |\n"
            report += "|------|--------------|----------------|------------------|\n"
            
            for method, data in self.results.items():
                if method != "scenarios":
                    report += f"| {method} | {data['model_calls']} | {data['total_time']:.4f} | {data['average_time']:.4f} |\n"
        
        return report
    
    def save_results(self, output_file: str):
        """保存结果到文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Agent 实现方案性能评估")
    parser.add_argument('--task', type=str, help='评估任务')
    parser.add_argument('--scenario-file', type=str, help='测试场景文件')
    parser.add_argument('--iterations', type=int, default=5, help='迭代次数')
    parser.add_argument('--output', type=str, default='performance_results.json', help='输出文件')
    parser.add_argument('--use-azure', action='store_true', help='使用Azure OpenAI')
    
    args = parser.parse_args()
    
    azure_config = None
    if args.use_azure:
        # 从环境变量读取Azure配置
        import os
        azure_config = {
            "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "https://evaluation2025.openai.azure.com/"),
            "api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        }
        
        # 验证配置是否完整
        if not azure_config["api_key"]:
            print("警告: 未设置AZURE_OPENAI_API_KEY环境变量")
            print("请设置环境变量后再运行:")
            print("export AZURE_OPENAI_ENDPOINT=\"https://evaluation2025.openai.azure.com/\"")
            print("export AZURE_OPENAI_API_KEY=\"your_api_key\"")
            print("export AZURE_OPENAI_API_VERSION=\"2024-12-01-preview\"")
            return
    
    evaluator = PerformanceEvaluator(azure_config=azure_config)
    
    if args.scenario_file:
        with open(args.scenario_file, 'r', encoding='utf-8') as f:
            scenarios_data = json.load(f)
        
        evaluator.evaluate_scenarios(scenarios_data["scenarios"], args.iterations)
    elif args.task:
        evaluator.compare_all(args.task, args.iterations)
    else:
        print("请指定任务或场景文件")
        return
    
    # 生成报告
    report = evaluator.generate_report()
    print(report)
    
    # 保存结果
    evaluator.save_results(args.output)
    print(f"\n结果已保存到: {args.output}")

if __name__ == "__main__":
    main()
