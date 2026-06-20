# Alemeno Backend Assignment

A scalable backend system for processing financial transaction datasets asynchronously using FastAPI, PostgreSQL, Redis, Celery, and Docker.

The platform accepts transaction CSV uploads, performs automated cleaning and normalization, enriches missing categories through AI-assisted classification, detects anomalous transactions, generates analytical summaries, and exposes results through REST APIs.

---

## Features

- CSV Upload & Processing
- Asynchronous Background Processing using Celery
- PostgreSQL Data Persistence
- Redis Message Queue Integration
- Automated Data Cleaning & Normalization
- Duplicate Transaction Removal
- Missing Value Handling
- Transaction Anomaly Detection
- Category-Based Spend Analysis
- AI-Assisted Category Classification
- Narrative Summary Generation
- Graceful Fallback when AI Services are Unavailable
- Dockerized Deployment

---

## System Architecture

The system follows an asynchronous event-driven architecture where uploaded CSV files are processed in the background to avoid blocking API requests.

![System Architecture](images/architecture.png)

### Components

- **FastAPI** handles incoming API requests.
- **PostgreSQL** stores job metadata and processed transaction records.
- **Redis** acts as the message broker between the API and worker services.
- **Celery Workers** perform background CSV processing.
- **Gemini Integration** enriches transaction categories and generates summaries.
- **Docker Compose** orchestrates all services in a reproducible environment.

---

## Processing Pipeline

The transaction processing workflow is executed asynchronously through Celery workers. This design ensures that large CSV uploads do not block API responses while enabling scalable background processing.

![Processing Pipeline](images/processing-pipeline.png)

### Workflow Stages

1. **Upload CSV** – User uploads a transaction dataset.
2. **Create Job** – A processing job is created and stored in PostgreSQL.
3. **Queue Background Task** – Celery receives the job through Redis.
4. **Read CSV** – Transaction data is loaded into memory.
5. **Remove Duplicates** – Duplicate records are eliminated.
6. **Normalize Data** – Currency, dates, amounts, and status values are standardized.
7. **Fill Missing Categories** – Missing categories are enriched using AI-assisted classification with fallback handling.
8. **Detect Anomalies** – Transactions are analyzed using rule-based anomaly detection.
9. **Generate Summary** – Risk insights and transaction summaries are generated.
10. **Store Transactions** – Processed records are persisted in PostgreSQL.
11. **Job Completed** – Results become available through API endpoints.

---
## Interactive API Documentation (Swagger UI)

FastAPI automatically generates OpenAPI-compliant documentation, allowing users to test endpoints directly from the browser.

![Swagger UI](images/swagger-ui.png)

### Available Endpoints

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | `/jobs/upload` | Upload a transaction CSV file |
| GET | `/jobs/` | Retrieve all processing jobs |
| GET | `/jobs/{job_id}/status` | Check processing status |
| GET | `/jobs/{job_id}/results` | Retrieve processed results and analytics |

---

## Technology Stack

| Layer | Technology |
|---------|------------|
| Backend Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Background Processing | Celery |
| Message Broker | Redis |
| Data Processing | Pandas |
| AI Integration | Gemini API |
| Containerization | Docker |
| API Documentation | Swagger / OpenAPI |

---

## Why These Technologies?

- **FastAPI** provides high-performance REST APIs with automatic OpenAPI documentation.
- **PostgreSQL** ensures reliable relational data storage.
- **SQLAlchemy** simplifies database interactions through ORM abstractions.
- **Redis** acts as a lightweight message broker.
- **Celery** enables asynchronous background task execution.
- **Pandas** supports efficient CSV processing and data transformation.
- **Docker** provides reproducible deployment environments.

---
## Database Schema

### Jobs Table

Stores metadata related to CSV processing jobs.

| Column | Type | Description |
|----------|----------|----------|
| id | Integer | Unique Job ID |
| file_name | String | Uploaded CSV filename |
| status | String | Job status (pending, processing, completed, failed) |
| row_count_raw | Integer | Original row count |
| row_count_clean | Integer | Row count after cleaning |
| risk_level | String | Risk assessment level |
| summary | String | Generated transaction summary |
| error_message | String | Processing error details |
| created_at | Timestamp | Job creation time |
| completed_at | Timestamp | Job completion time |

### Transactions Table

Stores processed transaction records.

| Column | Type | Description |
|----------|----------|----------|
| id | Integer | Unique Transaction ID |
| job_id | Integer | Associated Job ID |
| txn_id | String | Transaction Identifier |
| date | String | Transaction Date |
| merchant | String | Merchant Name |
| amount | Float | Transaction Amount |
| currency | String | Transaction Currency |
| status | String | Transaction Status |
| category | String | Transaction Category |
| account_id | String | Account Identifier |
| is_anomaly | Boolean | Anomaly Flag |
| anomaly_reason | String | Reason for anomaly detection |

---
## Sample API Response

### Job Status

```json
{
  "job_id": 1,
  "status": "completed",
  "row_count_raw": 95,
  "row_count_clean": 85,
  "error_message": null
}
```

### Processing Results

```json
{
  "job_id": 1,
  "status": "completed",
  "total_transactions": 85,
  "anomaly_count": 5,
  "category_breakdown": {
    "Food": 1250.0,
    "Travel": 3200.0,
    "Shopping": 5400.0
  }
}
```

---
## Project Structure

```text
app/
├── api/
│   └── jobs.py
│
├── core/
│   └── config.py
│
├── db/
│   ├── database.py
│   └── dependencies.py
│
├── models/
│   ├── job.py
│   └── transaction.py
│
├── services/
│   └── gemini_service.py
│
├── worker/
│   ├── celery_app.py
│   └── tasks.py
│
├── main.py
│
docker-compose.yml
Dockerfile
requirements.txt
README.md
```
---

## Local Setup

### Prerequisites

- Python 3.13+
- PostgreSQL
- Redis
- Git

### Clone Repository

```bash
git clone https://github.com/IlmaxRehman/alemeno-backend-assignment.git
cd alemeno-backend-assignment
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/alemeno
GEMINI_API_KEY=your_api_key
```

### Start Redis

```bash
redis-server
```

### Start Celery Worker

```bash
celery -A app.worker.celery_app worker --pool=solo --loglevel=info
```

### Start API Server

```bash
uvicorn app.main:app --reload
```

### Open Swagger UI

```text
http://localhost:8000/docs
```

---

## Docker Deployment

### Build and Start Services

```bash
docker compose up --build
```

### Access API

```text
http://localhost:8000
```

### Access Swagger Documentation

```text
http://localhost:8000/docs
```

### Stop Services

```bash
docker compose down
```

---

## Design Decisions

### Asynchronous Processing

Celery and Redis were used to process uploaded CSV files asynchronously, preventing long-running operations from blocking API requests.

### PostgreSQL Persistence

A relational database was selected to maintain transaction integrity and provide structured storage for jobs and processed records.

### Rule-Based Anomaly Detection

The implementation uses deterministic rules to provide explainable anomaly detection without requiring model training.

### AI-Assisted Enrichment

Gemini integration is used to enrich missing transaction categories and generate summaries. Fallback logic ensures system reliability when external AI services are unavailable.

### Dockerized Architecture

Docker Compose enables consistent development and deployment across environments.

---

## Future Improvements

- Replace rule-based anomaly detection with machine learning models.
- Add authentication and role-based access control.
- Support large-scale batch uploads.
- Introduce monitoring and observability dashboards.
- Migrate to the latest Google GenAI SDK.
- Add automated testing and CI/CD pipelines.
- Deploy to AWS, Azure, or GCP.

---