import os
from glob import glob
from tqdm import tqdm

# Import functions
from src.pdf_to_img import convert_pdf_to_png


## Define paths
from config import BASE_PATH, ARTIFACTS_PATH, forms_pdf_dir_path, forms_png_dir_path

def main():

    ## 01. Convert pdfs to pngs
    forms_pdf_all_paths = glob(os.path.join(forms_pdf_dir_path, "*.p[dD][fF]"), recursive=True)
    for form_pdf_path in tqdm(forms_pdf_all_paths):
        form_pdf_name = os.path.basename(form_pdf_path)[:-4]
        png_dir_path = os.path.join(forms_png_dir_path, form_pdf_name)
        os.makedirs(png_dir_path, exist_ok=True)

        convert_pdf_to_png(form_pdf_path, png_dir_path)



if __name__=="__main__":
    main()








