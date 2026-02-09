import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
import os

# ---- PIESLĒGŠANĀS DATUBĀZEI ----
# Ceļš uz datubāzes failu (tiks izveidots pašreizējā mapē)
db_path = os.path.join(os.getcwd(), "Kosmetologija.db")

# Pieslēgšanās SQLite datubāzei
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ---- TABULU IZVEIDE (ja tās vēl neeksistē) ----

# Klientu tabula
cursor.execute("""CREATE TABLE IF NOT EXISTS klienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- unikāls klienta ID
    vards TEXT NOT NULL,                    -- vārds
    uzvards TEXT NOT NULL,                  -- uzvārds
    talrunis TEXT NOT NULL UNIQUE           -- telefons (unikāls)
)""")

# Procedūru tabula
cursor.execute("""CREATE TABLE IF NOT EXISTS proceduras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- procedūras ID
    veids TEXT NOT NULL UNIQUE              -- procedūras nosaukums
)""")

# Vizīšu tabula
cursor.execute("""CREATE TABLE IF NOT EXISTS vizites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- vizītes ID
    klienta_id INTEGER NOT NULL,            -- saite uz klientu
    procedura_id INTEGER NOT NULL,          -- saite uz procedūru
    datums TEXT NOT NULL,                   -- vizītes datums
    FOREIGN KEY (klienta_id) REFERENCES klienti(id),
    FOREIGN KEY (procedura_id) REFERENCES proceduras(id)
)""")

# Produktu tabula (pagaidām netiek izmantota interfeisā)
cursor.execute("""CREATE TABLE IF NOT EXISTS produkti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums TEXT NOT NULL,   -- produkta nosaukums
    pievienots TEXT NOT NULL,  -- pievienošanas datums
    cena REAL NOT NULL         -- cena
)""")

conn.commit()

# ---- GALVENĀ LOGA IZVEIDE ----
window = tk.Tk()
window.title("Kosmetoloģijas salona lietotne")  # loga nosaukums
window.geometry("520x600")                       # loga izmērs
window.configure(bg="#F7EFEA")                   # fona krāsa

# ---- STILI ELEMENTIEM ----
style = ttk.Style()
style.theme_use("default")

style.configure("TLabel", background="#F7EFEA", foreground="#5A4A42", font=("Segoe UI", 10))
style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground="#C48B9F")
style.configure("TEntry", font=("Segoe UI", 10), padding=6)
style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8,
                background="#C48B9F", foreground="#5A4A42")
style.map("TButton", background=[("active", "#D9A6B5")])

# Lietotnes virsraksts
ttk.Label(window, text="🌸 Kosmetoloģijas klientu pieraksts", style="Title.TLabel").pack(pady=15)

# ---- KARTĪTE AR FORMU ----
card = tk.Frame(window, bg="#FFF8F5")
card.pack(padx=20, pady=10, fill="both", expand=True)

# Funkcija lauka nosaukuma izveidei
def label(text):
    ttk.Label(card, text=text, background="#FFF8F5").pack(anchor="w", padx=20, pady=(12, 4))

# Funkcija ievades lauka izveidei
def entry(var):
    ttk.Entry(card, textvariable=var, width=40).pack(anchor="w", padx=20)

# ---- IEVADES LAUKI ----

label("Klienta vārds")
name_var = tk.StringVar()   # mainīgais vārdam
entry(name_var)

label("Klienta uzvārds")
surname_var = tk.StringVar()  # mainīgais uzvārdam
entry(surname_var)

label("Tālrunis")
phone_var = tk.StringVar()    # mainīgais telefonam
entry(phone_var)

# ---- PROCEDŪRAS IZVĒLE ----
label("Procedūras veids")
procedure_var = tk.StringVar()

proc_frame = tk.Frame(card, bg="#FFF8F5")
proc_frame.pack(anchor="w", padx=20)

procedures_list = ["Sejas tīrīšana", "Pīlings", "Masāža", "Kopšana"]

# Radio pogas procedūras izvēlei
for p in procedures_list:
    ttk.Radiobutton(proc_frame, text=p, variable=procedure_var, value=p).pack(side="left", padx=5)

# ---- VIZĪTES DATUMS ----
label("Vizītes datums (DD.MM.GGGG)")
date_var = tk.StringVar()
entry(date_var)

# ---- IEVADES PĀRBAUDE ----
def validate_inputs():

    # Pārbaude: vai visi lauki ir aizpildīti
    if not all([name_var.get(), surname_var.get(), phone_var.get(), procedure_var.get(), date_var.get()]):
        messagebox.showerror("Kļūda", "Lūdzu aizpildiet visus laukus")
        return False

    # Tikai burti vārdā
    if not name_var.get().isalpha():
        messagebox.showerror("Kļūda", "Vārds var saturēt tikai burtus")
        return False

    # Tikai burti uzvārdā
    if not surname_var.get().isalpha():
        messagebox.showerror("Kļūda", "Uzvārds var saturēt tikai burtus")
        return False

    # Tikai cipari telefonā
    if not phone_var.get().isdigit():
        messagebox.showerror("Kļūda", "Tālrunis var saturēt tikai ciparus")
        return False

    # Datuma formāta pārbaude DD.MM.GGGG
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_var.get()):
        messagebox.showerror("Kļūda", "Datuma formātam jābūt DD.MM.GGGG")
        return False

    return True

