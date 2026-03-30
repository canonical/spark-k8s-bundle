# Outputs for $(basename "$moduleDir").

output "application" {
  description = "Object representing the deployed application."
  value = {
    name = juju_application.certificates.name
  }
}

output "provides" {
  description = "Relation endpoints provided by the manual-tls charm."
  value = {
    certificates = juju_application.certificates.name
  }
}

