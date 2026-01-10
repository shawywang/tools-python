import mimetypes
import os
import platform
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Set, Optional, Tuple, Dict

import pytz
from PIL import Image

shanghai_tz = pytz.timezone('Asia/Shanghai')
'''
支持的图片文件名类型（不限后缀）：
IMG_20250709_223914.jpg
B612Kaji_20250802_215204_683.jpg
B612Kaji_20250802_190608_673_edit_68650861669746.jpg
Screenshot_20250622_204910_com.tencent.mm.jpg
Screenshot_20250716_220517_com.tencent.mm_edit_10.jpg

时间戳：去掉某位3个数字之后是时间戳：1753107698解析为2025-07-21 22:21:38
    验证：https://tool.lu/timestamp/
mmexport1736867692236.jpg
wx_camera_1755962155780.png
tb_image_share_1721454235031.jpg
Camera_XHS_17253837228271040g008312s3613okk005p9n.jpg
photo_take_1752233284821.jpg
屏幕截图 2025-11-04 130018.png
'''

ps = platform.system().lower()
data_time: Dict[int, str] = {
    # 不用改
    0: r'(20\d{2})\.(\d{1,2})\.(\d{1,2})_(\d{4})\.',  # 2025.5.12_0812.jpg
    1: r'(20\d{2})\.(\d{1,2})\.(\d{1,2})\.',  # 2025.5.12.jpg
    # 改序号，日期不能变
    2: r'(20\d{2})\.(\d{1,2})\.(\d{1,2})_(\d{1,2})\.',  # 2025.5.12_序号.jpg
    3: r'(20\d{2})\.(\d{1,2})\.(\d{1,2})_(\d{4})_',  # 2025.5.12_0812_序号.jpg
    # 识别日期、时间为连续6位数
    4: r'(20\d{2})(\d{2})(\d{2})_(\d{6})',  # 20251025_124308
    5: r'(20\d{2})(\d{2})(\d{2})-(\d{6})',  # 20201008-224222
    6: r'(20\d{2})(\d{2})(\d{2})(\d{6})',  # 20191117132350
    7: r'(20\d{2})-(\d{2})-(\d{2}) (\d{6})',  # 2025-11-04 130018
    # 识别日期、时间为2*3共6位数
    8: r'(20\d{2})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})',  # 2025-03-25_13-12-40
    9: r'(20\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})',  # 2016-08-24-09-44-01
}
times_tamp: Dict[int, str] = {
    0: r'wx_camera_(1\d{9})',
    1: r'mmexport(1\d{9})',
    2: r'tb_image_share_(1\d{9})',
    3: r'Camera_XHS_(1\d{9})',
    4: r'photo_take_(1\d{9})',
    5: r'Image_(1\d{9})',
    6: r'Video_(1\d{9})',
    7: r'(1\d{12})',
}


# /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pip install --upgrade pip
# C:\ProgramData\miniconda3\python.exe -m pip install --upgrade pip


def withdraw_time(timestamp: int) -> Tuple[str, str, str, str]:
    dt = datetime.fromtimestamp(timestamp, tz=shanghai_tz)
    year = str(dt.year)
    month = str(dt.month)
    day = str(dt.day)
    hour = str(dt.hour).rjust(2, "0")
    minute = str(dt.minute).rjust(2, "0")
    return year, month, day, hour + minute


def extract_date(filename, directory: str) -> Tuple[str, str, str, str]:
    # ================== 显式的日期时间
    for i, dt in data_time.items():
        dm: Optional[re.Match] = re.search(dt, filename)
        if dm:
            if i in (0, 1):
                return "不用修改", "", "", ""
            if i == 2:
                year, month, day, _ = dm.groups()
                m = str(month.lstrip("0"))
                d = str(day.lstrip("0"))
                return year, m, d, "0"
            if i == 3:
                year, month, day, time = dm.groups()
                m = str(month.lstrip("0"))
                d = str(day.lstrip("0"))
                t: str = time
                return year, m, d, t
            if i in (4, 5, 6, 7):
                year, month, day, time = dm.groups()
                m = str(month.lstrip("0"))
                d = str(day.lstrip("0"))
                t: str = time[:-2]
                return year, m, d, t
            if i in (8, 9):
                year, month, day, hour, min, sec = dm.groups()
                m = str(month.lstrip("0"))
                d = str(day.lstrip("0"))
                t: str = hour + min
                return year, m, d, t
    # ================== 时间戳
    for i, t in times_tamp.items():
        ts: Optional[re.Match] = re.search(t, filename, re.IGNORECASE)
        if ts:
            if i in (0, 1, 2, 3, 4, 5, 6):
                return withdraw_time(int(ts.group(1)))
            if i == 7:
                stamp: int = int(ts.group(1)[:-3])
                return withdraw_time(stamp)
    # ================== 从EXIF取，或文件系统日期
    sys_datetime = get_datetime_sys(directory, filename)
    print(f"遇到疑问，把{filename}改成{sys_datetime}？")
    confirm = input("确认删除？输入Y：")
    if confirm == "Y":
        return sys_datetime
    else:
        sys.exit(-1)


