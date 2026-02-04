import tiktoken
from typing import Dict, Any, List
import json

class TokenAnalyzer:
    """Token使用量分析器"""
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        初始化Token分析器
        
        Args:
            model_name: 模型名称，用于选择正确的编码
        """
        self.model_name = model_name
        self.encoding = tiktoken.encoding_for_model(model_name)
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的Token数
        
        Args:
            text: 要计算的文本
            
        Returns:
            Token数
        """
        return len(self.encoding.encode(text))
    
    def analyze_interaction(self, input_text: str, output_text: str) -> Dict[str, int]:
        """
        分析单次交互的Token使用情况
        
        Args:
            input_text: 输入文本
            output_text: 输出文本
            
        Returns:
            Token使用情况
        """
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)
        total_tokens = input_tokens + output_tokens
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }
    
    def analyze_session(self, interactions: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        分析整个会话的Token使用情况
        
        Args:
            interactions: 会话交互列表，每个元素包含input和output
            
        Returns:
            会话Token使用分析
        """
        total_input = 0
        total_output = 0
        total_tokens = 0
        
        for interaction in interactions:
            input_text = interaction.get("input", "")
            output_text = interaction.get("output", "")
            
            input_tokens = self.count_tokens(input_text)
            output_tokens = self.count_tokens(output_text)
            
            total_input += input_tokens
            total_output += output_tokens
            total_tokens += (input_tokens + output_tokens)
        
        return {
            "total_interactions": len(interactions),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_tokens,
            "average_tokens_per_interaction": total_tokens / len(interactions) if interactions else 0
        }
    
    def analyze_performance_results(self, performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析性能评估结果中的Token使用情况
        
        Args:
            performance_results: 性能评估结果
            
        Returns:
            包含Token分析的结果
        """
        # 这里需要根据实际的性能评估结果格式进行调整
        # 假设结果中包含了输入和输出文本
        token_analysis = {}
        
        if "scenarios" in performance_results:
            for scenario_name, scenario_data in performance_results["scenarios"].items():
                token_analysis[scenario_name] = {}
                
                for method, method_data in scenario_data.items():
                    if method != "scenarios":
                        # 这里需要根据实际情况计算Token使用量
                        # 暂时使用模拟数据
                        token_analysis[scenario_name][method] = {
                            "input_tokens": 50,
                            "output_tokens": 80,
                            "total_tokens": 130
                        }
        
        return token_analysis

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Token使用量分析")
    parser.add_argument('--input-file', type=str, help='性能评估结果文件')
    parser.add_argument('--output', type=str, default='token_analysis.json', help='输出文件')
    parser.add_argument('--text', type=str, help='要分析的文本')
    
    args = parser.parse_args()
    
    analyzer = TokenAnalyzer()
    
    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            performance_results = json.load(f)
        
        token_analysis = analyzer.analyze_performance_results(performance_results)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(token_analysis, f, ensure_ascii=False, indent=2)
        
        print(f"Token分析结果已保存到: {args.output}")
    elif args.text:
        tokens = analyzer.count_tokens(args.text)
        print(f"文本Token数: {tokens}")
    else:
        print("请指定输入文件或文本")
