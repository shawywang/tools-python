from os.path import isdir
from pathlib import Path


def print_tree(path, indent=""):
    if not isdir(path):
        print(indent + path.name)
    indent += "    "
    for item in sorted(path.iterdir()):
        if item.name.startswith("."):
            continue
        print(indent + "|----" + item.name)
        if item.is_dir():
            print_tree(item, indent + "    ")


if __name__ == "__main__":
    dir_path = "/Users/wangxiao/Documents/github/tools-python"
    print("")
    print_tree(Path(dir_path))
