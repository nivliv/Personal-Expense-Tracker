# Personal-Expense-Tracker
Personal Expense Tracker – Brief Report
1. Problem Statement
Managing personal finances can be challenging without an organized system. People often lose track of daily expenses, leading to overspending and lack of budget control. The problem is the absence of a simple, user-friendly tool that:
- Records daily expenses.
- Categorizes spending.
- Analyzes spending patterns.
- Provides insights through summaries and visualizations.

This project aims to solve this problem by creating an interactive expense tracking solution.
2. Tools & Libraries Used
- Python – Main programming language.
- pandas – For data handling and analysis.
- numpy – For numeric operations.
- matplotlib & seaborn – For plotting charts and visualizations.
- ipywidgets – For creating an interactive UI inside Jupyter Notebook.
- SQLite (sqlite3 module) – For persistent storage of expenses.
- datetime – For handling dates and filtering by date range.
3. Solution Overview
We built an interactive expense tracker that allows users to:
- Add, Edit, and Delete Expenses with details like date, category, amount, and description.
- Categorize Expenses dynamically by adding or removing categories.
- Analyze Spending Patterns through:
  • Summary statistics (total, average, median spending).
  • Category-wise expense breakdown.
  • Pivot tables for daily category spend.
- Visualize Data with pie charts for category distribution.
- Filter Expenses by date range and category for targeted insights.
- Export Data to CSV for backup or further analysis.
- Persistent Storage using SQLite to save and retrieve expense history.

The UI is built with ipywidgets, making it interactive and easy to use within Jupyter Notebook.
