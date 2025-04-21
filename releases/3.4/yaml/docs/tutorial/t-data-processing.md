# 2. Distributed data processing

In this section, you will learn how to use PySpark and Spark Submit to run your Spark jobs. Make sure to finish setting up the environment from the [Environment setup](/t/13233) page.

## PySpark shell

The `spark-client` snap comes with a built-in Python shell where we can execute commands interactively against an Apache Spark cluster using the Python programming language.

To proceed, run the PySpark interactive CLI, specifying the service account to be used for retrieving configurations and running the executor pods (see more information below)

```bash
spark-client.pyspark --username spark --namespace spark
```

Once the shell is open and ready, you should see a welcome screen similar to the following:

```text
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
You can see them by fetching the list of pods in the `spark` namespace in a separate VM shell:

```bash
kubectl get pods -n spark
```

You should see output lines similar to the following:

```bash
NAME                                              READY   STATUS             RESTARTS   AGE
pysparkshell-xxxxxxxxxxxxxxxx-exec-1              1/1     Running            0          5s
pysparkshell-xxxxxxxxxxxxxxxx-exec-2              1/1     Running            0          5s
```

As you can see, PySpark spawned two executor pods within the `spark` namespace. This is the namespace that we provided as a value to the `--namespace` argument when launching `spark-client.pyspark`. It's in these executor pods that data is cached and the computation will be executed, therefore creating a computational architecture that can horizontally scale to large datasets ("big data"). 

On the other hand, the PySpark shell started by the `spark-client` snap will act as a `driver`, controlling and orchestrating the operations of the executors. More information about the Apache Spark architecture can be found in the [Apache Spark documentation](https://spark.apache.org/docs/latest/cluster-overview.html).

The PySpark shell is just like a regular Python shell with Apache Spark Context that can be easily accessed with variables `sc` and `spark` respectively. You can even see this printed in its welcome screen.

### Counting vowels

Let's try a simple example of counting the number of vowel characters in a string.

Using PySpark shell, run the following to set the string variable `lines` that we are going to use:

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
count_vowels(lines)
```

As a result, you should see the value returned by the function: `137`. 
However, this approach does not leverage parallelization or the distributed processing capabilities of Apache Spark. It simply executes the Python code.

Since Apache Spark is designed for distributed processing, we can run this task in parallel across multiple executor pods. This parallelization can be achieved as simply as:

```python
from operator import add
spark.sparkContext.parallelize(lines.splitlines(), 2).map(count_vowels).reduce(add)
```

[note]
If you get an error message containing `java.io.InvalidClassException`, like this:

```text
java.io.InvalidClassException: org.apache.spark.scheduler.Task; local class incompatible: stream classdesc serialVersionUID = -3760150995365899213, local class serialVersionUID = -8788749905090789633
```

Make sure your Apache Spark image used on the drivers and executors has the same version of Apache Spark as your local spark.client.
You can do that by manually setting the version of image used on the cluster side:

```bash
spark-client.service-account-registry add-config --username spark --namespace spark --conf spark.kubernetes.container.image=ghcr.io/canonical/charmed-spark:3.4.2-22.04_edge
```
[/note]

Here, we split the data into two parts, generating a distributed data structure, where each line is stored in one of the (possibly many) executors.
The number of vowels in each line is computed, line by line, with the `count_vowels` function on each executor in parallel.
Then the numbers are aggregated and added up to calculate the total number of occurrences of vowel characters in the entire dataset.

