import os
from pathlib import Path
from typing import Set


# C:\ProgramData\miniconda3\python.exe -m pip install --upgrade pip
# C:\ProgramData\miniconda3\python.exe -m pip install

def generate_new_name(f_n: str, ext: str, existing_names: Set[str]) -> str:
    name: str = f"{f_n}{ext}"
    if name not in existing_names:
        existing_names.add(name)
        return name
    counter: int = 2
    while True:
        new_name: str = f"{f_n}_{counter}{ext}"
        if new_name not in existing_names:
            existing_names.add(new_name)
            return new_name
        counter += 1


def rename_files(f_dir: str, to_dir: str):
    existing_names: Set[str] = set()
    for f in os.listdir(to_dir):
        existing_names.add(f)
    for f in os.listdir(f_dir):
        ext: str = Path(f).suffix
        if ext == ".ini":
            continue
        f_n: str = f.rstrip(ext)  # 文件原来的后缀
        new_name: str = generate_new_name(f_n, ext, existing_names)

        old_path: str = os.path.join(f_dir, f)
        new_path: str = os.path.join(f_dir, new_name)
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print(f"重命名: {f} -> {new_name}")
        else:
            print(f"警告！文件已存在，跳过：{f} -> {new_name}")


def main():
    # 文件名将被修改的所在目录
    # f_dir: str = "/Users/wangxiao/Downloads/临时"
    f_dir: str = r"C:\Users\wangxiao\Downloads\Phone Link"

    # 如上文件待合入的目录，不会做任何修改
    # to_dir: str = "/Volumes/RTL9210/6/手机3"
    to_dir: str = r"G:\6\手机3\别人的"

    rename_files(f_dir, to_dir)
    print(f"\n\n接下来你可以将：\n    {f_dir}\n中的文件，拖到：\n    {to_dir}\n中，而不会担心提示有相同文件了")


if __name__ == "__main__":
    main()
