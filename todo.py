import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar
from pymongo import MongoClient
from bson.objectid import ObjectId

try:
    client = MongoClient("mongodb://localhost:27017/todoDB")
    db = client["todoDB"]
    collection = db["tasks"]
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    messagebox.showerror("Database Error", f"Failed to connect to MongoDB:\n{e}")


def add_task():
    task = entry_task.get().strip()
    due_date = entry_date.get().strip()
    priority = priority_var.get()

    if task and due_date:
        collection.insert_one({"task": task, "due_date": due_date, "priority": priority, "completed": False})
        entry_task.delete(0, tk.END)
        entry_date.delete(0, tk.END)
        update_task_list()
    else:
        messagebox.showwarning("Warning", "Please enter both task and due date.")

def update_task_list():
    """Updates the Treeview to display tasks from the database."""
    task_list.delete(*task_list.get_children())  
    tasks = collection.find()

    for task in tasks:
        completed = "✓" if task["completed"] else "✗"
        task_list.insert("", "end", values=(task["task"], task["due_date"], task["priority"], completed))

def mark_completed():
    try:
        selected_item = task_list.selection()[0]
        task_name = task_list.item(selected_item, "values")[0]
        collection.update_one({"task": task_name}, {"$set": {"completed": True}})
        update_task_list()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to mark as completed.")

def delete_task():
    try:
        selected_item = task_list.selection()[0]
        task_name = task_list.item(selected_item, "values")[0]
        collection.delete_one({"task": task_name})
        update_task_list()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to delete.")

def open_calendar():
    def set_date():
        entry_date.delete(0, tk.END)
        entry_date.insert(0, cal.get_date())
        top.destroy()

    top = tk.Toplevel(root)
    top.title("Select Due Date")
    top.geometry("300x250")
    cal = Calendar(top, selectmode="day", date_pattern="dd-mm-yyyy")
    cal.pack(pady=10)

    ttk.Button(top, text="Select Date", command=set_date, style="TButton").pack(pady=3)


root = tk.Tk()
root.title("📝 Modern To-Do App with MongoDB")
root.geometry("700x500")
root.configure(bg="#f4f4f4")

style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=6)
style.configure("TLabel", font=("Arial", 11))
style.configure("TCombobox", font=("Arial", 11))

frame_entry = tk.Frame(root, bg="white", padx=10, pady=10, bd=2, relief="ridge")
frame_entry.pack(pady=10, padx=10, fill="x")

tk.Label(frame_entry, text="Task:", font=("Arial", 12), bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_task = ttk.Entry(frame_entry, width=40, font=("Arial", 12))
entry_task.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_entry, text="Due Date:", font=("Arial", 12), bg="white").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_date = ttk.Entry(frame_entry, width=30, font=("Arial", 12))
entry_date.grid(row=1, column=1, padx=5, pady=5)

ttk.Button(frame_entry, text="📅", command=open_calendar, width=3).grid(row=1, column=2, padx=5, pady=5)

tk.Label(frame_entry, text="Priority:", font=("Arial", 12), bg="white").grid(row=2, column=0, padx=5, pady=5, sticky="w")
priority_var = tk.StringVar(value="Low")
dropdown_priority = ttk.Combobox(frame_entry, textvariable=priority_var, values=["Low", "Medium", "High"], state="readonly", font=("Arial", 12))
dropdown_priority.grid(row=2, column=1, padx=5, pady=5)

# Task List Frame (Using Treeview for better UI)
frame_tasks = tk.Frame(root, bg="white", padx=10, pady=10, bd=2, relief="ridge")
frame_tasks.pack(pady=10, padx=10, fill="both", expand=True)

columns = ("Task", "Due Date", "Priority", "Completed")
task_list = ttk.Treeview(frame_tasks, columns=columns, show="headings")
task_list.heading("Task", text="Task")
task_list.heading("Due Date", text="Due Date")
task_list.heading("Priority", text="Priority")
task_list.heading("Completed", text="Completed")
task_list.column("Task", width=250)
task_list.column("Due Date", width=100)
task_list.column("Priority", width=100)
task_list.column("Completed", width=80)
task_list.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame_tasks, orient="vertical", command=task_list.yview)
scrollbar.pack(side="right", fill="y")
task_list.configure(yscrollcommand=scrollbar.set)

frame_buttons = tk.Frame(root, bg="white")
frame_buttons.pack(pady=10)

btn_add = ttk.Button(frame_buttons, text="➕ Add Task", command=add_task, width=15)
btn_add.grid(row=0, column=0, padx=5, pady=5)

btn_complete = ttk.Button(frame_buttons, text="✔ Mark Completed", command=mark_completed, width=15)
btn_complete.grid(row=0, column=1, padx=5, pady=5)

btn_delete = ttk.Button(frame_buttons, text="❌ Delete Task", command=delete_task, width=15)
btn_delete.grid(row=0, column=2, padx=5, pady=5)

update_task_list()

root.mainloop()
