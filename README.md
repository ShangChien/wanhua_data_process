# Odor data process Toolkit

A Python package for molecular chemistry data processing and analysis using RDKit, with focus on odor/flavor compounds and their properties.

## Overview

This project provides tools for:
- Molecular structure handling using RDKit
- Chemical data processing and analysis
- Odor/flavor compound classification and visualization
- Database operations for chemical compounds
- Web scraping utilities for chemical data retrieval

## Features

- **Molecular Structure Processing**: Utilizes RDKit for molecular structure analysis, including SMILES/SMARTS parsing, stereochemistry handling, and molecular fingerprinting.
- **Chemical Database Management**: Provides data models and utilities for storing and querying chemical compounds with properties like CAS numbers, molecular formulas, and odor labels.
- **Odor Analysis**: Tools for analyzing and visualizing odor/flavor compound distributions and relationships.
- **Web Scraping Utilities**: Automated tools for retrieving chemical data from public databases like PubChem and The Good Scents Company.
- **Data Visualization**: Functions for creating bar charts and treemaps to visualize odor label distributions.

## Installation

```bash
pip install uv # Install uv if you haven't already
uv sync
source .venv/bin/activate

```

## Dependencies

- RDKit: Molecular informatics library
- Pydantic: Data validation and settings management
- BeautifulSoup4: Web scraping
- LXML: XML/HTML parser
- Seaborn: Statistical data visualization
- Squarify: Treemap visualization
- Loguru: Logging
- Pandas: Data manipulation
- Matplotlib: Plotting

## Usage

### Basic Structure

The project is organized into the following modules:

- `src/struct/`: Data models using Pydantic for type validation
- `src/utils/`: Utility functions for molecular processing, web scraping, and visualization
- `src/database/`: Data files and database-related operations

### Key Data Models

- `MolBase`: Basic molecular data model with SMILES representation
- `MolDB`: Extended molecular model with properties like CAS, formula, odor labels, etc.
- `FilterItem`: Query filtering system for molecular searches
- `RES`: Generic response model for API-like interactions

### Example

```python
from src.struct.base import MolDB
from src.utils.base import is_valid_smiles

# Create a molecular record
mol = MolDB(
    id=1,
    smiles="CCO",  # Ethanol
    cas="64-17-5",
    odor_labels=["alcoholic", "sweet"]
)

# Validate SMILES
if is_valid_smiles(mol.smiles):
    print(f"Valid molecule: {mol.smiles}")
```

## Data Analysis Capabilities

The project includes utilities for:

- **Stereochemistry Analysis**: Counting E/Z isomers and chiral centers in SMILES
- **Odor Distribution Visualization**: Creating bar charts and treemaps of odor label frequencies
- **Molecular Property Calculations**: Molecular weight, formula, etc.

## Web Scraping Tools

The `robot.py` module provides asynchronous tools for:

- Fetching compound data from PubChem by CAS number
- Extracting odor and flavor labels from The Good Scents Company
- Retrieving molecular properties and IUPAC names

## File Structure
```
├── README.md 
├── main.py 
├── pyproject.toml 
├── src/ 
│ ├── database/ # Data files and datasets 
│ ├── struct/ # Data models 
│ │ └── base.py # Pydantic models for molecular data 
│ └── utils/ # Utility functions 
│ ├── base.py # Molecular processing and visualization 
│ └── robot.py # Web scraping utilities
```

## License

This project is licensed under the MIT License