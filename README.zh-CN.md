# emby-tmm-library-tools（中文说明）

用于清理和维护 Emby 媒体库中 tinyMediaManager 相关文件的 Python 脚本工具集。

English documentation: [README.md](README.md)

## 功能

当前仓库包含以下能力：

1. 批量添加 `.ignore` 与 `.tmmignore`：
   - 电影结构的一层子目录（`MovieName/*`）
   - 剧集结构的一层子目录（`ShowName/S1/*`）
   - 当存在季目录时，同级非季目录本身（`ShowName/Extra`、`ShowName/SPs` 等）
2. 批量删除 `.ignore` 与 `.tmmignore`：
   - 使用与 `add_ignore.py` 相同的一层媒体子目录扫描范围
3. 对**不含** `.ignore` 的目录执行清理：
   - 删除 `.png`、`.jpg` 文件（可选删除 `theme.mp3` 和 `.nfo`）
   - 删除 `.actors` 目录
   - 删除根目录下的 `.deletedByTMM` 目录（若存在）
4. 递归删除根目录下所有子文件夹中的垃圾文件：
   - `.bif` 文件（按扩展名匹配，不区分大小写）
   - `.DS_Store` 和 `Thumbs.db`（精确文件名匹配）

## 脚本说明

- `add_ignore.py`  
  扫描根目录下的一级媒体目录，支持两种结构：
  - `Root/MovieName/*`
  - `Root/ShowName/S1/*`（以及其它 `S<number>` 季目录），并在存在季目录时把同级非季目录（如 `Root/ShowName/Extra`）作为直接目标目录  
  采用“扫描 + 确认”流程。输入 `yes` 后创建缺失的 `.ignore` 和 `.tmmignore`。

- `clean_subfolders.py`  
  递归扫描根目录下所有子目录。采用“扫描 + 确认”流程。  
  启动时询问是否额外删除 `theme.mp3` 和/或 `.nfo` 文件。  
  对于不含 `.ignore` 的目录，删除图片文件（`.png`、`.jpg`）及所选可选文件类型，并删除 `.actors` 目录。根目录下的 `.deletedByTMM` 目录若存在也会整体计划删除。

- `remove_ignore.py`  
  采用与 `add_ignore.py` 相同的媒体遍历逻辑。采用“扫描 + 确认”流程。  
  用于批量删除目标一层媒体子目录中的 `.ignore` / `.tmmignore`。

- `clean_junk.py`  
  递归扫描根目录下每个顶层条目的全部子目录。采用“扫描 + 确认”流程。  
  删除所有 `.bif` 文件（按扩展名，不区分大小写）、`.DS_Store` 和 `Thumbs.db`。  
  计划输出按顶层媒体条目分组，以树形结构显示。

## 运行要求

- Python 3.8+（推荐）

## 使用方法

### 1）`add_ignore.py` — 向媒体子目录添加 `.ignore` 和 `.tmmignore`

```bash
python add_ignore.py /path/to/your/library
```

脚本启动后先询问输出语言：

```text
请选择输出语言 / Please choose output language [zh/en] (默认 zh):
```

随后按媒体根目录分组，以树形结构输出创建计划，每条目录条目包含以下标签之一：

- `[跳过] 跳过 .actors 目录` — `.actors` 目录始终跳过
- `[跳过] 跳过 .deletedByTMM 目录` — 根目录下的 `.deletedByTMM` 目录始终跳过
- `[跳过] .ignore/.tmmignore 均已存在` — 两个标记文件均已存在，无需操作
- `[计划] 两者都不存在，创建 .ignore 与 .tmmignore` — 将同时创建两个文件
- `[计划] 已有 .ignore，创建 .tmmignore` — 将补充创建 `.tmmignore`
- `[计划] 已有 .tmmignore，创建 .ignore` — 将补充创建 `.ignore`
- `[无需操作] 目录内不存在需要操作的子目录。` — 该媒体基目录下没有子目录

扫描结束后输出汇总：

```text
=== 扫描汇总 ===
扫描子目录数: N
计划创建数: N
跳过（已存在）: N
```

若无需创建任何文件则直接退出。否则询问确认：

```text
确认创建吗？输入 yes 继续:
```

输入 `yes` 后在目标目录中创建缺失的 `.ignore` 和 `.tmmignore`。其他任何输入都会取消操作。

### 2）`clean_subfolders.py` — 删除不含 `.ignore` 的目录中的图片文件和 `.actors` 目录

