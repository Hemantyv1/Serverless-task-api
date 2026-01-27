# Serverless Task Management API

A production-ready, serverless REST API built with AWS Lambda, API Gateway, and DynamoDB.

## Features

- CRUD operations for task management
- DynamoDB with on-demand capacity
- API Gateway REST API
- CloudWatch monitoring
- Infrastructure as Code with AWS SAM

## Prerequisites

- AWS Account
- AWS CLI configured
- AWS SAM CLI installed
- Python 3.11+
- Git

## Quick Start

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

### 3. Build

```bash
sam build
```

### 4. Deploy

```bash
sam deploy --guided
```

## API Endpoints

Base URL: `https://{api-id}.execute-api.{region}.amazonaws.com/{environment}`

### Create Task
```http
POST /tasks
Content-Type: application/json

{
  "title": "Task title",
  "description": "Task description",
  "priority": "high",
  "status": "pending",
  "dueDate": "2025-01-31",
  "tags": ["tag1", "tag2"]
}
```

### Get All Tasks
```http
GET /tasks
```

Query Parameters:
- `status`: Filter by status (pending/in-progress/completed)
- `priority`: Filter by priority (low/medium/high)

### Get Single Task
```http
GET /tasks/{taskId}
```

### Update Task
```http
PUT /tasks/{taskId}
Content-Type: application/json

{
  "status": "completed",
  "priority": "low"
}
```

### Delete Task
```http
DELETE /tasks/{taskId}
```

## Project Structure

```
serverless-task-api/
├── src/handlers/          # Lambda functions
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── template.yaml          # AWS SAM template
└── requirements.txt       # Python dependencies
```
