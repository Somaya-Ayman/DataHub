# DataHub Deployment Guide

This guide documents the full deployment of DataHub on a local Kubernetes cluster using Minikube and Helm.
It includes known issues encountered during setup and how to resolve them.

---

## Prerequisites

Make sure the following are installed before starting:

- Docker
- Minikube
- kubectl
- Helm 3.x

Minimum resources required for DataHub to run without crashlooping:

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 6 cores |
| RAM | 8GB | 12GB |

---

## Step 1 — Start Minikube

```bash
minikube start --cpus=6 --memory=12288 --driver=docker
```

Verify the cluster is healthy:

```bash
minikube status
kubectl get nodes
```

Expected output:
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   30s   v1.x.x
```

---

## Step 2 — Create Namespace and Secrets

```bash
kubectl create namespace datahub

kubectl create secret generic mysql-secrets \
  --from-literal=mysql-root-password=<your-password> \
  -n datahub

kubectl create secret generic neo4j-secrets \
  --from-literal=neo4j-password=<your-password> \
  -n datahub
```

> **Note:** Replace `<your-password>` with a strong password. Never commit real passwords to git.

---

## Step 3 — Add the DataHub Helm Repository

```bash
helm repo add datahub https://helm.datahubproject.io/
helm repo update
```

---

## Step 4 — Install Prerequisites

DataHub depends on OpenSearch, Kafka, and MySQL. These must be fully running before installing DataHub itself.

```bash
helm install prerequisites datahub/datahub-prerequisites \
  --namespace datahub
```

Wait for all prerequisite pods to reach `Running` state before continuing.
This takes around 5-10 minutes:

```bash
kubectl get pods -n datahub -w
```

Only proceed when you see all three running:

```
NAME                               READY   STATUS    RESTARTS   AGE
opensearch-cluster-master-0        1/1     Running   0          10m
prerequisites-kafka-controller-0   1/1     Running   0          10m
prerequisites-mysql-0              1/1     Running   0          10m
```

> **Important:** Do not install DataHub before all prerequisites are `Running`.
> Rushing this step causes the pre-install hook to fail.

---

## Step 5 — Install DataHub

```bash
helm install datahub datahub/datahub \
  --namespace datahub \
  --timeout 20m
```

Monitor the pods:

```bash
kubectl get pods -n datahub -w
```

All pods should eventually reach `Running` or `Completed`:

```
NAME                                            READY   STATUS
datahub-acryl-datahub-actions-xxx               1/1     Running
datahub-datahub-frontend-xxx                    1/1     Running
datahub-datahub-gms-xxx                         1/1     Running
datahub-system-update-xxx                       0/1     Completed
datahub-system-update-nonblk-xxx                0/1     Completed
opensearch-cluster-master-0                     1/1     Running
prerequisites-kafka-controller-0                1/1     Running
prerequisites-mysql-0                           1/1     Running
```

---

## Step 6 — Access DataHub

Port-forward the frontend service:

```bash
kubectl port-forward svc/datahub-datahub-frontend 9002:9002 -n datahub
```

Open http://localhost:9002 in your browser.

Default credentials:
- **Username:** `datahub`
- **Password:** `datahub`

To access the GraphQL playground:

```bash
kubectl port-forward svc/datahub-datahub-gms 8080:8080 -n datahub
```

Open http://localhost:8080/api/graphql

---

## Known Issues and Fixes

### Issue 1 — Pre-install hook conflict

**Error:**
```
Error: INSTALLATION FAILED: failed pre-install: resource Job/datahub/datahub-system-update
not ready. status: InProgress, message: Job in progress
context deadline exceeded
```

**Why it happens:**

DataHub runs a pre-install Job called `datahub-system-update` that handles database
migrations before the main install. If the install times out, Helm marks the release
as failed but leaves the Job behind. A second install attempt finds the Job already
exists and fails immediately.

**Fix:**

```bash
# Remove the failed Helm release
helm uninstall datahub -n datahub

# Delete the leftover Job manually
kubectl delete job datahub-system-update -n datahub

# Confirm it is gone
kubectl get jobs -n datahub

# Reinstall
helm install datahub datahub/datahub \
  --namespace datahub \
  --timeout 20m
```

---

### Issue 2 — ImagePullBackOff on DataHub pods

**Error:**
```
Failed to pull image "docker.io/acryldata/datahub-frontend-react:v1.6.0":
context deadline exceeded (Client.Timeout exceeded while awaiting headers)
```

**Why it happens:**

Minikube runs as a separate VM/container with its own Docker daemon. When Kubernetes
tries to pull DataHub images from Docker Hub, it times out because the connection
from inside Minikube is slow or unauthenticated.

**Fix — pre-pull images manually inside Minikube:**

```bash
# SSH into Minikube
minikube ssh

# Pull all DataHub images manually
docker pull acryldata/datahub-frontend-react:v1.6.0
docker pull acryldata/datahub-gms:v1.6.0
docker pull acryldata/acryl-datahub-actions:v1.6.0

# Exit Minikube
exit

# Delete the failing pod so Kubernetes creates a new one
# It will find the image already cached and start immediately
kubectl delete pod -n datahub <pod-name>
```

After deleting the pod, Kubernetes creates a replacement and finds the image
already cached inside Minikube — no pull needed, starts immediately.

---

## Uninstalling

To tear down the full deployment:

```bash
helm uninstall datahub -n datahub
helm uninstall prerequisites -n datahub
kubectl delete namespace datahub
```

---

## References

- [DataHub Documentation](https://datahubproject.io/docs/)
- [DataHub Helm Charts](https://github.com/acryldata/datahub-helm)
- [Kubernetes CronJob Docs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
