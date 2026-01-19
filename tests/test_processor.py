import datetime
from unittest.mock import patch

import pytest

from src.processor import SyncConfig, process_media


@pytest.fixture
def source_dir(tmp_path):
    d = tmp_path / "source"
    d.mkdir()
    return d


@pytest.fixture
def dest_dir(tmp_path):
    d = tmp_path / "dest"
    d.mkdir()
    return d


def test_process_simple_copy(source_dir, dest_dir):
    """Test basic copy functionality."""
    # 1. Create a dummy file
    src_file = source_dir / "photo.jpg"
    src_file.write_text("content")

    # 2. Mock metadata to return a fixed date
    fixed_date = datetime.datetime(2023, 10, 25, 12, 0, 0)

    with (
        patch("src.processor.get_media_date", return_value=fixed_date),
        patch("src.processor.generate_target_filename", return_value="final.jpg"),
    ):
        config = SyncConfig(source_dir=source_dir, dest_dir=dest_dir, mode="copy")
        process_media(config)

        # 3. Assertions
        expected_path = dest_dir / "2023" / "10" / "final.jpg"
        assert expected_path.exists()
        assert expected_path.read_text() == "content"
        # Source should still exist (Copy mode)
        assert src_file.exists()


def test_process_simple_move(source_dir, dest_dir):
    """Test basic move functionality."""
    src_file = source_dir / "video.mp4"
    src_file.write_text("video content")

    fixed_date = datetime.datetime(2023, 10, 25, 12, 0, 0)

    with (
        patch("src.processor.get_media_date", return_value=fixed_date),
        patch("src.processor.generate_target_filename", return_value="final.mp4"),
    ):
        config = SyncConfig(source_dir=source_dir, dest_dir=dest_dir, mode="move")
        process_media(config)

        expected_path = dest_dir / "2023" / "10" / "final.mp4"
        assert expected_path.exists()
        # Source should NOT exist (Move mode)
        assert not src_file.exists()


def test_duplicate_handling_identical(source_dir, dest_dir):
    """Test that identical files are skipped (in copy mode)."""
    # Create file in source
    src_file = source_dir / "photo.jpg"
    src_file.write_text("duplicate_content")

    # Create SAME file in destination (simulate previous run)
    target_dir = dest_dir / "2023" / "10"
    target_dir.mkdir(parents=True)
    target_file = target_dir / "final.jpg"
    target_file.write_text("duplicate_content")

    fixed_date = datetime.datetime(2023, 10, 25, 12, 0, 0)

    with (
        patch("src.processor.get_media_date", return_value=fixed_date),
        patch("src.processor.generate_target_filename", return_value="final.jpg"),
    ):
        config = SyncConfig(source_dir=source_dir, dest_dir=dest_dir, mode="copy")
        process_media(config)

        # Target should still be there
        assert target_file.exists()
        # Source should still be there
        assert src_file.exists()
        # No extra files created
        assert len(list(target_dir.glob("*"))) == 1


def test_duplicate_handling_different_content(source_dir, dest_dir):
    """Test that collision with different content creates a renamed copy."""
    # Source has "New Content"
    src_file = source_dir / "photo.jpg"
    src_file.write_text("New Content")

    # Destination has "Old Content" but same filename
    target_dir = dest_dir / "2023" / "10"
    target_dir.mkdir(parents=True)
    target_file = target_dir / "final.jpg"
    target_file.write_text("Old Content")

    fixed_date = datetime.datetime(2023, 10, 25, 12, 0, 0)

    with (
        patch("src.processor.get_media_date", return_value=fixed_date),
        patch("src.processor.generate_target_filename", return_value="final.jpg"),
        patch("src.processor.calculate_sha256") as mock_hash,
    ):

        # Mock hashes to be different
        mock_hash.side_effect = ["hash_new", "hash_old"]

        config = SyncConfig(source_dir=source_dir, dest_dir=dest_dir, mode="copy")
        process_media(config)

        # Original file stays
        assert target_file.read_text() == "Old Content"

        # New file should exist with hash suffix (hash_new -> 'hash')
        # name: final_hash.jpg
        expected_new = target_dir / "final_hash.jpg"
        assert expected_new.exists()
        assert expected_new.read_text() == "New Content"