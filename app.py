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

db.autocommit = True
cursor = db.cursor(dictionary=True)

# 🔐 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        account = request.form["account"]
        pin = request.form["pin"]

        try:
            account = int(account)
        except:
            return "Invalid Account Number"

        cursor.execute("SELECT * FROM users WHERE id=%s", (account,))
        user = cursor.fetchone()

        if user and str(user["pin"]) == str(pin):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
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

    cursor.execute("SELECT balance FROM users WHERE id=%s", (user_id,))
    result = cursor.fetchone()

    if not result:
        return "User not found"

    balance = result["balance"]
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

            cursor.execute(
                "INSERT INTO transactions (user_id, type, amount) VALUES (%s, %s, %s)",
                (user_id, "Deposit", amount)
            )

            message = "Deposit Successful!"

        elif action == "withdraw" and amount <= balance:
            balance -= amount

            cursor.execute(
                "UPDATE users SET balance=%s WHERE id=%s",
                (balance, user_id)
            )

            cursor.execute(
                "INSERT INTO transactions (user_id, type, amount) VALUES (%s, %s, %s)",
                (user_id, "Withdraw", amount)
            )

            message = "Withdraw Successful!"

        else:
            message = "Insufficient Balance!"

    cursor.execute("SELECT * FROM transactions WHERE user_id=%s", (user_id,))
    history = cursor.fetchall()

    return render_template(
        "dashboard.html",
        balance=balance,
        user_name=session.get("user_name"),
        history=history,
        message=message
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
            message = "❌ PIN must be numbers only!"

        elif len(new_pin) != 4:
            message = "❌ PIN must be 4 digits!"

        elif new_pin != confirm_pin:
            message = "❌ PINs do not match!"

        else:
            cursor.execute(
                "UPDATE users SET pin=%s WHERE id=%s",
                (int(new_pin), user_id)
            )

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