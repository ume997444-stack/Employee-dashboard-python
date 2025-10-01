import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ===== DATABASE SETUP =====
conn = sqlite3.connect("employees.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id TEXT PRIMARY KEY,
    name TEXT,
    department TEXT,
    phone TEXT,
    attendance TEXT
)
""")
conn.commit()

import re
def is_valid_phone(phone):
    # Simple regex for phone number validation (11 digits)
    pattern = r'^\d{11}$'
    return re.match(pattern, phone)

# ===== FUNCTION DEFINITIONS =====

def load_employees():
    tree.delete(*tree.get_children())  # Clear existing rows
    for row in cursor.execute("SELECT * FROM employees"):
        tree.insert("", "end", values=row)

def clear_fields():
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_dept.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    attendance_var.set("")
    btn_add.config(state="normal")  # Re-enable add
    entry_id.config(state="normal")

def add_employee():
    emp_id = entry_id.get().strip()
    name = entry_name.get().strip()
    dept = entry_dept.get().strip()
    phone = entry_phone.get().strip()
    attendance = attendance_var.get()

    if not all([emp_id, name, dept, phone, attendance]):
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    if not is_valid_phone(phone):
        messagebox.showwarning("Input Error", "Phone number must be 11 digits.")
        return

    try:
        cursor.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
                       (emp_id, name, dept, phone, attendance))
        conn.commit()
        load_employees()
        clear_fields()
        messagebox.showinfo("Success", "Employee added successfully.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Employee ID '{emp_id}' already exists.")
def update_employee():
    emp_id = entry_id.get().strip()
    name = entry_name.get().strip()
    dept = entry_dept.get().strip()
    phone = entry_phone.get().strip()
    attendance = attendance_var.get()

    if not all([emp_id, name, dept, phone, attendance]):
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    if not is_valid_phone(phone):
        messagebox.showwarning("Input Error", "Phone number must be 11 digits.")
        return

    cursor.execute("""
        UPDATE employees
        SET name = ?, department = ?, phone = ?, attendance = ?
        WHERE id = ?
    """, (name, dept, phone, attendance, emp_id))
    conn.commit()
    load_employees()
    clear_fields()
    messagebox.showinfo("Success", "Employee updated successfully.")

def delete_employee():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select an employee to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this employee?")
    if not confirm:
        return

    emp_id = tree.item(selected[0])['values'][0]
    cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    conn.commit()
    load_employees()
    clear_fields()
    messagebox.showinfo("Deleted", f"Employee ID '{emp_id}' has been deleted.")

# ===== UI SETUP =====

root = tk.Tk()
root.title("Employee Dashboard")
root.geometry("950x600")
root.config(bg="#71adca")

# Fonts
LABEL_FONT = ("Arial", 10, "bold")
ENTRY_FONT = ("Arial", 10)
BUTTON_FONT = ("Arial", 10, "bold")

# ---- Form Section ----
form_frame = tk.Frame(root, bg="#f4f6f7")
form_frame.pack(pady=10)

def create_form_row(label_text, row, widget):
    tk.Label(form_frame, text=label_text, font=LABEL_FONT, bg="#f4f6f7").grid(row=row, column=0, padx=10, pady=5, sticky="e")
    widget.grid(row=row, column=1, padx=10, pady=5)

entry_id = tk.Entry(form_frame, font=ENTRY_FONT)
entry_name = tk.Entry(form_frame, font=ENTRY_FONT)
entry_dept = tk.Entry(form_frame, font=ENTRY_FONT)
entry_phone = tk.Entry(form_frame, font=ENTRY_FONT)
attendance_var = tk.StringVar()
attendance_dropdown = ttk.Combobox(form_frame, textvariable=attendance_var, values=["Present", "Absent"], font=ENTRY_FONT)

create_form_row("Employee ID:", 0, entry_id)
create_form_row("Name:", 1, entry_name)
create_form_row("Department:", 2, entry_dept)
create_form_row("Phone Number:", 3, entry_phone)
create_form_row("Attendance:", 4, attendance_dropdown)

# ---- Buttons ----
btn_add = tk.Button(form_frame, text="Add", command=add_employee, bg="#27ae60", fg="white", font=BUTTON_FONT, width=15)
btn_update = tk.Button(form_frame, text="Update", command=update_employee, bg="#2980b9", fg="white", font=BUTTON_FONT, width=15)
btn_delete = tk.Button(form_frame, text="Delete", command=delete_employee, bg="#c0392b", fg="white", font=BUTTON_FONT, width=15)
btn_clear = tk.Button(form_frame, text="Clear", command=clear_fields, bg="#7f8c8d", fg="white", font=BUTTON_FONT, width=15)

btn_add.grid(row=5, column=0, pady=10)
btn_update.grid(row=5, column=1, pady=10)
btn_delete.grid(row=6, column=0, pady=5)
btn_clear.grid(row=6, column=1, pady=5)
# ---- Search Section ----
search_frame = tk.Frame(root, bg="#f4f6f7")
search_frame.pack(pady=5, fill=tk.X, padx=20)

tk.Label(search_frame, text="Search (ID or Name):", font=LABEL_FONT, bg="#f4f6f7").pack(side=tk.LEFT, padx=5)

search_var = tk.StringVar()
search_entry = tk.Entry(search_frame, textvariable=search_var, font=ENTRY_FONT)
search_entry.pack(side=tk.LEFT, padx=5)

def search_employee():
    query = search_var.get().strip()
    tree.delete(*tree.get_children())
    if not query:
        load_employees()
        return
    # Search in ID or Name columns
    cursor.execute("SELECT * FROM employees WHERE id LIKE ? OR name LIKE ?", (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)

search_btn = tk.Button(search_frame, text="Search", command=search_employee, bg="#2980b9", fg="white", font=BUTTON_FONT)
search_btn.pack(side=tk.LEFT, padx=5)

def clear_search():
    search_var.set("")
    load_employees()

clear_search_btn = tk.Button(search_frame, text="Clear Search", command=clear_search, bg="#7f8c8d", fg="white", font=BUTTON_FONT)
clear_search_btn.pack(side=tk.LEFT, padx=5)
# ---- Treeview Row Select Handler ----
def on_row_select(event):
    selected = event.widget.selection()
    if selected:
        item = event.widget.item(selected[0])
        values = item['values']
        if len(values) == 5:
            entry_id.delete(0, tk.END)
            entry_id.insert(0, values[0])
            entry_name.delete(0, tk.END)
            entry_name.insert(0, values[1])
            entry_dept.delete(0, tk.END)
            entry_dept.insert(0, values[2])
            entry_phone.delete(0, tk.END)
            entry_phone.insert(0, values[3])
            attendance_var.set(values[4])

# ---- Table Section ----
table_frame = tk.Frame(root)
table_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

columns = ("ID", "Name", "Department", "Phone", "Attendance")
tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                    yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

scroll_y.config(command=tree.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
scroll_x.config(command=tree.xview)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
tree.pack(fill=tk.BOTH, expand=True)

tree.bind("<<TreeviewSelect>>", on_row_select)

# ===== STARTUP =====
load_employees()
root.mainloop()
conn.close()
