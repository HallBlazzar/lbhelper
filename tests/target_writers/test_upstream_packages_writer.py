from typing import List

import pytest

from lbhelper import UpstreamPackages, PackagePriority
from lbhelper.defaults import PACKAGE_LIST_DIR
from lbhelper.target_writer import UpstreamPackagesWriter
from tests.validate_files import check_generated_files_expected, ExpectedFile
from dataclasses import dataclass


@dataclass
class UpstreamPackagesTestData:
    targets: List[UpstreamPackages]
    expected_files: List[ExpectedFile]


target_sub_dir = PACKAGE_LIST_DIR

def success_run_test_data():
    return [
        pytest.param(
            UpstreamPackagesTestData(
                targets=[
                    UpstreamPackages(
                        packages=[
                            "task-gnome-desktop",
                            "laptop"
                        ],
                        package_set_code="gnome-laptop-basic"
                    )
                ],
                expected_files=[
                    ExpectedFile(
                        file_path= target_sub_dir / "gnome-laptop-basic.list.chroot",
                        content=[
                            "task-gnome-desktop\n",
                            "laptop\n",
                        ]
                    )
                ]
            ),
            id="single package set"
        ),

        pytest.param(
            UpstreamPackagesTestData(
                targets=[
                    UpstreamPackages(
                        packages=[
                            "task-gnome-desktop",
                            "laptop",
                        ],
                        package_set_code="gnome-laptop-basic",
                    ),
                    UpstreamPackages(
                        packages=[
                            "vim",
                            "nano",
                        ],
                        package_set_code="editor",
                    ),
                ],
                expected_files=[
                    ExpectedFile(
                        file_path=target_sub_dir / "gnome-laptop-basic.list.chroot",
                        content=[
                            "task-gnome-desktop\n",
                            "laptop\n",
                        ]
                    ),
                    ExpectedFile(
                        file_path=target_sub_dir / "editor.list.chroot",
                        content=[
                            "vim\n",
                            "nano\n",
                        ]
                    )
                ]
            ),
            id="multiple package sets",
        )
    ]

@pytest.mark.parametrize("test_data", success_run_test_data())
def test_success_run(test_data, test_iso_build_dir, subtests, logger):
    # Act
    UpstreamPackagesWriter(iso_build_dir=test_iso_build_dir).execute(test_data.targets)

    # Assert
    check_generated_files_expected(
        subtests=subtests,
        iso_build_dir=test_iso_build_dir,
        expected_files=test_data.expected_files,
        logger=logger,
    )


def priority_test_data() -> List[UpstreamPackagesTestData]:
    test_data = []

    # NOTSET won't add priority to file
    # effective_priorities = list(PackagePriority)
    effective_priorities = [ member for member in PackagePriority ]
    effective_priorities.remove(PackagePriority.NOTSET)

    for priority in list(effective_priorities):
        test_data.append(
            pytest.param(
                UpstreamPackagesTestData(
                    targets=[
                        UpstreamPackages(
                            packages=[
                                "task-gnome-desktop",
                                "laptop"
                            ],
                            package_set_code="gnome-laptop-basic",
                            priority=priority,
                        ),
                    ],
                    expected_files=[
                        ExpectedFile(
                            file_path=target_sub_dir / "gnome-laptop-basic.list.chroot",
                            content=[
                                f"! Packages Priority {priority}\n",
                                "\n",
                                "task-gnome-desktop\n",
                                "laptop\n",
                            ]
                        )
                    ]
                ),
                id=f"priority {priority}"
            )
        )

    return test_data

@pytest.mark.parametrize("test_data", priority_test_data())
def test_priority(subtests, test_data, test_iso_build_dir, logger):
    # Act
    UpstreamPackagesWriter(iso_build_dir=test_iso_build_dir).execute(test_data.targets)

    # Assert
    check_generated_files_expected(
        subtests=subtests,
        iso_build_dir=test_iso_build_dir,
        expected_files=test_data.expected_files,
        logger=logger,
    )
