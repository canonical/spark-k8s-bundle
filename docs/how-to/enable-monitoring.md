(how-to-monitoring)=
# Enable and configuring monitoring

Charmed Apache Spark supports native integration with the Canonical Observability Stack (COS). If you want to enable monitoring on top of Charmed Apache Spark, make sure that you have a Juju model with COS correctly deployed.

To deploy COS on MicroK8s, follow the [step-by-step tutorial](https://charmhub.io/topics/canonical-observability-stack/tutorials/install-microk8s).
For more information about Charmed Apache Spark and COS integration, refer to the [COS documentation](https://charmhub.io/topics/canonical-observability-stack) and the [monitoring explanation section](/explanation/monitoring).

Once COS is correctly deployed, to enable monitoring it is necessary to:

1. Integrate and configure the COS bundle with Charmed Apache Spark
2. Configure the Apache Spark service account
3. (Optional) Integrate the optional components of Charmed Apache Spark (such as the Spark History Server charm and Charmed Apache Kyuubi) with the COS bundle

## Integrating/configuring with COS

The Charmed Apache Spark solution already bundles all the components required to integrate
COS as well as to configure the monitoring artifacts.

The deployments of these resources can be enabled/disabled using either overlays
(for Juju bundles) or input variables (for Terraform bundles).
Please refer to the [how-to deploy](how-to-deploy-spark) guide for more information.

After the deployment settles on an `active/idle` state, you can make sure that
Grafana is correctly set up with dedicated dashboards.
To do so, retrieve the credentials for logging into the Grafana dashboard, by
switching to the COS model (using `juju switch <cos_model>`) and
using the following action:

```shell
juju run grafana/leader get-admin-password
```

The action will also show you the grafana endpoint where you will be able to
log in with the provided credentials for the `admin` user.

After the login, Grafana will show a new dashboard: `Spark Dashboard` where
the Apache Spark metrics will be displayed.

### Configuring scraping intervals

The `prometheus-scrape-config-k8s` charm included in the bundle can be used to configure
the prometheus scraping jobs.

In particular, it is crucial to configure the scraping interval to make sure
data points have proper sampling frequency, e.g.:

```shell
juju config scrape-config --config scrape_interval=<SCRAPE_INTERVAL>
```

For more information about the properties that can be set using `prometheus-scrape-config-k8s`,
please refer to its [documentation](https://discourse.charmhub.io/t/prometheus-scrape-config-k8s-docs-index/6856).

### Enable log forwarding to Loki

Logs from each driver or executor can be enabled using two Spark configuration options:

- `spark.executorEnv.LOKI_URL`
- `spark.kubernetes.driverEnv.LOKI_URL`

They are used to forward executor and driver logs respectively to a Loki server.

There are two ways to provide the `LOKI_URL` variables:

1. Manually, via [Spark configuration](https://canonical.com/data/docs/spark/k8s/e-configuration):
   * `spark.executorEnv.LOKI_URL` - for executors
   * `spark.kubernetes.driverEnv.LOKI_URL` - for drivers
2. Using the [`logging` relation](https://charmhub.io/spark-integration-hub-k8s/integrations#logging)
   in an Integration Hub for Apache Spark charm either with the
   [Grafana-agent charm](https://charmhub.io/grafana-agent-k8s) (recommended) or
   directly with the [Loki charm](https://charmhub.io/loki-k8s), for example:

   ```shell
   juju integrate spark-integration-hub-k8s:logging grafana-agent-k8s:logging-provider
   ```

## Configure Apache Spark service account

Charmed Apache Spark service account created by `spark-client` snap and `spark8t` Python library
are automatically configured to use monitoring by the
[spark-integration-hub-k8s](https://charmhub.io/spark-integration-hub-k8s) charm, that
is deployed as part of the Charmed Apache Spark bundle.

Just make sure that the `spark-integration-hub-k8s` charm is correctly related to
the `prometheus-pushgateway` charm on the `pushgateway` interface.

You can also double-check that the configuration done by the `spark-integration-hub-k8s`
was effective by inspecting the Charmed Apache Spark service account properties using the snap:

```shell
spark-client.service-account-registry get-config --username <username> --namespace <namespace>
```

and check that the following property:

```shell
spark.metrics.conf.driver.sink.prometheus.pushgateway-address=<PROMETHEUS_GATEWAY_ADDRESS>:<PROMETHEUS_PORT>
```

is configured with the correct values. The Prometheus Pushgateway address and port should be can be
consistent with what is exposed by Juju, e.g.:

```shell
PROMETHEUS_GATEWAY=$(juju status --format=yaml | yq ".applications.prometheus-pushgateway-k8s.address")
```

```{note}
Besides the one above, the Charmed Apache Spark service accounts are configured
for exporting metrics by means of other properties, returned by the `get-config`
command. You can override some of them with custom values by either:

1. Providing custom configuration to the `spark-integration-hub-k8s` charm
(as explained in the [How to use integration hub guide](how-to-service-accounts-integration-hub)).
2. Adding the configurations to the Charmed Apache Spark service account
directly (as explained in the 
[How to manage Charmed Apache Spark accounts guide](/how-to/manage-service-accounts/using-spark-client-snap)).
3. Feeding these arguments directly to the `spark-submit` command (as shown in the
[Spark client tutorial](https://discourse.charmhub.io/t/spark-client-snap-tutorial-spark-submit/8953)).
```

## (Optional) Spark History Server and Charmed Apache Kyuubi 

Both the Spark History Server and Charmed Apache Kyuubi charms come with the [JMX exporter](https://github.com/prometheus/jmx_exporter/).
The metrics can be queried by accessing the `http://<history-server-unit-ip>:9101/metrics` and `http://<kyuubi-unit-ip>:10019/metrics` endpoints, respectively.

This section guides you how to set up monitoring with Canonical Observability Stack (COS) for both Spark History Server and Charmed Apache Kyuubi.

### Prerequisites

After setting up COS following the previous sections, you should have:

- a Juju model running the COS component
- Juju cross-model offers to integrate with the COS components
- the `grafana-agent-k8s` charm running and consuming the offers

### Setup

To benefit from the native COS support, integrate the charms with `grafana-agent`. 
For Spark History Server:

```shell
juju integrate grafana-agent-k8s spark-history-server-k8s:grafana-dashboard
juju integrate grafana-agent-k8s spark-history-server-k8s:logging
juju integrate grafana-agent-k8s spark-history-server-k8s:metrics-endpoint
```

For Charmed Apache Kyuubi:

```shell
juju integrate grafana-agent-k8s kyuubi-k8s:grafana-dashboard
juju integrate grafana-agent-k8s kyuubi-k8s:logging
juju integrate grafana-agent-k8s kyuubi-k8s:metrics-endpoint
```

Wait for all components to settle down to the `active/idle` state on both models.

Congratulations, the COS now monitors the two charms.

## Customize dashboards and alert rules

The `cos-configuration-k8s` charm included in the bundle can be used to customise the Grafana dashboards and alert rules.
If needed, we provide a [default dashboard](https://github.com/canonical/spark-k8s-bundle/blob/main/releases/3.4/resources/grafana) as part
of the bundle and dedicated dashboards for the [Spark History Server](https://github.com/canonical/spark-history-server-k8s-operator/tree/3/edge/src/grafana_dashboards)
and [Charmed Apache Kyuubi](https://github.com/canonical/kyuubi-k8s-operator/tree/3.4/edge/src/grafana_dashboards) charms.

The `cos-configuration-k8s` charm syncs the content of a repository with the resources
provided to Grafana, thus enabling versioning of the resource.

### Create a repository with a custom monitoring setup

Save your alert rules and dashboard models in a Git repository (new or existing) as separate directories:

- Prometheus rules
- Loki rules
- Dashboard models

For rule writing examples, see the
[Prometheus documentation](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) and
[Charmed Apache Kyuubi K8s repository](https://github.com/canonical/kyuubi-k8s-operator/blob/3.4/edge/src/prometheus_alert_rules/prometheus.yaml).

Make sure to push your changes to the remote repository.

### Deploy the COS configuration charm

Deploy the [COS configuration](https://charmhub.io/cos-configuration-k8s) charm in the COS Juju model with configuration parameters defining the repository, branch, and paths to the directories:

```shell
juju switch <cos_model_name>

juju deploy cos-configuration-k8s cos-config
  --config git_repo=<repository_url>
  --config git_branch=<branch>
  --config git_depth=1
  --config grafana_dashboards_path=<path_to_dashboard_folder> 
  --config prometheus_alert_rules_path=<path_to_prometheus_rules_folder>
  --config loki_alert_rules_path=<path_to_loki_rules>
```

And run the `sync-now` action:

```shell
juju run cos-configuration-k8s/leader sync-now
```

For more information, refer to the `cos-configuration-k8s` charm [docs](https://discourse.charmhub.io/t/cos-configuration-k8s-docs-index/7284).

### Forward the rules and dashboards

Integrate the charm to the COS operator to forward the rules and dashboards:

```shell
juju integrate cos-config prometheus
juju integrate cos-config grafana
juju integrate cos-config loki
```

After this is complete, the monitoring COS stack should be up, and ready to fire alerts based on your new rules.
As for the dashboards, they should be available in the Grafana interface.

## Conclusion

In this guide, we enabled monitoring on a Charmed Apache Spark deployment and integrated alert rules and dashboards by syncing a Git repository to the COS stack.
