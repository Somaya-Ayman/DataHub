# Data Ingestion & Governance Testing

This guide covers how to ingest demo data into DataHub and test the governance automation script.

## Prerequisites

- DataHub deployed on Kubernetes and running
- Access tokens configured
- Python 3.9+ with datahub CLI installed

## Step 1: Install DataHub CLI with Demo Data Support

```bash
pip install 'acryl-datahub[demo-data]'
```

## Step 2: Access DataHub UI and Generate Access Token

### Port-forward to DataHub Services

```bash
# Terminal 1: Forward to GMS (metadata service)
kubectl port-forward svc/datahub-datahub-gms 8080:8080 -n datahub

# Terminal 2: Forward to Frontend
kubectl port-forward svc/datahub-datahub-frontend 9002:9002 -n datahub
```

### Generate Access Token

1. Navigate to **http://localhost:9002**
2. Log in with credentials:
   - **Username:** `add username`
   - **Password:** `add password`
3. Click your **profile icon** (top right) → **Settings**
4. Go to **Access Tokens** → **Generate New Token**
5. Copy the generated token (you'll use this for ingestion)


## Step 3: Ingest Demo Data

### Option 1: Using Command Line

```bash
datahub ingest -c - <<EOF
source:
  type: demo-data
  config: {}
sink:
  type: datahub-rest
  config:
    server: http://localhost:8080
    token: "<your-access-token-here>"
EOF
```

Replace `<your-access-token-here>` with the token from Step 2.

### Successful Ingestion Output

```
[2026-06-19 02:23:44,125] INFO {datahub.cli.ingest_cli:202} - DataHub CLI version: 1.3.1.7.post3
[2026-06-19 02:23:44,159] INFO {datahub.ingestion.run.pipeline:225} - Sink configured successfully.
[2026-06-19 02:23:44,831] INFO {datahub.ingestion.run.pipeline:254} - Source configured successfully.
[2026-06-19 02:23:44,831] INFO {datahub.cli.ingest_cli:183} - Starting metadata ingestion
[2026-06-19 02:24:00,234] INFO {datahub.cli.ingest_cli:196} - Finished metadata ingestion

Pipeline finished successfully; produced 105 events in 15.92 seconds.
```

**Key metrics:**
- **Total records written:** 105
- **Events produced:** 103
- **Duration:** ~16 seconds

## Step 4: Verify Ingested Data

1. Go to **http://localhost:9002**
2. Navigate to **Search** or **Browse**
3. You should see several demo datasets:
   - `fct_users_created`
   - `fct_orders`
   - `dim_dates`
   - And more...

## Step 5: Test Governance Automation

### About the Governance Script

The governance script automatically:
- Finds datasets **without owners**
- Applies a `needs-owner` tag to them
- Can run on a schedule (CronJob in Kubernetes)

### Pre-Test Setup

#### Export Token Environment Variable

```bash
export DATAHUB_TOKEN="your-access-token-here"
```

#### Or Store in Kubernetes Secret

```bash
kubectl create secret generic governance-secret \
  --from-literal=DATAHUB_TOKEN="your-access-token-here" \
  -n datahub-jobs
```

### Test Scenario: Remove Owners and Verify Tag

#### 1. Remove Owner from a Dataset

```bash
# Using DataHub UI
# 1. Click on a dataset (e.g., fct_users_created)
# 2. Go to Ownership section
# 3. Click the trash icon to remove any existing owners
# 4. Save changes
```

**Or via GraphQL mutation** (advanced):

```bash
# Access DataHub GraphQL
# POST http://localhost:8080/api/graphql
```

#### 2. Run Governance Script in Dry-Run Mode

Test what would happen without making changes:

```bash
cd /home/somaya/Music/DataHub/src/governance
python governance.py --dry-run
```

**Expected output:**

```
2026-06-19 18:31:32,274 [INFO] Starting governance job. dry_run=True
2026-06-19 18:31:32,310 [WARNING] Tag may already exist (safe to ignore): ...
2026-06-19 18:31:33,295 [INFO] Found X unowned datasets out of Y total.
2026-06-19 18:31:33,295 [INFO] [DRY-RUN] Would tag: urn:li:dataset:(urn:li:dataPlatform:demo,fct_users_created,PROD)
```

#### 3. Run Governance Script (Apply Tags)

```bash
cd /home/somaya/Music/DataHub/src/governance
python governance.py
```

**Expected output:**

```
2026-06-19 18:31:32,274 [INFO] Starting governance job. dry_run=False
2026-06-19 18:31:32,310 [WARNING] Tag may already exist (safe to ignore): ...
2026-06-19 18:31:33,295 [INFO] Found 1 unowned datasets out of 105 total.
2026-06-19 18:31:33,500 [INFO] [TAGGED] urn:li:dataset:(urn:li:dataPlatform:demo,fct_users_created,PROD)
2026-06-19 18:31:33,600 [INFO] Done. tagged=1, skipped=0, failed=0
```

#### 4. Verify Tag in DataHub UI

```bash
# 1. Go to http://localhost:9002
# 2. Click on the dataset you just tagged
# 3. Look for the "needs-owner" tag in the Tags section
# 4. It should now be visible with a "needs-owner" label
```

### Complete Testing Workflow

```bash
# Terminal 1: Port-forward
kubectl port-forward svc/datahub-datahub-frontend 9002:9002 -n datahub

# Terminal 2: Set token and run
export DATAHUB_TOKEN="your-token"
cd /home/somaya/Music/DataHub/src/governance

# Test dry-run
python governance.py --dry-run

# Apply governance
python governance.py

# Verify in UI at http://localhost:9002
```

## Governance Script Details

### What It Does

1. **Ensures tag exists** - Creates `needs-owner` tag if missing
2. **Finds unowned datasets** - Searches for datasets with `owners:null`
3. **Tags datasets** - Applies the tag to mark datasets needing owners
4. **Logs results** - Reports tagged, skipped, and failed counts

### Output Metrics

```
tagged=X         # Number of datasets tagged
skipped=Y        # Already tagged (idempotent)
failed=Z         # Failed operations (causes exit code 1)
```

### Schedule as CronJob

The script runs automatically via Kubernetes CronJob:

```bash
# Deploy to dev (every 5 minutes)
kubectl apply -k k8s/overlays/dev/

# Check status
kubectl get cronjobs -n datahub-jobs
kubectl get pods -n datahub-jobs
```

### View CronJob Logs

```bash
# List completed jobs
kubectl get pods -n datahub-jobs

# Check logs from a specific run
kubectl logs <pod-name> -n datahub-jobs
```

## Troubleshooting

### No Unowned Datasets Found

**Cause:** All datasets have owners assigned or were ingested with owners.

**Solution:**
1. Use DataHub UI to remove owner from a dataset
2. Re-run the governance script

### GraphQL Validation Errors

**Cause:** Schema mismatch or invalid field names.

**Solution:**
1. Check DataHub version compatibility
2. Update GraphQL query in `governance.py`
3. Verify fields exist in your DataHub schema

### Authentication Failed

**Cause:** Invalid or expired token.

**Solution:**
1. Generate a new access token in DataHub UI
2. Update the `DATAHUB_TOKEN` secret
3. Restart the governance job

## Resources

- [DataHub Ingestion Documentation](https://datahub.acryldata.io/docs/generated/ingestion/sources/demo-data)
- [DataHub API Reference](https://datahubproject.io/docs/api/graphql)
- [DataHub Access Control](https://datahub.acryldata.io/docs/act/policies)
