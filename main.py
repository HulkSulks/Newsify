import os
import tkinter as tk
from tkinter import messagebox
import detector
from gui import FakeNewsDetectorApp

def main():
    # Check if models exist
    if not os.path.exists(detector.MODEL_PATH) or not os.path.exists(detector.VECTORIZER_PATH):
        root = tk.Tk()
        root.withdraw()
        response = messagebox.askyesno(
            "Models Not Found", 
            "The Machine Learning models were not found.\nWould you like to run the training script now?\n(Requires datasets/Fake.csv and True.csv)"
        )
        if response:
            import trainer
            try:
                success = trainer.train()
                if not success:
                    messagebox.showerror("Error", "Training failed. Please ensure datasets are present.")
                    return
            except Exception as e:
                messagebox.showerror("Training Error", str(e))
                return
        else:
            messagebox.showinfo("Exit", "Application cannot run without trained models.")
            return
        root.destroy()
        
    # Launch GUI
    root = tk.Tk()
    app = FakeNewsDetectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
