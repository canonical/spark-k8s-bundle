# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = merge(
    concat(
      module.spark[*].charms, module.s3[*].charms
    )...
  )
}

output "offers" {
  description = "The name and url of the various offers being exposed"
  value = merge(
    concat(
      module.spark[*].offers
    )...
  )
}

