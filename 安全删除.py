import os
from typing import List

import send2trash


def safe_delete_file(file_p: str):  # 输入单个文件全路径
    if os.path.isfile(file_p):
        print(f"即将删除{file_p}")
        confirm = input("确认删除？输入YES")
        if confirm == "YES":
            try:
                send2trash.send2trash(file_p)
                print("已放入回收站")
            except Exception as e:
                print(f"删除失败{e}")
        else:
            print("取消操作")


def safe_delete_files(folder_p: str):  # 输入文件夹路径，将遍历并删掉文件夹里所有文件
    if os.path.isdir(folder_p):
        to_delete: List[str] = []
        for f in os.listdir(folder_p):
            file_path = os.path.join(folder_p, f)
            if os.path.isfile(file_path):
                print(f"即将删除：{file_path}")
                to_delete.append(f"{file_path}")
        if len(to_delete) > 0:
            confirm = input("确认删除？输入YES")
            if confirm == "YES":
                for f in to_delete:
                    send2trash.send2trash(f)
                print("已放入回收站")
            else:
                print("取消操作")


def safe_delete_dir(folder_p: str):  # 输入文件夹路径，直接删掉文件夹
    if os.path.isdir(folder_p):
        print(f"即将删除{folder_p}")
        confirm = input("确认删除？输入YES")
        if confirm == "YES":
            try:
                send2trash.send2trash(folder_p)
                print("已放入回收站")
            except Exception as e:
                print(f"删除失败{e}")
        else:
            print("取消操作")


def main():
    safe_delete_files(r"C:\Users\wangxiao\不参与同步文件\code")


if __name__ == "__main__":
    main()
# 管理员运行：C:\ProgramData\miniconda3\python.exe -m pip install send2trash
# 所有shutil.rmtree()都应该替换为send2trash.send2trash()
