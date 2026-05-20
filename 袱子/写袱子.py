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

wangzefu: List[List[str]] = [
    ["孝", "婿/女", "王泽福/廖俊", "外孙", "男/女", "王骁/王云慧"], ["故岳", "考/妣", "廖", "公讳清贤/宅曹君庭秀", "老", "大/孺", "人二位收用"],
    ["孙", "婿/女", "王泽福/廖俊", "外曾孙", "男/女", "王骁/王云慧"], ["故太岳", "考/", "廖公", "讳/", "明富老大人一位收用"],
    ["外曾孙男王", "泽福/泽录/淼", "媳/", "廖俊//", "外玄孙", "男/女", "王骁/王云慧"], ["故外曾祖", "考/妣", "庞", "公讳义容/宅李君", "老", "大/孺", "人二位收用"],
    ["外孙男王", "泽福/泽录/淼", "媳/", "廖俊//", "外曾孙", "男/女", "王骁/王云慧"], ["故外祖", "考/妣", "张", "公讳家运/宅朱君友芬", "老", "大/孺", "人二位收用"],
    ["外曾孙男王", "泽福/泽录/淼", "媳/", "廖俊//", "外玄孙", "男/女", "王骁/王云慧"], ["故外曾祖", "考/妣", "张", "公讳邦恩/宅秦君", "老", "大/孺", "人二位收用"],
    
    ["孝男王", "泽福/泽录/淼", "孝", "媳/", "廖俊//", "孝孙", "男/女", "王", "骁/云慧"], ["故显考王公", "讳/", "汝上老大人一位收用"],
    ["孙男王", "泽福/泽录/淼", "孙", "媳/", "廖俊//", "曾孙", "男/女", "王", "骁/云慧"], ["故祖", "考/妣", "王", "公讳守玺/宅庞君怀美", "老", "大/孺", "人二位收用"],
    ["曾孙王", "泽福/泽录/淼", "媳/", "廖俊//", "玄孙", "男/女", "王", "骁/云慧"], ["故曾祖", "考/妣", "王", "公讳尚安/宅陈君", "老", "大/孺", "人二位收用"],
    ["曾孙王", "泽福/泽录/淼", "媳/", "廖俊//", "玄孙", "男/女", "王", "骁/云慧"], ["故曾祖", "考/妣", "王", "公讳尚璋/宅刘君", "老", "大/孺", "人二位收用"],
    ["玄孙王", "泽福/泽录/淼", "媳/", "廖俊//", "来孙", "男/女", "王", "骁/云慧"], ["故高祖", "考/妣", "王", "公讳支和/宅伯君", "老", "大/孺", "人二位收用"],
    ["玄孙王", "泽福/泽录/淼", "媳/", "廖俊//", "来孙", "男/女", "王", "骁/云慧"], ["故高祖", "考/妣", "王", "公讳支江/宅刘君", "老", "大/孺", "人二位收用"],
    ["来孙王", "泽福/泽录/淼", "媳/", "廖俊//", "晜孙", "男/女", "王", "骁/云慧"], ["故天祖", "考/妣", "王", "公讳万荣/宅李君", "老", "大/孺", "人二位收用"],
    ["晜孙王", "泽福/泽录/淼", "媳/", "廖俊//", "仍孙", "男/女", "王", "骁/云慧"], ["故烈祖", "考/妣", "王", "公讳自元/宅赵君", "老", "大/孺", "人二位收用"],
    ["仍孙王", "泽福/泽录/淼", "媳/", "廖俊//", "云孙", "男/女", "王", "骁/云慧"], ["故太祖", "考/妣", "王", "公讳敏/宅闫君", "老", "大/孺", "人二位收用"],
    ["云孙王", "泽福/泽录/淼", "媳/", "廖俊//", "耳孙", "男/女", "王", "骁/云慧"], ["故远祖", "考/妣", "王", "公讳耀德/宅罗君", "老", "大/孺", "人二位收用"],
    ["耳孙王", "泽福/泽录/淼", "媳/", "廖俊//", "十世孙", "男/女", "王", "骁/云慧"], ["故鼻祖", "考/妣", "王", "公讳映爵/宅罗君", "老", "大/孺", "人二位收用"],
    ["十世孙王", "泽福/泽录/淼", "媳/", "廖俊//", "十一世孙", "男/女", "王", "骁/云慧"], ["故十世祖", "考/妣", "王", "公讳述先/宅汪君", "老", "大/孺", "人二位收用"],
    ["十一世孙王", "泽福/泽录/淼", "媳/", "廖俊//", "十二世孙", "男/女", "王", "骁/云慧"], ["故十一世祖", "考/妣", "王", "公//宅", "讳西成/谢君/汪君", "老", "大/孺", "人三位收用"],
    ["十二世孙王", "泽福/泽录/淼", "媳/", "廖俊//", "十三世孙", "男/女", "王", "骁/云慧"], ["故十二世祖", "考/妣", "王", "公//宅", "讳心田/刘君/谢君", "老", "大/孺", "人三位收用"],

    [" 下民", "王泽福/廖俊/王泽录/王淼", " ", "王骁/王云慧"], ["本境土地福德正神祠前收用"],
    [" 下民", "王泽福/廖俊/王泽录/王淼", " ", "王骁/王云慧"], ["地盘业主孤魂野鬼魂下收用"],

    ["孙", "男/女", "王", "建亮/建霞", "孙", "媳/", "胡彩娥/", "曾孙王", "晶晶/炜承/彦涵"], ["故祖", "考/妣", "王", "公讳文鸿/宅卫君兰英", "老", "大/孺", "人二位收用"],
]

