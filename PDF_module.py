import os
import re
import multiprocessing
from functools import partial
import fitz  # Import the PyMuPDF library

class PdfSearcher:
    def __init__(self, search_string, directory):
        if search_string is not None:
            self.search_string = re.sub(r'\s+', '', search_string)  # Remove all whitespace for the search
        self.directory = directory

    def search_pdf(self, file_path, all_parts=False):
        # Print the name of the PDF file being searched through
        print(f"Searching through: {file_path}")
        
        if all_parts:
            search_pattern = r"GEO\\?(?:.*?\\?)*([^\\]+)\.GEO"
            match_list = []
        else:
            search_pattern = rf"GEO\\.*?{self.search_string}.*?\.GEO"
        pattern = re.compile(search_pattern, flags=re.IGNORECASE | re.DOTALL)
        
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text:
                    text = re.sub(r'\s+', '', text)
                    
                    # Return list of all parts in TAF file (PDF-TAF compare tab)
                    if all_parts:
                        matches = pattern.findall(text)
                        print(f"Matches: {matches}")
                        match_list.extend(matches)
                    
                    # Return filepath of taf with matching part (PDF search tab)
                    else:
                        if pattern.search(text):
                            print(f"Match found in: {file_path}")
                            doc.close()
                            return file_path
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
        pdf_files = [os.path.join(root, file)
                     for root, dirs, files in os.walk(self.directory)
                     for file in files if file.endswith(".pdf")]
        with multiprocessing.Pool() as pool:
            search_with_string = partial(self.search_pdf)
            for result in pool.imap_unordered(search_with_string, pdf_files):
                if result:
                    update_callback(result)
def main():
    search_string = input("Enter the search string: ")
    directory = input("Enter the directory to search in: ")
    searcher = PdfSearcher(search_string, directory)
    searcher.search_in_directory(print)

if __name__ == "__main__":
    main()
