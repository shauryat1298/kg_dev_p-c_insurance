import fitz
import os

def convert_pdf_to_png(pdf_path, output_folder):
    """Convert a single PDF to PNG images"""
    file_name = os.path.basename(pdf_path).replace(".pdf", "").replace(".PDF", "")
    pdf_document = fitz.open(pdf_path)

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        pixmap = page.get_pixmap(dpi=600)

        # Better way to format page numbers with leading zeros
        prefixed_page_no = f"{page_number + 1:03d}"

        output_file = f"{output_folder}/{file_name}_{prefixed_page_no}.png"
        pixmap.save(output_file)
    
    pdf_document.close()
    return file_name

def process_single_pdf(form_pdf_path, forms_png_dir_path):
    """Process a single PDF file - wrapper for ThreadPoolExecutor"""
    try:
        form_pdf_name = os.path.basename(form_pdf_path)[:-4]
        png_dir_path = os.path.join(forms_png_dir_path, form_pdf_name)
        os.makedirs(png_dir_path, exist_ok=True)

        convert_pdf_to_png(form_pdf_path, png_dir_path)
        return form_pdf_name, True, None
    except Exception as e:
        return form_pdf_path, False, str(e)
