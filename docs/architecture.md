# Architecture Documentation

## System Overview

The Serverless Task Management API is built on AWS serverless services, providing a highly available, scalable, and cost-effective solution for task management.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                           Client Layer                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│  │ Web App │  │ Mobile  │  │   CLI   │  │  Other  │                │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘                │
└───────┼───────────┼────────────┼───────────┼──────────────────────┘
        │           │            │           │
        └───────────┴────────────┴───────────┘
                    │
        ┌───────────▼────────────┐
        │    HTTPS / TLS 1.3     │
        └───────────┬────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────────┐
│                       API Gateway Layer                              │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │  Amazon API Gateway (REST API)                          │        │
│  │  • Request validation                                   │        │
│  │  • Rate limiting & throttling                          │        │
│  │  • CORS configuration                                   │        │
│  │  • CloudWatch logging                                   │        │
│  │  • X-Ray tracing                                        │        │
│  └──────────┬──────────────────────────────────────────────┘        │
└─────────────┼────────────────────────────────────────────────────────┘
              │
     ┌────────┴────────┐
     │                 │
┌────▼──────┐    ┌────▼──────┐
│  Lambda   │    │  Lambda   │
│  Proxy    │    │  Proxy    │
│  Auth     │    │  Route    │
└───────────┘    └────┬──────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼─────┐ ┌───▼──────┐ ┌──▼───────┐
    │  Create  │ │   Get    │ │  Update  │
    │  Lambda  │ │  Lambda  │ │  Lambda  │
    └────┬─────┘ └───┬──────┘ └──┬───────┘
         │           │            │
         └───────────┼────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────────┐
│                     Database Layer                                  │
│  ┌──────────────────────────────────────────────────────┐          │
│  │  Amazon DynamoDB                                     │          │
│  │  • On-demand capacity (auto-scaling)                │          │
│  │  • Global secondary indexes                         │          │
│  │  • Point-in-time recovery                           │          │
│  │  • Encryption at rest                               │          │
│  │  • DynamoDB Streams (for future features)           │          │
│  └──────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────────┐
│                  Monitoring & Alerting Layer                        │
│  ┌─────────────────────────┐  ┌─────────────────────────┐         │
│  │   Amazon CloudWatch     │  │   Amazon SNS            │         │
│  │  • Custom metrics       │  │  • Email notifications  │         │
│  │  • Log aggregation      │  │  • Alert subscribers    │         │
│  │  • Dashboards          │  │  • Incident response    │         │
│  │  • Alarms              │  │                         │         │
│  └─────────────────────────┘  └─────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Gateway

**Purpose**: Entry point for all HTTP requests

**Key Features**:
- REST API with resource-based routing
- Request/response transformation
- API versioning support
- Built-in DDoS protection
- CloudWatch logging and metrics

**Configuration**:
```yaml
Cors:
  AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
  AllowOrigin: "'*'"  # Restrict in production
TracingEnabled: true
```

**Security**:
- HTTPS only (TLS 1.2+)
- Optional API key authentication
- IAM authorization available
- Request throttling per client

### 2. Lambda Functions

**Purpose**: Serverless compute for business logic

**Functions**:

#### CreateTaskFunction
- **Trigger**: POST /tasks
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Concurrent executions**: 1000 (default)
- **Responsibilities**:
  - Validate input
  - Generate UUID for taskId
  - Write to DynamoDB
  - Return created task

#### GetTaskFunction
- **Triggers**: 
  - GET /tasks (list all)
  - GET /tasks/{taskId} (single task)
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Responsibilities**:
  - Query DynamoDB
  - Filter results
  - Return task(s)

#### UpdateTaskFunction
- **Trigger**: PUT /tasks/{taskId}
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Responsibilities**:
  - Validate task exists
  - Update specified fields
  - Return updated task

#### DeleteTaskFunction
- **Trigger**: DELETE /tasks/{taskId}
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Responsibilities**:
  - Verify task exists
  - Delete from DynamoDB
  - Return confirmation

