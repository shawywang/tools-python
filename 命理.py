from typing import List

# 天干
Celestial: List[str] = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
Terrestrial: List[str] = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def time_cel(day_cel: str, time_ter: str) -> str:
    ind_cel: int = Terrestrial.index(time_ter)
    if day_cel in {"甲", "己"}:
        pass
    elif day_cel in {"乙", "庚"}:
        ind_cel += 2
    elif day_cel in {"丙", "辛"}:
        ind_cel += 4
    elif day_cel in {"丁", "壬"}:
        ind_cel += 6
    elif day_cel in {"戊", "癸"}:
        ind_cel += 8
    else:
        pass
    if ind_cel < len(Celestial):
        time_cel = Celestial[ind_cel]
    else:
        time_cel = Celestial[ind_cel - len(Celestial)]

    print(f"time_cel = {time_cel}")
    return time_cel


def char_with_me(me_cel: str, char: str):
    pass


def main():
    print("")
    time_cel("丙", "申")
    char_with_me("乙", "亥")


if __name__ == '__main__':
    main()
