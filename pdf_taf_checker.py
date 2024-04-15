# This module contains all code related to PDF-TAF comparisons
from PDF_module import PdfSearcher
import re

# Check if string is number (positive or negative)
def is_number(s):
    try:
        float(s)  # Try converting the string to float
        return True
    except ValueError:
        return False
    
class ComparePdfTaf():
    """This class implements the comparison of PDF and TAF files. It uses the PdfSearcher class to search for parts in the PDF file and the FileManager class to get all parts from the TAF file. 
    The comparison is done by matching the parts before and after the underscore in the part number. If the parts before the underscore match, the parts after the underscore are compared. 
    If both parts match, the comparison result is stored as True, otherwise it is stored as False. If the TAF file is not found, the comparison result is stored as False. 
    The comparison results are stored in a list of tuples, where each tuple contains the TAF part number, the comparison result, the part number before the underscore in the TAF file, the part number before the underscore in the PDF file, 
    the part number after the underscore in the TAF file, and the part number after the underscore in the PDF file."""
    def __init__(self, pdf_path, taf_manager):
        """Initializes the ComparePdfTaf class with the path to the PDF file and the FileManager object."""
        self.taf_parts, self.pdf_parts, self.geo_parts = [], [], [] # Create the blank lists
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
        
        self.geo_parts = self.taf_manager.get_geo_list() # Get all parts from the GEO file
        
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

            found_match = False
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
                    found_match = True
                    break # Found a match
                
            # If no match was found, set the PDF part number to "Part not found". This occurs if the bottom of the PDF file is found without is_match being set
            if found_match == False:
                pdf_before_underscore = "Part not found"
                pdf_after_underscore = " "
            latest_geo_rev = '-1' # Initialize the latest revision number. Negative numbers should never appear in the GEO file under normal circumstances.
            for geo in self.geo_parts:
                geo_noex = geo.rsplit('.', 1)[0] # Remove the extension
                geo_split = geo_noex.rsplit('_', 1)  # Split at the first underscore from the right
                
                # Check there was a split (meaning there was an underscore in the part number indicating a revision)
                if len(geo_split) == 2:
                    geo_before_underscore, geo_after_underscore = geo_split  # Separate into before and after underscore
                    geo_after_underscore = geo_after_underscore.upper() # Convert to uppercase
                # No underscore in the part number so set the after underscore to "Missing Revision"
                else:
                    geo_before_underscore = geo_split[0]
                    geo_after_underscore = "Missing Revision"
                
                 # Check if the parts before the underscore match
                processed_geo = geo_before_underscore.replace(" ", "").lower() # Remove the spaces and convert to lowercase
                processed_pdf = pdf_before_underscore.replace(" ", "").lower()
                geo_is_match = processed_geo == processed_pdf
                
                # Check if the parts after the underscore match and ensure the geo after the underscore is not missing a revision
                if geo_is_match and geo_after_underscore != "Missing Revision":
                    print(f"GEO: {geo_after_underscore}")
                    if (geo_after_underscore.isalpha() and latest_geo_rev.isalpha() and geo_after_underscore.upper() > latest_geo_rev.upper())\
                        or (is_number(geo_after_underscore) and is_number(latest_geo_rev) and int(geo_after_underscore) > int(latest_geo_rev))\
                        or (geo_after_underscore.isalpha() and is_number(latest_geo_rev)):
                        latest_geo_rev = geo_after_underscore
                # If GEO is missing a revision, set the latest_geo_rev to -2. If the latest_geo_rev is already -2, keep it as -2.
                elif geo_is_match and geo_after_underscore == "Missing Revision" and (latest_geo_rev == '-1' or latest_geo_rev == '-2'):
                    latest_geo_rev = "-2"
        
            # Check if the latest_geo_rev was missing a revision
            if latest_geo_rev == '-2':
                pdf_geo_state = "GEO missing revision"
            # Check if the part number match was found
            elif latest_geo_rev == '-1':
                pdf_geo_state = "No GEO found or unsupported revision format"
            # Check if the GEO is a letter and the PDF is a number or if the revision in the GEO is higher than the PDF. This indicates that there is a newer version of the GEO.
            elif (latest_geo_rev.isalpha() and is_number(pdf_after_underscore))\
                or (is_number(latest_geo_rev) and is_number(pdf_after_underscore) and int(latest_geo_rev) > int(pdf_after_underscore))\
                or (latest_geo_rev.isalpha() and pdf_after_underscore.isalpha() and latest_geo_rev.upper() > pdf_after_underscore.upper()):
                pdf_geo_state = f"Newer GEO exists. Revision is {latest_geo_rev}"
            # Check if the GEO matches the PDF
            elif (is_number(latest_geo_rev) and is_number(pdf_after_underscore) and int(latest_geo_rev) == int(pdf_after_underscore)) or \
                (latest_geo_rev.isalpha() and pdf_after_underscore.isalpha() and latest_geo_rev.upper() == pdf_after_underscore.upper()):
                pdf_geo_state = f"Program contains latest GEO: {latest_geo_rev}"
                print(f"Not found.... GEO: {latest_geo_rev} PDF: {pdf_after_underscore}")
            # Catch the case where the GEO is outdated (indicates the file has been deleted)
            else:
                pdf_geo_state = f"Latest GEO revision is only: {latest_geo_rev}"
                        
                
            # Store the comparison result along with parts before and after the underscore as a list of tuples
            comparison_results.append((taf_part, is_match, taf_before_underscore, pdf_before_underscore, taf_after_underscore, pdf_after_underscore, pdf_geo_state))

        return comparison_results # Return list of tuples
