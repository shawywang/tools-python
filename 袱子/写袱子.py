# 管理员运行：
# python -m pip install --upgrade pip
# Install-Module PSReadLine -MinimumVersion 2.0.3 -Scope CurrentUser -Force
# pip install pillow svgelements cairosvg cairocffi==0.8
# pycairo用不上
# 安装字体：98WB-V.otf、98WB-U.otf以查看未显示字根
# 1.brew install libraqm freetype harfbuzz fribidi
# 2.pip uninstall Pillow
# 3.pip install --upgrade Pillow --global-option="build_ext" --global-option="--enable-raqm" --no-binary=Pillow
import platform
import sys
from typing import Dict, List

from PIL import Image, ImageDraw, ImageFont

ps = platform.system().lower()

wangxiao_wangyunhui: List[List[str]] = [
    ["孙(男/女)王(骁/云慧)", "祖父王公(讳)汝上老大人一位收用"],
    ["曾孙(男/女)王(骁/云慧)", "曾祖(父/母)王公(讳)(守玺/怀美)老(大/孺)人二位收用"],
    ["玄孙(男/女)王(骁/云慧)", "高祖(父/母)王公(讳)(尚安/陈君)老(大/孺)人二位收用"],
    ["孝男王永(雄/开/跃)孝孙(男/女)(王定海/毛勇/刘位/王雪莲/王雪萍)孝孙(媳/婿)(陈晓丽/侯富馨)", "慈母王(宅)朱君寄春老孺人一位收用"],
]

size: List[Dict[int, int]] = [
    {10: 5},
    {10: 5},
    {10: 5},
    {10: 5},
    {10: 5},
    {10: 5},
]


class Handle:
    def __init__(self):
        pass

    def gen_content(self):
        pass

    def draw(self, text: str, width: int = 700, height: int = 700):
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # 加圆角边框
        draw.rounded_rectangle(
            xy=[0, 0, width, height],
            fill=None,  # 不填充
            outline="black",
            width=3,  # 边框宽度
            radius=20,  # 圆角半径
        )

        # 绘制字根
        font = ImageFont.truetype("/Users/wangxiao/Library/Fonts/康熙字典体.otf", 20)
        draw.text(
            xy=(0, 0),
            text="孝男王永(雄/开/跃)孝孙(男/女)(王定海/毛勇/刘位/王雪莲/王雪萍)孝孙(媳/婿)(陈晓丽/侯富馨)",
            fill="black",
            font=font,
            direction="ttb"
        )

        palette_img = Image.new("P", (1, 1))  # 调色板
        palette_img.putpalette(
            [
                0, 0, 0,  # 黑色
                255, 0, 0,  # 红色
                26, 170, 47,  # 绿色
                255, 255, 255,  # 白色
                255, 204, 153,  # 浅橙色
                95, 95, 95,  # 灰色
                221, 221, 221,  # 浅灰色
            ]
        )

        fixed_image = image.quantize(palette=palette_img, dither=Image.Dither.NONE)

        if ps == "windows":
            dir_fp: str = f"C:\\Users\\wangxiao\\Downloads\\1.webp"
        elif ps == "darwin":  # macOS
            dir_fp: str = f"/Users/wangxiao/Downloads/1.webp"
        else:
            sys.exit(-1)

        fixed_image.save(
            fp=dir_fp,
            optimize=True,
            compress_level=5,
            dpi=(72, 72),
            format="WEBP",
            quality=80,
        )


def main():
    # print(f"CairoSVG版本：{cairosvg.__version__}")
    h = Handle()
    h.draw(text="")


if __name__ == "__main__":
    main()
