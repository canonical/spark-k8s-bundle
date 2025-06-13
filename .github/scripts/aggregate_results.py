#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.

# See LICENSE file for licensing details.

"""Aggregate results from test matrix into a tabular form"""

import json
import sys
import pandas as pd

FOOTNOTES = """

Legend:
✅: All tests passed for this dimension and this tox environment
❌: Some tests are failing for this dimension and this tox environment
empty: No test was run for this dimension and this tox environment

"""

def read_results(result_files: list[str]) -> list[dict]:
    """
    Read the test run result from the given list of JSON files.

    Args:
        result_files (list[str]): List of file paths to JSON result files.

    Returns:
        list[dict]: List of parsed JSON objects representing test results.
    """
    rows = []
    for file in result_files:
        with open(file) as f:
            rows.append(json.load(f))
    return rows


def main():
    # Get the list of result file paths from command-line arguments
    result_files = sys.argv[1:]

    # Read all test results into a list of dictionaries
    data = read_results(result_files=result_files)
    df = pd.DataFrame(data)

    # Identify all distinct tox environments. These are to be rendered as column heads
    tests = df["tox-env"].unique()

    # Identify dimensions (matrix parameters) by excluding 'tox-env' and 'status'
    dimensions = [col for col in df.columns if col not in ("tox-env", "status")]

    rows = []

    # For each matrix dimension (e.g., spark-version, bundle-backend, etc.)
    for dim in dimensions:
        # For each unique value in the dimension, sorted for consistent display
        for val in sorted(df[dim].dropna().unique(), key=lambda x: (x == "", x)):
            row = {"Matrix": dim, "Value": val}

            # For each tox env type, calculate pass/fail/not-run status for that value
            for test in tests:
                # Filter DataFrame for rows matching current matrix value and tox-env
                subset = df[(df[dim] == val) & (df["tox-env"] == test)]
                if subset.empty:
                    cell = ""  # No runs with this combination
                elif (subset["status"] == "fail").any():
                    cell = "❌"  # One or more failures for this combination
                else:
                    cell = "✅"  # All runs passed for this combination
                row[test] = cell

            # Append the constructed row to the result table
            rows.append(row)

    # Convert the aggregated results into a new DataFrame, and create summary in markdown table
    final = pd.DataFrame(rows)
    content = final.to_markdown(index=False)

    # Write the table to a file for use in GitHub summary or artifacts
    with open("matrix-summary.md", "w") as f:
        f.write(content)
        f.write(FOOTNOTES)
        f.flush()


if __name__ == "__main__":
    main()