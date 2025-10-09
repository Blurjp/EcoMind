# Secret Management for EcoMind

## Overview

This document describes how to manage secrets (database credentials, API keys, etc.) across different environments.

**SECURITY FIX (Codex Review P001)**:
- No hard-coded credentials in configuration files
- Environment-specific secret management
- References: phases/P001/codex_review.md:294-302

---

## Environment Strategy

### Local Development

**Method**: `.env` file (NOT committed to git)

```bash
# .env
DATABASE_URL=postgresql://ecomind:ecomind_dev_pass@localhost:5432/ecomind
REDIS_URL=redis://localhost:6379
JWT_SECRET=local_dev_secret_change_in_production
```

**Setup**:
```bash
cp .env.example .env
# Edit .env with your local values
```

**Loading**:
- Docker Compose: Automatically loaded via `env_file:`
- Local Python: Use `python-dotenv` package

---

### Staging Environment

**Method**: AWS Secrets Manager

**Secret Structure**:
```json
{
  "name": "ecomind/staging/database",
  "value": {
    "connection_string": "postgresql://user:password@rds-staging.us-east-1.rds.amazonaws.com:5432/ecomind",
    "host": "rds-staging.us-east-1.rds.amazonaws.com",
    "port": "5432",
    "database": "ecomind",
    "username": "ecomind_app",
    "password": "<generated-by-secrets-manager>"
  }
}
```

**Retrieval Methods**:

1. **ECS Task Execution** (Recommended):
```json
{
  "containerDefinitions": [{
    "secrets": [
      {
        "name": "DATABASE_URL",
        "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:ecomind/staging/database:connection_string::"
      }
    ]
  }]
}
```

2. **CLI**:
```bash
export DATABASE_URL=$(aws secretsmanager get-secret-value \
  --secret-id ecomind/staging/database \
  --query SecretString --output text | jq -r .connection_string)
```

3. **Python (boto3)**:
```python
import boto3
import json

def get_database_url(environment):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=f'ecomind/{environment}/database')
    secret = json.loads(response['SecretString'])
    return secret['connection_string']

# Usage
os.environ['DATABASE_URL'] = get_database_url('staging')
```

---

### Production Environment

**Method**: AWS Secrets Manager with automatic rotation

**Setup**:

1. **Create RDS Secret**:
```bash
aws secretsmanager create-secret \
  --name ecomind/prod/database \
  --description "EcoMind production database credentials" \
  --secret-string '{
    "engine": "postgres",
    "host": "ecomind-prod.cluster-xyz.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "dbname": "ecomind",
    "username": "ecomind_app",
    "password": "REPLACE_WITH_GENERATED_PASSWORD"
  }'
```

2. **Enable Rotation** (30 days):
```bash
aws secretsmanager rotate-secret \
  --secret-id ecomind/prod/database \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRDSPostgreSQLRotation \
  --rotation-rules AutomaticallyAfterDays=30
```

3. **Grant IAM Access**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:*:secret:ecomind/prod/*"
      ]
    }
  ]
}
```

---

## Migration Script Integration

### Option 1: ECS Task (Recommended for Production)

**Dockerfile** (migration-specific):
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY api/ /app/
RUN pip install -e .

# Migration entrypoint
ENTRYPOINT ["./scripts/run_migrations.sh"]
CMD ["upgrade", "head"]
```

**ECS Task Definition**:
```json
{
  "family": "ecomind-migration",
  "containerDefinitions": [{
    "name": "migration",
    "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/ecomind-migration:latest",
    "secrets": [
      {
        "name": "DATABASE_URL",
        "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:ecomind/prod/database:connection_string::"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/ecomind-migration",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "migration"
      }
    }
  }],
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "256",
  "memory": "512"
}
```

**Deployment Script**:
```bash
#!/bin/bash
# Run migration task before deploying API
aws ecs run-task \
  --cluster ecomind-prod \
  --task-definition ecomind-migration \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-abc123],
    securityGroups=[sg-xyz789],
    assignPublicIp=DISABLED
  }"

# Wait for task to complete
# Then deploy API service update
```

### Option 2: Kubernetes Init Container

**Deployment YAML**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecomind-api
spec:
  template:
    spec:
      initContainers:
      - name: migrate
        image: ecomind-migration:latest
        command: ["./scripts/run_migrations.sh", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ecomind-database
              key: connection-string
      containers:
      - name: api
        image: ecomind-api:latest
        # ... rest of API container spec
```

### Option 3: Docker Compose (Local/Dev)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ecomind
      POSTGRES_USER: ecomind
      POSTGRES_PASSWORD: ecomind_dev_pass
    ports:
      - "5432:5432"

  migrate:
    build:
      context: ./api
    command: ["./scripts/run_migrations.sh", "upgrade", "head"]
    env_file:
      - .env
    depends_on:
      - postgres

  api:
    build:
      context: ./api
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
    env_file:
      - .env
    depends_on:
      migrate:
        condition: service_completed_successfully
    ports:
      - "8000:8000"
```

---

## Security Best Practices

### 1. Never Commit Secrets

**.gitignore**:
```
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
```

### 2. Use Least Privilege IAM

Migration task role should only have:
- `secretsmanager:GetSecretValue` on database secret
- `rds-data:ExecuteStatement` if using RDS Data API
- `logs:CreateLogStream` and `logs:PutLogEvents` for CloudWatch

### 3. Enable Audit Logging

```bash
# Enable CloudTrail for Secrets Manager
aws cloudtrail create-trail \
  --name ecomind-secrets-audit \
  --s3-bucket-name ecomind-audit-logs

# Log all GetSecretValue calls
aws cloudtrail put-event-selectors \
  --trail-name ecomind-secrets-audit \
  --event-selectors '[{
    "ReadWriteType": "All",
    "IncludeManagementEvents": true,
    "DataResources": [{
      "Type": "AWS::SecretsManager::Secret",
      "Values": ["arn:aws:secretsmanager:us-east-1:*:secret:ecomind/*"]
    }]
  }]'
```

### 4. Rotate Credentials Regularly

- Production: Every 30 days (automated)
- Staging: Every 90 days
- Development: No rotation needed (local only)

### 5. Use SSL for Database Connections

```python
# In production, enforce SSL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL.endswith('?sslmode=require'):
    DATABASE_URL += '?sslmode=require'
```

---

## Troubleshooting

### Migration Fails: "Permission Denied"

**Cause**: ECS task role lacks Secrets Manager access

**Fix**:
```bash
aws iam attach-role-policy \
  --role-name ecomind-migration-task-role \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

### Secret Not Found

**Cause**: Wrong region or secret name

**Check**:
```bash
aws secretsmanager list-secrets --region us-east-1 | grep ecomind
```

### Connection Timeout

**Cause**: Security group blocking RDS access

**Fix**: Add ECS task security group to RDS inbound rules:
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-rds-database \
  --protocol tcp \
  --port 5432 \
  --source-group sg-ecs-tasks
```

---

## Environment Variable Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | Full PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | No | Redis connection string | `redis://host:6379` |
| `JWT_SECRET` | Yes | JWT signing secret (production) | Auto-generated |
| `AWS_REGION` | Production | AWS region for Secrets Manager | `us-east-1` |
| `ENVIRONMENT` | No | Environment name | `development`, `staging`, `production` |

---

## See Also

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [Alembic Configuration](../api/alembic.ini)
- [Migration Runner Script](../api/scripts/run_migrations.sh)
- [Deployment Guide](./deployment.md)
