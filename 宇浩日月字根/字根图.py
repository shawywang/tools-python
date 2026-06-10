import platform
import sys
from typing import Dict

from PIL import Image, ImageDraw, ImageFont

key_images: str = "qwertyuiopasdfghjklzxcvbnm"
ps = platform.system().lower()

# 六寸相纸（无白边打印）：152*102毫米，打印像素：1685*1131pix
# 相框可装尺寸：151*111毫米，能装下6寸相纸
# 显示屏16:9，照片像素应为：1685*948pix，上下空白像素应为116

mnemonic1: str = (
    "Q 几虫卯\n"
    "    ji ho mi\n"
    "W 人水合力食申\n"
    "      o  ko he li ka ke\n"
    "R 王毛文立石，单耳身黑\n"
    "    o  mi  i li ka       je   ke ho\n"
    "T 十巾火由尚\n"
    "   ka jo ho  u  ke\n"
    "Y 竹气西双耳\n"
    "    su qi xi   fu\n"
    "P 大夫𡗗雨犬\n"
    "   da fu di e  qi"
)
mnemonic2: str = (
    "S 山倒尸至二隶户，竖点片木尤用舌\n"
    "      ji  ka si  o  li hu      o    pe me  u  i  ke\n"
    "D 己言母金口，已长皮\n"
    "    ji e  me jo ke     i re pi\n"
    "F 一面手乃，而牙电甲鱼\n"
    "    i  me ke ne     o  a  di ja e\n"
    "G 目皿厂夭，广鹿麻儿九牛革\n"
    "    me mo  a  i     go lu ma o  ju nu ge"
)
mnemonic3: str = (
    "H 艮走亥其田，自习贝页止辰\n"
    "    ge ze he qi ti     zi xi bo e si re\n"
    "J 日早瓦工寸刀丰，夕川鬼门心巴骨，舟上臣矢巳\n"
    "   i  zi a  gi ci di fe     xi ri go me xo ba gu     se ke re ka si\n"
    "K 八千里，弓下白臼入框，三丁古，戈戊且之辛甫\n"
    "    ba qi li     gi xa be ju e  o     sa di gu      ge u qe si xo fu\n"
    "L 匕非子穴高曲向小，幺方予亡了干正欠\n"
    "   bi fo zi xe gi qe xo xi     i  fe  e  o  le ga se qi"
)
mnemonic4: str = (
    "X 横点羊鸟乌\n"
    "      ci   o  ni u\n"
    "C 乙世又女马禾生\n"
    "    i  ka u  ne ma he ke\n"
    "V 土士见山斤米业车\n"
    "    du ke je ka jo mi  e re\n"
    "B 虎爪示瓜卜，亦未末\n"
    "    hu sa ka ga bu    i  o  mo\n"
    "N 丶月缶壬足\n"
    "     di e  fe o  zu\n"
    "M 草头不耳七也丑\n"
    "       ci  bu  o  qi e  re"
)

m_font = "字根图字体/Dengb.ttf"
m_size = 25
a_font = "字根图字体/MONACO.TTF"
a_size = 15


