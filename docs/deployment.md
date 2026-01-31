# Deployment Guide

Complete guide for deploying and managing your Serverless Telegram Bot.

## Prerequisites

Before you begin, ensure you have:

- ✅ **AWS Account** ([Create one for free](https://aws.amazon.com/free/))
- ✅ **AWS CLI** installed and configured (`aws configure`)
- ✅ **Node.js** (v18+) and **Docker** (required for CDK Lambda bundling)
- ✅ **Python 3.13+** installed
- ✅ **Telegram Bot Token** (get it from [@BotFather](https://t.me/botfather))

### Setting Up AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter default output format (json)
```

### Installing Node.js and Docker

- **Node.js**: Download from [nodejs.org](https://nodejs.org/) (v18+)
- **Docker**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Project Structure

```
serverless-tg-bot-starter/
├── infra/                    # CDK infrastructure code
│   ├── app.py               # CDK app entrypoint
│   └── stack.py             # Main stack definition
├── src/
│   ├── receiver/            # Receiver Lambda
│   │   └── main.py          # Webhook receiver logic
│   └── worker/              # Worker Lambda
│       ├── handlers.py      # YOUR CODE GOES HERE ✨
│       ├── main.py          # Lambda entrypoint
│       └── requirements.txt # Lambda dependencies
├── .github/workflows/       # CI/CD workflows
├── cdk.json                 # CDK configuration
├── pyproject.toml           # Python project config
└── README.md                # Main documentation
```

## Manual Deployment

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/serverless-tg-bot-starter.git
cd serverless-tg-bot-starter
```

### 2. Install Dependencies

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_SECRET_TOKEN=your_secret_token_here
```

**Important:** Generate a strong random string for `TELEGRAM_WEBHOOK_SECRET_TOKEN` (e.g., use `openssl rand -hex 32`).

### 4. Bootstrap CDK (First Time Only)

```bash
cdk bootstrap
```

### 5. Deploy Infrastructure

```bash
# Deploy to dev environment
cdk deploy -c env=dev

# Or deploy to production
cdk deploy -c env=prod
```

After deployment, note the **API Gateway URL** from the output:
```
Outputs:
TelegramBotStack-devWebhookApiUrl = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com
```

### 6. Configure Telegram Webhook

Use the API Gateway URL to set your webhook:

```bash
# Replace YOUR_API_URL and YOUR_SECRET_TOKEN
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "YOUR_API_URL/webhook",
    "secret_token": "YOUR_SECRET_TOKEN"
  }'
```

### 7. Verify Deployment

Send a message to your bot on Telegram. You should receive a response!

## Deployment (CI/CD)

This template includes a **GitHub Actions workflow** (`.github/workflows/deploy.yml`) for automated deployments.

### Automatic Deployment

- **Push to `main`**: Automatically deploys to `dev` environment
- **Manual Trigger**: Use GitHub Actions UI to deploy to `dev` or `prod`

### Required GitHub Secrets

Configure these secrets in your GitHub repository:

- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `DEV_TELEGRAM_BOT_TOKEN` - Bot token for dev environment
- `DEV_TELEGRAM_WEBHOOK_SECRET_TOKEN` - Webhook secret for dev
- `PROD_TELEGRAM_BOT_TOKEN` - Bot token for production (if using prod)
- `PROD_TELEGRAM_WEBHOOK_SECRET_TOKEN` - Webhook secret for production

### Setting Up GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret listed above

### Manual Deployment via CI/CD

1. Go to **Actions** tab in your GitHub repository
2. Select **Deploy to AWS** workflow
3. Click **Run workflow**
4. Choose environment (`dev` or `prod`)
5. Click **Run workflow**

## Monitoring & Debugging

### CloudWatch Logs

View logs for your Lambda functions:

- **Receiver Lambda**: `/aws/lambda/tg-dev-receiver`
- **Worker Lambda**: `/aws/lambda/tg-dev-worker`

#### Accessing Logs via AWS Console

1. Go to [AWS CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)
2. Navigate to **Logs** → **Log groups**
3. Search for your Lambda function name
4. Click on the log group to view recent logs

#### Accessing Logs via AWS CLI

```bash
# View Receiver Lambda logs
aws logs tail /aws/lambda/tg-dev-receiver --follow

# View Worker Lambda logs
aws logs tail /aws/lambda/tg-dev-worker --follow
```

### Dead Letter Queue

Failed messages automatically go to the DLQ. Check it in AWS Console if messages aren't being processed.

#### Checking DLQ via AWS Console

1. Go to [AWS SQS Console](https://console.aws.amazon.com/sqs/)
2. Find the queue named `tg-dev-updates-dlq`
3. Click on it to view messages
4. Messages in DLQ indicate processing failures

#### Common DLQ Scenarios

- **Lambda timeout**: Increase timeout in `infra/stack.py`
- **DynamoDB errors**: Check IAM permissions
- **Telegram API errors**: Check bot token and API limits

### Common Issues

#### 1. Webhook returns 403

**Problem**: Telegram webhook requests are being rejected.

**Solution**:
- Check that `TELEGRAM_WEBHOOK_SECRET_TOKEN` matches your webhook configuration
- Verify the secret token in your `.env` file matches the one used in `setWebhook` call

#### 2. Messages not processed

**Problem**: Messages are received but not processed by Worker Lambda.

**Solution**:
- Check Worker Lambda logs in CloudWatch
- Check DLQ for failed messages
- Verify SQS event source mapping is configured correctly

#### 3. DynamoDB errors

**Problem**: Database operations are failing.

**Solution**:
- Verify IAM permissions in `infra/stack.py`
- Check table name matches environment variable
- Ensure table exists (should be created automatically by CDK)

#### 4. Lambda timeout

**Problem**: Lambda functions are timing out.

**Solution**:
- Increase timeout in `infra/stack.py` (default is 30s for receiver, 60s for worker)
- Optimize your handler code
- Check for external API calls that might be slow

#### 5. CDK deployment fails

**Problem**: `cdk deploy` command fails.

**Solution**:
- Ensure Docker is running (required for Lambda bundling)
- Check AWS credentials are configured correctly
- Verify all environment variables are set
- Check CDK bootstrap was completed

## Security Best Practices

- ✅ Secret Token validation for webhook requests
- ✅ Least-privilege IAM policies
- ✅ Environment variables for sensitive data (consider AWS Secrets Manager for production)
- ✅ SQS DLQ for error handling
- ✅ Input validation and error handling

## Updating Your Bot

### After Code Changes

1. Make your changes in `src/worker/handlers.py`
2. Commit and push to trigger CI/CD, or manually deploy:
   ```bash
   cdk deploy -c env=dev
   ```

### Updating Infrastructure

1. Modify `infra/stack.py` as needed
2. Deploy changes:
   ```bash
   cdk deploy -c env=dev
   ```

## Troubleshooting Tips

- Always check CloudWatch Logs first
- Use AWS Console to verify resource states
- Test webhook locally using tools like ngrok before deploying
- Keep your `.env` file secure and never commit it to git
