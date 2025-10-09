# Phase 3: Infrastructure-as-Code (Terraform + Kubernetes)

**Phase ID**: P003
**Duration**: 2 weeks (10 business days)
**Priority**: HIGH (PRODUCTION BLOCKER)
**Owner**: DevOps Team
**Status**: Design Review
**Dependencies**: P001 (migrations), P002 (auth)

---

## 1. Executive Summary

Implement production-ready Infrastructure-as-Code (IaC) using Terraform for AWS provisioning and Helm charts for Kubernetes deployment, enabling automated, repeatable, and scalable infrastructure management.

**Problem Statement:**
- **CRITICAL**: Empty `infra/terraform/` and `infra/helm/` directories
- Cannot deploy to production without automation
- Manual infrastructure setup is error-prone and not scalable
- No disaster recovery or multi-region support
- `ENTERPRISE_SETUP.md:134-186` promises Terraform/Helm but none exist

**Success Criteria:**
- ✅ Terraform provisions complete AWS infrastructure (ECS/EKS, RDS, MSK, Redis)
- ✅ Helm charts deploy all services to Kubernetes
- ✅ CI/CD pipeline deploys to staging/production automatically
- ✅ Infrastructure versioned in Git
- ✅ Disaster recovery tested (RTO < 4 hours)
- ✅ Cost optimization (< $500/month for small enterprise)

---

## 2. Technical Architecture

### 2.1 Current State Analysis

**Evidence from codebase:**

```bash
$ ls -la infra/terraform/
total 0
drwxr-xr-x@ 2 jianphua  staff   64 Sep 30 12:13 .

$ ls -la infra/helm/
total 0
drwxr-xr-x@ 2 jianphua  staff   64 Sep 30 12:13 .
```

**Status**: Completely empty (no Terraform modules, no Helm charts)

**Referenced in**: `ext-chrome/ENTERPRISE_SETUP.md:134-152`
```markdown
#### Option 1: AWS (Terraform - Automated)

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

**Provisions**:
- EKS cluster (Kubernetes)
- RDS PostgreSQL (with TimescaleDB)
- MSK (Kafka) or EC2 with Redpanda
- ElastiCache Redis
- S3 for exports
- CloudFront for UI
- ALB with TLS
```

**Problem**: Promises not delivered - no files exist.

### 2.2 Proposed Architecture

#### 2.2.1 AWS Infrastructure (Terraform)

```
┌────────────────────────────────────────────────────────────────┐
│                       AWS Cloud Architecture                   │
└────────────────────────────────────────────────────────────────┘

Internet
   │
   ├─> Route 53 (ecomind.acme.com)
   │      │
   │      ├─> CloudFront (CDN) ──> S3 (UI Static Assets)
   │      │
   │      └─> ALB (Application Load Balancer)
   │             │
   │             ├─> ECS/EKS Cluster
   │             │      ├─> Gateway (Go) - 3 instances
   │             │      ├─> API (FastAPI) - 3 instances
   │             │      ├─> Worker (Python) - 2 instances
   │             │      └─> UI (Next.js) - 2 instances
   │             │
   │             └─> VPC
   │                    ├─> Public Subnets (ALB, NAT Gateway)
   │                    └─> Private Subnets
   │                           ├─> RDS PostgreSQL (Multi-AZ)
   │                           ├─> ElastiCache Redis (Cluster mode)
   │                           └─> MSK (Kafka 3 brokers)
   │
   └─> S3 (Reports, Backups)
```

**Components:**

1. **Networking** (`infra/terraform/modules/networking/`)
   - VPC with 3 availability zones
   - Public subnets (24 IPs each)
   - Private subnets (256 IPs each)
   - NAT Gateway for outbound traffic
   - Security groups (least privilege)

2. **Compute** (`infra/terraform/modules/compute/`)
   - ECS Fargate (simpler) OR EKS (more powerful)
   - Auto Scaling Groups
   - Application Load Balancer
   - Target Groups for each service

3. **Database** (`infra/terraform/modules/database/`)
   - RDS PostgreSQL 15 with TimescaleDB extension
   - Multi-AZ for high availability
   - Automated backups (7-day retention)
   - Read replicas for analytics queries

