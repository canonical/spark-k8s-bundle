## Working with Charmed Kubernetes from within a pod

### Setup

After installing [Juju](https://juju.is/docs/olm/install-juju) and [Charmed Kubernetes](https://ubuntu.com/kubernetes/docs/install-manual) (together with applying [setup for the latter](https://ubuntu.com/kubernetes/docs/operations) ), now we can look into how to launch Spark jobs from within a pod in Charmed Kubernetes.

First, we create a pod using the Charmed Spark container image.

Edit the pod manifest file (we'll refer to it as `shell-demo.yaml`) by adding the following content:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: shell-demo
  namespace: default
spec:
  containers:
  - name: spark-client
    image: ghcr.io/canonical/charmed-spark:3.4-22.04_stable
    command: ["/bin/pebble", "run", "--hold"]
  serviceAccountName: spark
  hostNetwork: true
  dnsPolicy: Default
```

The pod can be created with the following command:

```shell
kubectl apply -f shell-demo.yaml
```

We can log into the pod as below:

```shell
$ kubectl exec --stdin --tty shell-demo -- /bin/bash 
```

Now let's create the Kubernetes configuration on the pod, with contents from the original server's `.kube/config`:

```shell
$ mkdir ~/.kube
$ cat > ~/.kube/config << EOF
<KUBECONFIG_CONTENTS_FROM_CHARMED_KUBERNETES>
EOF
```

Then we need to set up a service account for Spark job submission. Let's create a user called `spark` in `default` namespace:

```shell
$ python3 -m spark8t.cli.service_account_registry create --username spark
```

### Spark Job submission to Kubernetes cluster

There is a script called ```spark-submit``` packaged within the Charmed Spark container image for Spark job submission. We can sue the ```Spark Pi``` job example again, such as:

```shell
$ python3 -m spak8t.cli.spark_submit --username spark --class org.apache.spark.examples.SparkPi local:///opt/spark/examples/jars/spark-examples_2.12-3.3.2.jar 100
```
Or using the snap command (referring practically to the same thing):

```shell
$ spark-client.spark-submit --username spark --class org.apache.spark.examples.SparkPi local:///opt/spark/examples/jars/spark-examples_2.12-3.3.2.jar 100
```

### Spark shell

To invoke the Spark shell, you can run the following command within the pod:

```shell
$ python3 -m spark8t.cli.spark_shell --username spark
```

Or

```shell
$ spark-client.spark-shell --username spark
```

### PySpark shell

To launch a `pyspark` shell, run the following command within the pod:

```shell
$ python3 -m spark8t.cli.pyspark --username spark
```

Or

```shell
$ spark-client.pyspark --username spark
```
