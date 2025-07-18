# Dar.ai PDF Generation Microservice

A FastAPI microservice that generates professional PDF documents for real estate operations, enhanced with AI-powered property analysis.

## Features

- **Property Comparison**: Generate side-by-side comparisons of two properties with AI analysis
- **Quote Generation**: Create formal price quotes for properties
- **AI-Powered Insights**: Intelligent property analysis using OpenRouter's GPT-4o-mini model

## Setup

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. Configure Environment Variables

Copy the example environment file and add your OpenRouter API key:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 3. Run the Service

```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

### Property Comparison
```
GET /compare?property_id_1=1&property_id_2=2
```
Generates a PDF comparison between two properties with AI analysis.

### Personalized Property Recommendation
```
GET /recommend?property_ids=1,2,3&contact_id=1
```
Generates a personalized PDF recommendation comparing 2-3 properties against a contact's specific preferences (budget, area, rooms, property type, location). Perfect for helping clients choose between multiple options.

### Quote Generation
```
GET /quote?property_id=1&contact_id=1
```
Generates a formal PDF quote for a property and contact.

### Data Access
```
GET /properties - List properties
GET /contacts - List contacts  
GET /properties/{id} - Get specific property
GET /contacts/{id} - Get specific contact
```

### Health Checks
```
GET / - Basic health check
GET /health - Detailed health check with LLM status
```

## Project Structure

```
comparison/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── api/                      # API routes and endpoints
│   │   ├── __init__.py
│   │   └── routes.py            # All API endpoints
│   ├── core/                     # Core configuration
│   │   ├── __init__.py
│   │   └── config.py            # Application settings
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── models.py            # Pydantic models
│   └── services/                 # Business logic
│       ├── __init__.py
│       ├── pdf_service.py       # PDF generation
│       └── llm_service.py       # AI analysis
├── data/                         # Data files
│   ├── generate-data.py         # Test data generation
│   ├── properties.json          # Property database
│   └── contacts.json            # Contact database
├── docs/                         # Documentation and samples
│   ├── test_recommendation.pdf
│   ├── test_quote_fixed.pdf
│   └── test_recommendation_3props.pdf
├── tests/                        # Test files
│   └── test_api.py              # API tests
├── main.py                       # FastAPI application entry point
├── pyproject.toml               # Project configuration
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## AI Features

The comparison PDF now includes an "AI Analysis & Recommendation" section that provides:

1. Key differences overview
2. Value analysis (price per square meter)
3. Pros and cons of each property
4. Recommendations for different buyer profiles

The AI analysis gracefully falls back to a basic comparison if the LLM service is unavailable.

## Example Usage

```bash
# Test the service
curl "http://localhost:8000/"

# Check detailed health
curl "http://localhost:8000/health"

# Generate comparison PDF
curl "http://localhost:8000/compare?property_id_1=1&property_id_2=2" --output comparison.pdf

# Generate personalized recommendation PDF
curl "http://localhost:8000/recommend?property_ids=1,2,3&contact_id=1" --output recommendation.pdf

# Generate quote PDF
curl "http://localhost:8000/quote?property_id=1&contact_id=1" --output quote.pdf
```

## Testing

Run the tests with:

```bash
pytest tests/
```