class Handle:
    def __init__(self):
        pass

    def get_font_for_char(self, char):
        if char in "abcdefghijklmnopqrstuvwxyz":
            return ImageFont.truetype(font=a_font, size=a_size)
        elif char in {"𡗗"}:
            return ImageFont.truetype(font="字根图字体/PlangothicP1-Regular.ttf", size=(a_size + 10))
        else:
            return ImageFont.truetype(font=m_font, size=m_size)  # 等线，粗

    def drawmne(self, n_x, n_y, draw, mnemonic):
        _, t1, _, b1 = ImageFont.truetype(font=a_font, size=a_size).getbbox("j")
        alpha_height = b1 - t1
        _, t2, _, b2 = ImageFont.truetype(font=m_font, size=m_size).getbbox("我")
        c_height = b2 - t2
        cur_x = n_x
        cur_y = n_y
        last_c_is_alpha: bool = False
        for i, c in enumerate(mnemonic):
            if c == '\n':
                if last_c_is_alpha:
                    cur_y += (alpha_height // 1.5)
                elif not last_c_is_alpha:
                    cur_y += (c_height + c_height // 3)
                cur_x = n_x
                continue
            font = self.get_font_for_char(c)
            if c in "abcdefghijklmnopqrstuvwxyz" or c == " ":
                last_c_is_alpha = True
                draw.text(xy=(cur_x, cur_y - 8), text=c, fill=(95, 95, 95), font=font)
            else:
                last_c_is_alpha = False
                if c in {"几", "合", "力", "立", "气", "西", "隶", "户", "木", "己", "已", "皮", "一", "电",
                         "鹿", "革", "艮", "其", "田", "自", "习", "丰", "夕", "门", "巴", "骨", "巳", "八",
                         "千", "里", "三", "丁", "古", "戈", "甫", "匕", "子", "小", "了", "干", "欠", "不",
                         "七", "大", "夫", "鸟", "乙", "马", "禾", "米", "虎", "卜", "亦", "末", "丶", "足"
                         }:
                    draw.text(xy=(cur_x, cur_y), text=c, fill=(26, 170, 47), font=font)
                else:
                    draw.text(xy=(cur_x, cur_y), text=c, fill="black", font=font)
            bbox = font.getbbox(c)
            c_width = bbox[2] - bbox[0]
            cur_x += c_width

    def draw26(self):
        key_width = 167
        key_height = 232
        padding_h = -2  # 键之间的距离：水平方向
        padding_v = 15  # 键之间的距离：竖直方向
        lr: int = 30  # 画布左、右空白像素
        ud_u: int = 80  # 画布上空白像素
        ud_d: int = 342  # 画布下空白像素
        keyboard_layout = [
            list("qwertyuiop"),
            list("asdfghjkl"),
            list("zxcvbnm"),
        ]
        # 键盘底图，宽1703，高958
        keyboard_width = len(keyboard_layout[0]) * (key_width + padding_h) - padding_h + lr * 2  # 左右空白
        keyboard_height = len(keyboard_layout) * (key_height + padding_v) - padding_v + ud_u + ud_d  # 上下空白，以适配宽/高=1920/1080
        keyboard_image = Image.new("RGB", (keyboard_width, keyboard_height), (255, 255, 255))
        draw = ImageDraw.Draw(keyboard_image)
        # 加边框
        draw.rectangle(
            xy=[0, 0, keyboard_width, keyboard_height],
            fill=None,  # 不填充
            outline=(255, 228, 201),
            width=30,  # 边框宽度
        )
        # 加载单键文件
        letter_images = {letter: Image.open(f"/Users/wangxiao/Downloads/{letter}.webp") for letter in key_images}
        y_offset = ud_u  # 上方有155像素的空白
        x_add: Dict[int, int] = {  # 不同行起始位置偏移量
            0: 0 + lr,
            1: round(key_width * 0.4) + lr,
            2: round(key_width * 1.2) + lr,
        }
        for n, row in enumerate(keyboard_layout):
            x_offset = x_add[n]
            for l in row:
                keyboard_image.paste(letter_images[l], (x_offset, y_offset))
                x_offset += (key_width + padding_h)
            y_offset += (key_height + padding_v)

        # 加备注文字
        n_x = round(key_width * 1.2) + lr
        n_y = 3 * (key_height + padding_v) + ud_u
        n_font1 = ImageFont.truetype(font="字根图字体/Dengb.ttf", size=25)
        n_font2 = ImageFont.truetype(font="字根图字体/IntelOneMono-Bold.ttf", size=20)

        draw.text(xy=(lr, ud_u - 35), text="宇浩日月", fill=(0, 0, 0), font=n_font1)
        draw.text(xy=(lr + 138, ud_u - 35), text="https://shurufa.app", fill=(0, 0, 0), font=n_font2)

        # 加口诀
        self.drawmne(n_x=50, n_y=n_y, draw=draw, mnemonic=mnemonic1)
        self.drawmne(n_x=370, n_y=n_y, draw=draw, mnemonic=mnemonic2)
        self.drawmne(n_x=810, n_y=n_y, draw=draw, mnemonic=mnemonic3)
        self.drawmne(n_x=1400, n_y=n_y, draw=draw, mnemonic=mnemonic4)

        # 保存
        palette_img = Image.new("P", (1, 1))  # 调色板
        palette_img.putpalette(
            [
                0, 0, 0,  # 黑色
                255, 0, 0,  # 红色
                26, 170, 47,  # 绿色
                255, 255, 255,  # 白色
                255, 204, 153,  # 浅橙色
                255, 228, 201,  # 浅浅橙色
                95, 95, 95,  # 灰色
                221, 221, 221,  # 浅灰色
            ]
        )
        fixed_image = keyboard_image.quantize(palette=palette_img, dither=Image.Dither.NONE)
        if ps == "windows":
            dir_fp: str = f"C:\\Users\\wangxiao\\Downloads\\字根图（PIL生成）"
        elif ps == "darwin":  # macOS
            dir_fp: str = f"/Users/wangxiao/Downloads/字根图（PIL生成）"
        else:
            sys.exit(-1)

        fixed_image.save(
            fp=f"{dir_fp}.webp",
            optimize=True,
            compress_level=5,
            dpi=(72, 72),
            format="WEBP",
            quality=80,
        )
        fixed_image.save(
            fp=f"{dir_fp}.png",
            optimize=True,
            compress_level=5,
            dpi=(72, 72),
            format="PNG",
            quality=80,
        )


def main():
    h = Handle()
    h.draw26()


if __name__ == "__main__":
    main()
