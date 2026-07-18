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

wang_ze_fu: List[List[str]] = [
    ["孝外甥孫婿/女王澤福/廖俊玄孫王驍/王雲慧"],
    ["故內外祖顯", "考/妣", "曹", "公諱仕營/宅胡君應軒/繼男袁昌敬", "老", "大/孺", "人收用"],
    ["孝", "婿/女", "王澤福/廖俊", "外孫", "王驍/王雲慧"], ["故嶽顯", "考/妣", "廖", "公諱清賢/宅曹君庭秀", "老", "大/孺", "人二位收用"],
    ["孫", "婿/女", "王澤福/廖俊", "外曾孫", "王驍/王雲慧"], ["故太嶽顯", "考/妣", "廖", "公諱明富/宅楊君", "老", "大/孺", "人二位收用"],
]

char_font2: Set[str] = {"炜", "寿", "诞"}
char_font3: Set[str] = set()


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
            # self.fonts[1] = ImageFont.truetype(font="/Users/wangxiao/Library/Fonts/康熙字典体.otf", size=s)
            self.fonts[1] = ImageFont.truetype(font="/Users/wangxiao/Nutstore Files/我的坚果云/打字/字体/chinese-fonts-master/華康明體/DFMingStd-W7.otf", size=s)
            self.fonts[2] = ImageFont.truetype(font="/Users/wangxiao/Nutstore Files/我的坚果云/打字/字体/chinese-fonts-master/雲林黑體/YunlinSans-Regular.ttf", size=s)
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

    def make_data(self, thing: str, add: List[str], ti: str):
        self.content[0].insert(0, thing)
        self.content.insert(1, [f"    虔具信伏   封奉/上"])  # 虔具信伏、谨具冥财
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
        self.font_size = min(font_size)
        print(f"当前字体设置：{self.font_size}")

        char_width: int = 0  # 文字一共所占宽度
        for i in self.horizon_count:
            char_width += i * self.font_size
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
        draw.line(
            xy=[self.left_right - 3, 0, self.left_right - 3, self.height],
            fill='black',
            width=2
        )
        draw.line(
            xy=[self.width - self.left_right + 3, 0, self.width - self.left_right + 3, self.height],
            fill='black',
            width=2
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
    newList = [wang_ze_fu[i:i + n] for i in range(0, len(wang_ze_fu), n)]
    for i, l in enumerate(newList):
        h = Handle(content=l, size=[0, 0, 0, 0, 0], rank=[0, 0, 0, 0], img=f"/Users/wangxiao/Downloads/{i}.jpeg")
        # 新年、寿诞、清明拜扫、端午、中元、酬恩了愿
        # 中元堂前化帛、保佑清太吉祥如意
        h.horizontal_count()
        h.vertical_count()
        h.gen_font_size()
        h.gen_index()
        h.draw()
        print("")


if __name__ == "__main__":
    main()
