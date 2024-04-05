import os
import re
import multiprocessing
from functools import partial
from PyPDF2 import PdfReader

class PdfSearcher:
    def __init__(self, search_string, directory):
        self.search_string = search_string
        self.directory = directory

    def search_pdf(self, file_path):
        pattern = re.compile(r"\b{}\b".format(re.escape(self.search_string)), flags=re.IGNORECASE)
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text and pattern.search(text):
                    return file_path
        return None

    def search_in_directory(self, update_callback):
        pdf_files = [os.path.join(root, file)
                     for root, dirs, files in os.walk(self.directory)
                     for file in files if file.endswith(".pdf")]
        with multiprocessing.Pool() as pool:
            search_with_string = partial(self.search_pdf)
            for result in pool.imap_unordered(search_with_string, pdf_files):
                if result:
                    update_callback(result)