import pandas as pd
from sklearn.ensemble import IsolationForest
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

# ==========================
# ===== Utils Functions ====
# ==========================

def time_of_day(hour):
    """Convert numeric hour into time-of-day labels."""
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'


# ==========================
# ===== Model Logic ========
# ==========================

def run_detection():
    """Main function to process the file and detect anomalies."""
    global selected_file
    if not selected_file:
        messagebox.showwarning("No file selected", "Please select a CSV file first!")
        return

    try:
        df = pd.read_csv(selected_file)
    except Exception as e:
        messagebox.showerror("File Error", f"Failed to read file:\n{e}")
        return

    # Validate required columns
    required_cols = {'username', 'login_time', 'location'}
    if not required_cols.issubset(df.columns):
        messagebox.showerror("Data Error", f"CSV must contain columns: {', '.join(required_cols)}")
        return

    # Ensure login_time is numeric
    if not pd.api.types.is_numeric_dtype(df['login_time']):
        messagebox.showerror("Data Error", "login_time column must be numeric")
        return

    # Add time_of_day classification
    df['time_of_day'] = df['login_time'].apply(time_of_day)

    # Encode categorical columns
    df_encoded = pd.get_dummies(df[['username', 'location', 'time_of_day']])
    df_encoded['login_time'] = df['login_time']

    # Run Isolation Forest for anomaly detection
    model = IsolationForest(contamination=0.2, random_state=42)
    model.fit(df_encoded)

    # Add prediction result
    df['is_anomaly'] = model.predict(df_encoded)
    df['is_anomaly'] = df['is_anomaly'].apply(lambda x: 'Yes' if x == -1 else 'No')

    # Save results
    df.to_csv("analyzed_logins.csv", index=False)
    df[df['is_anomaly'] == 'Yes'].to_csv("anomalies.csv", index=False)

    # Show result
    anomaly_count = (df['is_anomaly'] == 'Yes').sum()
    messagebox.showinfo("Detection Complete", f"Anomalies found: {anomaly_count}")
    show_anomalies_treeview(df)


# ==========================
# ===== UI Functions =======
# ==========================

def select_file():
    """Open file dialog to select CSV file."""
    global selected_file
    file_path = filedialog.askopenfilename(
        title="Select login CSV file",
        filetypes=[("CSV files", "*.csv")]
    )
    if file_path:
        selected_file = file_path
        file_label.config(text=f"Selected: {file_path.split('/')[-1]}", fg="black")
        run_btn.config(state=tk.NORMAL)
        clear_btn.config(state=tk.NORMAL)

def clear_selection():
    """Clear selected file."""
    global selected_file
    selected_file = None
    file_label.config(text="No file selected", fg="red")
    run_btn.config(state=tk.DISABLED)
    clear_btn.config(state=tk.DISABLED)

def show_anomalies_treeview(df):
    """Display anomalies in a filtered TreeView window."""
    anomalies = df[df['is_anomaly'] == 'Yes']
    if anomalies.empty:
        messagebox.showinfo("Anomalies", "No anomalies detected.")
        return

    # Create pop-up window
    win = tk.Toplevel(root)
    win.title("Detected Anomalies")
    win.geometry("900x500")

    # === Filter Frame ===
    filter_frame = tk.Frame(win)
    filter_frame.pack(fill='x', padx=10, pady=5)

    tk.Label(filter_frame, text="Filter by Username:").pack(side='left')
    username_var = tk.StringVar()
    username_entry = tk.Entry(filter_frame, textvariable=username_var)
    username_entry.pack(side='left', padx=5)

    # === TreeView Frame ===
    tree_frame = tk.Frame(win)
    tree_frame.pack(expand=True, fill='both')

    tree = ttk.Treeview(tree_frame, columns=list(anomalies.columns), show='headings')
    tree.pack(side='left', expand=True, fill='both')

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscrollcommand=scrollbar.set)

    for col in anomalies.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    def update_treeview(dataframe):
        tree.delete(*tree.get_children())
        for _, row in dataframe.iterrows():
            tree.insert("", "end", values=list(row))

    def update_filter(*args):
        val = username_var.get().strip().lower()
        filtered = anomalies[anomalies['username'].str.lower().str.contains(val)] if val else anomalies
        update_treeview(filtered)

    username_var.trace_add('write', update_filter)
    update_treeview(anomalies)

    # === Export Buttons ===
    export_frame = tk.Frame(win)
    export_frame.pack(pady=10)

    def export_csv():
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if path:
            filtered = anomalies if not username_var.get().strip() else anomalies[anomalies['username'].str.lower().str.contains(username_var.get().strip().lower())]
            filtered.to_csv(path, index=False)
            messagebox.showinfo("Export", f"Anomalies exported to:\n{path}")

    def export_excel():
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if path:
            filtered = anomalies if not username_var.get().strip() else anomalies[anomalies['username'].str.lower().str.contains(username_var.get().strip().lower())]
            filtered.to_excel(path, index=False)
            messagebox.showinfo("Export", f"Anomalies exported to:\n{path}")

    btn_csv = tk.Button(export_frame, text="Export CSV", command=export_csv)
    btn_csv.pack(side='left', padx=10)

    btn_excel = tk.Button(export_frame, text="Export Excel", command=export_excel)
    btn_excel.pack(side='left', padx=10)


# ==========================
# ===== GUI Setup ==========
# ==========================

selected_file = None

root = tk.Tk()
root.title("Login Anomaly Detector")
root.geometry("450x250")

label = tk.Label(root, text="Detect Anomalies in login CSV file", font=("Arial", 14))
label.pack(pady=10)

file_label = tk.Label(root, text="No file selected", fg="red", font=("Arial", 10))
file_label.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=15)

select_btn = tk.Button(btn_frame, text="Select CSV File", command=select_file, width=15)
select_btn.grid(row=0, column=0, padx=10)

clear_btn = tk.Button(btn_frame, text="Clear Selection", command=clear_selection, width=15, state=tk.DISABLED)
clear_btn.grid(row=0, column=1, padx=10)

run_btn = tk.Button(root, text="Run Detection", command=run_detection, bg="green", fg="white", font=("Arial", 12), state=tk.DISABLED)
run_btn.pack(pady=20)

root.mainloop()
