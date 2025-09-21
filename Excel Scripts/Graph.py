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
        resample_period = 'ME'  # Monthly grouping (End of each month)
        period_label = "Monthly"
        bar_width = 15
    else:
        resample_period = f'{period_days}D'
        period_label = f"Every {period_days} Days"
        bar_width = max(1, period_days // 2)  # Dynamic width for better visuals

    # Group data by the selected period for non-refunded items
    grouped_data = non_refunded_data.resample(resample_period, on='Date').agg({
        'Income EUR': 'sum',  # Sum up income
        'Item Count': 'sum'   # Count items
    }).reset_index()

    # Group data by the selected period for refunded items
    grouped_refunded_data = refunded_data.resample(resample_period, on='Date').agg({
        'Income EUR': 'sum',  # Sum up refunded income
        'Item Count': 'sum'   # Count refunded items
    }).reset_index()

    # Calculate the daily average income per period
    grouped_data['Avg Daily Income EUR'] = grouped_data['Income EUR'] / (
        grouped_data['Date'].dt.days_in_month if period_days == 0 else period_days
    )

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

    # Refunded income (red bars)
    plt.bar(grouped_refunded_data['Date'], grouped_refunded_data['Income EUR'], label='Refunded Income EUR', 
            color='red', alpha=0.5, width=bar_width)

    # Refunded items (purple line)
    plt.plot(grouped_refunded_data['Date'], grouped_refunded_data['Item Count'], label='Refunded Items', 
             color='purple', marker='s', linestyle='-')

    # Formatting the graph
    plt.title(f'Income, Items Sold, and Average Daily Income ({period_label})', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Amount', fontsize=12)
    plt.xticks(rotation=45, ha='right')  # Align x-axis labels for better readability
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Show the graph
    plt.show()

    # Display the updated data with the daily average income
    print("Non-refunded data:")
    print(grouped_data[['Date', 'Income EUR', 'Item Count', 'Avg Daily Income EUR']])
    print("\nRefunded data:")
    print(grouped_refunded_data[['Date', 'Income EUR', 'Item Count']])

# Function to show the input dialog for period days
def get_period_from_user():
    # Create a simple Tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask the user for the number of days per period
    period_days = simpledialog.askinteger("Input", "Enter the number of days per period (0 for monthly breakdown):",
                                          minvalue=0, maxvalue=30)  # Allow 0 for monthly grouping

    # Check if the user entered a valid value
    if period_days is not None:
        # Proceed with the processing and plotting
        process_and_plot(period_days)
    else:
        # Show a message if no valid input was provided
        messagebox.showwarning("Invalid Input", "Please enter a valid number of days.")

# Run the GUI to get user input and process the data
get_period_from_user()
