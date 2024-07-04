#!/bin/bash
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

errcho(){ >&2 echo $@; }

wait_for_pod() {
    # Wait for the given pod in the given namespace to be ready.
    #
    # Arguments:
    # $1: Name of the pod
    # $2: Namespace that contains the pod

    pod_name=$1
    namespace=$2

    echo "Waiting for pod '$pod_name' to become ready..."
    kubectl wait --for condition=Ready pod/$pod_name -n $namespace --timeout 60s
}

setup_pod() {
  POD=$1
  NAMESPACE=$2
  MODE=$3

  if [ "${MODE}" == "admin" ]
  then
    KUBE_CONFIG_FILE=$4

    errcho "Creating admin test-pod"

    # Create a pod with admin service account
    yq ea ".spec.containers[0].env[0].name = \"KUBECONFIG\" | .spec.containers[0].env[0].value = \"/var/lib/spark/.kube/config\" | .metadata.name = \"${POD}\"" \
      ./resources/templates/testpod.yaml | \
      kubectl -n ${NAMESPACE} apply -f -
  else
    SERVICE_ACCOUNT=$4

    # Create the pod with the Spark service account
    yq ea ".spec.serviceAccountName = \"${SERVICE_ACCOUNT}\" | .metadata.name = \"${POD}\"" \
      ./resources/templates/testpod.yaml | \
      kubectl -n ${NAMESPACE} apply -f -
  fi

  OUTPUT=$(wait_for_pod $POD $NAMESPACE)

  if [ "${MODE}" == "admin" ] & [ -f "${KUBE_CONFIG_FILE}" ];
  then
    MY_KUBE_CONFIG=$(cat ${KUBE_CONFIG_FILE})
    kubectl -n $NAMESPACE exec $POD -- /bin/bash -c 'mkdir -p ~/.kube'
    kubectl -n $NAMESPACE exec $POD -- env KCONFIG="$MY_KUBE_CONFIG" /bin/bash -c 'echo "$KCONFIG" > ~/.kube/config'
  fi

  echo ${OUTPUT}:${NAMESPACE}
}

teardown_test_pod() {
  POD=$1
  NAMESPACE=$2

  kubectl -n $NAMESPACE delete pod $POD
}

case $1 in
  create)
    shift
    setup_pod $*
    ;;
  teardown)
    shift
    teardown_test_pod $*
    ;;
  *)
    echo "Mode not recognized"
    exit 1
    ;;
esac
