## Support self-signed certificates in `spark-client` snap

The `spark-client` snap offers the possibility to submit jobs to a Kubernetes cluster with the `spark-submit` command. 

In some use cases, there is the need to use self-signed certificates to trust self-hosted services such as Ceph or many others. 
For this reason we had a feature in the spark-client snap to add certificates in the Java truststore inside the snap and so being able to validate the desired service.

### Add certificate

In order to add a new certificate you can use the following command:

```bash
spark-client.import-certificate <CERTIFICATE_ALIAS> <CERTIFICATE_PATH>
```

where <CERTIFICATE_ALIAS> is the alias associated to the certificate and the <CERTIFICATE_PATH> is the path of the desired certificate. Please be sure that the path of the certificate is accessible by the `spark-client` snap. 

Please have a look at this [blog post](https://ubuntu.com/blog/deploy-an-on-premise-data-hub-with-canonical-maas-spark-kubernetes-and-ceph) that show how to deploy Charmed Spark, with MAAS, Kubernetes and Ceph with self-signed certificates.