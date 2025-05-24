import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import queue
import csv
import os
from tkcalendar import DateEntry # type: ignore
from PIL import Image, ImageTk # type: ignore

CSV_PENDING = "pending.csv"
CSV_DELIVERED = "DELIVERED.csv"

class OrderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Order Delivery System")
        self.root.configure(bg='#153e75')
        self.root.geometry("1000x800")

        header = tk.Label(root, text="Customer Order Delivery System", font=("Arial", 20, "bold"),
                          bg="#C62300", fg="white", pady=10)
        header.pack(fill='x')

        # Load and display image
        image_path = "sofa corner logo new.png"
        try:
            original_image = Image.open(image_path)
            resized_image = original_image.resize((150, 100))
            self.tk_image = ImageTk.PhotoImage(resized_image)
            image_label = tk.Label(root, image=self.tk_image, bg='#153e75')
            image_label.pack(pady=10)
        except Exception as e:
            print("Image load error:", e)

        self.order_queue = queue.PriorityQueue()
        self.order_counter = 0

        frame = tk.Frame(root, padx=10, pady=10, bg='#153e75')
        frame.pack()

        label_font = ("Arial", 10, "bold")

        tk.Label(frame, text="Customer Name:", bg='#153e75', fg='white', font=label_font).grid(row=0, column=0, sticky="e")
        self.entry_name = tk.Entry(frame)
        self.entry_name.grid(row=0, column=1)

        tk.Label(frame, text="Customer ID:", bg='#153e75', fg='white', font=label_font).grid(row=1, column=0, sticky="e")
        self.entry_cust_id = tk.Entry(frame)
        self.entry_cust_id.grid(row=1, column=1)

        tk.Label(frame, text="Address:", bg='#153e75', fg='white', font=label_font).grid(row=2, column=0, sticky="e")
        self.entry_address = tk.Entry(frame)
        self.entry_address.grid(row=2, column=1)

        tk.Label(frame, text="Product ID:", bg='#153e75', fg='white', font=label_font).grid(row=3, column=0, sticky="e")
        self.entry_prod_id = tk.Entry(frame)
        self.entry_prod_id.grid(row=3, column=1)

        tk.Label(frame, text="Phone Number:", bg='#153e75', fg='white', font=label_font).grid(row=4, column=0, sticky="e")
        self.entry_phone_number = tk.Entry(frame)
        self.entry_phone_number.grid(row=4, column=1)

        tk.Label(frame, text="Order Details:", bg='#153e75', fg='white', font=label_font).grid(row=5, column=0, sticky="e")
        self.entry_order_details = tk.Entry(frame)
        self.entry_order_details.grid(row=5, column=1)

        tk.Label(frame, text="Order Date:", bg='#153e75', fg='white', font=label_font).grid(row=6, column=0, sticky="e")
        self.entry_order_date = DateEntry(frame, date_pattern='yyyy-mm-dd', background='#000957', foreground='white', borderwidth=2)
        self.entry_order_date.grid(row=6, column=1)

        tk.Label(frame, text="Total Amount (₹):", bg='#153e75', fg='white', font=label_font).grid(row=7, column=0, sticky="e")
        self.entry_total_amount = tk.Entry(frame)
        self.entry_total_amount.grid(row=7, column=1)

        tk.Label(frame, text="Advance Paid (₹):", bg='#153e75', fg='white', font=label_font).grid(row=8, column=0, sticky="e")
        self.entry_advance_paid = tk.Entry(frame)
        self.entry_advance_paid.grid(row=8, column=1)

        tk.Label(frame, text="Important Customer:", bg='#153e75', fg='white', font=label_font).grid(row=9, column=0, sticky="e")
        self.var_important = tk.IntVar()
        tk.Checkbutton(frame, variable=self.var_important, bg='#153e75').grid(row=9, column=1, sticky="w")

        btn_frame = tk.Frame(root, pady=10, bg='#153e75')
        btn_frame.pack()

        button_font = ("Arial", 10, "bold")
        tk.Button(btn_frame, text="Add Order", command=self.add_order, font=button_font).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Deliver Next Order", command=self.deliver_order, font=button_font).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Show Pending Orders", command=self.show_orders, font=button_font).grid(row=0, column=2, padx=5)

        self.listbox = tk.Listbox(root, width=120, height=10, bg='lightblue', fg='black', font=("Arial", 10, "bold"))
        self.listbox.pack(padx=10, pady=10)

        footer = tk.Label(root, text="© 2025 Your Company Name - All rights reserved",
                          bg="#C62300", fg="white", font=("Arial", 10, "bold"), pady=5)
        footer.pack(fill='x', side='bottom')

        self.load_orders()

    def add_order(self):
        try:
            order_date_str = self.entry_order_date.get_date().strftime("%Y-%m-%d")
        except:
            order_date_str = datetime.today().strftime("%Y-%m-%d")

        name = self.entry_name.get().strip()
        cust_id = self.entry_cust_id.get().strip()
        phone_number = self.entry_phone_number.get().strip()
        address = self.entry_address.get().strip()
        prod_id = self.entry_prod_id.get().strip()
        order_details = self.entry_order_details.get().strip()
        total_amount_str = self.entry_total_amount.get().strip()
        advance_paid_str = self.entry_advance_paid.get().strip()
        important = self.var_important.get()

        if not (name and cust_id and address and prod_id and phone_number and order_details and total_amount_str and advance_paid_str):
            messagebox.showerror("Input Error", "Please fill all fields.")
            return

        try:
            order_date = datetime.strptime(order_date_str, "%Y-%m-%d").date()
            total_amount = float(total_amount_str)
            advance_paid = float(advance_paid_str)
        except ValueError:
            messagebox.showerror("Format Error", "Check date and amount formats.")
            return

        importance_flag = 0 if important else 1

        order = {
            "order_date": order_date,
            "name": name,
            "customer_id": cust_id,
            "address": address,
            "phone_number": phone_number,
            "product_id": prod_id,
            "order": order_details,
            "total_amount": total_amount,
            "advance_paid": advance_paid,
            "priority_flag": importance_flag
        }

        priority_tuple = (importance_flag, order_date, -total_amount, self.order_counter)
        self.order_queue.put((priority_tuple, order))
        self.order_counter += 1

        self.append_order_to_csv(order, CSV_PENDING)
        messagebox.showinfo("Success", f"Order added for {name}.")
        self.clear_inputs()
        self.show_orders()

    def deliver_order(self):
        if self.order_queue.empty():
            messagebox.showinfo("No Orders", "No orders to deliver.")
            return

        priority_tuple, order = self.order_queue.get()
        self.append_order_to_csv(order, CSV_DELIVERED)
        self.remove_order_from_pending(order)

        details = (
            f"Delivering Order:\n\n"
            f"Order Date    : {order['order_date']}\n"
            f"Customer Name : {order['name']}\n"
            f"Customer ID   : {order['customer_id']}\n"
            f"Address       : {order['address']}\n"
            f"Phone Number  : {order['phone_number']}\n"
            f"Product ID    : {order['product_id']}\n"
            f"Order Details : {order['order']}\n"
            f"Total Amount  : ₹{order['total_amount']}\n"
            f"Advance Paid  : ₹{order['advance_paid']}\n"
            f"Balance Due   : ₹{order['total_amount'] - order['advance_paid']}\n"
            f"Priority      : {'High' if order['priority_flag'] == 0 else 'Normal'}"
        )
        messagebox.showinfo("Order DELIVERED", details)
        self.show_orders()

    def show_orders(self):
        self.listbox.delete(0, tk.END)
        if self.order_queue.empty():
            self.listbox.insert(tk.END, "No pending orders.")
            return
        temp_list = list(self.order_queue.queue)
        temp_list.sort()
        for idx, (priority_tuple, order) in enumerate(temp_list, 1):
            display_text = (
                f"{idx}. {order['name']} | ID: {order['customer_id']} | Address: {order['address']} | Phone: {order['phone_number']} | "
                f"Prod ID: {order['product_id']} | Date: {order['order_date']} | "
                f"Total: ₹{order['total_amount']} | Advance: ₹{order['advance_paid']} | "
                f"Priority: {'High' if order['priority_flag'] == 0 else 'Normal'}"
            )
            self.listbox.insert(tk.END, display_text)

    def clear_inputs(self):
        self.entry_name.delete(0, tk.END)
        self.entry_cust_id.delete(0, tk.END)
        self.entry_address.delete(0, tk.END)
        self.entry_prod_id.delete(0, tk.END)
        self.entry_order_details.delete(0, tk.END)
        self.entry_phone_number.delete(0, tk.END)
        self.entry_order_date.set_date(datetime.today())
        self.entry_total_amount.delete(0, tk.END)
        self.entry_advance_paid.delete(0, tk.END)
        self.var_important.set(0)

    def append_order_to_csv(self, order, filename):
        file_exists = os.path.isfile(filename)
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["order_date", "name", "customer_id", "address", "phone_number",
                          "product_id", "order", "total_amount", "advance_paid", "priority_flag"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            order_to_write = order.copy()
            order_to_write['order_date'] = order['order_date'].strftime("%Y-%m-%d")
            writer.writerow(order_to_write)

    def remove_order_from_pending(self, order_to_remove):
        if not os.path.isfile(CSV_PENDING):
            return
        orders = []
        with open(CSV_PENDING, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if (row["name"] == order_to_remove["name"] and
                    row["customer_id"] == order_to_remove["customer_id"] and
                    row["product_id"] == order_to_remove["product_id"] and
                    row["order_date"] == order_to_remove["order_date"].strftime("%Y-%m-%d") and
                    abs(float(row["total_amount"]) - order_to_remove["total_amount"]) < 0.01):
                    continue
                orders.append(row)
        with open(CSV_PENDING, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["order_date", "name", "customer_id", "address", "phone_number",
                          "product_id", "order", "total_amount", "advance_paid", "priority_flag"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in orders:
                writer.writerow(row)

    def load_orders(self):
        if not os.path.isfile(CSV_PENDING):
            return
        with open(CSV_PENDING, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    order_date = datetime.strptime(row["order_date"], "%Y-%m-%d").date()
                    total_amount = float(row["total_amount"])
                    advance_paid = float(row["advance_paid"])
                    priority_flag = int(row["priority_flag"])
                except Exception as e:
                    print("Skipping invalid row:", row, "Error:", e)
                    continue
                order = {
                    "order_date": order_date,
                    "name": row["name"],
                    "customer_id": row["customer_id"],
                    "address": row["address"],
                    "phone_number": row["phone_number"],
                    "product_id": row["product_id"],
                    "order": row["order"],
                    "total_amount": total_amount,
                    "advance_paid": advance_paid,
                    "priority_flag": priority_flag
                }
                priority_tuple = (priority_flag, order_date, -total_amount, self.order_counter)
                self.order_queue.put((priority_tuple, order))
                self.order_counter += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = OrderApp(root)
    root.mainloop()
