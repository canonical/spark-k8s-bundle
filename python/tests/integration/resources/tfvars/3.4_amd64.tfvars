history_server_revision  = 122   # 3/beta        TODO: use stable
integration_hub_revision = 134   # 3/beta        TODO: use stable
kyuubi_revision          = 180   # 3.4/beta      TODO: use stable  
kyuubi_users_revision    = 927   # 16/stable
metastore_revision       = 927   # 16/stable
zookeeper_revision       = 78    # 3/stable
data_integrator_revision = 362   # latest/stable, 24.04
s3_revision              = 544   # 2/stable
ssc_revision             = 586   # 1/stable, 24.04
azure_storage_revision   = 282   # 1/stable

history_server_image = "ghcr.io/canonical/charmed-spark@sha256:7bcf100560677b9ee17b1ff4fe4e1a1cd9aed6db06f30ce5e94cc066b10fcd94"
# spark-version: 3.4.4, release date 24/06/2026
integration_hub_image = "ghcr.io/canonical/spark-integration-hub@sha256:a0439da3e6a9433a0db9501c8ea7b28ba3652af9a9ec22fcc2ad1b0197d48134"
# rev13, release date 19/03/2026
kyuubi_image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:31a176caacb57364e1da7b0a6544fb8eca28b188814c55bc2ca83f52996e22e8"
# rev24, spark-version: 3.4.4, kyuubi-version: 1.10.3, release date 24/06/2026

kyuubi_users_image = 200 # 16/stable, rev927
metastore_image    = 200 # 16/stable, rev927
zookeeper_image    = 34  # 3/stable, rev78
