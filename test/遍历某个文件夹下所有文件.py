import os


def read_files_to_one_file(source_dir, target_file):
    """
    遍历文件夹下所有文件，将内容写入目标文件
    :param source_dir: 要读取的源文件夹路径
    :param target_file: 输出的目标文件路径（如 result.txt）
    """
    # 打开目标文件，使用 utf-8 编码避免乱码
    with open(target_file, 'w', encoding='utf-8') as out_f:
        # 遍历所有目录和文件
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                # 获取文件完整路径
                file_path = os.path.join(root, file)

                try:
                    # 写入分隔线 + 文件路径（方便你知道内容来自哪个文件）
                    out_f.write(f"\n{'=' * 50}\n")
                    out_f.write(f"文件路径：{file_path}\n")
                    out_f.write(f"{'=' * 50}\n\n")

                    # 读取文件内容（只读取文本文件，二进制文件跳过）
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        out_f.write(content)
                        out_f.write("\n")

                    print(f"已读取：{file_path}")

                except Exception as e:
                    print(f"读取失败：{file_path}，原因：{str(e)}")

    print(f"\n✅ 所有文件内容已合并完成！保存到：{target_file}")


# ====================== 你只需要改这里 ======================
if __name__ == '__main__':
    # 源文件夹（你要读取的文件夹）
    SOURCE_FOLDER = r"F:\workspace\qc\gmis-manage-int-backend\jeecg-boot-module-project\src\main\java\org\jeecg\modules"

    # 目标文件（所有内容合并到这里）
    TARGET_FILE = "合并结果.txt"
    # =========================================================

    read_files_to_one_file(SOURCE_FOLDER, TARGET_FILE)