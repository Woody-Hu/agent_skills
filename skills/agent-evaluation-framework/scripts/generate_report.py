import json
import argparse
import os
from typing import Dict, Any, List

class ReportGenerator:
    """智能评估报告生成器"""
    
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
    
    def analyze_performance_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析性能评估结果
        
        Args:
            results: 评估结果数据
            
        Returns:
            分析结果
        """
        analysis = {}
        
        for scenario_name, scenario_data in results.items():
            if "error" in scenario_data:
                continue
            
            analysis[scenario_name] = {
                "best_performance": None,
                "best_model_calls": None,
                "best_overall": None,
                "comparison": {},
                "scores": {},
                "recommendation": None
            }
            
            # 性能对比
            performances = {}
            for method, data in scenario_data.items():
                if method in ["direct_tool", "mcp", "skill"]:
                    performances[method] = {
                        "model_calls": data.get("model_calls", 0),
                        "total_time": data.get("total_time", 0),
                        "average_time": data.get("average_time", 0)
                    }
            
            # 计算综合得分
            if performances:
                for method, data in performances.items():
                    # 计算综合得分（越低越好）
                    score = (data["average_time"] * 0.4 + 
                             data["model_calls"] * 0.3 + 
                             (data.get("total_tokens", 0) / 1000) * 0.3)
                    analysis[scenario_name]["scores"][method] = score
                
                # 找出最佳性能
                sorted_by_time = sorted(performances.items(), key=lambda x: x[1]["average_time"])
                analysis[scenario_name]["best_performance"] = sorted_by_time[0][0]
                
                # 找出最少模型调用
                sorted_by_calls = sorted(performances.items(), key=lambda x: x[1]["model_calls"])
                analysis[scenario_name]["best_model_calls"] = sorted_by_calls[0][0]
                
                # 找出综合最佳
                sorted_by_score = sorted(analysis[scenario_name]["scores"].items(), key=lambda x: x[1])
                analysis[scenario_name]["best_overall"] = sorted_by_score[0][0]
                analysis[scenario_name]["recommendation"] = sorted_by_score[0][0]
                analysis[scenario_name]["comparison"] = performances
        
        return analysis
    
    def generate_executive_summary(self, results: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        生成执行摘要
        
        Args:
            results: 评估结果数据
            analysis: 分析结果
            
        Returns:
            执行摘要
        """
        summary = "# Agent 实现方案评估报告\n\n"
        summary += "## 执行摘要\n\n"
        
        # 统计成功执行的场景
        successful_scenarios = [s for s, d in results.items() if "error" not in d]
        failed_scenarios = [s for s, d in results.items() if "error" in d]
        total_scenarios = len(results)
        
        summary += f"本次评估共执行了 {total_scenarios} 个场景，其中 {len(successful_scenarios)} 个场景执行成功，{len(failed_scenarios)} 个场景执行失败。\n\n"
        
        if failed_scenarios:
            summary += "### 失败场景\n\n"
            for scenario in failed_scenarios:
                error_msg = results[scenario].get("error", "未知错误")
                summary += f"- **{scenario}**: {error_msg}\n"
            summary += "\n"
        
        if successful_scenarios:
            summary += "### 推荐方案汇总\n\n"
            
            # 统计各方案的推荐次数
            recommendations = {"direct_tool": 0, "mcp": 0, "skill": 0}
            for scenario in successful_scenarios:
                if scenario in analysis:
                    best_overall = analysis[scenario]["best_overall"]
                    if best_overall:
                        recommendations[best_overall] += 1
            
            # 生成推荐统计
            method_names = {
                "direct_tool": "直接Tool",
                "mcp": "MCP",
                "skill": "Skill"
            }
            
            for method, count in recommendations.items():
                if count > 0:
                    percentage = (count / len(successful_scenarios)) * 100
                    summary += f"- **{method_names[method]}**: {count} 个场景推荐 ({percentage:.1f}%)\n"
            
            summary += "\n"
            
            # 生成整体性能分析
            summary += "### 整体性能分析\n\n"
            
            # 计算平均性能数据
            total_performance = {
                "direct_tool": {"model_calls": 0, "total_time": 0, "average_time": 0},
                "mcp": {"model_calls": 0, "total_time": 0, "average_time": 0},
                "skill": {"model_calls": 0, "total_time": 0, "average_time": 0}
            }
            
            for scenario in successful_scenarios:
                if scenario in analysis:
                    for method, data in analysis[scenario]["comparison"].items():
                        total_performance[method]["model_calls"] += data["model_calls"]
                        total_performance[method]["total_time"] += data["total_time"]
                        total_performance[method]["average_time"] += data["average_time"]
            
            # 计算平均值
            for method in total_performance:
                if len(successful_scenarios) > 0:
                    total_performance[method]["average_time"] /= len(successful_scenarios)
            
            # 生成性能对比表格
            summary += "| 方案 | 模型调用次数 | 总执行时间(秒) | 平均执行时间(秒) |\n"
            summary += "|------|--------------|----------------|------------------|\n"
            
            for method, data in total_performance.items():
                summary += f"| {method_names[method]} | {data['model_calls']} | {data['total_time']:.2f} | {data['average_time']:.2f} |\n"
            
            summary += "\n"
        
        return summary
    
    def generate_detailed_analysis(self, results: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        生成详细分析
        
        Args:
            results: 评估结果数据
            analysis: 分析结果
            
        Returns:
            详细分析报告
        """
        report = "\n"
        
        # 1. 场景详细分析
        report += "## 1. 场景详细分析\n\n"
        
        method_names = {
            "direct_tool": "直接Tool",
            "mcp": "MCP",
            "skill": "Skill"
        }
        
        for scenario_name, scenario_data in results.items():
            report += f"### 场景: {scenario_name}\n\n"
            
            if "error" in scenario_data:
                report += f"**执行错误**: {scenario_data['error']}\n\n"
                continue
            
            # 性能对比表格
            report += "#### 性能对比\n\n"
            report += "| 方案 | 模型调用次数 | 总执行时间(秒) | 平均执行时间(秒) | 综合得分 |\n"
            report += "|------|--------------|----------------|------------------|----------|\n"
            
            for method, data in scenario_data.items():
                if method in method_names:
                    model_calls = data.get("model_calls", 0)
                    total_time = data.get("total_time", 0)
                    avg_time = data.get("average_time", 0)
                    score = analysis[scenario_name]["scores"].get(method, "N/A")
                    
                    report += f"| {method_names[method]} | {model_calls} | {total_time:.2f} | {avg_time:.2f} | {score:.3f} |\n"
            
            report += "\n"
            
            # 推荐方案
            if scenario_name in analysis:
                best_performance = analysis[scenario_name]["best_performance"]
                best_model_calls = analysis[scenario_name]["best_model_calls"]
                best_overall = analysis[scenario_name]["best_overall"]
                
                report += "#### 评估结论\n\n"
                report += f"- **最佳性能方案**: {method_names.get(best_performance, best_performance)}\n"
                report += f"- **最少模型调用**: {method_names.get(best_model_calls, best_model_calls)}\n"
                report += f"- **综合推荐方案**: {method_names.get(best_overall, best_overall)}\n"
                report += "\n"
                
                # 方案优缺点分析
                report += "#### 方案优缺点分析\n\n"
                for method, name in method_names.items():
                    report += f"**{name}**:\n"
                    if method == "direct_tool":
                        report += "- **优点**: 性能最佳，执行速度快，资源消耗少\n"
                        report += "- **缺点**: 可重用性较低，维护成本较高\n"
                    elif method == "mcp":
                        report += "- **优点**: 实现简洁，利用模型上下文能力，开发效率高\n"
                        report += "- **缺点**: 性能可能不如直接Tool，模型依赖度高\n"
                    elif method == "skill":
                        report += "- **优点**: 高度可重用，标准化接口，易于团队协作\n"
                        report += "- **缺点**: 性能可能不如其他方案，实现复杂度较高\n"
                report += "\n"
        
        return report
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> str:
        """
        生成推荐结论
        
        Args:
            analysis: 分析结果
            
        Returns:
            推荐结论
        """
        report = "\n"
        report += "## 2. 推荐结论\n\n"
        
        # 统计各方案的表现
        method_performance = {"direct_tool": 0, "mcp": 0, "skill": 0}
        total_scenarios = 0
        
        for scenario, data in analysis.items():
            best_overall = data.get("best_overall")
            if best_overall:
                method_performance[best_overall] += 1
                total_scenarios += 1
        
        if total_scenarios > 0:
            # 生成基于数据的推荐
            report += "### 2.1 基于评估结果的推荐\n\n"
            
            method_names = {
                "direct_tool": "直接Tool",
                "mcp": "MCP",
                "skill": "Skill"
            }
            
            for method, count in method_performance.items():
                if count > 0:
                    percentage = (count / total_scenarios) * 100
                    report += f"- **{method_names[method]}**: 在 {percentage:.1f}% 的场景中表现最佳\n"
            
            report += "\n"
        
        # 基于场景类型的推荐
        report += "### 2.2 基于场景类型的推荐\n\n"
        report += "| 场景类型 | 推荐方案 | 理由 |\n"
        report += "|----------|----------|------|\n"
        report += "| 简单查询功能 | 直接Tool | 性能最优，实现简单，适合高频调用场景 |\n"
        report += "| 性能敏感场景 | 直接Tool | 执行速度快，资源消耗少，适合实时性要求高的场景 |\n"
        report += "| 快速原型开发 | MCP | 实现简洁，利用模型上下文能力，适合快速验证概念 |\n"
        report += "| 上下文相关功能 | MCP | 适合需要模型理解上下文的场景，如对话系统 |\n"
        report += "| 复杂业务流程 | Skill | 高度可重用，标准化接口，易于团队协作和维护 |\n"
        report += "| 团队协作开发 | Skill | 标准化接口，便于多人维护和扩展，适合大型项目 |\n"
        report += "| 多Agent系统 | Skill | 可重用性高，便于在多个Agent中共享功能 |\n"
        report += "| 资源受限环境 | 直接Tool | 资源消耗少，适合计算资源有限的环境 |\n"
        report += "| 模型能力依赖 | MCP | 充分利用模型能力，适合需要复杂推理的场景 |\n"
        report += "| 长期维护项目 | Skill | 标准化接口，便于长期维护和扩展 |\n"
        report += "\n"
        
        # 综合建议
        report += "### 2.3 综合建议\n\n"
        report += "1. **评估先行**：在选择实现方案前，使用本框架进行客观评估\n"
        report += "2. **混合策略**：大型项目建议采用混合策略，根据具体功能选择合适的实现方式\n"
        report += "3. **持续优化**：定期重新评估，适应业务需求和模型能力的变化\n"
        report += "4. **性能监控**：在生产环境中持续监控关键性能指标\n"
        report += "5. **团队培训**：根据团队规模和技术栈选择合适的实现方案，并提供相应培训\n"
        report += "6. **标准化**：建立统一的代码规范和实现标准，提高代码质量和可维护性\n"
        report += "7. **模块化**：无论选择哪种方案，都应注重代码的模块化和可测试性\n"
        report += "\n"
        
        return report
    
    def generate_improvement_suggestions(self) -> str:
        """
        生成改进建议
        
        Returns:
            改进建议
        """
        report = "\n"
        report += "## 3. 改进建议\n\n"
        
        report += "### 3.1 性能优化建议\n\n"
        report += "| 方案 | 优化建议 | 预期效果 |\n"
        report += "|------|----------|----------|\n"
        report += "| 直接Tool | 1. 实现缓存机制\n2. 批量处理请求\n3. 优化工具函数逻辑 | 减少重复计算，提高执行速度 |\n"
        report += "| MCP | 1. 优化提示词\n2. 合理设置上下文窗口\n3. 使用模型的批处理能力 | 减少Token使用量，提高理解准确性 |\n"
        report += "| Skill | 1. 模块化设计\n2. 优化技能调用链\n3. 实现异步执行 | 提高执行效率，减少模型调用次数 |\n"
        report += "\n"
        
        report += "### 3.2 架构改进建议\n\n"
        report += "1. **分层架构**：将业务逻辑与工具实现分离，提高代码可维护性\n"
        report += "2. **标准化接口**：统一工具和技能的接口设计，便于集成和测试\n"
        report += "3. **配置管理**：使用集中化的配置管理，便于调整和优化\n"
        report += "4. **监控系统**：实现性能监控和告警机制，及时发现问题\n"
        report += "5. **测试覆盖**：建立完善的单元测试和集成测试，确保系统稳定性\n"
        report += "6. **文档化**：编写详细的代码注释和使用文档，提高代码可读性\n"
        report += "\n"
        
        report += "### 3.3 开发流程建议\n\n"
        report += "1. **需求分析**：充分理解业务需求，明确功能边界和性能要求\n"
        report += "2. **原型设计**：使用MCP快速原型验证，确定功能可行性\n"
        report += "3. **性能评估**：使用本框架评估不同实现方案的性能\n"
        report += "4. **方案选择**：基于评估结果选择最佳实现方案\n"
        report += "5. **代码实现**：按照选定方案实现功能，注重代码质量\n"
        report += "6. **测试验证**：进行充分的测试，确保功能正确性和性能符合要求\n"
        report += "7. **部署监控**：部署到生产环境并持续监控性能指标\n"
        report += "8. **迭代优化**：根据实际运行情况持续优化和改进\n"
        report += "\n"
        
        return report
    
    def generate_report(self, results_file: str) -> str:
        """
        生成综合评估报告
        
        Args:
            results_file: 评估结果文件
            
        Returns:
            生成的报告
        """
        # 加载评估结果
        results = self.load_json_file(results_file)
        
        # 分析结果
        analysis = self.analyze_performance_results(results)
        
        # 生成报告
        report = ""
        
        # 1. 执行摘要
        report += self.generate_executive_summary(results, analysis)
        
        # 2. 详细分析
        report += self.generate_detailed_analysis(results, analysis)
        
        # 3. 推荐结论
        report += self.generate_recommendations(analysis)
        
        # 4. 改进建议
        report += self.generate_improvement_suggestions()
        
        # 5. 结论
        report += "## 4. 结论\n\n"
        report += "Agent实现方案的选择应基于具体业务场景的需求和约束，通过本评估框架的客观指标分析，可以做出更加合理的技术决策。\n\n"
        report += "无论选择哪种实现方案，都应注重代码质量、性能优化和可维护性，以构建既高效又可靠的Agent系统。\n"
        report += "\n"
        report += "通过科学的评估和合理的架构设计，可以充分发挥不同实现方案的优势，为业务提供更好的AI能力支持。\n"
        
        return report
    
    def save_report(self, report: str, output_file: str):
        """
        保存报告到文件
        
        Args:
            report: 报告内容
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"评估报告已保存到: {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="生成Agent实现方案评估报告")
    parser.add_argument('--results', type=str, required=True, help='评估结果文件')
    parser.add_argument('--output', type=str, default='final_report.md', help='输出报告文件')
    
    args = parser.parse_args()
    
    generator = ReportGenerator()
    report = generator.generate_report(args.results)
    generator.save_report(report, args.output)


if __name__ == "__main__":
    main()