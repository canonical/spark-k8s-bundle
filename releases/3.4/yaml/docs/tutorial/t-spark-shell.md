# Interacting with Spark using interactive shell

Spark comes with an interactive shell that provides a simple way to learn the API. It is available in either Scala or Python. In this section, we're going to play around a bit with Spark's shell to interact directly with the Spark cluster.

## PySpark shell

Spark comes with a built-in Python shell where we can run commands interactively against the Spark cluster using the Python programming language.

PySpark shell can be launched with the `spark-client` snap like this:

```bash
spark-client.pyspark \
  --username spark --namespace spark
```

Once the shell is open and ready, you should see a prompt similar to the following:

```
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version 3.4.1
      /_/

Using Python version 3.10.12 (main, Jun 11 2023 05:26:28)
Spark context Web UI available at http://172.31.29.134:4040
Spark context available as 'sc' (master = k8s://https://172.31.29.134:16443, app id = spark-b364a0a9a2cb41f3a713c62b900fbd82).
SparkSession available as 'spark'.
>>> 
```

When you open the PySpark shell, Spark spawns a couple of executor pods in the background to process commands. You can see them by fetching the list of pods in the `spark` namespace in a separate shell.

```bash
kubectl get pods -n spark
```

You should see output lines similar to the following:
```bash
pysparkshell-xxxxxxxxxxxxxxxx-exec-1              1/1     Running            0          xs
pysparkshell-xxxxxxxxxxxxxxxx-exec-2              1/1     Running            0          xs
```

As you can see, PySpark spawned two executor pods within the `spark` namespace. This is the namespace that we provided as a value to the `--namespace` argument when launching `pyspark`. It's in these executor pods that data is cached and the computation will be executed, therefore creating a computational architecture that can horizontally scale to large datasets ("big data"). On the other hand, the PySpark shell started by the `spark-client` snap will act as a `driver`, controlling and orchestrating the operations of the executors. More information about the Spark architecture can be found [here](https://spark.apache.org/docs/latest/cluster-overview.html).

The Spark context and session are already preloaded into the shell and can be easily accessed with variables `sc` and `spark` respectively. You can even see this printed in the logs above, where upon initialization, the PySpark shell says `Spark context available as 'sc'` and `SparkSession available as 'spark'`. This shell is just like a regular Python shell, with Spark context loaded on top of it.

To start, you can print `hello, world!` just like you'd do in a Python shell.

```python
>>> print('hello, world!')

hello, world!
```

Let's try a simple example of counting the number of vowel characters in a string. The following is the string that we are going to use:

```python
lines = """Canonical's Charmed Data Platform solution for Apache Spark runs Spark jobs on your Kubernetes cluster.
You can get started right away with MicroK8s - the mightiest tiny Kubernetes distro around! 
The spark-client snap simplifies the setup process to get you running Spark jobs against your Kubernetes cluster. 
Spark on Kubernetes is a complex environment with many moving parts.
Sometimes, small mistakes can take a lot of time to debug and figure out.
"""
```

The following is a function that returns the number of vowel characters in the string:

```python
def count_vowels(text: str) -> int:
  count = 0
  for char in text:
    if char.lower() in "aeiou":
      count += 1
  return count
```

To test this function, the string `lines` can now be passed into it and the number of vowels is printed to the console as follows:

```python
>>> count_vowels(lines)
128
```

Since Spark is a distributed processing framework, we can split up this task and parallelize it over multiple executor pods. This parallelization can be done as simply as:

```python
>>> from operator import add
>>> spark.sparkContext.parallelize(lines.splitlines(), 2).map(count_vowels).reduce(add)
128
```

Here, we split the data into the two executors (passed as an argument to `parallelize` function), generating a distributed data structure, e.g. RDD[str], where each line is stored in one of the (possibly many) executors. The number of vowels in each line is then computed, line by line, with the `map` function, and then the numbers are aggregated and added up to calculate the total number of occurrences of vowel characters in the entire dataset. This kind of parallelization of tasks is particularly useful in processing very large data sets which helps to reduce the processing time significantly, and it is generally referred to as the MapReduce pattern.

To exit from PySpark shell, you can simply run `exit()` or press `Ctrl` + Z key combination.

## Scala shell

Spark comes with a built-in interactive Scala shell as well. Enter the following command to enter an interactive Scala shell:

```bash
spark-client.spark-shell --username spark --namespace spark --num-executors 4
```

Notice how we can specify the number of executors when initializing the Spark shell (which by default would be `2`). Once the shell is open and ready, you should see a prompt similar to the following:

```
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 3.4.1
      /_/
         
Using Scala version 2.12.17 (OpenJDK 64-Bit Server VM, Java 11.0.20.1)
Type in expressions to have them evaluated.
Type :help for more information.

scala> 
```

Just as in the PySpark shell, the Spark context and Spark session are readily available in the shell as `sc` and `spark` respectively. Moreover, new executor pods are created in `spark` namespace to run the commands, just like with the PySpark shell.

The example of counting the vowel characters can be equivalently run in Scala with the following lines:

```scala
val lines = """Canonical's Charmed Data Platform solution for Apache Spark runs Spark jobs on your Kubernetes cluster.
You can get started right away with MicroK8s - the mightiest tiny Kubernetes distro around! 
The spark-client snap simplifies the setup to run Spark jobs against your Kubernetes cluster. 
Spark on Kubernetes is a complex environment with many moving parts.
Sometimes, small mistakes can take a lot of time to debug and figure out.
"""

def countVowels(text: String): Int = {
  text.toLowerCase.count("aeiou".contains(_))
}

sc.parallelize(lines.split("\n"), 2).map(countVowels).reduce(_ + _)
```

To exit from the Scala shell, simply press `Ctrl + C` key combination.

Interactive shells are a great way to try out experiments and to learn the basics of the Spark. For a more advanced usage, jobs can be submitted to the Spark cluster as scripts using `spark-submit`. That's what we will do in the next section with [Spark Submit](/t/13231).
