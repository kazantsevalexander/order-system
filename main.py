import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3


def init_db():
    conn = sqlite3.connect('business_orders.db')
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    order_details TEXT NOT NULL,
    status TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def add_order():
    if not customer_name_entry.get().strip() or not order_details_entry.get().strip():
        messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля!")
        return

    conn = sqlite3.connect('business_orders.db')
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO orders (customer_name, order_details, status) VALUES (?, ?, 'Новый')",
        (customer_name_entry.get(), order_details_entry.get()))

    conn.commit()
    conn.close()

    customer_name_entry.delete(0, tk.END)
    order_details_entry.delete(0, tk.END)

    view_orders()


def view_orders():
    for i in tree.get_children():
        tree.delete(i)

    conn = sqlite3.connect('business_orders.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM orders")
    rows = cur.fetchall()

    for row in rows:
        # Используем тег для визуального выделения завершённых заказов
        if row[3] == "Завершён":
            tree.insert("", tk.END, values=row, tags=("completed",))
        else:
            tree.insert("", tk.END, values=row)
    conn.close()


def complete_order():
    selected_item = tree.selection()
    if selected_item:
        item_id = selected_item[0]
        order_id = tree.item(item_id, 'values')[0]

        conn = sqlite3.connect('business_orders.db')
        cur = conn.cursor()

        cur.execute("UPDATE orders SET status='Завершён' WHERE id=?", (order_id,))

        conn.commit()
        conn.close()

        view_orders()
    else:
        messagebox.showwarning("Предупреждение", "Выберите заказ для завершения")


def delete_order():
    selected_item = tree.selection()
    if selected_item:
        item_id = selected_item[0]
        order_id = tree.item(item_id, 'values')[0]

        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот заказ?")
        if confirm:
            conn = sqlite3.connect('business_orders.db')
            cur = conn.cursor()

            cur.execute("DELETE FROM orders WHERE id=?", (order_id,))

            conn.commit()
            conn.close()

            view_orders()
    else:
        messagebox.showwarning("Предупреждение", "Выберите заказ для удаления")


app = tk.Tk()
app.title("Система управления заказами")
app.geometry("1200x800")  # Увеличено в 2 раза
app.resizable(False, False)

# Создание основной рамки
main_frame = tk.Frame(app, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# Рамка для ввода данных
input_frame = tk.LabelFrame(main_frame, text="Новый заказ", padx=10, pady=10)
input_frame.pack(fill=tk.X, pady=10)

tk.Label(input_frame, text="Имя клиента").grid(row=0, column=0, sticky="w", pady=5)
customer_name_entry = tk.Entry(input_frame, width=40)
customer_name_entry.grid(row=0, column=1, pady=5)

tk.Label(input_frame, text="Детали заказа").grid(row=1, column=0, sticky="w", pady=5)
order_details_entry = tk.Entry(input_frame, width=40)
order_details_entry.grid(row=1, column=1, pady=5)

add_button = tk.Button(input_frame, text="Добавить заказ", command=add_order, width=20)
add_button.grid(row=2, column=0, columnspan=2, pady=10)

# Рамка для управления заказами
action_frame = tk.Frame(main_frame, pady=10)
action_frame.pack(fill=tk.X)

complete_button = tk.Button(action_frame, text="Завершить заказ", command=complete_order, width=20)
complete_button.pack(side=tk.LEFT, padx=5)

delete_button = tk.Button(action_frame, text="Удалить заказ", command=delete_order, width=20)
delete_button.pack(side=tk.LEFT, padx=5)

# Рамка для отображения заказов
tree_frame = tk.LabelFrame(main_frame, text="Список заказов", padx=10, pady=10)
tree_frame.pack(fill=tk.BOTH, expand=True)

# Добавление прокрутки
scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

columns = ("id", "customer_name", "order_details", "status")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20, yscrollcommand=scrollbar.set)
scrollbar.config(command=tree.yview)

for column in columns:
    tree.heading(column, text=column)
    tree.column(column, anchor="center", width=200)

# Добавление стилей для завершённых заказов
tree.tag_configure("completed", background="#d3ffd3")  # Светло-зелёный фон для завершённых заказов

tree.pack(fill=tk.BOTH, expand=True)

# Инициализация и отображение
init_db()
view_orders()
app.mainloop()
