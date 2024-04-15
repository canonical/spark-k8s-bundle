# Contributing

## Overview

This documents explains the processes and practices recommended for contributing enhancements to this repository.

- Generally, before developing enhancements to this component, you should consider [opening an issue](https://github.com/canonical/spark-k8s-bundle/issues) explaining your problem with examples, and your desired use case.
- If you would like to chat with us about your use-cases or proposed implementation, you can reach us at [Data Platform Canonical Matrix public channel](https://matrix.to/#/#charmhub-data-platform:ubuntu.com) or [Discourse](https://discourse.charmhub.io/).
- All enhancements require review before being merged. Code review typically examines
  - code quality
  - test coverage
  - user experience for interacting with the other components of the Charmed Spark solution.
- Please help us out in ensuring easy to review branches by rebasing your pull request branch onto the `main` branch. This also avoids merge commits and creates a linear Git commit history.

To build and develop the package in this repository, we advise to use [Poetry](https://python-poetry.org/). For installing poetry on different platforms, please refer to [here](https://python-poetry.org/docs/#installation).

## Install from source

To install the package with poetry, checkout the repository

```bash
git clone https://github.com/canonical/spark-k8s-toolkit-py.git
cd spark-k8s-toolkit-py/
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
tox devenv -e integration
source venv/bin/activate
```

### Testing

Using tox you can also run several operations, such as

```shell
tox run -e fmt           # update your code according to linting rules
tox run -e lint          # code style
tox run -e unit          # unit tests
tox run -e integration   # integration tests
tox run -e all-tests     # unit+integration tests
tox                      # runs 'lint' and 'unit' environments
```

## Canonical Contributor Agreement

Canonical welcomes contributions to the Charmed Kafka Operator. Please check out our [contributor agreement](https://ubuntu.com/legal/contributors) if you're interested in contributing to the solution.