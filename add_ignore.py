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


def collect_creation_targets(root_dir: str):
    targets = []
    scanned_subdirs = 0
    skipped_count = 0

    for base_dir in iter_media_base_dirs(root_dir):
        for current_dir, _, filenames in os.walk(base_dir):
            if current_dir == base_dir:
                continue

            scanned_subdirs += 1
            has_ignore = ".ignore" in filenames
            has_tmmignore = ".tmmignore" in filenames
            ignore_path = os.path.join(current_dir, ".ignore")
            tmmignore_path = os.path.join(current_dir, ".tmmignore")

            if not has_ignore:
                targets.append(ignore_path)
                print(f"[PLAN] Create: {ignore_path}")
            else:
                skipped_count += 1
            if not has_tmmignore:
                targets.append(tmmignore_path)
                print(f"[PLAN] Create: {tmmignore_path}")
            else:
                skipped_count += 1

    return targets, scanned_subdirs, skipped_count


def apply_creation(targets):
    created_count = 0
    error_count = 0

    for path in targets:
        try:
            with open(path, "w", encoding="utf-8"):
                pass
            created_count += 1
            print(f"[CREATED] {path}")
        except OSError as e:
            error_count += 1
            print(f"[ERROR] Failed to create: {path} ({e})")

    return created_count, error_count


def add_ignore_and_tmmignore(root_dir: str):
    targets, scanned_subdirs, skipped_count = collect_creation_targets(root_dir)

    print("\n=== Scan Summary ===")
    print(f"Scanned subdirectories: {scanned_subdirs}")
    print(f"Planned creations: {len(targets)}")
    print(f"Skipped (already existed): {skipped_count}")

    if not targets:
        print("\nNothing to create.")
        return

    confirm = input("\nConfirm creation? Type yes to continue: ").strip().lower()
    if confirm != "yes":
        print("Canceled. No files were created.")
        return

    print("\nCreating files...")
    created_count, error_count = apply_creation(targets)

    print("\nDone.")
    print(f"Created: {created_count}")
    print(f"Skipped (already existed): {skipped_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Plan and create .ignore/.tmmignore in media subfolders: supports "
            "Root/MovieName/ and Root/ShowName/S1 layouts"
        )
    )
    parser.add_argument("root_dir", help="Path to the media library root directory")
    args = parser.parse_args()

    add_ignore_and_tmmignore(args.root_dir)
