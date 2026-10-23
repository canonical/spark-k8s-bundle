history_server_revision  = 146 # 3/edge               TODO: use stable
integration_hub_revision = 164 # 3/edge               TODO: use stable
kyuubi_revision          = 252 # 3.5/edge/pr-387      TODO: use stable
kyuubi_users_revision    = 925 # 14/stable
metastore_revision       = 925 # 14/stable
zookeeper_revision       = 78  # 3/stable
data_integrator_revision = 362 # latest/stable, 24.04
s3_revision              = 544 # 2/stable
ssc_revision             = 586 # 1/stable, 24.04
azure_storage_revision   = 282 # 1/stable

history_server_image = "ghcr.io/canonical/charmed-spark@sha256:b8ffcf05fa16cd06f7c962a94a0c9998d23ad3f658ed2be8a24f1e4c042f2d7a"
# rev31, spark-version: 3.5.8, release date 24/06/2026
integration_hub_image = "ghcr.io/canonical/spark-integration-hub@sha256:0a13097c10bcb245801b3c0040b8a83123274a3351e7ae25f983dfefab233973"
# rev13, release date 19/03/2026
kyuubi_image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:421a56a1f1634282b27157161d9d0b4263854f61e8b4f1552cc9b40b58895d27"
# rev26, spark-version: 3.5.8, kyuubi-version: 1.10.3, release date 24/06/2026

kyuubi_users_image = 201 # 14/stable, rev925
metastore_image    = 201 # 14/stable, rev925
zookeeper_image    = 34  # 3/stable, rev78

istio_k8s_platform = "microk8s"
istio_k8s_revision = 45
