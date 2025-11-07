# 管理员运行：
# C:\ProgramData\miniconda3\python.exe -m pip install --upgrade pip
# Install-Module PSReadLine -MinimumVersion 2.0.3 -Scope CurrentUser -Force
# C:\ProgramData\miniconda3\python.exe -m pip install pillow svgelements cairosvg pycairo cairocffi==0.8
import io
import os
import sys
from typing import List

import cairosvg
import send2trash
from PIL import Image


def safe_delete_files(folder_p: str):
    if os.path.isdir(folder_p):
        to_delete: List[str] = []
        for f in os.listdir(folder_p):
            file_path = os.path.join(folder_p, f)
            if os.path.isfile(file_path):
                print(f"即将删除：{file_path}")
                to_delete.append(f"{file_path}")
        if len(to_delete) > 0:
            confirm = input("确认删除？输入YES")
            if confirm == "YES":
                for f in to_delete:
                    send2trash.send2trash(f)
                print("已放入回收站")
            else:
                print("取消操作")


class Handle:
    def __init__(self):
        pass

    def syg_to_mini_png(self, in_dir, out_dir, f_name: str, target_width=200):
        out_name: str = f"{f_name.split('.')[0]}.png"
        svg_path: str = f"{in_dir}\\{f_name}"
        png_path: str = f"{out_dir}\\{out_name}"
        png_data = cairosvg.svg2png(
            url=svg_path,
            output_width=target_width,
            background_color="white",
        )
        img = Image.open(io.BytesIO(png_data))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        palette = [
            0, 0, 0,  # 黑色
            255, 0, 0,  # 红色
            255, 255, 255,  # 白色
        ]

        palette_img = Image.new("P", (1, 1))
        palette_img.putpalette(palette * 32)
        quantized_img = img.quantize(palette=palette_img, dither=Image.Dither.NONE)
        quantized_img.save(  # PIL默认dpi=会改成72
            png_path,
            optimize=True,  # 启用PNG优化
            compress_level=9,  # 最高压缩级别
            dpi=(72, 72),  # 降低DPI
            format='PNG',
        )
        svg_size = os.path.getsize(svg_path) / 1024
        png_size = os.path.getsize(png_path) / 1024
        print(f"{f_name} -> {out_name}，转换完成：{svg_size}kb -> {png_size}kb", end='')
        print(f"压缩率：{png_size / svg_size}倍")

    def cutbox(self, in_dir, out_dir, f_name: str, margin: int = 0):  # 默认边距0
        out_type: str = "WEBP"
        with Image.open(f"{in_dir}\\{f_name}") as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            # 获取非透明区域的边界框
            bbox = img.getbbox()
            if bbox:
                # 添加边距
                x1, y1, x2, y2 = bbox
                x1 = max(0, x1 - margin)
                y1 = max(0, y1 - margin)
                x2 = min(img.width, x2 + margin)
                y2 = min(img.height, y2 + margin)
                # 裁剪图片
                cropped_img = img.crop((x1, y1, x2, y2))
                # 保存为WebP格式，保持透明度
                cropped_img.save(  # PIL默认dpi=会改成72
                    f"{out_dir}\\{f_name.split('.')[0]}.{out_type.lower()}",
                    out_type,
                    quality=80
                )

    def reduce_space(self, in_dir, out_dir, f_name: str):
        out_type: str = "WEBP"
        with Image.open(f"{in_dir}\\{f_name}") as img_1:
            # 降低图像的宽、高像素
            wight_px: int = 80
            high_px: int = (img_1.size[1] * wight_px) // img_1.size[0]
            img_2 = img_1.resize((wight_px, high_px), Image.Resampling.LANCZOS)

            if img_2.mode in {"RGBA", "P", "LA"}:
                img = img_2.convert("RGBA")
                white_bg = Image.new("RGBA", img_2.size, (255, 255, 255, 255))
                # img_3 = Image.alpha_composite(white_bg, img).convert("RGB")  # 使用alpha通道粘贴，再转为rgb，丢弃alpha通道
                white_bg.paste(img, mask=img.split()[3])  # 使用alpha通道粘贴，再转为rgb，丢弃alpha通道
                img_3 = white_bg.convert("RGB")
            else:
                img_3 = img_2.convert("RGB")  # 确保无alpha

            # 色深，没必要改，已经很低了
            img_4 = img_3.quantize(colors=64, method=0, dither=Image.Dither.FLOYDSTEINBERG)
            img_4 = img_3.quantize(colors=64)

            # 保存图像
            img_3.save(  # PIL默认dpi=会改成72
                f"{out_dir}\\{f_name.split('.')[0]}.{out_type.lower()}",
                out_type,
                quality=100
            )

    def svg_to_mini_png_all(self, in_dir: str, out_dir: str):
        safe_delete_files(out_dir)
        for f in os.listdir(in_dir):
            f_path = os.path.join(in_dir, f)
            if os.path.isfile(f_path):
                try:
                    self.syg_to_mini_png(in_dir, out_dir, f)
                except Exception as e:
                    print(f"处理时发生异常：{f}")
                    sys.exit(-1)

    def cutbox_all(self, in_dir: str, out_dir: str):
        safe_delete_files(out_dir)
        for f in os.listdir(in_dir):
            f_path = os.path.join(in_dir, f)
            if os.path.isfile(f_path):
                try:
                    self.cutbox(in_dir, out_dir, f)  # 裁剪png、webp等格式白边，对高压缩率（失去形状边缘）无效
                except Exception as e:
                    print(f"处理时发生异常：{f}")
                    sys.exit(-1)

    def reduce_space_all(self, in_dir: str, out_dir: str):
        safe_delete_files(out_dir)
        for f in os.listdir(in_dir):
            f_path = os.path.join(in_dir, f)
            if os.path.isfile(f_path):
                try:
                    self.reduce_space(in_dir, out_dir, f)  # 压缩图片
                except Exception as e:
                    print(f"处理时发生异常：{f}")
                    sys.exit(-1)


