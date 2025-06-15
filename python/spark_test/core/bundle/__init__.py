#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""The base classes for bundle backend."""

import enum
import subprocess
from abc import abstractmethod
from pathlib import Path

from spark8t.utils import WithLogging


class BundleBackendEnum(str, enum.Enum):
    """The various backends to deploy the bundle."""

    YAML = "yaml"
    TERRAFORM = "terraform"


class BundleBackend(WithLogging):
    """The base class for bundle backend."""

    deployed_applications: list = []

    def __init__(self, backend: BundleBackendEnum, tempdir: str | Path) -> None:
        self.backend = backend
        self.tempdir = tempdir if isinstance(tempdir, Path) else Path(tempdir)

    def execute(self, *cmds: list[str]) -> list[str]:
        """Execute the given commands within the temp directory."""
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
        """Apply the bundle plan."""
        pass

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the bundle."""
        pass
