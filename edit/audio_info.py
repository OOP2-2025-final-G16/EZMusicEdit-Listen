from pathlib import Path
import subprocess
from typing import Optional


class AudioInfoError(Exception):
    """音声情報取得に失敗したときの例外"""
    
def get_duration_seconds(path: Path) -> Optional[float]:
    """
    ffprobe を使って音声ファイルの長さ（秒）を取得する。
    取得に失敗した場合は None を返す。
    ffprobe が存在しない・エラー終了した場合も None を返す。
    """
    if not path.is_file():
        return None

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    try:
        duration_sec = float(result.stdout.strip())
    except ValueError:
        return None

    if duration_sec <= 0:
        return None

    return duration_sec