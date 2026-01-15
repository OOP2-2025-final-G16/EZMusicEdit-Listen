# EZMusicEdit-Listen
複雑な操作なしに動画のクリップを作って再生できるGUIアプリ。

## 概要
- 複数音源から任意区間を切り出し、連結して再生・保存できます。
- 切り出し・連結は `ffmpeg`、情報取得は `ffprobe`、プレビュー再生は `ffplay` を利用します。
- エラーや状態通知は `tkinter.messagebox` で表示します。

## 依存ツール
- 必須: `ffmpeg`（`ffprobe`/`ffplay` を含む）
- macOS のインストール例:

```bash
brew install ffmpeg
```

操作方法
アプリは主に3つの画面（タブ）で構成されており、直感的な操作が可能

1. ライブラリ画面
保存済みの楽曲を管理・再生するメイン画面

楽曲の再生: リストから曲を選択し、再生ボタンで音楽を聴く
一覧表示: ライブラリに保存されたすべての楽曲がリストアップ

2. プレイリスト画面
お気に入りの曲を組み合わせて自分だけのリストを作成・再生

プレイリストの作成: ライブラリから曲を選び、新規プレイリストを作成して保存
プレイリストの再生: 作成したプレイリストを選択すると、連続して楽曲が再生

3. 追加・編集画面
新しい音源の取り込みや、特定区間の切り出し加工

ライブラリへの追加: PC上の音声・動画ファイルを選択し、ライブラリへインポート
セグメント編集: * タイムライン上でドラッグ、または数値入力により、音源の「開始時間」と「長さ」を指定.曲と曲を繋げることもできる

プレビュー: 保存前に ffplay を使用して、編集した区間を試聴

保存: 編集した内容は新しい楽曲としてライブラリへ保存されます。

## 主要モジュール
- [edit/segment_cutter.py](edit/segment_cutter.py)
	- `Segment`: `Path, start_sec, duration_sec` のタプル型。
	- `cut_segments_to_temp_files(tmpdir, segments, prefix, purpose_label)`: セグメントを一時ディレクトリに個別 MP3 として切り出し。
- [edit/library_saver.py](edit/library_saver.py)
	- `save_segments_to_library(library_dir, segments, output_filename=None)`: 連結してライブラリに保存。
	- `concat_segments_to_bytes(segments)`: 連結済み MP3 をメモリの `bytes` で返す（保存しない）。
	- `concat_segments_to_file(segments, output_path)`: 連結済み MP3 を指定パスへ保存。
	- `concat_segments_to_tempfile(segments, suffix='.mp3')`: 連結済み MP3 を一時ファイルに保存してパスを返す。
- [edit/bytes_saver.py](edit/bytes_saver.py)
	- `save_bytes_to_file(data, output_path)`: 任意の `bytes` を保存。
	- `save_mp3_bytes(data, output_path)`: `.mp3` 拡張子を保証して保存。
	- `save_mp3_bytes_with_timestamp(data, directory, prefix='edited')`: タイムスタンプ付きファイル名で保存。
- [edit/preview_player.py](edit/preview_player.py)
	- `preview_segments(segments)`: 切り出した一時 MP3 を順に `ffplay` で再生（簡易プレビュー）。
- [edit/audio_info.py](edit/audio_info.py)
	- `get_duration_seconds(path)`: `ffprobe` で音声長さ（秒）を取得。
- [edit/timeline_helper.py](edit/timeline_helper.py)
	- `TimelineController`: タイムライン描画・ドラッグ編集・数値欄同期・表示更新を担当。

## クイックスタート

```bash
python MyApp.py
```

## 使い方（コード例）

連結してファイル保存:

```python
from pathlib import Path
from edit.library_saver import concat_segments_to_file

# segments は [(Path("input.mp3"), 10.0, 5.0), ...] の形式
out = concat_segments_to_file(segments, Path("output/merged.mp3"))
```

連結結果を `bytes` として取得（保存せず利用）:

```python
from pathlib import Path
from edit.library_saver import concat_segments_to_bytes
from edit.bytes_saver import save_mp3_bytes_with_timestamp

data = concat_segments_to_bytes(segments)
if data is not None:
		save_mp3_bytes_with_timestamp(data, Path("library"), prefix="edited")
```

一時ファイルのパスを取得（パスが必要なライブラリ向け）:

```python
from edit.library_saver import concat_segments_to_tempfile

tmp_mp3 = concat_segments_to_tempfile(segments)
if tmp_mp3 is not None:
		# ここで再生/読み込みなどに使用（使用後は削除推奨）
		pass
```

プレビュー再生:

```python
from edit.preview_player import preview_segments

preview_segments(segments)
```

音声長さの取得:

```python
from pathlib import Path
from edit.audio_info import get_duration_seconds

length = get_duration_seconds(Path("input.mp3"))
```

## エラーハンドリング
- 外部コマンド未インストール・失敗時はメッセージを表示し、安全に中断します（`None` を返すなど）。
- ファイル操作失敗時も同様に通知します。
