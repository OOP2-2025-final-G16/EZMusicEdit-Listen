import tkinter as tk
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class TimelineController:
    """
    タイムライン描画とドラッグ操作を担当するヘルパー。
    EditPage 側からは UI 部品と状態(list[dict])、tk.Variable を渡すだけにして、
    描画・秒数⇔座標変換・ドラッグ処理・テキスト表示などはここに集約する。
    """

    canvases: List[tk.Canvas]
    info_label: tk.Label
    file_ranges: List[Dict[str, float]]  # 各要素: {"start", "duration", "total"}
    start_vars: List[tk.DoubleVar]
    end_vars: List[tk.DoubleVar]
    duration_vars: List[tk.DoubleVar]
    total_length_vars: List[tk.DoubleVar]

    _active_index: int = field(init=False, default=0)
    _dragging_handle: str | None = field(init=False, default=None)
    _is_syncing: bool = field(init=False, default=False)

    # ===== 公開 API =====

    def bind_canvas_events(self) -> None:
        """各 Canvas にイベントハンドラをバインドする。"""

        for canvas in self.canvases:
            canvas.bind("<Configure>", self.on_resize)
            canvas.bind("<Button-1>", self.on_press)
            canvas.bind("<B1-Motion>", self.on_drag)
            canvas.bind("<ButtonRelease-1>", self.on_release)

    def redraw(self) -> None:
        """全タイムラインの再描画。"""

        if not self.canvases:
            return

        for idx, canvas in enumerate(self.canvases):
            self._draw_single_timeline(idx, canvas)

        self._update_info_label()

    def sync_from_entries(self, index: int, use_end: bool = False) -> None:
        """数値入力欄の値から内部状態・タイムラインを更新する。"""

        if not (0 <= index < len(self.file_ranges)) or self._is_syncing:
            return

        r = self.file_ranges[index]

        try:
            start = float(self.start_vars[index].get())
        except (TypeError, ValueError):
            start = r.get("start", 0.0)

        try:
            duration = float(self.duration_vars[index].get())
        except (TypeError, ValueError):
            duration = r.get("duration", 0.0)

        try:
            total = float(self.total_length_vars[index].get())
        except (TypeError, ValueError):
            total = r.get("total", 60.0)

        total = max(total, 1.0)
        start = max(0.0, min(start, total))

        if use_end:
            try:
                end = float(self.end_vars[index].get())
            except (TypeError, ValueError):
                end = start + max(0.0, duration)
            end = max(start, min(end, total))
            duration = max(0.0, end - start)
            self._is_syncing = True
            try:
                self.duration_vars[index].set(round(duration, 1))
            finally:
                self._is_syncing = False
        else:
            end = start + max(0.0, duration)
            end = max(start, min(end, total))
            duration = max(0.0, end - start)
            self._is_syncing = True
            try:
                self.end_vars[index].set(round(end, 1))
            finally:
                self._is_syncing = False

        r["start"] = start
        r["duration"] = duration
        r["total"] = total

        self.redraw()

    # ===== Canvas イベント =====

    def on_resize(self, _event) -> None:
        self.redraw()

    def on_press(self, event) -> None:
        canvas = event.widget
        try:
            idx = self.canvases.index(canvas)
        except ValueError:
            return

        self._active_index = idx

        r = self.file_ranges[idx]
        start = float(r.get("start", 0.0))
        duration = float(r.get("duration", 0.0))
        total = max(float(r.get("total", 1.0)), 1.0)
        end = start + max(0.0, duration)

        x1 = self._sec_to_x(canvas, total, start)
        x2 = self._sec_to_x(canvas, total, end)
        self._dragging_handle = "start" if abs(event.x - x1) < abs(event.x - x2) else "end"

    def on_drag(self, event) -> None:
        if self._dragging_handle not in ("start", "end"):
            return

        canvas = event.widget
        try:
            idx = self.canvases.index(canvas)
        except ValueError:
            return

        r = self.file_ranges[idx]
        start = float(r.get("start", 0.0))
        duration = float(r.get("duration", 0.0))
        total = max(float(r.get("total", 1.0)), 1.0)
        end = start + max(0.0, duration)

        sec = self._x_to_sec(canvas, total, event.x)
        if self._dragging_handle == "start":
            start = min(sec, end)
        else:
            end = max(sec, start)

        duration = max(0.0, end - start)
        r["start"] = start
        r["duration"] = duration

        self.start_vars[idx].set(round(start, 1))
        self.duration_vars[idx].set(round(duration, 1))
        self.end_vars[idx].set(round(end, 1))

        self.redraw()

    def on_release(self, _event) -> None:
        self._dragging_handle = None

    # ===== 内部ヘルパー =====

    def _format_time(self, sec: float) -> str:
        try:
            s = max(0.0, float(sec))
        except (TypeError, ValueError):
            s = 0.0
        m = int(s) // 60
        s_int = int(s) % 60
        return f"{m:02d}:{s_int:02d}"

    def _sec_to_x(self, canvas: tk.Canvas, total: float, sec: float) -> float:
        width = max(canvas.winfo_width(), 1)
        margin = 20
        inner = max(width - margin * 2, 1)
        total = max(total, 1.0)
        sec = max(0.0, min(float(sec), total))
        return margin + inner * (sec / total)

    def _x_to_sec(self, canvas: tk.Canvas, total: float, x: float) -> float:
        width = max(canvas.winfo_width(), 1)
        margin = 20
        inner = max(width - margin * 2, 1)
        total = max(total, 1.0)
        x = max(margin, min(x, width - margin))
        return total * (x - margin) / inner

    def _draw_single_timeline(self, idx: int, canvas: tk.Canvas) -> None:
        canvas.delete("all")

        width = max(canvas.winfo_width(), 1)
        height = max(canvas.winfo_height(), 1)
        margin = 20
        bar_top = height / 2 - 10
        bar_bottom = height / 2 + 10

        # ベースバー
        canvas.create_rectangle(
            margin,
            bar_top,
            width - margin,
            bar_bottom,
            fill="#333",
            outline="",
        )

        r = self.file_ranges[idx]
        start = float(r.get("start", 0.0))
        duration = float(r.get("duration", 0.0))
        total = max(float(r.get("total", 1.0)), 1.0)

        start = max(0.0, min(start, total))
        end = max(start, min(start + max(0.0, duration), total))

        x1 = self._sec_to_x(canvas, total, start)
        x2 = self._sec_to_x(canvas, total, end)
        handle_w = 4

        canvas.create_rectangle(x1, bar_top, x2, bar_bottom, fill="#2ecc71", outline="")
        canvas.create_rectangle(
            x1 - handle_w,
            bar_top - 5,
            x1 + handle_w,
            bar_bottom + 5,
            fill="#ecf0f1",
            outline="",
        )
        canvas.create_rectangle(
            x2 - handle_w,
            bar_top - 5,
            x2 + handle_w,
            bar_bottom + 5,
            fill="#ecf0f1",
            outline="",
        )

    def _update_info_label(self) -> None:
        lines: list[str] = []
        for idx, r in enumerate(self.file_ranges):
            start = float(r.get("start", 0.0))
            duration = float(r.get("duration", 0.0))
            total = max(float(r.get("total", 1.0)), 1.0)
            end = start + max(0.0, duration)

            marker = "★" if idx == self._active_index else " "
            lines.append(
                f"{marker} ファイル{idx + 1}  "
                f"開始: {self._format_time(start)}  / "
                f"終了: {self._format_time(end)}  "
                f"(長さ: {self._format_time(end - start)} / 全長: {self._format_time(total)})"
            )

        self.info_label.config(text="\n".join(lines))
