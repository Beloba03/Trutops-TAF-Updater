from PDF_module import PdfSearcher
import re

class ComparePdfTaf():
    """This class implements the comparison of PDF and TAF files. It uses the PdfSearcher class to search for parts in the PDF file and the FileManager class to get all parts from the TAF file. 
    The comparison is done by matching the parts before and after the underscore in the part number. If the parts before the underscore match, the parts after the underscore are compared. 
    If both parts match, the comparison result is stored as True, otherwise it is stored as False. If the TAF file is not found, the comparison result is stored as False. 
    The comparison results are stored in a list of tuples, where each tuple contains the TAF part number, the comparison result, the part number before the underscore in the TAF file, the part number before the underscore in the PDF file, 
    the part number after the underscore in the TAF file, and the part number after the underscore in the PDF file."""
    def __init__(self, pdf_path, taf_manager):
        """Initializes the ComparePdfTaf class with the path to the PDF file and the FileManager object."""
        self.taf_parts, self.pdf_parts = [], [] # Create the blank lists
        self.pdf_path = pdf_path
        print(f"PDF path: {self.pdf_path}") # Debug print statement
        self.taf_manager = taf_manager

    def compare_pdf_taf(self):
        """Check all parts in a PDF with the TAF of the same name. Returns list of tuples: (taf_part, is_match (T/F), taf_before_underscore, pdf_before_underscore, taf_after_underscore, pdf_after_underscore) is the tuple format"""
        comparison_results = []  # This list will store the tuples with the comparison results
        pattern = r".*[/\\](.*)\.[^.]+$" # Pattern to match filename to replace extension
        taf_name = re.sub(pattern, r"\1.taf", self.pdf_path) # Replace the extension with .taf
        self.taf_parts = self.taf_manager.get_all_parts(taf_name) # Get all parts from the TAF file
        
        # Check the TAF file exists
        if self.taf_parts is False:
               return False
        
        # PdfSearcher doesn't require search string because it is looking for all matches to internal regex pattern. This creates a new PDFSearcher instance and searches the PDF file for all parts.
        searcher = PdfSearcher(None, self.pdf_path)
        self.pdf_parts = searcher.search_pdf(self.pdf_path, True)
        
        # Compare each part in the TAF with each part in the PDF
        for taf_part in self.taf_parts:
            taf_split = taf_part.rsplit('_', 1)  # Split at the first underscore from the right
            print(f"TAF Split: {taf_split}") # Debug print
            
            # Check there was a split (meaning there was an underscore in the part number indicating a revision)
            if len(taf_split) == 2:
                taf_before_underscore, taf_after_underscore = taf_split  # Separate into before and after underscore
            # No underscore in the part number so set the after underscore to "Missing Revision"
            else:
                taf_before_underscore = taf_split[0]
                taf_after_underscore = "Missing Revision"

            # Iterate over PDF for each part in the TAF
            for pdf_part in self.pdf_parts:
                pdf_split = pdf_part.rsplit('_', 1)  # Split at the first underscore from the right
                
                # Check there was a split (meaning there was an underscore in the part number indicating a revision)
                if len(pdf_split) == 2:
                    pdf_before_underscore, pdf_after_underscore = pdf_split  # Separate into before and after underscore
                # No underscore in the part number so set the after underscore to "Missing Revision"
                else:
                    pdf_before_underscore = pdf_split[0]
                    pdf_after_underscore = "Missing Revision"
                    
                # Check if the parts before the underscore match
                processed_taf = taf_before_underscore.replace(" ", "").lower() # Remove the spaces and convert to lowercase
                processed_pdf = pdf_before_underscore.replace(" ", "").lower()
                is_match = processed_taf == processed_pdf
                
                # If there is a matching part number, check the revisions and end loop.
                if is_match:
                    is_match = taf_after_underscore == pdf_after_underscore # Check if the parts after the underscore match
                    print(f"TAF After _: {taf_after_underscore}, PDF After _: {pdf_after_underscore}")
                    break # Found a match
                
            # Store the comparison result along with parts before and after the underscore as a list of tuples
            comparison_results.append((taf_part, is_match, taf_before_underscore, pdf_before_underscore, taf_after_underscore, pdf_after_underscore))

        return comparison_results # Return list of tuples
