# AddressBook AWS Deployment TODO

## Overview
Deploy FastAPI AddressBook application to AWS using ECS Fargate, RDS PostgreSQL, and Terraform.

## Current Status

### ✅ Completed (79 Tests Passing)
- [x] FastAPI app with health check and root endpoint
- [x] Pydantic settings configuration
- [x] SQLAlchemy database models (User, Contact)
- [x] Pydantic schemas with validation
- [x] JWT authentication utilities (bcrypt, tokens)
- [x] User service and auth router (register, login, /me)
- [x] Contact service with CRUD operations
- [x] Contact API router with 7 endpoints
- [x] Docker multi-stage build
- [x] Docker Compose (dev and prod)
- [x] Comprehensive test suite

### 🔄 Remaining Tasks

#### Phase 3: AWS Infrastructure (Terraform)
- [ ] Create `infrastructure/` directory structure
- [ ] Create VPC module (public/private subnets across 2 AZs)
- [ ] Create Internet Gateway and NAT Gateways
- [ ] Create Security Groups (ALB, ECS, RDS)
- [ ] Create ECS Cluster module (Fargate)
- [ ] Create ECS Task Definition
- [ ] Create ECS Service with auto-scaling (1-3 tasks)
- [ ] Create Application Load Balancer with HTTPS
- [ ] Create RDS PostgreSQL instance module
- [ ] Create RDS Subnet Group and Parameter Group
- [ ] Create ECR repository with lifecycle policies
- [ ] Create CloudWatch Log Groups
- [ ] Create IAM roles for ECS
- [ ] Create Secrets Manager for DB credentials
- [ ] Create main.tf to orchestrate all modules
- [ ] Create variables.tf with configurable parameters
- [ ] Create outputs.tf for resource ARNs/endpoints

#### Phase 4: CI/CD Pipeline
- [ ] Create `.github/workflows/deploy.yml`
- [ ] Configure GitHub Actions for testing on PR
- [ ] Configure Docker build and push to ECR
- [ ] Configure ECS deployment with rolling updates
- [ ] Add database migrations (alembic) to deployment
- [ ] Add GitHub Actions secrets documentation

#### Phase 5: Configuration & Secrets
- [ ] Create `.env.example` template
- [ ] Create environment variable documentation
- [ ] Set up AWS Secrets Manager integration
- [ ] Create local development setup guide
- [ ] Add README.md with project overview

#### Phase 6: Testing & Observability
- [ ] Add API integration tests
- [ ] Add load testing with locust
- [ ] Configure CloudWatch logs
- [ ] Set up CloudWatch metrics
- [ ] Add health check endpoints monitoring
- [ ] Create runbook for common issues

## Deployment Checklist
- [ ] Run all tests locally (79/79 passing ✅)
- [ ] Build and test Docker image locally
- [ ] Initialize Terraform backend (S3)
- [ ] Deploy infrastructure with Terraform
- [ ] Push Docker image to ECR
- [ ] Run database migrations
- [ ] Verify application health endpoint
- [ ] Test API endpoints
- [ ] Verify auto-scaling works
- [ ] Document deployment process

## Notes
- **Architecture**: ECS Fargate (serverless containers)
- **Database**: RDS PostgreSQL (db.t3.micro for dev)
- **Scaling**: Auto-scaling 1-3 tasks based on CPU/memory
- **Security**: Secrets in AWS Secrets Manager, no hardcoded credentials
- **Cost**: Optimized with right-sized instances and Fargate spot for non-prod

## AWS Resources to Create
- VPC with 2 AZs
- ECS Cluster + Service
- Application Load Balancer
- RDS PostgreSQL
- ECR Repository
- CloudWatch Log Groups
- Secrets Manager
- IAM Roles
- Security Groups

## Project Structure (Current)
```
AddressBook/
├── app/
│   ├── __init__.py
│   ├── main.py                 ✅
│   ├── config.py               ✅
│   ├── database.py             ✅
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             ✅
│   │   └── contact.py          ✅
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             ✅
│   │   ├── contact.py          ✅
│   │   └── token.py            ✅
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py             ✅
│   │   └── contacts.py         ✅
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py     ✅
│   │   └── contact_service.py  ✅
│   └── utils/
│       ├── __init__.py
│       └── auth.py             ✅
├── tests/
│   ├── __init__.py
│   ├── conftest.py             ✅
│   ├── test_main.py            ✅
│   ├── test_config.py          ✅
│   ├── test_schemas.py         ✅
│   ├── test_auth.py            ✅
│   ├── test_database.py        ✅
│   ├── test_contact_service.py ✅
│   └── test_contacts_endpoints.py ✅
├── infrastructure/             ⏳ Phase 3
├── .github/workflows/          ⏳ Phase 4
├── Dockerfile                  ✅
├── docker-compose.yml          ✅
├── docker-compose.prod.yml     ✅
├── .dockerignore               ✅
├── requirements.txt            ✅
├── pyproject.toml              ✅
├── TODO.md                     ✅
├── docs/PRD.md                 ✅
└── README.md                   ⏳ Phase 5
```
