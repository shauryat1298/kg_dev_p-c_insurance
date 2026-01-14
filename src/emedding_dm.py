import os
from pathlib import Path
from glob import glob

from chromadb import PersistentClient
import asyncio

from prompts.proto_sectional_desc import prompt_for_proto_sectional_dm
from src.utils import extract_proto_messages, generate_random_id, call_openrouter_llm_async, call_openrouter_embeddings_async
from config import chroma_db_client_path, collection_name, OPENROUTER_EMBEDDING_MODEL_NAME, SIMPLE_MODEL_NAME
from src.logging_config import get_logger

logger = get_logger(__name__)

client = PersistentClient(path=chroma_db_client_path)
collection = client.get_or_create_collection(name=collection_name)

async def embed_data_models_async(form_proto_dm_dir_path):
    page_proto_dm_paths = sorted(glob(os.path.join(form_proto_dm_dir_path, "*.proto"), recursive=True))
    
    async def process_page(page_proto_dm_path):
        try:
            page_name = os.path.basename(page_proto_dm_path)
            logger.info("extracting_page", page_name=page_name)
            with open(page_proto_dm_path, "r") as f:
                page_proto_dm = f.read()
            
            proto_dict = extract_proto_messages(page_proto_dm)
            proto_list = [v for _, v in proto_dict.items()]
            logger.debug("proto_messages_extracted", page_name=page_name, message_count=len(proto_list))
            
            async def get_sectional_desc(proto_sectional_dm):
                messages = prompt_for_proto_sectional_dm(proto_sectional_dm)
                try:
                    llm_response = await call_openrouter_llm_async(messages, SIMPLE_MODEL_NAME)
                    return llm_response
                except Exception as e:
                    logger.error("sectional_description_error", error=str(e), exc_info=True)
                    return ""
            
            sectional_desc_tasks = [get_sectional_desc(proto) for proto in proto_list]
            sectional_desc_proto_list = await asyncio.gather(*sectional_desc_tasks)
            
            logger.debug("generating_embeddings", page_name=page_name, count=len(sectional_desc_proto_list))
            embedding_list = await call_openrouter_embeddings_async(sectional_desc_proto_list, OPENROUTER_EMBEDDING_MODEL_NAME)
            
            metadata_list = [
                {
                    "sectional_headings": key, 
                    "sectional_dm": value, 
                    "page_proto_dm_path": page_proto_dm_path
                } 
                for key, value in proto_dict.items()
            ]
            ids = [f"{generate_random_id()}_{key}" for key in proto_dict.keys()]
            
            logger.info("page_processed", page_name=page_name, sections_count=len(ids))
            return {
                "documents": sectional_desc_proto_list,
                "embeddings": embedding_list,
                "ids": ids,
                "metadatas": metadata_list
            }
        except Exception as e:
            logger.error("page_processing_error", page_path=page_proto_dm_path, error=str(e), exc_info=True)
            return None
    
    logger.info("embedding_data_models_started", form_path=form_proto_dm_dir_path, page_count=len(page_proto_dm_paths))
    page_tasks = [process_page(path) for path in page_proto_dm_paths]
    results = await asyncio.gather(*page_tasks)
    
    successful_results = 0
    for result in results:
        if result:
            collection.add(
                documents=result["documents"],
                embeddings=result["embeddings"],
                ids=result["ids"],
                metadatas=result["metadatas"]
            )
            successful_results += len(result["ids"])
    
    logger.info("embedding_data_models_completed", form_path=form_proto_dm_dir_path, successful_pages=successful_results)




        




