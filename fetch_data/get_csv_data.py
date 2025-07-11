import pandas as pd
from pathlib import Path

def load_csv_data(file_path):
    """
    Load CSV data efficiently using pandas DataFrame.
    
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

if __name__ == "__main__":
    pass
    