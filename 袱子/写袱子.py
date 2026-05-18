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
]

wangxiong: List[List[str]] = [
    ["百期化钱 孝男王永", "雄/开/跃", "孝媳", "张秀华/刘方胜/刘翠英", "孝孙", "男/女", "王定海/毛勇/刘位/王雪莲/王雪萍", "孝孙", "媳/婿", "陈晓丽/侯富馨", "等具"],
    ["谨具冥财 七封奉/上"],
    ["故慈母王", "宅/", "朱君寄春老", "孺/", "人一位收用"],
    ["坟前化纳"],
    ["天运甲辰年二月十六日敬献"],
]
wangxiao: List[List[str]] = [
    ["酬恩了愿化钱 下民姓氏王永骁"],
    ["  情因本年中闰六月十八日请愿祈求二房东徐龙武退还/  车位办理费四百八十元特虔诚告曰愿躬赴九华山朝地藏/  并化宝帛敬奉土地言毕即应果蒙神佑诚心酬谢/正钱十五封俯伏上奉"],
    ["九华山幽冥教主地藏菩萨摩诃萨莲座下鉴纳/本境土地福德正神祠前收用"],
    ["保佑清太/吉祥如意", "路旁化帛"],
    ["天运乙巳年闰六月廿九日了愿是实"],
]


class Handle:
    def __init__(self, content: List[List[str]]):
        self.content = content
        self.img_path = "/Users/wangxiao/Downloads/1.webp"
        self.font_size = 26
        self.font_size_central = 35
        self.font_path = "/Users/wangxiao/Library/Fonts/KaiTi-YiMa.ttf"
        self.font_path2 = "/Users/wangxiao/Library/Fonts/康熙字典体.otf"
        self.width = 700
        self.height = 700
        self.blank = 10  # 四边空白像素
        self.horizon_count: List[int] = []  # 每列的并排数
        self.vert_count: List[int] = []  # 每列的长度
        self.line_index_x: List[int] = [0, 0, 0, 0, 0]  # 每一列绘制起点x
        self.line_index_y: List[int] = [0, 0, 0, 0, 0]  # 每一列绘制起点y

    def horizontal_count(self):  # 水平方向
        for i, l in enumerate(self.content):
            max_line = 1
            for c in l:
                num = c.count("/") + 1
                if num > max_line:
                    max_line = num
            self.horizon_count.append(max_line)

    def vertical_count(self):
        for i, l in enumerate(self.content):
            char_count = 0
            for c in l:
                if c.count("/") >= 1:
                    max_char = 1
                    for i in c.split("/"):
                        if len(i) > max_char:
                            max_char = len(i)
                    char_count += max_char
                else:
                    char_count += len(c)
            self.vert_count.append(char_count)

    def gen_font_size(self):
        vertical_font_size_max = (self.height - self.blank * 2) // max(self.vert_count)
        horizontal_font_size_max = (self.width - self.blank * 2) // sum(self.horizon_count) - 1
        self.font_size = min(vertical_font_size_max, horizontal_font_size_max)
        self.font_size_central = (self.height - self.blank * 2) // self.vert_count[2]  # 中央列，强制顶格起头、上下顶满

    def gen_index(self):
        half = self.horizon_count[2] // 2 * self.font_size_central

        self.line_index_x[0] = 0.5 * (self.width - self.blank - self.horizon_count[0] * self.font_size)
        self.line_index_x[1] = 0.5 * (self.width - self.blank - (self.horizon_count[0] + self.horizon_count[1]) * self.font_size)
        self.line_index_x[2] = self.width + half
        self.line_index_x[3] = 0.5 * (self.blank - half - self.font_size + self.horizon_count[3] * self.font_size)
        self.line_index_x[4] = 0.5 * (self.blank - half - self.font_size + (self.horizon_count[3] + self.horizon_count[4]) * self.font_size)
        print()

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(image)
        # 加圆角边框
        draw.rounded_rectangle(
            xy=[0, 0, self.width, self.height],
            fill=None,  # 不填充
            outline="black",
            width=3,  # 边框宽度
            radius=0,  # 圆角半径
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
        for i, l in enumerate(self.content):
            self.draw_line(l, self.line_index_x[i], 0)

    def draw_line(self, line: List[str], x: int, y=0):
        cur_y = y
        for sep in line:
            cur_x = x
            line_num = sep.count("/") + 1  # 列数
            if line_num > 1:
                line_half = line_num // 2
                if line_num % 2 == 0:  # 偶数列
                    cur_x += self.font_size // 2 + (line_half - 1) * self.font_size
                elif line_num % 2 == 1:
                    cur_x += line_half * self.font_size
            cur_y = self.sep(color="black", text=sep, x=cur_x, y=cur_y)

    def sep(self, text: str, color: str, x: int, y: int):
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


def main():
    # print(f"CairoSVG版本：{cairosvg.__version__}")
    h = Handle(wangxiao)
    h.horizontal_count()
    h.vertical_count()

    h.gen_font_size()

    h.gen_index()
    h.draw()


if __name__ == "__main__":
    main()
