# 管理员运行：
# python -m pip install --upgrade pip
# Install-Module PSReadLine -MinimumVersion 2.0.3 -Scope CurrentUser -Force
# pip install pillow svgelements cairosvg cairocffi==0.8
# pycairo用不上
# 安装字体：98WB-V.otf、98WB-U.otf以查看未显示字根
import platform
import sys
from typing import Dict, Set

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

ps = platform.system().lower()
# 键盘尺寸
width: int = 167
height: int = 232
# 小字母
alpha_font = "字根图字体/MONACO.TTF"

# 文津0
char_font1: Set[str] = {
    "⺊", "虍", "鹵", "灬", "馬", "魚", "礻", "亅", "𠃌", "㇇", "乚",
    "㇉", "飛", "來", "氵", "匚", "丂", "㐄", "丿", "龵", "見", "貝",
    "頁", "丆", "疒", "⺧", "豕", "扌", "丬", "⺌", "龷", "卅", "卌",
    "𠂇", "冖", "⺈", "乜", "コ", "丶", "亍", "厶", "钅", "𠂉", "酉",
    "刂", "罒", "丩", ""
}
# 文津2
char_font2: Set[str] = {
    "𠄎", "𡿨", "𫶧", "𧰨", "𬺰", "𦣞", "𣥂", "𭕄", "𠀎", "𫠠", "𠂤",
    "𠂭", "𠂆", "𦍌", "𢆉", ""
}
char_font3: Set[str] = {"𰁜", "𳑳", "𰀁", "𱼀", ""}  # 文津3
char_font4: Set[str] = {"𠂎", ""}  # 遍黑1
char_font5: Set[str] = {"ㅑ", "𘮌", "𱍸", ""}  # 遍黑2
# 宇浩
char_font6: Set[str] = {
    "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", ""
}
char_font7: Set[str] = {"𰀪"}  # 98V
char_font8: Set[str] = {""}  # 98U

back_car_orange: str = "QWERTASDFGZXCVB"
num_key: str = "QWERTYUIOP"


