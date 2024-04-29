import json
from pathlib import Path
import subprocess
import tempfile
import shutil

from spark8t.utils import WithLogging
from typing import Any

class TerraformNotInstalled(Exception):
    pass

class TerraformCmdError(Exception):
    def __init__(self, process_exception: Exception):
        self.process_exception = process_exception



class Terraform(WithLogging):

    DEFAULT_VARS_FILE = "terraform.tfvars.json"
    def __init__(self, path: Path | str, vars_file: str = DEFAULT_VARS_FILE):
        self.path = path if isinstance(path, Path) else Path(path)
        self.vars_file = self.path / vars_file

        self.version = self._get_version()
        self.init()

    def _exec_command(self, *cmds: list[str]) -> list[str]:

        try:
            result = subprocess.check_output(
                *cmds, stderr=subprocess.PIPE,
                cwd=self.path
            )
            for line in (lines := result.decode("utf-8").split("\n")):
                self.logger.info(line)
            return lines
        except subprocess.CalledProcessError as e:
            self.logger.error(
                f"command '{e.cmd}' return with error (code {e.returncode}): {e.output}")
            raise e

    def _get_version(self) -> str | None:

        try:
            version_output = self._exec_command(["terraform", "version"])
        except subprocess.CalledProcessError as e:
            raise TerraformNotInstalled()

        return version_output[0].split(" ")[1]

    def init(self):
        self._exec_command(["terraform", "init"])

    @staticmethod
    def serialize_value(value: Any) -> str:
        if isinstance(value, str | int | float):
            return str(value)
        else:
            return json.dumps(value)

    @property
    def tf_vars(self) -> dict:
        if self.vars_file.exists():
            with open(self.vars_file, "r") as fid:
                return json.load(fid)
        return {}

    def apply(
            self, tf_vars: dict[str, Any] | None = None, dry_run: bool = False,
            update_vars: bool = False
    ):

        new_vars = tf_vars if not update_vars else self.tf_vars | tf_vars

        bkp_file = Path(f"{self.vars_file}.bkp")
        if self.vars_file.exists():
            shutil.move(self.vars_file, bkp_file)

        with tempfile.NamedTemporaryFile(
                mode="w", dir=self.path, suffix=".tfvars.json"
        ) as tmp_file:
            if new_vars:
                json.dump(new_vars, tmp_file)
                args = [f"-var-file={tmp_file.name}"]
            else:
                args = []

            tmp_file.flush()
            cmds = [
                "terraform", "apply", "-auto-approve", *args
            ] if not dry_run else [
                "terraform", "plan", "-out", self.path / "plan.out", *args
            ]

            try:
                self._exec_command(cmds)
            except subprocess.CalledProcessError as e:
                # Rollback vars
                shutil.move(f"{self.vars_file}.bkp", self.vars_file)
                raise TerraformCmdError(e)

        # The command should have exited successfully, therefore consolidating
        # the new vars
        if new_vars:
            with open(self.vars_file, "w") as fid:
                json.dump(new_vars, fid)

        if bkp_file.exists():
            bkp_file.unlink()

        return self.outputs

    def destroy(self):
        self._exec_command(["terraform", "destroy", "-auto-approve"])

    @property
    def state(self):
        terraform_state = self.path / "terraform.tfstate"
        if not terraform_state.exists():
            return {}
        with open(terraform_state, "r") as fid:
            return json.load(fid)

    @property
    def outputs(self):
        return self.state.get("outputs", {})