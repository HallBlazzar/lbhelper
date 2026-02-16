import subprocess
from pathlib import Path
from typing import List

from .defaults import DEFAULT_LOGGER


def run_command(command: List[str], cwd: Path = None):
    str_command = " ".join(c for c in command)

    DEFAULT_LOGGER.info(f"Executing command: \"{str_command}\"")
    process = subprocess.Popen(
        str_command,
        shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    while process.poll() is None:
        write_command_to_logger(process)

    return_code = process.poll()

    DEFAULT_LOGGER.info(f"Command \"{str_command}\" exit with return code {return_code}")

    if return_code != 0:
        raise subprocess.CalledProcessError(returncode=return_code, cmd=str_command)


def write_command_to_logger(process: subprocess.Popen):
    while True:
        output = process.stdout.readline().decode()
        if output and len(output) > 0:
            if output[-1] == '\n':
               output = output[:-1]

            DEFAULT_LOGGER.info(output)
        else:
            break
