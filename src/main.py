import argparse
import sys
from pathlib import Path

from src.processor import SyncConfig, process_media
from src.utils import setup_logging


def parse_args():
    parser = argparse.ArgumentParser(
        description="Organize photos and videos by date metadata."
    )

    parser.add_argument(
        "--source",
        "-s",
        type=Path,
        required=True,
        help="Source directory containing media files.",
    )

    parser.add_argument(
        "--destination",
        "-d",
        type=Path,
        required=True,
        help="Destination directory for organized media.",
    )

    parser.add_argument(
        "--mode",
        "-m",
        choices=["copy", "move"],
        default="copy",
        help="Operation mode: 'copy' (default) or 'move'.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the process without making changes.",
    )

    parser.add_argument(
        "--duplicates-dir",
        type=Path,
        help="Directory to move duplicates to (only used in 'move' mode).",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # 1. Setup Logging
    # We use the destination parent or current dir for logs if dest doesn't exist yet
    log_file = setup_logging(log_dir_name="sort_photos_logs")
    print(f"Log file created at: {log_file}")

    # 2. Validate Paths
    if not args.source.exists():
        print(f"Error: Source directory '{args.source}' does not exist.")
        sys.exit(1)

    # 3. Create Configuration
    config = SyncConfig(
        source_dir=args.source,
        dest_dir=args.destination,
        mode=args.mode,
        dry_run=args.dry_run,
        duplicates_dir=args.duplicates_dir,
    )

    # 4. Run Processor
    try:
        process_media(config)
        print("Processing complete. Check logs for details.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
