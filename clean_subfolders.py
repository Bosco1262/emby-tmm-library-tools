import os
import argparse
import shutil


BASE_EXTENSIONS = {".png", ".jpg"}
NFO_EXTENSION = ".nfo"
MESSAGES = {
    "zh": {
        "choose_lang": "请选择输出语言 / Please choose output language [zh/en] (默认 zh): ",
        "ask_delete_nfo": "是否删除 .nfo 文件？[y/N]: ",
        "nfo_yes": ".nfo 文件将会被删除。",
        "nfo_no": ".nfo 文件不会被删除。",
        "scanning_header": "\n=== 正在扫描并规划删除 ===",
        "skip_ignore_tree": "[跳过] {path}（发现 .ignore，跳过整棵子树）",
        "plan_dir": "[计划] {path}",
        "plan_files": "  待删除文件:",
        "plan_dirs": "  待删除目录:",
        "plan_item": "    - {item}",
        "plan_noop": "[无需操作] {path}",
        "summary_header": "\n=== 汇总 ===",
        "scanned_subdirs": "扫描子目录数: {count}",
        "files_planned": "计划删除文件数（{types}）: {count}",
        "dirs_planned": "计划删除目录数: {count}",
        "ignored_trees": "因 .ignore 跳过的目录树: {count}",
        "nothing_to_delete": "\n无需删除任何内容。",
        "confirm_delete": "\n确认删除吗？输入 yes 继续: ",
        "canceled": "已取消，未执行删除。",
        "deleting": "\n正在删除...",
        "deleted_file": "[已删除文件] {path}",
        "deleted_dir": "[已删除目录] {path}",
        "error_file": "[错误] 删除文件失败: {path} ({error})",
        "error_dir": "[错误] 删除目录失败: {path} ({error})",
        "done": "\n完成。",
        "deleted_files_summary": "已删除文件（{types}）: {count}",
        "deleted_dirs_summary": "已删除特殊目录（.actors/.deletedByTMM）: {count}",
    },
    "en": {
        "choose_lang": "请选择输出语言 / Please choose output language [zh/en] (default zh): ",
        "ask_delete_nfo": "Delete .nfo files? [y/N]: ",
        "nfo_yes": ".nfo files WILL be deleted.",
        "nfo_no": ".nfo files will NOT be deleted.",
        "scanning_header": "\n=== Scanning and planning deletion ===",
        "skip_ignore_tree": "[SKIP] {path} (found .ignore, skip subtree)",
        "plan_dir": "[PLAN] {path}",
        "plan_files": "  Files to delete:",
        "plan_dirs": "  Directories to delete:",
        "plan_item": "    - {item}",
        "plan_noop": "[NOOP] {path}",
        "summary_header": "\n=== Summary ===",
        "scanned_subdirs": "Scanned subdirectories: {count}",
        "files_planned": "Files planned for deletion ({types}): {count}",
        "dirs_planned": "Directories planned for deletion: {count}",
        "ignored_trees": "Skipped directory trees with .ignore: {count}",
        "nothing_to_delete": "\nNothing to delete.",
        "confirm_delete": "\nConfirm deletion? Type yes to continue: ",
        "canceled": "Canceled. No deletion was performed.",
        "deleting": "\nDeleting...",
        "deleted_file": "[DELETED FILE] {path}",
        "deleted_dir": "[DELETED DIR] {path}",
        "error_file": "[ERROR] Failed to delete file: {path} ({error})",
        "error_dir": "[ERROR] Failed to delete directory: {path} ({error})",
        "done": "\nDone.",
        "deleted_files_summary": "Deleted files ({types}): {count}",
        "deleted_dirs_summary": "Deleted special directories (.actors/.deletedByTMM): {count}",
    },
}


def choose_language() -> str:
    answer = input(MESSAGES["zh"]["choose_lang"]).strip().lower()
    return "en" if answer == "en" else "zh"