**Best Practices Implemented**:
- ✅ Separate function per operation (microservices)
- ✅ Environment variables for configuration
- ✅ Structured logging for debugging
- ✅ Error handling with appropriate status codes
- ✅ CORS headers in all responses

#### Authentication (Optional Extension)

- The API is intentionally left **unauthenticated for demo and portfolio use**, so it can be exercised directly from tools like curl and Postman.
- The design assumes that production environments can enable one of the following without changing handler code:
  - **API keys + usage plans** on API Gateway (per‑client rate limiting and metering).
  - **Amazon Cognito user pools** with a JWT authorizer attached to the `TaskApi`.
  - **IAM authorization** for internal or CLI-only access.
- When auth is enabled at API Gateway, the Lambda handlers remain focused purely on business logic and trust the upstream identity/context provided in the event.

### 3. DynamoDB

**Purpose**: NoSQL database for task storage

**Table Design**:
```
Primary Key: taskId (String, HASH)
Attributes:
  - taskId: String (UUID)
  - title: String
  - description: String
  - status: String
  - priority: String
  - createdAt: String (ISO 8601)
  - updatedAt: String (ISO 8601)
  - dueDate: String (ISO 8601)
  - tags: List
```

**Global Secondary Index**:
```
Index Name: status-index
Partition Key: status (String)
Sort Key: createdAt (String)
```

**Capacity Mode**: On-demand
- Auto-scales based on traffic
- No capacity planning needed
- Pay per request
- Cost-effective for variable workloads

**Features Enabled**:
- ✅ Point-in-Time Recovery (PITR)
- ✅ Encryption at rest (AWS managed keys)
- ✅ DynamoDB Streams
- ✅ Auto-scaling

**Query Patterns**:
1. Get task by ID: `GetItem(taskId)`
2. List all tasks: `Scan()`
3. List by status: `Query(status-index, status=pending)`
4. List by date range: `Query(status-index, status, createdAt between)`

### 4. CloudWatch

**Purpose**: Monitoring, logging, and alerting

**Log Groups**:
- `/aws/lambda/dev-create-task`
- `/aws/lambda/dev-get-task`
- `/aws/lambda/dev-update-task`
- `/aws/lambda/dev-delete-task`
- `/aws/apigateway/dev-task-api`

**Custom Metrics**:
- Request count per endpoint
- Success/error rates
- Response times (p50, p95, p99)
- DynamoDB capacity consumption

**Alarms Configured**:

| Alarm | Threshold | Action |
|-------|-----------|--------|
| High Error Rate | >5% errors | Send SNS alert |
| High Latency | >1000ms avg | Send SNS alert |
| Lambda Errors | >5 in 5 min | Send SNS alert |
| DB Throttling | Any throttle | Send SNS alert |

**Dashboard Widgets**:
1. API Request Count (5XX, 4XX, 2XX)
2. API Latency Distribution
3. Lambda Invocations & Errors
4. DynamoDB Read/Write Capacity

### 5. SNS

**Purpose**: Alert notifications

**Topic**: `{environment}-task-api-alerts`
**Subscribers**: Email addresses for on-call team
**Triggered By**: CloudWatch alarms

## Data Flow

### Create Task Flow
```
1. Client sends POST /tasks with JSON body
2. API Gateway validates request format
3. API Gateway invokes CreateTaskFunction
4. Lambda function:
   a. Parses request body
   b. Validates required fields
   c. Generates UUID for taskId
   d. Adds timestamps
   e. Writes to DynamoDB
5. DynamoDB confirms write
6. Lambda returns 201 Created with task object
7. API Gateway forwards response to client
8. CloudWatch logs the transaction
```

### Get Task Flow
```
1. Client sends GET /tasks/{taskId}
2. API Gateway routes to GetTaskFunction
3. Lambda function:
   a. Extracts taskId from path
   b. Queries DynamoDB
   c. Returns task if found
4. If not found, returns 404
5. If found, returns 200 with task object
6. CloudWatch logs the transaction
```

## Security Architecture

### IAM Roles & Policies

**Lambda Execution Role**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/tasks-table"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

