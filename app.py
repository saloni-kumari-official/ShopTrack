from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
import os
import hmac
import secrets
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-development-only-change-me")
APP_PASSWORD = os.environ.get("APP_PASSWORD")
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "").lower() == "true")

DATABASE = os.environ.get("SHOPTRACK_DATABASE", "shoptrack.db")


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

def init_database():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL UNIQUE,
            quantity INTEGER NOT NULL,
            minimum_stock INTEGER NOT NULL,
            supplier_name TEXT NOT NULL,
            supplier_phone TEXT NOT NULL
        )
    """)

    connection.execute("""
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
    connection.close()


# =========================================================
# DASHBOARD
# =========================================================

@app.before_request
def protect_app():
    if request.method == "POST":
        submitted_token = request.form.get("_csrf_token", "")
        expected_token = session.get("_csrf_token", "")
        if not submitted_token or not expected_token or not hmac.compare_digest(submitted_token, expected_token):
            abort(400)

    if request.endpoint in {"login", "static"}:
        return
    if not APP_PASSWORD:
        if os.environ.get("RENDER"):
            abort(503)
        return

    if not session.get("authenticated"):
        return redirect(url_for("login", next=request.full_path))


@app.context_processor
def provide_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)
    return {"csrf_token": session["_csrf_token"]}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        candidate = request.form.get("password", "")
        if APP_PASSWORD and hmac.compare_digest(candidate, APP_PASSWORD):
            session["authenticated"] = True
            destination = request.form.get("next", "")
            if not destination.startswith("/") or destination.startswith("//"):
                destination = url_for("home")
            return redirect(destination)
        flash("Password sahi nahi hai.", "error")
    return render_template("login.html", next=request.args.get("next", ""))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def home():

    connection = get_db_connection()

    total_items = connection.execute(
        "SELECT COUNT(*) FROM items"
    ).fetchone()[0]

    low_stock = connection.execute(
        """
        SELECT COUNT(*)
        FROM items
        WHERE quantity <= minimum_stock
        """
    ).fetchone()[0]

    total_orders = connection.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    recent_orders = connection.execute(
        """
        SELECT *
        FROM orders
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        total_items=total_items,
        low_stock=low_stock,
        total_orders=total_orders,
        recent_orders=recent_orders
    )


# =========================================================
# ADD ITEM
# =========================================================

@app.route("/add-item", methods=["GET", "POST"])
def add_item():

    if request.method == "POST":

        item_name = request.form["item_name"].strip()
        quantity = request.form["quantity"].strip()
        minimum_stock = request.form["minimum_stock"].strip()
        supplier_name = request.form["supplier_name"].strip()
        supplier_phone = request.form["supplier_phone"].strip()

        if not item_name:
            flash("Item name is required.", "error")
            return redirect(url_for("add_item"))

        if not quantity.isdigit():
            flash("Quantity must be a number.", "error")
            return redirect(url_for("add_item"))

        if not minimum_stock.isdigit():
            flash("Minimum stock must be a number.", "error")
            return redirect(url_for("add_item"))

        if not supplier_phone.isdigit() or len(supplier_phone) != 10:
            flash("Phone number must contain 10 digits.", "error")
            return redirect(url_for("add_item"))

        connection = get_db_connection()

        try:

            connection.execute(
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
                    item_name,
                    int(quantity),
                    int(minimum_stock),
                    supplier_name,
                    supplier_phone
                )
            )

            connection.commit()

            flash("Item added successfully!", "success")

        except sqlite3.IntegrityError:

            flash("This item already exists.", "error")

        finally:

            connection.close()

        return redirect(url_for("inventory"))

    return render_template("add_item.html")


# =========================================================
# INVENTORY
# =========================================================

@app.route("/inventory")
def inventory():

    connection = get_db_connection()

    items = connection.execute(
        """
        SELECT *
        FROM items
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "inventory.html",
        items=items
    )


# =========================================================
# SEARCH
# =========================================================

@app.route("/search")
def search():

    search_text = request.args.get(
        "q",
        ""
    ).strip()

    connection = get_db_connection()

    if search_text:

        items = connection.execute(
            """
            SELECT *
            FROM items
            WHERE item_name LIKE ?
            ORDER BY id DESC
            """,
            ("%" + search_text + "%",)
        ).fetchall()

    else:

        items = []

    connection.close()

    return render_template(
        "search.html",
        items=items,
        search_text=search_text
    )


