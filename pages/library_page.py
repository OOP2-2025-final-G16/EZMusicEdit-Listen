import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pygame
from misc.library import library  # library.pyから読み込み

class LibraryPage(tk.Frame):
    def __init__(self, parent, theme, config):
        super().__init__(parent, bg=theme["bg"])
        self.theme = theme
        self.music_manager = library() # 音楽管理クラスをインスタンス化
        self.current_playing_path = None # 現在再生中のファイルのパスを保存
        self.current_button = None       # 現在操作中のボタンを保存
        self.music_duration = 0  # 曲の長さ

        # タイトル
        tk.Label(self, text="📚 LIBRARY", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        # シークバー表示用のフレーム
        self.info_frame = tk.Frame(self, bg=theme["bg"])
        self.info_frame.pack(fill=tk.X, padx=20)
        self.seek_bar = None
        self.time_label = tk.Label(self.info_frame, text="00:00 / 00:00", 
                                   bg=theme["bg"], fg="white", font=("Arial", 10))
        
        self._setup_scroll_area() # スクロール可能なエリアの作成
        self.refresh_list() # ページが作られた時にリストを表示する
        self.check_music_status() # 監視ループを開始する
        self.bind("<Destroy>", self.on_destroy) # このページが消された（MyAppがdestroyした）時に呼ばれる設定
        self.is_dragging = False # マウス操作中かどうかを判定するフラグ
        self.current_seek_start = 0  # シークを開始した時点の秒数

    def _setup_scroll_area(self):
        self.container = tk.Frame(self, bg=self.theme["bg"])
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(self.container, bg="#222", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#222")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def toggle_music(self, path, button):
        if self.current_playing_path == path and self.music_manager.is_playing():
            self.music_manager.stop_music()
            self._hide_seek_bar()
            button.config(text="▶")
            self.current_playing_path = None
            self.current_seek_start = 0 # リセット
        else:
            if self.current_button:
                self.current_button.config(text="▶")

            self.music_duration = self.music_manager.play_music(path)
            self.current_seek_start = 0 # 新規再生時は0
            self._show_seek_bar(self.music_duration)
            button.config(text="■")
            self.current_playing_path = path
            self.current_button = button

    def _format_time(self, seconds):
        """秒数を 00:00 の形式に変換"""
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def _show_seek_bar(self, duration):
        """シークバーを作成・表示"""
        if self.seek_bar:
            self.seek_bar.destroy()
        
        self.seek_bar = tk.Scale(self.info_frame, from_=0, to=duration, 
                                 orient=tk.HORIZONTAL, showvalue=False,
                                 bg=self.theme["bg"], fg="white", highlightthickness=0,
                                 command=self.on_seek) # マウスを離した時などに実行
        self.seek_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        # ラベルをシークバーの右に表示
        self.time_label.pack(side=tk.RIGHT, padx=10)
        self.time_label.config(text=f"00:00 / {self._format_time(duration)}")

        # マウスで触っている間、自動更新を止めるためのイベント
        self.seek_bar.bind("<ButtonPress-1>", self.on_drag_start)
        self.seek_bar.bind("<ButtonRelease-1>", self.on_drag_end)

    def _hide_seek_bar(self):
        """シークバーを隠す"""
        if self.seek_bar:
            self.seek_bar.destroy()
            self.seek_bar = None
        self.time_label.pack_forget()

    def on_drag_start(self, event):
        self.is_dragging = True

    def on_drag_end(self, event):
        self.is_dragging = False

    def on_seek(self, value):
        """シークバーが操作された時に再生位置を変更"""
        # ドラッグ中のみ処理を実行するようにし、頻繁な load/play を防ぐ
        if self.current_playing_path and self.is_dragging:
            sec = float(value)
            self.current_seek_start = sec # シークした位置を記憶
            self.music_manager.set_pos(self.current_playing_path, sec)

    def check_music_status(self):
        """音楽の再生状態とシークバーを更新"""
        if self.music_manager.is_playing():
            # ドラッグ中でない時だけ、シークバーの位置を更新する
            if self.seek_bar and not self.is_dragging:
                # 補正：シーク開始位置 + 再生開始からの経過時間
                current_pos = self.current_seek_start + self.music_manager.get_pos()
                
                # スケールの値を更新（command=on_seek が呼ばれないように直接値をセット）
                self.seek_bar.set(current_pos) 

                # 時間ラベルの更新
                current_str = self._format_time(current_pos)
                total_str = self._format_time(self.music_duration)
                self.time_label.config(text=f"{current_str} / {total_str}")
        else:
            # 再生が完全に終わった場合のみリセット
            if self.current_button and not self.is_dragging:
                self.current_button.config(text="▶")
                self._hide_seek_bar()
                self.current_playing_path = None
                self.current_button = None
                self.current_seek_start = 0

        self.after(200, self.check_music_status) # 頻度を上げて滑らかに

    def on_destroy(self, event):
        """ページが切り替わってこのウィジェットが破棄された時に実行される"""
        # pygameのミキサーが動いていれば停止する
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def refresh_list(self):
        # 既存リストのクリア
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 引数に "library_file" を指定して呼び出す
        files = self.music_manager.get_mp3_files("library_file")

        if not files:
            tk.Label(self.scrollable_frame, text="library_fileフォルダにMP3がありません", 
                     bg=self.theme["bg"], fg="gray").pack(pady=20)
            return

        for path in files:
            self.create_file_row(path)

    def create_file_row(self, file_path):
        row = tk.Frame(self.scrollable_frame, bg="#222")
        row.pack(fill=tk.X, pady=2, padx=5)

        # 切り替えボタンを作成（最初は「▶」）
        btn = tk.Button(row, text="▶", width=5)
        btn.config(command=lambda p=file_path, b=btn: self.toggle_music(p, b))
        btn.pack(side=tk.LEFT, padx=5)

        tk.Label(row, text=os.path.basename(file_path), bg="#222", fg="white", anchor="w").pack(side=tk.LEFT, padx=10)