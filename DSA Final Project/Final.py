import sqlite3
import tkinter as tk
import re
from tkinter import *
from tkinter import ttk, simpledialog
from tkinter import messagebox
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime

class ToDoApp:
    def __init__(self, db):
        self.db = db
        self.tasks = self.db.fetch_tasks()
        self.completed_tasks = self.db.fetch_completed_tasks()

    def add_task(self, task_title, task_deadline):
        self.tasks.append((task_title, task_deadline))
        self.db.insert_task(task_title, task_deadline)

    def delete_task(self, task_title, task_deadline):
        self.db.cursor.execute('DELETE FROM tasks WHERE title = ? AND deadline = ?', (task_title, task_deadline))
        self.db.connection.commit()
        self.tasks = [task for task in self.tasks if task[0] != task_title or task[1] != task_deadline]

    def check_task(self, task_title, task_deadline):
        self.tasks = [task for task in self.tasks if task[0] != task_title or task[1] != task_deadline]
        self.completed_tasks.append((task_title, task_deadline))
        self.db.mark_task_completed(task_title, task_deadline)

    def sort_tasks(self, sort_option):
        if sort_option == "Alphabetical":
            self.tasks.sort(key=lambda x: x[0].lower())
        elif sort_option == "Date (Ascending)":
            self.tasks.sort(key=lambda x: datetime.strptime(x[1], '%m/%d/%Y'))
        elif sort_option == "Date (Descending)":
            self.tasks.sort(key=lambda x: datetime.strptime(x[1], '%m/%d/%Y'), reverse=True)

    def reset_database(self):
        self.db.reset_database()
        self.tasks = []
        self.completed_tasks = []

