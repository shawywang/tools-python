import math
import sys


def my_comb(n, k: int):  # 组合数 C(n, k) = n! / (k! * (n-k)!)
    if k > n:
        sys.exit(-1)
    comb = math.comb(n, k)
    print(f"C({n}, {k}) = {comb}")  # 输出: C(9, 3) = 84


def my_perm(n, k: int):  # 排列数 P(n, k) = n! / (n-k)!
    if k > n:
        sys.exit(-1)
    perm = math.perm(n, k)
    print(f"P({n}, {k}) = {perm}")  # 输出: P(9, 3) = 504


def main():
    my_comb(9, 3)


if __name__ == "__main__":
    main()
# Python 3.8+
