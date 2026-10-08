---
myst:
  html_meta:
    description: "Documentation for manually validating Charmed Apache Spark on ProdStack 7 (PS7)."
---

(validation-ps7)=
# PS7

The repository contains the instructions and the artifact to validate the Charmed Spark solution on ProdStack (PS7).

You can find the resources used in the guide in the `spark-k8s-bundle` repo at [`./resources/ps7`](https://github.com/canonical/spark-k8s-bundle/tree/track/3.5/resources/ps7).

## Object storage setup

### Setup

Initialize a new lxd container with the provided cloud-init file `./setup/microceph.yaml`.
In the script file, replace the value of the proxy.

Execute the following commands:

```bash
lxc init ubuntu:jammy ceph -c limits.cpu=2 -c limits.memory=2GB -d root,size=5GB
lxc config set ceph cloud-init.user-data - < microceph.yaml
lxc start ceph 
```

Check the progress of the setup using

```
lxc exec ceph -- tail -f  /var/log/cloud-init-output.log
```

Verify that the setup has been done correctly using

```
lxc exec ceph -- cloud-init status --wait
```

Extract the endpoint, access key and secret key into variables

```bash
CEPH_IP=$(lxc list --format json | yq '.[] | select(.name == "ceph") .state.network.eth0.addresses.[] | select(.family == "inet") .address')
ENDPOINT_URL="http://$CEPH_IP:80"
S3_ACCESS_KEY=foo
S3_SECRET_KEY=bar
```

### Test the object storage

First install the AWS CLI

```bash
sudo snap install aws-cli --classic
```

Configure the snap with the access key, secret key

```bash
aws configure set aws_access_key_id $S3_ACCESS_KEY
aws configure set aws_secret_access_key $S3_SECRET_KEY
aws configure set endpoint_url $ENDPOINT_URL
```

Make sure that the Ceph IP is added to the NO_PROXY env variable

```bash
export NO_PROXY=$NO_PROXY,$CEPH_IP
export no_proxy=$NO_PROXY
```

Test that the connection is working by list

```bash
aws s3 ls
```

or creating a bucket

```
aws s3api create-bucket --bucket spark-tutorial --region us-east1
```

## Cloud Setup

Install concierge

```bash
sudo snap install concierge --classic
```

and install using the `concierge.yaml` file found in the `setup` folder. Make sure that the concierge.yaml is also setting the correct value for the proxy. Use the values that are stored in the HTTP_PROXY, HTTPS_PROXY and NO_PROXY environment variables.

```bash
cd setup
sudo concierge prepare
```

Once the command has finished, test that all the services are up and running:

* K8s
```bash
kubectl get pod -A
```

# Juju
```bash
juju model-config
```

Make sure that the proxy are correctly setup in the `juju-http-proxy`, `juju-https-proxy` and `juju-no-proxy`.

## Deploy Charmed Spark

Navigate to the `terraform` folder, and import the juju controller ip, username and password

```bash
source setup.sh
```

Also set the environment variable for s3 and proxies to be fed to the Terraform module

```bash
export TF_VAR_NO_PROXY=$NO_PROXY
export TF_VAR_HTTP_PROXY=$HTTP_PROXY
export TF_VAR_HTTPS_PROXY=$HTTPS_PROXY

export TF_VAR_S3_ENDPOINT_URL=$S3_ENDPOINT_URL
export TF_VAR_S3_ACCESS_KEY=$S3_ACCESS_KEY
export TF_VAR_S3_SECRET_KEY=$S3_SECRET_KEY
```

Initialize the Terraform plan

```bash
terraform init
```

and apply the module

```bash
terrafrom apply -auto-approve
```

Wait for all the services to go into active/idle.

Retrieve the ingress IP

```bash
INGRESS_IP=$(kubectl get svc -n cos traefik-lb -o yaml | yq '.status.loadBalancer.ingress[0].ip')
```

and add it to the NO_PROXY environment variable

```bash
export NO_PROXY=$NO_PROXY,$INGRESS_IP
export no_proxy=$NO_PROXY
```

## Running UATs

Clone the `spark-k8s-bundle` repository

```bash
git clone https://github.com/canonical/spark-k8s-bundle.git 
```

Create and activate a python environment (using python 3.10 or 3.12)

```
python -m venv uats
source uats/bin/activate
```

Install poetry and then use poetry to install the `integration` environment

```
pip install poetry
poetry install --with integration
```

At this point, you can run the UATs

```
poetry run pytest -vv --tb native --log-cli-level=INFO \
  -s -x "./tests/integration/test_kyuubi.py" \
  --no-deploy --keep-models --model spark --cos-model cos
```

Verify that the tests completes successfully

```
================================================================================================ warnings summary =================================================================================================
../../vks-validation/uats/lib/python3.12/site-packages/_pytest/config/__init__.py:1464
  /home/ubuntu/repos/vks-validation/uats/lib/python3.12/site-packages/_pytest/config/__init__.py:1464: PytestConfigWarning: Unknown config option: asyncio_mode
  
    self._warn_or_fail_if_strict(f"Unknown config option: {key}\n")

tests/integration/test_kyuubi.py:38
  /home/ubuntu/repos/spark-k8s-bundle/python/tests/integration/test_kyuubi.py:38: PytestUnknownMarkWarning: Unknown pytest.mark.skip_if_deployed - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.skip_if_deployed

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=============================================================================== 7 passed, 1 skipped, 2 warnings in 65.98s (0:01:05) ===============================================================================
```