import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import os
import constants as c

class PlaylistPage(tk.Frame):
    def __init__(self, parent, theme, config):
        # 親の背景色を使用
        super().__init__(parent, bg=theme["bg"])
        
        # プレイリストファイルのリスト
        self.playlist_files = []
        
        # タイトルラベル
        tk.Label(self, text="🎵 プレイリスト", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        # 共通のボタンスタイル（枠線を消す設定を追加）
        btn_style = {
            "bg": c.COLOR_HIGHLIGHT, 
            "fg": c.COLOR_BTN_TEXT, 
            "relief": "flat", 
            "highlightthickness": 0, 
            "bd": 0, 
            "padx": 20, 
            "pady": 5,
            "cursor": "hand2"
        }
        
        # プレイリスト作成ボタン
        tk.Button(self, text="+ 新規プレイリスト作成", **btn_style).pack(pady=10)
        
        # ファイル選択ボタン
        tk.Button(self, text="ファイルを選択", command=self.select_files, **btn_style).pack(pady=10)
        
        # ファイル一覧表示フレーム（背景をリスト専用色に統一）
        list_frame = tk.Frame(self, bg=c.COLOR_LIST_BG, width=600, height=400)
        list_frame.pack(pady=20, padx=50)
        list_frame.pack_propagate(False)
        
        # ファイル一覧のスクロール可能なキャンバス
        self.canvas = tk.Canvas(list_frame, bg=c.COLOR_LIST_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=c.COLOR_LIST_BG)
        
        # スクロール設定
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # キャンバスにフレームを配置
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # キャンバスとスクロールバーを配置
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def select_files(self):
        # ファイル選択ダイアログを開く
        files = filedialog.askopenfilenames(
            title="音楽ファイルを選択",
            filetypes=[("Audio Files", "*.mp3 *.mp4"), ("All Files", "*.*")]
        )
        
        # 選択されたファイルをリストに追加
        for file in files:
            if file not in self.playlist_files:
                self.playlist_files.append(file)
        
        # ファイル一覧を更新
        self.update_file_list()
        
        # XMLに保存
        self.save_to_xml()
    
    def update_file_list(self):
        # 既存のウィジェットをクリア
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # ファイルリストを表示
        for idx, file_path in enumerate(self.playlist_files):
            filename = os.path.basename(file_path)
            
            # ファイルアイテムフレーム
            item_frame = tk.Frame(self.scrollable_frame, bg=c.COLOR_LIST_BG)
            item_frame.pack(fill="x", padx=10, pady=5)
            
            # 再生アイコン（▶）とファイル名
            label = tk.Label(item_frame, text=f"▶ {filename}", 
                           fg=c.COLOR_LIST_TEXT, bg=c.COLOR_LIST_BG, font=("Arial", 12), anchor="w")
            label.pack(side="left", fill="x", expand=True)
    
    def save_to_xml(self):
        # XMLルート要素を作成
        root = ET.Element("playlist")
        
        for idx, file_path in enumerate(self.playlist_files):
            file_element = ET.SubElement(root, "file")
            file_element.set("order", str(idx + 1))
            file_element.set("path", file_path)
        
        # XML書き出し
        tree = ET.ElementTree(root)
        xml_path = "playlist.xml"
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        print(f"プレイリストを保存しました: {xml_path}")