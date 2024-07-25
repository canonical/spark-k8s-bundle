## Enabling GPU acceleration with Charmed Spark

The Charmed Spark solution offers an OCI image that supports the [Spark Rapids plugin](https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-gpu) that enables gpu acceleration on Spark jobs.

### Setup

After installing [spark-client](https://snapcraft.io/spark-client) and [Microk8s](https://microk8s.io/) with the gpu addon enabled, now we can look into how to launch Spark jobs with GPU in Kubernetes.


First, we need to create a pod template to limit the amount of gpu per container.

Edit the pod manifest file (we'll refer to it as ```gpu_executor_template.yaml```) by adding the following content:

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: executor
      resources:
        limits:
          nvidia.com/gpu: 1
```

### Submitting Spark Job

With the usage of the `spark-client` snap we can now submit the desired Spark job. 
In order to run the job with gpu acceleration, some configuration options need to be used:

```shell
spark-client.spark-submit \
--username spark \
--namespace spark \
--conf spark.kubernetes.driver.request.cores=100m \
--conf spark.kubernetes.executor.request.cores=100m \
--conf spark.executor.instances=1 \
--conf spark.executor.resource.gpu.amount=1 \
--conf spark.executor.memory=4G \
--conf spark.executor.cores=1 \
--conf spark.task.cpus=1 \
--conf spark.task.resource.gpu.amount=1 \
--conf spark.rapids.memory.pinnedPool.size=1G \
--conf spark.executor.memoryOverhead=1G \
--conf spark.sql.files.maxPartitionBytes=512m \
--conf spark.sql.shuffle.partitions=10 \
--conf spark.plugins=com.nvidia.spark.SQLPlugin \
--conf spark.executor.resource.gpu.discoveryScript=/opt/getGpusResources.sh \
--conf spark.executor.resource.gpu.vendor=nvidia.com \
--conf spark.kubernetes.container.image=docker pull ghcr.io/canonical/charmed-spark-gpu:3.4-22.04_edge \
--driver-memory 2G \
--conf spark.kubernetes.executor.podTemplateFile=gpu_executor_template.yaml \
  s3a://<BUCKET>/script-job.py'
```