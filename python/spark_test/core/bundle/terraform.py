#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Terraform backend to apply the bundle."""

import json
import shutil
import tempfile
from pathlib import Path

from . import BundleBackend, BundleBackendEnum


class TerraformBackend(BundleBackend):
    """Terraform bundle backend."""

    def __init__(self, tempdir, module_path: str | Path):
        self.module_path = module_path
        super().__init__(backend=BundleBackendEnum.TERRAFORM, tempdir=tempdir)
        self.init()

    def init(self) -> None:
        """Initialize terraform."""
        shutil.copytree(self.module_path, self.tempdir, dirs_exist_ok=True)
        self.execute(["terraform", "init"])

    def apply(self, vars: dict[str, str] | None = None) -> list[str]:
        """Apply the terraform plan."""
        with tempfile.NamedTemporaryFile(
            mode="w+",
            dir=self.tempdir,
            suffix=".tfvars.json",
        ) as tfvars_file:
            tfvars_file = tfvars_file
            json.dump(vars, tfvars_file)
            tfvars_file.flush()
            tfvars_file.seek(0)
            self.execute(
                ["terraform", "apply", "-auto-approve", "-var-file", tfvars_file.name]
            )
        self.deployed_applications = list(self.outputs["charms"]["value"].values())
        return self.deployed_applications

    def destroy(self):
        """Destroy the terraform plan."""
        self.execute(["terraform", "destroy", "-auto-approve"])

    @property
    def state(self):
        """The dictionary representing the TFState file."""
        tfstate_file = self.tempdir / "terraform.tfstate"
        if not tfstate_file.exists():
            return {}
        with open(tfstate_file) as fid:
            return json.load(fid)

    @property
    def outputs(self):
        """The terraform output."""
        return self.state.get("outputs", {})
