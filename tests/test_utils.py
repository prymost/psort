import pytest
import logging
import datetime
import hashlib
from unittest.mock import patch
from src.utils import setup_logging, calculate_sha256, generate_target_filename


@pytest.fixture(autouse=True)
def reset_logging():
    """
    Reset logging configuration before and after each test.
    """
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()
    yield
    # Cleanup
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()


def test_setup_logging_defaults(tmp_path):
    """
    Test setup_logging with default arguments.
    """
    fixed_date = datetime.datetime(2023, 10, 27, 10, 30, 0)

    with (
        patch("src.utils.datetime") as mock_datetime,
        patch("src.utils.Path.mkdir") as mock_mkdir,
        patch("logging.FileHandler") as mock_file_handler,
    ):

        mock_datetime.datetime.now.return_value = fixed_date
        mock_instance = mock_file_handler.return_value
        mock_instance.level = logging.NOTSET

        # Execute
        log_file = setup_logging()

        # Assertions
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        expected_name = "psort_10-27-2023_103000.log"
        assert log_file.name == expected_name
        assert str(log_file.parent) == "/tmp/logs"

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 2
        assert any(h == mock_instance for h in root_logger.handlers)


def test_setup_logging_custom_paths(tmp_path):
    """
    Test setup_logging with custom arguments using a temporary directory.
    """
    custom_dir = tmp_path / "custom_logs"
    custom_prefix = "test_run"
    fixed_date = datetime.datetime(2025, 1, 1, 12, 0, 0)

    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = fixed_date

        # Execute
        log_file = setup_logging(
            log_dir_name=str(custom_dir), log_file_name_prefix=custom_prefix
        )

        # Assertions
        assert custom_dir.exists()
        assert log_file.exists()

        # Check content
        content = log_file.read_text()
        assert "Logging initialized" in content


def test_logging_formatter_config(tmp_path):
    """
    Verify that the formatter is correctly configured on the handlers.
    """
    log_dir = tmp_path / "logs"

    # Execute
    setup_logging(log_dir_name=str(log_dir))

    # Get the handlers attached to the root logger
    root_logger = logging.getLogger()
    handlers = root_logger.handlers

    # Verify we have handlers
    assert len(handlers) > 0

    # Check the formatter on the first handler (FileHandler or StreamHandler)
    formatter = handlers[0].formatter
    assert formatter is not None
    assert formatter._fmt is not None
    assert "%(asctime)s" in formatter._fmt
    assert "%(levelname)s" in formatter._fmt
    assert "%(message)s" in formatter._fmt


def test_calculate_sha256(tmp_path):
    """Test SHA256 calculation with a real temp file."""
    # "hello world" sha256:
    # b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
    content = b"hello world"
    test_file = tmp_path / "test_hash.txt"
    test_file.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest()
    result = calculate_sha256(test_file)

    assert result == expected_hash


def test_generate_target_filename(tmp_path):
    """Test filename generation logic."""
    test_file = tmp_path / "original.JPG"
    test_file.touch()

    # 1. Mock file size = 123456789 (last 5 digits: 56789)
    # 2. Date = Sep 02, 2024 12:30

    date_taken = datetime.datetime(2024, 9, 2, 12, 30, 0)

    with patch("src.utils.Path.stat") as mock_stat:
        mock_stat.return_value.st_size = 123456789

        # We pass the Path object directly,
        # but the patch applies to the class method
        # invoked inside the function
        filename = generate_target_filename(test_file, date_taken)

        # Expected: 02Sep2024_1230 + 56789 + .jpg
        assert filename == "02Sep2024_123056789.jpg"


def test_generate_target_filename_small_size(tmp_path):
    """Test filename generation with small file size (padded behavior?)."""
    test_file = tmp_path / "tiny.PNG"
    test_file.touch()

    date_taken = datetime.datetime(2024, 1, 1, 9, 5, 0)

    with patch("src.utils.Path.stat") as mock_stat:
        mock_stat.return_value.st_size = 42

        filename = generate_target_filename(test_file, date_taken)

        # Expected: 01Jan2024_0905 + 42 + .png
        assert filename == "01Jan2024_090542.png"