def main():
    print(f"CairoSVG版本：{cairosvg.__version__}")
    h = Handle()
    # h.svg_to_mini_png_all(r"C:\Users\wangxiao\Nutstore\1\我的坚果云\打字\逸码\键盘助记svg源", r"C:\Users\wangxiao\Nutstore\1\我的坚果云\打字\逸码\键盘助记svg源\压缩转png、手工裁剪后")
    # h.cutbox_all(r"C:\Users\wangxiao\Nutstore\1\我的坚果云\打字\逸码\键盘助记svg源\压缩转png、手工裁剪后", r"C:\Users\wangxiao\Nutstore\1\我的坚果云\打字\逸码\键盘助记svg源\压缩转png、手工裁剪后\压缩")
    # h.reduce_space_all(r"C:\Users\wangxiao\Nutstore\1\我的坚果云\打字\逸码\键盘助记svg源\压缩转png、手工裁剪后", r"C:\Users\wangxiao\Nutstore\1\我的坚果云\打字\逸码\键盘助记svg源\压缩转png、手工裁剪后\压缩")

    # h.svg_to_mini_png_all(r"C:\Users\wangxiao\Downloads\svg源", r"C:\Users\wangxiao\Downloads\svg源\压缩转png、手工裁剪")
    # h.cutbox_all(r"C:\Users\wangxiao\Downloads\Phone Link", r"C:\Users\wangxiao\Downloads\Phone Link\裁剪")
    # h.reduce_space_all(r"C:\Users\wangxiao\Downloads\Phone Link\裁剪", r"C:\Users\wangxiao\Downloads\Phone Link\裁剪\压缩")


if __name__ == "__main__":
    main()
"""
    1.字根图.pptx中，ctrl+a选择单一键元素，保存为26张.svg
    2.格式工厂将.svg转换为.webp
    3.self.cutbox剪掉边框
    4.self.reduce_color压缩
1.ppt全选元素存为.svg
2.用cairo包，把svg读成字节流，调色板手工设定红、黑、白3色，关闭抖动，启用PNG优化，降低DPI到72，存为png（10kb以内）
3.手工裁剪白边（有的键的方框已经被极限压没了，自动裁剪失败）
4.最后一次压缩，用白底叠加alpha通道，并丢弃；再压缩色深为18，存为.webp

"""
