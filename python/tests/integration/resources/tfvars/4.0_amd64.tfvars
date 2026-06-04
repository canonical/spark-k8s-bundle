history_server_revision  = 109 #TODO: Use stable revision
integration_hub_revision = 132 #TODO: Use stable revision
kyuubi_revision          = 164 #TODO: Use stable revision
kyuubi_users_revision    = 774
metastore_revision       = 774
zookeeper_revision       = 78
data_integrator_revision = 362
s3_revision              = 544
ssc_revision             = 586
azure_storage_revision   = 282

history_server_image = "ghcr.io/canonical/charmed-spark@sha256:76d543d17f5e89de3a4aea0d149a0c9bfc1ccbe9b7000280fbd49fc836ff3e4c"
# spark-version: 4.0.2, release date 04/06/2026
integration_hub_image = "ghcr.io/canonical/spark-integration-hub@sha256:a0439da3e6a9433a0db9501c8ea7b28ba3652af9a9ec22fcc2ad1b0197d48134"
# rev13, release date 19/03/2026
kyuubi_image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:9b11d41b96ba4f6408a4ece1454db439ec0e0ce20cfa92223e6ef7162440dcf7"
# spark-version: 4.0.2, kyuubi-version: 1.11.0, release date 04/06/2026
kyuubi_users_image = 184
metastore_image    = 184
zookeeper_image    = 34
