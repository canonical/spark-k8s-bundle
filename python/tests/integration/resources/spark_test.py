import argparse
from random import random
from time import sleep

from pyspark.sql import SparkSession

parser = argparse.ArgumentParser("TestIceberg")
parser.add_argument("--textfile", "-f", type=str)
args = parser.parse_args()

file_uri = args.textfile
print(f"File: {file_uri}")

# Create Spark session
spark = SparkSession.builder.appName("SimpleExample").getOrCreate()
print(f"spark: {spark}")

text_file = spark.read.text(file_uri)

# give some buffer to send metrixs
sleep(10)
print(f"Number of lines {text_file.count()}")
