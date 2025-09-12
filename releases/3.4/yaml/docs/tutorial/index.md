(tutorial-introduction)=
# Charmed Apache Spark Solution Tutorial

Charmed Apache Spark provides utility client applications and additional components for seamless deployment on Kubernetes. For a detailed overview of its components, see the [Components overview](/explanation/component-overview) page.

## Prerequisites

While this tutorial intends to guide you as you deploy Charmed Apache Spark for the first time, it will be most beneficial if you have:

* Experience using a Linux-based CLI
* General familiarity with Kubernetes commands and concepts (e.g. `kubectl` command)
* Familiarity with Apache Spark commands and concepts
* A computer that meets the Minimum system requirements from the [Environment setup](tutorial-1-environment-setup) page

(tutorial-index)=
## Step-by-step learning experience

This tutorial is divided into multiple steps, which we recommend following in the specified order:

| Step | Description |
| ------- | ---------- |
| 1. [Environment setup](/tutorial/1-environment-setup) | Prepare your tutorial environment using a Multipass VM and deploy Apache Spark with the `spark-client` snap.|
| 2. [Distributed data processing](/tutorial/2-distributed-data-processing) | Explore how to process large datasets efficiently across multiple nodes.|
| 3. [Data stream processing](/tutorial/3-data-stream-processing) | Learn how to handle real-time data streams.|
| 4. [History server](/tutorial/4-history-server) | Integrate with Apache Spark History Server.|
| 5. [Monitoring with COS](/tutorial/5-monitoring-with-cos) | Set up monitoring and alerting using Canonical's Observability Stack (COS).|
| 6. [Apache Kyuubi](/tutorial/6-apache-kyuubi) | Learn how to deploy and use Charmed Apache Kyuubi.|
| 7. [Wrapping up](/tutorial/7-wrapping-up) | Finish the tutorial by decommissioning your Charmed Apache Spark environment to free up system resources.|

```{toctree}
:titlesonly:
:hidden:

1-environment-setup.md
2-distributed-data-processing.md
3-data-stream-processing.md
4-history-server.md
5. Monitoring with COS<5-monitoring-with-cos.md>
6. Apache Kyuubi<6-apache-kyuubi.md>
7-wrapping-up.md
```
