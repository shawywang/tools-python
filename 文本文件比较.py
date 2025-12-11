def are_files_equal(file1, file2):
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        if f1.read() == f2.read():
            print(f"两个文件内容完全相同：\n{file1}\n{file2}")
        else:
            print(f"两个文件内容不同：\n{file1}\n{file2}")


if __name__ == "__main__":
    file_a = ""
    file_b = ""
    are_files_equal(file_a, file_b)
