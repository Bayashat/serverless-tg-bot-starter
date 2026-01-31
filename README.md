[ 🇬🇧 English ](README.md) | [ 🇰🇿 Қазақша ](docs/README_KK.md) | [ 🇷🇺 Русский ](docs/README_RU.md)

# 🚀 Serverless Telegram Bot Starter

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![AWS CDK](https://img.shields.io/badge/AWS_CDK-v2-orange.svg)](https://docs.aws.amazon.com/cdk/)
[![Dependency Manager](https://img.shields.io/badge/uv-managed-purple)](https://github.com/astral-sh/uv)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A production-ready template for hosting Telegram Bots on AWS using Serverless architecture. Built with AWS CDK (Python), designed for developers transitioning from traditional VPS to Cloud Native.

## Why This Template?


### Async Architecture: The Game Changer

Unlike traditional synchronous Lambda functions that timeout after 15 minutes, this template uses an **asynchronous, event-driven architecture**:

```
Telegram → API Gateway → Receiver Lambda → SQS Queue → Worker Lambda → DynamoDB + Telegram API
```

**Key Benefits:**

- ✅ **No Timeouts**: Worker Lambda processes messages asynchronously.
- ✅ **Scalable**: Automatically handles traffic spikes (e.g., thousands of users).
- ✅ **Resilient**: Dead Letter Queue (DLQ) captures failed messages.
- ✅ **Cost-Effective**: Pay only for what you use (likely FREE for most bots).

### Stop Paying for Idle VPS!

Traditional VPS costs $5-10/month regardless of traffic. With Serverless, you pay per request. For most hobby bots and startups, **your AWS bill will be $0.00** thanks to the generous Free Tier.

## 🌟 Real-World Example

Curious about how this looks in production?

Check out the **[Zerde Bot Repository](https://github.com/Bayashat/zerde-serverless-bot)**.
It's an **open-source** anti-spam bot built with this exact template, currently serving a **900+ member IT community**.

**Status:** Running 24/7 on AWS Free Tier ($0 cost).

## Architecture

![Serverless Bot Architecture](assets/architecture.png)

## Cost Estimation

### Is it expensive? No. It's likely FREE.

| Resource | Free Tier Limit (Monthly) | Estimated Bot Capacity |
|----------|---------------------------|------------------------|
| AWS Lambda | 400,000 GB-seconds | ~3,000,000 messages |
| API Gateway | 300 million requests (1st yr) | Unlimited for bots |
| DynamoDB | 25 GB Storage | Millions of user records |
| SQS | 1 Million Requests | ~500,000 messages |

**Verdict:** For most startups and hobby bots, your AWS bill will be **$0.00**.

## 🛠️ Super Quick Start

### Prerequisites

- **[AWS CLI](https://aws.amazon.com/cli/)** configured with your account.
- **[Docker](https://www.docker.com/)** running (required for CDK bundling).
- **[uv](https://github.com/astral-sh/uv)** installed (The modern Python package manager).

### 1. Initialize Project

```bash
# Clone the repository
git clone https://github.com/Bayashat/serverless-tg-bot-starter.git
cd serverless-tg-bot-starter

# Install dependencies strictly from lockfile
uv sync
```

### 2. Configure Environment

```bash
# Generate a secure secret token and create .env
echo "TELEGRAM_BOT_TOKEN=your_token_from_botfather" > .env

# Generate a secure secret token for the webhook
echo "TELEGRAM_WEBHOOK_SECRET_TOKEN=$(openssl rand -hex 32)" >> .env
```

### 3. Deploy (Local Dev)

```bash
# Navigate to the infra directory
cd infra

# Bootstrap CDK (only needed once per AWS account/region)
uv run cdk bootstrap

# Deploy to Development environment
uv run cdk deploy -c env=dev
```

### 4. Connect Webhook

Locate the WebhookApiUrl in the terminal output (e.g., https://xyz.execute-api.eu-central-1.amazonaws.com).

```bash
# Replace YOUR_API_URL with the output from the previous step
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUR_API_URL/webhook", "secret_token": "YOUR_SECRET_TOKEN"}'
```

## 👨‍💻 Professional Workflow

This isn't just a template; it's a complete engineering environment.

### Code Quality (Pre-commit)

We use pre-commit to ensure code style consistency (Black, Flake8) before you push.

```bash
# Install git hooks
uv run pre-commit install

# (Optional) Run manually
uv run pre-commit run --all-files
```

### CI/CD Pipeline (GitHub Actions)

This project includes a fully automated pipeline (`.github/workflows/deploy.yml`) that deploys to `dev` on push and `prod` on manual trigger.

### Security: No Access Keys Required!

We use AWS OIDC (OpenID Connect) for passwordless, secure deployments.

Run the setup script:

```bash
# Make the script executable
chmod +x scripts/setup_oidc.sh

# Usage: ./scripts/setup_oidc.sh <github_user>/<repo_name>
./scripts/setup_oidc.sh yourname/serverless-tg-bot-starter
```

**Add Secrets to GitHub:** Copy the `AWS_ROLE_ARN` output from the script and add it to your repo secrets, along with your Bot Tokens.

## 📚 Documentation

- 📖 **[Developer Guide](developer_guide.md)**: How to write handlers, use the Context object, and add features.
- 🚀 **[Deployment Guide](deployment.md)**: Detailed CI/CD setup, OIDC explanation, and monitoring.

## 🤝 Contributing

Contributions are welcome! Please run pre-commit before submitting a Pull Request.

## License

MIT License - feel free to use this template for your projects!

---

**Made with ❤️ for developers in Central Asia transitioning to Serverless**
