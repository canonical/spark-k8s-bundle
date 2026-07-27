---
myst:
  html_meta:
    description: "Release notes for Charmed Apache Spark revision 7 featuring support for Apache Spark 4.0, updated Terraform modules and enhanced security"
---

(reference-releases-revision-7)=
# Charmed Apache Spark (revision 7)

July 28th, 2026

We're excited to announce a new stable release for Charmed Apache Spark.

This release most notably brings the support for Apache Spark 4.0 and a Charmed Apache Spark Terraform Module to deliver a seamless, production-ready and fully open-source data lake experience. Moreover, this new release also comes with enhanced security and bug fixes to the various components that makes the Charmed Apache Spark solution.

Charmhub: [4.0/stable](https://charmhub.io/kyuubi-k8s?channel=4.0/stable) | [Docs](https://canonical.com/data/spark/docs/4.0/) | [Deploy guide](https://canonical.com/data/spark/docs/4.0/how-to/deploy/) | [System requirements](https://canonical.com/data/spark/docs/4.0/reference/requirements/)

## Features

This release includes the following major feature:

* [[PRA-9](https://warthogs.atlassian.net/browse/PRA-9)] Support for Apache Spark 4.0
* [[PRA-234](https://warthogs.atlassian.net/browse/PRA-234)] Terraform modules refactor following CC008 ([#208](https://github.com/canonical/spark-k8s-bundle/pull/208))

## Enhancements

This release includes general enhancements across the solution, as well as to the individual components, as follows.

### General

* [[PRA-9](https://warthogs.atlassian.net/browse/PRA-9)] Support for Apache Spark 4.0
* [[PRA-322](https://warthogs.atlassian.net/browse/PRA-322)] Components upgrade:
  - Apache Spark versions: 4.0.2-ubuntu2
  - Apache Kyuubi versions: 1.11.1-ubuntu1
  - NVIDIA Spark-RAPIDS version: 26.04.2
* General updates of Python dependencies, craft build tools, CI workflows and Github actions
* [[PRA-63](https://warthogs.atlassian.net/browse/PRA-63)] Run integration tests using spread
* [[PRA-74](https://warthogs.atlassian.net/browse/PRA-74)][[PRA-76](https://warthogs.atlassian.net/browse/PRA-76)] Configure Renovate to update OCI resources
* [[PRA-264](https://warthogs.atlassian.net/browse/PRA-264)] Improve TIOBE workflow reliability

### Apache Kyuubi

* [MISC] Enable renovate on track 4, fix oci updates ([#233](https://github.com/canonical/kyuubi-k8s-operator/pull/233))
* [MISC] Log creation of a user and password update events ([#149](https://github.com/canonical/kyuubi-k8s-operator/pull/149)) ([#248](https://github.com/canonical/kyuubi-k8s-operator/pull/248)) ([#246](https://github.com/canonical/kyuubi-k8s-operator/pull/246))

### Apache Spark History Server

* [[PRA-287](https://warthogs.atlassian.net/browse/PRA-287)] Use s3 integrator from track 2 and adopt object-storage-charmlib ([#174](https://github.com/canonical/spark-history-server-k8s-operator/pull/174)) ([#173](https://github.com/canonical/spark-history-server-k8s-operator/pull/173))

### Spark Integration Hub

* [[PRA-277](https://warthogs.atlassian.net/browse/PRA-277)] Use s3 integrator from track 2 and adopt object-storage-charmlib ([#187](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/187)) ([#205](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/205))

### Apache Spark Client snap

* Component bumps (see General section for versions of various components)
* [MISC] Reduce the K8s matrix validation and disable fail-fast feature ([#148](https://github.com/canonical/spark-client-snap/pull/148)) ([#149](https://github.com/canonical/spark-client-snap/pull/149))
* [[PRA-211](https://warthogs.atlassian.net/browse/PRA-211)] Reorder PYTHONPATH to give priority to the snap's stdlib ([#146](https://github.com/canonical/spark-client-snap/pull/146)) ([#150](https://github.com/canonical/spark-client-snap/pull/150))
* [[PRA-256](https://warthogs.atlassian.net/browse/PRA-256)] Set driver metrics sink to JmxSink for shell entrypoints ([#159](https://github.com/canonical/spark-client-snap/pull/159)) ([#160](https://github.com/canonical/spark-client-snap/pull/160))
* [MISC] Remove workflow on_spark_update_available ([#154](https://github.com/canonical/spark-client-snap/pull/154))
* [MISC] Fix permissions for snap release workflow ([#156](https://github.com/canonical/spark-client-snap/pull/156))
* chore: adding scheduled test runs on weekends ([#168](https://github.com/canonical/spark-client-snap/pull/168))
* [MISC] Update renovate configuration ([#162](https://github.com/canonical/spark-client-snap/pull/162))


### Canonical security maintained OCI Images for Apache Spark

* Component bumps (see General section for versions of various components)
* [[PRA-222](https://warthogs.atlassian.net/browse/PRA-222)] Add additional labels (commit hash, source, description, etc.) to the images ([#225](https://github.com/canonical/charmed-spark-rock/pull/225)) ([#226](https://github.com/canonical/charmed-spark-rock/pull/226))


### Charmed Apache Spark Terraform Module

* [[PRA-101](https://warthogs.atlassian.net/browse/PRA-101)] Remove deprecated mailing and updating lock file ([#222](https://github.com/canonical/spark-k8s-bundle/pull/222))
* [[PRA-257](https://warthogs.atlassian.net/browse/PRA-257)] Automatic promotion bundle ([#214](https://github.com/canonical/spark-k8s-bundle/pull/214))
* [MISC] Let users decide whether to use COS in UAT tests ([#232](https://github.com/canonical/spark-k8s-bundle/pull/232))
* [[PRA-306](https://warthogs.atlassian.net/browse/PRA-306)] Unpin juju-agent-version in Spark K8s Bundle integration tests ([#231](https://github.com/canonical/spark-k8s-bundle/pull/231))
* [[PRA-7](https://warthogs.atlassian.net/browse/PRA-7)][[KF-8066](https://warthogs.atlassian.net/browse/KF-8066)] Enable Spark <> Kubeflow integration with new standard ([#233](https://github.com/canonical/spark-k8s-bundle/pull/233))
* [[PRA-318](https://warthogs.atlassian.net/browse/PRA-318)] Implement automated OCI getter for our products ([#240](https://github.com/canonical/spark-k8s-bundle/pull/240))
* [[PRA-324](https://warthogs.atlassian.net/browse/PRA-324)] Split bundle by tracks
* [[PRA-330](https://warthogs.atlassian.net/browse/PRA-330)] Update Postgresql to latest revision on 14/stable ([#251](https://github.com/canonical/spark-k8s-bundle/pull/251))
* [[PRA-324](https://warthogs.atlassian.net/browse/PRA-324)] Update renovate configuration (3.5) ([#253](https://github.com/canonical/spark-k8s-bundle/pull/253)) ([#255](https://github.com/canonical/spark-k8s-bundle/pull/255)) ([#256](https://github.com/canonical/spark-k8s-bundle/pull/256))
* [MISC] chore: adding CODEOWNERS file ([#287](https://github.com/canonical/spark-k8s-bundle/pull/287)) ([#289](https://github.com/canonical/spark-k8s-bundle/pull/289))
* [[PRA-330](https://warthogs.atlassian.net/browse/PRA-330)] Bump postgresql charm to 16/stable on track/4.0 ([#246](https://github.com/canonical/spark-k8s-bundle/pull/246))
* [[PRA-312](https://warthogs.atlassian.net/browse/PRA-312)] Split TLS private key and admin password secrets ([#241](https://github.com/canonical/spark-k8s-bundle/pull/241))

## Bug Fixes

This release includes several bug fixes across the solution, which are listed below categorized to individual components.

### Apache Kyuubi

* [MISC] Fix invalid JSON5 syntax in Renovate repository config ([#213](https://github.com/canonical/kyuubi-k8s-operator/pull/213)) ([#217](https://github.com/canonical/kyuubi-k8s-operator/pull/217)) ([#218](https://github.com/canonical/kyuubi-k8s-operator/pull/218))

### Apache Spark History Server

* [MISC] Fix Github workflow permissions ([#181](https://github.com/canonical/spark-history-server-k8s-operator/pull/181)) ([#182](https://github.com/canonical/spark-history-server-k8s-operator/pull/182))

### Spark Integration Hub

* [[PRA-168](https://warthogs.atlassian.net/browse/PRA-168)] Charm errors when related to the s3-integrator and bucket name is empty ([#203](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/203))
* [MISC] Grant actions: read and contents: read permissions to Release workflow ci-tests caller ([#216](https://github.com/canonical/spark-integration-hub-k8s-operator/pull/216))

### Canonical security maintained OCI Images for Apache Spark

* [[PRA-221](https://warthogs.atlassian.net/browse/PRA-221)] Fix trivy scan failures ([#248](https://github.com/canonical/charmed-spark-rock/pull/248)) ([#223](https://github.com/canonical/charmed-spark-rock/pull/223)) ([#224](https://github.com/canonical/charmed-spark-rock/pull/224))
* [MISC] Various fixes in the GithHub workflows ([#231](https://github.com/canonical/charmed-spark-rock/pull/231))

## Breaking Changes

This release includes the following breaking change:

### Charmed Apache Spark Terraform Module

* [[PRA-234](https://warthogs.atlassian.net/browse/PRA-234)] Terraform modules refactor following CC008 ([#208](https://github.com/canonical/spark-k8s-bundle/pull/208))

## Documentation improvements

The current release also features the following documentation changes:

* [[PRA-11](https://warthogs.atlassian.net/browse/PRA-11)] Automated tutorial testing ([#221](https://github.com/canonical/spark-k8s-bundle/pull/221))
* docs: FE Feedback fixes ([#210](https://github.com/canonical/spark-k8s-bundle/pull/210))
* [[PRA-309](https://warthogs.atlassian.net/browse/PRA-309)] Update docs for s3-integrator 2/stable and multi-track awareness ([#237](https://github.com/canonical/spark-k8s-bundle/pull/237))
* [[PRA-165](https://warthogs.atlassian.net/browse/PRA-165)] Update docs to reflect correct behavior when S3 region is not configured ([#257](https://github.com/canonical/spark-k8s-bundle/pull/257)) ([#284](https://github.com/canonical/spark-k8s-bundle/pull/284)) ([#286](https://github.com/canonical/spark-k8s-bundle/pull/286))
* [[PRA-324](https://warthogs.atlassian.net/browse/PRA-324)] Adapt docs content to match Spark version on various tracks ([#252](https://github.com/canonical/spark-k8s-bundle/pull/252)) ([#258](https://github.com/canonical/spark-k8s-bundle/pull/258)) ([#254](https://github.com/canonical/spark-k8s-bundle/pull/254))

## Security

The following CVEs have been fixed in the new artifacts:

```{eval-rst}
+------------------+----------+-----------------------------------------------------------------------------------------------+
| Component        | Severity | Fixed                                                                                         |
+==================+==========+===============================================================================================+
| Apache Spark     | High     | CVE-2025-48734, CVE-2025-67721, CVE-2026-24281, CVE-2026-24308, CVE-2025-54920                |
+                  +----------+-----------------------------------------------------------------------------------------------+
|                  | Medium   | CVE-2026-34477, CVE-2026-34478, CVE-2026-34479, CVE-2026-34480                                |
+------------------+----------+-----------------------------------------------------------------------------------------------+
| Apache Kyuubi    | High     | CVE-2025-48734, CVE-2026-33870, CVE-2026-33871, CVE-2026-35554, CVE-2026-42198,               |
|                  |          | CVE-2026-42577, CVE-2026-42579, CVE-2026-42583, CVE-2026-42584, CVE-2026-42587,               |
|                  |          | CVE-2026-44249, CVE-2026-45416, CVE-2026-45674, CVE-2026-47691, CVE-2026-50010                |
+                  +----------+-----------------------------------------------------------------------------------------------+
|                  | Medium   | CVE-2026-33558, CVE-2026-34477, CVE-2026-34478, CVE-2026-34479, CVE-2026-34480,               |
|                  |          | CVE-2026-41417, CVE-2026-42580, CVE-2026-42581, CVE-2026-42585, CVE-2026-45536,               |
|                  |          | CVE-2026-45673, CVE-2026-47244, CVE-2026-48043, CVE-2026-50020, CVE-2026-50560,               |
|                  |          | CVE-2026-6860                                                                                 |
+                  +----------+-----------------------------------------------------------------------------------------------+
|                  | Low      | CVE-2026-42578                                                                                |
+------------------+----------+-----------------------------------------------------------------------------------------------+
```

## Compatibility

The following table summarize the compatibility matrix of the solution:

```{eval-rst}
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Component                   | Hardware architecture | Channel             | Artifact                                                                                                                                                                                                                                                                                                                                        | Revision | Minimum Juju version | Recommended Juju version |
+=============================+=======================+=====================+=================================================================================================================================================================================================================================================================================================================================================+==========+======================+==========================+
| Apache Spark History Server | AMD64                 | 4/stable            | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark/967526337>`__ (Apache Spark version: `4.0.2-ubuntu2 <https://launchpad.net/spark-releases/+milestone/4.0.2-ubuntu2>`__)                                                                                                               | 119       | v.3.6.13+            | v.3.6.25                 |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 4/candidate         | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark/967526337>`__ (Apache Spark version: `4.0.2-ubuntu2 <https://launchpad.net/spark-releases/+milestone/4.0.2-ubuntu2>`__)                                                                                                               | 118       | v.3.6.13+            | v.3.6.25                 |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Spark Integration Hub       | AMD64                 | 3/stable            | `Integration Hub Image (13) <https://github.com/canonical/spark-integration-hub-rock/pkgs/container/spark-integration-hub/746475114>`__                                                                                                                                                                                                         | 134       | v.3.6.13+            | v.3.6.25                 |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 3/candidate         | `Integration Hub Image (13) <https://github.com/canonical/spark-integration-hub-rock/pkgs/container/spark-integration-hub/746475114>`__                                                                                                                                                                                                         | 133       | v.3.6.13+            | v.3.6.25                 |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Apache Kyuubi               | AMD64                 | 4.0/stable          | `Charmed Apache Kyuubi Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-kyuubi/967540665>`__ (Apache Spark version: `4.0.2-ubuntu2 <https://launchpad.net/spark-releases/+milestone/4.0.2-ubuntu2>`__, Apache Kyuubi version: `1.11.1-ubuntu1 <https://launchpad.net/kyuubi-releases/1.x/1.11.1-ubuntu1>`__) | 181      | v.3.6.13+            | v.3.6.25                 |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 4.0/candidate       | `Charmed Apache Kyuubi Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-kyuubi/967540665>`__ (Apache Spark version: `4.0.2-ubuntu2 <https://launchpad.net/spark-releases/+milestone/4.0.2-ubuntu2>`__, Apache Kyuubi version: `1.11.1-ubuntu1 <https://launchpad.net/kyuubi-releases/1.x/1.11.1-ubuntu1>`__) | 179      | v.3.6.13+            | v.3.6.25                 |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Apache Spark Client Snap    | AMD64                 | 4.0/stable          | Apache Spark version: `4.0.2-ubuntu2 <https://launchpad.net/spark-releases/+milestone/4.0.2-ubuntu2>`__                                                                                                                                                                                                                                         | 152      | N/A                  | N/A                      |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 4.0/candidate       | Apache Spark version: `4.0.2-ubuntu2 <https://launchpad.net/spark-releases/+milestone/4.0.2-ubuntu2>`__                                                                                                                                                                                                                                         | 151      | N/A                  | N/A                      |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Charmed Apache Spark        | AMD64                 | 4.0-22.04_stable    | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark/967526337>`__ Apache Spark version: `4.0.2-ubuntu2 <https://launchpad.net/spark-releases/+milestone/4.0.2-ubuntu2>`__                                                                                                                 | N/A      | N/A                  | N/A                      |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 4.0-22.04_candidate | `Charmed Apache Spark Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark/967526337>`__ Apache Spark version: `4.0.2-ubuntu2 <https://launchpad.net/spark-releases/+milestone/4.0.2-ubuntu2>`__                                                                                                                 | N/A      | N/A                  | N/A                      |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
| Charmed Apache Spark        | AMD64                 | 4.0-22.04_stable    | `Charmed Apache Spark GPU Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-gpu/967569367>`__ Apache Spark version: `4.0.2-ubuntu2 <https://launchpad.net/spark-releases/+milestone/4.0.2-ubuntu2>`__ NVIDIA Spark RAPIDS version: `26.04.2`                                                                  | N/A      | N/A                  | N/A                      |
+                             +-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
|                             | ARM64                 | 4.0-22.04_candidate | `Charmed Apache Spark GPU Image <https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark-gpu/967569367>`__ Apache Spark version: `4.0.2-ubuntu2 <https://launchpad.net/spark-releases/+milestone/4.0.2-ubuntu2>`__ NVIDIA Spark RAPIDS version: `26.04.2`                                                                  | N/A      | N/A                  | N/A                      |
+-----------------------------+-----------------------+---------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------+----------------------+--------------------------+
```

```{note}
Model destruction for controllers above 3.6.18+ may sometimes freeze (see [Juju issue #22105](https://github.com/juju/juju/issues/22105)). In these cases, we recommend destroying the resources manually.
```

## Acknowledgements

We are extremely grateful to the Apache Spark and Apache Kyuubi communities for their continuous work, involvement and engagement with open-source to make technologies that process data at scale available to the broader audience.