import tkinter as tk
from tkinter import ttk, messagebox

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python GUI Sidebar Layout")
        self.root.geometry("800x600")

        # --- 全体のレイアウト設定 ---
        # 左側のサイドバー (幅を固定気味にするため width 指定)
        self.sidebar = tk.Frame(self.root, width=240, bg="#2c3e50")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False) # 中身に合わせて小さくならないように固定

        # 右側のメインコンテンツ表示エリア
        self.content_area = tk.Frame(self.root, bg="black")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._setup_sidebar()
        
        # 初期ページを表示
        self.show_page_home()

    def _setup_sidebar(self):
        """サイドバーのボタン類を配置"""
        label = tk.Label(self.sidebar, text="MENU", fg="white", bg="#2c3e50", font=("Arial", 16, "bold"))
        label.pack(pady=20)

        # ナビゲーションボタン
        btn_home = tk.Button(self.sidebar, text="ホーム", command=self.show_page_home, bg="#34495e", fg="white", relief="flat", pady=10)
        btn_home.pack(fill=tk.X, padx=10, pady=5)

        btn_user = tk.Button(self.sidebar, text="ユーザー登録", command=self.show_page_user, bg="#34495e", fg="white", relief="flat", pady=10)
        btn_user.pack(fill=tk.X, padx=10, pady=5)

        btn_settings = tk.Button(self.sidebar, text="設定", command=self.show_page_settings, bg="#34495e", fg="white", relief="flat", pady=10)
        btn_settings.pack(fill=tk.X, padx=10, pady=5)

    def clear_content(self):
        """右側のコンテンツエリアを空にする"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # --- 各ページの描画処理 ---

    def show_page_home(self):
        self.clear_content()
        label = tk.Label(self.content_area, text="ホーム画面", font=("Arial", 20), bg="white")
        label.pack(pady=50)
        
        desc = tk.Label(self.content_area, text="左のメニューから機能を選択してください。", bg="white")
        desc.pack()

    def show_page_user(self):
        self.clear_content()
        container = tk.Frame(self.content_area, bg="white", padx=20, pady=20)
        container.pack(fill=tk.BOTH)

        tk.Label(container, text="ユーザー登録", font=("Arial", 18), bg="white").pack(pady=10)
        
        tk.Label(container, text="名前を入力:", bg="white").pack(anchor="w")
        self.entry = ttk.Entry(container, width=30)
        self.entry.pack(pady=5, anchor="w")

        btn = ttk.Button(container, text="実行", command=self.on_click)
        btn.pack(pady=20, anchor="w")

    def show_page_settings(self):
        self.clear_content()
        label = tk.Label(self.content_area, text="設定画面", font=("Arial", 18), bg="white")
        label.pack(pady=30)
        tk.Checkbutton(self.content_area, text="ダークモード（仮）", bg="white").pack()

    def on_click(self):
        name = self.entry.get()
        if name:
            messagebox.showinfo("成功", f"こんにちは、{name}さん！")
        else:
            messagebox.showwarning("入力エラー", "名前を入力してください。")

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()