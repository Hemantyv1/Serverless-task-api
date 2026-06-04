# Serverless Task Management API

A production-ready serverless REST API for managing tasks, built with **AWS Lambda**, **API Gateway**, and **DynamoDB** and deployed using **AWS SAM**.

## Features

- CRUD operations for tasks (create, read, update, delete)
- DynamoDB table with on-demand capacity and a status index
- API Gateway REST API with CORS enabled
- CloudWatch logging, metrics, and alarms (via CloudFormation/SAM)
- Infrastructure as Code with AWS SAM and GitHub Actions CI/CD

## Tech Stack

- **Language**: Python 3.11
- **Compute**: AWS Lambda
- **API Layer**: Amazon API Gateway (REST)
- **Database**: Amazon DynamoDB (on‑demand, GSI on `status`/`createdAt`)
- **IaC**: AWS SAM (`template.yaml`)
- **CI/CD**: GitHub Actions (test, lint, deploy)

## Getting Started

### Prerequisites

- AWS account
- AWS CLI configured (`aws configure`)
- AWS SAM CLI installed
- Python 3.11+
- Git

### 1. Clone and Install

```bash
git clone https://github.com/YOUR-USERNAME/serverless-task-api.git
cd serverless-task-api
pip install -r requirements.txt
```

### 2. Run Tests

```bash
pytest tests/ -v
```

### 3. Build the Application

```bash
sam build
```

### 4. Deploy to AWS

```bash
sam deploy --guided
```

## Security & Reliability

- **Security**
  - All data access is restricted via **least-privilege IAM policies** attached to each Lambda function (CRUD or read-only for the specific DynamoDB table).
  - The DynamoDB table is configured with **encryption at rest** enabled and the API is exposed only over **HTTPS** via API Gateway.
  - Error handlers log full exception details to CloudWatch but return **generic error messages** to clients to avoid leaking internal details.
  - CORS is enabled for rapid testing and demos; in a production setup you can restrict allowed origins to your frontend domains.
  - The architecture is designed to support adding authentication (e.g. API keys or Amazon Cognito authorizers) without code changes to the handlers.

- **Reliability & Operations**
  - CloudWatch metrics, logs, and alarms are defined to monitor **error rates, latency, and Lambda/DynamoDB health**, with optional SNS email alerts.
  - The API scales automatically using **Lambda concurrency** and **DynamoDB on‑demand capacity**; there are no servers to manage.
  - A GitHub Actions workflow runs **tests, linting, and SAM deployments** on every push to `develop` (dev) and `main` (prod), providing a simple CI/CD pipeline.
