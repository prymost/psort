import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.metadata import get_media_date


def test_get_image_date_success():
    """Verify image EXIF date parsing."""
    # We patch Image.open to avoid needing a real .jpg file
    with patch("src.metadata.Image.open") as mock_open:
        mock_img = MagicMock()

        # Use getexif() to match the new implementation
        mock_img.getexif.return_value = {0x9003: "2024:09:02 12:23:39"}
        mock_open.return_value.__enter__.return_value = mock_img
        # We patch mimetypes so the code thinks this is definitely an image
        with patch("mimetypes.guess_type", return_value=("image/jpeg", None)):
            path = Path("test.jpg")
            result = get_media_date(path)

            assert result == datetime.datetime(2024, 9, 2, 12, 23, 39)


def test_get_video_date_success():
    """Verify video metadata extraction."""
    fixed_date = datetime.datetime(2024, 1, 1, 10, 0, 0)

    with (
        patch("src.metadata.createParser") as mock_parser,
        patch("src.metadata.extractMetadata") as mock_extract,
    ):

        # Setup Hachoir mocks
        mock_meta = MagicMock()
        mock_meta.get.return_value = fixed_date
        mock_extract.return_value = mock_meta

        # Ensure createParser returns something "truthy" so the check passes
        mock_parser.return_value = MagicMock()

        # We patch mimetypes so the code thinks this is a video
        with patch("mimetypes.guess_type", return_value=("video/mp4", None)):
            result = get_media_date(Path("test.mp4"))
            assert result == fixed_date


def test_fallback_to_mtime():
    """Verify fallback to file system date when metadata is missing."""
    with (
        patch("src.metadata.Image.open") as mock_open,
        patch("src.metadata.Path.stat") as mock_stat,
    ):

        # Scenario: Image exists but returns None for getexif() (no metadata)
        mock_img = MagicMock()
        mock_img.getexif.return_value = None
        mock_open.return_value.__enter__.return_value = mock_img

        # Mock filesystem mtime (1700000000.0 is roughly Nov 2023)
        mock_stat.return_value.st_mtime = 1700000000.0

        # Force it to be treated as an image first
        with patch("mimetypes.guess_type", return_value=("image/jpeg", None)):
            result = get_media_date(Path("no_exif.jpg"))

            # 1700000000 timestamp = 2023-11-14 ...
            assert result.year == 2023
            assert result.month == 11
