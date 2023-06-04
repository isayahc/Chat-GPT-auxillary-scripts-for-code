"""
This module provides the `PythonCodeAnalyzer` class for analyzing Python code.

The `PythonCodeAnalyzer` class uses Python's abstract syntax trees (ASTs) to extract
information about functions and methods from a Python file. The details include function
signature (arguments and return type), docstring, dependencies, and whether the function
is an entry point (i.e., the function is named "__main__").

The module also provides a script interface. When run as a script, it uses command line
arguments to specify the Python file or directory to analyze, and other options.

The script usage is as follows:
    python python_code_analyzer.py -f <file>       # to analyze a single file
    python python_code_analyzer.py -d <directory> # to analyze all files in a directory
    Options:
        -c, --classattrs        Include class attributes in the analysis
        --include-venv          Include the venv directory in the analysis
        --exclude-docstrings    Exclude docstrings in the analysis
        --focus-docstrings      Focus on docstrings in the analysis

Note: The module provides a function to retrieve the module-level docstring from a Python
file. It only works for module-level docstrings that are defined as a string literal at the
top of the file. It won't work for docstrings that are dynamically generated or assigned to 
a variable before being assigned to __doc__. However, such practices are rare and not recommended.
"""


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
        
        if args.exclude_docstrings:
            func_details[func_name].pop('docstring', None)
        elif args.focus_docstrings:
            for key in list(func_details[func_name].keys()):
                if key != 'docstring':
                    func_details[func_name].pop(key, None)
        
        return func_details

    def handle_classdef(self, node: ast.ClassDef) -> Dict[str, Any]:
        """
        Handle a ClassDef node and extract class details.

        Args:
            node (ast.ClassDef): The ClassDef node to handle.

        Returns:
            Dict[str, Any]: A dictionary with class details.
        """
        class_details = {}
        for sub_node in node.body:
            class_details.update(self.get_func_details(sub_node, class_name=node.name))
        if self.include_class_attrs:
            class_details['class_attributes'] = [ast.unparse(attr) for attr in node.body if isinstance(attr, ast.Assign)]
        return class_details

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
    
    def get_module_docstring(self, filepath: str) -> Optional[str]:
        """
        Get the module-level docstring from a Python file.

        This approach only works for module-level docstrings that are defined as 
        a string literal at the top of the file. It won't work for docstrings that 
        are dynamically generated or assigned to a variable before being assigned 
        to __doc__. However, such practices are rare and not recommended.

        Args:
            filepath (str): The path to the Python file.

        Returns:
            Optional[str]: The module-level docstring, if it exists. Otherwise, None.
            """

        with open(filepath, 'r') as file:
            module = ast.parse(file.read())
            
        if module.body and isinstance(module.body[0], ast.Expr) and isinstance(module.body[0].value, ast.Str):
            return module.body[0].value.s
        
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get function details from a Python file.')
    parser.add_argument('-f', '--file', type=str, help='The Python file to analyze.')
    parser.add_argument('-d', '--directory', type=str, help='The directory containing Python files to analyze.')
    parser.add_argument('-c', '--classattrs', action='store_true', help='Include class attributes in the analysis.')
    parser.add_argument('--include-venv', action='store_true', default=False, help="Include the venv directory in the analysis")
    parser.add_argument('--exclude-docstrings', action='store_true', default=False, help="Exclude docstrings in the analysis")
    parser.add_argument('--focus-docstrings', action='store_true', default=False, help="Focus on docstrings in the analysis")

    # Add mutually exclusive group for docstring actions
    docstring_group = parser.add_mutually_exclusive_group()
    docstring_group.add_argument('--add-docstring', action='store_true', default=False, help="Add a module-level docstring")
    docstring_group.add_argument('--print-docstring', action='store_true', default=False, help="Print the module-level docstring and exit")

    args = parser.parse_args()
    
    if args.exclude_docstrings and args.focus_docstrings:
        raise ValueError("The flags --exclude-docstrings and --focus-docstrings cannot be used together")

    analyzer = PythonCodeAnalyzer(include_class_attrs=args.classattrs)

    # Handle docstring actions
    if args.print_docstring:
        if args.file:
            print(analyzer.get_module_docstring(args.file))
            exit()
        elif args.directory:
            for root, _, files in os.walk(args.directory):
                if "venv" in root and not args.include_venv:
                    continue

                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        print(f"\nFile: {filepath}")
                        print(analyzer.get_module_docstring(filepath))
            exit()

    # Continue with the rest of the analysis...
    try:
        if args.file:
            func_details = analyzer.analyze_python_file(args.file)
            print(f"\nFile: {args.file}")
            print(func_details)
        elif args.directory:
            for root, _, files in os.walk(args.directory):
                if "venv" in root and not args.include_venv:
                    continue

                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        print(f"\nFile: {filepath}")
                        print(analyzer.analyze_python_file(filepath))
    except ValueError as e:
        print(f"Error: {str(e)}")
