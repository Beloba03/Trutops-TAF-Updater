import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from file_handling import *
from PDF_module import PdfSearcher
from pdf_taf_checker import ComparePdfTaf
import os, sys
from sys import exit # Using this instead of typical exit because the program is run from a pyinstaller exe

# This function checks if an input if just a single number. If it is it adds a leading 0
def check_for_single_number(input_number):
    if re.match(r"^\d$", input_number): # Use regex to check for single digit number
        return '0' + input_number
    else:
        return input_number

# Function to get the directory containing the script or executable
def resource_path(relative_path):
    """Get the absolute path to the resource, works for development and for PyInstaller."""
    if getattr(sys, 'frozen', False):
        # If the application is run as a frozen executable (e.g., packaged with PyInstaller).
        application_path = os.path.dirname(sys.executable)
    else:
        # If the application is run in a development environment.
        application_path = os.path.dirname(__file__)

    return os.path.join(application_path, relative_path)

class CancelCheck(Exception):
    """This is a custom exception to be raised when the user cancels the file selection dialog."""
    pass
    


# https://tkdocs.com/tutorial/index.html was used extensively in the development of the Tkinter window class
class FileUpdaterGUI:
    """This is the GUI class for the file management application. It contains the setup for the window,tabs and the methods for the GUI features."""
    def __init__(self, root):
        """Assign the initialization variables and call the setup_gui method."""
        self.root = root
        self.root.withdraw()
        self.config_manager = ConfigManager(resource_path('config.txt')) # Open the config.txt file with the ConfigManager class
        self.load_config()

        self.file_manager = FileManager(self.taf_dir, self.geo_dir, self.backup_dir) # Create a new FileManager instance using the directories from the config
        self.root.deiconify()
        self.setup_gui() # Call the window setup method
        
    def select_directory_paths(self):
        """Open a file selector window for each directory path and save the selections to config.txt."""
        initial_dir = '/'  # Set initial directory for file dialogs
        try:
            geo_dir = filedialog.askdirectory(initialdir=initial_dir, title="Select GEO Directory")
            if geo_dir == "":  # If the directory is empty, the config file is empty or the directory doesn't exist
                raise CancelCheck
            taf_dir = filedialog.askdirectory(initialdir=os.path.join(geo_dir, '..'), title="Select TAF Directory")
            if taf_dir == "":  # If the directory is empty, the config file is empty or the directory doesn't exist
                raise CancelCheck
            tmt_dir = filedialog.askdirectory(initialdir=os.path.join(geo_dir, '..'), title="Select TMT Directory")
            if tmt_dir == "":  # If the directory is empty, the config file is empty or the directory doesn't exist
                raise CancelCheck
            backup_dir = filedialog.askdirectory(initialdir=os.path.join(geo_dir, '..'), title="Select Backup Directory")
            if backup_dir == "":  # If the directory is empty, the config file is empty or the directory doesn't exist
                raise CancelCheck
        except CancelCheck:
            return
        
        # Format the directory paths in config file format
        config_content = f"""GEO_DIR: "{geo_dir}"\nTAF_DIR: "{taf_dir}"\nTMT_DIR: "{tmt_dir}"\nBACKUP_DIR: "{backup_dir}\""""
        
        # Write the directory paths to the config.txt file
        with open('config.txt', 'w') as config_file:
            config_file.write(config_content)
        self.load_config()
            
    def load_config(self):
        """Attempt to load the configuration from the config file."""
        config_loaded = False
        while not config_loaded:
            # Try and read the directory paths from the config file
            try:
                self.geo_dir = self.config_manager.get_geo_dir()
                self.taf_dir = self.config_manager.get_taf_dir()
                self.backup_dir = self.config_manager.get_backup_dir()
                self.tmt_dir = self.config_manager.get_tmt_dir()
                config_loaded = True  # Config successfully loaded, exit loop
            except ValueError as error:
                messagebox.showerror("Error", error)
                exit(1)
            # One of the directories is wrong or missing, prompts the user if they want to select new ones
            except ConfigFileWrongDir as error:
                get_dirs = messagebox.askyesno("Warning", f"{error}\nWould you like to select new directories now?")
                if get_dirs:
                    self.select_directory_paths()
                else:
                    exit(1)
            # Config file was created from scratch (probably first run of the program), prompts the user to select directories
            except ConfigFileNotFoundError as error:
                messagebox.showwarning("Warning", error)
                self.select_directory_paths()

    def setup_gui(self):
        """Setup the main window and the tabs for the application."""
        # Setup the main window
        self.root.title("Laser File Management")
        self.root.geometry("1200x700")
        self.root.minsize(600, 400)
        try:
            self.root.iconbitmap(resource_path('FileIcon.ico'))
        except: # Don't want the programming being non-functional if the icon is missing
            pass
        
        # Create the menu bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # Create the "File" menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Add "Select New Directories" option to the "File" menu
        file_menu.add_command(label="Select New Directories", command=lambda: [self.select_directory_paths(), self.populate_pdf_list(), self.file_manager.set_backup_dir(self.backup_dir)]) # Replaces the config directories and then refreshes PDF list
        
        # Add exit option to the "File" menu
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Setup Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.tab_taf_updater = ttk.Frame(self.notebook)
        self.tab_tmt_checker = ttk.Frame(self.notebook)
        self.tab_comparison = ttk.Frame(self.notebook)
        
        # Add the tabs to the Tkinter notebook and name them
        self.notebook.add(self.tab_taf_updater, text="TAF Revision Updater")
        self.notebook.add(self.tab_tmt_checker, text="TMT Part Searcher")
        self.notebook.add(self.tab_comparison, text="TMT-TAF Comparison")
        self.notebook.pack(expand=True, fill="both") # Fit the notebook to the whole window

        # Setup the individual tabs
        self.setup_taf_updater_tab()
        self.setup_tmt_checker_tab()
        self.setup_comparison_tab()

    def setup_taf_updater_tab(self):
        """Setup all the fields in the TAF tab"""
        # Use an inner frame to hold the fixed-size elements (input fields, labels, buttons)
        input_frame = ttk.Frame(self.tab_taf_updater)
        input_frame.grid(row=0, column=0, sticky="ew")

        # Configure the tab's column to expand with the window
        self.tab_taf_updater.grid_columnconfigure(0, weight=1)

        # Input field for part number
        tk.Label(input_frame, text="Part Number:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10) # Label for above text box
        self.part_number_entry = tk.Entry(input_frame, font=("Arial", 12), width=30) # Text box for the part number
        self.part_number_entry.grid(row=0, column=1, padx=10, pady=10) # Place the text box in the window in column 1 (beside the label)

        # Input field for new revision
        tk.Label(input_frame, text="New Revision:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        self.new_revision_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.new_revision_entry.grid(row=1, column=1, padx=10, pady=10)

        # Buttons for selecting update mode
        tk.Button(input_frame, text="Update Whole Directory", command=self.update_directory, font=("Arial", 12), width=20).grid(row=2, column=0, padx=10, pady=30)
        tk.Button(input_frame, text="Update Specific TAFs", command=self.update_specific_files, font=("Arial", 12), width=20).grid(row=2, column=1, padx=10, pady=30)

        # Output text field
        self.debug_display = scrolledtext.ScrolledText(self.tab_taf_updater, font=("Arial", 10), height=8) # Place at bottom in of screen. Will resize with the window.
        self.debug_display.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Set the scrollable area height to expand with the window
        self.tab_taf_updater.grid_rowconfigure(1, weight=1)

    def update_directory(self):
        """Calls read_and_update_taf_files and prompts user with message box if GEO file doesn't exist. Updates entire TAF directory."""
        
        # Get the input from the fields
        part_number = self.part_number_entry.get()
        
        # Ensure part number is not empty. If it is this will erase all part numbers in the directory. Files can be recovered from the backup directory if this occurs.
        if part_number == "":
            messagebox.showwarning("Warning", "Please provide a valid part number")
            return
        
        # Allowing blank revisions to be entered. Won't hurt anything and might be useful?
        new_revision = check_for_single_number(self.new_revision_entry.get())
        
        # Call the read_and_update_taf_files method with the input. Status will return True if the GEO doesn't exist.
        status, updated_files = self.file_manager.read_and_update_taf_files(part_number, new_revision, None)
        
        # Prompt the user with a message box if the GEO doesn't exist
        if status:
            if messagebox.askyesno("Confirm Update", "The GEO does not exist. Are you sure you want to update?"):
                _, updated_files = self.file_manager.read_and_update_taf_files(part_number, new_revision, None, None, True)
                messagebox.showinfo("Finished", "Successfully updated directory!")
        else:
            messagebox.showinfo("Finished", "Successfully updated directory!")
        
        # Display updated files in the output display
        self.display_updated_files(updated_files)

    def update_specific_files(self):
        """Calls read_and_update_taf_files and prompts user with message box if GEO file doesn't exist. Updates specific TAF files."""
        
        # Get the input from the fields
        part_number = self.part_number_entry.get()
        new_revision = check_for_single_number(self.new_revision_entry.get())
        
        # Get the desired files from a file ask window.
        files = filedialog.askopenfilenames(title="Select TAF files", initialdir=self.taf_dir, filetypes=(("TAF files", "*.taf"), ("All files", "*.*")))

        if files:  # Proceed only if files were selected
            
            # Call the read_and_update_taf_files method with the input. Status will return True if the GEO doesn't exist. Files passed in as a list.
            status, updated_files = self.file_manager.read_and_update_taf_files(part_number, new_revision, files, "TAF_Temp")
            
            # Prompt the user with a message box if the GEO doesn't exist
            if status:
                if messagebox.askyesno("Confirm Update", "The GEO does not exist. Are you sure you want to update?"):
                    _, updated_files = self.file_manager.read_and_update_taf_files(part_number, new_revision, files, "TAF_Temp", True)
                    messagebox.showinfo("Finished", "Successfully updated directory!")
                else:
                    messagebox.showinfo("Finished", "Successfully updated directory!")
            
            # Display updated files in the output display
            self.display_updated_files(updated_files)
            
    def display_updated_files(self, updated_files):
        """Display updated files in the output display. If no files were updated, display a message."""
        self.debug_display.delete(1.0, tk.END)  # Clear display first
        
        # Check files were updated
        if updated_files:
            # Insert updated files into the output display after all previous text
            for file_info in updated_files:
                self.debug_display.insert(tk.END, f"Updated: {file_info[0]} - Part: {file_info[1]}, Old Ver: {file_info[3]}, New Ver: {file_info[2]}\n")
        else:
            self.debug_display.insert(tk.END, "No files were updated.\n")
             
    def setup_tmt_checker_tab(self):
        """Setup for TMT-TAF Revision Checker tab"""
        
        # Setup the search section with a label and input field. These use the packed window layout for simplicity.
        tk.Label(self.tab_tmt_checker, text="Search String:", font=("Arial", 12)).pack(pady=10)
        self.search_string_entry = tk.Entry(self.tab_tmt_checker, font=("Arial", 12))
        self.search_string_entry.pack(pady=10)
        
        # Create the search button
        tk.Button(self.tab_tmt_checker, text="Search PDFs", command=self.start_pdf_search, font=("Arial", 12)).pack(pady=10)
        
        # Create the output display
        self.search_results = scrolledtext.ScrolledText(self.tab_tmt_checker, font=("Arial", 12), height=10)
        self.search_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def start_pdf_search(self):
        """Searches through the PDF files in the TMT directory for the search string provided by the user."""
        
        # Get the search string from the input field
        search_string = self.search_string_entry.get()
        
        # Check string actually exists
        if search_string:
            self.search_results.delete(1.0, tk.END) # Clear output field
            searcher = PdfSearcher(search_string, self.tmt_dir)  # Use the directory from config manager. Has to be created each time because of the multi-cored search
            searcher.search_in_directory(self.update_search_results) # Call search in directory with callback to update the output field. This is done using multiprocessing (multicore) to speed up the search.
        else:
            messagebox.showwarning("Warning", "Please provide a search string.")
            
    def update_search_results(self, result):
        """Add result to search results display. This is a callback function for the search_in_directory method."""
        self.search_results.insert(tk.END, f"Match found in file: {result}\n") # Insert onto end of display
        self.search_results.yview(tk.END)
        
        
    def setup_comparison_tab(self):
        """Setup for PDF-TAF Comparison tab. This tab will allow the user to select a PDF file and compare it to the TAF files."""
        # Splitting the tab into left (for PDF selection) and right (for description) frames
        self.left_frame = ttk.Frame(self.tab_comparison)
        self.left_frame.pack(side="left", fill="both", expand=True)
        self.right_frame = ttk.Frame(self.tab_comparison)
        self.right_frame.pack(side="right", fill="both", expand=True)
        
        # RHS text box
        self.side_text = tk.Label(self.right_frame,\
            text="This is intended to function with standard part numbers of the form:\"XXX-XXXX-XX_XX\"\nFunctionality with other naming conventions can not be guaranteed (though it will work for most)!\n\n\n\nClick on a PDF file and the parts inside will appear to the right.\nIf the parts are the same revision in both the PDF and TAF file it will show as GREEN.\nIf there is no associated revision it will show as YELLOW. These should be manually checked.\nIf it shows as RED the revision is different in the PDF vs TAF. Both revisions will be shown in the RED box.",\
            font=("Arial", 12))
        self.side_text.pack(fill="both", expand=True)
        
        # Bind the frame resize event so the RHS text can be resized (might help readability)
        self.right_frame.bind('<Configure>', self.update_label_wrap)

        # Setup the PDF and results lists
        self.setup_scrollable_pdf_list()
        self.populate_pdf_list()  # Populate the left frame with PDFs
        self.setup_scrollable_results_frame()

    
    def update_label_wrap(self, event):
        """Event handler for resizing the right frame. This will adjust the wrap length of the label to match the RHS frame width."""
        # Set the wraplength of the label to the current width of the frame
        self.side_text.configure(wraplength=self.right_frame.winfo_width())

    def setup_scrollable_pdf_list(self):
        """Creates the PDF selection canvas"""
        # Create a canvas within the left_frame with a fixed width of 300 pixels
        self.pdf_list_canvas = tk.Canvas(self.left_frame, width=300)
        self.pdf_list_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.pdf_list_canvas.yview) # Add scrollbar to the canvas
        pdf_text = tk.Label(self.left_frame, text="Select PDF File:                                     Results:", font=("Arial", 14, "bold"), pady=5) # Top labels
        pdf_text.pack(side="top", anchor="w") # Labels are placed at top left
        
        # Create a container frame for the search box to keep it from taking up the whole window width
        search_container = tk.Frame(self.left_frame, width=300, height=75)
        search_container.pack_propagate(False)  # Prevent the frame from resizing to fit its contents
        search_container.pack(side="top", padx=10, anchor="w")

        # Add a search label and entry above the PDF list for clarity
        search_label = tk.Label(search_container, text="Search PDFs:", font=("Arial", 10, "bold"))
        search_label.pack(side="top", padx=10, pady=5)
        self.search_entry = tk.Entry(search_container, font=("Arial", 12))
        self.search_entry.pack(fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda event: self.filter_pdf_list()) # After every keystroke filter the PDF list
        
        # Configure the canvas to use the scrollbar
        self.pdf_list_canvas.configure(yscrollcommand=self.pdf_list_scrollbar.set)
        
        # Pack the canvas and the scrollbar closely together
        self.pdf_list_canvas.pack(side="left", fill="y", expand=False)
        self.pdf_list_scrollbar.pack(side="left", fill="y") 
        
        # Create an inner frame to hold the PDF buttons
        self.pdf_list_frame = ttk.Frame(self.pdf_list_canvas)
        self.pdf_list_canvas.create_window((0, 0), window=self.pdf_list_frame, anchor="nw", width=300)  # Set width of the window
        
        # Update the canvas' scroll region when the inner frame changes size
        self.pdf_list_frame.bind("<Configure>", lambda e: self.pdf_list_canvas.configure(scrollregion=self.pdf_list_canvas.bbox("all")))

        # Thanks to Mikhail T. at https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar for this solution to bind to the current active widget for scrolling!
        self.pdf_list_frame.bind('<Enter>', lambda event, canvas=self.pdf_list_canvas: self.bound_to_mousewheel(event, canvas))
        self.pdf_list_frame.bind('<Leave>', lambda event, canvas=self.pdf_list_canvas: self.unbound_to_mousewheel(event, canvas))
        
    def filter_pdf_list(self):
        """Filter pdf list based on search entry. This will hide any buttons that don't match the search string."""
        query = self.search_entry.get().lower() # Make lowercase to stop case mismatches
        for widget in self.pdf_list_frame.winfo_children():
            # Check if the widget's text contains the search query. If it does, display it, otherwise hide it
            if query in widget.cget("text").lower(): # Make lowercase to stop case mismatches
                widget.pack(fill="x", padx=5, pady=2)
            else:
                widget.pack_forget()

    def bound_to_mousewheel(self, event, passed_canvas):
        """Event handler for binding the mouse wheel scroll event to the canvas."""
        # Bind the mouse wheel scroll event to the canvas
        passed_canvas.bind_all("<MouseWheel>", lambda event, canvas=passed_canvas: self.on_mousewheel(event, canvas))

    def unbound_to_mousewheel(self, event, passed_canvas):
        """Event handler for unbinding the mouse wheel scroll event from the canvas."""
        # Unbind the mouse wheel scroll event from the bound canvas and bind back to results
        passed_canvas.bind_all("<MouseWheel>", lambda event, canvas=self.canvas: self.on_mousewheel(event, canvas))

    def on_mousewheel(self, event, canvas, amount=None):
        """Event handler to scroll the canvas with the mouse wheel."""
        canvas.yview_scroll(int(-1*(event.delta/120)), "units") # This is only setup for Windows currently. If program is ever run on mac or unix platforms the scroll handling will need to be adjusted.

    # https://www.tutorialspoint.com/python/tk_scrollbar.htm
    def setup_scrollable_results_frame(self):
        """Setup frame to hold the results output"""
        
        # Scrollable canvas set immediately to the right of the PDF list
        self.canvas = tk.Canvas(self.left_frame)
        scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")

        # Frame to hold the stack of results
        self.results_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        # Allow results list to be resized with the window
        self.results_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
   
    def populate_pdf_list(self):
        """Get all the PDF files in the TMT directory and add them to the PDF list frame."""
            # First, clear all existing buttons in the frame
        for widget in self.pdf_list_frame.winfo_children():
            widget.destroy()
            
        pdf_files = [f for f in os.listdir(self.tmt_dir) if f.endswith('.pdf')]
        
        # Create button for each file
        for pdf_file in pdf_files:
            tk.Button(self.pdf_list_frame, text=pdf_file, command=lambda pdf=pdf_file: self.select_pdf(pdf)).pack(fill="x")
            
    def select_pdf(self, pdf_file):
        """Called with a PDF file. Calls check with TAF file and displays the results."""
        pdf_path = os.path.join(self.tmt_dir, pdf_file) # Get TMT dir
        print(f"pdf_path: {pdf_path}")
        
        # Create instance of ComparePdfTaf and compare the PDF to the TAF files
        comparer = ComparePdfTaf(pdf_path, self.file_manager)
        comparison_results = comparer.compare_pdf_taf()
        
        # Check if the TAF file was found. If not, display an error message and end.
        if comparison_results is False:
            messagebox.showerror("Error", "TAF File not Found!")
            return
        print(f"comparison_results: {comparison_results}")

        # Display the results in the output list
        self.display_comparison_results(comparison_results)

    def display_comparison_results(self, results):
        """Creates a list of results in the results_frame. This will display the results of the PDF-TAF comparison.
        The results are color coded. RED is for different revisions, GREEN is for matching revisions, and ORANGE is for missing revisions."""
        # Clear previous results in the results frame's results display
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Iterate over all result tuples and create a color coded label for each
        for result in results:
            part_number, match, taf_before_underscore, pdf_before_underscore, taf_after_underscore, pdf_after_underscore = result[0], result[1], result[2], result[3], result[4], result[5] # Unpack the result tuple
            
            # Check if the parts match and revisions are present
            if match and taf_after_underscore != "Missing Revision" and pdf_after_underscore != "Missing Revision":
                bg_color = "green"
                text = f"{part_number}\nRevision: {pdf_after_underscore}"
            # Check if the parts match but revisions are missing
            elif match and taf_after_underscore == "Missing Revision" and pdf_after_underscore == "Missing Revision":
                bg_color = "orange"
                text = f"{part_number}\nTAF & PDF Missing Revision"
            # Parts dont have same revisions
            else:
                bg_color = "red"
                if result[2] != "Missing TAF":
                    text = f"{part_number}\nPDF: {pdf_before_underscore}_{pdf_after_underscore}, TAF: {taf_before_underscore}_{taf_after_underscore}"
                else:
                    text = f"{part_number}\nPDF: {pdf_before_underscore}_{pdf_after_underscore}, TAF: {taf_before_underscore}"

            label = tk.Label(self.results_frame, text=text, bg=bg_color, fg="white", padx=15, pady=5) # Create the label with the text and color
            label.pack(fill="both", padx=5, pady=5)