> **⚠ 请先运行 `add_ignore.py` 标记需要保护的目录，否则受保护目录中的文件可能被误删。**

```bash
python clean_subfolders.py /path/to/your/library
```

脚本启动后先询问输出语言：

```text
请选择输出语言 / Please choose output language [zh/en] (默认 zh):
```

随后询问是否删除 `theme.mp3` 文件：

```text
是否删除 theme.mp3 文件？[y/N]:
```

- 输入 `y` / `yes`：将 `theme.mp3` 纳入删除范围
- 直接回车（或其他输入）：不删除 `theme.mp3`（默认，更安全）

随后询问是否删除 `.nfo` 文件：

```text
是否删除 .nfo 文件？[y/N]:
```

- 输入 `y` / `yes`：将 `.nfo` 纳入删除范围
- 直接回车（或其他输入）：不删除 `.nfo`（默认，更安全）

脚本会递归扫描所有子目录，并逐目录输出计划：

- `[跳过] <path>（发现 .ignore，跳过整棵子树）` — 此目录树受 `.ignore` 保护，不会删除任何文件
- `[计划] <path>` 并附带待删文件/目录列表 — 这些内容将被删除
- `[无需操作] <path>` — 此目录内无需删除任何内容

若根目录下存在 `.deletedByTMM` 文件夹，会作为一个整体出现在根目录的 `[计划]` 条目中，计划整体删除。

扫描结束后输出汇总：

```text
=== 汇总 ===
扫描子目录数: N
计划删除文件数（.jpg/.png）: N
计划删除目录数: N
因 .ignore 跳过的目录树: N
```

汇总中的文件类型标签会反映你的选择：例如全部启用时显示 `（.jpg/.png/theme.mp3/.nfo）`，默认仅显示 `（.jpg/.png）`。

若无需删除则直接退出。否则询问确认：

```text
确认删除吗？输入 yes 继续:
```

输入 `yes` 后删除计划中的图片文件（`.png`、`.jpg`，以及你选择的可选类型）、`.actors` 目录，以及根目录下的 `.deletedByTMM` 目录（若存在）。其他任何输入都会取消操作。

### 3）`remove_ignore.py` — 从媒体子目录删除 `.ignore` 和 `.tmmignore`

```bash
python remove_ignore.py /path/to/your/library
```

脚本启动后先询问输出语言：

```text
请选择输出语言 / Please choose output language [zh/en] (默认 zh):
```

脚本采用与 `add_ignore.py` 相同的媒体遍历逻辑，按媒体根目录分组以树形结构输出删除计划，每条目录条目包含以下标签之一：

- `[无需操作] 目录内不存在需要操作的文件` — 未发现标记文件
- `[计划] 删除 .tmmignore 和 .ignore` — 将同时删除两个文件
- `[计划] 删除 .tmmignore` — 仅删除 `.tmmignore`
- `[计划] 删除 .ignore` — 仅删除 `.ignore`

扫描结束后输出汇总：

```text
=== 扫描汇总 ===
扫描子目录数: N
计划删除数: N
无需操作数: N
```

若无需删除任何文件则直接退出。否则询问确认：

```text
确认删除吗？输入 yes 继续:
```

输入 `yes` 后删除标记文件。其他任何输入都会取消操作。

### 4）`clean_junk.py` — 递归删除垃圾文件（`.bif`、`.DS_Store`、`Thumbs.db`）

```bash
python clean_junk.py /path/to/your/library
```

脚本启动后先询问输出语言：

```text
请选择输出语言 / Please choose output language [zh/en] (默认 zh):
```

脚本递归遍历每个顶层条目下的全部子目录，按顶层媒体条目分组，以树形结构输出删除计划。顶层条目目录本身中发现的垃圾文件显示在标题行，子目录中发现的垃圾文件则以树形展开。每条条目包含以下标签之一：

- `[无需操作] 目录内不存在需要删除的垃圾文件` — 该顶层条目内未发现任何垃圾文件
- `MediaDir/ [计划] 删除 <files>` — 垃圾文件位于顶层条目目录本身
- `└── subdir/ [计划] 删除 <files>` — 垃圾文件位于子目录

扫描结束后输出汇总：

```text
=== 扫描汇总 ===
扫描目录数: N
计划删除文件数: N
无垃圾文件的顶层条目数: N
```

若无需删除任何文件则直接退出。否则询问确认：

