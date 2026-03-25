import argparse
import os
from pathlib import PurePosixPath
import re
import unicodedata


SEASON_DIR_PATTERN = re.compile(r"^S\d+$", re.IGNORECASE)
MEDIA_LABEL_WIDTH = 20
MESSAGES = {
    "zh": {
        "choose_lang": "请选择输出语言 / Please choose output language [zh/en] (默认 zh): ",
        "plan_header": "\n{media_label}",
        "plan_header_noop": "\n{media_label} {detail}",
        "noop_dir": "[无需操作] 目录内不存在需要操作的文件",
        "delete_both": "[计划] 删除 .tmmignore 和 .ignore",
        "delete_tmmignore": "[计划] 删除 .tmmignore",
        "delete_ignore": "[计划] 删除 .ignore",
        "scan_summary": "\n=== 扫描汇总 ===",
        "scanned_subdirs": "扫描子目录数: {count}",
        "planned_deletions": "计划删除数: {count}",
        "noop_count": "无需操作数: {count}",
        "nothing_to_delete": "\n无需删除任何文件。",
        "confirm_delete": "\n确认删除吗？输入 yes 继续: ",
        "canceled": "已取消，未删除任何文件。",
        "deleting": "\n正在删除文件...",
        "deleted": "[已删除] {path}",
        "error_delete": "[错误] 删除失败: {path} ({error})",
        "done": "\n完成。",
        "deleted_count": "已删除: {count}",
        "errors": "错误: {count}",
    },
    "en": {
        "choose_lang": "请选择输出语言 / Please choose output language [zh/en] (default zh): ",
        "plan_header": "\n{media_label}",
        "plan_header_noop": "\n{media_label} {detail}",
        "noop_dir": "[NOOP] No files in this directory require action",
        "delete_both": "[PLAN] Delete .tmmignore and .ignore",
        "delete_tmmignore": "[PLAN] Delete .tmmignore",
        "delete_ignore": "[PLAN] Delete .ignore",
        "scan_summary": "\n=== Scan Summary ===",
        "scanned_subdirs": "Scanned subdirectories: {count}",
        "planned_deletions": "Planned deletions: {count}",
        "noop_count": "No-op directories: {count}",
        "nothing_to_delete": "\nNothing to delete.",
        "confirm_delete": "\nConfirm deletion? Type yes to continue: ",
        "canceled": "Canceled. No files were deleted.",
        "deleting": "\nDeleting files...",
        "deleted": "[DELETED] {path}",
        "error_delete": "[ERROR] Failed to delete: {path} ({error})",
        "done": "\nDone.",
        "deleted_count": "Deleted: {count}",
        "errors": "Errors: {count}",
    },
}


def choose_language() -> str:
    answer = input(MESSAGES["zh"]["choose_lang"]).strip().lower()
    return "en" if answer == "en" else "zh"


def iter_media_base_dirs(root_dir: str):
    # 先按剧集目录（S1/S2...）和非剧集目录拆分，便于后续统一处理
    for entry in os.scandir(root_dir):
        if not entry.is_dir():
            continue

        season_dirs = []
        non_season_dirs = []
        for child in os.scandir(entry.path):
            if not child.is_dir():
                continue
            if SEASON_DIR_PATTERN.match(child.name):
                season_dirs.append(child.path)
            else:
                non_season_dirs.append(child.path)

        if season_dirs:
            for season_dir in season_dirs:
                yield entry.path, season_dir, False
            for non_season_dir in non_season_dirs:
                yield entry.path, non_season_dir, True
        else:
            yield entry.path, entry.path, False


def flush_media_plan(media_label: str, plan_rows, messages):
    def display_width(text: str) -> int:
        width = 0
        for ch in text:
            # 宽字符(F/W)按2个显示位计算，其他字符按1个显示位计算，保证中英文混排时对齐稳定
            width += 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1
        return width

    def pad_to_width(text: str, target_width: int) -> str:
        return text + (" " * max(0, target_width - display_width(text)))

    if not plan_rows:
        media_line = f"{media_label}"
        aligned_media = pad_to_width(media_line, MEDIA_LABEL_WIDTH)
        print(messages["plan_header_noop"].format(media_label=aligned_media, detail=messages["noop_dir"]))
        return
    print(messages["plan_header"].format(media_label=media_label))

    root = {"children": {}}

    for rel_path, detail in plan_rows:
        parts = list(PurePosixPath(rel_path).parts)
        node = root
        for part in parts:
            children = node["children"]
            if part not in children:
                children[part] = {"children": {}, "detail": None}
            node = children[part]
        node["detail"] = detail

    lines = []

    def collect_lines(node, prefix=""):
        children = list(node["children"].items())
        for index, (name, child) in enumerate(children):
            is_last = index == len(children) - 1
            branch = "└──" if is_last else "├──"
            child_prefix = "    " if is_last else "│   "
            line_head = f"{prefix}{branch} {name}/"
            lines.append((line_head, child["detail"]))
            if child["children"]:
                collect_lines(child, prefix + child_prefix)

    collect_lines(root)
    max_head_width = max((display_width(line_head) for line_head, _ in lines), default=0)

    for line_head, detail in lines:
        if detail:
            aligned_head = pad_to_width(line_head, max_head_width)
            print(f"{aligned_head} {detail}")
        else:
            print(line_head)


