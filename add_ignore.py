import argparse
import os
import re


SEASON_DIR_PATTERN = re.compile(r"^S\d+$", re.IGNORECASE)


def iter_media_base_dirs(root_dir: str):
    for entry in os.scandir(root_dir):
        if not entry.is_dir():
            continue

        has_season_dirs = False
        for child in os.scandir(entry.path):
            if child.is_dir() and SEASON_DIR_PATTERN.match(child.name):
                has_season_dirs = True
                yield child.path

        if not has_season_dirs:
            yield entry.path


def add_ignore_to_subdirs(root_dir: str):
    created_count = 0
    skipped_count = 0
    error_count = 0

    for base_dir in iter_media_base_dirs(root_dir):
        for current_dir, _, filenames in os.walk(base_dir):
            if current_dir == base_dir:
                continue

            ignore_path = os.path.join(current_dir, ".ignore")
            if ".ignore" in filenames:
                skipped_count += 1
                print(f"[SKIPPED] Already exists: {ignore_path}")
                continue

            try:
                with open(ignore_path, "w", encoding="utf-8"):
                    pass
                created_count += 1
                print(f"[CREATED] {ignore_path}")
            except OSError as e:
                error_count += 1
                print(f"[ERROR] Failed to create: {ignore_path} ({e})")

    print("\nDone.")
    print(f"Created: {created_count}")
    print(f"Skipped (already existed): {skipped_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Create .ignore in media subfolders: supports "
            "Root/MovieName/ and Root/ShowName/S1 layouts"
        )
    )
    parser.add_argument("root_dir", help="Path to the media library root directory")
    args = parser.parse_args()

    add_ignore_to_subdirs(args.root_dir)
