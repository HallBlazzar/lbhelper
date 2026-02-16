import shutil
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest
from pathlib import Path
from typing import List


@pytest.fixture(scope="function")
def generate_test_files():
    # Even for function scope, reusing this fixture makes all_test_files persists.
    # Therefore, instead of directly interacting with all_test_files, always
    # returning current result there. The all_test_files should be used for cleanup.
    all_test_files = []

    try:
        def _generate_test_files(contents: List[List[str]]) -> List[Path]:
            generated_test_files = []
            for i, content in enumerate(contents):
                with NamedTemporaryFile(delete=False, mode="w") as f:
                    f.writelines(content)

                generated_test_files.append(Path(f.name))

            all_test_files.extend(generated_test_files)

            return generated_test_files

        yield _generate_test_files

    except Exception as e:
        pytest.fail(f"Caught exception during test files generation: {e}")

    finally:
        for test_file in all_test_files:
            test_file.unlink(missing_ok=True)


@pytest.fixture(scope="function")
def generate_test_dir():
    # Separate current result and cleanup for the same reason as generate_test_files
    generated_test_dirs = []

    try:
        def _generate_test_dir(files_under_dirs: List[List[Path]]) -> Path:
            for files in files_under_dirs:
                with TemporaryDirectory(delete=False) as tmp_dir:
                    for file in files:
                        shutil.copy(file, tmp_dir)

                    generated_test_dirs.append(Path(tmp_dir))

            return Path(tmp_dir)

        yield _generate_test_dir

    except Exception as e:
        pytest.fail(f"Caught exception during test dirs generation: {e}")

    finally:
        for test_dir in generated_test_dirs:
            shutil.rmtree(test_dir)
