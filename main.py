import os
from pathlib import Path
from glob import glob
from tqdm import tqdm
import shutil
import random

from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import asyncio
from dotenv import load_dotenv
from chromadb import PersistentClient

# Import functions
from src.pdf_to_img import process_single_pdf
from src.page_data_model_dev import convert_png_dir_to_proto_dm_async
from src.emedding_dm import embed_data_models_async
from src.section_to_entity_dev import build_cluster_dev_graph_workflow
from states.cluster_dev_state import ClusterDevState
from src.logging_config import get_logger

## Define paths
from config import BASE_PATH, ARTIFACTS_PATH, forms_pdf_dir_path, forms_png_dir_path, forms_proto_dm_dir_path, chroma_db_client_path, master_collection_name, collection_name

logger = get_logger(__name__)

client = PersistentClient(path=chroma_db_client_path)
master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
sectional_collection = client.get_or_create_collection(name=collection_name)

async def main():

    logger.info("process_started")

    ## 01. Convert pdfs to pngs
    logger.info("step_started", step=1, description="Converting PDFs to PNGs")
    forms_pdf_all_paths = glob(os.path.join(forms_pdf_dir_path, "*.p[dD][fF]"), recursive=True)

    if not forms_pdf_all_paths:
        logger.warning("no_pdf_files_found", directory=forms_pdf_dir_path)
    else:
        max_workers = min(multiprocessing.cpu_count()-5, len(forms_pdf_all_paths))
        
        logger.info("pdf_processing_started", pdf_count=len(forms_pdf_all_paths), max_workers=max_workers)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_pdf = {
                executor.submit(process_single_pdf, pdf_path, forms_png_dir_path): pdf_path 
                for pdf_path in forms_pdf_all_paths
            }
            
            with tqdm(total=len(forms_pdf_all_paths)) as pbar:
                for future in as_completed(future_to_pdf):
                    form_name, success, error = future.result()
                    if success:
                        logger.debug("pdf_processed", form_name=form_name)
                        pbar.set_description(f"✓ {form_name}")
                    else:
                        logger.error("pdf_processing_failed", form_name=form_name, error=error)
                        pbar.set_description(f"✗ {form_name} - Error: {error}")
                    pbar.update(1)

    logger.info("step_completed", step=1)

    ## 02. Data Model Generation
    logger.info("step_started", step=2, description="Developing Proto Data Models (page level)")
    form_png_dir_paths = glob(os.path.join(forms_png_dir_path, "*"))

    if not form_png_dir_paths:
        logger.warning("no_png_directories_found", directory=forms_png_dir_path)
    else:
        tasks = [
            convert_png_dir_to_proto_dm_async(
                form_png_dir_path,
                os.path.join(forms_proto_dm_dir_path, os.path.basename(form_png_dir_path))
            )
            for form_png_dir_path in form_png_dir_paths
        ]
        
        results = []
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            form_pdf_name = await coro
            logger.info("proto_data_model_created", form_pdf_name=form_pdf_name)
            results.append(form_pdf_name)

    logger.info("step_completed", step=2)

    ## 03. Embed the data models
    logger.info("step_started", step=3, description="Embed the proto data models")
    form_proto_dm_dir_paths = glob(os.path.join(forms_proto_dm_dir_path, "*"))
    
    for form_proto_dm_dir_path in tqdm(form_proto_dm_dir_paths):
        await embed_data_models_async(form_proto_dm_dir_path)
        
        form_pdf_name = os.path.basename(form_proto_dm_dir_path)
        logger.info("proto_data_model_embedded", form_pdf_name=form_pdf_name)
    
    logger.info("step_completed", step=3)

    ## 04. Knowledge graph entity development
    logger.info("step_started", step=4, description="Develop Entities for KG using extracted sectional information")

    section_col_dict = sectional_collection.get(include=['embeddings', 'documents', 'metadatas'])

    section_embeddings, section_descs, section_headings, section_proto_dm_meta = section_col_dict['embeddings'], section_col_dict['documents'], section_col_dict['metadatas'], section_col_dict['metadatas']
    section_headings = [l['sectional_headings'] for l in section_headings]
    section_proto_dm = [l['sectional_dm'] for l in section_proto_dm_meta]

    sections = list(zip(section_headings, section_descs, section_embeddings, section_proto_dm))
    random.shuffle(sections)
    section_headings, section_descs, section_embeddings, section_proto_dm = zip(*sections)
    
    logger.debug("sections_loaded", section_count=len(section_headings))
    graph = build_cluster_dev_graph_workflow()

    for (sec_heading, sec_desc, sec_emb, sec_dm) in zip(section_headings, section_descs, section_embeddings, section_proto_dm):
        initial_state: ClusterDevState = {
            "section": {
                "description": sec_desc,
                "embedding": sec_emb,
                "proto_heading": sec_heading,
                "proto_dm": sec_dm
            }
        }

        logger.info("processing_section", section_heading=sec_heading)

        result = graph.invoke(initial_state)
        logger.info("section_processed", 
                    section_heading=sec_heading,
                    section_matched=result.get('section_entity_match_bool'),
                    matched_entity_id=result.get('matched_entity_id', ''))
    
        if result.get('master_kg_entity'):
            logger.info("master_entity_info",
                       entity_heading=result['master_kg_entity'].get('heading', 'N/A'),
                       improvement_required=result.get('entity_improvement_required_bool', False))
        
        master_entity_ids = master_kg_entity_collection.get()['ids']
        logger.debug("master_kg_entities", entity_count=len(master_entity_ids), entity_ids=master_entity_ids)

    logger.info("step_completed", step=4)

    logger.info("all_tasks_completed")


if __name__=="__main__":
    asyncio.run(main())