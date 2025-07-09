"""
PubMed API module for fetching papers using E-Utilities API.
"""

import requests
import time
import re
import logging
from typing import List, Dict, Any, Optional, Union
from urllib.parse import quote
from .csv_utils import write_to_csv


class PubMedAPIError(Exception):
    """Custom exception for PubMed API errors."""
    pass


class PubMedParsingError(Exception):
    """Custom exception for XML parsing errors."""
    pass


def fetch_papers(query: str, max_results: int = 100, retstart: int = 0) -> List[Dict[str, Any]]:
    """
    Fetch papers from PubMed using E-Utilities API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 100)
        retstart: Starting position for results (default: 0)
    
    Returns:
        List of dictionaries containing paper metadata
        
    Raises:
        PubMedAPIError: If there's an error with the API request
        ValueError: If query is empty or invalid
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    if max_results <= 0:
        raise ValueError("max_results must be positive")
    
    if retstart < 0:
        raise ValueError("retstart must be non-negative")
    
    # Base URL for PubMed E-Utilities
    base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    # Step 1: Search for papers
    search_url: str = f"{base_url}/esearch.fcgi"
    search_params: Dict[str, Union[str, int]] = {
        'db': 'pubmed',
        'term': query.strip(),
        'retmax': max_results,
        'retstart': retstart,
        'retmode': 'json',
        'sort': 'relevance'
    }
    
    try:
        logging.debug(f"Searching PubMed with query: '{query}'")
        
        # Search for papers
        search_response: requests.Response = requests.get(search_url, params=search_params, timeout=30)
        search_response.raise_for_status()
        search_data: Dict[str, Any] = search_response.json()
        
        # Extract PMIDs
        id_list: List[str] = search_data.get('esearchresult', {}).get('idlist', [])
        
        if not id_list:
            logging.info("No papers found for the given query")
            return []
        
        logging.debug(f"Found {len(id_list)} PMIDs")
        
        # Step 2: Fetch detailed information for each paper
        fetch_url: str = f"{base_url}/efetch.fcgi"
        fetch_params: Dict[str, str] = {
            'db': 'pubmed',
            'id': ','.join(id_list),
            'retmode': 'xml',
            'rettype': 'abstract'
        }
        
        fetch_response: requests.Response = requests.get(fetch_url, params=fetch_params, timeout=60)
        fetch_response.raise_for_status()
        
        # Parse XML response
        papers: List[Dict[str, Any]] = _parse_pubmed_xml(fetch_response.text)
        
        # Respect NCBI's rate limiting (3 requests per second)
        time.sleep(0.34)
        
        logging.info(f"Successfully fetched {len(papers)} papers")
        return papers
        
    except requests.RequestException as e:
        error_msg: str = f"Failed to fetch papers from PubMed API: {str(e)}"
        logging.error(error_msg)
        raise PubMedAPIError(error_msg)
    except Exception as e:
        error_msg: str = f"Unexpected error during API request: {str(e)}"
        logging.error(error_msg)
        raise PubMedAPIError(error_msg)


def extract_paper_info(xml_data: str) -> List[Dict[str, str]]:
    """
    Parse XML from PubMed and extract paper information with industry affiliations.
    
    Args:
        xml_data: XML content from PubMed API
        
    Returns:
        List of dictionaries with fields: PubmedID, Title, Publication Date, 
        Non-academic Author(s), Company Affiliation(s), Corresponding Author Email
        
    Raises:
        PubMedParsingError: If XML parsing fails
        ValueError: If xml_data is empty or invalid
    """
    if not xml_data or not xml_data.strip():
        raise ValueError("XML data cannot be empty")
    
    import xml.etree.ElementTree as ET
    
    papers: List[Dict[str, str]] = []
    
    try:
        # Parse XML
        root: ET.Element = ET.fromstring(xml_data)
        
        # Find all PubmedArticle elements
        for article in root.findall('.//PubmedArticle'):
            paper_info: Dict[str, str] = {
                'PubmedID': '',
                'Title': '',
                'Publication Date': '',
                'Non-academic Author(s)': '',
                'Company Affiliation(s)': '',
                'Corresponding Author Email': ''
            }
            
            # Extract PMID
            pmid_elem: Optional[ET.Element] = article.find('.//PMID')
            if pmid_elem is not None and pmid_elem.text:
                paper_info['PubmedID'] = pmid_elem.text
            
            # Extract title
            title_elem: Optional[ET.Element] = article.find('.//ArticleTitle')
            if title_elem is not None and title_elem.text:
                paper_info['Title'] = title_elem.text
            
            # Extract publication date
            pub_date: Optional[ET.Element] = article.find('.//PubDate')
            if pub_date is not None:
                year_elem: Optional[ET.Element] = pub_date.find('Year')
                month_elem: Optional[ET.Element] = pub_date.find('Month')
                day_elem: Optional[ET.Element] = pub_date.find('Day')
                
                date_parts: List[str] = []
                if year_elem is not None and year_elem.text:
                    date_parts.append(year_elem.text)
                if month_elem is not None and month_elem.text:
                    date_parts.append(month_elem.text)
                if day_elem is not None and day_elem.text:
                    date_parts.append(day_elem.text)
                
                paper_info['Publication Date'] = '-'.join(date_parts)
            
            # Extract authors and their affiliations
            non_academic_authors: List[str] = []
            company_affiliations: List[str] = []
            corresponding_email: str = ""
            
            author_list: Optional[ET.Element] = article.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('.//Author'):
                    author_name: str = ""
                    last_name_elem: Optional[ET.Element] = author.find('LastName')
                    first_name_elem: Optional[ET.Element] = author.find('ForeName')
                    
                    if last_name_elem is not None and last_name_elem.text and first_name_elem is not None and first_name_elem.text:
                        author_name = f"{first_name_elem.text} {last_name_elem.text}"
                    
                    # Check for industry affiliations
                    affiliations: List[ET.Element] = author.findall('.//AffiliationInfo/Affiliation')
                    has_industry_affiliation: bool = False
                    
                    for affiliation in affiliations:
                        if affiliation.text:
                            affiliation_text: str = affiliation.text.lower()
                            
                            # Check if it's an industry affiliation
                            if _is_industry_affiliation(affiliation_text):
                                has_industry_affiliation = True
                                company_affiliations.append(affiliation.text)
                    
                    if has_industry_affiliation and author_name:
                        non_academic_authors.append(author_name)
                    
                    # Check for corresponding author email
                    if corresponding_email == "":
                        email_elem: Optional[ET.Element] = author.find('.//AffiliationInfo/Affiliation')
                        if email_elem is not None and email_elem.text and '@' in email_elem.text:
                            # Extract email from affiliation text
                            email_match: Optional[re.Match] = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_elem.text)
                            if email_match:
                                corresponding_email = email_match.group()
            
            paper_info['Non-academic Author(s)'] = '; '.join(non_academic_authors)
            paper_info['Company Affiliation(s)'] = '; '.join(set(company_affiliations))  # Remove duplicates
            paper_info['Corresponding Author Email'] = corresponding_email
            
            papers.append(paper_info)
            
    except ET.ParseError as e:
        error_msg: str = f"Failed to parse XML response: {str(e)}"
        logging.error(error_msg)
        raise PubMedParsingError(error_msg)
    except Exception as e:
        error_msg: str = f"Unexpected error during XML parsing: {str(e)}"
        logging.error(error_msg)
        raise PubMedParsingError(error_msg)
    
    return papers


def _is_industry_affiliation(affiliation_text: str) -> bool:
    """
    Determine if an affiliation is from industry (pharmaceutical/biotech) using heuristics.
    
    Args:
        affiliation_text: Affiliation text to analyze (should be lowercase)
        
    Returns:
        True if affiliation appears to be from industry, False otherwise
    """
    if not affiliation_text:
        return False
    
    # Keywords that indicate academic institutions (exclude these)
    academic_keywords: List[str] = [
        'university', 'college', 'institute', 'school', 'academy', 'hospital',
        'medical center', 'clinic', 'foundation', 'government', 'ministry',
        'department of', 'national institute', 'nih', 'nsf', 'nci', 'cdc',
        'fda', 'who', 'university of', 'college of', 'institute of'
    ]
    
    # Keywords that indicate industry (include these)
    industry_keywords: List[str] = [
        'pharma', 'biotech', 'biotechnology', 'pharmaceutical', 'inc.', 'ltd.',
        'corporation', 'corp.', 'company', 'co.', 'limited', 'llc', 'l.l.c.',
        'novartis', 'pfizer', 'merck', 'johnson & johnson', 'roche', 'astrazeneca',
        'bristol-myers', 'bristol myers', 'eli lilly', 'sanofi', 'gilead',
        'amgen', 'biogen', 'genentech', 'regeneron', 'moderna', 'biontech',
        'astra', 'zeneca', 'glaxosmithkline', 'gsk', 'abbvie', 'takeda',
        'bayer', 'boehringer', 'ingelheim', 'abbott', 'medtronic', 'baxter',
        'thermo fisher', 'illumina', 'qiagen', 'agilent', 'waters', 'perkinelmer'
    ]
    
    # Check for academic keywords first (exclude if found)
    for keyword in academic_keywords:
        if keyword in affiliation_text:
            return False
    
    # Check for industry keywords (include if found)
    for keyword in industry_keywords:
        if keyword in affiliation_text:
            return True
    
    # Additional heuristics for industry affiliations
    # Look for patterns like "X Research Laboratories" or "Y Therapeutics"
    industry_patterns: List[str] = [
        r'\b\w+\s+(research|therapeutics|sciences|technologies|solutions|partners)\b',
        r'\b\w+\s+&\s+\w+\s+(pharmaceuticals|biotechnology|sciences)\b',
        r'\b\w+\s+(pharma|biotech|therapeutics)\b'
    ]
    
    for pattern in industry_patterns:
        if re.search(pattern, affiliation_text):
            return True
    
    return False


def _parse_pubmed_xml(xml_content: str) -> List[Dict[str, Any]]:
    """
    Parse PubMed XML response and extract paper metadata.
    
    Args:
        xml_content: XML content from PubMed API
        
    Returns:
        List of dictionaries containing paper metadata
        
    Raises:
        PubMedParsingError: If XML parsing fails
    """
    import xml.etree.ElementTree as ET
    
    papers: List[Dict[str, Any]] = []
    
    try:
        # Parse XML
        root: ET.Element = ET.fromstring(xml_content)
        
        # Find all PubmedArticle elements
        for article in root.findall('.//PubmedArticle'):
            paper_data: Dict[str, Any] = {}
            
            # Extract PMID
            pmid_elem: Optional[ET.Element] = article.find('.//PMID')
            if pmid_elem is not None and pmid_elem.text:
                paper_data['pmid'] = pmid_elem.text
            
            # Extract title
            title_elem: Optional[ET.Element] = article.find('.//ArticleTitle')
            if title_elem is not None and title_elem.text:
                paper_data['title'] = title_elem.text
            
            # Extract abstract
            abstract_elem: Optional[ET.Element] = article.find('.//AbstractText')
            if abstract_elem is not None and abstract_elem.text:
                paper_data['abstract'] = abstract_elem.text
            else:
                paper_data['abstract'] = ""
            
            # Extract authors with affiliations and emails
            authors: List[str] = []
            industry_authors: List[str] = []
            industry_affiliations: List[str] = []
            corresponding_email: str = ""
            
            author_list: Optional[ET.Element] = article.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('.//Author'):
                    last_name_elem: Optional[ET.Element] = author.find('LastName')
                    first_name_elem: Optional[ET.Element] = author.find('ForeName')
                    
                    if last_name_elem is not None and last_name_elem.text and first_name_elem is not None and first_name_elem.text:
                        author_name: str = f"{first_name_elem.text} {last_name_elem.text}"
                        authors.append(author_name)
                        
                        # Check affiliations for industry
                        affiliations: List[ET.Element] = author.findall('.//AffiliationInfo/Affiliation')
                        for affiliation in affiliations:
                            if affiliation.text and _is_industry_affiliation(affiliation.text.lower()):
                                industry_authors.append(author_name)
                                industry_affiliations.append(affiliation.text)
                        
                        # Check for corresponding author email
                        if corresponding_email == "":
                            for affiliation in affiliations:
                                if affiliation.text and '@' in affiliation.text:
                                    # Extract email from affiliation text
                                    email_match: Optional[re.Match] = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', affiliation.text)
                                    if email_match:
                                        corresponding_email = email_match.group()
                                        break
            
            paper_data['authors'] = authors
            paper_data['industry_authors'] = industry_authors
            paper_data['industry_affiliations'] = list(set(industry_affiliations))  # Remove duplicates
            paper_data['corresponding_email'] = corresponding_email
            
            # Extract journal information
            journal_elem: Optional[ET.Element] = article.find('.//Journal/Title')
            if journal_elem is not None and journal_elem.text:
                paper_data['journal'] = journal_elem.text
            else:
                paper_data['journal'] = ""
            
            # Extract publication date
            pub_date: Optional[ET.Element] = article.find('.//PubDate')
            if pub_date is not None:
                year_elem: Optional[ET.Element] = pub_date.find('Year')
                month_elem: Optional[ET.Element] = pub_date.find('Month')
                if year_elem is not None and year_elem.text:
                    paper_data['publication_year'] = year_elem.text
                    paper_data['publication_month'] = month_elem.text if month_elem is not None and month_elem.text else ""
                else:
                    paper_data['publication_year'] = ""
                    paper_data['publication_month'] = ""
            else:
                paper_data['publication_year'] = ""
                paper_data['publication_month'] = ""
            
            # Extract DOI
            doi_elem: Optional[ET.Element] = article.find('.//ELocationID[@EIdType="doi"]')
            if doi_elem is not None and doi_elem.text:
                paper_data['doi'] = doi_elem.text
            else:
                paper_data['doi'] = ""
            
            papers.append(paper_data)
            
    except ET.ParseError as e:
        error_msg: str = f"Failed to parse XML response: {str(e)}"
        logging.error(error_msg)
        raise PubMedParsingError(error_msg)
    
    return papers


def search_papers_batch(query: str, total_results: int = 1000, batch_size: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch papers in batches to handle large result sets.
    
    Args:
        query: Search query string
        total_results: Total number of results to fetch
        batch_size: Number of results per batch
        
    Returns:
        List of dictionaries containing paper metadata
        
    Raises:
        PubMedAPIError: If there's an error with the API request
        ValueError: If parameters are invalid
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    if total_results <= 0:
        raise ValueError("total_results must be positive")
    
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    
    all_papers: List[Dict[str, Any]] = []
    
    try:
        for start in range(0, total_results, batch_size):
            batch_papers: List[Dict[str, Any]] = fetch_papers(query, max_results=batch_size, retstart=start)
            all_papers.extend(batch_papers)
            
            # Stop if we got fewer results than requested
            if len(batch_papers) < batch_size:
                break
        
        logging.info(f"Successfully fetched {len(all_papers)} papers in batches")
        return all_papers
        
    except Exception as e:
        error_msg: str = f"Error during batch search: {str(e)}"
        logging.error(error_msg)
        raise PubMedAPIError(error_msg) 