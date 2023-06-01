"""
A Python script to analyze another Python file and extract details about its functions, methods, dependencies, and entry points.

Usage: 
For single file: python python_code_analyzer.py -f <file-to-analyze.py>
For directory: python python_code_analyzer.py -d <directory>
"""

import ast
import argparse
import os
from typing import Optional, Dict, Any

class PythonCodeAnalyzer:
    def __init__(self, include_class_attrs: bool = False):
        self.include_class_attrs = include_class_attrs

    def get_func_details(self, node: ast.AST, class_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Recursively traverse an AST node to extract function/method details.

        :param node: The AST node to analyze
        :param class_name: The name of the class if the node is a method
        :return: A dictionary with function/method details
        """
        if isinstance(node, ast.FunctionDef):
            return self.handle_functiondef(node, class_name)
        elif isinstance(node, ast.ClassDef):
            return self.handle_classdef(node)
        elif isinstance(node, ast.Call):
            return self.handle_call(node)
        elif isinstance(node, ast.Module):
            return self.handle_module(node)
        else:
            return {}

    def handle_functiondef(self, node, class_name):
        func_details = {}
        func_name = f"{class_name}.{node.name}" if class_name else node.name
        func_details[func_name] = {
            'args': {arg.arg: ast.unparse(arg.annotation) if arg.annotation else None for arg in node.args.args},
            'return': ast.unparse(node.returns) if node.returns else None,
            'docstring': ast.get_docstring(node),
            'dependencies': [],
            'entry_point': class_name is None and node.name == '__main__',
        }
        return func_details

    def handle_classdef(self, node):
        func_details = {}
        for sub_node in node.body:
            func_details.update(self.get_func_details(sub_node, class_name=node.name))
        if self.include_class_attrs:
            func_details['class_attributes'] = [ast.unparse(attr) for attr in node.body if isinstance(attr, ast.Assign)]
        return func_details

    def handle_call(self, node):
        func_details = {'dependencies': []}
        if isinstance(node.func, ast.Name):
            func_details['dependencies'].append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            func_details['dependencies'].append(node.func.attr)
        return func_details

    def handle_module(self, node):
        func_details = {}
        for sub_node in node.body:
            func_details.update(self.get_func_details(sub_node))
        return func_details

    def analyze_python_file(self, filepath: str) -> Dict[str, Any]:
        """
        Analyze a Python file and extract details about its functions, methods, dependencies, and entry points.

        :param filepath: The path to the Python file
        :return: A dictionary with function/method details
        :raises ValueError: If the file does not exist, is not a Python file, or contains syntax errors
        """
        if not os.path.isfile(filepath):
            raise ValueError(f"{filepath} does not exist")

        if not filepath.endswith('.py'):
            raise ValueError(f"{filepath} is not a Python file")

        with open(filepath, 'r') as file:
            try:
                module = ast.parse(file.read())
            except SyntaxError as e:
                raise ValueError(f"{filepath} contains syntax errors: {str(e)}")

        return self.get_func_details(module)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get function details from a Python file.')
    parser.add_argument('-f', '--file', type=str, help='The Python file to analyze.')
    parser.add_argument('-d', '--directory', type=str, help='The directory containing Python files to analyze.')
    parser.add_argument('-c', '--classattrs', action='store_true', help='Include class attributes in the analysis.')

    args = parser.parse_args()
    analyzer = PythonCodeAnalyzer(include_class_attrs=args.classattrs)

    try:
        if args.file:
            func_details = analyzer.analyze_python_file(args.file)
            print(func_details)
        elif args.directory:
            for root, _, files in os.walk(args.directory):
                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        print(f"\nFile: {filepath}")
                        func_details = analyzer.analyze_python_file(filepath)
                        print(func_details)
    except ValueError as e:
        print(f"Error: {str(e)}")
