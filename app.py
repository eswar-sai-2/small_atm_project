import mysql.connector
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="sai",
    password="220f",
    database="atm_project"
)

cursor = db.cursor(dictionary=True)

# SAME VARIABLES
balance = 0
user_id = None
user_name = ""
transactions = []
deposit_count = 0
withdraw_count = 0


# 🔐 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    global balance, user_id, user_name

    if request.method == "POST":
        account = request.form["account"]
        pin = request.form["pin"]

        cursor.execute(
            "SELECT * FROM users WHERE id=%s AND pin=%s",
            (account, pin)
        )
        user = cursor.fetchone()

        if user:
            user_id = user["id"]
            balance = user["balance"]
            user_name = user["name"]
            return redirect("/dashboard")
        else:
            return "Incorrect PIN"

    return render_template("login.html")


# 🏠 DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    global balance, transactions, deposit_count, withdraw_count, user_id, user_name

    message = ""

    if request.method == "POST":
        amount = float(request.form["amount"])
        action = request.form["action"]

        if action == "deposit":
            balance += amount
            deposit_count += 1
            transactions.append(f"Deposited ₹{amount}")

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
            withdraw_count += 1
            transactions.append(f"Withdrawn ₹{amount}")

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

    cursor.execute("SELECT * FROM transactions WHERE user_id=%s", (user_id,))
    history = cursor.fetchall()

    return render_template(
        "dashboard.html",
        balance=balance,
        user_name=user_name,
        transactions=transactions,
        deposit_count=deposit_count,
        withdraw_count=withdraw_count,
        history=history,
        message=message
    )


# 📄 HISTORY PAGE
@app.route("/history")
def history_page():
    cursor.execute("SELECT * FROM transactions WHERE user_id=%s", (user_id,))
    history = cursor.fetchall()
    return render_template("history.html", history=history)


# 🔐 CHANGE PIN (FIXED 🔥)
@app.route("/change_pin", methods=["GET", "POST"])
def change_pin():
    message = ""

    if request.method == "POST":
        old_pin = request.form["old_pin"]
        new_pin = request.form["new_pin"]
        confirm_pin = request.form["confirm_pin"]

        # Get current PIN
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
    return redirect("/")


# ▶️ RUN
if __name__ == "__main__":
    app.run(debug=True)