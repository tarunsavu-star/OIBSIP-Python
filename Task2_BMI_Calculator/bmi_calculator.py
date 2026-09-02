import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import csv

import matplotlib.pyplot as plt


# ============================================================
# DATABASE
# ============================================================

DB_NAME = "bmi_database.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_database():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Unable to create database.\n\n{error}"
        )


# ============================================================
# BMI FUNCTIONS
# ============================================================

def calculate_bmi_value(weight, height):
    return weight / (height ** 2)


def get_category(bmi):
    if bmi < 18.5:
        return "Underweight"

    elif bmi < 25:
        return "Normal"

    elif bmi < 30:
        return "Overweight"

    return "Obese"


def get_category_color(category):
    colors = {
        "Underweight": "#2980b9",
        "Normal": "#27ae60",
        "Overweight": "#f39c12",
        "Obese": "#e74c3c"
    }

    return colors.get(category, "#34495e")


# ============================================================
# VALIDATION
# ============================================================

def validate_inputs():
    username = name_entry.get().strip()
    weight_text = weight_entry.get().strip()
    height_text = height_entry.get().strip()

    if not username:
        messagebox.showwarning(
            "Missing Name",
            "Please enter a user name."
        )
        return None

    if not weight_text:
        messagebox.showwarning(
            "Missing Weight",
            "Please enter your weight."
        )
        return None

    if not height_text:
        messagebox.showwarning(
            "Missing Height",
            "Please enter your height."
        )
        return None

    try:
        weight = float(weight_text)
        height = float(height_text)

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Weight and height must contain numbers only."
        )
        return None

    if weight <= 0:
        messagebox.showerror(
            "Invalid Weight",
            "Weight must be greater than zero."
        )
        return None

    if height <= 0:
        messagebox.showerror(
            "Invalid Height",
            "Height must be greater than zero."
        )
        return None

    if height > 3:
        messagebox.showwarning(
            "Check Height",
            "Height should be entered in meters.\n\n"
            "Example: 1.75"
        )
        return None

    return username, weight, height


# ============================================================
# CALCULATE
# ============================================================

def calculate_bmi():

    data = validate_inputs()

    if data is None:
        return

    username, weight, height = data

    bmi = calculate_bmi_value(
        weight,
        height
    )

    category = get_category(bmi)

    color = get_category_color(category)

    bmi_result_label.config(
        text=f"{bmi:.2f}"
    )

    category_result_label.config(
        text=category,
        foreground=color
    )

    update_meter(bmi, color)

    save_bmi_record(
        username,
        weight,
        height,
        bmi,
        category
    )

    status_label.config(
        text=f"Record saved for {username}."
    )


# ============================================================
# SAVE RECORD
# ============================================================

def save_bmi_record(
    username,
    weight,
    height,
    bmi,
    category
):

    try:
        connection = get_connection()
        cursor = connection.cursor()

        current_date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            INSERT INTO bmi_records
            (username, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            weight,
            height,
            bmi,
            category,
            current_date
        ))

        connection.commit()
        connection.close()

        load_history()
        load_users()
        update_dashboard()

    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Write Error",
            f"Unable to save the BMI record.\n\n{error}"
        )


# ============================================================
# UPDATE RECORD
# ============================================================

