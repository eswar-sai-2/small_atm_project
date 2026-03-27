import os
import mysql.connector
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, session
from datetime import timedelta
import bcrypt

app = Flask(__name__)
app.secret_key = "secret123"

# 🔗 DATABASE CONNECTION
url_str = os.environ.get("MYSQL_PUBLIC_URL")

if not url_str:
    raise Exception("MYSQL_PUBLIC_URL not set!")

url = urlparse(url_str)

db = mysql.connector.connect(
    host=url.hostname,
    user=url.username,
    password=url.password,
    database=url.path[1:],
    port=url.port
)

cursor = db.cursor(dictionary=True)

# 🔐 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        account = int(request.form["account"])
        pin = request.form["pin"]

        cursor.execute("SELECT * FROM users WHERE id=%s", (account,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(pin.encode(), user["pin"].encode()):
            session.clear()
            session["user_id"] = user["id"]
            return redirect("/dashboard")
        else:
            return "Incorrect PIN"

    return render_template("login.html")


# 🆕 SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        pin = request.form["pin"]
        balance = float(request.form["balance"])

        # AUTO ACCOUNT NUMBER
        cursor.execute("SELECT MAX(id) AS max_id FROM users")
        result = cursor.fetchone()
        new_id = (result["max_id"] or 0) + 1

        # HASH PIN
        hashed_pin = bcrypt.hashpw(pin.encode(), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO users (id, name, pin, balance) VALUES (%s, %s, %s, %s)",
            (new_id, name, hashed_pin.decode(), balance)
        )
        db.commit()

        return f"Account Created! Your Account Number is {new_id}"

    return render_template("signup.html")


# 🏠 DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/")

    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    if not user:
        return redirect("/")

    balance = user["balance"]
    user_name = user["name"]
    message = ""

    if request.method == "POST":
        amount = float(request.form["amount"])
        action = request.form["action"]

        if action == "deposit":
            balance += amount

            cursor.execute(
                "UPDATE users SET balance=%s WHERE id=%s",
                (balance, user_id)
            )
            db.commit()

            cursor.execute(
                "INSERT INTO transactions (user_id, type, amount) VALUES (%s, %s, %s)",
                (user_id, "Deposit", amount)
            )
            db.commit()

            message = "Deposit Successful!"

        elif action == "withdraw" and amount <= balance:
            balance -= amount

            cursor.execute(
                "UPDATE users SET balance=%s WHERE id=%s",
                (balance, user_id)
            )
            db.commit()

            cursor.execute(
                "INSERT INTO transactions (user_id, type, amount) VALUES (%s, %s, %s)",
                (user_id, "Withdraw", amount)
            )
            db.commit()

            message = "Withdraw Successful!"

        else:
            message = "Insufficient Balance!"

    cursor.execute("SELECT * FROM transactions WHERE user_id=%s ORDER BY id DESC", (user_id,))
    history = cursor.fetchall()

    deposit_count = sum(1 for t in history if t["type"] == "Deposit")
    withdraw_count = sum(1 for t in history if t["type"] == "Withdraw")

    return render_template(
        "dashboard.html",
        balance=balance,
        user_name=user_name,
        history=history,
        message=message,
        deposit_count=deposit_count,
        withdraw_count=withdraw_count,
        timedelta=timedelta
    )


# 📄 HISTORY
@app.route("/history")
def history_page():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/")

    cursor.execute("SELECT * FROM transactions WHERE user_id=%s ORDER BY id DESC", (user_id,))
    history = cursor.fetchall()

    return render_template(
        "history.html",
        history=history,
        timedelta=timedelta
    )


# 🔐 CHANGE PIN
@app.route("/change_pin", methods=["GET", "POST"])
def change_pin():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/")

    message = ""

    if request.method == "POST":
        old_pin = request.form["old_pin"]
        new_pin = request.form["new_pin"]
        confirm_pin = request.form["confirm_pin"]

        cursor.execute("SELECT pin FROM users WHERE id=%s", (user_id,))
        current_pin = cursor.fetchone()["pin"]

        if not bcrypt.checkpw(old_pin.encode(), current_pin.encode()):
            message = "❌ Old PIN is incorrect!"

        elif not new_pin.isdigit():
            message = "❌ PIN must contain only numbers!"

        elif len(new_pin) != 4:
            message = "❌ PIN must be exactly 4 digits!"

        elif new_pin != confirm_pin:
            message = "❌ PINs do not match!"

        else:
            hashed_new_pin = bcrypt.hashpw(new_pin.encode(), bcrypt.gensalt())

            cursor.execute(
                "UPDATE users SET pin=%s WHERE id=%s",
                (hashed_new_pin.decode(), user_id)
            )
            db.commit()

            return redirect("/dashboard")

    return render_template("change_pin.html", message=message)


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# 🔥 ADMIN LOGIN
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("admin"):
        return redirect("/admin/dashboard")

    message = ""   # ✅ IMPORTANT (fix error)

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin/dashboard")
        else:
            message = "❌ Invalid Username or Password"

    return render_template("admin_login.html", message=message)


# 🔥 ADMIN DASHBOARD
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    cursor.execute("SELECT id, name, balance FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
    transactions = cursor.fetchall()

    return render_template(
        "admin_dashboard.html",
        users=users,
        transactions=transactions
    )


# 🔥 DELETE USER
@app.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
    if not session.get("admin"):
        return redirect("/admin")

    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    db.commit()

    return redirect("/admin/dashboard")


# ▶️ RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)