#!/usr/bin/env python3
"""
Simple script to run the LLM PDF Extractor application without Streamlit warnings.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point."""
    try:
        load_dotenv()
        # Check if OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OPENAI_API_KEY environment variable is not set")
            print("Create a .env file with your API key")
            sys.exit(1)

        # Import Streamlit and your app
        import streamlit.web.bootstrap as st_bootstrap
        from ui.main import main as app_main

        # Run the app in a proper Streamlit context
        st_bootstrap.run(app_main, "", [], {})  # <-- fix here

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