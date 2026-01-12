import tkinter as tk
from library_page import LibraryPage
from playlist_page import PlaylistPage
from edit_page import EditPage
import constants as c

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Editor App")
        self.root.geometry("900x750")
        self.app_config = {"username": "Guest"}
        self.menu_items = {}
        self.current_page = "" # 現在のページを保持

        # レイアウト
        self.sidebar = tk.Frame(self.root, width=240, bg=c.COLOR_SIDEBAR)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.content_area = tk.Frame(self.root, bg=c.COLOR_CONTENT)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._setup_sidebar()
        self.show_page("library")

    def _setup_sidebar(self):
        tk.Label(self.sidebar, text="MENU", fg=c.COLOR_MENU_TEXT, 
                 bg=c.COLOR_SIDEBAR, font=("Arial", 40, "bold")).pack(pady=30)
        
        label_style = {
            "bg": c.COLOR_SIDEBAR, 
            "fg": c.COLOR_SIDEBAR_TEXT,
            "pady": 30,          
            "font": ("Arial", 18),
            "anchor": "center",
            "cursor": "hand2"
        }

        self._add_separator()
        self.menu_items["library"] = self._create_menu_item("ライブラリ", "library", label_style)
        self._add_separator()
        self.menu_items["playlist"] = self._create_menu_item("プレイリスト", "playlist", label_style)
        self._add_separator()
        self.menu_items["edit"] = self._create_menu_item("編集して追加", "edit", label_style)
        self._add_separator()

    def _create_menu_item(self, text, page_name, style):
        item = tk.Label(self.sidebar, text=text, **style)
        item.pack(fill=tk.X, pady=2)
        
        item.bind("<Button-1>", lambda e: self.show_page(page_name))
        item.bind("<Enter>", lambda e: self._on_hover(item, page_name))
        item.bind("<Leave>", lambda e: self._on_leave(item, page_name))
        
        return item

    def _on_hover(self, item, page_name):
        # 選択中のページでない場合のみ、ホバー色を適用
        if self.current_page != page_name:
            item.config(bg=c.COLOR_MENU_HOVER)

    def _on_leave(self, item, page_name):
        # 選択中のページでない場合は、元のサイドバーの色に戻す
        if self.current_page != page_name:
            item.config(bg=c.COLOR_SIDEBAR)

    def _add_separator(self):
        separator = tk.Frame(self.sidebar, height=1, bg=c.COLOR_SEP, bd=0, highlightthickness=0)
        separator.pack(fill=tk.X, padx=10, pady=2)

    def show_page(self, page_name):
        self.current_page = page_name
        
        # メニューの強調表示（選択中のページの色）を更新
        for name, label in self.menu_items.items():
            if name == page_name:
                label.config(bg=c.COLOR_BTN_BG) # 選択中の色
            else:
                label.config(bg=c.COLOR_SIDEBAR) # 通常の色

        # コンテンツの切り替え
        for widget in self.content_area.winfo_children():
            widget.destroy()

        theme = c.APP_THEME
        if page_name == "library":
            page = LibraryPage(self.content_area, theme, self.app_config)
        elif page_name == "playlist":
            page = PlaylistPage(self.content_area, theme, self.app_config)
        elif page_name == "edit":
            page = EditPage(self.content_area, theme, self.app_config)
        
        page.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()