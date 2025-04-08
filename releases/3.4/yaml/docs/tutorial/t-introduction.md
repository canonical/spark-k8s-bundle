# 1. Tutorial introduction

Charmed Apache Spark provides utility client applications and additional components for seamless deployment on Kubernetes. For a detailed overview of its components, see the [Components overview](/t/11685) page.

## Prerequisites

While this tutorial intends to guide you as you deploy Charmed Apache Spark for the first time, it will be most beneficial if you have:

* Experience using a Linux-based CLI
* General familiarity with Kubernetes commands and concepts (e.g. `kubectl` command)
* Familiarity with Apache Spark commands and concepts
* A computer that meets the Minimum system requirements from the [Initial set up page](set-up.md)

## Step-by-step learning experience

To get started, follow this tutorial through each step of the process:

| Step | Description |
| ------- | ---------- |
| 1. Introduction | This page.
| 2. [Environment setup](t-setup.md) | Prepare your tutorial environment using a Multipass VM and deploy Apache Spark with `spark-client` snap.
| 3. [Distributed data processing](t-data-processing.md) | Explore how to process large datasets efficiently across multiple nodes.
<!-- | 4. [Streaming workload processing](stream.md) | Learn how to handle real-time data streams. -->
| 4. [History server](t-history-server.md) | Integrate with Apache Spark History Server.
| 5. [Monitoring with COS](t-cos.md) | Set up monitoring and alerting using Canonical's Observability Stack (COS).
| 6. [Wrapping up](t-wrapping-up.md) | Finish the tutorial by decommissioning your Charmed Apache Spark environment to free up system resources.
