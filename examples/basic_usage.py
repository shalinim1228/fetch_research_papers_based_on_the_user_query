"""
Basic usage example for pubmed_fetcher.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pubmed_fetcher import fetch_papers, search_papers_batch


def main():
    # Example 1: Basic search
    print("Searching for papers about 'machine learning'...")
    papers = fetch_papers("machine learning", max_results=5)
    
    print(f"Found {len(papers)} papers:")
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.get('title', 'No title')}")
        print(f"   Authors: {', '.join(paper.get('authors', []))}")
        print(f"   Journal: {paper.get('journal', 'Unknown')}")
        print(f"   Year: {paper.get('publication_year', 'Unknown')}")
        print(f"   DOI: {paper.get('doi', 'No DOI')}")
        
        # Show corresponding email if available
        corresponding_email = paper.get('corresponding_email', '')
        if corresponding_email:
            print(f"   Corresponding Email: {corresponding_email}")
    
    # Example 2: Batch search
    print("\n" + "="*50)
    print("Searching for papers about 'cancer immunotherapy' in batches...")
    batch_papers = search_papers_batch("cancer immunotherapy", total_results=10, batch_size=5)
    
    print(f"Found {len(batch_papers)} papers in total")


if __name__ == "__main__":
    main() 