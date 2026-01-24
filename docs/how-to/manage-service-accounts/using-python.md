---
myst:
  html_meta:
    description: "Learn how to manage Charmed Apache Spark service accounts programmatically using the spark8t Python toolkit and API."
---

(how-to-service-accounts-python)=
# Manage Service Accounts using the Python API

The `spark-client` snap relies on the [`spark8t` toolkit](https://github.com/canonical/spark-k8s-toolkit-py). `spark8t` provides both a CLI and a programmatic interface to enhanced Apache Spark client functionalities. 

Here we describe how to use the `spark8t` toolkit (as part of the `spark-client` snap) to manage service accounts using Python.

## Preparation

The `spark8t` package is already part of the snap. However, if the python package is used outside of the snap context, please make sure that environment settings (described on the [tool's README](https://github.com/canonical/spark-k8s-toolkit-py)) are correctly configured.

Furthermore, you need to make sure that `PYTHONPATH` contains the location where the `spark8t` libraries were installed within the snap (something like `/snap/spark-client/current/lib/python3.10/site-packages`)

## Bind to Kubernetes

The following snipped allows you to import relevant environment variables
into a confined object, among which there should an auto-inference of your 
`kubeconfig` file location. 

```python
import os
from spark8t.domain import Defaults
from spark8t.services import KubeInterface

# Defaults for spark-client
defaults = Defaults(dict(os.environ))  # General defaults

# Create a interface connection to k8s
kube_interface = KubeInterface(defaults.kube_config)
```

Note that if you want to override some of these settings, you can extend the `Default` class accordingly. 

Alternatively, you can also use auto-inference using the `kubectl` command via

```python
from spark8t.services import KubeInterface

kube_interface = KubeInterface.autodetect(kubectl_cmd="kubectl")
```

Once bound to the k8s cluster, you have some properties of the connection readily available, e.g. 

```python
kube_interface.namespace
kube_interface.api_server
```

You can also issue some `kubectl` commands, using the `exec` method

```python
service_accounts = kube_interface.exec("get sa -A")
service_accounts_namespace = kube_interface.exec(
    "get sa", namespace=kube_interface.namespace
)
```

## Manage Spark Service Accounts

All functionalities for managing Apache Spark service accounts are embedded within
the `K8sServiceAccountRegistry` that can be instantiated using the `kube_interface`
object we defined above


```python
from spark8t.services import K8sServiceAccountRegistry

registry = K8sServiceAccountRegistry(kube_interface)
```

Once this object is instantiated we can perform several operations, as outlined 
in the sections below

### Create new Apache Spark service accounts

New Apache Spark service accounts can be created by first creating a `ServiceAccount`
domain object, and optionally specifying extra-properties, e.g. 

```python
from spark8t.domain import PropertyFile, ServiceAccount

configurations = PropertyFile({"my-key": "my-value"})
service_account = ServiceAccount(
    name="my-spark",
    namespace="default",
    api_server=kube_interface.api_server,
    primary=False,
    extra_confs=configurations,
)
```

The account can then be created using the registry

```python
service_account_id = registry.create(service_account)
```

This returns an id, which is effectively the `{namespace}:{username}`, e.g. "default:my-spark".

### Listing spark service accounts

Once Apache Spark service accounts have been created, these can be listed via

```python
spark_service_accounts = registry.all()
```

or retrieved using their ids

```python
retrieved_account = registry.get(service_account_id)
```

### Delete service account

The registry can also be used to delete existing service accounts

```python
registry.delete(primary_account_id)
```

or using an already existing `ServiceAccount` object:

```python
registry.delete(service_account.id)
```

### Manage Primary Accounts

`spark8t` and spark-client snap have the notation of the so-called 'primary' service account, the 
one that would be chosen by default if no specific account is provided. The
primary Apache Spark service account can be set up using:

```python
registry.set_primary(service_account_id)
```

or using an already existing `ServiceAccount` object:

```python
registry.set_primary(service_account.id)
```

The primary Apache Spark service account can be retrieved using 

```python
primary_account = registry.get_primary()
```

### Manage configurations of Spark service accounts

Apache Spark service accounts can have a configuration that is provided (unless 
overridden) during each execution of Spark jobs. This configuration is stored in the `PropertyFile` object, which can be provided on the creation of a `ServiceAccount` object (`extra_confs` argument). 

The `PropertyFile` object can either be created from a dictionary, as 
done above

```python
from spark8t.domain import PropertyFile

static_property = PropertyFile({"my-key": "my-value"})
```

or also read from a file, e.g.:

```python
from spark8t.domain import PropertyFile

static_property = PropertyFile.read(defaults.static_conf_file)
```

`PropertyFile` objects can be merged using the `+` operator:

```python
merged_property = static_property + service_account.extra_confs
```

And `ServiceAccount` properties can be updated using new "merged" properties 
via the API provided by the registry:

```python
registry.set_configurations(service_account.id, merged_property)
```

Alternatively, you can also store these properties in files:

```python
with open("my-file", "w") as fid:
    merged_property.log().write(fid)
```

