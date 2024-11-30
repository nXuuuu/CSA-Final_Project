import tkinter
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from docxtpl import DocxTemplate
import datetime
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def apply_azure_theme(window):
    style = ttk.Style(window)
    window.tk.call("source", r"D:\Code Aupp\invoiceproj\MyTheme\azure.tcl") 
    style.theme_use("azure-light") 



# --- Database Setup ---
def setup_database():
    conn = sqlite3.connect("admin_accounts.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

setup_database()

# --- Dynamic Form Switching ---
def load_login_form():
    clear_window(login_window)
    tkinter.Label(login_window, text="Admin Login", font=('Aptos Black', 25)).pack(pady=(150,40))
    tkinter.Label(login_window, text="Username", font=('Aptos Black', 20)).pack(pady=20)
    global login_username_entry, login_password_entry
    login_username_entry = tkinter.Entry(login_window, width = 15, font = ('Aptos Black', 20))
    login_username_entry.pack(pady=5)

    tkinter.Label(login_window, text="Password", font=('Aptos Black', 20)).pack(pady=25)
    login_password_entry = tkinter.Entry(login_window, show="*", width = 15, font = ('Aptos Black', 20))
    login_password_entry.pack(pady=5)   

    tkinter.Button(login_window, width= 9, height= 2 ,text="Login", font=('Aptos Black', 14), command=login).pack(pady=10)
    tkinter.Button(login_window, width= 9, height= 2 , text="Register", font=('Aptos Black', 14), command=register).pack(pady=5)

def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()

# --- Registration Form ---
def register():
    def register_user():
        username = reg_username_entry.get()
        password = reg_password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        try:
            conn = sqlite3.connect("admin_accounts.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Registration successful! Please log in.")
            load_login_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
            conn.close()

    clear_window(login_window)
    tkinter.Label(login_window, text="Register Admin", font=('Aptos Black', 25)).pack(pady=(150,40))
    tkinter.Label(login_window, text="Username", font=('Aptos Black', 20)).pack(pady=20)
    global reg_username_entry, reg_password_entry
    reg_username_entry = tkinter.Entry(login_window, width = 15, font = ('Aptos Black', 20))
    reg_username_entry.pack(pady=5)

    tkinter.Label(login_window, text="Password",  font=('Aptos Black', 20)).pack(pady=25)
    reg_password_entry = tkinter.Entry(login_window, show="*", width = 15, font = ('Aptos Black', 20))
    reg_password_entry.pack(pady=5)

    tkinter.Button(login_window, width= 9, height= 2 ,text="Register", font=('Aptos Black', 14), command=register_user).pack(pady=10)
    tkinter.Button(login_window, width= 12, height= 2 ,text="Back to Login", font=('Aptos Black', 14), command=load_login_form).pack(pady=5)

# --- Login Verification ---
def login():
    username = login_username_entry.get()
    password = login_password_entry.get()
    conn = sqlite3.connect("admin_accounts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
    account = cursor.fetchone()
    conn.close()
    if account:
        global logged_in_admin
        logged_in_admin = username  # Store the logged-in admin's username
        login_window.destroy()
        launch_main_app()
    else:
        messagebox.showerror("Error", "Invalid username or password.")


# --- Main Invoice Application ---
def launch_main_app():
    def clear_item():
        qty_spinbox.delete(0, tkinter.END)
        qty_spinbox.insert(0, "1")
        desc_entry.delete(0, tkinter.END)
        price_spinbox.delete(0, tkinter.END)
        price_spinbox.insert(0, "0.0")

    def add_item():
        try:
            qty = int(qty_spinbox.get())
            desc = desc_entry.get()
            price = float(price_spinbox.get())
            if qty <= 0 or price < 0:
                raise ValueError
            line_total = round(qty * price, 2)
            invoice_item = [qty, desc, price, line_total]
            tree.insert('', 0, values=invoice_item)
            clear_item()
            invoice_list.append(invoice_item)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for Quantity and Price.")

    def new_invoice():
        first_name_entry.delete(0, tkinter.END)
        last_name_entry.delete(0, tkinter.END)
        phone_entry.delete(0, tkinter.END)
        clear_item()
        tree.delete(*tree.get_children())
        invoice_list.clear()

    def generate_invoice():
        doc = DocxTemplate(r"D:\Code Aupp\invoiceproj\pyinvoice.docx")
        name = first_name_entry.get() + " " + last_name_entry.get()
        phone = phone_entry.get()
        subtotal = sum(item[3] for item in invoice_list)
        total = subtotal
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        doc.render({
            "admin_name": logged_in_admin,
            "name": name,
            "phone": phone,
            "invoice_list": invoice_list,
            "subtotal": subtotal,
            "total": total,
            "date": current_date
        })

        doc_name = "new_invoice_" + name.replace(" ", "_") + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".docx"
        doc.save(doc_name)
        messagebox.showinfo("Invoice Complete", "Invoice has been saved successfully.")
        new_invoice()

    invoice_list = []

    # --- Main App UI ---
    main_window = tkinter.Tk()
    main_window.state("zoomed")
    main_window.title("Invoice Generator Form")
    apply_azure_theme(main_window)

    frame = tkinter.Frame(main_window)
    frame.pack(padx=20, pady=200)

    tkinter.Label(frame, text="First Name", font = 15).grid(row=0, column=0)
    tkinter.Label(frame, text="Last Name", font = 15).grid(row=0, column=1)
    first_name_entry = tkinter.Entry(frame, width = 25)
    last_name_entry = tkinter.Entry(frame, width= 25)
    first_name_entry.grid(row=1, column=0)
    last_name_entry.grid(row=1, column=1)

    tkinter.Label(frame, text="Phone", font = 15).grid(row=0, column=2)
    phone_entry = tkinter.Entry(frame, width= 25)
    phone_entry.grid(row=1, column=2)

    tkinter.Label(frame, text="Qty", font = 15).grid(row=2, column=0)
    qty_spinbox = tkinter.Spinbox(frame, from_=1, to=100, width= 23)
    qty_spinbox.grid(row=3, column=0)

    tkinter.Label(frame, text="Description", font = 15).grid(row=2, column=1)
    desc_entry = tkinter.Entry(frame, width= 25)
    desc_entry.grid(row=3, column=1)

    tkinter.Label(frame, text="Unit Price", font = 15).grid(row=2, column=2)
    price_spinbox = tkinter.Spinbox(frame, from_=0.0, to=500, increment=0.5, width= 23)
    price_spinbox.grid(row=3, column=2)

    tkinter.Button(frame, text="Add Item", font = 12, command=add_item).grid(row=4, column=2, pady=5)

    columns = ('qty', 'desc', 'price', 'total')
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    tree.heading('qty', text='Qty')
    tree.heading('desc', text='Description')
    tree.heading('price', text='Unit Price')
    tree.heading('total', text="Total")
    tree.grid(row=5, column=0, columnspan=3, padx=20, pady=10)

    tkinter.Button(frame, text="Generate Invoice", font = 15, command=generate_invoice).grid(row=6, column=0, columnspan=3, sticky="news", padx=20, pady=5)
    tkinter.Button(frame, text="New Invoice", font = 15, command=new_invoice).grid(row=7, column=0, columnspan=3, sticky="news", padx=20, pady=5)

    main_window.mainloop()

# --- Login UI ---
logged_in_admin = None  # Variable to store the logged-in admin's username
login_window = tkinter.Tk()
login_window.state('zoomed')
login_window.title("Admin Login")
apply_azure_theme(login_window)
load_login_form()
login_window.mainloop()


