from operator import add

from pyspark.sql import SparkSession


def contains_ubuntu(text):
    return 1 if isinstance(text, str) and "ubuntu" in text.lower() else 0


# Create a Spark session
spark = SparkSession.builder.appName("CountUbuntuTweets").getOrCreate()

# Read the CSV file into a DataFrame and convert to RDD
rdd = spark.read.csv("s3a://spark-tutorial/twitter.csv", header=True).rdd

# Count how many rows contain the word "ubuntu" in the "text" column
count = (
    rdd.map(lambda row: row["text"])  # Extract the "text" column
    .map(contains_ubuntu)  # Apply the contains_ubuntu function
    .reduce(add)  # Sum all the 1 and 0 to get the total number of matches
)

# Print the result
print(f"Number of tweets containing Ubuntu: {count}")

spark.stop()
