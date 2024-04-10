# This module contains all code related to PDF management and reading
import os
import re
import multiprocessing
import fitz

class PdfSearcher:
    """This class is used to search through a PDF file for a specific string or all parts in the TAF file. The search_string is used to search for a specific part in the TAF file."""
    def __init__(self, search_string, directory):
        """Passes the search_string and the TMT directory to the class."""
        
        # Ensure that the search_string exists and remove all whitespace
        if search_string is not None:
            self.search_string = re.sub(r'\s+', '', search_string)  # Remove all whitespace for the search
        self.directory = directory

    def search_pdf(self, file_path, all_parts=False):
        """Search for specific part in the PDF or return list of all parts in the TAF file."""
        
        print(f"Searching through: {file_path}") # Debug print statement
        
        # Set the search_string depending on the all_parts flag
        if all_parts:
            search_pattern = r"GEO\\?(?:.*?\\?)*([^\\]+)\.GEO"
            match_list = []
        else:
            search_pattern = rf"GEO\\.*?{self.search_string}.*?\.GEO"
        pattern = re.compile(search_pattern, flags=re.IGNORECASE | re.DOTALL) # Compile the regex pattern
        
        # Open the PDF file and search through it
        try:
            doc = fitz.open(file_path) # OPen with PyMuPDF
            
            # Go through the pages in the PDF
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text:
                    text = re.sub(r'\s+', '', text) # Clean up page text
                    
                    # Return list of all parts in TAF file (PDF-TAF compare tab)
                    if all_parts:
                        matches = pattern.findall(text) # Find all matches for the regex pattern
                        print(f"Matches: {matches}")
                        match_list.extend(matches) # Add the matches to the list
                    
                    # Return filepath of taf with matching part (PDF search tab)
                    else:
                        if pattern.search(text):
                            print(f"Match found in: {file_path}")
                            doc.close()
                            return file_path
            # Return list of all parts in TAF file (PDF-TAF compare tab)
            if all_parts:
                print(f"Match List: {match_list}")
                doc.close()
                return match_list
            # Print a message if no match is found in the current PDF
            print(f"No match found in: {file_path}")
            doc.close()
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        return None

    def search_in_directory(self, update_callback):
        """Search each PDF in the directory using multiprocessing. The update_callback is used to update the GUI with the results."""
        pdf_files = [os.path.join(root, file) 
                     for root, _, files in os.walk(self.directory)
                     for file in files if file.endswith(".pdf")] # Create list of PDF files in the directory
        
        # Start new multiprocessing pool
        # https://docs.python.org/3/library/multiprocessing.html
        with multiprocessing.Pool() as pool:
            for result in pool.imap_unordered(self.search_pdf, pdf_files): # Pass the search_pdf function and the list of PDF files to the pool
                if result: # Check if the result is not None and update the callback
                    update_callback(result)