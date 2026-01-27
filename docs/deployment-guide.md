# Deployment Guide

Complete step-by-step guide to deploy the Serverless Task Management API to AWS.

## Prerequisites

Before you begin, ensure you have:

### 1. AWS Account
- Sign up at https://aws.amazon.com/free/
- Free tier includes:
  - 1M Lambda requests/month
  - 1M API Gateway requests/month
  - 25GB DynamoDB storage

### 2. Install AWS CLI
```bash
# macOS
brew install awscli

# Windows
choco install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

Verify installation:
```bash
aws --version
```

### 3. Configure AWS Credentials
```bash
aws configure
```

Enter:
- AWS Access Key ID: [Your access key]
- AWS Secret Access Key: [Your secret key]
- Default region: `us-east-1` (or your preferred region)
- Default output format: `json`

**How to get credentials:**
1. Go to AWS Console → IAM → Users → Your User
2. Security credentials → Create access key
3. Select "Command Line Interface (CLI)"
4. Save the credentials securely

### 4. Install AWS SAM CLI
```bash
# macOS
brew install aws-sam-cli

# Windows
choco install aws-sam-cli

# Linux
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install
```

Verify installation:
```bash
sam --version
```

### 5. Install Python 3.11+
```bash
python3 --version
```

## Deployment Steps

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/serverless-task-api.git
cd serverless-task-api

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Run Tests (Optional but Recommended)
```bash
# Run all tests
pytest tests/ -v

# Check code coverage
pytest tests/ --cov=src/handlers --cov-report=term
```

### Step 3: Update Configuration

Edit `samconfig.toml`:
```toml
parameter_overrides = "Environment=dev AlertEmail=YOUR-EMAIL@example.com"
```

**Important**: Replace `YOUR-EMAIL@example.com` with your actual email address for alerts.

### Step 4: Build the Application
```bash
sam build
```

This command:
- ✅ Validates your SAM template
- ✅ Resolves dependencies
- ✅ Prepares Lambda function packages
- ✅ Creates a `.aws-sam` directory with build artifacts

Expected output:
```
Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml
```

### Step 5: Deploy to AWS

#### First-Time Deployment (Guided)
```bash
sam deploy --guided
```

You'll be prompted for:
```
Stack Name [task-api-dev]: task-api-dev
AWS Region [us-east-1]: us-east-1
Parameter Environment [dev]: dev
Parameter AlertEmail [your-email@example.com]: your-actual-email@example.com
#Shows you resources changes to be deployed
Confirm changes before deploy [Y/n]: Y
#SAM needs permission to be able to create roles to connect to the resources
Allow SAM CLI IAM role creation [Y/n]: Y
#Preserves the state of previously provisioned resources
Disable rollback [y/N]: N
Save arguments to configuration file [Y/n]: Y
SAM configuration file [samconfig.toml]: samconfig.toml
SAM configuration environment [default]: default
```

#### Subsequent Deployments
```bash
sam build && sam deploy
```

### Step 6: Verify Deployment

After successful deployment, you'll see:
```
CloudFormation outputs from deployed stack
-------------------------------------------------------------------
Outputs
-------------------------------------------------------------------
Key                 ApiUrl
Description         API Gateway endpoint URL
Value               https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev
-------------------------------------------------------------------
```

**Save this API URL** - you'll need it for testing!

### Step 7: Test the API

#### Using curl
```bash
# Set your API URL
export API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/dev"

# Create a task
curl -X POST $API_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test deployment",
    "description": "Verify API is working",
    "priority": "high"
  }'

# List all tasks
curl $API_URL/tasks

# Get specific task (replace with actual taskId from previous response)
curl $API_URL/tasks/{taskId}

# Update task
curl -X PUT $API_URL/tasks/{taskId} \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Delete task
curl -X DELETE $API_URL/tasks/{taskId}
```

#### Using Postman
1. Download Postman: https://www.postman.com/downloads/
2. Import this collection: [Link to Postman collection]
3. Set the `API_URL` variable
4. Test all endpoints

### Step 8: Configure Email Notifications

After deployment:
1. Check your email for "AWS Notification - Subscription Confirmation"
2. Click the confirmation link
3. You'll now receive alerts for:
   - High error rates
   - High latency
   - Lambda errors
   - DynamoDB throttling

### Step 9: View CloudWatch Dashboard

1. Go to AWS Console → CloudWatch → Dashboards
2. Select `dev-task-api-dashboard`
3. View real-time metrics:
   - Request count
   - Error rates
   - API latency
   - Lambda performance
   - DynamoDB capacity usage

## Multi-Environment Deployment

### Development Environment
```bash
sam build
sam deploy --config-env default
```

### Production Environment
```bash
sam build
sam deploy --config-env prod
```

Edit `samconfig.toml` to add staging:
```toml
[staging.deploy.parameters]
stack_name = "task-api-staging"
parameter_overrides = "Environment=staging AlertEmail=your-email@example.com"
```

## Troubleshooting

### Issue: "Unable to locate credentials"
**Solution:**
```bash
aws configure
# Enter your credentials
```

### Issue: "Stack already exists"
**Solution:**
```bash
# Delete the existing stack
aws cloudformation delete-stack --stack-name task-api-dev

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name task-api-dev

