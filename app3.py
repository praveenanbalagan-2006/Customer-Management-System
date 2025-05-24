import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os
from PIL import Image, ImageTk  # type: ignore

CUSTOMER_CSV = "pending.csv"
VENDOR_CSV = "orders_export.csv"

# ----- LOGIN WINDOW -----
def show_login_window():
    login_win = tk.Tk()
    login_win.title("Login")
    login_win.geometry("300x200")
    login_win.configure(bg="lightblue")

    tk.Label(login_win, text="Username", bg="lightblue", font=("Arial", 12)).pack(pady=5)
    username_entry = tk.Entry(login_win)
    username_entry.pack(pady=5)

    tk.Label(login_win, text="Password", bg="lightblue", font=("Arial", 12)).pack(pady=5)
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack(pady=5)

    def validate_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if username == "admin" and password == "1234":
            login_win.destroy()
            open_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    tk.Button(login_win, text="Login", command=validate_login,
              bg="darkblue", fg="white", font=("Arial", 11)).pack(pady=15)

    login_win.mainloop()

# ----- MAIN APP CLASS -----
class TodaysPlanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Today's Plan - Delivery Status")
        self.root.geometry("1200x600")
        self.root.configure(bg='darkblue')

        # Header
        tk.Label(root, text="Today's Plan - Vendor Delivered Orders for Dispatch",
                 font=("Arial", 22, "bold"), bg='#C62300', fg='white').pack(fill='x')

        # Load logo image if available
        image_path = "sofa corner logo new.png"
        if os.path.exists(image_path):
            original_image = Image.open(image_path)
            resized_image = original_image.resize((150, 100))
            tk_image = ImageTk.PhotoImage(resized_image)
            image_label = tk.Label(root, image=tk_image)
            image_label.image = tk_image
            image_label.pack(pady=10)

        # Search box
        search_frame = tk.Frame(root, bg='darkblue')
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search by Customer Name:", bg='darkblue', fg='white',
                 font=("Arial", 13)).pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side='left')
        tk.Button(search_frame, text="Search", command=self.search_customer,
                  bg='darkblue', fg='white', font=('Arial', 11, 'bold')).pack(side='left', padx=10)

        # Treeview columns
        columns = ['Customer ID', 'Product ID', 'Customer Name', 'Phone Number', 'Address',
                   'Order Date', 'Product Name', 'Quantity', 'Total Amount', 'Vendor Delivered Date']

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="lightblue",
                        fieldbackground="lightblue",
                        foreground="black",
                        font=('Arial', 11))
        style.configure("Treeview.Heading",
                        font=('Arial', 12, 'bold'),
                        background='#C62300',
                        foreground='white')
        style.map("Treeview.Heading",
                  background=[('active', '#C62300')],
                  foreground=[('active', 'white')])

        tree_frame = tk.Frame(root, bg='darkblue', bd=2, relief='ridge')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style="Treeview")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=120)
        self.tree.pack(fill='both', expand=True)

        # Footer Button
        tk.Button(root, text="Load Today's Plan", command=self.load_todays_plan,
                  bg='#C62300', fg='white', font=("Arial", 13, "bold")).pack(pady=5, fill='x')

    def load_todays_plan(self):
        existing_entries = set()
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if values:
                existing_entries.add((values[0], values[1]))  # (Customer ID, Product ID)

        if not os.path.exists(CUSTOMER_CSV) or not os.path.exists(VENDOR_CSV):
            messagebox.showerror("File Error", "Customer or Vendor CSV file not found.")
            return

        today_str = datetime.now().strftime("%Y-%m-%d")
        vendor_delivered = set()
        vendor_dates = {}

        # Step 1: Collect vendor-delivered orders
        with open(VENDOR_CSV, newline='', encoding='utf-8') as vf:
            reader = csv.DictReader(vf)
            for row in reader:
                if row.get('Status', '').strip().lower() == 'delivered':
                    cust_id = row['Customer ID'].strip()
                    prod_id = row['Product ID'].strip()
                    delivered_date = row.get('Vendor Delivered Date', '').strip()
                    vendor_delivered.add((cust_id, prod_id))
                    vendor_dates[(cust_id, prod_id)] = delivered_date

        # Step 2: Build today's plan from pending.csv based on vendor delivery date
        updated_rows = []
        todays_plan = []

        with open(CUSTOMER_CSV, newline='', encoding='utf-8') as cf:
            reader = list(csv.DictReader(cf))
            for row in reader:
                cust_id = row['customer_id'].strip()
                prod_id = row['product_id'].strip()
                key = (cust_id, prod_id)
                delivered_date = vendor_dates.get(key, '')

                if key in vendor_delivered and delivered_date == today_str:
                    if key not in existing_entries:
                        todays_plan.append({
                            'Customer ID': cust_id,
                            'Product ID': prod_id,
                            'Customer Name': row['name'].strip(),
                            'Phone Number': row['phone_number'].strip(),
                            'Address': row['address'].strip(),
                            'Order Date': row['order_date'].strip(),
                            'Product Name': row['order'].strip(),
                            'Quantity': '1',
                            'Total Amount': float(row['total_amount']) if row['total_amount'] else 0,
                            'Vendor Delivered Date': delivered_date
                        })
                    # Don't keep it in pending.csv
                else:
                    updated_rows.append(row)

        # Step 3: Update pending.csv to remove completed dispatches
        if updated_rows:
            with open(CUSTOMER_CSV, 'w', newline='', encoding='utf-8') as cf:
                writer = csv.DictWriter(cf, fieldnames=updated_rows[0].keys())
                writer.writeheader()
                writer.writerows(updated_rows)

        # Step 4: Display Today's Plan sorted by Total Amount
        if todays_plan:
            todays_plan.sort(key=lambda x: x['Total Amount'], reverse=True)
            for plan in todays_plan:
                self.tree.insert('', 'end', values=(
                    plan['Customer ID'], plan['Product ID'], plan['Customer Name'],
                    plan['Phone Number'], plan['Address'], plan['Order Date'],
                    plan['Product Name'], plan['Quantity'],
                    f"{plan['Total Amount']:.2f}", plan['Vendor Delivered Date']
                ))
        else:
            self.show_custom_messagebox("No new vendor-delivered orders for today.")

    def show_custom_messagebox(self, message):
        top = tk.Toplevel(self.root)
        top.title("Info")
        top.configure(bg='lightblue')
        top.geometry("300x120")
        tk.Label(top, text=message, bg='lightblue', fg='black', font=('Arial', 12)).pack(pady=20)
        tk.Button(top, text="OK", command=top.destroy,
                  bg='darkblue', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)

    def search_customer(self):
        name_to_search = self.search_var.get().strip().lower()
        if not name_to_search:
            self.show_custom_messagebox("Enter a customer name to search.")
            return

        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if values and name_to_search in values[2].lower():  # Customer Name at index 2
                self.tree.selection_set(item)
                self.tree.see(item)
                return

        self.show_custom_messagebox("Customer not found in today's plan.")

def open_main_app():
    root = tk.Tk()
    app = TodaysPlanApp(root)
    root.mainloop()

if __name__ == "__main__":
    show_login_window()
