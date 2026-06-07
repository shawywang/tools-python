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

# 文津0
char_font1: Set[str] = {
    "⺊", "虍", "鹵", "灬", "馬", "魚", "礻", "亅", "𠃌", "㇇", "乚",
    "㇉", "飛", "來", "氵", "匚", "丂", "㐄", "丿", "龵", "見", "貝",
    "頁", "丆", "疒", "⺧", "豕", "扌", "丬", "⺌", ""
}
char_font2: Set[str] = {"𠄎", "𡿨", "𫶧", "𧰨", "𬺰", "𦣞", "𣥂", "𭕄", ""}  # 文津2
char_font3: Set[str] = {"𰁜", "𳑳", "𰀁", ""}  # 文津3
char_font4: Set[str] = {""}  # 遍黑1
char_font5: Set[str] = {"ㅑ", "𘮌", ""}  # 遍黑2
# 宇浩
char_font6: Set[str] = {
    "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", ""
}
char_font7: Set[str] = {""}  # 98V
char_font8: Set[str] = {""}  # 98U

back_car_orange: str = "QWERTASDFGZXCVB"
num_key: str = "QWERTYUIOP"


class FontManager:
    def __init__(self, size: int = 33):
        self.fonts: Dict[int, FreeTypeFont] = {}
        self.size = size
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
        else:
            return ImageFont.truetype("字根图字体/Dengb.ttf", self.size), 0  # 等线，粗

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

    def draw(self, f: FontManager, back_car, symbol, text: str, swipe_down: str = "", width: int = 167, height: int = 232):
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # 加圆角边框
        draw.rounded_rectangle(
            xy=[0, 0, width, height],
            fill=None,  # 不填充
            outline="black",
            width=5,  # 边框宽度
            radius=0,  # 圆角半径
        )

        # 绘制背景字母
        back_font = ImageFont.truetype(
            font="字根图字体/IntelOneMono-Bold.ttf",
            size=230
        )
        back_color = (255, 204, 153) if back_car in back_car_orange else (221, 221, 221)
        b_x, b_y, b_height = f.get_center_pix(width, height, f=back_font, text=back_car)
        draw.text(xy=(b_x, b_y - 90), text=back_car, fill=back_color, font=back_font)
        # 绘制长按符号
        long_font = ImageFont.truetype(font="字根图字体/msyhbd.ttc", size=28)  # r"C:\Windows\Fonts\dengb.ttf"
        long_font2 = ImageFont.truetype(font="字根图字体/msyhbd.ttc", size=40)
        if back_car in num_key:  # 数字置顶
            draw.text(xy=(round(width / 2) - 7, -6), text=symbol, fill=(255, 0, 0), font=long_font)
        elif back_car in "AXCV":  # 汉字：全选复制粘贴剪切
            draw.text(xy=(width - 58, height - 30), text=symbol, fill=(255, 0, 0), font=long_font)
        elif back_car in "GS":  # 多个符号，特殊
            draw.text(xy=(width - 80, height - 33), text=symbol, fill=(255, 0, 0), font=long_font)
        elif back_car in "FKL":  # 多个符号
            draw.text(xy=(width - 60, height - 45), text=symbol, fill=(255, 0, 0), font=long_font2)
        else:  # 单个符号
            draw.text(xy=(width - 43, height - 47), text=symbol, fill=(255, 0, 0), font=long_font2)
        # 绘制下滑符号
        if swipe_down != "":
            draw.text(xy=(7, height - 50), text=swipe_down, fill=(26, 170, 47), font=long_font2)

        # 绘制字根
        c_color = "black"
        text_line_num = text.count("\n") + 1
        # 字符宽高均以等线字体为准
        x, y, c_height = f.get_center_pix(width, height, f=ImageFont.truetype("字根图字体/Dengb.ttf", size=f.size), text=text.split("\n")[0], line_n=text_line_num)

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

    h.draw(FontManager(size=20), back_car="A", symbol="全选", text="了\n")
    h.draw(FontManager(size=20), back_car="B", symbol="；", swipe_down="\\、", text="虎爪示瓜卜亦未末\n𰁜⺊ㅑ𳑳虍鹵灬\n馬魚礻")
    h.draw(FontManager(size=18), back_car="C", symbol="复制", text="乙世又女禾马生鼠尾\n亅𠃌𠄎㇇乚㇉𡿨\n飛來氵")
    h.draw(FontManager(size=20), back_car="D", symbol="#", text="己言母金口已长皮\n凵屮彑宀廴")
    h.draw(FontManager(size=20), back_car="E", symbol="3", text="的")
    h.draw(FontManager(size=18), back_car="F", symbol="$￥", text="一面手乃而牙电甲鱼\n𘮌匚丂𰀁㐄丿龵")
    h.draw(FontManager(size=18), back_car="G", symbol="%℃°", text="目皿厂夭广鹿麻儿\n九牛革罒見貝\n頁丆疒𫶧⺧豕𧰨\n扌")
    h.draw(FontManager(size=20), back_car="H", symbol="!", swipe_down="+", text="下框艮走自其田\n贝页习亥止辰\n冂勹冊龰\n齒")
    h.draw(FontManager(size=20), back_car="I", symbol="8", text="是")
    h.draw(FontManager(size=20), back_car="J", symbol="&", swipe_down="-", text="日早鬼门心巴骨上\n瓦工寸刀丰\n夕舟川臣矢巳\n曰𦣞忄丄𬺰\n巛巜咼冎")
    h.draw(FontManager(size=15), back_car="K", symbol="*・", swipe_down="——", text="八千里下弓白臼且框之\n两三撇戊丁入古甫辛戈\n彳纟弋丬")

    h.draw(FontManager(size=20), back_car="L", symbol="（）", swipe_down="=", text="两三竖匕非小方子\n穴高曲向幺\n予了干正欠\n糹丨〢〣𣥂⺌𭕄\n亠亡兀\n饣辶長镸髟")

    h.draw(FontManager(size=20), back_car="M", symbol="？", swipe_down="|", text="草不耳七也丑\n")
    h.draw(FontManager(size=20), back_car="N", symbol="：", text="点月缶壬足\n")
    h.draw(FontManager(size=20), back_car="O", symbol="9", text="O")
    h.draw(FontManager(size=20), back_car="P", symbol="0", text="大夫春雨犬\n")
    h.draw(FontManager(size=20), back_car="Q", symbol="1", text="几虫卯\n")
    h.draw(FontManager(size=20), back_car="R", symbol="4", text="王毛文立石\n单耳身黑\n")
    h.draw(FontManager(size=20), back_car="S", symbol="@®©", text="山倒尸用户至隶\n二点片木尤用舌\n")
    h.draw(FontManager(size=20), back_car="T", symbol="5", text="十巾火衣由尚\n")
    h.draw(FontManager(size=20), back_car="U", symbol="7", text="U")
    h.draw(FontManager(size=20), back_car="V", symbol="粘贴", text="土士见山斤米业车\n")
    h.draw(FontManager(size=20), back_car="W", symbol="2", text="人水合力食申\n")
    h.draw(FontManager(size=20), back_car="X", symbol="剪切", swipe_down="{", text="羊鸟乌\n")
    h.draw(FontManager(size=20), back_car="Y", symbol="6", text="竹气西双耳\n")
    h.draw(FontManager(size=20), back_car="Z", symbol="\"", swipe_down="[", text="[反查]")


if __name__ == "__main__":
    main()
