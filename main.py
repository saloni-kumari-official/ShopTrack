import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime


# =========================================================
# DATABASE
# =========================================================

connection = sqlite3.connect("shoptrack.db")
cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    minimum_stock INTEGER NOT NULL,
    supplier_name TEXT NOT NULL,
    supplier_phone TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    item_name TEXT,
    quantity INTEGER,
    supplier_name TEXT,
    supplier_phone TEXT,
    order_date TEXT,
    status TEXT DEFAULT 'Ordered'
)
""")

connection.commit()


# =========================================================
# COLORS
# =========================================================

BG = "#F5F7FB"
SIDEBAR = "#172033"
SIDEBAR_HOVER = "#24324A"

WHITE = "#FFFFFF"

PRIMARY = "#2563EB"
PRIMARY_DARK = "#1D4ED8"

TEXT = "#172033"
MUTED = "#64748B"

SUCCESS = "#16A34A"
WARNING = "#F59E0B"
DANGER = "#DC2626"

BORDER = "#CBD5E1"


# =========================================================
# MAIN WINDOW
# =========================================================

window = tk.Tk()

window.title("ShopTrack | Inventory Manager")
window.geometry("1200x720")

window.configure(
    bg=BG
)

window.resizable(
    False,
    False
)


# =========================================================
# BUTTON FUNCTION
# =========================================================

def create_button(
    parent,
    text,
    command,
    bg=PRIMARY
):

    button = tk.Button(
        parent,
        text=text,
        command=command,

        bg=bg,
        fg=WHITE,

        activebackground=PRIMARY_DARK,
        activeforeground=WHITE,

        font=("Segoe UI", 10, "bold"),

        relief="flat",
        bd=0,

        cursor="hand2",

        padx=15,
        pady=10
    )

    return button


# =========================================================
# PROFESSIONAL TABLE FUNCTION
# =========================================================

def create_table(
    parent,
    columns,
    rows,
    widths=None
):

    # Main table frame

    table_frame = tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=10
    )


    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    for column_index, column_name in enumerate(columns):

        width = 15

        if widths:
            width = widths[column_index]

        header = tk.Label(
            table_frame,

            text=column_name,

            bg=SIDEBAR,
            fg=WHITE,

            font=(
                "Segoe UI",
                10,
                "bold"
            ),

            width=width,
            height=2,

            relief="solid",
            bd=1,

            anchor="center"
        )

        header.grid(
            row=0,
            column=column_index,

            sticky="nsew"
        )


    # -----------------------------------------------------
    # DATA ROWS
    # -----------------------------------------------------

    for row_index, row in enumerate(
        rows,
        start=1
    ):

        for column_index, value in enumerate(row):

            text_color = TEXT


            # Low stock quantity red

            if (
                len(row) >= 4
                and column_index == 2
            ):

                try:

                    current_quantity = int(
                        row[2]
                    )

                    minimum_quantity = int(
                        row[3]
                    )

                    if (
                        current_quantity
                        <=
                        minimum_quantity
                    ):

                        text_color = DANGER

                except:

                    pass


            cell = tk.Label(
                table_frame,

                text=value,

                bg=WHITE,
                fg=text_color,

                font=(
                    "Segoe UI",
                    10
                ),

                height=2,

                relief="solid",
                bd=1,

                anchor="center"
            )

            cell.grid(
                row=row_index,
                column=column_index,

                sticky="nsew"
            )


    # -----------------------------------------------------
    # COLUMN CONFIGURATION
    # -----------------------------------------------------

    for column_index in range(
        len(columns)
    ):

        table_frame.grid_columnconfigure(
            column_index,
            weight=1
        )


    # -----------------------------------------------------
    # EMPTY TABLE
    # -----------------------------------------------------

    if len(rows) == 0:

        empty_label = tk.Label(
            table_frame,

            text="No data available.",

            bg=WHITE,
            fg=MUTED,

            font=(
                "Segoe UI",
                11
            )
        )

        empty_label.grid(
            row=1,
            column=0,

            columnspan=len(columns),

            pady=30
        )


    return table_frame


# =========================================================
# DASHBOARD DATA
# =========================================================

def get_total_items():

    cursor.execute(
        "SELECT COUNT(*) FROM items"
    )

    return cursor.fetchone()[0]


def get_low_stock():

    cursor.execute("""
        SELECT COUNT(*)
        FROM items
        WHERE quantity <= minimum_stock
    """)

    return cursor.fetchone()[0]


def get_total_orders():

    cursor.execute(
        "SELECT COUNT(*) FROM orders"
    )

    return cursor.fetchone()[0]


def update_dashboard():

    total_label.config(
        text=str(
            get_total_items()
        )
    )

    low_label.config(
        text=str(
            get_low_stock()
        )
    )

    orders_label.config(
        text=str(
            get_total_orders()
        )
    )


# =========================================================
# VALIDATION
# =========================================================

def validate_item(
    name,
    quantity,
    minimum,
    supplier,
    phone
):

    if not name:

        messagebox.showerror(
            "Error",
            "Please enter item name."
        )

        return False


    if not quantity.isdigit():

        messagebox.showerror(
            "Error",
            "Quantity must be a number."
        )

        return False


    if not minimum.isdigit():

        messagebox.showerror(
            "Error",
            "Minimum stock must be a number."
        )

        return False


    if not supplier:

        messagebox.showerror(
            "Error",
            "Please enter supplier name."
        )

        return False


    if (
        not phone.isdigit()
        or len(phone) != 10
    ):

        messagebox.showerror(
            "Error",
            "Phone number must contain 10 digits."
        )

        return False


    return True


# =========================================================
# ADD ITEM
# =========================================================

def add_item():

    popup = tk.Toplevel(
        window
    )

    popup.title(
        "Add New Item"
    )

    popup.geometry(
        "450x540"
    )

    popup.configure(
        bg=BG
    )

    popup.resizable(
        False,
        False
    )


    tk.Label(
        popup,

        text="Add New Item",

        bg=BG,
        fg=TEXT,

        font=(
            "Segoe UI",
            20,
            "bold"
        )
    ).pack(
        pady=(25, 20)
    )


    fields = []


    labels = [
        "Item Name",
        "Current Quantity",
        "Minimum Stock",
        "Supplier Name",
        "Supplier Phone"
    ]


    for label_text in labels:

        tk.Label(
            popup,

            text=label_text,

            bg=BG,
            fg=TEXT,

            font=(
                "Segoe UI",
                10,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=45
        )


        entry = tk.Entry(
            popup,

            font=(
                "Segoe UI",
                11
            ),

            relief="solid",
            bd=1
        )


        entry.pack(
            fill="x",
            padx=45,

            pady=(
                5,
                12
            ),

            ipady=6
        )


        fields.append(
            entry
        )


    def save():

        name = fields[0].get().strip()

        quantity = fields[1].get().strip()

        minimum = fields[2].get().strip()

        supplier = fields[3].get().strip()

        phone = fields[4].get().strip()


        if not validate_item(
            name,
            quantity,
            minimum,
            supplier,
            phone
        ):

            return


        cursor.execute(
            """
            SELECT id
            FROM items
            WHERE LOWER(item_name)
            =
            LOWER(?)
            """,

            (name,)
        )


        if cursor.fetchone():

            messagebox.showerror(
                "Duplicate Item",
                "This item already exists."
            )

            return


        cursor.execute(
            """
            INSERT INTO items
            (
                item_name,
                quantity,
                minimum_stock,
                supplier_name,
                supplier_phone
            )

            VALUES (?, ?, ?, ?, ?)
            """,

            (
                name,
                int(quantity),
                int(minimum),
                supplier,
                phone
            )
        )


        connection.commit()


        messagebox.showinfo(
            "Success",
            "Item added successfully!"
        )


        popup.destroy()


        update_dashboard()


    create_button(
        popup,
        "Save Item",
        save
    ).pack(
        pady=15
    )


# =========================================================
# VIEW INVENTORY
# =========================================================

def view_items():

    popup = tk.Toplevel(
        window
    )

    popup.title(
        "All Inventory Items"
    )

    popup.geometry(
        "1050x600"
    )

    popup.configure(
        bg=BG
    )


    tk.Label(
        popup,

        text="All Inventory Items",

        bg=BG,
        fg=TEXT,

        font=(
            "Segoe UI",
            20,
            "bold"
        )
    ).pack(
        anchor="w",

        padx=25,

        pady=(
            25,
            20
        )
    )


    columns = (
        "ID",
        "Item",
        "Quantity",
        "Minimum",
        "Supplier",
        "Phone"
    )


    cursor.execute(
        """
        SELECT
            id,
            item_name,
            quantity,
            minimum_stock,
            supplier_name,
            supplier_phone

        FROM items

        ORDER BY id DESC
        """
    )


    rows = cursor.fetchall()


    create_table(
        popup,

        columns,

        rows,

        [
            8,
            20,
            12,
            12,
            20,
            18
        ]
    )


# =========================================================
# EDIT ITEM
# =========================================================

def edit_item():

    popup = tk.Toplevel(
        window
    )

    popup.title(
        "Edit Item"
    )

    popup.geometry(
        "450x600"
    )

    popup.configure(
        bg=BG
    )

    popup.resizable(
        False,
        False
    )


    tk.Label(
        popup,

        text="Edit Item",

        bg=BG,
        fg=TEXT,

        font=(
            "Segoe UI",
            20,
            "bold"
        )
    ).pack(
        pady=20
    )


    labels = [
        "Item ID",
        "Item Name",
        "Quantity",
        "Minimum Stock",
        "Supplier Name",
        "Supplier Phone"
    ]


    entries = []


    for label_text in labels:

        tk.Label(
            popup,

            text=label_text,

            bg=BG,
            fg=TEXT,

            font=(
                "Segoe UI",
                10,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=45
        )


        entry = tk.Entry(
            popup,

            font=(
                "Segoe UI",
                11
            ),

            relief="solid",
            bd=1
        )


        entry.pack(
            fill="x",

            padx=45,

            pady=(
                4,
                8
            ),

            ipady=5
        )


        entries.append(
            entry
        )


    def update_item():

        item_id = entries[0].get().strip()

        name = entries[1].get().strip()

        quantity = entries[2].get().strip()

        minimum = entries[3].get().strip()

        supplier = entries[4].get().strip()

        phone = entries[5].get().strip()


        if not item_id.isdigit():

            messagebox.showerror(
                "Error",
                "Invalid Item ID."
            )

            return


        if not validate_item(
            name,
            quantity,
            minimum,
            supplier,
            phone
        ):

            return


        cursor.execute(
            """
            SELECT id
            FROM items
            WHERE id = ?
            """,

            (int(item_id),)
        )


        if not cursor.fetchone():

            messagebox.showerror(
                "Error",
                "Item not found."
            )

            return


        cursor.execute(
            """
            UPDATE items

            SET
                item_name = ?,
                quantity = ?,
                minimum_stock = ?,
                supplier_name = ?,
                supplier_phone = ?

            WHERE id = ?
            """,

            (
                name,
                int(quantity),
                int(minimum),
                supplier,
                phone,
                int(item_id)
            )
        )


        connection.commit()


        messagebox.showinfo(
            "Success",
            "Item updated successfully!"
        )


        popup.destroy()


        update_dashboard()


    create_button(
        popup,
        "Save Changes",
        update_item
    ).pack(
        pady=20
    )


# =========================================================
# UPDATE STOCK
# =========================================================

def update_stock():

    popup = tk.Toplevel(
        window
    )

    popup.title(
        "Update Stock"
    )

    popup.geometry(
        "400x330"
    )

    popup.configure(
        bg=BG
    )


    tk.Label(
        popup,

        text="Update Stock",

        bg=BG,
        fg=TEXT,

        font=(
            "Segoe UI",
            20,
            "bold"
        )
    ).pack(
        pady=25
    )


    tk.Label(
        popup,

        text="Item ID",

        bg=BG,
        fg=TEXT
    ).pack()


    id_entry = tk.Entry(
        popup,

        font=(
            "Segoe UI",
            11
        )
    )


    id_entry.pack(
        padx=50,
        fill="x",

        pady=8,

        ipady=5
    )


    tk.Label(
        popup,

        text="New Quantity",

        bg=BG,
        fg=TEXT
    ).pack()


    quantity_entry = tk.Entry(
        popup,

        font=(
            "Segoe UI",
            11
        )
    )


    quantity_entry.pack(
        padx=50,
        fill="x",

        pady=8,

        ipady=5
    )


    def update():

        item_id = id_entry.get().strip()

        quantity = quantity_entry.get().strip()


        if not item_id.isdigit():

            messagebox.showerror(
                "Error",
                "Invalid Item ID."
            )

            return


        if not quantity.isdigit():

            messagebox.showerror(
                "Error",
                "Quantity must be a number."
            )

            return


        cursor.execute(
            """
            SELECT id
            FROM items
            WHERE id = ?
            """,

            (int(item_id),)
        )


        if not cursor.fetchone():

            messagebox.showerror(
                "Error",
                "Item not found."
            )

            return


        cursor.execute(
            """
            UPDATE items

            SET quantity = ?

            WHERE id = ?
            """,

            (
                int(quantity),
                int(item_id)
            )
        )


        connection.commit()


        messagebox.showinfo(
            "Success",
            "Stock updated successfully!"
        )


        popup.destroy()


        update_dashboard()


    create_button(
        popup,

        "Update Stock",

        update
    ).pack(
        pady=20
    )


# =========================================================
# DELETE ITEM
# =========================================================

def delete_item():

    popup = tk.Toplevel(
        window
    )

    popup.title(
        "Delete Item"
    )

    popup.geometry(
        "380x280"
    )

    popup.configure(
        bg=BG
    )


    tk.Label(
        popup,

        text="Delete Item",

        bg=BG,
        fg=DANGER,

        font=(
            "Segoe UI",
            20,
            "bold"
        )
    ).pack(
        pady=25
    )


    tk.Label(
        popup,

        text="Enter Item ID",

        bg=BG,
        fg=TEXT
    ).pack()


    id_entry = tk.Entry(
        popup,

        font=(
            "Segoe UI",
            11
        )
    )


    id_entry.pack(
        padx=50,

        fill="x",

        pady=10,

        ipady=5
    )


    def delete():

        item_id = id_entry.get().strip()


        if not item_id.isdigit():

            messagebox.showerror(
                "Error",
                "Invalid Item ID."
            )

            return


        cursor.execute(
            """
            SELECT item_name
            FROM items
            WHERE id = ?
            """,

            (int(item_id),)
        )


        result = cursor.fetchone()


        if not result:

            messagebox.showerror(
                "Error",
                "Item not found."
            )

            return


        confirm = messagebox.askyesno(
            "Confirm Delete",

            f"Delete {result[0]}?"
        )


        if confirm:

            cursor.execute(
                """
                DELETE FROM items
                WHERE id = ?
                """,

                (int(item_id),)
            )


            connection.commit()


            messagebox.showinfo(
                "Success",
                "Item deleted successfully."
            )


            popup.destroy()


            update_dashboard()


    create_button(
        popup,

        "Delete Item",

        delete,

        DANGER
    ).pack(
        pady=15
    )


# =========================================================
# SEARCH
# =========================================================

def search_inventory():

    text = search_entry.get().strip()


    if not text:

        messagebox.showinfo(
            "Search",
            "Enter an item name."
        )

        return


    popup = tk.Toplevel(
        window
    )

    popup.title(
        "Search Results"
    )

    popup.geometry(
        "1050x550"
    )

    popup.configure(
        bg=BG
    )


    tk.Label(
        popup,

        text=f"Search Results: {text}",

        bg=BG,
        fg=TEXT,

        font=(
            "Segoe UI",
            20,
            "bold"
        )
    ).pack(
        anchor="w",

        padx=25,

        pady=20
    )


    columns = (
        "ID",
        "Item",
        "Quantity",
        "Minimum",
        "Supplier",
        "Phone"
    )


    cursor.execute(
        """
        SELECT
            id,
            item_name,
            quantity,
            minimum_stock,
            supplier_name,
            supplier_phone

        FROM items

        WHERE item_name LIKE ?

        ORDER BY id DESC
        """,

        (
            "%" + text + "%",
        )
    )


    rows = cursor.fetchall()


    create_table(
        popup,

        columns,

        rows,

        [
            8,
            20,
            12,
            12,
            20,
            18
        ]
    )


# =========================================================
# LOW STOCK
# =========================================================

def low_stock_items():

    popup = tk.Toplevel(
        window
    )

    popup.title(
        "Low Stock Items"
    )

    popup.geometry(
        "950x550"
    )

    popup.configure(
        bg=BG
    )


    tk.Label(
        popup,

        text="Low Stock Items",

        bg=BG,
        fg=DANGER,

        font=(
            "Segoe UI",
            20,
            "bold"
        )
    ).pack(
        anchor="w",

        padx=25,

        pady=20
    )


    columns = (
        "ID",
        "Item",
        "Current",
        "Minimum",
        "Need",
        "Supplier"
    )


    cursor.execute(
        """
        SELECT
            id,
            item_name,
            quantity,
            minimum_stock,
            supplier_name

        FROM items

        WHERE quantity <= minimum_stock
        """
    )


    raw_rows = cursor.fetchall()


    rows = []


    for row in raw_rows:

        need = (
            row[3] - row[2]
        )


        rows.append(
            (
                row[0],
                row[1],
                row[2],
                row[3],
                need,
                row[4]
            )
        )


    create_table(
        popup,

        columns,

        rows,

        [
            8,
            20,
            12,
            12,
            12,
            20
        ]
    )


# =========================================================
# ITEMS TO ORDER
# =========================================================

def order_items():

    popup = tk.Toplevel(
        window
    )

    popup.title(
        "Items to Order"
    )

    popup.geometry(
        "950x600"
    )

    popup.configure(
        bg=BG
    )


    tk.Label(
        popup,

        text="Items to Order",

        bg=BG,
        fg=TEXT,

        font=(
            "Segoe UI",
            20,
            "bold"
        )
    ).pack(
        anchor="w",

        padx=25,

        pady=20
    )


    columns = (
        "ID",
        "Item",
        "Current",
        "Minimum",
        "Order Qty",
        "Supplier"
    )


    cursor.execute(
        """
        SELECT
            id,
            item_name,
            quantity,
            minimum_stock,
            supplier_name

        FROM items

        WHERE quantity <= minimum_stock
        """
    )


    raw_rows = cursor.fetchall()


    rows = []


    for row in raw_rows:

        order_quantity = (
            row[3] - row[2]
        )


        rows.append(
            (
                row[0],
                row[1],
                row[2],
                row[3],
                order_quantity,
                row[4]
            )
        )


    create_table(
        popup,

        columns,

        rows,

        [
            8,
            20,
            12,
            12,
            14,
            20
        ]
    )


    def mark_ordered():

        if len(rows) == 0:

            messagebox.showinfo(
                "Orders",
                "There are no items to order."
            )

            return


        order_window = tk.Toplevel(
            popup
        )

        order_window.title(
            "Place Order"
        )

        order_window.geometry(
            "400x300"
        )

        order_window.configure(
            bg=BG
        )


        tk.Label(
            order_window,

            text="Enter Item ID",

            bg=BG,
            fg=TEXT
        ).pack(
            pady=(30, 5)
        )


        id_entry = tk.Entry(
            order_window,

            font=(
                "Segoe UI",
                11
            )
        )


        id_entry.pack(
            padx=50,

            fill="x",

            ipady=5
        )


        def place_order():

            item_id = id_entry.get().strip()


            if not item_id.isdigit():

                messagebox.showerror(
                    "Error",
                    "Enter a valid Item ID."
                )

                return


            cursor.execute(
                """
                SELECT
                    item_name,
                    quantity,
                    minimum_stock,
                    supplier_name,
                    supplier_phone

                FROM items

                WHERE id = ?
                """,

                (int(item_id),)
            )


            item = cursor.fetchone()


            if not item:

                messagebox.showerror(
                    "Error",
                    "Item not found."
                )

                return


            if item[1] > item[2]:

                messagebox.showinfo(
                    "Stock OK",
                    "This item does not need ordering."
                )

                return


            order_quantity = (
                item[2] - item[1]
            )


            order_date = datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )


            cursor.execute(
                """
                INSERT INTO orders
                (
                    item_id,
                    item_name,
                    quantity,
                    supplier_name,
                    supplier_phone,
                    order_date,
                    status
                )

                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,

                (
                    int(item_id),
                    item[0],
                    order_quantity,
                    item[3],
                    item[4],
                    order_date,
                    "Ordered"
                )
            )


            connection.commit()


            messagebox.showinfo(
                "Success",

                f"Order placed for {item[0]}!"
            )


            order_window.destroy()

            popup.destroy()

            update_dashboard()


        create_button(
            order_window,

            "Place Order",

            place_order
        ).pack(
            pady=25
        )


    create_button(
        popup,

        "🛒  Place Order",
        mark_ordered
    ).pack(
        pady=15
    )


