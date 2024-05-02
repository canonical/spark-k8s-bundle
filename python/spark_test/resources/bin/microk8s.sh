#!/bin/bash
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

setup_microk8s() {
  sudo snap install microk8s --channel=1.28/stable --classic
  sudo snap alias microk8s.kubectl kubectl
  sudo usermod -a -G microk8s ${USER}
  mkdir -p ~/.kube
  sudo chown -f -R ${USER} ~/.kube
}

configure_microk8s() {
  ADDONS=$*

  KUBECONFIG=~/.kube/config

  microk8s status --wait-ready
  microk8s config | tee $KUBECONFIG

  for PLUGIN in $ADDONS
  do
    microk8s.enable $PLUGIN
  done
}

teardown_microk8s(){
  sudo snap remove microk8s --purge
}

case $1 in
  setup)
    shift
    setup_microk8s $*
    ;;
  configure)
    shift
    configure_microk8s $*
    ;;
  teardown)
    shift
    teardown_microk8s $*
    ;;
  *)
    echo "Mode not recognized"
    exit 1
    ;;
esac
