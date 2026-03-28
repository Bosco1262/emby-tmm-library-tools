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
   - Delete `.png`, `.jpg` files (and optionally `theme.mp3` and `.nfo` files)
   - Delete `.actors` directory if it exists
   - Delete `.deletedByTMM` directory at root level if it exists
4. Recursively delete junk files across all subfolders under the root:
   - `.bif` files (matched by extension, case-insensitive)
   - `.DS_Store` and `Thumbs.db` (matched by exact name)

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
  At startup asks whether to also delete `theme.mp3` and/or `.nfo` files.  
  For subfolders without `.ignore`, it deletes image files (`.png`, `.jpg`) and any optional file types you selected, and removes `.actors` directories. At root level, the `.deletedByTMM` directory is planned for deletion as a whole if present.

- `remove_ignore.py`  
  Uses the same media traversal logic as `add_ignore.py`.  
  Uses a scan + confirm workflow.  
  It plans and deletes existing `.ignore`/`.tmmignore` in target first-level media subfolders.

- `clean_junk.py`  
  Recursively scans all directories under each top-level entry in the root.  
  Uses a scan + confirm workflow.  
  Deletes `.bif` files (by extension, case-insensitive), `.DS_Store`, and `Thumbs.db` wherever they are found.  
  Plan output is grouped per top-level media entry and displayed as a tree.

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
- `[SKIP] Skip .deletedByTMM directory` — `.deletedByTMM` directories at root level are always skipped
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

Then it asks whether to delete `theme.mp3` files:

```text
Delete theme.mp3 files? [y/N]:
```

- Enter `y` or `yes` to include `theme.mp3` in the deletion.
- Press Enter (or type anything else) to skip `theme.mp3` files (default, safe choice).

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

At the root level, if a `.deletedByTMM` directory exists it is planned for deletion as a whole (shown as a `[PLAN]` entry under the root).

After scanning, a summary is printed:

```text
=== Summary ===
Scanned subdirectories: N
Files planned for deletion (.jpg/.png): N
Directories planned for deletion: N
Skipped directory trees with .ignore: N
```

The file-type label in the summary reflects your selections: for example `(.jpg/.png/theme.mp3/.nfo)` if all optional types are enabled, or just `(.jpg/.png)` by default.

If nothing needs to be deleted, the script exits. Otherwise it asks for confirmation:

```text
Confirm deletion? Type yes to continue:
```

Type `yes` to delete the planned image files (`.png`, `.jpg`, and any optional types you selected), `.actors` directories, and the `.deletedByTMM` root directory if present. Any other input cancels without making changes.

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

### 4) `clean_junk.py` — Recursively delete junk files (`.bif`, `.DS_Store`, `Thumbs.db`)

```bash
python clean_junk.py /path/to/your/library
```

The script first asks for output language:

```text
请选择输出语言 / Please choose output language [zh/en] (default zh):
```

It then recursively walks every directory inside each top-level entry and prints a planned deletion tree grouped by media root. Junk found directly inside a top-level entry directory is shown on the header line; junk found in deeper subdirectories is shown as a tree. Each entry is labeled with one of:

- `[NOOP] No junk files found in this entry` — no junk files found anywhere in this entry
- `MediaDir/ [PLAN] Delete <files>` — junk found directly in the top-level entry dir
- `└── subdir/ [PLAN] Delete <files>` — junk found in a subdirectory

After scanning, a summary is printed:

```text
=== Scan Summary ===
Scanned directories: N
Planned file deletions: N
Top-level entries with no junk: N
```

If there is nothing to delete, the script exits. Otherwise it asks for confirmation:

```text
Confirm deletion? Type yes to continue:
```

Type `yes` to delete all planned junk files. Any other input cancels without making changes.

**Matching rules:**
- `.bif` — matched by file extension, **case-insensitive** (e.g. `chapter00.bif`, `intro.BIF`)
- `.DS_Store` — matched by exact filename
- `Thumbs.db` — matched by exact filename

## Example (recommended order)

Given a library like:

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

**Step 1** — Run `python add_ignore.py /media` and confirm with `yes`.

The script scans first-level media subfolders and prints a creation plan:

```text
.deletedByTMM/ [SKIP] Skip .deletedByTMM directory

MovieA/
├── .actors/  [SKIP] Skip .actors directory
└── Extras/   [PLAN] Both missing, create .ignore and .tmmignore

ShowA/
├── S1/
│   ├── Featurettes/ [PLAN] Both missing, create .ignore and .tmmignore
│   └── SPs/         [PLAN] Both missing, create .ignore and .tmmignore
└── Specials/        [PLAN] Both missing, create .ignore and .tmmignore

=== Scan Summary ===
Scanned subdirectories: 4
Planned creations: 8
Skipped (already existed): 0

Confirm creation? Type yes to continue: yes

Creating files...
[CREATED] /media/MovieA/Extras/.ignore
[CREATED] /media/MovieA/Extras/.tmmignore
[CREATED] /media/ShowA/S1/Featurettes/.ignore
[CREATED] /media/ShowA/S1/Featurettes/.tmmignore
[CREATED] /media/ShowA/S1/SPs/.ignore
[CREATED] /media/ShowA/S1/SPs/.tmmignore
[CREATED] /media/ShowA/Specials/.ignore
[CREATED] /media/ShowA/Specials/.tmmignore
```

- `.deletedByTMM` at root level is skipped — no marker files are created in it.
- `.actors` inside `MovieA` is also skipped.
- `Specials` is a non-season sibling of `S1`; it is treated as a direct creation target (marker files are created inside `ShowA/Specials` itself, not in its children).