**Principle of Least Privilege**:
- Each Lambda function has minimum required permissions
- No wildcard (*) permissions
- Resource-specific ARNs
- No cross-account access

### Encryption

**Data in Transit**:
- HTTPS only (enforced by API Gateway)
- TLS 1.2 or higher
- Strong cipher suites only

**Data at Rest**:
- DynamoDB encryption enabled
- AWS-managed keys (KMS)
- CloudWatch Logs encrypted

## Scalability

### Horizontal Scaling
- **Lambda**: Auto-scales to 1000 concurrent executions
- **DynamoDB**: On-demand capacity adjusts automatically
- **API Gateway**: No scaling configuration needed

### Vertical Scaling
- Lambda memory can be increased (up to 10GB)
- Timeout can be extended (up to 15 minutes)

### Performance Optimizations
1. **Cold Start Mitigation**:
   - Provisioned concurrency for critical functions
   - Minimize deployment package size
   - Use Python 3.11 (faster startup)

2. **Database Optimization**:
   - Global Secondary Indexes for common queries
   - Batch operations for bulk updates
   - DynamoDB DAX for caching (optional)

3. **API Gateway**:
   - Response caching (up to 1 hour TTL)
   - Request throttling per client
   - Burst handling

## High Availability

### Multi-AZ Deployment
- Lambda automatically deploys across AZs
- DynamoDB replicates across 3 AZs
- API Gateway is multi-AZ by default

### Disaster Recovery
- **RTO**: < 1 hour (redeploy with SAM)
- **RPO**: 0 (DynamoDB PITR for point-in-time recovery)
- **Backup Strategy**: Continuous backups with PITR

### Failure Handling
1. **Lambda Retries**: Automatic retry with exponential backoff
2. **DLQ**: Dead Letter Queue for failed invocations
3. **Circuit Breaker**: API throttling prevents cascading failures

## Cost Analysis

### Monthly Cost Breakdown (Assumptions: 100K requests/month)

| Service | Usage | Free Tier | Cost |
|---------|-------|-----------|------|
| Lambda | 100K invocations × 512MB × 1s | 1M requests | $0.00 |
| API Gateway | 100K requests | 1M requests | $0.00 |
| DynamoDB | 100K reads/writes, 1GB storage | 25GB + 200M requests | $0.00 |
| CloudWatch | 5GB logs, 10 alarms | 5GB logs, 10 alarms | $0.00 |
| **Total** | | | **$0.00** |

### Cost Optimization Strategies
1. **On-Demand Pricing**: Only pay for actual usage
2. **Log Retention**: 30-day retention (vs. infinite)
3. **Reserved Capacity**: Not needed with on-demand
4. **Scheduled Scaling**: N/A for serverless

## Monitoring Strategy

### Golden Signals

1. **Latency**: p50, p95, p99 response times
2. **Traffic**: Requests per second
3. **Errors**: Error rate percentage
4. **Saturation**: Lambda concurrent executions, DynamoDB capacity

### SLOs (Service Level Objectives)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Availability | 99.9% | API uptime |
| Latency (p95) | < 500ms | API response time |
| Error Rate | < 0.1% | 5XX errors |
| Data Durability | 99.999999999% | DynamoDB guarantee |

### Alert Escalation

1. **Warning** (Yellow): Email to team
2. **Critical** (Red): Email + PagerDuty/on-call
3. **Emergency** (Purple): Immediate escalation to senior engineers

## Future Enhancements

### Phase 2
- [ ] Add Cognito for user authentication
- [ ] Implement WebSocket API for real-time updates
- [ ] Add Lambda@Edge for global CDN
- [ ] Enable X-Ray distributed tracing

### Phase 3
- [ ] Multi-region deployment
- [ ] GraphQL API support
- [ ] Machine learning for task recommendations
- [ ] Advanced analytics with QuickSight

### Phase 4
- [ ] Microservices decomposition
- [ ] Event-driven architecture with EventBridge
- [ ] Service mesh with App Mesh
- [ ] Kubernetes migration (EKS)

## References

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Serverless Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/)
