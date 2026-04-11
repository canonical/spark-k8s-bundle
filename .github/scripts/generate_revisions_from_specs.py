import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from charms_promotions import Charm


@dataclass(frozen=True)
class CharmSpec:
    name: str
    channel: str


@dataclass(frozen=True)
class Specs:
    architectures: list[str]
    releases: dict[str, list[CharmSpec]]
    revision_mapping: dict[str, str]


def normalize_channel(channel: str, risk: str) -> str:
    """Expand channel prefixes like '3.4/' to full channels like '3.4/beta'."""
    if channel.endswith("/"):
        return f"{channel}{risk}"
    return channel


def parse_specs(specs_file: Path) -> Specs:
    with specs_file.open("r", encoding="utf-8") as file_obj:
        data = yaml.safe_load(file_obj)

    if not isinstance(data, dict):
        raise ValueError("Invalid specs format: root must be a mapping")

    architectures = data.get("architectures")
    releases = data.get("releases")
    revision_mapping = data.get("revision_mapping")
    

    if not isinstance(architectures, list) or not all(isinstance(a, str) for a in architectures):
        raise ValueError("Invalid specs format: architectures must be a list of strings")

    if not isinstance(releases, dict):
        raise ValueError("Invalid specs format: releases must be a mapping")

    if not isinstance(revision_mapping, dict):
        raise ValueError("Invalid specs format: revision_mapping must be a mapping")

    if not all(
        isinstance(charm_name, str) and isinstance(mapped_name, str)
        for charm_name, mapped_name in revision_mapping.items()
    ):
        raise ValueError(
            "Invalid specs format: revision_mapping keys and values must be strings"
        )

    parsed_releases: dict[str, list[CharmSpec]] = {}
    for release, charms in releases.items():
        if not isinstance(charms, list):
            raise ValueError(
                f"Invalid specs format: releases.{release} must be a list"
            )

        parsed_entries: list[CharmSpec] = []
        for entry in charms:
            if not isinstance(entry, dict):
                raise ValueError(
                    f"Invalid specs format: release entry for {release} must be a mapping"
                )

            charm_name = entry.get("name")
            channel = entry.get("channel")
            if not isinstance(charm_name, str) or not isinstance(channel, str):
                raise ValueError(
                    f"Invalid specs format: release entry for {release} must have string name and channel"
                )

            parsed_entries.append(CharmSpec(name=charm_name, channel=channel))

        parsed_releases[str(release)] = parsed_entries

    return Specs(
        architectures=architectures,
        releases=parsed_releases,
        revision_mapping=revision_mapping,
    )


def resolve_revision(charm: Charm) -> int:
    items = charm.get_status()

    if not items:
        raise ValueError(
            f"No revision found for charm={charm.name}, channel={charm.channel}, architecture={charm.architecture}"
        )

    if len(items) > 1:
        revisions = sorted(item["revision"] for item in items)
        raise ValueError(
            "Multiple revisions found for "
            f"charm={charm.name}, channel={charm.channel}, architecture={charm.architecture}: {revisions}"
        )

    revision = items[0]["revision"]

    if not isinstance(revision, int):
        raise ValueError(
            f"Unexpected revision type for charm={charm.name}, channel={charm.channel}, architecture={charm.architecture}"
        )

    return revision


def build_output(specs: Specs, risk: str) -> dict:
    output = {}
    revision_mapping = specs.revision_mapping

    for architecture in specs.architectures:
        output[architecture] = {}
        for release, charms in specs.releases.items():
            output[architecture][str(release)] = {}

            for entry in charms:
                charm_name = entry.name
                channel = normalize_channel(entry.channel, risk)
                mapped_name = revision_mapping.get(charm_name)

                if not mapped_name:
                    raise ValueError(
                        f"Missing revision mapping for charm={charm_name}"
                    )

                charm = Charm(
                    name=charm_name,
                    revision=None,
                    channel=channel,
                    architecture=architecture,
                )
                revision = resolve_revision(charm)
                output[architecture][str(release)][mapped_name] = revision

    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Parse specs.yaml and fetch charm revisions by architecture/release/channel "
            "using charms_promotions.Charm"
        )
    )
    parser.add_argument(
        "--specs-file",
        default="scripts/specs.yaml",
        help="Input specs file (default: scripts/specs.yaml)",
    )
    parser.add_argument(
        "--output-file",
        default="scripts/revisions.yaml",
        help="Output YAML file (default: scripts/revisions.yaml)",
    )
    parser.add_argument(
        "--risk",
        default="beta",
        choices=("edge", "beta", "candidate", "stable"),
        help="Risk suffix used when channel in specs ends with '/'.",
    )
    args = parser.parse_args()

    try:
        specs = parse_specs(Path(args.specs_file))
        output = build_output(specs, risk=args.risk)

        with Path(args.output_file).open("w", encoding="utf-8") as file_obj:
            yaml.safe_dump(output, file_obj, sort_keys=False)

    except (KeyError, PermissionError, RuntimeError, ValueError) as err:
        print(f"ERROR: {type(err).__name__}: {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
