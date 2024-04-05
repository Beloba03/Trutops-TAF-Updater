import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# Assume parse_pdf and parse_taf are functions you'll implement
# def parse_pdf(pdf_path): return [{'part_number': '123', 'revision': 'A'}, ...]
# def parse_taf(taf_path): return [{'part_number': '123', 'revision': 'A'}, ...]

class FileUpdaterGUI:
    def __init__(self, root):
        self.root = root
        self.setup_gui()
    
    def setup_gui(self):
        self.root.title("File Management")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        self.notebook = ttk.Notebook(self.root)
        self.tab_comparison = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_comparison, text="PDF-TAF Comparison")
        self.notebook.pack(expand=True, fill="both")

        self.setup_comparison_tab()

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
