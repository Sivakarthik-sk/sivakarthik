import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import tkinter as tk 
from tkinter import filedialog, ttk, messagebox
import pandas as pd

def preprocess_text(text):
    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalnum()]
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

def calculate_similarity(documents):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix

def detect_plagiarism(files):
    texts = []
    filenames = []
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            filenames.append(os.path.basename(file))
            texts.append(preprocess_text(f.read()))
    similarity_matrix = calculate_similarity(texts)
    return similarity_matrix, filenames

def save_results(filenames, similarity_matrix, output_file):
    data = pd.DataFrame(similarity_matrix * 100, index=filenames, columns=filenames)
    data.to_csv(output_file)
    messagebox.showinfo("Saved", f"Results saved to {output_file}")

def show_progress_bar():
    global progress
    progress = ttk.Progressbar(frame, orient="horizontal", mode="indeterminate", length=300)
    progress.pack(pady=10)
    progress.start(10)

def hide_progress_bar():
    global progress
    if progress:
        progress.stop()
        progress.pack_forget()

def browse_files():
    files = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")])
    if files:
        file_list.set("\n".join(files))
        selected_files.extend(files)

def calculate_and_display():
    if not selected_files:
        messagebox.showerror("Error", "No files selected.")
        return
    show_progress_bar()
    root.update_idletasks()
    similarity_matrix, filenames = detect_plagiarism(selected_files)
    hide_progress_bar()
    result_window(similarity_matrix, filenames)

def result_window(similarity_matrix, filenames):
    result_win = tk.Toplevel(root)
    result_win.title("Plagiarism Results")
    tree = ttk.Treeview(result_win, columns=filenames, show="headings")
    for filename in filenames:
        tree.heading(filename, text=filename)
        tree.column(filename, anchor="center")
    for i, row in enumerate(similarity_matrix * 100):
        tree.insert("", "end", values=[f"{val:.2f}%" for val in row])
    tree.pack(fill="both", expand=True)
    save_button = ttk.Button(result_win, text="Save Results",
                             command=lambda: save_results(filenames, similarity_matrix, "plagiarism_results.csv"))
    save_button.pack(pady=10)

root = tk.Tk()
root.title("Plagiarism Checker")
root.geometry("800x600")
selected_files = []
file_list = tk.StringVar()
progress = None
frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)
ttk.Label(frame, text="Plagiarism Checker", font=("Helvetica", 16)).pack(pady=10)
ttk.Label(frame, text="Selected Files:").pack(anchor="w", pady=(10, 0))
file_display = tk.Label(frame, textvariable=file_list, anchor="w", justify="left", bg="white", relief="sunken",
                         wraplength=750)
file_display.pack(fill="x", pady=(0, 10))
ttk.Button(frame, text="Browse Files", command=browse_files).pack(pady=(10, 5))
ttk.Button(frame, text="Check Plagiarism", command=calculate_and_display).pack(pady=(5, 10))
root.mainloop()


