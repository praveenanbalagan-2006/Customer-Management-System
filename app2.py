import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry # type: ignore
import csv
from PIL import Image, ImageTk # type: ignore
import os

CSV_FILE = "orders_export.csv"

# Custom draggable message box
def custom_message(parent, title, message):
    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry("300x150")
    win.resizable(False, False)
    win.grab_set()

    # Load and display logo image if exists
    image_path = "sofa corner logo new.png"
    if os.path.exists(image_path):
        original_image = Image.open(image_path)
        resized_image = original_image.resize((250, 200))
        tk_image = ImageTk.PhotoImage(resized_image)
        image_label = tk.Label(win, image=tk_image)
        image_label.image = tk_image  # Keep reference to avoid GC
        image_label.pack(pady=10)

    # Make window draggable
    def start_move(event):
        win.x = event.x
        win.y = event.y
    def do_move(event):
        x = win.winfo_pointerx() - win.x
        y = win.winfo_pointery() - win.y
        win.geometry(f"+{x}+{y}")

    win.bind("<Button-1>", start_move)
    win.bind("<B1-Motion>", do_move)

    lbl = tk.Label(win, text=message, font=('Arial', 12), wraplength=280, justify='center')
    lbl.pack(expand=True, pady=10)
    btn = tk.Button(win, text="OK", command=win.destroy, width=10)
    btn.pack(pady=5)
    win.transient(parent)
    win.wait_window(win)

class VendorDeliveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vendor Delivery System")
        self.root.configure(bg='#000957')
        self.orders = []

        # Header with logo and text
        header_frame = tk.Frame(root, bg='#C5172E', pady=10)
        header_frame.pack(fill='x')

        # Load and resize the logo image
        image_path = "sofa corner logo new.png"
        if os.path.exists(image_path):
            original_image = Image.open(image_path)
            resized_image = original_image.resize((60, 40))
            self.logo_img = ImageTk.PhotoImage(resized_image)
            img_label = tk.Label(header_frame, image=self.logo_img, bg='#C5172E')
            img_label.pack(side='left', padx=10)

        header_label = tk.Label(header_frame, text="Vendor Delivery System",
                                font=('Arial', 20, 'bold'), bg='#C5172E', fg='white')
        header_label.pack(side='left')

        # Search Frame
        search_frame = tk.Frame(root, bg='#000957')
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search by Customer Name or ID:", bg='#000957', fg='white').pack(side='left')
        self.search_name = tk.Entry(search_frame)
        self.search_name.pack(side='left', padx=5)
        tk.Button(search_frame, text="Search", command=self.search_orders, bg='orange').pack(side='left', padx=5)
        tk.Button(search_frame, text="Reset", command=self.reset_search, bg='gray', fg='white').pack(side='left')

        # Delivery Status Display
        self.search_status_label = tk.Label(root, text="", font=('Arial', 12, 'bold'), bg='#000957', fg='yellow')
        self.search_status_label.pack(pady=5)

        # Form Frame
        form_frame = tk.Frame(root, bg='#000957', padx=10, pady=10)
        form_frame.pack()

        self.fields = ['Order Date', 'Customer ID', 'Product ID', 'Product Name', 'Customer Name',
                       'Quantity', 'Colour', 'Price', 'Status', 'Vendor Name', 'Vendor Delivered Date']
        self.entries = {}

        for i, field in enumerate(self.fields):
            tk.Label(form_frame, text=field, font=('Arial', 10), bg='#000957', fg='white').grid(row=i, column=0, sticky='w', pady=2)

            if field in ["Order Date", "Vendor Delivered Date"]:
                cal = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
                cal.grid(row=i, column=1, padx=5, pady=2)
                self.entries[field] = cal
            elif field == "Status":
                combo = ttk.Combobox(form_frame, values=["Delivered", "Not Delivered"], state="readonly")
                combo.current(1)
                combo.grid(row=i, column=1, padx=5, pady=2)
                self.entries[field] = combo
            else:
                entry = tk.Entry(form_frame)
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.entries[field] = entry

        # Buttons
        button_frame = tk.Frame(root, bg='#000957')
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Add Order", command=self.add_order, bg="green", fg="white", width=15).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update Selected", command=self.update_status_only, bg="blue", fg="white", width=15).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Delete Selected", command=self.delete_order, bg="#C5172E", fg="white", width=15).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_form, bg="gray", fg="white", width=15).grid(row=0, column=3, padx=5)

        # Treeview with vertical scrollbar
        tree_frame = tk.Frame(root)
        tree_frame.pack(padx=10, pady=10, fill='both', expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=[str(i) for i in range(len(self.fields) + 2)], show='headings', height=10)
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscroll=scrollbar.set)

        headers = ['S.No'] + self.fields + ['Total Price']
        for i, h in enumerate(headers):
            self.tree.heading(str(i), text=h)
            self.tree.column(str(i), width=100)

        self.tree.bind("<<TreeviewSelect>>", self.load_selected_order)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#f0f0ff", foreground="black", rowheight=25, fieldbackground="#f0f0ff")
        style.map("Treeview", background=[('selected', 'lightblue')])

        # Footer
        footer = tk.Label(root, text="© 2025 Vendor Delivery System | All rights reserved", font=('Arial', 10),
                          bg='#C5172E', fg='white', pady=5)
        footer.pack(fill='x')

        self.entries['Order Date'].set_date(datetime.now().date())

        # Load orders from CSV on startup
        self.load_orders_from_csv()
        self.populate_treeview()

    def calculate_total_price(self, quantity, price):
        try:
            return float(quantity) * float(price)
        except:
            return 0.0

    def add_order(self):
        try:
            order_data = []
            for field in self.fields:
                value = self.entries[field].get()
                if not value:
                    custom_message(self.root, "Input Error", f"Please enter {field}")
                    return
                order_data.append(value)

            total_price = self.calculate_total_price(order_data[5], order_data[7])  # quantity index 5, price index 7
            s_no = len(self.orders) + 1
            full_data = [s_no] + order_data + [f"{total_price:.2f}"]
            self.orders.append(full_data)
            self.tree.insert('', 'end', values=full_data)
            self.clear_form()

            # Auto-save to CSV after adding
            self.save_orders_to_csv()

        except Exception as e:
            custom_message(self.root, "Error", str(e))

    def clear_form(self):
        for field in self.fields:
            if field == "Status":
                self.entries[field].current(1)
            elif field in ["Order Date", "Vendor Delivered Date"]:
                self.entries[field].set_date(datetime.now().date())
            else:
                self.entries[field].delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())
        self.search_status_label.config(text="")

    def load_selected_order(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            for i, field in enumerate(self.fields):
                if field == "Status":
                    self.entries[field].set(values[i + 1])
                elif field in ["Order Date", "Vendor Delivered Date"]:
                    try:
                        self.entries[field].set_date(values[i + 1])
                    except:
                        self.entries[field].set_date(datetime.now().date())
                else:
                    self.entries[field].delete(0, tk.END)
                    self.entries[field].insert(0, values[i + 1])

    # ONLY update the Status field of the selected order
    def update_status_only(self):
        selected = self.tree.selection()
        if not selected:
            custom_message(self.root, "No selection", "Select an order to update.")
            return

        try:
            new_status = self.entries['Status'].get()
            if not new_status:
                custom_message(self.root, "Input Error", "Please select Status")
                return

            item = self.tree.item(selected[0])
            current_values = list(item['values'])  # Make a mutable copy

            status_index = self.fields.index('Status') + 1  # +1 because first column is S.No
            current_values[status_index] = new_status

            s_no = current_values[0]
            index = s_no - 1
            self.orders[index][status_index] = new_status

            # Update treeview display
            self.tree.item(selected[0], values=current_values)
            custom_message(self.root, "Success", "Status updated successfully.")

            # Auto-save after update
            self.save_orders_to_csv()

        except Exception as e:
            custom_message(self.root, "Error", str(e))

    def delete_order(self):
        selected = self.tree.selection()
        if not selected:
            custom_message(self.root, "No selection", "Select an order to delete.")
            return
        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this order?")
        if confirm:
            item = self.tree.item(selected[0])
            s_no = item['values'][0]
            self.tree.delete(selected[0])
            self.orders.pop(s_no - 1)
            # Re-number all remaining orders
            self.tree.delete(*self.tree.get_children())
            for i, order in enumerate(self.orders):
                order[0] = i + 1
                self.tree.insert('', 'end', values=order)

            # Auto-save after deletion
            self.save_orders_to_csv()
            self.clear_form()

    def save_orders_to_csv(self):
        try:
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['S.No'] + self.fields + ['Total Price'])
                writer.writerows(self.orders)
        except Exception as e:
            custom_message(self.root, "Error", f"Failed to save orders:\n{e}")

    def load_orders_from_csv(self):
        if not os.path.exists(CSV_FILE):
            return
        try:
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                self.orders.clear()
                for row in reader:
                    if len(row) == len(self.fields) + 2:
                        self.orders.append(row)
        except Exception as e:
            custom_message(self.root, "Error", f"Failed to load orders:\n{e}")

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for order in self.orders:
            self.tree.insert('', 'end', values=order)

    def search_orders(self):
        search_text = self.search_name.get().strip().lower()
        if not search_text:
            custom_message(self.root, "Input Error", "Please enter customer name or ID to search.")
            return

        found = False
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            customer_name = str(values[self.fields.index('Customer Name') + 1]).lower()
            customer_id = str(values[self.fields.index('Customer ID') + 1]).lower()

            if search_text == customer_name or search_text == customer_id:
                self.tree.selection_set(item)
                self.tree.focus(item)

                status = values[self.fields.index('Status') + 1]
                vendor_name = values[self.fields.index('Vendor Name') + 1]

                self.search_status_label.config(
                    text=f"Delivery Status: {status} | Vendor Name: {vendor_name}"
                )
                found = True
                break

        if not found:
            self.search_status_label.config(text="No matching customer found.")
            self.tree.selection_remove(self.tree.selection())

    def reset_search(self):
        self.search_name.delete(0, tk.END)
        self.search_status_label.config(text="")
        self.tree.selection_remove(self.tree.selection())

if __name__ == "__main__":
    root = tk.Tk()
    app = VendorDeliveryApp(root)
    root.mainloop()
