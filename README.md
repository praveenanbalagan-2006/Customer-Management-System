# Customer Management System

A Python desktop application (Tkinter-based) that manages customer orders and vendor deliveries using structured CSV data and simple data structures like queues and "priority sorting". The app includes login authentication and generates a "Today's Plan" view for dispatch-ready orders.

🧾 app.py – Customer Order Delivery System
Accepts customer details and orders.

Uses a priority queue to deliver important or expensive orders first.

Saves pending orders to pending.csv.

Marks orders as delivered and moves them to delivered.csv.

📦 app2.py – Vendor Delivery System
Records delivery status of products to vendors.

Updates delivery status as “Delivered” or “Not Delivered”.

Saves data to orders_export.csv.

Allows update/delete/search with vendor and status details.

🚚 app3.py – Today's Plan Generator
Validates login.

Loads only vendor-delivered orders for today from orders_export.csv.

Matches against customer orders from pending.csv.

Shows only those ready to dispatch based on:

Delivered today

Order exists

Not already shown

Removes those orders from pending.csv.

Sorts today's plan by total amount (₹) to prioritize dispatches.

