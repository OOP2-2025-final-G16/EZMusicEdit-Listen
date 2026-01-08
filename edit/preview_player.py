import subprocess
import tempfile
from pathlib import Path
from tkinter import messagebox
from typing import Iterable

from edit.segment_cutter import Segment, cut_segments_to_temp_files


def preview_segments(segments: Iterable[Segment]) -> None:
    """
    渡されたセグメントを順番に一時ファイルに切り出して再生する。
    segments: (元ファイル Path, 開始秒, 長さ秒) のタプルのイテラブル
    """

    segments = list(segments)
    if not segments:
        messagebox.showwarning("入力エラー", "再生する切り取り範囲がありません。")
        return

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # 共通ヘルパーを使って一時mp3として切り出し
            temp_files = cut_segments_to_temp_files(tmpdir_path, segments, "preview", "プレビュー用")
            if temp_files is None:
                return

            # 一時ファイルを順番に再生（=連結して再生するイメージ）
            for temp in temp_files:
                try:
                    subprocess.run(
                        [
                            "ffplay",
                            "-nodisp",
                            "-autoexit",
                            "-loglevel",
                            "error",
                            str(temp),
                        ],
                        check=True,
                    )
                except FileNotFoundError:
                    messagebox.showinfo(
                        "情報",
                        "ffplay が見つからないため、プレビュー再生ができませんでした。",
                    )
                    return
                except subprocess.CalledProcessError:
                    # 再生に失敗しても次は試さず終了
                    messagebox.showerror("エラー", "プレビュー再生中にエラーが発生しました。")
                    return
    except Exception as e:  # 想定外のエラー
        messagebox.showerror("エラー", f"プレビュー再生中に予期せぬエラーが発生しました:\n{e}")