def update_record():

    selected = history_tree.selection()

    if not selected:
        messagebox.showwarning(
            "Select Record",
            "Please select a record from the history."
        )
        return

    data = validate_inputs()

    if data is None:
        return

    username, weight, height = data

    bmi = calculate_bmi_value(
        weight,
        height
    )

    category = get_category(bmi)

    item = history_tree.item(
        selected[0]
    )

    record_id = item["values"][0]

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE bmi_records
            SET username = ?,
                weight = ?,
                height = ?,
                bmi = ?,
                category = ?
            WHERE id = ?
        """, (
            username,
            weight,
            height,
            bmi,
            category,
            record_id
        ))

        connection.commit()
        connection.close()

        load_history()
        load_users()
        update_dashboard()

        messagebox.showinfo(
            "Updated",
            "BMI record updated successfully."
        )

    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Write Error",
            f"Unable to update the record.\n\n{error}"
        )


# ============================================================
# DELETE RECORD
# ============================================================

def delete_record():

    selected = history_tree.selection()

    if not selected:
        messagebox.showwarning(
            "Select Record",
            "Please select a record."
        )
        return

    item = history_tree.item(
        selected[0]
    )

    record_id = item["values"][0]

    confirm = messagebox.askyesno(
        "Delete Record",
        "Are you sure you want to delete this record?"
    )

    if not confirm:
        return

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM bmi_records
            WHERE id = ?
        """, (record_id,))

        connection.commit()
        connection.close()

        load_history()
        load_users()
        update_dashboard()

        clear_form()

        messagebox.showinfo(
            "Deleted",
            "Record deleted successfully."
        )

    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Error",
            f"Unable to delete the record.\n\n{error}"
        )


# ============================================================
# LOAD HISTORY
# ============================================================

def load_history():

    for item in history_tree.get_children():
        history_tree.delete(item)

    search_text = search_entry.get().strip().lower()

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, username, weight, height,
                   bmi, category, date
            FROM bmi_records
            ORDER BY id DESC
        """)

        records = cursor.fetchall()

        connection.close()

        for record in records:

            username = str(record[1])

            if search_text:
                if search_text not in username.lower():
                    continue

            history_tree.insert(
                "",
                tk.END,
                values=(
                    record[0],
                    record[1],
                    f"{record[2]:.2f}",
                    f"{record[3]:.2f}",
                    f"{record[4]:.2f}",
                    record[5],
                    record[6]
                )
            )

    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Read Error",
            f"Unable to load BMI history.\n\n{error}"
        )


# ============================================================
# SELECT HISTORY RECORD
# ============================================================

def select_history_record(event=None):

    selected = history_tree.selection()

    if not selected:
        return

    item = history_tree.item(
        selected[0]
    )

    values = item["values"]

    if len(values) < 7:
        return

    name_entry.delete(0, tk.END)
    name_entry.insert(0, values[1])

    weight_entry.delete(0, tk.END)
    weight_entry.insert(0, values[2])

    height_entry.delete(0, tk.END)
    height_entry.insert(0, values[3])

    bmi_result_label.config(
        text=values[4]
    )

    category_result_label.config(
        text=values[5],
        foreground=get_category_color(
            values[5]
        )
    )


# ============================================================
# SEARCH
# ============================================================

def search_history(event=None):
    load_history()


# ============================================================
# LOAD USERS
# ============================================================

def load_users():

    user_combo["values"] = ()

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT DISTINCT username
            FROM bmi_records
            ORDER BY username
        """)

        users = [
            row[0]
            for row in cursor.fetchall()
        ]

        connection.close()

        user_combo["values"] = users

    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Error",
            f"Unable to load users.\n\n{error}"
        )


# ============================================================
# SELECT USER
# ============================================================

def select_user(event=None):

    username = user_combo.get().strip()

    if not username:
        return

    name_entry.delete(0, tk.END)
    name_entry.insert(0, username)

    show_user_latest(username)


