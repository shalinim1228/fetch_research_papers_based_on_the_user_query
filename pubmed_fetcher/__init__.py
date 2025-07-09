"""
PubMed Fetcher - A tool to fetch papers from PubMed using E-Utilities API.
"""

from .pubmed_api import (
    fetch_papers, 
    search_papers_batch, 
    extract_paper_info,
    PubMedAPIError,
    PubMedParsingError
)
from .csv_utils import write_to_csv, read_from_csv

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "fetch_papers", 
    "search_papers_batch", 
    "extract_paper_info",
    "write_to_csv",
    "read_from_csv",
    "PubMedAPIError",
    "PubMedParsingError"
] 