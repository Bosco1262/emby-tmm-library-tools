import argparse
import os
import re


SEASON_DIR_PATTERN = re.compile(r"^S\d+$", re.IGNORECASE)
MESSAGES = {
    "zh": {
        "choose_lang": "请选择输出语言 / Please choose output language [zh/en] (默认 zh): ",
        "plan_header": "\n{media_label}",
        "noop_dir": "[无需操作] 目录内不存在需要操作的文件",
        "skip_actors": "[跳过] 跳过 .actors 目录",
        "both_exists": "[无需操作] .ignore/.tmmignore 均已存在，跳过",
        "has_ignore": "[计划] 已有 .ignore，创建 .tmmignore",
        "has_tmmignore": "[计划] 已有 .tmmignore，创建 .ignore",
        "create_both": "[计划] 两者都不存在，创建 .ignore 与 .tmmignore",
        "scan_summary": "\n=== 扫描汇总 ===",
        "scanned_subdirs": "扫描子目录数: {count}",
        "planned_creations": "计划创建数: {count}",
        "skipped_exists": "跳过（已存在）: {count}",
        "nothing_to_create": "\n无需创建任何文件。",
        "confirm_create": "\n确认创建吗？输入 yes 继续: ",
        "canceled": "已取消，未创建任何文件。",
        "creating": "\n正在创建文件...",
        "created": "[已创建] {path}",
        "error_create": "[错误] 创建失败: {path} ({error})",
        "done": "\n完成。",
        "created_count": "已创建: {count}",
        "errors": "错误: {count}",
    },
    "en": {
        "choose_lang": "请选择输出语言 / Please choose output language [zh/en] (default zh): ",
        "plan_header": "\n{media_label}",
        "noop_dir": "[NOOP] No files in this directory require action",
        "skip_actors": "[SKIP] Skip .actors directory",
        "both_exists": "[NOOP] .ignore/.tmmignore already exist, skip",
        "has_ignore": "[PLAN] .ignore exists, create .tmmignore",
        "has_tmmignore": "[PLAN] .tmmignore exists, create .ignore",
        "create_both": "[PLAN] Both missing, create .ignore and .tmmignore",
        "scan_summary": "\n=== Scan Summary ===",
        "scanned_subdirs": "Scanned subdirectories: {count}",
        "planned_creations": "Planned creations: {count}",
        "skipped_exists": "Skipped (already existed): {count}",
        "nothing_to_create": "\nNothing to create.",
        "confirm_create": "\nConfirm creation? Type yes to continue: ",
        "canceled": "Canceled. No files were created.",
        "creating": "\nCreating files...",
        "created": "[CREATED] {path}",
        "error_create": "[ERROR] Failed to create: {path} ({error})",
        "done": "\nDone.",
        "created_count": "Created: {count}",
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
    if not plan_rows:
        print(messages["plan_header"].format(media_label=f"{media_label} {messages['noop_dir']}"))
        return
    print(messages["plan_header"].format(media_label=media_label))

    root = {"children": {}}

    for rel_path, detail in plan_rows:
        parts = [part for part in rel_path.split("/") if part and part != "."]
        node = root
        for part in parts:
            children = node["children"]
            if part not in children:
                children[part] = {"children": {}, "detail": None}
            node = children[part]
        node["detail"] = detail

    def print_tree(node, prefix=""):
        children = list(node["children"].items())
        for index, (name, child) in enumerate(children):
            is_last = index == len(children) - 1
            branch = "└──" if is_last else "├──"
            child_prefix = "    " if is_last else "│   "
            line = f"{prefix}{branch} {name}/"
            if child["detail"]:
                line = f"{line} {child['detail']}"
            print(line)
            if child["children"]:
                print_tree(child, prefix + child_prefix)

    print_tree(root)


def collect_creation_targets(root_dir: str, messages):
    targets = []
    scanned_subdirs = 0
    skipped_count = 0
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
                if rel_base != ".":
                    plan_rows.append((rel_base, messages["noop_dir"]))
                continue

        for current_dir in dirs_to_scan:
            rel_path = os.path.relpath(current_dir, media_root).replace(os.sep, "/")

            if os.path.basename(current_dir) == ".actors":
                plan_rows.append((rel_path, messages["skip_actors"]))
                continue
            with os.scandir(current_dir) as children:
                filenames = {child.name for child in children if child.is_file()}
            scanned_subdirs += 1
            has_ignore = ".ignore" in filenames
            has_tmmignore = ".tmmignore" in filenames
            ignore_path = os.path.join(current_dir, ".ignore")
            tmmignore_path = os.path.join(current_dir, ".tmmignore")

            if not has_ignore:
                targets.append(ignore_path)
            if not has_tmmignore:
                targets.append(tmmignore_path)
            if has_ignore and has_tmmignore:
                plan_rows.append((rel_path, messages["both_exists"]))
                skipped_count += 2
            elif has_ignore and not has_tmmignore:
                plan_rows.append((rel_path, messages["has_ignore"]))
                skipped_count += 1
            elif not has_ignore and has_tmmignore:
                plan_rows.append((rel_path, messages["has_tmmignore"]))
                skipped_count += 1
            else:
                plan_rows.append((rel_path, messages["create_both"]))

    if current_media_root is not None:
        media_label = f"{os.path.basename(current_media_root)}/"
        flush_media_plan(media_label, plan_rows, messages)

    return targets, scanned_subdirs, skipped_count


def apply_creation(targets, messages):
    created_count = 0
    error_count = 0

    for path in targets:
        try:
            with open(path, "w", encoding="utf-8"):
                pass
            created_count += 1
            print(messages["created"].format(path=path))
        except OSError as e:
            error_count += 1
            print(messages["error_create"].format(path=path, error=e))

    return created_count, error_count


def add_ignore_and_tmmignore(root_dir: str):
    messages = MESSAGES[choose_language()]
    targets, scanned_subdirs, skipped_count = collect_creation_targets(root_dir, messages)

    print(messages["scan_summary"])
    print(messages["scanned_subdirs"].format(count=scanned_subdirs))
    print(messages["planned_creations"].format(count=len(targets)))
    print(messages["skipped_exists"].format(count=skipped_count))

    if not targets:
        print(messages["nothing_to_create"])
        return

    confirm = input(messages["confirm_create"]).strip().lower()
    if confirm != "yes":
        print(messages["canceled"])
        return

    print(messages["creating"])
    created_count, error_count = apply_creation(targets, messages)

    print(messages["done"])
    print(messages["created_count"].format(count=created_count))
    print(messages["skipped_exists"].format(count=skipped_count))
    print(messages["errors"].format(count=error_count))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Plan and create .ignore/.tmmignore in media subfolders: supports "
            "Root/MovieName/ and Root/ShowName/S1 layouts"
        )
    )
    parser.add_argument("root_dir", help="Path to the media library root directory")
    args = parser.parse_args()

    add_ignore_and_tmmignore(args.root_dir)