# =========================================================
# ORDER HISTORY
# =========================================================

def order_history():

    popup = tk.Toplevel(
        window
    )

    popup.title(
        "Order History"
    )

    popup.geometry(
        "1050x600"
    )

    popup.configure(
        bg=BG
    )


    tk.Label(
        popup,

        text="Order History",

        bg=BG,
        fg=TEXT,

        font=(
            "Segoe UI",
            20,
            "bold"
        )
    ).pack(
        anchor="w",

        padx=25,

        pady=20
    )


    columns = (
        "ID",
        "Item",
        "Quantity",
        "Supplier",
        "Phone",
        "Date",
        "Status"
    )


    cursor.execute(
        """
        SELECT
            id,
            item_name,
            quantity,
            supplier_name,
            supplier_phone,
            order_date,
            status

        FROM orders

        ORDER BY id DESC
        """
    )


    rows = cursor.fetchall()


    create_table(
        popup,

        columns,

        rows,

        [
            7,
            17,
            10,
            17,
            16,
            18,
            12
        ]
    )


# =========================================================
# SIDEBAR
# =========================================================

sidebar = tk.Frame(
    window,

    bg=SIDEBAR,

    width=240
)


sidebar.pack(
    side="left",

    fill="y"
)


sidebar.pack_propagate(
    False
)


