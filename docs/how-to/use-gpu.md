(how-to-use-gpu)=
# Enabling GPU acceleration

The Charmed Apache Spark solution offers an OCI image that supports the [Apache Spark Rapids plugin](https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-gpu) that enables GPU acceleration on Spark jobs.

## Setup

After installing [spark-client](https://snapcraft.io/spark-client) and [Microk8s](https://microk8s.io/) with the GPU add-on enabled, now we can look into how to launch Spark jobs with GPU in Kubernetes.

First, we need to create a pod template to limit the amount of GPU per container.

Edit the pod manifest file (we'll refer to it as `gpu_executor_template.yaml`) by adding the following content:

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

## Submit a Spark job with GPU acceleration

With the usage of the `spark-client` snap, we can submit the desired Spark job
adding some configuration options for enabling GPU acceleration:

```shell
spark-client.spark-submit \
    ... \ 
    --conf spark.executor.resource.gpu.amount=1 \
    --conf spark.task.resource.gpu.amount=1 \
    --conf spark.rapids.memory.pinnedPool.size=1G \
    --conf spark.plugins=com.nvidia.spark.SQLPlugin \
    --conf spark.executor.resource.gpu.discoveryScript=/opt/getGpusResources.sh \
    --conf spark.executor.resource.gpu.vendor=nvidia.com \
    --conf spark.kubernetes.container.image=ghcr.io/canonical/charmed-spark-gpu:3.4-22.04_edge \
    --conf spark.kubernetes.executor.podTemplateFile=gpu_executor_template.yaml
    ...
```

The Apache Spark configuration options can also be set at the service account level using the Spark Client snap to use them on every job. Please refer to the [guide](https://discourse.charmhub.io/t/spark-client-snap-how-to-manage-spark-accounts/8959) on how to manage options at the service account level. To have more information on how the Apache Spark Client manages configuration options please refer to the [explanation section](https://discourse.charmhub.io/t/spark-client-snap-explanation-hierarchical-configuration-handling/8956). 

The options above are the minimal set that is needed to enable the Apache Spark Rapids plugin. 
For more information on available options, see the [full list](https://nvidia.github.io/spark-rapids/docs/configs.html).
