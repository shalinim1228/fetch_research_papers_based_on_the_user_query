import argparse
import logging
from pubmed_fetcher.pubmed_api import extract_paper_info
from pubmed_fetcher.csv_utils import write_to_csv
import requests
from typing import List, Dict


def print_papers(papers: List[Dict[str, str]]):
    if not papers:
        print("No papers found.")
        return
    print(f"Found {len(papers)} papers:\n")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.get('Title', 'No title')}")
        print(f"   PubmedID: {paper.get('PubmedID', '')}")
        print(f"   Publication Date: {paper.get('Publication Date', '')}")
        print(f"   Non-academic Author(s): {paper.get('Non-academic Author(s)', '')}")
        print(f"   Company Affiliation(s): {paper.get('Company Affiliation(s)', '')}")
        print(f"   Corresponding Author Email: {paper.get('Corresponding Author Email', '')}")
        print("-")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch PubMed papers for a query and save as CSV or print to terminal.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'query',
        nargs='?',
        default='cancer immunotherapy',
        help='Search query for PubMed (in quotes if multi-word)'
    )
    parser.add_argument(
        '-f', '--file',
        default=None,
        help='Output CSV filename (if not provided, print results to terminal)'
    )
    parser.add_argument(
        '-m', '--max-results',
        type=int,
        default=20,
        help='Maximum number of results to fetch'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Print debug information during execution'
    )
    args = parser.parse_args()

    # Setup logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.debug(f"Arguments: {args}")
    else:
        logging.basicConfig(level=logging.WARNING)

    query = args.query
    max_results = args.max_results
    output_file = args.file

    logging.info(f"Fetching up to {max_results} papers for query: '{query}'")

    # Fetch XML from PubMed
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    search_url = f"{base_url}/esearch.fcgi"
    search_params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'retmode': 'json',
        'sort': 'relevance'
    }
    if args.debug:
        logging.debug(f"Search URL: {search_url}")
        logging.debug(f"Search Params: {search_params}")
    search_response = requests.get(search_url, params=search_params)
    search_response.raise_for_status()
    id_list = search_response.json().get('esearchresult', {}).get('idlist', [])
    if not id_list:
        print("No papers found for the given query.")
        return
    fetch_url = f"{base_url}/efetch.fcgi"
    fetch_params = {
        'db': 'pubmed',
        'id': ','.join(id_list),
        'retmode': 'xml',
        'rettype': 'abstract'
    }
    if args.debug:
        logging.debug(f"Fetch URL: {fetch_url}")
        logging.debug(f"Fetch Params: {fetch_params}")
    fetch_response = requests.get(fetch_url, params=fetch_params)
    fetch_response.raise_for_status()
    xml_data = fetch_response.text

    # Extract paper info
    csv_data = extract_paper_info(xml_data)

    if output_file:
        write_to_csv(csv_data, output_file)
        print(f"Saved {len(csv_data)} papers to {output_file}")
    else:
        print_papers(csv_data)


if __name__ == "__main__":
    main() 