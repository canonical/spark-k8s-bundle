---
myst:
  html_meta:
    description: "How-to guide for configuring and running Apache Spark Streaming jobs against Apache Kafka on Kubernetes using structured streaming."
---

(how-to-streaming-jobs)=
# How to run Apache Spark Streaming against Apache Kafka

The following guide is to set up Apache Spark for structured streaming with Apache Kafka. 

As a pre-requisite, [Juju](https://juju.is/docs/olm/install-juju) has to be installed together with a kubernetes-based juju controller.

## Setup

First, create a fresh Juju model to be used as a workspace for spark-streaming experiments:

```shell
juju add-model spark-streaming
```

Deploy the Apache ZooKeeper and the Apache Kafka k8s-charms. Single units should be enough. 

```shell
juju deploy zookeeper-k8s --series=jammy --channel=edge

juju deploy kafka-k8s --series=jammy --channel=edge

juju integrate  kafka-k8s  zookeeper-k8s
```

Deploy a test producer application, to write messages to Charmed Apache Kafka:

```shell
juju deploy kafka-test-app --series=jammy --channel=edge --config role=producer --config topic_name=spark-streaming-store --config num_messages=1000

juju integrate kafka-test-app  kafka-k8s
```

To consume these messages we need to establish a connection between Apache Spark and Apache Kafka, which requires credentials.

We need to deploy the `data-integrator` charm, which performs credential retrieval:

```shell
juju deploy data-integrator --series=jammy --channel=edge --config extra-user-roles=consumer,admin --config topic-name=spark-streaming-store

juju integrate data-integrator kafka-k8s 

juju run-action data-integrator/0 get-credentials --wait 
```

```{note}
We are using the service account set up in the previous examples.
```

We need to set up the environment in a Kubernetes pod launched in the same namespace as the Juju model (i.e. `spark-streaming` in this example).

The pod specification yaml goes as below:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: testpod
spec:
  containers:
  - image: ghcr.io/canonical/charmed-spark:3.4.1-22.04_stable
    name: spark
    ports:
    - containerPort: 18080
    command: ["sleep"]
    args: ["3600"]
```

Create the pod in the same namespace as the Juju model.

Launch a Bash shell inside the test pod. 

```shell
kubectl apply -f ./testpod.yaml --namespace=spark-streaming
kubectl exec -it testpod -n spark-streaming -- /bin/bash
```

Create a Kubernetes cluster configuration within the test pod shell session to be able to work with `spark-client`.

Launch a `pyspark` shell to read the structured stream from Apache Kafka.

```shell
cd /home/spark
mkdir .kube
cat > .kube/config << EOF
<<KUBECONFIG CONTENTS>>
EOF

spark-client.service-account-registry create --username hello --namespace spark-streaming

spark-client.service-account-registry list

spark-client.pyspark --username hello --namespace spark-streaming --conf spark.executor.instances=1 --conf spark.jars.ivy=/tmp --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0
```

Within the `pyspark` shell, now use the credentials retrieved previously to read stream from Apache Kafka.

```python
from pyspark.sql.functions import udf
from json import loads

username="relation-8"
password="iGvE6HrCru1vqEsUdgRTsZKlOLqbebMJ"
lines = spark.readStream \
          .format("kafka") \
          .option("kafka.bootstrap.servers", "kafka-k8s-0.kafka-k8s-endpoints:9092") \
          .option("kafka.sasl.mechanism", "SCRAM-SHA-512") \
          .option("kafka.security.protocol", "SASL_PLAINTEXT") \
          .option("kafka.sasl.jaas.config", f'org.apache.kafka.common.security.scram.ScramLoginModule required username={username} password={password};') \
          .option("subscribe", "spark-streaming-store") \
          .option("includeHeaders", "true") \
          .load()

get_origin = udf(lambda x: loads(x)["origin"])
count = lines.withColumn("origin", get_origin(col("value"))).select("origin")\
          .groupBy("origin", "partition")\
          .count()

count.awaitTermination()
```

