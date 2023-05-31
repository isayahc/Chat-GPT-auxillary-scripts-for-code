"""
A Python script to analyze Python files in a directory and extract details about its functions, methods, dependencies, and entry points.

Usage: python python_code_analyzer.py <directory-to-analyze>
"""

import ast
import argparse
import os
from typing import Optional, Dict, Any


def get_func_details(node: ast.AST, class_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Recursively traverse an AST node to extract function/method details, including dependencies and entry points.

    :param node: The AST node to analyze
    :param class_name: The name of the class if the node is a method
    :return: A dictionary with function/method details
    """
    func_details = {}

    if isinstance(node, ast.FunctionDef):
        # Extract function/method details
        func_name = f"{class_name}.{node.name}" if class_name else node.name
        func_details[func_name] = {
            'args': {arg.arg: ast.unparse(arg.annotation) if arg.annotation else None for arg in node.args.args},
            'return': ast.unparse(node.returns) if node.returns else None,
            'docstring': ast.get_docstring(node),
            'dependencies': [],
            'entry_point': class_name is None and node.name == '__main__',
        }
    elif isinstance(node, ast.ClassDef):
        # Extract class method details
        for sub_node in node.body:
            func_details.update(get_func_details(sub_node, class_name=node.name))
    elif isinstance(node, ast.Call):
        # Extract dependencies
        if isinstance(node.func, ast.Name):
            func_details['dependencies'].append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            func_details['dependencies'].append(node.func.attr)
    elif isinstance(node, ast.Module):
        # Check for any nested functions or classes
        for sub_node in node.body:
            func_details.update(get_func_details(sub_node))

    return func_details


def analyze_python_file(filepath: str) -> Dict[str, Any]:
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

    return get_func_details(module)


def analyze_python_directory(directory: str):
    """
    Analyze all Python files in a directory and extract details about their functions, methods, dependencies, and entry points.

    :param directory: The path to the directory
    :return: None
    """
    if not os.path.isdir(directory):
        raise ValueError(f"{directory} does not exist")

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    func_details = analyze_python_file(filepath)
                    print(f"{filepath}:")
                    print(func_details)
                except ValueError as e:
                    print(f"Error with {filepath}: {str(e)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get function details from Python files.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', type=str, help='The Python file to analyze.')
    group.add_argument('--directory', type=str, help='The directory of Python files to analyze.')
    args = parser.parse_args()

    if args.file:
        try:
            func_details = analyze_python_file(args.file)
            print(func_details)
        except ValueError as e:
            print(f"Error: {str(e)}")
    elif args.directory:
        analyze_python_directory(args.directory)
