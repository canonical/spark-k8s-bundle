#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""YAML backend to apply the bundle."""

import os
from pathlib import Path

import jinja2
import yaml

from . import BundleBackend, BundleBackendEnum


class YamlBackend(BundleBackend):
    """The YAML bundle backend."""

    bundle_file = None

    def __init__(
        self,
        model: str,
        tempdir,
        bundle_file: str | Path,
        overlays: list[str | Path] = None,
    ):
        super().__init__(backend=BundleBackendEnum.YAML.value, tempdir=tempdir)
        self.model = model
        self.bundle_file = bundle_file
        self.overlays = overlays

    def render_template(
        self, template_file: str | Path, vars: dict[str, str] | None
    ) -> str:
        """Render the yaml.j2 template file with given template vars."""
        if vars is None:
            vars = {}
        with open(template_file) as source:
            template = jinja2.Template(source.read())
            return template.render(**vars)

    def apply(self, vars: dict[str, str] | None = None):
        """Apply the YAML bundle."""
        rendered_bundle_file = self.tempdir / os.path.basename(self.bundle_file)
        deployed_applications = []
        with open(rendered_bundle_file, mode="w") as destination:
            content = self.render_template(self.bundle_file, vars=vars)
            destination.write(content)
            destination.flush()

            content_yaml = yaml.safe_load(content)
            deployed_applications.extend(list(content_yaml["applications"].keys()))

        command = [
            "juju",
            "deploy",
            "--model",
            self.model,
            "--trust",
            rendered_bundle_file,
        ]

        for overlay in self.overlays:
            rendered_overlay_file = self.tempdir / os.path.basename(overlay)
            with open(rendered_overlay_file, mode="w") as destination:
                content = self.render_template(overlay, vars=vars)
                destination.write(content)
                destination.flush()
                deployed_applications.extend(
                    list(yaml.safe_load(content)["applications"].keys())
                )
            command.extend(["--overlay", rendered_overlay_file])

        self.execute(command)
        self.deployed_applications = deployed_applications
        return deployed_applications

    def destroy(self):
        """Destroy the bundle."""
        for app in self.deployed_applications:
            command = ["juju", "remove-application", "--force", "--no-prompt", app]
            self.execute(command)
