---
myst:
  html_meta:
    description: "Guides for deploying and configuring Charmed Apache Spark to schedule workloads on dedicated worker pools."
---

(how-to-advanced-scheduling-index)=

# Advanced Scheduling

You can optimize infrastructure governance and performance by configuring Charmed Apache Spark with Kubernetes mechanisms, such as node affinity and toleration.

Those mechanisms are used to decouple control plane operations from user-driven workloads, ensuring system services remain stable on cost-effective instance.
Spark executors can benefit from specialized hardware (high-memory nodes, custom hardware resources such as GPU, specific architecture) while maintaining the flexibility to scale idle resources to zero.

```{toctree}
:titlesonly:

Advanced scheduling of Spark jobs<jobs.md>
Advanced scheduling of Charmed Apache Spark components<components.md>
```
