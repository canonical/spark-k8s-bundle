(explanation-configuration)=
# Configuration management

Apache Spark comes with a wide range of [configuration properties](https://spark.apache.org/docs/3.4.2/configuration.html#available-properties) that can be fed into Apache Spark using a single property file, e.g. `spark.properties`, or by passing configuration values on the command line, as an argument to `spark-submit`, `pyspark` and `spark-shell`.

Charmed Apache Spark improves on this capability by enabling a set of hierarchical layers of configurations, that are merged and overridden based on a precedence rule. 

Each layer may also be linked to a particular component of the Charmed Apache Spark solution. For more information about components, see the [components overview](/explanation/component-overview) page.

Using the different layers appropriately allow to organize and centralize configuration definition consistently for groups, single users, single environment and session.
The sections below summarize the hierarchical levels of configurations. The final configuration is resolved by merging the different layers, starting from top to bottom, overriding the latter sources on top of previous ones in case of multi-level definitions.

## Group configuration

Group configurations are centrally stored as secrets in K8s,
and managed by `spark-integration-hub-k8s` charm that takes care of managing
their lifecycle from creation, modification and deletion. Please refer to [this how-to guide](/)
for more information on the usage of the `spark-integration-hub-k8s` charm for
setting up group configurations. Theese are valid across users, machines and sessions.

## User configuration

User configurations are centrally stored as secrets in K8s, but they are
managed by the user using the `spark-client` snap and/or `spark8t` Python library.
For more information, please refer to
[here](/how-to/manage-service-accounts/using-spark-client-snap) for the `spark-client`
snap and [here](/how-to/manage-service-accounts/using-python) for the `spark8t`
Python library. They are valid across machines and sessions.

## Environment configuration

Environment configurations are stored in your local environment, and they can apply 
to multiple Apache Spark users launched/used from the same machine. They are valid 
across users and sessions. These configurations may be stored in:

* *static properties files* specified via environment variable `SPARK_CLIENT_ENV_CONF`
* `$SNAP_DATA/etc/spark8t/spark-defaults.conf`

The file specified by the environment variable takes the precedence. 

## Session configuration

Session configurations are provided as CLI arguments to the `spark-client` command, 
and they are only valid for the related command/session. CLI configurations may 
be provided by:

* *Single Property* specified using parameter(s) `--conf <key>=<value>` 
* *Properties Files* specified using parameter(s) `--properties-file` 

Single Property takes the precedence.
