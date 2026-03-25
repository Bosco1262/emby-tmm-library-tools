# emby-tmm-library-tools

Utility Python scripts to clean and maintain tinyMediaManager files for Emby media libraries.

中文文档请见：[README.zh-CN.md](README.zh-CN.md)

## Features

This repository currently includes scripts to:

1. Add `.ignore` and `.tmmignore`:
   - in first-level subfolders under movie bases (`MovieName/*`)
   - in first-level subfolders under show/season bases (`ShowName/S1/*`) and directly in season-layout sibling non-season dirs (`ShowName/Extra`, `ShowName/SPs`, etc.)
2. Remove `.ignore` and `.tmmignore`:
   - in the same first-level media subfolders scanned by `add_ignore.py`
3. In subfolders **without** `.ignore`:
   - Delete `.png`, `.jpg` files (and optionally `.nfo` files)
   - Delete `.actors` directory if it exists

## Scripts

- `add_ignore.py`  
  Scans first-level media directories under the root.  
  Supports two structures:
  - `Root/MovieName/*`
  - `Root/ShowName/S1/*` (and other `S<number>` seasons), plus sibling non-season directories when seasons exist (for example `Root/ShowName/Extra`)  
  Uses a scan + confirm workflow.  
  After you type `yes`, it creates missing `.ignore` and `.tmmignore` files in target directories.

- `clean_subfolders.py`  
  Scans all subfolders under a root directory.  
  Uses a scan + confirm workflow.  
  For subfolders without `.ignore`, it deletes image files (`.png`, `.jpg`) and optionally `.nfo` files (you are prompted at startup), and removes `.actors` directory.

- `remove_ignore.py`  
  Uses the same media traversal logic as `add_ignore.py`.  
  Uses a scan + confirm workflow.  
  It plans and deletes existing `.ignore`/`.tmmignore` in target first-level media subfolders.

## Requirements

- Python 3.8+ (recommended)

## Usage

### 1) `add_ignore.py` — Add `.ignore` and `.tmmignore` to media subfolders

```bash
python add_ignore.py /path/to/your/library
```

The script first asks for output language:

```text
请选择输出语言 / Please choose output language [zh/en] (default zh):
```

It then scans and prints a planned creation tree grouped by media root. Each entry is labeled with one of:

- `[SKIP] Skip .actors directory` — `.actors` directories are always skipped
- `[SKIP] .ignore/.tmmignore already exist` — both marker files are already present
- `[PLAN] Both missing, create .ignore and .tmmignore` — will create both files
- `[PLAN] .ignore exists, create .tmmignore` — will create the missing `.tmmignore`
- `[PLAN] .tmmignore exists, create .ignore` — will create the missing `.ignore`
- `[NOOP] No files in this directory require action` — no subdirectories found under this media base

After scanning, a summary is printed:

```text
=== Scan Summary ===
Scanned subdirectories: N
Planned creations: N
Skipped (already existed): N
```

If there is nothing to create, the script exits. Otherwise it asks for confirmation:

```text
Confirm creation? Type yes to continue:
```

Type `yes` to create the missing `.ignore` and `.tmmignore` files. Any other input cancels without making changes.

### 2) `clean_subfolders.py` — Delete image files and `.actors` directories in subfolders without `.ignore`

> **⚠ Run `add_ignore.py` first to mark folders you want to protect, or files in those folders may be deleted.**

```bash
python clean_subfolders.py /path/to/your/library
```

The script first asks for output language:

```text
请选择输出语言 / Please choose output language [zh/en] (default zh):
```

Then it asks whether to include `.nfo` files in the deletion:

```text
Delete .nfo files? [y/N]:
```

- Enter `y` or `yes` to include `.nfo` files in the deletion.
- Press Enter (or type anything else) to skip `.nfo` files (default, safe choice).

The script then recursively walks all subdirectories and prints the planned actions directory by directory:

- `[SKIP] <path> (found .ignore, skip subtree)` — subtree is protected by `.ignore`, no files will be deleted here
- `[PLAN] <path>` followed by files/directories planned for deletion — these will be removed
- `[NOOP] <path>` — nothing to delete in this directory

After scanning, a summary is printed:

```text
=== Summary ===
Scanned subdirectories: N
Files planned for deletion (.png/.jpg): N
Directories planned for deletion: N
Skipped directory trees with .ignore: N
```

If nothing needs to be deleted, the script exits. Otherwise it asks for confirmation:

```text
Confirm deletion? Type yes to continue:
```

Type `yes` to delete the planned image files (`.png`, `.jpg`, and optionally `.nfo`) and `.actors` directories. Any other input cancels without making changes.

### 3) `remove_ignore.py` — Remove `.ignore` and `.tmmignore` from media subfolders

```bash
python remove_ignore.py /path/to/your/library
```

The script first asks for output language:

```text
请选择输出语言 / Please choose output language [zh/en] (default zh):
```

It uses the same media traversal logic as `add_ignore.py` and prints a planned deletion tree grouped by media root. Each entry is labeled with one of:

- `[NOOP] No files in this directory require action` — no marker files found
- `[PLAN] Delete .tmmignore and .ignore` — both files will be deleted
- `[PLAN] Delete .tmmignore` — only `.tmmignore` will be deleted
- `[PLAN] Delete .ignore` — only `.ignore` will be deleted

After scanning, a summary is printed:

```text
=== Scan Summary ===
Scanned subdirectories: N
Planned deletions: N
No-op directories: N
```

If there is nothing to delete, the script exits. Otherwise it asks for confirmation:

```text
Confirm deletion? Type yes to continue:
```

Type `yes` to delete the marker files. Any other input cancels without making changes.

## Example (recommended order)

Given a library like:

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

1. Run `python add_ignore.py /media` and confirm with `yes`.  
   This creates marker files in first-level media subfolders, for example:
   - `/media/MovieA/Extras/.ignore`
   - `/media/MovieA/Extras/.tmmignore`
   - `/media/ShowA/S1/SPs/.ignore`
   - `/media/ShowA/S1/SPs/.tmmignore`
2. Run `python clean_subfolders.py /media`.  
   During scan, these marked folders are skipped (you will see `[SKIP] ... found .ignore, skip subtree`), so files in those protected trees are not deleted.
3. Run `python remove_ignore.py /media` and confirm with `yes`.  
   This removes marker files (`.ignore`, `.tmmignore`) from the same first-level media subfolders after cleanup.

## Notes

- Please back up your media library (or test on a sample directory) before running cleanup scripts.
- File extension matching is case-insensitive.
- `add_ignore.py` decision logic:
  1. Under `root`, each first-level folder is inspected.
  2. If that folder contains any `S<number>` directories:
     - each season dir (`S1`, `S2`, ...) is treated as a media base dir and the script scans its first-level child directories (`S1/*`) as creation targets;
     - each sibling non-season dir (for example `SPs`, `Extras`) is treated as a direct creation target (creates `.ignore`/`.tmmignore` in `ShowName/SPs` itself, not only in `ShowName/SPs/*`).
  3. If that folder contains no `S<number>` directories, it is treated as a movie base dir and the script scans its first-level child directories (`MovieName/*`) as creation targets.
   4. Any directory named `.actors` is always skipped (both “with seasons” and “without seasons” cases), so `.actors` is not treated as a creation target and no `.ignore`/`.tmmignore` files are created in it.
- `remove_ignore.py` uses the same first-level media traversal logic and only handles `.ignore` / `.tmmignore` marker files.
- `clean_subfolders.py` walks recursively and skips any subtree that contains `.ignore`.

## License

This project is licensed under the [MIT License](LICENSE).
