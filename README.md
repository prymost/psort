# Media Sync

This is a personal script I wrote to help organize my photo and video collection. It's a Python migration of an [old PowerShell script](https://github.com/n2501r/spiderzebra/blob/master/PowerShell/Media_Sync.ps1) I used to use. I'm sharing it here in case anyone else finds it useful for their own library.

The code was generated with the help of AI and reviewed to ensure it works as intended.

## What it does

The script scans a source folder and organizes media into a structure like `Destination/YYYY/MM/`.

- **Sorting**: Uses EXIF data for photos and creation metadata for videos.
- **Duplicates**: If two files are identical (checked via SHA-256), it can skip them or move them to a separate folder.
- **Collisions**: If two different files have the same name, it appends a short hash to the filename so nothing is overwritten.
- **Safety**: Includes a `--dry-run` flag to see what would happen before any files are actually touched.

## 📦 Installation

This project is managed with [Poetry](https://python-poetry.org/).

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/sort_photos.git
    cd sort_photos
    ```

2.  **Install Dependencies:**
    ```bash
    poetry install
    ```

## 🏗️ Building as a standalone binary

If you want to run this tool on a machine without Python or Poetry installed, you can build it as a single executable file.

**Note:** PyInstaller builds a binary for the OS it is running on. Building in the Dev Container produces a Linux binary.

1.  **Build the binary:**
    ```bash
    ./scripts/build.sh
    ```
2.  **Run the binary:**
    ```bash
    ./dist/media-sync --help
    ```

## 🛠️ Usage

Run the script from the root directory using `src/main.py`.

### Basic examples

**Test without making changes:**
```bash
poetry run python src/main.py -s ./my_camera_dump -d ./my_photos --dry-run
```

**Copy and sort files:**
```bash
poetry run python src/main.py -s ./source -d ./destination
```

**Move files and store duplicates elsewhere:**
```bash
poetry run python src/main.py -s ./source -d ./destination --mode move --duplicates-dir ./duplicates
```

## Development

I've included a suite of tests to make sure the logic holds up.

```bash
# Run tests
poetry run pytest tests

# Check formatting
poetry run black .
poetry run flake8
```

## Structure

- `src/main.py`: Entry point and CLI arguments.
- `src/processor.py`: The logic for scanning and sorting.
- `src/metadata.py`: Reading dates from images and videos.
- `src/utils.py`: Hashing, naming, and logging helpers.

