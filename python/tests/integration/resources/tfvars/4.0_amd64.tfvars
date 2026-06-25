history_server_revision  = 119 # 4/edge        TODO: Use stable revision
integration_hub_revision = 132 # 3/edge        TODO: Use stable revision
kyuubi_revision          = 181 # 4.0/edge TODO: Use stable revision
kyuubi_users_revision    = 774 # 14/stable
metastore_revision       = 774 # 14/stable
zookeeper_revision       = 78  # 3/stable
data_integrator_revision = 362 # latest/stable, 24.04
s3_revision              = 544 # 2/stable
ssc_revision             = 586 # 1/stable, 24.04
azure_storage_revision   = 282 # 1/stable

history_server_image = "ghcr.io/canonical/charmed-spark@sha256:0505173879d2ed4ab103d860364aa759f13d7a29de33c89de02d47d431c54125"
# rev30, spark-version: 4.0.2, release date 08/06/2026
integration_hub_image = "ghcr.io/canonical/spark-integration-hub@sha256:a0439da3e6a9433a0db9501c8ea7b28ba3652af9a9ec22fcc2ad1b0197d48134"
# rev13, release date 19/03/2026
kyuubi_image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:533273d788cb9726586b5cf5297ee670b018e40e137bcf8f34f661b6fe74544a"
# rev25, spark-version: 4.0.2, kyuubi-version: 1.11.0, release date 08/06/2026

kyuubi_users_image = 184 # 14/stable, rev774
metastore_image    = 184 # 14/stable, rev774
zookeeper_image    = 34  # 3/stable, rev78