tk.Label(
    sidebar,

    text="SHOPTRACK",

    bg=SIDEBAR,
    fg=WHITE,

    font=(
        "Segoe UI",
        23,
        "bold"
    )
).pack(
    pady=(35, 5)
)


tk.Label(
    sidebar,

    text="Inventory Manager",

    bg=SIDEBAR,
    fg="#94A3B8",

    font=(
        "Segoe UI",
        9
    )
).pack(
    pady=(0, 35)
)


def sidebar_button(
    text,
    command
):

    button = tk.Button(
        sidebar,

        text=text,

        command=command,

        bg=SIDEBAR,
        fg="#CBD5E1",

        activebackground=SIDEBAR_HOVER,
        activeforeground=WHITE,

        font=(
            "Segoe UI",
            10
        ),

        anchor="w",

        relief="flat",
        bd=0,

        cursor="hand2",

        padx=25,
        pady=13
    )


    button.pack(
        fill="x",

        pady=2
    )


sidebar_button(
    "＋  Add Item",
    add_item
)


sidebar_button(
    "▣  View Inventory",
    view_items
)


sidebar_button(
    "✎  Edit Item",
    edit_item
)


sidebar_button(
    "↻  Update Stock",
    update_stock
)


sidebar_button(
    "⚠  Low Stock",
    low_stock_items
)


