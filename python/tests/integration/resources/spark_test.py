import argparse
from random import random
from time import sleep

from pyspark.sql import SparkSession

parser = argparse.ArgumentParser("TestIceberg")
parser.add_argument("--bucket", "-b", type=str)
args = parser.parse_args()
bucket = args.bucket
print(f"bucket: {bucket}")
# Create Spark session
spark = SparkSession.builder.appName("SimpleExample").getOrCreate()
print(f"spark: {spark}")
text_file = spark.read.text(f"s3a://{bucket}/example.txt")
# give some buffer to send metrixs
sleep(10)
print(f"Number of lines {text_file.count()}")
