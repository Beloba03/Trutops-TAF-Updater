from file_handling import FileManager
from PDF_module import PdfSearcher
import re

class ComparePDFTAF():
    def __init__(self, tmt_dir):
        self.taf_parts, self.pdf_parts = [], []
        self.tmt_dir = tmt_dir
    def compare(self, pdf_name):
        # Pattern to match filename to replace extension
        pattern = r"(.*)\.[^.]+$"
        taf_name = re.sub(pattern, r"\1.taf", pdf_name)
        self.taf_parts = get_all_parts(taf_name)