from dataclasses import dataclass
from typing import List

import pytest

from lbhelper import DirectConfig
from lbhelper.target_writer import DirectConfigWriter
from tests.validate_files import check_generated_files_expected, ExpectedFile


@dataclass
class DirectConfigTestData:
    targets: List[DirectConfig]
    expected_files: List[ExpectedFile]


@pytest.fixture()
def generate_files_only_test_data(generate_test_files):
    test_data = DirectConfigTestData(
        targets=[],
        expected_files=[],
    )

    def _generate_test_data(contents: List[List[str]]):
        test_files = generate_test_files(contents=contents)

        for i, test_file in enumerate(test_files):
            # lambda value is decided during execution time but definition time
            # see https://stackoverflow.com/questions/63123011/lambda-functions-created-in-a-for-loop-being-overwritten
            test_data.targets.append(
                DirectConfig(
                    get_source_file=lambda path=test_file: path,
                    target_filepath=test_file,
                )
            )

            test_data.expected_files.append(ExpectedFile(
                file_path=test_file.relative_to(test_file.anchor),
                content=contents[i]
            ))


        return test_data


    yield _generate_test_data


def success_run_test_data():
    test_data = [
        pytest.param(
        [
            ["file1\n", ]
        ], id=f"single file"
    ), pytest.param(
        [
            # hook file 1 content
            ["file1\n", ],
            # hook file 2 content
            ["file2\n", ]
        ], id=f"multiple files"
    )]

    return test_data


@pytest.mark.parametrize("contents", success_run_test_data())
def test_success_run(generate_files_only_test_data, contents, test_iso_build_dir, subtests, logger):
    # Arrange
    full_test_data = generate_files_only_test_data(contents=contents)

    # Act
    DirectConfigWriter(iso_build_dir=test_iso_build_dir).execute(full_test_data.targets)

    # Assert
    check_generated_files_expected(
        subtests=subtests,
        iso_build_dir=test_iso_build_dir,
        expected_files=full_test_data.expected_files,
        logger=logger,
    )


# For test data with both dirs and files based targets
# The way we create test data there is creating dir per test file.
# For n test files, we'll get a set of test data mixed with:
# - n test dirs which with 1 test files under them
# - n test files
@pytest.fixture(scope="function")
def generate_mixed_test_data(generate_files_only_test_data, generate_test_dir):
    test_data = DirectConfigTestData(
        targets=[],
        expected_files=[],
    )

    def _generate_mixed_test_data(contents: List[List[str]]):
        file_only_test_data = generate_files_only_test_data(contents=contents)

        for i, target in enumerate(file_only_test_data.targets):
            source_file_path = target.get_source_file()
            test_dir = generate_test_dir([[source_file_path]])

            # Add test dir
            test_data.targets.append(
                DirectConfig(
                    get_source_file=lambda path=test_dir: path,
                    target_filepath=test_dir,
                )
            )

            expected_test_dir_path = test_dir.relative_to(test_dir.anchor)

            # expected test dir path
            test_data.expected_files.append(ExpectedFile(
                file_path=expected_test_dir_path,
                content=[]
            ))
            # expected test file path
            test_data.expected_files.append(ExpectedFile(
                file_path=expected_test_dir_path / source_file_path.name,
                content=file_only_test_data.expected_files[i].content
            ))

            # Add test file
            test_data.targets.append(target)
            test_data.expected_files.append(file_only_test_data.expected_files[i])
        return test_data

    yield _generate_mixed_test_data


@pytest.mark.parametrize("contents", success_run_test_data())
def test_mixed_targets(generate_mixed_test_data, contents, test_iso_build_dir, subtests, logger):
    # Arrange
    full_test_data = generate_mixed_test_data(contents=contents)

    # Act
    DirectConfigWriter(iso_build_dir=test_iso_build_dir).execute(full_test_data.targets)

    # Assert
    check_generated_files_expected(
        subtests=subtests,
        iso_build_dir=test_iso_build_dir,
        expected_files=full_test_data.expected_files,
        logger=logger,
    )