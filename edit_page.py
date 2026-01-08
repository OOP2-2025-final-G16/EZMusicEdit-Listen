import tkinter as tk
from tkinter import ttk
import constants as c

class EditPage(tk.Frame):
    def __init__(self, parent, theme, config):
        # 背景色をテーマ定数から取得
        super().__init__(parent, bg=theme["bg"])
        
        # タイトルラベル (テーマの文字色を使用)
        tk.Label(self, text="✂️ EDIT & ADD", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        # フォーム用フレーム
        form = tk.Frame(self, bg=theme["bg"])
        form.pack(pady=10)
        
        # ラベル (テーマの文字色を使用)
        tk.Label(form, text="ファイル名:", bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=0, pady=5)
        ttk.Entry(form, width=30).grid(row=0, column=1, pady=5)
        
        # 保存ボタン (背景色にアクセントカラー、文字色にボタン専用テキスト色を使用)
        tk.Button(self, 
                  text="保存してライブラリに追加", 
                  bg=c.COLOR_ACCENT, 
                  fg=c.COLOR_BTN_TEXT).pack(pady=20)