4. **Streaming** (`infra/terraform/modules/streaming/`)
   - MSK (managed Kafka) OR
   - EC2 instances with Redpanda (cost-effective alternative)

5. **Cache** (`infra/terraform/modules/cache/`)
   - ElastiCache Redis (Cluster mode)
   - Replication for high availability

6. **Storage** (`infra/terraform/modules/storage/`)
   - S3 buckets for reports, exports, backups
   - Lifecycle policies (archive after 90 days)

7. **CDN** (`infra/terraform/modules/cdn/`)
   - CloudFront distribution
   - ACM certificate for HTTPS
   - Route 53 DNS records

#### 2.2.2 Kubernetes Deployment (Helm)

```
infra/helm/ecomind/
├── Chart.yaml                  # Helm chart metadata
├── values.yaml                 # Default configuration
├── values-dev.yaml             # Development overrides
├── values-staging.yaml         # Staging overrides
├── values-prod.yaml            # Production overrides
├── templates/
│   ├── gateway/
│   │   ├── deployment.yaml     # Gateway deployment
│   │   ├── service.yaml        # Gateway service
│   │   ├── hpa.yaml            # Horizontal Pod Autoscaler
│   │   └── configmap.yaml      # Gateway config
│   ├── api/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── hpa.yaml
│   │   └── migration-job.yaml  # Database migration job
│   ├── worker/
│   │   ├── deployment.yaml
│   │   └── configmap.yaml
│   ├── ui/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml        # Ingress for UI
│   ├── ingress.yaml            # Main ingress controller
│   ├── secrets.yaml            # Secrets (JWT, DB passwords)
│   └── networkpolicy.yaml      # Network policies
└── crds/                       # Custom Resource Definitions (if needed)
```

### 2.3 Directory Structure

```
EcoMind/
├── infra/
│   ├── terraform/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   ├── outputs.tf
│   │   │   │   └── terraform.tfvars
│   │   │   ├── staging/
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   ├── outputs.tf
│   │   │   │   └── terraform.tfvars
│   │   │   └── prod/
│   │   │       ├── main.tf
│   │   │       ├── variables.tf
│   │   │       ├── outputs.tf
│   │   │       └── terraform.tfvars.example
│   │   ├── modules/
│   │   │   ├── networking/
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   ├── compute/           # ECS/EKS cluster
│   │   │   ├── database/          # RDS
│   │   │   ├── streaming/         # MSK
│   │   │   ├── cache/             # Redis
│   │   │   ├── storage/           # S3
│   │   │   └── cdn/               # CloudFront
│   │   └── README.md
│   └── helm/
│       ├── ecomind/
│       │   ├── Chart.yaml
│       │   ├── values.yaml
│       │   ├── values-dev.yaml
│       │   ├── values-staging.yaml
│       │   ├── values-prod.yaml
│       │   └── templates/
│       └── README.md
├── .github/
│   └── workflows/
│       ├── terraform-plan.yml      # NEW: Terraform validation
│       ├── terraform-apply.yml     # NEW: Terraform deployment
│       ├── helm-deploy.yml         # NEW: Helm deployment
│       └── e2e-tests.yml           # NEW: End-to-end tests
└── docs/
    ├── DEPLOYMENT.md               # UPDATED: Add IaC deployment
    └── DISASTER_RECOVERY.md        # NEW: DR runbook
```

---

## 3. Implementation Plan

### 3.1 Week 1: Terraform Foundation

#### Day 1-2: Networking Module

**Tasks:**

