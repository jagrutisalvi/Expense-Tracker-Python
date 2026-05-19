import tkinter as tk
import csv
from tkinter import ttk,messagebox
from tkcalendar import DateEntry
from datetime import date
from collections import defaultdict
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


# Main window
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("900x500")

# ===== LEFT FRAME (Form) =====
left_frame = tk.Frame(root, bg="lightblue", width=400,padx=10, pady=10)
left_frame.pack(side="left", fill="y")
left_frame.pack_propagate(False)

tk.Label(left_frame, text="Add Expense", font=("Arial", 14, "bold")).pack(pady=10)

# Date
date_row = tk.Frame(left_frame, bg="lightblue")
date_row.pack(fill="x", pady=5)
tk.Label(date_row, text="Date", width=10, anchor="w", bg="lightblue").pack(side="left")
date_entry = DateEntry(
    date_row,
    width=20,
    date_pattern='dd-mm-yyyy',
    maxdate=date.today()   # disables future dates
)
date_entry.pack(side="left", fill="x", expand=True)

# Category
category_row = tk.Frame(left_frame, bg="lightblue")
category_row.pack(fill='x',pady=5)
tk.Label(category_row, text="Category", width=10, anchor="w", bg="lightblue").pack(side="left")
category = ttk.Combobox(category_row, values=["Food", "Transport", "Shopping", "Bills"],state='readonly')
category.set('Select Category')
category.pack(side="left", fill="x", expand=True)

# Description
description_row = tk.Frame(left_frame, bg="lightblue")
description_row.pack(fill='x',pady=5)
tk.Label(description_row, text="Description", width=10, anchor="w", bg="lightblue").pack(side="left")
desc_entry = tk.Entry(description_row,width=20)
desc_entry.pack(side="left", fill="x", expand=True)

def validate_amount(new_value):
    if new_value == "":
        return True
    try:
        float(new_value)
        return True
    except ValueError:
        return False

# Amount
amount_row = tk.Frame(left_frame, bg="lightblue")
amount_row.pack(fill='x',pady=5)
tk.Label(amount_row, text="Amount", width=10, anchor="w", bg="lightblue").pack(side="left")

vcmd = (root.register(validate_amount), "%P")

amount_entry = tk.Entry(amount_row, validate="key", validatecommand=vcmd)
amount_entry.pack(side="left", fill="x", expand=True)

# ===== FUNCTIONS =====

def add_expense():
    if not amount_entry.get() or not desc_entry.get() or  (category.get()=='Select Category' or not category.get()):
        messagebox.showwarning("Warning", "Please fill all fields")
        return

    tree.insert("", "end", values=(
        date_entry.get(),
        category.get(),
        desc_entry.get(),
        amount_entry.get()
    ))
    update_total()
    clear_fields()

def clear_fields():
    desc_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    category.set("")

def delete_expense():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a row to delete")
        return
    tree.delete(selected)
    update_total()

def update_total():
    total = 0
    amount = []
    for item in tree.get_children():
        values = tree.item(item)["values"]
        total += float(values[3]) 
        amount.append(values)  # amount column
    total_label.config(text=f"💰 Total Expense: ₹{total}")

def save_expense():
    items = tree.get_children()

    if not items:
        messagebox.showwarning("Warning", "No data to save")
        return

    with open("expenses.csv", "w", newline="") as file:
        writer = csv.writer(file)

        # heading
        writer.writerow(["Date", "Category", "Description", "Amount"])

        # table rows
        for item in items:
            row = tree.item(item)["values"]
            writer.writerow(row)

    messagebox.showinfo("Saved", "Data saved successfully")

    # Clear fields
    date_entry.delete(0, "end")
    category.set("Select Category")
    amount_entry.delete(0, "end")

def load_expenses():
    try:
        with open("expenses.csv", "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)   # skip header row

            for row in reader:
                tree.insert("", "end", values=row)
            update_total()

    except FileNotFoundError:
        pass   # file not created yet

def show_chart():
    category_totals = defaultdict(float)

    # Read data from treeview
    for item in tree.get_children():
        row = tree.item(item)["values"]
        category = row[1]   # Category column
        amount = float(row[3])   # Amount column
        category_totals[category] += amount

    if not category_totals:
        print("No data available")
        return

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    chart_window = tk.Toplevel(root)
    chart_window.title("Expense Chart")

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
    ax.set_title("Expense by Category")

    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack()
# ===== BUTTONS =====
# Button Frame
button_frame = tk.Frame(left_frame, bg="lightblue")
button_frame.pack(pady=20)

# Buttons beside each other
add_btn = tk.Button(button_frame, text="Add Expense",command=add_expense)
add_btn.pack(side="left", padx=5)

save_btn = tk.Button(button_frame, text="Save Expense", command=save_expense)
save_btn.pack(side="left", padx=5)

clear_btn = tk.Button(button_frame, text="Clear",command=clear_fields)
clear_btn.pack(side="left", padx=5)

delete_btn = tk.Button(button_frame, text="Delete",command=delete_expense)
delete_btn.pack(side="left", padx=5)

chart_btn = tk.Button(button_frame, text="Show Chart", command=show_chart)
chart_btn.pack(side="left", padx=5)

total_label = tk.Label(left_frame, text="💰 Total Expense: ₹0", bg="lightblue", font=("Arial", 12, "bold"),fg="blue")
total_label.pack(pady=20)

# ===== RIGHT FRAME (TABLE) =====
right_frame = tk.Frame(root, padx=10, pady=10)
right_frame.pack(side="right", fill="both", expand=True)

columns = ("Date", "Category", "Description", "Amount")
tree = ttk.Treeview(right_frame, columns=columns, show="headings")
load_expenses()

for col in columns:
    tree.heading(col, text=col,anchor="center")
    tree.column(col, width=120,anchor="center")

tree.pack(fill="both", expand=True)


# Run app
root.mainloop()