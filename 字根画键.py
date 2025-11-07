# 管理员运行：
# C:\ProgramData\miniconda3\python.exe -m pip install --upgrade pip
# Install-Module PSReadLine -MinimumVersion 2.0.3 -Scope CurrentUser -Force
# C:\ProgramData\miniconda3\python.exe -m pip install pillow svgelements cairosvg pycairo cairocffi==0.8
# 安装字体：98WB-V.otf、98WB-U.otf以查看未显示字根
import sys
from typing import Dict, Set

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

char_font2: Set[str] = {
    "󰁰", "", "",
    "", "", "", "", "",
    "", "", "", "", "", "", "", "",
    "", "", "",
    "", "𰀃", "",
    "", "", "",
    "衤", "", "", "",
    "", "", "", "",
    "", "", "", "",
    "", "󰀠", "", "", "", "", "", "",
    "", "",
    "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "",
    "", "",
    "", "",
    "", "",
    "", "",
    "𰀆", "", "", "",
    "", "", "", "󰁹", "卩",
    "", "", "",
    "", "", "",
}
char_font3: Set[str] = {
    "𦫻", "𢀖", "𦭝", "𣎆", "𭤨", "𬜠", "𡨄", "𠮦", "𠂔", "𠔿", "𡭔",
}
back_car_orange: str = "QWERTASDFGZXCVB"


