#!/usr/bin/env python
# coding: utf-8

# In[2]:


# Install required packages for the personal expense tracker
get_ipython().system('pip install pandas numpy matplotlib seaborn jupyter ipywidgets plotly')

# Verify package installation
try:
    import pandas
    import numpy
    import matplotlib
    import seaborn
    import ipywidgets
    import plotly
    import sqlite3
    print("All packages installed and imported successfully!")
except ImportError as e:
    print(f"Error importing package: {e}")


# In[14]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import sqlite3
from datetime import datetime

# Initialize SQLite database
conn = sqlite3.connect('expense_tracker.db')
cursor = conn.cursor()

# Create expenses table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        Date TEXT,
        Category TEXT,
        Amount REAL,
        Description TEXT
    )
''')
conn.commit()

# Load existing expenses and ensure correct data types
expenses = pd.read_sql('SELECT * FROM expenses', conn)
if not expenses.empty:
    expenses['Date'] = pd.to_datetime(expenses['Date'], errors='coerce')
    expenses['Amount'] = pd.to_numeric(expenses['Amount'], errors='coerce')
    expenses = expenses.sort_values('Date').reset_index(drop=True)  # Sort by date

# Initialize categories
default_categories = ['Food', 'Transport', 'Entertainment', 'Bills', 'Other']
categories = list(set(default_categories + (list(expenses['Category'].unique()) if not expenses.empty else [])))

# Create interactive widgets
date_input = widgets.Text(description='Date (YYYY-MM-DD):', value=datetime.now().strftime('%Y-%m-%d'))
category_input = widgets.Dropdown(description='Category:', options=categories)
amount_input = widgets.FloatText(description='Amount (₹):', value=0.0)
description_input = widgets.Text(description='Description:', value='')
add_button = widgets.Button(description='Add Expense', button_style='success')
summary_button = widgets.Button(description='Show Summary', button_style='info')
plot_button = widgets.Button(description='Plot Expenses', button_style='primary')
filter_button = widgets.Button(description='Filter Expenses', button_style='warning')
export_button = widgets.Button(description='Export to CSV', button_style='danger')
clear_button = widgets.Button(description='Clear Table', button_style='danger')
edit_index = widgets.IntText(description='Edit Index:', value=-1)
edit_button = widgets.Button(description='Edit Expense', button_style='primary')
delete_index = widgets.IntText(description='Delete Index:', value=-1)
delete_button = widgets.Button(description='Delete Expense', button_style='danger')
pivot_button = widgets.Button(description='Show Pivot Table', button_style='info')
new_category_input = widgets.Text(description='New Category:', value='')
add_category_button = widgets.Button(description='Add Category', button_style='success')
remove_category = widgets.Dropdown(description='Remove Category:', options=categories)
remove_category_button = widgets.Button(description='Remove Category', button_style='danger')
start_date = widgets.Text(description='Start Date:', value=(datetime.now().date() - pd.Timedelta(days=30)).strftime('%Y-%m-%d'))
end_date = widgets.Text(description='End Date:', value=datetime.now().strftime('%Y-%m-%d'))
category_filter = widgets.Dropdown(description='Filter Category:', options=['All'] + categories)
output = widgets.Output()

# Style for tabular output
def style_df(df):
    formatters = {
        'Amount': '₹{:.2f}'.format,  # Use Rupee symbol
        'Date': lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) and isinstance(x, (pd.Timestamp, np.datetime64)) else ''
    }
    # Handle pivot table numeric columns
    for col in df.columns:
        if col not in formatters and pd.api.types.is_numeric_dtype(df[col]):
            formatters[col] = '₹{:.2f}'.format
    return df.style.format(formatters, na_rep='').set_properties(**{
        'text-align': 'left',
        'border': '1px solid #ddd',
        'padding': '5px'
    }).set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#f4f4f4'), ('font-weight', 'bold'), ('text-align', 'left'), ('padding', '5px')]}
    ])

# Add expense
def add_expense(b):
    with output:
        clear_output()
        global expenses
        try:
            date = pd.to_datetime(date_input.value, format='%Y-%m-%d', errors='raise')
            amount = float(amount_input.value)
            if amount <= 0:
                print("Error: Amount must be positive!")
                return
            new_expense = pd.DataFrame({
                'Date': [date],
                'Category': [category_input.value],
                'Amount': [amount],
                'Description': [description_input.value]
            })
            expenses = pd.concat([expenses, new_expense], ignore_index=True)
            expenses = expenses.sort_values('Date').reset_index(drop=True)  # Sort by date
            new_expense.to_sql('expenses', conn, if_exists='append', index=False)
            display(HTML("<b>Expense added successfully!</b>"))
            display(style_df(expenses))
            update_category_options()
        except ValueError as e:
            print(f"Error: Invalid date format or input. Use YYYY-MM-DD. Details: {e}")

# Edit expense
def edit_expense(b):
    with output:
        clear_output()
        global expenses
        try:
            idx = edit_index.value
            if idx < 0 or idx >= len(expenses):
                print(f"Error: Invalid index. Choose between 0 and {len(expenses)-1}.")
                return
            date = pd.to_datetime(date_input.value, format='%Y-%m-%d', errors='raise')
            amount = float(amount_input.value)
            if amount <= 0:
                print("Error: Amount must be positive!")
                return
            expenses.iloc[idx] = [date, category_input.value, amount, description_input.value]
            expenses = expenses.sort_values('Date').reset_index(drop=True)  # Sort by date
            expenses.to_sql('expenses', conn, if_exists='replace', index=False)
            display(HTML("<b>Expense edited successfully!</b>"))
            display(style_df(expenses))
            update_category_options()
        except ValueError as e:
            print(f"Error: Invalid date format or input. Use YYYY-MM-DD. Details: {e}")

# Delete expense
def delete_expense(b):
    with output:
        clear_output()
        global expenses
        try:
            idx = delete_index.value
            if idx < 0 or idx >= len(expenses):
                print(f"Error: Invalid index. Choose between 0 and {len(expenses)-1}.")
                return
            expenses = expenses.drop(idx).reset_index(drop=True)
            expenses = expenses.sort_values('Date').reset_index(drop=True)  # Sort by date
            expenses.to_sql('expenses', conn, if_exists='replace', index=False)
            display(HTML("<b>Expense deleted successfully!</b>"))
            display(style_df(expenses))
            update_category_options()
        except ValueError as e:
            print(f"Error: Invalid index. Details: {e}")

# Clear table
def clear_table(b):
    with output:
        clear_output()
        global expenses
        expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
        cursor.execute('DELETE FROM expenses')
        conn.commit()
        display(HTML("<b>Table cleared successfully!</b>"))
        update_category_options()

# Show summary
def show_summary(b):
    with output:
        clear_output()
        if expenses.empty:
            print("No expenses recorded yet.")
            return
        summary = pd.DataFrame({
            'Metric': ['Total Spending', 'Average Expense', 'Median Expense', 'Number of Expenses'],
            'Value': [
                expenses['Amount'].sum(),
                expenses['Amount'].mean(),
                expenses['Amount'].median(),
                len(expenses)
            ]
        })
        summary_styler = summary.style.format({
            'Value': lambda x: f"₹{x:.2f}" if isinstance(x, (int, float)) and x != len(expenses) else str(x)
        }, na_rep='').set_properties(**{
            'text-align': 'left',
            'border': '1px solid #ddd',
            'padding': '5px'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f4f4f4'), ('font-weight', 'bold'), ('text-align', 'left'), ('padding', '5px')]}
        ])
        category_summary = expenses.groupby('Category')['Amount'].sum().reset_index()
        display(HTML("<b>Summary Statistics</b>"))
        display(summary_styler)
        display(HTML("<b>Expenses by Category</b>"))
        display(style_df(category_summary))

# Filter expenses
def filter_expenses(b):
    with output:
        clear_output()
        filtered = expenses.copy()
        try:
            if start_date.value:
                filtered = filtered[filtered['Date'] >= pd.to_datetime(start_date.value, format='%Y-%m-%d')]
            if end_date.value:
                filtered = filtered[filtered['Date'] <= pd.to_datetime(end_date.value, format='%Y-%m-%d')]
            if category_filter.value != 'All':
                filtered = filtered[filtered['Category'] == category_filter.value]
            if filtered.empty:
                print("No expenses match the filter criteria.")
            else:
                filtered = filtered.sort_values('Date').reset_index(drop=True)  # Sort by date
                display(HTML("<b>Filtered Expenses</b>"))
                display(style_df(filtered))
        except ValueError as e:
            print(f"Error: Invalid date format. Use YYYY-MM-DD. Details: {e}")

# Show pivot table
def show_pivot_table(b):
    with output:
        clear_output()
        if expenses.empty:
            print("No expenses to pivot.")
            return
        pivot = expenses.pivot_table(values='Amount', index='Date', columns='Category', aggfunc='sum', fill_value=0)
        pivot = pivot.reset_index().sort_values('Date')  # Sort by date
        display(HTML("<b>Pivot Table (Amount by Date and Category)</b>"))
        display(style_df(pivot))

# Add category
def add_category(b):
    with output:
        clear_output()
        global categories
        new_category = new_category_input.value.strip()
        if not new_category:
            print("Error: Category name cannot be empty!")
            return
        if new_category in categories:
            print(f"Error: Category '{new_category}' already exists!")
            return
        categories.append(new_category)
        category_input.options = categories
        category_filter.options = ['All'] + categories
        remove_category.options = categories
        display(HTML(f"<b>Category '{new_category}' added successfully!</b>"))
        if not expenses.empty:
            display(style_df(expenses))

# Remove category
def remove_category_func(b):
    with output:
        clear_output()
        global expenses, categories
        category_to_remove = remove_category.value
        if category_to_remove not in categories:
            print(f"Error: Category '{category_to_remove}' not found!")
            return
        if expenses['Category'].eq(category_to_remove).any():
            print(f"Error: Cannot remove '{category_to_remove}' as it is used in expenses!")
            display(style_df(expenses))
            return
        categories.remove(category_to_remove)
        category_input.options = categories
        category_filter.options = ['All'] + categories
        remove_category.options = categories
        display(HTML(f"<b>Category '{category_to_remove}' removed successfully!</b>"))
        if not expenses.empty:
            display(style_df(expenses))

# Update category options
def update_category_options():
    global categories
    used_categories = list(expenses['Category'].unique()) if not expenses.empty else []
    categories = list(set(default_categories + used_categories))
    category_input.options = categories
    category_filter.options = ['All'] + categories
    remove_category.options = categories

# Export to CSV
def export_expenses(b):
    with output:
        clear_output()
        if expenses.empty:
            print("No expenses to export.")
            return
        filename = f'expenses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        expenses.to_csv(filename, index=False)
        display(HTML(f"<b>Exported to {filename}</b>"))

# Plot pie chart
def plot_expenses(b):
    with output:
        clear_output()
        if expenses.empty:
            print("No expenses to visualize.")
            return
        category_sums = expenses.groupby('Category')['Amount'].sum()
        plt.figure(figsize=(8, 6))
        plt.pie(category_sums, labels=category_sums.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
        plt.title('Expenses by Category')
        plt.show()

# Bind buttons
add_button.on_click(add_expense)
edit_button.on_click(edit_expense)
delete_button.on_click(delete_expense)
clear_button.on_click(clear_table)
summary_button.on_click(show_summary)
filter_button.on_click(filter_expenses)
pivot_button.on_click(show_pivot_table)
add_category_button.on_click(add_category)
remove_category_button.on_click(remove_category_func)
export_button.on_click(export_expenses)
plot_button.on_click(plot_expenses)

# Display widgets
display(widgets.VBox([
    widgets.HBox([date_input, category_input]),
    widgets.HBox([amount_input, description_input]),
    widgets.HBox([edit_index, edit_button, delete_index, delete_button]),
    widgets.HBox([new_category_input, add_category_button, remove_category, remove_category_button]),
    widgets.HBox([add_button, summary_button, plot_button, filter_button, pivot_button, export_button, clear_button]),
    widgets.HBox([start_date, end_date, category_filter]),
    output
]))

# Display existing expenses
if not expenses.empty:
    display(HTML("<b>Current Expenses</b>"))
    display(style_df(expenses))


# In[ ]:




