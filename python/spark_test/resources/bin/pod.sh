#!/bin/bash
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

errcho(){ >&2 echo $@; }

wait_for_pod() {

  POD=$1
  NAMESPACE=$2

  SLEEP_TIME=10
  for i in {1..5}
  do
    pod_status=$(kubectl -n ${NAMESPACE} get pod ${POD} | awk '{ print $3 }' | tail -n 1)
    errcho $pod_status
    if [[ "${pod_status}" == "Running" ]]
    then
        errcho "testpod is Running now!"
        break
    elif [[ "${i}" -le "5" ]]
    then
        errcho "Waiting for the pod to come online..."
        sleep $SLEEP_TIME
    else
        errcho "testpod did not come up. Test Failed!"
        exit 3
    fi
    SLEEP_TIME=$(expr $SLEEP_TIME \* 2);
  done

  echo ${POD}
}

setup_pod() {
  POD=$1
  NAMESPACE=$2
  MODE=$3

  IMAGE_NAME=$4

  if [ "${MODE}" == "admin" ]
  then
    KUBE_CONFIG_FILE=$5

    errcho "Creating admin test-pod"

    # Create a pod with admin service account
    yq ea ".spec.containers[0].image = \"${IMAGE_NAME}\" | .spec.containers[0].env[0].name = \"KUBECONFIG\" | .spec.containers[0].env[0].value = \"/var/lib/spark/.kube/config\" | .metadata.name = \"${POD}\"" \
      ./resources/templates/testpod.yaml | \
      kubectl -n ${NAMESPACE} apply -f -
  else
    SERVICE_ACCOUNT=$5

    # Create the pod with the Spark service account
    yq ea ".spec.containers[0].image = \"${IMAGE_NAME}\" | .spec.serviceAccountName = \"${SERVICE_ACCOUNT}\" | .metadata.name = \"${POD}\"" \
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
