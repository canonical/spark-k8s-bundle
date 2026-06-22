history_server_revision  = 113 # 4.0/candidate TODO: Use stable revision
integration_hub_revision = 132 # 3/candidate   TODO: Use stable revision
kyuubi_revision          = 171 # 4.0/candidate TODO: Use stable revision
kyuubi_users_revision    = 774 # 14/stable
metastore_revision       = 774 # 14/stable
zookeeper_revision       = 78  # 3/stable
data_integrator_revision = 362 # latest/stable, 24.04
s3_revision              = 544 # 2/stable
ssc_revision             = 586 # 1/stable, 24.04
azure_storage_revision   = 282 # 1/stable

history_server_image = "ghcr.io/canonical/charmed-spark@sha256:66100e9c9831e37e644efb0e98346c6495d0a775846366a8dcca0b1c68d5e6ed"
# spark-version: 4.0.2, release date 08/06/2026
integration_hub_image = "ghcr.io/canonical/spark-integration-hub@sha256:a0439da3e6a9433a0db9501c8ea7b28ba3652af9a9ec22fcc2ad1b0197d48134"
# rev13, release date 19/03/2026
kyuubi_image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:6641d8a6b54d793c8dd8dc0ff80b13d992980b35eb9d08b78f3c963cfd2fc844"
# spark-version: 4.0.2, kyuubi-version: 1.11.0, release date 08/06/2026

kyuubi_users_image = 184 # 14/stable, rev774
metastore_image    = 184 # 14/stable, rev774
zookeeper_image    = 34  # 3/stable, rev78
