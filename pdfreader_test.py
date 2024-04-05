import sys
from PyPDF2 import PdfReader

def read_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
            return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_pdf.py <path_to_pdf>")
        sys.exit(1)

    file_path = sys.argv[1]
    pdf_text = read_pdf(file_path)
    print(pdf_text)
