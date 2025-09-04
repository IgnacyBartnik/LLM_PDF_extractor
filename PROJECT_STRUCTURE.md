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

## Core Components

### 1. Data Models (`src/models/`)

#### `schemas.py`
- **ExtractionConfig**: Configuration for data extraction
- **FormMetadata**: Metadata about uploaded forms
- **ExtractedData**: Individual extracted data fields
- **ExtractionResult**: Complete extraction results
- **FormTypeTemplate**: Templates for different form types

#### `database.py`
- **DatabaseManager**: SQLite database operations
- Table creation and management
- CRUD operations for forms and extracted data
- Form template management

### 2. Services (`src/services/`)

#### `pdf_processor.py`
- **PDFProcessor**: PDF file handling and text extraction
- File validation and size limits
- Text extraction from multiple pages
- Error handling for corrupted files

#### `openai_service.py`
- **OpenAIService**: OpenAI API integration
- Structured data extraction prompts
- Retry logic and error handling
- Response parsing and validation

#### `extraction_service.py`
- **ExtractionService**: Main orchestration service
- Coordinates PDF processing and AI extraction
- Manages extraction workflow
- Handles form templates and history

### 3. User Interface (`src/ui/`)

#### `main.py`
- **Streamlit Application**: Web-based user interface
- File upload and processing
- Configuration management
- Results display and history
- Settings and administration

### 4. Utilities (`src/utils/`)

#### `config.py`
- Configuration loading from environment/files
- Configuration validation
- Default configuration creation

#### `logging.py`
- Logging setup and configuration
- Log level management
- File and console logging

## Data Flow

```
1. User Upload → PDF File
2. PDF Processing → Text Extraction
3. AI Processing → Structured Data
4. Data Storage → SQLite Database
5. Results Display → Streamlit UI
```

## Key Features

### PDF Processing
- **Multi-page support**: Handles PDFs with multiple pages
- **Text extraction**: Extracts readable text from PDFs
- **File validation**: Checks file size and format
- **Error handling**: Graceful handling of corrupted files

### AI-Powered Extraction
- **Configurable fields**: Define what data to extract
- **Template system**: Pre-defined extraction templates
- **Confidence scores**: AI confidence in extractions
- **Reasoning**: AI explanations for extractions

### Data Management
- **Persistent storage**: SQLite database for all data
- **Extraction history**: Track all processing attempts
- **Template management**: Create and manage form templates
- **Data export**: Results in structured format

### User Interface
- **Intuitive design**: Clean, modern Streamlit interface
- **Real-time processing**: Live updates during extraction
- **Configuration options**: Adjustable AI parameters
- **Results visualization**: Clear display of extracted data

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required OpenAI API key
- `DATABASE_PATH`: Database file location
- `LOG_LEVEL`: Logging verbosity
- `MAX_FILE_SIZE`: Maximum PDF file size
- `DEFAULT_MODEL`: Default AI model
- `DEFAULT_TEMPERATURE`: AI response randomness

### Form Templates
- **Customer Registration**: Basic customer information
- **Insurance Claim**: Claim and policy details
- **Loan Application**: Financial and personal data
- **Custom Templates**: User-defined extraction fields

## Testing

### Test Structure
- **Unit tests**: Individual component testing
- **Integration tests**: Service interaction testing
- **Mock testing**: External API simulation
- **Coverage reporting**: Code coverage metrics

### Test Commands
```bash
# Run all tests
make test

# Run with coverage
pytest --cov=src

# Run specific test file
pytest src/tests/test_pdf_processor.py
```

## Docker Support

### Development
- **Local development**: Easy setup and testing
- **Volume mounting**: Persistent data storage
- **Environment variables**: Flexible configuration

### Production
- **Optimized images**: Multi-stage builds
- **Health checks**: Application monitoring
- **Resource limits**: Memory and CPU constraints
- **Scaling**: Horizontal scaling support

## Security Features

- **Non-root containers**: Secure Docker execution
- **File validation**: Prevents malicious file uploads
- **API key protection**: Secure credential management
- **Input sanitization**: Prevents injection attacks

## Performance Considerations

- **Async processing**: Non-blocking operations
- **Memory management**: Efficient PDF handling
- **Caching**: Redis integration for performance
- **Resource limits**: Docker resource constraints

## Monitoring and Logging

- **Structured logging**: Consistent log format
- **Performance metrics**: Processing time tracking
- **Error tracking**: Comprehensive error logging
- **Health checks**: Application status monitoring

## Future Enhancements

- **Multi-language support**: Internationalization
- **Advanced AI models**: Support for other LLMs
- **Cloud integration**: AWS, Azure, GCP support
- **API endpoints**: RESTful API for integration
- **Batch processing**: Multiple file processing
- **Machine learning**: Custom model training
