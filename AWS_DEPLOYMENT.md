# TraceProof AWS Deployment Guide

TraceProof uses **AWS SAM (Serverless Application Model)** to deploy five managed AWS services configured for least privilege and synthetic research safety.

> [!CAUTION]
> **STRICT SAFETY POLICY:**
> The repository code and local SAM artifacts are deployment-ready. However, **do not run `sam deploy` without explicit user authorization.** TraceProof processes only synthetic sample registrations and never calls destructive cloud APIs such as DynamoDB `DeleteItem` or S3 `DeleteObject`.

---

## 1. Managed AWS Services Architecture

| Service Family | Specific Resources | Architectural Role in TraceProof |
|---|---|---|
| **1. Amazon API Gateway** | `TraceProofHttpApi` (HTTP API) | Ingests all frontend HTTP requests (`GET`, `POST`, `OPTIONS`), enforces CORS policy restricted to `FrontendOrigin`, routes requests directly to `ApiFunction`. |
| **2. AWS Lambda** | `ApiFunction`<br>`WorkerFunction` | **ApiFunction:** Synchronous request router, Pydantic/JSON validation, DynamoDB reads/writes, SQS enqueueing, S3 presigned URL generation, experiment runner.<br>**WorkerFunction:** Asynchronous SQS consumer, dependency graph traversal, deletion verification simulation, S3 report storage, DLQ redrive handling. |
| **3. Amazon DynamoDB** | `ResourceTable`<br>`RequestTable`<br>`ExperimentTable` | Three on-demand tables:<br>• `ResourceTable`: Registered cloud resources and dependency metadata (`depends_on`).<br>• `RequestTable`: Deletion request status tracking (`Pending`, `Processing`, `Verified`, `Incomplete`, `Failed`).<br>• `ExperimentTable`: Persisted experiment results with 7-day TTL (`ttl` attribute). |
| **4. Amazon SQS** | `DeletionQueue`<br>`DeletionDeadLetterQueue` | Asynchronous decoupled message processing with SSE-SQS encryption:<br>• `DeletionQueue`: 300s visibility timeout, redrive policy configured with `maxReceiveCount` (default: 3).<br>• `DeletionDeadLetterQueue`: Retains messages after max retries for audit and troubleshooting (14-day retention). |
| **5. Amazon S3** | `ReportBucket` | Private AES-256 encrypted bucket with Block Public Access enabled:<br>• `reports/{request_id}.json`: Auditable deletion verification reports (served via 5-min presigned URLs).<br>• `experiments/{experiment_id}/trial_records.json`: Raw Monte Carlo trial datasets.<br>• Automatic 90-day lifecycle expiration policy. |

---

## 2. Request Lifecycle & Asynchronous Processing

```
[React Browser App]
       │
       ▼ (POST /deletion-requests)
[API Gateway HTTP API]
       │
       ▼
[ApiFunction Lambda] ──► Validates resource & writes "Pending" to DynamoDB RequestTable
       │
       ▼ Enqueues {request_id}
[Amazon SQS DeletionQueue]
       │
       ▼ (BatchSize: 1, MaxConcurrency: 2)
[WorkerFunction Lambda]
       ├── Sets status = "Processing" in RequestTable
       ├── Traverses registered dependency graph (cycle-safe BFS)
       ├── Executes simulated deletion on root and all dependent resources
       ├── Writes JSON verification report to S3 (`reports/<request_id>.json`)
       └── Sets terminal status in RequestTable ("Verified" or "Incomplete")
       │
       ▼ (If retries exceed MaxReceiveCount)
[SQS DeletionDeadLetterQueue] (Sets status = "Failed")
```

When the browser requests `/deletion-requests/{request_id}/report`, `ApiFunction` generates a temporary 5-minute presigned S3 GET URL and returns an HTTP 302 redirect.

---

## 3. Prerequisites