1. Create `infra/terraform/modules/networking/main.tf`
   ```hcl
   # VPC
   resource "aws_vpc" "main" {
     cidr_block           = var.vpc_cidr
     enable_dns_hostnames = true
     enable_dns_support   = true

     tags = {
       Name        = "${var.project_name}-vpc"
       Environment = var.environment
     }
   }

   # Public Subnets (3 AZs)
   resource "aws_subnet" "public" {
     count                   = 3
     vpc_id                  = aws_vpc.main.id
     cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
     availability_zone       = data.aws_availability_zones.available.names[count.index]
     map_public_ip_on_launch = true

     tags = {
       Name = "${var.project_name}-public-${count.index + 1}"
     }
   }

   # Private Subnets (3 AZs)
   resource "aws_subnet" "private" {
     count             = 3
     vpc_id            = aws_vpc.main.id
     cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
     availability_zone = data.aws_availability_zones.available.names[count.index]

     tags = {
       Name = "${var.project_name}-private-${count.index + 1}"
     }
   }

   # Internet Gateway
   resource "aws_internet_gateway" "main" {
     vpc_id = aws_vpc.main.id

     tags = {
       Name = "${var.project_name}-igw"
     }
   }

   # NAT Gateway (1 per AZ for HA)
   resource "aws_eip" "nat" {
     count  = 3
     domain = "vpc"
   }

   resource "aws_nat_gateway" "main" {
     count         = 3
     allocation_id = aws_eip.nat[count.index].id
     subnet_id     = aws_subnet.public[count.index].id

     tags = {
       Name = "${var.project_name}-nat-${count.index + 1}"
     }
   }

   # Route Tables
   resource "aws_route_table" "public" {
     vpc_id = aws_vpc.main.id

     route {
       cidr_block = "0.0.0.0/0"
       gateway_id = aws_internet_gateway.main.id
     }

     tags = {
       Name = "${var.project_name}-public-rt"
     }
   }

   resource "aws_route_table" "private" {
     count  = 3
     vpc_id = aws_vpc.main.id

     route {
       cidr_block     = "0.0.0.0/0"
       nat_gateway_id = aws_nat_gateway.main[count.index].id
     }

     tags = {
       Name = "${var.project_name}-private-rt-${count.index + 1}"
     }
   }
   ```

2. Create `infra/terraform/modules/networking/variables.tf`
   ```hcl
   variable "project_name" {
     description = "Project name (ecomind)"
     type        = string
   }

   variable "environment" {
     description = "Environment (dev/staging/prod)"
     type        = string
   }

   variable "vpc_cidr" {
     description = "VPC CIDR block"
     type        = string
     default     = "10.0.0.0/16"
   }
   ```

3. Test networking module
   ```bash
   cd infra/terraform/environments/dev
   terraform init
   terraform plan
   ```

**Deliverables:**
- ✅ VPC with 3 AZs
- ✅ Public/private subnets
- ✅ NAT gateways
- ✅ Route tables

#### Day 3-4: Database & Cache Modules

**Tasks:**

1. Create `infra/terraform/modules/database/main.tf`
   ```hcl
   resource "aws_db_subnet_group" "main" {
     name       = "${var.project_name}-db-subnet"
     subnet_ids = var.private_subnet_ids

     tags = {
       Name = "${var.project_name}-db-subnet"
     }
   }

   resource "aws_security_group" "rds" {
     name        = "${var.project_name}-rds-sg"
     description = "Security group for RDS PostgreSQL"
     vpc_id      = var.vpc_id

     ingress {
       from_port   = 5432
       to_port     = 5432
       protocol    = "tcp"
       cidr_blocks = [var.vpc_cidr]
     }

     egress {
       from_port   = 0
       to_port     = 0
       protocol    = "-1"
       cidr_blocks = ["0.0.0.0/0"]
     }
   }

   resource "aws_db_instance" "main" {
     identifier             = "${var.project_name}-postgres"
     engine                 = "postgres"
     engine_version         = "15.4"
     instance_class         = var.db_instance_class
     allocated_storage      = var.db_allocated_storage
     storage_encrypted      = true
     db_name                = "ecomind"
     username               = var.db_username
     password               = var.db_password  # Use AWS Secrets Manager in prod
     db_subnet_group_name   = aws_db_subnet_group.main.name
     vpc_security_group_ids = [aws_security_group.rds.id]
     multi_az               = var.environment == "prod" ? true : false
     backup_retention_period = 7
     skip_final_snapshot    = var.environment != "prod"

     # TimescaleDB extension
     parameter_group_name = aws_db_parameter_group.timescale.name

     tags = {
       Name        = "${var.project_name}-postgres"
       Environment = var.environment
     }
   }

   resource "aws_db_parameter_group" "timescale" {
     name   = "${var.project_name}-timescale"
     family = "postgres15"

     parameter {
       name  = "shared_preload_libraries"
       value = "timescaledb"
     }
   }
   ```

