import tkinter as tk
from tkinter import ttk

class EditPage(tk.Frame):
    def __init__(self, parent, theme, config):
        super().__init__(parent, bg=theme["bg"])
        
        tk.Label(self, text="✂️ EDIT & ADD", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        # 編集用フォーム
        form = tk.Frame(self, bg=theme["bg"])
        form.pack(pady=10)
        
        tk.Label(form, text="ファイル名:", bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=0, pady=5)
        ttk.Entry(form, width=30).grid(row=0, column=1, pady=5)
        
        tk.Button(self, text="保存してライブラリに追加", bg="#e67e22", fg="white").pack(pady=20)