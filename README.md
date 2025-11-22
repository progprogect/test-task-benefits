# Benefit Reimbursement Automation System

A full-stack application for automated benefit reimbursement processing using AI-powered invoice extraction and category matching.

## Architecture

- **Backend**: FastAPI (Python) with PostgreSQL database
- **Frontend**: React + Vite
- **File Storage**: Cloudinary
- **AI/OCR**: OpenAI GPT-4 Vision API
- **Deployment**: Railway (single instance)

## Features

- Upload invoice images (JPG, PNG, PDF) for reimbursement requests
- Automatic data extraction using OpenAI Vision API
- Intelligent category matching based on keywords
- Balance and limit validation
- Category and keyword management
- Employee balance tracking and viewing

## Project Structure

```
benefit-reimbursement-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database connection
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic services
│   │   └── api/                 # API routes
│   ├── seed_data.py             # Database seeding script
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   └── services/            # API client
│   └── package.json             # Node dependencies
├── docker/
│   └── Dockerfile               # Docker build file
├── railway.json                 # Railway configuration
└── README.md                    # This file
```

## Setup Instructions

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd benefit-reimbursement-system
   ```

2. **Set up PostgreSQL database**
   - Install PostgreSQL locally or use a cloud service
   - Create a database named `benefits_db`

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set:
   - `DATABASE_URL`: PostgreSQL connection string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name
   - `CLOUDINARY_API_KEY`: Your Cloudinary API key
   - `CLOUDINARY_API_SECRET`: Your Cloudinary API secret

4. **Set up backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python seed_data.py  # Seed initial data
   ```

5. **Set up frontend**
   ```bash
   cd ../frontend
   npm install
   ```

6. **Run the application**
   
   Terminal 1 (Backend):
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   
   Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```

7. **Access the application**
   - Frontend: http://localhost:5173
   - API docs: http://localhost:8000/docs

### Railway Deployment

1. **Create Railway account and project**

2. **Add PostgreSQL service**
   - Add PostgreSQL addon in Railway dashboard
   - Railway will automatically set `DATABASE_URL` environment variable

3. **Set environment variables**
   In Railway project settings, add:
   - `OPENAI_API_KEY`
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
   - `ENVIRONMENT=production`

4. **Deploy**
   - Connect your GitHub repository to Railway
   - Railway will automatically build and deploy using the Dockerfile

5. **Seed database**
   After first deployment, run seed script:
   ```bash
   railway run python backend/seed_data.py
   ```

## API Endpoints

### Reimbursement
- `POST /api/v1/reimbursement/submit` - Submit reimbursement request
- `GET /api/v1/reimbursement/{request_id}` - Get request details

### Employees
- `GET /api/v1/employees` - List all employees

### Categories
- `GET /api/v1/categories` - List all categories
- `POST /api/v1/categories` - Create category
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category

### Keywords
- `GET /api/v1/categories/{id}/keywords` - List keywords for category
- `POST /api/v1/categories/{id}/keywords` - Add keyword
- `DELETE /api/v1/categories/{id}/keywords/{keyword_id}` - Delete keyword

### Balances
- `GET /api/v1/employees/{employee_id}/balances` - Get employee balances

## Database Schema

- **employees**: Employee information
- **benefit_categories**: Benefit categories with limits
- **category_keywords**: Keywords for category matching
- **employee_benefit_balances**: Employee balance tracking per category
- **reimbursement_requests**: Reimbursement request records
- **invoices**: Extracted invoice data

## Technology Choices

### Backend
- **FastAPI**: Modern, fast Python web framework with automatic API documentation
- **SQLAlchemy**: Powerful ORM for database operations
- **PostgreSQL**: Robust relational database
- **Alembic**: Database migration tool

### Frontend
- **React**: Popular UI library
- **Vite**: Fast build tool
- **Axios**: HTTP client

### Services
- **OpenAI GPT-4 Vision**: OCR and intelligent category matching
- **Cloudinary**: Cloud-based file storage and management

## Testing

The system includes three test scenarios as specified:

1. **Successful reimbursement**: Valid invoice with sufficient balance
2. **Rejection**: Insufficient balance or invalid category
3. **Edge case**: Ambiguous category or missing invoice data

## Notes

- All code comments and documentation are in English
- The system processes requests synchronously (can be upgraded to async processing)
- File uploads are limited to 10MB
- Supported file types: JPG, PNG, PDF

## License

This project is created for testing purposes.

