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
   - 删除 `.png`、`.jpg` 文件（可选删除 `.nfo`）
   - 删除 `.actors` 目录

## 脚本说明

- `add_ignore.py`  
  扫描根目录下的一级媒体目录，支持两种结构：
  - `Root/MovieName/*`
  - `Root/ShowName/S1/*`（以及其它 `S<number>` 季目录），并在存在季目录时把同级非季目录（如 `Root/ShowName/Extra`）作为直接目标目录  
  采用“扫描 + 确认”流程。输入 `yes` 后创建缺失的 `.ignore` 和 `.tmmignore`。

- `clean_subfolders.py`  
  递归扫描根目录下所有子目录。采用“扫描 + 确认”流程。  
  对于不含 `.ignore` 的目录，删除图片文件（`.png`、`.jpg`）并可选删除 `.nfo`，同时删除 `.actors` 目录。  

- `remove_ignore.py`  
  采用与 `add_ignore.py` 相同的媒体遍历逻辑。采用“扫描 + 确认”流程。  
  用于批量删除目标一层媒体子目录中的 `.ignore` / `.tmmignore`。

## 运行要求

- Python 3.8+（推荐）

## 使用方法

### 1）先添加 `.ignore` / `.tmmignore`（扫描 + 确认）

```bash
python add_ignore.py /path/to/your/library
```

脚本启动后会先询问输出语言：

```text
请选择输出语言 / Please choose output language [zh/en] (default zh):
```

> 推荐顺序：依次运行 `add_ignore.py` → `clean_subfolders.py` → `remove_ignore.py`。

### 2）清理不含 `.ignore` 的目录（扫描 + 确认）

```bash
python clean_subfolders.py /path/to/your/library
```

脚本会先询问输出语言：

```text
请选择输出语言 / Please choose output language [zh/en] (default zh):
```

随后询问是否删除 `.nfo`：

```text
Delete .nfo files? [y/N]:
```

- 输入 `y` / `yes`：会把 `.nfo` 纳入删除范围
- 直接回车（或其它输入）：不删除 `.nfo`（默认，更安全）

之后脚本会按目录输出扫描计划（先显示目录，再显示该目录下的待删项），最后再次询问是否输入 `yes` 确认执行。

### 3）删除媒体子目录中的 `.ignore` / `.tmmignore`（扫描 + 确认）

```bash
python remove_ignore.py /path/to/your/library
```

脚本启动后会先询问输出语言：

```text
请选择输出语言 / Please choose output language [zh/en] (default zh):
```

随后按树形结构输出计划，包含以下类型：
- `[无需操作] 目录内不存在需要操作的文件`
- `[计划] 删除 .tmmignore 和 .ignore`
- `[计划] 删除 .tmmignore`
- `[计划] 删除 .ignore`

## 示例（推荐顺序）

给定媒体库：

```text
/media
├── MovieA
│   └── Extras
│       ├── poster.jpg
│       └── .actors
└── ShowA
    └── S1
        └── SPs
            ├── poster.jpg
            └── info.nfo
```

1. 运行 `python add_ignore.py /media` 并确认 `yes`。  
   会在一级媒体子目录中创建标记文件，例如：
   - `/media/MovieA/Extras/.ignore`
   - `/media/MovieA/Extras/.tmmignore`
   - `/media/ShowA/S1/SPs/.ignore`
   - `/media/ShowA/S1/SPs/.tmmignore`
2. 再运行 `python clean_subfolders.py /media`。  
   扫描阶段会跳过上述已标记目录树（会输出 `[SKIP] ... found .ignore, skip subtree`），这些目录中的文件不会被删除。
3. 最后运行 `python remove_ignore.py /media` 并确认 `yes`。  
   清理完成后，可将同一批目录中的标记文件（`.ignore`、`.tmmignore`）移除。

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
- `remove_ignore.py` 使用相同的一层媒体遍历逻辑，只处理 `.ignore` / `.tmmignore` 标记文件。
- `clean_subfolders.py` 为递归遍历；任意目录内如果检测到 `.ignore`，会跳过该目录整棵子树。

## 许可证

本项目采用 [MIT License](LICENSE)。