# ---- VIZĪTES SAGLABĀŠANA ----
def save_visit():

    # Vispirms pārbaudām ievadi
    if not validate_inputs():
        return

    try:
        # Pārbaudām, vai klients ar šādu telefonu jau eksistē
        cursor.execute("SELECT id FROM klienti WHERE talrunis=?", (phone_var.get(),))
        klient = cursor.fetchone()

        if klient:
            klienta_id = klient[0]
        else:
            # Ja nē — izveidojam jaunu klientu
            cursor.execute(
                "INSERT INTO klienti (vards, uzvards, talrunis) VALUES (?, ?, ?)",
                (name_var.get(), surname_var.get(), phone_var.get())
            )
            klienta_id = cursor.lastrowid

        # Pārbaudām procedūru
        cursor.execute("SELECT id FROM proceduras WHERE veids=?", (procedure_var.get(),))
        proc = cursor.fetchone()

        if proc:
            procedura_id = proc[0]
        else:
            # Pievienojam jaunu procedūru
            cursor.execute("INSERT INTO proceduras (veids) VALUES (?)", (procedure_var.get(),))
            procedura_id = cursor.lastrowid

        # Pievienojam vizītes ierakstu
        cursor.execute(
            "INSERT INTO vizites (klienta_id, procedura_id, datums) VALUES (?, ?, ?)",
            (klienta_id, procedura_id, date_var.get())
        )

        conn.commit()

        messagebox.showinfo("Saglabāts", "✨ Vizīte veiksmīgi pierakstīta")

        # Formas notīrīšana
        name_var.set("")
        surname_var.set("")
        phone_var.set("")
        procedure_var.set("")
        date_var.set("")

    except sqlite3.IntegrityError as e:
        messagebox.showerror("Kļūda DB", f"Datubāzes kļūda: {e}")

# ---- LOGS AR KLIENTU SARAKSTU ----
def show_clients():

    win = tk.Toplevel(window)
    win.title("Visi klienti")
    win.geometry("400x400")
    win.configure(bg="#F7EFEA")

    ttk.Label(win, text="📋 Visi klienti", style="Title.TLabel").pack(pady=10)

    columns = ("vards", "uzvards", "talrunis")

    tree = ttk.Treeview(win, columns=columns, show="headings", height=15)
    tree.pack(padx=20, pady=10, fill="both", expand=True)

    # Tabulas virsraksti
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=100, anchor="center")

    # Klientu ielāde no datubāzes
    cursor.execute("SELECT vards, uzvards, talrunis FROM klienti ORDER BY vards")

    for r in cursor.fetchall():
        tree.insert("", "end", values=r)

    ttk.Button(win, text="Aizvērt", command=win.destroy).pack(pady=10)

# ---- LOGS AR VIZĪŠU SARAKSTU ----
def show_visits():

    win = tk.Toplevel(window)
    win.title("Visas vizītes")
    win.geometry("500x400")
    win.configure(bg="#F7EFEA")

    ttk.Label(win, text="📋 Visas vizītes", style="Title.TLabel").pack(pady=10)

    columns = ("vards", "uzvards", "procedura", "datums")

    tree = ttk.Treeview(win, columns=columns, show="headings", height=15)
    tree.pack(padx=20, pady=10, fill="both", expand=True)

    # Virsraksti
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=100, anchor="center")

    # SQL JOIN — apvienojam 3 tabulas
    cursor.execute("""
        SELECT k.vards, k.uzvards, p.veids, v.datums
        FROM vizites v
        JOIN klienti k ON v.klienta_id = k.id
        JOIN proceduras p ON v.procedura_id = p.id
        ORDER BY v.datums
    """)

    for r in cursor.fetchall():
        tree.insert("", "end", values=r)

    ttk.Button(win, text="Aizvērt", command=win.destroy).pack(pady=10)

# ---- POGAS GALVENAJĀ LOGĀ ----
btn_frame = tk.Frame(window, bg="#F7EFEA")
btn_frame.pack(pady=20)

ttk.Button(btn_frame, text="💾 SAGLABĀT VIZĪTI", command=save_visit).pack(side="left", padx=10)
ttk.Button(btn_frame, text="📋 SKATĪT VIZĪTES", command=show_visits).pack(side="left", padx=10)
ttk.Button(btn_frame, text="👥 SKATĪT KLIENTUS", command=show_clients).pack(side="left", padx=10)

# ---- LIETOTNES PALAIŠANA ----
window.mainloop()

# Datubāzes savienojuma aizvēršana pēc loga aizvēršanas
conn.close()
