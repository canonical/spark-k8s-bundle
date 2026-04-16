"""Utilities for parsing charm status and promoting charm revisions."""

import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Callable

import yaml

RISKS = {"edge": 1, "beta": 2, "candidate": 3, "stable": 4}


class Charm:
    """Representation of a charm with helpers to query status and promote revisions."""

    def __init__(
        self,
        name: str,
        revision: Optional[int] = None,
        channel: Optional[str] = None,
        architecture: Optional[str] = None,
    ):
        self.name = name
        self.revision = revision
        self.channel = channel
        self.architecture = architecture

        self._status: Optional[dict] = None

    def __str__(self):
        """Return a readable charm representation."""
        return f"{self.name}:{self.channel}({self.revision})"

    def __repr__(self):
        """Return the canonical debug representation."""
        return self.__str__()

    def to_dict(self) -> dict:
        """Return a dictionary representation of the charm."""
        return {k:v for k,v in {
            "name": self.name,
            "revision": self.revision,
            "channel": self.channel,
            "architecture": self.architecture,
        }.items() if v is not None}

    @staticmethod
    def from_dict(data: dict) -> 'Charm':
        """Create a Charm instance from a dictionary."""
        return Charm(
            name=data["name"],
            revision=data.get("revision"),
            channel=data.get("channel"),
            architecture=data.get("architecture"),
        )

    def get_status(
        self,
        channel: Optional[str] = None,
        revision: Optional[int] = None,
        architecture: Optional[str] = None,
    ):
        """Return matching status entries for this charm."""
        if not channel:
            channel = self.channel
        if not revision:
            revision = self.revision
        if not architecture:
            architecture = self.architecture

        if not self._status:
            result = subprocess.run(
                ["charmcraft", "status", self.name, "--format", "json"],
                capture_output=True,
            )

            if result.returncode != 0:
                err_output = (
                    (result.stderr or b"").decode("utf-8", errors="replace").strip()
                )
                std_output = (
                    (result.stdout or b"").decode("utf-8", errors="replace").strip()
                )
                if (
                    "permission-required" in std_output
                    or "permission-required" in err_output
                ):
                    raise PermissionError(self.name)
                else:
                    raise RuntimeError(
                        self.name, shlex.join(result.args), err_output or std_output
                    )

            self._status = json.loads(result.stdout.decode("utf-8"))

        items = [
            {"base": mapping["base"]} | release
            for track in self._status
            for mapping in track["mappings"]
            for release in mapping["releases"]
            if mapping["base"]
            if (not channel or channel == release["channel"])
            and (not revision or revision == release["revision"])
            and (not architecture or architecture == mapping["base"]["architecture"])
        ]

        return items

    def resolve_architecture(self) -> 'Charm':
        """Resolve a single architecture for a charm/channel/revision tuple."""
        if self.architecture is not None:
            print(f"INFO: Using provided architecture {self.architecture}")
            return self

        items = self.get_status(channel=self.channel, revision=self.revision)

        if not items:
            raise ValueError(
                f"No architecture found for charm={self.name}, channel={self.channel}, revision={self.revision}"
            )

        if len(items) > 1:
            architectures = sorted(item["base"]["architecture"] for item in items)
            raise ValueError(
                "Multiple architectures found for "
                f"charm={self.name}, channel={self.channel}, revision={self.revision}: {architectures}"
            )

        architecture = items[0]["base"]["architecture"]

        if not isinstance(architecture, str):
            raise ValueError(
                f"Unexpected architecture type for charm={self.name}, channel={self.channel}, revision={self.revision}"
            )

        self.architecture = architecture
        return self
    
    def resolve_revision(self) -> 'Charm':
        """Resolve a single revision for a charm/channel/architecture tuple."""
        if self.revision is not None:
            print(f"INFO: Using provided revision {self.revision}")
            return self

        items = self.get_status(channel=self.channel, architecture=self.architecture)

        if not items:
            raise ValueError(
                f"No revision found for charm={self.name}, channel={self.channel}, architecture={self.architecture}"
            )

        if len(items) > 1:
            revisions = sorted(item["revision"] for item in items)
            raise ValueError(
                "Multiple revisions found for "
                f"charm={self.name}, channel={self.channel}, architecture={self.architecture}: {revisions}"
            )

        revision = items[0]["revision"]

        if not isinstance(revision, int):
            raise ValueError(
                f"Unexpected revision type for charm={self.name}, channel={self.channel}, architecture={self.architecture}"
            )

        self.revision = revision
        return self

    def promote_version(self, risk: str, dry_run: bool = True):
        """Promote a charm revision to a higher-risk channel."""
        if risk not in RISKS.keys():
            raise ValueError("The risk is not recognized")

        if not self.channel:
            raise ValueError(
                "channel field is not specified, that is required for promotion"
            )

        items = self.get_status(revision=self.revision, channel=self.channel)

        if len(items) > 1:
            raise ValueError(
                f"Multiple tracks match the provide revision and channel combination: {items}"
            )

        if len(items) == 0:
            raise ValueError(f"No match found for charm {self}")

        item = items[0]

        _channel = Path(item["channel"])
        risk_from = str(_channel.name)

        if risk_from not in RISKS.keys():
            raise ValueError("The revision does not belong to a risk channel")

        if RISKS[risk] <= RISKS[risk_from]:
            raise ValueError("A charm revision cannot be promoted to a lower risk.")

        channel_to = str(_channel.parent / risk)

        cmds = [
            "charmcraft",
            "release",
            self.name,
            f"--channel={channel_to}",
            f"--revision={self.revision}",
        ] + [
            f"--resource={resource['name']}:{resource['revision']}"
            for resource in item["resources"]
        ]

        if dry_run:
            return "INFO: (dry-run mode) " + shlex.join(cmds)

        return subprocess.check_output(cmds).decode("utf-8")


