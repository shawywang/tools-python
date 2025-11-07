import os
import re
import shutil
from typing import Set

import pypinyin

SplitWithABlankLine = r'\n\n+'  # 空行分割块
SplitWithLineBreak = r'\n'  # 换行分割块

SortWithLineBreaks = '\n'  # 换行排序分割
SortWithColon = '：'  # 冒号排序分割

WriteUseBlankLine = '\n\n'  # 写入空行分割
WriteUseLineBreak = '\n'  # 写入换行分割


class Backup:
    def __init__(self):
        self.files = None
        self.files_name = []
        self.backup_path = None

    def set_files(self, files: Set[str], backup_path: str):
        self.files = files
        self.backup_path = backup_path
        for s in self.files:
            self.files_name.append(s.split('\\')[len(s.split('\\')) - 1])

    def clear_old_backup(self):
        # 删除指定目录中的指定文件
        if os.path.exists(self.backup_path):
            for f in os.listdir(self.backup_path):
                if f in self.files_name:
                    f_path = os.path.join(self.backup_path, f)
                    try:
                        if os.path.isfile(f_path):
                            os.remove(f_path)
                    except Exception as e:
                        print(f"删除备份文件：{f_path}时发生错误: {e}")

    def make_backup(self):
        for f in self.files:
            if os.path.exists(f):
                # 复制文件
                shutil.copy2(f, self.backup_path)
                print(f"已复制文件 {f} 到 {self.backup_path}")
            else:
                print(f"文件不存在：{f}")


class Partition:
    def __init__(self):
        self.files = None
        self.block = None  # 块分隔符
        self.sort = None  # 排序分割符
        self.write = None  # 写入换行符

    def set_files(self, files: Set[str]):
        self.files = files

    def op(self, t: int):
        if t == 1:
            self.block = SplitWithABlankLine
            self.sort = SortWithLineBreaks
            self.write = WriteUseBlankLine
            return Operation(self)
        if t == 2:
            self.block = SplitWithLineBreak
            self.sort = SortWithColon
            self.write = WriteUseLineBreak
            return Operation(self)
        return


class Operation:
    def __init__(self, pa: Partition):
        self.pa = pa

    def blocks_sort(self):
        for file in self.pa.files:
            with open(file, 'r', encoding='utf-8') as f:
                # 删除文件开头无意义的空行
                content = f.read().lstrip()
                # 分割出块
                blocks = re.split(self.pa.block, content)
            # 删除空白块block
            blocks = [block for block in blocks if block.strip()]
            # 按照每个块的第一行进行排序
            blocks = sorted(blocks, key=lambda x: pypinyin.lazy_pinyin(x.split(self.pa.sort)[0], style='normal'))
            # 将排序后的块重新写入文件
            with open(file, 'w', encoding='utf-8') as f:
                f.write(self.pa.write.join(blocks))
            print(f"===>已完成文件修改：：{f}")


def main():
    backup_path = "C:\\Users\\wangxiao\\Nutstore\\1\\我的坚果云\\我的文档\\个人\\密码修改前备份"
    file_1 = {"C:\\Users\\wangxiao\\Nutstore\\1\\我的坚果云\\我的文档\\个人\\密码-国内.txt",
              "C:\\Users\\wangxiao\\Nutstore\\1\\我的坚果云\\我的文档\\个人\\密码-国外.txt",
              "C:\\Users\\wangxiao\\Nutstore\\1\\我的坚果云\\我的文档\\个人\\密码-金融、支付.txt",
              "C:\\Users\\wangxiao\\Nutstore\\1\\我的坚果云\\我的文档\\个人\\密码-其它、不常用.txt"}
    file_2 = {"C:\\Users\\wangxiao\\Nutstore\\1\\我的坚果云\\我的文档\\个人\\浏览器收藏.txt"}

    # 备份
    b = Backup()
    b.set_files(file_1, backup_path)
    b.clear_old_backup()
    b.make_backup()
    # 修改
    p = Partition()
    p.set_files(file_1)
    p.op(1).blocks_sort()

    # ===================
    # 备份
    b = Backup()
    b.set_files(file_2, backup_path)
    b.clear_old_backup()
    b.make_backup()
    # 修改
    p = Partition()
    p.set_files(file_2)
    p.op(2).blocks_sort()


if __name__ == '__main__':
    main()
