import fitz  # PyMuPDF



def extract_headings_and_images(pdf_path):
    # Open the PDF document
    doc = fitz.open(pdf_path)

    headings_with_images = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        
        # Extract text and classify headings based on font size and style
        blocks = page.get_text("dict")["blocks"]
        heading = None
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_size = span["size"]
                        font_flags = span["flags"]  # Detect bold, italics, etc.
                        
                        # Example heuristic: If the font size is large, consider it a heading
                        if font_size > 10 :  # Bold text
                            heading = span["text"]
                            print(f"Detected heading: {heading}")
            
            # Detect images using get_images method
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]  # Extract the image reference
                base_image = doc.extract_image(xref)  # Extract image using the xref
                img_bbox = block["bbox"]
                print(f"Detected image at {img_bbox}")

                # If an image follows a heading within a certain distance, associate them
                if heading:
                    headings_with_images.append((heading, img_bbox))
                    heading = None  # Reset after finding the associated image

    return headings_with_images


headings_with_images = extract_headings_and_images(PDF_FILE)

# Print all detected headings and associated images
for heading, image_bbox in headings_with_images:
    print(f"Heading: {heading} is associated with image at {image_bbox}")





