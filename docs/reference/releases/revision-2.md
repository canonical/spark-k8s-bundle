---
myst:
  html_meta:
    description: "Release notes for Charmed Apache Spark revision 2 featuring Apache Kyuubi, enhanced security, Azure support, and observability."
---

(reference-releases-revision-2)=
# Charmed Apache Spark (revision 2)

Jul 29, 2025

We're excited to introduce Apache Kyuubi as part of our expanded Apache Spark charmed bundle—bringing enhanced multi-tenant support and a simplified SQL interface for big data analytics.

This release includes Apache Kyuubi, the Spark History Server, Spark Integration Hub, Spark Client Snap, and Apache Spark OCI Images to deliver a seamless, production-ready fully open-source datalake experience. The Charmed Apache Spark with Apache Kyuubi is available on [charmhub.io](https://charmhub.io) at the `3.4/stable` and `3.5/stable` channels.

Charmhub: [3.4/stable](https://charmhub.io/kyuubi-k8s?channel=3.4/stable), [3.5/stable](https://charmhub.io/kyuubi-k8s?channel=3.5/stable) | [Docs](https://charmhub.io/spark-k8s-bundle) | [Deploy guide](https://charmhub.io/spark-k8s-bundle/docs/h-deploy-kyuubi) | [System requirements](https://canonical.com/data/docs/postgresql/iaas/r-system-requirements)

## Features

### General

- [[DPE-4344](https://warthogs.atlassian.net/browse/DPE-4344);[DPE-2863](https://warthogs.atlassian.net/browse/DPE-2863)] Bundle implementation and integrated testing
- [[DPE-5784](https://warthogs.atlassian.net/browse/DPE-5784)] Azure AKS solution validation

### Kyuubi

- [[DPE-2858](https://warthogs.atlassian.net/browse/DPE-2858)] Basic charm functionalities and testing (s3 support)
- [[DPE-4324](https://warthogs.atlassian.net/browse/DPE-4324)] Support for Azure Object Storage and ADLSv2
- [[DPE-4349](https://warthogs.atlassian.net/browse/DPE-4349)] Enable Kyuubi server high-availability
- [[DPE-4351](https://warthogs.atlassian.net/browse/DPE-4351)] Canonical Observability Stack integration
- [[DPE-5783](https://warthogs.atlassian.net/browse/DPE-5783)] Support for external access with Kubernetes NodePort and LoadBalancer
- [[DPE-5805](https://warthogs.atlassian.net/browse/DPE-5805)] Enable JDBC endpoint encryption
- [[DPE-7087](https://warthogs.atlassian.net/browse/DPE-7087);[DPE-4350](https://warthogs.atlassian.net/browse/DPE-4350)] In-place upgrades with v3 user-experience
- [[DPE-7089](https://warthogs.atlassian.net/browse/DPE-7089)] Canonical built artifact to provide bug fixes and security patching
- [[DPE-7090](https://warthogs.atlassian.net/browse/DPE-7090)] Backup and Restore

### Spark History Server

- [[DPE-2471](https://warthogs.atlassian.net/browse/DPE-2471)] Upgrade to Juju 3
- [[DPE-2859](https://warthogs.atlassian.net/browse/DPE-2859)] OIDC authentication
- [[DPE-3491](https://warthogs.atlassian.net/browse/DPE-3491)] Add tls-chain support in the Spark History Server
- [[DPE-4324](https://warthogs.atlassian.net/browse/DPE-4324)] Support for Azure Object Storage and ADLSv2
- [[DPE-4351](https://warthogs.atlassian.net/browse/DPE-4351)] Canonical Observability Stack integration
- [[DPE-6266](https://warthogs.atlassian.net/browse/DPE-6266)] Prepare charm for charmcraft 3

### Spark Integration Hub

- [[DPE-2861](https://warthogs.atlassian.net/browse/DPE-2861)] Basic charm functionalities and testing (s3 support)
- [[DPE-3724](https://warthogs.atlassian.net/browse/DPE-3724)] Create Integration Hub OCI image
- [[DPE-4324](https://warthogs.atlassian.net/browse/DPE-4324)] Support for Azure Object Storage and ADLSv2
- [[DPE-4351](https://warthogs.atlassian.net/browse/DPE-4351)] Canonical Observability Stack integration
- [[DPE-5794](https://warthogs.atlassian.net/browse/DPE-5794)] Implementation of client <> server charm relation

### Spark Client Snap

- [[DPE-2164](https://warthogs.atlassian.net/browse/DPE-2164)] Expose Spark SQL in Spark Client snap
- [[DPE-3552](https://warthogs.atlassian.net/browse/DPE-3552)] Add self signed certificate handling to the Spark-Client on spark-submit
- [[DPE-4482](https://warthogs.atlassian.net/browse/DPE-4482)] Add tests for Azure Object Storage and ADLSv2
- [[DPE-7131](https://warthogs.atlassian.net/browse/DPE-7131)] Add beeline client to snap

### Charmed Spark OCI Images

- [[DPE-2164](https://warthogs.atlassian.net/browse/DPE-2164)] Add Spark SQL into Charmed Spark Rock image
- [[DPE-2858](https://warthogs.atlassian.net/browse/DPE-2858)] Add Apache Kyuubi Image
- [[DPE-3012](https://warthogs.atlassian.net/browse/DPE-3012)] Add Volcano-integration binaries
- [[DPE-3104](https://warthogs.atlassian.net/browse/DPE-3104)] Create Jupyter notebook image
- [[DPE-3194](https://warthogs.atlassian.net/browse/DPE-3194)] Integrate Apache Iceberg jars with Rock Image
- [[DPE-3514](https://warthogs.atlassian.net/browse/DPE-3514)] Add Apache Kyuubi entrypoint to Charmed Spark base rock image
- [[DPE-4324](https://warthogs.atlassian.net/browse/DPE-4324)] Support for Azure Blob Storage and ADLSv2
- [[DPE-4327](https://warthogs.atlassian.net/browse/DPE-4327)] Create Spark Image with RAPIDS library for GPU support
- [[DPE-4351](https://warthogs.atlassian.net/browse/DPE-4351)] Canonical Observability Stack integration


## Bug fixes

### Spark History Server

- [[DPE-5036](https://warthogs.atlassian.net/browse/DPE-5036);[DPE-3666](https://warthogs.atlassian.net/browse/DPE-3666)] Create S3 bucket if not existing
- [[DPE-6861](https://warthogs.atlassian.net/browse/DPE-6861)] Invalid proxy base when exposed under a subdomain

### Spark Client Snap

- [[DPE-3472](https://warthogs.atlassian.net/browse/DPE-3472)] Fix error when using S3 with PySpark or Spark shell
- [[DPE-3621](https://warthogs.atlassian.net/browse/DPE-3621)] Fix usage of KUBECONFIG environment variable

### Charmed Spark OCI Images

- [[DPE-3017](https://warthogs.atlassian.net/browse/DPE-3017)] Patch Pebble issue on shutdown on failure

## Breaking changes

### Charmed Spark OCI Images

- [[DPE-3067](https://warthogs.atlassian.net/browse/DPE-3067)] Changes following up entrypoint service refactoring\
  _(This change removed the python files needed by Jupyter service, as the Jupyter binaries were moved into a separate image to reduce the security surface of the image)_

## Other improvements

- [[DPE-4325](https://warthogs.atlassian.net/browse/DPE-4325)] Security hardening documentation
- [[DPE-4326](https://warthogs.atlassian.net/browse/DPE-4326)] SSDLC compliance and artifacts
- [[DPE-508](https://warthogs.atlassian.net/browse/DPE-508);[DPE-1748](https://warthogs.atlassian.net/browse/DPE-1748);[DPE-7089](https://warthogs.atlassian.net/browse/DPE-7089)] Artifacts & distributions built from source
- [[DPE-5849](https://warthogs.atlassian.net/browse/DPE-5849)] Kyuubi usage documentation

## Security

The new artifacts have been fixing the following CVEs:

| Severity | Fixed CVEs                                                                                                                                                                                                                                                                                                |
| :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Critical | CVE-2019-10202,CVE-2022-46337,CVE-2023-44981,CVE-2024-47561                                                                                                                                                                                                                                               |
| High     | CVE-2019-0205,CVE-2019-10172,CVE-2020-13949,CVE-2021-22569,CVE-2021-22570,<br>CVE-2021-31684,CVE-2022-3509,CVE-2022-3510,CVE-2022-46751,CVE-2023-1370,<br>CVE-2023-39410,CVE-2023-43642,CVE-2023-52428,CVE-2024-23945,CVE-2024-25638,<br>CVE-2024-36114,CVE-2024-47554,CVE-2024-7254,GHSA-xpw8-rcwv-8f8pe |
| Medium   | CVE-2022-3171,CVE-2023-26048,CVE-2023-34462,CVE-2023-3635,CVE-2023-40167,<br>CVE-2023-42503,CVE-2024-23944,CVE-2024-25710,CVE-2024-26308,CVE-2024-29025,<br>CVE-2024-29131,CVE-2024-29133,CVE-2024-47535,CVE-2024-8184,CVE-2024-9823,<br>CVE-2025-25193                                                   |
| Low      | CVE-2023-26049,CVE-2023-36479,GHSA-58qw-p7qm-5rvh                                                                                                                                                                                                                                                         |


## Compatibility

|          Component          | Hardware architecture |  Channel   |                                                                                                                                                                     Artefact                                                                                                                                                                     | Charm revision | Minimum Juju version | Recommended Juju version |
| :-------------------------: | :-------------------: | :--------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :------------: | :------------------: | :----------------------: |
| Apache Spark History Server |         AMD64         |  3/stable  |                                                   [Charmed Apache Spark Image](http://ghcr.io/canonical/charmed-spark@sha256:f1f944369108c0b0112212fb0242f3c314dfad362926c234857029f13c5de2c0) (Spark version: [3.5.5-ubuntu1](https://launchpad.net/spark-releases/+milestone/3.5.5-ubuntu1))                                                   |       47       |       v.3.4.3+       |         v.3.6.8          |
|    Spark Integration Hub    |         AMD64         |  3/stable  |                                                                                               [Integration Hub Image (3)](http://ghcr.io/canonical/spark-integration-hub@sha256:fa5e73d6339b2eb137b5917771caa62bd6605284b8dfab3dafb7d6026a9a3b1a)                                                                                                |       67       |       v.3.4.3+       |         v.3.6.8          |
|        Apache Kyuubi        |         AMD64         | 3.4/stable | [Charmed Apache Kyuubi Image](http://ghcr.io/canonical/charmed-spark-kyuubi@sha256:38f35ce47b84b8370da9a371edaf83ca9911347a1efd6eb0cfbc8128f051b1e4) (Spark version: [3.4.4-ubuntu2](https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu2), Kyuubi version: [1.10.2-ubuntu1](https://launchpad.net/kyuubi-releases/1.x/1.10.2-ubuntu1)) |      113       |       v.3.4.3+       |         v.3.6.8          |
|        Apache Kyuubi        |         AMD64         | 3.5/stable | [Charmed Apache Kyuubi Image](http://ghcr.io/canonical/charmed-spark-kyuubi@sha256:e2029c6976fc5b9ee2865eced632ca42ce554039d9832af20dfa3e63113e00f7) (Spark version: [3.5.5-ubuntu1](https://launchpad.net/spark-releases/+milestone/3.5.5-ubuntu1), Kyuubi version: [1.10.2-ubuntu1](https://launchpad.net/kyuubi-releases/1.x/1.10.2-ubuntu1)) |      112       |       v.3.4.3+       |         v.3.6.8          |
|      Spark Client Snap      |         AMD64         | 3.4/stable |                                                                                                                          Spark version: [3.4.4-ubuntu2](https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu2)                                                                                                                           |       84       |         N/A          |           N/A            |
|      Spark Client Snap      |         AMD64         | 3.5/stable |                                                                                                                          Spark version: [3.5.5-ubuntu1](https://launchpad.net/spark-releases/+milestone/3.5.5-ubuntu1)                                                                                                                           |       86       |         N/A          |           N/A            |