sidebar_button(
    "🛒  Items to Order",
    order_items
)


sidebar_button(
    "◷  Order History",
    order_history
)


sidebar_button(
    "✕  Delete Item",
    delete_item
)


# =========================================================
# CONTENT AREA
# =========================================================

content = tk.Frame(
    window,

    bg=BG
)


content.pack(
    side="left",

    fill="both",

    expand=True
)


# =========================================================
# HEADER
# =========================================================

header = tk.Frame(
    content,

    bg=BG
)


header.pack(
    fill="x",

    padx=35,

    pady=(30, 10)
)


tk.Label(
    header,

    text="Dashboard",

    bg=BG,
    fg=TEXT,

    font=(
        "Segoe UI",
        28,
        "bold"
    )
).pack(
    anchor="w"
)


tk.Label(
    header,

    text="Manage your shop inventory and orders",

    bg=BG,
    fg=MUTED,

    font=(
        "Segoe UI",
        11
    )
).pack(
    anchor="w",

    pady=3
)


# =========================================================
# DASHBOARD CARDS
# =========================================================

cards = tk.Frame(
    content,

    bg=BG
)


cards.pack(
    fill="x",

    padx=35,

    pady=25
)


def create_card(
    parent,
    title,
    value,
    color
):

    card = tk.Frame(
        parent,

        bg=WHITE,

        width=220,
        height=115,

        highlightbackground=BORDER,
        highlightthickness=1
    )


    card.pack_propagate(
        False
    )


    tk.Label(
        card,

        text=title,

        bg=WHITE,
        fg=MUTED,

        font=(
            "Segoe UI",
            10
        )
    ).pack(
        anchor="w",

        padx=20,

        pady=(18, 3)
    )


    label = tk.Label(
        card,

        text=value,

        bg=WHITE,
        fg=color,

        font=(
            "Segoe UI",
            24,
            "bold"
        )
    )


    label.pack(
        anchor="w",

        padx=20
    )


    return card, label


