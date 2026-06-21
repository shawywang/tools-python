#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字四柱提取 — 简化版
输入 lunardate.LunarDate + 时辰，直接输出四柱干支
无需公历→农历转换，也无需 lunarcalendar 库
"""

import csv
import os
from datetime import date, datetime
from typing import Tuple, Dict, Optional, List

from lunardate import LunarDate

LOOKUP = os.path.join(os.path.dirname(__file__), '日柱表.csv')

# ========== 基础常量 ==========
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五虎遁：甲己年→寅月天干=丙(2)，乙庚年→寅月天干=戊(4) ...
WU_HU_DUN = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}

# 五鼠遁：甲己日→子时天干=甲(0)，乙庚日→子时天干=丙(2) ...
WU_SHU_DUN = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}

# ========== 12节（月支分界点）==========
# (名称, 典型月, 典型日, 最早日, 最晚日)
# 对应地支索引 = (序号 + 1) % 12
JIE_TABLE = [
    ("小寒", 1, 5, 4, 6),  # → 丑(1)
    ("立春", 2, 4, 3, 5),  # → 寅(2)
    ("惊蛰", 3, 5, 5, 6),  # → 卯(3)
    ("清明", 4, 5, 4, 6),  # → 辰(4)
    ("立夏", 5, 6, 5, 7),  # → 巳(5)
    ("芒种", 6, 6, 5, 7),  # → 午(6)
    ("小暑", 7, 7, 6, 8),  # → 未(7)
    ("立秋", 8, 8, 7, 9),  # → 申(8)
    ("白露", 9, 8, 7, 9),  # → 酉(9)
    ("寒露", 10, 8, 7, 9),  # → 戌(10)
    ("立冬", 11, 8, 7, 9),  # → 亥(11)
    ("大雪", 12, 7, 6, 8),  # → 子(0)
]

JIE_TABLE2: List[str] = [
    "小寒1月4,5,6",
    "立春2月3,4,5",
    "惊蛰3月5,6",
    "清明4月4,5,6",
    "立夏5月5,6,7",
    "芒种6月5,6,7",
]
# ========== 缓存 ==========
_DAY_LOOKUP: Optional[dict] = None
# 用户运行期间输入的节气精确时间，避免重复询问
# {year: {节名称: (month, day, hour, minute)}}
_TERM_CACHE: dict = {}


# ========== 日柱查表 ==========

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

        # 先转公历，年柱/月柱需要公历+节气判断
        self.solar_date = lunar_date.toSolarDate()

        # ---- 四柱计算，结果存为实例属性 ----
        self.year_gan, self.year_zhi = self._calc_year()
        self.month_gan, self.month_zhi = self._calc_month()
        self.day_gan, self.day_zhi = self._calc_day()
        self.hour_gan, self.hour_zhi = self._calc_hour()

    # ---- 年柱（以立春为界）----

    def _calc_year(self) -> Tuple[str, str]:
        """以立春（2月3~5日）为界定年柱，远离立春则自动判断"""
        m, d = self.solar_date.month, self.solar_date.day

        # 1) 远在立春月之前 → 肯定是前一年
        if m < 2:
            actual_year = self.solar_date.year - 1
            print(f"  ℹ️ 出生 {self.solar_date} 在立春月(2月)之前 → 年柱用前一年\n")
        # 2) 远在立春月之后 → 肯定是当年
        elif m > 2:
            actual_year = self.solar_date.year
            print(f"  ℹ️ 出生 {self.solar_date} 在立春月(2月)之后 → 年柱用当年\n")
        else:
            # m == 2：看是否在立春模糊范围(2/3~2/5)内
            if d < 3:
                actual_year = self.solar_date.year - 1
                print(f"  ℹ️ 出生 {self.solar_date} 在立春(2/3~5)之前 → 年柱用前一年\n")
            elif d > 5:
                actual_year = self.solar_date.year
                print(f"  ℹ️ 出生 {self.solar_date} 在立春(2/3~5)之后 → 年柱用当年\n")
            else:
                # 3) 落在模糊范围 → 交互式输入
                actual_year = self._ask_lichun()

        gan_idx = (actual_year - 4) % 10
        zhi_idx = (actual_year - 4) % 12
        return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]

    def _ask_lichun(self) -> int:
        """交互式输入立春精确时间，判断出生在其前/后，返回实际年份"""
        year = self.solar_date.year
        cached = _TERM_CACHE.get(year, {}).get("立春")
        if cached is not None:
            m, d, h, mi = cached
        else:
            print(f"\n⚠️ 出生日期 {self.solar_date} 接近立春，需确认是否已过。")
            inp = input(f"  请输入{year}年立春的月 日 时 分（空格分隔，如 2 4 4 1）: ").strip()
            parts = list(map(int, inp.split()))
            if len(parts) < 4:
                print("  ❌ 格式错误，用典型日期 2月4日 0时判断。")
                m, d, h, mi = 2, 4, 0, 0
            else:
                m, d, h, mi = parts
            _TERM_CACHE.setdefault(year, {})["立春"] = (m, d, h, mi)

        lichun_dt = datetime(year, m, d, h, mi)
        birth_dt = datetime(year, self.solar_date.month, self.solar_date.day,
                            self.hour, self.minute)

        if birth_dt < lichun_dt:
            print(f"  ℹ️ 出生 {self.solar_date} {self.hour:02d}:{self.minute:02d}"
                  f" 在立春 {lichun_dt} 之前 → 年柱用前一年\n")
            return year - 1
        else:
            print(f"  ℹ️ 出生 {self.solar_date} {self.hour:02d}:{self.minute:02d}"
                  f" 在立春 {lichun_dt} 之后 → 年柱用当年\n")
            return year

    # ---- 月柱（以12节为界）----

    def _calc_month(self) -> Tuple[str, str]:
        month_zhi = self._get_month_zhi()
        year_gan_idx = TIAN_GAN.index(self.year_gan)
        base_gan_idx = WU_HU_DUN[year_gan_idx]
        offset = (DI_ZHI.index(month_zhi) - 2) % 12
        month_gan = TIAN_GAN[(base_gan_idx + offset) % 10]
        return month_gan, month_zhi

    def _get_month_zhi(self) -> str:
        """按公历月+日判断月支（按12节，遇模糊日期交互式查询）"""
        m, d = self.solar_date.month, self.solar_date.day

        # 1) 检查是否落在某节的模糊范围内
        for i, (name, tm, _, min_d, max_d) in enumerate(JIE_TABLE):
            if m == tm and min_d <= d <= max_d:
                return self._ask_jie(i)

        # 2) 不在模糊范围，用典型日期直接判断
        for i in range(12):
            cur_m, cur_d = JIE_TABLE[i][1], JIE_TABLE[i][2]
            next_m, next_d = JIE_TABLE[(i + 1) % 12][1], JIE_TABLE[(i + 1) % 12][2]
            if (m == cur_m and d >= cur_d) or (m == next_m and d < next_d):
                return DI_ZHI[(i + 1) % 12]
        return DI_ZHI[1]

    def _ask_jie(self, jie_idx: int) -> str:
        """交互式输入某节的精确时间，判断出生在其前/后"""
        name, tm, td, _, _ = JIE_TABLE[jie_idx]
        year = self.solar_date.year

        # 立春可能已被年柱问过，直接复用缓存
        cached = _TERM_CACHE.get(year, {}).get(name)
        if cached is not None:
            m, d, h, mi = cached
        else:
            print(f"\n⚠️ 出生日期 {self.solar_date} 接近{name}，需确认是否已过该节气。")
            inp = input(f"  请输入{year}年{name}的月 日 时 分（空格分隔，如 {tm} {td} 0 0）: ").strip()
            parts = list(map(int, inp.split()))
            if len(parts) < 4:
                print(f"  ❌ 格式错误，用典型日期 {tm}月{td}日 0时判断。")
                m, d, h, mi = tm, td, 0, 0
            else:
                m, d, h, mi = parts
            _TERM_CACHE.setdefault(year, {})[name] = (m, d, h, mi)

        jie_dt = datetime(year, m, d, h, mi)
        birth_dt = datetime(year, self.solar_date.month, self.solar_date.day,
                            self.hour, self.minute)

        if birth_dt < jie_dt:
            result = DI_ZHI[jie_idx % 12]
            print(f"  ℹ️ 出生 {self.solar_date} {self.hour:02d}:{self.minute:02d}"
                  f" 在{name} {jie_dt} 之前 → 月支 {result}\n")
        else:
            result = DI_ZHI[(jie_idx + 1) % 12]
            print(f"  ℹ️ 出生 {self.solar_date} {self.hour:02d}:{self.minute:02d}"
                  f" 在{name} {jie_dt} 之后 → 月支 {result}\n")
        return result

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
        if total_min < 60 or total_min >= 1380:  # 1380为23小时整
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
        (LunarDate(year=1998, month=11, day=17, isLeapMonth=False), 16, 00),

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

# 24节气常见日期范围（参考）：
#   小寒 1/4-6   大寒 1/19-21
#   立春 2/3-5   雨水 2/18-20
#   惊蛰 3/5-6   春分 3/20-22
#   清明 4/4-6   谷雨 4/19-21
#   立夏 5/5-7   小满 5/20-22
#   芒种 6/5-7   夏至 6/21-22
#   小暑 7/6-8   大暑 7/22-24
#   立秋 8/7-9   处暑 8/22-24
#   白露 9/7-9   秋分 9/22-24
#   寒露 10/7-9  霜降 10/22-24
#   立冬 11/7-9  小雪 11/22-23
#   大雪 12/6-8  冬至 12/21-23
# （带下划线的为12"节"，用于定月支）
