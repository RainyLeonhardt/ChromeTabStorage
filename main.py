import pygetwindow as gw
import pyautogui
import time
import webbrowser
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, Frame, Scrollbar, Listbox, filedialog
import clipboard
import subprocess
import os
import platform

def find_chrome_path():
    system_platform = platform.system()
    
    if system_platform == "Windows":
        paths = [
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        ]
        for path in paths:
            if os.path.exists(path):
                return path

    elif system_platform == "Darwin":  # macOS
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(path):
            return path

    elif system_platform == "Linux":
        # On Linux, we can usually just use the command "google-chrome"
        return "google-chrome"

    return None

chrome_path = find_chrome_path()
if chrome_path:
    print(f"Found Chrome at: {chrome_path}")
else:
    print("Chrome not found.")

def list_chrome_windows():
    windows = [window for window in gw.getWindowsWithTitle('') if 'Google Chrome' in window.title]
    return windows

def get_all_tabs_from_window(window):
    window.restore()  # This will bring the window out of minimized state
    window.maximize()  # This will maximize the window
    window.activate()
    tabs = []
    pyautogui.hotkey('ctrl', '1')  # Start with the first tab
    time.sleep(1)
    tab_names = set()
    
    while True:
        pyautogui.hotkey('ctrl', 'l')  # Highlight the address bar
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'c')  # Copy the URL
        time.sleep(1)
        copied_url = clipboard.paste()
        tab_title = window.title.split(' - ')[0]
        if tab_title in tab_names:
            break
        tab_names.add(tab_title)
        tabs.append((tab_title, copied_url))
        pyautogui.hotkey('ctrl', 'tab')  # Move to next tab
        time.sleep(1)
    return tabs

def store_tabs(tabs, filename="tabs.txt"):
    with open(filename, 'w', encoding='utf-8') as f:  # specify the encoding as utf-8
        for tab_name, tab_url in tabs:
            f.write(f"{tab_name}||{tab_url}\n")


def reopen_tabs(filename="tabs.txt"):
    chrome_path = find_chrome_path()
    if not chrome_path:
        print("Chrome not found.")
        return

    urls = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            _, tab_url = line.strip().split('||')
            urls.append(tab_url)

    subprocess.Popen([chrome_path, '--new-window'] + urls)


def gui_main():
    root = tk.Tk()
    root.title("Chrome Tabs Manager")
    root.geometry('500x500')

    def update_listbox_with_tabs(tabs):
        tabs_listbox.delete(0, tk.END)
        for tab_name, _ in tabs:
            tabs_listbox.insert(tk.END, tab_name)

    def on_save_tabs():
        chrome_windows = list_chrome_windows()
        if not chrome_windows:
            messagebox.showerror("Error", "No Chrome windows found!")
            return
        
        window_titles = [window.title for window in chrome_windows]
        choice = simpledialog.askstring("Select Chrome Window", "Enter window number:\n" + "\n".join([f"{idx}. {title}" for idx, title in enumerate(window_titles, 1)]))
        
        if not choice or not choice.isdigit() or int(choice) < 1 or int(choice) > len(chrome_windows):
            messagebox.showerror("Error", "Invalid selection!")
            return
        
        # Ask user for a filename and directory
        default_filename = os.path.join(os.getcwd(), f"ChromeTabs-{int(time.time())}.txt")
        filename = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save Tabs As", initialfile=default_filename, defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        
        if not filename:
            return

        tabs = get_all_tabs_from_window(chrome_windows[int(choice) - 1])
        store_tabs(tabs, filename=filename)
        update_listbox_with_tabs(tabs)
        messagebox.showinfo("Success", f"Tabs saved to {filename}")


    def on_open_tabs():
        folder_selected = filedialog.askdirectory(initialdir=os.getcwd(), title="Select folder with saved tabs")
        saved_files = [f for f in os.listdir(folder_selected) if f.endswith(".txt")]

        if not saved_files:
            messagebox.showerror("Error", "No saved tabs found!")
            return

        choice = simpledialog.askstring("Select Saved Tabs File", "Enter file number:\n" + "\n".join([f"{idx}. {fname}" for idx, fname in enumerate(saved_files, 1)]))

        if not choice or not choice.isdigit() or int(choice) < 1 or int(choice) > len(saved_files):
            messagebox.showerror("Error", "Invalid selection!")
            return

        reopen_tabs(os.path.join(folder_selected, saved_files[int(choice) - 1]))
        messagebox.showinfo("Success", "Tabs opened successfully!")

    save_btn = tk.Button(root, text="Save Tabs", command=on_save_tabs, font=("Arial", 14), padx=40, pady=20)
    save_btn.pack(pady=20)

    open_btn = tk.Button(root, text="Open Tabs", command=on_open_tabs, font=("Arial", 14), padx=40, pady=20)
    open_btn.pack(pady=20)

    scrollbar = Scrollbar(root)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tabs_listbox = Listbox(root, yscrollcommand=scrollbar.set, font=("Arial", 12), height=10, width=50)
    tabs_listbox.pack(pady=20)
    scrollbar.config(command=tabs_listbox.yview)

    root.mainloop()

if __name__ == "__main__":
    gui_main()
