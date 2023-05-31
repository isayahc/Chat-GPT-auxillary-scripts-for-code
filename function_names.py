import ast
import argparse
import os


def get_func_details(node, class_name=None):
    func_details = {}

    if isinstance(node, ast.FunctionDef):
        # Extract function/method details
        func_name = f"{class_name}.{node.name}" if class_name else node.name
        func_details[func_name] = {
            'args': {arg.arg: ast.unparse(arg.annotation) if arg.annotation else None for arg in node.args.args},
            'return': ast.unparse(node.returns) if node.returns else None,
            'docstring': ast.get_docstring(node)
        }
    elif isinstance(node, ast.ClassDef):
        # Extract class method details
        for sub_node in node.body:
            func_details.update(get_func_details(sub_node, class_name=node.name))

    # Check for any nested functions or classes
    if isinstance(node, ast.Module):
        for sub_node in node.body:
            func_details.update(get_func_details(sub_node))

    return func_details


def analyze_python_file(filepath):
    # Check if the file exists
    if not os.path.isfile(filepath):
        raise ValueError(f"{filepath} does not exist")

    # Check if the file is a Python file
    if not filepath.endswith('.py'):
        raise ValueError(f"{filepath} is not a Python file")

    with open(filepath, 'r') as file:
        try:
            # Parse the file to an Abstract Syntax Tree (AST)
            module = ast.parse(file.read())
        except SyntaxError as e:
            raise ValueError(f"{filepath} contains syntax errors: {str(e)}")

    return get_func_details(module)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get function details from a Python file.')
    parser.add_argument('file', type=str, help='The Python file to analyze.')

    args = parser.parse_args()

    try:
        func_details = analyze_python_file(args.file)
        print(func_details)
    except ValueError as e:
        print(f"Error: {str(e)}")
