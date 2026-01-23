import pathlib
import tomllib


def test_python_version_consistency():
    """
    Ensure the python version in .python-version
    matches the constraint in pyproject.toml
    """
    root_dir = pathlib.Path(__file__).parent.parent

    # Read .python-version
    python_version_file = root_dir / ".python-version"
    assert python_version_file.exists(), ".python-version file is missing"
    target_version = python_version_file.read_text().strip()

    # Read pyproject.toml
    pyproject_file = root_dir / "pyproject.toml"
    assert pyproject_file.exists(), "pyproject.toml file is missing"

    with open(pyproject_file, "rb") as f:
        pyproject_data = tomllib.load(f)

    requires_python = pyproject_data.get("project", {}).get("requires-python")
    if not requires_python:
        # Fallback to poetry legacy location if not in [project]
        requires_python = (
            pyproject_data.get("tool", {})
            .get("poetry", {})
            .get("dependencies", {})
            .get("python")
        )

    assert requires_python, "Could not find requires-python in pyproject.toml"

    # Simple string check for now
    # assuming standard format like ">=3.14,<3.15" or "^3.14"
    # We want to ensure our target version (e.g. 3.14) is the base of the requirement

    # Check if the target version is explicitly mentioned or compatible
    # For >=3.14,<3.15, 3.14 is the lower bound.

    assert (
        target_version in requires_python
    ), f"Target version {target_version} not found in requirement {requires_python}"

    # Check Dockerfile
    dockerfile_path = root_dir / ".devcontainer" / "Dockerfile"
    if dockerfile_path.exists():
        dockerfile_content = dockerfile_path.read_text()
        expected_image = f"python:{target_version}"
        assert (
            expected_image in dockerfile_content
        ), f"Dockerfile should use {expected_image}"
