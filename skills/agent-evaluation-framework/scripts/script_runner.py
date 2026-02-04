import os
import importlib.util
import json
from typing import Dict, Any, List

class ScriptRunner:
    """评估脚本执行器"""
    
    def __init__(self, scripts_dir="generated_scripts"):
        self.scripts_dir = scripts_dir
    
    def discover_scripts(self) -> List[str]:
        """发现所有生成的评估脚本"""
        scripts = []
        
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
        
        for file in os.listdir(self.scripts_dir):
            if file.endswith(".py") and not file.startswith("_"):
                scripts.append(os.path.join(self.scripts_dir, file))
        
        return scripts
    
    def load_script(self, script_path: str):
        """加载脚本模块"""
        module_name = os.path.basename(script_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def run_script(self, script_path: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行单个评估脚本"""
        module = self.load_script(script_path)
        
        # 查找评估器类
        evaluator_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if hasattr(obj, "__class__") and "Evaluator" in name:
                evaluator_class = obj
                break
        
        if not evaluator_class:
            raise ValueError(f"脚本 {script_path} 中未找到评估器类")
        
        # 创建评估器实例并运行
        evaluator = evaluator_class()
        results = evaluator.run_evaluation(test_cases)
        
        return results
    
    def run_all_scripts(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行所有评估脚本"""
        all_results = {}
        scripts = self.discover_scripts()
        
        for script_path in scripts:
            script_name = os.path.basename(script_path).replace(".py", "")
            print(f"执行评估脚本: {script_name}")
            
            try:
                results = self.run_script(script_path, test_cases)
                all_results[script_name] = results
            except Exception as e:
                print(f"执行脚本 {script_name} 时出错: {str(e)}")
                all_results[script_name] = {"error": str(e)}
        
        return all_results
    
    def generate_combined_report(self, results: Dict[str, Any]) -> str:
        """生成综合评估报告"""
        report = "# 综合评估报告\n\n"
        
        for script_name, script_results in results.items():
            report += f"## {script_name}\n\n"
            
            if "error" in script_results:
                report += f"**执行错误**: {script_results['error']}\n\n"
            else:
                # 生成脚本特定的报告内容
                report += "### 评估结果\n\n"
                
                # 检查是否有方案对比结果
                if "direct_tool" in script_results and "mcp" in script_results and "skill" in script_results:
                    report += "#### 方案对比\n\n"
                    report += "| 方案 | 模型调用次数 | 总执行时间(秒) | 平均执行时间(秒) |\n"
                    report += "|------|--------------|----------------|------------------|\n"
                    
                    for method in ["direct_tool", "mcp", "skill"]:
                        method_name = {
                            "direct_tool": "直接Tool",
                            "mcp": "MCP",
                            "skill": "Skill"
                        }[method]
                        
                        data = script_results[method]
                        model_calls = data.get("model_calls", 0)
                        total_time = data.get("total_time", 0)
                        avg_time = data.get("average_time", 0)
                        
                        report += f"| {method_name} | {model_calls} | {total_time:.2f} | {avg_time:.2f} |\n"
                    
                    report += "\n"
                
                # 添加其他结果信息
                report += "### 详细信息\n\n"
                report += f"```json\n{json.dumps(script_results, ensure_ascii=False, indent=2)}\n```\n\n"
        
        return report

if __name__ == "__main__":
    runner = ScriptRunner()
    
    # 测试用例
    test_cases = [
        {
            "name": "测试用例1",
            "input": "测试输入1",
            "expected_output": "期望输出1"
        }
        # 添加更多测试用例
    ]
    
    # 执行所有脚本
    results = runner.run_all_scripts(test_cases)
    
    # 生成报告
    report = runner.generate_combined_report(results)
    print(report)
    
    # 保存结果
    with open("combined_evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存报告
    with open("combined_evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(report)