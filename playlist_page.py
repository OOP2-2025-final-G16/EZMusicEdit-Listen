import tkinter as tk
from pathlib import Path

from xml_playlist_manager import SortMode, XmlPlaylistManager

class PlaylistPage(tk.Frame):
    def __init__(self, parent, theme, config):
        super().__init__(parent, bg=theme["bg"])
        
        # 任意のxmlファイル名
        self.manager = XmlPlaylistManager(Path(__file__).with_name("playlist.xml"))
        self.order_var = tk.StringVar(value=SortMode.ADDED.value)
        
        tk.Label(self, text="🎵 PLAYLIST", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        # プレイリスト作成ボタン
        btn = tk.Button(self, text="+ 新規プレイリスト作成", bg="#3498db", fg="white", relief="flat", padx=10)
        btn.pack(pady=10)

        # 並び順制御用のコントロール
        controls = tk.Frame(self, bg=theme["bg"])
        controls.pack(pady=10)

        tk.Label(controls, text="並び順", bg=theme["bg"], fg=theme["fg"]).pack(side=tk.LEFT, padx=6)
        tk.OptionMenu(
            controls,
            self.order_var,
            *[mode.value for mode in SortMode],
            command=self.refresh_list,
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            controls,
            text="XMLを更新",
            bg="#3498db",
            fg="white",
            relief="flat",
            padx=10,
            command=self.refresh_list,
        ).pack(side=tk.LEFT, padx=6)

        # プレイリスト表示用のリストボックス
        self.listbox = tk.Listbox(self, bg="#222", fg="white", selectbackground="#3498db")
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.refresh_list()

    def refresh_list(self, *_):
        # XMLを読み込んで選択モードで並び替えて保存
        entries = self.manager.load_entries()
        ordered = self.manager.reorder(entries, SortMode(self.order_var.get()))
        self.manager.save_entries(ordered)

        # リストボックスを更新して新しい順序を表示
        self.listbox.delete(0, tk.END)
        for entry in ordered:
            self.listbox.insert(tk.END, entry.title)