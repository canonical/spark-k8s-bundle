## Enable and configuring Spark monitoring

Charmed Spark supports native integration with the Canonical Observability Stack (COS). If you want to enable monitoring on top of Charmed Spark, make sure that you have a Juju model with COS correctly deployed. 
To deploy COS on MicroK8s, follow the [step-by-step tutorial](https://charmhub.io/topics/canonical-observability-stack/tutorials/install-microk8s). 
For more information about Charmed Spark and COS integration, refer to the [COS documentation](https://charmhub.io/topics/canonical-observability-stack) and the [monitoring explanation section](//t/charmed-spark-documentation-explanation-monitoring/14299).

Once COS is correctly setup, to enable monitoring it is necessary to:

1. Integrate and configure the COS bundle with Charmed Spark
2. Configure the Spark service account

## Integrating/Configuring with COS

The Charmed Spark solution already bundles all the components required to integrate 
COS as well as to configure the monitoring artifacts. 

The deployments of these resources can be enabled/disabled using either overlays
(for Juju bundles) or input variables (for Terraform bundles). 
Please refer to the [how-to deploy](/t/charmed-spark-k8s-documentation-how-to-deploy-charmed-spark/10979) guide for more information.

After the deployment settles on an `active/idle` state, you can make sure that 
Grafana is correctly setup with dedicated dashboards.
To do so, retrieve the credentials for logging into the Grafana dashboard, by 
switching to the COS model (using `juju switch <cos_model>`) and 
using the following action:

``` shell
juju run grafana/leader get-admin-password
```

The action will also show you the grafana endpoint where you will be able to
log in with the provided credentials for the `admin` user.

After the login, Grafana will show a new dashboard: `Spark Dashboard` where 
the Spark metrics will be displayed.

### Customize Charmed Spark dashboards

The `cos-configuration-k8s` charm included in the bundle can be used to customise 
the Grafana dashboard. If needed, we provide a [default dashboard](https://github.com/canonical/spark-k8s-bundle/blob/main/releases/3.4/resources/grafana) as part 
of the bundle.

The `cos-configuration-k8s` charm syncs the content of a repository with the resources 
provided to Grafana, thus enabling versioning of the resource. 
You can specify the repository, branch and folder using the config options, i.e.

```shell
# deploy cos configuration charm to import the grafana dashboard
juju config cos-configuration \
  git_repo=<your-repo> \
  git_branch=<your-branch> \
  git_depth=1 \
  grafana_dashboards_path=<path-to-dashboard-folder>
```

After updating the configuration or whenever the repository is updated, 
contents is synced either upon a `update-status` event or after running the action:

```shell
juju run cos-configuration-k8s/leader sync-now
```

For more information, refer to the `cos-configuration-k8s` charm [docs](https://discourse.charmhub.io/t/cos-configuration-k8s-docs-index/7284).

### Configuring Scraping intervals

The `prometheus-scrape-config-k8s` charm included in the bundle can be used to configure 
the prometheus scraping jobs. 

In particular, it is crucial to configure the scraping interval to make sure 
data points have proper sampling frequency, e.g. 

```shell
juju config scrape-config --config scrape_interval=<SCRAPE_INTERVAL>
```

For more information about the properties that can be set using `prometheus-scrape-config-k8s`, 
please refer to [here](https://discourse.charmhub.io/t/prometheus-scrape-config-k8s-docs-index/6856).


## Configure Spark service account

Charmed Spark service account created by `spark-client` snap and `spark8t` Python library
are automatically configured to use monitoring by the 
[spark-integration-hub-k8s](https://charmhub.io/spark-integration-hub-k8s) charm, that 
is deployed as part of the Charmed Spark bundle. 

Just make sure that the `spark-integration-hub-k8s` charm is correctly related to
the `prometheus-pushgateway` charm on the `pushgateway` interface.

You can also double-check that the configuration done by the `spark-integration-hub-k8s`
was effective by inspecting the Charmed Spark service account properties using the snap

```shell
spark-client.service-account-registry get-config --username <username> --namespace <namespace>
```

and check that the following property

```shell
spark.metrics.conf.driver.sink.prometheus.pushgateway-address=<PROMETHEUS_GATEWAY_ADDRESS>:<PROMETHEUS_PORT>
```

is configured with the correct values. The Prometheus Pushgateway address and port should be can be consistent with what is exposed by Juju, e.g. 

```shell
PROMETHEUS_GATEWAY=$(juju status --format=yaml | yq ".applications.prometheus-pushgateway-k8s.address") 
```

> **NOTE** Beside the one above, the Charmed Spark service accounts are configured 
> for exporting metrics by means of other properties, returned by the `get-config`
> command.
> Should you want to override some of these with other custom values, this 
> can be done by either:
>   1. providing custom configuration to the `spark-integration-hub-k8s` charm 
>      (as explained [here](/t/charmed-spark-k8s-documentation-how-to-use-spark-integration-hub/14296))
>   2. adding the configurations to the Charmed Spark service account 
>      directly (as explained [here](/t/spark-client-snap-how-to-manage-spark-accounts/8959))
>   3. feeding these arguments directly to the spark-submit command (as shown 
>      [here](/t/spark-client-snap-tutorial-spark-submit/8953)).