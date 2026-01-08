import tkinter as tk
from tkinter import filedialog, messagebox
import os
from library import library
import constants as c  # 定数をインポート

class LibraryPage(tk.Frame):
    def __init__(self, parent, theme, config):
        # 背景色を定数から取得
        super().__init__(parent, bg=theme["bg"])
        self.theme = theme
        self.music_manager = library()
        
        # タイトル (色の定数化)
        tk.Label(self, text="📚 LIBRARY", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        # フォルダ選択ボタン (ボタンスタイルを定数化)
        tk.Button(self, text="フォルダを選択してMP3を検索", 
                  bg=c.COLOR_BTN_BG, fg=c.COLOR_BTN_TEXT,
                  command=self.select_folder).pack(pady=10)
        
        self.status_label = tk.Label(self, text="フォルダを選択してください", 
                                     bg=theme["bg"], fg=theme["fg"])
        self.status_label.pack(pady=5)

        self._setup_scroll_area()

    def _setup_scroll_area(self):
        """スクロールエリアのセットアップ"""
        self.container = tk.Frame(self, bg=self.theme["bg"])
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # リスト背景色を定数化
        self.canvas = tk.Canvas(self.container, bg=c.COLOR_LIST_BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=c.COLOR_LIST_BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def select_folder(self):
        """フォルダ選択ダイアログを表示し、MP3ファイルをリストアップする"""
        folder_selected = filedialog.askdirectory()
        if not folder_selected:
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        mp3_files = self.music_manager.get_mp3_files(folder_selected)

        if not mp3_files:
            messagebox.showinfo("情報", "MP3ファイルが見つかりませんでした。")
            return

        for path in mp3_files:
            self.create_file_row(path)

        self.status_label.config(text=f"{len(mp3_files)} 個のファイルが見つかりました")

    def create_file_row(self, file_path):
        """ファイル1行分のUIを作成"""
        # 行の背景色を定数化
        row = tk.Frame(self.scrollable_frame, bg=c.COLOR_LIST_BG)
        row.pack(fill=tk.X, pady=2, padx=5)

        file_name = os.path.basename(file_path)

        # 再生・停止ボタン
        tk.Button(row, text="▶", width=3, command=lambda: self.play_music(file_path)).pack(side=tk.LEFT, padx=5)
        tk.Button(row, text="■", width=3, command=self.music_manager.stop_music).pack(side=tk.LEFT)

        # ファイル名のテキスト色を定数化
        tk.Label(row, text=file_name, bg=c.COLOR_LIST_BG, fg=c.COLOR_LIST_TEXT, anchor="w").pack(side=tk.LEFT, padx=10)

    def play_music(self, path):
        """音楽を再生しステータスを更新"""
        try:
            self.music_manager.play_music(path)
            # 再生中のハイライト色を定数化
            self.status_label.config(text=f"再生中: {os.path.basename(path)}", fg=c.COLOR_HIGHLIGHT)
        except Exception as e:
            messagebox.showerror("エラー", f"再生失敗: {e}")