This kind of parallelization of tasks is particularly useful in processing very large data sets which helps to reduce the processing time significantly, and it is generally referred to as the [MapReduce pattern](https://en.wikipedia.org/wiki/MapReduce).

The returned result should be the same as we've seen earlier, with a non-distributed version: `137`.

To continue with this tutorial, leave the PySpark shell: run `exit()` or press `Ctrl + D` key combination.

### Distributed data processing

Apache Spark is made to efficiently analyze large datasets across multiple nodes.
Often times, the data files to be processed contain a huge amount of data, and it’s common to store them in an S3 storage and then have jobs read data from there in order to process it.

Let's download a sample dataset, store it in an S3 object storage, and do some distributed processing with PySpark.

#### Prepare a dataset

For the purpose of this tutorial, we will use a dataset from Kaggle with over 3 million tweets: [Customer Support on Twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter).

If you download and check this dataset, you'll see it contains seven columns/fields, but we are only interested in the one with the header `text`.

The dataset takes more then 500 MB of disk space, and we will process it on multiple Apache Spark executors.

First, let's download the dataset to the VM:

```bash
curl -L -o ./twitter.zip https://www.kaggle.com/api/v1/datasets/download/thoughtvector/customer-support-on-twitter
```

Now let's install zip and extract the archive:

```bash
sudo apt install zip
unzip twitter.zip
```

This archive unpacks a directory called `twcs` with a single csv file of the same in it.
Let's upload it to our S3 storage:

```bash
aws s3 cp ./twcs/twcs.csv s3://spark-tutorial/twitter.csv --checksum-algorithm SHA256
```

Now the dataset is stored in our MinIO instance: in the `spark-tutorial` bucket with the filename `twitter.csv`.
You can check this by listing all files in the bucket:

```bash
aws s3 ls spark-tutorial
```

#### Distributed dataset processing

To demonstrate how simple it is to use distributed data processing in Charmed Apache Spark, let's count the number of tweets that mention Ubuntu.
Start the PySpark:

```bash
spark-client.pyspark --username spark --namespace spark
```

For distributed and parallel data processing Apache Spark actively uses the concept of a [resilient distributed dataset (RDD)](https://spark.apache.org/docs/latest/rdd-programming-guide.html#resilient-distributed-datasets-rdds), which is a fault-tolerant collection of elements that can be operated on in parallel across the nodes of the cluster.

Read CSV from S3 and create an RDD from our sample dataset:

```python
rdd = spark.read.csv("s3a://spark-tutorial/twitter.csv", header=True).rdd
```

Now that RDD can be used for parallel processing by multiple Apache Spark executors.

Count the number of tweets (lines in CSV) with "text" field containing "Ubuntu" in a case insensitive way:

```python
count = rdd.map(lambda row: row['text']).map(lambda cell: 1 if isinstance(cell, str) and "ubuntu" in cell.lower() else 0).reduce(add)
```

Here, we extract the value of the `text` column for each row and for each value we convert it to lower case and check whether it contains `ubuntu`. If it does, we return `1`, otherwise - `0`.
Finally, on a reduce step, we add up all values (ones and zeroes), resulting in the total number of rows that mention `ubuntu`.

To get the answer, we just need to print it:

```python
print("Number of tweets containing Ubuntu:", count)
```

The result should look similar to the following:

```text
Number of tweets containing Ubuntu: 54
```

## Run a script

Charmed Apache Spark comes with a command that can be used to submit Spark jobs to the cluster from scripts written in high-level languages like Python and Scala. For that purpose, we can use the `spark-submit` command from the `spark-client` snap.

### Prepare a script

For a quick example, let's see how it can be done using slightly refactored code from the previous section:

```python
from operator import add
from pyspark.sql import SparkSession

def contains_ubuntu(text):
    return 1 if isinstance(text, str) and "ubuntu" in text.lower() else 0

# Create a Spark session 
spark = SparkSession\
        .builder\
        .appName("CountUbuntuTweets")\
        .getOrCreate()

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
```

We’ve added a few more lines to what we’ve executed so far. The Apache Spark session, which would be available by default in a PySpark shell, needs to be explicitly created. Also, we’ve added `spark.stop()` at the end of the file to stop the Apache Spark session after completion of the job.

Let’s save the aforementioned script in a file named `count-ubuntu.py` and proceed further to run it.

### Run

When submitting a Spark job, the driver won’t be running in the local machine but on a K8s pod, hence the script needs to be downloaded and then executed remotely on Kubernetes in a dedicated pod.
For that reason, we'll copy the file to the S3 storage to be easily accessible from K8s pods.

Upload the file to the Multipass VM:

```bash
multipass transfer count-ubuntu.py spark-tutorial:count-ubuntu.py
```

where `spark-tutorial` is the name of the VM.

Copy the file to the S3-compatible storage:

```bash
aws s3 cp count-ubuntu.py s3://spark-tutorial/count-ubuntu.py
```

Now run the script by issuing the following command:

```bash
spark-client.spark-submit \
    --username spark --namespace spark \
    --deploy-mode cluster \
    s3a://spark-tutorial/count-ubuntu.py
```

The --deploy-mode cluster option tells Spark Submit to run the driver on a K8s pod.

When you execute the command, the console will display log output showing the state of the pods running the task.

While the `spark-submit` command spins up K8s pods and runs the script, you can check the K8s pods statuses by running the following command in a different shell on the VM:

```bash
watch -n1 "kubectl get pods -n spark"
```

You should see output similar to the following:

```text
NAME                                        READY   STATUS      RESTARTS   AGE
count-ubuntu-py-752c77960d097604-driver     1/1     Running     0          11s
countubuntutweets-a4b68a960d0982c4-exec-1   1/1     Running     0          8s
countubuntutweets-a4b68a960d0982c4-exec-2   0/1     Pending     0          8s
```

Here, we have a “driver” pod, that will be executing the script and spawning and coordinating the other two "executor" pods.
The state of the pods transitions from `Pending` to `Running` and then, finally, to `Completed`.

Once the job is completed, the driver and the executor pods are transitioned to the Completed state.
The executor pods are deleted automatically.

The script prints the result to the console output, but that's the driver's console.
To see the printed message, let's find the driver pod's name and filter the logs from it:

```bash
pod_name=$(kubectl get pods -n spark | grep "count-ubuntu-.*-driver" | tail -n 1 | cut -d' ' -f1)
kubectl logs $pod_name -n spark | grep "Number of tweets containing Ubuntu:"
```

The result should look similar to the following:

```text
2025-04-07T11:32:44.872Z [sparkd] Number of tweets containing Ubuntu: 54
```

By default, Apache Spark stores the logs of drivers and executors as pod logs in the local file systems, which are lost once the pods are deleted. Apache Spark can store these logs in a persistent object storage system, like S3, so that they can later be retrieved and visualised by a component called Spark History Server.