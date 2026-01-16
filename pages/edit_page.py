import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from edit.changemp3 import convert_mp4_to_mp3, ConvertError
from edit.preview_player import preview_segments
from edit.library_saver import concat_segments_to_tempfile, copy_temp_to_library
from edit.audio_info import get_duration_seconds
from edit.timeline_helper import TimelineController


class EditPage(tk.Frame):
    def __init__(self, parent, theme, config):
        super().__init__(parent, bg=theme["bg"])
        self.config_data = config
        self.theme = theme
        
        # スクロール可能なコンテナを作成
        canvas = tk.Canvas(self, bg=theme["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=theme["bg"])
        
        def _update_canvas_window(event=None):
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            frame_width = self.scrollable_frame.winfo_reqwidth()
            x_position = max(0, (canvas_width - frame_width) // 2)
            canvas.coords("content_window", x_position, 0)
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.scrollable_frame.bind("<Configure>", _update_canvas_window)
        canvas.bind("<Configure>", _update_canvas_window)
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="content_window")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # マウスホイールでスクロール
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # タイトル
        tk.Label(self.scrollable_frame, text="✂️ EDIT & ADD", font=("Arial", 20, "bold"), 
                 bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        # ファイル数を動的に管理
        self.file_vars = [tk.StringVar()]
        self.start_vars = [tk.DoubleVar(value=0.0)]
        self.end_vars = [tk.DoubleVar(value=0.0)]
        self.duration_vars = [tk.DoubleVar(value=0.0)]
        self.total_length_vars = [tk.DoubleVar(value=0.0)]
        self._file_ranges = [{"start": 0.0, "duration": 0.0, "total": 0.0}]
        
        self.form_frame = tk.Frame(self.scrollable_frame, bg=theme["bg"])
        self.form_frame.pack(pady=10, fill=tk.X, expand=False, padx=10)
        
        self._create_file_input_ui()
        
        # ボタン群
        self._create_action_buttons()
        
        # タイムライン
        self.editor_frame = tk.Frame(self.scrollable_frame, bg=theme["bg"])
        self.editor_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        tk.Label(
            self.editor_frame,
            text="切り取りタイムライン",
            bg=theme["bg"],
            fg=theme["fg"],
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=20)
        
        self.timeline_canvases = []
        self.timeline_rows = []
        self._add_timeline_for_file(0)
        
        self.timeline_info = tk.Label(
            self.editor_frame,
            text="",
            bg=theme["bg"],
            fg=theme["fg"],
            anchor="w",
        )
        self.timeline_info.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(10, 0))
        
        # タイムラインコントローラ
        self.timeline_controller = TimelineController(
            canvases=self.timeline_canvases,
            info_label=self.timeline_info,
            file_ranges=self._file_ranges,
            start_vars=self.start_vars,
            end_vars=self.end_vars,
            duration_vars=self.duration_vars,
            total_length_vars=self.total_length_vars,
        )
        self.timeline_controller.bind_canvas_events()
        self._bind_var_traces()
        self.timeline_controller.redraw()

    def _create_file_input_ui(self):
        """ファイル入力UIを生成"""
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        
        # ファイル入力欄
        for idx, file_var in enumerate(self.file_vars):
            tk.Label(self.form_frame, text=f"ファイル{idx + 1}(mp3/mp4):", 
                     bg=self.theme["bg"], fg=self.theme["fg"]).grid(
                row=idx, column=0, pady=5, padx=5, sticky="e"
            )
            ttk.Entry(self.form_frame, textvariable=file_var, width=40).grid(
                row=idx, column=1, columnspan=4, pady=5, padx=5, sticky="ew"
            )
            btn = ttk.Button(self.form_frame, text="参照...", 
                            command=lambda i=idx: self._browse_file(i))
            btn.grid(row=idx, column=5, padx=5, pady=5)
        
        # ＋ボタンと－ボタン
        button_frame = tk.Frame(self.form_frame, bg=self.theme["bg"])
        button_frame.grid(row=len(self.file_vars), column=0, pady=5, padx=5)
        
        add_btn = ttk.Button(button_frame, text="+", width=3,
                            command=self._add_file)
        add_btn.pack(side=tk.LEFT, padx=2)
        
        remove_btn = ttk.Button(button_frame, text="−", width=3,
                               command=self._remove_file)
        remove_btn.pack(side=tk.LEFT, padx=2)
        
        # パラメータヘッダー
        tk.Label(self.form_frame, text="", bg=self.theme["bg"], 
                fg=self.theme["fg"]).grid(
            row=len(self.file_vars) + 1, column=0, pady=5, padx=5, sticky="e"
        )
        for idx in range(len(self.file_vars)):
            tk.Label(self.form_frame, text=f"ファイル{idx + 1}", 
                    bg=self.theme["bg"], fg=self.theme["fg"]).grid(
                row=len(self.file_vars) + 1, column=idx + 1, pady=5, padx=5
            )
        
        # 開始位置
        tk.Label(self.form_frame, text="開始位置(秒):", bg=self.theme["bg"], 
                fg=self.theme["fg"]).grid(
            row=len(self.file_vars) + 2, column=0, pady=5, padx=5, sticky="e"
        )
        for idx, var in enumerate(self.start_vars):
            ttk.Entry(self.form_frame, textvariable=var, width=10).grid(
                row=len(self.file_vars) + 2, column=idx + 1, pady=5, padx=5
            )
        
        # 終了位置
        tk.Label(self.form_frame, text="終了位置(秒):", bg=self.theme["bg"], 
                fg=self.theme["fg"]).grid(
            row=len(self.file_vars) + 3, column=0, pady=5, padx=5, sticky="e"
        )
        for idx, var in enumerate(self.end_vars):
            ttk.Entry(self.form_frame, textvariable=var, width=10).grid(
                row=len(self.file_vars) + 3, column=idx + 1, pady=5, padx=5
            )
        
        # 長さ
        tk.Label(self.form_frame, text="長さ(秒):", bg=self.theme["bg"], 
                fg=self.theme["fg"]).grid(
            row=len(self.file_vars) + 4, column=0, pady=5, padx=5, sticky="e"
        )
        for idx, var in enumerate(self.duration_vars):
            ttk.Entry(self.form_frame, textvariable=var, width=10).grid(
                row=len(self.file_vars) + 4, column=idx + 1, pady=5, padx=5
            )
        
        # 曲の長さ
        tk.Label(self.form_frame, text="曲の長さ(秒):", bg=self.theme["bg"], 
                fg=self.theme["fg"]).grid(
            row=len(self.file_vars) + 5, column=0, pady=5, padx=5, sticky="e"
        )
        for idx, var in enumerate(self.total_length_vars):
            ttk.Entry(self.form_frame, textvariable=var, width=10, 
                     state="readonly").grid(
                row=len(self.file_vars) + 5, column=idx + 1, pady=5, padx=5
            )

    def _add_file(self):
        """ファイル入力欄を追加"""
        self.file_vars.append(tk.StringVar())
        self.start_vars.append(tk.DoubleVar(value=0.0))
        self.end_vars.append(tk.DoubleVar(value=0.0))
        self.duration_vars.append(tk.DoubleVar(value=0.0))
        self.total_length_vars.append(tk.DoubleVar(value=0.0))
        self._file_ranges.append({"start": 0.0, "duration": 0.0, "total": 0.0})
        
        self._create_file_input_ui()
        self._add_timeline_for_file(len(self.file_vars) - 1)
        self._bind_var_traces()
        self.timeline_controller.redraw()

    def _remove_file(self):
        """最後のファイル入力欄を削除"""
        if len(self.file_vars) <= 1:
            messagebox.showwarning("削除エラー", "最後のファイルは削除できません。")
            return
        
        self.file_vars.pop()
        self.start_vars.pop()
        self.end_vars.pop()
        self.duration_vars.pop()
        self.total_length_vars.pop()
        self._file_ranges.pop()
        
        # タイムラインの最後の行を削除
        if self.timeline_rows:
            row = self.timeline_rows.pop()
            row.destroy()
        
        if self.timeline_canvases:
            self.timeline_canvases.pop()
        
        self._create_file_input_ui()
        self._bind_var_traces()
        self.timeline_controller.redraw()

    def _add_timeline_for_file(self, idx: int):
        """タイムラインを追加"""
        row = tk.Frame(self.editor_frame, bg=self.theme["bg"])
        row.pack(fill=tk.X, padx=20, pady=2)
        self.timeline_rows.append(row)
        
        tk.Label(row, text=f"ファイル{idx + 1}", bg=self.theme["bg"], 
                fg=self.theme["fg"]).pack(anchor="w")
        
        canvas = tk.Canvas(row, height=60, bg="#1e1e1e", highlightthickness=0)
        canvas.pack(fill=tk.X, pady=2)
        self.timeline_canvases.append(canvas)

    def _browse_file(self, index: int):
        """ファイルを参照"""
        library_dir = self._get_library_dir()
        path = filedialog.askopenfilename(
            title=f"ファイル{index + 1}の音声ファイルを選択",
            initialdir=str(library_dir),
            filetypes=[("Audio files", "*.mp3 *.mp4"), ("All files", "*.*")],
        )
        if path:
            self.file_vars[index].set(path)
            self._update_total_length_from_file(index, path)

    def _bind_var_traces(self):
        """変数の変更を監視"""
        for i in range(len(self.start_vars)):
            self.start_vars[i].trace_add(
                "write",
                lambda *_, idx=i: self.timeline_controller.sync_from_entries(
                    idx, use_end=False
                ),
            )
            self.duration_vars[i].trace_add(
                "write",
                lambda *_, idx=i: self.timeline_controller.sync_from_entries(
                    idx, use_end=False
                ),
            )
            self.end_vars[i].trace_add(
                "write",
                lambda *_, idx=i: self.timeline_controller.sync_from_entries(
                    idx, use_end=True
                ),
            )

    def _create_action_buttons(self):
        """アクションボタンを生成"""
        btn_frame = tk.Frame(self.scrollable_frame, bg=self.theme["bg"])
        btn_frame.pack(pady=15)
        
        def create_action_label(parent, text, command, bg_color, hover_bg):
            lbl = tk.Label(
                parent,
                text=text,
                bg=bg_color,
                fg="white",
                padx=14,
                pady=8,
                font=("Arial", 11),
                cursor="hand2",
            )
            
            def on_click(_event=None):
                command()
            
            def on_enter(_event=None):
                lbl.config(bg=hover_bg)
            
            def on_leave(_event=None):
                lbl.config(bg=bg_color)
            
            lbl.bind("<Button-1>", on_click)
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            return lbl
        
        create_action_label(
            btn_frame,
            text="mp4 → mp3 変換",
            command=self.on_convert,
            bg_color="#3498db",
            hover_bg="#4aa3df",
        ).pack(side=tk.LEFT, padx=10)
        
        create_action_label(
            btn_frame,
            text="選択範囲を再生",
            command=self.on_preview,
            bg_color="#2ecc71",
            hover_bg="#43d17e",
        ).pack(side=tk.LEFT, padx=10)
        
        create_action_label(
            self.scrollable_frame,
            text="保存してライブラリに追加",
            command=self.on_save_to_library,
            bg_color="#7f8c8d",
            hover_bg="#95a5a6",
        ).pack(pady=10)

    def _get_library_dir(self) -> Path:
        lib = Path(self.config_data.get("library_dir", "library"))
        if not lib.is_absolute():
            base = Path(__file__).resolve().parent
            lib = base / lib
        lib.mkdir(exist_ok=True)
        return lib

    def _update_total_length_from_file(self, index: int, path: str) -> None:
        audio_path = Path(path)
        duration_sec = get_duration_seconds(audio_path)
        
        if duration_sec is None:
            return
        
        self._file_ranges[index]["total"] = duration_sec
        self.total_length_vars[index].set(round(duration_sec, 1))
        self.timeline_controller.redraw()

    def _collect_segments(self, action_label: str):
        targets = []
        for idx, file_var in enumerate(self.file_vars):
            if file_var.get().strip():
                targets.append((idx, file_var))
        
        if not targets:
            messagebox.showwarning(
                "入力エラー", f"{action_label}するファイルを1つ以上入力してください。"
            )
            return []
        
        segments = []
        for idx, file_var in targets:
            r = self._file_ranges[idx]
            start = float(r.get("start", 0.0))
            duration = float(r.get("duration", 0.0))
            if duration <= 0:
                continue
            path = Path(file_var.get())
            if not path.is_file():
                messagebox.showerror("エラー", f"ファイルが見つかりません:\n{path}")
                continue
            segments.append((path, start, duration))
        
        return segments

    def on_convert(self) -> None:
        targets = []
        for file_var in self.file_vars:
            if file_var.get().strip():
                targets.append(file_var)
        
        if not targets:
            messagebox.showwarning("入力エラー", "変換するファイルを1つ以上入力してください。")
            return
        
        for var in targets:
            src = Path(var.get())
            try:
                out = convert_mp4_to_mp3(src)
            except FileNotFoundError as e:
                messagebox.showerror("エラー", str(e))
                continue
            except ConvertError as e:
                messagebox.showerror("変換エラー", str(e))
                continue
            
            if out == src and out.suffix.lower() == ".mp3":
                messagebox.showinfo("情報", f"{src.name} は mp3 のため変換をスキップしました。")
            else:
                var.set(str(out))
                messagebox.showinfo("完了", f"変換が完了しました:\n{out}")

    def on_save_to_library(self) -> None:
        segments = self._collect_segments("保存")
        if not segments:
            return
        tmp_path = concat_segments_to_tempfile(segments)
        if tmp_path is None:
            return
        
        library_dir = self._get_library_dir()
        filename = filedialog.asksaveasfilename(
            initialdir=str(library_dir),
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")],
            title="保存するファイル名を指定してください"
        )
        
        if not filename:
            try:
                tmp_path.unlink()
            except Exception:
                pass
            return
        
        copy_temp_to_library(library_dir, tmp_path, output_filename=Path(filename).name)
        
        try:
            tmp_path.unlink()
        except Exception:
            pass
    
    def on_preview(self) -> None:
        segments = self._collect_segments("プレビュー再生")
        if not segments:
            return
        preview_segments(segments)