class FontManager:
    def __init__(self, size: int = 33):
        self.fonts: Dict[int, FreeTypeFont] = {}
        self.size = size
        self.load_font()

    def load_font(self):  # 加载字体到管理器
        try:
            self.fonts[1] = ImageFont.truetype(r"C:\Windows\Fonts\dengb.ttf", self.size)
            self.fonts[2] = ImageFont.truetype(r"C:\Windows\Fonts\98WB-V.otf", self.size)
            self.fonts[3] = ImageFont.truetype(r"C:\Windows\Fonts\98WB-U.otf", self.size)
        except OSError as e:
            print(f"字体加载失败，文件问题：{e}")
            sys.exit(-1)
        except Exception as e:
            print(f"字体加载失败: {e}")
            sys.exit(-1)

    def get_font_for_char(self, char):
        if char in char_font2:
            return self.fonts[2], 2
        if char in char_font3:
            return self.fonts[3], 3
        else:
            return self.fonts[1], 1

    def get_center_pix(self, width, height: int, f: FreeTypeFont, text: str, line_n: int = 1):
        left, top, right, bottom = f.getbbox(text)
        all_width = right - left
        all_height = (bottom - top) * line_n

        minus_x = width - all_width
        minus_y = height - all_height

        if len(text) != 1:
            if minus_x < 0 or minus_x > 7:
                print(f"提示：{text}:minus_x={minus_x}，可适当调整字体")
            if minus_y < 0:
                print(f"提示：{text}:minus_y={minus_y}，可适当调整字体")

        c_x = max(minus_x // 2, 0)  # 中心点横坐标
        c_y = max(minus_y // 2, 0)  # 中心店纵坐标
        c_height = bottom - top  # 单行文本高度
        return c_x, c_y, c_height


class Handle:
    def __init__(self):
        pass

    def draw(self, f: FontManager, back_car, text: str, width: int = 167, height: int = 232):
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

        # 绘制背景字母
        back_font = ImageFont.truetype(
            font=r"C:\Users\wangxiao\AppData\Local\Microsoft\Windows\Fonts\IntelOneMono-Bold.ttf",
            size=230
        )
        back_color = (255, 204, 153) if back_car in back_car_orange else (221, 221, 221)
        b_x, b_y, b_height = f.get_center_pix(width, height, f=back_font, text=back_car)
        draw.text(xy=(b_x, b_y - 90), text=back_car, fill=back_color, font=back_font)

        # 绘制字符
        c_color = "black"
        text_line_num = text.count("\n") + 1
        x, y, c_height = f.get_center_pix(
            width,
            height,
            f=ImageFont.truetype(r"C:\Windows\Fonts\dengb.ttf", size=f.size),  # 字符宽高均以等线字体为准
            text=text.split("\n")[0],
            line_n=text_line_num,
        )

        cur_x = x
        cur_y = y

        for c in text:
            if c == '\n':
                cur_y += c_height
                cur_x = x
                continue
            font, num = f.get_font_for_char(c)
            # print(f"字符{c}，使用{font.path}")

            if text == "一":  # 特殊处理"一"
                draw.text((cur_x, cur_y - 45), c, fill=(95, 95, 95), font=font)
            elif text == "ノ":  # 特殊处理"ノ"
                draw.text((cur_x, cur_y - 20), c, fill=(95, 95, 95), font=font)
            elif text == "丨" or text == "㇡":
                draw.text((cur_x, cur_y), c, fill=(95, 95, 95), font=font)
            elif back_car == "J" and c in {"一", "丨", "丶", "丿"}:  # 特殊处理首笔画
                draw.text((cur_x, cur_y), c, fill=(255, 0, 0), font=font)
            elif c in {"落", "释"}:  # 特殊处理：两个需要裁掉一部分的字根上色
                draw.text((cur_x, cur_y), c, fill=(255, 0, 0), font=font)
            else:
                draw.text((cur_x, cur_y), c, fill=c_color, font=font)

            # 加粗绘制特殊字体（多层绘制）
            if num != 1:
                for dx in [-1, 0, 1]:
                    draw.text((cur_x + dx, cur_y), c, fill=c_color, font=font)
                    draw.text((cur_x, cur_y + dx), c, fill=c_color, font=font)

            bbox = font.getbbox(c)
            c_width = bbox[2] - bbox[0]
            cur_x += c_width

        palette_img = Image.new("P", (1, 1))  # 调色板
        palette_img.putpalette(
            [
                0, 0, 0,  # 黑色
                255, 0, 0,  # 红色
                255, 255, 255,  # 白色
                255, 204, 153,  # 浅橙色
                95, 95, 95,  # 灰色
                221, 221, 221,  # 浅灰色
            ]
        )

        fixed_image = image.quantize(palette=palette_img, dither=Image.Dither.NONE)

        fixed_image.save(
            fp=f"C:\\Users\\wangxiao\\Downloads\\{back_car.lower()}.webp",
            optimize=True,
            compress_level=5,
            dpi=(72, 72),
            format="WEBP",
            quality=80,
        )


def main():
    # print(f"CairoSVG版本：{cairosvg.__version__}")
    h = Handle()

    h.draw(FontManager(size=41), back_car="A", text="于亍丁厂\n牙由曲甲\n几仑尔欠\n前广马丑\n壴䒑󰁰\n彑")
    h.draw(FontManager(size=41), back_car="B", text="更髟歹屯\n目且虫长\n代乎争夕\n以辟亠\n镸\n丩")
    h.draw(FontManager(size=40), back_car="C", text="丽赤小四\n皿公牛合\n禾了尹奴\n彐罒\n\n牜厶")
    h.draw(FontManager(size=33), back_car="D", text="石未末耒甘\n廿执贝虍人\n入白鱼卑豸\n殳酋穴也糸\n𭤨丆𬜠\n")
    h.draw(FontManager(size=162), back_car="E", text="一")
    h.draw(FontManager(size=41), back_car="F", text="天者甫见\n从夭彳八\n鸟门又双\n艹卌𰀃\n耂")
    h.draw(FontManager(size=41), back_car="G", text="可其至里\n田畀生先\n段九已己\n巴巳扌\n")
    h.draw(FontManager(size=33), back_car="H", text="不青直面平\n圭豆豕止齿\n凹凸光月乂\n角立单亥予\n矛艮忄礻衤\n𡨄吅㠯\n⺝㐅厃")
    h.draw(FontManager(size=162), back_car="I", text="丨")
    h.draw(FontManager(size=40), back_car="J", text="一夫五丌\n兀瓦韦寸\n业自告勿\n衣半㐄\n亻\n丨丶丿")
    h.draw(FontManager(size=41), back_car="K", text="大正戊弋\n戈戋敖口\n囗片之主\n羊尺爿\n𠮦勹\n戉")
    h.draw(FontManager(size=33), back_car="L", text="下元工龙士\n土鬲上卜内\n父竹心京农\n󰀠\n疒禸⽱\n⺊")
    h.draw(FontManager(size=41), back_car="M", text="走云林区\n比折骨氏\n隹方音鹿\n女疋龰\n释")
    h.draw(FontManager(size=33), back_car="N", text="开干吉页七\n廾水手千匕\n舌文义辛\n氺氵灬\n刂𡭔夂\n旡")
    h.draw(FontManager(size=162), back_car="O", text="ノ")
    h.draw(FontManager(size=33), back_car="P", text="三十犬尧共\n雨食舟卯定\n次火亦乙幺\n𦫻犭\n饣\n𢀖乚")
    h.draw(FontManager(size=41), back_car="Q", text="革臣因旦\n今令丘斤\n六米民叚\n朿\n亼冖㐫㡀")
    h.draw(FontManager(size=81), back_car="R", text="丶辶\n廴")
    h.draw(FontManager(size=41), back_car="S", text="王示亚是\n呆分壬鬼\n及言子孑\n聿刀凵\n冂讠屰")
    h.draw(FontManager(size=41), back_car="T", text="才木西酉\n此占用鼠\n久臼户加\n甬乛㇕\nㄅ㇉㇡覀\n朩")
    h.draw(FontManager(size=162), back_car="U", text="㇡")  # ㄋ
    h.draw(FontManager(size=41), back_car="V", text="相古中少\n气矢金母\n毋毌匚コ\n钅\n宀")
    h.draw(FontManager(size=33), back_car="W", text="去求万日曰\n我毛川象曾\n力乃⺀冫丷\n𰀆𦭝丂\n彡巛󰁹卩")
    h.draw(FontManager(size=41), back_car="X", text="丰尢回黑\n儿刍弟亡\n发弓\n纟\n𠂔𠔿")
    h.draw(FontManager(size=33), back_car="Y", text="而二莫辰车\n井耳堇山巾\n化缶瓜爪麻\n兼习羽落\n爫癶屮\n阝𣎆車")
    h.draw(FontManager(size=49), back_car="Z", text="束非北\n身垂各\n乍皮尸\n\n丬")


if __name__ == "__main__":
    main()
