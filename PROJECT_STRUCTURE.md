# Project Structure

This document provides a comprehensive overview of the LLM PDF Extractor project structure.

## Directory Layout

```
llm-pdf-extractor/
├── src/                          # Source code
│   ├── models/                   # Data models and database
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite database manager
│   │   └── schemas.py           # Pydantic data schemas
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── pdf_processor.py     # PDF text extraction
│   │   ├── openai_service.py    # OpenAI API integration
│   │   └── extraction_service.py # Main orchestration service
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   └── logging.py           # Logging utilities
│   ├── ui/                      # Streamlit user interface
│   │   ├── __init__.py
│   │   └── main.py              # Main Streamlit application
│   └── tests/                   # Test suite
│       ├── __init__.py
│       └── test_pdf_processor.py # PDF processor tests
├── data/                         # Database and data storage
├── uploads/                      # Temporary file uploads
├── logs/                         # Application logs
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Development Docker setup
├── docker-compose.prod.yml      # Production Docker setup
├── .dockerignore                 # Docker build exclusions
├── Makefile                      # Development commands
├── pytest.ini                   # Test configuration
├── env.example                   # Environment variables template
├── README.md                     # Main project documentation
├── DOCKER_README.md             # Docker setup guide
├── PROJECT_STRUCTURE.md         # This file
└── run.py                       # Simple application runner
```

