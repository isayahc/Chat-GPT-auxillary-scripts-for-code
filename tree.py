import os
import argparse

def tree(startpath, exclude_dirs=None):
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
        indent = ' ' * 4 * (level - 1)
        subindent = ' ' * 4 * level

        # Print directory
        if level > 0:
            print('{}├───{}/'.format(indent, os.path.basename(root)))

        # Print files
        for i, f in enumerate(sorted(files)):
            prefix = '├───' if i != len(files) - 1 else '└───'
            print('{}{}{}'.format(subindent, prefix, f))


def process_paths(path):
    return path.replace(".\\", "")

if __name__ == "__main__":  
  parser = argparse.ArgumentParser()  

  parser.add_argument("startpath", nargs='?', default=".", type=str, help="The start path for the tree. Defaults to the current directory.")  
  parser.add_argument("-e", "--exclude", nargs='*', default=["venv"], type=process_paths, 
                      help="List of directories to exclude. Defaults to the ['venv'] directory. If multiple directories, separate them by space.")  

  args = parser.parse_args()  

  tree(args.startpath, args.exclude)
