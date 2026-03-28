import argparse
import os
from pathlib import PurePosixPath
import unicodedata


# 目标垃圾文件：精确文件名匹配（区分大小写）
JUNK_EXACT_NAMES = {".DS_Store", "Thumbs.db"}
# 目标垃圾文件：按扩展名匹配（不区分大小写）
JUNK_SUFFIXES = {".bif"}


def is_junk_file(filename: str) -> bool:
    """判断文件名是否属于垃圾文件（精确名称或扩展名匹配）"""
    if filename in JUNK_EXACT_NAMES:
        return True
    _, ext = os.path.splitext(filename)
    return ext.lower() in JUNK_SUFFIXES


MESSAGES = {
    "zh": {
        "choose_lang": "请选择输出语言 / Please choose output language [zh/en] (默认 zh): ",
        "plan_header": "\n{media_label}",
        "plan_header_noop": "\n{media_label} {detail}",
        "noop_dir": "[无需操作] 目录内不存在需要删除的垃圾文件",
        "plan_delete": "[计划] 删除 {files}",
        "scan_summary": "\n=== 扫描汇总 ===",
        "scanned_dirs": "扫描目录数: {count}",
        "planned_deletions": "计划删除文件数: {count}",
        "noop_count": "无垃圾文件的顶层条目数: {count}",
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
        "noop_dir": "[NOOP] No junk files found in this entry",
        "plan_delete": "[PLAN] Delete {files}",
        "scan_summary": "\n=== Scan Summary ===",
        "scanned_dirs": "Scanned directories: {count}",
        "planned_deletions": "Planned file deletions: {count}",
        "noop_count": "Top-level entries with no junk: {count}",
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


def flush_media_plan(media_label: str, plan_rows, messages, root_detail=None):
    def display_width(text: str) -> int:
        width = 0
        for ch in text:
            # 宽字符(F/W)按2个显示位计算，其他字符按1个显示位计算，保证中英文混排时对齐稳定
            width += 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1
        return width

    def pad_to_width(text: str, target_width: int) -> str:
        return text + (" " * max(0, target_width - display_width(text)))

    if not plan_rows:
        # 无子目录计划行：显示根目录垃圾文件信息或无需操作提示
        detail = root_detail if root_detail is not None else messages["noop_dir"]
        print(messages["plan_header_noop"].format(media_label=media_label, detail=detail))
        return
    # 有子目录计划行：若根目录本身也有垃圾文件，将其显示在标题行同侧
    if root_detail is not None:
        print(messages["plan_header_noop"].format(media_label=media_label, detail=root_detail))
    else:
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
    scanned_dirs = 0
    noop_count = 0

    # 遍历根目录下的每个直接子条目（顶层媒体文件夹）
    for entry in sorted(os.scandir(root_dir), key=lambda e: e.name.lower()):
        if not entry.is_dir():
            continue

        media_root = entry.path
        media_label = f"{entry.name}/"
        plan_rows = []

        # 递归遍历当前顶层条目及其所有子目录，查找垃圾文件
        root_detail = None  # 顶层条目目录本身含垃圾文件时的详情
        for dirpath, dirnames, filenames in os.walk(media_root):
            scanned_dirs += 1
            # 找出该目录下所有属于垃圾文件名集合的文件，并排序以保证输出稳定
            junk_found = sorted(f for f in filenames if is_junk_file(f))
            if junk_found:
                rel_path = os.path.relpath(dirpath, media_root).replace(os.sep, "/")
                detail = messages["plan_delete"].format(files=", ".join(junk_found))
                if rel_path == ".":
                    # 垃圾文件位于顶层条目目录本身，单独记录以便在标题行显示
                    root_detail = detail
                else:
                    plan_rows.append((rel_path, detail))
                for junk_file in junk_found:
                    targets.append(os.path.join(dirpath, junk_file))

        if not plan_rows and root_detail is None:
            noop_count += 1

        flush_media_plan(media_label, plan_rows, messages, root_detail=root_detail)

    return targets, scanned_dirs, noop_count


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


def clean_junk_files(root_dir: str):
    messages = MESSAGES[choose_language()]
    targets, scanned_dirs, noop_count = collect_deletion_targets(root_dir, messages)

    print(messages["scan_summary"])
    print(messages["scanned_dirs"].format(count=scanned_dirs))
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
            "递归扫描根目录下所有子文件夹，删除 .bif、.DS_Store、Thumbs.db 等垃圾文件，"
            "支持先扫描预览再确认执行"
        )
    )
    parser.add_argument("root_dir", help="媒体库根目录路径")
    args = parser.parse_args()

    clean_junk_files(args.root_dir)
