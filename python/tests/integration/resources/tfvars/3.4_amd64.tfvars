history_server_revision  = 115   # 3/edge   TODO: use stable
integration_hub_revision = 132   # 3/edge   TODO: use stable
kyuubi_revision          = 177   # 3.4/edge TODO: use stable  
kyuubi_users_revision    = 774   # 14/stable
metastore_revision       = 774   # 14/stable
zookeeper_revision       = 78    # 3/stable
data_integrator_revision = 362   # latest/stable, 24.04
s3_revision              = 544   # 2/stable
ssc_revision             = 586   # 1/stable, 24.04
azure_storage_revision   = 282   # 1/stable

history_server_image = "ghcr.io/canonical/charmed-spark@sha256:620d6b75486d96516a0c9fec99118e52dab5de32974d211da0bc7b1cea324516"
# spark-version: 3.4.4, release date 22/04/2026
integration_hub_image = "ghcr.io/canonical/spark-integration-hub@sha256:a0439da3e6a9433a0db9501c8ea7b28ba3652af9a9ec22fcc2ad1b0197d48134"
# rev13, release date 19/03/2026
kyuubi_image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:696474452413f036516ffe91070365b7d5b8ca9f6806dad04b127920f3943ced"
# rev23, spark-version: 3.4.4, kyuubi-version: 1.10.3, release date 22/04/2026

kyuubi_users_image = 184    # 14/stable, rev774
metastore_image    = 184    # 14/stable, rev774
zookeeper_image    = 34     # 3/stable, rev78