```text
确认删除吗？输入 yes 继续:
```

输入 `yes` 后删除所有计划中的垃圾文件。其他任何输入都会取消操作。

**匹配规则：**
- `.bif` — 按文件扩展名匹配，**不区分大小写**（如 `chapter00.bif`、`intro.BIF`）
- `.DS_Store` — 精确文件名匹配
- `Thumbs.db` — 精确文件名匹配

## 示例（推荐顺序）

给定如下媒体库：

```text
/media
├── .deletedByTMM
│   └── OldShow
├── MovieA
│   ├── .actors
│   │   └── actor1.jpg
│   ├── Extras
│   │   └── poster.jpg
│   ├── poster.jpg
│   └── theme.mp3
└── ShowA
    ├── S1
    │   ├── Featurettes
    │   │   └── thumb.png
    │   └── SPs
    │       └── poster.jpg
    └── Specials
        └── ep0.jpg
```

**第一步** — 运行 `python add_ignore.py /media` 并确认 `yes`。

脚本扫描一级媒体子目录并输出创建计划：

```text
.deletedByTMM/ [跳过] 跳过 .deletedByTMM 目录

MovieA/
├── .actors/  [跳过] 跳过 .actors 目录
└── Extras/   [计划] 两者都不存在，创建 .ignore 与 .tmmignore

ShowA/
├── S1/
│   ├── Featurettes/ [计划] 两者都不存在，创建 .ignore 与 .tmmignore
│   └── SPs/         [计划] 两者都不存在，创建 .ignore 与 .tmmignore
└── Specials/        [计划] 两者都不存在，创建 .ignore 与 .tmmignore

=== 扫描汇总 ===
扫描子目录数: 4
计划创建数: 8
跳过（已存在）: 0

确认创建吗？输入 yes 继续: yes

正在创建文件...
[已创建] /media/MovieA/Extras/.ignore
[已创建] /media/MovieA/Extras/.tmmignore
[已创建] /media/ShowA/S1/Featurettes/.ignore
[已创建] /media/ShowA/S1/Featurettes/.tmmignore
[已创建] /media/ShowA/S1/SPs/.ignore
[已创建] /media/ShowA/S1/SPs/.tmmignore
[已创建] /media/ShowA/Specials/.ignore
[已创建] /media/ShowA/Specials/.tmmignore
```

- 根目录下的 `.deletedByTMM` 始终跳过，不会在其中创建标记文件。
- `MovieA` 内的 `.actors` 同样始终跳过。
- `Specials` 是 `S1` 的同级非季目录，作为直接创建目标（标记文件直接写入 `ShowA/Specials`，而非其子目录）。

**第二步** — 运行 `python clean_subfolders.py /media`，对 `theme.mp3` 输入 `y`，对 `.nfo` 输入 `N`，然后确认 `yes`。

脚本递归遍历所有子目录。根目录下的 `.deletedByTMM` 计划整体删除；含 `.ignore` 的子树整体跳过；其余目录执行清理：

```text
=== 正在扫描并规划删除 ===
[计划] /media
  待删除目录:
    - .deletedByTMM/
[计划] /media/MovieA
  待删除文件:
    - poster.jpg
    - theme.mp3
  待删除目录:
    - .actors/
[跳过] /media/MovieA/Extras（发现 .ignore，跳过整棵子树）
[无需操作] /media/ShowA
[无需操作] /media/ShowA/S1
[跳过] /media/ShowA/S1/Featurettes（发现 .ignore，跳过整棵子树）
[跳过] /media/ShowA/S1/SPs（发现 .ignore，跳过整棵子树）
[跳过] /media/ShowA/Specials（发现 .ignore，跳过整棵子树）

=== 汇总 ===
扫描子目录数: 7
计划删除文件数（.jpg/.png/theme.mp3）: 2
计划删除目录数: 2
因 .ignore 跳过的目录树: 4

确认删除吗？输入 yes 继续: yes

正在删除...
[已删除文件] /media/MovieA/poster.jpg
[已删除文件] /media/MovieA/theme.mp3
[已删除目录] /media/.deletedByTMM
[已删除目录] /media/MovieA/.actors
```

`MovieA/Extras`、`ShowA/S1/Featurettes`、`ShowA/S1/SPs` 和 `ShowA/Specials` 内的文件不受影响，因为这些子树受 `.ignore` 保护。

**第三步** — 运行 `python remove_ignore.py /media` 并确认 `yes`。

