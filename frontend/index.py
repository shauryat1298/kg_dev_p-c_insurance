import streamlit as st
import os
import asyncio
from glob import glob
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from chromadb import PersistentClient

# Import backend functions
from src.pdf_to_img import process_single_pdf
from src.page_data_model_dev import convert_png_dir_to_proto_dm_async
from src.emedding_dm import embed_data_models_async
from src.section_to_entity_dev import build_cluster_dev_graph_workflow
from states.cluster_dev_state import ClusterDevState
from config import (
    BASE_PATH, ARTIFACTS_PATH, forms_pdf_dir_path, forms_png_dir_path, 
    forms_proto_dm_dir_path, chroma_db_client_path, master_collection_name, collection_name
)

# Page configuration
st.set_page_config(
    page_title="Insurance Data Model Builder",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure required directories exist
os.makedirs(forms_pdf_dir_path, exist_ok=True)
os.makedirs(forms_png_dir_path, exist_ok=True)
os.makedirs(forms_proto_dm_dir_path, exist_ok=True)
os.makedirs(chroma_db_client_path, exist_ok=True)

# Initialize ChromaDB clients
@st.cache_resource
def get_chroma_clients():
    client = PersistentClient(path=chroma_db_client_path)
    master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
    sectional_collection = client.get_or_create_collection(name=collection_name)
    return client, master_kg_entity_collection, sectional_collection

client, master_kg_entity_collection, sectional_collection = get_chroma_clients()

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["🏠 Home", "📤 Upload Documents", "⚙️ Process Pipeline", "📊 View Results", "🔍 Explore Entities"]
)

