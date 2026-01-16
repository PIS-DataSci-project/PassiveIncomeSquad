"""
Script to parse and make the DOAJ CSV file readable.
Cleans up formatting, handles missing values, and provides readable output.
"""

import pandas as pd
from pathlib import Path

def clean_doaj_csv(input_file, output_file=None):
    """
    Parse and clean the DOAJ CSV file.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save cleaned CSV (optional)
    
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    # Read the CSV file
    df = pd.read_csv(input_file, keep_default_na=False)
    
    # Clean up whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Convert Yes/No columns to boolean
    df['DOAJ Seal'] = df['DOAJ Seal'].apply(lambda x: x.lower() == 'yes')
    df['APC'] = df['APC'].apply(lambda x: x.lower() == 'yes')
    
    # Replace empty strings with 'N/A' for better readability
    df = df.replace('', 'N/A')
    
    # Optionally save cleaned CSV
    if output_file:
        df.to_csv(output_file, index=False)
        print(f"Cleaned CSV saved to: {output_file}")
    
    return df

def display_journals(df, num_rows=10):
    """
    Display journals in a readable format.
    
    Args:
        df (pd.DataFrame): The dataframe to display
        num_rows (int): Number of rows to display
    """
    print(f"\n{'='*100}")
    print(f"DOAJ Journal Database - First {num_rows} Entries")
    print(f"{'='*100}\n")
    
    for idx, row in df.head(num_rows).iterrows():
        print(f"Journal #{idx + 1}")
        print("-" * 80)
        for col, value in row.items():
            print(f"  {col:45s}: {value}")
        print()

def print_statistics(df):
    """
    Print basic statistics about the dataset.
    
    Args:
        df (pd.DataFrame): The dataframe to analyze
    """
    print(f"\n{'='*100}")
    print("Dataset Statistics")
    print(f"{'='*100}\n")
    
    print(f"Total journals: {len(df)}")
    print(f"Journals with DOAJ Seal: {df['DOAJ Seal'].sum()}")
    print(f"Journals with APC: {df['APC'].sum()}")
    print(f"\nMissing ISSN values:")
    print(f"  Print ISSN: {(df['Journal ISSN (print version)'] == 'N/A').sum()}")
    print(f"  Online EISSN: {(df['Journal EISSN (online version)'] == 'N/A').sum()}")
    
    print(f"\nTop 5 Publishers:")
    print(df['Publisher'].value_counts().head())
    
    print(f"\nLanguages distribution (top 5):")
    # Note: languages are comma-separated, this is approximate
    print(df['Languages in which the journal accepts manuscripts'].value_counts().head())

if __name__ == "__main__":
    # Define file paths
    input_file = "doaj-csv.csv"
    output_file = "doaj-csv-cleaned.csv"
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found in current directory")
        exit(1)
    
    # Clean the CSV
    print(f"Reading {input_file}...")
    df = clean_doaj_csv(input_file, output_file)
    
    # Display results
    display_journals(df, num_rows=5)
    print_statistics(df)
    
    print(f"\n✓ Successfully processed {len(df)} journals")
