import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

# ===== DB =====
conn = sqlite3.connect("Kosmetologija.db")
cursor = conn.cursor()

# ===== WINDOW =====
window = tk.Tk()
window.title("Kosmetoloģijas salona lietotne")
window.geometry("520x560")
window.configure(bg="#F7EFEA")  # bēšs fons

# ===== STYLE =====
style = ttk.Style()
style.theme_use("default")

style.configure("TLabel",
    background="#F7EFEA",
    foreground="#5A4A42",
    font=("Segoe UI", 10)
)

style.configure("Title.TLabel",
    font=("Segoe UI", 18, "bold"),
    foreground="#C48B9F"  # rozā akcents
)

style.configure("TEntry",
    font=("Segoe UI", 10),
    padding=6
)

style.configure("TButton",
    font=("Segoe UI", 10, "bold"),
    padding=8,
    background="#C48B9F",
    foreground="#5A4A42"
)

style.map("TButton",
    background=[("active", "#D9A6B5")]
)

# ===== TITLE =====
ttk.Label(
    window,
    text="🌸 Kosmetoloģijas klientu pieraksts",
    style="Title.TLabel"
).pack(pady=15)

# ===== CARD =====
card = tk.Frame(window, bg="#FFF8F5", bd=0)
card.pack(padx=20, pady=10, fill="both", expand=True)

def label(text):
    ttk.Label(card, text=text, background="#FFF8F5").pack(anchor="w", padx=20, pady=(12, 4))

def entry(var):
    ttk.Entry(card, textvariable=var, width=40).pack(anchor="w", padx=20)

# ===== CLIENT =====
label("Klienta vārds")
name_var = tk.StringVar()
entry(name_var)

label("Klienta uzvārds")
surname_var = tk.StringVar()
entry(surname_var)

label("Tālrunis")
phone_var = tk.StringVar()
entry(phone_var)

# ===== PROCEDURE =====
label("Procedūras veids")
procedure_var = tk.StringVar()

proc_frame = tk.Frame(card, bg="#FFF8F5")
proc_frame.pack(anchor="w", padx=20)

for p in ["Sejas tīrīšana", "Pīlings", "Masāža", "Kopšana"]:
    ttk.Radiobutton(
        proc_frame,
        text=p,
        variable=procedure_var,
        value=p
    ).pack(side="left", padx=5)

# ===== DATE =====
label("Vizītes datums")
date_var = tk.StringVar()
entry(date_var)

# ===== SAVE =====
def save_visit():
    if not all([name_var.get(), surname_var.get(), phone_var.get(), procedure_var.get(), date_var.get()]):
        messagebox.showerror("Kļūda", "Lūdzu aizpildiet visus laukus")
        return

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vizites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vards TEXT,
            uzvards TEXT,
            talrunis TEXT,
            procedura TEXT,
            datums TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO vizites (vards, uzvards, talrunis, procedura, datums)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name_var.get(),
        surname_var.get(),
        phone_var.get(),
        procedure_var.get(),
        date_var.get()
    ))

    conn.commit()
    messagebox.showinfo("Saglabāts", "✨ Vizīte veiksmīgi pierakstīta")

# ===== SHOW =====
def show_visits():
    cursor.execute("SELECT vards, uzvards, procedura, datums FROM vizites")
    rows = cursor.fetchall()

    text = ""
    for r in rows:
        text += f"👩 {r[0]} {r[1]}\n💆 {r[2]}\n📅 {r[3]}\n\n"

    messagebox.showinfo("Vizītes", text or "Nav pierakstu")

# ===== BUTTONS =====
btn_frame = tk.Frame(window, bg="#F7EFEA")
btn_frame.pack(pady=20)

ttk.Button(
    btn_frame,
    text="💾 SAGLABĀT VIZĪTI",
    command=save_visit
).pack(side="left", padx=10)

ttk.Button(
    btn_frame,
    text="📋 SKATĪT VIZĪTES",
    command=show_visits
).pack(side="left", padx=10)

window.mainloop()
conn.close()