wangxiong: List[List[str]] = [["孝男王永", "雄/开/跃", "孝媳", "张秀华/刘方胜/刘翠英", "孝孙", "男/女", "王定海/毛勇/刘位/王雪莲/王雪萍", "孝孙", "媳/婿", "陈晓丽/侯富馨"], ["故慈母王", "宅/", "朱君寄春老孺人一位收用"]]
wangxiao: List[List[str]] = [
    ["酬恩了愿化钱 下民姓氏王永骁"],
    ["  情因本年中闰六月十八日请愿祈求二房东徐龙武退还/  车位办理费四百八十元特虔诚告曰愿躬赴九华山朝地藏/  并化宝帛敬奉土地言毕即应果蒙神佑诚心酬谢/  正钱十五封俯伏上奉"],
    ["九华山幽冥教主地藏菩萨摩诃萨莲座下鉴纳/本境土地福德正神祠前收用"],
    ["  ", "保佑清太/吉祥如意", "路旁化帛"],
    ["天运乙巳年闰六月廿九日了愿是实"],
]


class Handle:
    def __init__(self, content: List[List[str]], size: List[int], rank: List[int], img: str):
        self.content = content
        self.font_size = size
        self.rank_blank = rank
        self.img_path = img
        self.font_path = "/Users/wangxiao/Library/Fonts/FZLongZhaoJW.TTF"  # KaiTi-YiMa.ttf、康熙字典体.otf、FZLongZhaoJW.TTF
        self.width = 1100
        self.height = 800
        self.blank = 10  # 四边空白像素
        self.horizon_count: List[int] = []  # 每列的并排数
        self.vert_count: List[int] = []  # 每列的长度
        self.line_index_x: List[int] = []  # 每一列绘制起点x

    def make_data(self, thing: str, num: str, add: List[str], ti: str):
        self.content[0].insert(0, thing)
        self.content.insert(1, [f"    虔具信伏 {num}封奉/上"])  # 虔具信伏、谨具冥财
        self.content.append(add)
        self.content.append([f"天运{ti}敬献"])

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
            font_size.append((self.height - self.blank * 2) // v)
        horizontal_max = (self.width - self.blank * 2) // sum(self.horizon_count)
        font_size = [min(x, horizontal_max) for x in font_size]
        odd_max = max(font_size[i] for i in range(0, len(font_size), 2))  # 设置奇数列文字尺寸为最大值
        self.font_size = [min(x, odd_max) for x in font_size]
        print(f"当前字体设置：{self.font_size}")

        char_width: int = 0  # 文字一共所占宽度
        for i, s in enumerate(self.font_size):
            char_width += self.horizon_count[i] * s
        blank = (self.width - self.blank * 2 - char_width) // (len(self.content) - 1)
        self.rank_blank = [blank] * (len(self.content) - 1)
        print(f"当前列间隔设置：{self.rank_blank}")

    def gen_index(self):
        right: int = self.width - self.blank - self.font_size[0]
        for i, f in enumerate(self.font_size):
            if i > 0:
                right = right - (self.horizon_count[i - 1] - 1) * self.font_size[i - 1] - self.rank_blank[i - 1] - self.font_size[i]
            left = right - (self.horizon_count[i] - 1) * self.font_size[i]
            self.line_index_x.append(left + (right - left) // 2)

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
            draw.text((now_x, now_y), c, font=ImageFont.truetype(self.font_path, self.font_size[i]), fill=color)
            # 加粗绘制特殊字体（多层绘制）
            for dx in [-1, 0, 1]:
                draw.text((now_x + dx, now_y), c, font=ImageFont.truetype(self.font_path, self.font_size[i]), fill=color)
                draw.text((now_x, now_y + dx), c, font=ImageFont.truetype(self.font_path, self.font_size[i]), fill=color)

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
        h.make_data(thing="端午之期", num="十", add=["    路边化钱"], ti="丙午二零二六年五月初五日")
        h.horizontal_count()
        h.vertical_count()
        h.gen_font_size()
        h.gen_index()
        h.draw()
        print("")


if __name__ == "__main__":
    main()
