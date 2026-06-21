#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字四柱提取
输入公历 + 时辰，输出四柱干支
"""

import csv
import os
from datetime import date, datetime, timedelta
from typing import Tuple, Dict, Optional

LOOKUP = os.path.join(os.path.dirname(__file__), '日柱表.csv')

# ========== 基础常量 ==========
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五虎遁口诀：用来求每年第一个月的天干
# 甲己之年丙作首：每逢年干是甲或己的年份，正月的月干从丙上数起。
# 乙庚之年戊为头：每逢年干是乙或庚的年份，正月的月干从戊上数起。
# 丙辛之岁寻庚上：每逢年干是丙或辛的年份，正月的月干从庚上数起。
# 丁壬壬寅顺水流：每逢年干是丁或壬的年份，正月的月干从壬上数起。
# 若问戊癸何方发，甲寅之上好追求：每逢年干是戊或癸的年份，正月的月干从甲上数起。
WU_HU_DUN = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}

# 五鼠遁：求每日子时的天干
# 甲己还加甲：凡是甲己日，时辰从甲子时开始往下推。
# 乙庚丙作初：凡是乙庚日，时辰从丙子时开始往下推。
# 丙辛从戊起：凡是丙辛日，时辰从戊子时开始往下推。
# 丁壬庚子居：凡是丁壬日，时辰从庚子时开始往下推。
# 戊癸何方发，壬子是真途：凡是戊癸日，时辰从壬子时开始往下推。
WU_SHU_DUN = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}

# ========== 12节（月支分界点）==========
# 月份与可能日期集合，顺序：小寒→立春→惊蛰→...→大雪
JIE = [  # 节气 → 哪个月支的开始
    {1.4, 1.5, 1.6},  # 小寒 → 丑
    {2.3, 2.4, 2.5},  # 立春 → 寅
    {3.5, 3.6},  # 惊蛰 → 卯
    {4.4, 4.5, 4.6},  # 清明 → 辰
    {5.5, 5.6, 5.7},  # 立夏 → 巳
    {6.5, 6.6, 6.7},  # 芒种 → 午
    {7.6, 7.7, 7.8},  # 小暑 → 未
    {8.7, 8.8, 8.9},  # 立秋 → 申
    {9.7, 9.8, 9.9},  # 白露 → 酉
    {10.7, 10.8, 10.9},  # 寒露 → 戌
    {11.7, 11.8, 11.9},  # 立冬 → 亥
    {12.6, 12.7, 12.8},  # 大雪 → 子
]

# 预计算 JIE 集合中的最早日期（月.日 浮点数）
JIE_MIN = [min(s) for s in JIE]  # [1.4, 2.3, 3.5, ...]
JIE_MING = ["小寒", "立春", "惊蛰", "清明", "立夏", "芒种", "小暑", "立秋", "白露", "寒露", "立冬", "大雪"]
JIE_ZHI = ["丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子"]

# 时辰→具体时间映射（取各时辰中点）
SHICHEN_MAP = {
    "子": (0, 0), "丑": (2, 0), "寅": (4, 0), "卯": (6, 0),
    "辰": (8, 0), "巳": (10, 0), "午": (12, 0), "未": (14, 0),
    "申": (16, 0), "酉": (18, 0), "戌": (20, 0), "亥": (22, 0),
}

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
        bz = BaZi(2026, 3, 4, 8, 0)  # 公历2026-03-04 辰时
        print(bz.compact)       # 紧凑字符串
        print(bz.four_pillars)  # 字典
        print(bz.year_gan)      # 年干
        print(bz.month_zhi)     # 月支
    """

    def __init__(self, year: int, month: int, day: int, hour: int = 0,
                 minute: int = 0, shichen: Optional[str] = None):
        # 时辰名称 → 具体时间
        if shichen:
            if shichen not in SHICHEN_MAP:
                raise ValueError(f"未知时辰: {shichen}，应为 {list(SHICHEN_MAP)} 之一")
            hour, minute = SHICHEN_MAP[shichen]

        self.solar_date = date(year, month, day)
        self.hour = hour
        self.minute = minute

        # ---- 四柱计算，结果存为实例属性 ----
        self.year_gan, self.year_zhi = self._calc_year()
        self.month_gan, self.month_zhi = self._calc_month()
        self.day_gan, self.day_zhi = self._calc_day()
        self.hour_gan, self.hour_zhi = self._calc_hour()

        # 子时边界(23:00~23:59)特殊处理
        total_min = hour * 60 + minute
        if 1380 <= total_min < 1440:
            self._compute_zishi_variants()

    # ---- 年柱（以立春为界）----

    def _calc_year(self) -> Tuple[str, str]:
        """以立春（2月3~5日）为界定年柱，远离立春则自动判断"""
        m, d = self.solar_date.month, self.solar_date.day

        if m < 2 or (m == 2 and d < 3):
            actual_year = self.solar_date.year - 1
        elif m > 2 or (m == 2 and d > 5):
            actual_year = self.solar_date.year
        else:
            actual_year = self._ask_term("立春", 2, 4, "年柱用前一年", "年柱用当年", ret_year=True)

        gan_idx = (actual_year - 4) % 10
        zhi_idx = (actual_year - 4) % 12
        return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]

    def _ask_term(self, term_name: str, default_m: int, default_d: int,
                  msg_before: str, msg_after: str, ret_year: bool = False):
        """通用：询问某节气精确时间，判断出生在其前/后

        ret_year=True  → 返回实际年份（用于立春）
        ret_year=False → 返回地支字符串（用于月支）
        """
        year = self.solar_date.year
        cached = _TERM_CACHE.get(year, {}).get(term_name)
        if cached is not None:
            m, d, h, mi = cached
        else:
            print("https://dijizhou.100xgj.com/jieqibiao/1999")
            print(f"\n⚠️ 出生日期 {self.solar_date} 接近{term_name}，需确认是否已过。")
            inp = input(f"  请输入{year}年{term_name}的月 日 时 分（空格分隔，如 {default_m} {default_d} 0 0）: ").strip()
            parts = list(map(int, inp.split()))
            if len(parts) < 4:
                print(f"  ❌ 格式错误，用典型日期 {default_m}月{default_d}日 0时判断。")
                m, d, h, mi = default_m, default_d, 0, 0
            else:
                m, d, h, mi = parts
            _TERM_CACHE.setdefault(year, {})[term_name] = (m, d, h, mi)

        term_dt = datetime(year, m, d, h, mi)
        birth_dt = datetime(year, self.solar_date.month, self.solar_date.day,
                            self.hour, self.minute)

        if birth_dt < term_dt:
            print(f"  ℹ️ 出生 {self.solar_date} {self.hour:02d}:{self.minute:02d}"
                  f" 在{term_name} {term_dt} 之前 → {msg_before}\n")
            return (year - 1) if ret_year else JIE_ZHI[(
                                                               JIE_MING.index(term_name) - 1) % 12]
        else:
            print(f"  ℹ️ 出生 {self.solar_date} {self.hour:02d}:{self.minute:02d}"
                  f" 在{term_name} {term_dt} 之后 → {msg_after}\n")
            return year if ret_year else JIE_ZHI[JIE_MING.index(term_name)]

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
        key = float(f"{m}.{d}")

        # 1) 是否在某个节的模糊日期内
        for i, days in enumerate(JIE):
            if key in days:
                return self._ask_jie(i)

        # 2) 不在模糊范围 → 用最早日期判断
        for i in range(12):
            cur, nxt = JIE_MIN[i], JIE_MIN[(i + 1) % 12]
            cur_m, cur_d = int(cur), round((cur - int(cur)) * 10)
            nxt_m, nxt_d = int(nxt), round((nxt - int(nxt)) * 10)
            if (m == cur_m and d >= cur_d) or (m == nxt_m and d < nxt_d):
                return JIE_ZHI[i]
        return JIE_ZHI[0]

    def _ask_jie(self, jie_idx: int) -> str:
        name = JIE_MING[jie_idx]
        v = JIE_MIN[jie_idx]
        tm, td = int(v), round((v - int(v)) * 10)
        return self._ask_term(name, tm, td, f"月支 {JIE_ZHI[(jie_idx - 1) % 12]}", f"月支 {JIE_ZHI[jie_idx]}")

    # ---- 日柱 ----

    def _calc_day(self) -> Tuple[str, str]:
        return self._lookup_day_ganzhi(self.solar_date)

    def _lookup_day_ganzhi(self, dt: date) -> Tuple[str, str]:
        """查任意公历日期的日柱干支"""
        global _DAY_LOOKUP
        if _DAY_LOOKUP is None:
            _DAY_LOOKUP = _load_day_lookup()
        if _DAY_LOOKUP is not None:
            key = dt.strftime('%Y-%m-%d')
            if key in _DAY_LOOKUP:
                return _DAY_LOOKUP[key]

        base = date(2000, 1, 1)
        days = (dt - base).days
        gan_idx = (4 + days) % 10
        zhi_idx = (6 + days) % 12
        return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]

    # ---- 时柱 ----

    def _calc_hour(self) -> Tuple[str, str]:
        total_min = self.hour * 60 + self.minute
        zhi_idx = self._get_hour_zhi(total_min)
        return self._calc_hour_for_zhi(self.day_gan, zhi_idx)

    @staticmethod
    def _calc_hour_for_zhi(day_gan: str, zhi_idx: int) -> Tuple[str, str]:
        """给定日干和时辰地支索引，按时柱干支（五鼠遁）"""
        day_gan_idx = TIAN_GAN.index(day_gan)
        base_gan_idx = WU_SHU_DUN[day_gan_idx]
        gan_idx = (base_gan_idx + zhi_idx) % 10
        return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]

    @staticmethod
    def _get_hour_zhi(total_min: int) -> int:
        if total_min < 60 or total_min >= 1380:  # 1380为23小时整
            return 0  # 子 23-1
        if total_min < 180:
            return 1  # 丑 1-3
        if total_min < 300:
            return 2  # 寅 3-5
        if total_min < 420:
            return 3  # 卯 5-7
        if total_min < 540:
            return 4  # 辰 7-9
        if total_min < 660:
            return 5  # 巳 9-11
        if total_min < 780:
            return 6  # 午 11-13
        if total_min < 900:
            return 7  # 未 13-15
        if total_min < 1020:
            return 8  # 申 15-17
        if total_min < 1140:
            return 9  # 酉 17-19
        if total_min < 1260:
            return 10  # 戌 19-21
        return 11  # 亥 21-23

    def _compute_zishi_variants(self):
        """23:00~23:59 子时边界特殊处理，输出3种八字"""
        total_min = self.hour * 60 + self.minute
        if not (1380 <= total_min < 1440):
            return

        yg, yz = self.year_gan, self.year_zhi
        mg, mz = self.month_gan, self.month_zhi
        dg, dz = self.day_gan, self.day_zhi

        # Variant 1：次日日时
        next_date = self.solar_date + timedelta(days=1)
        v1_dg, v1_dz = self._lookup_day_ganzhi(next_date)
        v1_hg, v1_hz = self._calc_hour_for_zhi(v1_dg, 0)  # 子时

        # Variant 2：（通常建议）当日日时不变，即当前结果
        v2_hg, v2_hz = self.hour_gan, self.hour_zhi

        # Variant 3：取亥时(21~23)天干+1作为子时天干
        hai_zhi = 11
        day_gan_idx = TIAN_GAN.index(dg)
        hai_gan_idx = (WU_SHU_DUN[day_gan_idx] + hai_zhi) % 10
        v3_hg = TIAN_GAN[(hai_gan_idx + 1) % 10]
        v3_hz = DI_ZHI[0]  # 子时

        ts = f"{self.hour:02d}:{self.minute:02d}"
        print(f"\n⚠️ 出生时间 {ts} 处于子时(23~1点)的23~24交界，特殊处理3个八字：")
        print(f"  第一种，23~24算次日，日时都变：\n\t{yg}{yz} {mg}{mz} {v1_dg}{v1_dz} {v1_hg}{v1_hz}")
        print(f"  第二种（通常建议），23~24同当日0~1，日时都不变：\n\t{yg}{yz} {mg}{mz} {dg}{dz} {v2_hg}{v2_hz}")
        print(f"  第三种，9~11的时干，再往后数一个天干作为时干，只变时柱：\n\t{yg}{yz} {mg}{mz} {dg}{dz} {v3_hg}{v3_hz}\n")

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


# ========== 演示 ==========
if __name__ == '__main__':
    bz = BaZi(year=1993, month=9, day=12, hour=23, minute=45)
    print(f" → {bz.compact}")
    print("-" * 60)
    bz = BaZi(year=1950, month=6, day=12, shichen="辰")
    print(f" → {bz.compact}")

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
