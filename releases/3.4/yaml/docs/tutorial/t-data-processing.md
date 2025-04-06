# Distributed data processing

[Apache Spark](https://spark.apache.org/) is an open-source unified analytics engine for large-scale data processing.

Charmed Apache Spark prvodes you with multiple options to run your Spark jobs:

* PySpark
* Spark Submit
* Scala shell

<!-- Expand the list to be exhaustive -->

For this tutorial we will use PySpark and Spark Submit.

## PySpark shell

The `spark-client` snap comes with a built-in Python shell where we can execute commands interactively against an Apache Spark cluster using the Python programming language.

To proceed, run the PySpark interactive CLI:

```bash
spark-client.pyspark --username spark --namespace spark
```

Once the shell is open and ready, you should see a prompt similar to the following:

```
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version 3.4.2
      /_/

Using Python version 3.10.12 (main, Jan 17 2025 14:35:34)
Spark context Web UI available at http://10.181.60.89:4040
Spark context available as 'sc' (master = k8s://https://10.181.60.89:16443, app id = spark-79ab7a21242c4a81bc88c1f71348c102).
SparkSession available as 'spark'.
>>>
```

When you open the PySpark shell, Charmed Apache Spark spawns a couple of executor K8s pods in the background to process commands. 
You can see them by fetching the list of pods in the `spark` namespace in a separate shell:

```bash
kubectl get pods -n spark
```

You should see output lines similar to the following:

```bash
pysparkshell-xxxxxxxxxxxxxxxx-exec-1              1/1     Running            0          xs
pysparkshell-xxxxxxxxxxxxxxxx-exec-2              1/1     Running            0          xs
```

As you can see, PySpark spawned two executor pods within the `spark` namespace. This is the namespace that we provided as a value to the `--namespace` argument when launching `spark-client.pyspark`. It's in these executor pods that data is cached and the computation will be executed, therefore creating a computational architecture that can horizontally scale to large datasets ("big data"). 

On the other hand, the PySpark shell started by the `spark-client` snap will act as a `driver`, controlling and orchestrating the operations of the executors. More information about the Apache Spark architecture can be found in the [Apache Spark documentation](https://spark.apache.org/docs/latest/cluster-overview.html).

The PySpark shell is just like a regular Python shell with Apache Spark Context that can be easily accessed with variables `sc` and `spark` respectively. You can even see this printed in its welcome screen.

### Hello world 

Let's start by printing a simple 'hello, world!', just like you'd do in a regular Python shell:

```python
print('hello, world!')
```

You should see the phrase printed immediately.

### Counting vowels

Let's try a simple example of counting the number of vowel characters in a string.

Using PySpark shell, run the following to add the string variable `lines` that we are going to use:

```python
lines = """Canonical's Charmed Data Platform solution for Apache Spark runs Spark jobs on your Kubernetes cluster.
You can get started right away with MicroK8s - the mightiest tiny Kubernetes distro around! 
The spark-client snap simplifies the setup process to get you running Spark jobs against your Kubernetes cluster. 
Apache Spark on Kubernetes is a complex environment with many moving parts.
Sometimes, small mistakes can take a lot of time to debug and figure out.
"""
```

Now use the following code to add a function that returns the number of vowel characters in a string:

```python
def count_vowels(text: str) -> int:
  count = 0
  for char in text:
    if char.lower() in "aeiou":
      count += 1
  return count
```

To test this function, the string `lines` can now be passed into it so the number of vowels will be returned to the console as follows:

```python
>>> count_vowels(lines)
134
```

Since Apache Spark is a distributed processing framework, we can split up this task and parallelize it over multiple executor pods. This parallelization can be done as simply as:

```python
>>> from operator import add
>>> spark.sparkContext.parallelize(lines.splitlines(), 2).map(count_vowels).reduce(add)
134
```

Here, we split the data into two executors (passed as an argument to `parallelize` function), generating a distributed data structure, e.g. RDD[str], where each line is stored in one of the (possibly many) executors. The number of vowels in each line is then computed, line by line, with the `map` function, and then the numbers are aggregated and added up to calculate the total number of occurrences of vowel characters in the entire dataset. This kind of parallelization of tasks is particularly useful in processing very large data sets which helps to reduce the processing time significantly, and it is generally referred to as the MapReduce pattern.

Now leave the PySpark shell: run `exit()` or press `Ctrl + D` key combination.

### Dataset distributed processing

For Big Data applications you may want to use bigger datasets then fir into a single string variable.

Let's download a sample dataset, store it in S3 object storage, and do some simple processing with PySpark.

#### Dataset

For the purpose of this tutorial, we will use a sample dataset from Kaggle with Twitter posts.
We will process this dataset on multiple Apache Spark executors to count the number of Twits with the word "Ubuntu" in them.

First things first, let's download the dataset to the VM:

```bash
curl -L -o ./twitter.zip https://www.kaggle.com/api/v1/datasets/download/thoughtvector/customer-support-on-twitter
```

Now let's install zip and extract the archive:

```bash
sudo apt install zip
unzip twitter.zip
```

Now that we have the files on the VM, let's upload them to our S3 storage:

```bash
aws s3 cp ./twcs/twcs.csv s3://spark-tutorial/twitter.csv --checksum-algorithm SHA256
```

The dataset is stored now in our S3-compatible MinIO instance - in the `spark-tutorial` bucket with the filename `twitter.csv`. You can check this by listing all files in the bucket:

```bash
aws s3 ls spark-tutorial
```

#### Distributed dataset processing

For distributed and parallel processing of data Apache Spark actively uses the concept of a [resilient distributed dataset (RDD)](https://spark.apache.org/docs/latest/rdd-programming-guide.html#resilient-distributed-datasets-rdds), which is a fault-tolerant collection of elements that can be operated on in parallel across the nodes of the cluster. 
There are two ways to create RDDs: parallelizing an existing collection in a program, or referencing a dataset in an external storage system.

Now that the dataset is stored in S3 we can access through PySpark.
Let's start PySpark:

```bash
spark-client.pyspark --username spark --namespace spark
```

Now create an RDD from our sample dataset:

```bash
rdd = spark.read.csv("s3a://spark-tutorial/twitter.csv", header=True).rdd
```

Count the number of tweets (lines in CSV) with "text" field containing "Ubuntu" in a case insensitive way:

```bash
count = rdd.map(lambda row: row['text']).map(lambda cell: 1 if isinstance(cell, str) and "ubuntu" in cell.lower() else 0).reduce(add)
```

```bash
print("Number of tweets containing Ubuntu:", count)
```

For more information on Spark jobs, see the web GUI by the link from the PySpark welcome screen:

http://10.181.60.89:4040/

## Spark submit

Interactive shells are a great way to experiment and learn the basics of Apache Spark. For a more advanced use case, jobs can be submitted to the Apache Spark cluster as scripts using `spark-submit`. 

```bash

```

