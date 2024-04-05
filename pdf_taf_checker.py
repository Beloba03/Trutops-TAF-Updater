from file_handling import FileManager
from PDF_module import PdfSearcher
import re

class ComparePdfTaf():
    def __init__(self, pdf_path, taf_manager):
        self.taf_parts, self.pdf_parts = [], []
        self.pdf_path = pdf_path
        print(f"PDF path: {self.pdf_path}")
        self.taf_manager = taf_manager

    def compare_pdf_taf(self):
        comparison_results = []  # This list will store the tuples with the comparison results
        # Pattern to match filename to replace extension
        pattern = r".*[/\\](.*)\.[^.]+$"
        taf_name = re.sub(pattern, r"\1.taf", self.pdf_path)
        self.taf_parts = self.taf_manager.get_all_parts(taf_name)   
        
        # PdfSearcher doesn't require search string because it is looking for all matches to internal regex pattern
        searcher = PdfSearcher(None, self.pdf_path)
        self.pdf_parts = searcher.search_pdf(self.pdf_path, True)
        

        for taf_part in self.taf_parts:
            taf_split = taf_part.split('_', 1)  # Split at the first underscore
            if len(taf_split) == 2:
                taf_before_underscore, taf_after_underscore = taf_split  # Separate into before and after underscore

                for pdf_part in self.pdf_parts:
                    pdf_split = pdf_part.split('_', 1)  # Split at the first underscore
                    if len(pdf_split) == 2:
                        pdf_before_underscore, pdf_after_underscore = pdf_split  # Separate into before and after underscore

                        # Check if the parts before the underscore match
                        is_match = taf_before_underscore == pdf_before_underscore

                        # Store the comparison result along with parts before and after the underscore
                        comparison_results.append((taf_part, is_match, taf_before_underscore, pdf_before_underscore, taf_after_underscore, pdf_after_underscore))

        return comparison_results
