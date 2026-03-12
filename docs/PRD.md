# Product Requirements Document (PRD)

## AddressBook - FastAPI Contact Management API

**Version**: 1.0  
**Date**: 2024-03-12  
**Author**: Naveesh  
**Status**: Draft

---

## 1. Executive Summary

### 1.1 Product Overview
AddressBook is a REST API built with FastAPI for managing personal and professional contacts. It serves as a comprehensive learning project demonstrating modern Python development practices, cloud deployment on AWS, and production-grade architecture patterns.

### 1.2 Purpose
- **Primary**: Personal learning and skill development
- **Secondary**: Portfolio/demo project showcasing full-stack Python development
- **Tertiary**: Reference implementation for FastAPI + AWS deployment patterns

### 1.3 Success Criteria
- [ ] Fully functional CRUD API with JWT authentication
- [ ] Successfully deployed to AWS ECS Fargate with RDS PostgreSQL
- [ ] Infrastructure as Code using Terraform
- [ ] Comprehensive test coverage (>80%)
- [ ] Full observability stack (logging, metrics, tracing)
- [ ] Complete documentation (API docs, architecture, deployment guide)
- [ ] CI/CD pipeline with automated testing and deployment

---

## 2. Target User

### 2.1 Primary User
**You** - A developer learning:
- FastAPI and modern Python async patterns
- Docker containerization best practices
- AWS cloud services and infrastructure
- Terraform and Infrastructure as Code
- Production deployment workflows

### 2.2 Secondary Users
- Other developers exploring the codebase on GitHub
- Future you (referencing this implementation)

---

## 3. Core Features

### 3.1 Contact Management

#### Contact Fields (Full Profile)
- **Basic Info**: First name, Last name, Full name (computed)
- **Contact Methods**:
  - Multiple email addresses (with type: work, personal, other)
  - Multiple phone numbers (with type: mobile, work, home, other)
- **Professional**: Company name, Job title, Department
- **Address**: Street, City, State/Province, ZIP/Postal code, Country
- **Personal**: Birthday, Notes, Profile photo/avatar
- **Organization**: Tags/Categories (work, family, friends, etc.)
- **Metadata**: Created at, Updated at, Is active (soft delete)

#### CRUD Operations
- **Create**: Add new contacts with full details
- **Read**:
  - Get single contact by ID
  - List all contacts with pagination
  - Search contacts by name, email, company
  - Filter by tags/categories
- **Update**: Full or partial updates (PATCH support)
- **Delete**: Soft delete (mark as inactive) with recovery option

#### Import/Export
- **Import**: Upload CSV file to bulk create contacts
- **Export**: Download all contacts as CSV

### 3.2 Authentication & Authorization

#### JWT Authentication
- User registration with email/password
- Login endpoint returning JWT access token
- Protected routes requiring valid JWT
- Token refresh mechanism
- Password hashing with bcrypt

#### User Model
- Email (unique)
- Hashed password
- Full name
- Created/updated timestamps

### 3.3 API Features

#### Search & Filtering
- Full-text search across name, email, company
- Filter by tags/categories
- Pagination (limit/offset or cursor-based)
- Sorting options (name, created date, updated date)

#### Data Validation
- Email format validation
- Phone number format validation
- Required field validation
- Unique constraint validation (email per user)

---

## 4. Technical Requirements

### 4.1 Backend Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.11+ |
| Framework | FastAPI | 0.109+ |
| ORM | SQLAlchemy | 2.0+ |
| Database | PostgreSQL | 15+ |
| Migrations | Alembic | 1.13+ |
| Validation | Pydantic | 2.5+ |
| Auth | python-jose | Latest |
| Password Hashing | bcrypt | Latest |
| Async Support | asyncpg | Latest |

### 4.2 Performance Requirements

Given this is a learning/demo project with small scale:

- **Best Effort**: Performance is secondary to learning
- **Acceptable Response Times**:
  - Simple queries: < 500ms
  - Complex queries with joins: < 1s
  - File uploads: < 5s
- **Scale Target**: Support up to 100 contacts, light concurrent usage (1-5 users)

### 4.3 Security Requirements

- **Authentication**: JWT tokens with 30-minute expiration
- **Authorization**: Users can only access their own contacts
- **Input Validation**: All inputs validated with Pydantic
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- **Password Security**: bcrypt hashing with salt
- **HTTPS**: Required for production deployment
- **CORS**: Configured for specific origins only

### 4.4 Data Storage

