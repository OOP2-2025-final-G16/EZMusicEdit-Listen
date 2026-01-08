import tkinter as tk
from tkinter import ttk
import constants as c

class EditPage(tk.Frame):
    def __init__(self, parent, theme, config):
        super().__init__(parent, bg=theme["bg"])
        
        tk.Label(self, text="✂️ EDIT & ADD", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        form = tk.Frame(self, bg=theme["bg"])
        form.pack(pady=10)
        
        tk.Label(form, text="ファイル名:", bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=0, pady=5)
        ttk.Entry(form, width=30).grid(row=0, column=1, pady=5)
        
        # ボタンの枠線を完全に消去
        tk.Button(self, 
                  text="保存してライブラリに追加", 
                  bg=c.COLOR_ACCENT, 
                  fg=c.COLOR_BTN_TEXT,
                  font=("Arial", 11, "bold"),
                  highlightthickness=0,    # フォーカス枠を消す
                  borderwidth=0,           # 境界線を消す
                  activebackground=c.COLOR_ACCENT, # クリック時の色を維持
                  activeforeground=c.COLOR_BTN_TEXT,
                  padx=20, 
                  pady=10,
                  cursor="hand2").pack(pady=20)