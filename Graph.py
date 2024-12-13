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

    # Group data by user-defined period (e.g., every 'period_days' days)
    grouped_data = sales_data.resample(f'{period_days}D', on='Date').agg({
        'Income EUR': 'sum',  # Sum up income
        'Item Count': 'sum'   # Count items
    }).reset_index()

    # Calculate the daily average income per defined period
    grouped_data['Avg Daily Income EUR'] = grouped_data['Income EUR'] / period_days

    # Plot the data (swapped visuals, with Income EUR as bars and Items Sold as a line)
    plt.figure(figsize=(12, 6))
    plt.bar(grouped_data['Date'], grouped_data['Income EUR'], label='Income EUR', color='orange', alpha=0.7, width=2)
    plt.plot(grouped_data['Date'], grouped_data['Item Count'], label='Items Sold', color='blue', marker='o')

    # Add a line for the average daily income per user-defined period
    plt.plot(grouped_data['Date'], grouped_data['Avg Daily Income EUR'], label='Avg Daily Income EUR', color='green', linestyle='--', marker='x')

    # Formatting the graph
    plt.title(f'Income, Items Sold, and Average Daily Income Every {period_days} Days', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Amount', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Show the graph
    plt.show()

    # Display the updated data with the daily average income
    print(grouped_data[['Date', 'Income EUR', 'Item Count', 'Avg Daily Income EUR']])

# Function to show the input dialog for period days
def get_period_from_user():
    # Create a simple Tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask the user for the number of days per period
    period_days = simpledialog.askinteger("Input", "Enter the number of days per period:",
                                          minvalue=1, maxvalue=30)  # Set a reasonable range for period days

    # Check if the user entered a valid value
    if period_days:
        # Proceed with the processing and plotting
        process_and_plot(period_days)
    else:
        # Show a message if no valid input was provided
        messagebox.showwarning("Invalid Input", "Please enter a valid number of days.")

# Run the GUI to get user input and process the data
get_period_from_user()
