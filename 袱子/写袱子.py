# 管理员運行：
# python -m pip install --upgrade pip
# Install-Module PSReadLine -MinimumVersion 2.0.3 -Scope CurrentUser -Force
# pip install pillow svgelements cairosvg cairocffi==0.8
# pycairo用不上
# 安装字体：98WB-V.otf、98WB-U.otf以查看未顯示字根
# raqm：竖排等复杂布局文本支撑
# 源码编译安装libraqm：https://github.com/HOST-Oman/libraqm，函数文档https://host-oman.github.io/libraqm
# 1.brew install freetype harfbuzz fribidi meson gtk-doc
# export XML_CATALOG_FILES="/usr/local/etc/xml/catalog" # for the docs
# 2.pip uninstall Pillow
# 3.pip install --upgrade Pillow --global-option="build_ext" --global-option="--enable-raqm" --no-binary=Pillow
import platform
import sys
from typing import List, Dict, Set

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

ps = platform.system().lower()

wangzefu: List[List[str]] = [
    ["孝", "婿/女", "王澤福/廖俊", "外孫", "男/女", "王驍/王云慧"], ["故岳", "考/妣", "廖", "公諱清賢/宅曹君庭秀", "老", "大/孺", "人二位收用"],
    ["孫", "婿/女", "王澤福/廖俊", "外曾孫", "男/女", "王驍/王云慧"], ["故太岳", "考/妣", "廖", "公諱明富/宅楊君", "老", "大/孺", "人二位收用"],
    ["外曾孫男王", "澤福/澤錄/淼", "媳/", "廖俊//", "外玄孫", "男/女", "王驍/王云慧"], ["故外曾祖", "考/妣", "龐", "公諱義容/宅李君", "老", "大/孺", "人二位收用"],
    ["外孫男王", "澤福/澤錄/淼", "媳/", "廖俊//", "外曾孫", "男/女", "王驍/王云慧"], ["故外祖", "考/妣", "張", "公諱家運/宅朱君友芬", "老", "大/孺", "人二位收用"],
    ["外曾孫男王", "澤福/澤錄/淼", "媳/", "廖俊//", "外玄孫", "男/女", "王驍/王云慧"], ["故外曾祖", "考/妣", "張", "公諱邦恩/宅秦君", "老", "大/孺", "人二位收用"],

    ["孝男王", "澤福/澤錄/淼", "孝", "媳/", "廖俊//", "孝孫", "男/女", "王", "驍/云慧"], ["故顯考王公", "諱/", "汝上老大人一位收用"],
    ["孫男王", "澤福/澤錄/淼", "孫", "媳/", "廖俊//", "曾孫", "男/女", "王", "驍/云慧"], ["故祖", "考/妣", "王", "公諱守璽/宅龐君懷美", "老", "大/孺", "人二位收用"],
    ["曾孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "玄孫", "男/女", "王", "驍/云慧"], ["故曾祖", "考/妣", "王", "公諱尚安/宅陳君", "老", "大/孺", "人二位收用"],
    ["曾孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "玄孫", "男/女", "王", "驍/云慧"], ["故曾祖", "考/妣", "王", "公諱尚璋/宅劉君", "老", "大/孺", "人二位收用"],
    ["玄孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "來孫", "男/女", "王", "驍/云慧"], ["故高祖", "考/妣", "王", "公諱支和/宅伯君", "老", "大/孺", "人二位收用"],
    ["玄孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "來孫", "男/女", "王", "驍/云慧"], ["故高祖", "考/妣", "王", "公諱支江/宅劉君", "老", "大/孺", "人二位收用"],
    ["來孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "晜孫", "男/女", "王", "驍/云慧"], ["故天祖", "考/妣", "王", "公諱萬榮/宅李君", "老", "大/孺", "人二位收用"],
    ["晜孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "仍孫", "男/女", "王", "驍/云慧"], ["故烈祖", "考/妣", "王", "公諱自元/宅趙君", "老", "大/孺", "人二位收用"],
    ["仍孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "云孫", "男/女", "王", "驍/云慧"], ["故太祖", "考/妣", "王", "公諱敏/宅閻君", "老", "大/孺", "人二位收用"],
    ["云孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "耳孫", "男/女", "王", "驍/云慧"], ["故遠祖", "考/妣", "王", "公諱耀德/宅羅君", "老", "大/孺", "人二位收用"],
    ["耳孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "十世孫", "男/女", "王", "驍/云慧"], ["故鼻祖", "考/妣", "王", "公諱映爵/宅羅君", "老", "大/孺", "人二位收用"],
    ["十世孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "十一世孫", "男/女", "王", "驍/云慧"], ["故十世祖", "考/妣", "王", "公諱述先/宅汪君", "老", "大/孺", "人二位收用"],
    ["十一世孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "十二世孫", "男/女", "王", "驍/云慧"], ["故十一世祖", "考/妣", "王", "公//宅", "諱西成/謝君/汪君", "老", "大/孺", "人三位收用"],
    ["十二世孫王", "澤福/澤錄/淼", "媳/", "廖俊//", "十三世孫", "男/女", "王", "驍/云慧"], ["故十二世祖", "考/妣", "王", "公//宅", "諱心田/劉君/謝君", "老", "大/孺", "人三位收用"],

    [" 下民", "王澤福/廖俊/王澤錄/王淼", " ", "王驍/王云慧"], ["本境土地福德正神祠前收用"],
    [" 下民", "王澤福/廖俊/王澤錄/王淼", " ", "王驍/王云慧"], ["地盤業主孤魂野鬼魂下收用"],

    ["孫", "男/女", "王", "建亮/建霞", "孫", "媳/", "胡彩娥/", "曾孫王", "晶晶/炜承/彥涵"], ["故祖", "考/妣", "王", "公諱文鴻/宅衛君蘭英", "老", "大/孺", "人二位收用"],
    ["孝男王永", "雄/開/躍", "孝媳", "張秀華/劉方勝/劉翠英", "孝孫", "男/女", "王定海/毛勇/劉位/王雪蓮/王雪萍", "孝孫", "媳/婿", "陳曉麗/侯富馨"], ["故慈母王", "宅/", "朱君寄春老孺人一位收用"],
]

wangxiao: List[List[str]] = [
    ["酬恩了愿化錢 下民姓氏王永驍"],
    ["  情因本年中闰六月十八日请愿祈求二房东徐龙武退还/  车位办理费四百八十元特虔诚告曰愿躬赴九华山朝地藏/  并化宝帛敬奉土地言毕即应果蒙神佑诚心酬謝/  正錢十五封俯伏上奉"],
    ["九华山幽冥教主地藏菩萨摩诃萨莲座下鉴纳/本境土地福德正神祠前收用"],
    ["  ", "保佑清太/吉祥如意", "路旁化帛"],
    ["天運乙巳年闰六月廿九日了愿是实"],
]

char_font2: Set[str] = {"淼", "炜"}
char_font3: Set[str] = {"晜"}


class Handle:
    def __init__(self, content: List[List[str]], size: List[int], rank: List[int], img: str):
        self.content = content
        self.font_size = size
        self.rank_blank = rank
        self.img_path = img
        self.font_path = "/Users/wangxiao/Library/Fonts/康熙字典体.otf"  # KaiTi-YiMa.ttf、康熙字典体.otf、FZLongZhaoJW.TTF
        self.width = 1100
        self.height = 800
        self.up_down = 10  # 外圈空白像素
        self.left_right = 160  # 外圈空白像素
        self.horizon_count: List[int] = []  # 每列的并排数
        self.vert_count: List[int] = []  # 每列的长度
        self.line_index_x: List[int] = []  # 每一列绘制起点x
        self.fonts: Dict[int, FreeTypeFont] = {}

    def get_font(self, c: str, s: int):
        try:
            self.fonts[1] = ImageFont.truetype(font="/Users/wangxiao/Library/Fonts/康熙字典体.otf", size=s)
            self.fonts[2] = ImageFont.truetype(font="/Users/wangxiao/Library/Fonts/FZLongZhaoJW.TTF", size=s)
            self.fonts[3] = ImageFont.truetype(font="/Users/wangxiao/Library/Fonts/KaiTi-YiMa.ttf", size=s)
        except Exception as e:
            print(f"字体加载失败: {e}")
            sys.exit(-1)
        if c in char_font2:
            return self.fonts[2]
        if c in char_font3:
            return self.fonts[3]
        else:
            return self.fonts[1]

    def make_data(self, thing: str, num: str, add: List[str], ti: str):
        self.content[0].insert(0, thing)
        self.content.insert(1, [f"    虔具信伏 {num}封奉/上"])  # 虔具信伏、谨具冥财
        self.content.append(add)
        self.content.append([f"天運{ti}敬獻"])

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
        font_size: List[int] = []
        for i, v in enumerate(self.vert_count):
            font_size.append((self.height - self.up_down * 2) // v)
        horizontal_max = (self.width - self.left_right * 2) // sum(self.horizon_count)
        font_size = [min(x, horizontal_max) for x in font_size]
        odd_max = max(font_size[i] for i in range(0, len(font_size), 2))  # 设置奇数列文字尺寸为最大值
        self.font_size = [min(x, odd_max) for x in font_size]
        print(f"当前字体设置：{self.font_size}")

        char_width: int = 0  # 文字一共所占宽度
        for i, s in enumerate(self.font_size):
            char_width += self.horizon_count[i] * s
        blank = (self.width - self.left_right * 2 - char_width) // (len(self.content) - 1)
        self.rank_blank = [blank] * (len(self.content) - 1)
        print(f"当前列间隔设置：{self.rank_blank}")

    def gen_index(self):
        right: int = self.width - self.left_right - self.font_size[0]
        for i, f in enumerate(self.font_size):
            if i > 0:
                right = right - (self.horizon_count[i - 1] - 1) * self.font_size[i - 1] - self.rank_blank[i - 1] - self.font_size[i]
            left = right - (self.horizon_count[i] - 1) * self.font_size[i]
            self.line_index_x.append(left + (right - left) // 2)

    def draw(self):
        image = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(image)
        # 加圆角邊框
        draw.rounded_rectangle(
            xy=[0, 0, self.width, self.height],
            fill=None,  # 不填充
            outline="black",
            width=3,  # 邊框宽度
            radius=0,  # 圆角半径
        )

        image.save(
            fp=self.img_path,
            optimize=True,
            compress_level=5,
            dpi=(72, 72),
            format="JPEG",
            quality=80,
        )
        for i, l in enumerate(self.content):
            self.draw_line(i, l)

    def draw_line(self, i: int, line: List[str]):
        cur_y = 0
        for sep in line:
            cur_x = self.line_index_x[i]
            line_num = sep.count("/") + 1  # 列数
            if line_num > 1:
                line_half = line_num // 2
                if line_num % 2 == 0:  # 偶数列
                    cur_x += self.font_size[i] // 2 + (line_half - 1) * self.font_size[i]
                elif line_num % 2 == 1:
                    cur_x += line_half * self.font_size[i]
            cur_y = self.sep(i=i, color="black", text=sep, x=cur_x, y=cur_y)

    def sep(self, i: int, text: str, color: str, x: int, y: int):
        max_y = y
        img = Image.open(self.img_path).convert('RGB')
        draw = ImageDraw.Draw(img)
        now_y = y
        now_x = x
        for c in text:
            if c == "/":
                now_y = y
                now_x -= self.font_size[i]
                continue
            fo = self.get_font(c, self.font_size[i])
            draw.text(xy=(now_x, now_y), text=c, font=fo, fill=color)
            # 加粗绘制（多层绘制）
            for dx in [-1, 0]:  # 加粗 [-1, 0, 1]
                draw.text(xy=(now_x + dx, now_y), text=c, font=fo, fill=color)
                draw.text(xy=(now_x, now_y + dx), text=c, font=fo, fill=color)

            now_y += self.font_size[i]  # 字的高度
            if now_y > max_y:
                max_y = now_y
        img.save(self.img_path)
        return max_y


def main():
    # print(f"CairoSVG版本：{cairosvg.__version__}")
    n = 2  # 每组2个元素
    newList = [wangzefu[i:i + n] for i in range(0, len(wangzefu), n)]
    for i, l in enumerate(newList):
        h = Handle(content=l, size=[0, 0, 0, 0, 0], rank=[0, 0, 0, 0], img=f"/Users/wangxiao/Downloads/{i}.jpeg")
        # 新年、寿诞、清明拜扫、端午、中元、酬恩了愿
        # 中元堂前化帛、保佑清太吉祥如意
        h.make_data(thing="端午之期", num="十", add=["    路邊化錢"], ti="丙午二〇二六年五月初五日")
        h.horizontal_count()
        h.vertical_count()
        h.gen_font_size()
        h.gen_index()
        h.draw()
        print("")


if __name__ == "__main__":
    main()