# Redeploy
sam build && sam deploy
```

### Issue: "No changes to deploy"
**Solution:**
- This is normal if you haven't made any changes
- Force redeployment: Add `--force-upload` to deploy command

### Issue: Lambda timeout errors
**Solution:**
- Check CloudWatch Logs: AWS Console → CloudWatch → Log Groups
- Look for `/aws/lambda/dev-create-task`
- Increase timeout in `template.yaml` under `Globals.Function.Timeout`

### Issue: DynamoDB throttling
**Solution:**
- Enable on-demand capacity (already enabled in template)
- Check CloudWatch metrics for read/write capacity
- Review query patterns for optimization

## Updating the Application

### Code Changes
```bash
# 1. Make your changes to Lambda functions
# 2. Run tests
pytest tests/ -v

# 3. Build and deploy
sam build && sam deploy
```

### Infrastructure Changes
```bash
# 1. Update template.yaml
# 2. Validate template
sam validate

# 3. Deploy changes
sam build && sam deploy
```

## Monitoring Post-Deployment

### Check Application Logs
```bash
# View logs for a specific function
sam logs --stack-name task-api-dev --tail

# View logs for create function
sam logs -n CreateTaskFunction --stack-name task-api-dev --tail
```

### Monitor Costs
1. Go to AWS Console → Billing Dashboard
2. View cost breakdown by service
3. Set up billing alerts

### Set Budget Alerts
```bash
# Create a $10 budget with 80% alert
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

## Cleanup / Deletion

To delete all resources and avoid charges:

```bash
# Delete the CloudFormation stack
aws cloudformation delete-stack --stack-name task-api-dev

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name task-api-dev

# Verify deletion
aws cloudformation describe-stacks --stack-name task-api-dev
# Should return: "Stack with id task-api-dev does not exist"
```

**Note**: This will permanently delete:
- All Lambda functions
- API Gateway
- DynamoDB table and all data
- CloudWatch logs (after retention period)
- SNS topics
- IAM roles

## CI/CD Setup (GitHub Actions)

### Step 1: Add AWS Credentials to GitHub Secrets
1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
   - `ALERT_EMAIL`: Email for notifications

### Step 2: Enable GitHub Actions
1. Push code to `main` or `develop` branch
2. GitHub Actions will automatically:
   - Run tests
   - Build application
   - Deploy to AWS

### Step 3: View Deployment Status
- Go to repository → Actions tab
- See build and deployment progress

## Best Practices

### Security
- ✅ Never commit AWS credentials to Git
- ✅ Use IAM roles with minimum permissions
- ✅ Enable MFA on AWS account
- ✅ Rotate access keys regularly
- ✅ Use AWS Secrets Manager for sensitive data

### Cost Optimization
- ✅ Monitor AWS Free Tier usage
- ✅ Set up billing alerts at $5, $10, $20
- ✅ Delete unused stacks promptly
- ✅ Use CloudWatch log retention (30 days)

### Development Workflow
- ✅ Test locally with `sam local`
- ✅ Deploy to dev environment first
- ✅ Run integration tests
- ✅ Deploy to prod only after validation

## Next Steps

After successful deployment:

1. **Add Custom Domain**: Configure Route53 and API Gateway custom domain
2. **API Keys**: Enable API key requirement in production
3. **Rate Limiting**: Add usage plans for API throttling
4. **Caching**: Enable API Gateway caching for frequently accessed data
5. **WAF**: Add AWS WAF for DDoS protection
6. **Cognito**: Implement user authentication

## Support

If you encounter issues:
1. Check CloudWatch Logs
2. Review AWS CloudFormation events
3. Open an issue on GitHub
4. Contact: your.email@example.com

## Resources

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
