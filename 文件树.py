from pathlib import Path


def print_tree(path, indent=""):
    if not path.exists():
        print(f"路径不存在：{path}")
        return
    if path.is_file():
        return
    indent += "    "
    for item in sorted(path.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_dir():
            print(indent + "|----" + item.name + "\\")
            print_tree(item, indent + "    ")
        else:
            print(indent + "|----" + item.name)


if __name__ == "__main__":
    # dir_path = "/Volumes/RTL9210/高中教材"
    dir_path = "/Volumes/RTL9210/电影"
    print_tree(Path(dir_path))
