import time
import json
import random
import os
from typing import Dict, Any

class SalesRecommendationEvaluator:
    """销量推荐场景评估器"""
    
    def __init__(self, config_file=None):
        self.results = {}
        self.config = self._load_config(config_file)
    
    def _load_config(self, config_file):
        """加载评估配置文件"""
        default_config = {
            "model_calls": {
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
            },
            "execution": {
                "iterations": 5,
                "concurrency": 1,
                "timeout": 30
            }
        }
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 尝试自动查找配置文件
        default_config_path = "config/sales_config.json"
        if os.path.exists(default_config_path):
            with open(default_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return default_config
    
    def _get_task_complexity(self, task):
        """根据任务内容判断复杂度"""
        task = task.lower()
        if any(keyword in task for keyword in ["复杂", "推荐", "分析", "多步", "详细"]):
            return "complex"
        elif any(keyword in task for keyword in ["查询", "获取", "简单"]):
            return "simple"
        else:
            return "medium"
    
    def _generate_tools(self):
        """生成场景所需的工具"""
        # 模拟工具列表
        class MockTool:
            def __init__(self, name, description):
                self.name = name
                self.description = description
        
        tools = []
        tools.append(MockTool("get_sales_data", "获取商品销量数据"))
        tools.append(MockTool("get_product_info", "获取商品信息"))
        tools.append(MockTool("generate_recommendation", "生成销量推荐"))
        
        return tools
    
    def evaluate_direct_tool(self, task: str, iterations: int = None) -> Dict[str, Any]:
        """评估直接Tool方案"""
        tools = self._generate_tools()
        iterations = iterations or self.config["execution"]["iterations"]
        
        total_time = 0
        model_calls = 0
        
        # 获取任务复杂度
        complexity = self._get_task_complexity(task)
        # 从配置获取模型调用次数
        calls_per_iteration = self.config["model_calls"]["direct_tool"][complexity]
        
        for i in range(iterations):
            # 模拟执行
            exec_time = random.uniform(0.8, 1.2)
            total_time += exec_time
            model_calls += calls_per_iteration
            time.sleep(0.1)  # 避免执行过快
        
        return {
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": total_time / iterations,
            "iterations": iterations,
            "complexity": complexity,
            "calls_per_iteration": calls_per_iteration
        }
    
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
            exec_time = random.uniform(0.7, 1.0)
            total_time += exec_time
            model_calls += calls_per_iteration
            time.sleep(0.1)
        
        return {
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": total_time / iterations,
            "iterations": iterations,
            "complexity": complexity,
            "calls_per_iteration": calls_per_iteration
        }
    
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
            exec_time = random.uniform(0.9, 1.3)
            total_time += exec_time
            model_calls += calls_per_iteration
            time.sleep(0.1)
        
        return {
            "model_calls": model_calls,
            "total_time": total_time,
            "average_time": total_time / iterations,
            "iterations": iterations,
            "complexity": complexity,
            "calls_per_iteration": calls_per_iteration
        }
    
    def run_evaluation(self, test_cases):
        """运行完整评估"""
        results = {}
        
        for test_case in test_cases:
            task = test_case.get("input", "推荐销量好的商品")
            
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
    # 加载配置文件（如果存在）
    config_file = "config/sales_config.json"
    evaluator = SalesRecommendationEvaluator(config_file)
    
    # 测试用例
    test_cases = [
        {
            "name": "简单销量推荐",
            "input": "查询销量好的商品",
            "expected_output": "包含销量好的商品推荐列表"
        },
        {
            "name": "复杂分类销量推荐",
            "input": "详细分析并推荐电子产品类别中销量好的商品",
            "expected_output": "包含电子产品类别销量好的商品推荐列表"
        }
    ]
    
    # 运行评估
    results = evaluator.run_evaluation(test_cases)
    
    # 打印结果
    print("\n评估结果:")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    
    # 保存结果
    with open("sales_recommendation_evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)