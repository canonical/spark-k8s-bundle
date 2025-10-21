(how-to-self-signed-certificates)=

# Support self-signed certificates in Charmed Apache Spark

In some use cases, there is the need to use self-signed certificates to trust self-hosted services such as Ceph or many others.

## Spark-client snap

The Spark-client snap offers the possibility to submit jobs to a Kubernetes cluster with the `spark-submit` command.
For this reason, we have a feature in the Apache Spark Client snap to add certificates in the Java truststore inside the snap to validate the desired service.

To add a new certificate you can use the following command:

```bash
spark-client.import-certificate <CERTIFICATE_ALIAS> <CERTIFICATE_PATH>
```

where `<CERTIFICATE_ALIAS>` is the alias associated to the certificate and the `<CERTIFICATE_PATH>` is the path of the desired certificate. Please be sure that the path of the certificate is accessible by the Apache Spark Client snap.

For more information, see the blog post on [how to deploy Charmed Apache Spark, with MAAS, Kubernetes and Ceph with self-signed certificates](https://ubuntu.com/blog/deploy-an-on-premise-data-hub-with-canonical-maas-spark-kubernetes-and-ceph).

## Apache Spark applications

Apache Spark applications can interact with a TLS enabled object storage with a self-signed certificates using the following procedure.\
First, create a truststore from the certificate file:

```bash
keytool -import -alias ceph-cert -file <CERTIFICATE_PATH> -storetype JKS -keystore <STORE_PATH> -storepass <PASSWORD> -noprompt
```

```bash
kubectl create secret generic <STORE_SECRET> --from-file <STORE_PATH>
```

The application can be instructed to use the truststore we just created.
This can be done on a per-application basic by passing additional properties to the `spark-submit` command, or on a service account-wide setting as follows:

```bash
spark-client.service-account-registry add-config --username <USERNAME> \
  --conf spark.executor.extraJavaOptions="-Djavax.net.ssl.trustStore=/<STORE_SECRET>/<STORE_PATH> -Djavax.net.ssl.trustStorePassword=<PASSWORD>" \
  --conf spark.driver.extraJavaOptions="-Djavax.net.ssl.trustStore=/<STORE_SECRET>/<STORE_PATH> -Djavax.net.ssl.trustStorePassword=<PASSWORD>" \
  --conf spark.kubernetes.executor.secrets.<STORE_SECRET>=/<STORE_SECRET> \
  --conf spark.kubernetes.driver.secrets.<STORE_SECRET>=/<STORE_SECRET> \
  --conf spark.hadoop.fs.s3a.connection.ssl.enabled=true
```