2. Create `infra/terraform/modules/cache/main.tf`
   ```hcl
   resource "aws_elasticache_subnet_group" "main" {
     name       = "${var.project_name}-redis-subnet"
     subnet_ids = var.private_subnet_ids
   }

   resource "aws_security_group" "redis" {
     name        = "${var.project_name}-redis-sg"
     vpc_id      = var.vpc_id

     ingress {
       from_port   = 6379
       to_port     = 6379
       protocol    = "tcp"
       cidr_blocks = [var.vpc_cidr]
     }
   }

   resource "aws_elasticache_replication_group" "main" {
     replication_group_id       = "${var.project_name}-redis"
     replication_group_description = "Redis cluster for EcoMind"
     engine                     = "redis"
     engine_version             = "7.0"
     node_type                  = var.redis_node_type
     num_cache_clusters         = var.environment == "prod" ? 3 : 1
     port                       = 6379
     subnet_group_name          = aws_elasticache_subnet_group.main.name
     security_group_ids         = [aws_security_group.redis.id]
     automatic_failover_enabled = var.environment == "prod" ? true : false
     at_rest_encryption_enabled = true
     transit_encryption_enabled = true
   }
   ```

**Deliverables:**
- ✅ RDS PostgreSQL with TimescaleDB
- ✅ ElastiCache Redis cluster

#### Day 5: Streaming Module (MSK or Redpanda)

**Tasks:**

1. Create `infra/terraform/modules/streaming/main.tf`
   ```hcl
   # Option 1: MSK (managed, more expensive)
   resource "aws_msk_cluster" "main" {
     cluster_name           = "${var.project_name}-kafka"
     kafka_version          = "3.5.1"
     number_of_broker_nodes = 3

     broker_node_group_info {
       instance_type   = var.kafka_instance_type
       client_subnets  = var.private_subnet_ids
       security_groups = [aws_security_group.kafka.id]
       storage_info {
         ebs_storage_info {
           volume_size = 100
         }
       }
     }

     encryption_info {
       encryption_in_transit {
         client_broker = "TLS"
       }
     }

     tags = {
       Name        = "${var.project_name}-kafka"
       Environment = var.environment
     }
   }

   # Option 2: EC2 with Redpanda (cost-effective)
   resource "aws_instance" "redpanda" {
     count         = var.use_redpanda ? 3 : 0
     ami           = data.aws_ami.ubuntu.id
     instance_type = "t3.medium"
     subnet_id     = var.private_subnet_ids[count.index]
     vpc_security_group_ids = [aws_security_group.kafka.id]

     user_data = file("${path.module}/redpanda-setup.sh")

     tags = {
       Name = "${var.project_name}-redpanda-${count.index + 1}"
     }
   }
   ```

**Deliverables:**
- ✅ MSK cluster OR Redpanda EC2 instances

### 3.2 Week 2: Compute, CI/CD & Helm

#### Day 6-7: Compute Module (ECS Fargate)

**Tasks:**

1. Create `infra/terraform/modules/compute/main.tf`
   ```hcl
   # ECS Cluster
   resource "aws_ecs_cluster" "main" {
     name = "${var.project_name}-cluster"

     setting {
       name  = "containerInsights"
       value = "enabled"
     }
   }

   # Application Load Balancer
   resource "aws_lb" "main" {
     name               = "${var.project_name}-alb"
     internal           = false
     load_balancer_type = "application"
     security_groups    = [aws_security_group.alb.id]
     subnets            = var.public_subnet_ids

     enable_deletion_protection = var.environment == "prod"
   }

   # Target Groups
   resource "aws_lb_target_group" "gateway" {
     name     = "${var.project_name}-gateway-tg"
     port     = 8080
     protocol = "HTTP"
     vpc_id   = var.vpc_id
     target_type = "ip"

     health_check {
       path                = "/health"
       interval            = 30
       healthy_threshold   = 2
       unhealthy_threshold = 3
     }
   }

   # ECS Task Definitions
   resource "aws_ecs_task_definition" "gateway" {
     family                   = "${var.project_name}-gateway"
     network_mode             = "awsvpc"
     requires_compatibilities = ["FARGATE"]
     cpu                      = 256
     memory                   = 512
     execution_role_arn       = aws_iam_role.ecs_execution.arn

     container_definitions = jsonencode([{
       name  = "gateway"
       image = "${var.ecr_registry}/ecomind-gateway:latest"
       portMappings = [{
         containerPort = 8080
         protocol      = "tcp"
       }]
       environment = [
         { name = "KAFKA_BROKERS", value = var.kafka_brokers },
         { name = "REDIS_ADDR", value = var.redis_endpoint }
       ]
       logConfiguration = {
         logDriver = "awslogs"
         options = {
           "awslogs-group"         = "/ecs/${var.project_name}/gateway"
           "awslogs-region"        = var.region
           "awslogs-stream-prefix" = "ecs"
         }
       }
     }])
   }

   # ECS Service
   resource "aws_ecs_service" "gateway" {
     name            = "${var.project_name}-gateway"
     cluster         = aws_ecs_cluster.main.id
     task_definition = aws_ecs_task_definition.gateway.arn
     desired_count   = var.gateway_replicas
     launch_type     = "FARGATE"

     network_configuration {
       subnets          = var.private_subnet_ids
       security_groups  = [aws_security_group.gateway.id]
       assign_public_ip = false
     }

     load_balancer {
       target_group_arn = aws_lb_target_group.gateway.arn
       container_name   = "gateway"
       container_port   = 8080
     }
   }
   ```

