## Configuration Setup and Runtime behavior for Apache Spark client

Apache Spark comes with wide range of [configuration properties](https://spark.apache.org/docs/3.3.1/configuration.html#available-properties).

Passing each and every configuration in command line is cumbersome, so Apache Spark supports the use of properties configuration files allowing the user to reuse settings across submissions. 

In addition, the user can still add or override configuration values on the command line.

`spark-client` tools provide the same rich set of options to specify configuration properties and also override them similarly to Apache Spark.

Following is the hierarchy of configurations merged during `spark-client` commands:

* **_Snap Configuration_**: Immutable defaults provided in the Snap
* **_Service Account Configuration_**: Set up time generated immutable defaults kept as a secret collection in Kubernetes. Valid across sessions and machines. Please refer to the [setup](https://discourse.charmhub.io/t/spark-client-snap-tutorial-setup-environment/8952) section, specifically the part about ```service-account```. 
* **_Environment Configuration_**: Properties in file specified via environment variable (```$SPARK_CLIENT_ENV_CONF```) valid across spark-submit commands in a shell session.
* **CLI Properties File**: Properties file specified as a parameter (```--properties-file```) 
* **CLI Configuration**: Properties specified as parameters (list of ```--conf```) 

The final configuration is resolved by merging the above, overriding the latter sources on top of previous ones in case of multi-level definitions. 

***

* Previous: [Requirements](/t/spark-client-snap-reference-requirements/8962)                               
* [Charmed Spark Documentation](https://discourse.charmhub.io/t/charmed-spark-documentation/8963)