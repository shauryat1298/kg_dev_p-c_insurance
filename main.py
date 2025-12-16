import os
from pathlib import Path
from glob import glob
from tqdm import tqdm
import shutil
import random

from dotenv import load_dotenv
from chromadb import PersistentClient

# Import functions
from src.pdf_to_img import convert_pdf_to_png
from src.page_data_model_dev import convert_png_dir_to_proto_dm
from src.emedding_dm import embed_data_models
from src.section_to_entity_dev import build_cluster_dev_graph_workflow
from states.cluster_dev_state import ClusterDevState

## Define paths
from config import BASE_PATH, ARTIFACTS_PATH, forms_pdf_dir_path, forms_png_dir_path, forms_proto_dm_dir_path, chroma_db_client_path, master_collection_name, collection_name

client = PersistentClient(path=chroma_db_client_path)
try:
    client.delete_collection(master_collection_name)
except: 
    pass
master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
sectional_collection = client.get_or_create_collection(name=collection_name)

def main():

    print("===== PROCESS STARTED =====")

    ## 01. Convert pdfs to pngs
    # print("\nStep 1: Converting PDFs to PNGs...")
    # forms_pdf_all_paths = glob(os.path.join(forms_pdf_dir_path, "*.p[dD][fF]"), recursive=True)

    # if not forms_pdf_all_paths:
    #     print("No PDF files found.")
    # else:
    #     for form_pdf_path in tqdm(forms_pdf_all_paths):
    #         form_pdf_name = os.path.basename(form_pdf_path)[:-4]
    #         png_dir_path = os.path.join(forms_png_dir_path, form_pdf_name)
    #         os.makedirs(png_dir_path, exist_ok=True)

    #         convert_pdf_to_png(form_pdf_path, png_dir_path)
    #         print(f"✓ Converted: {form_pdf_name}")

    # print("Step 1 Completed.\n")

    ## 02. Data Model Generation
    # print("Step 2: Developing Proto Data Models (page level)...")
    # form_png_dir_paths = glob(os.path.join(forms_png_dir_path, "*"))

    # if not form_png_dir_paths:
    #     print("No PNG directories found.")
    # else:
    #     for _, form_png_dir_path in tqdm(enumerate(form_png_dir_paths)):
    #         form_pdf_name = os.path.basename(form_png_dir_path)
    #         form_proto_dm_dir_path = os.path.join(forms_proto_dm_dir_path, form_pdf_name)
    #         os.makedirs(form_proto_dm_dir_path, exist_ok=True)

    #         convert_png_dir_to_proto_dm(form_png_dir_path, form_proto_dm_dir_path)
    #         print(f"✓ Proto Data Model Created: {form_pdf_name}")


    # print("Step 2 Completed.\n")

    ## 03. Embed the data models
    # print("Step 3: Embed the proto data models")
    # form_proto_dm_dir_paths = glob(os.path.join(forms_proto_dm_dir_path, "*"))
    # for form_proto_dm_dir_path in tqdm(form_proto_dm_dir_paths):
    #     embed_data_models(form_proto_dm_dir_path)

    #     form_pdf_name = os.path.basename(form_proto_dm_dir_path)
    #     print(f"✓ Proto Data Model Embedded: {form_pdf_name}")

    # print("Step 3 Completed.\n")

    ## 04. Knowledge graph entity development
    print("Step 4: Develop Entities for KG using extracted sectional information")

    section_col_dict = sectional_collection.get(include=['embeddings', 'documents', 'metadatas'])

    section_embeddings, section_descs, section_headings, section_proto_dm_meta = section_col_dict['embeddings'], section_col_dict['documents'], section_col_dict['metadatas'], section_col_dict['metadatas']
    section_headings = [l['sectional_headings'] for l in section_headings]
    section_proto_dm = [l['sectional_dm'] for l in section_proto_dm_meta]

    sections = list(zip(section_headings, section_descs, section_embeddings, section_proto_dm))
    random.shuffle(sections)
    section_headings, section_descs, section_embeddings, section_proto_dm = zip(*sections)
    
    master_kg_entity_collection = client.get_or_create_collection(name=master_collection_name)
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

        print(f"\nProcessing section: {sec_heading}")
        print("-" * 80)

        result = graph.invoke(initial_state)
        print(f"Section matched: {result.get('section_entity_match_bool', "No answer")} \nMatched entity id: {result.get('matched_entity_id', '')}")
    
        if result.get('master_kg_entity'):
            print(f"Master entity heading: {result['master_kg_entity'].get('heading', 'N/A')}")
            print(f"Entity improvement required: {result.get('entity_improvement_required_bool', False)}")
        
        print("Master KG entities: ", master_kg_entity_collection.get()['ids'])

    print("Step 4 Completed.\n")

    print("===== ALL TASKS COMPLETED SUCCESSFULLY =====")


if __name__=="__main__":
    main()