class Format(str, Enum):
    """Supported status input formats."""

    TEXT = "text"
    YAML = "yaml"


@dataclass
class Bundle:
    """Collection of charms parsed from status content."""

    charms: list[Charm]

    @classmethod
    def from_status(
        cls, content: str | Path, format: Format | str = Format.TEXT
    ):
        """Parse status content into a Bundle."""
        if isinstance(content, Path):
            content = content.read_text(encoding="utf-8")

        parsers = {Format.TEXT: TextParser, Format.YAML: YAMLParser}
        normalized_format = Format(format)

        return parsers[normalized_format].parse(content)

    def filter(self, condition: Callable[[Charm], bool]) -> 'Bundle':
        """Return a new Bundle containing only charms that satisfy the condition."""
        return Bundle(charms=[charm for charm in self.charms if condition(charm)])

    def exclude(self, names: set[str]) -> 'Bundle':
        """Return a new Bundle excluding charms whose name is in the provided set."""
        return self.filter(lambda charm: charm.name not in names)

    def to_status(self, file: Path, format: Format | str = Format.YAML):
        """Serialize the Bundle to a status format."""
        # This method is not implemented as it's not required for the current use case,
        # but it could be implemented if needed in the future.
        if format == Format.TEXT:
            raise NotImplementedError("Bundle.to_status with text format is not implemented yet.")

        remapping_keys = {
            "channel": "charm-channel",
            "revision": "charm-rev",
            "architecture": "charm-arch",
            "name": "charm-name",
        }

        def remap_charm_dict(charm_dict: dict) -> dict:
            return {remapping_keys.get(k, k): v for k, v in charm_dict.items()}

        with file.open("w", encoding="utf-8") as fid:
            yaml.dump({"applications": {charm.name: remap_charm_dict(charm.to_dict()) for charm in self.charms}}, fid)

    def to_tfvars(self, filename: Path, mapping: dict):
        """Serialize the Bundle to a Terraform JSON format."""
        with filename.open("w", encoding="utf-8") as fid:
            yaml.dump({
                mapping.get(charm.name, charm.name): charm.revision
                for charm in self.charms
            }, fid)

