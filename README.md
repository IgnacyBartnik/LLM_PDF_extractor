# LLM PDF Extractor

A Python application that extracts structured data from PDF forms using OpenAI models and presents the results through a Streamlit web interface.

## Features

- **PDF Upload & Processing**: Upload PDF forms and extract text content
- **AI-Powered Extraction**: Use OpenAI models to intelligently extract key-value pairs
- **Configurable Data Elements**: Define custom extraction fields for different form types
- **Data Storage**: SQLite database for storing extracted data and metadata
- **Web Interface**: Streamlit-based UI for easy interaction
- **Error Handling**: Robust error handling and validation
- **Testing**: Automated testing with pytest

## Architecture

```
src/
├── models/          # Data models and database schemas
├── services/        # Business logic and OpenAI integration
├── utils/           # Utility functions and helpers
├── ui/              # Streamlit UI components
└── tests/           # Test files
```

## Installation

### Option 1: Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-pdf-extractor.git
cd llm-pdf-extractor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your OpenAI API key
```

### Option 2: Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-pdf-extractor.git
cd llm-pdf-extractor
```

2. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your OpenAI API key
```

3. Build and run with Docker:
```bash
# Build the image
make docker-build

# Run the application
make docker-run
```

4. Access the application at `http://localhost:8501`

For detailed Docker setup instructions, see [DOCKER_README.md](DOCKER_README.md).

## Usage

1. Start the Streamlit application:
```bash
streamlit run src/ui/main.py
```

2. Open your browser and navigate to the provided URL

3. Upload a PDF form and configure extraction fields

4. View extracted data in the web interface

## Configuration

The application supports configurable data elements. Example configurations:

- **Customer Information**: name, email, phone, address
- **Form Details**: form_type, date, reference_number
- **Business Data**: branch_name, claim_type, amount

## Testing

Run tests with pytest:
```bash
pytest src/tests/ -v --cov=src
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details