def show_user_latest(username):

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT weight, height, bmi, category
            FROM bmi_records
            WHERE username = ?
            ORDER BY id DESC
            LIMIT 1
        """, (username,))

        record = cursor.fetchone()

        connection.close()

        if record:

            weight_entry.delete(0, tk.END)
            weight_entry.insert(
                0,
                f"{record[0]:.2f}"
            )

            height_entry.delete(0, tk.END)
            height_entry.insert(
                0,
                f"{record[1]:.2f}"
            )

            bmi_result_label.config(
                text=f"{record[2]:.2f}"
            )

            category_result_label.config(
                text=record[3],
                foreground=get_category_color(
                    record[3]
                )
            )

    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Error",
            f"Unable to load user data.\n\n{error}"
        )


# ============================================================
# TREND GRAPH
# ============================================================

def show_trend():

    username = user_combo.get().strip()

    if not username:
        username = name_entry.get().strip()

    if not username:

        messagebox.showwarning(
            "User Required",
            "Please select or enter a user name."
        )

        return

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT date, bmi
            FROM bmi_records
            WHERE username = ?
            ORDER BY id ASC
        """, (username,))

        records = cursor.fetchall()

        connection.close()

        if not records:

            messagebox.showinfo(
                "No Records",
                f"No BMI history found for {username}."
            )

            return

        dates = [
            record[0]
            for record in records
        ]

        bmi_values = [
            record[1]
            for record in records
        ]

        plt.figure(
            figsize=(11, 6)
        )

        plt.plot(
            dates,
            bmi_values,
            marker="o",
            linewidth=2
        )

        plt.axhline(
            18.5,
            linestyle="--",
            label="18.5 - Underweight"
        )

        plt.axhline(
            25,
            linestyle="--",
            label="25 - Overweight"
        )

        plt.axhline(
            30,
            linestyle="--",
            label="30 - Obese"
        )

        plt.title(
            f"BMI Trend - {username}"
        )

        plt.xlabel(
            "Date"
        )

        plt.ylabel(
            "BMI"
        )

        plt.xticks(
            rotation=45,
            ha="right"
        )

        plt.legend()

        plt.tight_layout()

        plt.show()

    except sqlite3.Error as error:

        messagebox.showerror(
            "Database Error",
            f"Unable to create BMI graph.\n\n{error}"
        )


# ============================================================
# EXPORT CSV
# ============================================================