- **Primary Database**: PostgreSQL 15 (AWS RDS in production)
- **File Storage**: Local filesystem (dev), AWS S3 (production) for photos
- **Cache**: Optional Redis for session/token storage
- **Backup**: Daily automated backups (7-day retention)

---

## 5. Non-Functional Requirements

### 5.1 Observability (Comprehensive)

#### Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging with correlation IDs
- Error tracking with stack traces
- AWS CloudWatch Logs integration

#### Metrics
- Application metrics (requests/sec, latency, error rates)
- Business metrics (contacts created, API usage)
- Infrastructure metrics (CPU, memory, disk)
- AWS CloudWatch Metrics

#### Health Checks
- `/health` - Basic liveness check
- `/health/ready` - Readiness check (DB connectivity)
- `/health/deep` - Deep health check (all dependencies)

#### Tracing
- Distributed tracing with AWS X-Ray
- Request correlation IDs
- Performance profiling

#### Alerting
- Error rate thresholds
- Response time thresholds
- Infrastructure alerts (CPU, memory)
- AWS SNS for notifications

### 5.2 Testing Strategy (Comprehensive)

#### Unit Tests
- Business logic in services
- Utility functions
- Target: >80% coverage

#### Integration Tests
- API endpoint testing
- Database integration
- Authentication flows

#### End-to-End Tests
- Full user workflows
- Critical paths only

#### Performance Tests
- Load testing (locust/k6)
- Benchmark key endpoints
- Identify bottlenecks

#### Test Infrastructure
- pytest framework
- Test database (SQLite or PostgreSQL)
- Fixtures for test data
- Mock external services
- CI/CD integration

### 5.3 Documentation (Full)

#### Code Documentation
- Docstrings for all modules, classes, functions
- Type hints throughout
- Inline comments for complex logic

#### API Documentation
- OpenAPI/Swagger UI auto-generated
- Request/response examples
- Authentication documentation
- Error codes and handling

#### Architecture Documentation
- System architecture diagrams
- Data flow diagrams
- Database schema documentation
- Deployment architecture

#### Developer Documentation
- Setup instructions (local development)
- Environment configuration
- Testing guide
- Contribution guidelines

#### Operations Documentation
- Deployment procedures
- Troubleshooting guide
- Monitoring and alerting runbook
- Disaster recovery procedures

---

## 6. User Stories

### 6.1 Authentication

**US-001: User Registration**
> As a user, I want to create an account with email and password so that I can securely access my contacts.

**Acceptance Criteria:**
- Email must be unique and valid format
- Password must be at least 8 characters
- Account created with hashed password
- Returns JWT token upon success

**US-002: User Login**
> As a user, I want to log in with my credentials so that I can access my contacts.

**Acceptance Criteria:**
- Validate email and password
- Return JWT access token on success
- Return appropriate error on failure
- Token expires after 30 minutes

### 6.2 Contact Management

**US-003: Create Contact**
> As a user, I want to add a new contact with all their details so that I can keep track of my network.

**Acceptance Criteria:**
- Accept all contact fields
- Validate required fields (at least name or email)
- Associate contact with authenticated user
- Return created contact with ID

**US-004: View Contact List**
> As a user, I want to see all my contacts in a list so that I can browse my network.

**Acceptance Criteria:**
- Return paginated list of contacts
- Show basic info (name, email, phone)
- Order by most recently updated
- Support pagination (default 20 per page)

**US-005: Search Contacts**
> As a user, I want to search for contacts by name, email, or company so that I can quickly find someone.

**Acceptance Criteria:**
- Full-text search across multiple fields
- Case-insensitive search
- Return matching results sorted by relevance
- Support partial matches

**US-006: View Contact Details**
> As a user, I want to view all details of a specific contact so that I can see their complete information.

**Acceptance Criteria:**
- Return all contact fields
- Return 404 if contact not found or not owned by user
- Include metadata (created/updated dates)

**US-007: Update Contact**
> As a user, I want to edit a contact's information so that I can keep it up to date.

**Acceptance Criteria:**
- Support partial updates (PATCH)
- Validate updated fields
- Update 'updated_at' timestamp
- Return updated contact

**US-008: Delete Contact (Soft Delete)**
> As a user, I want to delete a contact but be able to recover it later so that I don't lose data permanently.

**Acceptance Criteria:**
- Mark contact as inactive (soft delete)
- Exclude from normal list views
- Ability to view deleted contacts
- Ability to restore deleted contacts

