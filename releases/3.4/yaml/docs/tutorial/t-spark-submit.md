# Submitting Jobs using Spark Submit

Spark comes with a command called `spark-submit` which can be used to submit Spark jobs to the cluster from scripts written in high level languages like Python and Scala. For a quick example, let's gather the statements that we ran in the Python shell earlier and put them together in a script. The script looks like the following:


```python
from operator import add
from pyspark.sql import SparkSession


def count_vowels(text: str) -> int:
  count = 0
  for char in text:
    if char.lower() in "aeiou":
      count += 1
  return count

# Create a Spark session 
spark = SparkSession\
        .builder\
        .appName("CountVowels")\
        .getOrCreate()

lines = """Canonical's Charmed Data Platform solution for Apache Spark runs Spark jobs on your Kubernetes cluster.
You can get started right away with MicroK8s - the mightiest tiny Kubernetes distro around! 
The spark-client snap simplifies the setup process to run Spark jobs against your Kubernetes cluster. 
Spark on Kubernetes is a complex environment with many moving parts.
Sometimes, small mistakes can take a lot of time to debug and figure out.
"""

n = spark.sparkContext.parallelize(lines.splitlines(), 2).map(count_vowels).reduce(add)
print(f"The number of vowels in the string is {n}")

spark.stop()
```

We've added a few more lines to what we've executed so far. The Spark session, which would be available by default in a PySpark shell, needs to be explicitly created. Also, we've added `spark.stop` at the end of the file to stop the Spark session after completion of the job.

Let's save the aforementioned script in a file named `count_vowels.py`. Once saved, let's copy it to the S3 bucket because it needs to be accessible to pods in kubernetes. In fact, when submitting the job, the driver won't be running in the local machine but on a K8s pod, hence the script needs to be downloaded and then executed remotely in a dedicated pod. Copying the file to the S3 bucket can be done by the following command.

```bash
aws s3 cp count_vowels.py s3://spark-tutorial/count_vowels.py
#
# upload: ./count_vowels.py to s3://spark-tutorial/count_vowels.py 
```

You can verify whether the file has been copied to the S3 bucket either using the MinIO Console UI or using the following command:

```bash
aws s3 ls spark-tutorial
# 
# 2024-02-05 05:09:44        925 count_vowels.py
```

Now that the script has been uploaded to S3, we can run `spark-submit` and specify the path of the script in S3 as an argument.

```bash
spark-client.spark-submit \
    --username spark --namespace spark \
    --deploy-mode cluster \
    s3a://spark-tutorial/count_vowels.py
```

When you run the command, you'll see log output in the console with information about the state of the pods executing the task. The state of the pods transitions from `ContainerCreating` to `Running` and then finally to `Completed`. The state of the pods can also be viewed using the `kubectl` command in a new shell. 

```bash
watch -n1 "kubectl get pods -n spark"
```

You should see output similar to the following:
```
NAME                                      READY   STATUS      RESTARTS   AGE
...
count-vowels-py-f6af998d77ce02d0-driver   1/1     Running     0          17s
countvowels-2975f78d77ce2e6f-exec-2       1/1     Running     0          6s
countvowels-2975f78d77ce2e6f-exec-1       1/1     Running     0          6s
```

Among these pods, as explained before, we have a "driver" pod, that will be executing the script and orchestrating/coordinating the other two executor pods. If you observe closely the status of the pods while the job is being submitted, it's the driver pod that gets created first. The driver pod spawns executor pods to execute the jobs. Once the job completes, the driver and the executor pods are transitioned to `Completed` state. We can see the job execution logs by viewing pod logs of the driver pod.

To view the pod logs, we first need to identify the name of the driver pod. You can do that with `kubectl` and some text filtering as:

```bash
pod_name=$(kubectl get pods -n spark | grep "count-vowels-.*-driver" | tail -n 1 | cut -d' ' -f1)
echo $pod_name
```

Once we have identified the pod name, we can see the pod logs with `kubectl logs` command. To filter out just the output line from the logs, `grep` can be used together with `kubectl logs`.

```bash
# View entire pod logs
kubectl logs $pod_name -n spark 

# View only the line containing the output
kubectl logs $pod_name -n spark | grep "The number of vowels in the string is"
# 
# 2024-02-05T05:47:09.183Z [entrypoint] The number of vowels in the string is 128
```

Often times, the data files to be processed contain a huge amount of data, and it's common to store them in S3 and then have jobs read data from there in order to process it. The example program that we have discussed earlier can be extended so that the text for our vowel character counting job is now fetched directly from a file in S3. For that, let's download a sample file and then copy it to the S3 bucket as follows:

```bash
# Download a sample text file
wget "https://raw.githubusercontent.com/canonical/spark-client-snap/3.4/edge/README.md"

aws s3 cp README.md s3://spark-tutorial/README.md
```

Now, let's modify the Python script `count_words.py` to process the lines read from the file in S3 instead.


```python
from operator import add
from pyspark.sql import SparkSession


def count_vowels(text: str) -> int:
  count = 0
  for char in text:
    if char.lower() in "aeiou":
      count += 1
  return count

# Create a Spark session 
spark = SparkSession\
        .builder\
        .appName("SubmitExample")\
        .getOrCreate()

lines = spark.sparkContext.textFile("s3a://spark-tutorial/README.md")

n = lines.map(count_vowels).reduce(add)
print(f"The number of vowels in the string is {n}")

spark.stop()
```

Now, let's copy this script to S3 with the same command as before, and then run it with `spark-submit`

```bash
aws s3 cp count_vowels.py s3://spark-tutorial/count_vowels.py

spark-client.spark-submit \
    --username spark --namespace spark \
    --deploy-mode cluster \
    s3a://spark-tutorial/count_vowels.py
```

As before, you can get the results from pod logs with the following commands:

```bash
pod_name=$(kubectl get pods -n spark | grep "count-vowels-.*-driver" | tail -n 1 | cut -d' ' -f1)

kubectl logs $pod_name -n spark | grep "The number of vowels in the string is"
```

In this section, we learned how to submit jobs using `spark-submit`. In the [next section](/t/13230), we'll learn how to process streaming data in Spark.