# Helper function to run async code
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# Home Page
if page == "🏠 Home":
    st.markdown('<div class="main-header">Insurance Data Model Builder</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <h3>Welcome to the Insurance Data Model Builder</h3>
        <p>This application helps you build comprehensive canonical data models for specialty insurance by:</p>
        <ul>
            <li>📄 Processing broker supplemental application forms</li>
            <li>🤖 Using AI agents to extract questions and structure data</li>
            <li>🔗 Clustering similar data models into entities</li>
            <li>📊 Creating a master knowledge graph</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get statistics
    try:
        master_entities = master_kg_entity_collection.get()
        sections = sectional_collection.get()
        
        num_entities = len(master_entities.get('ids', [])) if master_entities.get('ids') else 0
        num_sections = len(sections.get('ids', [])) if sections.get('ids') else 0
        
        # Count uploaded PDFs
        pdf_files = glob(os.path.join(forms_pdf_dir_path, "*.p[dD][fF]"), recursive=True)
        num_forms = len(pdf_files)
        
        # Count proto data models
        proto_dirs = glob(os.path.join(forms_proto_dm_dir_path, "*"))
        num_proto_models = len(proto_dirs)
        
    except Exception as e:
        num_entities = 0
        num_sections = 0
        num_forms = 0
        num_proto_models = 0
    
    with col1:
        st.metric("📄 Uploaded Forms", num_forms)
    with col2:
        st.metric("📋 Proto Data Models", num_proto_models)
    with col3:
        st.metric("🔗 Sections", num_sections)
    with col4:
        st.metric("⭐ Master Entities", num_entities)
    
    st.markdown("---")
    st.markdown("### Quick Start")
    st.markdown("""
    1. **Upload Documents**: Go to the Upload Documents page to add PDF forms
    2. **Process Pipeline**: Run the processing pipeline to extract and structure data
    3. **View Results**: Explore the generated data models and entities
    4. **Explore Entities**: Dive deep into individual entities and their relationships
    """)

# Upload Documents Page
elif page == "📤 Upload Documents":
    st.markdown('<div class="main-header">Upload Documents</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        Upload broker supplemental application forms (PDF files) for processing.
        Multiple files can be uploaded at once.
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) selected**")
        
        if st.button("📥 Upload Files", type="primary"):
            os.makedirs(forms_pdf_dir_path, exist_ok=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            uploaded_count = 0
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Uploading {uploaded_file.name}...")
                
                # Save file
                file_path = os.path.join(forms_pdf_dir_path, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                uploaded_count += 1
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text(f"✅ Successfully uploaded {uploaded_count} file(s)!")
            st.success(f"All files uploaded successfully!")
            st.balloons()
    
    # Show existing files
    st.markdown("---")
    st.markdown("### Existing Uploaded Files")
    
    pdf_files = glob(os.path.join(forms_pdf_dir_path, "*.p[dD][fF]"), recursive=True)
    if pdf_files:
        for pdf_file in pdf_files:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"📄 {os.path.basename(pdf_file)}")
            with col2:
                if st.button("🗑️ Delete", key=f"del_{os.path.basename(pdf_file)}"):
                    try:
                        os.remove(pdf_file)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting file: {e}")
    else:
        st.info("No files uploaded yet.")

# Process Pipeline Page
elif page == "⚙️ Process Pipeline":
    st.markdown('<div class="main-header">Process Pipeline</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        Run the complete processing pipeline to extract data models from uploaded PDFs.
        This process includes: PDF to PNG conversion, data model generation, embedding, and entity clustering.
    </div>
    """, unsafe_allow_html=True)
    
    # Check if files exist
    pdf_files = glob(os.path.join(forms_pdf_dir_path, "*.p[dD][fF]"), recursive=True)
    
    if not pdf_files:
        st.warning("⚠️ No PDF files found. Please upload files first.")
    else:
        st.info(f"📄 Found {len(pdf_files)} PDF file(s) ready for processing.")
        
        if st.button("🚀 Start Processing", type="primary"):
            # Initialize session state for progress tracking
            if 'processing' not in st.session_state:
                st.session_state.processing = False
            if 'current_step' not in st.session_state:
                st.session_state.current_step = ""
            
            st.session_state.processing = True
            
            # Create containers for each step
            step1_container = st.container()
            step2_container = st.container()
            step3_container = st.container()
            step4_container = st.container()
            
            try:
                # Step 1: Convert PDFs to PNGs
                with step1_container:
                    st.markdown("### Step 1: Converting PDFs to PNGs")
                    step1_progress = st.progress(0)
                    step1_status = st.empty()
                    
                    max_workers = min(multiprocessing.cpu_count()-5, len(pdf_files))
                    step1_status.text(f"Processing {len(pdf_files)} PDFs using {max_workers} threads...")
                    
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        future_to_pdf = {
                            executor.submit(process_single_pdf, pdf_path, forms_png_dir_path): pdf_path 
                            for pdf_path in pdf_files
                        }
                        
                        completed = 0
                        for future in as_completed(future_to_pdf):
                            form_name, success, error = future.result()
                            completed += 1
                            step1_progress.progress(completed / len(pdf_files))
                            if success:
                                step1_status.text(f"✓ Processed: {form_name}")
                            else:
                                step1_status.text(f"✗ Error in {form_name}: {error}")
                    
                    st.success("✅ Step 1 Completed: PDFs converted to PNGs")
                
                # Step 2: Data Model Generation
                with step2_container:
                    st.markdown("### Step 2: Developing Proto Data Models")
                    step2_progress = st.progress(0)
                    step2_status = st.empty()
                    
                    form_png_dir_paths = glob(os.path.join(forms_png_dir_path, "*"))
                    
                    if form_png_dir_paths:
                        total = len(form_png_dir_paths)
                        completed = [0]  # Use list to allow modification in nested function
                        
                        async def process_forms():
                            tasks = [
                                convert_png_dir_to_proto_dm_async(
                                    form_png_dir_path,
                                    os.path.join(forms_proto_dm_dir_path, os.path.basename(form_png_dir_path))
                                )
                                for form_png_dir_path in form_png_dir_paths
                            ]
                            
                            for coro in asyncio.as_completed(tasks):
                                form_pdf_name = await coro
                                completed[0] += 1
                                step2_progress.progress(completed[0] / total)
                                step2_status.text(f"✓ Proto Data Model Created: {form_pdf_name}")
                        
                        run_async(process_forms())
                        st.success("✅ Step 2 Completed: Proto Data Models Generated")
                    else:
                        st.warning("No PNG directories found.")
                
                # Step 3: Embed Data Models
                with step3_container:
                    st.markdown("### Step 3: Embedding Data Models")
                    step3_progress = st.progress(0)
                    step3_status = st.empty()
                    
                    form_proto_dm_dir_paths = glob(os.path.join(forms_proto_dm_dir_path, "*"))
                    
                    if form_proto_dm_dir_paths:
                        total = len(form_proto_dm_dir_paths)
                        completed = [0]  # Use list to allow modification in nested function
                        
                        async def embed_forms():
                            for form_proto_dm_dir_path in form_proto_dm_dir_paths:
                                await embed_data_models_async(form_proto_dm_dir_path)
                                form_pdf_name = os.path.basename(form_proto_dm_dir_path)
                                completed[0] += 1
                                step3_progress.progress(completed[0] / total)
                                step3_status.text(f"✓ Embedded: {form_pdf_name}")
                        
                        run_async(embed_forms())
                        st.success("✅ Step 3 Completed: Data Models Embedded")
                    else:
                        st.warning("No proto data model directories found.")
                
                # Step 4: Knowledge Graph Entity Development
                with step4_container:
                    st.markdown("### Step 4: Developing Knowledge Graph Entities")
                    step4_progress = st.progress(0)
                    step4_status = st.empty()
                    
                    section_col_dict = sectional_collection.get(include=['embeddings', 'documents', 'metadatas'])
                    
                    section_embeddings, section_descs, section_headings, section_proto_dm_meta = section_col_dict['embeddings'], section_col_dict['documents'], section_col_dict['metadatas'], section_col_dict['metadatas']
                    section_headings = [l['sectional_headings'] for l in section_headings]
                    section_proto_dm = [l['sectional_dm'] for l in section_proto_dm_meta]
                    

                    sections = list(zip(section_headings, section_descs, section_embeddings, section_proto_dm))
                    random.shuffle(sections)
                    section_headings, section_descs, section_embeddings, section_proto_dm = zip(*sections)
                    
                    graph = build_cluster_dev_graph_workflow()
                    
                    total = len(section_headings)
                    completed = 0
                    
                    for (sec_heading, sec_desc, sec_emb, sec_dm) in zip(section_headings, section_descs, section_embeddings, section_proto_dm):
                        initial_state: ClusterDevState = {
                            "section": {
                                "description": sec_desc,
                                "embedding": sec_emb,
                                "proto_heading": sec_heading,
                                "proto_dm": sec_dm
                            }
                        }
                        
                        step4_status.text(f"Processing section: {sec_heading}")
                        result = graph.invoke(initial_state)
                        
                        completed += 1
                        step4_progress.progress(completed / total)
                        
                        if result.get('master_kg_entity'):
                            step4_status.text(f"✓ Processed: {sec_heading} → {result['master_kg_entity'].get('heading', 'N/A')}")
                    
                    st.success("✅ Step 4 Completed: Knowledge Graph Entities Developed")
                
                st.markdown("---")
                st.markdown('<div class="success-box"><h3>🎉 All Processing Steps Completed Successfully!</h3></div>', unsafe_allow_html=True)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error during processing: {str(e)}")
                st.exception(e)
            finally:
                st.session_state.processing = False

# View Results Page
elif page == "📊 View Results":
    st.markdown('<div class="main-header">View Results</div>', unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Master Entities", "🔗 Sections", "📄 Forms Overview"])
    
    with tab1:
        st.markdown("### Master Knowledge Graph Entities")
        
        try:
            master_entities = master_kg_entity_collection.get(include=['documents', 'metadatas'])
            
            if master_entities.get('ids'):
                st.info(f"Found {len(master_entities['ids'])} master entities")
                
                for idx, entity_id in enumerate(master_entities['ids']):
                    with st.expander(f"⭐ {entity_id}", expanded=False):
                        entity_desc = master_entities['documents'][idx] if master_entities.get('documents') else "N/A"
                        entity_meta = master_entities['metadatas'][idx] if master_entities.get('metadatas') else {}
                        entity_proto_dm = entity_meta.get('proto_dm', 'N/A')
                        
                        st.markdown(f"**Description:** {entity_desc}")
                        st.markdown("**Proto Data Model:**")
                        st.code(entity_proto_dm, language='protobuf')
            else:
                st.info("No master entities found. Run the processing pipeline first.")
        except Exception as e:
            st.error(f"Error loading entities: {str(e)}")
    
    with tab2:
        st.markdown("### Extracted Sections")
        
        try:
            sections = sectional_collection.get(include=['documents', 'metadatas'])
            
            if sections.get('ids'):
                st.info(f"Found {len(sections['ids'])} sections")
                
                # Search/filter
                search_term = st.text_input("🔍 Search sections", "")
                
                filtered_sections = []
                if search_term:
                    for idx, section_id in enumerate(sections['ids']):
                        section_desc = sections['documents'][idx] if sections.get('documents') else ""
                        section_meta = sections['metadatas'][idx] if sections.get('metadatas') else {}
                        section_heading = section_meta.get('sectional_headings', '')
                        
                        if search_term.lower() in section_desc.lower() or search_term.lower() in section_heading.lower():
                            filtered_sections.append((idx, section_id, section_desc, section_meta))
                else:
                    for idx, section_id in enumerate(sections['ids']):
                        section_desc = sections['documents'][idx] if sections.get('documents') else ""
                        section_meta = sections['metadatas'][idx] if sections.get('metadatas') else {}
                        filtered_sections.append((idx, section_id, section_desc, section_meta))
                
                for idx, section_id, section_desc, section_meta in filtered_sections:
                    with st.expander(f"🔗 {section_meta.get('sectional_headings', section_id)}", expanded=False):
                        st.markdown(f"**Description:** {section_desc}")
                        st.markdown(f"**Source:** {section_meta.get('page_proto_dm_path', 'N/A')}")
                        st.markdown("**Proto Data Model:**")
                        st.code(section_meta.get('sectional_dm', 'N/A'), language='protobuf')
            else:
                st.info("No sections found. Run the processing pipeline first.")
        except Exception as e:
            st.error(f"Error loading sections: {str(e)}")
    
    with tab3:
        st.markdown("### Forms Overview")
        
        # List uploaded PDFs
        pdf_files = glob(os.path.join(forms_pdf_dir_path, "*.p[dD][fF]"), recursive=True)
        if pdf_files:
            st.info(f"Found {len(pdf_files)} uploaded form(s)")
            
            for pdf_file in pdf_files:
                form_name = os.path.basename(pdf_file)
                with st.expander(f"📄 {form_name}", expanded=False):
                    # Check for corresponding PNG directory
                    png_dir = os.path.join(forms_png_dir_path, form_name.replace('.pdf', ''))
                    if os.path.exists(png_dir):
                        png_files = glob(os.path.join(png_dir, "*.png"))
                        st.write(f"**Pages:** {len(png_files)}")
                    
                    # Check for proto data model
                    proto_dir = os.path.join(forms_proto_dm_dir_path, form_name.replace('.pdf', ''))
                    if os.path.exists(proto_dir):
                        proto_files = glob(os.path.join(proto_dir, "*.proto"))
                        st.write(f"**Proto Data Models:** {len(proto_files)}")
        else:
            st.info("No forms uploaded yet.")

# Explore Entities Page
elif page == "🔍 Explore Entities":
    st.markdown('<div class="main-header">Explore Entities</div>', unsafe_allow_html=True)
    
    try:
        master_entities = master_kg_entity_collection.get(include=['documents', 'metadatas'])
        
        if master_entities.get('ids'):
            entity_names = master_entities['ids']
            
            selected_entity = st.selectbox(
                "Select an entity to explore",
                entity_names
            )
            
            if selected_entity:
                idx = entity_names.index(selected_entity)
                entity_desc = master_entities['documents'][idx] if master_entities.get('documents') else "N/A"
                entity_meta = master_entities['metadatas'][idx] if master_entities.get('metadatas') else {}
                entity_proto_dm = entity_meta.get('proto_dm', 'N/A')
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### Entity Information")
                    st.markdown(f"**Entity ID:** `{selected_entity}`")
                    st.markdown(f"**Description:** {entity_desc}")
                
                with col2:
                    st.markdown("### Statistics")
                    # Count related sections
                    sections = sectional_collection.get(include=['metadatas'])
                    related_count = 0
                    if sections.get('metadatas'):
                        for meta in sections['metadatas']:
                            # Simple check - could be improved with semantic similarity
                            if selected_entity.lower() in str(meta).lower():
                                related_count += 1
                    
                    st.metric("Related Sections", related_count)
                
                st.markdown("---")
                st.markdown("### Proto Data Model")
                st.code(entity_proto_dm, language='protobuf')
                
                # Download button
                st.download_button(
                    label="📥 Download Proto Data Model",
                    data=entity_proto_dm,
                    file_name=f"{selected_entity}.proto",
                    mime="text/plain"
                )
        else:
            st.info("No entities found. Run the processing pipeline first.")
    except Exception as e:
        st.error(f"Error loading entities: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Insurance Data Model Builder | Built with Streamlit</div>",
    unsafe_allow_html=True
)

