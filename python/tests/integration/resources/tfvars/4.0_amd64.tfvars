history_server_revision  = 101 #TODO: Use stable revision
integration_hub_revision = 132 #TODO: Use stable revision
kyuubi_revision          = 164 #TODO: Use stable revision
kyuubi_users_revision    = 774
metastore_revision       = 774
zookeeper_revision       = 78
data_integrator_revision = 362
s3_revision              = 544
ssc_revision             = 586
azure_storage_revision   = 282

history_server_image = "ghcr.io/canonical/charmed-spark@sha256:9f303b788561876eb4b30c293b69b3594b11ede1e7211dbce5345ce68b45ffbe"
# spark-version: 4.0.1, release date 08/04/2026
integration_hub_image = "ghcr.io/canonical/spark-integration-hub@sha256:a0439da3e6a9433a0db9501c8ea7b28ba3652af9a9ec22fcc2ad1b0197d48134"
# rev13, release date 19/03/2026
kyuubi_image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:28e739963fcb86a357d796478b515ba5835ab78313f2c75a747754f9d116a458"
# spark-version: 4.0.1, kyuubi-version: 1.11.0, release date 22/04/2026
kyuubi_users_image = 184
metastore_image    = 184
zookeeper_image    = 34

spark_risk         = "edge" #TODO: Use stable risk
