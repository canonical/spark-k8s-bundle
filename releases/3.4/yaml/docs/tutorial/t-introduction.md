# Tutorial

Charmed Apache Spark provides utility client applications and additional components for seamless deployment on Kubernetes. For a detailed overview of its components, see the [Components overview](/t/11685) page.

## Prerequisites

While this tutorial intends to guide you as you deploy Charmed Apache Spark for the first time, it will be most beneficial if you have:

* Experience using a Linux-based CLI
* General familiarity with Kubernetes commands and concepts (e.g. `kubectl` command)
* Familiarity with Apache Spark commands and concepts
* A computer that meets the [minimum system requirements](/t/8962)

## Step-by-step learning experience

To get started, follow this tutorial through each step of the process:

| Step | Description |
| ------- | ---------- |
| 1. Introduction | This page.
| 2. [Initial set up](set-up.md) | Prepare your cloud environment using Multipass and deploy Apache Spark with Juju.
| 3. [Distributed data processing](distributed.md) | Explore how to process large datasets efficiently across multiple nodes.
| 4. [Streaming workload processing](stream.md) | Learn how to handle real-time data streams.
| 5. [History server](history-server.md) | Integrate with Apache Spark History Server.
| 6. [Monitoring](cos.md) | Set up monitoring and alerting using Canonical's Observability Stack (COS).
| 7. [Kyuubi](kyuubi.md) | Scale your application by adding or removing juju units
| 8. [Finish and clean up](finish.md) | Finish the tutorial by decommissioning your Charmed Apache Spark deployment and Juju environment to free up system resources.

## Next step

Let's proceed to set up the environment needed for this tutorial in the [next section](/t/13233).