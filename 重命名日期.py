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


# /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m pip install --upgrade pip
# C:\ProgramData\miniconda3\python.exe -m pip install --upgrade pip

# 合并文件夹，为了避免重复，重复的文件在日期前面加a之类，不要在后面加


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
    data_time: Dict[int, str] = {
        0: r'(20\d{2})\.(\d{1,2})\.(\d{1,2})',  # 2025.5.12
        1: r'(20\d{2})(\d{2})(\d{2})_(\d{6})',  # 20251025_124308
        2: r'(20\d{2})(\d{2})(\d{2})-(\d{6})',  # 20201008-224222
        3: r'(20\d{2})(\d{2})(\d{2})(\d{6})',  # 20191117132350
        4: r'(20\d{2})-(\d{2})-(\d{2}) (\d{6})',  # 2025-11-04 130018
        5: r'(20\d{2})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})',  # 2025-03-25_13-12-40
        6: r'(20\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})',  # 2016-08-24-09-44-01
    }
    for i, dt in data_time.items():
        dm: Optional[re.Match] = re.search(dt, filename)
        if dm:
            if i == 0:
                print(f"不用修改。", end='')  # 已经改过名字了的文件
                return None
            if i in (1, 2, 3, 4):
                year, month, day, time = dm.groups()
                m = str(month.lstrip("0"))
                d = str(day.lstrip("0"))
                t: str = time[:-2]
                return year, m, d, t
            if i in (5, 6):
                year, month, day, hour, min, sec = dm.groups()
                m = str(month.lstrip("0"))
                d = str(day.lstrip("0"))
                t: str = hour + min
                return year, m, d, t
    # ================== 时间戳
    timestamp: Dict[int, str] = {
        0: r'wx_camera_(1\d{9})',
        1: r'mmexport(1\d{9})',
        2: r'tb_image_share_(1\d{9})',
        3: r'Camera_XHS_(1\d{9})',
        4: r'photo_take_(1\d{9})',
        5: r'Image_(1\d{9})',
        6: r'Video_(1\d{9})',
        7: r'(1\d{12})',
    }
    for i, t in timestamp.items():
        ts: Optional[re.Match] = re.search(t, filename, re.IGNORECASE)
        if ts:
            if i in (0, 1, 2, 3, 4, 5, 6):
                return withdraw_time(int(ts.group(1)))
            if i == 7:
                stamp: int = int(ts.group(1)[:-3])
                return withdraw_time(stamp)
    # ================== 从EXIF取，或文件系统日期
    return get_image_date_info(os.path.join(directory, filename))


def generate_new_name(date: Tuple[str, str, str, str], ext: str, existing_names: Set[str]) -> str:
    year, month, day, time = date
    name: str = f"{year}.{month}.{day}_{time}{ext}"

    if name not in existing_names:
        existing_names.add(name)
        return name
    counter: int = 2
    while True:
        new_name: str = f"{year}.{month}.{day}_{time}_{counter}{ext}"
        if new_name not in existing_names:
            existing_names.add(new_name)
            return new_name
        counter += 1


def get_image_date_info(f: str) -> Tuple[str, str, str, str]:
    try:
        with Image.open(f) as img:
            exif_data = img.getexif()
            if exif_data and 306 in exif_data:  # 拍摄时间36867、图片数字化时间36868
                data_t = datetime.strptime(exif_data[306], "%Y:%m:%d %H:%M:%S")
                year = str(data_t.year)
                month = str(data_t.month)
                day = str(data_t.day)
                hour = str(data_t.hour).rjust(2, "0")
                minute = str(data_t.minute).rjust(2, "0")
                print("从exif中获取306；", end='')
                return year, month, day, hour + minute
            else:  # 读取文件系统信息
                stat = os.stat(f)
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
    except Exception as e:
        print(f"获取文件{f}日期信息失败:{e}")
        sys.exit(-1)


def rename_files(directory: str):
    existing_names: Set[str] = set()
    for f in os.listdir(directory):
        if f == ".DS_Store" or f.startswith("."):
            continue
        date = extract_date(f, directory)
        if date:
            ext: str = Path(f).suffix  # 文件原来的后缀
            if ext == ".ini":
                continue
            new_name: str = generate_new_name(date, ext, existing_names)
            old_path: str = os.path.join(directory, f)
            new_path: str = os.path.join(directory, new_name)
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"重命名: {f} -> {new_name}")
            else:
                print(f"警告！文件已存在，跳过：{f} -> {new_name}")
        else:
            print(f"文件名提取不出日期: {f}", end='')
            get_image_date_info(os.path.join(directory, f))


def main():
    if ps == "windows":
        dir: str = r"C:\Users\wangxiao\Downloads\Phone Link"
    elif ps == "linux":
        dir: str = ""
    elif ps == "darwin":  # macOS
        # dir: str = "/Users/wangxiao/Downloads"
        dir: str = "/Volumes/RTL9210/6/手机3/别人的"
    else:
        dir: str = ""

    rename_files(dir)


if __name__ == "__main__":
    main()
