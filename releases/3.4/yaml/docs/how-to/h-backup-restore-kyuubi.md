# How to to back up and restore data for Charmed Apache Kyuubi

The Charmed Apache Kyuubi stores data files and the metastore separately. The data files are stored in an object storage
(S3 compliant or Azure Storage) and the metadata is stored in a metastore inside an external PostgreSQL database. 
To back up an existing deployment of Charmed Apache Kyuubi and restore it into a different one, you need to have both the data files and the metadata.

## Back up and restore data

Since the data files are stored in an object storage outside of the Kubernetes cluster and Juju, for their backup and restore processes please follow the documentation specific from the relevant cloud providers (for example, [AWS Backups](https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html) and [Azure Backups](https://learn.microsoft.com/en-us/azure/backup/blob-backup-overview?tabs=operational-backup)).
When restoring a new Kyuubi deployment, just point the [s3-integrator](https://charmhub.io/s3-integrator) or [azure-storage-integrator](https://charmhub.io/azure-storage-integrator?channel=1/stable) to the existing bucket/container or to a new one with the restored content.

In order to backup the metastore more steps are needed, and this requires a backup of the PostgreSQL database that stores that information. 

### Back up the metastore

First of all, we need to create a backup of the database that stores the metastore from the Apache Kyuubi deployment that you want to back up.

The PostgreSQL charm supports the creation of a backup to an S3 compliant object storage. Please refer to [PostgreSQL documentation](https://canonical-charmed-postgresql-k8s.readthedocs-hosted.com/14/how-to/back-up-and-restore/) to check the available options. 

After the selection of the object storage, the first step is the create an S3 bucket (by using one of the supported S3 providers that has TLS enabled).

Deploy a new instance of S3 Integrator that will be needed to share the credential with the metastore charm to store the backup.

```bash
juju deploy s3-integrator <metastore-backup> --channel 1/stable
```

Configure it with the bucket name, path and s3 endpoint: 

```bash
juju config <metastore-backup> \
  bucket=<S3_BUCKET> \
  endpoint=<S3_ENDPOINT> \
  path=<S3_PATH>
```

and configure the credentials:

In the `<metastore-backup>`, credentials are fed using an action:

```bash
juju run <metastore-backup>/leader sync-s3-credentials \
  access-key=$S3_ACCESS_KEY \
  secret-key=$S3_SECRET_KEY
```

Integrate the metastore charm with this new S3 Integrator configured with the backup credentials and storage information.

```bash
juju integrate <metastore-backup> <metastore>
```

The next step is to create a backup.

```bash
juju run <metastore>/leader create-backup
```

After the completion of the backup, check that the backup is listed.

```bash
juju run <metastore>/leader list-backup
```


Once the database backup is done, remove the metastore and the new S3 integrator relation.

```bash
juju remove-relation <metastore-backup> <metastore>
```

### Restore the metastore

Let's switch to the new cluster that you want to restore the data to.

```bash
juju switch <new-model>
```
In the destination cluster, deploy a new S3 Integrator in the same way you have done in the old deployment.
Configure it with the bucket name and credentials of the same bucket that holds the backup from the previous cluster.


In the new (destination) cluster, integrate the new S3 integrator (`<new-metastore-backup>`) with the new metastore (`<new-metastore>`).

```bash
juju integrate <new-metastore-backup> <new-metastore>
```

After the integration, the `<new-metastore>` charm will move in blocked state with the following message: "the s3 bucket contains backup from a different cluster".

Confirm that the backup is present in the S3 storage.

```bash
juju run <new-metastore>/leader list-backups
```

Restore the backup to the metastore in the new deployment.

```shell
juju run <new-metastore>/leader restore --backup-id <id>
```

Once the restore is complete, remove the relation between the metastore from the S3 integrator instance used to restore backup.

```bash
juju remove-relation <new-metastore-backup> <new-metastore>
```

Now the new deployment is completely restored with the information present in the original deployment.
