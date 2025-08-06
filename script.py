import pandas as pd

def read_file_info(file_path):
    # Read file depending on extension
    if file_path.lower().endswith(('.xls', '.xlsx', '.xlsm', '.xlsb')):
        df = pd.read_excel(file_path)
    elif file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format")

    rows, cols = df.shape
    total_cells = df.size  # total number of data cells
    total_missing = df.isnull().sum().sum()  # total missing values
    total_unique = df.nunique().sum()  # total unique values

    print(f"📄 File: {file_path}")
    print(f"📏 Rows: {rows}")
    print(f"📐 Columns: {cols}")
    print(f"🔢 Total Data Cells: {total_cells}")
    print(f"❓ Missing Values: {total_missing}")
    print(f"🔍 Unique Values (all cols): {total_unique}")
    print(f"📋 Column Names: {list(df.columns)}")
    print(f"\n--- Data Preview ---")
    print(df.head())  # show first 5 rows

# Example usage
read_file_info("Initiatives and Orgs (Responses) - Form Responses.csv")