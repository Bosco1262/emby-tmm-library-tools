import argparse
import os
from pathlib import PurePosixPath
import unicodedata


# 精确匹配文件名（区分大小写）
JUNK_NAMES = {"Thumbs.db", ".DS_Store"}
# 匹配文件扩展名（不区分大小写）
JUNK_EXTENSIONS = {".bif"}
MEDIA_LABEL_WIDTH = 20
MESSAGES = {
    "zh": {
        "choose_lang": "请选择输出语言 / Please choose output language [zh/en] (默认 zh): ",
        "plan_header": "\n{media_label}",
        "plan_header_noop": "\n{media_label} {detail}",
        "noop_label": "[无需操作] 该媒体目录内未发现垃圾文件。",
        "plan_delete": "[计划] 将删除",
        "scan_summary": "\n=== 扫描汇总 ===",
        "scanned_dirs": "扫描目录数: {count}",
        "planned_deletions": "计划删除文件数: {count}",
        "nothing_to_delete": "\n未发现任何垃圾文件，无需删除。",
        "confirm_delete": "\n确认删除吗？输入 yes 继续: ",
        "canceled": "已取消，未执行删除。",
        "deleting": "\n正在删除...",
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
        "noop_label": "[NOOP] No junk files found in this media directory.",
        "plan_delete": "[PLAN] Will delete",
        "scan_summary": "\n=== Scan Summary ===",
        "scanned_dirs": "Scanned directories: {count}",
        "planned_deletions": "Planned deletions: {count}",
        "nothing_to_delete": "\nNo junk files found. Nothing to delete.",
        "confirm_delete": "\nConfirm deletion? Type yes to continue: ",
        "canceled": "Canceled. No deletion was performed.",
        "deleting": "\nDeleting...",
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


def is_junk_file(filename: str) -> bool:
    """判断文件是否为需要清理的垃圾文件（.bif、.DS_Store、Thumbs.db）"""
    if filename in JUNK_NAMES:
        return True
    _, ext = os.path.splitext(filename)
    return ext.lower() in JUNK_EXTENSIONS


def flush_junk_plan(media_label: str, plan_rows, messages):
    """按媒体目录输出垃圾文件扫描计划，使用树形结构展示（文件节点不加 /）"""
    def display_width(text: str) -> int:
        width = 0
        for ch in text:
            # 宽字符(F/W)按2个显示位计算，其他字符按1个显示位计算，保证中英文混排时对齐稳定
            width += 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1
        return width

    def pad_to_width(text: str, target_width: int) -> str:
        return text + (" " * max(0, target_width - display_width(text)))

    if not plan_rows:
        aligned_media = pad_to_width(media_label, MEDIA_LABEL_WIDTH)
        print(messages["plan_header_noop"].format(media_label=aligned_media, detail=messages["noop_label"]))
        return

    print(messages["plan_header"].format(media_label=media_label))

    # 构建树结构，区分文件节点（叶子，不加 /）和目录节点（中间节点，加 /）
    root = {"children": {}, "detail": None, "is_file": False}
    for rel_path, detail in plan_rows:
        parts = list(PurePosixPath(rel_path).parts)
        node = root
        for i, part in enumerate(parts):
            children = node["children"]
            if part not in children:
                # 路径最后一个部分为文件节点，其余为目录节点
                is_file = i == len(parts) - 1
                children[part] = {"children": {}, "detail": None, "is_file": is_file}
            node = children[part]
        node["detail"] = detail

    lines = []

    def collect_lines(node, prefix=""):
        children = list(node["children"].items())
        for index, (name, child) in enumerate(children):
            is_last = index == len(children) - 1
            branch = "└──" if is_last else "├──"
            child_prefix = "    " if is_last else "│   "
            # 文件节点不加 /，目录节点加 /
            suffix = "" if child["is_file"] else "/"
            line_head = f"{prefix}{branch} {name}{suffix}"
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


def collect_junk_targets(root_dir: str, messages):
    """扫描根目录下所有媒体子目录，收集需删除的垃圾文件（.bif、.DS_Store、Thumbs.db）"""
    targets = []
    scanned_dirs = 0

    # 获取根目录下所有媒体子目录，排序以保证输出稳定
    media_roots = sorted(
        [entry.path for entry in os.scandir(root_dir) if entry.is_dir()],
        key=lambda p: os.path.basename(p).lower(),
    )

    for media_root in media_roots:
        plan_rows = []

        # 递归遍历该媒体目录下的所有子目录（含本身），收集垃圾文件
        for current_dir, _dirnames, filenames in os.walk(media_root):
            scanned_dirs += 1
            for filename in filenames:
                if is_junk_file(filename):
                    file_path = os.path.join(current_dir, filename)
                    # 相对于媒体根目录的路径，用于树形展示
                    rel_to_media = os.path.relpath(file_path, media_root).replace(os.sep, "/")
                    targets.append(file_path)
                    plan_rows.append((rel_to_media, messages["plan_delete"]))

        # 输出该媒体目录的垃圾文件计划树
        media_label = f"{os.path.basename(media_root)}/"
        flush_junk_plan(media_label, plan_rows, messages)

    return targets, scanned_dirs


def apply_deletion(targets, messages):
    """执行文件删除，返回已删除数量和错误数量"""
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
    targets, scanned_dirs = collect_junk_targets(root_dir, messages)

    print(messages["scan_summary"])
    print(messages["scanned_dirs"].format(count=scanned_dirs))
    print(messages["planned_deletions"].format(count=len(targets)))

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
            "扫描并删除媒体库中的垃圾文件（.bif、.DS_Store、Thumbs.db），"
            "支持先预览后确认执行"
        )
    )
    parser.add_argument("root_dir", help="媒体库根目录路径")
    args = parser.parse_args()

    clean_junk_files(args.root_dir)
