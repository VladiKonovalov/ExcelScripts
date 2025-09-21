
![Figure_1](https://github.com/user-attachments/assets/6dd7cb14-7dbf-443d-83f6-73e19b655d38)


# Sales Data Visualization Tool

This Python script processes sales data from multiple CSV files located in a `sales` folder, generates a graph that displays **income**, **items sold**, and the **average daily income** over custom periods of days. The user can adjust the period dynamically through a simple GUI prompt.

## Features
- **Dynamic Period Selection**: Choose any period (e.g., 3, 5, 7, 10 days) to group and visualize the data.
- **Graphs**: Visualize income over the chosen period as bars, items sold as a line, and average daily income as a dashed line.
- **Customizable Input**: Easily adjust the number of days for each period through a user-friendly interface.

## Requirements

Before running the script, make sure to install the required dependencies:

```bash
pip install pandas matplotlib
Additionally, make sure to have **Tkinter** installed (it comes pre-installed with Python on most systems).
```



## How to Use

1. **Prepare Your Data**:
    - Organize your CSV files into a folder named `sales` in the same directory as the Python script.
    - Ensure the CSV files are in the format `sales-YYYY-MM.csv`.
    - Your CSV files should have the following columns:
      - **Date**: The date of the sale (in a format like `YYYY-MM-DD`).
      - **Income EUR**: The total income for the sale in EUR.
      - **Item Count**: The number of items sold.

2. **Run the Script**:
    - After setting up your files and environment, run the script. It will prompt you to enter the **number of days per period** (e.g., 3, 5, 10 days).
    - The script will then process the data and display a graph.

3. **Customize for Your Data**:
    - If your data structure differs, you can easily adjust the column names in the script:
      ```python
      sales_data['Date']        # Column name for date
      sales_data['Income EUR']  # Column name for income
      sales_data['Item Count']  # Column name for the number of items
      ```

## Example Folder Structure

Ensure that your files are organized as follows:

/your-project-directory ├── sales/ │ ├── sales-2024-01.csv │ ├── sales-2024-02.csv │ └── sales-2024-03.csv ├── script.py └── README.md

markdown
Copy code

The script will automatically process all CSV files inside the `sales` folder.

## Troubleshooting

- If you encounter any issues, check the following:
    - Ensure all CSV files are in the correct format (`sales-YYYY-MM.csv`).
    - Verify that the **Date** column is in a valid date format (e.g., `YYYY-MM-DD`).
    - Make sure the `Income EUR` and `Item Count` columns exist and contain numeric data.