def collect_deletion_targets(root_dir: str, messages):
    targets = []
    scanned_subdirs = 0
    noop_count = 0
    current_media_root = None
    plan_rows = []

    for media_root, base_dir, scan_self in iter_media_base_dirs(root_dir):
        if current_media_root != media_root:
            if current_media_root is not None:
                media_label = f"{os.path.basename(current_media_root)}/"
                flush_media_plan(media_label, plan_rows, messages)
            current_media_root = media_root
            plan_rows = []

        if scan_self:
            dirs_to_scan = [base_dir]
        else:
            with os.scandir(base_dir) as entries:
                dirs_to_scan = [entry.path for entry in entries if entry.is_dir()]
            if not dirs_to_scan:
                rel_base = os.path.relpath(base_dir, media_root).replace(os.sep, "/")
                # rel_base == "." 表示电影目录本身无子目录；该场景由媒体级“无需操作”头行展示，
                # 这里只为嵌套基目录补充逐行“无需操作”，避免重复输出。
                if rel_base != ".":
                    plan_rows.append((rel_base, messages["noop_dir"]))
                    noop_count += 1
                continue

        for current_dir in dirs_to_scan:
            scanned_subdirs += 1
            rel_path = os.path.relpath(current_dir, media_root).replace(os.sep, "/")
            with os.scandir(current_dir) as children:
                filenames = {child.name for child in children if child.is_file()}

            has_ignore = ".ignore" in filenames
            has_tmmignore = ".tmmignore" in filenames

            if has_ignore and has_tmmignore:
                targets.append(os.path.join(current_dir, ".tmmignore"))
                targets.append(os.path.join(current_dir, ".ignore"))
                plan_rows.append((rel_path, messages["delete_both"]))
            elif has_tmmignore:
                targets.append(os.path.join(current_dir, ".tmmignore"))
                plan_rows.append((rel_path, messages["delete_tmmignore"]))
            elif has_ignore:
                targets.append(os.path.join(current_dir, ".ignore"))
                plan_rows.append((rel_path, messages["delete_ignore"]))
            else:
                plan_rows.append((rel_path, messages["noop_dir"]))
                noop_count += 1

    if current_media_root is not None:
        media_label = f"{os.path.basename(current_media_root)}/"
        flush_media_plan(media_label, plan_rows, messages)

    return targets, scanned_subdirs, noop_count


def apply_deletion(targets, messages):
    deleted_count = 0
    error_count = 0

    for path in targets:
        try:
            os.remove(path)
            deleted_count += 1
            print(messages["deleted"].format(path=path))
        except OSError as e:
            error_count += 1
            print(messages["error_delete"].format(path=path, error=e))

    return deleted_count, error_count


def remove_ignore_and_tmmignore(root_dir: str):
    messages = MESSAGES[choose_language()]
    targets, scanned_subdirs, noop_count = collect_deletion_targets(root_dir, messages)

    print(messages["scan_summary"])
    print(messages["scanned_subdirs"].format(count=scanned_subdirs))
    print(messages["planned_deletions"].format(count=len(targets)))
    print(messages["noop_count"].format(count=noop_count))

    if not targets:
        print(messages["nothing_to_delete"])
        return

    confirm = input(messages["confirm_delete"]).strip().lower()
    if confirm != "yes":
        print(messages["canceled"])
        return

    print(messages["deleting"])
    deleted_count, error_count = apply_deletion(targets, messages)

    print(messages["done"])
    print(messages["deleted_count"].format(count=deleted_count))
    print(messages["errors"].format(count=error_count))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "扫描并规划在媒体子目录中删除 .ignore/.tmmignore，支持 "
            "Root/MovieName/ 与 Root/ShowName/S1 两种结构"
        )
    )
    parser.add_argument("root_dir", help="媒体库根目录路径")
    args = parser.parse_args()

    remove_ignore_and_tmmignore(args.root_dir)
