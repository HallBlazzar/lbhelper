from dataclasses import dataclass
from typing import List

import pytest

from lbhelper import AptPreference, AptPreferenceType
from lbhelper.defaults import BUILD_TIME_APT_PREFERENCE_FILE, RUN_TIME_APT_PREFERENCE_FILE
from lbhelper.target_writer import AptPreferencesWriter
from tests.validate_files import check_generated_files_expected, ExpectedFile


@dataclass
class AptPreferencesTestData:
    targets: List[AptPreference]
    expected_files: List[ExpectedFile]


def generate_test_data():
    type_to_file_map = {
        AptPreferenceType.BUILD_TIME.name: BUILD_TIME_APT_PREFERENCE_FILE,
        AptPreferenceType.RUN_TIME.name: RUN_TIME_APT_PREFERENCE_FILE,
    }

    test_data = []

    for pref_type, target_file in type_to_file_map.items():
        test_data.append(
            pytest.param(
                AptPreferencesTestData(
                    targets=[
                        AptPreference(
                            package="vim",
                            pin="*",
                            pin_priority=100,
                            preference_type=AptPreferenceType[pref_type],
                        )
                    ],
                    expected_files=[
                        ExpectedFile(
                            file_path=target_file,
                            content=[
                                f"Package: vim\n",
                                f"Pin: *\n",
                                f"Pin-Priority: 100\n",
                                "\n",
                            ]
                        )
                    ]
                ),
                id=f"{pref_type} - single preference in one target",
            )
        )

        test_data.append(
            pytest.param(
                AptPreferencesTestData(
                    targets=[
                        AptPreference(
                            package="vim",
                            pin="*",
                            pin_priority=100,
                            preference_type=AptPreferenceType[pref_type],
                        ),
                        AptPreference(
                            package="nano",
                            pin="*",
                            pin_priority=200,
                            preference_type=AptPreferenceType[pref_type],
                        )
                    ],
                    expected_files=[
                        ExpectedFile(
                            file_path=target_file,
                            content=[
                                f"Package: vim\n",
                                f"Pin: *\n",
                                f"Pin-Priority: 100\n",
                                "\n",
                                f"Package: nano\n",
                                f"Pin: *\n",
                                f"Pin-Priority: 200\n",
                                "\n",
                            ]
                        )
                    ]
                ),
                id=f"{pref_type} - multiple preference in one target",
            )
        )

    test_data.append(
        pytest.param(
            AptPreferencesTestData(
                targets=[
                    AptPreference(
                        package="vim",
                        pin="*",
                        pin_priority=100,
                        preference_type=AptPreferenceType.BUILD_TIME,
                    ),
                    AptPreference(
                        package="nano",
                        pin="*",
                        pin_priority=200,
                        preference_type=AptPreferenceType.RUN_TIME,
                    )
                ],
                expected_files=[
                    ExpectedFile(
                        file_path=BUILD_TIME_APT_PREFERENCE_FILE,
                        content=[
                            f"Package: vim\n",
                            f"Pin: *\n",
                            f"Pin-Priority: 100\n",
                            "\n"
                        ]
                    ),
                    ExpectedFile(
                        file_path=RUN_TIME_APT_PREFERENCE_FILE,
                        content=[
                            f"Package: nano\n",
                            f"Pin: *\n",
                            f"Pin-Priority: 200\n",
                            "\n",
                        ]
                    )
                ]
            )
        )
    )

    return test_data


@pytest.mark.parametrize("test_data", generate_test_data())
def test_success_run(test_data, test_iso_build_dir, subtests, logger):
    # Act
    AptPreferencesWriter(iso_build_dir=test_iso_build_dir).execute(test_data.targets)

    # Assert
    check_generated_files_expected(
        subtests=subtests,
        iso_build_dir=test_iso_build_dir,
        expected_files=test_data.expected_files,
        logger=logger,
    )
