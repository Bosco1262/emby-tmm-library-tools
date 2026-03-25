# emby-tmm-library-tools

Utility Python scripts to clean and maintain tinyMediaManager files for Emby media libraries.

中文文档请见：[README.zh-CN.md](README.zh-CN.md)

## Features

This repository currently includes scripts to:

1. Add `.ignore` and `.tmmignore`:
   - in first-level subfolders under movie bases (`MovieName/*`)
   - in first-level subfolders under show/season bases (`ShowName/S1/*`) and directly in season-layout sibling non-season dirs (`ShowName/Extra`, `ShowName/SPs`, etc.)
2. In subfolders **without** `.ignore`:
   - Delete `.png`, `.jpg` files (and optionally `.nfo` files)
   - Delete `.actors` directory if it exists

## Scripts

- `add_ignore.py`  
  Scans first-level media directories under the root.  
  Supports two structures:
  - `Root/MovieName/*`
  - `Root/ShowName/S1/*` (and other `S<number>` seasons), plus sibling non-season directories when seasons exist (for example `Root/ShowName/Extra`)  
  First performs a scan and prints all planned file creations, then asks for confirmation.  
  After you type `yes`, it creates missing `.ignore` and `.tmmignore` files in target directories.

- `clean_subfolders.py`  
  Scans all subfolders under a root directory.  
  For subfolders without `.ignore`, deletes image files (`.png`, `.jpg`) and optionally `.nfo` files (you are prompted at startup), and removes `.actors` directory.

## Requirements

- Python 3.8+ (recommended)

## Usage

### 1) Add `.ignore` and `.tmmignore` to media subfolders (scan + confirm)

```bash
python add_ignore.py /path/to/your/library
```

The script first asks:

```text
请选择输出语言 / Please choose output language [zh/en] (default zh):
```

> Recommended order: run this script first, then run `clean_subfolders.py`, to avoid unnecessary file loss in folders that should be protected.

### 2) Clean folders without `.ignore`

```bash
python clean_subfolders.py /path/to/your/library
```

The script will first ask:

```text
请选择输出语言 / Please choose output language [zh/en] (default zh):
```

Then it asks:

```
Delete .nfo files? [y/N]:
```

- Enter `y` or `yes` to include `.nfo` files in the deletion.
- Press Enter (or type anything else) to skip `.nfo` files (default, safe choice).

Then it scans and prints planned deletions directory-by-directory (shows current path first, then filenames to be deleted under that path), and asks for a final `yes` confirmation before making any changes.

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
- `clean_subfolders.py` walks recursively and skips any subtree that contains `.ignore`.

## License

This project is licensed under the [MIT License](LICENSE).
