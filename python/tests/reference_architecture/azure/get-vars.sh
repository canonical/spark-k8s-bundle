#!/bin/bash

CURRENT_CONTROLLER=$(cat ~/.local/share/juju/controllers.yaml | yq .current-controller)

export TF_VAR_JUJU_CONTROLLER_IPS=$(cat ~/.local/share/juju/controllers.yaml | yq ".controllers.${CURRENT_CONTROLLER}.api-endpoints" | sed 's/\[\(.*\)\]/\1/g' | sed "s/'//g")
export TF_VAR_JUJU_USERNAME=$(cat ~/.local/share/juju/accounts.yaml| yq ".controllers.${CURRENT_CONTROLLER}.user")
export TF_VAR_JUJU_PASSWORD=$(cat ~/.local/share/juju/accounts.yaml| yq ".controllers.${CURRENT_CONTROLLER}.password")
export TF_VAR_JUJU_CA_CERTIFICATE=$(cat ~/.local/share/juju/controllers.yaml | yq ".controllers.${CURRENT_CONTROLLER}.ca-cert" | base64)
export TF_VAR_K8S_CLOUD=$(cat ~/.local/share/juju/controllers.yaml | yq ".controllers.${CURRENT_CONTROLLER}.cloud")
export TF_VAR_K8S_CREDENTIAL=$TF_VAR_K8S_CLOUD
