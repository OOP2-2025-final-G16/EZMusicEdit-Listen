from __future__ import annotations

# プレイリスト順序をUIから独立して扱うユーティリティ
# XMLの読み書きと並び替えロジックを一箇所に集約
# UIはこのAPIだけ呼べば順序維持と更新ができる
# 使い方:
#   manager = XmlPlaylistManager(Path("playlist.xml"))
#   entries = manager.load_entries()
#   entries = manager.add_missing(entries, manager.scan_directory(Path("music")))
#   ordered = manager.reorder(entries, SortMode.TITLE)
#   manager.save_entries(ordered)
import argparse
import time
import unicodedata
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Optional
import xml.etree.ElementTree as ET


class SortMode(str, Enum):
    ADDED = "added"        # 追加された順番で並び替え
    TITLE = "title"        # タイトルを正規化してソート
    PATH = "path"          # パス文字列の辞書順で並び替え


@dataclass
class TrackEntry:
    path: str
    title: str
    added_seq: int
    # order属性は保存時に付与するだけなのでメモリ上では保持しない


class XmlPlaylistManager:
    # XMLの読み書きと並び替えロジックをまとめたクラス
    # added_seqは追加時刻、orderは表示順序で別の概念

    def __init__(self, xml_path: Path):
        self.xml_path = Path(xml_path)

    def load_entries(self) -> List[TrackEntry]:
        # XMLを読み込んでTrackEntryリストを返す
        # ファイルが無ければ空リストを返す
        if not self.xml_path.exists():
            return []

        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        entries: List[TrackEntry] = []
        for idx, node in enumerate(root.findall("track")):
            # titleが無ければパス名から補完
            # added_seqが無ければ読み込み順を使う
            path = node.get("path", "")
            title = node.get("title") or Path(path).name
            added_seq = _safe_int(node.get("added_seq"), idx)
            entries.append(TrackEntry(path=path, title=title, added_seq=added_seq))
        return entries

    def save_entries(self, entries: Iterable[TrackEntry]) -> None:
        # 現在の順序をXMLに保存する
        # 既存ファイルは上書きされる
        root = ET.Element("playlist")
        root.set("generated_at", str(int(time.time())))

        for order_idx, entry in enumerate(entries):
            # orderは0始まりで保存して表示順序を記録
            track = ET.SubElement(root, "track")
            track.set("path", entry.path)
            track.set("title", entry.title)
            track.set("added_seq", str(entry.added_seq))
            track.set("order", str(order_idx))

        # ディレクトリが無ければ作成してからファイル書き出し
        self.xml_path.parent.mkdir(parents=True, exist_ok=True)
        tree = ET.ElementTree(root)
        tree.write(self.xml_path, encoding="utf-8", xml_declaration=True)

    def reorder(self, entries: Iterable[TrackEntry], mode: SortMode) -> List[TrackEntry]:
        # 指定されたモードで並び替えたリストを返す
        # 元のリストは変更しない
        entries_list = list(entries)

        if mode == SortMode.ADDED:
            # 追加順で昇順ソート
            return sorted(entries_list, key=lambda e: e.added_seq)
        if mode == SortMode.TITLE:
            # タイトルを正規化してからソート、同じタイトルなら追加順で安定ソート
            return sorted(entries_list, key=lambda e: (_normalize_title(e.title), e.added_seq))
        if mode == SortMode.PATH:
            # パスを小文字化して辞書順、同値は追加順で安定化
            return sorted(entries_list, key=lambda e: (e.path.casefold(), e.added_seq))
        return entries_list

    def add_missing(self, entries: List[TrackEntry], new_tracks: Iterable[Path]) -> List[TrackEntry]:
        # 既存に無いパスだけを末尾に追加して連番を振る
        known_paths = {entry.path for entry in entries}
        added_seq_start = max([e.added_seq for e in entries], default=-1) + 1
        result = list(entries)
        for offset, track_path in enumerate(new_tracks):
            resolved = str(track_path)
            if resolved in known_paths:
                # 既に登録済みならスキップ
                continue
            result.append(
                TrackEntry(path=resolved, title=track_path.name, added_seq=added_seq_start + offset)
            )
        return result

    def scan_directory(self, directory: Path, extensions: Optional[List[str]] = None) -> List[Path]:
        # ディレクトリ以下を再帰的に走査してファイルを集める
        # 対象拡張子のみをソート順で返す
        # extensionsがNoneなら標準的な音声形式を使う
        if extensions is None:
            extensions = [".mp3", ".wav", ".flac", ".aac", ".m4a"]

        directory = Path(directory)
        files: List[Path] = []
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix.lower() in extensions:
                files.append(path)
        return files


def _normalize_title(title: str) -> str:
    # タイトルを正規化してソート時の安定性を確保
    # 大文字小文字と濁点を統一する
    folded = unicodedata.normalize("NFKD", title).casefold()
    return folded


def _safe_int(value: Optional[str], default: int) -> int:
    # 文字列を数値に変換、失敗時はデフォルト値を返す
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


def run_cli(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Playlist XML ordering tool")
    parser.add_argument("--xml", type=Path, required=True, help="Path to playlist XML")
    parser.add_argument("--scan", type=Path, help="Directory to scan and append")
    parser.add_argument("--mode", choices=[m.value for m in SortMode], default=SortMode.ADDED.value)
    parser.add_argument("--ext", nargs="*", help="File extensions to include (default: audio files)")
    args = parser.parse_args(argv)

    # CLIフロー: 読み込み -> スキャンして不足曲追加 -> 並び替え -> XML保存

    manager = XmlPlaylistManager(args.xml)
    entries = manager.load_entries()

    if args.scan:
        # ドット付きの拡張子に統一してからディレクトリ走査
        extensions = [e if e.startswith(".") else f".{e}" for e in (args.ext or [])] or None
        scanned = manager.scan_directory(args.scan, extensions)
        entries = manager.add_missing(entries, scanned)

    mode = SortMode(args.mode)
    entries = manager.reorder(entries, mode)
    manager.save_entries(entries)

    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
