# 此电脑上安装了cairosvg，过程艰难
import cairosvg


def main():
    print(f"CairoSVG版本：{cairosvg.__version__}")


if __name__ == '__main__':
    main()
# 管理员运行：C:\ProgramData\miniconda3\python.exe -m pip install pillow svgelements cairosvg pycairo cairocffi==0.8
