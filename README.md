# EZMusicEdit-Listen

> **✨ 複雑な設定なし。タイムラインをドラッグするだけで、音声クリップ編集が完成。**

複雑な操作なしに動画のクリップを作って再生できるGUIアプリ。

## 🎯 テーマ

**「直感的な音声編集」**

音声編集ツール（Adobe Audition、GarageBand など）は高機能で高額。でも、**「複数の音声ファイルから自分の好きな部分だけを切り出して、つなぎ合わせたい」** という単純なニーズに応えるアプリがほしい。

EZMusicEdit-Listen は、そのシンプルなニーズを徹底的に追求しました。

---

## ⭐ アピールポイント

### 1. **直感的なUI - タイムラインドラッグ編集**
- 複雑なボタンやメニューなし
- **マウスをドラッグするだけ** で音声の開始位置と終了位置を指定
- 視覚的にわかりやすい3つの画面構成

### 2. **4ステップで完成**
```
ファイル指定 → タイムラインをドラッグ → 再生確認 → 保存
```
4ステップで音声編集が完了。難しい設定は一切不要。

### 3. **複数音源をカンタン組み合わせ**
- ファイル1、ファイル2、ファイル3...と複数ファイルを同時編集
- 各ファイルから切り出した部分を **自動的に連結**
- DJの「つなぎ」のようなプレイリスト作成も可能

### 4. **MP4・MP3 両対応**
- MP4 → MP3 への自動変換機能
- 動画ファイルから直接音声を抽出して編集可能

### 5. **プレビュー再生で確認**
- 編集内容を保存前に試聴可能
- 「思ってたのと違う」を事前に防止

### 6. **機能的なライブラリ＆プレイリスト管理**
| 機能 | 説明 |
|------|------|
| **ライブラリ** | 保存済みの楽曲をリスト表示・再生 |
| **プレイリスト** | 複数の曲を組み合わせて再生順序を管理 |
| **編集画面** | タイムラインで視覚的に音声編集 |

---

## 概要

- 複数音源から任意区間を切り出し、連結して再生・保存できます。
- 切り出し・連結は `ffmpeg`、情報取得は `ffprobe`、プレビュー再生は `ffplay` を利用します。
- エラーや状態通知は `tkinter.messagebox` で表示します。

---
- 必須: `ffmpeg`（`ffprobe`/`ffplay` を含む）
- macOS のインストール例:

```bash
brew install ffmpeg
```

## 前提条件

### システム要件

| 項目 | 要件 |
|------|------|
| **OS** | macOS 10.13+, Linux, Windows 10+ |
| **Python** | 3.9 以上 |
| **ffmpeg** | 4.0 以上 |
| **メモリ** | 最小 4GB（音声ファイル処理時） |

### OS別セットアップ

#### macOS（推奨）

```bash
# 1. ffmpeg をインストール
brew install ffmpeg

# 2. インストール確認
ffmpeg -version
ffprobe -version
ffplay -version
```

#### Linux（Ubuntu/Debian）

```bash
# 1. パッケージマネージャーでインストール
sudo apt update
sudo apt install ffmpeg

# 2. インストール確認
ffmpeg -version
ffprobe -version
ffplay -version
```

#### Windows

```bash
# オプション1: chocolatey を使用
choco install ffmpeg

# オプション2: scoop を使用
scoop install ffmpeg

# オプション3: 公式サイトから手動ダウンロード
# https://ffmpeg.org/download.html
```

### Python 環境構築

```bash
# 1. Python 3.9+ がインストール済みか確認
python3 --version

# 2. リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/EZMusicEdit-Listen.git
cd EZMusicEdit-Listen

# 3. 仮想環境を作成（オプションだが推奨）
python3 -m venv venv

# 4. 仮想環境を有効化
# macOS/Linux の場合
source venv/bin/activate

# Windows の場合
venv\Scripts\activate

# 5. 依存パッケージはアプリに同梱されているため、追加インストール不要
```

### ディレクトリ構成

アプリ起動時に以下のディレクトリが自動作成されます：

```
EZMusicEdit-Listen/
├── MyApp.py                 # メインアプリケーション
├── README.md                # このファイル
├── pages/
│   ├── edit_page.py         # 編集・追加画面
│   ├── library_page.py      # ライブラリ画面
│   └── playlist_page.py     # プレイリスト画面
├── edit/
│   ├── audio_info.py        # 音声情報取得
│   ├── segment_cutter.py    # セグメント切り出し
│   ├── library_saver.py     # 保存処理
│   ├── preview_player.py    # プレビュー再生
│   ├── timeline_helper.py   # タイムライン制御
│   └── changemp3.py         # MP4→MP3変換
├── misc/
│   ├── constants.py         # 定数定義
│   └── library.py           # ライブラリ管理
├── library_file/            # ✅ 自動作成（保存済み楽曲）
├── playlist_file/           # ✅ 自動作成（プレイリストデータ）
└── editfiles/               # ✅ 自動作成（一時ファイル）
```

