import ast
import argparse
import os
from typing import Optional, Dict, Any

class PythonCodeAnalyzer:
    def __init__(self, include_class_attrs: bool = True):
        """
        Initialize the PythonCodeAnalyzer.

        Args:
            include_class_attrs (bool, optional): Whether to include class attributes in the analysis. Defaults to True.
        """
        self.include_class_attrs = include_class_attrs
        self.package_details = {}

    def get_func_details(self, node: ast.AST, class_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Recursively traverse an AST node to extract function/method details.

        Args:
            node (ast.AST): The AST node to analyze.
            class_name (str, optional): The name of the class if the node is a method.

        Returns:
            Dict[str, Any]: A dictionary with function/method details.
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

    def handle_functiondef(self, node: ast.FunctionDef, class_name: Optional[str]) -> Dict[str, Any]:
        """
        Handle a FunctionDef node and extract function details.

        Args:
            node (ast.FunctionDef): The FunctionDef node to handle.
            class_name (Optional[str]): The name of the class if the node is a method.

        Returns:
            Dict[str, Any]: A dictionary with function details.
        """
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

    def handle_classdef(self, node: ast.ClassDef) -> Dict[str, Any]:
        """
        Handle a ClassDef node and extract class details.

        Args:
            node (ast.ClassDef): The ClassDef node to handle.

        Returns:
            Dict[str, Any]: A dictionary with class details.
        """
        func_details = {}
        for sub_node in node.body:
            func_details.update(self.get_func_details(sub_node, class_name=node.name))
        if self.include_class_attrs:
            func_details['class_attributes'] = [ast.unparse(attr) for attr in node.body if isinstance(attr, ast.Assign)]
        return func_details

    def handle_call(self, node: ast.Call) -> Dict[str, Any]:
        """
        Handle a Call node and extract dependency details.

        Args:
            node (ast.Call): The Call node to handle.

        Returns:
            Dict[str, Any]: A dictionary with dependency details.
        """
        func_details = {'dependencies': []}
        if isinstance(node.func, ast.Name):
            func_details['dependencies'].append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            func_details['dependencies'].append(node.func.attr)
        return func_details

    def handle_module(self, node: ast.Module) -> Dict[str, Any]:
        """
        Handle a Module node and extract function details.

        Args:
            node (ast.Module): The Module node to handle.

        Returns:
            Dict[str, Any]: A dictionary with function details.
        """
        func_details = {}
        for sub_node in node.body:
            func_details.update(self.get_func_details(sub_node))
        return func_details

    def analyze_python_file(self, filepath: str) -> Dict[str, Any]:
        """
        Analyze a Python file and extract details about its functions, methods, dependencies, and entry points.

        Args:
            filepath (str): The path to the Python file.

        Returns:
            Dict[str, Any]: A dictionary with function/method details.

        Raises:
            ValueError: If the file does not exist, is not a Python file, or contains syntax errors.
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
    parser.add_argument('--include-venv', action='store_true', default=False, help="Include the venv directory in the analysis")

    args = parser.parse_args()
    analyzer = PythonCodeAnalyzer(include_class_attrs=args.classattrs)

    try:
        if args.file:
            func_details = analyzer.analyze_python_file(args.file)
            print(f"\nFile: {args.file}")
            print(func_details)
        elif args.directory:
            for root, _, files in os.walk(args.directory):
                # Skip venv directory if the flag is not set
                if "venv" in root and not args.include_venv:
                    continue

                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        print(f"\nFile: {filepath}")
                        print(analyzer.analyze_python_file(filepath))
    except ValueError as e:
        print(f"Error: {str(e)}")

