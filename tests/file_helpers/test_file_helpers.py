from tempfile import NamedTemporaryFile

import pytest

from lbhelper import render_template_to_file, render_template_to_string
from lbhelper import escape_string_for_shell_script
from lbhelper import download_file
from pathlib import Path
from importlib.resources import files


@pytest.fixture
def temp_file(logger):
    try:
        with NamedTemporaryFile(mode="w+", delete=False) as tmp:
            yield tmp

    except Exception as e:
        logger.exception(f"Error occur for created temp file {tmp} {e}")

    finally:
        logger.exception(f"Remove temp file {tmp}")
        Path(tmp.name).unlink(missing_ok=True)


@pytest.fixture
def validate_file_with_cleanup(logger):
    def _validate_file_with_cleanup(file_path: Path, content: str):
        try:
            # Assert
            assert file_path.exists()

            with open(file_path, "r") as f:
                assert f.read() == content

        except Exception as e:
            logger.exception(f"Error occur while validating file {file_path}: {e}")

        finally:
            logger.exception(f"Remove file {file_path}")
            file_path.unlink()

    yield _validate_file_with_cleanup

def test_render_template_to_specific_file(temp_file, validate_file_with_cleanup):
    # Arrange
    template = Path(str(files(__package__) / "template.j2"))
    content = "some content"

    # Act
    rendered_template = render_template_to_file(
        template_path=template,
        target_path=Path(temp_file.name),
        content=content,
    )

    # Assert
    validate_file_with_cleanup(rendered_template, content)


def test_render_template_to_temp_file(validate_file_with_cleanup):
    # Arrange
    template = Path(str(files(__package__) / "template.j2"))
    content = "some content"

    # Act
    rendered_template = render_template_to_file(
        template_path=template,
        content=content,
    )

    # Assert
    validate_file_with_cleanup(rendered_template, content)


def test_render_template_to_string():
    # Arrange
    template = Path(str(files(__package__) / "template.j2"))
    content = "some content"

    # Act
    rendered_template = render_template_to_string(template_path=template, content=content)

    # Assert
    assert rendered_template == content


def test_escape_string_for_shell_script():
    # Arrange
    source_string = """
    #!/bin/bash
    
    cat >/some/file <EOL
    echo $SOME_ENV
    echo \\
    EOL
    """

    expected_string = """
    #!/bin/bash
    
    cat >/some/file <EOL
    echo \\$SOME_ENV
    echo \\\\
    EOL
    """

    # Act
    escaped = escape_string_for_shell_script(source_string)

    # Assert
    assert escaped == expected_string


def test_download_file(httpserver, validate_file_with_cleanup):
    # Arrange
    expected_content = "some content"
    httpserver.serve_content(
        content=expected_content,
        code=200,
    )

    # Act
    file_path = download_file(httpserver.url)

    # Assert
    validate_file_with_cleanup(file_path, expected_content)
