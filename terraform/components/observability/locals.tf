# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  revisions = {
    # TODO: bump the revision to 1/stable when both of the following issue gets fixed:
    # https://github.com/canonical/cos-configuration-k8s-operator/issues/128 
    # https://github.com/canonical/cos-configuration-k8s-operator/issues/84
    cos_configuration = 65
    grafana_agent     = 164
    pushgateway       = 30
    scrape_config     = 69
  }
  images = {
    grafana_agent = "46"
    pushgateway   = "11"
  }
}