### トラブルシューティング

| 問題 | 原因 | 解決策 |
|------|------|--------|
| `ffmpeg: command not found` | ffmpeg未インストール | OS別セットアップを実行 |
| `ModuleNotFoundError: No module named 'tkinter'` | tkinter未インストール | `sudo apt install python3-tk`（Linux）|
| 音声ファイルが再生されない | ffplay パスが通っていない | `which ffplay` で確認、PATHを設定 |
| ライブラリディレクトリが作成されない | パーミッション不足 | ホームディレクトリ内で実行 |

---

## 実行方法

### アプリの起動

```bash
# リポジトリディレクトリに移動
cd EZMusicEdit-Listen

# アプリを起動
python3 MyApp.py
```

### 初回起動時の処理

1. **ディレクトリの自動作成**
   - `library_file/` - ライブラリディレクトリ
   - `playlist_file/` - プレイリストディレクトリ
   - `editfiles/` - 一時ファイルディレクトリ

2. **GUI の起動**
   - 3つのタブ（ライブラリ、プレイリスト、編集）が表示されます
   - ライブラリ画面がデフォルトで開きます

### 基本的な使い方フロー

```
1. 編集画面 → 音源ファイル（MP3/MP4）を指定
        ↓
2. 切り出し範囲をタイムラインでドラッグ指定
        ↓
3. プレビュー再生で確認
        ↓
4. 「保存してライブラリに追加」でライブラリ保存
        ↓
5. ライブラリ画面で再生・管理
        ↓
6. プレイリスト画面で複数曲を組み合わせ
```

---

## 役割分担・サポート情報

### 開発チーム

| 役割 | 学籍番号 | 担当者名 | 担当機能 | 連絡先 |
|--------|--------|----------|--------|
| プロジェクトリード | X24006 | 井手和海 | - | - |
| 機能開発 | K21003 | 高宮千聖 | ライブラリ | - |
| 機能開発 | k24091 | 浅山心良 | - | - |
| 機能開発 | k24109 | 中島優斗 | プレイリスト | - |
| 機能開発 | k24110 | 中本夏生 | 編集機能・タイムライン | https://github.com/nakamoto007 |

### ドキュメント

- [README.md](README.md) - このファイル（全体ガイド）

---
アプリは3つの画面で構成されている

- ライブラリ画面
	保存済みの楽曲を管理・再生するメイン画面

	楽曲の再生: リストから曲を選択し、再生ボタンで音楽を聴く
	一覧表示: ライブラリに保存されたすべての楽曲がリストアップ

- プレイリスト画面
	お気に入りの曲を組み合わせて自分だけのリストを作成・再生

	プレイリストの作成: ライブラリから曲を選び、新規プレイリストを作成して保存
	プレイリストの再生: 作成したプレイリストを選択すると、連続して楽曲が再生

- 追加・編集画面
	新しい音源の取り込みや、特定区間の切り出し加工

	ライブラリへの追加: PC上の音声・動画ファイルを選択し、ライブラリへインポート
	セグメント編集: * タイムライン上でドラッグ、または数値入力により、音源の「開始時間」と「長さ」を指定.曲と曲を繋げることもできる
	プレビュー: 保存前に編集した区間を試聴

保存: 編集した内容は新しい楽曲としてライブラリへ保存されます。

---

## 📋 仕様書

### 機能仕様

| 機能 | 説明 | ステータス |
|------|------|----------|
| **ファイル選択** | MP3/MP4ファイルを複数選択可能 | ✅ 実装済み |
| **タイムライン編集** | マウスドラッグで開始位置・終了位置を指定 | ✅ 実装済み |
| **数値入力編集** | 秒単位で正確な位置指定 | ✅ 実装済み |
| **複数ファイル対応** | 複数ファイルを同時編集・自動連結 | ✅ 実装済み |
| **MP4→MP3変換** | MP4ファイルを自動MP3化 | ✅ 実装済み |
| **プレビュー再生** | 編集内容を保存前に試聴 | ✅ 実装済み |
| **ライブラリ管理** | 保存済み楽曲の再生・一覧表示 | ✅ 実装済み |
| **プレイリスト** | 複数曲を順序付けで組み合わせ | ✅ 実装済み |
| **自動ディレクトリ作成** | library_file/, playlist_file/ 自動作成 | ✅ 実装済み |

