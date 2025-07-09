"""
CSV utilities for PubMed Fetcher.
"""

import csv
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path


def write_to_csv(data: List[Dict[str, str]], filename: str) -> None:
    """
    Write results to a CSV file with standard columns.
    
    Args:
        data: List of dictionaries containing paper data
        filename: Output CSV filename
        
    Raises:
        FileNotFoundError: If the directory doesn't exist and can't be created
        PermissionError: If the file can't be written due to permissions
        ValueError: If data is empty or malformed
    """
    if not data:
        raise ValueError("No data provided to write to CSV")
    
    # Define the standard columns in order
    columns = [
        'PubmedID',
        'Title', 
        'Publication Date',
        'Non-academic Author(s)',
        'Company Affiliation(s)',
        'Corresponding Author Email'
    ]
    
    # Ensure the output directory exists
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for row in data:
                # Ensure all required columns exist, fill missing ones with empty string
                formatted_row = {col: row.get(col, '') for col in columns}
                writer.writerow(formatted_row)
        
        logging.info(f"Successfully wrote {len(data)} records to {filename}")
        
    except FileNotFoundError as e:
        logging.error(f"Directory not found for file {filename}: {e}")
        raise
    except PermissionError as e:
        logging.error(f"Permission denied writing to {filename}: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error writing CSV file {filename}: {e}")
        raise


def read_from_csv(filename: str) -> List[Dict[str, str]]:
    """
    Read data from a CSV file.
    
    Args:
        filename: Input CSV filename
        
    Returns:
        List of dictionaries containing paper data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is malformed
    """
    if not Path(filename).exists():
        raise FileNotFoundError(f"CSV file not found: {filename}")
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)
        
        logging.info(f"Successfully read {len(data)} records from {filename}")
        return data
        
    except Exception as e:
        logging.error(f"Error reading CSV file {filename}: {e}")
        raise ValueError(f"Failed to read CSV file: {e}") 