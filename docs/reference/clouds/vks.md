---
myst:
  html_meta:
    description: "Documentation for manually validating Charmed Apache Spark on vSphere Kubernetes Service (VKS)."
---

(validation-vks)=
# Charmed Spark Validation on VKS

This guide contains the instructions to validate the Charmed Spark solution on VMware vSphere Kubernetes Service (VKS).

You can find the resources used in the guide in the `spark-k8s-bundle` repository at [`./resources/vks`](https://github.com/canonical/spark-k8s-bundle/tree/track/3.5/resources/vks).

## Instructions

### System Access

Validation has been done on the VMware Lab. The platform is available at the link: [https://labplatform.broadcom.com/isv-lab/](https://labplatform.broadcom.com/isv-lab/).

Login using username and password as provided by VMware. Once logged in, start a new session by clicking "ENROLLED" in the "ISV VKS Validation" Lab. This will provide connection to the a small VVF 9.0.2 environment running WCP 3.6.2 with a 2 node VKS cluster for ISV software validation.

The edge node contains a number of useful scripts under `/home/holuser/Desktop/Scripts/`.

### Deleting existing VKS cluster (Optional)

Once logged in, an existing VKS cluster may be present, running on 1.35. The validation had been agreed to be performed on 1.34. Follow the below steps to delete an existing cluster. 

First go to the scripts folder `/home/holuser/Desktop/Scripts/`.

Then, login into the supervisor

```
./ns1-login
```

(use the password provided in the text file PASSWORD.txt)

Torn down an existing cluster using

```
./ns1-delete-vks1
```

### Setup new VKS cluster

To setup the VKS cluster, go to the folder ~/Desktop/Scripts where all the scripts to manage K8s cluster are found. 

Then, first login in the supervisor (if not yet logged in)

```
./ns1-login
```

(use the password provided in the text file PASSWORD.txt)

Deploy a new K8s cluster (version 1.34) using 

```
./ns1-create-vks1-1.34
```

The process should take about 15-20 minutes.


Once the cluster is up and running, login to the K8s using 

```
./ns1-login-vks1
```

Once logged in, you should be able to use `kubectl` normally. You can list all the contexts (and the one active) using 

```
kubectl config get-contexts
```

### Setup Juju

First, install juju and terraform

```
sudo snap install juju --channel 3.6/stable
```

(use the password provided in the text file PASSWORD.txt if needed to gain elevated privileges)

Use the context active to bootstrap the controller. So first add the k8s:

```
juju add-k8s --context-name <name> vks-cloud
```

and then bootstrap controller on that cloud

```
juju bootstrap vks-cloud vks-controller
```

Note that the controller that is bootstrapped in this way will not be reachable from the edge node since it will not be exposed outside of K8s. `juju` commands (using the SNAP) will still be working since Juju CLI will proxy the requests via `kubectl` and the K8s api. However terraform provider will not be able to connect to the Juju controller. Unfortunately, bootstrapping Juju controller using `--config controller-service-type=loadbalance` did not work out of the box and returned an error when bootstrapping:

```
ERROR unable to contact api server after 0 attempts: unknown error in bootstrap api connect: unable to connect to API: read tcp 10.1..10.130:48286->10.1.7.5:17070: read: connection reset by peer
```

To expose the controller service, you can create an LoadBalancer dedicated service by first finding out the namespace for the controller

```
kubectl get ns
```

And apply the LB service resource provided in this repository:

```
kubectl apply -f setup/juju-lb.yaml -n <controller-vks-namespace>
```

Check that the newly created LB service has been assigned with an external IP:

```
kubectl get svc -n controller-vks
```

Store the IP into a dedicated environment variable:

```
export CONTROLLER_IP=$(kubectl get svc controller-service-lb -n <controller-vks-namespace> -o yaml | yq '.status.loadBalancer.ingress[0].ip')
```

### Deploy Charmed Spark (manually)

Charmed Spark can be deployed following the guide in the [documentation](https://canonical.com/data/spark/docs/3.5/how-to/deploy/kyuubi/) with no issue. Note that you will need to provide the credentials for an S3 bucket during the process.

The deployment can be validated as shown in the documentation by connecting to Spark using `beeline`. Feel free to use the `beeline` provided in the `spark-client` snap that can be easily installed with

```
sudo snap install spark-client --channel 3.5/stable
```

### Deploy Charmed Spark using Terraform

First install the terraform snap

```
sudo snap install terraform --classic
```

Once this is done, navigate to the `terraform` folder, where the Terraform scripts are stored. Along side the `.tf` files, there is also `setup.sh` to parse the YAML files for Juju connections details into TF variables:

```
source setup.sh
```

You can check the value of the variables using

```
env | grep TF_VAR_
```

The controller IP may however be the internal one. Replace its value with the external IP:

```
export TF_VAR_JUJU_CONTROLLER_IPS=$CONTROLLER_IP:17070
```

Lastly, set the value of the S3 credentials:

```
export TF_VAR_S3_ACCESS_KEY=...
export TF_VAR_S3_SECRET_KEY=...
```

Once all the TF vars are set using environment variable, the TF modules can be planned and applied:

```
terraform plan
```

Review the changes before applying

```
terraform apply -auto-approve
```

### Manual Verification

The deployments using TF comes with encryption provided by self-signed certificates. In order to connect to the service using beeline first retrieve credentials/connections information from `data-integrator`

```
juju run data-integrator/leader get-credentials > credentials.yaml
```

Export the CA into a file:

```
yq ".kyuubi.tls-ca" credentials.yaml > ca.cert
```

and importing into the truststore using the `spark-client' snap

```
spark-client.import-certificate kyuubi ca.cert
```

At this point you can connect using `beeline` using the following command:

```
spark-client.beeline -u "$(yq '.kyuubi.uris' credentials.yaml);ssl=true;trustStorePassword=changeit;sslTrustStore=/var/snap/spark-client/current/etc/ssl/certs/java/cacerts;"  -p $(yq '.kyuubi.password' credentials.yaml) -n $(yq '.kyuubi.username' credentials.yaml)
```

To test that everything works correctly, you can use the following SQL query

```
create database abc;
use abc;
create table users (id int);
insert into users values (1);
select * from users;
```

### Running UATs

#### Setting up the Python Environment

To run the UATs, a working Python 3.10 environment is needed, and miniconda will be used. Therefore, first download and install anaconda:

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Then initialize the environment, by also unsetting the PYTHONPATH environment variable:

```
unset PYTHONPATH
eval "$(/home/holuser/miniconda3/bin/conda shell.bash hook)"
```

At this point, use `conda` to create and activate a new python 3.10 environment:

```
conda create -n uats python=3.10
conda activate uats
```

Within the environment, install `tox` and `poetry`

```
pip install tox
pip install poetry
```

#### Running the UATs

To run the UATs, first clone the UATs repository

```
git clone https://github.com/canonical/spark-k8s-bundle.git
```

Once it is cloned, navigate to the folder `./python` and install the python dependencies

```
cd python/
poetry install --with integration
```

The bastion node is behind a proxy, as you can verify by listing the environment variables:

```
env | grep PROXY
env | grep proxy
```

To make sure the UATs runs smoothly, it may be important to make sure that the calls directed to the VKS cluster do not go through the proxy. To do so, just add the various IPs in the `NO_PROXY` and `no_proxy` variables:

```
export NO_PROXY=$NO_PROXY,10.1.7.5,10.1.7.6,10.1.7.7,10.1.7.8
export no_proxy=$NO_PROXY
```

And this point, the UATs can be run

```
poetry run pytest -vv --tb native --log-cli-level=INFO -s -x "./tests/integration/test_kyuubi.py" --no-deploy --keep-models --model spark --cos-model cos
```

Running the UATs worked fine, confirmed by the message in the logs:

```
================================================== tests coverage ==================================================
________________________________________ coverage: platform linux, python 3.10.20-final-0 ________________________________________

Name                                  Stmts   Miss  Cover
---------------------------------------------------------
spark_test/__init__.py                    5      0   100%
spark_test/core/__init__.py              23      7    70%
spark_test/core/azure_storage.py        74     45    39%
spark_test/core/bundle/__init__.py       27     12    56%
spark_test/core/bundle/terraform.py     37     23    38%
spark_test/core/kyuubi.py               117     15    87%
spark_test/core/pod.py                   54     29    46%
spark_test/core/s3.py                    80     46    42%
spark_test/fixtures/__init__.py           0      0   100%
spark_test/fixtures/azure_storage.py     21     11    48%
spark_test/fixtures/k8s.py               39     18    54%
spark_test/fixtures/pod.py               26     10    62%
spark_test/fixtures/s3.py                28     16    43%
spark_test/fixtures/service_account.py   38     13    66%
spark_test/utils.py                      23     23     0%
---------------------------------------------------------
TOTAL                                   592    268    55%

==================================== 7 passed, 1 skipped, 2 warnings in 103.31s (0:01:43) ====================================
```