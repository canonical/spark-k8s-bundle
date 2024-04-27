output "charms" {
  value = merge(
      module.base.charms, module.cos[*].charms...
  )
}

