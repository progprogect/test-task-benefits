# Technical Specifications - Required Deliverables

## 1. Working Prototype

### Implementation Approach: Custom Python-based Solution

We have implemented a **custom Python-based solution** using FastAPI for the backend and React for the frontend, rather than using low-code platforms like n8n, Make.com, or Zapier.

#### Why Custom Solution Over Low-Code Platforms (n8n, Make.com, Zapier)?

**1. Complex Multi-Step API Workflow**
- Our system requires multiple sequential API calls: Cloudinary upload → OpenAI Vision OCR → OpenAI GPT category matching → Database validation → Balance calculation
- Low-code platforms become cumbersome when orchestrating 5+ API calls with conditional logic and error handling
- The visual workflow in n8n becomes cluttered and hard to maintain with complex branching logic

**2. Data Transformation and Business Logic**
- We need sophisticated data transformations: currency conversion, balance calculations, validation rules
- Custom business logic (e.g., "if confidence < 0.7, set status to pending_review") is easier to implement and maintain in code
- Low-code platforms require workarounds and complex expressions for non-trivial logic

**3. State Management and Database Operations**
- Complex database operations (transactions, joins, aggregations) are better handled with an ORM (SQLAlchemy)
- Maintaining state across multiple steps (request → invoice → balance updates) is cleaner in code
- Database migrations and schema management are more straightforward with Alembic

**4. Error Handling and Debugging**
- Custom code provides better error handling, logging, and debugging capabilities
- Stack traces and detailed error messages are easier to track in code than in visual workflows
- Testing is more straightforward with unit tests and integration tests

**5. Scalability and Performance**
- Custom solution allows for async operations, connection pooling, and optimization
- Better control over resource usage and performance tuning
- Low-code platforms have limitations on concurrent requests and processing time

**6. Maintainability**
- Code is version-controlled, reviewable, and follows best practices (SOLID, DRY)
- Easier to onboard new developers who know Python/JavaScript
- Visual workflows in n8n can become "spaghetti code" with many nodes and connections

**7. Cost Efficiency**
- Low-code platforms charge per execution or have usage limits
- Custom solution on Railway/VPS is more cost-effective for high-volume usage
- No vendor lock-in with proprietary platforms

#### Why Not Separate OCR Service?

While we could create a separate microservice for OCR, we chose to keep it as part of the main application because:

- **Simplicity**: Fewer services to deploy, monitor, and maintain
- **Latency**: No network overhead between services (OCR is called synchronously)
- **Cost**: Single deployment is more cost-effective than multiple services
- **Complexity**: Managing service-to-service communication, error handling, and retries adds complexity
- **Current Scale**: For MVP, a monolithic approach is sufficient; we can extract services later if needed

The OCR functionality is cleanly separated as a service module (`app/services/ocr_service.py`) and can be easily extracted into a separate service if requirements change.

### Technology Stack

**Backend:**
- **FastAPI** - Modern, fast Python web framework with automatic API documentation
- **PostgreSQL** - Relational database for structured data
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migration tool
- **OpenAI GPT-4 Vision** - OCR and invoice data extraction
- **OpenAI GPT-4** - Category matching based on keywords
- **Cloudinary** - File storage for invoice images
- **httpx** - Async HTTP client for external API calls

**Frontend:**
- **React** - UI library
- **Vite** - Build tool
- **Axios** - HTTP client
- **Tailwind CSS** - Styling

**Deployment:**
- **Docker** - Containerization
- **Railway** - Hosting platform
- **Multi-stage build** - Optimized Docker image

## 2. Documentation

### Architecture Diagram

