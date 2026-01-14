import subprocess
import tempfile
import shutil
from pathlib import Path
from tkinter import messagebox
from typing import Iterable, Optional
import datetime as _dt

from edit.segment_cutter import Segment, cut_segments_to_temp_files


def save_segments_to_library(library_dir: Path, segments: Iterable[Segment], output_filename: Optional[str] = None) -> Optional[Path]:
    """
    セグメント群を一時ファイルに切り出し、1つの mp3 に連結して保存する。
    library_dir: 保存先ディレクトリ
    segments: (元ファイル Path, 開始秒, 長さ秒) のタプルのイテラブル
    output_filename: 出力ファイル名（例: "my_song.mp3"）。None の場合はタイムスタンプベース

    正常終了時は保存先 Path を返す。失敗時は None を返す。
    """

    segments = list(segments)
    if not segments:
        messagebox.showwarning("入力エラー", "保存する切り取り範囲がありません。")
        return None

    library_dir.mkdir(exist_ok=True)

    # 出力ファイル名
    if output_filename is None:
        # デフォルト: タイムスタンプベース
        timestamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"edited_{timestamp}.mp3"
    
    out_path = library_dir / output_filename

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # 共通ヘルパーを使って一時mp3として切り出し
            temp_files = cut_segments_to_temp_files(tmpdir_path, segments, "seg", "保存用")
            if temp_files is None:
                return None

            # concat用リストファイルを作成
            list_file = tmpdir_path / "concat_list.txt"
            with list_file.open("w", encoding="utf-8") as f:
                for p in temp_files:
                    f.write(f"file '{p.as_posix()}'\n")

            # 一つのmp3に連結
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-f",
                        "concat",
                        "-safe",
                        "0",
                        "-i",
                        str(list_file),
                        "-c",
                        "copy",
                        str(out_path),
                    ],
                    check=True,
                    capture_output=True,
                )
            except FileNotFoundError:
                messagebox.showinfo(
                    "情報",
                    "ffmpeg が見つからないため、連結して保存できませんでした。",
                )
                return None
            except subprocess.CalledProcessError as e:
                messagebox.showerror(
                    "エラー",
                    f"連結処理に失敗しました:\n{e}",
                )
                return None
    except Exception as e:
        messagebox.showerror("エラー", f"保存中に予期せぬエラーが発生しました:\n{e}")
        return None

    messagebox.showinfo(
        "保存完了",
        f"切り取り範囲をライブラリに保存しました:\n{out_path}",
    )
    return out_path


def concat_segments_to_tempfile(segments: Iterable[Segment], suffix: str = ".mp3") -> Optional[Path]:
    """
    セグメント群を結合し、一時ファイル（削除フラグを無効化）に保存してその Path を返す。
    ライブラリには保存せず、呼び出し側で後片付けできるようにします。

    例: Pygame などファイルパスが必要なライブラリで即時再生したい場合に便利。

    正常終了時は一時ファイルの Path を返す。失敗時は None を返す。
    """
    segments = list(segments)
    if not segments:
        messagebox.showwarning("入力エラー", "結合する切り取り範囲がありません。")
        return None

    # 連結先となる一時ファイルを先に確保しておく（後で ffmpeg で上書き）
    try:
        tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        out_path = Path(tmp_out.name)
        tmp_out.close()
    except Exception as e:
        messagebox.showerror("エラー", f"一時ファイルの作成に失敗しました:\n{e}")
        return None

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            temp_files = cut_segments_to_temp_files(tmpdir_path, segments, "seg", "一時結合用")
            if temp_files is None:
                return None

            list_file = tmpdir_path / "concat_list.txt"
            with list_file.open("w", encoding="utf-8") as f:
                for p in temp_files:
                    f.write(f"file '{p.as_posix()}'\n")

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(list_file),
                    "-c",
                    "copy",
                    str(out_path),
                ],
                check=True,
                capture_output=True,
            )
    except FileNotFoundError:
        out_path.unlink(missing_ok=True)
        messagebox.showinfo("情報", "ffmpeg が見つからないため、一時ファイルを作成できませんでした。")
        return None
    except subprocess.CalledProcessError as e:
        out_path.unlink(missing_ok=True)
        messagebox.showerror("エラー", f"結合処理に失敗しました:\n{e}")
        return None
    except Exception as e:
        out_path.unlink(missing_ok=True)
        messagebox.showerror("エラー", f"一時ファイル作成中に予期せぬエラーが発生しました:\n{e}")
        return None

    return out_path


def copy_temp_to_library(library_dir: Path, tmp_path: Path, output_filename: Optional[str] = None) -> Optional[Path]:
    """
    一時ファイルをライブラリディレクトリにコピーして保存する。

    library_dir: 保存先ディレクトリ
    tmp_path: 一時ファイルのパス
    output_filename: 出力ファイル名（例: "my_song.mp3"）。None の場合はタイムスタンプベース

    正常終了時は保存先 Path を返す。失敗時は None を返す。
    """
    if not tmp_path.exists():
        messagebox.showerror("エラー", f"一時ファイルが見つかりません:\n{tmp_path}")
        return None

    library_dir.mkdir(parents=True, exist_ok=True)

    # 出力ファイル名
    if output_filename is None:
        # デフォルト: タイムスタンプベース
        timestamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"edited_{timestamp}.mp3"
    
    out_path = library_dir / output_filename

    try:
        shutil.copy2(str(tmp_path), str(out_path))
    except Exception as e:
        messagebox.showerror("エラー", f"ファイルの保存に失敗しました:\n{e}")
        return None

    messagebox.showinfo("保存完了", f"ファイルをライブラリに保存しました:\n{out_path}")
    return out_path
