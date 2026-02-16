from pathlib import Path
from typing import List

import pytest

from lbhelper.run_command import run_command


@pytest.fixture
def patch_subprocess(monkeypatch):
    def _patch_subprocess(outputs: List[str], return_code: int, expected_command: str, expected_cwd: Path):

        class MockProcess:
            def __init__(self, *args, **kwargs):
                self.__current_return = 0
                self.stdout = self

                # Assert received command
                assert args[0] == expected_command
                assert kwargs["cwd"] == expected_cwd

            def poll(self):
                if self.__current_return >= len(outputs):
                    return return_code
                else:
                    return None

            def readline(self):
                if self.__current_return < len(outputs):
                    output = outputs[self.__current_return]
                    self.__current_return += 1
                else:
                    output = ""

                return output.encode("utf-8")

        monkeypatch.setattr("lbhelper.run_command.subprocess.Popen", MockProcess)

    yield _patch_subprocess

def test_run_command(patch_subprocess, caplog):
    patch_subprocess(
        outputs=["--some", "--output"], return_code=0,
        expected_command="some command", expected_cwd=Path("some/dir"))

    run_command(command=["some", "command"], cwd=Path("some/dir"))

    assert "Executing command: \"some command\"" in caplog.text
    assert "--some" in caplog.text
    assert "--output" in caplog.text
    assert "Command \"some command\" exit with return code 0" in caplog.text