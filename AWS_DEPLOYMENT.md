# TraceProof AWS deployment

TraceProof uses AWS SAM because this prototype consists of a small set of Lambda functions and managed AWS resources. The AWS path processes only the repository's synthetic sample registry; it never calls DynamoDB `DeleteItem`, S3 `DeleteObject`, or another cloud deletion API. Local FastAPI remains available for development.

## Architecture and request flow

The React application sends requests to API Gateway HTTP API. The API Lambda validates a registered synthetic resource, stores a `Pending` request in DynamoDB, and enqueues its ID in SQS. The worker Lambda moves the request to `Processing`, runs the shared dependency-aware simulation on an in-memory copy, writes a JSON verification report to private S3, then records `Verified` or `Incomplete` and report metadata in DynamoDB. Worker processing errors are retried by SQS; after the configured receive limit, SQS moves the message to the DLQ and the request is marked `Failed` where possible. Duplicate deliveries skip terminal requests, and conditional status updates prevent completed results being overwritten.

The resource table is seeded idempotently from `backend/deletion_engine.py`. Every AWS report is labelled as simulation output. Report downloads go through an API endpoint that issues a five-minute presigned S3 redirect; AWS credentials are never sent to the browser.

Resources provisioned: API Gateway HTTP API, API and worker Lambdas, on-demand DynamoDB resource and request tables, encrypted SQS queue and DLQ, encrypted private S3 report bucket, and CloudWatch Lambda log groups with 14-day retention. The SQS event source is limited to two concurrent worker invocations. Lambda invocation/error/duration metrics are available through the standard CloudWatch Lambda namespace.

## Prerequisites

- AWS CLI configured for the intended account and region, preferably through IAM Identity Center/SSO or another short-lived role session.
- AWS SAM CLI and Python 3.12. Docker is optional for this code because the included Lambda dependency is pure Python; use SAM's container build if your local platform requires it.
- Permissions to create/update CloudFormation stacks, API Gateway HTTP APIs, Lambda functions and roles, DynamoDB tables, SQS queues/event source mappings, S3 buckets, and CloudWatch log groups. The deploying principal also needs `iam:PassRole` for SAM-created Lambda execution roles. Follow your organization's deployment policy and use a dedicated prototype account where possible.
- A deployed frontend origin, or `http://localhost:5173` for local frontend testing. Configure the exact origin with no path or trailing slash.

No AWS access keys or credentials belong in this repository or in Vite environment variables.

## Build and deploy manually

From the repository root:

```powershell
sam validate --lint
sam build
sam deploy --guided
```

During guided deployment, choose the AWS region and a stack name. Supply the exact frontend origin as the `FrontendOrigin` parameter, for example `https://your-frontend.example` (replace with your real origin). The receive limit defaults to 3 and can be set with `MaxReceiveCount` from 2 to 5. Review the generated change set and IAM capabilities before accepting deployment. Deployment is intentionally not run by this project workflow.

After deployment, copy the `ApiBaseUrl` stack output. The API is public and unauthenticated in this research prototype; a public production deployment needs an appropriate authentication and authorization strategy before use.

## Configure the frontend

Copy `frontend/.env.example` to `frontend/.env.local` and set:

```dotenv
VITE_API_BASE_URL=https://<api-id>.execute-api.<region>.amazonaws.com
```

Use the actual `ApiBaseUrl` output; do not include an endpoint path. Restart Vite after changing the environment. The checked-in default points to local FastAPI:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

In a second terminal, run the frontend:

```powershell
cd frontend
npm run dev
```

## Test the deployed workflow

1. Open the frontend and confirm the resource selector lists IDs/names returned by the API.
2. Submit a deletion request for `student_001`. The UI should show `Pending`, then poll until it displays `Verified` and the Requests/Reports pages show its JSON report link.
3. Submit another request with simulated failure enabled. The worker should finish as `Incomplete` and its report should show a remaining synthetic target.
4. Open the report link. It redirects to a private S3 object through a short-lived presigned URL.
5. Check `/deletion-requests` and `/experiments/compare`; optionally submit the experiment configuration to `/experiments/run`.

Test only synthetic IDs. No production storage target is implemented by the worker.

## Logs and failed jobs

Lambda logs are in CloudWatch Logs groups `/aws/lambda/<stack>-ApiFunction-...` and `/aws/lambda/<stack>-WorkerFunction-...`; use the names shown in the Lambda console if SAM's generated names differ. Log retention is 14 days. Lambda invocation, duration, throttling, and error metrics are available in CloudWatch under `AWS/Lambda`.

Inspect the SQS DLQ's ApproximateNumberOfMessagesVisible metric or view its messages in the SQS console. Do not purge the queue until messages have been reviewed. A request whose worker exhausts retries is marked `Failed` when possible, with the message retained in the DLQ for diagnosis.

## Security limits

- The HTTP API has no authorizer and the Lambda endpoints are publicly callable. CORS is restricted to the configured browser origin, but CORS is not authentication; add an appropriate auth mechanism before public production use.
- IAM roles are scoped to the prototype tables, queue, and `reports/` S3 prefix. Worker permissions do not include cloud deletion operations.
- S3 public access is blocked and reports use AES256 server-side encryption. Reports expire after 90 days. DynamoDB tables use AWS's default encryption at rest with an AWS-owned key; no customer-managed KMS key is provisioned.
- Synthetic results demonstrate behavior in a controlled graph, not physical erasure from AWS storage or every system that may hold a copy.

## Costs and teardown

This stack is small but is not guaranteed to be free. Potential charges include API Gateway requests, Lambda invocations and CloudWatch logs, DynamoDB on-demand reads/writes and stored data, SQS requests, S3 storage and requests, and the SAM deployment artifact bucket. Check current costs in AWS Billing and Cost Management, Cost Explorer, and the Free Tier page for the selected account/region; use AWS Budgets for alerts. The report bucket lifecycle expires reports after 90 days, but CloudWatch log retention and any SAM artifact bucket should also be reviewed.

To remove the stack after reviewing its data:

```powershell
sam delete --stack-name <stack-name> --region <region>
```

The report bucket is deliberately retained by CloudFormation to prevent accidental loss of reports. Find its name in stack outputs, inspect it, then empty and remove it explicitly if no longer needed:

```powershell
aws s3 ls s3://<report-bucket-name>/ --recursive --region <region>
aws s3 rm s3://<report-bucket-name>/ --recursive --region <region>
aws s3api delete-bucket --bucket <report-bucket-name> --region <region>
```

The bucket is not versioned, so the recursive removal deletes its current report objects. Confirm the bucket name and contents before running removal commands. The DynamoDB tables, queues, functions, and 14-day CloudWatch log groups are stack-managed and normally removed with the stack. SAM's deployment artifact bucket may be shared with other stacks; inspect it separately and do not remove it without confirming ownership and contents.
