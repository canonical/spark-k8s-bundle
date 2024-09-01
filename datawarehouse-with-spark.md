# Data Warehousing with Spark
       
The use-case aims at setting up a minimal Data warehouse stack, able to consume and analyse streaming data. 

The use-case shows how to:
* Generate streaming data to be published to Kafka
* Use Spark streaming to consumer the data from Kafka and generate some real-time aggregation
* Real-time aggregation are written into a Hive table, persisted on a S3-compatible backend
* The Hive table is then imported and queried using Apache Kyuubi

The setup and integration make use of charms and Juju. 

## Setup Environment 

### Pre-Requisites

* MicroK8s: version 1.29-strict/stable
  * Add-ons:
    * `hostpath-storage`
    * `dns`
    * `rbac`
    * `storage`
    * `minio`
  
  Command:
  ```commandline
  sudo microk8s enable hostpath-storage dns rbac storage minio
  sudo snap alias microk8s.kubectl kubectl
  microk8s config > ~/.kube/config
  ```
* Juju: version 3.5/stable (3.5.3)

### Setup Bucket to be used with Spark

Refer to [Charmed Spark Documentation](https://charmhub.io/spark-k8s-bundle/docs/h-setup-k8s). Remember to create the `spark-events` object in the bucket. 

### Juju Models

#### Kafka

```juju add-model kafka```

> :warning: Issue #8 prevented to use the edge version that would have had a feature to expose the cluster outside of the Kubernetes cluster.

Use the following bundle:

```commandline
bundle: kubernetes
applications:
  admin:
    charm: data-integrator
    channel: latest/stable
    revision: 41
    scale: 1
    options:
      consumer-group-prefix: admin-cg
      extra-user-roles: admin
      topic-name: test-topic
    constraints: arch=amd64
  kafka:
    charm: kafka-k8s
    channel: 3/stable
    revision: 56
    resources:
      kafka-image: 43
    scale: 1
    constraints: arch=amd64
    storage:
      data: kubernetes,1,10240M
    trust: true
  producer:
    charm: kafka-test-app
    channel: latest/edge
    revision: 11
    scale: 1
    options:
      num_messages: 180
      role: producer
      topic_name: test-topic
    constraints: arch=amd64
  zookeeper:
    charm: zookeeper-k8s
    channel: 3/stable
    revision: 51
    resources:
      zookeeper-image: 29
    scale: 1
    constraints: arch=amd64
    storage:
      zookeeper: kubernetes,1,10240M
    trust: true
relations:
- - kafka:zookeeper
  - zookeeper:zookeeper
- - admin:kafka
  - kafka:kafka-client
```

Once the model is up and running, get the credentials of the Kafka cluster to be used in the Spark streaming job:

```commandline
$ juju run admin/0 get-credentials --model kafka
Running operation 6 with 1 task
  - task 7 on unit-admin-0

Waiting for task 7...
kafka:
  data: '...'
  endpoints: <KAFKA_ENDPOINT>
  password: <KAFKA_PASSWORD>
  tls: disabled
  topic: <KAFKA_TOPIC>
  username: <KAFKA_USERNAME>
  zookeeper-uris: ...
ok: "True"
```

Store somewhere the values of the placeholder above.

#### Spark

```juju add-model spark```

Use the following bundle:

> To simplify the deployment, I have only deployed one PostgreSQL instance, both related for auth-db and metastore

```commandline
bundle: kubernetes
applications:
  kyuubi:
    charm: kyuubi-k8s
    channel: latest/edge
    revision: 17
    resources:
      kyuubi-image: 2
    scale: 1
    options:
      namespace: spark
      service-account: kyuubi-engine
    constraints: arch=amd64
    trust: true
  metastore:
    charm: postgresql-k8s
    channel: 14/stable
    revision: 281
    resources:
      postgresql-image: 159
    scale: 1
    constraints: arch=amd64
    storage:
      pgdata: kubernetes,1,1024M
    trust: true
  s3:
    charm: s3-integrator
    channel: latest/edge
    revision: 17
    scale: 1
    options:
      bucket: spark
      endpoint: "http://10.152.183.128:80"
      path: spark-events
    constraints: arch=amd64
  history-server:
    charm: spark-history-server-k8s
    channel: 3.4/edge
    revision: 25
    resources:
      spark-history-server-image: 12
    scale: 1
    constraints: arch=amd64
  integration-hub:
    charm: spark-integration-hub-k8s
    channel: latest/edge
    revision: 10
    resources:
      integration-hub-image: 1
    scale: 1
    constraints: arch=amd64
    trust: true
relations:
- - integration-hub:s3-credentials
  - s3:s3-credentials
- - kyuubi:s3-credentials
  - s3:s3-credentials
- - history-server:s3-credentials
  - s3:s3-credentials
- - kyuubi:metastore-db
  - metastore:database
- - kyuubi:auth-db
  - metastore:database
- - kyuubi:spark-service-account
  - integration-hub:spark-service-account%  
```

Provide the S3-credentials via the action:

```commandline
uju run s3/leader sync-s3-credentials \
    access-key=<S3_ACCESS_KEY> \
    secret-key=<S3_SECRET_KEY>
```

The model should now be up and running.

Fetch important information from the deployment:

* Information from Kyuubi
  * username: `admin`
  * Kyuubi password:
    ```commandline
    $ juju run kyuubi/leader get-password
    Running operation 74 with 1 task
      - task 75 on unit-kyuubi-0
  
    Waiting for task 75...
    password: <KYUUBI_PASSWORD>
    ```
  * Kyuubi endpoint:
    ```commandline
    $ juju run kyuubi/leader get-jdbc-endpoint                                       ubuntu@ip-172-31-28-106
    Running operation 76 with 1 task
      - task 77 on unit-kyuubi-0
  
    Waiting for task 77...
    endpoint: <KYUUBI_ENDPOINT>
    ```
* Hive Metastore information (PostgreSQL backend):
  ```commandline
  $ juju ssh --model spark --container kyuubi kyuubi/0 cat /etc/spark8t/conf/hive-site.xml 
  <HIVE_CONF>
  ```

#### (Optional) Small environments

If you are in a small environment with limited resources, you can add the following configuration with the Integration hub:

```commandline
juju run integration-hub/0 add-config conf=spark.kubernetes.driver.request.cores=100m
juju run integration-hub/0 add-config conf=spark.kubernetes.executor.request.cores=100m
```

> :warning: Note that if you make a mistake sometimes it is not possible to remove the config (it happened to me with `spark.kubernetes.executor.request.cores`), where I tried to use both `remove-config` and `clear-config`, but the config would still linger around (Issue #2).

### Setup Edge node for Spark jobs

On the `kafka` namespace (Issue #1), create a pod to perform admin operations as well as trigger Spark jobs. 

Create a pod using the following YAML:

> :warning: we need to use kyuubi image because the `postgresql-*.jar` are not available in the charmed spark base image (see Issue #4 and Issue #5)

```commandline
apiVersion: v1
kind: Pod
metadata:
  name: testpod
spec:
  containers:
  - image: ghcr.io/canonical/charmed-spark-kyuubi:3.4-22.04_edge
    name: spark
    ports:
    - containerPort: 18080
    command: ["sleep"]
    args: ["36000"]  
```

Once the pod is up and running, login in the pod

```commandline
kubectl exec -it testpod -n kafka -- /bin/bash
```

and create a kube config such that the edge node can have admin rights on the K8s cluster:

```commandline
mkdir $HOME/.kube
cat > $HOME/.kube/config << EOF
<KUBECONFIG CONTENTS>
EOF
```

Also inject the `hive-site.xml` information

```commandline
cat > /etc/spark8t/conf/hive-site.xml << EOF
<HIVE_CONF>
EOF
```

Create the Spark user to be used for running Spark jobs:

```commandline
spark-client.service-account-registry create \
  --username spark-user  --namespace kafka
```

Verify that also the integration hub information have been added to the user (this may create some security concern - Issue #3)

```commandline
spark-client.service-account-registry get-config \
  --username spark-user  --namespace kafka
```

Exit from the Spark edge node pod. 

## Use-case

### Start generation of data into Kafka

From the juju edge node

```commandline
juju relate kafka producer
```

You can verify in the producer that date is effectively being streamed:

```commandline
juju ssh producer/0 sudo -i

$ cat /tmp/1*_producer.log
```

### Spark streaming consumption and persistence

Log in the `testpod`

```commandline
spark-client.pyspark --username spark-user --namespace kafka \
    --conf spark.executor.instances=2 --conf spark.sql.warehouse.dir="s3a://spark/warehouse"  \
    --conf spark.kubernetes.container.image=ghcr.io/canonical/charmed-spark:3.4-22.04_edge  \
    --conf spark.jars.ivy=/tmp \
    --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.4.2,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.2
```

Once the shell is up and running:

```commandline
# Input
username=...
password=...
endpoints=...
topic_name=...

# Output
table_name=...

lines = spark.readStream \
          .format("kafka") \
          .option("kafka.bootstrap.servers", endpoints) \
          .option("kafka.sasl.mechanism", "SCRAM-SHA-512") \
          .option("kafka.security.protocol", "SASL_PLAINTEXT") \
          .option("kafka.sasl.jaas.config", f'org.apache.kafka.common.security.scram.ScramLoginModule required username={username} password={password};') \
          .option("subscribe", topic_name) \
          .option("includeHeaders", "true") \
          .load()

from pyspark.sql.functions import udf, col, window
from json import loads

get_origin = udf(lambda x: loads(x)["origin"])

count = lines\
	.withColumn("origin", get_origin(col("value")))\
	.select("origin", "timestamp")\
	.withWatermark("timestamp", "10 seconds")\
    .groupBy(
        window("timestamp", "10 seconds"),
        "origin"
    )\
    .count()

if table_name:
    count.writeStream \
        .option("checkpointLocation", "s3a://spark/checkpoints/<random-id>")\
        .format("parquet") \
        .outputMode("append") \
        .toTable(table_name)
else:
    query = count.writeStream.outputMode("complete").format("console").start()
    query.awaitTermination()
```

(This command was somewhat taken from the documentation, although documentation has broken examples - Issue #6)

Depending on whether you provide `table_name` or not, you could either output the streaming analytics to the screen or persist that into an Hive table.

### Data analysis using Kyuubi

From the `testpod` edge node, using `beeline` to connect to Kyuubi (here I had to figure this out from the tests, since we are missing Kyuubi documentation - Issue #7)

```commandline
/opt/spark/bin/beeline -u <KYUUBI_ENDPOINT> -n admin -p <KYUUBI_PASSWORD>
```

> Note that it may take some time for the endpoint to be available as it is needed to start the Kyuubi pod engines, both driver and executors.

Once the prompt is active, check that the table is available

```commandline
SHOW TABLES;
```

and perform a simple query:

```commandline
SELECT count(*) FROM newtable;
```

Or peak into the table:

```commandline
jdbc:hive2://10.1.63.222:10009/> SELECT * FROM newtable LIMIT 10;
+----------------------------------------------------+---------------------------+--------+
|                       window                       |          origin           | count  |
+----------------------------------------------------+---------------------------+--------+
| {"start":2024-09-01 19:42:15,"end":2024-09-01 19:42:25} | producer-0 (10.1.63.230)  | 4      |
| {"start":2024-09-01 19:42:30,"end":2024-09-01 19:42:40} | producer-0 (10.1.63.230)  | 20     |
| {"start":2024-09-01 19:42:35,"end":2024-09-01 19:42:45} | producer-0 (10.1.63.230)  | 20     |
| {"start":2024-09-01 19:42:25,"end":2024-09-01 19:42:35} | producer-0 (10.1.63.230)  | 19     |
| {"start":2024-09-01 19:42:20,"end":2024-09-01 19:42:30} | producer-0 (10.1.63.230)  | 13     |
| {"start":2024-09-01 19:42:45,"end":2024-09-01 19:42:55} | producer-0 (10.1.63.230)  | 19     |
| {"start":2024-09-01 19:42:50,"end":2024-09-01 19:43:00} | producer-0 (10.1.63.230)  | 19     |
| {"start":2024-09-01 19:42:40,"end":2024-09-01 19:42:50} | producer-0 (10.1.63.230)  | 20     |
| {"start":2024-09-01 19:43:10,"end":2024-09-01 19:43:20} | producer-0 (10.1.63.230)  | 20     |
| {"start":2024-09-01 19:43:00,"end":2024-09-01 19:43:10} | producer-0 (10.1.63.230)  | 20     |
+----------------------------------------------------+---------------------------+--------+
10 rows selected (1.638 seconds)
```

### Monitoring

Use the usual tooling, for analyzing the logs and the metrics of the jobs. Here we did not deploy the Observability stack, but that can be done as per documentation and tutorials available.

## Issues Found

1. Spark-streaming job does not work using endpoints returned by Kafka (the Spark streaming application must live in the same namespace as the Kafka cluster)
2. Integration Hub has a clunky and buggy UX when it comes to the user-configurations
3. Security Bug: It is very easy to leak credentials using Integration Hub: as soon as someone creates a new service account with the spark client can get access to the S3 credentials or other sensitive information. Spark accounts should probably be registered manually, and we should not create configurations for all spark8t service account by default
4. charmed-spark-kyuubi: the postgresql jar has wrong user and permission settings
5. charmed-spark: We should probably include also for the base image the PosgreSQL jars
6. Documentations for Spark streaming is broken and not working (both How-to and Tutorial):
   * Missing reference to `col` function in import
   * (Tutorial) `w_count` in the tutorial not defined 
   * (How-to) `partition` column not available (need to be add to the `select`, but maybe it is not that important to groupby partition)
7. Missing Documentation on Kyuubi
8. Issue with deploying latest version of Kafka: 
    ```commandline
    bundle: kubernetes
    applications:
      admin:
        charm: data-integrator
        channel: latest/stable
        revision: 41
        scale: 1
        options:
          consumer-group-prefix: admin-cg
          extra-user-roles: admin
          topic-name: test-topic
        constraints: arch=amd64
      kafka:
        charm: kafka-k8s
        channel: 3/edge
        revision: 69
        resources:
          kafka-image: 46
        scale: 1
        constraints: arch=amd64
        storage:
          data: kubernetes,1,10240M
        trust: true
      producer:
        charm: kafka-test-app
        channel: latest/edge
        revision: 11
        scale: 1
        options:
          num_messages: 180
          role: producer
          topic_name: test-topic
        constraints: arch=amd64
      zookeeper:
        charm: zookeeper-k8s
        channel: 3/edge
        revision: 59
        resources:
          zookeeper-image: 31
        scale: 1
        constraints: arch=amd64
        storage:
          zookeeper: kubernetes,1,10240M
        trust: true
    relations:
    - - kafka:zookeeper
      - zookeeper:zookeeper
    - - admin:kafka
      - kafka:kafka-client
    ```