2. Repeat for API, Worker, UI services

**Deliverables:**
- ✅ ECS cluster with all services

#### Day 8-9: Helm Charts

**Tasks:**

1. Create `infra/helm/ecomind/Chart.yaml`
   ```yaml
   apiVersion: v2
   name: ecomind
   description: EcoMind Enterprise Telemetry Platform
   version: 0.1.0
   appVersion: "0.1.0"
   ```

2. Create `infra/helm/ecomind/values.yaml`
   ```yaml
   global:
     environment: dev
     domain: ecomind.dev.acme.com

   gateway:
     replicaCount: 2
     image:
       repository: ecomind/gateway
       tag: latest
       pullPolicy: IfNotPresent
     resources:
       requests:
         cpu: 100m
         memory: 128Mi
       limits:
         cpu: 500m
         memory: 512Mi
     autoscaling:
       enabled: true
       minReplicas: 2
       maxReplicas: 10
       targetCPUUtilizationPercentage: 70

   api:
     replicaCount: 2
     image:
       repository: ecomind/api
       tag: latest
     env:
       DATABASE_URL: postgresql://user:pass@rds-endpoint:5432/ecomind
       REDIS_URL: redis://redis-endpoint:6379

   worker:
     replicaCount: 2
     image:
       repository: ecomind/worker
       tag: latest

   postgresql:
     enabled: false  # Use external RDS
     external:
       host: rds-endpoint.region.rds.amazonaws.com
       port: 5432
       database: ecomind

   redis:
     enabled: false  # Use external ElastiCache

   ingress:
     enabled: true
     className: nginx
     annotations:
       cert-manager.io/cluster-issuer: letsencrypt-prod
     hosts:
       - host: ecomind.dev.acme.com
         paths:
           - path: /
             pathType: Prefix
     tls:
       - secretName: ecomind-tls
         hosts:
           - ecomind.dev.acme.com
   ```

