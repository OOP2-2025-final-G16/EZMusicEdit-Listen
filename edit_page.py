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

        title = tk.Label(
            self,
            text="✂️ EDIT & ADD",
            font=("Arial", 20, "bold"),
            bg=theme["bg"],
            fg=theme["fg"],
        )
        title.pack(pady=20)

        # ---------- ファイル入力 ----------
        form = tk.Frame(self, bg=theme["bg"])
        form.pack(pady=10)

        self.file1_var = tk.StringVar()
        self.file2_var = tk.StringVar()

        tk.Label(form, text="ファイル1(mp3/mp4):", bg=theme["bg"], fg=theme["fg"]).grid(
            row=0, column=0, pady=5, padx=5, sticky="e"
        )
        ttk.Entry(form, textvariable=self.file1_var, width=40).grid(
            row=0, column=1, pady=5, padx=5
        )
        ttk.Button(form, text="参照...", command=self.browse_file1).grid(
            row=0, column=2, padx=5, pady=5
        )

        tk.Label(form, text="ファイル2(mp3/mp4):", bg=theme["bg"], fg=theme["fg"]).grid(
            row=1, column=0, pady=5, padx=5, sticky="e"
        )
        ttk.Entry(form, textvariable=self.file2_var, width=40).grid(
            row=1, column=1, pady=5, padx=5
        )
        ttk.Button(form, text="参照...", command=self.browse_file2).grid(
            row=1, column=2, padx=5, pady=5
        )

        # ---------- 切り取りパラメータ ----------
        self.start_vars = [tk.DoubleVar(value=0.0) for _ in range(2)]
        self.end_vars = [tk.DoubleVar(value=0.0) for _ in range(2)]
        self.duration_vars = [tk.DoubleVar(value=0.0) for _ in range(2)]
        self.total_length_vars = [tk.DoubleVar(value=0.0) for _ in range(2)]

        tk.Label(form, text="", bg=theme["bg"], fg=theme["fg"]).grid(
            row=2, column=0, pady=5, padx=5, sticky="e"
        )
        tk.Label(form, text="ファイル1", bg=theme["bg"], fg=theme["fg"]).grid(
            row=2, column=1, pady=5, padx=5, sticky="w"
        )
        tk.Label(form, text="ファイル2", bg=theme["bg"], fg=theme["fg"]).grid(
            row=2, column=2, pady=5, padx=5, sticky="w"
        )

        # 開始
        tk.Label(form, text="開始位置(秒):", bg=theme["bg"], fg=theme["fg"]).grid(
            row=3, column=0, pady=5, padx=5, sticky="e"
        )
        ttk.Entry(form, textvariable=self.start_vars[0], width=10).grid(
            row=3, column=1, sticky="w", pady=5, padx=5
        )
        ttk.Entry(form, textvariable=self.start_vars[1], width=10).grid(
            row=3, column=2, sticky="w", pady=5, padx=5
        )

        # 終了
        tk.Label(form, text="終了位置(秒):", bg=theme["bg"], fg=theme["fg"]).grid(
            row=4, column=0, pady=5, padx=5, sticky="e"
        )
        ttk.Entry(form, textvariable=self.end_vars[0], width=10).grid(
            row=4, column=1, sticky="w", pady=5, padx=5
        )
        ttk.Entry(form, textvariable=self.end_vars[1], width=10).grid(
            row=4, column=2, sticky="w", pady=5, padx=5
        )

        # 長さ
        tk.Label(form, text="長さ(秒):", bg=theme["bg"], fg=theme["fg"]).grid(
            row=5, column=0, pady=5, padx=5, sticky="e"
        )
        ttk.Entry(form, textvariable=self.duration_vars[0], width=10).grid(
            row=5, column=1, sticky="w", pady=5, padx=5
        )
        ttk.Entry(form, textvariable=self.duration_vars[1], width=10).grid(
            row=5, column=2, sticky="w", pady=5, padx=5
        )

        # 曲の長さ（表示のみ）
        tk.Label(form, text="曲の長さ(秒):", bg=theme["bg"], fg=theme["fg"]).grid(
            row=6, column=0, pady=5, padx=5, sticky="e"
        )
        ttk.Entry(
            form,
            textvariable=self.total_length_vars[0],
            width=10,
            state="readonly",
        ).grid(row=6, column=1, sticky="w", pady=5, padx=5)
        ttk.Entry(
            form,
            textvariable=self.total_length_vars[1],
            width=10,
            state="readonly",
        ).grid(row=6, column=2, sticky="w", pady=5, padx=5)

        # 内部状態（切り取り範囲）
        self._file_ranges = [
            {"start": 0.0, "duration": 0.0, "total": 0.0},
            {"start": 0.0, "duration": 0.0, "total": 0.0},
        ]

        # ---------- ボタン群 ----------
        btn_frame = tk.Frame(self, bg=theme["bg"])
        btn_frame.pack(pady=15)

        # macOS では tk.Button の bg が反映されにくいので
        # 色付きアクションボタンは Label を使って実装する
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
            self,
            text="保存してライブラリに追加",
            command=self.on_save_to_library,
            bg_color="#7f8c8d",
            hover_bg="#95a5a6",
        ).pack(pady=10)

        # ---------- タイムライン ----------
        editor_frame = tk.Frame(self, bg=theme["bg"])
        editor_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        tk.Label(
            editor_frame,
            text="切り取りタイムライン",
            bg=theme["bg"],
            fg=theme["fg"],
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=20)

        self.timeline_canvases = []
        for idx in range(2):
            row = tk.Frame(editor_frame, bg=theme["bg"])
            row.pack(fill=tk.X, padx=20, pady=2)

            tk.Label(
                row,
                text=f"ファイル{idx + 1}",
                bg=theme["bg"],
                fg=theme["fg"],
            ).pack(anchor="w")

            canvas = tk.Canvas(row, height=60, bg="#1e1e1e", highlightthickness=0)
            canvas.pack(fill=tk.X, pady=2)

            self.timeline_canvases.append(canvas)

        self.timeline_info = tk.Label(
            editor_frame,
            text="",
            bg=theme["bg"],
            fg=theme["fg"],
            anchor="w",
        )
        self.timeline_info.pack(fill=tk.X, padx=20)

        # タイムラインコントローラに UI 部品と状態を渡す
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

        # trace で数値入力とタイムラインを同期
        for i in range(2):
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

        self.timeline_controller.redraw()

    # ---------- ファイル選択 ----------
    def _get_library_dir(self) -> Path:
        lib = Path(self.config_data.get("library_dir", "library"))
        if not lib.is_absolute():
            base = Path(__file__).resolve().parent
            lib = base / lib
        lib.mkdir(exist_ok=True)
        return lib

    def browse_file1(self) -> None:
        library_dir = self._get_library_dir()
        path = filedialog.askopenfilename(
            title="ファイル1の音声ファイルを選択",
            initialdir=str(library_dir),
            filetypes=[("Audio files", "*.mp3 *.mp4"), ("All files", "*.*")],
        )
        if path:
            self.file1_var.set(path)
            self._active_index = 0
            self._update_total_length_from_file(0, path)

    def browse_file2(self) -> None:
        library_dir = self._get_library_dir()
        path = filedialog.askopenfilename(
            title="ファイル2の音声ファイルを選択",
            initialdir=str(library_dir),
            filetypes=[("Audio files", "*.mp3 *.mp4"), ("All files", "*.*")],
        )
        if path:
            self.file2_var.set(path)
            self._active_index = 1
            self._update_total_length_from_file(1, path)

    # ---------- 長さ取得 ----------
    def _update_total_length_from_file(self, index: int, path: str) -> None:
        audio_path = Path(path)
        duration_sec = get_duration_seconds(audio_path)

        if duration_sec is None:
            # 取得に失敗しても致命的ではないので、そのまま無視
            return

        self._file_ranges[index]["total"] = duration_sec
        self.total_length_vars[index].set(round(duration_sec, 1))
        self.timeline_controller.redraw()

    # ---------- 変換 / 保存 / プレビュー ----------
    def _collect_segments(self, action_label: str):
        targets = []
        if self.file1_var.get().strip():
            targets.append((0, self.file1_var))
        if self.file2_var.get().strip():
            targets.append((1, self.file2_var))

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
        if self.file1_var.get().strip():
            targets.append(self.file1_var)
        if self.file2_var.get().strip():
            targets.append(self.file2_var)

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

        # ユーザーにファイル名を指定させる
        library_dir = self._get_library_dir()
        filename = filedialog.asksaveasfilename(
            initialdir=str(library_dir),
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")],
            title="保存するファイル名を指定してください"
        )
        
        if not filename:  # キャンセル時
            try:
                tmp_path.unlink()
            except Exception:
                pass
            return
        
        # 一時ファイルをライブラリに保存
        copy_temp_to_library(library_dir, tmp_path, output_filename=Path(filename).name)
        
        # 保存後は一時ファイルを自動削除
        try:
            tmp_path.unlink()
        except Exception:
            pass
    
    def on_preview(self) -> None:
        segments = self._collect_segments("プレビュー再生")
        if not segments:
            return
        preview_segments(segments)
