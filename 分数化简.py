import math


def simplify_fraction(ratio_str):
    try:
        a, b = map(int, ratio_str.split(':'))
        gcd = math.gcd(a, b)# 计算最大公约数
        # 化简分数
        simplified_a = a // gcd
        simplified_b = b // gcd

        return f"{simplified_a}:{simplified_b}"

    except (ValueError, ZeroDivisionError):
        return "输入格式错误，请使用 '数字:数字' 的格式"





def main():
    test_cases = [
        "1920:1080",
        "1072:1448",
    ]
    for test in test_cases:
        result = simplify_fraction(test)
        print(f"{test} -> {result}")



if __name__ == "__main__":
    main()
