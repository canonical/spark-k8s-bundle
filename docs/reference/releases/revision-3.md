---
myst:
  html_meta:
    description: "Release notes for Charmed Apache Spark revision 3 featuring Apache Kyuubi, enhanced security, Azure support, and observability."
---

(reference-releases-revision-3)=
# Charmed Apache Spark (revision 3)

Mar XX, 2026

We're excited to announce a new stable release for Charmed Apache Spark.

This release includes support for Apache Kyuubi, the Apache Spark History Server, Spark Integration Hub, Apache Spark Client Snap, Canonical security maintained OCI images for Apache Spark and a Charmed Apache Spark Terraform Module to deliver a seamless, production-ready and fully open-source datalake experience. Charmed Apache Spark with Apache Kyuubi is available on [charmhub.io](https://charmhub.io) at the `3.4/stable` and `3.5/stable` channels.

Charmhub: [3.4/candidate](https://charmhub.io/kyuubi-k8s?channel=3.4/candidate), [3.5/candidate](https://charmhub.io/kyuubi-k8s?channel=3.5/candidate) | [Docs](https://canonical-charmed-spark.readthedocs-hosted.com/) | [Deploy guide](https://canonical-charmed-spark.readthedocs-hosted.com/main/how-to/deploy/) | [System requirements](https://canonical-charmed-spark.readthedocs-hosted.com/main/reference/requirements/)

## Features

This release includes general updates across the solution, as well as changes to individual components.

### General

- [[DPE-7941](https://warthogs.atlassian.net/browse/DPE-2858)] Add GPU Support. Please refer to the [How to use GPU](/how-to/use-gpu) user guide for more information. 
- [[PRA-156](https://warthogs.atlassian.net/browse/PRA-156)] Add ARM support (experimental) - the feature will only be available on candidate risks for now. To deploy on ARM architecture, use the juju `set-model-constraints` command line switch when creating juju models or specify the architecture using the juju `--constraints` command line switch at deploy time. More information can be found in the [Advanced Scheduling](/how-to/advanced-scheduling) user guide
- [[PRA-158](https://warthogs.atlassian.net/browse/PRA-158)] Components upgrade:
  - Apache Spark version: 3.4.4-ubuntu7 and 3.5.7-ubuntu2
  - Apache Kyuubi version: 1.10.3-ubuntu1 
  - spark8t python library: 1.3.1
  - nvidia spark-rapids: 25.12.0
- [[PRA-73](https://warthogs.atlassian.net/browse/PRA-73)] Update juju version to 3.6.13+
- [[PRA-145](https://warthogs.atlassian.net/browse/PRA-145)] Validation on multiple K8s supported versions (refer to the requirements documentation for more info)
- [[DPE-8681](https://warthogs.atlassian.net/browse/DPE-8681)] Testing and validation for MicroCeph instead of MinIO
- Migrated from DPE to PRA Jira project
- General updates of Python dependencies, craft build tools, CI workflows and Github actions

### Apache Kyuubi

- [[PRA-158](https://warthogs.atlassian.net/browse/PRA-158)] Apache Kyuubi version update to 1.10.3-ubuntu1
- [[DPE-8542](https://warthogs.atlassian.net/browse/DPE-8542),[DPE-8549](https://warthogs.atlassian.net/browse/DPE-8549)] Rework health check ([#150](https://github.com/canonical/kyuubi-k8s-operator/pull/150)) ([#151](https://github.com/canonical/kyuubi-k8s-operator/pull/151))
- [[DPE-8342](https://warthogs.atlassian.net/browse/DPE-8342)] Rework metrics alerts ([#142](https://github.com/canonical/kyuubi-k8s-operator/pull/142)) ([#146](https://github.com/canonical/kyuubi-k8s-operator/pull/146))
- [[DPE-8288](https://warthogs.atlassian.net/browse/DPE-8288)] Implement new dashboard from upstream ([#144](https://github.com/canonical/kyuubi-k8s-operator/pull/144)) ([#145](https://github.com/canonical/kyuubi-k8s-operator/pull/145))
- [[DPE-8376](https://warthogs.atlassian.net/browse/PRA-8376)] Charm consolidation ([#147](https://github.com/canonical/kyuubi-k8s-operator/pull/147))

### Apache Spark History Server

- [[PRA-200](https://warthogs.atlassian.net/browse/PRA-200)] Explicit proxy support for S3-compliant storage ([#143](https://github.com/canonical/spark-history-server-k8s-operator/pull/143))
- [[DPE-8481](https://warthogs.atlassian.net/browse/DPE-8481)] Add integration with oauth2proxy ([#123](https://github.com/canonical/spark-history-server-k8s-operator/pull/123))
- Enforce type checking ([#146](https://github.com/canonical/spark-history-server-k8s-operator/pull/146))

### Spark Integration Hub

- [[PRA-158](https://warthogs.atlassian.net/browse/PRA-158)] Update OCI resource to latest release ([#181](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/181))
- [[PRA-200](https://warthogs.atlassian.net/browse/PRA-200)] Explicit proxy support for S3-compliant storage ([#171](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/171))
- [[PRA-156](https://warthogs.atlassian.net/browse/PRA-156)] Fix broken release check due to multiple platforms ([#158](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/158))
- [[PRA-152](https://warthogs.atlassian.net/browse/PRA-152)] Serialize asterisk characters when generating resource manifest ([#144](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/144))
- [[PRA-113](https://warthogs.atlassian.net/browse/PRA-113)] Add a config option to specify custom Apache Spark image ([#134](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/134))
- [[PRA-30](https://warthogs.atlassian.net/browse/PRA-30)] Add monitored-service-accounts configuration option ([#120](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/120))
- [[DPE-7840](https://warthogs.atlassian.net/browse/DPE-7840)] Share manifest of the K8s resources over the spark service account relation ([#99](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/99))
- [[PRA-199](https://warthogs.atlassian.net/browse/PRA-199)[PRA-220](https://warthogs.atlassian.net/browse/PRA-220)] Add support for s3 certificates and fix secret deletion ([#180](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/180))

### Apache Spark Client snap

- [[DPE-7923](https://warthogs.atlassian.net/browse/DPE-7923)] Suppress AWS Java SDK v1 warning message in snap ([#131](https://github.com/canonical/spark-client-snap/pull/131))

### Canonical security maintained OCI Images for Apache Spark

- [[PRA-158](https://warthogs.atlassian.net/browse/PRA-158)] Component bumps ([#217](https://github.com/canonical/charmed-spark-rock/pull/217))
- [[DPE-7941](https://warthogs.atlassian.net/browse/DPE-7941)] Add gpu executor pod template to Charmed Apache Kyuubi image ([#165](https://github.com/canonical/charmed-spark-rock/pull/165))
- [[PRA-189](https://warthogs.atlassian.net/browse/PRA-189)] Check for environment variable expansion ([#221](https://github.com/canonical/charmed-spark-rock/pull/221))
- Download Hive from mirror ([#163](https://github.com/canonical/charmed-spark-rock/pull/163))
- Perform disk cleanup at the start of all workflows ([#190](https://github.com/canonical/charmed-spark-rock/pull/190))
- Run Trivy scan on 3.5/edge and 3.4/edge ([#151](https://github.com/canonical/charmed-spark-rock/pull/151)) ([#171](https://github.com/canonical/charmed-spark-rock/pull/171))

### Charmed Apache Spark Terraform Module

- [[DPE-7943](https://warthogs.atlassian.net/browse/DPE-7943)] Improve stability of UAT and CI tests ([#142](https://github.com/canonical/spark-k8s-bundle/pull/142))
- [[DPE-7722](https://warthogs.atlassian.net/browse/DPE-7722)] Enable Reference Architecture (AKS) testing ([#136](https://github.com/canonical/spark-k8s-bundle/pull/136)) ([#173](https://github.com/canonical/spark-k8s-bundle/pull/173))
- [[DPE-6777](https://warthogs.atlassian.net/browse/DPE-6777] Demo update based on Charmed Apache Kyuubi GA ([#131](https://github.com/canonical/spark-k8s-bundle/pull/131))
- [MISC] Pin cos-configuration-k8s to rev65 on YAML bundle ([#156](https://github.com/canonical/spark-k8s-bundle/pull/156))

## Bug fixes

This release includes bug fixes grouped by component.

### Apache Spark History Server

- [[PRA-140](https://warthogs.atlassian.net/browse/PRA-140)] Block charm in case of missing object storage path ([#145](https://github.com/canonical/spark-history-server-k8s-operator/pull/145))

### Canonical security maintained OCI Images for Apache Spark

- [[PRA-134](https://warthogs.atlassian.net/browse/PRA-134)] Add py4j dependency to PYTHONPATH in rock image ([#180](https://github.com/canonical/charmed-spark-rock/pull/180))
- [[PRA-136](https://warthogs.atlassian.net/browse/PRA-136)] Release tag not found ([#182](https://github.com/canonical/charmed-spark-rock/pull/182)) ([#185](https://github.com/canonical/charmed-spark-rock/pull/185)) ([#186](https://github.com/canonical/charmed-spark-rock/pull/186))
- [[PRA-222](https://warthogs.atlassian.net/browse/PRA-222)] Add additional labels to rocks ([#225](https://github.com/canonical/charmed-spark-rock/pull/225))

### Charmed Apache Spark Terraform Module

- [[PRA-163](https://warthogs.atlassian.net/browse/PRA-163)] Remove wrong quote ([#191](https://github.com/canonical/spark-k8s-bundle/pull/191))
- [[DPE-8292](https://warthogs.atlassian.net/browse/DPE-8292)] Add missing offers in Charmed Apache Spark 3.5 ([#144](https://github.com/canonical/spark-k8s-bundle/pull/144))
- fix: Pin terraform provider to <1.0.0 ([#167](https://github.com/canonical/spark-k8s-bundle/pull/167))

## Breaking changes

This release includes breaking changes grouped by component.

### Spark Integration Hub

- [[PRA-73](https://warthogs.atlassian.net/browse/PRA-73)] Restore Juju 3.6.13+ compatibility ([#172](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/172))

## Documentation improvements

The current release also features the following documentation changes:

- Polish the terminology capitalisation ([#188](https://github.com/canonical/spark-k8s-bundle/pull/188))
- Add auto-generated metadata description ([#186](https://github.com/canonical/spark-k8s-bundle/pull/186))
- Fix the docs badge in README ([#187](https://github.com/canonical/spark-k8s-bundle/pull/187))
- Home page remodeling ([#181](https://github.com/canonical/spark-k8s-bundle/pull/181))
- Update home page ([#163](https://github.com/canonical/spark-k8s-bundle/pull/163))
- Clarify how to use self-signed S3 endpoints ([#164](https://github.com/canonical/spark-k8s-bundle/pull/164))
- Add landing pages ([#159](https://github.com/canonical/spark-k8s-bundle/pull/159))
- Add cookie consent request ([#157](https://github.com/canonical/spark-k8s-bundle/pull/157))
- Update the cookie banner design ([#193](https://github.com/canonical/spark-k8s-bundle/pull/193))
- Update spelling to US English ([#196](https://github.com/canonical/spark-k8s-bundle/pull/196))
- Add redirects for RTD docs ([#160](https://github.com/canonical/spark-k8s-bundle/pull/160))
- Update documentation on Security page to reflect new UX ([#158](https://github.com/canonical/spark-k8s-bundle/pull/158))
- Initial documentation migration to RTD ([#148](https://github.com/canonical/spark-k8s-bundle/pull/148))
- Add Charmed Apache Kyuubi docs ([#134](https://github.com/canonical/spark-k8s-bundle/pull/134))

## Security

The new artifacts have been fixing the following CVEs:

```{eval-rst}
+------------------+----------+-----------------------------------------------------------------------------------------------+
| Component        | Severity | Fixed                                                                                         |
+==================+==========+===============================================================================================+
| Apache Spark     | High     | CVE-2021-33813, CVE-2024-13009, CVE-2025-12183, CVE-2025-66566                                |
+                  +----------+-----------------------------------------------------------------------------------------------+
|                  | Medium   | CVE-2025-68161                                                                                |
+------------------+----------+-----------------------------------------------------------------------------------------------+
| Apache Kyuubi    | High     | CVE-2025-24970, CVE-2025-55163, CVE-2025-66518                                                |
+                  +----------+-----------------------------------------------------------------------------------------------+
|                  | Medium   | CVE-2024-47535, CVE-2025-25193, CVE-2025-58057, CVE-2025-67735, CVE-2025-68161, CVE-2026-1002 |
+------------------+----------+-----------------------------------------------------------------------------------------------+
```

## Compatibility

The following table summarize the compatibility matrix of the solution:


```{eval-rst}
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Component                   | Hardware architecture | Channel             | Artefact                                                                                                                                                                                                                                                                                                                                        | Revision | Minimum Juju version | Recommended Juju version |
+=============================+=======================+=====================+=================================================================================================================================================================================================================================================================================================================================================+==========+======================+==========================+
| Apache Spark History Server | AMD64                 | 3/stable            | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark/709275803>`__ (Apache Spark version: `3.5.7-ubuntu2 <https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2>`__)                                                                                                               | 94       | v.3.6.13+            | v.3.6.14                 |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3/candidate         | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark/709276863>`__ (Apache Spark version: `3.5.7-ubuntu2 <https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2>`__)                                                                                                               | 93       | v.3.6.13+            | v.3.6.14                 |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Spark Integration Hub       | AMD64                 | 3/stable            | `Integration Hub Image (11) <https://github.com/canonical/spark-integration-hub-rock/pkgs/container/spark-integration-hub/746474644>`__                                                                                                                                                                                                         | 113      | v.3.6.13+            | v.3.6.14                 |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3/candidate         | `Integration Hub Image (11) <https://github.com/canonical/spark-integration-hub-rock/pkgs/container/spark-integration-hub/746475030>`__                                                                                                                                                                                                         | 114      | v.3.6.13+            | v.3.6.14                 |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Apache Kyuubi               | AMD64                 | 3.4/stable          | `Charmed Apache Kyuubi Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-kyuubi/708924316>`__ (Apache Spark version: `3.4.4-ubuntu7 <https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7>`__, Apache Kyuubi version: `1.10.3-ubuntu1 <https://launchpad.net/kyuubi-releases/1.x/1.10.3-ubuntu1>`__) | 140      | v.3.6.13+            | v.3.6.14                 |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3.4/candidate       | `Charmed Apache Kyuubi Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-kyuubi/708924974>`__ (Apache Spark version: `3.4.4-ubuntu7 <https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7>`__, Apache Kyuubi version: `1.10.3-ubuntu1 <https://launchpad.net/kyuubi-releases/1.x/1.10.3-ubuntu1>`__) | 141      | v.3.6.13+            | v.3.6.14                 |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | AMD64                 | 3.5/stable          | `Charmed Apache Kyuubi Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-kyuubi/709279230>`__ (Apache Spark version: `3.5.7-ubuntu2 <https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2>`__, Apache Kyuubi version: `1.10.3-ubuntu1 <https://launchpad.net/kyuubi-releases/1.x/1.10.3-ubuntu1>`__) | 142      | v.3.6.13+            | v.3.6.14                 |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3.5/candidate       | `Charmed Apache Kyuubi Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-kyuubi/709281645>`__ (Apache Spark version: `3.5.7-ubuntu2 <https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2>`__, Apache Kyuubi version: `1.10.3-ubuntu1 <https://launchpad.net/kyuubi-releases/1.x/1.10.3-ubuntu1>`__) | 143      | v.3.6.13+            | v.3.6.14                 |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Apache Spark Client Snap    | AMD64                 | 3.4/stable          | Apache Spark version: `3.4.4-ubuntu7 <https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7>`__                                                                                                                                                                                                                                         | 100      | N/A                  | N/A                      |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3.4/candidate       | Apache Spark version: `3.4.4-ubuntu7 <https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7>`__                                                                                                                                                                                                                                         | 102      | N/A                  | N/A                      |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | AMD64                 | 3.5/stable          | Apache Spark version: `3.5.7-ubuntu2 <https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2>`__                                                                                                                                                                                                                                         | 101      | N/A                  | N/A                      |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3.5/candidate       | Apache Spark version: `3.5.7-ubuntu2 <https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2>`__                                                                                                                                                                                                                                         | 99       | N/A                  | N/A                      |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Charmed Apache Spark        | AMD64                 | 3.4-22.04_stable    | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark/708922026>`__ Apache Spark version: `3.4.4-ubuntu7 <https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7>`__                                                                                                                 | 100      | N/A                  | N/A                      |
+ Base Image                  +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3.4-22.04_candidate | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark/708921424>`__ Apache Spark version: `3.4.4-ubuntu7 <https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7>`__                                                                                                                 | 102      | N/A                  | N/A                      |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | AMD64                 | 3.5-22.04_stable    | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark/709275803>`__ Apache Spark version: `3.5.7-ubuntu2 <https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2>`__                                                                                                                 | 101      | N/A                  | N/A                      |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3.5-22.04_candidate | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark/709276863>`__ Apache Spark version: `3.5.7-ubuntu2 <https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2>`__                                                                                                                 | 99       | N/A                  | N/A                      |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Charmed Apache Spark        | AMD64                 | 3.4-22.04_stable    | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-gpu/708928598>`__ Apache Spark version: `3.4.4-ubuntu7 <https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7>`__                                                                                                             | 100      | N/A                  | N/A                      |
+ GPU Image                   +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3.4-22.04_candidate | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-gpu/708927104>`__ Apache Spark version: `3.4.4-ubuntu7 <https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7>`__                                                                                                             | 102      | N/A                  | N/A                      |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | AMD64                 | 3.5-22.04_stable    | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-gpu/709285355>`__ Apache Spark version: `3.5.7-ubuntu2 <https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2>`__                                                                                                             | 101      | N/A                  | N/A                      |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3.5-22.04_candidate | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-gpu/709284268>`__ Apache Spark version: `3.5.7-ubuntu2 <https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2>`__                                                                                                             | 99       | N/A                  | N/A                      |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
```

```{note}
Juju controller versions from `3.9.10` to `3.6.12` are affected by a [regression in Juju](https://github.com/juju/juju/issues/21312) that has been fixed in `3.6.13` that will not claim management over resources when tag appropriately.
Support for Juju `3.6.13+` has been addressed by [this issue](https://github.com/canonical/spark-integration-hub-k8s-operator/issues/119) to now forcefully label 
resources managed by integration hub with `app.kubernetes.io/managed-by=spark8t`.
```

```{note}
When using Juju controller versions greater or equal to `3.6.13`, make sure you use a charm revision above `107` for `spark-integration-hub-k8s`. On Juju controller versions lower or equal to `3.6.9`, use charm revisions below `107`.
```

```{note}
Model destruction for controllers above 3.6.18+ may sometimes freeze (see [Juju issue #22105](https://github.com/juju/juju/issues/22105)). In these cases, we recommend destroying the resources manually.
```
