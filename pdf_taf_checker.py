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
        
        if self.taf_parts is False:
               return False
        
        # PdfSearcher doesn't require search string because it is looking for all matches to internal regex pattern
        searcher = PdfSearcher(None, self.pdf_path)
        self.pdf_parts = searcher.search_pdf(self.pdf_path, True)
        

        for taf_part in self.taf_parts:
            taf_split = taf_part.rsplit('_', 1)  # Split at the first underscore from the right
            print(f"TAF Split: {taf_split}")
            if len(taf_split) == 2:
                taf_before_underscore, taf_after_underscore = taf_split  # Separate into before and after underscore
            else:
                taf_before_underscore = taf_split[0]
                taf_after_underscore = "Missing Revision"

            for pdf_part in self.pdf_parts:
                pdf_split = pdf_part.rsplit('_', 1)  # Split at the first underscore from the right
                if len(pdf_split) == 2:
                    pdf_before_underscore, pdf_after_underscore = pdf_split  # Separate into before and after underscore
                else:
                    pdf_before_underscore = pdf_split[0]
                    pdf_after_underscore = "Missing Revision"
                # Check if the parts before the underscore match
                processed_taf = taf_before_underscore.replace(" ", "").lower()
                processed_pdf = pdf_before_underscore.replace(" ", "").lower()
                is_match = processed_taf == processed_pdf
                if is_match:
                    is_match = taf_after_underscore == pdf_after_underscore # Check if the parts after the underscore match
                    print(f"TAF After _: {taf_after_underscore}, PDF After _: {pdf_after_underscore}")
                    break # Found a match
            if not is_match:
                taf_before_underscore = "Missing TAF"
                taf_after_underscore = " "
            # Store the comparison result along with parts before and after the underscore
            comparison_results.append((taf_part, is_match, taf_before_underscore, pdf_before_underscore, taf_after_underscore, pdf_after_underscore))

        return comparison_results
