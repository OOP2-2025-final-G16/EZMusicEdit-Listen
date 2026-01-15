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
        
        self._setup_initial_seek_bar() # 起動時にシークバーをあらかじめ作成して表示しておく
        self._setup_scroll_area() # スクロール可能なエリアの作成
        self.refresh_list() # ページが作られた時にリストを表示する
        self.check_music_status() # 監視ループを開始する
        self.bind("<Destroy>", self.on_destroy) # このページが消された（MyAppがdestroyした）時に呼ばれる設定
        self.is_dragging = False # マウス操作中かどうかを判定するフラグ
        self.is_paused = False  # 一時停止状態かどうかのフラグ
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

        self.scrollable_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.scrollable_window, width=e.width)
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _setup_initial_seek_bar(self):
        """初期状態のシークバーを作成（中身は0）"""
        if self.seek_bar:
            self.seek_bar.destroy()
        
        # 暫定的に to=100 などで作成
        self.seek_bar = tk.Scale(self.info_frame, from_=0, to=100, 
                                 orient=tk.HORIZONTAL, showvalue=False,
                                 bg=self.theme["bg"], fg="white", highlightthickness=0,
                                 command=self.on_seek)
        self.seek_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)
        self.time_label.pack(side=tk.RIGHT, padx=10)
        # イベントをバインドして、マウス操作を検知できるようにする
        self.seek_bar.bind("<ButtonPress-1>", self.on_drag_start)
        self.seek_bar.bind("<ButtonRelease-1>", self.on_drag_end)

    def toggle_music(self, path, button):
        if self.current_playing_path == path and self.music_manager.is_playing():
            self.current_seek_start += self.music_manager.get_pos()
            self.music_manager.stop_music()
            self.is_paused = True
            button.config(text="▶")
        else:
            # 別の曲を再生する場合、または一時停止からの復帰
            if self.current_playing_path != path:
                # 全く別の曲なら位置をリセット
                self.current_seek_start = 0
                self.is_paused = False
                if self.current_button:
                    self.current_button.config(text="▶")
            
            # 保存されている位置（0 または停止した位置）から再生
            self.music_duration = self.music_manager.play_music(path)
            self.music_manager.set_pos(path, self.current_seek_start)
            
            # シークバーを新しく作らず、既存のものの最大値を更新する
            if self.seek_bar:
                self.seek_bar.config(to=self.music_duration)
            
            button.config(text="■")
            self.current_playing_path = path
            self.current_button = button
            self.is_paused = False

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

    def on_drag_start(self, event):
        self.is_dragging = True

    def on_drag_end(self, event):
        if self.current_playing_path:
            # ドラッグ終了時の値を確定させる
            new_pos = float(self.seek_bar.get())
            self.current_seek_start = new_pos
            # 再生位置をスキップ
            self.music_manager.set_pos(self.current_playing_path, new_pos)
        
        # 最後にフラグを戻す（check_music_statusによる上書きを再開）
        self.after(100, self._reset_dragging)

    def _reset_dragging(self):
        self.is_dragging = False

    def on_seek(self, value):
        """シークバーが操作された時に再生位置を変更"""
        # ドラッグ中のみ処理を実行するようにし、頻繁な load/play を防ぐ
        if self.is_dragging:
            current_str = self._format_time(value)
            total_str = self._format_time(self.music_duration)
            self.time_label.config(text=f"{current_str} / {total_str}")

    def check_music_status(self):
        """音楽の再生状態とシークバーを更新"""
        if self.music_manager.is_playing():
            # ドラッグ中でない時だけ、シークバーの位置を更新する
            if self.seek_bar and not self.is_dragging:
                passed_time = self.music_manager.get_pos()
                current_pos = self.current_seek_start + passed_time
                self.seek_bar.set(current_pos)
                self.time_label.config(text=f"{self._format_time(current_pos)} / {self._format_time(self.music_duration)}")
        else:
            # 一時停止中（is_paused == True）なら、UIをリセットせずに維持する
            if self.current_button and not self.is_dragging and not self.is_paused:
                # 曲が最後まで再生し終わった時だけリセット
                self.current_button.config(text="▶")
                self.current_playing_path = None
                self.current_button = None
                self.current_seek_start = 0
                self.seek_bar.set(0)

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

        # 引数に "library" を指定して呼び出す
        files = self.music_manager.get_mp3_files("library")

        if not files:
            tk.Label(self.scrollable_frame, text="libraryフォルダにMP3がありません", 
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
