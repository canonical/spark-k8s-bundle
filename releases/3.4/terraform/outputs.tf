# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = merge(
    concat(
      module.spark[*].charms, module.azure_storage[*].charms, module.s3[*].charms, module.bundled_cos[*].charms, module.observability[*].charms
    )...
  )
}

