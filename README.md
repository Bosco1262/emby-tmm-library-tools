# emby-tmm-library-tools

Utility Python scripts to clean and maintain tinyMediaManager files for Emby media libraries.

## Features

This repository currently includes scripts to:

1. Add `.tmmignore` to subfolders that contain `.ignore`
2. Add `.ignore` to subfolders under media directories (`MovieName/*`, `ShowName/S1/*`)
2. In subfolders **without** `.ignore`:
   - Delete `.nfo`, `.png`, `.jpg` files
   - Delete `.actors` directory if it exists

## Scripts

- `add_tmmignore.py`  
  Scans all subfolders under a root directory.  
  If a subfolder contains `.ignore` and does not contain `.tmmignore`, it creates an empty `.tmmignore`.

- `add_ignore.py`  
  Scans first-level media directories under the root.  
  Supports two structures:
  - `Root/MovieName/*`
  - `Root/ShowName/S1/*` (and other `S<number>` seasons)  
  Creates an empty `.ignore` in subfolders where it does not already exist.

- `clean_subfolders.py`  
  Scans all subfolders under a root directory.  
  For subfolders without `.ignore`, deletes image files (`.png`, `.jpg`) and optionally `.nfo` files (you are prompted at startup), and removes `.actors` directory.

## Requirements

- Python 3.8+ (recommended)

## Usage

### 1) Add `.tmmignore`

```bash
python add_tmmignore.py /path/to/your/library
```

### 2) Add `.ignore` to media subfolders

```bash
python add_ignore.py /path/to/your/library
```

### 3) Clean folders without `.ignore`

```bash
python clean_subfolders.py /path/to/your/library
```

The script will first ask:

```
Delete .nfo files? [y/N]:
```

- Enter `y` or `yes` to include `.nfo` files in the deletion.
- Press Enter (or type anything else) to skip `.nfo` files (default, safe choice).

It then prints a dry-run preview of everything that would be deleted and asks for a final `yes` confirmation before making any changes.

## Notes

- Please back up your media library (or test on a sample directory) before running cleanup scripts.
- File extension matching is case-insensitive.
- Scripts process subfolders recursively.

## Suggested `.gitignore`

If needed, create a `.gitignore` file:

```gitignore
__pycache__/
*.pyc
.DS_Store
Thumbs.db
```

## License

MIT (recommended).  
You can add a `LICENSE` file to make usage terms explicit.
