import time
import json
import argparse
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
            return init_chat_model(self.model_name)
    
    def evaluate_direct_tool(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """评估直接Tool方案"""
        @tool
        def get_weather(city: str) -> str:
            """Get weather for a given city"""
            return f"{city}的天气晴朗，温度25°C"
        
        model = self._init_model()
        agent = create_agent(
            model=model,
            tools=[get_weather],
            system_prompt="你是一个天气助手，可以回答天气相关问题"
        )
        
        total_time = 0
        model_calls = 0
        
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
        
        self.results["direct_tool"] = result
        return result
    
    def evaluate_mcp(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """评估MCP方案"""
        model = self._init_model()
        agent = create_agent(
            model=model,
            system_prompt="你是一个天气助手，可以回答天气相关问题。当用户问天气时，直接基于常识回答，假设天气晴朗。"
        )
        
        total_time = 0
        model_calls = 0
        
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
        @tool
        def get_weather(city: str) -> str:
            """Get weather for a given city"""
            return f"{city}的天气晴朗，温度25°C"
        
        model = self._init_model()
        agent = create_agent(
            model=model,
            tools=[get_weather],
            system_prompt="你是一个天气助手，可以使用天气查询技能回答天气相关问题"
        )
        
        total_time = 0
        model_calls = 0
        
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
        
        self.results["skill"] = result
        return result
    
    def compare_all(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """对比所有方案"""
        self.evaluate_direct_tool(task, iterations)
        self.evaluate_mcp(task, iterations)
        self.evaluate_skill(task, iterations)
        
        return self.results
    
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
