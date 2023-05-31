import ast
import argparse
import os


def get_func_details(filepath):
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

    func_details = {}

    # Traverse the top-level statements in the AST
    for node in module.body:
        if isinstance(node, ast.FunctionDef):
            func_details[node.name] = {'args': {}, 'return': None}

            # Get arguments and their annotations if present
            for arg in node.args.args:
                arg_type = ast.unparse(arg.annotation) if arg.annotation else None
                func_details[node.name]['args'][arg.arg] = arg_type

            # Get return annotation if present
            if node.returns:
                return_type = ast.unparse(node.returns)
                func_details[node.name]['return'] = return_type

    return func_details


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get function details from a Python file.')
    parser.add_argument('file', type=str, help='The Python file to analyze.')

    args = parser.parse_args()

    try:
        func_details = get_func_details(args.file)
        print(func_details)
    except ValueError as e:
        print(f"Error: {str(e)}")
