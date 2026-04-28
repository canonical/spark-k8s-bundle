import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from json import loads

# Create a Spark Session
spark = SparkSession.builder.appName("SparkStreaming").getOrCreate()

# Read username, password and endpoint from command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--kafka-username", "-u",
                help="The username to authenticate to Kafka",
                required=True)
parser.add_argument("--kafka-password", "-p",
                help="The password to authenticate to Kafka",
                  required=True)
parser.add_argument("--kafka-endpoint", "-e",
                  help="The bootstrap server endpoint",
                    required=True)
parser.add_argument("--kafka-topic", "-t",
                  help="The Kafka topic to subscribe to",
                    required=True)
args = parser.parse_args()
username=args.kafka_username
password=args.kafka_password
endpoint=args.kafka_endpoint
topic=args.kafka_topic

# Authenticating with Kafka and reading the stream from the topic
lines = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", endpoint) \
        .option("kafka.sasl.mechanism", "SCRAM-SHA-512") \
        .option("kafka.security.protocol", "SASL_PLAINTEXT") \
        .option(
          "kafka.sasl.jaas.config",
          f'org.apache.kafka.common.security.scram.ScramLoginModule required username="{username}" password="{password}";'
        ).option("subscribe", topic) \
        .option("includeHeaders", "true") \
        .load()

# User defined function that returns the origin of one particular event
get_origin = udf(lambda x: loads(x)["origin"])

# Group by origin of the event and count number of event for each origins
count = lines.withColumn(
            "origin",
            get_origin(col("value"))
          ).select("origin").groupBy("origin").count()

# Start writing the result to console
query = count.writeStream.outputMode("complete").format("console").start()

# Keep doing this until the job is terminated
query.awaitTermination()
