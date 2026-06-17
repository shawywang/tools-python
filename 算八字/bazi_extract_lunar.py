#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字四柱提取 — 简化版
输入 lunardate.LunarDate + 时辰，直接输出四柱干支
无需公历→农历转换，也无需 lunarcalendar 库
"""

import csv
import os
from datetime import date
from typing import Tuple, Dict, Optional

from lunardate import LunarDate

LOOKUP = os.path.join(os.path.dirname(__file__), 'day_gan_zhi_lookup_final.csv')

# ========== 基础常量 ==========
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五虎遁：甲己年→寅月天干=丙(2)，乙庚年→寅月天干=戊(4) ...
# 甲己之年丙作首——逢年干是甲或己的年份，正月的月干从丙上起
# 乙庚之岁戊为头——逢年干是乙或庚的年份，正月的月干从戊上起
# 丙辛必定寻庚起——逢年干是丙或辛的年份，正月的月干从庚上起
# 丁壬壬位顺行流——逢年干是丁或壬的年份，正月的月干从壬上起
# 若问戊癸何方发，甲寅之上好追求——逢年干是戊或癸的年份，正月的月干从甲上起
WU_HU_DUN = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}

# 五鼠遁：甲己日→子时天干=甲(0)，乙庚日→子时天干=丙(2) ...
WU_SHU_DUN = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}

# ========== 二十四节气——"节"（月令分界点）日期表 ==========
# 每个元组代表该节气起始的(月, 日)
# 顺序固定（对应地支索引 0~11）：
#   小寒→丑(0), 立春→寅(1), 惊蛰→卯(2), 清明→辰(3),
#   立夏→巳(4), 芒种→午(5), 小暑→未(6), 立秋→申(7),
#   白露→酉(8), 寒露→戌(9), 立冬→亥(10), 大雪→子(11)
# 格式：JIE_DATES_TABLE = {
#     (起始年份, 结束年份): [ (月, 日), (月, 日), ... ],
#     ...
# }
JIE_DATES_TABLE = {
    (2020, 2035): [
        (1, 6),   # 小寒 → 丑月
        (2, 4),   # 立春 → 寅月
        (3, 5),   # 惊蛰 → 卯月
        (4, 5),   # 清明 → 辰月
        (5, 6),   # 立夏 → 巳月
        (6, 5),   # 芒种 → 午月
        (7, 7),   # 小暑 → 未月
        (8, 7),   # 立秋 → 申月
        (9, 7),   # 白露 → 酉月
        (10, 8),  # 寒露 → 戌月
        (11, 7),  # 立冬 → 亥月
        (12, 7),  # 大雪 → 子月
    ],
}


def _get_jie_dates(year: int) -> list:
    """根据年份查找对应的节气日期表，兜底用 2020~2035 的数值"""
    for (y_start, y_end), dates in JIE_DATES_TABLE.items():
        if y_start <= year <= y_end:
            return dates
    return JIE_DATES_TABLE[(2020, 2035)]


def get_year_gan_zhi(lunar_date: LunarDate) -> Tuple[str, str]:
    """年柱：直接用农历年份（用户已传正确的农历日期）"""
    gan_idx = (lunar_date.year - 4) % 10
    zhi_idx = (lunar_date.year - 4) % 12
    return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]


def _get_month_zhi_approx(year: int, month: int, day: int) -> str:
    """按月+日判断月支（按节气），使用年份查表确定节气日期"""
    dates = _get_jie_dates(year)
    # 遍历 12 个月支，判断公历日期落在哪个节气区间内
    for i in range(12):
        cur_m, cur_d = dates[i]
        next_m, next_d = dates[(i + 1) % 12]
        if (month == cur_m and day >= cur_d) or (month == next_m and day < next_d):
            return DI_ZHI[i]
    return DI_ZHI[0]  # 兜底


def get_month_gan_zhi(year_gan: str, solar_d: date) -> Tuple[str, str]:
    """月柱：月支（按节气近似，需公历日期）+ 月干（五虎遁）"""
    month_zhi = _get_month_zhi_approx(solar_d.year, solar_d.month, solar_d.day)
    year_gan_idx = TIAN_GAN.index(year_gan)
    base_gan_idx = WU_HU_DUN[year_gan_idx]
    offset = (DI_ZHI.index(month_zhi) - 2) % 12
    month_gan = TIAN_GAN[(base_gan_idx + offset) % 10]
    return month_gan, month_zhi


def _load_day_lookup() -> Optional[dict]:
    """加载日柱查表CSV"""
    if not os.path.exists(LOOKUP):
        return None
    lookup = {}
    with open(LOOKUP, 'r', encoding='utf-8') as f:
        for row in csv.reader(f):
            if len(row) >= 3:
                lookup[row[0].strip()] = (row[1].strip(), row[2].strip())
    return lookup


_DAY_LOOKUP: Optional[dict] = None


def get_day_gan_zhi(solar_d: date) -> Tuple[str, str]:
    """日柱：优先查表，回退公式"""
    global _DAY_LOOKUP

    if _DAY_LOOKUP is None:
        _DAY_LOOKUP = _load_day_lookup()
    if _DAY_LOOKUP is not None:
        key = solar_d.strftime('%Y-%m-%d')
        if key in _DAY_LOOKUP:
            return _DAY_LOOKUP[key]

    # 公式法：2000-01-01 = 戊午日（干4, 支6）
    base = date(2000, 1, 1)
    days = (solar_d - base).days
    gan_idx = (4 + days) % 10
    zhi_idx = (6 + days) % 12
    return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]


def get_hour_gan_zhi(day_gan: str, hour: int, minute: int = 0) -> Tuple[str, str]:
    """时柱：时支（时间段）+ 时干（五鼠遁）"""
    total_min = hour * 60 + minute
    if total_min < 60 or total_min >= 1380:
        zhi_idx = 0  # 子 23-1
    elif total_min < 180:
        zhi_idx = 1  # 丑 1-3
    elif total_min < 300:
        zhi_idx = 2  # 寅 3-5
    elif total_min < 420:
        zhi_idx = 3  # 卯 5-7
    elif total_min < 540:
        zhi_idx = 4  # 辰 7-9
    elif total_min < 660:
        zhi_idx = 5  # 巳 9-11
    elif total_min < 780:
        zhi_idx = 6  # 午 11-13
    elif total_min < 900:
        zhi_idx = 7  # 未 13-15
    elif total_min < 1020:
        zhi_idx = 8  # 申 15-17
    elif total_min < 1140:
        zhi_idx = 9  # 酉 17-19
    elif total_min < 1260:
        zhi_idx = 10  # 戌 19-21
    else:
        zhi_idx = 11  # 亥 21-23

    day_gan_idx = TIAN_GAN.index(day_gan)
    base_gan_idx = WU_SHU_DUN[day_gan_idx]
    gan_idx = (base_gan_idx + zhi_idx) % 10
    return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]


def get_four_pillars(lunar_date: LunarDate, hour: int, minute: int = 0,
                     ) -> Dict[str, Tuple[str, str]]:
    """
    四柱主函数 — 输入农历日期+时辰，返回四柱

    参数:
        lunar_date: lunardate.LunarDate 对象（含 year, month, day, is_leap）
        hour:     出生小时 (0-23)
        minute:   出生分钟 (0-59)
    返回:
        {"年柱": (天干, 地支), "月柱": (天干, 地支),
         "日柱": (天干, 地支), "时柱": (天干, 地支)}
    """
    # 1. 年柱 — 直接取农历年份
    year_gan, year_zhi = get_year_gan_zhi(lunar_date)

    # 月柱、日柱需要公历日期（节气判断 + 日干支查表）
    solar_d = lunar_date.toSolarDate()

    # 2. 月柱
    month_gan, month_zhi = get_month_gan_zhi(year_gan, solar_d)

    # 3. 日柱
    day_gan, day_zhi = get_day_gan_zhi(solar_d)

    # 4. 时柱
    hour_gan, hour_zhi = get_hour_gan_zhi(day_gan, hour, minute)

    return {
        "年柱": (year_gan, year_zhi),
        "月柱": (month_gan, month_zhi),
        "日柱": (day_gan, day_zhi),
        "时柱": (hour_gan, hour_zhi),
    }


def get_four_pillars_compact(lunar_date: LunarDate, hour: int, minute: int = 0) -> str:
    """返回紧凑字符串，如 '己巳 丁卯 丁未 辛亥'"""
    p = get_four_pillars(lunar_date, hour, minute)
    return ' '.join(f'{g}{z}' for g, z in p.values())


# ========== 演示 ==========
if __name__ == '__main__':
    # 测试用例：用农历日期直接构造
    test_cases = [
        # (LunarDate, hour, minute)
        (LunarDate(year=1992, month=2, day=28, isLeapMonth=False), 4, 0),
        (LunarDate(year=1930, month=2, day=28, isLeapMonth=False), 4, 0),
        (LunarDate(year=1929, month=5, day=25, isLeapMonth=False), 11, 30),
        (LunarDate(year=1950, month=4, day=27, isLeapMonth=False), 8, 30),
        (LunarDate(year=1993, month=7, day=27, isLeapMonth=False), 0, 0),

        (LunarDate(year=1946, month=9, day=6, isLeapMonth=False), 0, 0),
        (LunarDate(year=1969, month=9, day=22, isLeapMonth=False), 4, 0),
        (LunarDate(year=1967, month=1, day=5, isLeapMonth=False), 11, 30),
        (LunarDate(year=1973, month=3, day=22, isLeapMonth=False), 8, 30),
        (LunarDate(year=1976, month=3, day=8, isLeapMonth=False), 20, 30),

        (LunarDate(year=1998, month=11, day=17, isLeapMonth=False), 16, 00),
        (LunarDate(year=2005, month=2, day=2, isLeapMonth=False), 11, 30),
        (LunarDate(year=2005, month=6, day=3, isLeapMonth=False), 18, 30),
        (LunarDate(year=2010, month=5, day=28, isLeapMonth=False), 7, 30),
        (LunarDate(year=2005, month=2, day=7, isLeapMonth=False), 11, 30),
    ]

    print(f"{'农历日期':<22} → 年柱    月柱    日柱    时柱")
    print("-" * 60)
    for ld, h, m in test_cases:
        result = get_four_pillars_compact(ld, h, m)
        label = f"{ld.year:04d}-{ld.month:02d}-{ld.day:02d}"
        print(f"{label:<22} → {result}")
