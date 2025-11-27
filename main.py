import os
from pathlib import Path
from glob import glob
from tqdm import tqdm

from dotenv import load_dotenv

# Import functions
from src.pdf_to_img import convert_pdf_to_png
from src.page_data_model_dev import convert_png_dir_to_proto_dm
from src.emedding_dm import embed_data_models

## Define paths
from config import BASE_PATH, ARTIFACTS_PATH, forms_pdf_dir_path, forms_png_dir_path, forms_proto_dm_dir_path

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
    print("Step 3: Embed the proto data models")
    form_proto_dm_dir_paths = glob(os.path.join(forms_proto_dm_dir_path, "*"))
    for form_proto_dm_dir_path in tqdm(form_proto_dm_dir_paths):
        embed_data_models(form_proto_dm_dir_path)

        form_pdf_name = os.path.basename(form_proto_dm_dir_path)
        print(f"✓ Proto Data Model Embedded: {form_pdf_name}")
        break

    print("Step 3 Completed.\n")

    print("===== ALL TASKS COMPLETED SUCCESSFULLY =====")


if __name__=="__main__":
    main()
