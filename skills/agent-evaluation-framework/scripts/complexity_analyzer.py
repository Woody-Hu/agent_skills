import ast
import os
from typing import Dict, Any

class ComplexityAnalyzer:
    """代码复杂度分析器"""
    
    def __init__(self):
        """初始化代码复杂度分析器"""
        pass
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        分析单个文件的复杂度
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件复杂度分析结果
        """
        if not os.path.exists(file_path):
            return {
                "error": f"文件不存在: {file_path}"
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            lines_of_code = len(content.splitlines())
            cyclomatic_complexity = self.calculate_cyclomatic_complexity(tree)
            function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            
            return {
                "file_path": file_path,
                "lines_of_code": lines_of_code,
                "cyclomatic_complexity": cyclomatic_complexity,
                "function_count": function_count,
                "class_count": class_count
            }
        except Exception as e:
            return {
                "error": f"分析文件时出错: {str(e)}"
            }
    
    def analyze_directory(self, directory: str) -> Dict[str, Any]:
        """
        分析目录中所有文件的复杂度
        
        Args:
            directory: 目录路径
            
        Returns:
            目录复杂度分析结果
        """
        if not os.path.exists(directory):
            return {
                "error": f"目录不存在: {directory}"
            }
        
        results = {
            "directory": directory,
            "files": []
        }
        
        total_lines = 0
        total_complexity = 0
        total_functions = 0
        total_classes = 0
        
        for root, dirs, files in os.walk(directory):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_result = self.analyze_file(file_path)
                    
                    if "error" not in file_result:
                        results["files"].append(file_result)
                        total_lines += file_result["lines_of_code"]
                        total_complexity += file_result["cyclomatic_complexity"]
                        total_functions += file_result["function_count"]
                        total_classes += file_result["class_count"]
        
        results["summary"] = {
            "total_files": len(results["files"]),
            "total_lines_of_code": total_lines,
            "total_cyclomatic_complexity": total_complexity,
            "total_functions": total_functions,
            "total_classes": total_classes
        }
        
        return results
    
    def calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """
        计算圈复杂度
        
        Args:
            tree: AST树
            
        Returns:
            圈复杂度
        """
        complexity = 1  # 基础复杂度为1
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, 
                                 ast.With, ast.Assert, ast.Break, ast.Continue)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # 每个布尔操作增加复杂度
                complexity += len(node.values) - 1
        
        return complexity

if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="代码复杂度分析")
    parser.add_argument('--directory', type=str, help='要分析的目录')
    parser.add_argument('--file', type=str, help='要分析的文件')
    parser.add_argument('--output', type=str, default='complexity_results.json', help='输出文件')
    
    args = parser.parse_args()
    
    analyzer = ComplexityAnalyzer()
    
    if args.directory:
        results = analyzer.analyze_directory(args.directory)
    elif args.file:
        results = analyzer.analyze_file(args.file)
    else:
        print("请指定要分析的目录或文件")
        exit(1)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"复杂度分析结果已保存到: {args.output}")