class FontManager:
    def __init__(self, size: int = 33, a_size: int = 22):
        self.fonts: Dict[int, FreeTypeFont] = {}
        self.size = size
        self.alpha_size = a_size
        self.load_font()

    def load_font(self):  # 加载字体到管理器
        try:
            self.fonts[1] = ImageFont.truetype("字根图字体/WenJinMinchoP0-Regular.ttf", self.size)
            self.fonts[2] = ImageFont.truetype("字根图字体/WenJinMinchoP2-Regular.ttf", self.size)
            self.fonts[3] = ImageFont.truetype("字根图字体/WenJinMinchoP3-Regular.ttf", self.size)
            self.fonts[4] = ImageFont.truetype("字根图字体/PlangothicP1-Regular.ttf", self.size)
            self.fonts[5] = ImageFont.truetype("字根图字体/PlangothicP2-Regular.ttf", self.size)
            self.fonts[6] = ImageFont.truetype("字根图字体/Yuniversus.ttf", self.size)
            self.fonts[7] = ImageFont.truetype("字根图字体/98WB-V.otf", self.size)
            self.fonts[8] = ImageFont.truetype("字根图字体/98WB-U.otf", self.size)
        except OSError as e:
            print(f"字体加载失败，文件问题：{e}")
            sys.exit(-1)
        except Exception as e:
            print(f"字体加载失败: {e}")
            sys.exit(-1)

    def get_font_for_char(self, char):
        if char in char_font1:
            return self.fonts[1], 1
        if char in char_font2:
            return self.fonts[2], 2
        if char in char_font3:
            return self.fonts[3], 3
        if char in char_font4:
            return self.fonts[4], 4
        if char in char_font5:
            return self.fonts[5], 5
        if char in char_font6:
            return self.fonts[6], 6
        if char in char_font7:
            return self.fonts[7], 7
        if char in char_font8:
            return self.fonts[8], 8
        if char in "abcdefghijklmnopqrstuvwxyz":
            return ImageFont.truetype(alpha_font, size=self.alpha_size), 0
        else:
            return ImageFont.truetype("字根图字体/Dengb.ttf", self.size), 0  # 等线，粗

    def get_center_pix(self, f: FreeTypeFont, text: str, line_n: int = 1):
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

    def draw(self, f: FontManager, back_car, text: str):
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # 加圆角边框
        draw.rounded_rectangle(
            xy=[0, 0, width, height],
            fill=None,  # 不填充
            outline="black",
            width=1,  # 边框宽度
            radius=0,  # 圆角半径
        )

        # 绘制背景字母
        back_font = ImageFont.truetype(
            font="字根图字体/IntelOneMono-Bold.ttf",
            size=230
        )
        back_color = (255, 204, 153) if back_car in back_car_orange else (221, 221, 221)
        b_x, b_y, b_height = f.get_center_pix(f=back_font, text=back_car)
        draw.text(xy=(b_x, b_y - 90), text=back_car, fill=back_color, font=back_font)

        # 绘制字根
        c_color = "black"
        text_line_num = text.count("\n") + 1

        l, t, r, b = ImageFont.truetype(alpha_font, size=f.alpha_size).getbbox("j")
        alpha_height = b - t

        # 宽，以第一排字符等线字体为准
        x, y, c_height = f.get_center_pix(f=ImageFont.truetype("字根图字体/Dengb.ttf", size=f.size), text=text.split("\n")[0], line_n=text_line_num)

        cur_x = x
        cur_y = y
        last_c_is_alpha: bool = False
        for i, c in enumerate(text):
            if c == '\n':
                if last_c_is_alpha:
                    cur_y += (alpha_height // 2)
                elif not last_c_is_alpha:
                    cur_y += (c_height + c_height // 3)
                cur_x = x
                continue

            font, num = f.get_font_for_char(c)
            # print(f"字符{c}，使用{font.path}")
            if c in "abcdefghijklmnopqrstuvwxyz" or c == " ":
                last_c_is_alpha = True
                draw.text((cur_x, cur_y - 8), c, fill=(95, 95, 95), font=font)
            else:
                last_c_is_alpha = False
                if c == "ノ":  # 特殊处理"ノ"
                    draw.text((cur_x, cur_y - 20), c, fill=(95, 95, 95), font=font)
                elif c == "丨" or c == "㇡":
                    draw.text((cur_x, cur_y), c, fill=(95, 95, 95), font=font)
                elif back_car == "J" and c in {"一", "丨", "丶", "丿"}:  # 特殊处理首笔画
                    draw.text((cur_x, cur_y), c, fill=(255, 0, 0), font=font)
                elif c in {"落", "释"}:  # 特殊处理：两个需要裁掉一部分的字根上色
                    draw.text((cur_x, cur_y), c, fill=(255, 0, 0), font=font)
                else:
                    draw.text((cur_x, cur_y), c, fill=c_color, font=font)

            # 加粗绘制特殊字体（多层绘制）
            if num != 0:
                for dx in [-1, 0]:  # [-1, 0, 1]
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
                26, 170, 47,  # 绿色
                255, 255, 255,  # 白色
                255, 204, 153,  # 浅橙色
                95, 95, 95,  # 灰色
                221, 221, 221,  # 浅灰色
            ]
        )

        fixed_image = image.quantize(palette=palette_img, dither=Image.Dither.NONE)

        if ps == "windows":
            dir_fp: str = f"C:\\Users\\wangxiao\\Downloads\\{back_car.lower()}.webp"
        elif ps == "darwin":  # macOS
            dir_fp: str = f"/Users/wangxiao/Downloads/{back_car.lower()}.webp"
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
    h.draw(FontManager(size=36, a_size=24), back_car="A", text="了")
    tb: str = (
        "ㅑ𳑳虍\n"
        " o  o  hu\n"
        "鹵灬馬\n"
        "lu bi  ma\n"
        "魚礻\n"
        "e  ka"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="B", text=tb)
    # -----------------
    tc: str = (
        "亅𠃌𠄎㇇\n"
        "乚㇉𡿨\n"
        "i\n"
        "飛來氵\n"
        "fo  le o ko"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="C", text=tc)
    # -----------------
    td: str = (
        "凵屮\n"
        "o\n\n"
        "彑宀廴〇\n"
        "ji  me o  li"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="D", text=td)
    # -----------------
    h.draw(FontManager(size=36, a_size=24), back_car="E", text="的")
    tf: str = (
        "𘮌丂匚\n"
        "ki      fe\n"
        "𰀁㐄丿\n"
        " o         pe\n"
        "龵\n"
        "ke"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="F", text=tf)
    # -----------------
    tg: str = (
        "頁丆見貝\n"
        " e  a  je bo\n"
        "罒𫶧\n"
        " o\n"
        "⺧疒扌\n"
        "nu lu ne ke\n"
        "豕𧰨\n"
        "ka"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="G", text=tg)
    # -----------------
    th: str = (
        "冂勹\n"
        "o\n\n"
        "冊龰齒\n"
        "ge ce si ri"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="H", text=th)
    # -----------------
    h.draw(FontManager(size=36, a_size=24), back_car="I", text="是")
    tj: str = (
        "曰𦣞\n"
        " e   i\n\n"
        "忄丄咼冎\n"
        "fu xo ga\n\n"
        "巛巜𬺰\n"
        "ri     o\n"
        "\n"
        "fu si"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="J", text=tj)
    # -----------------
    tk: str = (
        "彡𰀪纟\n"
        "ka     si\n\n"
        "弋彳\n"
        " i  ri o      qo\n"
        "丬\n"
        "qo"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="K", text=tk)
    # -----------------
    tl: str = (
        "〢〣亡\n"
        " o\n\n"
        "亠𣥂⺌𭕄\n"
        "lo te xi\n\n"
        "辶髟兀糹長镸\n"
        "ro bi u si re\n\n"
        "饣丨\n"
        "gi ka xo gi"
    )
    h.draw(FontManager(size=28, a_size=20), back_car="L", text=tl)
    # -----------------
    tm: str = (
        "コ冖⺈\n"
        " o\n"
        "乜卅卌\n"
        " o  me sa xi\n\n"
        "𠂇𫠠龷𠀎\n"
        " zo qi ci\n"
        "𠂤\n"
        "u do"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="M", text=tm)
    # -----------------
    tn: str = (
        "𱼀亍厶\n"
        " e  o  ru si"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="N", text=tn)
    # -----------------
    h.draw(FontManager(size=36, a_size=24), back_car="O", text="我")
    tp: str = (
        "犭豸\n"
        "qi si"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="P", text=tp)
    # -----------------
    tq: str = (
        "殳風丱\n"
        "ku fe gi mi\n\n"
        "𱍸𠂎\n"
        " o\n"
        "丩\n"
        " o"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="Q", text=tq)
    # -----------------
    tr: str = (
        "烏鳥\n"
        " u     ni\n\n"
        "車門鬥丌\n"
        "re me de ji"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="R", text=tr)
    # -----------------
    ts: str = (
        "爿尢\n"
        "pa  o"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="S", text=ts)
    # -----------------
    tt: str = (
        "衤龸攵\n"
        "i   o  pe\n"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="T", text=tt)
    # -----------------
    h.draw(FontManager(size=36, a_size=24), back_car="U", text="不")
    tv: str = (
        "龶壴戶讠\n"
        "ke su hu e\n\n"
        "耂癶ス龴\n"
        "o\n"
        "𠂆乂𠂭\n"
        "o   i\n"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="V", text=tv)
    # -----------------
    tw: str = (
        "僉隹\n"
        "qi co  o\n\n"
        "禺\n"
        " e"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="W", text=tw)
    # -----------------
    tx: str = (
        "リ钅\n"
        "ci  jo"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="X", text=tx)
    # -----------------
    ty: str = (
        "𠂉酉刂\n"
        " o su  u di"
    )
    h.draw(FontManager(size=36, a_size=24), back_car="Y", text=ty)
    # -----------------
    h.draw(FontManager(size=36, a_size=24), back_car="Z", text="[反查]")


if __name__ == "__main__":
    main()