**US-009: Import Contacts**
> As a user, I want to import contacts from a CSV file so that I can migrate from another system.

**Acceptance Criteria:**
- Accept CSV file upload
- Validate CSV format
- Create contacts in bulk
- Return import summary (created, failed, errors)

**US-010: Export Contacts**
> As a user, I want to export my contacts to a CSV file so that I can back them up or use elsewhere.

**Acceptance Criteria:**
- Generate CSV with all contact fields
- Include all active contacts
- Downloadable file

### 6.3 Organization

**US-011: Tag Contacts**
> As a user, I want to assign tags to contacts (work, family, friends) so that I can organize them.

**Acceptance Criteria:**
- Support multiple tags per contact
- Predefined tags + custom tags
- Filter contacts by tag

**US-012: Filter by Category**
> As a user, I want to filter my contacts by category so that I can view specific groups.

**Acceptance Criteria:**
- Filter by single or multiple tags
- Combine with search
- Return filtered results

---

## 7. API Specification

### 7.1 Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.addressbook.example.com`

### 7.2 Authentication Endpoints

```
POST   /api/v1/auth/register     # Register new user
POST   /api/v1/auth/login        # Login, get JWT token
POST   /api/v1/auth/refresh      # Refresh access token
GET    /api/v1/auth/me           # Get current user info
```

### 7.3 Contact Endpoints

```
GET    /api/v1/contacts          # List contacts (with search/filter/pagination)
POST   /api/v1/contacts          # Create new contact
GET    /api/v1/contacts/{id}     # Get contact details
PATCH  /api/v1/contacts/{id}     # Update contact
DELETE /api/v1/contacts/{id}     # Soft delete contact
GET    /api/v1/contacts/deleted  # List deleted contacts
POST   /api/v1/contacts/{id}/restore  # Restore deleted contact
POST   /api/v1/contacts/import   # Import from CSV
GET    /api/v1/contacts/export   # Export to CSV
```

### 7.4 Health & Monitoring

```
GET    /health                   # Liveness check
GET    /health/ready             # Readiness check
GET    /health/deep              # Deep health check
GET    /metrics                  # Prometheus metrics (optional)
```

---

## 8. Data Models

### 8.1 User Model
```python
{
  "id": "uuid",
  "email": "string (unique)",
  "hashed_password": "string",
  "full_name": "string",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 8.2 Contact Model
```python
{
  "id": "uuid",
  "user_id": "uuid (foreign key)",
  "first_name": "string",
  "last_name": "string",
  "emails": [
    {"email": "string", "type": "work|personal|other", "is_primary": "boolean"}
  ],
  "phones": [
    {"number": "string", "type": "mobile|work|home|other", "is_primary": "boolean"}
  ],
  "company": "string",
  "job_title": "string",
  "department": "string",
  "address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "postal_code": "string",
    "country": "string"
  },
  "birthday": "date",
  "notes": "text",
  "photo_url": "string",
  "tags": ["string"],
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## 9. Deployment Architecture

### 9.1 AWS Infrastructure

| Component | Service | Purpose |
|-----------|---------|---------|
| Compute | ECS Fargate | Run FastAPI containers |
| Database | RDS PostgreSQL | Primary data storage |
| Load Balancer | ALB | Traffic distribution, SSL termination |
| Container Registry | ECR | Store Docker images |
| DNS | Route 53 | Domain management (optional) |
| SSL | ACM | HTTPS certificates |
| Secrets | Secrets Manager | DB credentials, JWT secret |
| Monitoring | CloudWatch | Logs, metrics, alarms |
| Tracing | X-Ray | Distributed tracing |
| Object Storage | S3 | Contact photos (optional) |

### 9.2 Network Architecture

- **VPC**: Multi-AZ deployment (2 availability zones)
- **Public Subnets**: ALB, NAT Gateways
- **Private Subnets**: ECS tasks, RDS
- **Security Groups**: Least privilege access

### 9.3 Scaling Strategy

- **ECS**: Auto-scaling 1-3 tasks based on CPU/memory
- **RDS**: Single instance (db.t3.micro), upgradeable
- **Scaling Triggers**: CPU > 70%, Memory > 70%

---

## 10. Development Workflow

### 10.1 Local Development
1. Clone repository
2. Create virtual environment
3. Install dependencies
4. Start PostgreSQL (Docker)
5. Run migrations
6. Start development server
7. Access API at http://localhost:8000

### 10.2 Testing Workflow
1. Write tests first (TDD approach)
2. Run tests locally
3. Tests run in CI on PR
4. Coverage report generated
5. Merge only when tests pass

