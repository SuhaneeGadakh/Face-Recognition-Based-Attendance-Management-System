import os
import pandas as pd
from tkinter import *
from tkinter import ttk, messagebox
import time

# ===================== Show Attendance Window =====================

def show_attendance_window():
    root = Tk()
    root.title("📊 Live Attendance Dashboard")
    root.geometry("900x600")
    root.configure(bg="#f5f5f5")

    title_label = Label(root, text="📋 Attendance Dashboard (Live Refresh)",
                        font=("Arial", 20, "bold"), bg="#f5f5f5", fg="#333")
    title_label.pack(pady=20)

    # Frame for table
    frame = Frame(root, bg="#ffffff", bd=2, relief=RIDGE)
    frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # Treeview for showing data
    tree = ttk.Treeview(frame,
                        columns=("Enrollment", "Name", "Date", "Time", "Status"),
                        show="headings")
    tree.heading("Enrollment", text="Enrollment")
    tree.heading("Name", text="Name")
    tree.heading("Date", text="Date")
    tree.heading("Time", text="Time")
    tree.heading("Status", text="Status")

    tree.column("Enrollment", width=120)
    tree.column("Name", width=180)
    tree.column("Date", width=100)
    tree.column("Time", width=100)
    tree.column("Status", width=100)
    tree.pack(fill=BOTH, expand=True)

    # Label for status / last refresh
    status_label = Label(root, text="", font=("Arial", 10), bg="#f5f5f5", fg="#555")
    status_label.pack(pady=5)

    REFRESH_INTERVAL = 10_000  # milliseconds → 10 seconds

    # ===================== Function to calculate attendance =====================
    def load_attendance():
        attendance_path = "Attendance"  # Folder where .csv files are stored
        df_list = []

        # Ensure folder exists
        if not os.path.exists(attendance_path):
            messagebox.showerror("Error", f"'{attendance_path}' folder not found!")
            return

        # Collect all .csv files
        for f in os.listdir(attendance_path):
            if f.endswith(".csv"):
                file_path = os.path.join(attendance_path, f)
                try:
                    data = pd.read_csv(file_path)
                    df_list.append(data)
                except Exception as e:
                    print(f"Warning: could not read file {f}: {e}")

        # Check if any files found
        if len(df_list) == 0:
            for item in tree.get_children():
                tree.delete(item)
            status_label.config(text="⚠️ No attendance files found!")
            return

        # Merge all dataframes
        merged_df = pd.concat(df_list, ignore_index=True)

        # Clear previous records
        for item in tree.get_children():
            tree.delete(item)

        # Display merged data in treeview
        # Normalize column names
        cols = {c.strip(): c for c in merged_df.columns}
        id_col = 'Enrollment' if 'Enrollment' in cols else ('Id' if 'Id' in cols else None)
        name_col = 'Name' if 'Name' in cols else None
        date_col = 'Date' if 'Date' in cols else None
        time_col = 'Time' if 'Time' in cols else None
        status_col = 'Status' if 'Status' in cols else None

        for _, row in merged_df.iterrows():
            tree.insert("", "end", values=(
                row.get(id_col, "") if id_col else "",
                row.get(name_col, "") if name_col else "",
                row.get(date_col, "") if date_col else "",
                row.get(time_col, "") if time_col else "",
                row.get(status_col, "Present") if status_col else "Present"
            ))

        # Update last refresh time
        current_time = time.strftime("%H:%M:%S")
        status_label.config(text=f"✅ Last updated at: {current_time}")

        # Schedule next refresh automatically
        root.after(REFRESH_INTERVAL, load_attendance)

    # ===================== Buttons =====================
    btn_frame = Frame(root, bg="#f5f5f5")
    btn_frame.pack(pady=10)

    Button(btn_frame, text="Manual Refresh", command=load_attendance,
           bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
           width=16, relief=RAISED).grid(row=0, column=0, padx=10)

    Button(btn_frame, text="Exit", command=root.destroy,
           bg="#f44336", fg="white", font=("Arial", 12, "bold"),
           width=10, relief=RAISED).grid(row=0, column=1, padx=10)

    # ===================== Start auto-refresh loop =====================
    load_attendance()

    root.mainloop()


# ===================== Run window =====================
if __name__ == "__main__":
    show_attendance_window()
