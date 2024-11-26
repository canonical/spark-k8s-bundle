## Monitoring 

An important requirement of a production-ready system is to provide a way for the admins to 
monitor and actively observe the operation of the cluster. 
Charmed Apache Spark delivers a comprehensive observability stack which includes:

* **business analytical monitoring** via the deployment of Spark History Server, 
  that provides a UI that allows Apache Spark users (such as Data Scientist and Data Engineers) 
  to analyze the logs of their jobs at a more business level, allowing to break down a Spark Job into 
  its different parts and stages 
* **cluster administration monitoring** via integration with the Canonical 
  Observability Stack (COS) for aggregating raw application metrics,  
  and setting up alerts and dashboards based on resource utilization.

In the following we will describe the architecture and how the different components 
connect among themselves, providing the monitoring capabilities of the solution.

Before diving in, it is worth providing a brief reminder of the structure of 
a Spark Job. 

### Spark Job structure

A Spark Job is generally composed by two main types of processes:

* Spark Driver, that executes the main program, interacts with the Cluster Manager 
  to request computational resources (Executors), and control the workflow by providing
  instructions to the Executors on which operations/tasks to be executed. The Apache Spark 
  driver generally holds a small fraction of the data, generally resulting on the
  aggregation/reduction operation done by the Executors. 

* Spark Executors, that hold the raw data in memory and do the actual processing.  
  The Executors generally communicate among themselves to shuffle data whenever 
  needed, and they provide the horizontally scalable structure that enables 
  analysis to be distributed and scaled out to massive datasets. 

Spark Driver and Spark Executors are allocated by a Cluster Manager that in the
Charmed Apache Spark solution is represented by the K8s control plane. Therefore, 
in Charmed Apache Spark, driver and executors run as Kubernetes pods, 
belonging to a given namespace.
Every pod needs to be run using a service account that needs to be set up with the 
correct permissions. Charmed Apache Spark tooling, i.e. the `spark-client` snap
and the `spark8t` Python libraries, make sure that service account are 
created correctly and configured appropriately. The driver pod must be running
with a service account that is able to create pods, services and configmaps in 
order to correctly spawn executors. Moreover, Charmed Apache Spark service accounts
also store Apache Spark configuration centrally in Kubernetes as secrets, that must 
be readable/writable depending on their scope. Please refer to the explanations 
about the [Charmed Apache Spark hierachical configuration](/todo) for more information. 

### Metrics

Spark Jobs are ephemeral processes that may be long-lived in some cases but also very 
short-lived on others. Spark Jobs may be launch occasionally, or multiple Spark Jobs
may be running at the same times. 

In this sense, Apache Spark is very different from traditional database management systems
(such as Kafka, MongoDB, PostgreSQL, etc), that are generally unique, with stable endpoints and 
up and running at all times. 

Such services generally expose a stable endpoint where relevant metrics (such as
memory consumption, errors, GC time, etc) can be scraped at regular intervals
by a metric collector component, such as the [Prometheus](https://prometheus.io/)
bundled in COS. However, because of the intrinsic characteristics of Apache Spark, such 
an approach is not directly suitable and feasible for Apache Spark. 

Instead of being passively scraped and metrics being pulled directly by Prometheus, 
Spark Jobs running with Charmed Apache Spark actively push the metrics into 
[Prometheus Pushgateway](https://github.com/prometheus/pushgateway), that is a *sink* component able to temporarily 
store the metrics, and exposing a stable, reliable and long-lived endpoint to be 
scraped by Prometheus. Metrics pushed into Prometheus Pushgateway are organized 
into groups and characterized by a series of labels.

Therefore, Spark Driver and Spark Executors need to be able to export metrics 
and push them to the Prometheus Pushgateway, in appropriate 
groups, so that they can be temporarily stored, exposed and then 
scraped by Prometheus.
Charmed Apache Spark comes with the [spark-metrics](https://github.com/banzaicloud/spark-metrics) 
exporter already packaged in the [Charmed Apache Spark OCI image](https://github.com/canonical/charmed-spark-rock), 
that is used as default base for both Driver and Executors pods.
This exporter is designed to push metrics to the [prometheus-pushgateway-k8s](https://charmhub.io/prometheus-pushgateway)
charm, which is integrated with the [Canonical Observability Stack](https://charmhub.io/topics/canonical-observability-stack).

Once the metrics are ingested by Prometheus, they are then exposed to the user 
through [Grafana](https://grafana.com/) where they can be visualized in custom dashboards. 
Custom alerting rules can also be defined and efficiently managed by [AlertManager](https://prometheus.io/docs/alerting/latest/alertmanager/).

### Logs 

Logs of driver and executors are stored on the pod local filesystem by default, 
however they can also be forwarded to the [Loki](https://grafana.com/oss/loki/) via the `LOKI_URL`
environment variable. This variable is used by [Pebble](https://canonical-pebble.readthedocs-hosted.com/en/latest/),
to configure [log-forwarding](https://canonical-pebble.readthedocs-hosted.com/en/latest/reference/log-forwarding/)
to remote Loki server.

This feature is available from Charmed Spark version [3.4.2/edge](ghcr.io/canonical/charmed-spark:3.4.2-22.04_edge@sha256:321b6deb13f10c045028c9b25264b8113c6fdcbe4f487ff472a06fd7bdcb2758)
and requires a working Loki. Hence, we recommend using it with
[COS](https://charmhub.io/topics/canonical-observability-stack).

Charmed Spark also allows you to store these logs into S3 or Azure storage, so that they can
be re-read and visualized using the Spark History Server, allowing users to monitor 
and visualize the information and metrics about the job execution.