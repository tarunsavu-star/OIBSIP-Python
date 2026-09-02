# 🔐 Advanced Random Password Generator

An advanced desktop-based Random Password Generator developed using Python and Tkinter as part of the Oasis Infobyte Python Programming Internship.

## 📌 About the Project

This application generates strong and secure random passwords using Python's `secrets` module.

It provides customizable password generation, strength analysis, entropy estimation, password history, export options, presets, and a professional graphical user interface.

---

## 🚀 Features

### 🔑 Password Generation
- Secure random password generation
- Password length from 4 to 128 characters
- Uppercase letters
- Lowercase letters
- Numbers
- Special characters
- Custom characters
- Exclude ambiguous characters
- Cryptographically secure generation using Python `secrets`

### 📊 Password Strength Analysis
- Very Weak
- Weak
- Moderate
- Strong
- Very Strong
- Visual strength meter
- Entropy estimation in bits
- Character-set size information

### ⚡ Quick Presets
- PIN
- Strong
- Ultra Secure

### 📋 Password Management
- Copy password to clipboard
- Show / Hide password
- Clear generated password
- Generate again
- Generate multiple passwords at once
- Copy multiple passwords

### 🗂️ Password History
- Automatically saves generated passwords locally
- Displays generation date and time
- Displays password length
- Displays password strength
- Copy selected password
- Delete selected record
- Clear complete history

### 📤 Export
- Export password history to TXT
- Export password history to CSV

### 🎨 User Interface
- Professional Tkinter GUI
- Light and dark theme
- Organized tabs
- Generator dashboard
- History management
- Security information section
- Responsive application layout
- Input validation
- Error handling

---

## 🛠️ Technologies Used

- Python
- Tkinter
- Secrets
- String
- Math
- JSON
- CSV
- OS
- DateTime

---

## 📁 Project Structure

```text
Task3_Password_Generator/
│
├── password_generator.py
├── README.md
└── password_history.json
