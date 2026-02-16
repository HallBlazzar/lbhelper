from pathlib import Path
from typing import List
from dataclasses import dataclass

import pytest


@dataclass
class ExpectedFile:
    file_path: Path
    content: List[str]


def check_generated_files_expected(subtests, iso_build_dir: Path, expected_files: List[ExpectedFile], logger):
    expected_files_with_full_path = __convert_expected_files_path_to_full_path(
        iso_build_dir=iso_build_dir, expected_files=expected_files)

    if not __check_files_exist_with_expected_content(
            subtests=subtests, expected_files=expected_files_with_full_path, logger=logger):
        pytest.fail("not all expected files exist")

    __check_no_unexpected_files(
        iso_build_dir=iso_build_dir, expected_files=expected_files_with_full_path)


def __convert_expected_files_path_to_full_path(iso_build_dir: Path, expected_files: List[ExpectedFile]) -> List[ExpectedFile]:
    expected_files_with_full_path = []
    for expected_file in expected_files:
        expected_file_with_full_path = expected_file
        expected_file_with_full_path.file_path = iso_build_dir / expected_file_with_full_path.file_path
        expected_files_with_full_path.append(expected_file_with_full_path)

    return expected_files_with_full_path


def __check_files_exist_with_expected_content(subtests, expected_files: List[ExpectedFile], logger):
    result = True
    for expected_file in expected_files:
        if not __check_single_file_content_valid(subtests, expected_file, logger):
            result = False

    return result


def __check_single_file_content_valid(subtests, expected_file: ExpectedFile, logger):
    with subtests.test(msg=f"validate file {expected_file.file_path}"):
        if not expected_file.file_path.exists():
            logger.error(f"File {expected_file.file_path} does not exist")
            return False

        if expected_file.file_path.is_dir():
            logger.info(f"File {expected_file.file_path} is a directory. Skip content checking.")
        else:
            with open(expected_file.file_path, "r") as f:
                lines = f.readlines()
                if not lines == expected_file.content:
                    logger.error(f"Expected {expected_file.content} but got {lines}")
                    return False

        return True


def __check_no_unexpected_files(iso_build_dir: Path, expected_files: List[ExpectedFile]):
    collected_files = iso_build_dir.rglob("*")

    unexpected_files = []

    for collected_file in collected_files:
        if not __check_single_file_expected(
            collected_file=collected_file, expected_files=expected_files
        ):
            unexpected_files.append(collected_file)

    assert len(unexpected_files) == 0, f"unexpected files {unexpected_files}"

def __check_single_file_expected(collected_file: Path, expected_files: List[ExpectedFile]) -> bool:
    for expected_file in expected_files:
        if (collected_file.samefile(expected_file.file_path) or
                (collected_file.is_dir() and
                 collected_file in expected_file.file_path.parents)):
            return True


    return False
