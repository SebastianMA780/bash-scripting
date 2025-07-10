import pandas as pd
from pathlib import Path

def load_csv_data(file_path):
    """
    Load CSV data efficiently using pandas DataFrame.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: The loaded data
    """
    try:
        csv_path = Path(file_path)
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        df = pd.read_csv(csv_path)
        
        print(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns")
        return df
        
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def get_data_info(df):
    if df is not None:
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Data types:\n{df.dtypes}")
        return df.info()

# Example usage
if __name__ == "__main__":
    # Example file path
    csv_file = "/Users/sebastian/dev/learning/dc-account/info/Balance - Log Chats.csv"
    
    # Load the data
    data = load_csv_data(csv_file)
    
    if data is not None:
        # Display basic info
        get_data_info(data)
        
        # Show first few rows
        print("\nFirst 5 rows:")
        print(data.head())