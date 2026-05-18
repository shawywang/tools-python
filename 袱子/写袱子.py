# 管理员运行：
# python -m pip install --upgrade pip
# Install-Module PSReadLine -MinimumVersion 2.0.3 -Scope CurrentUser -Force
# pip install pillow svgelements cairosvg cairocffi==0.8
# pycairo用不上
# 安装字体：98WB-V.otf、98WB-U.otf以查看未显示字根
# raqm：竖排等复杂布局文本支撑
# 源码编译安装libraqm：https://github.com/HOST-Oman/libraqm，函数文档https://host-oman.github.io/libraqm
# 1.brew install freetype harfbuzz fribidi meson gtk-doc
# export XML_CATALOG_FILES="/usr/local/etc/xml/catalog" # for the docs
# 2.pip uninstall Pillow
# 3.pip install --upgrade Pillow --global-option="build_ext" --global-option="--enable-raqm" --no-binary=Pillow
import platform
from typing import List

from PIL import Image, ImageDraw, ImageFont

ps = platform.system().lower()

wangxiao_wangyunhui: List[List[str]] = [
    ["孙(男/女)王(骁/云慧)", "祖父王公(讳)汝上老大人一位收用"],
    ["曾孙(男/女)王(骁/云慧)", "曾祖(父/母)王公(讳)(守玺/怀美)老(大/孺)人二位收用"],
    ["玄孙(男/女)王(骁/云慧)", "高祖(父/母)王公(讳)(尚安/陈君)老(大/孺)人二位收用"],
    ["孝男王永(雄/开/跃)孝孙(男/女)(王定海/毛勇/刘位/王雪莲/王雪萍)孝孙(媳/婿)(陈晓丽/侯富馨)", "慈母王(宅)朱君寄春老孺人一位收用"],
]

wangxiong: List[str] = ["孝男王永", "雄/开/跃", "孝孙", "男/女", "王定海/毛勇/刘位/王雪莲/王雪萍", "孝孙", "媳/婿", "陈晓丽/侯富馨", "慈母王", "宅/", "朱君寄春老", "孺/", "人一位收用"]


class Handle:
    def __init__(self):
        self.img_path = "/Users/wangxiao/Downloads/1.webp"
        self.font_size = 20
        self.font_path = "/Users/wangxiao/Library/Fonts/KaiTi-YiMa.ttf"
        self.font_path2 = "/Users/wangxiao/Library/Fonts/康熙字典体.otf"
        self.width = 700
        self.height = 700

    def portrait(self, text: str, color: str, x: int, y: int):
        max_y = y
        img = Image.open(self.img_path).convert('RGB')
        draw = ImageDraw.Draw(img)
        now_y = y
        now_x = x
        for c in text:
            if c == "/":
                now_y = y
                now_x -= self.font_size
                continue
            draw.text((now_x, now_y), c, font=ImageFont.truetype(self.font_path, self.font_size), fill=color)
            now_y += self.font_size  # 字的高度
            if now_y > max_y:
                max_y = now_y
        img.save(self.img_path)
        return max_y

    def draw(self, x: int, y=0):
        image = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(image)
        # 加圆角边框
        draw.rounded_rectangle(
            xy=[0, 0, self.width, self.height],
            fill=None,  # 不填充
            outline="black",
            width=3,  # 边框宽度
            radius=20,  # 圆角半径
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
        fixed_image.save(
            fp=self.img_path,
            optimize=True,
            compress_level=5,
            dpi=(72, 72),
            format="WEBP",
            quality=80,
        )
        cur_y = y
        for sep in wangxiong:
            cur_x = x
            line_num = sep.count("/") + 1  # 列数
            if line_num > 1:
                line_half = line_num // 2
                if line_num % 2 == 0:  # 偶数列
                    cur_x += self.font_size // 2 + (line_half - 1) * self.font_size
                elif line_num % 2 == 1:
                    cur_x += line_half * self.font_size
            cur_y = self.portrait(color="black", text=sep, x=cur_x, y=cur_y)


def main():
    # print(f"CairoSVG版本：{cairosvg.__version__}")
    h = Handle()
    h.draw(x=60, y=0)


if __name__ == "__main__":
    main()