脚本采用与 `add_ignore.py` 相同的遍历逻辑，规划并删除所有标记文件：

```text
MovieA/
└── Extras/          [计划] 删除 .tmmignore 和 .ignore

ShowA/
├── S1/
│   ├── Featurettes/ [计划] 删除 .tmmignore 和 .ignore
│   └── SPs/         [计划] 删除 .tmmignore 和 .ignore
└── Specials/        [计划] 删除 .tmmignore 和 .ignore

=== 扫描汇总 ===
扫描子目录数: 4
计划删除数: 8
无需操作数: 0

确认删除吗？输入 yes 继续: yes

正在删除文件...
[已删除] /media/MovieA/Extras/.tmmignore
[已删除] /media/MovieA/Extras/.ignore
[已删除] /media/ShowA/S1/Featurettes/.tmmignore
[已删除] /media/ShowA/S1/Featurettes/.ignore
[已删除] /media/ShowA/S1/SPs/.tmmignore
[已删除] /media/ShowA/S1/SPs/.ignore
[已删除] /media/ShowA/Specials/.tmmignore
[已删除] /media/ShowA/Specials/.ignore
```

### `clean_junk.py` — 独立示例

`clean_junk.py` 与 `.ignore` 工作流无关，可在任意时刻独立运行。它递归进入每个顶层条目的所有子目录，因此能覆盖任意层级深度。给定一个垃圾文件散布在四层子目录中的媒体库：

```text
/media
├── MovieA
│   ├── .DS_Store
│   └── Bonus
│       └── Behind the Scenes
│           ├── Thumbs.db
│           └── Interviews
│               └── intro.BIF
└── ShowB
    └── S2
        └── Extras
            ├── chapter00.bif
            └── Scenes
                └── clip.DS_Store
```

运行 `python clean_junk.py /media`：

```text
MovieA/ [计划] 删除 .DS_Store
└── Bonus/
    └── Behind the Scenes/ [计划] 删除 Thumbs.db
        └── Interviews/    [计划] 删除 intro.BIF

ShowB/
└── S2/
    └── Extras/  [计划] 删除 chapter00.bif
        └── Scenes/ [计划] 删除 clip.DS_Store

=== 扫描汇总 ===
扫描目录数: 8
计划删除文件数: 5
无垃圾文件的顶层条目数: 0

确认删除吗？输入 yes 继续: yes

正在删除文件...
[已删除] /media/MovieA/.DS_Store
[已删除] /media/MovieA/Bonus/Behind the Scenes/Thumbs.db
[已删除] /media/MovieA/Bonus/Behind the Scenes/Interviews/intro.BIF
[已删除] /media/ShowB/S2/Extras/chapter00.bif
[已删除] /media/ShowB/S2/Extras/Scenes/clip.DS_Store
```


## 说明

- 强烈建议先备份媒体库，或先在测试目录验证。
- 文件后缀匹配不区分大小写。
- `add_ignore.py` 的判定逻辑：
  1. 在 `root` 下逐个检查一级目录。
  2. 若该目录下存在 `S<number>` 季目录：
     - 每个季目录（`S1`、`S2`...）作为媒体基目录，并扫描其一级子目录（`S1/*`）作为创建目标；
     - 每个同级非季目录（如 `SPs`、`Extras`）作为直接创建目标（即在 `ShowName/SPs` 本身创建标记文件）。
  3. 若不存在 `S<number>` 季目录，则按电影目录处理，扫描其一级子目录（`MovieName/*`）。
  4. 名为 `.actors` 的目录总是跳过，不会在其中创建 `.ignore` / `.tmmignore`。
  5. 根目录下名为 `.deletedByTMM` 的目录也始终跳过，不会在其中创建标记文件。
- `remove_ignore.py` 使用相同的一层媒体遍历逻辑，只处理 `.ignore` / `.tmmignore` 标记文件。
- `clean_subfolders.py` 为递归遍历；任意目录内如果检测到 `.ignore`，会跳过该目录整棵子树。根目录下的 `.deletedByTMM` 目录（若存在）会作为整体删除，不会递归进入其内部。
- `clean_junk.py` 对每个顶层条目的全部子目录做递归遍历。按扩展名（不区分大小写）匹配 `.bif`，按精确文件名匹配 `.DS_Store` 和 `Thumbs.db`。不与 `.ignore` 文件交互。

## 许可证

本项目采用 [MIT License](LICENSE)。