- **AWS CLI v2** configured with valid credentials (`aws configure` or AWS IAM Identity Center SSO).
- **AWS SAM CLI** (v1.110+).
- **Python 3.12** and **Node.js 18+**.
- **IAM Deployment Permissions:**
  - `cloudformation:*` (scoped to stack deployment)
  - `apigateway:*` (HTTP APIs)
  - `lambda:*` (functions, versions, event source mappings)
  - `dynamodb:*` (tables with on-demand billing and TTL)
  - `sqs:*` (standard queues, redrive policies)
  - `s3:*` (bucket creation, lifecycle configuration, encryption)
  - `logs:*` (log groups with 14-day retention)
  - `iam:PassRole`, `iam:CreateRole`, `iam:AttachRolePolicy` (scoped to SAM-generated Lambda execution roles)
- **Frontend Origin:** The exact origin where Vite or your static web host runs (e.g., `http://localhost:5173` or `https://your-frontend.example.com`).

---

## 4. SAM Build Instructions

Run from the repository root:

```powershell
# Step 1: Validate SAM template with linter
sam validate --lint

# Step 2: Build containerless arm64 artifacts
sam build
```

The SAM build processes `backend/requirements.txt`, bundles pure-Python dependencies into `.aws-sam/build/`, and generates CloudFormation template artifacts.

---

## 5. Deployment Instructions (Requires Explicit Approval)

When ready to deploy to your AWS account:

```powershell
sam deploy --guided
```

### Guided Prompts:
- **Stack Name:** `traceproof-research` (or your preferred name)
- **AWS Region:** `ap-south-1` (or your preferred region, e.g., `us-east-1`)
- **Parameter FrontendOrigin:** `http://localhost:5173` (or your production frontend URL)
- **Parameter MaxReceiveCount:** `3` (retries before moving to DLQ: 2 to 5)
- **Confirm changes before deploy:** `Y`
- **Allow SAM CLI IAM role creation:** `Y`
- **Disable rollback:** `N`
- **Save arguments to configuration file (samconfig.toml):** `Y`

After deployment succeeds, SAM outputs the API base URL:
```
Outputs:
--------------------------------------------------------------------------------------
Key                 ApiBaseUrl
Description         API Gateway HTTP API base URL
Value               https://<api-id>.execute-api.<region>.amazonaws.com
--------------------------------------------------------------------------------------
```

---

## 6. Frontend Environment Configuration

Copy `frontend/.env.example` to `frontend/.env.local` and set:

```dotenv
# AWS Mode
VITE_API_BASE_URL=https://<api-id>.execute-api.<region>.amazonaws.com
```

Restart the Vite development server:
```powershell
cd frontend
npm run dev
```

The frontend Settings tab will now display `AWS Cloud Serverless (AWS MODE)` with an operational status check.

---

## 7. Verification Steps

1. **Health Check:**
   ```powershell
   Invoke-RestMethod -Uri https://<api-id>.execute-api.<region>.amazonaws.com/health
   # Returns: {"name": "TraceProof API", "status": "running", "mode": "synthetic-aws", "service": "TraceProof API"}
   ```
2. **List Registered Resources:**
   ```powershell
   Invoke-RestMethod -Uri https://<api-id>.execute-api.<region>.amazonaws.com/resources
   # Auto-seeds DynamoDB ResourceTable and returns resources array
   ```
3. **Submit Simulated Deletion:**
   ```powershell
   $body = '{"resource_id": "student_001", "simulate_failure": false}'
   $req = Invoke-RestMethod -Method Post -Uri https://<api-id>.execute-api.<region>.amazonaws.com/deletion-requests -ContentType 'application/json' -Body $body
   $req.request_id
   # Returns HTTP 202 Accepted with status: "Pending"
   ```
4. **Poll Status:**
   ```powershell
   Invoke-RestMethod -Uri "https://<api-id>.execute-api.<region>.amazonaws.com/deletion-requests/$($req.request_id)"
   # Updates to status: "Verified" with targets_checked: 3
   ```