**Step 2** — Run `python clean_subfolders.py /media`, answer `y` to delete `theme.mp3`, answer `N` for `.nfo`, then confirm with `yes`.

The script recursively walks all subdirectories. The root-level `.deletedByTMM` is planned for whole-directory deletion. Subfolders with `.ignore` are skipped entirely; others are cleaned:

```text
=== Scanning and planning deletion ===
[PLAN] /media
  Directories to delete:
    - .deletedByTMM/
[PLAN] /media/MovieA
  Files to delete:
    - poster.jpg
    - theme.mp3
  Directories to delete:
    - .actors/
[SKIP] /media/MovieA/Extras (found .ignore, skip subtree)
[NOOP] /media/ShowA
[NOOP] /media/ShowA/S1
[SKIP] /media/ShowA/S1/Featurettes (found .ignore, skip subtree)
[SKIP] /media/ShowA/S1/SPs (found .ignore, skip subtree)
[SKIP] /media/ShowA/Specials (found .ignore, skip subtree)

=== Summary ===
Scanned subdirectories: 7
Files planned for deletion (.jpg/.png/theme.mp3): 2
Directories planned for deletion: 2
Skipped directory trees with .ignore: 4

Confirm deletion? Type yes to continue: yes

Deleting...
[DELETED FILE] /media/MovieA/poster.jpg
[DELETED FILE] /media/MovieA/theme.mp3
[DELETED DIR] /media/.deletedByTMM
[DELETED DIR] /media/MovieA/.actors
```

Files inside `MovieA/Extras`, `ShowA/S1/Featurettes`, `ShowA/S1/SPs`, and `ShowA/Specials` are untouched because those subtrees are protected by `.ignore`.

**Step 3** — Run `python remove_ignore.py /media` and confirm with `yes`.

The script uses the same traversal logic as `add_ignore.py` and plans removal of all marker files:

```text
MovieA/
└── Extras/          [PLAN] Delete .tmmignore and .ignore

ShowA/
├── S1/
│   ├── Featurettes/ [PLAN] Delete .tmmignore and .ignore
│   └── SPs/         [PLAN] Delete .tmmignore and .ignore
└── Specials/        [PLAN] Delete .tmmignore and .ignore

=== Scan Summary ===
Scanned subdirectories: 4
Planned deletions: 8
No-op directories: 0

Confirm deletion? Type yes to continue: yes

Deleting files...
[DELETED] /media/MovieA/Extras/.tmmignore
[DELETED] /media/MovieA/Extras/.ignore
[DELETED] /media/ShowA/S1/Featurettes/.tmmignore
[DELETED] /media/ShowA/S1/Featurettes/.ignore
[DELETED] /media/ShowA/S1/SPs/.tmmignore
[DELETED] /media/ShowA/S1/SPs/.ignore
[DELETED] /media/ShowA/Specials/.tmmignore
[DELETED] /media/ShowA/Specials/.ignore
```

### `clean_junk.py` — standalone example

`clean_junk.py` is independent of the `.ignore` workflow and can be run at any time. It recurses into all subdirectories of each top-level entry, so it covers any nesting depth. Given a library like:

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
            ├── chapter01.bif
            ├── Thumbs.db
            └── Scenes
                └── clip.DS_Store
```

Run `python clean_junk.py /media`:

```text
MovieA/ [PLAN] Delete .DS_Store
└── Bonus/
    └── Behind the Scenes/ [PLAN] Delete Thumbs.db
        └── Interviews/    [PLAN] Delete intro.BIF

ShowB/
└── S2/
    └── Extras/ [PLAN] Delete Thumbs.db, chapter00.bif, chapter01.bif

=== Scan Summary ===
Scanned directories: 8
Planned file deletions: 6
Top-level entries with no junk: 0

Confirm deletion? Type yes to continue: yes

Deleting files...
[DELETED] /media/MovieA/.DS_Store
[DELETED] /media/MovieA/Bonus/Behind the Scenes/Thumbs.db
[DELETED] /media/MovieA/Bonus/Behind the Scenes/Interviews/intro.BIF
[DELETED] /media/ShowB/S2/Extras/Thumbs.db
[DELETED] /media/ShowB/S2/Extras/chapter00.bif
[DELETED] /media/ShowB/S2/Extras/chapter01.bif
```

Notes on the output above:

- **Multiple files in one directory**: `Extras/` has three junk files (`Thumbs.db`, `chapter00.bif`, `chapter01.bif`); they are all listed on one `[PLAN]` line and deleted together.
- **`clip.DS_Store` is not deleted**: the script matches `.DS_Store` by exact filename only. A file named `clip.DS_Store` has a different name and is left untouched. `Scenes/` does not appear in the plan at all because it contains no matching junk files.


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
  5. Any directory named `.deletedByTMM` directly under `root` is also always skipped — no marker files are created in it.
- `remove_ignore.py` uses the same first-level media traversal logic and only handles `.ignore` / `.tmmignore` marker files.
- `clean_subfolders.py` walks recursively and skips any subtree that contains `.ignore`. At root level, the `.deletedByTMM` directory (if present) is deleted as a whole rather than recursed into.
- `clean_junk.py` walks recursively across the entire subtree of each top-level entry. It matches `.bif` by file extension (case-insensitive) and `.DS_Store` / `Thumbs.db` by exact filename. It does not interact with `.ignore` files.

## License

This project is licensed under the [MIT License](LICENSE).