def export_csv():

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, username, weight,
                   height, bmi, category, date
            FROM bmi_records
            ORDER BY id DESC
        """)

        records = cursor.fetchall()

        connection.close()

        if not records:

            messagebox.showinfo(
                "No Data",
                "There are no BMI records to export."
            )

            return

        file_path = filedialog.asksaveasfilename(
            title="Save BMI History",
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv")
            ]
        )

        if not file_path:
            return

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "ID",
                "User",
                "Weight (kg)",
                "Height (m)",
                "BMI",
                "Category",
                "Date"
            ])

            writer.writerows(records)

        messagebox.showinfo(
            "Export Complete",
            "BMI history exported successfully."
        )

    except (sqlite3.Error, OSError) as error:

        messagebox.showerror(
            "Export Error",
            f"Unable to export BMI history.\n\n{error}"
        )


# ============================================================
# CLEAR FORM
# ============================================================

def clear_form():

    name_entry.delete(
        0,
        tk.END
    )

    weight_entry.delete(
        0,
        tk.END
    )

    height_entry.delete(
        0,
        tk.END
    )

    user_combo.set("")

    bmi_result_label.config(
        text="--"
    )

    category_result_label.config(
        text="Enter your details",
        foreground="#667085"
    )

    meter_canvas.delete(
        "all"
    )

    status_label.config(
        text="Ready"
    )


# ============================================================
# BMI METER
# ============================================================

def update_meter(bmi, color):

    meter_canvas.delete(
        "all"
    )

    width = 430
    height = 22

    x = 10
    y = 15

    meter_canvas.create_rectangle(
        x,
        y,
        width,
        y + height,
        outline="",
        fill="#e5e7eb"
    )

    percentage = min(
        bmi / 40,
        1
    )

    meter_canvas.create_rectangle(
        x,
        y,
        x + (width - 10) * percentage,
        y + height,
        outline="",
        fill=color
    )


# ============================================================
# DASHBOARD
# ============================================================

def update_dashboard():

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM bmi_records"
        )

        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(DISTINCT username) FROM bmi_records"
        )

        users = cursor.fetchone()[0]

        cursor.execute(
            "SELECT AVG(bmi) FROM bmi_records"
        )

        average = cursor.fetchone()[0]

        cursor.execute("""
            SELECT category, COUNT(*)
            FROM bmi_records
            GROUP BY category
        """)

        categories = cursor.fetchall()

        connection.close()

        total_value.config(
            text=str(total)
        )

        users_value.config(
            text=str(users)
        )

        if average:
            average_value.config(
                text=f"{average:.2f}"
            )
        else:
            average_value.config(
                text="--"
            )

        category_counts = {
            "Underweight": 0,
            "Normal": 0,
            "Overweight": 0,
            "Obese": 0
        }

        for category, count in categories:
            category_counts[category] = count

        underweight_value.config(
            text=str(
                category_counts["Underweight"]
            )
        )

        normal_value.config(
            text=str(
                category_counts["Normal"]
            )
        )

        overweight_value.config(
            text=str(
                category_counts["Overweight"]
            )
        )

        obese_value.config(
            text=str(
                category_counts["Obese"]
            )
        )

    except sqlite3.Error as error:

        messagebox.showerror(
            "Dashboard Error",
            f"Unable to load dashboard data.\n\n{error}"
        )


# ============================================================
# WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "BMI Calculator - Advanced"
)

root.geometry(
    "1180x780"
)

root.minsize(
    1000,
    700
)

root.configure(
    background="#f4f6f8"
)


# ============================================================
# STYLE
# ============================================================

style = ttk.Style()

try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure(
    "TButton",
    font=("Arial", 10, "bold"),
    padding=10
)

style.configure(
    "TNotebook",
    background="#f4f6f8",
    borderwidth=0
)

style.configure(
    "TNotebook.Tab",
    font=("Arial", 11, "bold"),
    padding=(20, 10)
)

style.configure(
    "Treeview",
    rowheight=32,
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold")
)


# ============================================================
# HEADER
# ============================================================

header = tk.Frame(
    root,
    background="#17202a",
    height=85
)

header.pack(
    fill="x"
)

tk.Label(
    header,
    text="BMI Calculator",
    font=("Arial", 27, "bold"),
    background="#17202a",
    foreground="white"
).pack(
    side="left",
    padx=30,
    pady=20
)

tk.Label(
    header,
    text="Advanced Health & BMI Tracker",
    font=("Arial", 11),
    background="#17202a",
    foreground="#bdc3c7"
).pack(
    side="right",
    padx=30
)


# ============================================================
# NOTEBOOK
# ============================================================

notebook = ttk.Notebook(
    root
)

notebook.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)


# ============================================================
# CALCULATOR TAB
# ============================================================

calculator_tab = tk.Frame(
    notebook,
    background="#f4f6f8"
)

notebook.add(
    calculator_tab,
    text="  Calculator  "
)


# ============================================================
# INPUT CARD
# ============================================================

input_card = tk.LabelFrame(
    calculator_tab,
    text=" User Details ",
    font=("Arial", 13, "bold"),
    background="white",
    padx=25,
    pady=20
)

input_card.pack(
    fill="x",
    padx=20,
    pady=20
)


tk.Label(
    input_card,
    text="Existing User",
    font=("Arial", 10, "bold"),
    background="white"
).grid(
    row=0,
    column=0,
    padx=10,
    pady=8,
    sticky="w"
)


user_combo = ttk.Combobox(
    input_card,
    width=24,
    state="readonly"
)

user_combo.grid(
    row=0,
    column=1,
    padx=10,
    pady=8
)

user_combo.bind(
    "<<ComboboxSelected>>",
    select_user
)


tk.Label(
    input_card,
    text="User Name",
    font=("Arial", 10, "bold"),
    background="white"
).grid(
    row=0,
    column=2,
    padx=10,
    pady=8,
    sticky="w"
)


name_entry = ttk.Entry(
    input_card,
    width=25
)

name_entry.grid(
    row=0,
    column=3,
    padx=10,
    pady=8
)


tk.Label(
    input_card,
    text="Weight (kg)",
    font=("Arial", 10, "bold"),
    background="white"
).grid(
    row=1,
    column=0,
    padx=10,
    pady=8,
    sticky="w"
)


weight_entry = ttk.Entry(
    input_card,
    width=25
)

weight_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=8
)


tk.Label(
    input_card,
    text="Height (m)",
    font=("Arial", 10, "bold"),
    background="white"
).grid(
    row=1,
    column=2,
    padx=10,
    pady=8,
    sticky="w"
)


height_entry = ttk.Entry(
    input_card,
    width=25
)

height_entry.grid(
    row=1,
    column=3,
    padx=10,
    pady=8
)


button_frame = tk.Frame(
    input_card,
    background="white"
)

button_frame.grid(
    row=2,
    column=0,
    columnspan=4,
    pady=15
)


ttk.Button(
    button_frame,
    text="Calculate BMI",
    command=calculate_bmi
).pack(
    side="left",
    padx=5
)


ttk.Button(
    button_frame,
    text="Clear",
    command=clear_form
).pack(
    side="left",
    padx=5
)


# ============================================================
# RESULT
# ============================================================

result_card = tk.LabelFrame(
    calculator_tab,
    text=" BMI Result ",
    font=("Arial", 13, "bold"),
    background="white",
    padx=30,
    pady=20
)

result_card.pack(
    fill="x",
    padx=20,
    pady=(0, 20)
)


bmi_result_label = tk.Label(
    result_card,
    text="--",
    font=("Arial", 48, "bold"),
    background="white",
    foreground="#17202a"
)

bmi_result_label.pack()


category_result_label = tk.Label(
    result_card,
    text="Enter your details",
    font=("Arial", 17, "bold"),
    background="white",
    foreground="#667085"
)

category_result_label.pack(
    pady=5
)


meter_canvas = tk.Canvas(
    result_card,
    width=430,
    height=50,
    background="white",
    highlightthickness=0
)

meter_canvas.pack()


tk.Label(
    result_card,
    text=(
        "Underweight < 18.5    "
        "Normal 18.5–24.9    "
        "Overweight 25–29.9    "
        "Obese ≥ 30"
    ),
    font=("Arial", 9),
    background="white",
    foreground="#667085"
).pack()


status_label = tk.Label(
    result_card,
    text="Ready",
    font=("Arial", 10),
    background="white",
    foreground="#667085"
)

status_label.pack(
    pady=8
)


# ============================================================
# HISTORY TAB
# ============================================================

history_tab = tk.Frame(
    notebook,
    background="#f4f6f8"
)

notebook.add(
    history_tab,
    text="  History  "
)


history_top = tk.Frame(
    history_tab,
    background="#f4f6f8"
)

history_top.pack(
    fill="x",
    padx=20,
    pady=20
)


tk.Label(
    history_top,
    text="Search User:",
    font=("Arial", 11, "bold"),
    background="#f4f6f8"
).pack(
    side="left",
    padx=(0, 8)
)


search_entry = ttk.Entry(
    history_top,
    width=30
)

search_entry.pack(
    side="left"
)

search_entry.bind(
    "<KeyRelease>",
    search_history
)


ttk.Button(
    history_top,
    text="Export CSV",
    command=export_csv
).pack(
    side="right",
    padx=5
)


ttk.Button(
    history_top,
    text="Delete Selected",
    command=delete_record
).pack(
    side="right",
    padx=5
)


ttk.Button(
    history_top,
    text="Update Selected",
    command=update_record
).pack(
    side="right",
    padx=5
)


# ============================================================
# HISTORY TABLE
# ============================================================

history_frame = tk.Frame(
    history_tab,
    background="white"
)

history_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(0, 20)
)


columns = (
    "ID",
    "User",
    "Weight",
    "Height",
    "BMI",
    "Category",
    "Date"
)


history_tree = ttk.Treeview(
    history_frame,
    columns=columns,
    show="headings"
)


for column in columns:

    history_tree.heading(
        column,
        text=column
    )

    history_tree.column(
        column,
        anchor="center",
        width=130
    )


history_tree.column(
    "ID",
    width=55
)


history_scroll = ttk.Scrollbar(
    history_frame,
    orient="vertical",
    command=history_tree.yview
)

history_tree.configure(
    yscrollcommand=history_scroll.set
)


history_tree.pack(
    side="left",
    fill="both",
    expand=True
)

history_scroll.pack(
    side="right",
    fill="y"
)


history_tree.bind(
    "<<TreeviewSelect>>",
    select_history_record
)


# ============================================================
# TREND TAB
# ============================================================

trend_tab = tk.Frame(
    notebook,
    background="#f4f6f8"
)

notebook.add(
    trend_tab,
    text="  BMI Trend  "
)


tk.Label(
    trend_tab,
    text="BMI Trend Analysis",
    font=("Arial", 25, "bold"),
    background="#f4f6f8",
    foreground="#17202a"
).pack(
    pady=(50, 10)
)


tk.Label(
    trend_tab,
    text=(
        "Select a user from the Calculator tab "
        "or enter a user name, then view their BMI history."
    ),
    font=("Arial", 11),
    background="#f4f6f8",
    foreground="#667085"
).pack(
    pady=5
)


ttk.Button(
    trend_tab,
    text="View BMI Trend Graph",
    command=show_trend
).pack(
    pady=30
)


# ============================================================
# DASHBOARD TAB
# ============================================================

dashboard_tab = tk.Frame(
    notebook,
    background="#f4f6f8"
)

notebook.add(
    dashboard_tab,
    text="  Dashboard  "
)


tk.Label(
    dashboard_tab,
    text="BMI Dashboard",
    font=("Arial", 25, "bold"),
    background="#f4f6f8",
    foreground="#17202a"
).pack(
    pady=(35, 25)
)


dashboard_frame = tk.Frame(
    dashboard_tab,
    background="#f4f6f8"
)

dashboard_frame.pack()


def create_stat_card(parent, title, variable, row, column):

    card = tk.Frame(
        parent,
        background="white",
        width=210,
        height=120,
        bd=1,
        relief="solid"
    )

    card.grid(
        row=row,
        column=column,
        padx=10,
        pady=10
    )

    card.grid_propagate(False)

    tk.Label(
        card,
        text=title,
        font=("Arial", 10, "bold"),
        background="white",
        foreground="#667085"
    ).pack(
        pady=(20, 5)
    )

    tk.Label(
        card,
        textvariable=variable,
        font=("Arial", 27, "bold"),
        background="white",
        foreground="#17202a"
    ).pack()


total_value = tk.StringVar(value="0")
users_value = tk.StringVar(value="0")
average_value = tk.StringVar(value="--")
underweight_value = tk.StringVar(value="0")
normal_value = tk.StringVar(value="0")
overweight_value = tk.StringVar(value="0")
obese_value = tk.StringVar(value="0")


create_stat_card(
    dashboard_frame,
    "Total Records",
    total_value,
    0,
    0
)

create_stat_card(
    dashboard_frame,
    "Total Users",
    users_value,
    0,
    1
)

create_stat_card(
    dashboard_frame,
    "Average BMI",
    average_value,
    0,
    2
)

create_stat_card(
    dashboard_frame,
    "Underweight",
    underweight_value,
    1,
    0
)

create_stat_card(
    dashboard_frame,
    "Normal",
    normal_value,
    1,
    1
)

create_stat_card(
    dashboard_frame,
    "Overweight",
    overweight_value,
    1,
    2
)

create_stat_card(
    dashboard_frame,
    "Obese",
    obese_value,
    1,
    3
)


# ============================================================
# FOOTER
# ============================================================

footer = tk.Label(
    root,
    text="BMI Calculator | Python • Tkinter • SQLite • Matplotlib",
    font=("Arial", 9),
    background="#17202a",
    foreground="#bdc3c7"
)

footer.pack(
    fill="x",
    pady=0
)


# ============================================================
# START APPLICATION
# ============================================================

create_database()

load_users()

load_history()

update_dashboard()

root.mainloop()
