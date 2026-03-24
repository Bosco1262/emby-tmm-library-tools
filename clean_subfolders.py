import os
import argparse
import shutil


BASE_EXTENSIONS = {".png", ".jpg"}
NFO_EXTENSION = ".nfo"


def collect_targets(root_dir: str, delete_nfo: bool = False):
    target_extensions = BASE_EXTENSIONS | ({NFO_EXTENSION} if delete_nfo else set())

    files_to_delete = []
    dirs_to_delete = []
    skipped_ignore_trees = []
    scanned_subdirs = 0

    for current_dir, dirnames, filenames in os.walk(root_dir, topdown=True):
        # 根目录本身不处理删除逻辑，但继续遍历它的子目录
        if current_dir == root_dir:
            continue
        scanned_subdirs += 1

        # 如果当前目录包含 .ignore，则跳过该目录整棵子树
        if ".ignore" in filenames:
            skipped_ignore_trees.append(current_dir)
            print(f"[SKIP] {current_dir} (found .ignore, skip subtree)")
            dirnames.clear()  # 阻止 os.walk 继续进入其子目录
            continue

        planned_filenames = []

        # 收集当前目录下要删除的文件
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.lower() in target_extensions:
                files_to_delete.append(os.path.join(current_dir, filename))
                planned_filenames.append(filename)

        # 收集 .actors 文件夹（并避免继续遍历它）
        has_actors_dir = False
        if ".actors" in dirnames:
            actors_dir = os.path.join(current_dir, ".actors")
            if os.path.isdir(actors_dir):
                dirs_to_delete.append(actors_dir)
                has_actors_dir = True
            dirnames.remove(".actors")

        if planned_filenames or has_actors_dir:
            print(f"[PLAN] {current_dir}")
            if planned_filenames:
                print("  Files to delete:")
                for filename in sorted(planned_filenames):
                    print(f"    - {filename}")
            if has_actors_dir:
                print("  Directories to delete:")
                print("    - .actors/")

    return files_to_delete, dirs_to_delete, skipped_ignore_trees, scanned_subdirs


def apply_deletion(files_to_delete, dirs_to_delete):
    deleted_files = 0
    deleted_dirs = 0

    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            deleted_files += 1
            print(f"[DELETED FILE] {file_path}")
        except Exception as e:
            print(f"[ERROR] Failed to delete file: {file_path} ({e})")

    for dir_path in dirs_to_delete:
        try:
            shutil.rmtree(dir_path)
            deleted_dirs += 1
            print(f"[DELETED DIR] {dir_path}")
        except Exception as e:
            print(f"[ERROR] Failed to delete directory: {dir_path} ({e})")

    return deleted_files, deleted_dirs


def main(root_dir: str):
    # 询问是否删除 .nfo 文件（默认：否）
    nfo_answer = input("Delete .nfo files? [y/N]: ").strip().lower()
    delete_nfo = nfo_answer in ("y", "yes")
    if delete_nfo:
        print(".nfo files WILL be deleted.")
    else:
        print(".nfo files will NOT be deleted.")

    print("\n=== Scanning and planning deletion ===")
    files_to_delete, dirs_to_delete, skipped_ignore_trees, scanned_subdirs = collect_targets(
        root_dir, delete_nfo=delete_nfo
    )

    file_types_label = ".nfo/.png/.jpg" if delete_nfo else ".png/.jpg"
    print("\n=== Summary ===")
    print(f"Scanned subdirectories: {scanned_subdirs}")
    print(f"Files planned for deletion ({file_types_label}): {len(files_to_delete)}")
    print(f"Directories planned for deletion: {len(dirs_to_delete)}")
    print(f"Skipped directory trees with .ignore: {len(skipped_ignore_trees)}")

    if not files_to_delete and not dirs_to_delete:
        print("\nNothing to delete.")
        return

    # 第二阶段：确认后执行删除
    confirm = input("\nConfirm deletion? Type yes to continue: ").strip().lower()
    if confirm != "yes":
        print("Canceled. No deletion was performed.")
        return

    print("\nDeleting...")
    deleted_files, deleted_dirs = apply_deletion(files_to_delete, dirs_to_delete)

    print("\nDone.")
    print(f"Deleted files ({file_types_label}): {deleted_files}")
    print(f"Deleted '.actors' directories: {deleted_dirs}")
    print(f"Skipped directory trees with .ignore: {len(skipped_ignore_trees)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="先预览后确认：删除无 .ignore 目录中的 .nfo/.png/.jpg 文件，并删除 .actors；遇到 .ignore 跳过整棵子树"
    )
    parser.add_argument("root_dir", help="要扫描的根目录路径")
    args = parser.parse_args()

    main(args.root_dir)
