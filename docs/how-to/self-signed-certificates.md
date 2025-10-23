(how-to-self-signed-certificates)=

# Support self-signed certificates in Charmed Apache Spark

In some use cases, there is the need to use self-signed certificates to trust self-hosted services such as Ceph or many others.
For this reason, both the Spark-client snap and the Apache Spark applications need to add certificates in their respective truststore to validate the desired service.

## Import certificates in the Spark-client snap

To add a new certificate you can use the following command:

```bash
spark-client.import-certificate <CERTIFICATE_ALIAS> <CERTIFICATE_PATH>
```

where `<CERTIFICATE_ALIAS>` is the alias associated to the certificate and the `<CERTIFICATE_PATH>` is the path of the desired certificate. Please be sure that the path of the certificate is accessible by the Apache Spark Client snap.

For more information, see the blog post on [how to deploy Charmed Apache Spark, with MAAS, Kubernetes and Ceph with self-signed certificates](https://ubuntu.com/blog/deploy-an-on-premise-data-hub-with-canonical-maas-spark-kubernetes-and-ceph).

## Import certificates in Apache Spark applications

Apache Spark applications can interact with a TLS enabled object storage with a self-signed certificates using the following procedure.

First, create a truststore from the certificate file:

```bash
keytool -import -alias ceph-cert -file <CERTIFICATE_PATH> -storetype JKS -keystore <STORE_PATH> -storepass <PASSWORD> -noprompt
```

Then, create a new Kubernetes secret from this file:

```bash
kubectl create secret generic <STORE_SECRET> --from-file <STORE_PATH>
```

Configure the application to consume the secret and use the truststore we just created.
Apply the configuration on a per-application basic by specifying additional properties to the `spark-submit` command, or at the service account level as shown below:

```bash
spark-client.service-account-registry add-config --username <USERNAME> \
  --conf spark.executor.extraJavaOptions="-Djavax.net.ssl.trustStore=/<STORE_SECRET>/<STORE_PATH> -Djavax.net.ssl.trustStorePassword=<PASSWORD>" \
  --conf spark.driver.extraJavaOptions="-Djavax.net.ssl.trustStore=/<STORE_SECRET>/<STORE_PATH> -Djavax.net.ssl.trustStorePassword=<PASSWORD>" \
  --conf spark.kubernetes.executor.secrets.<STORE_SECRET>=/<STORE_SECRET> \
  --conf spark.kubernetes.driver.secrets.<STORE_SECRET>=/<STORE_SECRET> \
  --conf spark.hadoop.fs.s3a.connection.ssl.enabled=true
```
