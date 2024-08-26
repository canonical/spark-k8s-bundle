## Configure Service Account using the Spark Integration Hub Charm

The Integration Hub charm allows seamless configuration of Charmed Spark service accounts
via Juju relations, therefore providing a charming, integrated user-experience. 

The Integration Hub charm is part of the Charmed Spark bundle, that can be deployed following 
[this](/t/charmed-spark-k8s-documentation-how-to-deploy-charmed-spark/10979) how-to guide. Alternatively, you can also deploy the 
Spark Integration Hub charm standalone by running the following command

```shell
juju deploy spark-integration-hub-k8s --channel edge -n1
```

Once deployed, the Spark Integration Hub will automatically manage the properties for all the service 
accounts created either with the `spark-client` snap or using the `spark8t` python library. 
Refer to the how-to guides for more information on the [snap usage](/t/spark-client-snap-how-to-manage-spark-accounts/8959) and 
on the [python library](/t/spark-client-snap-how-to-python-api/8958).

### Enable object storage integration

Spark Integration Hub can consume:

* `s3-credentials` relation provided by the [S3-integrator](https://charmhub.io/s3-integrator) to enable integration with an S3-compatible 
object storage system
* `azure-credentials` relation provided by the [Azure Storage Integrator](https://charmhub.io/azure-storage-integrator) to enable integration with Azure Storages, such as Azure Blob Storage (WASB) and Azure DataLake Gen2 Storage (ABFS).

#### S3-compatible object storage

In order to enable integration with a s3-compatible storage, deploy the S3-integrator charm

```shell
juju deploy s3-integration --channel stable
```

And configure the appropriate parameters via config options, i.e.

```shell
juju config s3-integration \
  bucket=<S3_BUCKET> \
  endpoint=<S3_ENDPOINT> \
  path=spark-events
```

In the `s3-integrator`, credentials are fed using an action:

```shell
juju run s3-integrator/leader sync-s3-credentials \
  access-key=$S3_ACCESS_KEY \
  secret-key=$S3_SECRET_KEY
```

Please refer to the [How-To Setup Environment](/t/charmed-spark-k8s-documentation-how-to-setup-k8s-environment/11618) for guidance on how to set up and retrieve the 
different parameters for a MinIO deployed on MicroK8s and AWS S3. 
For more information on how to deploy and configure the `s3-integrator` charm refer to the charm documentation.

Once the `s3-integrator` is set up and on an idle/active state, the Spark Integration Hub charm can be integrated with

```shell
juju integrate s3-integrator spark-integration-hub-k8s
```

This will automatically add relevant configuration properties to your spark jobs,
depending on the storage backend. 
This can be verified using the tools provided in the spark-client snap, e.g. 

```shell
spark-client.service-account-registry get-config --username <service_account> --namespace <namespace>
```

You should see the following configuration automatically added to your service-account:

```shell
spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider
spark.hadoop.fs.s3a.connection.ssl.enabled=false
spark.hadoop.fs.s3a.path.style.access=true \
spark.hadoop.fs.s3a.access.key=<S3_ACCESS_KEY>
spark.hadoop.fs.s3a.endpoint=<S3_ENDPOINT>
spark.hadoop.fs.s3a.secret.key=<S3_SECRET_KEY>
```

#### Azure storage

In order to enable integration with an Azure storage, deploy the Azure Storage Integrator charm

```shell
juju deploy azure-storage-integrator --channel edge
```

`storage_account` and `container` are provided to the charm using normal configuration, while
`storage_key` is provided using Juju secrets, in order to provide confidentiality and 
security over its value. 

Thus, create a Juju secret holding its value:

```shell
juju add-secret azure-credentials secret-key=<AZURE_STORAGE_KEY>
```

This should prompt the `secret:<secret_id>` that can be used to configure 
the Azure Storage Integrator charm. 

Before configuring the charm, make sure the Azure Storage Integrator charm 
has granted permission to it:

```shell
juju grant-secret <secret_id> azure-storage
```

Then, Use the `secret_id` to configure the charm, i.e.

```shell
juju config azure-storage-integrator \
  credentials=secret:<secret_id> \
  storage-account=<AZURE_STORAGE_ACCOUNT> \
  container=<AZURE_CONTAINER> \
  path="spark-events"
```

Please refer to the [How-To Setup Environment](/t/charmed-spark-k8s-documentation-how-to-setup-k8s-environment/11618) for guidance on how to set up and retrieve the 
different parameters for Azure Storage backends. 
For more information on how to deploy and configure the Azure Storage Integrator charm refer 
to the charm documentation.

Once the Azure Storage Integrator charm is set up and on an `idle/active` state, the Spark Integration Hub charm can be integrated with

```shell
juju integrate azure-storage-integrator spark-integration-hub-k8s
```

This will automatically add relevant configuration properties to your spark jobs,
depending on the storage backend. 
This can be verified using the tools provided in the spark-client snap, e.g. 

```shell
spark-client.service-account-registry get-config --username <service_account> --namespace <namespace>
```

You should see the following configuration automatically added to your service-account:

```shell
spark.hadoop.fs.azure.account.key.<AZURE_STORAGE_ACCOUNT>.dfs.core.windows.net=<AZURE_STORAGE_KEY>
```

### Enable Monitoring with Prometheus pushgateway

Spark Integration Hub can consume the `pushgateway` relation provided by the 
[Prometheus Pushgateway charm](https://charmhub.io/prometheus-pushgateway) to enable integration with an object storage. 

You can find more information on how to deploy and configure a `prometheus-pushgateway` 
charm [here](https://discourse.charmhub.io/t/prometheus-pushgateway-operator-k8s-docs-using-prometheus-pushgateway/11979/2).

Once a `prometheus-pushgateway` charm is set up, the Spark Integration Hub charm can be related with

```shell
juju integrate prometheus-pushgateway spark-integration-hub-k8s
```

This will add relevant configuration properties to your Charmed Spark service accounts, 
that can be verified using the snap, e.g. 

```shell
spark-client.service-account-registry get-config --username <service_account> --namespace <namespace>
```

where you should see additional configuration automatically added to your service-account

```shell
spark.metrics.conf.driver.sink.prometheus.pushgateway-address=<PROMETHEUS_GATEWAY_ADDRESS>:<PROMETHEUS_PORT>
spark.metrics.conf.driver.sink.prometheus.class=org.apache.spark.banzaicloud.metrics.sink.PrometheusSink
spark.metrics.conf.driver.sink.prometheus.enable-dropwizard-collector=true
spark.metrics.conf.driver.sink.prometheus.period=5
spark.metrics.conf.driver.sink.prometheus.metrics-name-capture-regex=([a-z0-9]*_[a-z0-9]*_[a-z0-9]*_)(.+)
spark.metrics.conf.driver.sink.prometheus.metrics-name-replacement=\$2
spark.metrics.conf.executor.sink.prometheus.pushgateway-address=<PROMETHEUS_GATEWAY_ADDRESS>:<PROMETHEUS_PORT>
spark.metrics.conf.executor.sink.prometheus.class=org.apache.spark.banzaicloud.metrics.sink.PrometheusSink
spark.metrics.conf.executor.sink.prometheus.enable-dropwizard-collector=true
spark.metrics.conf.executor.sink.prometheus.period=5
spark.metrics.conf.executor.sink.prometheus.metrics-name-capture-regex=([a-z0-9]*_[a-z0-9]*_[a-z0-9]*_)(.+)
spark.metrics.conf.executor.sink.prometheus.metrics-name-replacement=\$2
```

### Overriding values and adding other configurations

Beside the configurations enabled by relations, custom configuration can also 
be added directly using actions. 

In order to add a new custom configuration property

```shell
juju run integration-hub/leader add-config conf="<property>=<value>"
```

Configuration properties can be removed using 

```shell
juju run integration-hub/leader clear-config
```

or they can be removed one by one using

```shell
juju run integration-hub/leader remove-config key="<property>"
```

Finally, to list all custom configuration properties, use

```shell
juju run integration-hub/leader list-config
```

> **NOTE** Since the configurations provided using actions take the precedence,
> the configuration items already provided by the integration may be overridden, 
> thus allowing some customisation of what is automatically configured by default.