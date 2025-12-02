import os
import platform
import sys
from pathlib import Path
from typing import Set


# C:\ProgramData\miniconda3\python.exe -m pip install --upgrade pip
# C:\ProgramData\miniconda3\python.exe -m pip install

def generate_new_name(f_n: str, ext: str, existing_names, existing_names_to_dir: Set[str]):
    name: str = f"{f_n}{ext}"
    if name not in existing_names_to_dir:
        return name, False  # 没改
    counter: int = 2
    while True:
        new_name: str = f"{f_n}_{counter}{ext}"
        if new_name not in existing_names:
            existing_names.add(new_name)
            return new_name, True  # 改过
        counter += 1


def rename_files(f_dir: str, to_dir: str):
    existing_names: Set[str] = set()  # 两个文件夹所有的已知文件名
    existing_names_to_dir: Set[str] = set()
    for f0 in os.listdir(f_dir):
        if f0 == ".DS_Store" or f0.startswith("."):
            continue
        if os.path.isdir(os.path.join(f_dir, f0)):
            continue
        existing_names.add(f0)

    for f1 in os.listdir(to_dir):
        if f1 == ".DS_Store" or f1.startswith("."):
            continue
        if os.path.isdir(os.path.join(f_dir, f1)):
            continue
        existing_names.add(f1)
        existing_names_to_dir.add(f1)

    # 重命名
    for f2 in os.listdir(f_dir):
        if f2 == ".DS_Store" or f2.startswith("."):
            continue
        if os.path.isdir(os.path.join(f_dir, f2)):
            continue
        ext: str = Path(f2).suffix
        if ext == ".ini":
            continue

        f_n: str = f2.rstrip(ext)  # 文件原来的后缀
        new_name, flag = generate_new_name(f_n, ext, existing_names, existing_names_to_dir)

        if flag:  # 改过名字
            old_path: str = os.path.join(f_dir, f2)
            old_path_after_rename: str = os.path.join(f_dir, new_name)
            new_path: str = os.path.join(to_dir, new_name)
            if not os.path.exists(new_path):  # 新文件夹尚不存在此文件名，可以用
                os.rename(old_path, old_path_after_rename)
                print(f"重命名: {f2} -> {new_name}")
            else:
                print(f"错误！新文件夹已存在此文件名：{f2}->{new_name}")
                sys.exit(-1)
        else:  # 名字没变
            new_path: str = os.path.join(to_dir, f2)
            if not os.path.exists(new_path):  # 新文件夹尚不存在此文件名，可以用
                print(f"直接移: {f2}")
            else:
                print(f"错误！新文件夹已存在此文件名：{f2}")
                sys.exit(-1)


def main():
    ps = platform.system().lower()
    if ps == "windows":
        f_dir: str = r"C:\Users\wangxiao\Downloads\Phone Link"
        to_dir: str = r"G:\6\手机3\别人的"
    elif ps == "linux":
        f_dir: str = ""
        to_dir: str = ""
    elif ps == "darwin":  # macOS
        f_dir: str = "/Users/wangxiao/Downloads"
        to_dir: str = "/Volumes/RTL9210/6/手机3/别人的"
    else:
        f_dir: str = ""
        to_dir: str = ""

    rename_files(f_dir, to_dir)
    print(f"\n\n接下来你可以将：\n    {f_dir}\n中的文件，拖到：\n    {to_dir}\n中，而不会担心提示有相同文件了")


if __name__ == "__main__":
    main()
