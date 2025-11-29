import os
import platform
import sys
from typing import List

import send2trash


class Handle:
    def __init__(self):
        self.junk: List[str] = []

    def find_mac_junk_files(self, parent_dir):
        for root, dirs, files in os.walk(parent_dir):
            for file in files:
                if file == ".DS_Store":  # or file.startswith("._")
                    file_path = os.path.join(root, file)
                    self.junk.append(file_path)

    def delete_files(self):
        for file_path in self.junk:
            try:
                send2trash.send2trash(file_path)
                print(f"已放入回收站：{file_path}")
            except Exception as e:
                print(f"删文件出错：{file_path}: {e}")
                sys.exit(-1)

    def handle(self, parent_dir: str):
        if parent_dir == "":
            sys.exit(-1)
        if not os.path.exists(parent_dir):
            sys.exit(-1)
        print("正在扫描文件...")
        self.find_mac_junk_files(parent_dir)
        if len(self.junk) == 0:
            print("未找到需要删除的文件")
            sys.exit(-1)
        print(f"找到 {len(self.junk)} 个需要删除的文件：")
        for file in self.junk:
            print(f"  {file}")
        # 确认
        confirm = input(f"\n确定要删除这 {len(self.junk)} 个文件吗？(yes/no): ")
        if confirm.lower() != 'yes':
            print("操作已取消")
            sys.exit(-1)
        # 执行删除
        self.delete_files()
        print(f"\n操作完成！")


def main():
    h = Handle()
    ps = platform.system().lower()
    if ps == "windows":
        dir: str = r"G:\\"
    elif ps == "linux":
        dir: str = ""
    elif ps == "darwin":  # macOS
        dir: str = "/Volumes/RTL9210"
        print("\n1.mac不会放回收站，直接删除\n2.mac只能适用于外部存储，本身系统里存在.DS_Store是正常的，比如系统盘的“我的坚果云”，不能乱删\n")
    else:
        dir: str = ""

    h.handle(dir)


if __name__ == "__main__":
    main()
