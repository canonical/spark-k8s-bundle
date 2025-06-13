#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.

# See LICENSE file for licensing details.

import json
from pathlib import Path
import sys
import pandas as pd

def read_data(result_files: list[str]) -> list[dict]:
    rows = []
    for file in result_files:
        with open(file) as f:
            rows.append(json.load(f))
    return rows

def main():
    result_files = sys.argv[1:]
    data = read_data(result_files=result_files)
    df = pd.DataFrame(data)
    print(df)
    tests = df['tox-env'].unique()
    dimensions = [col for col in df.columns if col not in ('tox-env', 'status')]

    rows = []
    for dim in dimensions:
        for val in sorted(df[dim].dropna().unique(), key=lambda x: (x == '', x)):
            row = {'Matrix': dim, 'Value': val}
            for test in tests:
                subset = df[(df[dim] == val) & (df['tox-env'] == test)]
                if subset.empty:
                    cell = ''
                elif (subset['status'] == 'fail').any():
                    cell = '❌'
                else:
                    cell = '✅'
                row[test] = cell
            rows.append(row)

    final = pd.DataFrame(rows)
    content = final.to_markdown(index=False)

    with open("matrix-summary.md", "w") as f:
        f.write(content)
        f.flush()

if __name__ == "__main__":
    main()