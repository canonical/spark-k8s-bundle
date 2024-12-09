# Contributing

## Overview

This documents explains the processes and practices recommended for contributing enhancements to this repository.

- Generally, before developing enhancements to this component, you should consider [opening an issue](https://github.com/canonical/spark-k8s-bundle/issues) explaining your problem with examples, and your desired use case.
- If you would like to chat with us about your use-cases or proposed implementation, you can reach us at [Data Platform Canonical Matrix public channel](https://matrix.to/#/#charmhub-data-platform:ubuntu.com) or [Discourse](https://discourse.charmhub.io/).
- All enhancements require review before being merged. Code review typically examines
  - code quality
  - test coverage
  - user experience for interacting with the other components of the Charmed Apache Spark solution.
- Please help us out in ensuring easy to review branches by rebasing your pull request branch onto the `main` branch. This also avoids merge commits and creates a linear Git commit history.

To build and develop the package in this repository, we advise to use [Poetry](https://python-poetry.org/). For installing poetry on different platforms, please refer to [here](https://python-poetry.org/docs/#installation).

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

## Documentation

Product documentation is stored in [Discourse](https://discourse.charmhub.io/t/charmed-spark-k8s-documentation/8963) and published on Charmhub and the Canonical website via Discourse API. 
The documentation in this repository under the release folder (e.g. `releases/3.4/docs`) is a mirror synched by [Discourse Gatekeeper](https://github.com/canonical/discourse-gatekeeper), that takes care of automatically raising and updating a PR whenever changes to the content on Discourse are made.
Although Discourse content can be edited directly, unless the modifications are trivial and obvious (typos, spellings, formatting) we generally recommend to follow a review process:

1. Create a branch (either in the main repo or in a fork) from the current `main` and modify documentation files as necessary.
2. Raise a PR against the `main` to start the review process, and conduct the code review within the PR.
3. Once the PR is approved and all comments are addressed, the PR should NOT be merged directly! All the modifications should be applied to Discourse manually. If needed, new Discourse topics can be created, and referenced in the navigation table of the main index file on Discourse.
4. Discourse Gatekeeper will raise a new PR or add new commits to an open Discourse PR, tracking the `discourse-gatekeeper/migrate` branch. The [sync_docs.yaml](https://github.com/canonical/spark-k8s-bundle/blob/main/.github/workflows/sync_docs.yaml) GitHub Actions provides further details on the Gatekeeper integration that can be run (a) in a scheduled fashion every night; (b) as a part of pull request CI, and (c) can be triggered manually. If new topics are referenced in the main index file on Discourse, these will be added to `docs/index.md` and the new topics pulled from Discourse.
5. Once Gatekeeper has raised a new or updated an existing PR, feel free to close the initial PR manually created in step 2, with a comment referring to the PR created by Gatekeeper. If the initial PR was referring to a ticket, add the ticket to either the title or the description of the GateKeeper PR.


## Canonical Contributor Agreement

Canonical welcomes contributions to the Charmed Kafka Operator. Please check out our [contributor agreement](https://ubuntu.com/legal/contributors) if you're interested in contributing to the solution.