5. **Fetch Presigned Report:**
   ```powershell
   Invoke-WebRequest -Uri "https://<api-id>.execute-api.<region>.amazonaws.com/deletion-requests/$($req.request_id)/report" -MaximumRedirection 0
   # Returns HTTP 302 redirect with Location pointing to presigned S3 URL
   ```
6. **Run Experiment & Download Exports:**
   ```powershell
   $exp = Invoke-RestMethod -Method Post -Uri https://<api-id>.execute-api.<region>.amazonaws.com/experiments/run -ContentType 'application/json' -Body '{"num_resources":12,"trials":5,"random_seed":42}'
   Invoke-WebRequest -Uri "https://<api-id>.execute-api.<region>.amazonaws.com/experiments/$($exp.experiment_id)/aggregates.csv" -OutFile "aws-aggregates.csv"
   ```

---

## 8. CloudWatch Monitoring & Troubleshooting

- **Lambda Log Groups (14-Day Retention):**
  - `/aws/lambda/<stack>-ApiFunction-...`
  - `/aws/lambda/<stack>-WorkerFunction-...`
- **Inspecting Failed Jobs in DLQ:**
  ```powershell
  aws sqs get-queue-attributes --queue-url <dlq-url> --attribute-names ApproximateNumberOfMessages
  ```
- **Reviewing DLQ Messages:**
  View messages in the AWS SQS Console under `DeletionDeadLetterQueue` > `Send and receive messages` > `Poll for messages`.

---

## 9. Security & Least Privilege Audit

- **CORS:** Restricted to `FrontendOrigin`. Note: CORS is not authentication. The prototype HTTP API is unauthenticated for research evaluation.
- **IAM Policies:**
  - `ApiFunction`:
    - `dynamodb:GetItem`, `dynamodb:PutItem`, `dynamodb:Scan` on `ResourceTable`
    - `dynamodb:GetItem`, `dynamodb:PutItem`, `dynamodb:Scan`, `dynamodb:UpdateItem` on `RequestTable`
    - `dynamodb:GetItem`, `dynamodb:PutItem` on `ExperimentTable`
    - `sqs:SendMessage` on `DeletionQueue`
    - `s3:GetObject` on `reports/*` and `experiments/*`
    - `s3:PutObject` on `experiments/*`
  - `WorkerFunction`:
    - `dynamodb:Scan` on `ResourceTable`
    - `dynamodb:GetItem`, `dynamodb:UpdateItem` on `RequestTable`
    - `s3:PutObject` on `reports/*`
  - No wildcard admin policies or destructive cloud erasure permissions (`dynamodb:DeleteItem`, `s3:DeleteObject`) are granted.
- **S3 Bucket:** Private, `BlockPublicAcls`, `BlockPublicPolicy`, `IgnorePublicAcls`, `RestrictPublicBuckets`, AES-256 server-side encryption, 90-day lifecycle rule.

---

## 10. Cost Considerations & Teardown

### Cost Breakdown
- **API Gateway HTTP API:** Free tier covers 1M requests/month; then \$1.00 per million.
- **AWS Lambda:** 1M free requests and 3.2M seconds of compute/month under Free Tier.
- **Amazon DynamoDB:** Pay-per-request billing mode; \$0 for inactive tables.
- **Amazon SQS:** 1M requests/month free under Free Tier.
- **Amazon S3:** Standard storage rates for small report JSON files (< \$0.01/month).

### Teardown (Clean Deletion of All Resources)
To remove all AWS resources created by TraceProof:

```powershell
# Step 1: Delete CloudFormation Stack
sam delete --stack-name <stack-name> --region <region>

# Step 2: Empty and Delete Retained Report Bucket (Deliberately retained by DeletionPolicy)
aws s3 rm s3://<report-bucket-name>/ --recursive --region <region>
aws s3api delete-bucket --bucket <report-bucket-name> --region <region>
```
All tables, queues, functions, and log groups are automatically removed with the SAM stack.
