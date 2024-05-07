The Charmed Spark solution comes with the [spark-metrics](https://github.com/banzaicloud/spark-metrics) exporter embedded in the [Charmed Spark OCI image](https://github.com/canonical/charmed-spark-rock), used as base for driver and executors pods .
This exporter is designed to push metrics to the [prometheus pushgateway](https://github.com/prometheus/pushgateway), that is integrated with the [Canonical Observability Stack](https://charmhub.io/topics/canonical-observability-stack). 


In order to enable the observability on Charmed Spark two steps are necessary:

1. Setup the Observability bundle with juju
2. Configure the Spark service account


## Setup the Observability bundle with Juju

As a prerequisite, you need to have Juju 3 installed with a MicroK8s controller bootstrapped. This can be done following this [tutorial](https://charmhub.io/topics/canonical-observability-stack/tutorials/install-microk8s).


As a first step, start by deploying cos-lite bundle in a Kubernetes environment with Juju.

```shell
juju add-model cos
juju switch cos
juju deploy cos-lite --trust
```
Some extra charms are needed to integrate the Charmed Spark with the Observability bundle. This includes the `prometheus-pushgateway-k8s` charm and the `cos-configuration-k8s grafana` that is used to configure the Grafana dashboard. We provide a basic dashboard [here](https://github.com/canonical/charmed-spark-rock/blob/dashboard/dashboards/prod/grafana/spark_dashboard.json).

```shell
juju deploy prometheus-pushgateway-k8s --channel edge
# deploy cos configuration charm to import the grafana dashboard
juju deploy cos-configuration-k8s \
  --config git_repo=https://github.com/canonical/charmed-spark-rock \
  --config git_branch=dashboard \
  --config git_depth=1 \
  --config grafana_dashboards_path=dashboards/prod/grafana/
# relate cos-configration charm to import grafana dashboard
juju relate cos-configuration-k8s grafana
juju relate prometheus-pushgateway-k8s prometheus

```

The observability bundle can be optionally further customized using additional charms:
```shell


# deploy the prometheus-scrape-config-k8s to configure a more fine grained scraping interval 
juju deploy prometheus-scrape-config-k8s scrape-interval-config --config scrape_interval=<SCRAPE_INTERVAL>
juju relate scrape-interval-config prometheus-pushgateway-k8s
juju relate scrape-interval-config:metrics-endpoint prometheus:metrics-endpoint

```

This allows to configure a custom scraping interval that prometheus will used to retrieve the exposed metrics.


Eventually, you will need to retrive the credentials for logging into the Grafana dashboard, by using the following action:
``` shell
juju run grafana/leader get-admin-password
```

After the login, Grafana will show a new dashboard: `Spark Dashboard` where the metrics are displayed.

## Configure Spark service account


To enable the push of metrics you only need to add the following lines as configuration to a `spark-client` configuration file (e.g., `spark-defaults.conf`): 

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

or as alternative you can feed these arguments directly to the spark-submit command, as shown [here](https://discourse.charmhub.io/t/spark-client-snap-tutorial-spark-submit/8953).

The Prometheus Pushgateway address and port can be exposed with the following commands: 

```shell
export PROMETHEUS_GATEWAY=$(juju status --format=yaml | yq ".applications.prometheus-pushgateway-k8s.address") 
export PROMETHEUS_PORT=9091
```