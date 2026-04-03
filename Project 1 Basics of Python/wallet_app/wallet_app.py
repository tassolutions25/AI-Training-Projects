import tkinter as tk
from tkinter import messagebox
import re

USER_FILE = "eth_users.txt"
TRANS_FILE = "eth_trans.txt"

users = []
transactions = []
current_user = None


def load_data():
    try:
        with open(USER_FILE, "r") as f:
            for line in f:
                name, phone, bal = line.strip().split(",")
                users.append({"name": name, "phone": phone, "balance": float(bal)})
        with open(TRANS_FILE, "r") as f:
            for line in f:
                s, r, a = line.strip().split(",")
                transactions.append({"sender": s, "receiver": r, "amt": float(a)})
    except FileNotFoundError:
        pass


def save_data():
    with open(USER_FILE, "w") as f:
        for u in users:
            f.write(f"{u['name']},{u['phone']},{u['balance']}\n")
    with open(TRANS_FILE, "w") as f:
        for t in transactions:
            f.write(f"{t['sender']},{t['receiver']},{t['amt']}\n")


def is_valid_eth_phone(phone):
    """Regex for Ethiopian Format: Starts with 09, 07, or +251 followed by 8 digits."""
    pattern = r"^(\+2519|\+2517|09|07)\d{8}$"
    return re.match(pattern, phone) is not None


def register_user(name, phone):
    if not is_valid_eth_phone(phone):
        return "Invalid format"
    for u in users:
        if u["phone"] == phone:
            return "Exists"
    users.append({"name": name, "phone": phone, "balance": 1000.0})
    save_data()
    return "Success"


def login_user(phone):
    global current_user
    if not is_valid_eth_phone(phone):
        return False
    for u in users:
        if u["phone"] == phone:
            current_user = u
            return True
    return False


def send_money(receiver_phone, amount):
    if not is_valid_eth_phone(receiver_phone):
        return "Invalid receiver phone format"
    if amount <= 0:
        return "Invalid amount"
    if current_user["balance"] < amount:
        return "Insufficient funds"

    receiver = None
    for u in users:
        if u["phone"] == receiver_phone:
            receiver = u
            break

    if receiver:
        current_user["balance"] -= amount
        receiver["balance"] += amount
        transactions.append(
            {"sender": current_user["phone"], "receiver": receiver_phone, "amt": amount}
        )
        save_data()
        return "Success"
    return "Receiver not found"


class WalletApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ethiopian Mobile Wallet")
        self.root.geometry("450x650")
        self.show_auth_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_auth_screen(self):
        self.clear_screen()
        tk.Label(
            self.root, text="Ethiopian Wallet", font=("Arial", 18, "bold"), fg="#0039a6"
        ).pack(pady=10)

        tk.Label(self.root, text="Phone Number (e.g., 0912... or 0712...):").pack()
        self.phone_ent = tk.Entry(self.root, font=("Arial", 12))
        self.phone_ent.pack(pady=5)

        tk.Button(
            self.root,
            text="Login",
            command=self.do_login,
            width=15,
            bg="#0039a6",
            fg="white",
        ).pack(pady=5)

        tk.Label(self.root, text="--- REGISTER NEW USER ---").pack(pady=10)
        tk.Label(self.root, text="Full Name:").pack()
        self.name_ent = tk.Entry(self.root, font=("Arial", 12))
        self.name_ent.pack(pady=5)
        tk.Button(
            self.root, text="Register", command=self.do_register, width=15, bg="#febd17"
        ).pack(pady=5)

    def do_login(self):
        if login_user(self.phone_ent.get()):
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Ethiopian format or User not found")

    def do_register(self):
        res = register_user(self.name_ent.get(), self.phone_ent.get())
        if res == "Success":
            messagebox.showinfo("Success", "Registered! Please Login.")
        elif res == "Invalid format":
            messagebox.showerror("Error", "Use valid format (09... or 07...)")
        else:
            messagebox.showerror("Error", "Phone already registered")

    def show_dashboard(self):
        self.clear_screen()
        tk.Label(
            self.root, text=f"Welcome, {current_user['name']}", font=("Arial", 14)
        ).pack(pady=10)
        self.bal_label = tk.Label(
            self.root,
            text=f"Balance: {current_user['balance']} ETB",
            font=("Arial", 14, "bold"),
            fg="green",
        )
        self.bal_label.pack(pady=10)

        # Transfer
        tk.Label(self.root, text="Send Money to Phone:").pack()
        self.rec_ent = tk.Entry(self.root, font=("Arial", 12))
        self.rec_ent.pack(pady=5)
        tk.Label(self.root, text="Amount (ETB):").pack()
        self.amt_ent = tk.Entry(self.root, font=("Arial", 12))
        self.amt_ent.pack(pady=5)
        tk.Button(
            self.root,
            text="Transfer Funds",
            command=self.do_transfer,
            bg="#ef3340",
            fg="white",
        ).pack(pady=10)

        # History
        tk.Label(self.root, text="Transactions:").pack()
        self.hist_list = tk.Listbox(self.root, width=50, height=10)
        self.hist_list.pack(pady=5)
        self.update_history()

        tk.Button(self.root, text="Logout", command=self.show_auth_screen).pack(pady=10)

    def do_transfer(self):
        try:
            amt = float(self.amt_ent.get())
            res = send_money(self.rec_ent.get(), amt)
            if res == "Success":
                messagebox.showinfo("Done", "Money Sent Successfully!")
                self.bal_label.config(text=f"Balance: {current_user['balance']} ETB")
                self.update_history()
            else:
                messagebox.showerror("Failed", res)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")

    def update_history(self):
        self.hist_list.delete(0, tk.END)
        for t in transactions:
            if t["sender"] == current_user["phone"]:
                self.hist_list.insert(
                    tk.END, f"SENT: {t['amt']} ETB to {t['receiver']}"
                )
            elif t["receiver"] == current_user["phone"]:
                self.hist_list.insert(
                    tk.END, f"RECV: {t['amt']} ETB from {t['sender']}"
                )


load_data()
root = tk.Tk()
app = WalletApp(root)
root.mainloop()
