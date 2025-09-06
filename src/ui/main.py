"""
Main Streamlit application for PDF data extraction.
"""

import streamlit as st
import os
import logging
from datetime import datetime
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the src directory to Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.database import DatabaseManager
from models.schemas import ExtractionConfig
from services.openai_service import OpenAIService
from services.extraction_service import ExtractionService
from dotenv import load_dotenv

def initialize_services():
    """Initialize all services."""
    try:
        # Initialize database
        db_manager = DatabaseManager()
        
        # Initialize OpenAI service
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            st.error("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            return None, None, None
        
        openai_service = OpenAIService(openai_api_key)
        
        # Initialize extraction service
        extraction_service = ExtractionService(db_manager, openai_service)
        
        return db_manager, openai_service, extraction_service
        
    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        return None, None, None


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="LLM PDF Extractor",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📄 LLM PDF Extractor")
    st.markdown("Extract structured data from PDF forms using AI")
    
    # Initialize services
    db_manager, openai_service, extraction_service = initialize_services()
    
    if not all([db_manager, openai_service, extraction_service]):
        st.stop()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Form type selection
        form_templates = extraction_service.get_form_templates()
        template_names = [t["name"] for t in form_templates]
        selected_template = st.selectbox("Form Template", template_names)
        
        # Get selected template details
        selected_template_data = next(
            (t for t in form_templates if t["name"] == selected_template), 
            None
        )
        
        if selected_template_data:
            st.info(f"**Template:** {selected_template_data['description']}")
            st.write("**Fields to extract:**")
            for field in selected_template_data["extraction_fields"]:
                st.write(f"• {field}")
        
        # AI model configuration
        st.subheader("AI Model Settings")
        model_name = st.selectbox(
            "Model", 
            ["gpt-5-nano", "gpt-5-mini", "gpt-5"],
            help="Select the OpenAI model to use for extraction"
        )
        
        
        max_tokens = st.slider(
            "Max Tokens", 
            min_value=100, 
            max_value=4000, 
            value=1000, 
            step=100,
            help="Maximum number of tokens in the response"
        )
        
        # Custom fields
        st.subheader("Custom Fields")
        custom_fields = st.text_area(
            "Additional Fields (one per line)",
            help="Enter additional fields to extract, one per line"
        )
        
        if custom_fields:
            additional_fields = [f.strip() for f in custom_fields.split('\n') if f.strip()]
        else:
            additional_fields = []
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Extract", "📊 Results", "⚙️ Settings"])
    
    with tab1:
        st.header("Upload PDF and Extract Data")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF form to extract data from"
        )
        
        if uploaded_file is not None:
            # Display file info
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.1f} KB",
                "File type": uploaded_file.type
            }
            
            col1, col2 = st.columns(2)
            with col1:
                st.json(file_details)
            
            with col2:
                if st.button("🔍 Preview PDF Content", type="secondary"):
                    try:
                        # Read file content
                        file_content = uploaded_file.read()
                        
                        # Extract text for preview
                        from services.pdf_processor import PDFProcessor
                        pdf_processor = PDFProcessor()
                        success, text, error = pdf_processor.extract_text(file_content)
                        
                        if success:
                            st.text_area("Extracted Text Preview", text[:2000] + "..." if len(text) > 2000 else text, height=300)
                        else:
                            st.error(f"Failed to extract text: {error}")
                    except Exception as e:
                        st.error(f"Error previewing PDF: {e}")
            
            # Extraction configuration
            st.subheader("Extraction Configuration")
            
            # Combine template fields with custom fields
            if selected_template_data:
                all_fields = selected_template_data["extraction_fields"] + additional_fields
            else:
                all_fields = additional_fields
            
            if all_fields:
                st.write("**Fields to extract:**")
                for i, field in enumerate(all_fields):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {field}")
                    with col2:
                        if st.button(f"Remove", key=f"remove_{i}"):
                            all_fields.pop(i)
                            st.rerun()
                
                # Start extraction
                if st.button("🚀 Start Extraction", type="primary"):
                    try:
                        with st.spinner("Processing PDF..."):
                            # Create extraction config
                            config = ExtractionConfig(
                                form_type=selected_template,
                                extraction_fields=all_fields,
                                model_name=model_name,
                                max_tokens=max_tokens
                            )
                            
                            # Process the file
                            file_content = uploaded_file.read()
                            result = extraction_service.process_pdf_file(
                                file_content, 
                                uploaded_file.name, 
                                config
                            )
                            
                            if result.success:
                                st.success("✅ Extraction completed successfully!")
                                
                                # Display results
                                st.subheader("Extracted Data")
                                
                                # Create results dataframe
                                results_data = []
                                for data in result.extracted_data:
                                    results_data.append({
                                        "Field": data.field_name,
                                        "Value": data.field_value,
                                        "Confidence": f"{data.confidence_score:.2%}" if data.confidence_score else "N/A"
                                    })
                                
                                df = pd.DataFrame(results_data)
                                st.dataframe(df, use_container_width=True)
                                
                                # Processing stats
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Processing Time", f"{result.processing_time:.2f}s")
                                with col2:
                                    st.metric("Fields Extracted", len(result.extracted_data))
                                with col3:
                                    st.metric("Success Rate", f"{(sum(1 for d in result.extracted_data if d.field_value != 'Not found') / len(result.extracted_data)) * 100:.1f}%")
                                
                                # Store in session state for results tab
                                st.session_state.last_result = result
                                
                            else:
                                st.error(f"❌ Extraction failed: {result.error_message}")
                                
                    except Exception as e:
                        st.error(f"❌ Error during extraction: {e}")
                        logger.error(f"Extraction error: {e}")
            else:
                st.warning("⚠️ Please add fields to extract before starting extraction.")
    
    with tab2:
        st.header("Extraction Results & History")
        
        # Show last result if available
        if 'last_result' in st.session_state:
            st.subheader("Last Extraction Result")
            result = st.session_state.last_result
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Filename", result.form_metadata.filename)
                st.metric("Form Type", result.form_metadata.form_type)
                st.metric("Status", result.form_metadata.processing_status)
            
            with col2:
                st.metric("Processing Time", f"{result.processing_time:.2f}s")
                st.metric("Fields Extracted", len(result.extracted_data))
                st.metric("Success Rate", f"{(sum(1 for d in result.extracted_data if d.field_value != 'Not found') / len(result.extracted_data)) * 100:.1f}%")
            
            st.divider()
        
        # Show extraction history
        st.subheader("Extraction History")
        
        try:
            history = extraction_service.get_extraction_history(limit=20)
            
            if history:
                # Create history dataframe
                history_data = []
                for item in history:
                    form = item["form"]
                    history_data.append({
                        "ID": form.id,
                        "Filename": form.filename,
                        "Form Type": form.form_type,
                        "Status": form.processing_status,
                        "Upload Date": form.upload_date.strftime("%Y-%m-%d %H:%M"),
                        "Fields Extracted": item["data_count"],
                        "File Size": f"{form.file_size / 1024:.1f} KB"
                    })
                
                history_df = pd.DataFrame(history_data)
                st.dataframe(history_df, use_container_width=True)
                
                # Allow viewing details of specific extractions
                selected_id = st.selectbox(
                    "View details for extraction ID:",
                    [item["form"].id for item in history]
                )
                
                if selected_id:
                    selected_form = next(item for item in history if item["form"].id == selected_id)
                    st.subheader(f"Details for Extraction {selected_id}")
                    
                    # Show form metadata
                    form = selected_form["form"]
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Filename:** {form.filename}")
                        st.write(f"**Form Type:** {form.form_type}")
                        st.write(f"**Status:** {form.processing_status}")
                    
                    with col2:
                        st.write(f"**Upload Date:** {form.upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**File Size:** {form.file_size / 1024:.1f} KB")
                        if form.error_message:
                            st.write(f"**Error:** {form.error_message}")
                    
                    # Show extracted data
                    if selected_form["extracted_data"]:
                        st.subheader("Extracted Data")
                        data_list = []
                        for data in selected_form["extracted_data"]:
                            data_list.append({
                                "Field": data.field_name,
                                "Value": data.field_value,
                                "Confidence": f"{data.confidence_score:.2%}" if data.confidence_score else "N/A",
                                "Extraction Date": data.extraction_date.strftime("%Y-%m-%d %H:%M:%S")
                            })
                        
                        data_df = pd.DataFrame(data_list)
                        st.dataframe(data_df, use_container_width=True)
                    else:
                        st.info("No extracted data available for this form.")
            else:
                st.info("No extraction history available.")
                
        except Exception as e:
            st.error(f"Error loading extraction history: {e}")
    
    with tab3:
        st.header("Application Settings")
        
        # API Key validation
        st.subheader("OpenAI API Configuration")
        
        if openai_service:
            try:
                is_valid = openai_service.validate_api_key()
                if is_valid:
                    st.success("✅ OpenAI API key is valid")
                else:
                    st.error("❌ OpenAI API key is invalid")
            except Exception as e:
                st.error(f"❌ Error validating API key: {e}")
        
        # Form templates management
        st.subheader("Form Templates")
        
        if st.button("🔄 Refresh Templates"):
            st.rerun()
        
        # Show existing templates
        templates = extraction_service.get_form_templates()
        if templates:
            for template in templates:
                with st.expander(f"📋 {template['name']}"):
                    st.write(f"**Description:** {template['description']}")
                    st.write(f"**Fields:** {', '.join(template['extraction_fields'])}")
                    if template['example_prompt']:
                        st.write(f"**Example Prompt:** {template['example_prompt']}")
        
        # Create new template
        st.subheader("Create New Template")
        
        with st.form("new_template"):
            new_name = st.text_input("Template Name")
            new_description = st.text_area("Description")
            new_fields = st.text_area("Extraction Fields (one per line)")
            
            if st.form_submit_button("Create Template"):
                if new_name and new_description and new_fields:
                    fields_list = [f.strip() for f in new_fields.split('\n') if f.strip()]
                    
                    success = extraction_service.create_custom_template(
                        name=new_name,
                        description=new_description,
                        extraction_fields=fields_list
                    )
                    
                    if success:
                        st.success("✅ Template created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create template")
                else:
                    st.warning("⚠️ Please fill in all fields")
        
        # Database info
        st.subheader("Database Information")
        
        try:
            # Get some basic stats
            forms = db_manager.get_all_forms(limit=1000)
            total_forms = len(forms)
            completed_forms = len([f for f in forms if f.processing_status == "completed"])
            failed_forms = len([f for f in forms if f.processing_status == "failed"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Forms", total_forms)
            with col2:
                st.metric("Completed", completed_forms)
            with col3:
                st.metric("Failed", failed_forms)
            
            if st.button("🗑️ Clear All Data"):
                if st.checkbox("I understand this will delete all data"):
                    # This would need to be implemented in DatabaseManager
                    st.warning("Data clearing not implemented yet")
                    
        except Exception as e:
            st.error(f"Error getting database info: {e}")


if __name__ == "__main__":
    main()