### 制限事項・動作環境

| 項目 | 仕様 |
|------|------|
| **対応形式** | MP3, MP4（ffmpeg対応形式全般） |
| **最大ファイルサイズ** | 制限なし（メモリ・ディスク次第） |
| **最大処理時間** | ファイルサイズに依存 |
| **同時編集ファイル数** | 無制限（UI上は動的に追加可能） |
| **プレイリスト内曲数** | 無制限 |
| **サンプリングレート** | ffmpeg対応全般 |
| **ビットレート** | ffmpeg対応全般 |

### 問い合わせ・報告先ガイド

どのような場合にどこに問い合わせればよいかを以下に示します：

#### 🎯 **機能追加の具体的な相談**

```
以下の担当者に GitHub mention (@ユーザー名) で相談
```

| 相談内容 | 担当者 | 連絡先 |
|---------|--------|----------------|
| **編集画面・タイムライン機能** | - | @aitch.ac.jp |
| **ライブラリ・プレイリスト機能** | - | @aitch.ac.jp |
| **ffmpeg 統合・音声処理** | 中本夏生 | k24110@aitch.ac.jp |
| **全般的なご質問** |  | @aitch.ac.jp |

---

### 問い合わせ時の記載項目チェックリスト

#### ✅ バグ報告時

```markdown
## 環境情報
- OS: macOS 12.0 / Linux / Windows 11
- Python: 3.10
- ffmpeg: 4.4

## 問題の詳細
（何が起きたか、正確に記述）

## 再現手順
1. ...
2. ...
3. ...

## 期待される動作
（どうなるべきだったか）

## 実際の動作
（何が起きたか）

## エラーメッセージ
（表示されたメッセージをコピー）
```

#### 💡 機能要望時

```markdown
## 要望概要
（何がしたいか、簡潔に）

## 背景・ユースケース
（なぜその機能が必要か）

## 実装案（あれば）
（技術的な実装方法の提案）

## 優先度
- [ ] 高（なくても困らないが、あると嬉しい）
- [ ] 中（できれば欲しい）
- [ ] 低（いつかあるといい）
```

---

## アーキテクチャ概要

```
入力処理
├─ [audio_info.py]         音声ファイルの情報取得
│  └─ get_duration_seconds() → 音声の長さを秒単位で取得

変換・連結
├─ [segment_cutter.py]     音声セグメントの切り出し
│  ├─ Segment型: (Path, start_sec, duration_sec) タプル
│  └─ cut_segments_to_temp_files() → 複数セグメントを個別MP3化
│
└─ [library_saver.py]      セグメント結合・保存の統合処理
   ├─ concat_segments_to_tempfile() → 一時MP3ファイル生成
   ├─ concat_segments_to_bytes() → MP3をbytesで取得（保存なし）
   └─ concat_segments_to_file() → 指定パスへ直接保存

出力処理
├─ [bytes_saver.py]        bytesデータの保存
│  └─ save_mp3_bytes_with_timestamp() → タイムスタンプ付きファイル名で保存
│
├─ [preview_player.py]     プレビュー再生
│  └─ preview_segments() → ffplayで順次再生
│
└─ [timeline_helper.py]    UI制御（タイムラインドラッグ編集）
   └─ TimelineController → 描画・同期・ドラッグ操作を一括管理
```

## クイックスタート

```bash
python MyApp.py
```

## ユースケース別 コード例

### 📝 ケース1: 音声ファイルの情報取得

```python
from pathlib import Path
from edit.audio_info import get_duration_seconds

# ファイルの長さを秒で取得
path = Path("input.mp3")
duration = get_duration_seconds(path)

if duration is not None:
    print(f"長さ: {duration:.1f}秒")
else:
    print("ファイル情報の取得に失敗しました")
```

### 🎬 ケース2: 複数セグメントの切り出しと連結をファイルに保存

```python
from pathlib import Path
from edit.library_saver import concat_segments_to_file

# セグメント定義: (ファイルパス, 開始秒, 長さ秒)
segments = [
    (Path("song1.mp3"), 10.0, 5.0),   # song1の10秒から5秒間
    (Path("song2.mp3"), 20.0, 8.0),   # song2の20秒から8秒間
]

output = Path("merged.mp3")
result = concat_segments_to_file(segments, output)

if result is not None:
    print(f"✓ 保存完了: {result}")
else:
    print("✗ ファイル保存に失敗しました")
```

### 💾 ケース3: 連結結果をメモリ保持してから保存（カスタム処理が必要な場合）

