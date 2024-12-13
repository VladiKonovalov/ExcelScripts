import pandas as pd

# Load the Excel file
file_path = 'creations-2024-12-10.csv'
df = pd.read_csv(file_path)

# Check if necessary columns exist
required_columns = ['Design', 'Views', 'Total']
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"Missing one of the required columns: {', '.join(required_columns)}")

# Sort by 'Total' first, then by 'Views' in case of ties
df_sorted = df.sort_values(by=['Total', 'Views'], ascending=[False, False])

# Get the top 10 sellable items
top_10 = df_sorted.head(10)

# Display the results in a table format
print(top_10[['Design', 'Views', 'Total']])

# Optionally, save the result to a new CSV
top_10.to_csv('top_10_sellable_items.csv', index=False)
