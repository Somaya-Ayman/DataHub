# DataHub Governance Automation

A complete DataHub deployment with automated data governance on Kubernetes.

## What I Built

**Governance Automation** — A Kubernetes CronJob that automatically finds all datasets without owners in DataHub and tags them with `needs-owner` for follow-up.

**Key Features:**
- Automated owner assignment enforcement
- Runs on a schedule (nightly in production, every 5 minutes in dev)
- Idempotent — safe to run multiple times
- Dry-run mode for testing
- Comprehensive logging and error handling

## How to Run Locally

### Prerequisites

- **Minikube** (or any Kubernetes cluster)
- **Helm 3.x**
- **kubectl**
- **Docker** (for image building and pushing)
- **Python 3.9+** (for local testing)

### 1. Start Minikube

```bash
minikube start --cpus=6 --memory=12288 --driver=docker
```

### 2. Deploy DataHub

```bash
helm repo add datahub https://helm.datahubproject.io/
helm repo update

# Create namespace and secrets
kubectl create namespace datahub
kubectl create secret generic mysql-secrets \
  --from-literal=mysql-root-password=datahub \
  -n datahub

# Deploy prerequisites (OpenSearch, Kafka, MySQL)
helm install prerequisites datahub/datahub-prerequisites \
  --namespace datahub

# Wait for all pods to be Running
kubectl get pods -n datahub -w

# Deploy DataHub
helm install datahub datahub/datahub \
  --namespace datahub \
  --timeout 20m
```

**For detailed setup:** See [docs/deployment.md](docs/deployment.md)

### 3. Ingest Sample Data

```bash
# Port-forward to GMS
kubectl port-forward svc/datahub-datahub-gms 8080:8080 -n datahub &

# Install datahub CLI
pip install 'acryl-datahub[demo-data]'

# Generate access token in UI first:
# 1. kubectl port-forward svc/datahub-datahub-frontend 9002:9002 -n datahub
# 2. Go to http://localhost:9002, login (datahub/datahub)
# 3. Profile → Settings → Access Tokens → Generate New Token
# 4. Copy token and use below

# Ingest demo data
datahub ingest -c - <<EOF
source:
  type: demo-data
  config: {}
sink:
  type: datahub-rest
  config:
    server: http://localhost:8080
    token: "<your-access-token>"
EOF
```

**For detailed guide:** See [docs/ingestion-and-governance.md](docs/ingestion-and-governance.md)

### 4. Create Governance Secret

```bash
# Create the secret in Kubernetes
kubectl create secret generic governance-secret \
  --from-literal=DATAHUB_TOKEN="your-access-token" \
  -n datahub-jobs
```

Or manually edit the placeholder:

```bash
# Edit the local file (NOT committed to git)
cat > k8s/base/governance/secret.yaml <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: governance-secret
  namespace: datahub-jobs
type: Opaque
stringData:
  DATAHUB_TOKEN: "your-actual-token-here"
EOF
```

### 5. Build and Push Docker Image

```bash
# Build image
docker build -t <docker-username>/governance-job:latest src/governance/

# Push to Docker Hub
docker login  # If not already logged in
docker push <docker-username>/governance-job:latest
```

Update the image reference in `k8s/base/governance/cronjob.yaml`:

```yaml
containers:
- name: governance
  image: <docker-username>/governance-job:latest  # Update this line
```

### 6. Deploy Governance Job

```bash
# Deploy dev overlay (runs every 5 minutes)
kubectl apply -k k8s/overlays/dev/

# Check status
kubectl get cronjobs -n datahub-jobs
kubectl get pods -n datahub-jobs

# View logs
kubectl logs -n datahub-jobs -l job-name --tail=50
```

### 7. Test Locally

```bash
# Set token as environment variable
export DATAHUB_TOKEN="your-access-token"

# Run dry-run (preview changes)
cd src/governance
python governance.py --dry-run

# Run with actual tagging
python governance.py
```

## Key Design Decisions

### Idempotency
The governance script checks if a dataset is already tagged before tagging it. Running it multiple times produces the same result — no duplicate tags.

### Pagination
All dataset queries paginate in batches of 100 to handle large catalogs without memory issues.

### Dry-run Mode
Both scripts support `--dry-run` to preview changes without modifying anything. Perfect for testing.

### Kustomize Overlays
- **Base:** Standard production schedule (nightly at midnight)
- **Dev overlay:** Runs every 5 minutes for rapid testing

Easily switch environments:

```bash
# Dev (every 5 minutes)
kubectl apply -k k8s/overlays/dev/

# Production (nightly)
kubectl apply -k k8s/overlays/prod/
```

### Non-root Containers
Dockerfile creates a non-root `govadmin` user for security.

### Secrets Pattern
- Actual secrets are NOT committed to git (.gitignore)
- Secret files contain placeholders only
- Created manually or via CI/CD before deployment

## What I Would Improve

- Add Sealed Secrets for encrypted secrets in git
- Add Prometheus metrics (datasets tagged per run, errors)
- Add alerts (Slack webhook on job failure)
- Unit tests for GraphQL queries
- Helm chart for the jobs themselves
- Database for job run history and auditing
- Multi-environment support (dev/staging/prod)

## Known Limitations

- Images built and pushed manually — no automated CI/CD pipeline yet
- Only tested with demo data — real production data sources would need additional testing
- Single node Minikube setup — production uses multi-node clusters
- Governance script currently tags datasets without owners — could extend to other policies
- No role-based access control (RBAC) beyond Kubernetes default

## Documentation

- [Deployment Guide](docs/deployment.md) — Detailed DataHub setup
- [Ingestion & Governance Guide](docs/ingestion-and-governance.md) — Complete testing workflow
- [Docker Registry Guide](docs/docker-registry.md) — Image building and pushing

## Quick Reference

```bash
# Check cluster status
kubectl get pods -n datahub
kubectl get pods -n datahub-jobs

# View logs
kubectl logs -n datahub-jobs <pod-name>

# Trigger job manually
kubectl create job --from=cronjob/governance-job governance-manual -n datahub-jobs

# Port-forward to UI
kubectl port-forward svc/datahub-datahub-frontend 9002:9002 -n datahub

# Port-forward to GMS
kubectl port-forward svc/datahub-datahub-gms 8080:8080 -n datahub
```

## Repository Structure

```
DataHub/
├── src/governance/           # Governance automation script
│   ├── governance.py         # Main script
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Container image
├── k8s/                       # Kubernetes manifests
│   ├── base/                  # Base configs
│   │   └── governance/
│   │       ├── cronjob.yaml
│   │       ├── configmap.yaml
│   │       ├── secret.yaml    # ⚠️ In .gitignore (local only)
│   │       └── kustomization.yaml
│   └── overlays/
│       └── dev/               # Dev environment (5-min schedule)
├── docs/                      # Documentation
│   ├── deployment.md
│   ├── ingestion-and-governance.md
│   └── docker-registry.md
└── README.md
```

## Resources

- [DataHub Documentation](https://datahubproject.io/docs/)
- [DataHub Helm Charts](https://github.com/acryldata/datahub-helm)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Guide](https://kustomize.io/)
