# Chat-GPT Auxiliary Scripts for Code

This Python project contains two primary components:

1. **Python Code Analyzer**: A script that analyzes Python code to extract details about functions and methods, including arguments, return types, docstrings, dependencies, and whether they are entry points. It also supports class methods and nested functions.

2. **Directory Tree Printer**: A script that prints the directory tree for a given path, with options to exclude directories, filter by file type, limit the depth, include file sizes and modification times, and sort by modification time.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/isayahc/Chat-GPT-auxillary-scripts-for-code.git
```

2. Navigate to the project directory:

```bash
cd Chat-GPT-auxillary-scripts-for-code
```

3. Ensure you have Python 3.8 or later installed. You can verify this with `python --version`.

## Usage

### Python Code Analyzer

To use the Python Code Analyzer, run the script with a Python file as an argument:

```bash
python python_code_analyzer.py <filename>.py
```

This will print out a dictionary detailing each function and method in the file.

### Directory Tree Printer

To use the Directory Tree Printer, run the script with the directory you want to print:
```bash
python directory_tree_printer.py <directory_path>
```
You can customize the output with various options:
- `-f "*.py"` or `--filter "*.py"` to filter by file type (e.g., "*.py" for Python files)
- `-d 2` or `--depth 2` to limit the depth of the directory tree
- `-s` or `--size` to include file sizes
- `--sort` to sort the files by modification time

For example, to print only Python files up to a depth of 2, include file sizes, and sort by modification time, you would run:

```bash
python directory_tree_printer.py <directory_path> -f "*.py" -d 2 -s --sort
```

## Contributing
If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcome.

## License
This project is licensed under the terms of the MIT license.
