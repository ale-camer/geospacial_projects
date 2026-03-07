import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE_DIR, "world_administrative_boundaries.xlsx")

try:
    df = pd.read_excel(FILE)
    print("Columns found:", df.columns.tolist())
    print("First 5 rows:\n", df.head(5))
except Exception as e:
    print(f"Error: {e}")