```python
from pathlib import Path
from edit.library_saver import concat_segments_to_bytes
from edit.bytes_saver import save_mp3_bytes_with_timestamp

segments = [
    (Path("song1.mp3"), 0.0, 10.0),
    (Path("song2.mp3"), 5.0, 15.0),
]

# MP3をbytesで取得
audio_data = concat_segments_to_bytes(segments)

if audio_data is not None:
    # タイムスタンプ付きファイル名で保存
    # 例: library/edited_20260116_143022.mp3
    path = save_mp3_bytes_with_timestamp(
        audio_data, 
        Path("library"), 
        prefix="edited"
    )
    print(f"✓ 保存: {path}")
else:
    print("✗ 連結処理に失敗しました")
```

### ⏯️ ケース4: プレビュー再生

```python
from pathlib import Path
from edit.preview_player import preview_segments

segments = [
    (Path("song1.mp3"), 10.0, 5.0),
    (Path("song2.mp3"), 20.0, 8.0),
]

# セグメントを順に再生（ffplay使用）
preview_segments(segments)
```

### ⚙️ ケース5: 一時ファイル経由の処理（外部ライブラリとの連携）

```python
from pathlib import Path
from edit.library_saver import concat_segments_to_tempfile

segments = [(Path("input.mp3"), 0.0, 20.0)]

# 一時MP3を生成してパスを取得
tmp_path = concat_segments_to_tempfile(segments)

if tmp_path is not None:
    # 外部ライブラリで処理（例：pygame、librosa など）
    # ※使用後は必ず削除推奨
    try:
        # ここで tmp_path を利用
        print(f"一時ファイル: {tmp_path}")
    finally:
        # 後処理：一時ファイル削除
        try:
            tmp_path.unlink()
        except Exception as e:
            print(f"警告: 一時ファイル削除失敗 - {e}")
else:
    print("✗ 一時ファイル生成に失敗")
```

## エラーハンドリング詳細

### ffmpeg/ffprobe 未インストール時

```python
from pathlib import Path
from edit.audio_info import get_duration_seconds

try:
    path = Path("input.mp3")
    duration = get_duration_seconds(path)
    
    if duration is None:
        print("エラー: ffprobe が見つかりません。")
        print("macOS: brew install ffmpeg")
        print("Linux: apt install ffmpeg")
        return
    
    print(f"✓ 長さ: {duration}秒")
    
except Exception as e:
    print(f"予期せぬエラー: {e}")
```

### ファイルが見つからない場合

```python
from pathlib import Path
from edit.library_saver import concat_segments_to_file

segments = [
    (Path("nonexistent.mp3"), 0.0, 10.0),
]

result = concat_segments_to_file(segments, Path("output.mp3"))

if result is None:
    print("✗ ファイルが見つかりません")
    print("  → ファイルパスを確認してください")
```

### ffmpeg 連結エラー時

```python
from pathlib import Path
from edit.library_saver import concat_segments_to_file

segments = [
    (Path("broken.mp3"), 0.0, 10.0),  # 破損ファイルなど
]

try:
    result = concat_segments_to_file(segments, Path("output.mp3"))
    
    if result is None:
        # ffmpeg がメッセージボックスで詳細を表示
        print("✗ 連結処理が失敗しました")
        print("  → 入力ファイルの形式を確認してください")
        
except Exception as e:
    print(f"予期せぬエラー: {e}")
```

### ディスク容量不足時

```python
from pathlib import Path
from edit.library_saver import concat_segments_to_file

segments = [...]

try:
    result = concat_segments_to_file(segments, Path("/output.mp3"))
    
    if result is None:
        print("✗ 保存に失敗しました")
        print("  → ディスク容量を確認してください")
        
except OSError as e:
    print(f"✗ ディスクエラー: {e}")
except Exception as e:
    print(f"予期せぬエラー: {e}")
```

### ベストプラクティス

```python
from pathlib import Path
from edit.library_saver import concat_segments_to_tempfile

def safe_process_segments(segments, output_dir):
    """セグメント処理のベストプラクティス例"""
    
    # 1. 出力ディレクトリの存在確認
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. 一時ファイル生成
    tmp_path = concat_segments_to_tempfile(segments)
    
    if tmp_path is None:
        print("✗ セグメント生成に失敗")
        return None
    
    try:
        # 3. ここで外部処理など
        print(f"✓ 一時ファイル生成: {tmp_path}")
        return tmp_path
        
    except Exception as e:
        print(f"✗ 処理エラー: {e}")
        return None
        
    finally:
        # 4. 必ず一時ファイルをクリーンアップ
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
                print(f"✓ クリーンアップ完了")
            except Exception as e:
                print(f"⚠️  クリーンアップ失敗: {e}")

# 使用例
result = safe_process_segments(segments, Path("output"))
```
