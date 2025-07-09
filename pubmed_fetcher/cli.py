#!/usr/bin/env python3
"""
Command-line interface for PubMed Fetcher.
"""

import argparse
import sys
import logging
from typing import List, Dict, Any
from .pubmed_api import fetch_papers, extract_paper_info, PubMedAPIError, PubMedParsingError
from .csv_utils import write_to_csv


def setup_logging(debug: bool = False) -> None:
    """
    Setup logging configuration.
    
    Args:
        debug: If True, set logging level to DEBUG
    """
    level: int = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def display_papers(papers: List[Dict[str, Any]], show_industry_only: bool = False) -> None:
    """
    Display papers in a formatted way.
    
    Args:
        papers: List of paper dictionaries
        show_industry_only: If True, only show papers with industry authors
    """
    if not papers:
        print("No papers found.")
        return
    
    filtered_papers: List[Dict[str, Any]] = papers
    if show_industry_only:
        filtered_papers = [p for p in papers if p.get('industry_authors')]
        if not filtered_papers:
            print("No papers with industry authors found.")
            return
    
    print(f"\nFound {len(filtered_papers)} papers:")
    print("=" * 80)
    
    for i, paper in enumerate(filtered_papers, 1):
        print(f"\n{i}. {paper.get('title', 'No title')}")
        print(f"   PMID: {paper.get('pmid', 'N/A')}")
        print(f"   Journal: {paper.get('journal', 'Unknown')}")
        print(f"   Year: {paper.get('publication_year', 'Unknown')}")
        print(f"   DOI: {paper.get('doi', 'No DOI')}")
        
        # Show corresponding email if available
        corresponding_email = paper.get('corresponding_email', '')
        if corresponding_email:
            print(f"   Corresponding Email: {corresponding_email}")
        
        # Show all authors
        authors: List[str] = paper.get('authors', [])
        if authors:
            print(f"   Authors: {', '.join(authors)}")
        
        # Highlight industry authors
        industry_authors: List[str] = paper.get('industry_authors', [])
        if industry_authors:
            print(f"   Industry Authors: {', '.join(industry_authors)}")
        
        # Show industry affiliations
        industry_affiliations: List[str] = paper.get('industry_affiliations', [])
        if industry_affiliations:
            print(f"   Industry Affiliations: {', '.join(industry_affiliations)}")
        
        print("-" * 80)


def main() -> None:
    """Main CLI function."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Fetch papers from PubMed with industry affiliation detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "cancer immunotherapy"
  %(prog)s "machine learning" -f results.csv
  %(prog)s "COVID-19 vaccine" -d -f vaccine_papers.csv
        """
    )
    
    parser.add_argument(
        'query',
        help='Search query for PubMed papers'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Save results to CSV file'
    )
    
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Show debug logs'
    )
    
    parser.add_argument(
        '-i', '--industry-only',
        action='store_true',
        help='Show only papers with industry authors'
    )
    
    parser.add_argument(
        '-m', '--max-results',
        type=int,
        default=50,
        help='Maximum number of results to fetch (default: 50)'
    )
    
    args: argparse.Namespace = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    try:
        logging.info(f"Searching PubMed for: '{args.query}'")
        logging.info(f"Max results: {args.max_results}")
        
        # Fetch papers
        papers: List[Dict[str, Any]] = fetch_papers(args.query, max_results=args.max_results)
        
        if not papers:
            print("No papers found for the given query.")
            return
        
        logging.info(f"Retrieved {len(papers)} papers")
        
        # Count papers with industry authors
        industry_papers: List[Dict[str, Any]] = [p for p in papers if p.get('industry_authors')]
        logging.info(f"Found {len(industry_papers)} papers with industry authors")
        
        # Display results
        display_papers(papers, show_industry_only=args.industry_only)
        
        # Save to CSV if requested
        if args.file:
            try:
                write_to_csv(papers, args.file)
            except Exception as e:
                logging.error(f"Failed to save CSV file: {e}")
                print(f"Error: Could not save to CSV file: {e}")
        
        # Summary
        print(f"\nSummary:")
        print(f"  Total papers: {len(papers)}")
        print(f"  Papers with industry authors: {len(industry_papers)}")
        if args.file:
            print(f"  Results saved to: {args.file}")
    
    except PubMedAPIError as e:
        logging.error(f"PubMed API error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except PubMedParsingError as e:
        logging.error(f"XML parsing error: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info("Operation cancelled by user")
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 