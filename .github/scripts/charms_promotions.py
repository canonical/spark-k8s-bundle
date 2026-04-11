import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml

RISKS = {"edge": 1, "beta": 2, "candidate": 3, "stable": 4}

class Charm:

    def __init__(self, name: str, revision: Optional[int]=None, channel: Optional[str]=None, architecture: Optional[str] = None):
        self.name = name
        self.revision = revision
        self.channel = channel
        self.architecture = architecture

        self._status: Optional[dict] = None

    def __str__(self):
        return f"{self.name}:{self.channel}({self.revision})"

    def __repr__(self):
        return self.__str__()

    def get_status(self, channel: Optional[str] = None, revision: Optional[int] = None, architecture: Optional[str] = None):

        if not channel:
            channel = self.channel
        if not revision:
            revision = self.revision
        if not architecture:
            architecture = self.architecture

        if not self._status:

            output = subprocess.run(
                ["charmcraft", "status", self.name, "--format", "json"],
                capture_output=True
            )

            if output.returncode != 0:
                err_output = (output.stderr or b"").decode("utf-8", errors="replace").strip()
                output = (output.stdout or b"").decode("utf-8", errors="replace").strip()
                if "permission-required" in output or "permission-required" in err_output:
                    raise PermissionError(self.name)
                else:
                    raise RuntimeError(charm.name, shlex.join(err.cmd), err)

            self._status = json.loads(output.stdout.decode("utf-8"))

        items = [
            mapping["base"] | release
            for track in self._status
            for mapping in track["mappings"]
            for release in mapping["releases"]
            if mapping["base"]
            if (not channel or channel == release["channel"]) and (
                        not revision or revision == release["revision"]) and (
                        not architecture or architecture == mapping["base"]["architecture"]
                        )
        ]

        return items


    def promote_version(self, risk: str, dry_run: bool = True):
        if risk not in RISKS.keys():
            raise ValueError("The risk is not recognized")

        if not self.channel:
            raise ValueError("channel field is not specified, that is required for promotion")

        items = self.get_status(revision=self.revision, channel=self.channel)

        if len(items) > 1:
            raise ValueError(f"Multiple tracks match the provide revision and channel combination: {items}")

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

        cmds = (
                ["charmcraft", "release", self.name, f"--channel={channel_to}",
                 f"--revision={self.revision}"] +
                [f"--resource={resource['name']}:{resource['revision']}" for
                 resource in item["resources"]]
        )

        if dry_run:
            return "INFO: (dry-run mode) " + shlex.join(cmds)

        return subprocess.check_output(cmds).decode("utf-8")


class Format(str,Enum):
    TEXT = "text"
    YAML = "yaml"

@dataclass
class Bundle:

    charms: list[Charm]

    @classmethod
    def from_status(cls, content: str, format: Format | str = Format.TEXT):
        parsers = {
            Format.TEXT: TextParser,
            Format.YAML: YAMLParser
        }
        normalized_format = Format(format)

        return parsers[normalized_format].parse(content)


class YAMLParser:

    @staticmethod
    def parse(content: str):
        data = yaml.safe_load(content)

        return Bundle([
            Charm(app["charm-name"], int(app["charm-rev"]), app.get("charm-channel"))
            for _, app in data["applications"].items()
        ])


class TextParser:
    """
    Parse a juju status output to find the charms deployed and their metadata (channel, revision, etc)

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
        m = TextParser.word_with_leading_spaces.match(mystring)
        if m:
            return mystring[m.start():m.end()]
        return ""

    @staticmethod
    def parse_line(line, indices):
        return [line[start:end].strip() for start, end in indices]

    @staticmethod
    def parse(content: str):
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
        ends=[s.end() for s in white_spaces.finditer(header)]
        indices = list(zip([0]+ends, ends+[-1]))

        # Columns names
        columns = TextParser.parse_line(header, indices)

        # Second guess of width based on maximum width of values
        # This is due to the fact that some columns the text extends to before the start
        # of the columns header (text aligned right)
        widths = [len(column) for column in columns]
        for line in table_lines[1:]:

            widths = list(map(max,zip(
                widths,
                [len(TextParser.extract_first_word(line[start:end])) for start, end in indices]
            )))

        # New guess
        ends = [start+width for (start,_), width in zip(indices, widths)]

        indices = list(zip([0]+ends[:-1], ends[:-1]+[-1]))

        data = [
            dict(zip(columns, TextParser.parse_line(line, indices)))
            for line in table_lines[1:]
            if line.strip()
        ]

        return Bundle([
            Charm(item["Charm"], int(item["Rev"]), item["Channel"])
            for item in data
            if item["Charm"]
        ])


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--file", required=True)
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Print release commands without executing them (default)",
    )
    action_group.add_argument(
        "--apply",
        dest="dry_run",
        action="store_false",
        help="Execute charmcraft release commands",
    )
    parser.set_defaults(dry_run=True)
    parser.add_argument("--format", choices=("text", "yaml"), default="text")
    parser.add_argument("--promote-to", choices=("beta", "candidate", "stable"), default="beta")
    parser.add_argument("--exclude", nargs="*", default=["mysql-k8s"])
    args = parser.parse_args()

    with open(args.file) as fid:
        bundle = Bundle.from_status(fid.read(), args.format)

    for charm in bundle.charms:
        if not charm.name in args.exclude:
            try:
                print(charm.promote_version(args.promote_to, args.dry_run))
            except ValueError as err:
                print(f"ERROR: skipping {charm.name} due to failure in promotion. Reason: {type(err).__name__} - Details: {','.join(err.args)}")
            except PermissionError as err:
                print(
                        f"WARNING: skipping '{charm.name}' due to missing permissions. Add it to --exclude to avoid this warning.",
                        file=sys.stderr,
                )
            except RuntimeError as err:
                print(
                    f"WARNING: skipping '{err.args[0]}' after command failure: {err.args[1]}",
                    file=sys.stderr,
                )
        else:
            print(f"WARNING: excluding charm {charm.name} (see --exclude flag)", file=sys.stderr)
