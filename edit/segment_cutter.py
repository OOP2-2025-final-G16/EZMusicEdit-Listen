import logging
import subprocess
from pathlib import Path
from tkinter import messagebox
from typing import Iterable, Tuple, List, Optional


logger = logging.getLogger(__name__)

Segment = Tuple[Path, float, float]

def cut_segments_to_temp_files(
    tmpdir: Path,
    segments: Iterable[Segment],
    prefix: str,
    purpose_label: str,
) -> Optional[List[Path]]:
    """
    セグメント群を一時ディレクトリに mp3 として切り出して返す。
    tmpdir: 一時ディレクトリの Path
    segments: (元ファイル Path, 開始秒, 長さ秒) のイテラブル
    prefix: 出力ファイル名のプレフィックス（例: "preview", "seg"）
    purpose_label: メッセージ用の用途ラベル（例: "プレビュー用", "保存用"）

    ffmpeg / ffplay の有無や実行エラー時のメッセージボックス表示・
    ロギングもここで行い、失敗時は None を返す。
    """

    temp_files: List[Path] = []

    for i, (src, start, duration) in enumerate(segments):
        out_path = tmpdir / f"{prefix}_{i}.mp3"
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-ss",
                    str(start),
                    "-t",
                    str(duration),
                    "-i",
                    str(src),
                    "-acodec",
                    "copy",
                    str(out_path),
                ],
                check=True,
                capture_output=True,
            )
        except FileNotFoundError:
            msg = f"ffmpeg が見つからないため、{purpose_label}の切り出しができませんでした。"
            logger.error(msg)
            messagebox.showinfo("情報", msg)
            return None
        except subprocess.CalledProcessError as e:
            msg = f"{purpose_label}の切り出しに失敗しました:\n{src}\n{e}"
            logger.error(msg)
            messagebox.showerror("エラー", msg)
            return None

        temp_files.append(out_path)

    return temp_files
