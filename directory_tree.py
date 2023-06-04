"""
A script to display the directory tree structure of a given path in the console.

This script accepts a path and several optional parameters to customize the output. It walks through the directory tree
and prints the structure in a clear and legible way. It provides options to exclude certain directories, filter files by
type, limit the depth of the tree, include file sizes, include file modification times, and sort files by modification
time.

This script uses the built-in `os` module for filesystem operations and the `argparse` module for command-line argument
parsing. It also uses the `fnmatch` module to support file name filtering.

Example usage:
    python directory_structure.py --startpath ./my_project --exclude venv .git --filter *.py --depth 3 --sizes --times --sort

Functions:
    print_directory_structure: The main function that prints the directory tree structure.
    process_paths: A helper function that cleans up paths in command-line arguments.

If executed as a script, it uses argparse to parse command-line arguments and calls `print_directory_structure` with
the appropriate parameters.

Author: Your Name
Date: 2023-06-02
"""

import os
import argparse
import fnmatch

def print_directory_structure(startpath, exclude_dirs=None, file_filter=None, max_depth=None, include_sizes=False, include_times=False, sort_by_time=False):
    """
    Recursively displays the directory tree structure starting from the specified path.

    Args:
        startpath (str): The path to the root directory to display the tree structure from.
        exclude_dirs (list[str], optional): Directories to exclude from the tree structure. Defaults to None.
        file_filter (str, optional): Filter for file names. Only files matching the filter will be displayed. Defaults to None.
        max_depth (int, optional): Maximum depth of the tree structure. Directories beyond this depth will be excluded. Defaults to None.
        include_sizes (bool, optional): Flag to include file sizes in the output. Defaults to False.
        include_times (bool, optional): Flag to include file modification times in the output. Defaults to False.
        sort_by_time (bool, optional): Flag to sort files by modification time. Defaults to False.

    Returns:
        None

    Prints the directory tree structure to the console.
    """
    if exclude_dirs is None:
        exclude_dirs = []

    # Normalize startpath and exclude_dirs for the current OS
    startpath = os.path.normpath(startpath)
    exclude_dirs = [os.path.normpath(d) for d in exclude_dirs]

    # Print root directory
    print(os.path.basename(startpath))
    for root, dirs, files in os.walk(startpath):
        # Exclude directories specified in exclude_dirs
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        level = root.replace(startpath, '').count(os.sep)
        if max_depth is not None and level > max_depth:
            continue

        indent = ' ' * 4 * (level - 1)
        subindent = ' ' * 4 * level

        # Print directory
        if level > 0:
            print('{}├───{}/'.format(indent, os.path.basename(root)))

        # Filter files if needed
        if file_filter:
            files = fnmatch.filter(files, file_filter)

        # Sort files by modification time if needed
        if sort_by_time:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(root, x)))

        # Print files
        for i, f in enumerate(sorted(files)):
            details = []
            if include_sizes:
                size = os.path.getsize(os.path.join(root, f))
                details.append(f"{size} bytes")
            if include_times:
                mtime = os.path.getmtime(os.path.join(root, f))
                details.append(f"Modified: {mtime}")
            prefix = '├───' if i != len(files) - 1 else '└───'
            print('{}{}{} {}'.format(subindent, prefix, f, ' '.join(details)))


def process_paths(path):
    return path.replace(".\\", "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("startpath", nargs='?', default=".", type=str, help="The start path for the tree. Defaults to the current directory.")
    parser.add_argument("-e", "--exclude", nargs='*', default=["venv", ".git", "pycache", ".pytest_cache/","__pycache__"], type=process_paths,
                        help="List of directories to exclude. Defaults to the ['venv'] directory. If multiple directories, separate them by space.")
    parser.add_argument("-f", "--filter", type=str, help="File type filter (e.g. '*.py' for Python files)")
    parser.add_argument("-d", "--depth", type=int, help="Max depth of the displayed tree")
    parser.add_argument("-s", "--sizes", action='store_true', help="Include file sizes in the output")
    parser.add_argument("-t", "--times", action='store_true', help="Include file modification times in the output")
    parser.add_argument("--sort", action='store_true', help="Sort files by modification time")

    args = parser.parse_args()

    print_directory_structure(args.startpath, args.exclude, args.filter, args.depth, args.sizes, args.times, args.sort)
