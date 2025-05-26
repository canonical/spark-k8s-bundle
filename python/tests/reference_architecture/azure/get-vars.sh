#!/bin/bash

export TF_VAR_JUJU_CONTROLLER_IPS=$(cat ~/.local/share/juju/controllers.yaml | yq .controllers.micro.api-endpoints | sed 's/\[\(.*\)\]/\1/g' | sed "s/'//g")
export TF_VAR_JUJU_USERNAME=$(cat ~/.local/share/juju/accounts.yaml| yq .controllers.micro.user)
export TF_VAR_JUJU_PASSWORD=$(cat ~/.local/share/juju/accounts.yaml| yq .controllers.micro.password)
export TF_VAR_JUJU_CA_CERTIFICATE=$(cat ~/.local/share/juju/controllers.yaml | yq .controllers.micro.ca-cert | base64)
export TF_VAR_K8S_CLOUD="microk8s"
export TF_VAR_K8S_CREDENTIAL="microk8s"
