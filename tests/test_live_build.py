import pytest

from lbhelper.live_build import LBOperation, run_lb_operation
from lbhelper.live_build import remove_build_dir
import shutil


@pytest.fixture(scope="function")
def mock_success_command_runner(monkeypatch):
    def _mock_success_command_runner(test_iso_build_dir, operation):
        def validate_command(*args, **kwargs):
            assert kwargs["command"] == ["/usr/bin/lb", operation], "command is not expected or not given"
            assert kwargs["cwd"].resolve() == test_iso_build_dir.resolve(), "cwd is not expected or not given"

        # See https://alexmarandon.com/articles/python_mock_gotchas/
        monkeypatch.setattr("lbhelper.live_build.run_command", validate_command)

    yield _mock_success_command_runner


@pytest.mark.parametrize("operation",[LBOperation.BUILD, LBOperation.CLEAN, LBOperation.CONFIG])
def test_run_lb_operation(operation, mock_success_command_runner, test_iso_build_dir):
    # Arrange, Assert
    mock_success_command_runner(test_iso_build_dir, operation.value)

    # Act
    run_lb_operation(operation=operation, iso_build_dir=test_iso_build_dir)


@pytest.fixture
def mock_remove_dir(monkeypatch):
    def _mock_remove_dir(test_iso_build_dir):
        def validate_build_dir(*args, **kwargs):
            assert args[0] == test_iso_build_dir, "build_dir is not expected or not given"
            assert kwargs["ignore_errors"] == True

        monkeypatch.setattr(shutil, "rmtree", validate_build_dir)

    yield _mock_remove_dir


def test_remove_build_dir(mock_remove_dir, test_iso_build_dir):
    # Arrange, Assert
    remove_build_dir(test_iso_build_dir)

    # Act
    remove_build_dir(test_iso_build_dir)
