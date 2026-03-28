import argparse
import os
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


def display_width(text: str) -> int:
    """计算字符串的显示宽度（宽字符按 2 计算，其余按 1 计算）"""
    width = 0
    for ch in text:
        width += 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1
    return width


def pad_to_width(text: str, target_width: int) -> str:
    """在字符串末尾填充空格以达到目标显示宽度"""
    return text + (" " * max(0, target_width - display_width(text)))


MESSAGES = {
    "zh": {
        "choose_lang": "请选择输出语言 / Please choose output language [zh/en] (默认 zh): ",
        "noop_dir": "[无需操作] 目录内不存在需要删除的垃圾文件",
        "plan_delete": "[计划] 删除 {filename}",
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
        "noop_dir": "[NOOP] No junk files found in this directory",
        "plan_delete": "[PLAN] Delete {filename}",
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


def build_entry_tree(entry_path: str, messages: dict) -> tuple:
    """
    递归构建顶层条目的完整目录树（包含所有子目录和垃圾文件节点）。

    每个节点结构：
        {'name': str, 'is_dir': bool, 'children': list, 'detail': str | None}

    - 垃圾文件作为叶子节点，detail 为 plan_delete 标签。
    - 无垃圾文件且无子目录的目录节点，detail 为 noop_dir 标签。
    - 其余目录节点 detail 为 None，由 children 展开。

    返回 (root_node, targets, dir_count)：
        root_node  — 条目根节点
        targets    — 需要删除的文件绝对路径列表
        dir_count  — 扫描的目录总数
    """
    targets = []
    dir_count = [0]

    def build_node(dir_path: str) -> dict:
        dir_count[0] += 1
        node = {
            "name": os.path.basename(dir_path),
            "is_dir": True,
            "children": [],
            "detail": None,
        }
        try:
            raw_entries = sorted(os.scandir(dir_path), key=lambda e: e.name.lower())
        except OSError:
            node["detail"] = messages["noop_dir"]
            return node

        junk_files = [e for e in raw_entries if e.is_file() and is_junk_file(e.name)]
        subdirs = [e for e in raw_entries if e.is_dir()]

        if not junk_files and not subdirs:
            # 叶子目录：无可处理垃圾文件，且无子目录
            node["detail"] = messages["noop_dir"]
            return node

        # 垃圾文件节点（文件名升序）排在同级子目录之前
        for e in junk_files:
            targets.append(e.path)
            node["children"].append(
                {
                    "name": e.name,
                    "is_dir": False,
                    "children": [],
                    "detail": messages["plan_delete"].format(filename=e.name),
                }
            )

        # 子目录节点递归构建（目录名升序）
        for e in subdirs:
            node["children"].append(build_node(e.path))

        return node

    root_node = build_node(entry_path)
    return root_node, targets, dir_count[0]


def render_entry_lines(entry_node: dict) -> list:
    """
    将条目节点的子树渲染为树形行列表。

    同一父目录下的兄弟节点（文件与子目录混合）按显示宽度对齐，
    使各自的状态标签（detail）起始列保持一致。
    条目本身以 └── 分支显示，故其子节点从 4 空格缩进开始。
    """
    lines = []

    def collect(node, prefix):
        children = node["children"]
        if not children:
            return

        # 预计算同级所有子节点的行首文字
        heads = []
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            branch = "└──" if is_last else "├──"
            heads.append(f"{prefix}{branch} {child['name']}")

        # 以同级有内联标签的节点的最大显示宽度对齐（展开节点不参与列宽计算）
        labeled_widths = [display_width(h) for h, child in zip(heads, children) if child["detail"]]
        max_width = max(labeled_widths) if labeled_widths else 0

        for i, (child, head) in enumerate(zip(children, heads)):
            is_last = i == len(children) - 1
            child_prefix = prefix + ("    " if is_last else "│   ")

            if child["detail"]:
                lines.append(f"{pad_to_width(head, max_width)} {child['detail']}")
            else:
                lines.append(head)

            collect(child, child_prefix)

    # 条目始终以 └── 显示（每个条目独占一个块），子节点缩进 4 个空格
    collect(entry_node, "    ")
    return lines


def flush_entry_plan(root_dir: str, entry_node: dict, messages: dict, has_targets: bool):
    """打印单个顶层条目的计划展示块（先打印 root_dir 标题行，再展开条目树）"""
    print()
    entry_line = f"└── {entry_node['name']}"
    print(root_dir)
    if not has_targets:
        # 整个条目树内无垃圾文件：折叠为单行 noop（即使条目本身有子目录）
        print(f"{entry_line} {messages['noop_dir']}")
    else:
        print(entry_line)
        for line in render_entry_lines(entry_node):
            print(line)


def collect_deletion_targets(root_dir: str, messages: dict) -> tuple:
    """
    扫描根目录下的所有顶层条目，构建并打印各条目的完整树形计划。

    返回 (targets, scanned_dirs, noop_count)：
        targets      — 全部待删除文件的绝对路径列表
        scanned_dirs — 扫描的目录总数（含各条目子目录）
        noop_count   — 无垃圾文件的顶层条目数
    """
    targets = []
    scanned_dirs = 0
    noop_count = 0

    try:
        root_scan = sorted(os.scandir(root_dir), key=lambda e: e.name.lower())
    except OSError:
        return [], 0, 0

    # 根目录本身直接包含的垃圾文件（不隶属于任何子条目）
    root_junk = [e for e in root_scan if e.is_file() and is_junk_file(e.name)]
    if root_junk:
        print()
        print(root_dir)
        heads = []
        for i, e in enumerate(root_junk):
            branch = "└──" if i == len(root_junk) - 1 else "├──"
            heads.append(f"{branch} {e.name}")
        max_w = max(display_width(h) for h in heads)
        for e, head in zip(root_junk, heads):
            label = messages["plan_delete"].format(filename=e.name)
            print(f"{pad_to_width(head, max_w)} {label}")
        targets.extend(e.path for e in root_junk)

    top_entries = [e for e in root_scan if e.is_dir()]

    if not top_entries:
        if not root_junk:
            print(f"\n{root_dir} {messages['noop_dir']}")
        return targets, 0, 0

    for entry in top_entries:
        entry_node, entry_targets, entry_dir_count = build_entry_tree(entry.path, messages)
        scanned_dirs += entry_dir_count

        if not entry_targets:
            noop_count += 1

        flush_entry_plan(root_dir, entry_node, messages, bool(entry_targets))
        targets.extend(entry_targets)

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
