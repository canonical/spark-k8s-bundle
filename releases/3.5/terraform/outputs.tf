# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  value = merge(concat(
      module.s3[*].charms, module.azure[*].charms, module.cos[*].charms
  )...)
}

