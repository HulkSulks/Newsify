import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import detector
import utils
import history

# Colors for Dark Mode
BG_COLOR = "#0F172A"
PANEL_COLOR = "#1E293B"
TEXT_COLOR = "#F8FAFC"
ACCENT_BLUE = "#3B82F6"
ACCENT_GREEN = "#10B981"
ACCENT_RED = "#EF4444"

class FakeNewsDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Newsify - Fake News Detector")
        self.root.geometry("800x600")
        self.root.configure(bg=BG_COLOR)
        
        self.setup_ui()
        
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Title
        title_lbl = tk.Label(self.root, text="NEWSIFY", font=("Helvetica", 24, "bold"), bg=BG_COLOR, fg=ACCENT_BLUE)
        title_lbl.pack(pady=20)
        
        # Input Frame
        input_frame = tk.Frame(self.root, bg=PANEL_COLOR, padx=20, pady=20)
        input_frame.pack(fill=tk.X, padx=40, pady=10)
        
        tk.Label(input_frame, text="Enter News Article URL:", bg=PANEL_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).pack(anchor=tk.W)
        self.url_entry = tk.Entry(input_frame, font=("Helvetica", 12), bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.url_entry.pack(fill=tk.X, pady=10)
        
        # Buttons Frame
        btn_frame = tk.Frame(input_frame, bg=PANEL_COLOR)
        btn_frame.pack(fill=tk.X)
        
        self.analyze_btn = tk.Button(btn_frame, text="Analyze URL", bg=ACCENT_BLUE, fg="white", font=("Helvetica", 10, "bold"), command=self.analyze_url, relief=tk.FLAT)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.upload_btn = tk.Button(btn_frame, text="Upload Image", bg=ACCENT_GREEN, fg="white", font=("Helvetica", 10, "bold"), command=self.upload_image, relief=tk.FLAT)
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(btn_frame, text="Clear", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 10, "bold"), command=self.clear_fields, relief=tk.FLAT)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.history_btn = tk.Button(btn_frame, text="History", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 10, "bold"), command=self.show_history, relief=tk.FLAT)
        self.history_btn.pack(side=tk.RIGHT, padx=5)
        
        self.copy_btn = tk.Button(btn_frame, text="Copy Output", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 10, "bold"), command=self.copy_output, relief=tk.FLAT)
        self.copy_btn.pack(side=tk.RIGHT, padx=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=40, pady=5)
        
        # Output Area
        self.output_text = scrolledtext.ScrolledText(self.root, font=("Consolas", 11), bg=PANEL_COLOR, fg=TEXT_COLOR, state=tk.DISABLED, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bg=BG_COLOR, fg="gray", anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)

    def set_buttons_state(self, state):
        self.analyze_btn.config(state=state)
        self.upload_btn.config(state=state)
        self.clear_btn.config(state=state)

    def clear_fields(self):
        self.url_entry.delete(0, tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.status_var.set("Ready")
        self.progress.stop()

    def print_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)

    def copy_output(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
        messagebox.showinfo("Copied", "Output copied to clipboard!")

    def analyze_url(self):
        url = self.url_entry.get().strip()
        if not utils.is_valid_url(url):
            messagebox.showerror("Invalid URL", "Check URL format.")
            return

        self.set_buttons_state("disabled")
        self.progress.start(15)
        self.status_var.set("Analyzing URL...")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.run_url_analysis, args=(url,))
        thread.daemon = True
        thread.start()

    def run_url_analysis(self, url):
        try:
            article_text = utils.fetch_url_text(url)
            if not article_text.strip():
                raise Exception("Could not extract any text from the URL.")
                
            result = detector.predict_news(article_text)
            self.root.after(0, lambda: self.show_prediction(result, "URL"))
            history.add_entry("URL", article_text, result["label"], result["confidence"])
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.print_output(f"Error analyzing URL: {e}"))
        finally:
            self.root.after(0, self.analysis_complete)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not file_path:
            return
            
        self.set_buttons_state("disabled")
        self.progress.start(15)
        self.status_var.set("Processing Image OCR...")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.run_image_analysis, args=(file_path,))
        thread.daemon = True
        thread.start()

    def run_image_analysis(self, file_path):
        try:
            article_text = utils.extract_image_text(file_path)
            if not article_text.strip():
                raise Exception("Could not extract any text from the image.")
                
            result = detector.predict_news(article_text)
            self.root.after(0, lambda: self.show_prediction(result, "Image OCR"))
            history.add_entry("Image", article_text, result["label"], result["confidence"])
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.print_output(f"Error processing image: {e}"))
        finally:
            self.root.after(0, self.analysis_complete)

    def show_prediction(self, result, source_type):
        self.print_output("============================================")
        self.print_output(f"             NEWSIFY ANALYSIS                ")
        self.print_output("============================================")
        self.print_output(f"Source: {source_type}")
        
        label = result["label"]
        conf = result["confidence"] * 100
        
        self.print_output(f"Verdict: {label}")
        self.print_output(f"Confidence: {conf:.2f}%")
        self.print_output("\nDetails:")
        self.print_output(result["explanation"])
        self.print_output("============================================")

    def analysis_complete(self):
        self.progress.stop()
        self.set_buttons_state("normal")
        self.status_var.set("Ready")

    def show_history(self):
        hist_win = tk.Toplevel(self.root)
        hist_win.title("Session History")
        hist_win.geometry("600x400")
        hist_win.configure(bg=BG_COLOR)
        
        cols = ("Time", "Source", "Result", "Confidence", "Preview")
        tree = ttk.Treeview(hist_win, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
            
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for entry in history.get_history():
            tree.insert("", "end", values=(entry["timestamp"], entry["source_type"], entry["result"], entry["confidence"], entry["preview"]))
            
        def export_csv():
            if history.export_to_csv():
                messagebox.showinfo("Exported", "History exported to fake_news_history.csv")
            else:
                messagebox.showwarning("Warning", "No history to export.")
                
        export_btn = tk.Button(hist_win, text="Export as CSV", command=export_csv, bg=ACCENT_BLUE, fg="white", relief=tk.FLAT)
        export_btn.pack(pady=10)

def main():
    root = tk.Tk()
    app = FakeNewsDetectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
