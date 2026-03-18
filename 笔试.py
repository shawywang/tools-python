from typing import List, Dict


def search_arr(nums: List[int], target: int):
    if not nums:
        return -1
    l, r = 0, len(nums) - 1
    while l <= r:
        mid = (l + r) // 2
        if nums[mid] == target:
            return mid
        if nums[l] <= nums[mid]:
            if nums[l] <= target < nums[mid]:
                r = mid - 1
            else:
                l = mid + 1
        else:
            if nums[mid] < target <= nums[r]:
                l = mid + 1
            else:
                r = mid - 1
    return -1


def merge(nums: List[List[int]]) -> List[List[int]]:
    if not nums:
        return []
    nums.sort(key=lambda x: x[0])
    merged = [nums[0]]
    for n in nums[1:]:
        curr_s, curr_e = n
        last_e = merged[-1][1]
        if curr_s <= last_e:
            merged[-1][1] = max(last_e, curr_e)
        else:
            merged.append(n)
    return merged


def find_one(arr: List[int]) -> int:
    mark: Dict[int, int] = {}
    for a in arr:
        if a not in mark:
            mark[a] = 1
        else:
            mark[a] += 1
    for m, v in mark.items():
        if v == 1:
            return m
    return 0


def main():
    # 1.只出现一次的数字；
    # 某个元素只出现一次以外，其余每个元素均出现两次，找出1次的
    # 输入：nums = [2,2,1]
    # 输出：1
    print(find_one([2, 2, 1]))
    # 2.搜索旋转排序数组
    # 输入:nums = [4,5,6,7,0,1,2], target = 0
    # 输出target的数组下标:4
    print(search_arr([4, 5, 6, 7, 0, 1, 2], 0))
    # 3.合并区间
    # 输入：[[1,3],[2,6],[8,10],[15,18]]
    # 输出：[[1,6],[8,10],[15,18]]
    # 解释：区间[1,3]和[2,6]重叠,将它们合并为[1,6].
    print(merge([[1, 3], [2, 6], [8, 10], [15, 18]]))


if __name__ == '__main__':
    main()
