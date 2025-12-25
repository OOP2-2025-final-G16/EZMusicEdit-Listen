import tkinter as tk
from library_page import LibraryPage
from playlist_page import PlaylistPage
from edit_page import EditPage

class MyApp:
    COLOR_SIDEBAR = "#2c3e50"
    COLOR_CONTENT = "black"
    COLOR_TEXT_MAIN = "white"
    COLOR_MENU_TEXT = "#3498db"

    def __init__(self, root):
        self.root = root
        self.root.title("Music Editor App")
        self.root.geometry("900x650")
        self.app_config = {"username": "Guest"}

        # レイアウト
        self.sidebar = tk.Frame(self.root, width=240, bg=self.COLOR_SIDEBAR)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.content_area = tk.Frame(self.root, bg=self.COLOR_CONTENT)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._setup_sidebar()
        self.show_page("library") # 初期はライブラリを表示

    def _setup_sidebar(self):
        tk.Label(self.sidebar, text="MENU", fg=self.COLOR_MENU_TEXT, bg=self.COLOR_SIDEBAR, font=("Arial", 16, "bold")).pack(pady=20)
        
        btn_style = {"bg": "#34495e", "fg": "white", "relief": "flat", "pady": 10, "font": ("Arial", 11)}
        
        # メニューボタンの配置
        tk.Button(self.sidebar, text="📚 ライブラリ", command=lambda: self.show_page("library"), **btn_style).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(self.sidebar, text="🎵 プレイリスト", command=lambda: self.show_page("playlist"), **btn_style).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(self.sidebar, text="✂️ 編集して追加", command=lambda: self.show_page("edit"), **btn_style).pack(fill=tk.X, padx=10, pady=2)

    def show_page(self, page_name):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        theme = {"bg": self.COLOR_CONTENT, "fg": self.COLOR_TEXT_MAIN}

        # ページ名に応じたクラスをインスタンス化
        if page_name == "library":
            page = LibraryPage(self.content_area, theme, self.app_config)
        elif page_name == "playlist":
            page = PlaylistPage(self.content_area, theme, self.app_config)
        elif page_name == "edit":
            page = EditPage(self.content_area, theme, self.app_config)
        
        page.pack(fill=tk.BOTH, expand=True)

    def save_settings(self, data):
        self.app_config.update(data)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()