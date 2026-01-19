import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.metadata import get_media_date
from src.utils import calculate_sha256, generate_target_filename


@dataclass(frozen=True)
class SyncConfig:
    """Immutable configuration for the sync process."""

    source_dir: Path
    dest_dir: Path
    mode: str = "copy"
    dry_run: bool = False
    duplicates_dir: Optional[Path] = None

    valid_extensions: frozenset = frozenset(
        {".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi", ".mkv"}
    )


def process_media(config: SyncConfig):
    """Main entry point to scan and process files."""
    logging.info(f"Starting processing: {config.source_dir} -> {config.dest_dir}")
    logging.info(f"Mode: {config.mode}, Dry Run: {config.dry_run}")

    if not config.source_dir.exists():
        logging.error(f"Source directory not found: {config.source_dir}")
        return

    # Recursive scan
    for file_path in config.source_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in config.valid_extensions:
            process_single_file(file_path, config)


def process_single_file(source_path: Path, config: SyncConfig):
    try:
        # 1. Extract Date
        date_taken = get_media_date(source_path)

        # 2. Determine Destination Path: Dest / YYYY / MM
        year_folder = date_taken.strftime("%Y")
        month_folder = date_taken.strftime("%m")
        target_dir = config.dest_dir / year_folder / month_folder

        # 3. Generate Filename
        target_filename = generate_target_filename(source_path, date_taken)
        target_path = target_dir / target_filename

        # 4. Handle Conflicts (Target already exists)
        final_target_path = resolve_conflict(source_path, target_path, config)

        if not final_target_path:
            # File was determined to be a duplicate
            return

        # 5. Perform Action (Copy/Move)
        perform_action(source_path, final_target_path, config)

    except Exception as e:
        logging.error(f"Failed to process {source_path}: {e}")


def resolve_conflict(
    source_path: Path, target_path: Path, config: SyncConfig
) -> Optional[Path]:
    """
    Checks if target exists.
    Returns None if duplicate is handled (skipped/moved).
    Returns Path where the file should be saved if content is different.
    """
    if not target_path.exists():
        return target_path

    # Conflict detected! Check hashes.
    logging.info(f"Conflict detected for {target_path.name}. Checking hashes...")

    source_hash = calculate_sha256(source_path)
    target_hash = calculate_sha256(target_path)

    if source_hash == target_hash:
        logging.info("Files are identical.")
        handle_identical_duplicate(source_path, config)
        return None

    # Content is different: Rename source file to keep both
    logging.info("Files have same name but different content. Renaming...")
    short_hash = source_hash[:4]
    new_name = f"{target_path.stem}_{short_hash}{target_path.suffix}"
    return target_path.parent / new_name


def handle_identical_duplicate(source_path: Path, config: SyncConfig):
    """Dispatches duplicate handling logic based on mode."""
    if config.mode == "copy":
        logging.info(f"Skipping duplicate: {source_path}")
    elif config.mode == "move":
        handle_duplicate_move(source_path, config)


def handle_duplicate_move(source_path: Path, config: SyncConfig):
    """Decides whether to move duplicate to specific folder or delete it."""
    if config.duplicates_dir:
        move_to_duplicates(source_path, config.duplicates_dir, config.dry_run)
    else:
        delete_source(source_path, config.dry_run)


def move_to_duplicates(source_path: Path, target_dir: Path, dry_run: bool):
    """Moves source file to the duplicates directory."""
    if dry_run:
        logging.info(f"[DRY RUN] Would move duplicate to {target_dir}")
        return

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / source_path.name
        logging.info(f"Moving duplicate to {dest}")
        shutil.move(source_path, dest)
    except Exception as e:
        logging.error(f"Failed to move duplicate {source_path}: {e}")


def delete_source(source_path: Path, dry_run: bool):
    """Deletes the source file (used when no duplicates dir is provided)."""
    logging.warning(
        "Duplicate detected but no duplicates_dir set. "
        f"Deleting source {source_path}"
    )
    if not dry_run:
        try:
            source_path.unlink()
        except Exception as e:
            logging.error(f"Failed to delete {source_path}: {e}")


def perform_action(source: Path, dest: Path, config: SyncConfig):
    if config.dry_run:
        logging.info(f"[DRY RUN] {config.mode.upper()} {source} -> {dest}")
        return

    # Ensure parent dir exists
    dest.parent.mkdir(parents=True, exist_ok=True)

    if config.mode == "copy":
        shutil.copy2(source, dest)
        logging.info(f"Copied to {dest}")
    elif config.mode == "move":
        shutil.move(source, dest)
        logging.info(f"Moved to {dest}")
