import os
import platform
import re
from typing import List, Set


# /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pip install --upgrade pip
# C:\ProgramData\miniconda3\python.exe -m pip install --upgrade pip


def smart_split(text):  # 匹配除了URL协议外的冒号
    pattern = r'(?<!://):(?!//)'
    return re.split(pattern, text)


def show_envs():
    for k, v in os.environ.items():
        print(f"{k} ------> ", end="")
        es: List[str] = v.split(";")
        for c, e in enumerate(es):
            if e == "":
                continue
            if c > 1:
                print(f" " * (len(k) + 9), end="")
            print(e)


def show_envs2():
    for k, v in os.environ.items():
        print(f"{k} ------> ", end="")
        es: List[str] = smart_split(v)
        for c, e in enumerate(es):
            if e == "":
                continue
            if c > 0:
                print(f" " * (len(k) + 9), end="")
            print(e)


def main():
    print("\n")
    ps = platform.system().lower()
    if ps == "windows":
        show_envs()
    elif ps == "linux":
        show_envs2()
    elif ps == "darwin":  # macOS
        key_files: Set[str] = {
            # 系统
            "/etc/profile",
            "/etc/paths",
            "/etc/paths.d/homebrew",
            # 用户
            "/Users/wangxiao/.bash_profile",
            "/Users/wangxiao/.zprofile",
            "/Users/wangxiao/.zprofile.pysave",
            "/Users/wangxiao/.zshrc",
        }
        show_envs2()
    else:
        pass


if __name__ == "__main__":
    main()
