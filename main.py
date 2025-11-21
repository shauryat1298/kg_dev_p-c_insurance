import os
from pathlib import Path
from glob import glob
from tqdm import tqdm

from dotenv import load_dotenv

# Import functions
from src.pdf_to_img import convert_pdf_to_png
from src.page_data_model_dev import convert_png_dir_to_proto_dm


## Define paths
from config import BASE_PATH, ARTIFACTS_PATH, forms_pdf_dir_path, forms_png_dir_path, forms_proto_dm_dir_path

def main():

    ## 01. Convert pdfs to pngs
    # forms_pdf_all_paths = glob(os.path.join(forms_pdf_dir_path, "*.p[dD][fF]"), recursive=True)
    # print("Step 1: Convert PDFs to PNGs")

    # for form_pdf_path in tqdm(forms_pdf_all_paths):
    #     form_pdf_name = os.path.basename(form_pdf_path)[:-4]
    #     png_dir_path = os.path.join(forms_png_dir_path, form_pdf_name)
    #     os.makedirs(png_dir_path, exist_ok=True)

    #     convert_pdf_to_png(form_pdf_path, png_dir_path)
    
    ## 02. Data Model Generation
    form_png_dir_paths = glob(os.path.join(forms_png_dir_path, "*"))
    print("Step 2: Develop Proto Data Models (page level)")

    for form_png_dir_path in tqdm(form_png_dir_paths):
        form_pdf_name = os.path.basename(form_png_dir_path)
        form_proto_dm_dir_path = os.path.join(forms_proto_dm_dir_path, form_pdf_name)
        os.makedirs(form_proto_dm_dir_path, exist_ok=True)

        convert_png_dir_to_proto_dm(form_png_dir_path, form_proto_dm_dir_path)




if __name__=="__main__":
    main()








