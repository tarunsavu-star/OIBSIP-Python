import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import secrets
import string
import math
import csv
import json
import os
from datetime import datetime


# ============================================================
# PASSWORD GENERATOR - ADVANCED
# OIBSIP PYTHON INTERNSHIP
# ============================================================

APP_TITLE = "Advanced Password Generator"
HISTORY_FILE = "password_history.json"


class PasswordGeneratorApp:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1100x760")
        self.root.minsize(900, 650)

        self.dark_mode = False
        self.history = []
        self.generated_passwords = []

        # Variables
        self.length_var = tk.IntVar(value=16)

        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.number_var = tk.BooleanVar(value=True)
        self.symbol_var = tk.BooleanVar(value=True)
        self.exclude_var = tk.BooleanVar(value=False)

        self.custom_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar(value=False)

        self.strength_var = tk.StringVar(value="Ready")
        self.entropy_var = tk.StringVar(value="Entropy: -- bits")
        self.charset_var = tk.StringVar(value="Character set: --")
        self.status_var = tk.StringVar(value="Ready")

        self.load_history()
        self.setup_style()
        self.build_ui()
        self.refresh_history()

    # ========================================================
    # STYLE
    # ========================================================

    def setup_style(self):
        self.style = ttk.Style()

        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            bg = "#171717"
            card = "#222222"
            fg = "#F5F5F5"
            entry = "#2D2D2D"
            accent = "#00C896"
        else:
            bg = "#F4F6F8"
            card = "#FFFFFF"
            fg = "#202124"
            entry = "#FFFFFF"
            accent = "#2563EB"

        self.bg_color = bg
        self.card_color = card
        self.fg_color = fg
        self.entry_color = entry
        self.accent_color = accent

        self.root.configure(bg=bg)

        self.style.configure(
            "TFrame",
            background=bg
        )

        self.style.configure(
            "Card.TFrame",
            background=card
        )

        self.style.configure(
            "TLabel",
            background=bg,
            foreground=fg,
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "Title.TLabel",
            background=bg,
            foreground=fg,
            font=("Segoe UI", 26, "bold")
        )

        self.style.configure(
            "Subtitle.TLabel",
            background=bg,
            foreground=fg,
            font=("Segoe UI", 11)
        )

        self.style.configure(
            "CardTitle.TLabel",
            background=card,
            foreground=fg,
            font=("Segoe UI", 13, "bold")
        )

        self.style.configure(
            "CardText.TLabel",
            background=card,
            foreground=fg,
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "TCheckbutton",
            background=card,
            foreground=fg,
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 8)
        )

        self.style.configure(
            "Accent.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(18, 10)
        )

        self.style.configure(
            "TNotebook",
            background=bg
        )

        self.style.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 10, "bold"),
            padding=(15, 8)
        )

        self.style.configure(
            "Treeview",
            font=("Segoe UI", 9),
            rowheight=28
        )

        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold")
        )

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        # Header
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=30, pady=(25, 10))

        ttk.Label(
            header,
            text="🔐 Advanced Password Generator",
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Create strong, secure and customizable passwords using Python.",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(5, 0))

        theme_button = ttk.Button(
            header,
            text="☀ / ☾ Theme",
            command=self.toggle_theme
        )
        theme_button.pack(anchor="e", pady=(0, 5))

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        self.generator_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.info_tab = ttk.Frame(self.notebook)

        self.notebook.add(
            self.generator_tab,
            text="  Generator  "
        )

        self.notebook.add(
            self.history_tab,
            text="  History  "
        )

        self.notebook.add(
            self.info_tab,
            text="  Security Info  "
        )

        self.build_generator_tab()
        self.build_history_tab()
        self.build_info_tab()

        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        ttk.Label(
            status_frame,
            textvariable=self.status_var
        ).pack(side="left")

    # ========================================================
    # GENERATOR TAB
    # ========================================================

    def build_generator_tab(self):

        container = ttk.Frame(self.generator_tab)
        container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # Left panel
        left = ttk.Frame(
            container,
            style="Card.TFrame"
        )
        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        # Right panel
        right = ttk.Frame(
            container,
            style="Card.TFrame"
        )
        right.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        # ----------------------------------------------------
        # LEFT
        # ----------------------------------------------------

        ttk.Label(
            left,
            text="Password Settings",
            style="CardTitle.TLabel"
        ).pack(anchor="w", padx=20, pady=(20, 15))

        length_frame = ttk.Frame(
            left,
            style="Card.TFrame"
        )
        length_frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        ttk.Label(
            length_frame,
            text="Password Length",
            style="CardText.TLabel"
        ).pack(side="left")

        self.length_label = ttk.Label(
            length_frame,
            text="16",
            style="CardText.TLabel"
        )
        self.length_label.pack(side="right")

        self.length_scale = ttk.Scale(
            left,
            from_=4,
            to=128,
            orient="horizontal",
            command=self.update_length
        )
        self.length_scale.set(16)
        self.length_scale.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        options = [
            ("Uppercase (A-Z)", self.upper_var),
            ("Lowercase (a-z)", self.lower_var),
            ("Numbers (0-9)", self.number_var),
            ("Special characters", self.symbol_var),
            ("Exclude ambiguous characters", self.exclude_var)
        ]

        for text, variable in options:
            ttk.Checkbutton(
                left,
                text=text,
                variable=variable,
                command=self.update_charset_info
            ).pack(
                anchor="w",
                padx=20,
                pady=4
            )

        ttk.Label(
            left,
            text="Custom Characters (optional)",
            style="CardText.TLabel"
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        custom_entry = tk.Entry(
            left,
            textvariable=self.custom_var,
            bg=self.entry_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief="solid",
            bd=1,
            font=("Segoe UI", 10)
        )
        custom_entry.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        preset_frame = ttk.Frame(
            left,
            style="Card.TFrame"
        )
        preset_frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        ttk.Label(
            preset_frame,
            text="Quick Presets:",
            style="CardText.TLabel"
        ).pack(anchor="w", pady=(0, 8))

        ttk.Button(
            preset_frame,
            text="PIN",
            command=self.preset_pin
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            preset_frame,
            text="Strong",
            command=self.preset_strong
        ).pack(side="left", padx=5)

        ttk.Button(
            preset_frame,
            text="Ultra Secure",
            command=self.preset_ultra
        ).pack(side="left", padx=5)

        ttk.Button(
            left,
            text="Generate Password",
            style="Accent.TButton",
            command=self.generate_password
        ).pack(
            fill="x",
            padx=20,
            pady=20
        )

        # ----------------------------------------------------
        # RIGHT
        # ----------------------------------------------------

        ttk.Label(
            right,
            text="Generated Password",
            style="CardTitle.TLabel"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 12)
        )

        password_frame = ttk.Frame(
            right,
            style="Card.TFrame"
        )
        password_frame.pack(
            fill="x",
            padx=20
        )

        self.password_entry = tk.Entry(
            password_frame,
            textvariable=self.password_var,
            show="•",
            bg=self.entry_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief="solid",
            bd=1,
            font=("Consolas", 15, "bold")
        )

        self.password_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=9
        )

        ttk.Button(
            password_frame,
            text="Copy",
            command=self.copy_password
        ).pack(
            side="left",
            padx=(8, 0)
        )

        ttk.Checkbutton(
            right,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        ).pack(
            anchor="w",
            padx=20,
            pady=10
        )

        # Strength
        ttk.Label(
            right,
            text="Password Strength",
            style="CardText.TLabel"
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        self.strength_label = ttk.Label(
            right,
            textvariable=self.strength_var,
            style="CardTitle.TLabel"
        )
        self.strength_label.pack(
            anchor="w",
            padx=20
        )

        self.strength_bar = ttk.Progressbar(
            right,
            orient="horizontal",
            mode="determinate",
            maximum=100
        )
        self.strength_bar.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ttk.Label(
            right,
            textvariable=self.entropy_var,
            style="CardText.TLabel"
        ).pack(
            anchor="w",
            padx=20,
            pady=3
        )

        ttk.Label(
            right,
            textvariable=self.charset_var,
            style="CardText.TLabel"
        ).pack(
            anchor="w",
            padx=20,
            pady=3
        )

        buttons = ttk.Frame(
            right,
            style="Card.TFrame"
        )
        buttons.pack(
            fill="x",
            padx=20,
            pady=20
        )

        ttk.Button(
            buttons,
            text="Copy",
            command=self.copy_password
        ).pack(
            side="left",
            padx=(0, 5)
        )

        ttk.Button(
            buttons,
            text="Generate Again",
            command=self.generate_password
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            buttons,
            text="Clear",
            command=self.clear_password
        ).pack(
            side="left",
            padx=5
        )

        # Multiple passwords
        multi_frame = ttk.Frame(
            right,
            style="Card.TFrame"
        )
        multi_frame.pack(
            fill="x",
            padx=20
        )

        ttk.Label(
            multi_frame,
            text="Generate multiple passwords",
            style="CardText.TLabel"
        ).pack(anchor="w")

        self.multiple_spin = ttk.Spinbox(
            multi_frame,
            from_=1,
            to=20,
            width=8
        )
        self.multiple_spin.set(5)
        self.multiple_spin.pack(
            side="left",
            pady=8
        )

        ttk.Button(
            multi_frame,
            text="Generate Multiple",
            command=self.generate_multiple
        ).pack(
            side="left",
            padx=8
        )

        self.update_charset_info()

    # ========================================================
    # HISTORY TAB
    # ========================================================

    def build_history_tab(self):

        frame = ttk.Frame(self.history_tab)
        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        ttk.Label(
            frame,
            text="Password History",
            style="Title.TLabel"
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        ttk.Label(
            frame,
            text="Generated passwords are stored locally for this application.",
            style="Subtitle.TLabel"
        ).pack(
            anchor="w",
            pady=(0, 15)
        )

        table_frame = ttk.Frame(frame)
        table_frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "date",
            "password",
            "length",
            "strength"
        )

        self.history_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.history_tree.heading(
            "date",
            text="Date"
        )

        self.history_tree.heading(
            "password",
            text="Password"
        )

        self.history_tree.heading(
            "length",
            text="Length"
        )

        self.history_tree.heading(
            "strength",
            text="Strength"
        )

        self.history_tree.column(
            "date",
            width=180
        )

        self.history_tree.column(
            "password",
            width=420
        )

        self.history_tree.column(
            "length",
            width=80,
            anchor="center"
        )

        self.history_tree.column(
            "strength",
            width=150,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.history_tree.yview
        )

        self.history_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.history_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        button_frame = ttk.Frame(frame)
        button_frame.pack(
            fill="x",
            pady=15
        )

        ttk.Button(
            button_frame,
            text="Copy Selected",
            command=self.copy_selected_history
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Delete Selected",
            command=self.delete_selected_history
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Export TXT",
            command=self.export_txt
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Export CSV",
            command=self.export_csv
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Clear History",
            command=self.clear_history
        ).pack(
            side="right",
            padx=5
        )

    # ========================================================
    # INFO TAB
    # ========================================================

    def build_info_tab(self):

        frame = ttk.Frame(self.info_tab)
        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=30
        )

        ttk.Label(
            frame,
            text="Security & Application Information",
            style="Title.TLabel"
        ).pack(
            anchor="w",
            pady=(0, 20)
        )

        info_text = (
            "SECURE PASSWORD GENERATION\n\n"
            "This application uses Python's secrets module for "
            "cryptographically secure random generation.\n\n"
            "PASSWORD STRENGTH\n\n"
            "Strength is estimated using password length, character "
            "diversity and estimated entropy.\n\n"
            "ENTROPY\n\n"
            "Entropy represents the estimated number of bits of "
            "randomness available in the generated password.\n\n"
            "BEST PRACTICES\n\n"
            "• Use long passwords.\n"
            "• Use different passwords for different accounts.\n"
            "• Include multiple character types.\n"
            "• Avoid personal information.\n"
            "• Use a password manager when possible.\n\n"
            "TECHNOLOGIES\n\n"
            "Python • Tkinter • secrets • JSON • CSV"
        )

        text_box = tk.Text(
            frame,
            wrap="word",
            font=("Segoe UI", 11),
            bg=self.entry_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief="solid",
            bd=1
        )

        text_box.insert(
            "1.0",
            info_text
        )

        text_box.configure(
            state="disabled"
        )

        text_box.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # PASSWORD GENERATION
    # ========================================================

    def get_character_set(self):

        characters = ""

        if self.upper_var.get():
            characters += string.ascii_uppercase

        if self.lower_var.get():
            characters += string.ascii_lowercase

        if self.number_var.get():
            characters += string.digits

        if self.symbol_var.get():
            characters += string.punctuation

        custom = self.custom_var.get()

        if custom:
            characters += custom

        if self.exclude_var.get():
            ambiguous = "Il1O0o|`'\""
            characters = "".join(
                char for char in characters
                if char not in ambiguous
            )

        return "".join(dict.fromkeys(characters))

    def generate_secure_password(self, length):

        characters = self.get_character_set()

        if not characters:
            raise ValueError(
                "Select at least one character type."
            )

        if length < 4 or length > 128:
            raise ValueError(
                "Password length must be between 4 and 128."
            )

        password = []

        selected_groups = []

        if self.upper_var.get():
            selected_groups.append(
                string.ascii_uppercase
            )

        if self.lower_var.get():
            selected_groups.append(
                string.ascii_lowercase
            )

        if self.number_var.get():
            selected_groups.append(
                string.digits
            )

        if self.symbol_var.get():
            selected_groups.append(
                string.punctuation
            )

        if self.custom_var.get():
            selected_groups.append(
                self.custom_var.get()
            )

        # Remove ambiguous characters
        if self.exclude_var.get():
            ambiguous = "Il1O0o|`'\""

            selected_groups = [
                "".join(
                    c for c in group
                    if c not in ambiguous
                )
                for group in selected_groups
            ]

            selected_groups = [
                group for group in selected_groups
                if group
            ]

        # Guarantee character diversity
        for group in selected_groups:
            password.append(
                secrets.choice(group)
            )

        remaining = length - len(password)

        for _ in range(max(0, remaining)):
            password.append(
                secrets.choice(characters)
            )

        # Secure shuffle
        for i in range(len(password) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password[i], password[j] = (
                password[j],
                password[i]
            )

        return "".join(password[:length])

    def generate_password(self):

        try:
            length = int(self.length_var.get())

            password = self.generate_secure_password(
                length
            )

            self.password_var.set(password)

            self.update_strength(password)
            self.save_to_history(password)

            self.status_var.set(
                "Secure password generated successfully."
            )

        except ValueError as error:
            messagebox.showwarning(
                "Invalid Settings",
                str(error)
            )

    # ========================================================
    # STRENGTH
    # ========================================================

    def calculate_entropy(self, password):

        charset = 0

        if any(c.islower() for c in password):
            charset += 26

        if any(c.isupper() for c in password):
            charset += 26

        if any(c.isdigit() for c in password):
            charset += 10

        if any(c in string.punctuation for c in password):
            charset += len(string.punctuation)

        if charset == 0:
            return 0

        return len(password) * math.log2(charset)

    def calculate_strength(self, password):

        if not password:
            return "Ready", 0

        entropy = self.calculate_entropy(password)

        if entropy < 28:
            return "Very Weak", 20

        if entropy < 36:
            return "Weak", 40

        if entropy < 60:
            return "Moderate", 60

        if entropy < 80:
            return "Strong", 80

        return "Very Strong", 100

    def update_strength(self, password=None):

        if password is None:
            password = self.password_var.get()

        strength, score = self.calculate_strength(
            password
        )

        self.strength_var.set(
            f"Strength: {strength}"
        )

        self.strength_bar["value"] = score

        entropy = self.calculate_entropy(
            password
        )

        self.entropy_var.set(
            f"Entropy: {entropy:.1f} bits"
        )

        self.update_charset_info()

    # ========================================================
    # UI HELPERS
    # ========================================================

    def update_length(self, value):

        length = int(float(value))

        self.length_var.set(length)
        self.length_label.config(
            text=str(length)
        )

    def update_charset_info(self):

        charset = self.get_character_set()

        self.charset_var.set(
            f"Character set: {len(charset)} characters"
        )

    def toggle_password_visibility(self):

        if self.show_password_var.get():
            self.password_entry.config(
                show=""
            )
        else:
            self.password_entry.config(
                show="•"
            )

    def copy_password(self):

        password = self.password_var.get()

        if not password:
            messagebox.showinfo(
                "Copy Password",
                "Generate a password first."
            )
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()

        self.status_var.set(
            "Password copied to clipboard."
        )

    def clear_password(self):

        self.password_var.set("")
        self.strength_var.set("Ready")
        self.strength_bar["value"] = 0
        self.entropy_var.set(
            "Entropy: -- bits"
        )

        self.status_var.set(
            "Password cleared."
        )

    def toggle_theme(self):

        self.dark_mode = not self.dark_mode

        # Rebuild widgets so colors update
        for widget in self.root.winfo_children():
            widget.destroy()

        self.setup_style()
        self.build_ui()

        self.status_var.set(
            "Theme changed."
        )

    # ========================================================
    # PRESETS
    # ========================================================

    def preset_pin(self):

        self.length_scale.set(6)
        self.length_var.set(6)

        self.upper_var.set(False)
        self.lower_var.set(False)
        self.number_var.set(True)
        self.symbol_var.set(False)

        self.custom_var.set("")

        self.length_label.config(text="6")
        self.update_charset_info()

        self.status_var.set(
            "PIN preset selected."
        )

    def preset_strong(self):

        self.length_scale.set(16)
        self.length_var.set(16)

        self.upper_var.set(True)
        self.lower_var.set(True)
        self.number_var.set(True)
        self.symbol_var.set(True)

        self.custom_var.set("")

        self.length_label.config(text="16")
        self.update_charset_info()

        self.status_var.set(
            "Strong preset selected."
        )

    def preset_ultra(self):

        self.length_scale.set(32)
        self.length_var.set(32)

        self.upper_var.set(True)
        self.lower_var.set(True)
        self.number_var.set(True)
        self.symbol_var.set(True)
        self.exclude_var.set(True)

        self.custom_var.set("")

        self.length_label.config(text="32")
        self.update_charset_info()

        self.status_var.set(
            "Ultra Secure preset selected."
        )

    # ========================================================
    # MULTIPLE PASSWORDS
    # ========================================================

    def generate_multiple(self):

        try:
            count = int(
                self.multiple_spin.get()
            )

            if count < 1 or count > 20:
                raise ValueError

            length = int(
                self.length_var.get()
            )

            passwords = []

            for _ in range(count):
                password = self.generate_secure_password(
                    length
                )
                passwords.append(password)
                self.save_to_history(password)

            self.show_multiple_passwords(
                passwords
            )

        except ValueError:
            messagebox.showwarning(
                "Invalid Number",
                "Enter a number between 1 and 20."
            )

    def show_multiple_passwords(
        self,
        passwords
    ):

        window = tk.Toplevel(self.root)

        window.title(
            "Generated Passwords"
        )

        window.geometry(
            "700x500"
        )

        text = tk.Text(
            window,
            font=("Consolas", 12),
            wrap="none"
        )

        text.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        for index, password in enumerate(
            passwords,
            start=1
        ):
            text.insert(
                "end",
                f"{index:02d}. {password}\n"
            )

        ttk.Button(
            window,
            text="Copy All",
            command=lambda: self.copy_multiple(
                passwords
            )
        ).pack(
            pady=(0, 15)
        )

    def copy_multiple(self, passwords):

        text = "\n".join(passwords)

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

        self.status_var.set(
            "Multiple passwords copied."
        )

    # ========================================================
    # HISTORY
    # ========================================================

    def save_to_history(self, password):

        strength, _ = self.calculate_strength(
            password
        )

        record = {
            "date": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "password": password,
            "length": len(password),
            "strength": strength
        }

        self.history.insert(
            0,
            record
        )

        # Keep last 100 records
        self.history = self.history[:100]

        self.save_history_file()

        if hasattr(
            self,
            "history_tree"
        ):
            self.refresh_history()

    def load_history(self):

        if not os.path.exists(
            HISTORY_FILE
        ):
            return

        try:
            with open(
                HISTORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if isinstance(data, list):
                self.history = data

        except (
            OSError,
            json.JSONDecodeError
        ):
            self.history = []

    def save_history_file(self):

        try:
            with open(
                HISTORY_FILE,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    self.history,
                    file,
                    indent=4
                )

        except OSError:
            pass

    def refresh_history(self):

        if not hasattr(
            self,
            "history_tree"
        ):
            return

        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for record in self.history:
            self.history_tree.insert(
                "",
                "end",
                values=(
                    record.get("date", ""),
                    record.get("password", ""),
                    record.get("length", ""),
                    record.get("strength", "")
                )
            )

    def copy_selected_history(self):

        selected = self.history_tree.selection()

        if not selected:
            messagebox.showinfo(
                "History",
                "Select a password first."
            )
            return

        item = self.history_tree.item(
            selected[0]
        )

        password = item["values"][1]

        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()

        self.status_var.set(
            "Selected password copied."
        )

    def delete_selected_history(self):

        selected = self.history_tree.selection()

        if not selected:
            messagebox.showinfo(
                "History",
                "Select a record first."
            )
            return

        item_id = selected[0]
        values = self.history_tree.item(
            item_id
        )["values"]

        password = values[1]
        date = values[0]

        self.history = [
            record
            for record in self.history
            if not (
                record.get("password") == password
                and record.get("date") == date
            )
        ]

        self.save_history_file()
        self.refresh_history()

        self.status_var.set(
            "Selected record deleted."
        )

    def clear_history(self):

        if not self.history:
            return

        confirm = messagebox.askyesno(
            "Clear History",
            "Delete all password history?"
        )

        if not confirm:
            return

        self.history.clear()

        self.save_history_file()
        self.refresh_history()

        self.status_var.set(
            "Password history cleared."
        )

    # ========================================================
    # EXPORT
    # ========================================================

    def export_txt(self):

        if not self.history:
            messagebox.showinfo(
                "Export",
                "There is no history to export."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save Password History",
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt")
            ]
        )

        if not path:
            return

        try:
            with open(
                path,
                "w",
                encoding="utf-8"
            ) as file:

                for record in self.history:
                    file.write(
                        f"Date: {record['date']}\n"
                        f"Password: {record['password']}\n"
                        f"Length: {record['length']}\n"
                        f"Strength: {record['strength']}\n"
                        f"{'-' * 60}\n"
                    )

            messagebox.showinfo(
                "Export Complete",
                "Password history exported successfully."
            )

        except OSError as error:
            messagebox.showerror(
                "Export Error",
                str(error)
            )

    def export_csv(self):

        if not self.history:
            messagebox.showinfo(
                "Export",
                "There is no history to export."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save Password History",
            defaultextension=".csv",
            filetypes=[
                ("CSV Files", "*.csv")
            ]
        )

        if not path:
            return

        try:
            with open(
                path,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "date",
                        "password",
                        "length",
                        "strength"
                    ]
                )

                writer.writeheader()
                writer.writerows(
                    self.history
                )

            messagebox.showinfo(
                "Export Complete",
                "Password history exported successfully."
            )

        except OSError as error:
            messagebox.showerror(
                "Export Error",
                str(error)
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = PasswordGeneratorApp(
        root
    )

    root.mainloop()
