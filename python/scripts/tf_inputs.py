"""TF input parser script.

This script provides an easy way to transform the 'variables.tf' file into
a compact table representation for a readme.
"""

from textwrap import shorten
from typing import TypedDict

import hcl2


class TFInput(TypedDict):
    """Table fields."""

    name: str
    description: str
    type: str
    nullable: bool
    default: str


def _main(release: str) -> None:
    with open(f"../releases/{release}/terraform/variables.tf", "r") as file:
        variables = hcl2.load(file)["variable"]

    parsed_inputs: list[TFInput] = []
    for variable in variables:
        name, definition = next(iter(variable.items()))

        new_entry = TFInput(
            name=name,
            description=shorten(definition.get("description", ""), 79),
            type=(
                str(content)
                if len(content := definition.get("type", "")) < 10
                else "map"
            ),
            nullable=definition.get("nullable", True),
            default=(
                str(content).replace("None", "null")
                if isinstance(
                    (content := definition.get("default", "")),
                    (str, int, bool, type(None)),
                )
                else "See variables.tf"
            ),
        )
        parsed_inputs.append(new_entry)

    data = [["Variable", "Description", "Type", "Nullable", "Default"]] + [
        list(var.values()) for var in parsed_inputs
    ]
    md_table = "\n".join(
        [
            "| " + " | ".join(map(str, row)) + " |"
            for row in [data[0], ["---"] * len(data[0])] + data[1:]
        ]
    )
    print(md_table)


if __name__ == "__main__":
    print("Release 3.4")
    _main("3.4")
    print("\n\nRelease 3.5")
    _main("3.5")
