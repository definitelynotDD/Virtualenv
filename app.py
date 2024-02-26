from flask import Flask, render_template, request, send_file, jsonify
from PyPDF2 import PdfMerger
from pdf2image import convert_from_path
import pytesseract as pyt
from pytesseract import Output

import cv2
import re
import os
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Set Tesseract path
pyt.pytesseract.tesseract_cmd = "C:\\Users\dell\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract"


# Function to merge PDFs
def merge_pdfs(files):
    merger = PdfMerger()

    for pdf in files:
        merger.append(pdf)

    # Generate a unique filename for the merged PDF using uuid
    unique_filename = f'merged_output_{uuid.uuid4()}.pdf'
    merged_output_path = os.path.join(app.root_path, unique_filename)
    merger.write(merged_output_path)
    merger.close()

    return merged_output_path

# Function to perform OCR on an image with table extraction
def perform_ocr_on_image_with_table(image_path):
    img = cv2.imread(image_path)

    # Perform OCR on the image with page segmentation mode 6
    custom_config = r'--psm 6'
    text = pyt.image_to_string(img, config=custom_config)

    # Save the extracted text to a text file
    txt_output_path = f'ocr_output_{uuid.uuid4()}.txt'
    with open(txt_output_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)

    return txt_output_path



# Route for Merging PDFs
@app.route('/merge', methods=['POST'])
def merge():
    try:
        uploaded_files = request.files.getlist('files[]')
        print(uploaded_files)

        if len(uploaded_files) < 2:
            return "Please upload at least two files for merging."

        filenames = []
        for file in uploaded_files:
            filename = os.path.join(app.root_path, file.filename)
            file.save(filename)
            filenames.append(filename)
        print(filenames)    

        merged_path = merge_pdfs(filenames)
        return send_file(merged_path, as_attachment=True, download_name=os.path.basename(merged_path))
        
    except Exception as e:
        return str(e)



# Route for OCR on an image with table extraction
@app.route('/ocr_with_table', methods=['post'])
def ocr_with_table():
    try:
        uploaded_file = request.files['file']

        if not uploaded_file:
            return "Please upload an image for OCR."

        # Save the uploaded image to a temporary location
        image_path = os.path.join(app.root_path, 'temp_image.jpg')
        uploaded_file.save(image_path)

        txt_output_path = perform_ocr_on_image_with_table(image_path)

        # Remove the temporary image file after OCR
        os.remove(image_path)

        return send_file(txt_output_path, as_attachment=True, download_name=os.path.basename(txt_output_path))

    except Exception as e:
        return str(e)


# Route for converting PDF to images
@app.route('/pdf_to_images', methods=['post'])
def pdf_to_images():
    try:
        uploaded_file = request.files['file']

        if not uploaded_file:
            return "Please upload a PDF file for conversion to images."

        # Save the uploaded PDF file to a temporary location
        pdf_path = os.path.join(app.root_path, 'temp_upload.pdf')
        uploaded_file.save(pdf_path)

         # Convert PDF to images
        images = convert_from_path(pdf_path, 500, poppler_path=r'C:\Program Files\poppler-23.11.0\Library\bin')

       # Save images to files
        saved_image_paths = []
        for i, img in enumerate(images):
            image_path = os.path.join(app.root_path, f'page_{i}.jpg')
            img.save(image_path, 'JPEG')
            saved_image_paths.append(image_path)

        # Remove the temporary PDF file after conversion
        os.remove(pdf_path)

        # Return the paths of saved images
        return jsonify({'image_paths': saved_image_paths})

    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(debug=True)
   


    