### 10.3 Deployment Workflow
1. Push to main branch
2. CI runs tests
3. Build Docker image
4. Push to ECR
5. Run database migrations
6. Deploy to ECS (rolling update)
7. Verify health checks
8. Monitor deployment

---

## 11. Out of Scope

The following features are explicitly **NOT** included in this version:

- **Mobile App**: No native mobile applications
- **Web UI**: API only, no frontend (can be added later)
- **Real-time Updates**: No WebSockets or real-time sync
- **Advanced Search**: No Elasticsearch or fuzzy search
- **Email Integration**: No email sending or receiving
- **Calendar Integration**: No Google/Outlook calendar sync
- **Multi-tenancy**: Single user per account
- **Role-based Access**: Simple user auth only
- **API Rate Limiting**: Basic protection only
- **GraphQL**: REST API only
- **Microservices**: Monolithic architecture

---

## 12. Timeline & Milestones

**Note**: No fixed deadline - work at comfortable pace

### Milestone 1: Core API (MVP)
- [ ] FastAPI project setup
- [ ] Database models and migrations
- [ ] Basic CRUD endpoints
- [ ] JWT authentication
- [ ] Unit tests
- **Goal**: Working local API

### Milestone 2: Docker & Local Dev
- [ ] Dockerfile
- [ ] Docker Compose
- [ ] Local PostgreSQL setup
- [ ] Integration tests
- **Goal**: Containerized app running locally

### Milestone 3: AWS Infrastructure
- [ ] Terraform modules
- [ ] VPC and networking
- [ ] ECS cluster and service
- [ ] RDS PostgreSQL
- [ ] ALB and SSL
- **Goal**: Infrastructure deployable

### Milestone 4: CI/CD Pipeline
- [ ] GitHub Actions workflow
- [ ] Automated testing
- [ ] Docker build and push
- [ ] ECS deployment
- **Goal**: Push-to-deploy working

### Milestone 5: Advanced Features
- [ ] Import/Export CSV
- [ ] Contact photos
- [ ] Soft delete and recovery
- [ ] Search and filtering
- [ ] Tags and categories
- **Goal**: Feature-complete API

### Milestone 6: Production Readiness
- [ ] Comprehensive monitoring
- [ ] Full observability stack
- [ ] Documentation complete
- [ ] Performance testing
- [ ] Security hardening
- **Goal**: Production-ready application

---

## 13. Success Metrics

### 13.1 Functional Success
- [ ] All user stories implemented and tested
- [ ] API responds correctly to all requests
- [ ] Authentication works securely
- [ ] Data persists correctly

### 13.2 Technical Success
- [ ] Code coverage > 80%
- [ ] All tests passing
- [ ] No critical security vulnerabilities
- [ ] Successfully deployed to AWS
- [ ] Auto-scaling works
- [ ] Monitoring captures all metrics

### 13.3 Learning Success
- [ ] Understanding of FastAPI patterns
- [ ] Experience with Docker best practices
- [ ] Knowledge of AWS services
- [ ] Terraform proficiency
- [ ] CI/CD pipeline experience
- [ ] Production deployment knowledge

---

## 14. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| AWS costs exceed budget | Medium | Low | Use free tier, monitor costs, tear down when not needed |
| Learning curve too steep | High | Medium | Break into smaller tasks, focus on one thing at a time |
| Scope creep | Medium | High | Stick to PRD, document future features separately |
| Time constraints | Low | Medium | No deadline, work at own pace |
| Technical debt | Medium | Medium | Write tests, document decisions, refactor regularly |

---

## 15. Appendix

### 15.1 Glossary
- **CRUD**: Create, Read, Update, Delete
- **JWT**: JSON Web Token
- **ECS**: Elastic Container Service
- **RDS**: Relational Database Service
- **ALB**: Application Load Balancer
- **VPC**: Virtual Private Cloud
- **IaC**: Infrastructure as Code

### 15.2 References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/intro.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [12-Factor App](https://12factor.net/)

### 15.3 Future Considerations
- Frontend web application (React/Vue)
- Mobile responsiveness
- Social authentication (OAuth)
- Contact sharing between users
- Advanced analytics
- API versioning

---

**Document Control**
- **Author**: Naveesh
- **Reviewers**: Self
- **Approval**: N/A (Personal project)
- **Last Updated**: 2024-03-12

**Changelog**
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-03-12 | Naveesh | Initial draft |
