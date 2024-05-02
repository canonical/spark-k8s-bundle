#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import argparse
import random

from pyspark.sql import SparkSession
from pyspark.sql.types import LongType, StructField, StructType

parser = argparse.ArgumentParser("TestIceberg")
parser.add_argument("--num_rows", "-n", type=int)
args = parser.parse_args()
num_rows = args.num_rows

# Create Spark session
spark = SparkSession.builder.appName("IcebergExample").getOrCreate()

# Create schema
schema = StructType(
    [StructField("row_id", LongType(), True), StructField("row_val", LongType(), True)]
)

# Generate 'num_rows' number of random rows to be inserted.
data = []
for idx in range(num_rows):
    row = (idx + 1, random.randint(1, 100))
    data.append(row)

# Create a data frame and write it
df = spark.createDataFrame(data, schema)
df.writeTo("demo.foo.bar").create()

# Read back the inserted data and count the number of rows
df = spark.table("demo.foo.bar")
count = df.count()

# Print the number of rows
print(f"Number of rows inserted: {count}")
