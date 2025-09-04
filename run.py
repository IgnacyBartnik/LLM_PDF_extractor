#!/usr/bin/env python3
"""
Simple script to run the LLM PDF Extractor application.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point."""
    try:
        # Check if OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OPENAI_API_KEY environment variable is not set")
            print("Please set your OpenAI API key:")
            print("export OPENAI_API_KEY=your-api-key-here")
            print("\nOr create a .env file with your API key")
            sys.exit(1)
        
        # Import and run Streamlit app
        from ui.main import main as streamlit_main
        streamlit_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
