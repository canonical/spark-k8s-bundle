## Manage Charmed Apache Spark Service Accounts

This is an introduction to the CLI interface for creating, managing and configuring Charmed Apache Spark service accounts. 

[note]
Charmed Apache Spark service accounts are designed to work seamlessly with the Integration Hub for Apache Spark charm, allowing you to manage Apache Spark configuration using Juju relations. For more information about how to use the configuration hub see the [How to guide](/t/charmed-spark-k8s-documentation-how-to-use-spark-integration-hub/14296).
[/note]

[note type="caution"]
The following commands assume that you have administrative permission on the namespaces (or on the Kubernetes cluster) so that the corresponding resources (such as service accounts, secrets, roles, and role bindings) can be created and deleted. 
[/note]

### Create Service Account

In case using another namespace than `default`, make sure that it already exists in Kubernetes:

```bash
$ kubectl create namespace demonamespace
namespace/demonamespace created
```

Now we can define a service account within the scope of this namespace. In case we have a configuration file with default settings for the account, we can also include those when defining the account. The syntax of the config file is identical to [Apache Spark Configuration Properties](https://spark.apache.org/docs/latest/configuration.html#available-properties). For example:

```bash
$ echo "spark.kubernetes.deploy-mode=cluster" > /home/demouser/conf/spark-overrides.conf
```

The command below creates a service account associated with configuration properties provided either via property file or explicit 
configuration arguments.  The flags `--primary` specifies that the newly created account will be the primary account to 
be used. (If another primary exists, the latter account primary flag will be set to `false`.)

```bash
spark-client.service-account-registry create --username demouser --namespace demonamespace  --primary --properties-file /home/demouser/conf/spark-overrides.conf  --conf spark.app.name=demo-spark-app-overrides
```

### List all service accounts

To display a list of the service accounts available, and whether they are primary or service accounts:

```bash
spark-client.service-account-registry list
```

### Add more entries to Service Account Configuration

To upsert into the existing configuration associated with the account:

```bash
spark-client.service-account-registry add-config --username demouser --namespace demonamespace  --properties-file /home/demouser/conf/spark-overrides.conf  --conf spark.app.name=demo-spark-app-overrides
```

### Remove entries from Service Account Configuration

To remove the specified keys from the existing configuration associated with the account:

```bash
spark-client.service-account-registry remove-config --username demouser --namespace demonamespace  --conf conf.key1.to.remove --conf conf.key2.to.remove
```

### Print configuration for a given Service Account 

To print the configuration for a given service account:

```bash
spark-client.service-account-registry get-config --username demouser --namespace demonamespace 
```

### Delete Service Account Configuration

To delete the configurations associated with a given service account:

```bash
spark-client.service-account-registry clear-config --username demouser --namespace demonamespace 
```

### Inspect Primary Service Account

To find out which is the primary account, together with related configuration settings:

```bash
spark-client.service-account-registry get-primary
```

### Cleanup a Service Account

To delete the service account together with the other resources created, e.g. secrets, role, role-bindings, etc.:

```bash
spark-client.service-account-registry delete --username demouser --namespace demonamespace 
```