def get_datetime_sys(directory, filename: str) -> Tuple[str, str, str, str]:
    f_type = get_file_type_by_mime(os.path.join(directory, filename))
    if f_type == "图片":
        try:
            with Image.open(os.path.join(directory, filename)) as img:
                exif_data = img.getexif()
                if exif_data and 306 in exif_data:  # 拍摄时间36867、图片数字化时间36868
                    try:
                        data_t = datetime.strptime(exif_data[306], "%Y:%m:%d %H:%M:%S")
                    except Exception as e:
                        print("exif无拍摄时间", end='')
                        return get_datetime_from_file_sys(directory, filename)
                    year = str(data_t.year)
                    month = str(data_t.month)
                    day = str(data_t.day)
                    hour = str(data_t.hour).rjust(2, "0")
                    minute = str(data_t.minute).rjust(2, "0")
                    print("从exif中获取306；", end='')
                    return year, month, day, hour + minute
                else:  # 读取文件系统信息
                    return get_datetime_from_file_sys(directory, filename)
        except Exception as e:
            print(f"文件{filename}无任何可用日期信息：{e}")
            sys.exit(-1)
    elif f_type == "视频":
        try:
            # 读取文件系统信息
            return get_datetime_from_file_sys(directory, filename)
        except Exception as e:
            print(f"文件{filename}无任何可用日期信息：{e}")
            sys.exit(-1)
    else:
        return "不用修改", "", "", ""


def get_datetime_from_file_sys(directory, filename: str):
    stat = os.stat(os.path.join(directory, filename))
    mod_time = datetime.fromtimestamp(stat.st_mtime)  # 最后修改时间
    if ps == "windows":
        create_time = datetime.fromtimestamp(stat.st_ctime)
    else:
        create_time = datetime.fromtimestamp(stat.st_birthtime)
    fi_t = create_time if create_time < mod_time else mod_time
    year = str(fi_t.year)
    month = str(fi_t.month)
    day = str(fi_t.day)
    hour = str(fi_t.hour).rjust(2, "0")
    minute = str(fi_t.minute).rjust(2, "0")
    print("从文件系统中获取；", end='')
    return year, month, day, hour + minute


def generate_new_name(date: Tuple[str, str, str, str], ext: str, existing_names: Set[str]):
    year, month, day, time = date
    if time != "0":
        name: str = f"{year}.{month}.{day}_{time}{ext}"
    else:
        name: str = f"{year}.{month}.{day}{ext}"

    if name not in existing_names:
        existing_names.add(name)
        return name, True  # 直接使用规范命名

    counter: int = 2
    if time != "0":
        while True:
            new_name: str = f"{year}.{month}.{day}_{time}_{counter}{ext}"
            if new_name not in existing_names:
                existing_names.add(new_name)
                return new_name, False  # 末尾加了序号
            counter += 1
    else:
        while True:
            new_name: str = f"{year}.{month}.{day}_{counter}{ext}"
            if new_name not in existing_names:
                existing_names.add(new_name)
                return new_name, False  # 末尾加了序号
            counter += 1


def get_file_type_by_mime(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith('video/'):
        return "视频"
    elif mime_type and mime_type.startswith('image/'):
        return "图片"
    elif mime_type and mime_type.startswith('text/'):
        return "文本"
    else:
        return "其他"


class Handle:
    def __init__(self):
        pass

    def rename_files(self, directory: str):
        dont_renames: Set[str] = set()  # 已经规范的文件名，不用改了
        existing_names: Set[str] = set()  # 当前文件夹所有文件名
        # 第一次遍历，把已经为规范名的文件，添加到已存在的库中
        for f1 in os.listdir(directory):
            if f1 == ".DS_Store" or f1.startswith("."):
                continue
            if os.path.isdir(os.path.join(directory, f1)):
                continue
            existing_names.add(f1)
            date = extract_date(f1, directory)
            if date[0] == "不用修改":
                dont_renames.add(f1)

        print("\n\n====第二次遍历，修改文件名====\n\n")
        for f2 in os.listdir(directory):
            if f2 == ".DS_Store" or f2.startswith("."):
                continue
            if os.path.isdir(os.path.join(directory, f2)):
                continue
            if f2 in dont_renames:
                continue
            date = extract_date(f2, directory)
            ext: str = Path(f2).suffix  # 文件原来的后缀
            if ext == ".ini":
                continue
            existing_names.remove(f2)
            new_name, flag = generate_new_name(date, ext, existing_names)
            old_path: str = os.path.join(directory, f2)
            new_path: str = os.path.join(directory, new_name)

            if old_path == new_path:
                existing_names.add(f2)
                continue

            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"重命名: {f2} -> {new_name}")
            else:
                print(f"出错！文件已存在：{f2} -> {new_name}")
                existing_names.add(f2)
                sys.exit(-1)


def main():
    h = Handle()
    if ps == "windows":
        dir: str = r"C:\Users\wangxiao\Downloads"
    elif ps == "linux":
        dir: str = ""
    elif ps == "darwin":  # macOS
        dir: str = "/Users/wangxiao/Downloads"
        # dir: str = "/Volumes/RTL9210/6/手机3/别人的"
    else:
        dir: str = ""

    h.rename_files(dir)


if __name__ == "__main__":
    main()
