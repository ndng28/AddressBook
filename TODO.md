# AddressBook AWS Deployment TODO

## Overview
Deploy FastAPI AddressBook application to AWS using ECS Fargate, RDS PostgreSQL, and Terraform.

## Phases

### Phase 1: Build FastAPI Application
- [ ] Create `app/main.py` - FastAPI app entry with health check
- [ ] Create `app/config.py` - Pydantic settings for environment variables
- [ ] Create `app/database.py` - SQLAlchemy async setup with connection pooling
- [ ] Create `app/models/contact.py` - Contact SQLAlchemy model
- [ ] Create `app/schemas/contact.py` - Pydantic request/response schemas
- [ ] Create `app/routers/contacts.py` - CRUD API endpoints
- [ ] Create `app/services/contact_service.py` - Business logic layer
- [ ] Create `app/__init__.py` - Package initialization
- [ ] Create `tests/conftest.py` - Pytest fixtures
- [ ] Create `tests/test_contacts.py` - API tests

### Phase 2: Docker Setup
- [ ] Create `Dockerfile` - Multi-stage build (slim Python image)
- [ ] Create `.dockerignore` - Optimize build context
- [ ] Create `docker-compose.yml` - Local development with PostgreSQL
- [ ] Create `docker-compose.prod.yml` - Production-like local testing
- [ ] Test Docker build locally

### Phase 3: AWS Infrastructure (Terraform)
- [ ] Create `infrastructure/` directory structure
- [ ] Create VPC with public/private subnets across 2 AZs
- [ ] Create Internet Gateway and NAT Gateways
- [ ] Create Security Groups (ALB, ECS, RDS)
- [ ] Create ECS Cluster (Fargate)
- [ ] Create ECS Task Definition
- [ ] Create ECS Service with auto-scaling (1-3 tasks)
- [ ] Create Application Load Balancer with HTTPS
- [ ] Create RDS PostgreSQL instance
- [ ] Create RDS Subnet Group and Parameter Group
- [ ] Create ECR repository with lifecycle policies
- [ ] Create CloudWatch Log Groups
- [ ] Create IAM roles for ECS
- [ ] Create Secrets Manager for DB credentials

### Phase 4: CI/CD Pipeline
- [ ] Create `.github/workflows/deploy.yml`
- [ ] Configure GitHub Actions for testing on PR
- [ ] Configure Docker build and push to ECR
- [ ] Configure ECS deployment with rolling updates
- [ ] Add database migrations (alembic) to deployment

### Phase 5: Configuration & Secrets
- [ ] Create `.env.example` template
- [ ] Create environment variable documentation
- [ ] Set up AWS Secrets Manager integration
- [ ] Document local development setup

## Deployment Checklist
- [ ] Run all tests locally
- [ ] Build and test Docker image locally
- [ ] Initialize Terraform backend
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

## AWS Resources Created
- VPC with 2 AZs
- ECS Cluster + Service
- Application Load Balancer
- RDS PostgreSQL
- ECR Repository
- CloudWatch Log Groups
- Secrets Manager
- IAM Roles
- Security Groups
