# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  revisions = {
    history_server  = 94
    integration_hub = 113
    kyuubi          = 140
  }
  images = {
    history_server = "ghcr.io/canonical/charmed-spark@sha256:c7eef66beaeff463fdb7b707c630c0574912df8b843d8e3169f358adee2ae706"
    # rev23, spark-version: 3.5.7, release date 2026-02-27
    integration_hub = "ghcr.io/canonical/spark-integration-hub@sha256:c04d2d95874612883f6ead105d5f1dd74230370b23a08ea81175df81ba2e06fa"
    # rev11, release date 2026-03-02
    kyuubi = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:761a50ca0597825e5962c071a6575e7275e7eb04cae958d578bd7cc7f54fbb3e"
    # rev16, spark-3.4.4, kyuubi 1.10.3 release date 2026-02-27
  }
}
