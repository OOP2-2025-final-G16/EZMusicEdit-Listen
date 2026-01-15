import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import os
import glob
import misc.constants as c  # 定数をインポート
from misc.library import library

class PlaylistPage(tk.Frame):
    """
    プレイリスト管理ページ
    - プレイリストの作成、編集、削除
    - プレイリスト内の曲の追加・削除
    - プレイリストの再生機能
    """
    
    def __init__(self, parent, theme, config):
        super().__init__(parent, bg=theme["bg"])
        self.theme = theme
        
        # プレイリスト管理用の変数
        self.playlists = {}  # {プレイリスト名: [ファイルパスリスト]}
        self.selected_playlist = None  # 編集中のプレイリスト名
        self.selected_file_index = None  # プレイリスト内の選択されたファイルインデックス
        self.selected_playlist_for_play = None  # 再生用に選択されたプレイリスト名
        self.view_mode = "list"  # 表示モード: "list"（一覧）, "detail"（詳細）
        self.music_manager = library()  # 音楽再生用のライブラリ
        
        # 連続再生用の変数
        self.current_playing_playlist = None  # 現在再生中のプレイリスト名
        self.current_track_index = 0  # 現在再生中の曲のインデックス
        self.is_playing = False  # 再生中かどうか
        
        # === UI要素の配置 ===
        
        # タイトルラベル
        self.title_label = tk.Label(self, text="🎵 プレイリスト", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"])
        self.title_label.pack(pady=20)
        
        # ボタンフレーム（戻るボタン、追加・削除ボタン、再生・停止ボタン用）
        self.button_frame = tk.Frame(self, bg=theme["bg"])
        self.button_frame.pack(pady=(0, 10))
        
        # スクロールエリア用コンテナ
        self.container = tk.Frame(self, bg=theme["bg"])
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # スクロールエリアのセットアップ
        self._setup_scroll_area()
        
        # === 初期化処理 ===
        
        # 既存のXMLファイルからプレイリストを読み込み
        self.load_existing_playlists()
        # プレイリスト一覧画面を表示
        self.show_playlist_list()
    
    def _setup_scroll_area(self):
        """
        スクロール可能なコンテンツエリアのセットアップ
        キャンバスとスクロールバーを組み合わせてスクロール可能にする
        """
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
    
    # ==========================================
    # プレイリスト一覧表示
    # ==========================================
    
    def show_playlist_list(self):
        """
        プレイリスト一覧画面を表示
        - 新規プレイリスト作成フォーム
        - 再生・停止ボタン
        - プレイリスト一覧（クリックで選択、ダブルクリックで詳細へ）
        """
        self.view_mode = "list"
        self.title_label.config(text="🎵 プレイリスト")
        
        # ボタンフレームをクリア
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # 新規プレイリスト作成フレーム
        form_frame = tk.Frame(self.button_frame, bg=self.theme["bg"])
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="プレイリスト名", bg=self.theme["bg"], 
                fg=self.theme["fg"], font=("Arial", 11)).grid(row=0, column=0, padx=(0, 8))
        
        self.playlist_name_entry = tk.Entry(form_frame, width=20)
        self.playlist_name_entry.grid(row=0, column=1, padx=(0, 8))
        
        tk.Button(form_frame, text="+ 新規作成", bg=c.COLOR_BTN_BG, fg=c.COLOR_BTN_TEXT,
                  command=self.create_new_playlist, width=12).grid(row=0, column=2)
        
        # 再生・停止ボタン
        play_frame = tk.Frame(self.button_frame, bg=self.theme["bg"])
        play_frame.pack(pady=(5, 0))
        
        tk.Button(play_frame, text="▶ 再生", bg=c.COLOR_BTN_BG, fg=c.COLOR_BTN_TEXT,
                  command=self.play_selected_playlist, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(play_frame, text="■ 停止", bg=c.COLOR_BTN_BG, fg=c.COLOR_BTN_TEXT,
                  command=self.stop_playlist, width=10).pack(side=tk.LEFT, padx=5)
        
        # スクロールエリアをクリア
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # プレイリスト一覧を表示
        for pl_name, files in self.playlists.items():
            row = tk.Frame(self.scrollable_frame, bg=c.COLOR_LIST_BG)
            row.pack(fill=tk.X, pady=2, padx=5)
            
            # 選択状態を管理
            row.is_selected = False
            row.playlist_name = pl_name
            
            label = tk.Label(row, text=f"▶ {len(files)}曲 {pl_name}", 
                           bg=c.COLOR_LIST_BG, fg=c.COLOR_LIST_TEXT, 
                           font=("Arial", 12), anchor="w", cursor="hand2")
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # 左クリックで選択、ダブルクリックで詳細
            def on_click(e, frame=row, name=pl_name):
                self.toggle_playlist_selection(frame, name)
            
            def on_double_click(e, name=pl_name):
                self.show_playlist_detail(name)
            
            label.bind("<Button-1>", on_click)
            row.bind("<Button-1>", on_click)
            label.bind("<Double-Button-1>", on_double_click)
            row.bind("<Double-Button-1>", on_double_click)
    
    # ==========================================
    # プレイリスト詳細表示（編集画面）
    # ==========================================
    
    def show_playlist_detail(self, playlist_name):
        """
        プレイリスト詳細画面を表示（編集モード）
        - 戻るボタン、追加・削除ボタン
        - プレイリスト内の曲一覧（クリックで選択可能）
        """
        self.view_mode = "detail"
        self.selected_playlist = playlist_name
        self.title_label.config(text=f"🎵 {playlist_name}")
        
        # ボタンフレームをクリア
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # 戻るボタン
        tk.Button(self.button_frame, text="← 戻る", bg=c.COLOR_BTN_BG, fg=c.COLOR_BTN_TEXT,
                  command=self.show_playlist_list, width=10).pack(side=tk.LEFT, padx=5)
        
        # 追加・削除ボタン
        tk.Button(self.button_frame, text="追加", bg=c.COLOR_BTN_BG, fg=c.COLOR_BTN_TEXT,
                  command=self.add_files, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="削除", bg=c.COLOR_BTN_BG, fg=c.COLOR_BTN_TEXT,
                  command=self.remove_selected, width=10).pack(side=tk.LEFT, padx=5)
        
        # スクロールエリアをクリア
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # プレイリスト内容を表示
        if playlist_name not in self.playlists:
            return
        
        files = self.playlists[playlist_name]
        for idx, file_path in enumerate(files):
            filename = os.path.basename(file_path)
            
            row = tk.Frame(self.scrollable_frame, bg=c.COLOR_LIST_BG)
            row.pack(fill=tk.X, pady=2, padx=5)
            
            # 選択状態を管理するための内部フレーム
            row.is_selected = False
            row.file_index = idx
            
            label = tk.Label(row, text=f"▶ {filename}", 
                    bg=c.COLOR_LIST_BG, fg=c.COLOR_LIST_TEXT, 
                    font=("Arial", 12), anchor="w", cursor="hand2")
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # クリックで選択/解除
            def on_click(e, frame=row, index=idx):
                self.toggle_file_selection(frame, index)
            
            label.bind("<Button-1>", on_click)
            row.bind("<Button-1>", on_click)
    
    # ==========================================
    # データ読み込み・保存
    # ==========================================
    
    def load_existing_playlists(self):
        """
        既存のXMLプレイリストファイルを読み込み
        カレントディレクトリの全.xmlファイルをスキャンして
        プレイリストデータとして読み込む
        """
        xml_files = glob.glob("*.xml")
        for xml_file in xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                files = [f.get("path") for f in root.findall("file")]
                playlist_name = os.path.splitext(xml_file)[0]
                self.playlists[playlist_name] = files
            except:
                pass
    
    # ==========================================
    # プレイリスト作成・編集
    # ==========================================
    
    def create_new_playlist(self):
        """
        新規プレイリストを作成
        入力された名前で空のプレイリストを作成し、XMLファイルに保存
        """
        name = self.playlist_name_entry.get().strip()
        
        if not name:
            messagebox.showinfo("入力エラー", "プレイリスト名を入力してください。")
            return
        
        if name in self.playlists:
            messagebox.showinfo("エラー", "同じ名前のプレイリストが既に存在します。")
            return
        
        # 空のプレイリストを作成
        self.playlists[name] = []
        self.save_playlist(name)
        
        # テキスト入力欄をクリア
        self.playlist_name_entry.delete(0, tk.END)
        
        # プレイリスト一覧を更新
        self.show_playlist_list()
        messagebox.showinfo("作成完了", f"プレイリスト「{name}」を作成しました。")
    
    def add_files(self):
        """
        プレイリストに曲を追加
        ファイル選択ダイアログで選択したmp3/mp4ファイルをプレイリストに追加
        """
        if not self.selected_playlist:
            messagebox.showinfo("プレイリスト未選択", "プレイリストを選択してください。")
            return
        
        files = filedialog.askopenfilenames(
            title="音楽ファイルを選択",
            filetypes=[("Audio Files", "*.mp3 *.mp4"), ("All Files", "*.*")]
        )
        
        for file in files:
            if file not in self.playlists[self.selected_playlist]:
                self.playlists[self.selected_playlist].append(file)
        
        self.save_playlist(self.selected_playlist)
        self.show_playlist_detail(self.selected_playlist)
    
    def remove_selected(self):
        """
        選択された曲をプレイリストから削除
        クリックで選択された曲をプレイリストから削除し、XMLを更新
        """
        if self.selected_file_index is None:
            messagebox.showinfo("選択なし", "削除する曲を選択してください。")
            return
        
        if not self.selected_playlist or self.selected_playlist not in self.playlists:
            return
        
        # ファイルを削除
        if 0 <= self.selected_file_index < len(self.playlists[self.selected_playlist]):
            del self.playlists[self.selected_playlist][self.selected_file_index]
            self.selected_file_index = None
            self.save_playlist(self.selected_playlist)
            self.show_playlist_detail(self.selected_playlist)
            messagebox.showinfo("削除完了", "曲を削除しました。")
    
    # ==========================================
    # 選択状態管理
    # ==========================================
    
    def toggle_file_selection(self, frame, file_index):
        """
        プレイリスト詳細画面での曲の選択状態を切り替え
        選択された曲の背景色を変更して視覚的にフィードバック
        """
        # 前回選択されたアイテムの選択を解除
        for widget in self.scrollable_frame.winfo_children():
            if hasattr(widget, 'is_selected') and widget.is_selected:
                widget.config(bg=c.COLOR_LIST_BG)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=c.COLOR_LIST_BG)
                widget.is_selected = False
        
        # 新しいアイテムを選択
        frame.config(bg=c.COLOR_HIGHLIGHT)
        for child in frame.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=c.COLOR_HIGHLIGHT)
        frame.is_selected = True
        self.selected_file_index = file_index
    
    def toggle_playlist_selection(self, frame, playlist_name):
        """
        プレイリスト一覧画面でのプレイリストの選択状態を切り替え
        選択されたプレイリストの背景色を変更（再生用の選択）
        """
        # 前回選択されたアイテムの選択を解除
        for widget in self.scrollable_frame.winfo_children():
            if hasattr(widget, 'is_selected') and widget.is_selected:
                widget.config(bg=c.COLOR_LIST_BG)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=c.COLOR_LIST_BG)
                widget.is_selected = False
        
        # 新しいアイテムを選択
        frame.config(bg=c.COLOR_HIGHLIGHT)
        for child in frame.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=c.COLOR_HIGHLIGHT)
        frame.is_selected = True
        self.selected_playlist_for_play = playlist_name
    
    # ==========================================
    # 再生機能
    # ==========================================
    
    def play_selected_playlist(self):
        """
        選択されたプレイリストを順次再生
        プレイリスト内の全ての曲を順番に再生する
        """
        if not self.selected_playlist_for_play:
            messagebox.showinfo("選択なし", "再生するプレイリストを選択してください。")
            return
        
        if self.selected_playlist_for_play not in self.playlists:
            return
        
        files = self.playlists[self.selected_playlist_for_play]
        if not files:
            messagebox.showinfo("曲なし", "プレイリストに曲がありません。")
            return
        
        # 再生状態を初期化
        self.current_playing_playlist = self.selected_playlist_for_play
        self.current_track_index = 0
        self.is_playing = True
        
        # 最初の曲を再生
        self._play_current_track()
        
        # 定期的に再生状態をチェック
        self._check_playback_status()
    
    def _play_current_track(self):
        """
        現在のトラックを再生
        """
        if not self.current_playing_playlist or self.current_playing_playlist not in self.playlists:
            return
        
        files = self.playlists[self.current_playing_playlist]
        if self.current_track_index >= len(files):
            # 全ての曲を再生完了
            self.is_playing = False
            self.title_label.config(text="🎵 プレイリスト")
            return
        
        try:
            current_file = files[self.current_track_index]
            self.music_manager.play_music(current_file)
            # タイトルラベルに再生中のプレイリスト名を表示
            self.title_label.config(text=f"🎵 [{self.current_playing_playlist}]を再生しています")
            print(f"再生中: {os.path.basename(current_file)} ({self.current_track_index + 1}/{len(files)})")
        except Exception as e:
            messagebox.showerror("再生エラー", f"再生できませんでした: {e}")
            self.is_playing = False
    
    def _check_playback_status(self):
        """
        再生状態を定期的にチェックし、曲が終わったら次の曲を再生
        """
        if not self.is_playing:
            return
        
        # pygameの音楽が再生中かチェック
        import pygame
        if not pygame.mixer.music.get_busy():
            # 曲が終了した
            self.current_track_index += 1
            if self.current_playing_playlist and self.current_track_index < len(self.playlists.get(self.current_playing_playlist, [])):
                # 次の曲を再生
                self._play_current_track()
            else:
                # プレイリスト終了
                self.is_playing = False
                self.title_label.config(text="🎵 プレイリスト")
                return
        
        # 100ミリ秒後に再度チェック
        self.after(100, self._check_playback_status)
    
    def stop_playlist(self):
        """
        プレイリストの再生を停止
        """
        self.music_manager.stop_music()
        self.is_playing = False
        self.current_playing_playlist = None
        self.current_track_index = 0
        # 一覧画面の場合はタイトルをリセット
        if self.view_mode == "list":
            self.title_label.config(text="🎵 プレイリスト")
    
    # ==========================================
    # XMLファイル保存
    # ==========================================
    
    def save_playlist(self, playlist_name):
        """
        プレイリストをXMLファイルに保存
        
        XML構造:
        <playlist name="プレイリスト名">
            <file order="1" path="/path/to/file1.mp3" />
            <file order="2" path="/path/to/file2.mp3" />
        </playlist>
        
        保存先: カレントディレクトリの「プレイリスト名.xml」
        """
        root = ET.Element("playlist")
        root.set("name", playlist_name)
        
        for idx, file_path in enumerate(self.playlists[playlist_name]):
            file_element = ET.SubElement(root, "file")
            file_element.set("order", str(idx + 1))
            file_element.set("path", file_path)
        
        tree = ET.ElementTree(root)
        xml_path = f"{playlist_name}.xml"
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        print(f"プレイリストを保存しました: {xml_path}")