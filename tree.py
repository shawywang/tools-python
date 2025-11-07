from collections import deque
from typing import Dict, List


class TNode:
    def __init__(self, value):
        self.value: str = value
        self.child = []

    def add_child(self, child):
        if not isinstance(child, TNode):
            child_node = TNode(child)
        else:
            child_node = child
        self.child.append(child_node)
        return child_node

    def remove_child(self, child_node):
        self.child = [child for child in self.child if child != child_node]

    def remove_child_all(self):
        self.child = []

    def trav_show(self, level=0):
        print("  " * level + f"┕┅{self.value}")
        for child in self.child:
            child.trav_show(level + 1)


def trav_dfs_with_level(root, target_level):
    result: List[Dict[int, int]] = []

    def dfs(node, current_level):
        if current_level == target_level:
            print(f"层：{current_level}，值：{node.value}")
            result.append({current_level: node.value})
        if current_level >= target_level:
            return
        for child in node.child:
            dfs(child, current_level + 1)

    dfs(root, 0)
    return result


def find_node_by_value(root, target_level, targetg_value):
    if not root:
        return None
    queue = deque([(root, 0)])
    while queue:
        node, current_level = queue.popleft()
        if current_level == target_level:
            if node.value == targetg_value:
                return node
            continue
        for child in node.child:
            queue.append((child, current_level + 1))
        if current_level >= target_level:
            break
    return None


def find_parent(root, target_node):
    if root is None:
        return None
    queue = deque([(root, None)])
    while queue:
        node, parent = queue.popleft()
        if node == target_node:
            return parent
        for child in node.child:
            queue.append((child, node))
    return None


def main():
    root = TNode("根")

    guangzhou = root.add_child(TNode("广州"))
    chongqing = root.add_child(TNode("重庆"))

    guangqi = guangzhou.add_child(TNode("广汽"))
    xiaopeng = guangzhou.add_child(TNode("小鹏"))
    changan = chongqing.add_child(TNode("长安"))
    seres = chongqing.add_child(TNode("塞力斯"))

    guangqi.add_child(TNode("本田"))
    guangqi.add_child(TNode("埃安"))
    xiaopeng.add_child(TNode("Mona"))
    xiaopeng.add_child(TNode("P7"))

    changan.add_child(TNode("深蓝"))
    changan.add_child(TNode("启源"))
    seres.add_child(TNode("问界"))

    print("0-1-2-3-4")
    root.trav_show()


if __name__ == '__main__':
    main()
"""
0-1-2-3-4
┕┅根
  ┕┅广州
    ┕┅广汽
      ┕┅本田
      ┕┅埃安
    ┕┅小鹏
      ┕┅Mona
      ┕┅P7
  ┕┅重庆
    ┕┅长安
      ┕┅深蓝
      ┕┅启源
    ┕┅塞力斯
      ┕┅问界
"""