```
┌─────────────────┐
│   React Frontend │
│   (User Interface)│
└────────┬─────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                  │
│  ┌───────────────────────────────────┐  │
│  │  API Routes                        │  │
│  │  - /reimbursement/submit           │  │
│  │  - /employees                      │  │
│  │  - /categories                     │  │
│  │  - /balances                       │  │
│  └───────────┬────────────────────────┘  │
│              │                            │
│  ┌───────────▼────────────────────────┐  │
│  │  Services Layer                    │  │
│  │  - OCR Service (OpenAI Vision)      │  │
│  │  - Category Matcher (OpenAI GPT)   │  │
│  │  - Currency Converter              │  │
│  │  - Validator                       │  │
│  │  - Cloudinary Service              │  │
│  └───────────┬────────────────────────┘  │
│              │                            │
│  ┌───────────▼────────────────────────┐  │
│  │  Database Layer (SQLAlchemy)       │  │
│  │  - Employees                       │  │
│  │  - Categories & Keywords           │  │
│  │  - Balances                        │  │
│  │  - Reimbursement Requests          │  │
│  │  - Invoices                        │  │
│  └────────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │                    │
         │                    │
    ┌────▼────┐         ┌─────▼─────┐
    │Cloudinary│         │  OpenAI   │
    │  (Files) │         │   APIs    │
    └──────────┘         └───────────┘
```

### Workflow Steps

1. **User Uploads Invoice**
   - Frontend sends file to `/api/v1/reimbursement/submit`
   - Backend receives file and employee_id

2. **File Upload to Cloudinary**
   - File is uploaded to Cloudinary
   - Returns secure URL for the image

3. **OCR Extraction (OpenAI Vision)**
   - Image URL sent to GPT-4 Vision API
   - Extracts: vendor_name, purchase_date, items, total_amount, currency, invoice_number, extracted_text

4. **Category Matching (OpenAI GPT-4)**
   - Invoice text and items sent to GPT-4
   - Compares against categories and keywords from database
   - Returns category_id, confidence, matched_keywords, reasoning
   - If confidence < 0.7 or no match → status = pending_review

5. **Currency Conversion**
   - Amount converted to USD using Exchange Rate API
   - All limits compared in USD

6. **Validation**
   - Checks transaction limit
   - Checks monthly balance
   - Checks annual balance
   - If valid → status = approved, else → status = rejected

7. **Balance Update**
   - If approved, updates employee balance (stored in USD)
   - Creates invoice record

8. **Response**
   - Returns structured response with all data
   - Frontend displays result

### Setup Instructions

#### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database
- Docker (optional, for containerized deployment)

#### Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Create `.env` file:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/benefits_db
   OPENAI_API_KEY=sk-your-openai-api-key
   CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
   EXCHANGE_RATE_API_KEY=your-exchange-rate-api-key
   ENVIRONMENT=development
   ```

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Seed initial data:**
   ```bash
   python seed_data.py
   ```

5. **Start backend server:**
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API URL:**
   Update `frontend/src/services/api.js` if needed

3. **Start development server:**
   ```bash
   npm run dev
   ```

#### Railway Deployment

1. **Connect GitHub repository to Railway**

2. **Add PostgreSQL service** (Railway automatically sets `DATABASE_URL`)

3. **Set environment variables:**
   - `OPENAI_API_KEY`
   - `CLOUDINARY_URL` or individual Cloudinary variables
   - `EXCHANGE_RATE_API_KEY`
   - `ENVIRONMENT=production`

4. **Deploy:**
   - Railway automatically builds and deploys using Dockerfile

5. **Run migrations:**
   ```bash
   railway run alembic upgrade head
   railway run python backend/seed_data.py
   ```

### API/Service Choices and Rationale

#### OpenAI GPT-4 Vision for OCR
- **Why**: High accuracy in extracting structured data from invoice images
- **Alternative considered**: Tesseract OCR - but requires more preprocessing and has lower accuracy
- **Cost**: Pay-per-use, reasonable for MVP scale

#### OpenAI GPT-4 for Category Matching
- **Why**: Natural language understanding to match invoices to categories based on keywords
- **Alternative considered**: Simple keyword matching - but less flexible and accurate
- **Cost**: Pay-per-use, optimized with temperature=0.3 for consistent results

#### Cloudinary for File Storage
- **Why**: Easy integration, automatic image optimization, CDN delivery
- **Alternative considered**: AWS S3 - but requires more setup and configuration
- **Cost**: Free tier sufficient for MVP

#### Exchange Rate API (exchangerate-api.com)
- **Why**: Free tier available, reliable, supports many currencies
- **Alternative considered**: Fixer.io - but has stricter free tier limits
- **Cost**: Free tier sufficient, can upgrade if needed

#### PostgreSQL Database
- **Why**: Relational data with complex relationships (employees, categories, balances, requests)
- **Alternative considered**: MongoDB - but relational structure fits better
- **Cost**: Free tier on Railway sufficient

#### FastAPI Framework
- **Why**: Modern, fast, automatic API documentation, async support
- **Alternative considered**: Django REST Framework - but FastAPI is faster and more modern
- **Performance**: Async support for concurrent requests

### Sample Test Data

#### Employees
- John Smith (EMP001)
- Jane Doe (EMP002)
- Bob Johnson (EMP003)
- Alice Williams (EMP004)
- Charlie Brown (EMP005)

#### Categories with Keywords
1. **Wellness & Fitness** ($500/month, $5000/year)
   - Keywords: gym, fitness, yoga, workout, exercise, sports, personal trainer, fitness center

2. **Professional Development** ($500/month, $3000/year)
   - Keywords: course, training, certification, conference, workshop, book, education, learning

3. **Home Office Equipment** ($1000/month, $5000/year)
   - Keywords: monitor, keyboard, mouse, desk, chair, laptop stand, headphones, webcam

4. **Transportation** ($300/month, $2000/year)
   - Keywords: taxi, uber, fuel, parking, public transport, metro, bus, train

5. **Health & Medical** ($400/month, $3000/year)
   - Keywords: doctor, medical, pharmacy, prescription, health check, clinic, hospital

### Expected Outputs

#### Successful Reimbursement Response
```json
{
  "id": "uuid",
  "employee_id": "uuid",
  "employee_name": "John Smith",
  "employee_employee_id": "EMP001",
  "category_id": "uuid",
  "category_name": "Wellness & Fitness",
  "status": "approved",
  "amount": 50.00,
  "currency": "USD",
  "cloudinary_url": "https://res.cloudinary.com/.../invoice.png",
  "submission_timestamp": "2024-01-15T10:30:00Z",
  "rejection_reason": null,
  "remaining_balance": 450.00,
  "remaining_balance_currency": "USD",
  "invoice": {
    "vendor_name": "Fitness Center",
    "purchase_date": "2024-01-10",
    "items": [{"description": "Monthly membership", "amount": 50.00}],
    "total_amount": 50.00,
    "currency": "USD",
    "invoice_number": "INV-12345"
  }
}
```

## 3. Test Scenarios

### Test Case 1: Successful Reimbursement

**Conditions:**
- Valid invoice image
- Clear category match (e.g., gym membership)
- Sufficient balance (requested amount < remaining balance)
- Valid currency (converted to USD)

**Steps:**
1. Upload invoice image with gym/fitness content
2. System extracts invoice data via OCR
3. System matches to "Wellness & Fitness" category
4. System validates balance (e.g., $50 request, $500 limit available)
5. System approves request
6. System updates balance ($500 - $50 = $450 remaining)

**Expected Result:**
- Status: `approved`
- Category: `Wellness & Fitness`
- Remaining balance: $450.00 USD
- Balance updated in database

**Test Command:**
```bash
curl -X POST 'https://test-task-benefits-production.up.railway.app/api/v1/reimbursement/submit' \
  -F 'employee_id=<employee_id>' \
  -F 'file=@gym_invoice.png'
