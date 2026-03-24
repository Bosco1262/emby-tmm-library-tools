import os
import argparse


def add_tmmignore(root_dir: str):
    created_count = 0
    skipped_count = 0

    for current_dir, dirnames, filenames in os.walk(root_dir):
        # 只处理子文件夹（不处理根目录本身）
        if current_dir == root_dir:
            continue

        has_ignore = ".ignore" in filenames
        has_tmmignore = ".tmmignore" in filenames

        if has_ignore:
            tmmignore_path = os.path.join(current_dir, ".tmmignore")
            if not has_tmmignore:
                # 创建空的 .tmmignore 文件
                with open(tmmignore_path, "w", encoding="utf-8"):
                    pass
                created_count += 1
                print(f"[CREATED] {tmmignore_path}")
            else:
                skipped_count += 1
                print(f"[SKIPPED] Already exists: {tmmignore_path}")

    print("\nDone.")
    print(f"Created: {created_count}")
    print(f"Skipped (already existed): {skipped_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="为含有 .ignore 的子文件夹创建 .tmmignore 文件"
    )
    parser.add_argument(
        "root_dir",
        help="要扫描的根目录路径"
    )

    args = parser.parse_args()
    add_tmmignore(args.root_dir)