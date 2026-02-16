from dataclasses import dataclass
from typing import List

import pytest

from lbhelper import CustomDeb
from lbhelper.defaults import CHROOT_DEB_DIR
from lbhelper.target_writer import CustomDebWriter
from tests.validate_files import check_generated_files_expected, ExpectedFile


@dataclass
class CustomDebTestData:
    debs: List[CustomDeb]
    expected_files: List[ExpectedFile]


target_sub_dir =  CHROOT_DEB_DIR

@pytest.fixture
def generate_test_data(generate_test_files):
    test_data = CustomDebTestData(
        debs=[],
        expected_files=[],
    )

    def _generate_test_data(contents: List[List[str]]):
        test_files = generate_test_files(contents=contents)

        for i, test_file in enumerate(test_files):
            # lambda value is decided during execution time but definition time
            # see https://stackoverflow.com/questions/63123011/lambda-functions-created-in-a-for-loop-being-overwritten
            test_data.debs.append(CustomDeb(get_deb=lambda path=test_file: path))
            test_data.expected_files.append(ExpectedFile(
                file_path=target_sub_dir / test_file.name,
                content=contents[i]
            ))

        return test_data

    yield _generate_test_data


def success_run_test_data():
    # each element represents file content(list of strings for multiple lines) of a deb
    return [
        pytest.param(
            [
                ["deb1\n",]
            ], id="single deb"
        ),
        pytest.param(
            [
                # deb file 1 content
                ["deb1\n",],
                # deb file 2 content
                ["deb2\n",]
            ], id="multiple debs"),
    ]


@pytest.mark.parametrize("test_data", success_run_test_data())
def test_success_run(test_data, generate_test_data, test_iso_build_dir, subtests, logger):
    # Arrange
    full_test_data = generate_test_data(contents=test_data)
    logger.info(f"Generated custom debs files: {[deb.get_deb() for deb in full_test_data.debs]}")
    logger.info(f"Expected custom debs files: {full_test_data.expected_files}")

    # Act
    CustomDebWriter(iso_build_dir=test_iso_build_dir).execute(full_test_data.debs)

    # Assert
    check_generated_files_expected(
        subtests=subtests,
        iso_build_dir=test_iso_build_dir,
        expected_files=full_test_data.expected_files,
        logger=logger,
    )
