## Configure Service Account using the Spark Integration Hub Charm

The Integration Hub charm allows seamless configuration of Charmed Spark service accounts
via Juju relations, therefore providing a charming, integrated user-experience. 

The Integration Hub charm is part of the Charmed Spark bundle, that can be deployed following 
[this](/TODO) how-to guide. Alternatively, you can also deploy the 
Spark Integration Hub charm standalone by running the following command

```shell
juju deploy spark-integration-hub-k8s --channel edge -n1
```

Once deployed, the Spark Integration Hub will automatically manage the properties for all the service 
accounts created either with the `spark-client` snap or using the `spark8t` python library. 
More information on the snap and on the python library can be found 
[here](/t/spark-client-snap-how-to-manage-spark-accounts/8959) and 
[here](/t/spark-client-snap-how-to-python-api/8958).

### Enable S3 object storage bindings

Spark Integration Hub can consume the `s3-credentials` relation provided by the 
[S3 integrator charm](https://charmhub.io/s3-integrator) to enable integration with an S3-compatible 
object storage system. 

You can find more information on how to deploy and configure a `s3-integrator` 
charm [here](https://github.com/canonical/s3-integrator).

Once a `s3-integrator` charm is set up, the Spark Integration Hub charm can be 
integrated with

```shell
juju integrate s3-integrator spark-integration-hub-k8s
```

This will automatically add relevant configuration properties to your spark jobs, 
that can be verified using the tools provided in the spark-client snap, e.g. 

```shell
spark-client.service-account-registry get-config --username <service_account> --namespace <namespace>
```

You should see additional configuration automatically added to your service-account, i.e.

```shell
spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider
spark.hadoop.fs.s3a.connection.ssl.enabled=false
spark.hadoop.fs.s3a.path.style.access=true \
spark.hadoop.fs.s3a.access.key=<ACCESS_KEY>
spark.hadoop.fs.s3a.endpoint=<S3_ENDPOINT>
spark.hadoop.fs.s3a.secret.key=<SECRET_KEY>
```

### Enable Monitoring with Prometheus pushgateway

Spark Integration Hub can consume the `pushgateway` relation provided by the 
[Prometheus Pushgateway charm](https://charmhub.io/prometheus-pushgateway) to enable integration with an S3 object storage. 

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