#!/bin/bash
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

errcho(){ >&2 echo $@; }

setup_bucket() {
  # errcho $(microk8s.enable minio)

  # Get Access key and secret key from MinIO
  kubectl get secret -n minio-operator microk8s-user-1
  if [ $? -eq 0 ]; then
    ACCESS_KEY=$(kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_ACCESS_KEY}' | base64 -d)
    SECRET_KEY=$(kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_SECRET_KEY}' | base64 -d)
  else
    echo "Using default MinIO access key and secret key..."
    ACCESS_KEY=minio
    SECRET_KEY=minio123
  fi

  # Get S3 endpoint from MinIO
  S3_ENDPOINT=$(kubectl get service minio -n minio-operator -o jsonpath='{.spec.clusterIP}')

  echo "access_key:${ACCESS_KEY},secret_key:${SECRET_KEY},host:${S3_ENDPOINT}"
}

teardown_bucket() {
  # errcho $(microk8s.disable minio)

  echo "ok"
}

case $1 in
  create)
    shift
    setup_bucket $*
    ;;
  teardown)
    shift
    teardown_bucket $*
    ;;
  *)
    echo "Mode not recognized"
    exit 1
    ;;
esac
