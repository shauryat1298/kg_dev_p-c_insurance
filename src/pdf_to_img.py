import fitz
import os

def convert_pdf_to_png(pdf_path, output_folder):
    file_name = os.path.basename(pdf_path).replace(".pdf", "")
    pdf_document = fitz.open(pdf_path)

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        pixmap = page.get_pixmap(dpi=600)

        if len(str(page_number+1)) == 1:
            prefixed_page_no = "00"+str(page_number+1)
        elif len(str(page_number+1)) == 2:
            prefixed_page_no = "0"+str(page_number+1)

        output_file = f"{output_folder}/{file_name}_{prefixed_page_no}.png"
        pixmap.save(output_file)
        # print(f"Saved: {output_file}")
    
    pdf_document.close()
