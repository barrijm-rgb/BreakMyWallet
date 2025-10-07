#!/usr/bin/env python3
"""
BreakMyWallet — BMW Maintenance Tracker
Standalone Tkinter + SQLite application
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import json
import os
from PIL import Image, ImageTk

DB_FILE = "bmw_maint.db"
ASSETS_DIR = os.path.join("assets", "logos")

# Supported vehicles
VEHICLES = [
    {"name": "2008 BMW M3", "logo": "logo_2008_m3.svg"},
    {"name": "2013 BMW 335i M Sport Sedan", "logo": "logo_2013_335i.svg"},
    {"name": "2020 BMW X7 xDrive40i", "logo": "logo_2020_x7.svg"},
    {"name": "2021 BMW X3 sDrive30i", "logo": "logo_2021_x3.svg"},
]

# Default maintenance tasks
DEFAULT_TASKS = [
    {"task": "Oil Change", "interval_miles": 7500, "interval_months": 12},
    {"task": "Brake Fluid", "interval_miles": 30000, "interval_months": 24},
    {"task": "Coolant Flush", "interval_miles": 60000, "interval_months": 48},
    {"task": "Spark Plugs", "interval_miles": 45000, "interval_months": 36},
    {"task": "Air Filter", "interval_miles": 15000, "interval_months": 12},
]


class BreakMyWalletApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BreakMyWallet — BMW Maintenance Tracker")
        self.geometry("900x600")
        self.icon_path = os.path.join(ASSETS_DIR, "icon.svg")

        # Connect to database
        self.conn = sqlite3.connect(DB_FILE)
        self.create_tables()

        self.current_vehicle = None
        self.setup_ui()

    # -----------------------------
    # Database
    # -----------------------------
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle TEXT,
            task TEXT,
            last_date TEXT,
            last_mileage INTEGER,
            notes TEXT
        )
        """)
        self.conn.commit()

    # -----------------------------
    # UI setup
    # -----------------------------
    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        mainframe = ttk.Frame(self, padding=10)
        mainframe.grid(sticky="nsew")
        mainframe.columnconfigure(1, weight=1)
        mainframe.rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ttk.Frame(mainframe, width=200)
        sidebar.grid(row=0, column=0, sticky="ns")
        ttk.Label(sidebar, text="Vehicles", font=("Arial", 14, "bold")).pack(pady=(0, 10))

        for v in VEHICLES:
            btn = ttk.Button(sidebar, text=v["name"], command=lambda v=v: self.load_vehicle(v))
            btn.pack(fill="x", pady=2)

        ttk.Button(sidebar, text="Add Maintenance", command=self.add_maintenance_popup).pack(pady=(20, 5))
        ttk.Button(sidebar, text="Export Data", command=self.export_data).pack(pady=5)
        ttk.Button(sidebar, text="Import Data", command=self.import_data).pack(pady=5)

        # Main display
        self.display_frame = ttk.Frame(mainframe)
        self.display_frame.grid(row=0, column=1, sticky="nsew")

        self.vehicle_label = ttk.Label(self.display_frame, text="Select a Vehicle", font=("Arial", 18, "bold"))
        self.vehicle_label.pack(pady=10)

        self.tree = ttk.Treeview(
            self.display_frame,
            columns=("Task", "Last Date", "Last Mileage", "Notes"),
            show="headings",
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # -----------------------------
    # Load vehicle data
    # -----------------------------
    def load_vehicle(self, vehicle):
        self.current_vehicle = vehicle
        self.vehicle_label.config(text=vehicle["name"])
        self.tree.delete(*self.tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute("SELECT task, last_date, last_mileage, notes FROM maintenance WHERE vehicle=?", (vehicle["name"],))
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        if not self.tree.get_children():
            for t in DEFAULT_TASKS:
                self.tree.insert("", "end", values=(t["task"], "—", "—", ""))

    # -----------------------------
    # Add maintenance popup
    # -----------------------------
    def add_maintenance_popup(self):
        if not self.current_vehicle:
            messagebox.showerror("Error", "Please select a vehicle first.")
            return

        popup = tk.Toplevel(self)
        popup.title("Add Maintenance Record")
        popup.geometry("400x300")

        ttk.Label(popup, text="Task:").pack(pady=5)
        task_entry = ttk.Entry(popup)
        task_entry.pack(fill="x", padx=20)

        ttk.Label(popup, text="Date (YYYY-MM-DD):").pack(pady=5)
        date_entry = ttk.Entry(popup)
        date_entry.pack(fill="x", padx=20)

        ttk.Label(popup, text="Mileage:").pack(pady=5)
        mileage_entry = ttk.Entry(popup)
        mileage_entry.pack(fill="x", padx=20)

        ttk.Label(popup, text="Notes:").pack(pady=5)
        notes_entry = ttk.Entry(popup)
        notes_entry.pack(fill="x", padx=20)

        def save_record():
            task = task_entry.get().strip()
            date = date_entry.get().strip()
            mileage = mileage_entry.get().strip()
            notes = notes_entry.get().strip()
            if not task:
                messagebox.showerror("Error", "Task name is required.")
                return
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO maintenance (vehicle, task, last_date, last_mileage, notes) VALUES (?, ?, ?, ?, ?)",
                    (self.current_vehicle["name"], task, date, mileage or None, notes),
                )
                self.conn.commit()
                self.load_vehicle(self.current_vehicle)
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

        ttk.Button(popup, text="Save", command=save_record).pack(pady=15)

    # -----------------------------
    # Export / Import JSON
    # -----------------------------
    def export_data(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        cursor = self.conn.cursor()
        cursor.execute("SELECT vehicle, task, last_date, last_mileage, notes FROM maintenance")
        data = cursor.fetchall()
        json.dump(data, open(path, "w"), indent=2)
        messagebox.showinfo("Export Complete", f"Data saved to {path}")

    def import_data(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            data = json.load(open(path))
            cursor = self.conn.cursor()
            for v, t, d, m, n in data:
                cursor.execute(
                    "INSERT INTO maintenance (vehicle, task, last_date, last_mileage, notes) VALUES (?, ?, ?, ?, ?)",
                    (v, t, d, m, n),
                )
            self.conn.commit()
            if self.current_vehicle:
                self.load_vehicle(self.current_vehicle)
            messagebox.showinfo("Import Complete", "Data imported successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = BreakMyWalletApp()
    app.mainloop()
