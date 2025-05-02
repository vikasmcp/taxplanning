# Indian Tax Planning Assistant

A Python-based application that calculates estimated tax liability based on user inputs and provides basic tax-saving recommendations under the current Indian tax laws.

## Features

- Input form to collect user financial data (annual income, deductions, investments, etc.)
- Calculate taxable income based on income slabs for India
- Suggest possible deductions or investment options under sections (80C, 80D, etc.)
- Generate a summary report of tax computation and recommendations
- Export the report as a downloadable Excel file
- Streamlit UI for easy interaction

## Requirements

- Python 3.7+
- Required packages listed in requirements.txt

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

## Features

- Supports both Old and New tax regimes
- Handles various deduction sections (80C, 80D, 80TTA, HRA)
- Interactive UI with real-time calculations
- Exportable reports in Excel format
- Tax saving recommendations