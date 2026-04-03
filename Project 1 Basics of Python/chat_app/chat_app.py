import tkinter as tk
from tkinter import messagebox

FILE_NAME = "chat_history.txt"
messages = []


def loadChatFromFile():
    try:
        with open(FILE_NAME, "r") as f:
            for line in f:
                if ":" in line:
                    user, msg = line.strip().split(":", 1)
                    messages.append({"user": user, "message": msg})
    except FileNotFoundError:
        pass


def save_data():
    with open(FILE_NAME, "w") as f:
        for msg in messages:
            f.write(f"{msg['user']}:{msg['message']}\n")


def addMessage():
    user = user_entry.get().strip()
    msg = msg_entry.get().strip()

    if user and msg:
        messages.append({"user": user, "message": msg})

        chat_listbox.insert(tk.END, f"{user}: {msg}")

        msg_entry.delete(0, tk.END)

        save_data()
    else:
        messagebox.showwarning("Input Error", "Please enter both name and message.")


def clearChat():
    messages.clear()
    chat_listbox.delete(0, tk.END)
    save_data()


root = tk.Tk()
root.title("Python Chat App")
root.geometry("400x500")

frame = tk.Frame(root)
frame.pack(pady=10)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

chat_listbox = tk.Listbox(frame, width=50, height=15, yscrollcommand=scrollbar.set)
chat_listbox.pack(side=tk.LEFT)
scrollbar.config(command=chat_listbox.yview)

# 2. Input Fields
tk.Label(root, text="Your Name:").pack()
user_entry = tk.Entry(root, width=40)
user_entry.pack(pady=2)

tk.Label(root, text="Your Message:").pack()
msg_entry = tk.Entry(root, width=40)
msg_entry.pack(pady=2)

# 3. Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

send_btn = tk.Button(btn_frame, text="Send Message", command=addMessage, bg="lightblue")
send_btn.pack(side=tk.LEFT, padx=5)

clear_btn = tk.Button(btn_frame, text="Clear All", command=clearChat, bg="salmon")
clear_btn.pack(side=tk.LEFT, padx=5)

loadChatFromFile()
for entry in messages:
    chat_listbox.insert(tk.END, f"{entry['user']}: {entry['message']}")

root.mainloop()
