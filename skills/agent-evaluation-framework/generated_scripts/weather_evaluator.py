import time
import json
import random
from typing import Dict, Any

class WeatherEvaluator:
    """天气查询场景评估器"""
    
    def __init__(self):
        self.results = {}
    
    def _generate_tools(self):
        """生成场景所需的工具"""
        # 模拟工具列表
        class MockTool:
            def __init__(self, name, description):
                self.name = name
                self.description = description
        
        tools = []
        tools.append(MockTool("get_weather", "获取城市天气信息"))
        tools.append(MockTool("get_location", "获取用户当前位置"))
        
        return tools
    
    def evaluate_direct_tool(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """评估直接Tool方案"""
        tools = self._generate_tools()
        
        total_time = 0
        model_calls = 0
        
        for i in range(iterations):
            # 模拟执行
            exec_time = random.uniform(0.5, 0.8)
            total_time += exec_time
            model_calls += 1
            time.sleep(0.1)  # 避免执行过快
        
        return {
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": total_time / iterations,
            "iterations": iterations
        }
    
    def evaluate_mcp(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """评估MCP方案"""
        total_time = 0
        model_calls = 0
        
        for i in range(iterations):
            # 模拟执行
            exec_time = random.uniform(0.4, 0.7)
            total_time += exec_time
            model_calls += 1
            time.sleep(0.1)
        
        return {
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": total_time / iterations,
            "iterations": iterations
        }
    
    def evaluate_skill(self, task: str, iterations: int = 5) -> Dict[str, Any]:
        """评估Skill方案"""
        total_time = 0
        model_calls = 0
        
        for i in range(iterations):
            # 模拟执行
            exec_time = random.uniform(0.6, 0.9)
            total_time += exec_time
            model_calls += 1
            time.sleep(0.1)
        
        return {
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": total_time / iterations,
            "iterations": iterations
        }
    
    def run_evaluation(self, test_cases):
        """运行完整评估"""
        results = {}
        
        for test_case in test_cases:
            task = test_case.get("input", "北京今天的天气怎么样？")
            
            print(f"执行测试用例: {test_case.get('name', '默认测试')}")
            print(f"输入: {task}")
            
            # 评估三种方案
            direct_tool_result = self.evaluate_direct_tool(task)
            mcp_result = self.evaluate_mcp(task)
            skill_result = self.evaluate_skill(task)
            
            results[test_case.get('name', 'default')] = {
                "direct_tool": direct_tool_result,
                "mcp": mcp_result,
                "skill": skill_result
            }
        
        # 汇总结果
        summary = {
            "direct_tool": {
                "model_calls": sum(r["direct_tool"]["model_calls"] for r in results.values()),
                "total_time": sum(r["direct_tool"]["total_time"] for r in results.values()),
                "average_time": sum(r["direct_tool"]["average_time"] for r in results.values()) / len(results)
            },
            "mcp": {
                "model_calls": sum(r["mcp"]["model_calls"] for r in results.values()),
                "total_time": sum(r["mcp"]["total_time"] for r in results.values()),
                "average_time": sum(r["mcp"]["average_time"] for r in results.values()) / len(results)
            },
            "skill": {
                "model_calls": sum(r["skill"]["model_calls"] for r in results.values()),
                "total_time": sum(r["skill"]["total_time"] for r in results.values()),
                "average_time": sum(r["skill"]["average_time"] for r in results.values()) / len(results)
            }
        }
        
        return summary

if __name__ == "__main__":
    evaluator = WeatherEvaluator()
    
    # 测试用例
    test_cases = [
        {
            "name": "天气查询",
            "input": "北京今天的天气怎么样？",
            "expected_output": "北京的天气晴朗，温度25°C"
        },
        {
            "name": "位置感知天气",
            "input": "我现在在哪里？这里的天气怎么样？",
            "expected_output": "您在北京，这里的天气晴朗，温度25°C"
        }
    ]
    
    # 运行评估
    results = evaluator.run_evaluation(test_cases)
    
    # 打印结果
    print("\n评估结果:")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    
    # 保存结果
    with open("weather_evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)