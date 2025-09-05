(tutorial-7-wrapping-up)=
# 7. Wrapping Up

This section concludes the Tutorial by freeing up the resources used so far.

## Clean up

Since we've used a Multipass VM for this tutorial, the clean up process consists of making sure the VM is deleted from the Host machine.

```shell
multipass delete --purge spark-tutorial
```

This command immediately deletes VM and all associated resources.

## Learn more

Parts of this tutorial were originally presented in a talk at Ubuntu Summit 2023.

The recording is available on [YouTube](https://www.youtube.com/watch?v=nu1ll7VRqbI).

This tutorial covers running Charmed Apache Spark locally using MicroK8s.

Running Charmed Apache Spark on MicroK8s locally is limited by the available system resources.

For a more scalable and production-ready setup, you can deploy the Charmed Apache Spark solution on AWS EKS.

Refer to the [how-to guide](/) for instructions on deploying and configuring an AWS EKS cluster for Charmed Apache Spark.

You can also check out a video demonstration from the [2023 Operator Day demo](https://github.com/deusebio/operator-day-2023-charmed-spark) showcasing Charmed Apache Spark running on AWS EKS.

