import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.simpledialog import askstring
from file_handling import *
from PDF_module import PdfSearcher

# This function checks if an input if just a single number. If it is it adds a leading 0
def check_for_single_number(input_number):
    if re.match(r"^\d$", input_number): # Use regex to check for single digit number
        return '0' + input_number
    else:
        return input_number
    
class FileUpdaterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Management")
        self.root.geometry("600x400")  # Adjust the initial size of the window

        # Setup Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.tab_taf_updater = ttk.Frame(self.notebook)
        self.tab_tmt_checker = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_taf_updater, text="TAF Revision Updater")
        self.notebook.add(self.tab_tmt_checker, text="TMT-TAF Revision Checker")
        self.notebook.pack(expand=True, fill="both")

        self.config_manager = ConfigManager('config.txt')
        self.geo_dir = self.config_manager.get_geo_dir()
        self.taf_dir = self.config_manager.get_taf_dir()
        self.backup_dir = self.config_manager.get_backup_dir()
        self.file_manager = FileManager(self.taf_dir, self.geo_dir, self.backup_dir)

        self.setup_taf_updater_tab()

    def setup_taf_updater_tab(self):
        # Input for part number
        tk.Label(self.tab_taf_updater, text="Part Number:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.part_number_entry = tk.Entry(self.tab_taf_updater, font=("Arial", 12), width=30)
        self.part_number_entry.grid(row=0, column=1, padx=10, pady=10)

        # Input for new revision
        tk.Label(self.tab_taf_updater, text="New Revision:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        self.new_revision_entry = tk.Entry(self.tab_taf_updater, font=("Arial", 12), width=30)
        self.new_revision_entry.grid(row=1, column=1, padx=10, pady=10)

        # Buttons for selecting update mode
        tk.Button(self.tab_taf_updater, text="Update Directory", command=self.update_directory, font=("Arial", 12), width=20).grid(row=2, column=0, padx=10, pady=10)
        tk.Button(self.tab_taf_updater, text="Select TAF Files", command=self.update_specific_files, font=("Arial", 12), width=20).grid(row=2, column=1, padx=10, pady=10)

    def update_directory(self):
        part_number = self.part_number_entry.get()
        new_revision = check_for_single_number(self.new_revision_entry.get())
        status = self.file_manager.read_and_update_taf_files(part_number, new_revision, None)
        if status:
            if messagebox.askyesno("Confirm Update", "The GEO does not exist. Are you sure you want to update?"):
                self.file_manager.read_and_update_taf_files(part_number, new_revision, None, None, True)
            else:
                messagebox.showinfo("Update Cancelled", "Finished without modifications.")

    def update_specific_files(self):
        part_number = self.part_number_entry.get()
        new_revision = check_for_single_number(self.new_revision_entry.get())
        files = filedialog.askopenfilenames(title="Select TAF files", initialdir=self.taf_dir, filetypes=(("TAF files", "*.taf"), ("All files", "*.*")))

        if files:  # Proceed only if files were selected
            # Process all selected files as a batch
            status = self.file_manager.read_and_update_taf_files(part_number, new_revision, files, "TAF_Temp")
            
            # Check for GEO existence, similar logic to the update_directory method
            if status:
                # If the GEO does not exist, prompt the user to confirm the update
                if messagebox.askyesno("Confirm Update", "The GEO does not exist. Are you sure you want to update?"):
                    # If the user confirms, proceed with the update, overriding the GEO check
                    self.file_manager.read_and_update_taf_files(part_number, new_revision, files, "TAF_Temp", True)
                else:
                    messagebox.showinfo("Update Cancelled", "Finished without modifications.")
    def setup_tmt_checker_tab(self):
        self.search_string_var = tk.StringVar()
        tk.Label(self.tab_tmt_checker, text="Search String:", font=("Arial", 12)).pack(pady=10)
        self.search_string_entry = tk.Entry(self.tab_tmt_checker, font=("Arial", 12), textvariable=self.search_string_var)
        self.search_string_entry.pack(pady=10)
        tk.Button(self.tab_tmt_checker, text="Search PDFs", command=self.start_pdf_search, font=("Arial", 12)).pack(pady=10)
        self.search_results = scrolledtext.ScrolledText(self.tab_tmt_checker, font=("Arial", 12), height=10)
        self.search_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def update_search_results(self, result):
        self.search_results.insert(tk.END, f"Match found in file: {result}\n")
        self.search_results.yview(tk.END)

    def start_pdf_search(self):
        search_string = self.search_string_var.get()
        directory = filedialog.askdirectory(title="Select PDF Directory")
        if search_string and directory:
            searcher = PdfSearcher(search_string, directory)
            self.search_results.delete(1.0, tk.END)
            searcher.search_in_directory(self.update_search_results)
        else:
            messagebox.showwarning("Warning", "Please provide a search string and select a directory.")

def main():
    root = tk.Tk()
    app = FileUpdaterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
