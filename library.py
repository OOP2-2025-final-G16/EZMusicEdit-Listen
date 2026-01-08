import glob
import os
import pygame

# pygameのミキサーを初期化
pygame.mixer.init()

class library:
    def get_mp3_files(self, folder_path):
        """フォルダ内のMP3ファイル一覧を取得"""
        if not folder_path:
            return []
        return glob.glob(os.path.join(folder_path, "*.mp3"))

    def play_music(self, file_path):
        """音楽を再生"""
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

    def stop_music(self):
        """音楽を停止"""
        pygame.mixer.music.stop()