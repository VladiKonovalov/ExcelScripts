import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog, messagebox

# Function to process and generate the graph based on user input
def process_and_plot(period_days):
    # Get the directory where the script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Define the path to the "sales" folder within the same directory
    sales_directory = os.path.join(script_directory, 'sales')

    # Get all CSV files in the "sales" directory that match the naming pattern "sales-YYYY-MM.csv"
    files = [f for f in os.listdir(sales_directory) if f.startswith('sales-') and f.endswith('.csv')]

    # Initialize an empty list to store data
    all_data = []

    # Load all the files and append them to the list
    for file in files:
        file_path = os.path.join(sales_directory, file)
        data = pd.read_csv(file_path)
        
        # Extract year-month from filename (e.g., "sales-2024-03.csv" -> "2024-03")
        file_month = file.replace('sales-', '').replace('.csv', '')
        data['File_Month'] = file_month
        
        all_data.append(data)

    # Concatenate all data into one DataFrame
    sales_data = pd.concat(all_data, ignore_index=True)

    # Convert the "Date" column to datetime and ensure clean data
    sales_data['Date'] = pd.to_datetime(sales_data['Date'], errors='coerce')

    # Filter out rows where the 'Date' is invalid
    sales_data = sales_data.dropna(subset=['Date'])

    # Add a column for the count of items (each row represents one item)
    sales_data['Item Count'] = 1

    # Separate refunded and non-refunded items
    refunded_data = sales_data[sales_data['Status'].str.contains('Refunded', case=False, na=False)]
    non_refunded_data = sales_data[~sales_data['Status'].str.contains('Refunded', case=False, na=False)]

    # Determine the resampling period
    if period_days == 0:
        # Group by the CSV file month instead of calendar month
        period_label = "Monthly (by File)"
        bar_width = 15
        
        # Group by File_Month for non-refunded items
        grouped_data = non_refunded_data.groupby('File_Month').agg({
            'Income EUR': 'sum',
            'Item Count': 'sum',
            'Date': 'min'  # Use the earliest date in each file as the x-axis point
        }).reset_index()
        
        # Group by File_Month for refunded items
        grouped_refunded_data = refunded_data.groupby('File_Month').agg({
            'Income EUR': 'sum',
            'Item Count': 'sum',
            'Date': 'min'
        }).reset_index()
        
        # Calculate days in each file's month for average
        grouped_data['Days_in_Period'] = grouped_data['File_Month'].apply(
            lambda x: pd.Period(x).days_in_month
        )
        grouped_data['Avg Daily Income EUR'] = grouped_data['Income EUR'] / grouped_data['Days_in_Period']
        
    else:
        resample_period = f'{period_days}D'
        period_label = f"Every {period_days} Days"
        bar_width = max(1, period_days // 2)

        # Group data by the selected period for non-refunded items
        grouped_data = non_refunded_data.resample(resample_period, on='Date').agg({
            'Income EUR': 'sum',
            'Item Count': 'sum'
        }).reset_index()

        # Group data by the selected period for refunded items
        grouped_refunded_data = refunded_data.resample(resample_period, on='Date').agg({
            'Income EUR': 'sum',
            'Item Count': 'sum'
        }).reset_index()

        # Calculate the daily average income per period
        grouped_data['Avg Daily Income EUR'] = grouped_data['Income EUR'] / period_days

    # Sort by date to ensure proper plotting
    grouped_data = grouped_data.sort_values('Date')
    grouped_refunded_data = grouped_refunded_data.sort_values('Date')

    # Plot the data
    plt.figure(figsize=(12, 6))

    # Non-refunded income (bar)
    plt.bar(grouped_data['Date'], grouped_data['Income EUR'], label='Income EUR (Non-Refunded)', 
            color='orange', alpha=0.7, width=bar_width)

    # Items Sold (line with markers)
    plt.plot(grouped_data['Date'], grouped_data['Item Count'], label='Items Sold (Non-Refunded)', 
             color='blue', marker='o', linestyle='-')

    # Avg Daily Income (dashed line with labels)
    plt.plot(grouped_data['Date'], grouped_data['Avg Daily Income EUR'], label='Avg Daily Income EUR', 
             color='green', linestyle='--', marker='x')

    # Annotate Avg Daily Income
    for i, row in grouped_data.iterrows():
        plt.text(row['Date'], row['Avg Daily Income EUR'], 
                 f"{row['Avg Daily Income EUR']:.2f}", 
                 fontsize=10, color='green', ha='left', va='bottom')

    # Annotate Income EUR on top of bar
    for i, row in grouped_data.iterrows():
        plt.text(row['Date'], row['Income EUR'], 
                 f"{row['Income EUR']:.0f}€", 
                 fontsize=10, color='darkorange', ha='center', va='bottom')

    # Annotate Items Sold next to dot
    for i, row in grouped_data.iterrows():
        plt.text(row['Date'], row['Item Count'], 
                 f"{int(row['Item Count'])}", 
                 fontsize=10, color='blue', ha='center', va='bottom')

    # Refunded income (red bars) - only if there's refunded data
    if not grouped_refunded_data.empty:
        plt.bar(grouped_refunded_data['Date'], grouped_refunded_data['Income EUR'], 
                label='Refunded Income EUR', color='red', alpha=0.5, width=bar_width)

        # Refunded items (purple line)
        plt.plot(grouped_refunded_data['Date'], grouped_refunded_data['Item Count'], 
                 label='Refunded Items', color='purple', marker='s', linestyle='-')

    # Formatting the graph
    plt.title(f'Income, Items Sold, and Average Daily Income ({period_label})', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Amount', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Show the graph
    plt.show()

    # Display the updated data with the daily average income
    print("Non-refunded data:")
    if period_days == 0:
        print(grouped_data[['File_Month', 'Date', 'Income EUR', 'Item Count', 'Avg Daily Income EUR']])
    else:
        print(grouped_data[['Date', 'Income EUR', 'Item Count', 'Avg Daily Income EUR']])
    
    if not grouped_refunded_data.empty:
        print("\nRefunded data:")
        if period_days == 0:
            print(grouped_refunded_data[['File_Month', 'Date', 'Income EUR', 'Item Count']])
        else:
            print(grouped_refunded_data[['Date', 'Income EUR', 'Item Count']])

# Function to show the input dialog for period days
def get_period_from_user():
    # Create a simple Tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask the user for the number of days per period
    period_days = simpledialog.askinteger("Input", "Enter the number of days per period (0 for monthly breakdown):",
                                          minvalue=0, maxvalue=30)

    # Check if the user entered a valid value
    if period_days is not None:
        # Proceed with the processing and plotting
        process_and_plot(period_days)
    else:
        # Show a message if no valid input was provided
        messagebox.showwarning("Invalid Input", "Please enter a valid number of days.")

# Run the GUI to get user input and process the data
get_period_from_user()