@dataclass
class Release:
    bundles: dict[str, Bundle]

    @staticmethod
    def bucketize(charms: list[Charm], key: Callable[[Charm], str]) -> dict[str, Bundle]:
        buckets: dict[str, list[Charm]] = {}
        for charm in charms:
            bucket_key = key(charm)
            buckets.setdefault(bucket_key, []).append(charm)

        return {bucket_key: Bundle(charms) for bucket_key, charms in buckets.items()}

    def to_json(self) -> dict:
        return {name: [charm.to_dict() for charm in bundle.charms] for name, bundle in self.bundles.items()}

    @staticmethod
    def from_json(data: dict) -> 'Release':
        bundles = {
            name: Bundle(
                [Charm.from_dict(charm_data) for charm_data in bundle_data]
            ) for name, bundle_data in data.items()
        }
        return Release(bundles=bundles)

class YAMLParser:
    """Parser for Juju YAML status output."""

    @staticmethod
    def parse(content: str | Path):
        """Parse YAML status content and return a Bundle."""
        if isinstance(content, Path):
            content = content.read_text(encoding="utf-8")

        data = yaml.safe_load(content)

        return Bundle(
            [
                Charm(
                    name=app["charm-name"], 
                    revision=int(app["charm-rev"]), 
                    channel=app.get("charm-channel"),
                    architecture=app.get("charm-arch"),
                ).resolve_architecture() 
                for _, app in data["applications"].items()
            ]
        )


class TextParser:
    """
    Parse a juju status output to find the charms deployed and their metadata (channel, revision, etc).

    The `parse` method is used to extract the list of charms, returned as a Bundle class.
    The reason why simpler parsing methods could not be used, is that the output format of a juju status is
    made peculiar by some columns header being aligned right instead of left, e.g. see Rev below:

    App                      Version                  Status   Scale  Charm                    Channel         Rev  Address       Exposed  Message
    ...
    istio-ingressgateway                              active       1  istio-gateway            1.28/edge      1594  10.0.165.149  no
    ...

    The algorithm parse the header and finds a first guess for the columns start. When parsing each rows, the algorithm updates the width
    of each column using the width of the value itself, then treating the remaining chars as the values for the next columns. This algorithm falls short
    if the values has multiple white spaces (also in headers). However this only happens in the value of the "Message" column, which is accounted for.
    """

    # The following regex extract the first word that may be preceded by
    # leading spaces
    word_with_leading_spaces = re.compile(r"^\s*[^\s]+")

    @staticmethod
    def extract_first_word(mystring):
        """Extract the first token, preserving leading spaces in the match."""
        m = TextParser.word_with_leading_spaces.match(mystring)
        if m:
            return mystring[m.start() : m.end()]
        return ""

    @staticmethod
    def parse_line(line, indices):
        """Split a line using fixed-width index ranges."""
        return [line[start:end].strip() for start, end in indices]

    @staticmethod
    def parse(content: str | Path):
        """Parse text status output and return a Bundle."""
        if isinstance(content, Path):
            content = content.read_text(encoding="utf-8")

        lines = content.splitlines()

        white_spaces = re.compile(r"\s+\s+")

        app_header_index = next(
            (
                index
                for index, line in enumerate(lines)
                if line.strip().startswith("App")
                and "Charm" in line
                and "Channel" in line
            ),
            None,
        )

        if app_header_index is None:
            raise ValueError("Could not locate applications table in status text")

        table_lines = []
        for line in lines[app_header_index:]:
            if table_lines and (not line.strip() or line.strip().startswith("Unit")):
                break
            table_lines.append(line)

        if len(table_lines) < 2:
            raise ValueError("Applications table is empty in status text")

        # Get header
        header = table_lines[0]

        # First guess of width based on headers
        ends = [s.end() for s in white_spaces.finditer(header)]
        indices = list(zip([0] + ends, ends + [-1], strict=False))

        # Columns names
        columns = TextParser.parse_line(header, indices)

        # Second guess of width based on maximum width of values
        # This is due to the fact that some columns the text extends to before the start
        # of the columns header (text aligned right)
        widths = [len(column) for column in columns]
        for line in table_lines[1:]:
            widths = list(
                map(
                    max,
                    zip(
                        widths,
                        [
                            len(TextParser.extract_first_word(line[start:end]))
                            for start, end in indices
                        ],
                        strict=False,
                    ),
                )
            )

        # New guess
        ends = [
            start + width for (start, _), width in zip(indices, widths, strict=False)
        ]

        indices = list(zip([0] + ends[:-1], ends[:-1] + [-1], strict=False))

        data = [
            dict(zip(columns, TextParser.parse_line(line, indices), strict=False))
            for line in table_lines[1:]
            if line.strip()
        ]

        return Bundle(
            [
                Charm(item["Charm"], int(item["Rev"]), item["Channel"]).resolve_architecture()
                for item in data
                if item["Charm"]
            ]
        )


@dataclass(frozen=True)
class CharmSpec:
    """Charm specification for a release."""

    name: str
    channel: str
    revision: Optional[int] = None


@dataclass(frozen=True)
class Specs:
    """Top-level specs model."""

    architectures: list[str]
    releases: dict[str, list[CharmSpec]]

    @classmethod
    def parse(cls, content: str | Path) -> 'Specs':
        """Load and validate specs YAML, returning a typed Specs object."""
        if isinstance(content, Path):
            content = content.read_text(encoding="utf-8")

        data = yaml.safe_load(content)

        if not isinstance(data, dict):
            raise ValueError("Invalid specs format: root must be a mapping")

        architectures = data.get("architectures")
        releases = data.get("releases")

        if not isinstance(architectures, list) or not all(
            isinstance(a, str) for a in architectures
        ):
            raise ValueError(
                "Invalid specs format: architectures must be a list of strings"
            )

        if not isinstance(releases, dict):
            raise ValueError("Invalid specs format: releases must be a mapping")

        parsed_releases: dict[str, list[CharmSpec]] = {}
        for release, charms in releases.items():
            if not isinstance(charms, list):
                raise ValueError(f"Invalid specs format: releases.{release} must be a list")

            parsed_entries: list[CharmSpec] = []
            for entry in charms:
                if not isinstance(entry, dict):
                    raise ValueError(
                        f"Invalid specs format: release entry for {release} must be a mapping"
                    )

                charm_name = entry.get("name")
                channel = entry.get("channel")
                revision = entry.get("revision")

                if not isinstance(charm_name, str) or not isinstance(channel, str):
                    raise ValueError(
                        f"Invalid specs format: release entry for {release} must have string name and channel"
                    )

                parsed_entries.append(CharmSpec(name=charm_name, channel=channel, revision=revision))

            parsed_releases[str(release)] = parsed_entries

        return cls(
            architectures=architectures,
            releases=parsed_releases
        )

    @staticmethod
    def _normalize_channel(channel: str, risk: str) -> str:
        """Expand channel prefixes like '3.4/' to full channels like '3.4/beta'."""
        if channel.endswith("/"):
            return f"{channel}{risk}"
        return channel

    def resolve_charms(self, risk: str = "edge") -> Release:
        """Build the output mapping keyed by architecture, release, and mapped revision key."""
        releases = {} 

        for release, charms in self.releases.items():
            items = []
            for architecture in self.architectures:

                for entry in charms:
                    charm_name = entry.name
                    channel = self._normalize_channel(entry.channel, risk)
 
                    items.append(
                        Charm(
                            name=charm_name,
                            revision=None,
                            channel=channel,
                            architecture=architecture,
                        ).resolve_revision()
                    )
                
            releases[str(release)] = Release.bucketize(items, key=lambda charm: charm.architecture)

        # Flatten the mapping to have keys of the form "release@architecture"
        return Release(bundles={
            f"{release}@{architercture}": bundle 
            for release, bundles in releases.items() 
            for architercture, bundle in bundles.items()
        })


MAPPING = {
    "kyuubi-k8s": "kyuubi_revision",
    "spark-history-server-k8s": "history_server_revision",
    "spark-integration-hub-k8s": "integration_hub_revision"
}


def _source_risk_for_target(target_risk: str) -> str:
    """Return the risk channel that should be used as source for a promotion target."""
    order = ["edge", "beta", "candidate", "stable"]
    idx = order.index(target_risk)
    if idx == 0:
        raise ValueError("Cannot infer source risk for target edge")
    return order[idx - 1]


def _load_release(input_file: Path, format_name: str, risk: Optional[str] = None) -> Release:
    """Load release data from status/spec input based on the selected format."""
    if format_name in ("text", "yaml"):
        filename = input_file.name.removesuffix(input_file.suffix)
        return Release(
            bundles={
                filename: Bundle.from_status(input_file, format_name),
            }
        )

    if format_name == "spec":
        source_risk = _source_risk_for_target(risk) if risk else "edge"
        return Specs.parse(input_file).resolve_charms(risk=source_risk)

    raise ValueError(f"Unsupported format: {format_name}")


def _write_revisions(release: Release, output_dir: Path, output_format: str):
    """Write one status file per release bundle, using bundle key as filename."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if output_format == "tfvars":
        for key, bundle in release.bundles.items():
            bundle.to_tfvars(output_dir / f"{key}.tfvars.yaml", mapping=MAPPING)
    elif output_format == "yaml":
        for key, bundle in release.bundles.items():
            bundle.to_status(output_dir / f"{key}.yaml")


def _run_promote(args) -> int:
    """Execute promotion flow."""
    release = _load_release(Path(args.file), args.format, risk=args.promote_to)

    for variant, bundle in release.bundles.items():
        print(f"Processing release {variant} with charms: {bundle.charms}")
        for charm in bundle.charms:
            try:
                print(charm.promote_version(args.promote_to, args.dry_run))
            except ValueError as err:
                print(
                    f"ERROR: skipping {charm.name} due to failure in promotion. Reason: {type(err).__name__} - Details: {','.join(err.args)}"
                )
            except PermissionError:
                print(
                    f"WARNING: skipping '{charm.name}' due to missing permissions.",
                    file=sys.stderr,
                )
            except RuntimeError as err:
                print(
                    f"WARNING: skipping '{err.args[0]}' after command failure: {err.args[1]}",
                    file=sys.stderr,
                )

    return 0


def _run_get_revisions(args) -> int:
    """Execute revisions generation flow."""
    release = _load_release(Path(args.file), args.format, risk=args.risk)
    _write_revisions(release, Path(args.output_dir), args.output)
    print(f"INFO: wrote revisions files under {args.output_dir}")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    promote_parser = subparsers.add_parser("promote")
    promote_action_group = promote_parser.add_mutually_exclusive_group()
    promote_action_group.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Print release commands without executing them (default)",
    )
    promote_action_group.add_argument(
        "--apply",
        dest="dry_run",
        action="store_false",
        help="Execute charmcraft release commands",
    )
    promote_parser.set_defaults(dry_run=True)
    promote_parser.add_argument(
        "--promote-to", choices=("beta", "candidate", "stable"), required=True
    )
    promote_parser.add_argument(
        "--format", choices=("text", "yaml", "spec"), required=True
    )
    promote_parser.add_argument("--file", required=True)

    get_revisions_parser = subparsers.add_parser("get-revisions")
    get_revisions_parser.add_argument(
        "--format", choices=("text", "yaml", "spec"), required=True
    )
    get_revisions_parser.add_argument("--file", required=True)
    get_revisions_parser.add_argument(
        "--risk", choices=("edge", "beta", "candidate", "stable"), default="edge"
    )
    get_revisions_parser.add_argument(
        "--output", choices=("yaml", "tfvars"), default="yaml"
    )
    get_revisions_parser.add_argument("--output-dir", default=".")

    args = parser.parse_args()

    if args.command == "promote":
        raise SystemExit(_run_promote(args))

    if args.command == "get-revisions":
        raise SystemExit(_run_get_revisions(args))