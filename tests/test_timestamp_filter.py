"""
Test script to verify timestamp filter works correctly.
"""
import pandas as pd
from datetime import datetime, timedelta

# Create test data
test_data = {
    'Timestamp': [
        '1/20/2026 10:00:00',
        '1/22/2026 14:00:00',
        '1/22/2026 15:00:00',
        '1/23/2026 09:00:00',
        '1/25/2026 12:00:00',
    ],
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Question1': ['A', 'B', 'A', 'B', 'A']
}

df = pd.DataFrame(test_data)

print("Original data:")
print(df)
print(f"\nTotal rows: {len(df)}")

# Test timestamp filter
cutoff_str = '1/22/2026 14:10:12'
timestamp_format = '%m/%d/%Y %H:%M:%S'

print(f"\n--- Applying timestamp filter: >= {cutoff_str} ---")

# Parse cutoff
cutoff = pd.to_datetime(cutoff_str, format=timestamp_format)
print(f"Parsed cutoff: {cutoff}")

# Parse timestamp column
timestamp_series = pd.to_datetime(df['Timestamp'], format=timestamp_format, errors='coerce')
print(f"\nParsed timestamps:")
print(timestamp_series)

# Apply filter
filtered_df = df[timestamp_series >= cutoff].copy().reset_index(drop=True)

print(f"\nFiltered data:")
print(filtered_df)
print(f"\nRows after filter: {len(filtered_df)} / {len(df)}")

# Verify
expected_names = ['Charlie', 'David', 'Eve']
actual_names = filtered_df['Name'].tolist()

if actual_names == expected_names:
    print("\n✅ Timestamp filter works correctly!")
else:
    print(f"\n❌ Filter failed! Expected {expected_names}, got {actual_names}")
