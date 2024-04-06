import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.simpledialog import askstring
from file_handling import *
from PDF_module import PdfSearcher
from pdf_taf_checker import ComparePdfTaf

# This function checks if an input if just a single number. If it is it adds a leading 0
def check_for_single_number(input_number):
    if re.match(r"^\d$", input_number): # Use regex to check for single digit number
        return '0' + input_number
    else:
        return input_number
    
class FileUpdaterGUI:
    def __init__(self, root):
        self.root = root
        self.config_manager = ConfigManager('config.txt')
        self.geo_dir = self.config_manager.get_geo_dir()
        self.taf_dir = self.config_manager.get_taf_dir()
        self.backup_dir = self.config_manager.get_backup_dir()
        self.tmt_dir = self.config_manager.get_tmt_dir()  # Assuming get_TMT_dir method exists in ConfigManager
        self.file_manager = FileManager(self.taf_dir, self.geo_dir, self.backup_dir)
        self.setup_gui()
    
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
        # Splitting the tab into left (for PDF selection) and right (for comparison results) frames
        self.left_frame = ttk.Frame(self.tab_comparison)
        self.left_frame.pack(side="left", fill="both", expand=True)
        self.setup_scrollable_pdf_list()
        self.populate_pdf_list()  # Populate the left frame with PDFs
        self.setup_scrollable_results_frame()
    def setup_scrollable_pdf_list(self):
        # Create a canvas within the left_frame with a fixed width of 300 pixels
        self.pdf_list_canvas = tk.Canvas(self.left_frame, width=300)
        self.pdf_list_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.pdf_list_canvas.yview)
        top_text = tk.Label(self.left_frame,\
            text="Click on a PDF file and the parts inside will appear to the right.\nIf the parts are the same revision in both the PDF and TAF file it will show as GREEN.\nIf there is no associated revision it will show as YELLOW. These should be manually checked.\nIf it shows as RED the revision is different in the PDF vs TAF. Both revisions will be shown in the RED box.", font=("Arial", 12))
        top_text.pack(side="top")
        pdf_text = tk.Label(self.left_frame, text="Select PDF File:                                     Results:", font=("Arial", 14, "bold"), pady=5)
        pdf_text.pack(side="top", anchor="w")
        
        # Configure the canvas to use the scrollbar
        self.pdf_list_canvas.configure(yscrollcommand=self.pdf_list_scrollbar.set)
        
        # Pack the canvas and the scrollbar closely together
        self.pdf_list_canvas.pack(side="left", fill="y", expand=False)  # Changed fill to "y" to fill vertically only
        self.pdf_list_scrollbar.pack(side="left", fill="y")  # Adjusted to fill "y" to match the canvas
        
        # Create an inner frame to hold the PDF buttons
        self.pdf_list_frame = ttk.Frame(self.pdf_list_canvas)
        self.pdf_list_canvas.create_window((0, 0), window=self.pdf_list_frame, anchor="nw", width=300)  # Set width of the window
        
        # Ensure the canvas' scrollregion is updated when the inner frame changes size
        self.pdf_list_frame.bind("<Configure>", lambda e: self.pdf_list_canvas.configure(scrollregion=self.pdf_list_canvas.bbox("all")))

        # Thanks to Mikhail T. at https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar for this solution to bind to the current active widget!
        self.pdf_list_frame.bind('<Enter>', lambda event, canvas=self.pdf_list_canvas: self.bound_to_mousewheel(event, canvas))
        self.pdf_list_frame.bind('<Leave>', lambda event, canvas=self.pdf_list_canvas: self.unbound_to_mousewheel(event, canvas))
        
    def bound_to_mousewheel(self, event, passed_canvas):
        # Bind the mouse wheel scroll event to the canvas
        passed_canvas.bind_all("<MouseWheel>", lambda event, canvas=passed_canvas: self.on_mousewheel(event, canvas))

    def unbound_to_mousewheel(self, event, passed_canvas):
        # Unbind the mouse wheel scroll event from the bound canvas and bind back to results
        passed_canvas.bind_all("<MouseWheel>", lambda event, canvas=self.canvas: self.on_mousewheel(event, canvas))

    def on_mousewheel(self, event, canvas, amount=None):
        """Scroll the canvas with the mouse wheel."""
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def setup_scrollable_results_frame(self):
        self.canvas = tk.Canvas(self.left_frame)
        self.scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="left", fill="y")


        self.results_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        self.results_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        
    def populate_pdf_list(self):
        # Assuming self.tmt_dir is correctly set up before this method is called
        pdf_files = [f for f in os.listdir(self.tmt_dir) if f.endswith('.pdf')]
        for pdf_file in pdf_files:
            tk.Button(self.pdf_list_frame, text=pdf_file, command=lambda pdf=pdf_file: self.select_pdf(pdf)).pack(fill="x")
    def select_pdf(self, pdf_file):
        pdf_path = os.path.join(self.tmt_dir, pdf_file)
        print(f"pdf_path: {pdf_path}")

        comparer = ComparePdfTaf(pdf_path, self.file_manager)
        comparison_results = comparer.compare_pdf_taf()
        print(f"comparison_results: {comparison_results}")

        self.display_comparison_results(comparison_results)

    def display_comparison_results(self, results):
        # Clear previous results in the right frame's results display
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Adjusting this part to work with the results_frame specifically
        for idx, result in enumerate(results):
            part_number, match, taf_after_underscore, pdf_after_underscore = result[0], result[1], result[4], result[5]
            if match and taf_after_underscore != "Missing Revision" and pdf_after_underscore != "Missing Revision":
                bg_color = "green"
                text = part_number
            elif taf_after_underscore == "Missing Revision" and pdf_after_underscore == "Missing Revision":
                bg_color = "orange"
                text = f"{part_number}\nTAF & PDF Missing Revision"
            else:
                bg_color = "red"
                text = f"{part_number}\nPDF: {result[2]}_{pdf_after_underscore}, TAF: {result[3]}_{taf_after_underscore}"

            label = tk.Label(self.results_frame, text=text, bg=bg_color, fg="white", padx=5, pady=5)
            label.pack(fill="both", padx=5, pady=5)

def main():
    root = tk.Tk()
    app = FileUpdaterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
