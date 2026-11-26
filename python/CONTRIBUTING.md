# Contributing

## Overview

This document explains the processes and practices for contributing to this repository. We welcome contributions of all sizes, from typo fixes to new features.

If you would like to discuss use cases or a proposed implementation, reach out on the [Analytics Canonical Matrix public channel](https://matrix.to/#/#charmhub-analytics:ubuntu.com) or [Discourse](https://discourse.charmhub.io/).

To build and develop the package in this repository, we recommend using [Poetry](https://python-poetry.org/). For installing Poetry on different platforms, see the [Poetry installation guide](https://python-poetry.org/docs/#installation).

## Before you open a pull request

To make your pull request (PR) easier to review:

- For new features, architectural changes, or major documentation updates, [open an issue](https://github.com/canonical/spark-k8s-bundle/issues) first. Explain your problem with examples and your desired use case, so we can agree on the approach before you or we spend time on its implementation and review.
- Keep your changes focused and consistent with the structure of the codebase. The PR should also add or update relevant documentation and tests or agreed with the maintainers that these changes will follow up on a dedicated work item.
- In your PR description, say what was wrong or missing, why you chose your approach, and how you verified the result (for example, test output or a local docs build).
- Whether you write code or documentation by hand or with AI or other tools, test your changes locally and make sure you can explain how they work during review. PRs raised by contributors not willing to critically understand and discuss changes done by agents will be closed.

All changes require review before being merged. Code review typically examines code quality, test coverage, and the user experience for interacting with the other components of the Charmed Apache Spark solution.

## Install from source

To install the package with poetry, checkout the repository

```bash
git clone https://github.com/canonical/spark-k8s-bundle.git
cd spark-k8s-bundle/
```

and run

```bash
poetry install
```

## Developing

When developing we advise you to use virtual environment to confine the installation of this package and its dependencies. Please refer to [venv](https://docs.python.org/3/library/venv.html), [pyenv](https://github.com/pyenv/pyenv) or [conda](https://docs.conda.io/en/latest/), for some tools that help you to create and manage virtual environments.
We also advise you to read how Poetry integrates with virtual environments [here](https://python-poetry.org/docs/managing-environments/).

The project uses [tox](https://tox.wiki/en/latest/) for running CI/CD pipelines.

You can create an environment for development with `tox`:

```shell
tox devenv -e unit
source venv/bin/activate
```

### Testing

Using tox you can also run several operations, such as

```shell
tox run -e format                 # update your code according to linting rules
tox run -e lint                   # code style
tox run -e unit                   # unit tests
tox run -e integration-<domain>   # <domain> integration tests
```

## Documentation

Product documentation is hosted on [Read the Docs](https://canonical-charmed-spark.readthedocs-hosted.com/).
To edit the documentation content, we recommend the following process:

1. Create a branch (either in the main repository or in a fork) from the current `track/<major>.<minor>` branch and modify documentation files as necessary.
2. Raise a PR against the previous `track/<major>.<minor>` branch to start the review process, and conduct the code review within the PR. A link to the preview build is accessible from the PR.
3. Once the PR is approved and all comments are addressed, the PR can be merged. The Read the Docs automation handles building the documentation website from the branch and publishing it.

### Terminology

Apache®, [Apache Spark, Spark™](https://spark.apache.org/) and their respective logos are either registered trademarks or trademarks of the [Apache Software Foundation](https://www.apache.org/) in the United States and/or other countries.

For documentation in this repository the following conventions are applied (see the table below).

| Full form                          | Alternatives                | Incorrect examples            |
| ---------------------------------- | --------------------------- | ----------------------------- |
| Apache Spark                       |                             | Spark                         |
| Charmed Apache Spark               |                             | Charmed Spark                 |
| Spark History Server               | Apache Spark History Server |                               |
| Spark jobs                         |                             | Spark Jobs                    |
| Spark Driver                       |                             |                               |
| Spark Executor                     |                             |                               |
| Spark Context                      |                             |                               |
| Integration Hub for Apache Spark   | Integration Hub             | Spark Integration Hub         |
| Client tools snap for Apache Spark |                             | Spark client snap, tools snap |

The full form must be used at least once per page.
The full form must be used at the first entry to the page’s headings, body of text, callouts, and graphics.
For subsequent usage, the full form can be substituted by alternatives.

### Kubernetes Terminology

When documenting Kubernetes concepts, follow the [Kubernetes Documentation Style Guide](https://kubernetes.io/docs/contribute/style/style-guide/#use-upper-camel-case-for-api-objects) for API object capitalization:

- **Use UpperCamelCase** (PascalCase) when referring specifically to Kubernetes API objects: Pod, Service, Namespace, ConfigMap, Secret, Ingress, Deployment, Node, etc.
- **Use lowercase** when generally discussing the concept or referring to instances in prose.

For example, "The Pod object contains a `hostPath` field" (API reference) vs "the pod is running on node-1" (general discussion).

Special cases:

- **kubeconfig**: Use lowercase when referring to the configuration file (e.g., "update the kubeconfig file").
- **KUBECONFIG**: Use uppercase when referring to the environment variable.
- **Product names**: Capitalize properly (e.g., "Azure Kubernetes Service", "Amazon Elastic Kubernetes Service").

## Canonical Contributor Agreement

Canonical welcomes contributions to Charmed Apache Spark. Please check out our [contributor agreement](https://ubuntu.com/legal/contributors) if you're interested in contributing to the solution.
