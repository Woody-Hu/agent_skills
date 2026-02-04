import os
import importlib.util
import json
import argparse
from typing import Dict, Any, List
import concurrent.futures

class ScriptRunner:
    """评估脚本执行器 - 专注于加载和执行脚本"""
    
    def __init__(self, scripts_dir="generated_scripts", config_dir="config"):
        """
        初始化脚本执行器
        
        Args:
            scripts_dir: 评估脚本目录
            config_dir: 配置文件目录
        """
        self.scripts_dir = scripts_dir
        self.config_dir = config_dir
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def discover_scripts(self) -> List[str]:
        """发现所有生成的评估脚本"""
        scripts = []
        
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
    
    def find_evaluator_class(self, module):
        """查找评估器类"""
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and "Evaluator" in name:
                return obj
        return None
    
    def get_config_file(self, script_path: str) -> str:
        """获取脚本对应的配置文件"""
        script_name = os.path.basename(script_path).replace(".py", "")
        return os.path.join(self.config_dir, f"{script_name}_config.json")
    
    def run_script(self, script_path: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行单个评估脚本"""
        try:
            # 加载脚本模块
            module = self.load_script(script_path)
            
            # 查找评估器类
            evaluator_class = self.find_evaluator_class(module)
            if not evaluator_class:
                raise ValueError(f"脚本 {script_path} 中未找到评估器类")
            
            # 自动查找对应的配置文件
            config_file = self.get_config_file(script_path)
            
            # 创建评估器实例
            if os.path.exists(config_file):
                evaluator = evaluator_class(config_file)
            else:
                evaluator = evaluator_class()
            
            # 运行评估
            results = evaluator.run_evaluation(test_cases)
            return results
        except Exception as e:
            error_msg = str(e)
            print(f"执行脚本 {script_path} 时出错: {error_msg}")
            return {"error": error_msg}
    
    def run_all_scripts(self, test_cases: List[Dict[str, Any]], max_workers: int = 4) -> Dict[str, Any]:
        """执行所有评估脚本（支持并行执行）"""
        all_results = {}
        scripts = self.discover_scripts()
        
        if not scripts:
            print("未发现评估脚本，请先生成评估脚本")
            return all_results
        
        print(f"发现 {len(scripts)} 个评估脚本，准备执行...")
        
        # 使用线程池并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有脚本执行任务
            future_to_script = {
                executor.submit(self.run_script, script_path, test_cases): script_path
                for script_path in scripts
            }
            
            # 收集执行结果
            for future in concurrent.futures.as_completed(future_to_script):
                script_path = future_to_script[future]
                script_name = os.path.basename(script_path).replace(".py", "")
                
                try:
                    results = future.result()
                    all_results[script_name] = results
                    print(f"✓ 脚本 {script_name} 执行成功")
                except Exception as e:
                    error_msg = str(e)
                    all_results[script_name] = {"error": error_msg}
                    print(f"✗ 脚本 {script_name} 执行失败: {error_msg}")
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], output_file: str = "combined_evaluation_results.json"):
        """保存评估结果"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"评估结果已保存到: {output_file}")


def load_test_cases(test_cases_file: str = None) -> List[Dict[str, Any]]:
    """加载测试用例"""
    if test_cases_file and os.path.exists(test_cases_file):
        with open(test_cases_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 默认测试用例
    return [
        {
            "name": "默认测试用例",
            "input": "测试任务",
            "expected_output": "期望结果"
        }
    ]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Agent 评估脚本执行器")
    parser.add_argument('--script', type=str, help='指定要执行的脚本名称（不带.py扩展名）')
    parser.add_argument('--test-cases', type=str, help='测试用例文件路径')
    parser.add_argument('--output', type=str, default='combined_evaluation_results.json', help='结果输出文件')
    parser.add_argument('--max-workers', type=int, default=4, help='并行执行的最大线程数')
    parser.add_argument('--scripts-dir', type=str, default='generated_scripts', help='评估脚本目录')
    parser.add_argument('--config-dir', type=str, default='config', help='配置文件目录')
    
    args = parser.parse_args()
    
    # 初始化脚本执行器
    runner = ScriptRunner(
        scripts_dir=args.scripts_dir,
        config_dir=args.config_dir
    )
    
    # 加载测试用例
    test_cases = load_test_cases(args.test_cases)
    
    if args.script:
        # 执行指定脚本
        script_path = os.path.join(args.scripts_dir, f"{args.script}.py")
        if not os.path.exists(script_path):
            print(f"脚本 {script_path} 不存在")
            return
        
        print(f"执行脚本: {args.script}")
        try:
            results = runner.run_script(script_path, test_cases)
            script_name = os.path.basename(script_path).replace(".py", "")
            all_results = {script_name: results}
        except Exception as e:
            print(f"执行脚本时出错: {str(e)}")
            return
    else:
        # 执行所有脚本
        all_results = runner.run_all_scripts(test_cases, max_workers=args.max_workers)
    
    # 保存结果
    runner.save_results(all_results, args.output)


if __name__ == "__main__":
    main()