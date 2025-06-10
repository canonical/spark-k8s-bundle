from abc import abstractmethod
import enum
from pathlib import Path
import subprocess
from spark8t.utils import WithLogging


class BundleBackendEnum(enum.StrEnum):
    YAML = "yaml"
    TERRAFORM = "terraform"


class BundleBackend(WithLogging):
    deployed_applications: list = []

    def __init__(self, backend: BundleBackendEnum, tempdir: str | Path) -> None:
        self.backend = backend
        self.tempdir = tempdir if isinstance(tempdir, Path) else Path(tempdir)

    def execute(self, *cmds: list[str]) -> list[str]:
        try:
            result = subprocess.check_output(
                *cmds, stderr=subprocess.PIPE, cwd=self.tempdir
            )
            for line in (lines := result.decode("utf-8").split("\n")):
                self.logger.info(line)
            return lines
        except subprocess.CalledProcessError as e:
            self.logger.error(
                f"command '{e.cmd}' return with error (code {e.returncode})\n"
                f"***STDOUT***\n{e.output}\n"
                f"***STDERR***\n{e.stderr}\n"
            )
            raise e

    @abstractmethod
    def apply(self, vars: dict[str, str] = None) -> None:
        pass

    @abstractmethod
    def destroy(self) -> None:
        pass
