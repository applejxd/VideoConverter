import os
import tkinter as tk
from tkinter import filedialog, messagebox


def browse_folder():
    folder_path = filedialog.askdirectory()  # フォルダを選択するダイアログを表示
    if folder_path:
        file_listbox.delete(0, tk.END)  # 一覧をクリア

        # 選択されたフォルダ内のファイル一覧を取得し、リストボックスに追加
        files = os.listdir(folder_path)
        for file in files:
            file_listbox.insert(tk.END, file)


def show_selected_file():
    selected_index = file_listbox.curselection()
    if selected_index:
        selected_file = file_listbox.get(selected_index[0])
        file_path = os.path.join(folder_path, selected_file)
        messagebox.showinfo("選択されたファイル", f"選択されたファイルのパス: {file_path}")
    else:
        messagebox.showwarning("警告", "ファイルが選択されていません。")


# Tkinterウィンドウの作成
root = tk.Tk()
root.title("フォルダとファイル選択")

# フォルダ選択ボタン
browse_button = tk.Button(root, text="フォルダを選択", command=browse_folder)
browse_button.pack(pady=10)

# ファイル一覧を表示するリストボックス
file_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=10)
file_listbox.pack(pady=10)

# ファイル選択ボタン
select_button = tk.Button(root, text="ファイルを選択", command=show_selected_file)
select_button.pack(pady=10)

# 選択されたフォルダのパスを格納する変数
folder_path = ""

# Tkinterウィンドウのメインループ
root.mainloop()