card1, total_label = create_card(
    cards,

    "TOTAL ITEMS",

    "0",

    PRIMARY
)


card1.pack(
    side="left",

    padx=(0, 15)
)


card2, low_label = create_card(
    cards,

    "LOW STOCK",

    "0",

    WARNING
)


card2.pack(
    side="left",

    padx=15
)


card3, orders_label = create_card(
    cards,

    "TOTAL ORDERS",

    "0",

    SUCCESS
)


card3.pack(
    side="left",

    padx=15
)


# =========================================================
# QUICK ACTIONS
# =========================================================

tk.Label(
    content,

    text="Quick Actions",

    bg=BG,
    fg=TEXT,

    font=(
        "Segoe UI",
        17,
        "bold"
    )
).pack(
    anchor="w",

    padx=35,

    pady=(15, 12)
)


actions = tk.Frame(
    content,

    bg=BG
)


actions.pack(
    anchor="w",

    padx=35
)


create_button(
    actions,

    "＋  Add New Item",

    add_item
).grid(
    row=0,
    column=0,

    padx=(0, 10)
)


create_button(
    actions,

    "▣  View Inventory",

    view_items,

    "#475569"
).grid(
    row=0,
    column=1,

    padx=10
)


create_button(
    actions,

    "🛒  Check Orders",

    order_items,

    "#7C3AED"
).grid(
    row=0,
    column=2,

    padx=10
)


# =========================================================
# SEARCH
# =========================================================

search_frame = tk.Frame(
    content,

    bg=WHITE,

    highlightbackground=BORDER,
    highlightthickness=1
)


search_frame.pack(
    fill="x",

    padx=35,

    pady=35,

    ipady=5
)


tk.Label(
    search_frame,

    text="Search Inventory",

    bg=WHITE,
    fg=TEXT,

    font=(
        "Segoe UI",
        11,
        "bold"
    )
).pack(
    side="left",

    padx=20
)


search_entry = tk.Entry(
    search_frame,

    width=35,

    font=(
        "Segoe UI",
        11
    ),

    relief="flat",

    bg="#F8FAFC"
)


search_entry.pack(
    side="left",

    padx=10,

    ipady=7
)


create_button(
    search_frame,

    "Search",

    search_inventory
).pack(
    side="right",

    padx=10
)


# =========================================================
# INITIAL DASHBOARD
# =========================================================

update_dashboard()


# =========================================================
# CLOSE DATABASE SAFELY
# =========================================================

def close_app():

    connection.close()

    window.destroy()


window.protocol(
    "WM_DELETE_WINDOW",
    close_app
)


# =========================================================
# START APPLICATION
# =========================================================

window.mainloop()
