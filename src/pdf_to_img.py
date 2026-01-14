import fitz
import os
from src.logging_config import get_logger

logger = get_logger(__name__)

def convert_pdf_to_png(pdf_path, output_folder):
    """Convert a single PDF to PNG images"""
    file_name = os.path.basename(pdf_path).replace(".pdf", "").replace(".PDF", "")
    logger.debug("converting_pdf_to_png", pdf_path=pdf_path, file_name=file_name)
    pdf_document = fitz.open(pdf_path)
    total_pages = len(pdf_document)

    successful_pages = 0
    for page_number in range(total_pages):
        try:
            page = pdf_document.load_page(page_number)
            pixmap = page.get_pixmap(dpi=600)

            prefixed_page_no = f"{page_number + 1:03d}"

            output_file = f"{output_folder}/{file_name}_{prefixed_page_no}.png"
            pixmap.save(output_file)
            successful_pages += 1
        except Exception as e:
            logger.error("page_conversion_error", pdf_path=pdf_path, page_number=page_number, error=str(e), exc_info=True)
            continue
    
    pdf_document.close()
    logger.info("pdf_conversion_completed", pdf_path=pdf_path, file_name=file_name, total_pages=total_pages, successful_pages=successful_pages)
    return file_name

def process_single_pdf(form_pdf_path, forms_png_dir_path):
    """Process a single PDF file - wrapper for ThreadPoolExecutor"""
    try:
        form_pdf_name = os.path.basename(form_pdf_path)[:-4]
        png_dir_path = os.path.join(forms_png_dir_path, form_pdf_name)
        os.makedirs(png_dir_path, exist_ok=True)

        convert_pdf_to_png(form_pdf_path, png_dir_path)
        logger.info("pdf_processed", form_pdf_name=form_pdf_name, pdf_path=form_pdf_path)
        return form_pdf_name, True, None
    except Exception as e:
        logger.error("pdf_processing_failed", pdf_path=form_pdf_path, error=str(e), exc_info=True)
        return form_pdf_path, False, str(e)
