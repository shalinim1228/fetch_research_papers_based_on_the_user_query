"""
Example script demonstrating industry affiliation detection.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pubmed_fetcher import fetch_papers, extract_paper_info


def analyze_industry_papers(query: str, max_results: int = 20):
    """Analyze papers for industry affiliations."""
    
    print(f"Searching for papers about: '{query}'")
    print("=" * 60)
    
    # Fetch papers
    papers = fetch_papers(query, max_results=max_results)
    
    if not papers:
        print("No papers found.")
        return
    
    # Analyze industry involvement
    total_papers = len(papers)
    industry_papers = [p for p in papers if p.get('industry_authors')]
    industry_count = len(industry_papers)
    
    print(f"Total papers found: {total_papers}")
    print(f"Papers with industry authors: {industry_count}")
    print(f"Industry involvement rate: {(industry_count/total_papers)*100:.1f}%")
    print()
    
    # Show detailed analysis
    print("Papers with Industry Authors:")
    print("-" * 60)
    
    for i, paper in enumerate(industry_papers, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   PMID: {paper['pmid']}")
        print(f"   Journal: {paper['journal']}")
        print(f"   Year: {paper['publication_year']}")
        
        # Show industry authors
        industry_authors = paper.get('industry_authors', [])
        if industry_authors:
            print(f"   Industry Authors: {', '.join(industry_authors)}")
        
        # Show industry affiliations
        industry_affiliations = paper.get('industry_affiliations', [])
        if industry_affiliations:
            print(f"   Companies: {', '.join(industry_affiliations)}")
    
    # Summary of companies
    all_affiliations = []
    for paper in industry_papers:
        all_affiliations.extend(paper.get('industry_affiliations', []))
    
    if all_affiliations:
        print(f"\nCompanies involved:")
        print("-" * 60)
        unique_companies = list(set(all_affiliations))
        for company in sorted(unique_companies):
            count = all_affiliations.count(company)
            print(f"  {company}: {count} paper(s)")


def main():
    """Main function with example queries."""
    
    # Example queries to test
    queries = [
        "cancer immunotherapy",
        "COVID-19 vaccine development",
        "Alzheimer's disease treatment",
        "diabetes drug discovery"
    ]
    
    for query in queries:
        print(f"\n{'='*80}")
        analyze_industry_papers(query, max_results=15)
        print(f"{'='*80}")


if __name__ == "__main__":
    main() 