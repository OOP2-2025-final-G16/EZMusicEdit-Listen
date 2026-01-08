import sys
import subprocess
from pathlib import Path

# 例: 他のスクリプトからの利用方法

#from pathlib import Path
#from changemp3 import convert_mp4_to_mp3, ConvertError

#try:
#    out_path = convert_mp4_to_mp3(Path("/path/to/file.mp4"))
#    print("出力先:", out_path)
#except FileNotFoundError:
#    print("ファイルが見つかりません")
#except ConvertError as e:
#    print("変換エラー:", e)

class ConvertError(Exception):
	"""mp4→mp3 変換時のエラー用例外"""

def convert_mp4_to_mp3(input_file: Path) -> Path:
	"""
	mp4 ファイルを mp3 に変換するライブラリ関数。
	- mp3 の場合: 変換せず、そのまま Path を返す
	- mp4 の場合: mp3 を生成し、その mp3 の Path を返す
	- それ以外: ConvertError を送出
	"""

	if not input_file.exists():
		raise FileNotFoundError(f"ファイルが見つかりません: {input_file}")

	if not input_file.is_file():
		raise ConvertError(f"通常のファイルではありません: {input_file}")

	ext = input_file.suffix.lower()

	if ext == ".mp3":
		# 変換不要
		return input_file

	if ext != ".mp4":
		raise ConvertError("対応していないファイル形式です。（mp3 または mp4 のみ対応）")

	# 変換後の mp3 は、このスクリプトと同じフォルダ配下の
	# "editfiles" ディレクトリに保存する
	base_dir = Path(__file__).resolve().parent
	output_dir = base_dir / "editfiles"
	output_dir.mkdir(exist_ok=True)

	output_file = output_dir / f"{input_file.stem}.mp3"

	cmd = [
		"ffmpeg",
		"-y",  # 上書き確認なし
		"-i",
		str(input_file),
		"-vn",  # 映像を無効化
		"-acodec",
		"libmp3lame",
		"-ab",
		"192k",
		str(output_file),
	]

	try:
		subprocess.run(cmd, check=True)
	except FileNotFoundError as exc:
		raise ConvertError("ffmpeg コマンドが見つかりません。ffmpeg をインストールしてください。") from exc
	except subprocess.CalledProcessError as exc:
		raise ConvertError("変換中に問題が発生しました。") from exc

	return output_file


def main() -> None:

	if len(sys.argv) < 2:
		print("使い方: python changemp3.py 入力ファイルパス", file=sys.stderr)
		sys.exit(1)

	input_path = Path(sys.argv[1])

	try:
		out_path = convert_mp4_to_mp3(input_path)
	except FileNotFoundError as e:
		print(f"エラー: {e}", file=sys.stderr)
		sys.exit(1)
	except ConvertError as e:
		print(f"エラー: {e}", file=sys.stderr)
		sys.exit(1)

	# mp3 の場合はスキップメッセージ、それ以外(mp4変換成功)は完了メッセージ
	if out_path == input_path and out_path.suffix.lower() == ".mp3":
		print("mp3ファイルのため変換をスキップします。")
	else:
		print(f"変換完了: {out_path}")


if __name__ == "__main__":
	main()

