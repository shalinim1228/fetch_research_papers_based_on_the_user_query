#!/usr/bin/env python3
"""
Test script to verify email extraction functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pubmed_fetcher import fetch_papers


def test_email_extraction():
    """Test email extraction with a simple query."""
    
    print("Testing email extraction...")
    print("=" * 50)
    
    # Test with a query that might have emails
    query = "corresponding author"
    papers = fetch_papers(query, max_results=5)
    
    if not papers:
        print("No papers found.")
        return
    
    print(f"Found {len(papers)} papers:")
    print()
    
    emails_found = 0
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.get('title', 'No title')}")
        print(f"   PMID: {paper.get('pmid', 'N/A')}")
        
        # Show corresponding email
        corresponding_email = paper.get('corresponding_email', '')
        if corresponding_email:
            print(f"   📧 Email: {corresponding_email}")
            emails_found += 1
        else:
            print(f"   📧 Email: Not found")
        
        # Show authors
        authors = paper.get('authors', [])
        if authors:
            print(f"   👥 Authors: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
        
        print("-" * 50)
    
    print(f"\nSummary:")
    print(f"  Total papers: {len(papers)}")
    print(f"  Papers with emails: {emails_found}")
    print(f"  Email success rate: {(emails_found/len(papers))*100:.1f}%")


if __name__ == "__main__":
    test_email_extraction() 