```

### Test Case 2: Rejection - Insufficient Balance

**Conditions:**
- Valid invoice image
- Clear category match
- Insufficient balance (requested amount > remaining balance)

**Steps:**
1. Employee has used $450 of $500 monthly limit
2. Upload invoice for $100
3. System extracts invoice data
4. System matches category correctly
5. System validates balance ($100 > $50 remaining)
6. System rejects request

**Expected Result:**
- Status: `rejected`
- Rejection reason: "Insufficient monthly balance. Remaining: $50.00 USD, Requested: $100.00 USD"
- Balance NOT updated

**Test Command:**
```bash
# First, submit requests to use up balance
# Then submit request exceeding limit
curl -X POST 'https://test-task-benefits-production.up.railway.app/api/v1/reimbursement/submit' \
  -F 'employee_id=<employee_id>' \
  -F 'file=@large_invoice.png'
```

### Test Case 3: Rejection - Wrong Category / Transaction Limit Exceeded

**Conditions:**
- Valid invoice image
- Amount exceeds category's max_transaction_amount

**Steps:**
1. Upload invoice for $600 (category limit: $500 per transaction)
2. System extracts invoice data
3. System matches category
4. System checks transaction limit ($600 > $500)
5. System rejects request

**Expected Result:**
- Status: `rejected`
- Rejection reason: "Amount $600.00 USD exceeds maximum transaction limit of $500.00 USD"
- Balance NOT updated

### Test Case 4: Edge Case - Ambiguous Category

**Conditions:**
- Valid invoice image
- Unclear or unusual invoice content
- No clear keyword matches

**Steps:**
1. Upload invoice with unclear description (e.g., "Random Store - Mystery Item XYZ123")
2. System extracts invoice data via OCR
3. System attempts category matching
4. GPT returns low confidence (< 0.7) or no match
5. System sets status to pending_review

**Expected Result:**
- Status: `pending_review`
- Category: `Not determined (pending review)`
- Balance NOT updated
- Requires manual review by admin

**Test Command:**
```bash
curl -X POST 'https://test-task-benefits-production.up.railway.app/api/v1/reimbursement/submit' \
  -F 'employee_id=<employee_id>' \
  -F 'file=@unclear_invoice.png'
```

### Test Case 5: Edge Case - Missing Invoice Data

**Conditions:**
- Invoice image with poor quality or missing fields
- OCR extracts partial data

**Steps:**
1. Upload low-quality invoice image
2. OCR extracts some fields but missing others (e.g., no total_amount)
3. System handles missing data gracefully
4. System processes available data

**Expected Result:**
- Status: `pending_review` or `rejected` (depending on validation)
- Invoice data shows available fields, null for missing ones
- Error message indicates missing required data

### Test Case 6: Edge Case - Currency Conversion

**Conditions:**
- Invoice in non-USD currency (e.g., RUB)
- Amount needs conversion to USD for comparison

**Steps:**
1. Upload invoice in RUB (e.g., 31,000 RUB)
2. System extracts currency: RUB, amount: 31000
3. System converts to USD (31,000 RUB ≈ $341 USD)
4. System compares $341 USD against $500 USD limit
5. System approves (if balance sufficient)

**Expected Result:**
- Status: `approved` (if $341 < remaining balance)
- Amount shown in original currency: 31,000 RUB
- Remaining balance shown in USD: $159.00 USD
- Balance updated in USD

**Test Command:**
```bash
curl -X POST 'https://test-task-benefits-production.up.railway.app/api/v1/reimbursement/submit' \
  -F 'employee_id=<employee_id>' \
  -F 'file=@russian_invoice.png'
```

## Summary

The custom Python-based solution provides:
- ✅ Full control over business logic and workflow
- ✅ Better error handling and debugging
- ✅ Scalable architecture ready for growth
- ✅ Cost-effective deployment
- ✅ Maintainable codebase following best practices
- ✅ Comprehensive test coverage

All three required deliverables are complete:
1. ✅ Working prototype (deployed on Railway)
2. ✅ Complete documentation (this document)
3. ✅ Test scenarios (6 test cases covering success, rejection, and edge cases)

