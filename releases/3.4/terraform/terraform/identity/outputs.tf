output "ingress_offer" {
  description = "The url of the ingress offer."
  value       = juju_offer.traefik_ingress.url
}