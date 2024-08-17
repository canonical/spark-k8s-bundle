## Manage Charmed Spark service accounts

This is an introduction to the CLI interface for creating, managing and configuring Charmed Spark service accounts.

> **Note**: Charmed Spark service accounts are designed to work seamlessly with the Spark Integration Hub charm, letting you manage Spark configuration using Juju relations. For more information about how to use configuration hub, see the [How to use the Spark Integration Hub charm](/t/charmed-spark-k8s-documentation-how-to-use-spark-integration-hub/14296) guide.

> :warning: The following commands assume that you have administrative permission on the namespaces (or on the Kubernetes cluster) so that the corresponding resources (such as service accounts, secrets, roles and role-bindings) can be created and deleted. 

### Create service account

In case of using another namespace, rather than `default`, make sure that it already exists in Kubernetes:

```bash
$ kubectl create namespace demonamespace
namespace/demonamespace created
```

Now we can define a service account within the scope of this namespace. In case we may have a configuration file with default settings for the account, we could also include those when defining the account. The syntax of the config file is identical to [Spark Configuration Properties](https://spark.apache.org/docs/latest/configuration.html#available-properties), for example:

```bash
$ echo "spark.kubernetes.deploy-mode=cluster" > /home/demouser/conf/spark-overrides.conf
```

The command below creates a service account associated with configuration properties provided either via property file or explicit 
configuration arguments. The flags `--primary` specifies that the newly created account will be the primary account to 
be used. If another primary exists, the latter account primary flag will be set to `false`.

```bash
spark-client.service-account-registry create --username demouser --namespace demonamespace  --primary --properties-file /home/demouser/conf/spark-overrides.conf  --conf spark.app.name=demo-spark-app-overrides
```

### List all service accounts

The command below displays a list of the service accounts available, and whether they are primary account or service accounts:

```bash
spark-client.service-account-registry list
```

### Add more entries to service account configuration

The command below will upsert into the existing configuration associated with the account:

```bash
spark-client.service-account-registry add-config --username demouser --namespace demonamespace  --properties-file /home/demouser/conf/spark-overrides.conf  --conf spark.app.name=demo-spark-app-overrides
```

### Remove entries from service account configuration

The command below will remove the specified keys from existing configuration associated with the account:

```bash
spark-client.service-account-registry remove-config --username demouser --namespace demonamespace  --conf conf.key1.to.remove --conf conf.key2.to.remove
```

### Print configuration for a given service account

This command will print the configuration for a given service account:

```bash
spark-client.service-account-registry get-config --username demouser --namespace demonamespace 
```

### Delete service account configuration

This command will delete the configurations associated to a given service account: 

```bash
spark-client.service-account-registry clear-config --username demouser --namespace demonamespace 
```

### Inspect primary service account

This command lets the user find out which is the primary account, together with related configuration settings:

```bash
spark-client.service-account-registry get-primary
```

### Cleanup a service account

This command will delete the service account together with the other resources created, e.g., secrets, role, role-bindings:

```bash
spark-client.service-account-registry delete --username demouser --namespace demonamespace 
```