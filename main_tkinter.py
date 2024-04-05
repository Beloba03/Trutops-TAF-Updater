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
        self.setup_gui()
        self.config_manager = ConfigManager('config.txt')
        self.geo_dir = self.config_manager.get_geo_dir()
        self.taf_dir = self.config_manager.get_taf_dir()
        self.backup_dir = self.config_manager.get_backup_dir()
        self.tmt_dir = self.config_manager.get_tmt_dir()  # Assuming get_TMT_dir method exists in ConfigManager
        self.file_manager = FileManager(self.taf_dir, self.geo_dir, self.backup_dir)
    
    def setup_gui(self):
        self.root.title("File Management")
        self.root.geometry("1200x700")
        self.root.minsize(600, 400)

        # Setup Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.tab_taf_updater = ttk.Frame(self.notebook)
        self.tab_tmt_checker = ttk.Frame(self.notebook)
        self.tab_comparison = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_taf_updater, text="TAF Revision Updater")
        self.notebook.add(self.tab_tmt_checker, text="TMT Part Searcher")
        self.notebook.add(self.tab_comparison, text="PDF-TAF Comparison")
        self.notebook.pack(expand=True, fill="both")

        self.setup_taf_updater_tab()
        self.setup_tmt_checker_tab()
        self.setup_comparison_tab()

    def setup_taf_updater_tab(self):
        # Use an inner frame to hold the fixed-size elements (input fields, labels, buttons)
        input_frame = ttk.Frame(self.tab_taf_updater)
        input_frame.grid(row=0, column=0, sticky="ew")

        # Configure the tab's column to expand, allowing the inner frame to stay centered
        self.tab_taf_updater.grid_columnconfigure(0, weight=1)

        # Input for part number
        tk.Label(input_frame, text="Part Number:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.part_number_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.part_number_entry.grid(row=0, column=1, padx=10, pady=10)

        # Input for new revision
        tk.Label(input_frame, text="New Revision:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        self.new_revision_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.new_revision_entry.grid(row=1, column=1, padx=10, pady=10)

        # Buttons for selecting update mode
        tk.Button(input_frame, text="Update Directory", command=self.update_directory, font=("Arial", 12), width=20).grid(row=2, column=0, padx=10, pady=30)
        tk.Button(input_frame, text="Select TAF Files", command=self.update_specific_files, font=("Arial", 12), width=20).grid(row=2, column=1, padx=10, pady=30)

        # Scrollable Debug Display for updated files information
        self.debug_display = scrolledtext.ScrolledText(self.tab_taf_updater, font=("Arial", 10), height=8)
        self.debug_display.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Make the scrollable area expand with the window
        self.tab_taf_updater.grid_rowconfigure(1, weight=1)

    def update_directory(self):
        part_number = self.part_number_entry.get()
        new_revision = check_for_single_number(self.new_revision_entry.get())
        status, updated_files = self.file_manager.read_and_update_taf_files(part_number, new_revision, None)
        if status:
            if messagebox.askyesno("Confirm Update", "The GEO does not exist. Are you sure you want to update?"):
                _, updated_files = self.file_manager.read_and_update_taf_files(part_number, new_revision, None, None, True)
        else:
            messagebox.showinfo("Update Cancelled", "Finished without modifications.")
        
        # Display updated files in the debug display
        self.display_updated_files(updated_files)

    def update_specific_files(self):
        part_number = self.part_number_entry.get()
        new_revision = check_for_single_number(self.new_revision_entry.get())
        files = filedialog.askopenfilenames(title="Select TAF files", initialdir=self.taf_dir, filetypes=(("TAF files", "*.taf"), ("All files", "*.*")))

        if files:  # Proceed only if files were selected
            # Process all selected files as a batch
            status, updated_files = self.file_manager.read_and_update_taf_files(part_number, new_revision, files, "TAF_Temp")
            
            if status:
                if messagebox.askyesno("Confirm Update", "The GEO does not exist. Are you sure you want to update?"):
                    _, updated_files = self.file_manager.read_and_update_taf_files(part_number, new_revision, files, "TAF_Temp", True)
                else:
                    messagebox.showinfo("Update Cancelled", "Finished without modifications.")
            
            # Display updated files in the debug display
            self.display_updated_files(updated_files)
            
    def display_updated_files(self, updated_files):
        self.debug_display.delete(1.0, tk.END)  # Clear previous content
        if updated_files:
            for file_info in updated_files:
                self.debug_display.insert(tk.END, f"Updated: {file_info[0]} - Part: {file_info[1]}, Old Ver: {file_info[3]}, New Ver: {file_info[2]}\n")
        else:
            self.debug_display.insert(tk.END, "No files were updated.\n")
             
    def setup_tmt_checker_tab(self):
        # Setup for TMT-TAF Revision Checker tab
        self.search_string_var = tk.StringVar()
        tk.Label(self.tab_tmt_checker, text="Search String:", font=("Arial", 12)).pack(pady=10)
        self.search_string_entry = tk.Entry(self.tab_tmt_checker, font=("Arial", 12), textvariable=self.search_string_var)
        self.search_string_entry.pack(pady=10)
        tk.Button(self.tab_tmt_checker, text="Search PDFs", command=self.start_pdf_search, font=("Arial", 12)).pack(pady=10)
        self.search_results = scrolledtext.ScrolledText(self.tab_tmt_checker, font=("Arial", 12), height=10)
        self.search_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def start_pdf_search(self):
        search_string = self.search_string_var.get()
        if search_string:
            self.search_results.delete(1.0, tk.END)
            searcher = PdfSearcher(search_string, self.tmt_dir)  # Use the directory from config manager. Has to be created each time because of the multi-cored search
            searcher.search_in_directory(self.update_search_results)
        else:
            messagebox.showwarning("Warning", "Please provide a search string.")
    def update_search_results(self, result):
        self.search_results.insert(tk.END, f"Match found in file: {result}\n")
        self.search_results.yview(tk.END)
        
        
    def setup_comparison_tab(self):
        tk.Button(self.tab_comparison, text="Select PDF", command=self.select_pdf).pack(pady=20)
        self.results_frame = ttk.Frame(self.tab_comparison)
        self.results_frame.pack(fill="both", expand=True)

    def select_pdf(self):
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            return  # User cancelled the dialog

        # Dummy data for demonstration
        comparison_results = [('1234A', True), ('5678B', False, 'A', 'B'), ('5678asB', False, 'A', 'B'), ('56de78B', False, 'A', 'B')]

        # Display results
        self.display_comparison_results(comparison_results)

    def display_comparison_results(self, results):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Configure results to display in centre with width of 200 pixels no matter the window size
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(1, minsize=300)
        self.results_frame.grid_columnconfigure(2, weight=1)
        for idx, result in enumerate(results):
            part_number, match = result[0], result[1]
            if match:
                bg_color = "green"
                text = part_number
            else:
                bg_color = "red"
                text = f"{part_number}\nPDF: {result[2]}, TAF: {result[3]}"

            label = tk.Label(self.results_frame, text=text, bg=bg_color, fg="white")
            label.grid(row=idx, column=1, padx=15, pady=10, sticky="ew")
        # If there are no results, configure the middle column to take up the space
        if not results:
            self.results_frame.grid_rowconfigure(0, weight=1)
        # Ensure the labels stay centered vertically within the middle column
        self.results_frame.grid_rowconfigure(len(results), weight=1)

def main():
    root = tk.Tk()
    app = FileUpdaterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
