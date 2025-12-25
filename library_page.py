import tkinter as tk

class LibraryPage(tk.Frame):
    def __init__(self, parent, theme, config):
        super().__init__(parent, bg=theme["bg"])
        
        tk.Label(self, text="📚 LIBRARY", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        # 仮のリスト表示
        listbox = tk.Listbox(self, bg="#222", fg="white", selectbackground="#3498db")
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        for i in range(10):
            listbox.insert(tk.END, f"楽曲データ {i+1}.mp3")