class ToDoAppGUI:
    def __init__(self, window, app):
        self.window = window
        self.app = app
        self.window.geometry("1366x768")
        self.window.state("zoomed")
        self.window.title("Taskly")

        self.setup_ui()

    def setup_ui(self):
        # Load and set the background image
        Image1 = Image.open('BG.png')
        Background = ImageTk.PhotoImage(Image1.resize((1366, 768)))
        BgLabel = Label(self.window, image=Background)
        BgLabel.image = Background
        BgLabel.place(x=0, y=0)

        Image2 = Image.open('Logo1.png').convert("RGBA")
        Logo1 = ImageTk.PhotoImage(Image2.resize((50, 55)))
        Logo1Label = Label(self.window, image=Logo1, bg='white', borderwidth=0)
        Logo1Label.image = Logo1
        Logo1Label.place(x=34, y=22)

        Image3 = Image.open('Taskly.png').convert("RGBA")
        Logo2 = ImageTk.PhotoImage(Image3.resize((100, 35)))
        Logo2Label = Label(self.window, image=Logo2, bg='white', borderwidth=0)
        Logo2Label.image = Logo2
        Logo2Label.place(x=105, y=35)

        Image4 = Image.open('add.png').convert("RGBA")
        Add = ImageTk.PhotoImage(Image4.resize((80, 80)))

        Image5 = Image.open('delete.png').convert("RGBA")
        self.Delete = ImageTk.PhotoImage(Image5.resize((35, 35)))

        Image6 = Image.open('done.png').convert("RGBA")
        self.Done = ImageTk.PhotoImage(Image6.resize((35, 35)))

        Image7 = Image.open('load.png').convert("RGBA")
        self.Load = ImageTk.PhotoImage(Image7.resize((35, 35)))

        self.TodoMainLabel = self.MainLabel(width=404, x=33, y=101)
        self.todo_frame = self.AllFrame(width=415, height=510, x=27, y=164)
        self.SortMainLabel = self.MainLabel(width=210, x=483, y=101)
        self.sort_frame = self.AllFrame(width=415, height=510, x=477, y=164)
        self.ProgressMainLabel = self.MainLabel(width=125, x=933, y=101)
        self.progress_frame = self.AllFrame(width=415, height=360, x=926, y=164)

        self.TodoLabel = self.Heading(x=160, y=98, text="TO DO LIST")
        self.SortLabel = self.Heading(x=484, y=98, text="SORT")
        self.ProgressLabel = self.Heading(x=934, y=98, text="YOUR PROGRESS")

        self.todo_scrollbar = tk.Scrollbar(self.todo_frame)
        self.todo_scrollbar.place(relx=1.0, rely=0, relheight=1, anchor='ne')
        self.todo_listbox = tk.Listbox(self.todo_frame, width=400, height=500, yscrollcommand=self.todo_scrollbar.set)
        self.todo_listbox.place(width=800, height=900, anchor='center')
        self.todo_scrollbar.config(command=self.todo_listbox.yview)

        self.sort_scrollbar = tk.Scrollbar(self.sort_frame)
        self.sort_scrollbar.place(relx=1.0, rely=0, relheight=0.92, anchor='ne')
        self.sort_listbox = tk.Listbox(self.sort_frame, fg='black', bg='#c8d1e0', font=("Helvetica", 16, "bold"), yscrollcommand=self.sort_scrollbar.set)
        self.sort_listbox.place(width=400, height=470)
        self.sort_scrollbar.config(command=self.sort_listbox.yview)

        self.sort_combobox = ttk.Combobox(self.SortMainLabel, values=["----------------", "Alphabetical", "Date (Ascending)", "Date (Descending)"], state="readonly", width=17)
        self.sort_combobox.place(x=80, y=7, anchor='nw')
        self.sort_combobox.current(0)
        self.sort_combobox.bind("<<ComboboxSelected>>", self.sort_tasks)

        self.add_button = tk.Button(self.window, image=Add, bg='white', borderwidth=0, command=self.add_task)
        self.add_button.image = Add
        self.add_button.place(x=200, y=590)

        self.reset_button = tk.Button(self.window, text="Reset", command=self.reset_database)
        self.reset_button.place(x=1300, y=500)

        self.markascomplete_button = tk.Button(self.window, image=self.Done, bg='white', borderwidth=0, command=self.mark_selectedtask_complete)
        self.markascomplete_button.place(x=740, y=640, anchor='nw')

        self.deletetasks_button = tk.Button(self.window, image=self.Delete, bg='white', borderwidth=0, command=self.delete_selectedtask)
        self.deletetasks_button.place(x=790, y=640, anchor='nw')

        self.show_savedtasks_button = tk.Button(self.window, image=self.Load, bg='white', borderwidth=0,command=self.show_savedtasks)
        self.show_savedtasks_button.place(x=840, y=640, anchor='nw')

        self.task_position = 0

        self.insert_donut_chart()

    def add_task(self):
        task_title = simpledialog.askstring("Task Title", "Enter the title of your task:", parent=self.window)
        if task_title:
            while True:
                task_deadline = simpledialog.askstring("Task Deadline", "Enter the deadline of your task (MM/DD/YYYY):", parent=self.window)
                if re.match(r'^\d{2}/\d{2}/\d{4}$', task_deadline):
                    break
                else:
                    messagebox.showerror("Invalid Format", "Please enter the date in MM/DD/YYYY format.")

            self.app.add_task(task_title, task_deadline)
            self.sort_listbox.insert(END, f"{task_deadline:<30} {task_title}")
            self.update_donut_chart()

            task_frame = Frame(self.todo_frame, width=400, height=50, bg='#c8d1e0', pady=5, padx=5)
            task_frame.place(x=0, y=self.task_position)

            label_frame = Frame(task_frame, width=400, height=50, bg='#c8d1e0')
            label_frame.place(x=0, y=0)

            task_title_label = Label(label_frame, text=task_title, bg='#c8d1e0', fg='black', font=("Helvetica", 12, "bold"))
            task_title_label.pack(side=LEFT, padx=5)

            task_deadline_label = Label(label_frame, text=task_deadline, bg='#c8d1e0', fg='black', font=("Helvetica", 12, "italic"))
            task_deadline_label.pack(side=RIGHT, padx=5)

            delete_button = Button(task_frame, image=self.Delete, bg='#c8d1e0', borderwidth=0, command=lambda: self.delete_task(task_title, task_deadline, task_frame))
            delete_button.image = self.Delete
            delete_button.place(x=350, y=0)

            done_button = Button(task_frame, image=self.Done, bg='#c8d1e0', borderwidth=0, command=lambda: self.check_task(task_title, task_deadline, task_frame))
            done_button.image = self.Done
            done_button.place(x=310, y=0)

            self.task_position += 60

    def reset_taskposition(self):
        self.task_position = 0

    def delete_task(self, task_title, task_deadline, task_frame):
        self.app.delete_task(task_title, task_deadline)
        task_frame.destroy()
        self.update_sort()
        self.update_donut_chart()
        self.reset_taskposition()

    def check_task(self, task_title, task_deadline, task_frame):
        self.app.check_task(task_title, task_deadline)
        task_frame.destroy()
        self.update_sort()
        self.update_donut_chart()
        self.reset_taskposition()

    def update_sort(self):
        self.sort_listbox.delete(0, tk.END)
        for task_title, task_deadline in self.app.tasks:
            formatted_text = f"{task_deadline:<30} {task_title}"
            self.sort_listbox.insert(tk.END, formatted_text)

    def sort_tasks(self, event=None):
        sort_option = self.sort_combobox.get()
        self.app.sort_tasks(sort_option)
        self.update_sort()

    def update_donut_chart(self):
        for widget in self.progress_frame.winfo_children():
            widget.destroy()

        total_tasks = len(self.app.tasks) + len(self.app.completed_tasks)
        if total_tasks == 0:
            values = [1]
            labels = ["No Tasks"]
            colors = ['#d4d6de']
        else:
            values = [len(self.app.completed_tasks), len(self.app.tasks)]
            labels = ["Completed", "Pending"]
            colors = ['#edcb46', '#d4d6de']

        fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
        wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85)

        for text in texts:
            text.set_fontsize(6.5)
        for autotext in autotexts:
            autotext.set_fontsize(8)

        center_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(center_circle)

        ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=self.progress_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.place(relx=0.5, rely=0.5, anchor='center')
        canvas.draw()

    def show_savedtasks(self):
        self.sort_listbox.delete(0, tk.END)
        for task_title, task_deadline in self.app.tasks:
            self.sort_listbox.insert(tk.END, f"{task_deadline:<30} {task_title}")

        self.sort_listbox.bind("<<ListboxSelect>>", self.on_taskselect)

    def on_taskselect(self, event):
        selected_index = self.sort_listbox.curselection()
        if selected_index:
            selected_task = self.sort_listbox.get(selected_index)
            task_deadline, task_title = selected_task.split(maxsplit=1)
            self.markascomplete_button.config(
                command=lambda: self.mark_taskcomplete(task_title.strip(), task_deadline.strip()))
            self.deletetasks_button.config(
                command=lambda: self.delete_taskfromsort(task_title.strip(), task_deadline.strip()))

    def mark_taskcomplete(self, task_title, task_deadline):
        self.app.check_task(task_title, task_deadline)
        self.update_sort()
        self.update_donut_chart()

    def delete_taskfromsort(self, task_title, task_deadline):
        self.app.delete_task(task_title, task_deadline)
        self.update_sort()
        self.update_donut_chart()

    def mark_selectedtask_complete(self):
        selected_index = self.sort_listbox.curselection()
        if selected_index:
            selected_task = self.sort_listbox.get(selected_index)
            task_deadline, task_title = selected_task.split(maxsplit=1)
            self.mark_taskcomplete(task_title.strip(), task_deadline.strip())

    def delete_selectedtask(self):
        selected_index = self.sort_listbox.curselection()
        if selected_index:
            selected_task = self.sort_listbox.get(selected_index)
            task_deadline, task_title = selected_task.split(maxsplit=1)
            self.delete_taskfromsort(task_title.strip(), task_deadline.strip())

    def reset_database(self):
        self.app.reset_database()
        self.update_sort()
        self.update_donut_chart()
        self.reset_taskposition()

    def round_rectangle(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def frame1_design(self, parent_frame, x, y, width_size, height_size, bg_color, corner_radius=25):
        self.canvas = Canvas(parent_frame, width=width_size, height=height_size, highlightthickness=0, bg='#ecedf4')
        self.canvas.place(x=x, y=y)
        self.round_rectangle(self.canvas, 0, 0, width_size, height_size, radius=corner_radius, fill=bg_color)
        return self.canvas

    def AllFrame(self, width, height, x, y):
        self.frame = Frame(width=width, height=height, border=0, bg="white")
        self.frame.place(x=x, y=y)
        return self.frame

    def MainLabel(self, width, x, y):
        self.frame = Frame(width=width, height=32, border=0, bg='#a6a6a6')
        self.frame.place(x=x, y=y)
        return self.frame

    def Heading(self, x, y, text):
        label = tk.Label(text=text, font=("Century Gothic", 20, "bold"), bg='#a6a6a6', fg='black')
        label.place(x=x, y=y)
        return label

    def insert_donut_chart(self):
        self.update_donut_chart()

    # database
class ToDoAppDatabase:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                                id INTEGER PRIMARY KEY,
                                title TEXT NOT NULL,
                                deadline TEXT NOT NULL,
                                completed INTEGER DEFAULT 0
                            )''')
        self.connection.commit()

    def insert_task(self, task_title, task_deadline):
        self.cursor.execute('INSERT INTO tasks (title, deadline) VALUES (?, ?)', (task_title, task_deadline))
        self.connection.commit()

    def fetch_tasks(self):
        self.cursor.execute('SELECT title, deadline FROM tasks WHERE completed = 0')
        return self.cursor.fetchall()

    def fetch_completed_tasks(self):
        self.cursor.execute('SELECT title, deadline FROM tasks WHERE completed = 1')
        return self.cursor.fetchall()

    def mark_task_completed(self, task_title, task_deadline):
        self.cursor.execute('UPDATE tasks SET completed = 1 WHERE title = ? AND deadline = ?', (task_title, task_deadline))
        self.connection.commit()

    def reset_database(self):
        self.cursor.execute('DELETE FROM tasks')
        self.connection.commit()

    def __del__(self):
        self.connection.close()


if __name__ == "__main__":
    db = ToDoAppDatabase('tasks.db')
    app = ToDoApp(db)

    root = tk.Tk()
    gui = ToDoAppGUI(root, app)
    root.mainloop()