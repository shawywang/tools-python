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

LOOKUP = os.path.join(os.path.dirname(__file__), '日柱表.csv')

# ========== 基础常量 ==========
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五虎遁：甲己年→寅月天干=丙(2)，乙庚年→寅月天干=戊(4) ...
WU_HU_DUN = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}

# 五鼠遁：甲己日→子时天干=甲(0)，乙庚日→子时天干=丙(2) ...
WU_SHU_DUN = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}

# ========== 24节气 & 日柱缓存（模块级，所有实例共享）==========
JIEQI_FILE = os.path.join(os.path.dirname(__file__), '二十四节气.csv')
_JIE_LOOKUP: Optional[dict] = None
_DAY_LOOKUP: Optional[dict] = None


def _load_jie_lookup() -> dict:
    """加载节气日值表，返回 {年份: [(月, 日)*12]}"""
    lookup = {}
    with open(JIEQI_FILE, 'r', encoding='utf-8') as f:
        for row in csv.reader(f):
            if len(row) != 25:
                continue
            vals = [int(x) for x in row]
            year = vals[-1]
            # 取偶数索引（0,2,4,...,22）作为12个"节"的日值
            days = [vals[i] for i in range(0, 24, 2)]
            lookup[year] = [(m + 1, days[m]) for m in range(12)]
    return lookup


def _get_jie_dates(year: int) -> list:
    """根据年份查找对应的12节日期 [(月, 日), ...]"""
    global _JIE_LOOKUP
    if _JIE_LOOKUP is None:
        _JIE_LOOKUP = _load_jie_lookup()
    if year in _JIE_LOOKUP:
        return _JIE_LOOKUP[year]
    nearest = min(_JIE_LOOKUP.keys(), key=lambda y: abs(y - year))
    return _JIE_LOOKUP[nearest]


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


# ========== 八字计算器类 ==========

class BaZi:
    """八字四柱计算器

    用法:
        bz = BaZi(LunarDate(1992, 2, 28), 4, 0)
        print(bz.compact)       # 紧凑字符串
        print(bz.four_pillars)  # 字典
        print(bz.year_gan)      # 年干
        print(bz.month_zhi)     # 月支
    """

    def __init__(self, lunar_date: LunarDate, hour: int, minute: int = 0):
        self.lunar_date = lunar_date
        self.hour = hour
        self.minute = minute

        # ---- 四柱计算，结果存为实例属性 ----
        self.year_gan, self.year_zhi = self._calc_year()

        # 月柱、日柱需要公历日期
        self.solar_date = lunar_date.toSolarDate()

        self.month_gan, self.month_zhi = self._calc_month()
        self.day_gan, self.day_zhi = self._calc_day()
        self.hour_gan, self.hour_zhi = self._calc_hour()

    # ---- 年柱 ----

    def _calc_year(self) -> Tuple[str, str]:
        gan_idx = (self.lunar_date.year - 4) % 10
        zhi_idx = (self.lunar_date.year - 4) % 12
        return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]

    # ---- 月柱 ----

    def _calc_month(self) -> Tuple[str, str]:
        month_zhi = self._get_month_zhi()
        year_gan_idx = TIAN_GAN.index(self.year_gan)
        base_gan_idx = WU_HU_DUN[year_gan_idx]
        offset = (DI_ZHI.index(month_zhi) - 2) % 12
        month_gan = TIAN_GAN[(base_gan_idx + offset) % 10]
        return month_gan, month_zhi

    def _get_month_zhi(self) -> str:
        """按月+日判断月支（按节气）"""
        dates = _get_jie_dates(self.solar_date.year)
        m, d = self.solar_date.month, self.solar_date.day
        for i in range(12):
            cur_m, cur_d = dates[i]
            next_m, next_d = dates[(i + 1) % 12]
            if (m == cur_m and d >= cur_d) or (m == next_m and d < next_d):
                return DI_ZHI[i]
        return DI_ZHI[0]

    # ---- 日柱 ----

    def _calc_day(self) -> Tuple[str, str]:
        global _DAY_LOOKUP
        if _DAY_LOOKUP is None:
            _DAY_LOOKUP = _load_day_lookup()
        if _DAY_LOOKUP is not None:
            key = self.solar_date.strftime('%Y-%m-%d')
            if key in _DAY_LOOKUP:
                return _DAY_LOOKUP[key]

        base = date(2000, 1, 1)
        days = (self.solar_date - base).days
        gan_idx = (4 + days) % 10
        zhi_idx = (6 + days) % 12
        return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]

    # ---- 时柱 ----

    def _calc_hour(self) -> Tuple[str, str]:
        total_min = self.hour * 60 + self.minute
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

        day_gan_idx = TIAN_GAN.index(self.day_gan)
        base_gan_idx = WU_SHU_DUN[day_gan_idx]
        gan_idx = (base_gan_idx + zhi_idx) % 10
        return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]

    # ---- 输出 ----

    @property
    def four_pillars(self) -> Dict[str, Tuple[str, str]]:
        return {
            "年柱": (self.year_gan, self.year_zhi),
            "月柱": (self.month_gan, self.month_zhi),
            "日柱": (self.day_gan, self.day_zhi),
            "时柱": (self.hour_gan, self.hour_zhi),
        }

    @property
    def compact(self) -> str:
        return ' '.join(f'{g}{z}' for g, z in self.four_pillars.values())


# ========== 兼容旧接口（薄封装）==========

def get_four_pillars(lunar_date: LunarDate, hour: int, minute: int = 0,
                     ) -> Dict[str, Tuple[str, str]]:
    """四柱（兼容旧调用方式）"""
    return BaZi(lunar_date, hour, minute).four_pillars


def get_four_pillars_compact(lunar_date: LunarDate, hour: int, minute: int = 0) -> str:
    """紧凑字符串（兼容旧调用方式）"""
    return BaZi(lunar_date, hour, minute).compact


# ========== 演示 ==========
if __name__ == '__main__':
    test_cases = [
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
        bz = BaZi(ld, h, m)
        label = f"{ld.year:04d}-{ld.month:02d}-{ld.day:02d}"
        print(f"{label:<22} → {bz.compact}")