# =========================================================
# EDIT ITEM
# =========================================================

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):

    connection = get_db_connection()

    item = connection.execute(
        """
        SELECT *
        FROM items
        WHERE id = ?
        """,
        (item_id,)
    ).fetchone()

    if item is None:

        connection.close()

        flash("Item not found.", "error")

        return redirect(url_for("inventory"))

    if request.method == "POST":

        item_name = request.form["item_name"].strip()
        quantity = request.form["quantity"].strip()
        minimum_stock = request.form["minimum_stock"].strip()
        supplier_name = request.form["supplier_name"].strip()
        supplier_phone = request.form["supplier_phone"].strip()

        if not quantity.isdigit():
            connection.close()
            flash("Quantity must be a number.", "error")
            return redirect(url_for("edit_item", item_id=item_id))

        if not minimum_stock.isdigit():
            connection.close()
            flash("Minimum stock must be a number.", "error")
            return redirect(url_for("edit_item", item_id=item_id))

        if not supplier_phone.isdigit() or len(supplier_phone) != 10:
            connection.close()
            flash("Phone number must contain 10 digits.", "error")
            return redirect(url_for("edit_item", item_id=item_id))

        try:

            connection.execute(
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
                    item_name,
                    int(quantity),
                    int(minimum_stock),
                    supplier_name,
                    supplier_phone,
                    item_id
                )
            )

            connection.commit()

            flash("Item updated successfully!", "success")

        except sqlite3.IntegrityError:

            flash("Another item with this name already exists.", "error")

        connection.close()

        return redirect(url_for("inventory"))

    connection.close()

    return render_template(
        "edit_item.html",
        item=item
    )


# =========================================================
# UPDATE STOCK
# =========================================================

@app.route("/update-stock/<int:item_id>", methods=["POST"])
def update_stock(item_id):

    quantity = request.form["quantity"].strip()

    if not quantity.isdigit():

        flash(
            "Quantity must be a number.",
            "error"
        )

        return redirect(url_for("inventory"))

    connection = get_db_connection()

    connection.execute(
        """
        UPDATE items
        SET quantity = ?
        WHERE id = ?
        """,
        (
            int(quantity),
            item_id
        )
    )

    connection.commit()
    connection.close()

    flash(
        "Stock updated successfully!",
        "success"
    )

    return redirect(url_for("inventory"))


# =========================================================
# DELETE ITEM
# =========================================================

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM items
        WHERE id = ?
        """,
        (item_id,)
    )

    connection.commit()
    connection.close()

    flash(
        "Item deleted successfully!",
        "success"
    )

    return redirect(url_for("inventory"))


# =========================================================
# LOW STOCK
# =========================================================

@app.route("/low-stock")
def low_stock():

    connection = get_db_connection()

    items = connection.execute(
        """
        SELECT *
        FROM items
        WHERE quantity <= minimum_stock
        ORDER BY quantity ASC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "low_stock.html",
        items=items
    )


# =========================================================
# ITEMS TO ORDER
# =========================================================

@app.route("/items-to-order")
def items_to_order():

    connection = get_db_connection()

    items = connection.execute(
        """
        SELECT
            *,
            (minimum_stock - quantity) AS order_quantity

        FROM items

        WHERE quantity < minimum_stock

        ORDER BY order_quantity DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "items_to_order.html",
        items=items
    )


# =========================================================
# PLACE ORDER
# =========================================================

@app.route("/place-order/<int:item_id>", methods=["POST"])
def place_order(item_id):

    connection = get_db_connection()

    item = connection.execute(
        """
        SELECT *
        FROM items
        WHERE id = ?
        """,
        (item_id,)
    ).fetchone()

    if item is None:

        connection.close()

        flash(
            "Item not found.",
            "error"
        )

        return redirect(url_for("items_to_order"))

    if item["quantity"] >= item["minimum_stock"]:

        connection.close()

        flash(
            "This item does not need ordering.",
            "error"
        )

        return redirect(url_for("items_to_order"))

    order_quantity = (
        item["minimum_stock"]
        - item["quantity"]
    )

    order_date = datetime.now().strftime(
        "%d-%m-%Y %H:%M"
    )

    connection.execute(
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
            item["id"],
            item["item_name"],
            order_quantity,
            item["supplier_name"],
            item["supplier_phone"],
            order_date,
            "Ordered"
        )
    )

    connection.commit()
    connection.close()

    flash(
        "Order placed successfully!",
        "success"
    )

    return redirect(url_for("order_history"))


# =========================================================
# ORDER HISTORY
# =========================================================

@app.route("/order-history")
def order_history():

    connection = get_db_connection()

    orders = connection.execute(
        """
        SELECT *
        FROM orders
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "order_history.html",
        orders=orders
    )


# =========================================================
# START APPLICATION
# =========================================================

init_database()


if __name__ == "__main__":

    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000"))
    )










