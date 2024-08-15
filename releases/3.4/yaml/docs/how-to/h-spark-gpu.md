# Enabling GPU acceleration

The Charmed Spark solution offers an OCI image that supports the [Spark Rapids plugin](https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-gpu) that enables gpu acceleration on Spark jobs.

## Setup

After installing [spark-client](https://snapcraft.io/spark-client) and [Microk8s](https://microk8s.io/) with the gpu addon enabled, now we can look into how to launch Spark jobs with GPU in Kubernetes.

First, we need to create a pod template to limit the amount of gpu per container.

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

### Submitting a Spark job with gpu acceleration

With the usage of the `spark-client` snap we can now submit the desired Spark job. 
In order to run the job with gpu acceleration, some configuration options need to be used:

```shell
spark.executor.resource.gpu.amount=1
spark.task.resource.gpu.amount=1
spark.rapids.memory.pinnedPool.size=1G
spark.plugins=com.nvidia.spark.SQLPlugin
spark.executor.resource.gpu.discoveryScript=/opt/getGpusResources.sh
spark.executor.resource.gpu.vendor=nvidia.com
spark.kubernetes.container.image=ghcr.io/canonical/charmed-spark-gpu:3.4-22.04_edge
spark.kubernetes.executor.podTemplateFile=gpu_executor_template.yaml
```

The Spark configuration options can be set at the spark service account with the Spark Client snap to use them on all the jobs. Please refer to the [guide](https://discourse.charmhub.io/t/spark-client-snap-how-to-manage-spark-accounts/8959) on how to manage options at service account level. To have more information on how the Spark Client manages configuration options please refer to the [explanation section](https://discourse.charmhub.io/t/spark-client-snap-explanation-hierarchical-configuration-handling/8956). 

The options above are the minimal set that is needed to enable the Spark Rapids plugin. 
For more information on available options, see the [full list](https://nvidia.github.io/spark-rapids/docs/configs.html).