def collect_targets(root_dir: str, messages, delete_nfo: bool = False):
    target_extensions = BASE_EXTENSIONS | ({NFO_EXTENSION} if delete_nfo else set())

    files_to_delete = []
    dirs_to_delete = []
    skipped_ignore_trees = []
    scanned_subdirs = 0

    for current_dir, dirnames, filenames in os.walk(root_dir, topdown=True):
        # 根目录本身不处理删除逻辑，但继续遍历它的子目录
        if current_dir == root_dir:
            # 根目录下的 .deletedByTMM 文件夹整体删除，阻止 os.walk 进入其内部
            if ".deletedByTMM" in dirnames:
                deleted_by_tmm_path = os.path.join(root_dir, ".deletedByTMM")
                if os.path.isdir(deleted_by_tmm_path):
                    dirs_to_delete.append(deleted_by_tmm_path)
                dirnames.remove(".deletedByTMM")
                print(messages["plan_dir"].format(path=root_dir))
                print(messages["plan_dirs"])
                print(messages["plan_item"].format(item=".deletedByTMM/"))
            continue
        scanned_subdirs += 1

        # 如果当前目录包含 .ignore，则跳过该目录整棵子树
        if ".ignore" in filenames:
            skipped_ignore_trees.append(current_dir)
            print(messages["skip_ignore_tree"].format(path=current_dir))
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
            print(messages["plan_dir"].format(path=current_dir))
            if planned_filenames:
                print(messages["plan_files"])
                for filename in sorted(planned_filenames):
                    print(messages["plan_item"].format(item=filename))
            if has_actors_dir:
                print(messages["plan_dirs"])
                print(messages["plan_item"].format(item=".actors/"))
        else:
            print(messages["plan_noop"].format(path=current_dir))

    return files_to_delete, dirs_to_delete, skipped_ignore_trees, scanned_subdirs


def apply_deletion(files_to_delete, dirs_to_delete, messages):
    deleted_files = 0
    deleted_dirs = 0

    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            deleted_files += 1
            print(messages["deleted_file"].format(path=file_path))
        except Exception as e:
            print(messages["error_file"].format(path=file_path, error=e))

    for dir_path in dirs_to_delete:
        try:
            shutil.rmtree(dir_path)
            deleted_dirs += 1
            print(messages["deleted_dir"].format(path=dir_path))
        except Exception as e:
            print(messages["error_dir"].format(path=dir_path, error=e))

    return deleted_files, deleted_dirs


def main(root_dir: str):
    messages = MESSAGES[choose_language()]
    # 询问是否删除 .nfo 文件（默认：否）
    nfo_answer = input(messages["ask_delete_nfo"]).strip().lower()
    delete_nfo = nfo_answer in ("y", "yes")
    if delete_nfo:
        print(messages["nfo_yes"])
    else:
        print(messages["nfo_no"])

    print(messages["scanning_header"])
    files_to_delete, dirs_to_delete, skipped_ignore_trees, scanned_subdirs = collect_targets(
        root_dir, messages, delete_nfo=delete_nfo
    )

    file_types_label = ".nfo/.png/.jpg" if delete_nfo else ".png/.jpg"
    print(messages["summary_header"])
    print(messages["scanned_subdirs"].format(count=scanned_subdirs))
    print(messages["files_planned"].format(types=file_types_label, count=len(files_to_delete)))
    print(messages["dirs_planned"].format(count=len(dirs_to_delete)))
    print(messages["ignored_trees"].format(count=len(skipped_ignore_trees)))

    if not files_to_delete and not dirs_to_delete:
        print(messages["nothing_to_delete"])
        return

    # 第二阶段：确认后执行删除
    confirm = input(messages["confirm_delete"]).strip().lower()
    if confirm != "yes":
        print(messages["canceled"])
        return

    print(messages["deleting"])
    deleted_files, deleted_dirs = apply_deletion(files_to_delete, dirs_to_delete, messages)

    print(messages["done"])
    print(messages["deleted_files_summary"].format(types=file_types_label, count=deleted_files))
    print(messages["deleted_dirs_summary"].format(count=deleted_dirs))
    print(messages["ignored_trees"].format(count=len(skipped_ignore_trees)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="先预览后确认：删除无 .ignore 目录中的 .nfo/.png/.jpg 文件，并删除 .actors；遇到 .ignore 跳过整棵子树"
    )
    parser.add_argument("root_dir", help="要扫描的根目录路径")
    args = parser.parse_args()

    main(args.root_dir)
