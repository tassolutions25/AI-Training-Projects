import tkinter as tk
from tkinter import messagebox

ACCOUNTS_FILE = "accounts.txt"
TRANS_FILE = "transactions.txt"

accounts = []
transactions = []
current_user = None


def load_data():
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            for line in f:
                card, pin, bal = line.strip().split(",")
                accounts.append({"card": card, "pin": pin, "balance": float(bal)})
        with open(TRANS_FILE, "r") as f:
            for line in f:
                card, t_type, amt = line.strip().split(",")
                transactions.append({"card": card, "type": t_type, "amount": amt})
    except FileNotFoundError:
        # Create a default account if file doesn't exist
        accounts.append({"card": "1234", "pin": "1111", "balance": 1000.0})


def save_data():
    with open(ACCOUNTS_FILE, "w") as f:
        for acc in accounts:
            f.write(f"{acc['card']},{acc['pin']},{acc['balance']}\n")
    with open(TRANS_FILE, "w") as f:
        for t in transactions:
            f.write(f"{t['card']},{t['type']},{t['amount']}\n")


def validate_login(card, pin):
    global current_user
    for acc in accounts:
        if acc["card"] == card and acc["pin"] == pin:
            current_user = acc
            return True
    return False


def process_transaction(t_type, amount):
    if t_type == "Withdraw":
        if amount % 10 != 0:
            return "Error: Please enter multiples of 10."
        if amount > current_user["balance"]:
            return "Error: Insufficient balance."
        current_user["balance"] -= amount
    else:
        current_user["balance"] += amount

    transactions.append(
        {"card": current_user["card"], "type": t_type, "amount": amount}
    )
    save_data()
    return "Success"


class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Simulator")
        self.root.geometry("400x400")
        self.show_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="ATM LOGIN", font=("Arial", 18)).pack(pady=20)

        tk.Label(self.root, text="Card Number:").pack()
        self.card_ent = tk.Entry(self.root)
        self.card_ent.pack()

        tk.Label(self.root, text="PIN:").pack()
        self.pin_ent = tk.Entry(self.root, show="*")
        self.pin_ent.pack()

        tk.Button(
            self.root, text="Login", command=self.attempt_login, bg="green", fg="white"
        ).pack(pady=20)

    def attempt_login(self):
        if validate_login(self.card_ent.get(), self.pin_ent.get()):
            self.show_main_menu()
        else:
            messagebox.showerror("Error", "Invalid Card or PIN")

    def show_main_menu(self):
        self.clear_screen()
        tk.Label(
            self.root, text=f"Welcome, {current_user['card']}", font=("Arial", 12)
        ).pack(pady=10)

        tk.Button(
            self.root, text="Check Balance", width=20, command=self.check_bal
        ).pack(pady=5)
        tk.Button(
            self.root,
            text="Withdraw Cash",
            width=20,
            command=lambda: self.show_input("Withdraw"),
        ).pack(pady=5)
        tk.Button(
            self.root,
            text="Deposit Cash",
            width=20,
            command=lambda: self.show_input("Deposit"),
        ).pack(pady=5)
        tk.Button(
            self.root, text="Mini-Statement", width=20, command=self.show_statement
        ).pack(pady=5)
        tk.Button(
            self.root, text="Logout", width=20, command=self.show_login_screen, bg="red"
        ).pack(pady=10)

    def check_bal(self):
        messagebox.showinfo(
            "Balance", f"Current Balance: {current_user['balance']} ETB"
        )

    def show_input(self, t_type):
        self.clear_screen()
        tk.Label(self.root, text=f"{t_type} Amount:", font=("Arial", 14)).pack(pady=20)
        amt_ent = tk.Entry(self.root)
        amt_ent.pack()

        def confirm():
            try:
                amt = float(amt_ent.get())
                result = process_transaction(t_type, amt)
                if "Error" in result:
                    messagebox.showerror("Failed", result)
                else:
                    messagebox.showinfo("Success", f"{t_type} successful!")
                    self.show_main_menu()
            except ValueError:
                messagebox.showerror("Error", "Enter a valid number")

        tk.Button(self.root, text="Confirm", command=confirm).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_main_menu).pack()

    def show_statement(self):
        self.clear_screen()
        tk.Label(self.root, text="Recent Transactions").pack()
        lb = tk.Listbox(self.root, width=40)
        lb.pack(pady=10)

        # Filter transactions for current card and loop through them
        for t in transactions:
            if t["card"] == current_user["card"]:
                lb.insert(tk.END, f"{t['type']}: {t['amount']} ETB")

        tk.Button(self.root, text="Back", command=self.show_main_menu).pack()


load_data()
root = tk.Tk()
app = ATMApp(root)
root.mainloop()
