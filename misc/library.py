import glob
import os
import pygame

# pygameのミキサーを初期化
pygame.mixer.init()

class library:
    def get_mp3_files(self, folder_name="library_file"): # デフォルトを library_file に変更
        """実行ファイルと同じ階層にある指定フォルダからMP3を取得"""
        # library.py がある場所 (misc/) を取得
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 1つ上の階層（プロジェクトのルート）の絶対パスを取得
        base_path = os.path.dirname(current_dir)

        # ルートディレクトリ配下に library_file パスを作成
        target_dir = os.path.join(base_path, folder_name)

        # フォルダが存在しない場合は自動で作成
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            return []
            
        # 作成した target_dir 内のMP3ファイルを検索
        return glob.glob(os.path.join(target_dir, "*.mp3"))

    def play_music(self, file_path):
        """音楽を再生"""
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        sound = pygame.mixer.Sound(file_path)
        return sound.get_length()

    def stop_music(self):
        """音楽を停止"""
        pygame.mixer.music.stop()

    def is_playing(self):
        """現在再生中（ビジー状態）かを確認"""
        return pygame.mixer.music.get_busy()
    
    def set_pos(self, file_path, sec):
        """指定した秒数から再生を開始する"""
        pygame.mixer.music.load(file_path)
        # start引数に秒数を指定して再生
        pygame.mixer.music.play(start=sec)

    def get_pos(self):
        """現在の再生位置を秒で返す"""
        return pygame.mixer.music.get_pos() / 1000.0