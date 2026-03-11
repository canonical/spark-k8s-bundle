---
myst:
  html_meta:
    description: "Release notes for Charmed Apache Spark revision 3 featuring Apache Kyuubi, enhanced security, Azure support, and observability."
---

(reference-releases-revision-3)=
# Charmed Apache Spark (revision 3)

Mar XX, 2026

We're excited to announce a new stable release for Charmed Spark.

This release includes Apache Kyuubi, the Spark History Server, Spark Integration Hub, Spark Client Snap, Apache Spark OCI Images and a Charmed Spark Terraform Module to deliver a seamless, production-ready and fully open-source datalake experience. The Charmed Apache Spark with Apache Kyuubi is available on [charmhub.io](https://charmhub.io) at the `3.4/stable` and `3.5/stable` channels.

Charmhub: [3.4/candidate](https://charmhub.io/kyuubi-k8s?channel=3.4/candidate), [3.5/candidate](https://charmhub.io/kyuubi-k8s?channel=3.5/candidate) | [Docs](https://charmhub.io/spark-k8s-bundle) | [Deploy guide](https://charmhub.io/spark-k8s-bundle/docs/h-deploy-kyuubi) | [System requirements](https://canonical.com/data/docs/postgresql/iaas/r-system-requirements)

## Features

### General

- [[DPE-7941](https://warthogs.atlassian.net/browse/DPE-2858)] Add GPU Support
- [[PRA-156](https://warthogs.atlassian.net/browse/PRA-156)] Add ARM support (experimental) - the feature will only be available on candidate risks
- [[PRA-158](https://warthogs.atlassian.net/browse/PRA-158)] Components upgrade:
  - Spark version: 3.4.4-ubuntu7 and 3.5.7-ubuntu2
  - Kyuubi version: 1.10.3-ubuntu1 
  - spark8t python library: 1.3.1
  - spark-rapids: 25.12.0
- [[PRA-73](https://warthogs.atlassian.net/browse/PRA-73)] Update juju version to 3.6.14+
- [[PRA-145](https://warthogs.atlassian.net/browse/PRA-145)] Validation on multiple K8s supported versions (refer to the requirements documentation for more info)
- [[DPE-8681](https://warthogs.atlassian.net/browse/DPE-8681)] Testing and validation for MicroCeph instead of MinIO
- Migrated from DPE to PRA Jira project
- General updates of Python dependencies, craft build tools, CI workflows and Github actions

### Kyuubi

- [[PRA-158](https://warthogs.atlassian.net/browse/PRA-158)] Kyuubi version update to 1.10.3-ubuntu1
- [[DPE-8542](https://warthogs.atlassian.net/browse/DPE-8542),[DPE-8549](https://warthogs.atlassian.net/browse/DPE-8549)] Rework health check (#150) (#151)
- [[DPE-8342](https://warthogs.atlassian.net/browse/DPE-8342)] Rework metrics alerts (#142) (#146)
- [[DPE-8288](https://warthogs.atlassian.net/browse/DPE-8288)] Implement new dashboard from upstream (#144) (#145)
- [[DPE-8376](https://warthogs.atlassian.net/browse/PRA-8376)] Charm consolidation (#147)

### Spark History Server

- [[PRA-200](https://warthogs.atlassian.net/browse/PRA-200)] Explicit proxy support for S3-compliant storage (#143)
- [[DPE-8481](https://warthogs.atlassian.net/browse/DPE-8481)] Add integration with oauth2proxy (#123)
- Enforce type checking (#146)

### Spark Integration Hub

- [[PRA-158](https://warthogs.atlassian.net/browse/PRA-158)] Update OCI resource to latest release (#181)
- [[PRA-200](https://warthogs.atlassian.net/browse/PRA-200)] Explicit proxy support for S3-compliant storage (#171)
- [[PRA-156](https://warthogs.atlassian.net/browse/PRA-156)] Fix broken release check due to multiple platforms (#158)
- [[PRA-152](https://warthogs.atlassian.net/browse/PRA-152)] Serialize asterisk characters when generating resource manifest (#144)
- [[PRA-113](https://warthogs.atlassian.net/browse/PRA-113)] Add a config option to specify custom Spark image (#134)
- [[PRA-30](https://warthogs.atlassian.net/browse/PRA-30)] Add monitored-service-accounts configuration option (#120)
- [[DPE-7840](https://warthogs.atlassian.net/browse/DPE-7840)] Share manifest of the K8s resources over the spark service account relation (#99)

### Spark Client Snap

- [[DPE-7923](https://warthogs.atlassian.net/browse/DPE-7923)] Supress AWS Java SDK v1 warning message in snap (#131)

### Charmed Spark OCI Images

- [[PRA-158](https://warthogs.atlassian.net/browse/PRA-158)] Component bumps (#217)
- [[DPE-7941](https://warthogs.atlassian.net/browse/DPE-7941)] Add gpu executor pod template to Kyuubi image (#165)
- Download Hive from mirror (#163)
- Perform disk cleanup at the start of all workflows (#190)
- Run trivy scan on 3.5/edge and 3.4/edge (#151) (#171)

### Charmed Spark Terraform Module

- [[DPE-7943](https://warthogs.atlassian.net/browse/DPE-7943)] Improve stability of UAT and CI tests (#142)
- [[DPE-7722](https://warthogs.atlassian.net/browse/DPE-7722)] Enable Reference Architecture (AKS) testing (#136) (#173)
- [[DPE-6777](https://warthogs.atlassian.net/browse/DPE-6777] Demo update based on Kyuubi GA (#131)
- [MISC] Pin cos-configuration-k8s to rev65 on YAML bundle (#156)

## Bug fixes

### Spark History Server

- [[PRA-140](https://warthogs.atlassian.net/browse/PRA-140)] Block charm in case of missing object storage path (#145)

### Charmed Spark OCI Images

- [[PRA-134](https://warthogs.atlassian.net/browse/PRA-134)] Add py4j dependency to PYTHONPATH in rock image (#180)
- [[PRA-136](https://warthogs.atlassian.net/browse/PRA-136)] Release tag not found (#182) (#185) (#186)

### Charmed Spark Terraform Module

- [[PRA-163](https://warthogs.atlassian.net/browse/PRA-163)] Remove wrong quote (#191)
- [[DPE-8292](https://warthogs.atlassian.net/browse/DPE-8292)] Add missing offers in Spark 3.5 (#144)
- fix: Pin tf provider to <1.0.0 (#167)

## Breaking changes

### Spark Integration Hub

- [[PRA-73](https://warthogs.atlassian.net/browse/PRA-73)] Restore Juju 3.6.14+ compatibility (#172)

```{note}
Juju controller versions from `3.9.10` to `3.6.13` are affected by a [regression in Juju](https://github.com/juju/juju/issues/21312) that has been fixed in `3.6.14` that will not claim management over resources when tag appropriately.
Support for Juju `3.6.14+` has been addressed by [this issue](https://github.com/canonical/spark-integration-hub-k8s-operator/issues/119) to now forcefully label 
resources managed by integration hub with `app.kubernetes.io/managed-by=spark8t`.

When using Juju controller versions greater or equal to `3.6.14`, make sure you use a charm revision above `107` for `spark-integration-hub-k8s`. On Juju controller versions lower or equal to `3.6.9`, use charm revisions below `107`.
```

## Documentation improvements

- Polish the terminology capitalisation (#188)
- Add autogenerated metadata description (#186)
- Fix the docs badge in README (#187)
- Home page remodeling (#181)
- Update home page (#163)
- Clarify how to use self-signed S3 endpoints (#164)
- Add landing pages (#159)
- Add cookie consent request (#157)
- Update the cookie banner design (#193)
- Update spelling to US English (#196)
- Add redirects for RTD docs (#160)
- Update documentation on Security page to reflect new UX (#158)
- Initial documentation migration to RTD (#148)
- Add Kyuubi docs (#134)

## Security (TO BE COMPLETED)

The new artifacts have been fixing the following CVEs:

| Severity | Fixed CVEs                                                                                                                                                                                                                                                                                                |
| :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Critical |                                                                                                                                                                                                                                               |
| High     |  |
| Medium   |                                      |
| Low      |      |

## Compatibility

|          Component          | Hardware architecture |    Channel    |                                                                                                          Artefact                                                                                                           | Revision | Minimum Juju version | Recommended Juju version |
| :-------------------------: | :-------------------: |:-------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:--------:|:--------------------:|:------------------------:|
| Apache Spark History Server |         AMD64         |  3/stable     |                                               [Charmed Apache Spark Image]() (Spark version: [3.5.7-ubuntu2](https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2))                                                |    94    |      v.3.6.14+       |         v.3.6.14         |
| Apache Spark History Server |         ARM64         |  3/candidate  |                                               [Charmed Apache Spark Image]() (Spark version: [3.5.7-ubuntu2](https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2))                                                |    93    |      v.3.6.14+       |         v.3.6.14         |
|    Spark Integration Hub    |         AMD64         |   3/stable    |                                                                                               [Integration Hub Image (11)]()                                                                                                |   113    |      v.3.6.14+       |         v.3.6.14         |
|    Spark Integration Hub    |         ARM64         |  3/candidate  |                                                                                               [Integration Hub Image (11)]()                                                                                                |   114    |      v.3.6.14+       |         v.3.6.14         |
|        Apache Kyuubi        |         AMD64         |  3.4/stable   | [Charmed Apache Kyuubi Image]() (Spark version: [3.4.4-ubuntu7](https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7), Kyuubi version: [1.10.3-ubuntu1](https://launchpad.net/kyuubi-releases/1.x/1.10.3-ubuntu1)) |   140    |      v.3.6.14+       |         v.3.6.14         |
|        Apache Kyuubi        |         ARM64         | 3.4/candidate | [Charmed Apache Kyuubi Image]() (Spark version: [3.4.4-ubuntu7](https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7), Kyuubi version: [1.10.3-ubuntu1](https://launchpad.net/kyuubi-releases/1.x/1.10.3-ubuntu1)) |   141    |      v.3.6.14+       |         v.3.6.14         |
|        Apache Kyuubi        |         AMD64         |  3.5/stable   | [Charmed Apache Kyuubi Image]() (Spark version: [3.5.7-ubuntu2](https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2), Kyuubi version: [1.10.3-ubuntu1](https://launchpad.net/kyuubi-releases/1.x/1.10.3-ubuntu1)) |   142    |      v.3.6.14+       |         v.3.6.14         |
|        Apache Kyuubi        |         ARM64         | 3.5/candidate | [Charmed Apache Kyuubi Image]() (Spark version: [3.5.7-ubuntu2](https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2), Kyuubi version: [1.10.3-ubuntu1](https://launchpad.net/kyuubi-releases/1.x/1.10.3-ubuntu1)) |   143    |      v.3.6.14+       |         v.3.6.14         |
|      Spark Client Snap      |         AMD64         |  3.4/stable   |                                                                Spark version: [3.4.4-ubuntu7](https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7)                                                                |   100    |         N/A          |           N/A            |
|      Spark Client Snap      |         ARM64         | 3.4/candidate |                                                                Spark version: [3.4.4-ubuntu7](https://launchpad.net/spark-releases/+milestone/3.4.4-ubuntu7)                                                                |   102    |         N/A          |           N/A            |
|      Spark Client Snap      |         AMD64         |  3.5/stable   |                                                                Spark version: [3.5.7-ubuntu2](https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2)                                                                |   101    |         N/A          |           N/A            |
|      Spark Client Snap      |         ARM64         | 3.5/candidate |                                                                Spark version: [3.5.7-ubuntu2](https://launchpad.net/spark-releases/+milestone/3.5.7-ubuntu2)                                                                |    99    |         N/A          |           N/A            |