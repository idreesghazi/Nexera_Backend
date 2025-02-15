import os
import PyPDF2

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def extract_text_from_files(data_folder, output_file):
    extracted_text = ""
    for root, _, files in os.walk(data_folder):
        for file in files:
            print(file)
            file_path = os.path.join(root, file)
            if file.endswith('.txt'):
                extracted_text += extract_text_from_txt(file_path)
            elif file.endswith('.pdf'):
                extracted_text += extract_text_from_pdf(file_path)
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(extracted_text)

if __name__ == "__main__":
    data_folder = 'data'
    output_file = 'finaldata.txt'
    extract_text_from_files(data_folder, output_file)