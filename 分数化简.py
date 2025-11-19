import math


def simplify_fraction(ratio_str):
    try:
        a, b = map(int, ratio_str.split(':'))
        gcd = math.gcd(a, b)  # 计算最大公约数
        # 化简分数
        simplified_a = a // gcd
        simplified_b = b // gcd

        return f"{simplified_a}:{simplified_b}"

    except (ValueError, ZeroDivisionError):
        return "输入格式错误，请使用 '数字:数字' 的格式"


def parse_ratio(input_str, max_value=20):
    """解析输入并找到最接近的比例"""
    try:
        width, height = map(int, input_str.split(':'))
        return find_closest_ratio_optimized(width, height, max_value)
    except:
        return "无效输入"


def find_closest_ratio_optimized(width, height, max_value=20):
    """
    优化版本：使用连分数展开来找到最接近的比例
    """
    original_ratio = width / height

    best_error = float('inf')
    best_num, best_den = 1, 1

    # 遍历分母，计算最接近的分子
    for den in range(1, max_value + 1):
        num = round(original_ratio * den)

        # 确保分子在合理范围内
        if 1 <= num <= max_value:
            error = abs(num / den - original_ratio)

            if error < best_error:
                best_error = error
                best_num, best_den = num, den

    # 简化比例
    gcd = math.gcd(best_num, best_den)
    simplified_num = best_num // gcd
    simplified_den = best_den // gcd

    # 如果简化后的比例超过范围，使用原始最佳匹配
    if simplified_num > max_value or simplified_den > max_value:
        return f"{best_num}:{best_den}"

    return f"{simplified_num}:{simplified_den}"


def main():
    test_cases = [
        "1920:1080",  # 标准1080P
        "1448:1072",  # kindle paperwhite4
        "1280:800",  # 笔记本常用的分辨率
        "1280:1024",
        "1280:960",
    ]

    for test in test_cases:
        result = simplify_fraction(test)
        if len(result) > 5:
            print(f"{test} -> {result}", end='')
            print(f"，接近：{parse_ratio(test)}")
        else:
            print(f"{test} -> {result}")


if __name__ == "__main__":
    main()
