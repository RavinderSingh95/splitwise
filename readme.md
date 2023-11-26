# Expense Sharing App

# Overview
Expense Sharing App is a web application that allows users to add and split expenses among different people. The app keeps track of balances between users, making it easy to manage shared expenses

# Features
- Add expenses and split them among multiple users.
- Supports three types of expenses: EQUAL, EXACT, and PERCENT.
- View balances between users.
- Simplify expenses to minimize the number of transactions.

# Prerequisites
- Python (3.x)
- Django
- Django REST framework

# Installation

# Clone the repository:
git clone https://github.com/your-username/expense-sharing-app.git

# Navigate to the project directory:
cd expense-sharing-app

# Install dependencies
pip install -r requirements.txt

# Run the development server:
python manage.py runserver

The app will be accessible at http://localhost:8000/

# API Endpoints
main/add_expense: create a new expense
main/user_passbook/{user_uuid}: View passbook of a specific user
main/user_balances/{user_uuid}: View balances between users