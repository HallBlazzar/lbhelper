import random
import string
from dataclasses import dataclass
from typing import List

import pytest

from lbhelper import HookScript
from lbhelper.target_writer import HookScriptWriter
from tests.validate_files import check_generated_files_expected, ExpectedFile
from lbhelper.defaults import LIVE_HOOKS_DIR, NORMAL_HOOKS_DIR


@dataclass
class HookScriptTestData:
    targets: List[HookScript]
    expected_files: List[ExpectedFile]


@pytest.fixture
def generate_test_data(generate_test_files):
    test_data = HookScriptTestData(
        targets=[],
        expected_files=[],
    )

    def _generate_test_data(live_only: bool, contents: List[List[str]]):
        test_files = generate_test_files(contents=contents)
        for i, test_file in enumerate(test_files):
            hook_dir = LIVE_HOOKS_DIR if live_only else NORMAL_HOOKS_DIR
            hook_name = ''.join(random.choices(string.ascii_letters, k=10))

            # lambda value is decided during execution time but definition time
            # see https://stackoverflow.com/questions/63123011/lambda-functions-created-in-a-for-loop-being-overwritten
            test_data.targets.append(
                HookScript(
                    get_script_file=lambda path=test_file: path,
                    live_only=live_only,
                    hook_name=hook_name,
                )
            )
            test_data.expected_files.append(ExpectedFile(
                file_path=hook_dir / f"{i+1:04}-{hook_name}.hook.chroot",
                content=contents[i]
            ))

        return test_data

    yield _generate_test_data


def get_test_data_prefix(live_only: bool) -> str:
    return "live-only" if live_only else "normal"


def success_run_test_data():
    test_data = []

    for live_only in [True, False]:
        prefix = get_test_data_prefix(live_only=live_only)

        test_data.append(
            # each element represents file content(list of strings for multiple lines) of a hook
            pytest.param(
                live_only,
                [
                    ["hook1\n", ],
                ], id=f"{prefix} - single hook"
            ),
        )

        test_data.append(
            pytest.param(
                live_only,
                [
                    # hook file 1 content
                    ["hook1\n", ],
                    # hook file 2 content
                    ["hook2\n", ],
                ], id=f"{prefix} - multiple hooks"
            ),
        )

    return test_data


@pytest.mark.parametrize("live_only, contents", success_run_test_data())
def test_success_run(generate_test_data, live_only, contents, test_iso_build_dir, subtests, logger):
    # Arrange
    full_test_data = generate_test_data(live_only=live_only, contents=contents)

    # Act
    HookScriptWriter(iso_build_dir=test_iso_build_dir).execute(full_test_data.targets)

    # Assert
    check_generated_files_expected(
        subtests=subtests,
        iso_build_dir=test_iso_build_dir,
        expected_files=full_test_data.expected_files,
        logger=logger,
    )


def no_overlap_test_data():
    test_data = []
    live_only_to_max_num_pair = {
        True: 100,
        False: 10000
    }

    live_only_to_reserved_orders_map = {
        True: [10, 50],
        False: [
            1000, 1010, 1020,
            5000, 5010, 5020, 5030, 5040, 5050,
            8000, 8010, 8020, 8030, 8040, 8050, 8060, 8070, 8080, 8090, 8100, 8110,
            9000, 9010, 9020
        ]
    }

    live_only_to_hook_dir_map = {
        True: LIVE_HOOKS_DIR,
        False: NORMAL_HOOKS_DIR
    }

    for live_only, max_num in live_only_to_max_num_pair.items():
        contents = []
        for n in range(max_num):
            contents.append([])

        prefix = get_test_data_prefix(live_only=live_only)


        test_data.append(
            pytest.param(
                live_only,
                live_only_to_reserved_orders_map[live_only],
                contents,
                live_only_to_hook_dir_map[live_only],
                id=f"{prefix} - single hook"
            ),
        )

    return test_data


# Make sure hooks orders won't overlap with existing or pre-defined hooks.
@pytest.mark.parametrize("live_only, reserved_order, contents, hooks_dir", no_overlap_test_data())
def test_no_overlap(
        generate_test_data,
    live_only, reserved_order, contents, hooks_dir,
    test_iso_build_dir, logger
):
    # Arrange
    full_test_data = generate_test_data(live_only=live_only, contents=contents)

    # Act
    HookScriptWriter(iso_build_dir=test_iso_build_dir).execute(full_test_data.targets)

    # Assert
    # collect all targets
    collected_orders = []
    saved_hooks = (test_iso_build_dir / hooks_dir).glob("*")
    for saved_hook in saved_hooks:
        collected_orders.append(saved_hook.name.split("-")[0])

    logger.info(f"collected orders: {collected_orders}")

    checked_order = []
    for collected_order in collected_orders:
        assert collected_order not in checked_order, f"order {collected_order} conflicted"
        assert collected_order not in reserved_order
        checked_order.append(collected_order)