3. Create `infra/helm/ecomind/templates/gateway/deployment.yaml`
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: {{ include "ecomind.fullname" . }}-gateway
     labels:
       app: gateway
   spec:
     replicas: {{ .Values.gateway.replicaCount }}
     selector:
       matchLabels:
         app: gateway
     template:
       metadata:
         labels:
           app: gateway
       spec:
         containers:
           - name: gateway
             image: "{{ .Values.gateway.image.repository }}:{{ .Values.gateway.image.tag }}"
             ports:
               - containerPort: 8080
             env:
               - name: KAFKA_BROKERS
                 value: {{ .Values.kafka.brokers }}
               - name: REDIS_ADDR
                 value: {{ .Values.redis.endpoint }}
             resources:
               {{- toYaml .Values.gateway.resources | nindent 14 }}
             livenessProbe:
               httpGet:
                 path: /health
                 port: 8080
               initialDelaySeconds: 10
               periodSeconds: 10
             readinessProbe:
               httpGet:
                 path: /health
                 port: 8080
               initialDelaySeconds: 5
               periodSeconds: 5
   ```

**Deliverables:**
- ✅ Complete Helm charts for all services

#### Day 10: CI/CD Pipeline

**Tasks:**

1. Create `.github/workflows/terraform-apply.yml`
   ```yaml
   name: Terraform Apply

   on:
     push:
       branches: [main]
       paths:
         - 'infra/terraform/**'

   jobs:
     terraform:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3

         - name: Setup Terraform
           uses: hashicorp/setup-terraform@v2

         - name: Terraform Init
           run: |
             cd infra/terraform/environments/staging
             terraform init

         - name: Terraform Plan
           run: terraform plan -out=tfplan

         - name: Terraform Apply
           if: github.ref == 'refs/heads/main'
           run: terraform apply -auto-approve tfplan
           env:
             AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
             AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
   ```

2. Create `.github/workflows/helm-deploy.yml`
   ```yaml
   name: Helm Deploy

   on:
     workflow_run:
       workflows: ["Build and Push Images"]
       types: [completed]

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3

         - name: Configure kubectl
           uses: azure/k8s-set-context@v3
           with:
             method: kubeconfig
             kubeconfig: ${{ secrets.KUBE_CONFIG }}

         - name: Deploy with Helm
           run: |
             helm upgrade --install ecomind infra/helm/ecomind \
               -f infra/helm/ecomind/values-staging.yaml \
               --namespace ecomind \
               --create-namespace
   ```

**Deliverables:**
- ✅ Automated Terraform deployments
- ✅ Automated Helm deployments

---

## 4. Cost Analysis

### 4.1 Small Enterprise (100-500 users, ~100k calls/day)

**AWS Resources:**
- ECS Fargate (4 services, 2 replicas each): $150/month
- RDS PostgreSQL (db.t3.medium): $70/month
- ElastiCache Redis (cache.t3.small): $30/month
- MSK (3 brokers, kafka.t3.small): $200/month
- NAT Gateway (3 AZs): $100/month
- ALB: $20/month
- Data transfer: $30/month

**Total**: ~$600/month

**Cost Optimization**:
- Use Redpanda on EC2 instead of MSK: -$150/month
- Single NAT Gateway: -$70/month
- **Optimized Total**: ~$380/month

### 4.2 Medium Enterprise (1000+ users, ~1M calls/day)

**Total**: ~$2,500/month (as estimated in previous review)

---

## 5. Risk Analysis

### 5.1 High Risks

**Risk 1: Infrastructure Downtime During Deployment**
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**:
  - Blue-green deployment
  - Canary deployments (5% → 50% → 100%)
  - Automated rollback on failure

**Risk 2: Cost Overruns**
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**:
  - AWS Cost Explorer alerts
  - Budget alarms ($500, $1000 thresholds)
  - Right-sizing instances monthly

### 5.2 Medium Risks

**Risk 3: Terraform State Conflicts**
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**:
  - Remote state in S3 with DynamoDB locking
  - Separate states per environment
  - State backup before changes

---

## 6. Success Metrics

**Quantitative:**
- ✅ < 5 minutes deployment time (Helm)
- ✅ < 30 minutes infrastructure provisioning (Terraform)
- ✅ 99.9% uptime SLA
- ✅ < 4 hours disaster recovery (RTO)

**Qualitative:**
- ✅ Infrastructure reproducible across environments
- ✅ Developers can deploy without DevOps assistance
- ✅ Infrastructure changes reviewable via Git

---

## 7. Dependencies

**Upstream (Blockers):**
- P001: Database migrations (schema must be stable)
- P002: Authentication (secure deployment required)

**Downstream (Dependent on this):**
- P004: Monitoring (needs production infrastructure)

---

## 8. Acceptance Criteria

- [ ] Terraform provisions complete AWS infrastructure
- [ ] Helm charts deploy all services successfully
- [ ] CI/CD pipeline deploys to staging automatically
- [ ] Disaster recovery tested (database backup/restore)
- [ ] Cost monitoring alerts configured
- [ ] Documentation complete (`DEPLOYMENT.md`, `DISASTER_RECOVERY.md`)
- [ ] Infrastructure code peer-reviewed
- [ ] Zero-downtime deployment tested
- [ ] Rollback tested successfully

---

**Design Status**: Ready for Codex Review
**Next Step**: Codex review → Implementation → Testing → Production deployment
