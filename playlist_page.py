import tkinter as tk

class PlaylistPage(tk.Frame):
    def __init__(self, parent, theme, config):
        super().__init__(parent, bg=theme["bg"])
        
        tk.Label(self, text="🎵 PLAYLIST", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        # プレイリスト作成ボタンなど
        btn = tk.Button(self, text="+ 新規プレイリスト作成", bg="#3498db", fg="white", relief="flat", padx=10)
        btn.pack(pady=10)