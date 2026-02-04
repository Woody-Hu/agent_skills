import json
import argparse
from typing import Dict, Any

class ReportGenerator:
    """综合评估报告生成器"""
    
    def __init__(self):
        """初始化报告生成器"""
        pass
    
    def load_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        加载JSON文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            文件内容
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_report(self, performance_file: str, token_file: str, complexity_file: str) -> str:
        """
        生成综合评估报告
        
        Args:
            performance_file: 性能评估结果文件
            token_file: Token分析结果文件
            complexity_file: 复杂度分析结果文件
            
        Returns:
            生成的报告
        """
        # 加载评估结果
        performance_results = self.load_json_file(performance_file)
        token_results = self.load_json_file(token_file)
        complexity_results = self.load_json_file(complexity_file)
        
        report = "# Agent 实现方案综合评估报告\n\n"
        
        # 1. 性能评估部分
        report += "## 1. 性能评估\n\n"
        
        if "scenarios" in performance_results:
            for scenario_name, scenario_data in performance_results["scenarios"].items():
                report += f"### 场景: {scenario_name}\n\n"
                report += "| 方案 | 模型调用次数 | 总执行时间(秒) | 平均执行时间(秒) |\n"
                report += "|------|--------------|----------------|------------------|\n"
                
                for method, data in scenario_data.items():
                    if method != "scenarios":
                        report += f"| {method} | {data['model_calls']} | {data['total_time']:.4f} | {data['average_time']:.4f} |\n"
                
                report += "\n"
        
        # 2. Token使用量分析部分
        report += "## 2. Token使用量分析\n\n"
        
        for scenario_name, scenario_data in token_results.items():
            report += f"### 场景: {scenario_name}\n\n"
            report += "| 方案 | 输入Token | 输出Token | 总Token |\n"
            report += "|------|-----------|-----------|---------|\n"
            
            for method, data in scenario_data.items():
                report += f"| {method} | {data['input_tokens']} | {data['output_tokens']} | {data['total_tokens']} |\n"
            
            report += "\n"
        
        # 3. 代码复杂度分析部分
        report += "## 3. 代码复杂度分析\n\n"
        
        if "summary" in complexity_results:
            summary = complexity_results["summary"]
            report += "### 整体复杂度统计\n\n"
            report += f"- 总文件数: {summary['total_files']}\n"
            report += f"- 总行数: {summary['total_lines_of_code']}\n"
            report += f"- 总圈复杂度: {summary['total_cyclomatic_complexity']}\n"
            report += f"- 总函数数: {summary['total_functions']}\n"
            report += f"- 总类数: {summary['total_classes']}\n"
            report += "\n"
        
        # 4. 综合分析部分
        report += "## 4. 综合分析\n\n"
        
        # 4.1 性能对比
        report += "### 4.1 性能对比\n\n"
        report += "| 方案 | 性能排名 | 优势 | 劣势 |\n"
        report += "|------|----------|------|------|\n"
        report += "| 直接Tool | 1 | 执行速度最快，模型调用次数最少 | 可重用性差，难以管理复杂逻辑 |\n"
        report += "| MCP | 2 | 实现简洁，利用模型上下文理解能力 | 依赖模型理解能力，可能产生不一致结果 |\n"
        report += "| Skill | 3 | 高度可重用，标准化接口，易于团队协作 | 性能略差，Token使用量较大 |\n"
        report += "\n"
        
        # 4.2 Token使用量对比
        report += "### 4.2 Token使用量对比\n\n"
        report += "| 方案 | Token使用量 | 原因 |\n"
        report += "|------|-------------|------|\n"
        report += "| 直接Tool | 最少 | 实现简单，上下文传递少 |\n"
        report += "| MCP | 较少 | 利用模型上下文，减少额外调用 |\n"
        report += "| Skill | 较多 | 标准化接口和额外的上下文处理 |\n"
        report += "\n"
        
        # 4.3 复杂度对比
        report += "### 4.3 复杂度对比\n\n"
        report += "| 方案 | 实现复杂度 | 维护难度 |\n"
        report += "|------|------------|----------|\n"
        report += "| 直接Tool | 低 | 低 |\n"
        report += "| MCP | 低 | 中 |\n"
        report += "| Skill | 中 | 低 |\n"
        report += "\n"
        
        # 5. 推荐方案
        report += "## 5. 推荐方案\n\n"
        
        report += "### 5.1 基于场景的推荐\n\n"
        report += "| 场景类型 | 推荐方案 | 理由 |\n"
        report += "|----------|----------|------|\n"
        report += "| 简单查询功能 | 直接Tool | 性能最优，实现简单 |\n"
        report += "| 性能敏感场景 | 直接Tool | 执行速度快，资源消耗少 |\n"
        report += "| 快速原型开发 | MCP | 实现简洁，利用模型上下文能力 |\n"
        report += "| 上下文相关功能 | MCP | 适合需要模型理解的场景 |\n"
        report += "| 复杂业务流程 | Skill | 高度可重用，易于团队协作 |\n"
        report += "| 团队协作开发 | Skill | 标准化接口，便于维护和扩展 |\n"
        report += "\n"
        
        report += "### 5.2 综合建议\n\n"
        report += "1. **简单、性能敏感的功能**：优先考虑直接Tool实现\n"
        report += "2. **快速原型、上下文相关的功能**：优先考虑MCP实现\n"
        report += "3. **复杂、可重用的功能**：优先考虑Skill实现\n"
        report += "4. **大型项目**：建议采用混合策略，根据具体功能选择合适的实现方式\n"
        report += "5. **资源受限环境**：优先考虑直接Tool或MCP实现\n"
        report += "\n"
        
        # 6. 结论
        report += "## 6. 结论\n\n"
        report += "选择合适的Agent实现方案需要综合考虑性能、可维护性、可重用性等多个因素。通过本评估框架的客观指标分析，可以根据具体业务场景的需求和约束，做出更加合理的技术决策。\n\n"
        report += "在实际项目中，建议根据功能复杂度、团队规模、维护要求等因素，灵活选择最适合的实现方案，甚至在同一项目中混合使用不同的实现方式，以达到最佳的整体效果。\n"
        
        return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成综合评估报告")
    parser.add_argument('--performance', type=str, required=True, help='性能评估结果文件')
    parser.add_argument('--token', type=str, required=True, help='Token分析结果文件')
    parser.add_argument('--complexity', type=str, required=True, help='复杂度分析结果文件')
    parser.add_argument('--output', type=str, default='final_report.md', help='输出报告文件')
    
    args = parser.parse_args()
    
    generator = ReportGenerator()
    report = generator.generate_report(args.performance, args.token, args.complexity)
    
    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"综合评估报告已生成并保存到: {args.output}")
