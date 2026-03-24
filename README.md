# emby-tmm-library-tools

Utility Python scripts to clean and maintain tinyMediaManager files for Emby media libraries.

## Features

This repository currently includes scripts to:

1. Add `.tmmignore` to subfolders that contain `.ignore`
2. In subfolders **without** `.ignore`:
   - Delete `.nfo`, `.png`, `.jpg` files
   - Delete `.actors` directory if it exists

## Scripts

- `add_tmmignore.py`  
  Scans all subfolders under a root directory.  
  If a subfolder contains `.ignore` and does not contain `.tmmignore`, it creates an empty `.tmmignore`.

- `clean_subfolders.py`  
  Scans all subfolders under a root directory.  
  For subfolders without `.ignore`, deletes metadata/image files (`.nfo`, `.png`, `.jpg`) and removes `.actors` directory.

## Requirements

- Python 3.8+ (recommended)

## Usage

### 1) Add `.tmmignore`

```bash
python add_tmmignore.py /path/to/your/library
```

### 2) Clean folders without `.ignore`

```bash
python clean_subfolders.py /path/to/your/library
```

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
