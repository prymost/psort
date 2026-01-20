import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from src.main import main, parse_args


def test_parse_args():
    """Verify CLI arguments are parsed correctly."""
    # Simulate: program -s /src -d /dest --dry-run
    test_args = [
        "prog",
        "--source",
        "/src",
        "--destination",
        "/dest",
        "--dry-run",
        "--mode",
        "move",
    ]
    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert args.source == Path("/src")
        assert args.destination == Path("/dest")
        assert args.dry_run is True
        assert args.mode == "move"


def create_test_image(path: Path, date_str: str):
    """Helper to create a valid JPEG with specific EXIF DateTimeOriginal."""
    # 1. Create a simple red square image
    img = Image.new("RGB", (100, 100), color="red")

    # 2. Get the EXIF object
    exif = img.getexif()

    # 3. Set DateTimeOriginal (0x9003)
    # Format must be "YYYY:MM:DD HH:MM:SS"
    exif[0x9003] = date_str

    # 4. Save with metadata
    img.save(path, "JPEG", exif=exif)


def test_e2e_real_files_copy(tmp_path, capsys):
    """
    Generates a REAL image with REAL EXIF data.
    Runs the full application stack without logic mocks.
    """
    # 1. Setup Filesystem
    source = tmp_path / "source"
    source.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    # 2. Create a real JPEG with a known date (May 4th, 2025)
    date_str = "2025:05:04 15:30:00"
    src_file = source / "holiday.jpg"
    create_test_image(src_file, date_str)

    # 3. Run Main (Copy Mode)
    cli_args = ["prog", "-s", str(source), "-d", str(dest), "--mode", "copy"]

    with patch("sys.argv", cli_args):
        main()

    # 4. Verify Results

    # A. Check stdout
    captured = capsys.readouterr()
    assert "Processing complete" in captured.out

    # B. Verify Destination Structure: Dest / 2025 / 05
    target_dir = dest / "2025" / "05"
    assert target_dir.exists()

    # C. Find the processed file
    found_files = list(target_dir.glob("04May2025_1530*.jpg"))
    assert len(found_files) == 1

    # D. Verify source still exists (Copy mode)
    assert src_file.exists()


def test_e2e_real_files_move(tmp_path, capsys):
    """
    Verifies that the source file is deleted after processing.
    """
    source = tmp_path / "source"
    source.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    date_str = "2025:05:04 15:30:00"
    src_file = source / "move_me.jpg"
    create_test_image(src_file, date_str)

    # Run Main with --mode move
    cli_args = ["prog", "-s", str(source), "-d", str(dest), "--mode", "move"]

    with patch("sys.argv", cli_args):
        main()

    # Verify Results
    captured = capsys.readouterr()
    assert "Processing complete" in captured.out

    # Verify Destination
    target_dir = dest / "2025" / "05"
    found_files = list(target_dir.glob("04May2025_1530*.jpg"))
    assert len(found_files) == 1

    # Verify Source is GONE
    assert not src_file.exists()


def test_e2e_dry_run(tmp_path, capsys):
    """
    True E2E test (Dry Run):
    Verifies that NO changes are made to the filesystem.
    """
    source = tmp_path / "source"
    source.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    date_str = "2025:05:04 15:30:00"
    src_file = source / "dry_run.jpg"
    create_test_image(src_file, date_str)

    # Run Main with --dry-run (with mode=move)
    cli_args = [
        "prog",
        "-s",
        str(source),
        "-d",
        str(dest),
        "--mode",
        "move",
        "--dry-run",
    ]

    with patch("sys.argv", cli_args):
        main()

    # Verify Results
    captured = capsys.readouterr()
    assert "Processing complete" in captured.out

    # Verify Destination is EMPTY (no subfolders created)
    # The logs might mention creating folders, but pathlib.glob should find nothing
    # Actually, processor checks date then creates dir.
    # But in dry run, _perform_action returns early.
    # However, process_single_file calls get_media_date.

    # Check if dest has any files
    assert len(list(dest.rglob("*"))) == 0

    # Verify Source still EXISTS
    assert src_file.exists()


def test_main_missing_source(tmp_path, capsys):
    """Verify main exits gracefully if source doesn't exist."""
    bad_source = tmp_path / "non_existent"
    dest = tmp_path / "dest"

    with patch("sys.argv", ["prog", "-s", str(bad_source), "-d", str(dest)]):
        with pytest.raises(SystemExit) as excinfo:
            main()

        assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "does not exist" in captured.out
