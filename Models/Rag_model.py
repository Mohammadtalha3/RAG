import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import pytesseract
from tabula import read_pdf
import pandas as pd

class AdvancedPDFProcessor:
    def __init__(self):
        self.tesseract_config = r'--oem 3 --psm 6'

    def process_pdf(self, pdf_path):
        print('this is the pdf path', pdf_path)
        doc = fitz.open(pdf_path)

        print('we have received the data here', doc)
        processed_content = []

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Extract text
            text = page.get_text()

            # Process images
            images = self.extract_images(page)

            # Process tables
            tables = self.extract_tables(pdf_path, page_num + 1)

            processed_content.append({
                'page_num': page_num + 1,
                'text': text,
                'images': images,
                'tables': tables
            })

        return processed_content

    def extract_images(self, page):
        image_list = page.get_images(full=True)
        images = []

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]

            # Convert to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Perform OCR on the image
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            ocr_text = pytesseract.image_to_string(pil_image, config=self.tesseract_config)

            images.append({
                'image_index': img_index,
                'ocr_text': ocr_text.strip()
            })

        return images

    def extract_tables(self, pdf_path, page_num):
        tables = read_pdf(pdf_path, pages=page_num, multiple_tables=True)
        processed_tables = []

        for idx, table in enumerate(tables):
            # Convert table to string representation
            table_string = table.to_string(index=False)
            processed_tables.append({
                'table_index': idx,
                'content': table_string
            })

        return processed_tables

    def preprocess_content(self, processed_content):
        final_content = []

        for page in processed_content:
            page_text = page['text']

            # Append OCR text from images
            for image in page['images']:
                page_text += f"\n[Image Content: {image['ocr_text']}]\n"

            # Append table content
            for table in page['tables']:
                page_text += f"\n[Table Content:\n{table['content']}]\n"

            final_content.append(page_text)


            print('this is the final content', final_content)

        return "\n".join(final_content)



