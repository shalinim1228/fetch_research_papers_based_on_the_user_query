# PubMed Fetcher

A Python tool to fetch papers from PubMed using the E-Utilities API with intelligent detection of pharmaceutical and biotech industry affiliations.

## Project Overview

PubMed Fetcher is designed to help researchers and analysts identify scientific papers with industry involvement. It uses heuristics to distinguish between academic and industry affiliations, making it easier to track pharmaceutical and biotech company participation in research.

---

## Code Organization

The codebase is organized as follows:

```
project_root/
├── pubmed_fetcher/
│   ├── __init__.py
│   ├── pubmed_api.py         # Main logic for fetching and parsing PubMed data
│   ├── cli.py                # Command-line interface (optional, for advanced use)
│   └── csv_utils.py          # CSV writing and reading utilities
├── save_papers_to_csv.py     # Main script for fetching and saving/printing results
├── examples/
│   ├── basic_usage.py        # Example usage script
│   └── industry_analysis.py  # Example for industry affiliation analysis
├── tests/
│   └── test_pubmed_api.py    # Unit tests
├── README.md                 # Project documentation
└── pyproject.toml            # Dependency and project metadata (if using Poetry)
```

- **pubmed_fetcher/pubmed_api.py**: Contains core functions for querying PubMed, parsing XML, and extracting structured information (including industry affiliation and emails).
- **pubmed_fetcher/csv_utils.py**: Contains functions for writing and reading CSV files.
- **save_papers_to_csv.py**: The main entry-point script for end users. Accepts command-line arguments for query, output file, debug, etc.
- **examples/**: Contains example scripts for different use cases.
- **tests/**: Contains unit tests for core functionality.

---

## Installation & Execution

### Prerequisites
- Python 3.8 or higher

### 1. Clone the Repository
```bash
cd "C:/Users/Intel/Desktop/PAPER FETCH/pubmed_fetcher"
```

### 2. (Optional) Create and Activate a Virtual Environment
```bash
python -m venv venv
./venv/Scripts/activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install requests pandas
```

### 4. Run the Program

**Print results to terminal:**
```bash
python save_papers_to_csv.py "machine learning"
```

**Save results to a CSV file:**
```bash
python save_papers_to_csv.py "COVID-19 vaccine" -f covid_papers.csv
```

**Show help:**
```bash
python save_papers_to_csv.py -h
```

---

## Tools and Libraries Used

- [requests](https://docs.python-requests.org/en/latest/): For HTTP requests to the PubMed E-Utilities API
- [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html): For parsing XML responses
- [csv (Python standard library)](https://docs.python.org/3/library/csv.html): For reading and writing CSV files
- [argparse (Python standard library)](https://docs.python.org/3/library/argparse.html): For command-line argument parsing
- [logging (Python standard library)](https://docs.python.org/3/library/logging.html): For debug and info output
- [typing (Python standard library)](https://docs.python.org/3/library/typing.html): For type hints and code clarity

**No LLMs (Large Language Models) are used in the code itself.**

---

## Industry Affiliation Detection

The system uses a multi-layered heuristic approach to identify industry affiliations:
- **Academic Institution Exclusion**: Excludes affiliations with terms like university, college, institute, hospital, etc.
- **Industry Keyword Detection**: Includes affiliations with terms like pharma, biotech, inc., ltd., and major company names.
- **Pattern Matching**: Additional regex patterns for company-like names.

---

## Troubleshooting

- Always use `-h` as an option to your script, not by itself. Example:
  ```bash
  python save_papers_to_csv.py -h
  ```
- If you get an import error, make sure you are running the script from the correct directory and your environment is activated.
- If you get a permissions error writing the CSV, try a different output filename or directory.
- If you see empty results, try a broader query or check your internet connection.

---

## License

This project is licensed under the MIT License. 