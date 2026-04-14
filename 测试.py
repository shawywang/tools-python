# 此电脑上安装了cairosvg，过程艰难

class File:
    def __init__(self):  # 初始化一个类
        self.file_name: str = ""
        self.age: int = 0
        self.high: float = 1.78

    def read_file(self, address: str):
        with open(address, 'r', encoding='utf-8', errors='ignore') as infile:
            content = infile.read()
        print(f"content = {content}")
        pass

    def handle_pictures(self):
        pass

    def show_pictures(self):
        age = 6
        print(age)
        print(self.age)
        pass


def make_calendar():
    a = 5
    print(a)
    pass


def main():
    people = File()
    people.read_file(address="/Users/wangxiao/Downloads/test.txt")
    print(people.age)

    # print(f"CairoSVG版本：{cairosvg.__version__}")
    # name: str = "DAHUITU"
    # age: int = 27
    # high: float = 1.78
    # print(f"姓名：{name}，年龄：{age}，身高：{high}")
    #
    # print(f"将{name}变成小写：{name.lower()}")


if __name__ == '__main__':
    main()
# 管理员运行：C:\ProgramData\miniconda3\python.exe -m pip install pillow svgelements cairosvg pycairo cairocffi==0.8
"""
io
12
"""
