# 🏧 ATM Banking System (Flask + MySQL)

A complete **ATM Banking Web Application** built using **Flask, MySQL, and Bootstrap**.
This project allows users to perform banking operations like deposit, withdraw, and view transaction history, along with an **Admin Dashboard**.

---

## 🚀 Features

### 👤 User Features

* 🔐 Secure Login (Account Number + PIN)
* 🆕 Create New Account
* 💰 Deposit Money
* 💸 Withdraw Money
* 📊 View Transaction History
* 🔑 Change PIN
* 🌙 Dark / Light Mode
* 📱 Mobile Responsive UI

---

### 👨‍💼 Admin Features

* 🔐 Admin Login
* 📊 View All Users
* 💳 View All Transactions
* 📈 Transaction Analytics (Chart.js)
* 🗑 Delete Users
* 🧹 Clear Transaction History
* 🚪 Admin Logout

---
🤖 Built with Chatbot Assistance

This project was developed with the help of an AI assistant:

*💡 UI design improvements
*🧠 Backend logic guidance
*🎨 Responsive and modern layout
*🐞 Debugging and issue fixing

ChatGPT was used as a learning and development assistant throughout the project.

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **Database:** MySQL
* **Frontend:** HTML, CSS, Bootstrap
* **Charts:** Chart.js
* **Authentication:** bcrypt (PIN hashing)

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/atm-banking-system.git
cd atm-banking-system
```

### 2️⃣ Install Dependencies

```bash
pip install flask mysql-connector-python bcrypt
```

### 3️⃣ Setup Database

Create database and tables:

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    pin VARCHAR(255),
    balance FLOAT
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    type VARCHAR(20),
    amount FLOAT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 4️⃣ Set Environment Variable

```bash
export MYSQL_PUBLIC_URL="mysql://username:password@host:port/database"
```

---

### 5️⃣ Run Project

```bash
python app.py
```

---

## 🔑 Default Admin Login

```
Username: admin
Password: admin123
```

---

---

## 📂 Project Structure

```
├── app.py
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── admin_dashboard.html
│   └── ...
├── static/
│   └── favicon.ico
```

---

## 🌟 Future Enhancements

* 📧 Email Notifications
* 🔐 OTP Authentication
* 📊 Monthly Reports
* 📱 Mobile App Version
* 💳 ATM Card UI

---

## 👨‍💻 Author

**V. SAI ESWAR**


---

## 📜 License

This project is for educational purposes.
