from pathlib import Path
from typing import List

import pytest

from lbhelper.auto_scripts.auto_scripts import write_auto_script, AutoScriptType
from tests.validate_files import ExpectedFile, check_generated_files_expected
from importlib.resources import files


def get_expected_content(file_name: str) -> List[str]:
    expected_content_file = Path(str(files(__package__) / file_name))

    with open(expected_content_file, encoding="utf-8") as f:
        expected_content = f.readlines()

    return expected_content


def get_test_data():
    return [
        pytest.param(
            AutoScriptType.BUILD,
            {},
            ExpectedFile(
                file_path=Path("auto/build"),
                content=get_expected_content("build"),
                permission=0o755,
            ),
            id="build-script"
        ),
        pytest.param(
            AutoScriptType.CONFIG,
            {"distribution": "trixie", "image_name": "myos"},
            ExpectedFile(
                file_path=Path("auto/config"),
                content=get_expected_content("config"),
                permission=0o755,
            ),
            id="config-script"
        ),
        pytest.param(
            AutoScriptType.CLEAN,
            {},
            ExpectedFile(
                file_path=Path("auto/clean"),
                content=get_expected_content("clean"),
                permission=0o755,
            ),
            id="clean-script"
        )
    ]

@pytest.mark.parametrize("auto_script_type, extra_params, expected_file", get_test_data())
def test_write_auto_script(test_iso_build_dir, subtests, auto_script_type, expected_file, extra_params, logger):
    # Arrange, Act
    write_auto_script(
        iso_build_dir=test_iso_build_dir, script_type=auto_script_type, **extra_params)

    # Assert
    check_generated_files_expected(
        subtests=subtests, iso_build_dir=test_iso_build_dir,
        expected_files=[expected_file], logger=logger
    )
