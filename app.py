import os
import mysql.connector
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, session

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

        if user and str(user["pin"]).strip() == str(pin).strip():
            session.clear()
            session["user_id"] = user["id"]
            return redirect("/dashboard")
        else:
            return "Incorrect PIN"

    return render_template("login.html")


# 🏠 DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/")

    # Get user data
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

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

    # 📄 Transaction history
    cursor.execute("SELECT * FROM transactions WHERE user_id=%s", (user_id,))
    history = cursor.fetchall()

    # 📊 COUNT FIX
    cursor.execute(
        "SELECT COUNT(*) AS total FROM transactions WHERE user_id=%s AND type='Deposit'",
        (user_id,)
    )
    deposit_count = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) AS total FROM transactions WHERE user_id=%s AND type='Withdraw'",
        (user_id,)
    )
    withdraw_count = cursor.fetchone()["total"]

    return render_template(
        "dashboard.html",
        balance=balance,
        user_name=user_name,
        history=history,
        message=message,
        deposit_count=deposit_count,
        withdraw_count=withdraw_count
        timedelta=timedelta
    )


# 📄 HISTORY PAGE
@app.route("/history")
def history_page():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/")

    cursor.execute("SELECT * FROM transactions WHERE user_id=%s", (user_id,))
    history = cursor.fetchall()

    return render_template("history.html", history=history)


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

        if str(old_pin) != str(current_pin):
            message = "❌ Old PIN is incorrect!"

        elif not new_pin.isdigit():
            message = "❌ PIN must contain only numbers!"

        elif len(new_pin) != 4:
            message = "❌ PIN must be exactly 4 digits!"

        elif new_pin != confirm_pin:
            message = "❌ New PIN and Confirm PIN do not match!"

        else:
            cursor.execute(
                "UPDATE users SET pin=%s WHERE id=%s",
                (int(new_pin), user_id)
            )
            db.commit()

            return redirect("/dashboard")

    return render_template("change_pin.html", message=message)


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ▶️ RUN
if __name__ == "__main__":
    app.run()